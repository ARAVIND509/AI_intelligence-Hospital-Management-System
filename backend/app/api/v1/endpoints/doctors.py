from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorResponse

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.get(
    "/",
    summary="Get All Doctors",
    description="Returns all registered doctors.",
    status_code=status.HTTP_200_OK,
)
def get_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    items = [DoctorResponse.model_validate(d).model_dump() for d in doctors]
    return {
        "success": True,
        "message": "Doctors fetched successfully",
        "data": items
    }


@router.post(
    "/",
    summary="Create Doctor",
    description="Creates a new doctor record.",
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    doctor = Doctor(
        name=payload.name,
        specialization=payload.specialization,
        is_active=payload.is_active,
        is_available=payload.is_available,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return {
        "success": True,
        "message": "Doctor created successfully",
        "data": DoctorResponse.model_validate(doctor).model_dump()
    }


@router.get(
    "/{doctor_id}",
    summary="Get Doctor by ID",
    description="Returns details of a specific doctor.",
    status_code=status.HTTP_200_OK,
)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found"
        )
    return {
        "success": True,
        "message": "Doctor found",
        "data": DoctorResponse.model_validate(doctor).model_dump()
    }