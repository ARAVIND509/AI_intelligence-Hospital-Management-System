import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.laboratory import LabTestCatalog, LabOrder, LabResult
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.repositories.laboratory_repository import (
    lab_test_catalog_repository,
    lab_order_repository,
    lab_result_repository,
)
from app.schemas.laboratory import (
    LabTestCatalogCreate,
    LabTestCatalogUpdate,
    LabOrderCreate,
    SampleCollectRequest,
    LabResultCreate,
    DoctorResultReviewRequest,
    PatientLabReport,
)


class LaboratoryService:
    def create_catalog_item(self, db: Session, obj_in: LabTestCatalogCreate) -> LabTestCatalog:
        existing = lab_test_catalog_repository.get_by_code(db, obj_in.test_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lab test with code '{obj_in.test_code}' already exists"
            )
        return lab_test_catalog_repository.create(db, obj_in=obj_in)

    def get_catalog_item(self, db: Session, item_id: int) -> LabTestCatalog:
        item = lab_test_catalog_repository.get(db, item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab test catalog item not found")
        return item

    def list_catalog(self, db: Session, skip: int = 0, limit: int = 50) -> tuple[List[LabTestCatalog], int]:
        return lab_test_catalog_repository.get_multi(db, skip=skip, limit=limit)

    def update_catalog_item(self, db: Session, item_id: int, obj_in: LabTestCatalogUpdate) -> LabTestCatalog:
        item = self.get_catalog_item(db, item_id)
        return lab_test_catalog_repository.update(db, db_obj=item, obj_in=obj_in)

    def create_lab_order(self, db: Session, obj_in: LabOrderCreate) -> LabOrder:
        # Check patient & doctor existence
        patient = db.query(Patient).filter(Patient.id == obj_in.patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        doctor = db.query(Doctor).filter(Doctor.id == obj_in.doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        test = lab_test_catalog_repository.get(db, obj_in.lab_test_id)
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab test catalog item not found")

        order_number = f"LAB-{uuid.uuid4().hex[:8].upper()}"
        order_data = obj_in.model_dump()
        order_data["order_number"] = order_number
        order_data["status"] = "ORDERED"
        order_data["sample_type"] = test.sample_type

        return lab_order_repository.create(db, obj_in=order_data)

    def get_lab_order(self, db: Session, order_id: int) -> LabOrder:
        order = lab_order_repository.get(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab order not found")
        return order

    def list_lab_orders(
        self, db: Session, skip: int = 0, limit: int = 50, patient_id: Optional[int] = None, status_filter: Optional[str] = None
    ) -> tuple[List[LabOrder], int]:
        filters = {}
        if patient_id:
            filters["patient_id"] = patient_id
        if status_filter:
            filters["status"] = status_filter
        return lab_order_repository.get_multi(db, skip=skip, limit=limit, filters=filters)

    def collect_sample(self, db: Session, order_id: int, user_id: int, sample_req: SampleCollectRequest) -> LabOrder:
        order = self.get_lab_order(db, order_id)
        if order.status in ["COMPLETED", "CANCELLED"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot collect sample for order in status '{order.status}'")

        update_data = {
            "status": "SAMPLE_COLLECTED",
            "sample_id": sample_req.sample_id,
            "sample_type": sample_req.sample_type or order.sample_type,
            "sample_collected_at": datetime.now(timezone.utc),
            "collected_by_id": user_id,
        }
        return lab_order_repository.update(db, db_obj=order, obj_in=update_data)

    def enter_result(self, db: Session, order_id: int, user_id: int, result_in: LabResultCreate) -> LabResult:
        order = self.get_lab_order(db, order_id)
        if order.status == "CANCELLED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot enter results for a cancelled order")

        result_data = result_in.model_dump()
        result_data["lab_order_id"] = order_id
        result_data["entered_by_id"] = user_id
        result_data["reference_range"] = result_in.reference_range or (order.test_catalog.reference_range if order.test_catalog else None)

        res = lab_result_repository.create(db, obj_in=result_data)

        # Update order status to IN_ANALYSIS or COMPLETED
        lab_order_repository.update(db, db_obj=order, obj_in={"status": "COMPLETED"})
        return res

    def review_result(self, db: Session, result_id: int, doctor_id: int, review_in: DoctorResultReviewRequest) -> LabResult:
        result = lab_result_repository.get(db, result_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab result not found")

        update_data = {
            "doctor_review_status": "REVIEWED",
            "doctor_notes": review_in.doctor_notes,
            "reviewed_at": datetime.now(timezone.utc),
            "reviewed_by_doctor_id": doctor_id,
        }
        return lab_result_repository.update(db, db_obj=result, obj_in=update_data)

    def get_patient_lab_report(self, db: Session, patient_id: int) -> PatientLabReport:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        orders = lab_order_repository.get_by_patient(db, patient_id)
        completed_orders = [o for o in orders if o.status == "COMPLETED"]

        return PatientLabReport(
            patient_id=patient.id,
            patient_name=patient.name,
            total_orders=len(orders),
            completed_orders=len(completed_orders),
            orders=orders
        )


laboratory_service = LaboratoryService()
