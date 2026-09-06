from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientResponse

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.get(
    "/",
    summary="Get All Patients",
    description="Returns a list of all registered patients.",
    status_code=status.HTTP_200_OK,
)
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    items = [PatientResponse.model_validate(p).model_dump() for p in patients]
    return {
        "success": True,
        "message": "Patients fetched successfully",
        "data": items
    }


@router.post(
    "/",
    summary="Create Patient",
    description="Creates a new patient record.",
    status_code=status.HTTP_201_CREATED,
)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        is_active=payload.is_active,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return {
        "success": True,
        "message": "Patient created successfully",
        "data": PatientResponse.model_validate(patient).model_dump()
    }


@router.get(
    "/{patient_id}",
    summary="Get Patient by ID",
    description="Returns details of a specific patient.",
    status_code=status.HTTP_200_OK,
)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    return {
        "success": True,
        "message": "Patient found",
        "data": PatientResponse.model_validate(patient).model_dump()
    }