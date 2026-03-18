from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.ala import Ala
from app.models.user import User
from typing import List

router = APIRouter(prefix="/alas", tags=["alas"])

@router.get("/")
def list_alas(db: Session = Depends(get_db), user: User = Depends(require_role("admin", "gestor", "rh", "visualizador"))):
    return [{"id": a.id, "code": a.code, "name": a.name} for a in db.query(Ala).order_by(Ala.code).all()]

@router.post("/")
def create_ala(data: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
    code = str(data.get("code", "")).strip().upper()
    name = str(data.get("name", "")).strip()
    if not code or not name:
        raise HTTPException(status_code=400, detail="code e name são obrigatórios")
    existing = db.query(Ala).filter(Ala.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ala com código {code} já existe")
    ala = Ala(code=code, name=name)
    db.add(ala)
    db.commit()
    db.refresh(ala)
    return {"id": ala.id, "code": ala.code, "name": ala.name}

@router.put("/{id}")
def update_ala(id: int, data: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
    ala = db.query(Ala).filter(Ala.id == id).first()
    if not ala:
        raise HTTPException(status_code=404, detail="Ala não encontrada")
    if "code" in data:
        ala.code = str(data["code"]).strip().upper()
    if "name" in data:
        ala.name = str(data["name"]).strip()
    db.commit()
    db.refresh(ala)
    return {"id": ala.id, "code": ala.code, "name": ala.name}

@router.delete("/{id}")
def delete_ala(id: int, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
    ala = db.query(Ala).filter(Ala.id == id).first()
    if not ala:
        raise HTTPException(status_code=404, detail="Ala não encontrada")
    db.delete(ala)
    db.commit()
    return {"ok": True}
