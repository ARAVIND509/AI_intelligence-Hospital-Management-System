from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class MedicineInventory(Base):
    __tablename__ = "medicine_inventory"

    id = Column(Integer, primary_key=True, index=True)
    medicine_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), index=True, nullable=False)
    category = Column(String(100), nullable=False)
    unit_price = Column(Float, default=0.0, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=10, nullable=False)
    expiry_date = Column(Date, nullable=True)
    manufacturer = Column(String(150), nullable=True)
    location_rack = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    dispense_items = relationship("PharmacyDispenseItem", back_populates="medicine")
    inventory_logs = relationship("InventoryLog", back_populates="medicine")


class PharmacyDispense(Base):
    __tablename__ = "pharmacy_dispenses"

    id = Column(Integer, primary_key=True, index=True)
    dispense_number = Column(String(30), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    dispensed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(30), default="DISPENSED", nullable=False)  # PENDING, DISPENSED, CANCELLED
    total_amount = Column(Float, default=0.0, nullable=False)
    dispensed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient")
    prescription = relationship("Prescription")
    dispensed_by = relationship("User", foreign_keys=[dispensed_by_id])
    items = relationship("PharmacyDispenseItem", back_populates="dispense", cascade="all, delete-orphan")


class PharmacyDispenseItem(Base):
    __tablename__ = "pharmacy_dispense_items"

    id = Column(Integer, primary_key=True, index=True)
    dispense_id = Column(Integer, ForeignKey("pharmacy_dispenses.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicine_inventory.id"), nullable=False)
    medicine_name = Column(String(150), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    dispense = relationship("PharmacyDispense", back_populates="items")
    medicine = relationship("MedicineInventory", back_populates="dispense_items")


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicine_inventory.id"), nullable=False)
    change_type = Column(String(30), nullable=False)  # DISPENSED, RESTOCKED, ADJUSTMENT
    quantity_change = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    medicine = relationship("MedicineInventory", back_populates="inventory_logs")
    performed_by = relationship("User", foreign_keys=[performed_by_id])
