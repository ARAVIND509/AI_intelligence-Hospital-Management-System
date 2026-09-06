from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.prescription import Prescription
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from app.repositories.base_repository import CRUDBase


class CRUDPrescription(CRUDBase[Prescription, PrescriptionCreate, PrescriptionUpdate]):
    def get_by_rx_id(self, db: Session, rx_id: str) -> Optional[Prescription]:
        return db.query(Prescription).filter(Prescription.rx_id == rx_id).first()

    def get_by_id_or_rx_id(self, db: Session, identifier: str) -> Optional[Prescription]:
        if identifier.isdigit():
            return db.query(Prescription).filter(Prescription.id == int(identifier)).first()
        return self.get_by_rx_id(db, identifier)

    def get_patient_history(self, db: Session, patient_id: int) -> List[Prescription]:
        return db.query(Prescription).filter(Prescription.patient_id == patient_id).order_by(Prescription.created_at.desc()).all()


prescription_repository = CRUDPrescription(Prescription)
