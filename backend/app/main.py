from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from app.core.config import Settings
from app.core.database import Base, engine
import app.models.employee
import app.models.department
import app.models.ala
import app.models.position
import app.models.user
import app.models.audit
import app.models.course
import app.models.document
import app.models.evaluation
import app.models.loan
import app.models.loan_installment
import app.models.payroll
import app.models.position_history
import app.models.timesheet
import app.models.timesheet_import

settings = Settings()

CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173", "http://[::1]:5173"]
if settings.CORS_ORIGINS:
    CORS_ORIGINS = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

ALAS_E_CARGOS = [
    ("DEV", "Desenvolvedores", [
        ("Estagiário DEV", "Estagiário de Desenvolvimento", 2000, "Estagiário"),
        ("Desenvolvedor Júnior Nível 1", "Desenvolvedor Júnior", 4000, "Júnior 1"),
        ("Desenvolvedor Júnior Nível 2", "Desenvolvedor Júnior", 5000, "Júnior 2"),
        ("Desenvolvedor Júnior Nível 3", "Desenvolvedor Júnior", 6000, "Júnior 3"),
        ("Desenvolvedor Pleno", "Desenvolvedor Pleno", 8000, "Pleno"),
        ("Desenvolvedor Sênior", "Desenvolvedor Sênior", 12000, "Sênior"),
    ]),
    ("DS", "Data Science", [
        ("Estagiário DS", "Estagiário de Data Science", 2000, "Estagiário"),
        ("Cientista de Dados Júnior", "Cientista de Dados Júnior", 5000, "Júnior"),
        ("Cientista de Dados Pleno", "Cientista de Dados Pleno", 9000, "Pleno"),
        ("Cientista de Dados Sênior", "Cientista de Dados Sênior", 14000, "Sênior"),
    ]),
    ("RH", "Recursos Humanos", [
        ("Estagiário RH", "Estagiário de RH", 1800, "Estagiário"),
        ("Analista RH Júnior", "Analista de RH Júnior", 3500, "Júnior"),
        ("Analista RH Pleno", "Analista de RH Pleno", 5000, "Pleno"),
        ("Analista RH Sênior", "Analista de RH Sênior", 7000, "Sênior"),
    ]),
    ("Marketing", "Marketing", [
        ("Estagiário Marketing", "Estagiário de Marketing", 1800, "Estagiário"),
        ("Analista de Marketing Júnior", "Analista de Marketing Júnior", 3500, "Júnior"),
        ("Analista de Marketing Pleno", "Analista de Marketing Pleno", 5500, "Pleno"),
        ("Analista de Marketing Sênior", "Analista de Marketing Sênior", 8000, "Sênior"),
    ]),
    ("Comercial", "Comercial", [
        ("Estagiário Comercial", "Estagiário Comercial", 1800, "Estagiário"),
        ("Analista Comercial Júnior", "Analista Comercial Júnior", 3500, "Júnior"),
        ("Analista Comercial Pleno", "Analista Comercial Pleno", 5500, "Pleno"),
        ("Analista Comercial Sênior", "Analista Comercial Sênior", 8000, "Sênior"),
    ]),
    ("Juridico", "Jurídico", [
        ("Estagiário Jurídico", "Estagiário Jurídico", 2000, "Estagiário"),
        ("Assessor Jurídico Júnior", "Assessor Jurídico Júnior", 5000, "Júnior"),
        ("Assessor Jurídico Pleno", "Assessor Jurídico Pleno", 7500, "Pleno"),
        ("Assessor Jurídico Sênior", "Assessor Jurídico Sênior", 11000, "Sênior"),
    ]),
    ("CTO", "CTO / Liderança Técnica", [
        ("Tech Lead", "Tech Lead", 15000, "Liderança"),
        ("CTO", "Chief Technology Officer", 25000, "C-Level"),
    ]),
    ("PO", "Product Owner", [
        ("Estagiário PO", "Estagiário de Produto", 2000, "Estagiário"),
        ("Product Owner Júnior", "Product Owner Júnior", 6000, "Júnior"),
        ("Product Owner Pleno", "Product Owner Pleno", 9000, "Pleno"),
        ("Product Owner Sênior", "Product Owner Sênior", 13000, "Sênior"),
    ]),
    ("Designer", "Design", [
        ("Estagiário Designer", "Estagiário de Design", 1800, "Estagiário"),
        ("Designer Júnior", "Designer Júnior", 3500, "Júnior"),
        ("Designer Pleno", "Designer Pleno", 5500, "Pleno"),
        ("Designer Sênior", "Designer Sênior", 8000, "Sênior"),
    ]),
]

def _seed_alas(db):
    from app.models.ala import Ala
    from app.models.position import Position
    for code, name, cargos in ALAS_E_CARGOS:
        ala = Ala(code=code, name=name)
        db.add(ala)
        db.flush()
        for title, desc, salary, level in cargos:
            pos = Position(title=title, description=desc, base_salary=salary, level=level, ala_id=ala.id)
            db.add(pos)
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE evaluations ADD COLUMN evaluation_type VARCHAR(50)"))
            conn.commit()
    except Exception:
        pass
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE timesheets ADD COLUMN overtime_disposition VARCHAR(20)"))
            conn.execute(text("ALTER TABLE timesheets ADD COLUMN overtime_parecer VARCHAR(500)"))
            conn.commit()
    except Exception:
        pass
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE timesheets ADD COLUMN overtime_used INTEGER"))
            conn.commit()
    except Exception:
        pass
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE positions ADD COLUMN level VARCHAR(40)"))
            conn.commit()
    except Exception:
        pass
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE positions ADD COLUMN ala_id INTEGER"))
            conn.commit()
    except Exception:
        pass
    try:
        from app.models.ala import Ala
        from app.models.position import Position
        from app.core.database import SessionLocal
        db = SessionLocal()
        if db.query(Ala).count() == 0:
            _seed_alas(db)
        db.close()
    except Exception:
        pass
    yield


app = FastAPI(title="Dashboard RH", lifespan=lifespan, redirect_slash=False)


def _cors_headers(origin: str) -> dict:
    if origin in CORS_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    return {}


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    """Garante CORS em respostas de erro HTTP (401, 403, etc)."""
    origin = request.headers.get("origin", "")
    content = {"detail": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=content, headers=_cors_headers(origin))


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Garante CORS em erros 500 (exceções não tratadas)."""
    import traceback
    traceback.print_exc()
    origin = request.headers.get("origin", "")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=_cors_headers(origin),
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

from app.api import router as api_router
app.include_router(api_router)
