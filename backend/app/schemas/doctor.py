from typing import Optional
from pydantic import BaseModel, ConfigDict


class DoctorCreate(BaseModel):
    name: str
    specialization: Optional[str] = None
    is_active: bool = True
    is_available: bool = True


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: Optional[str] = None
    is_active: bool = True
    is_available: bool = True

    model_config = ConfigDict(from_attributes=True)
