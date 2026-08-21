from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.doctor import (
    DoctorAvailabilityUpdate,
    DoctorCreate,
    DoctorListResponse,
    DoctorResponse,
    DoctorStatusUpdate,
    DoctorUpdate,
)
from app.services.doctor_service import (
    create_doctor,
    delete_doctor,
    get_doctor_by_doctor_id,
    get_doctor_by_id,
    get_doctor_by_user_id,
    get_doctors,
    update_doctor,
    update_doctor_availability,
    update_doctor_status,
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


# ==================================================
# CREATE DOCTOR
# ==================================================

@router.post(
    "/",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    ),
):
    """
    Register a new doctor.

    Only administrators can register doctors.
    """

    # Check whether the user account is already
    # linked to another doctor.
    if doctor_data.user_id is not None:
        existing_doctor = get_doctor_by_user_id(
            db,
            doctor_data.user_id,
        )

        if existing_doctor is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This user account is already "
                    "linked to a doctor"
                ),
            )

    try:
        return create_doctor(
            db,
            doctor_data,
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==================================================
# LIST DOCTORS
# ==================================================

@router.get(
    "/",
    response_model=DoctorListResponse,
)
def list_doctors(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    specialization: str | None = Query(
        default=None,
        max_length=150,
    ),
    department: str | None = Query(
        default=None,
        max_length=150,
    ),
    is_available: bool | None = Query(
        default=None,
    ),
    is_active: bool | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get a paginated list of doctors.
    """

    doctors, total = get_doctors(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        specialization=specialization,
        department=department,
        is_available=is_available,
        is_active=is_active,
    )

    total_pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return DoctorListResponse(
        items=doctors,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ==================================================
# GET DOCTOR BY DATABASE ID
# ==================================================

@router.get(
    "/id/{doctor_id}",
    response_model=DoctorResponse,
)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get a doctor using the database ID.
    """

    doctor = get_doctor_by_id(
        db,
        doctor_id,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return doctor


# ==================================================
# GET DOCTOR BY HOSPITAL DOCTOR ID
# ==================================================

@router.get(
    "/doctor-id/{doctor_identifier}",
    response_model=DoctorResponse,
)
def get_doctor_by_identifier(
    doctor_identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get a doctor using the hospital doctor ID.

    Example:
        DR-000001
    """

    doctor = get_doctor_by_doctor_id(
        db,
        doctor_identifier,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return doctor


# ==================================================
# UPDATE DOCTOR
# ==================================================

@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
def update_doctor_details(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "admin",
        )
    ),
):
    """
    Update doctor information.

    Only administrators can update doctor
    information.
    """

    doctor = get_doctor_by_id(
        db,
        doctor_id,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return update_doctor(
        db,
        doctor,
        doctor_data,
    )


# ==================================================
# UPDATE DOCTOR STATUS
# ==================================================

@router.patch(
    "/{doctor_id}/status",
    response_model=DoctorResponse,
)
def change_doctor_status(
    doctor_id: int,
    status_data: DoctorStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "admin",
        )
    ),
):
    """
    Activate or deactivate a doctor.
    """

    doctor = get_doctor_by_id(
        db,
        doctor_id,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return update_doctor_status(
        db,
        doctor,
        status_data.is_active,
    )


# ==================================================
# UPDATE DOCTOR AVAILABILITY
# ==================================================

@router.patch(
    "/{doctor_id}/availability",
    response_model=DoctorResponse,
)
def change_doctor_availability(
    doctor_id: int,
    availability_data: DoctorAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "admin",
            "doctor",
        )
    ),
):
    """
    Mark a doctor as available or unavailable.
    """

    doctor = get_doctor_by_id(
        db,
        doctor_id,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return update_doctor_availability(
        db,
        doctor,
        availability_data.is_available,
    )


# ==================================================
# DELETE DOCTOR
# ==================================================

@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    ),
):
    """
    Permanently delete a doctor.

    Restricted to administrators.
    """

    doctor = get_doctor_by_id(
        db,
        doctor_id,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    delete_doctor(
        db,
        doctor,
    )

    return None