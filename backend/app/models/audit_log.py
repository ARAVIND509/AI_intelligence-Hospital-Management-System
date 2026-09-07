from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    username = Column(String(100), nullable=True, index=True)
    role = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # e.g. LOGIN, CREATE_PATIENT, DISPENSE_MEDICINE, DISCHARGE_PATIENT
    resource_type = Column(String(50), nullable=True)  # PATIENT, APPOINTMENT, PHARMACY, LAB, BILLING, ADMISSION
    resource_id = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    status_code = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
