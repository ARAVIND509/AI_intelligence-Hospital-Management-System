from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.patient import PatientResponse
from app.schemas.doctor import DoctorResponse


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
    patient: Optional[PatientResponse] = None
    doctor: Optional[DoctorResponse] = None

    model_config = ConfigDict(from_attributes=True)
