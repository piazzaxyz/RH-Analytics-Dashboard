from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.schemas.timesheet import TimesheetResponse, TimesheetImportResponse
from app.models.timesheet import Timesheet, TimesheetStatus
from app.models.employee import Employee
from app.models.timesheet_import import TimesheetImport, TimesheetImportFormat
from app.services.file_parser import parse_csv, parse_json, parse_pdf
from app.services.audit_service import log_audit
from app.core.config import Settings
from typing import List, Optional
from datetime import datetime, date

router = APIRouter(prefix="/timesheets", tags=["timesheets"])
settings = Settings()

@router.get("/", response_model=List[TimesheetResponse])
def list_timesheets(
	employee_id: Optional[int] = None,
	month: Optional[str] = None,
	db: Session = Depends(get_db),
	user: User = Depends(require_role("admin", "gestor", "rh", "visualizador"))
):
	query = db.query(Timesheet)
	if employee_id:
		query = query.filter(Timesheet.employee_id == employee_id)
	if month:
		query = query.filter(Timesheet.date.like(f"{month}-%"))
	timesheets = query.all()
	emp_ids = list(set(t.employee_id for t in timesheets))
	emp_names = {e.id: e.full_name for e in db.query(Employee).filter(Employee.id.in_(emp_ids)).all()} if emp_ids else {}
	return [TimesheetResponse(
		id=t.id,
		employee_id=t.employee_id,
		employee_name=emp_names.get(t.employee_id, ""),
		date=t.date,
		clock_in=t.clock_in,
		clock_out=t.clock_out,
		clock_in_2=t.clock_in_2,
		clock_out_2=t.clock_out_2,
		total_minutes=t.total_minutes,
		overtime_50_minutes=t.overtime_50_minutes,
		overtime_100_minutes=t.overtime_100_minutes,
		night_shift_minutes=t.night_shift_minutes,
		overtime_disposition=getattr(t, "overtime_disposition", None),
		overtime_parecer=getattr(t, "overtime_parecer", None),
		overtime_used=getattr(t, "overtime_used", None),
		justification=t.justification,
		status=t.status.value,
		created_at=t.created_at,
		updated_at=t.updated_at
	) for t in timesheets]


@router.post("/overtime", response_model=TimesheetResponse)
def create_overtime(data: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
	employee_id = int(data.get("employee_id", 0))
	date_str = str(data.get("date", ""))[:10]
	overtime_50 = int(data.get("overtime_50_minutes", 0))
	overtime_100 = int(data.get("overtime_100_minutes", 0))
	if not employee_id or not date_str:
		raise HTTPException(status_code=400, detail="employee_id e date são obrigatórios")
	try:
		date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
	except ValueError:
		raise HTTPException(status_code=400, detail="Data inválida")
	emp = db.query(Employee).filter(Employee.id == employee_id).first()
	if not emp:
		raise HTTPException(status_code=400, detail="Colaborador não encontrado")
	total = overtime_50 + overtime_100
	t = Timesheet(
		employee_id=employee_id,
		date=date_val,
		total_minutes=total,
		overtime_50_minutes=overtime_50,
		overtime_100_minutes=overtime_100,
		overtime_disposition=data.get("overtime_disposition", "pago"),
		overtime_parecer=data.get("overtime_parecer"),
		overtime_used=1 if data.get("overtime_used") else 0,
	)
	db.add(t)
	db.commit()
	db.refresh(t)
	log_audit(db, user.id, "create_overtime", "timesheet", t.id, None, data, "127.0.0.1")
	return TimesheetResponse(
		id=t.id,
		employee_id=t.employee_id,
		employee_name=emp.full_name,
		date=t.date,
		clock_in=None,
		clock_out=None,
		clock_in_2=None,
		clock_out_2=None,
		total_minutes=t.total_minutes,
		overtime_50_minutes=t.overtime_50_minutes,
		overtime_100_minutes=t.overtime_100_minutes,
		night_shift_minutes=0,
		overtime_disposition=getattr(t, "overtime_disposition", None),
		overtime_parecer=getattr(t, "overtime_parecer", None),
		overtime_used=getattr(t, "overtime_used", None),
		justification=None,
		status="ok",
		created_at=t.created_at,
		updated_at=t.updated_at
	)


@router.post("/import", response_model=TimesheetImportResponse)
def import_timesheets(
	file: UploadFile = File(...),
	format: str = "csv",
	db: Session = Depends(get_db),
	user: User = Depends(require_role("admin", "rh"))
):
	if format == "csv":
		records = parse_csv(file.file)
	elif format == "json":
		records = parse_json(file.file)
	elif format == "pdf":
		records = parse_pdf(file.file)
	else:
		raise HTTPException(status_code=400, detail="Formato inválido")
	imported = 0
	failed = 0
	for rec in records:
		try:
			if isinstance(rec, dict) and "employee_id" in rec and "date" in rec:
				d = rec["date"]
				date_val = d if isinstance(d, date) else datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
				t = Timesheet(
					employee_id=int(rec["employee_id"]),
					date=date_val,
					total_minutes=int(rec.get("total_minutes", 0)),
					overtime_50_minutes=int(rec.get("overtime_50_minutes", 0)),
					overtime_100_minutes=int(rec.get("overtime_100_minutes", 0)),
					night_shift_minutes=int(rec.get("night_shift_minutes", 0))
				)
				db.add(t)
				imported += 1
		except Exception:
			failed += 1
	db.commit()
	fmt = TimesheetImportFormat.csv if format == "csv" else (TimesheetImportFormat.json if format == "json" else TimesheetImportFormat.pdf)
	imp = TimesheetImport(
		imported_by=user.id,
		filename=file.filename or "upload",
		format=fmt,
		records_imported=imported,
		records_failed=failed
	)
	db.add(imp)
	db.commit()
	db.refresh(imp)
	log_audit(db, user.id, "import_timesheets", "timesheet_import", imp.id, None, {"filename": file.filename}, "127.0.0.1")
	return TimesheetImportResponse(
		id=imp.id,
		imported_by=imp.imported_by,
		imported_by_name="",
		filename=imp.filename,
		format=imp.format.value,
		records_imported=imp.records_imported,
		records_failed=imp.records_failed,
		imported_at=imp.imported_at
	)

def _serializable(val):
	if val is None:
		return None
	if hasattr(val, "isoformat"):
		return val.isoformat()
	if hasattr(val, "value"):
		return val.value
	return val

@router.put("/{id}", response_model=TimesheetResponse)
def edit_timesheet(id: int, data: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
	t = db.query(Timesheet).filter(Timesheet.id == id).first()
	if not t:
		raise HTTPException(status_code=404, detail="Registro de ponto não encontrado")
	old_data = {k: _serializable(getattr(t, k, None)) for k in data.keys() if hasattr(t, k)}
	for key, value in data.items():
		if hasattr(t, key):
			setattr(t, key, value)
	db.commit()
	db.refresh(t)
	log_audit(db, user.id, "edit_timesheet", "timesheet", t.id, old_data, data, "127.0.0.1")
	emp = db.query(Employee).filter(Employee.id == t.employee_id).first()
	return TimesheetResponse(
		id=t.id,
		employee_id=t.employee_id,
		employee_name=emp.full_name if emp else "",
		date=t.date,
		clock_in=t.clock_in,
		clock_out=t.clock_out,
		clock_in_2=t.clock_in_2,
		clock_out_2=t.clock_out_2,
		total_minutes=t.total_minutes,
		overtime_50_minutes=t.overtime_50_minutes,
		overtime_100_minutes=t.overtime_100_minutes,
		night_shift_minutes=t.night_shift_minutes,
		overtime_disposition=getattr(t, "overtime_disposition", None),
		overtime_parecer=getattr(t, "overtime_parecer", None),
		overtime_used=getattr(t, "overtime_used", None),
		justification=t.justification,
		status=t.status.value,
		created_at=t.created_at,
		updated_at=t.updated_at
	)

@router.get("/inconsistencies", response_model=List[TimesheetResponse])
def list_inconsistencies(db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
	timesheets = db.query(Timesheet).filter(Timesheet.status == TimesheetStatus.inconsistente).all()
	emp_ids = list(set(t.employee_id for t in timesheets))
	emp_names = {e.id: e.full_name for e in db.query(Employee).filter(Employee.id.in_(emp_ids)).all()} if emp_ids else {}
	return [TimesheetResponse(
		id=t.id,
		employee_id=t.employee_id,
		employee_name=emp_names.get(t.employee_id, ""),
		date=t.date,
		clock_in=t.clock_in,
		clock_out=t.clock_out,
		clock_in_2=t.clock_in_2,
		clock_out_2=t.clock_out_2,
		total_minutes=t.total_minutes,
		overtime_50_minutes=t.overtime_50_minutes,
		overtime_100_minutes=t.overtime_100_minutes,
		night_shift_minutes=t.night_shift_minutes,
		overtime_disposition=getattr(t, "overtime_disposition", None),
		overtime_parecer=getattr(t, "overtime_parecer", None),
		overtime_used=getattr(t, "overtime_used", None),
		justification=t.justification,
		status=t.status.value,
		created_at=t.created_at,
		updated_at=t.updated_at
	) for t in timesheets]
