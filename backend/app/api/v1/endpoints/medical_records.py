import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.medical_record_service import medical_record_service
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
)

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"]
)


@router.post(
    "/",
    summary="Create Medical Record",
    status_code=status.HTTP_201_CREATED,
)
def create_record(payload: MedicalRecordCreate, db: Session = Depends(get_db)):
    rec = medical_record_service.create_record(db, payload)
    return {
        "success": True,
        "message": "Medical record created successfully",
        "data": MedicalRecordResponse.model_validate(rec).model_dump()
    }


@router.get(
    "/",
    summary="Get Medical Records",
    status_code=status.HTTP_200_OK,
)
def get_records(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    items, total = medical_record_service.get_records(
        db, page=page, limit=limit, patient_id=patient_id, doctor_id=doctor_id, search=search
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    serialized = [MedicalRecordResponse.model_validate(r).model_dump() for r in items]
    return {
        "success": True,
        "message": "Medical records fetched successfully",
        "data": {
            "items": serialized,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    }


@router.get(
    "/{record_id}",
    summary="Get Medical Record by ID",
    status_code=status.HTTP_200_OK,
)
def get_record(record_id: str, db: Session = Depends(get_db)):
    rec = medical_record_service.get_record_or_404(db, record_id)
    return {
        "success": True,
        "message": "Medical record details fetched successfully",
        "data": MedicalRecordResponse.model_validate(rec).model_dump()
    }


@router.get(
    "/patient/{patient_id}",
    summary="Get Patient Medical History",
    status_code=status.HTTP_200_OK,
)
def get_patient_history(patient_id: int, db: Session = Depends(get_db)):
    items = medical_record_service.get_patient_history(db, patient_id)
    serialized = [MedicalRecordResponse.model_validate(r).model_dump() for r in items]
    return {
        "success": True,
        "message": "Patient medical history fetched successfully",
        "data": serialized
    }


@router.patch(
    "/{record_id}",
    summary="Update Medical Record",
    status_code=status.HTTP_200_OK,
)
def update_record(record_id: str, payload: MedicalRecordUpdate, db: Session = Depends(get_db)):
    rec = medical_record_service.update_record(db, record_id, payload)
    return {
        "success": True,
        "message": "Medical record updated successfully",
        "data": MedicalRecordResponse.model_validate(rec).model_dump()
    }
