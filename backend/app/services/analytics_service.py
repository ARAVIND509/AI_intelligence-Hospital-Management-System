from datetime import date, datetime, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.appointment import Appointment
from app.models.laboratory import LabOrder
from app.models.pharmacy import PharmacyDispense, PharmacyDispenseItem
from app.models.billing import Billing, PaymentTransaction
from app.models.admission import Admission, Ward, Bed
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    DoctorWorkloadSummary,
    DepartmentPerformanceSummary,
)


class AnalyticsService:
    def get_hospital_analytics_overview(self, db: Session) -> AnalyticsOverviewResponse:
        now = datetime.now(timezone.utc)
        today = date.today()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        # Patients
        total_patients = db.query(Patient).count()
        new_patients_today = db.query(Patient).filter(Patient.created_at >= datetime.combine(today, datetime.min.time())).count()

        # Appointments / Visits
        total_appointments = db.query(Appointment).count()
        scheduled_appointments = db.query(Appointment).filter(Appointment.status == "scheduled").count()
        completed_appointments = db.query(Appointment).filter(Appointment.status == "completed").count()

        visits_today = db.query(Appointment).filter(Appointment.appointment_date == today).count()
        visits_this_week = db.query(Appointment).filter(Appointment.created_at >= seven_days_ago).count()
        visits_this_month = db.query(Appointment).filter(Appointment.created_at >= thirty_days_ago).count()

        # Financial Revenue
        total_revenue_res = db.query(func.sum(Billing.net_amount)).filter(Billing.payment_status == "paid").scalar()
        total_revenue = float(total_revenue_res or 0.0)

        revenue_today_res = db.query(func.sum(PaymentTransaction.amount)).filter(
            PaymentTransaction.created_at >= datetime.combine(today, datetime.min.time()),
            PaymentTransaction.transaction_type == "PAYMENT"
        ).scalar()
        revenue_today = float(revenue_today_res or 0.0)

        revenue_this_month_res = db.query(func.sum(PaymentTransaction.amount)).filter(
            PaymentTransaction.created_at >= thirty_days_ago,
            PaymentTransaction.transaction_type == "PAYMENT"
        ).scalar()
        revenue_this_month = float(revenue_this_month_res or 0.0)

        # Laboratory
        total_lab_orders = db.query(LabOrder).count()
        completed_lab_orders = db.query(LabOrder).filter(LabOrder.status == "COMPLETED").count()

        # Pharmacy
        total_dispenses = db.query(PharmacyDispense).count()
        pharm_rev_res = db.query(func.sum(PharmacyDispense.total_amount)).scalar()
        total_dispense_revenue = float(pharm_rev_res or 0.0)

        # Admissions & Beds
        active_admissions = db.query(Admission).filter(Admission.status == "ADMITTED").count()
        discharges_today = db.query(Admission).filter(
            Admission.status == "DISCHARGED",
            Admission.discharge_date >= datetime.combine(today, datetime.min.time())
        ).count()

        total_beds = db.query(Bed).count()
        occupied_beds = db.query(Bed).filter(Bed.status == "OCCUPIED").count()
        bed_occupancy_rate = round((occupied_beds / total_beds * 100), 2) if total_beds > 0 else 0.0

        return AnalyticsOverviewResponse(
            total_patients=total_patients,
            new_patients_today=new_patients_today,
            visits_today=visits_today,
            visits_this_week=visits_this_week,
            visits_this_month=visits_this_month,
            total_appointments=total_appointments,
            scheduled_appointments=scheduled_appointments,
            completed_appointments=completed_appointments,
            total_revenue=total_revenue,
            revenue_today=revenue_today,
            revenue_this_month=revenue_this_month,
            total_lab_orders=total_lab_orders,
            completed_lab_orders=completed_lab_orders,
            total_dispenses=total_dispenses,
            total_dispense_revenue=total_dispense_revenue,
            active_admissions=active_admissions,
            discharges_today=discharges_today,
            total_beds=total_beds,
            occupied_beds=occupied_beds,
            bed_occupancy_rate=bed_occupancy_rate,
        )

    def get_doctor_workload_summary(self, db: Session) -> List[DoctorWorkloadSummary]:
        doctors = db.query(Doctor).all()
        result = []
        for doc in doctors:
            dept_name = doc.department.name if doc.department else "General"
            total_apts = db.query(Appointment).filter(Appointment.doctor_id == doc.id).count()
            completed_apts = db.query(Appointment).filter(Appointment.doctor_id == doc.id, Appointment.status == "completed").count()
            pending_apts = db.query(Appointment).filter(Appointment.doctor_id == doc.id, Appointment.status == "scheduled").count()
            completion_rate = round((completed_apts / total_apts * 100), 2) if total_apts > 0 else 0.0

            result.append(DoctorWorkloadSummary(
                doctor_id=doc.id,
                doctor_name=doc.name,
                specialization=doc.specialization or "General Physician",
                department_name=dept_name,
                total_appointments=total_apts,
                completed_appointments=completed_apts,
                pending_appointments=pending_apts,
                completion_rate=completion_rate,
            ))
        return result

    def get_department_performance_summary(self, db: Session) -> List[DepartmentPerformanceSummary]:
        departments = db.query(Department).all()
        result = []
        for dept in departments:
            doc_ids = [d.id for d in dept.doctors]
            total_doctors = len(doc_ids)
            total_apts = db.query(Appointment).filter(Appointment.doctor_id.in_(doc_ids)).count() if doc_ids else 0
            total_admissions = db.query(Admission).filter(Admission.department_id == dept.id).count()
            total_lab_orders = db.query(LabOrder).filter(LabOrder.doctor_id.in_(doc_ids)).count() if doc_ids else 0

            # Revenue generated by department appointments/bills
            revenue_res = db.query(func.sum(Billing.net_amount)).filter(
                Billing.appointment_id.in_([a.id for a in db.query(Appointment).filter(Appointment.doctor_id.in_(doc_ids)).all()])
            ).scalar() if doc_ids else 0.0

            result.append(DepartmentPerformanceSummary(
                department_id=dept.id,
                department_name=dept.name,
                total_doctors=total_doctors,
                total_appointments=total_apts,
                total_admissions=total_admissions,
                total_lab_orders=total_lab_orders,
                revenue_generated=float(revenue_res or 0.0),
            ))
        return result


analytics_service = AnalyticsService()
