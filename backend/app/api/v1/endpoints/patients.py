import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.patient_service import patient_service
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    summary="Create Patient",
    status_code=status.HTTP_201_CREATED,
)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    patient = patient_service.create_patient(db, payload)
    return {
        "success": True,
        "message": "Patient created successfully",
        "data": PatientResponse.model_validate(patient).model_dump()
    }


@router.get(
    "/",
    summary="Get All Patients",
    status_code=status.HTTP_200_OK,
)
def get_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    items, total = patient_service.get_patients(db, page=page, limit=limit, is_active=is_active, search=search)
    pages = math.ceil(total / limit) if total > 0 else 1
    serialized = [PatientResponse.model_validate(p).model_dump() for p in items]
    return {
        "success": True,
        "message": "Patients fetched successfully",
        "data": {
            "items": serialized,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    }


@router.get(
    "/{patient_id}",
    summary="Get Patient by ID",
    status_code=status.HTTP_200_OK,
)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_service.get_patient_or_404(db, patient_id)
    return {
        "success": True,
        "message": "Patient found",
        "data": PatientResponse.model_validate(patient).model_dump()
    }


@router.patch(
    "/{patient_id}",
    summary="Update Patient",
    status_code=status.HTTP_200_OK,
)
def update_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    patient = patient_service.update_patient(db, patient_id, payload)
    return {
        "success": True,
        "message": "Patient updated successfully",
        "data": PatientResponse.model_validate(patient).model_dump()
    }


@router.delete(
    "/{patient_id}",
    summary="Deactivate Patient",
    status_code=status.HTTP_200_OK,
)
def deactivate_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_service.deactivate_patient(db, patient_id)
    return {
        "success": True,
        "message": "Patient deactivated successfully",
        "data": PatientResponse.model_validate(patient).model_dump()
    }