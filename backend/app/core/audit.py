import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.core.database import SessionLocal

logger = logging.getLogger("medimind.audit")
logger.setLevel(logging.INFO)


def log_audit_event(
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    role: Optional[str] = None,
    action: str = "UNKNOWN_ACTION",
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status_code: Optional[int] = 200,
    details: Optional[str] = None,
    db: Optional[Session] = None,
):
    timestamp = datetime.now(timezone.utc).isoformat()
    log_msg = (
        f"[AUDIT LOG] {timestamp} | User: {username or 'Anonymous'} (ID: {user_id or 'N/A'}, Role: {role or 'N/A'}) | "
        f"Action: {action} | Resource: {resource_type or 'General'}:{resource_id or 'N/A'} | IP: {ip_address or '127.0.0.1'} | Status: {status_code}"
    )
    logger.info(log_msg)

    # Persist to database
    close_db_session = False
    if db is None:
        db = SessionLocal()
        close_db_session = True

    try:
        audit_entry = AuditLog(
            user_id=user_id,
            username=username,
            role=role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status_code=status_code,
            details=details,
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to persist audit log entry to database: {e}")
    finally:
        if close_db_session:
            db.close()
