from datetime import date, time
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.repositories.base_repository import CRUDBase


class CRUDAppointment(CRUDBase[Appointment, AppointmentCreate, AppointmentUpdate]):
    def get_by_apt_id(self, db: Session, apt_id: str) -> Optional[Appointment]:
        return db.query(Appointment).filter(Appointment.apt_id == apt_id).first()

    def get_by_id_or_apt_id(self, db: Session, identifier: str) -> Optional[Appointment]:
        if identifier.isdigit():
            return db.query(Appointment).filter(Appointment.id == int(identifier)).first()
        return self.get_by_apt_id(db, identifier)

    def check_conflict(
        self,
        db: Session,
        doctor_id: int,
        appointment_date: date,
        appointment_time: time,
        exclude_apt_id: Optional[int] = None
    ) -> Optional[Appointment]:
        query = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status != "cancelled",
        )
        if exclude_apt_id:
            query = query.filter(Appointment.id != exclude_apt_id)
        return query.first()

    def get_by_doctor_and_date(self, db: Session, doctor_id: int, appointment_date: date) -> List[Appointment]:
        return db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status != "cancelled"
        ).all()


appointment_repository = CRUDAppointment(Appointment)
