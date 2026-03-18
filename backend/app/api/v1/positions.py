from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.position import Position
from app.models.ala import Ala
from app.models.user import User
from typing import List, Optional

router = APIRouter(prefix="/positions", tags=["positions"])

@router.get("/")
def list_positions(
    ala_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "gestor", "rh", "visualizador"))
):
    query = db.query(Position)
    if ala_id:
        query = query.filter(Position.ala_id == ala_id)
    positions = query.order_by(Position.ala_id, Position.title).all()
    ala_map = {a.id: {"code": a.code, "name": a.name} for a in db.query(Ala).all()}
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "base_salary": p.base_salary,
            "level": getattr(p, "level", None),
            "department_id": p.department_id,
            "ala_id": getattr(p, "ala_id", None),
            "ala_code": ala_map.get(p.ala_id, {}).get("code") if getattr(p, "ala_id", None) else None,
            "ala_name": ala_map.get(p.ala_id, {}).get("name") if getattr(p, "ala_id", None) else None,
        }
        for p in positions
    ]

@router.post("/")
def create_position(data: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
    title = str(data.get("title", "")).strip()
    if not title:
        raise HTTPException(status_code=400, detail="title é obrigatório")
    ala_id = data.get("ala_id")
    if ala_id is not None:
        ala = db.query(Ala).filter(Ala.id == int(ala_id)).first()
        if not ala:
            raise HTTPException(status_code=400, detail="Ala não encontrada")
    position = Position(
        title=title,
        description=str(data.get("description", "")),
        base_salary=float(data.get("base_salary", 0)),
        level=data.get("level"),
        department_id=data.get("department_id"),
        ala_id=int(ala_id) if ala_id is not None else None,
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return {
        "id": position.id,
        "title": position.title,
        "description": position.description,
        "base_salary": position.base_salary,
        "level": getattr(position, "level", None),
        "ala_id": getattr(position, "ala_id", None),
    }

@router.put("/{id}")
def update_position(id: int, data: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
    position = db.query(Position).filter(Position.id == id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    if "title" in data:
        position.title = str(data["title"]).strip()
    if "description" in data:
        position.description = str(data["description"])
    if "base_salary" in data:
        position.base_salary = float(data["base_salary"])
    if "level" in data:
        position.level = data["level"] if data["level"] else None
    if "ala_id" in data:
        position.ala_id = int(data["ala_id"]) if data["ala_id"] else None
    if "department_id" in data:
        position.department_id = data["department_id"]
    db.commit()
    db.refresh(position)
    return {
        "id": position.id,
        "title": position.title,
        "description": position.description,
        "base_salary": position.base_salary,
        "level": getattr(position, "level", None),
        "ala_id": getattr(position, "ala_id", None),
    }

@router.delete("/{id}")
def delete_position(id: int, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
    position = db.query(Position).filter(Position.id == id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    db.delete(position)
    db.commit()
    return {"ok": True}
