import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.doctor_service import doctor_service
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post(
    "/",
    summary="Create Doctor",
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    doctor = doctor_service.create_doctor(db, payload)
    return {
        "success": True,
        "message": "Doctor created successfully",
        "data": DoctorResponse.model_validate(doctor).model_dump()
    }


@router.get(
    "/",
    summary="Get All Doctors",
    status_code=status.HTTP_200_OK,
)
def get_doctors(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    department_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_available: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    items, total = doctor_service.get_doctors(
        db,
        page=page,
        limit=limit,
        department_id=department_id,
        is_active=is_active,
        is_available=is_available,
        search=search
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    serialized = [DoctorResponse.model_validate(d).model_dump() for d in items]
    return {
        "success": True,
        "message": "Doctors fetched successfully",
        "data": {
            "items": serialized,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    }


@router.get(
    "/{doctor_id}",
    summary="Get Doctor by ID",
    status_code=status.HTTP_200_OK,
)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = doctor_service.get_doctor_or_404(db, doctor_id)
    return {
        "success": True,
        "message": "Doctor found",
        "data": DoctorResponse.model_validate(doctor).model_dump()
    }


@router.patch(
    "/{doctor_id}",
    summary="Update Doctor",
    status_code=status.HTTP_200_OK,
)
def update_doctor(doctor_id: int, payload: DoctorUpdate, db: Session = Depends(get_db)):
    doctor = doctor_service.update_doctor(db, doctor_id, payload)
    return {
        "success": True,
        "message": "Doctor updated successfully",
        "data": DoctorResponse.model_validate(doctor).model_dump()
    }


@router.delete(
    "/{doctor_id}",
    summary="Deactivate Doctor",
    status_code=status.HTTP_200_OK,
)
def deactivate_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = doctor_service.deactivate_doctor(db, doctor_id)
    return {
        "success": True,
        "message": "Doctor deactivated successfully",
        "data": DoctorResponse.model_validate(doctor).model_dump()
    }