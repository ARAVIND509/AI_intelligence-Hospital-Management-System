from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles, verify_patient_access
from app.models.user import User
from app.services.analytics_service import analytics_service
from app.services.patient_analytics_service import patient_analytics_service
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    DoctorWorkloadSummary,
    DepartmentPerformanceSummary,
    PatientAnalyticsResponse,
)

router = APIRouter(prefix="/analytics", tags=["Hospital & Patient Analytics"])


@router.get("/dashboard", response_model=AnalyticsOverviewResponse)
def get_hospital_analytics_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return analytics_service.get_hospital_analytics_overview(db)


@router.get("/doctor-workload", response_model=List[DoctorWorkloadSummary])
def get_doctor_workload(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return analytics_service.get_doctor_workload_summary(db)


@router.get("/department-performance", response_model=List[DepartmentPerformanceSummary])
def get_department_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return analytics_service.get_department_performance_summary(db)


@router.get("/patients/{patient_id}", response_model=PatientAnalyticsResponse)
def get_patient_analytics(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_patient_access(current_user, patient_id)
    return patient_analytics_service.get_patient_analytics(db, patient_id)
