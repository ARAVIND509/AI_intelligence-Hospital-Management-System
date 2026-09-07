from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.patient import PatientResponse


class BillItemBase(BaseModel):
    item_name: str
    quantity: int = 1
    unit_price: float


class BillItemCreate(BillItemBase):
    pass


class BillItemResponse(BillItemBase):
    id: int
    bill_id: int
    total_price: float

    model_config = ConfigDict(from_attributes=True)


class PaymentTransactionCreate(BaseModel):
    amount: float
    payment_method: str  # cash, card, insurance, upi
    notes: Optional[str] = None


class RefundRequest(BaseModel):
    amount: float
    reason: str


class PaymentTransactionResponse(BaseModel):
    id: int
    bill_id: int
    transaction_number: str
    amount: float
    payment_method: str
    transaction_type: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillingBase(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    admission_id: Optional[int] = None
    pharmacy_dispense_id: Optional[int] = None
    lab_order_id: Optional[int] = None
    billing_type: Optional[str] = "CONSULTATION"  # CONSULTATION, LAB, PHARMACY, ADMISSION, COMPREHENSIVE
    discount: float = 0.0
    tax: float = 0.0
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class BillingCreate(BillingBase):
    items: List[BillItemCreate] = []


class BillingUpdate(BaseModel):
    discount: Optional[float] = None
    tax: Optional[float] = None
    payment_status: Optional[str] = None  # unpaid, paid, partially_paid, cancelled, refunded
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class BillingResponse(BillingBase):
    id: int
    bill_id: str
    total_amount: float
    net_amount: float
    payment_status: str
    created_at: datetime
    updated_at: datetime
    patient: Optional[PatientResponse] = None
    items: List[BillItemResponse] = []
    payments: List[PaymentTransactionResponse] = []

    model_config = ConfigDict(from_attributes=True)
