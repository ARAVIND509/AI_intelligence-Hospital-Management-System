from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import CRUDBase
from app.models.admission import Ward, Bed, Admission, BedTransferLog
from app.schemas.admission import WardCreate, BedCreate, AdmissionCreate


class CRUDWard(CRUDBase[Ward, WardCreate, dict]):
    def get_by_name(self, db: Session, ward_name: str) -> Optional[Ward]:
        return db.query(Ward).filter(Ward.ward_name == ward_name).first()


class CRUDBed(CRUDBase[Bed, BedCreate, dict]):
    def get_vacant_beds_in_ward(self, db: Session, ward_id: int) -> List[Bed]:
        return db.query(Bed).filter(Bed.ward_id == ward_id, Bed.status == "VACANT").all()


class CRUDAdmission(CRUDBase[Admission, AdmissionCreate, dict]):
    def get_by_admission_number(self, db: Session, admission_number: str) -> Optional[Admission]:
        return db.query(Admission).filter(Admission.admission_number == admission_number).first()

    def get_active_admissions(self, db: Session) -> List[Admission]:
        return db.query(Admission).filter(Admission.status == "ADMITTED").all()

    def get_by_patient(self, db: Session, patient_id: int) -> List[Admission]:
        return db.query(Admission).filter(Admission.patient_id == patient_id).order_by(Admission.id.desc()).all()


class CRUDBedTransferLog(CRUDBase[BedTransferLog, dict, dict]):
    def get_by_admission(self, db: Session, admission_id: int) -> List[BedTransferLog]:
        return db.query(BedTransferLog).filter(BedTransferLog.admission_id == admission_id).order_by(BedTransferLog.id.desc()).all()


ward_repository = CRUDWard(Ward)
bed_repository = CRUDBed(Bed)
admission_repository = CRUDAdmission(Admission)
bed_transfer_log_repository = CRUDBedTransferLog(BedTransferLog)
