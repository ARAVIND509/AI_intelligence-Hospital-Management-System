from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "PATIENT"  # ADMIN, DOCTOR, RECEPTIONIST, PATIENT
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None


class UserLogin(BaseModel):
    username_or_email: str
    password: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
