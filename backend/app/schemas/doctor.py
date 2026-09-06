from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.department import DepartmentResponse


class DoctorBase(BaseModel):
    name: str
    specialization: Optional[str] = None
    department_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    working_days: str = "Monday,Tuesday,Wednesday,Thursday,Friday"
    working_hours_start: time = time(9, 0)
    working_hours_end: time = time(17, 0)
    is_active: bool = True
    is_available: bool = True


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    department_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    working_days: Optional[str] = None
    working_hours_start: Optional[time] = None
    working_hours_end: Optional[time] = None
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None


class DoctorResponse(DoctorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentResponse] = None

    model_config = ConfigDict(from_attributes=True)
