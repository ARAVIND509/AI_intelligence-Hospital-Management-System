from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.repositories.base_repository import CRUDBase


class CRUDDoctor(CRUDBase[Doctor, DoctorCreate, DoctorUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[Doctor]:
        return db.query(Doctor).filter(Doctor.email == email).first()

    def get_by_department(self, db: Session, department_id: int) -> List[Doctor]:
        return db.query(Doctor).filter(Doctor.department_id == department_id, Doctor.is_active == True).all()


doctor_repository = CRUDDoctor(Doctor)
