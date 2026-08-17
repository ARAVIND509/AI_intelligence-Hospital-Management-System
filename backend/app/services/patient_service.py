from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


# --------------------------------------------------
# GENERATE PATIENT ID
# --------------------------------------------------

def generate_patient_id(db: Session) -> str:
    """
    Generate a hospital patient identifier.

    Example:
        PT-000001
        PT-000002
        PT-000003
    """

    last_patient_id = db.scalar(
        select(Patient.patient_id)
        .order_by(Patient.id.desc())
        .limit(1)
    )

    if not last_patient_id:
        return "PT-000001"

    try:
        last_number = int(last_patient_id.split("-")[-1])
    except (ValueError, IndexError):
        last_number = 0

    return f"PT-{last_number + 1:06d}"


# --------------------------------------------------
# CREATE PATIENT
# --------------------------------------------------

def create_patient(
    db: Session,
    patient_data: PatientCreate,
) -> Patient:
    """
    Create and save a new patient.
    """

    patient = Patient(
        patient_id=generate_patient_id(db),
        user_id=patient_data.user_id,
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        blood_group=patient_data.blood_group,
        phone=patient_data.phone,
        email=patient_data.email,
        address=patient_data.address,
        emergency_contact_name=patient_data.emergency_contact_name,
        emergency_contact_phone=patient_data.emergency_contact_phone,
        emergency_contact_relation=patient_data.emergency_contact_relation,
        allergies=patient_data.allergies,
        chronic_conditions=patient_data.chronic_conditions,
        is_active=True,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


# --------------------------------------------------
# GET PATIENT BY DATABASE ID
# --------------------------------------------------

def get_patient_by_id(
    db: Session,
    patient_id: int,
) -> Patient | None:
    """
    Get a patient using the database primary key.
    """

    return db.scalar(
        select(Patient).where(
            Patient.id == patient_id
        )
    )


# --------------------------------------------------
# GET PATIENT BY PATIENT ID
# --------------------------------------------------

def get_patient_by_patient_id(
    db: Session,
    patient_identifier: str,
) -> Patient | None:
    """
    Get a patient using hospital patient ID.

    Example:
        PT-000001
    """

    return db.scalar(
        select(Patient).where(
            Patient.patient_id == patient_identifier
        )
    )


# --------------------------------------------------
# GET PATIENT BY USER ID
# --------------------------------------------------

def get_patient_by_user_id(
    db: Session,
    user_id: int,
) -> Patient | None:
    """
    Find the patient linked to a MediMind user account.
    """

    return db.scalar(
        select(Patient).where(
            Patient.user_id == user_id
        )
    )


# --------------------------------------------------
# LIST PATIENTS
# --------------------------------------------------

def get_patients(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[Patient], int]:
    """
    Get a paginated list of patients.

    Supports:
    - Search by patient ID
    - Search by first name
    - Search by last name
    - Search by phone
    - Filter by active status
    """

    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    query = select(Patient)

    # Search
    if search:
        search_pattern = f"%{search}%"

        query = query.where(
            or_(
                Patient.patient_id.ilike(search_pattern),
                Patient.first_name.ilike(search_pattern),
                Patient.last_name.ilike(search_pattern),
                Patient.phone.ilike(search_pattern),
            )
        )

    # Active status filter
    if is_active is not None:
        query = query.where(
            Patient.is_active == is_active
        )

    # Total count
    count_query = select(
        func.count()
    ).select_from(
        query.subquery()
    )

    total = db.scalar(count_query) or 0

    # Pagination
    offset = (page - 1) * page_size

    query = (
        query
        .order_by(Patient.id.desc())
        .offset(offset)
        .limit(page_size)
    )

    patients = list(
        db.scalars(query).all()
    )

    return patients, total


# --------------------------------------------------
# UPDATE PATIENT
# --------------------------------------------------

def update_patient(
    db: Session,
    patient: Patient,
    patient_data: PatientUpdate,
) -> Patient:
    """
    Update an existing patient.

    Only fields provided by the request are changed.
    """

    update_data = patient_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    return patient


# --------------------------------------------------
# UPDATE PATIENT STATUS
# --------------------------------------------------

def update_patient_status(
    db: Session,
    patient: Patient,
    is_active: bool,
) -> Patient:
    """
    Activate or deactivate a patient.
    """

    patient.is_active = is_active

    db.commit()
    db.refresh(patient)

    return patient


# --------------------------------------------------
# DELETE PATIENT
# --------------------------------------------------

def delete_patient(
    db: Session,
    patient: Patient,
) -> None:
    """
    Permanently delete a patient.

    This should normally be restricted to authorized
    administrative users.
    """

    db.delete(patient)
    db.commit()