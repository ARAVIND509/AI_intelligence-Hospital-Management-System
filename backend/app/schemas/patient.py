from typing import Optional
from pydantic import BaseModel, ConfigDict


class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    is_active: bool = True


class PatientResponse(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
