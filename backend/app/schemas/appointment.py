from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class PatientSummary(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class DoctorSummary(BaseModel):
    id: int
    name: str
    specialization: Optional[str] = None
    is_active: bool = True
    is_available: bool = True

    model_config = ConfigDict(from_attributes=True)


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class AppointmentReschedule(BaseModel):
    appointment_date: date
    appointment_time: time


class AppointmentResponse(BaseModel):
    id: int
    apt_id: str
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    patient: Optional[PatientSummary] = None
    doctor: Optional[DoctorSummary] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentPaginatedResponse(BaseModel):
    items: List[AppointmentResponse]
    total: int
    page: int
    limit: int
    pages: int
