from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import CRUDBase
from app.models.laboratory import LabTestCatalog, LabOrder, LabResult
from app.schemas.laboratory import LabTestCatalogCreate, LabTestCatalogUpdate, LabOrderCreate, LabResultCreate


class CRUDLabTestCatalog(CRUDBase[LabTestCatalog, LabTestCatalogCreate, LabTestCatalogUpdate]):
    def get_by_code(self, db: Session, test_code: str) -> Optional[LabTestCatalog]:
        return db.query(LabTestCatalog).filter(LabTestCatalog.test_code == test_code).first()


class CRUDLabOrder(CRUDBase[LabOrder, LabOrderCreate, dict]):
    def get_by_order_number(self, db: Session, order_number: str) -> Optional[LabOrder]:
        return db.query(LabOrder).filter(LabOrder.order_number == order_number).first()

    def get_by_patient(self, db: Session, patient_id: int) -> List[LabOrder]:
        return db.query(LabOrder).filter(LabOrder.patient_id == patient_id).order_by(LabOrder.id.desc()).all()


class CRUDLabResult(CRUDBase[LabResult, LabResultCreate, dict]):
    def get_by_order(self, db: Session, lab_order_id: int) -> List[LabResult]:
        return db.query(LabResult).filter(LabResult.lab_order_id == lab_order_id).all()


lab_test_catalog_repository = CRUDLabTestCatalog(LabTestCatalog)
lab_order_repository = CRUDLabOrder(LabOrder)
lab_result_repository = CRUDLabResult(LabResult)
