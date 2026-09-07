from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class LabTestCatalog(Base):
    __tablename__ = "lab_test_catalog"

    id = Column(Integer, primary_key=True, index=True)
    test_code = Column(String(50), unique=True, index=True, nullable=False)
    test_name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    description = Column(Text, nullable=True)
    cost = Column(Float, default=0.0, nullable=False)
    reference_range = Column(String(100), nullable=True)
    sample_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    department = relationship("Department")
    orders = relationship("LabOrder", back_populates="test_catalog")


class LabOrder(Base):
    __tablename__ = "lab_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(30), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    lab_test_id = Column(Integer, ForeignKey("lab_test_catalog.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    priority = Column(String(20), default="NORMAL", nullable=False)  # NORMAL, URGENT, EMERGENCY
    status = Column(String(30), default="ORDERED", nullable=False)  # ORDERED, SAMPLE_COLLECTED, IN_ANALYSIS, COMPLETED, CANCELLED
    sample_id = Column(String(50), nullable=True)
    sample_type = Column(String(50), nullable=True)
    sample_collected_at = Column(DateTime(timezone=True), nullable=True)
    collected_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    doctor_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient")
    doctor = relationship("Doctor")
    test_catalog = relationship("LabTestCatalog", back_populates="orders")
    collected_by = relationship("User", foreign_keys=[collected_by_id])
    results = relationship("LabResult", back_populates="lab_order", cascade="all, delete-orphan")


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    lab_order_id = Column(Integer, ForeignKey("lab_orders.id"), nullable=False)
    result_value = Column(String(255), nullable=False)
    reference_range = Column(String(100), nullable=True)
    is_abnormal = Column(Boolean, default=False, nullable=False)
    technician_notes = Column(Text, nullable=True)
    entered_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    doctor_review_status = Column(String(20), default="PENDING", nullable=False)  # PENDING, REVIEWED
    doctor_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by_doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    lab_order = relationship("LabOrder", back_populates="results")
    entered_by = relationship("User", foreign_keys=[entered_by_id])
    reviewed_by_doctor = relationship("Doctor", foreign_keys=[reviewed_by_doctor_id])
