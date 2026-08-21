from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate


# ==================================================
# GENERATE DOCTOR ID
# ==================================================

def generate_doctor_id(db: Session) -> str:
    """
    Generate a hospital doctor identifier.

    Examples:
        DR-000001
        DR-000002
        DR-000003
    """

    last_doctor_id = db.scalar(
        select(Doctor.doctor_id)
        .order_by(Doctor.id.desc())
        .limit(1)
    )

    if not last_doctor_id:
        return "DR-000001"

    try:
        last_number = int(
            last_doctor_id.split("-")[-1]
        )
    except (ValueError, IndexError):
        last_number = 0

    return f"DR-{last_number + 1:06d}"


# ==================================================
# CREATE DOCTOR
# ==================================================

def create_doctor(
    db: Session,
    doctor_data: DoctorCreate,
) -> Doctor:
    """
    Create and save a new doctor.
    """

    doctor = Doctor(
        doctor_id=generate_doctor_id(db),
        user_id=doctor_data.user_id,
        first_name=doctor_data.first_name,
        last_name=doctor_data.last_name,
        date_of_birth=doctor_data.date_of_birth,
        gender=doctor_data.gender,
        specialization=doctor_data.specialization,
        qualification=doctor_data.qualification,
        experience_years=doctor_data.experience_years,
        license_number=doctor_data.license_number,
        phone=doctor_data.phone,
        email=doctor_data.email,
        address=doctor_data.address,
        department=doctor_data.department,
        consultation_fee=doctor_data.consultation_fee,
        is_available=True,
        is_active=True,
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


# ==================================================
# GET DOCTOR BY DATABASE ID
# ==================================================

def get_doctor_by_id(
    db: Session,
    doctor_id: int,
) -> Doctor | None:
    """
    Get a doctor using the database primary key.
    """

    return db.scalar(
        select(Doctor).where(
            Doctor.id == doctor_id
        )
    )


# ==================================================
# GET DOCTOR BY HOSPITAL DOCTOR ID
# ==================================================

def get_doctor_by_doctor_id(
    db: Session,
    doctor_identifier: str,
) -> Doctor | None:
    """
    Get a doctor using the hospital doctor ID.

    Example:
        DR-000001
    """

    return db.scalar(
        select(Doctor).where(
            Doctor.doctor_id == doctor_identifier
        )
    )


# ==================================================
# GET DOCTOR BY USER ID
# ==================================================

def get_doctor_by_user_id(
    db: Session,
    user_id: int,
) -> Doctor | None:
    """
    Find the doctor linked to a MediMind user account.
    """

    return db.scalar(
        select(Doctor).where(
            Doctor.user_id == user_id
        )
    )


# ==================================================
# LIST DOCTORS
# ==================================================

def get_doctors(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    specialization: str | None = None,
    department: str | None = None,
    is_available: bool | None = None,
    is_active: bool | None = None,
) -> tuple[list[Doctor], int]:
    """
    Get a paginated list of doctors.

    Supports:

    - Search by doctor ID
    - Search by first name
    - Search by last name
    - Search by phone
    - Search by specialization
    - Filter by specialization
    - Filter by department
    - Filter by availability
    - Filter by active status
    """

    page = max(page, 1)
    page_size = min(
        max(page_size, 1),
        100,
    )

    query = select(Doctor)

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    if search:
        search_pattern = f"%{search}%"

        query = query.where(
            or_(
                Doctor.doctor_id.ilike(
                    search_pattern
                ),
                Doctor.first_name.ilike(
                    search_pattern
                ),
                Doctor.last_name.ilike(
                    search_pattern
                ),
                Doctor.phone.ilike(
                    search_pattern
                ),
                Doctor.specialization.ilike(
                    search_pattern
                ),
            )
        )

    # --------------------------------------------------
    # SPECIALIZATION FILTER
    # --------------------------------------------------

    if specialization:
        query = query.where(
            Doctor.specialization.ilike(
                specialization
            )
        )

    # --------------------------------------------------
    # DEPARTMENT FILTER
    # --------------------------------------------------

    if department:
        query = query.where(
            Doctor.department.ilike(
                department
            )
        )

    # --------------------------------------------------
    # AVAILABILITY FILTER
    # --------------------------------------------------

    if is_available is not None:
        query = query.where(
            Doctor.is_available == is_available
        )

    # --------------------------------------------------
    # ACTIVE STATUS FILTER
    # --------------------------------------------------

    if is_active is not None:
        query = query.where(
            Doctor.is_active == is_active
        )

    # --------------------------------------------------
    # TOTAL COUNT
    # --------------------------------------------------

    count_query = select(
        func.count()
    ).select_from(
        query.subquery()
    )

    total = db.scalar(count_query) or 0

    # --------------------------------------------------
    # PAGINATION
    # --------------------------------------------------

    offset = (page - 1) * page_size

    query = (
        query
        .order_by(Doctor.id.desc())
        .offset(offset)
        .limit(page_size)
    )

    doctors = list(
        db.scalars(query).all()
    )

    return doctors, total


# ==================================================
# UPDATE DOCTOR
# ==================================================

def update_doctor(
    db: Session,
    doctor: Doctor,
    doctor_data: DoctorUpdate,
) -> Doctor:
    """
    Update an existing doctor.

    Only fields provided by the request
    are changed.
    """

    update_data = doctor_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            doctor,
            field,
            value,
        )

    db.commit()
    db.refresh(doctor)

    return doctor


# ==================================================
# UPDATE DOCTOR STATUS
# ==================================================

def update_doctor_status(
    db: Session,
    doctor: Doctor,
    is_active: bool,
) -> Doctor:
    """
    Activate or deactivate a doctor.
    """

    doctor.is_active = is_active

    db.commit()
    db.refresh(doctor)

    return doctor


# ==================================================
# UPDATE DOCTOR AVAILABILITY
# ==================================================

def update_doctor_availability(
    db: Session,
    doctor: Doctor,
    is_available: bool,
) -> Doctor:
    """
    Mark a doctor as available or unavailable.
    """

    doctor.is_available = is_available

    db.commit()
    db.refresh(doctor)

    return doctor


# ==================================================
# DELETE DOCTOR
# ==================================================

def delete_doctor(
    db: Session,
    doctor: Doctor,
) -> None:
    """
    Permanently delete a doctor.

    This should normally be restricted to
    authorized administrative users.
    """

    db.delete(doctor)
    db.commit()