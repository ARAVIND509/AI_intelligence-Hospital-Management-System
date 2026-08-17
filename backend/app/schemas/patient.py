from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --------------------------------------------------
# PATIENT BASE
# --------------------------------------------------

class PatientBase(BaseModel):
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

    blood_group: str | None = Field(
        default=None,
        max_length=10,
    )

    phone: str = Field(
        ...,
        min_length=5,
        max_length=20,
    )

    email: EmailStr | None = None

    address: str | None = None

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=255,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=20,
    )

    emergency_contact_relation: str | None = Field(
        default=None,
        max_length=100,
    )

    allergies: str | None = None

    chronic_conditions: str | None = None


# --------------------------------------------------
# PATIENT CREATE
# --------------------------------------------------

class PatientCreate(PatientBase):
    """
    Data required to register a new patient.
    """

    user_id: int | None = None


# --------------------------------------------------
# PATIENT UPDATE
# --------------------------------------------------

class PatientUpdate(BaseModel):
    """
    Data allowed when updating an existing patient.

    All fields are optional so partial updates are supported.
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

    blood_group: str | None = Field(
        default=None,
        max_length=10,
    )

    phone: str | None = Field(
        default=None,
        min_length=5,
        max_length=20,
    )

    email: EmailStr | None = None

    address: str | None = None

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=255,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=20,
    )

    emergency_contact_relation: str | None = Field(
        default=None,
        max_length=100,
    )

    allergies: str | None = None

    chronic_conditions: str | None = None

    is_active: bool | None = None


# --------------------------------------------------
# PATIENT RESPONSE
# --------------------------------------------------

class PatientResponse(PatientBase):
    """
    Patient data returned by the API.
    """

    id: int
    patient_id: str
    user_id: int | None = None

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


# --------------------------------------------------
# PATIENT LIST ITEM
# --------------------------------------------------

class PatientListItem(BaseModel):
    """
    Lightweight patient representation for patient lists.
    """

    id: int
    patient_id: str

    first_name: str
    last_name: str

    date_of_birth: date
    gender: str
    blood_group: str | None = None

    phone: str
    email: EmailStr | None = None

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


# --------------------------------------------------
# PATIENT LIST RESPONSE
# --------------------------------------------------

class PatientListResponse(BaseModel):
    """
    Paginated patient list response.
    """

    items: list[PatientListItem]

    total: int

    page: int

    page_size: int

    total_pages: int


# --------------------------------------------------
# PATIENT STATUS UPDATE
# --------------------------------------------------

class PatientStatusUpdate(BaseModel):
    """
    Request schema for activating/deactivating a patient.
    """

    is_active: bool