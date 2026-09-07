from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.laboratory import LabOrder, LabTestCatalog
from app.models.pharmacy import PharmacyDispense
from app.models.admission import Admission, Ward, Bed
from app.schemas.department_head import (
    DepartmentOverviewResponse,
    DepartmentOverviewStats,
    DepartmentDoctorSummary,
)


class DepartmentHeadService:
    def get_department_overview(self, db: Session, department_id: int) -> DepartmentOverviewResponse:
        dept = db.query(Department).filter(Department.id == department_id).first()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

        doctors = db.query(Doctor).filter(Doctor.department_id == department_id).all()
        doc_ids = [d.id for d in doctors]

        doctors_count = len(doctors)

        # Department appointments
        appointments = db.query(Appointment).filter(Appointment.doctor_id.in_(doc_ids)).all() if doc_ids else []
        total_appointments = len(appointments)
        scheduled_appointments = len([a for a in appointments if a.status == "scheduled"])
        completed_appointments = len([a for a in appointments if a.status == "completed"])

        # Patient count associated with department doctors
        patient_ids = list(set([a.patient_id for a in appointments]))
        patients_count = len(patient_ids)

        # Department lab orders
        lab_orders = db.query(LabOrder).filter(LabOrder.doctor_id.in_(doc_ids)).all() if doc_ids else []
        lab_orders_count = len(lab_orders)

        # Active Admissions in Wards belonging to this Department
        wards = db.query(Ward).filter(Ward.department_id == department_id).all()
        ward_ids = [w.id for w in wards]

        beds = db.query(Bed).filter(Bed.ward_id.in_(ward_ids)).all() if ward_ids else []
        total_beds = len(beds)
        occupied_beds = len([b for b in beds if b.status == "OCCUPIED"])
        bed_occupancy_rate = round((occupied_beds / total_beds * 100), 2) if total_beds > 0 else 0.0

        active_admissions_count = db.query(Admission).filter(
            Admission.department_id == department_id, Admission.status == "ADMITTED"
        ).count()

        # Pharmacy dispenses count for department patients
        pharmacy_dispenses_count = db.query(PharmacyDispense).filter(
            PharmacyDispense.patient_id.in_(patient_ids)
        ).count() if patient_ids else 0

        stats = DepartmentOverviewStats(
            department_id=dept.id,
            department_name=dept.name,
            doctors_count=doctors_count,
            patients_count=patients_count,
            total_appointments=total_appointments,
            scheduled_appointments=scheduled_appointments,
            completed_appointments=completed_appointments,
            lab_orders_count=lab_orders_count,
            pharmacy_dispenses_count=pharmacy_dispenses_count,
            active_admissions_count=active_admissions_count,
            total_beds=total_beds,
            occupied_beds=occupied_beds,
            bed_occupancy_rate=bed_occupancy_rate,
        )

        doc_summaries = [
            DepartmentDoctorSummary(
                id=d.id,
                name=d.name,
                specialization=d.specialization or "",
                doctor_id_code=f"DOC-{d.id}",
                contact=d.phone,
                is_available=d.is_available,
            )
            for d in doctors
        ]

        return DepartmentOverviewResponse(stats=stats, doctors=doc_summaries)


department_head_service = DepartmentHeadService()
