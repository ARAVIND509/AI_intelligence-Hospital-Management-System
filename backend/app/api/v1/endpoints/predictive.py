from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.ai.predictive_models import ai_predictive_engine
from app.schemas.analytics import (
    NoShowPredictionRequest,
    NoShowPredictionResponse,
    ReadmissionRiskRequest,
    ReadmissionRiskResponse,
    BedOccupancyForecastResponse,
    MedicineDemandForecastItem,
    LabWorkloadForecastResponse,
)

router = APIRouter(prefix="/ai/predict", tags=["Predictive Analytics"])


@router.post("/no-show", response_model=NoShowPredictionResponse)
def predict_appointment_no_show(
    payload: NoShowPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR", "RECEPTIONIST"])),
):
    return ai_predictive_engine.predict_appointment_no_show(db, payload)


@router.post("/readmission-risk", response_model=ReadmissionRiskResponse)
def predict_readmission_risk(
    payload: ReadmissionRiskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR"])),
):
    return ai_predictive_engine.predict_readmission_risk(db, payload)


@router.get("/bed-occupancy", response_model=BedOccupancyForecastResponse)
def forecast_bed_occupancy(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DEPARTMENT_HEAD"])),
):
    return ai_predictive_engine.forecast_bed_occupancy(db, days=days)


@router.get("/medicine-demand", response_model=List[MedicineDemandForecastItem])
def forecast_medicine_demand(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "PHARMACY", "DEPARTMENT_HEAD"])),
):
    return ai_predictive_engine.forecast_medicine_demand(db)


@router.get("/lab-workload", response_model=LabWorkloadForecastResponse)
def forecast_lab_workload(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "LABORATORY", "DEPARTMENT_HEAD"])),
):
    return ai_predictive_engine.forecast_lab_workload(db)
