from datetime import datetime
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
from app.models.laboratory import LabOrder, LabResult
from app.models.pharmacy import PharmacyDispense
from app.models.admission import Admission
from app.schemas.analytics import (
    PatientAnalyticsResponse,
    PatientTimelineEvent,
    PatientLabTrendItem,
)


class PatientAnalyticsService:
    def get_patient_analytics(self, db: Session, patient_id: int) -> PatientAnalyticsResponse:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        # 1. Appointments & Medical Records
        appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).order_by(Appointment.created_at.desc()).all()
        medical_records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).order_by(MedicalRecord.created_at.desc()).all()
        prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient_id).order_by(Prescription.created_at.desc()).all()
        lab_orders = db.query(LabOrder).filter(LabOrder.patient_id == patient_id).order_by(LabOrder.created_at.desc()).all()
        dispenses = db.query(PharmacyDispense).filter(PharmacyDispense.patient_id == patient_id).order_by(PharmacyDispense.created_at.desc()).all()
        admissions = db.query(Admission).filter(Admission.patient_id == patient_id).order_by(Admission.created_at.desc()).all()

        total_visits = len(appointments)
        total_prescriptions = len(prescriptions)
        total_lab_tests = len(lab_orders)
        total_admissions = len(admissions)

        # 2. Lab trends and abnormal lab count
        abnormal_count = 0
        lab_trends = []
        for order in lab_orders:
            for res in order.results:
                if res.is_abnormal:
                    abnormal_count += 1
                lab_trends.append(PatientLabTrendItem(
                    order_number=order.order_number,
                    test_name=order.test_catalog.test_name if order.test_catalog else "Lab Test",
                    result_value=res.result_value,
                    reference_range=res.reference_range,
                    is_abnormal=res.is_abnormal,
                    date=res.created_at,
                ))

        # 3. Timeline Events Generation
        timeline: List[PatientTimelineEvent] = []
        for apt in appointments:
            timeline.append(PatientTimelineEvent(
                event_type="APPOINTMENT",
                timestamp=apt.created_at,
                title=f"Appointment #{apt.apt_id} ({apt.status.upper()})",
                details={
                    "doctor": apt.doctor.name if apt.doctor else "N/A",
                    "date": str(apt.appointment_date),
                    "reason": apt.reason or "Routine Visit"
                }
            ))

        for mr in medical_records:
            timeline.append(PatientTimelineEvent(
                event_type="MEDICAL_RECORD",
                timestamp=mr.created_at,
                title=f"Diagnosis: {mr.diagnosis or 'Clinical Consultation'}",
                details={
                    "symptoms": mr.symptoms or "None noted",
                    "doctor_notes": mr.notes or ""
                }
            ))

        for order in lab_orders:
            timeline.append(PatientTimelineEvent(
                event_type="LAB_ORDER",
                timestamp=order.created_at,
                title=f"Lab Order #{order.order_number} ({order.status})",
                details={
                    "test_name": order.test_catalog.test_name if order.test_catalog else "Lab Test",
                    "priority": order.priority
                }
            ))

        for dsp in dispenses:
            timeline.append(PatientTimelineEvent(
                event_type="DISPENSE",
                timestamp=dsp.dispensed_at,
                title=f"Pharmacy Dispense #{dsp.dispense_number}",
                details={
                    "total_amount": dsp.total_amount,
                    "items_count": len(dsp.items)
                }
            ))

        for adm in admissions:
            timeline.append(PatientTimelineEvent(
                event_type="ADMISSION",
                timestamp=adm.admission_date,
                title=f"Hospital Admission #{adm.admission_number} ({adm.status})",
                details={
                    "reason": adm.reason_for_admission or "Hospitalization",
                    "bed": adm.bed.bed_number if adm.bed else "N/A"
                }
            ))

        # Sort timeline by timestamp descending
        timeline.sort(key=lambda x: x.timestamp, reverse=True)

        # 4. Risk Assessment Calculation
        risk_indicators = []
        if abnormal_count >= 2:
            risk_indicators.append(f"{abnormal_count} abnormal lab results recorded")
        if total_admissions >= 2:
            risk_indicators.append(f"Multiple admissions ({total_admissions} active/past admissions)")
        if any(a.status == "cancelled" for a in appointments):
            risk_indicators.append("History of cancelled appointments")

        risk_level = "LOW"
        if len(risk_indicators) == 1:
            risk_level = "MODERATE"
        elif len(risk_indicators) >= 2:
            risk_level = "HIGH"

        if not risk_indicators:
            risk_indicators.append("No active health risk flags detected")

        return PatientAnalyticsResponse(
            patient_id=patient.id,
            patient_name=patient.name,
            age=patient.age,
            gender=patient.gender,
            total_visits=total_visits,
            total_prescriptions=total_prescriptions,
            total_lab_tests=total_lab_tests,
            abnormal_lab_count=abnormal_count,
            total_admissions=total_admissions,
            risk_level=risk_level,
            risk_indicators=risk_indicators,
            lab_trends=lab_trends,
            timeline=timeline,
        )


patient_analytics_service = PatientAnalyticsService()
