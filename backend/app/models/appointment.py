from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    apt_id = Column(String(20), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="scheduled", nullable=False)
    appointment_type = Column(String(20), default="OP", nullable=False)  # OP, IP
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    medical_record = relationship("MedicalRecord", back_populates="appointment", uselist=False)
    prescription = relationship("Prescription", back_populates="appointment", uselist=False)
    bill = relationship("Billing", back_populates="appointment", uselist=False)