from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.medical_record_repository import medical_record_repository
from app.services.patient_service import patient_service
from app.services.doctor_service import doctor_service
from app.services.appointment_service import appointment_service
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate
from app.models.medical_record import MedicalRecord
from app.utils.id_generator import generate_medical_record_id


class MedicalRecordService:
    def get_record_or_404(self, db: Session, record_id: str) -> MedicalRecord:
        rec = medical_record_repository.get_by_id_or_record_id(db, record_id)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical record '{record_id}' not found"
            )
        return rec

    def create_record(self, db: Session, payload: MedicalRecordCreate) -> MedicalRecord:
        patient_service.get_patient_or_404(db, payload.patient_id)
        doctor_service.get_doctor_or_404(db, payload.doctor_id)

        if payload.appointment_id:
            appointment_service.get_appointment_or_404(db, str(payload.appointment_id))

        rec_id = generate_medical_record_id(db)
        create_data = payload.model_dump()
        create_data["record_id"] = rec_id

        return medical_record_repository.create(db, obj_in=create_data)

    def get_records(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        search: Optional[str] = None
    ):
        skip = (page - 1) * limit
        filters = {}
        if patient_id is not None:
            filters["patient_id"] = patient_id
        if doctor_id is not None:
            filters["doctor_id"] = doctor_id

        items, total = medical_record_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            search_query=search,
            search_fields=["record_id", "diagnosis", "symptoms", "treatment_plan"]
        )
        return items, total

    def get_patient_history(self, db: Session, patient_id: int) -> List[MedicalRecord]:
        patient_service.get_patient_or_404(db, patient_id)
        return medical_record_repository.get_patient_history(db, patient_id)

    def update_record(self, db: Session, record_id: str, payload: MedicalRecordUpdate) -> MedicalRecord:
        rec = self.get_record_or_404(db, record_id)
        return medical_record_repository.update(db, db_obj=rec, obj_in=payload)


medical_record_service = MedicalRecordService()
