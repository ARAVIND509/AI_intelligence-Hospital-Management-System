from typing import Optional
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.repositories.base_repository import CRUDBase


class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[Patient]:
        return db.query(Patient).filter(Patient.email == email).first()


patient_repository = CRUDPatient(Patient)
