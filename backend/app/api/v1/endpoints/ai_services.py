from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles, verify_patient_access
from app.models.user import User
from app.ai.summary_engine import ai_summary_engine
from app.schemas.analytics import (
    AIHealthSummaryRequest,
    AIHealthSummaryResponse,
    AILabExplanationRequest,
    AILabExplanationResponse,
)

router = APIRouter(prefix="/ai", tags=["AI Clinical Assistance"])


@router.post("/patient-summary/{patient_id}", response_model=AIHealthSummaryResponse)
def generate_ai_patient_health_summary(
    patient_id: int,
    payload: AIHealthSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "DOCTOR"])),
):
    verify_patient_access(current_user, patient_id)
    return ai_summary_engine.generate_patient_health_summary(db, patient_id, doctor_notes=payload.doctor_notes)


@router.post("/explain-lab-result", response_model=AILabExplanationResponse)
def explain_lab_result(
    payload: AILabExplanationRequest,
    current_user: User = Depends(get_current_user),
):
    return ai_summary_engine.explain_lab_result(payload)
