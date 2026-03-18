from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TimesheetStatus(enum.Enum):
	ok = "ok"
	inconsistente = "inconsistente"
	justificado = "justificado"

class Timesheet(Base):
	__tablename__ = "timesheets"

	id = Column(Integer, primary_key=True, autoincrement=True)
	employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
	date = Column(Date, nullable=False)
	clock_in = Column(Time, nullable=True)
	clock_out = Column(Time, nullable=True)
	clock_in_2 = Column(Time, nullable=True)
	clock_out_2 = Column(Time, nullable=True)
	total_minutes = Column(Integer, nullable=False, default=0)
	overtime_50_minutes = Column(Integer, nullable=False, default=0)
	overtime_100_minutes = Column(Integer, nullable=False, default=0)
	night_shift_minutes = Column(Integer, nullable=False, default=0)
	overtime_disposition = Column(String(20), nullable=True)
	overtime_parecer = Column(String(500), nullable=True)
	overtime_used = Column(Integer, nullable=True)
	justification = Column(String(255), nullable=True)
	status = Column(Enum(TimesheetStatus), nullable=False, default=TimesheetStatus.ok)
	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
	updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

	employee = relationship("Employee")
