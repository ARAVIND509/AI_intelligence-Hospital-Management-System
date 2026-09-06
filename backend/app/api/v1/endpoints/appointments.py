import math
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.services.appointment_service import appointment_service
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentReschedule,
    AppointmentResponse,
)
from app.models.user import User

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post(
    "/",
    summary="Create Appointment",
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_patient_access(current_user, payload.patient_id)
    apt = appointment_service.create_appointment(db, payload)
    return {
        "success": True,
        "message": "Appointment created successfully",
        "data": AppointmentResponse.model_validate(apt).model_dump()
    }


@router.get(
    "/",
    summary="List Appointments",
    status_code=status.HTTP_200_OK,
)
def list_appointments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    appointment_date: Optional[date] = Query(None),
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.upper() == "PATIENT":
        patient_id = current_user.patient_id

    items, total = appointment_service.get_appointments(
        db,
        page=page,
        limit=limit,
        patient_id=patient_id,
        doctor_id=doctor_id,
        status_filter=status_filter,
        appointment_date=appointment_date,
        search=search
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    serialized = [AppointmentResponse.model_validate(a).model_dump() for a in items]
    return {
        "success": True,
        "message": "Appointments fetched successfully",
        "data": {
            "items": serialized,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    }


@router.get(
    "/{appointment_id}",
    summary="Get Appointment Details",
    status_code=status.HTTP_200_OK,
)
def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    apt = appointment_service.get_appointment_or_404(db, appointment_id)
    verify_patient_access(current_user, apt.patient_id)
    return {
        "success": True,
        "message": "Appointment details fetched successfully",
        "data": AppointmentResponse.model_validate(apt).model_dump()
    }


@router.put(
    "/{appointment_id}",
    summary="Update Appointment",
    status_code=status.HTTP_200_OK,
)
def update_appointment(
    appointment_id: str,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    apt = appointment_service.get_appointment_or_404(db, appointment_id)
    verify_patient_access(current_user, apt.patient_id)
    updated_apt = appointment_service.update_appointment(db, appointment_id, payload)
    return {
        "success": True,
        "message": "Appointment updated successfully",
        "data": AppointmentResponse.model_validate(updated_apt).model_dump()
    }


@router.patch(
    "/{appointment_id}/reschedule",
    summary="Reschedule Appointment",
    status_code=status.HTTP_200_OK,
)
def reschedule_appointment(
    appointment_id: str,
    payload: AppointmentReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    apt = appointment_service.get_appointment_or_404(db, appointment_id)
    verify_patient_access(current_user, apt.patient_id)
    rescheduled_apt = appointment_service.reschedule_appointment(db, appointment_id, payload)
    return {
        "success": True,
        "message": "Appointment rescheduled successfully",
        "data": AppointmentResponse.model_validate(rescheduled_apt).model_dump()
    }


@router.delete(
    "/{appointment_id}",
    summary="Cancel Appointment",
    status_code=status.HTTP_200_OK,
)
def cancel_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    apt = appointment_service.get_appointment_or_404(db, appointment_id)
    verify_patient_access(current_user, apt.patient_id)
    cancelled_apt = appointment_service.cancel_appointment(db, appointment_id)
    return {
        "success": True,
        "message": "Appointment cancelled successfully",
        "data": AppointmentResponse.model_validate(cancelled_apt).model_dump()
    }