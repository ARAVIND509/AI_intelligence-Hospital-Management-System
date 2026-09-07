from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.services.hospital_report_service import hospital_report_service
from app.schemas.analytics import HospitalReportResponse

router = APIRouter(prefix="/reports", tags=["Hospital Reports Generator"])


@router.get("/daily", response_model=HospitalReportResponse)
def get_daily_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return hospital_report_service.generate_daily_report(db)


@router.get("/monthly", response_model=HospitalReportResponse)
def get_monthly_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return hospital_report_service.generate_monthly_report(db)


@router.get("/department/{department_id}", response_model=HospitalReportResponse)
def get_department_report(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return hospital_report_service.generate_department_report(db, department_id)


@router.get("/revenue", response_model=HospitalReportResponse)
def get_revenue_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return hospital_report_service.generate_revenue_report(db)


@router.get("/pharmacy", response_model=HospitalReportResponse)
def get_pharmacy_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "PHARMACY", "DEPARTMENT_HEAD"])),
):
    return hospital_report_service.generate_pharmacy_report(db)


@router.get("/laboratory", response_model=HospitalReportResponse)
def get_laboratory_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "LABORATORY", "DEPARTMENT_HEAD"])),
):
    return hospital_report_service.generate_laboratory_report(db)


@router.get("/patient-statistics", response_model=HospitalReportResponse)
def get_patient_statistics_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return hospital_report_service.generate_patient_statistics_report(db)
