import re
from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
from app.models.billing import Billing


def _generate_sequential_id(db: Session, model_class, prefix: str, id_col_name: str) -> str:
    last_record = db.query(model_class).order_by(model_class.id.desc()).first()
    if not last_record:
        next_num = 1
    else:
        existing_code = getattr(last_record, id_col_name, "")
        match = re.search(r"\d+", existing_code or "")
        if match:
            next_num = int(match.group()) + 1
        else:
            next_num = last_record.id + 1

    while True:
        candidate = f"{prefix}-{next_num:06d}"
        filter_kwargs = {id_col_name: candidate}
        exists = db.query(model_class).filter_by(**filter_kwargs).first()
        if not exists:
            return candidate
        next_num += 1


def generate_appointment_id(db: Session) -> str:
    return _generate_sequential_id(db, Appointment, "APT", "apt_id")


def generate_medical_record_id(db: Session) -> str:
    return _generate_sequential_id(db, MedicalRecord, "REC", "record_id")


def generate_prescription_id(db: Session) -> str:
    return _generate_sequential_id(db, Prescription, "RX", "rx_id")


def generate_bill_id(db: Session) -> str:
    return _generate_sequential_id(db, Billing, "INV", "bill_id")
