from app.services.inss_calculator import calculate_inss
from app.services.irrf_calculator import calculate_irrf
from app.models.payroll import Payroll, PayrollStatus
from app.models.timesheet import Timesheet, TimesheetStatus
from app.models.employee import Employee
from app.models.loan import Loan
from app.models.loan_installment import LoanInstallment, LoanInstallmentStatus
from sqlalchemy.orm import Session
from datetime import datetime

def calculate_payroll(employee_id: int, month: str, db: Session):
	employee = db.query(Employee).filter(Employee.id == employee_id).first()
	if not employee:
		raise ValueError(f"Colaborador {employee_id} não encontrado")
	timesheets = db.query(Timesheet).filter(Timesheet.employee_id == employee_id, Timesheet.date.like(f"{month}-%")).all()
	base_salary = float(employee.salary or 0)
	overtime_50 = 0.0
	overtime_100 = 0.0
	night_additional = 0.0
	dsr = 0.0
	bonus = 0.0
	hazard_pay = 0.0
	unhealthy_pay = 0.0
	total_minutes = 0
	overtime_50_minutes = 0
	overtime_100_minutes = 0
	night_shift_minutes = 0
	days_worked = 0
	domingos_feriados = 0
	for t in timesheets:
		total_minutes += (t.total_minutes or 0)
		overtime_50_minutes += (t.overtime_50_minutes or 0)
		overtime_100_minutes += (t.overtime_100_minutes or 0)
		night_shift_minutes += (t.night_shift_minutes or 0)
		if t.status == TimesheetStatus.ok or (hasattr(t.status, 'value') and t.status.value == 'ok'):
			days_worked += 1
		if t.date and t.date.weekday() == 6:
			domingos_feriados += 1
	overtime_50 = (base_salary / 220) * 1.5 * (overtime_50_minutes / 60) if base_salary else 0
	overtime_100 = (base_salary / 220) * 2.0 * (overtime_100_minutes / 60) if base_salary else 0
	night_additional = (base_salary / 220) * 0.2 * (night_shift_minutes / 60) if base_salary else 0
	dsr = ((overtime_50 + overtime_100) / days_worked) * domingos_feriados if days_worked else 0
	gross_salary = base_salary + overtime_50 + overtime_100 + night_additional + dsr + bonus + hazard_pay + unhealthy_pay
	inss_value = calculate_inss(gross_salary)
	dependents = 0
	irrf_value = calculate_irrf(gross_salary - inss_value, dependents)
	# Descontos
	vt_discount = 0.0
	vr_discount = 0.0
	health_plan_discount = 0.0
	loan_ids = [l.id for l in db.query(Loan).filter(Loan.employee_id == employee_id).all()]
	loan_discount = sum([li.amount for li in db.query(LoanInstallment).filter(
		LoanInstallment.loan_id.in_(loan_ids),
		LoanInstallment.due_month == month,
		LoanInstallment.status == LoanInstallmentStatus.pendente
	).all()]) if loan_ids else 0
	absence_discount = 0.0
	alimony_discount = 0.0
	other_discounts = 0.0
	net_salary = gross_salary - inss_value - irrf_value - vt_discount - vr_discount - health_plan_discount - loan_discount - absence_discount - alimony_discount - other_discounts
	payroll = Payroll(
		employee_id=employee_id,
		reference_month=month,
		base_salary=base_salary,
		overtime_50_value=overtime_50,
		overtime_100_value=overtime_100,
		night_additional_value=night_additional,
		dsr_value=dsr,
		bonus_value=bonus,
		hazard_pay=hazard_pay,
		unhealthy_pay=unhealthy_pay,
		gross_salary=gross_salary,
		inss_value=inss_value,
		irrf_value=irrf_value,
		vt_discount=vt_discount,
		vr_discount=vr_discount,
		health_plan_discount=health_plan_discount,
		loan_discount=loan_discount,
		absence_discount=absence_discount,
		alimony_discount=alimony_discount,
		other_discounts=other_discounts,
		net_salary=net_salary,
		status=PayrollStatus.rascunho,
		processed_at=None
	)
	return payroll
