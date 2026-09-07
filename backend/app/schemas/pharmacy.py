from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class MedicineInventoryBase(BaseModel):
    medicine_code: str
    name: str
    category: str
    unit_price: float
    stock_quantity: int
    reorder_level: int = 10
    expiry_date: Optional[date] = None
    manufacturer: Optional[str] = None
    location_rack: Optional[str] = None


class MedicineInventoryCreate(MedicineInventoryBase):
    pass


class MedicineInventoryUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    reorder_level: Optional[int] = None
    expiry_date: Optional[date] = None
    manufacturer: Optional[str] = None
    location_rack: Optional[str] = None


class MedicineInventoryResponse(MedicineInventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DispenseItemCreate(BaseModel):
    medicine_id: int
    quantity: int


class PharmacyDispenseCreate(BaseModel):
    patient_id: int
    prescription_id: Optional[int] = None
    notes: Optional[str] = None
    items: List[DispenseItemCreate]


class PharmacyDispenseItemResponse(BaseModel):
    id: int
    dispense_id: int
    medicine_id: int
    medicine_name: str
    quantity: int
    unit_price: float
    total_price: float

    model_config = ConfigDict(from_attributes=True)


class PharmacyDispenseResponse(BaseModel):
    id: int
    dispense_number: str
    patient_id: int
    prescription_id: Optional[int] = None
    dispensed_by_id: int
    status: str
    total_amount: float
    dispensed_at: datetime
    notes: Optional[str] = None
    created_at: datetime
    items: List[PharmacyDispenseItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class InventoryLogResponse(BaseModel):
    id: int
    medicine_id: int
    change_type: str
    quantity_change: int
    previous_quantity: int
    new_quantity: int
    performed_by_id: int
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
