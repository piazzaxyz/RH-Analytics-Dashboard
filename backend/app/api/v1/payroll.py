from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.schemas.payroll import PayrollResponse
from app.models.payroll import Payroll, PayrollStatus
from app.models.employee import Employee, EmployeeStatus
from app.services.payroll_calculator import calculate_payroll
from app.services.audit_service import log_audit
from app.core.config import Settings
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/payroll", tags=["payroll"])
settings = Settings()

@router.get("/", response_model=List[PayrollResponse])
def list_payrolls(month: Optional[str] = None, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "gestor", "rh", "visualizador"))):
	query = db.query(Payroll)
	if month:
		query = query.filter(Payroll.reference_month == month)
	payrolls = query.order_by(Payroll.reference_month.desc()).limit(100).all()
	emp_ids = list(set(p.employee_id for p in payrolls))
	emp_names = {e.id: e.full_name for e in db.query(Employee).filter(Employee.id.in_(emp_ids)).all()} if emp_ids else {}
	return [PayrollResponse(id=p.id, employee_id=p.employee_id, employee_name=emp_names.get(p.employee_id, ""), reference_month=p.reference_month,
		base_salary=p.base_salary, overtime_50_value=p.overtime_50_value, overtime_100_value=p.overtime_100_value,
		night_additional_value=p.night_additional_value, dsr_value=p.dsr_value, bonus_value=p.bonus_value,
		hazard_pay=p.hazard_pay, unhealthy_pay=p.unhealthy_pay, gross_salary=p.gross_salary, inss_value=p.inss_value,
		irrf_value=p.irrf_value, vt_discount=p.vt_discount, vr_discount=p.vr_discount,
		health_plan_discount=p.health_plan_discount, loan_discount=p.loan_discount, absence_discount=p.absence_discount,
		alimony_discount=p.alimony_discount, other_discounts=p.other_discounts, net_salary=p.net_salary,
		status=p.status.value, processed_at=p.processed_at, created_at=p.created_at, updated_at=p.updated_at) for p in payrolls]

@router.post("/calculate/{employee_id}/{month}", response_model=PayrollResponse)
def calculate_individual_payroll(employee_id: int, month: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
	payroll = calculate_payroll(employee_id, month, db)
	db.add(payroll)
	db.commit()
	db.refresh(payroll)
	log_audit(db, user.id, "calculate_payroll", "payroll", payroll.id, None, {"month": month}, "127.0.0.1")
	return PayrollResponse(
		id=payroll.id,
		employee_id=payroll.employee_id,
		employee_name="",
		reference_month=payroll.reference_month,
		base_salary=payroll.base_salary,
		overtime_50_value=payroll.overtime_50_value,
		overtime_100_value=payroll.overtime_100_value,
		night_additional_value=payroll.night_additional_value,
		dsr_value=payroll.dsr_value,
		bonus_value=payroll.bonus_value,
		hazard_pay=payroll.hazard_pay,
		unhealthy_pay=payroll.unhealthy_pay,
		gross_salary=payroll.gross_salary,
		inss_value=payroll.inss_value,
		irrf_value=payroll.irrf_value,
		vt_discount=payroll.vt_discount,
		vr_discount=payroll.vr_discount,
		health_plan_discount=payroll.health_plan_discount,
		loan_discount=payroll.loan_discount,
		absence_discount=payroll.absence_discount,
		alimony_discount=payroll.alimony_discount,
		other_discounts=payroll.other_discounts,
		net_salary=payroll.net_salary,
		status=payroll.status.value,
		processed_at=payroll.processed_at,
		created_at=payroll.created_at,
		updated_at=payroll.updated_at
	)

@router.post("/calculate-batch/{month}", response_model=List[PayrollResponse])
def calculate_batch_payroll(month: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
	try:
		# Remove folhas existentes do mês para evitar duplicatas
		db.query(Payroll).filter(Payroll.reference_month == month).delete()
		db.commit()
	except Exception:
		db.rollback()
	employees = db.query(Employee).filter(Employee.status == EmployeeStatus.ativo).all()
	payrolls = []
	for e in employees:
		try:
			payroll = calculate_payroll(e.id, month, db)
			db.add(payroll)
			db.commit()
			db.refresh(payroll)
		except Exception as ex:
			db.rollback()
			raise HTTPException(status_code=500, detail=f"Erro ao processar folha do colaborador {e.id}: {str(ex)}")
		log_audit(db, user.id, "calculate_payroll", "payroll", payroll.id, None, {"month": month}, "127.0.0.1")
		payrolls.append(PayrollResponse(
			id=payroll.id,
			employee_id=payroll.employee_id,
			employee_name="",
			reference_month=payroll.reference_month,
			base_salary=payroll.base_salary,
			overtime_50_value=payroll.overtime_50_value,
			overtime_100_value=payroll.overtime_100_value,
			night_additional_value=payroll.night_additional_value,
			dsr_value=payroll.dsr_value,
			bonus_value=payroll.bonus_value,
			hazard_pay=payroll.hazard_pay,
			unhealthy_pay=payroll.unhealthy_pay,
			gross_salary=payroll.gross_salary,
			inss_value=payroll.inss_value,
			irrf_value=payroll.irrf_value,
			vt_discount=payroll.vt_discount,
			vr_discount=payroll.vr_discount,
			health_plan_discount=payroll.health_plan_discount,
			loan_discount=payroll.loan_discount,
			absence_discount=payroll.absence_discount,
			alimony_discount=payroll.alimony_discount,
			other_discounts=payroll.other_discounts,
			net_salary=payroll.net_salary,
			status=payroll.status.value,
			processed_at=payroll.processed_at,
			created_at=payroll.created_at,
			updated_at=payroll.updated_at
		))
	return payrolls

@router.get("/{employee_id}/{month}", response_model=PayrollResponse)
def get_payroll(employee_id: int, month: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "gestor", "rh", "visualizador"))):
	payroll = db.query(Payroll).filter(Payroll.employee_id == employee_id, Payroll.reference_month == month).first()
	if not payroll:
		raise HTTPException(status_code=404, detail="Folha não encontrada")
	return PayrollResponse(
		id=payroll.id,
		employee_id=payroll.employee_id,
		employee_name="",
		reference_month=payroll.reference_month,
		base_salary=payroll.base_salary,
		overtime_50_value=payroll.overtime_50_value,
		overtime_100_value=payroll.overtime_100_value,
		night_additional_value=payroll.night_additional_value,
		dsr_value=payroll.dsr_value,
		bonus_value=payroll.bonus_value,
		hazard_pay=payroll.hazard_pay,
		unhealthy_pay=payroll.unhealthy_pay,
		gross_salary=payroll.gross_salary,
		inss_value=payroll.inss_value,
		irrf_value=payroll.irrf_value,
		vt_discount=payroll.vt_discount,
		vr_discount=payroll.vr_discount,
		health_plan_discount=payroll.health_plan_discount,
		loan_discount=payroll.loan_discount,
		absence_discount=payroll.absence_discount,
		alimony_discount=payroll.alimony_discount,
		other_discounts=payroll.other_discounts,
		net_salary=payroll.net_salary,
		status=payroll.status.value,
		processed_at=payroll.processed_at,
		created_at=payroll.created_at,
		updated_at=payroll.updated_at
	)

@router.get("/summary/{month}", response_model=List[dict])
def payroll_summary(month: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "gestor", "rh", "visualizador"))):
	from app.models.department import Department
	summary = []
	departments = db.query(Department).all()
	for dept in departments:
		total = db.query(Payroll).filter(Payroll.reference_month == month, Payroll.employee_id.in_(
			db.query(Employee.id).filter(Employee.department_id == dept.id)
		)).with_entities(Payroll.gross_salary).all()
		total_gross = sum([t[0] for t in total])
		summary.append({
			"department_id": dept.id,
			"department_name": dept.name,
			"total_gross_salary": total_gross
		})
	return summary

@router.patch("/{id}/bonus", response_model=PayrollResponse)
def update_payroll_bonus(id: int, data: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
	from app.services.inss_calculator import calculate_inss
	from app.services.irrf_calculator import calculate_irrf
	payroll = db.query(Payroll).filter(Payroll.id == id).first()
	if not payroll:
		raise HTTPException(status_code=404, detail="Folha não encontrada")
	bonus = float(data.get("bonus_value", 0) or 0)
	payroll.bonus_value = bonus
	payroll.gross_salary = payroll.base_salary + payroll.overtime_50_value + payroll.overtime_100_value + payroll.night_additional_value + payroll.dsr_value + bonus + payroll.hazard_pay + payroll.unhealthy_pay
	payroll.inss_value = calculate_inss(payroll.gross_salary)
	payroll.irrf_value = calculate_irrf(payroll.gross_salary - payroll.inss_value, 0)
	payroll.net_salary = payroll.gross_salary - payroll.inss_value - payroll.irrf_value - payroll.vt_discount - payroll.vr_discount - payroll.health_plan_discount - payroll.loan_discount - payroll.absence_discount - payroll.alimony_discount - payroll.other_discounts
	db.commit()
	db.refresh(payroll)
	log_audit(db, user.id, "update_bonus", "payroll", payroll.id, None, {"bonus_value": bonus}, "127.0.0.1")
	return PayrollResponse(
		id=payroll.id,
		employee_id=payroll.employee_id,
		employee_name="",
		reference_month=payroll.reference_month,
		base_salary=payroll.base_salary,
		overtime_50_value=payroll.overtime_50_value,
		overtime_100_value=payroll.overtime_100_value,
		night_additional_value=payroll.night_additional_value,
		dsr_value=payroll.dsr_value,
		bonus_value=payroll.bonus_value,
		hazard_pay=payroll.hazard_pay,
		unhealthy_pay=payroll.unhealthy_pay,
		gross_salary=payroll.gross_salary,
		inss_value=payroll.inss_value,
		irrf_value=payroll.irrf_value,
		vt_discount=payroll.vt_discount,
		vr_discount=payroll.vr_discount,
		health_plan_discount=payroll.health_plan_discount,
		loan_discount=payroll.loan_discount,
		absence_discount=payroll.absence_discount,
		alimony_discount=payroll.alimony_discount,
		other_discounts=payroll.other_discounts,
		net_salary=payroll.net_salary,
		status=payroll.status.value,
		processed_at=payroll.processed_at,
		created_at=payroll.created_at,
		updated_at=payroll.updated_at
	)

@router.post("/{id}/approve", response_model=PayrollResponse)
def approve_payroll(id: int, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "rh"))):
	payroll = db.query(Payroll).filter(Payroll.id == id).first()
	if not payroll:
		raise HTTPException(status_code=404, detail="Folha não encontrada")
	payroll.status = PayrollStatus.processado
	db.commit()
	db.refresh(payroll)
	log_audit(db, user.id, "approve_payroll", "payroll", payroll.id, None, {"status": "processado"}, "127.0.0.1")
	return PayrollResponse(
		id=payroll.id,
		employee_id=payroll.employee_id,
		employee_name="",
		reference_month=payroll.reference_month,
		base_salary=payroll.base_salary,
		overtime_50_value=payroll.overtime_50_value,
		overtime_100_value=payroll.overtime_100_value,
		night_additional_value=payroll.night_additional_value,
		dsr_value=payroll.dsr_value,
		bonus_value=payroll.bonus_value,
		hazard_pay=payroll.hazard_pay,
		unhealthy_pay=payroll.unhealthy_pay,
		gross_salary=payroll.gross_salary,
		inss_value=payroll.inss_value,
		irrf_value=payroll.irrf_value,
		vt_discount=payroll.vt_discount,
		vr_discount=payroll.vr_discount,
		health_plan_discount=payroll.health_plan_discount,
		loan_discount=payroll.loan_discount,
		absence_discount=payroll.absence_discount,
		alimony_discount=payroll.alimony_discount,
		other_discounts=payroll.other_discounts,
		net_salary=payroll.net_salary,
		status=payroll.status.value,
		processed_at=payroll.processed_at,
		created_at=payroll.created_at,
		updated_at=payroll.updated_at
	)
