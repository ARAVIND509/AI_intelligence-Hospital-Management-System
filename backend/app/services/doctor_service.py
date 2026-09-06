from datetime import date, time
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.doctor_repository import doctor_repository
from app.repositories.department_repository import department_repository
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.models.doctor import Doctor


class DoctorService:
    def get_doctor_or_404(self, db: Session, doctor_id: int) -> Doctor:
        doctor = doctor_repository.get(db, doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor with ID {doctor_id} not found"
            )
        return doctor

    def create_doctor(self, db: Session, payload: DoctorCreate) -> Doctor:
        if payload.department_id:
            dept = department_repository.get(db, payload.department_id)
            if not dept:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department with ID {payload.department_id} not found"
                )
        if payload.email:
            existing = doctor_repository.get_by_email(db, payload.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Doctor with email '{payload.email}' already exists"
                )
        return doctor_repository.create(db, obj_in=payload)

    def get_doctors(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        department_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_available: Optional[bool] = None,
        search: Optional[str] = None
    ):
        skip = (page - 1) * limit
        filters = {}
        if department_id is not None:
            filters["department_id"] = department_id
        if is_active is not None:
            filters["is_active"] = is_active
        if is_available is not None:
            filters["is_available"] = is_available

        items, total = doctor_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            search_query=search,
            search_fields=["name", "specialization", "email"]
        )
        return items, total

    def check_doctor_availability(
        self,
        db: Session,
        doctor_id: int,
        target_date: date,
        target_time: time
    ) -> bool:
        doctor = self.get_doctor_or_404(db, doctor_id)

        if not doctor.is_active or not doctor.is_available:
            return False

        # Check working days (e.g. "Monday,Tuesday,...")
        day_name = target_date.strftime("%A")
        allowed_days = [d.strip() for d in doctor.working_days.split(",") if d.strip()]
        if day_name not in allowed_days:
            return False

        # Check shift timing bounds
        if not (doctor.working_hours_start <= target_time <= doctor.working_hours_end):
            return False

        return True

    def update_doctor(self, db: Session, doctor_id: int, payload: DoctorUpdate) -> Doctor:
        doctor = self.get_doctor_or_404(db, doctor_id)
        if payload.department_id:
            dept = department_repository.get(db, payload.department_id)
            if not dept:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department with ID {payload.department_id} not found"
                )
        if payload.email and payload.email != doctor.email:
            existing = doctor_repository.get_by_email(db, payload.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Doctor with email '{payload.email}' already exists"
                )
        return doctor_repository.update(db, db_obj=doctor, obj_in=payload)

    def deactivate_doctor(self, db: Session, doctor_id: int) -> Doctor:
        doctor = self.get_doctor_or_404(db, doctor_id)
        return doctor_repository.update(db, db_obj=doctor, obj_in={"is_active": False, "is_available": False})


doctor_service = DoctorService()
