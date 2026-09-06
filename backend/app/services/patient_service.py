from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.patient_repository import patient_repository
from app.schemas.patient import PatientCreate, PatientUpdate
from app.models.patient import Patient


class PatientService:
    def get_patient_or_404(self, db: Session, patient_id: int) -> Patient:
        patient = patient_repository.get(db, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        return patient

    def create_patient(self, db: Session, payload: PatientCreate) -> Patient:
        if payload.email:
            existing = patient_repository.get_by_email(db, payload.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Patient with email '{payload.email}' already exists"
                )
        return patient_repository.create(db, obj_in=payload)

    def get_patients(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ):
        skip = (page - 1) * limit
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active

        items, total = patient_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            search_query=search,
            search_fields=["name", "email", "phone"]
        )
        return items, total

    def update_patient(self, db: Session, patient_id: int, payload: PatientUpdate) -> Patient:
        patient = self.get_patient_or_404(db, patient_id)
        if payload.email and payload.email != patient.email:
            existing = patient_repository.get_by_email(db, payload.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Patient with email '{payload.email}' already exists"
                )
        return patient_repository.update(db, db_obj=patient, obj_in=payload)

    def deactivate_patient(self, db: Session, patient_id: int) -> Patient:
        patient = self.get_patient_or_404(db, patient_id)
        return patient_repository.update(db, db_obj=patient, obj_in={"is_active": False})


patient_service = PatientService()
