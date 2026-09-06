import logging
from datetime import datetime, timezone

logger = logging.getLogger("medimind.audit")
logger.setLevel(logging.INFO)


def log_audit_event(user_id: int | str, role: str, action: str, resource: str):
    timestamp = datetime.now(timezone.utc).isoformat()
    log_msg = f"[AUDIT] timestamp={timestamp} user_id={user_id} role={role} action={action} resource={resource}"
    logger.info(log_msg)
    print(log_msg)
