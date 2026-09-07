from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Billing(Base):
    __tablename__ = "billings"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(String(20), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    admission_id = Column(Integer, ForeignKey("admissions.id"), nullable=True)
    pharmacy_dispense_id = Column(Integer, ForeignKey("pharmacy_dispenses.id"), nullable=True)
    lab_order_id = Column(Integer, ForeignKey("lab_orders.id"), nullable=True)
    billing_type = Column(String(30), default="CONSULTATION", nullable=False)  # CONSULTATION, LAB, PHARMACY, ADMISSION, COMPREHENSIVE
    total_amount = Column(Float, default=0.0, nullable=False)
    discount = Column(Float, default=0.0, nullable=False)
    tax = Column(Float, default=0.0, nullable=False)
    net_amount = Column(Float, default=0.0, nullable=False)
    payment_status = Column(String(20), default="unpaid", nullable=False)  # unpaid, paid, partially_paid, cancelled, refunded
    payment_method = Column(String(50), nullable=True)  # cash, card, insurance, upi
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="bills")
    appointment = relationship("Appointment", back_populates="bill")
    admission = relationship("Admission")
    pharmacy_dispense = relationship("PharmacyDispense")
    lab_order = relationship("LabOrder")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    payments = relationship("PaymentTransaction", back_populates="bill", cascade="all, delete-orphan")


class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("billings.id"), nullable=False)
    item_name = Column(String(150), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    bill = relationship("Billing", back_populates="items")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("billings.id"), nullable=False)
    transaction_number = Column(String(30), unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, card, insurance, upi
    transaction_type = Column(String(20), default="PAYMENT", nullable=False)  # PAYMENT, REFUND
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    bill = relationship("Billing", back_populates="payments")
