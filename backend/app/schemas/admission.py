from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class WardBase(BaseModel):
    ward_name: str
    ward_type: str  # GENERAL, ICU, PRIVATE, SEMI_PRIVATE
    department_id: Optional[int] = None
    total_beds: int = 0


class WardCreate(WardBase):
    pass


class WardResponse(WardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BedBase(BaseModel):
    ward_id: int
    bed_number: str
    bed_type: str
    daily_rate: float = 0.0
    status: Optional[str] = "VACANT"  # VACANT, OCCUPIED, MAINTENANCE


class BedCreate(BedBase):
    pass


class BedResponse(BedBase):
    id: int
    ward_id: int
    bed_number: str
    bed_type: str
    daily_rate: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdmissionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    department_id: int
    bed_id: int
    admission_type: Optional[str] = "ELECTIVE"  # EMERGENCY, ELECTIVE, TRANSFER
    reason_for_admission: Optional[str] = None


class BedTransferRequest(BaseModel):
    to_bed_id: int
    reason: Optional[str] = None


class DischargeRequest(BaseModel):
    discharge_summary: str


class BedTransferLogResponse(BaseModel):
    id: int
    admission_id: int
    from_bed_id: int
    to_bed_id: int
    transfer_date: datetime
    reason: Optional[str] = None
    transferred_by_id: int

    model_config = ConfigDict(from_attributes=True)


class AdmissionResponse(BaseModel):
    id: int
    admission_number: str
    patient_id: int
    doctor_id: int
    department_id: int
    bed_id: int
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    admission_type: str
    status: str
    reason_for_admission: Optional[str] = None
    discharge_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    bed: Optional[BedResponse] = None
    transfer_logs: List[BedTransferLogResponse] = []

    model_config = ConfigDict(from_attributes=True)
