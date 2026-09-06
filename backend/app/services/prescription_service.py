from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.prescription_repository import prescription_repository
from app.services.patient_service import patient_service
from app.services.doctor_service import doctor_service
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from app.models.prescription import Prescription, PrescriptionMedicine
from app.utils.id_generator import generate_prescription_id


class PrescriptionService:
    def get_prescription_or_404(self, db: Session, rx_id: str) -> Prescription:
        rx = prescription_repository.get_by_id_or_rx_id(db, rx_id)
        if not rx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prescription '{rx_id}' not found"
            )
        return rx

    def create_prescription(self, db: Session, payload: PrescriptionCreate) -> Prescription:
        patient_service.get_patient_or_404(db, payload.patient_id)
        doctor_service.get_doctor_or_404(db, payload.doctor_id)

        rx_id = generate_prescription_id(db)

        db_rx = Prescription(
            rx_id=rx_id,
            patient_id=payload.patient_id,
            doctor_id=payload.doctor_id,
            appointment_id=payload.appointment_id,
            medical_record_id=payload.medical_record_id,
            notes=payload.notes,
        )
        db.add(db_rx)
        db.flush()

        for med in payload.medicines:
            db_med = PrescriptionMedicine(
                prescription_id=db_rx.id,
                medicine_name=med.medicine_name,
                dosage=med.dosage,
                frequency=med.frequency,
                duration=med.duration,
                instructions=med.instructions,
            )
            db.add(db_med)

        db.commit()
        db.refresh(db_rx)
        return db_rx

    def get_prescriptions(
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

        items, total = prescription_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            search_query=search,
            search_fields=["rx_id", "notes"]
        )
        return items, total

    def get_patient_history(self, db: Session, patient_id: int) -> List[Prescription]:
        patient_service.get_patient_or_404(db, patient_id)
        return prescription_repository.get_patient_history(db, patient_id)

    def update_prescription(self, db: Session, rx_id: str, payload: PrescriptionUpdate) -> Prescription:
        rx = self.get_prescription_or_404(db, rx_id)

        if payload.notes is not None:
            rx.notes = payload.notes

        if payload.medicines is not None:
            # Re-create medicines
            db.query(PrescriptionMedicine).filter(PrescriptionMedicine.prescription_id == rx.id).delete()
            for med in payload.medicines:
                db_med = PrescriptionMedicine(
                    prescription_id=rx.id,
                    medicine_name=med.medicine_name,
                    dosage=med.dosage,
                    frequency=med.frequency,
                    duration=med.duration,
                    instructions=med.instructions,
                )
                db.add(db_med)

        db.commit()
        db.refresh(rx)
        return rx


prescription_service = PrescriptionService()
