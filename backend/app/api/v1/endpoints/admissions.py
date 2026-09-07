from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.services.admission_service import admission_service
from app.schemas.admission import (
    WardCreate,
    WardResponse,
    BedCreate,
    BedResponse,
    AdmissionCreate,
    AdmissionResponse,
    BedTransferRequest,
    DischargeRequest,
)

router = APIRouter(prefix="/admissions", tags=["IP / Admission Management"])


# Ward Endpoints
@router.post("/wards", response_model=WardResponse, status_code=status.HTTP_201_CREATED)
def create_ward(
    obj_in: WardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return admission_service.create_ward(db, obj_in)


@router.get("/wards", response_model=List[WardResponse])
def list_wards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return admission_service.list_wards(db)


# Bed Endpoints
@router.post("/beds", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
def create_bed(
    obj_in: BedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return admission_service.create_bed(db, obj_in)


@router.get("/beds", response_model=List[BedResponse])
def list_beds(
    ward_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return admission_service.list_beds(db, ward_id=ward_id, status_filter=status_filter)


# Admission Endpoints
@router.post("", response_model=AdmissionResponse, status_code=status.HTTP_201_CREATED)
def admit_patient(
    obj_in: AdmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR", "RECEPTIONIST"])),
):
    return admission_service.admit_patient(db, obj_in)


@router.get("", response_model=List[AdmissionResponse])
def list_admissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    patient_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admissions, _ = admission_service.list_admissions(db, skip=skip, limit=limit, patient_id=patient_id, status_filter=status_filter)
    return admissions


@router.get("/{admission_id}", response_model=AdmissionResponse)
def get_admission(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return admission_service.get_admission(db, admission_id)


@router.post("/{admission_id}/transfer", response_model=AdmissionResponse)
def transfer_bed(
    admission_id: int,
    transfer_req: BedTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR", "RECEPTIONIST"])),
):
    return admission_service.transfer_bed(db, admission_id, current_user.id, transfer_req)


@router.post("/{admission_id}/discharge", response_model=AdmissionResponse)
def discharge_patient(
    admission_id: int,
    discharge_req: DischargeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR"])),
):
    return admission_service.discharge_patient(db, admission_id, discharge_req)
