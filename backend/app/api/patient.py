from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.patient import (
    PatientCreate,
    PatientListItem,
    PatientListResponse,
    PatientResponse,
    PatientStatusUpdate,
    PatientUpdate,
)
from app.services.patient_service import (
    create_patient,
    delete_patient,
    get_patient_by_id,
    get_patient_by_patient_id,
    get_patients,
    update_patient,
    update_patient_status,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


# --------------------------------------------------
# CREATE PATIENT
# --------------------------------------------------

@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):
    """
    Register a new patient.

    Allowed roles:
    - admin
    - doctor
    - nurse
    - receptionist
    """

    if patient_data.user_id is not None:
        existing_patient = (
            db.query(PatientResponse)
        )

    try:
        return create_patient(
            db,
            patient_data,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# --------------------------------------------------
# LIST PATIENTS
# --------------------------------------------------

@router.get(
    "/",
    response_model=PatientListResponse,
)
def list_patients(
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
    is_active: bool | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a paginated list of patients.
    """

    patients, total = get_patients(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
    )

    total_pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return PatientListResponse(
        items=patients,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# --------------------------------------------------
# GET PATIENT BY DATABASE ID
# --------------------------------------------------

@router.get(
    "/id/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a patient using the database ID.
    """

    patient = get_patient_by_id(
        db,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


# --------------------------------------------------
# GET PATIENT BY HOSPITAL PATIENT ID
# --------------------------------------------------

@router.get(
    "/patient-id/{patient_identifier}",
    response_model=PatientResponse,
)
def get_patient_by_identifier(
    patient_identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a patient using the hospital patient ID.

    Example:
        PT-000001
    """

    patient = get_patient_by_patient_id(
        db,
        patient_identifier,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


# --------------------------------------------------
# UPDATE PATIENT
# --------------------------------------------------

@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
def update_patient_details(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):
    """
    Update patient information.
    """

    patient = get_patient_by_id(
        db,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return update_patient(
        db,
        patient,
        patient_data,
    )


# --------------------------------------------------
# UPDATE PATIENT STATUS
# --------------------------------------------------

@router.patch(
    "/{patient_id}/status",
    response_model=PatientResponse,
)
def change_patient_status(
    patient_id: int,
    status_data: PatientStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
        )
    ),
):
    """
    Activate or deactivate a patient.
    """

    patient = get_patient_by_id(
        db,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return update_patient_status(
        db,
        patient,
        status_data.is_active,
    )


# --------------------------------------------------
# DELETE PATIENT
# --------------------------------------------------

@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    ),
):
    """
    Permanently delete a patient.

    Restricted to administrators.
    """

    patient = get_patient_by_id(
        db,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    delete_patient(
        db,
        patient,
    )

    return None