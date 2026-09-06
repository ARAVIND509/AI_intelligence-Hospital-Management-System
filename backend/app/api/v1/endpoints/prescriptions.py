import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles, verify_patient_access
from app.services.prescription_service import prescription_service
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionResponse,
)
from app.models.user import User

router = APIRouter(
    prefix="/prescriptions",
    tags=["Prescriptions"]
)


@router.post(
    "/",
    summary="Create Prescription",
    status_code=status.HTTP_201_CREATED,
)
def create_prescription(
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR"]))
):
    rx = prescription_service.create_prescription(db, payload)
    return {
        "success": True,
        "message": "Prescription created successfully",
        "data": PrescriptionResponse.model_validate(rx).model_dump()
    }


@router.get(
    "/",
    summary="Get Prescriptions",
    status_code=status.HTTP_200_OK,
)
def get_prescriptions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR"]))
):
    items, total = prescription_service.get_prescriptions(
        db, page=page, limit=limit, patient_id=patient_id, doctor_id=doctor_id, search=search
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    serialized = [PrescriptionResponse.model_validate(r).model_dump() for r in items]
    return {
        "success": True,
        "message": "Prescriptions fetched successfully",
        "data": {
            "items": serialized,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    }


@router.get(
    "/{rx_id}",
    summary="Get Prescription by ID",
    status_code=status.HTTP_200_OK,
)
def get_prescription(
    rx_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rx = prescription_service.get_prescription_or_404(db, rx_id)
    verify_patient_access(current_user, rx.patient_id)
    return {
        "success": True,
        "message": "Prescription details fetched successfully",
        "data": PrescriptionResponse.model_validate(rx).model_dump()
    }


@router.get(
    "/patient/{patient_id}",
    summary="Get Patient Prescriptions History",
    status_code=status.HTTP_200_OK,
)
def get_patient_history(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_patient_access(current_user, patient_id)
    items = prescription_service.get_patient_history(db, patient_id)
    serialized = [PrescriptionResponse.model_validate(r).model_dump() for r in items]
    return {
        "success": True,
        "message": "Patient prescription history fetched successfully",
        "data": serialized
    }


@router.patch(
    "/{rx_id}",
    summary="Update Prescription",
    status_code=status.HTTP_200_OK,
)
def update_prescription(
    rx_id: str,
    payload: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR"]))
):
    rx = prescription_service.update_prescription(db, rx_id, payload)
    return {
        "success": True,
        "message": "Prescription updated successfully",
        "data": PrescriptionResponse.model_validate(rx).model_dump()
    }
