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
    appointment_type: Optional[str] = "OP"  # OP, IP


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None  # scheduled, in_progress, completed, cancelled, rescheduled
    appointment_type: Optional[str] = None


class AppointmentReschedule(BaseModel):
    appointment_date: date
    appointment_time: time


class DoctorAvailabilityCheck(BaseModel):
    doctor_id: int
    date: date


class TimeSlot(BaseModel):
    time: time
    is_available: bool


class DoctorAvailabilityResponse(BaseModel):
    doctor_id: int
    date: date
    available_slots: List[TimeSlot]


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
    appointment_type: str = "OP"
    created_at: datetime
    updated_at: datetime
    patient: Optional[PatientResponse] = None
    doctor: Optional[DoctorResponse] = None

    model_config = ConfigDict(from_attributes=True)
