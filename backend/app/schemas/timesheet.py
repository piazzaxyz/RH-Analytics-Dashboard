from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, date, time

class TimesheetResponse(BaseModel):
	id: int
	employee_id: int
	employee_name: str
	date: date
	clock_in: Optional[time]
	clock_out: Optional[time]
	clock_in_2: Optional[time]
	clock_out_2: Optional[time]
	total_minutes: int
	overtime_50_minutes: int
	overtime_100_minutes: int
	night_shift_minutes: int
	overtime_disposition: Optional[str] = None
	overtime_parecer: Optional[str] = None
	overtime_used: Optional[int] = None
	justification: Optional[str] = None
	status: Literal["ok", "inconsistente", "justificado"]
	created_at: datetime
	updated_at: datetime

class TimesheetImportResponse(BaseModel):
	id: int
	imported_by: int
	imported_by_name: str
	filename: str
	format: Literal["csv", "json", "pdf"]
	records_imported: int
	records_failed: int
	imported_at: datetime
