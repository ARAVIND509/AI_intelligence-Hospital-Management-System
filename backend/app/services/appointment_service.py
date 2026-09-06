from datetime import date, time
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.appointment_repository import appointment_repository
from app.services.patient_service import patient_service
from app.services.doctor_service import doctor_service
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentReschedule,
)
from app.models.appointment import Appointment
from app.utils.id_generator import generate_appointment_id

VALID_TRANSITIONS = {
    "scheduled": ["confirmed", "cancelled"],
    "confirmed": ["completed", "cancelled", "no_show"],
    "completed": [],
    "cancelled": [],
    "no_show": [],
}


class AppointmentService:
    def get_appointment_or_404(self, db: Session, appointment_id: str) -> Appointment:
        apt = appointment_repository.get_by_id_or_apt_id(db, appointment_id)
        if not apt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Appointment '{appointment_id}' not found"
            )
        return apt

    def create_appointment(self, db: Session, payload: AppointmentCreate) -> Appointment:
        # Validate patient
        patient = patient_service.get_patient_or_404(db, payload.patient_id)
        if not patient.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Patient ID {payload.patient_id} is inactive"
            )

        # Validate doctor
        doctor = doctor_service.get_doctor_or_404(db, payload.doctor_id)
        if not doctor.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Doctor ID {payload.doctor_id} is inactive"
            )
        if not doctor.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Doctor ID {payload.doctor_id} is currently unavailable"
            )

        # Check doctor schedule bounds
        if not doctor_service.check_doctor_availability(db, payload.doctor_id, payload.appointment_date, payload.appointment_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested date or time falls outside doctor's working schedule/hours"
            )

        # Prevent double booking
        conflict = appointment_repository.check_conflict(
            db, payload.doctor_id, payload.appointment_date, payload.appointment_time
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Doctor already has an active appointment scheduled at this date and time"
            )

        apt_id = generate_appointment_id(db)
        create_data = payload.model_dump()
        create_data["apt_id"] = apt_id
        create_data["status"] = "scheduled"

        return appointment_repository.create(db, obj_in=create_data)

    def get_appointments(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        appointment_date: Optional[date] = None,
        search: Optional[str] = None
    ):
        skip = (page - 1) * limit
        filters = {}
        if patient_id is not None:
            filters["patient_id"] = patient_id
        if doctor_id is not None:
            filters["doctor_id"] = doctor_id
        if status_filter is not None:
            filters["status"] = status_filter
        if appointment_date is not None:
            filters["appointment_date"] = appointment_date

        items, total = appointment_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            search_query=search,
            search_fields=["apt_id", "reason", "notes"]
        )
        return items, total

    def update_appointment(self, db: Session, appointment_id: str, payload: AppointmentUpdate) -> Appointment:
        apt = self.get_appointment_or_404(db, appointment_id)

        if payload.status is not None and payload.status != apt.status:
            current_status = apt.status
            new_status = payload.status
            allowed = VALID_TRANSITIONS.get(current_status, [])
            if new_status not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status transition from '{current_status}' to '{new_status}'. Allowed: {allowed}"
                )

        return appointment_repository.update(db, db_obj=apt, obj_in=payload)

    def reschedule_appointment(
        self,
        db: Session,
        appointment_id: str,
        payload: AppointmentReschedule
    ) -> Appointment:
        apt = self.get_appointment_or_404(db, appointment_id)

        if apt.status in ["cancelled", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reschedule an appointment with status '{apt.status}'"
            )

        # Check doctor working bounds
        if not doctor_service.check_doctor_availability(db, apt.doctor_id, payload.appointment_date, payload.appointment_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reschedule target falls outside doctor's working schedule/hours"
            )

        # Check conflict
        conflict = appointment_repository.check_conflict(
            db, apt.doctor_id, payload.appointment_date, payload.appointment_time, exclude_apt_id=apt.id
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Doctor already has an active appointment at requested date and time"
            )

        return appointment_repository.update(db, db_obj=apt, obj_in=payload)

    def cancel_appointment(self, db: Session, appointment_id: str) -> Appointment:
        apt = self.get_appointment_or_404(db, appointment_id)

        if apt.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel a completed appointment"
            )

        if apt.status == "cancelled":
            return apt

        return appointment_repository.update(db, db_obj=apt, obj_in={"status": "cancelled"})


appointment_service = AppointmentService()
