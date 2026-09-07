from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.services.laboratory_service import laboratory_service
from app.schemas.laboratory import (
    LabTestCatalogCreate,
    LabTestCatalogUpdate,
    LabTestCatalogResponse,
    LabOrderCreate,
    LabOrderResponse,
    SampleCollectRequest,
    LabResultCreate,
    LabResultResponse,
    DoctorResultReviewRequest,
    PatientLabReport,
)

router = APIRouter(prefix="/laboratory", tags=["Laboratory Management"])


# Catalog Endpoints
@router.post("/catalog", response_model=LabTestCatalogResponse, status_code=status.HTTP_201_CREATED)
def create_lab_test_catalog(
    obj_in: LabTestCatalogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "LABORATORY"])),
):
    return laboratory_service.create_catalog_item(db, obj_in)


@router.get("/catalog", response_model=List[LabTestCatalogResponse])
def list_lab_test_catalog(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, _ = laboratory_service.list_catalog(db, skip=skip, limit=limit)
    return items


@router.get("/catalog/{item_id}", response_model=LabTestCatalogResponse)
def get_lab_test_catalog(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return laboratory_service.get_catalog_item(db, item_id)


@router.put("/catalog/{item_id}", response_model=LabTestCatalogResponse)
def update_lab_test_catalog(
    item_id: int,
    obj_in: LabTestCatalogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "LABORATORY"])),
):
    return laboratory_service.update_catalog_item(db, item_id, obj_in)


# Orders Endpoints
@router.post("/orders", response_model=LabOrderResponse, status_code=status.HTTP_201_CREATED)
def create_lab_order(
    obj_in: LabOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR", "LABORATORY"])),
):
    return laboratory_service.create_lab_order(db, obj_in)


@router.get("/orders", response_model=List[LabOrderResponse])
def list_lab_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    patient_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders, _ = laboratory_service.list_lab_orders(db, skip=skip, limit=limit, patient_id=patient_id, status_filter=status_filter)
    return orders


@router.get("/orders/{order_id}", response_model=LabOrderResponse)
def get_lab_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return laboratory_service.get_lab_order(db, order_id)


@router.post("/orders/{order_id}/collect-sample", response_model=LabOrderResponse)
def collect_sample(
    order_id: int,
    sample_req: SampleCollectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "LABORATORY", "RECEPTIONIST"])),
):
    return laboratory_service.collect_sample(db, order_id, current_user.id, sample_req)


@router.post("/orders/{order_id}/results", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED)
def enter_lab_result(
    order_id: int,
    result_in: LabResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "LABORATORY"])),
):
    return laboratory_service.enter_result(db, order_id, current_user.id, result_in)


@router.post("/results/{result_id}/review", response_model=LabResultResponse)
def review_lab_result(
    result_id: int,
    review_in: DoctorResultReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR"])),
):
    doctor_id = current_user.doctor_id if current_user.doctor_id else 1
    return laboratory_service.review_result(db, result_id, doctor_id, review_in)


@router.get("/patients/{patient_id}/report", response_model=PatientLabReport)
def get_patient_lab_report(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return laboratory_service.get_patient_lab_report(db, patient_id)
