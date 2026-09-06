from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.patient import PatientResponse
from app.schemas.doctor import DoctorResponse


class PrescriptionMedicineBase(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = None


class PrescriptionMedicineCreate(PrescriptionMedicineBase):
    pass


class PrescriptionMedicineResponse(PrescriptionMedicineBase):
    id: int
    prescription_id: int

    model_config = ConfigDict(from_attributes=True)


class PrescriptionBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    medical_record_id: Optional[int] = None
    notes: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    medicines: List[PrescriptionMedicineCreate] = []


class PrescriptionUpdate(BaseModel):
    notes: Optional[str] = None
    medicines: Optional[List[PrescriptionMedicineCreate]] = None


class PrescriptionResponse(PrescriptionBase):
    id: int
    rx_id: str
    created_at: datetime
    updated_at: datetime
    patient: Optional[PatientResponse] = None
    doctor: Optional[DoctorResponse] = None
    medicines: List[PrescriptionMedicineResponse] = []

    model_config = ConfigDict(from_attributes=True)
