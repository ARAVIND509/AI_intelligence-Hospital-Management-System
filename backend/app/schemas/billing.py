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


class BillingBase(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    discount: float = 0.0
    tax: float = 0.0
    payment_method: Optional[str] = None


class BillingCreate(BillingBase):
    items: List[BillItemCreate] = []


class BillingUpdate(BaseModel):
    discount: Optional[float] = None
    tax: Optional[float] = None
    payment_status: Optional[str] = None  # unpaid, paid, cancelled
    payment_method: Optional[str] = None


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

    model_config = ConfigDict(from_attributes=True)
