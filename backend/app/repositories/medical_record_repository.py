from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.medical_record import MedicalRecord
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate
from app.repositories.base_repository import CRUDBase


class CRUDMedicalRecord(CRUDBase[MedicalRecord, MedicalRecordCreate, MedicalRecordUpdate]):
    def get_by_record_id(self, db: Session, record_id: str) -> Optional[MedicalRecord]:
        return db.query(MedicalRecord).filter(MedicalRecord.record_id == record_id).first()

    def get_by_id_or_record_id(self, db: Session, identifier: str) -> Optional[MedicalRecord]:
        if identifier.isdigit():
            return db.query(MedicalRecord).filter(MedicalRecord.id == int(identifier)).first()
        return self.get_by_record_id(db, identifier)

    def get_patient_history(self, db: Session, patient_id: int) -> List[MedicalRecord]:
        return db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).order_by(MedicalRecord.created_at.desc()).all()


medical_record_repository = CRUDMedicalRecord(MedicalRecord)
