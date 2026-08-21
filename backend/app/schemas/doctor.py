from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==================================================
# DOCTOR BASE
# ==================================================

class DoctorBase(BaseModel):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    date_of_birth: date

    gender: str = Field(
        ...,
        min_length=1,
        max_length=20,
    )

    specialization: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )

    qualification: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    experience_years: int = Field(
        default=0,
        ge=0,
    )

    license_number: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    phone: str = Field(
        ...,
        min_length=5,
        max_length=20,
    )

    email: EmailStr | None = None

    address: str | None = None

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    consultation_fee: int | None = Field(
        default=None,
        ge=0,
    )


# ==================================================
# DOCTOR CREATE
# ==================================================

class DoctorCreate(DoctorBase):
    """
    Data required to register a new doctor.
    """

    user_id: int | None = None


# ==================================================
# DOCTOR UPDATE
# ==================================================

class DoctorUpdate(BaseModel):
    """
    Data allowed when updating an existing doctor.

    All fields are optional so partial updates
    are supported.
    """

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    date_of_birth: date | None = None

    gender: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    specialization: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    qualification: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    experience_years: int | None = Field(
        default=None,
        ge=0,
    )

    license_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        min_length=5,
        max_length=20,
    )

    email: EmailStr | None = None

    address: str | None = None

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    consultation_fee: int | None = Field(
        default=None,
        ge=0,
    )

    is_available: bool | None = None

    is_active: bool | None = None


# ==================================================
# DOCTOR RESPONSE
# ==================================================

class DoctorResponse(DoctorBase):
    """
    Complete doctor data returned by the API.
    """

    id: int

    doctor_id: str

    user_id: int | None = None

    is_available: bool

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==================================================
# DOCTOR LIST ITEM
# ==================================================

class DoctorListItem(BaseModel):
    """
    Lightweight doctor representation for lists.
    """

    id: int

    doctor_id: str

    first_name: str

    last_name: str

    specialization: str

    qualification: str

    experience_years: int

    department: str | None = None

    consultation_fee: int | None = None

    phone: str

    email: EmailStr | None = None

    is_available: bool

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==================================================
# DOCTOR LIST RESPONSE
# ==================================================

class DoctorListResponse(BaseModel):
    """
    Paginated doctor list response.
    """

    items: list[DoctorListItem]

    total: int

    page: int

    page_size: int

    total_pages: int


# ==================================================
# DOCTOR STATUS UPDATE
# ==================================================

class DoctorStatusUpdate(BaseModel):
    """
    Request schema for activating/deactivating
    a doctor.
    """

    is_active: bool


# ==================================================
# DOCTOR AVAILABILITY UPDATE
# ==================================================

class DoctorAvailabilityUpdate(BaseModel):
    """
    Request schema for changing doctor availability.
    """

    is_available: bool