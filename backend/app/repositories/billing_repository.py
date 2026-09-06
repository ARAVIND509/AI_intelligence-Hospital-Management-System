from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.billing import Billing
from app.schemas.billing import BillingCreate, BillingUpdate
from app.repositories.base_repository import CRUDBase


class CRUDBilling(CRUDBase[Billing, BillingCreate, BillingUpdate]):
    def get_by_bill_id(self, db: Session, bill_id: str) -> Optional[Billing]:
        return db.query(Billing).filter(Billing.bill_id == bill_id).first()

    def get_by_id_or_bill_id(self, db: Session, identifier: str) -> Optional[Billing]:
        if identifier.isdigit():
            return db.query(Billing).filter(Billing.id == int(identifier)).first()
        return self.get_by_bill_id(db, identifier)

    def get_patient_history(self, db: Session, patient_id: int) -> List[Billing]:
        return db.query(Billing).filter(Billing.patient_id == patient_id).order_by(Billing.created_at.desc()).all()


billing_repository = CRUDBilling(Billing)
