from app.models.audit import AuditLog
from sqlalchemy.orm import Session
from typing import Optional, Any
import json
from datetime import date, datetime, time

def _to_json_safe(obj: Any) -> Any:
	if obj is None:
		return None
	if isinstance(obj, (date, datetime, time)):
		return obj.isoformat()
	if hasattr(obj, "value") and not isinstance(obj, (bool, int, str, float)):
		return obj.value
	if isinstance(obj, dict):
		return {str(k): _to_json_safe(v) for k, v in obj.items()}
	if isinstance(obj, (list, tuple)):
		return [_to_json_safe(v) for v in obj]
	if isinstance(obj, (str, int, float, bool)):
		return obj
	return str(obj)

def log_audit(db: Session, user_id: int, action: str, entity: str, entity_id: int, old_value: Optional[dict], new_value: Optional[dict], ip_address: str):
	old_str = json.dumps(_to_json_safe(old_value)) if old_value else None
	new_str = json.dumps(_to_json_safe(new_value)) if new_value else None
	audit = AuditLog(
		user_id=user_id,
		action=action,
		entity=entity,
		entity_id=entity_id,
		old_value=old_str,
		new_value=new_str,
		ip_address=ip_address
	)
	db.add(audit)
	db.commit()
