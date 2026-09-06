import math
from datetime import date, time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentReschedule,
    AppointmentResponse,
    AppointmentPaginatedResponse,
)
from app.utils.id_generator import generate_appointment_id

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

VALID_TRANSITIONS = {
    "scheduled": ["confirmed", "cancelled"],
    "confirmed": ["completed", "cancelled", "no_show"],
    "completed": [],
    "cancelled": [],
    "no_show": [],
}


def _get_appointment_by_id_or_apt_id(db: Session, identifier: str) -> Appointment:
    if identifier.isdigit():
        apt = db.query(Appointment).filter(Appointment.id == int(identifier)).first()
    else:
        apt = db.query(Appointment).filter(Appointment.apt_id == identifier).first()

    if not apt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID or APT ID '{identifier}' not found"
        )
    return apt


@router.post(
    "/",
    summary="Create Appointment",
    description="Creates a new appointment after validating patient, doctor, availability, and double-booking.",
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db)
):
    # 1. Validate Patient
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {payload.patient_id} not found"
        )
    if not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patient with ID {payload.patient_id} is inactive"
        )

    # 2. Validate Doctor
    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {payload.doctor_id} not found"
        )
    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doctor with ID {payload.doctor_id} is inactive"
        )
    if not doctor.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doctor with ID {payload.doctor_id} is currently unavailable"
        )

    # 3. Prevent Double Booking
    existing_conflict = db.query(Appointment).filter(
        Appointment.doctor_id == payload.doctor_id,
        Appointment.appointment_date == payload.appointment_date,
        Appointment.appointment_time == payload.appointment_time,
        Appointment.status != "cancelled",
    ).first()

    if existing_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor already has an active appointment scheduled at this date and time"
        )

    # 4. Generate APT ID & Create Record
    apt_id = generate_appointment_id(db)
    new_apt = Appointment(
        apt_id=apt_id,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        reason=payload.reason,
        notes=payload.notes,
        status="scheduled",
    )
    db.add(new_apt)
    db.commit()
    db.refresh(new_apt)

    return {
        "success": True,
        "message": "Appointment created successfully",
        "data": AppointmentResponse.model_validate(new_apt).model_dump()
    }


@router.get(
    "/",
    summary="List Appointments",
    description="Returns a paginated list of appointments with optional filtering.",
    status_code=status.HTTP_200_OK,
)
def list_appointments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    appointment_date: Optional[date] = Query(None, description="Filter by appointment date"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    doctor_id: Optional[int] = Query(None, description="Filter by doctor ID"),
    db: Session = Depends(get_db)
):
    query = db.query(Appointment)

    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    if appointment_date:
        query = query.filter(Appointment.appointment_date == appointment_date)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)

    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit

    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.asc()).offset(offset).limit(limit).all()

    items = [AppointmentResponse.model_validate(a).model_dump() for a in appointments]

    return {
        "success": True,
        "message": "Appointments fetched successfully",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    }


@router.get(
    "/{appointment_id}",
    summary="Get Appointment Details",
    description="Fetch a specific appointment by integer ID or APT ID.",
    status_code=status.HTTP_200_OK,
)
def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db)
):
    apt = _get_appointment_by_id_or_apt_id(db, appointment_id)
    return {
        "success": True,
        "message": "Appointment details fetched successfully",
        "data": AppointmentResponse.model_validate(apt).model_dump()
    }


@router.put(
    "/{appointment_id}",
    summary="Update Appointment",
    description="Update appointment reason, notes, or status with state transition validation.",
    status_code=status.HTTP_200_OK,
)
def update_appointment(
    appointment_id: str,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    apt = _get_appointment_by_id_or_apt_id(db, appointment_id)

    if payload.reason is not None:
        apt.reason = payload.reason
    if payload.notes is not None:
        apt.notes = payload.notes

    if payload.status is not None and payload.status != apt.status:
        current_status = apt.status
        new_status = payload.status
        allowed = VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from '{current_status}' to '{new_status}'. Allowed transitions: {allowed}"
            )
        apt.status = new_status

    db.commit()
    db.refresh(apt)

    return {
        "success": True,
        "message": "Appointment updated successfully",
        "data": AppointmentResponse.model_validate(apt).model_dump()
    }


@router.patch(
    "/{appointment_id}/reschedule",
    summary="Reschedule Appointment",
    description="Reschedules an appointment to a new date and time after checking doctor availability and double-booking.",
    status_code=status.HTTP_200_OK,
)
def reschedule_appointment(
    appointment_id: str,
    payload: AppointmentReschedule,
    db: Session = Depends(get_db)
):
    apt = _get_appointment_by_id_or_apt_id(db, appointment_id)

    if apt.status in ["cancelled", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reschedule an appointment with status '{apt.status}'"
        )

    # Check doctor status & availability
    doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
    if not doctor or not doctor.is_active or not doctor.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned doctor is unavailable or inactive for rescheduling"
        )

    # Check double booking conflict
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == apt.doctor_id,
        Appointment.appointment_date == payload.appointment_date,
        Appointment.appointment_time == payload.appointment_time,
        Appointment.status != "cancelled",
        Appointment.id != apt.id,
    ).first()

    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor already has another active appointment at the requested date and time"
        )

    apt.appointment_date = payload.appointment_date
    apt.appointment_time = payload.appointment_time
    db.commit()
    db.refresh(apt)

    return {
        "success": True,
        "message": "Appointment rescheduled successfully",
        "data": AppointmentResponse.model_validate(apt).model_dump()
    }


@router.delete(
    "/{appointment_id}",
    summary="Cancel Appointment",
    description="Soft cancels an appointment by setting status to cancelled.",
    status_code=status.HTTP_200_OK,
)
def cancel_appointment(
    appointment_id: str,
    db: Session = Depends(get_db)
):
    apt = _get_appointment_by_id_or_apt_id(db, appointment_id)

    if apt.status == "cancelled":
        return {
            "success": True,
            "message": "Appointment is already cancelled",
            "data": AppointmentResponse.model_validate(apt).model_dump()
        }

    if apt.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed appointment"
        )

    apt.status = "cancelled"
    db.commit()
    db.refresh(apt)

    return {
        "success": True,
        "message": "Appointment cancelled successfully",
        "data": AppointmentResponse.model_validate(apt).model_dump()
    }