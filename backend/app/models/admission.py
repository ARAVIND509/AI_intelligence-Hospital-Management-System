from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    ward_name = Column(String(100), unique=True, index=True, nullable=False)
    ward_type = Column(String(50), nullable=False)  # GENERAL, ICU, PRIVATE, SEMI_PRIVATE
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    total_beds = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    department = relationship("Department")
    beds = relationship("Bed", back_populates="ward", cascade="all, delete-orphan")


class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=False)
    bed_number = Column(String(30), nullable=False)
    bed_type = Column(String(50), nullable=False)  # GENERAL, ICU, PRIVATE, SEMI_PRIVATE
    daily_rate = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="VACANT", nullable=False)  # VACANT, OCCUPIED, MAINTENANCE
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    ward = relationship("Ward", back_populates="beds")
    admissions = relationship("Admission", back_populates="bed")


class Admission(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True, index=True)
    admission_number = Column(String(30), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)
    admission_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    discharge_date = Column(DateTime(timezone=True), nullable=True)
    admission_type = Column(String(30), default="ELECTIVE", nullable=False)  # EMERGENCY, ELECTIVE, TRANSFER
    status = Column(String(30), default="ADMITTED", nullable=False)  # ADMITTED, DISCHARGED, TRANSFERRED
    reason_for_admission = Column(Text, nullable=True)
    discharge_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient")
    doctor = relationship("Doctor")
    department = relationship("Department")
    bed = relationship("Bed", back_populates="admissions")
    transfer_logs = relationship("BedTransferLog", back_populates="admission", cascade="all, delete-orphan")


class BedTransferLog(Base):
    __tablename__ = "bed_transfer_logs"

    id = Column(Integer, primary_key=True, index=True)
    admission_id = Column(Integer, ForeignKey("admissions.id"), nullable=False)
    from_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)
    to_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)
    transfer_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    reason = Column(Text, nullable=True)
    transferred_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    admission = relationship("Admission", back_populates="transfer_logs")
    from_bed = relationship("Bed", foreign_keys=[from_bed_id])
    to_bed = relationship("Bed", foreign_keys=[to_bed_id])
    transferred_by = relationship("User", foreign_keys=[transferred_by_id])
