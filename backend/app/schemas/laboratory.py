from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# Catalog Schemas
class LabTestCatalogBase(BaseModel):
    test_code: str
    test_name: str
    department_id: Optional[int] = None
    description: Optional[str] = None
    cost: float = 0.0
    reference_range: Optional[str] = None
    sample_type: Optional[str] = None


class LabTestCatalogCreate(LabTestCatalogBase):
    pass


class LabTestCatalogUpdate(BaseModel):
    test_name: Optional[str] = None
    department_id: Optional[int] = None
    description: Optional[str] = None
    cost: Optional[float] = None
    reference_range: Optional[str] = None
    sample_type: Optional[str] = None


class LabTestCatalogResponse(LabTestCatalogBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Order Schemas
class LabOrderCreate(BaseModel):
    patient_id: int
    doctor_id: int
    lab_test_id: int
    appointment_id: Optional[int] = None
    priority: Optional[str] = "NORMAL"  # NORMAL, URGENT, EMERGENCY
    doctor_notes: Optional[str] = None


class SampleCollectRequest(BaseModel):
    sample_id: str
    sample_type: Optional[str] = None


class LabResultCreate(BaseModel):
    result_value: str
    reference_range: Optional[str] = None
    is_abnormal: bool = False
    technician_notes: Optional[str] = None


class DoctorResultReviewRequest(BaseModel):
    doctor_notes: Optional[str] = None


class LabResultResponse(BaseModel):
    id: int
    lab_order_id: int
    result_value: str
    reference_range: Optional[str] = None
    is_abnormal: bool
    technician_notes: Optional[str] = None
    entered_by_id: int
    entered_at: datetime
    doctor_review_status: str
    doctor_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by_doctor_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LabOrderResponse(BaseModel):
    id: int
    order_number: str
    patient_id: int
    doctor_id: int
    lab_test_id: int
    appointment_id: Optional[int] = None
    priority: str
    status: str
    sample_id: Optional[str] = None
    sample_type: Optional[str] = None
    sample_collected_at: Optional[datetime] = None
    collected_by_id: Optional[int] = None
    doctor_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    test_catalog: Optional[LabTestCatalogResponse] = None
    results: List[LabResultResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PatientLabReport(BaseModel):
    patient_id: int
    patient_name: str
    total_orders: int
    completed_orders: int
    orders: List[LabOrderResponse]
