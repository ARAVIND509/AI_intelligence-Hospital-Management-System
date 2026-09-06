import re
from sqlalchemy.orm import Session
from app.models.appointment import Appointment


def generate_appointment_id(db: Session) -> str:
    """
    Generates a unique hospital-friendly appointment ID (e.g. APT-000001).
    """
    last_apt = db.query(Appointment).order_by(Appointment.id.desc()).first()
    if not last_apt:
        next_num = 1
    else:
        match = re.search(r"\d+", last_apt.apt_id or "")
        if match:
            next_num = int(match.group()) + 1
        else:
            next_num = last_apt.id + 1

    while True:
        candidate = f"APT-{next_num:06d}"
        exists = db.query(Appointment).filter(Appointment.apt_id == candidate).first()
        if not exists:
            return candidate
        next_num += 1
