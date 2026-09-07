from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
from app.models.laboratory import LabOrder
from app.models.appointment import Appointment
from app.schemas.analytics import (
    AIHealthSummaryResponse,
    AILabExplanationRequest,
    AILabExplanationResponse,
)


class AISummaryEngine:
    def generate_patient_health_summary(
        self, db: Session, patient_id: int, doctor_notes: Optional[str] = None
    ) -> AIHealthSummaryResponse:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        # Gather clinical history
        records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).order_by(MedicalRecord.created_at.desc()).all()
        prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient_id).order_by(Prescription.created_at.desc()).all()
        lab_orders = db.query(LabOrder).filter(LabOrder.patient_id == patient_id).order_by(LabOrder.created_at.desc()).all()
        appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).order_by(Appointment.created_at.desc()).all()

        # 1. Previous Conditions
        previous_conditions = []
        if patient.medical_history:
            previous_conditions.append(patient.medical_history)
        for r in records:
            if r.diagnosis and r.diagnosis not in previous_conditions:
                previous_conditions.append(r.diagnosis)
        if not previous_conditions:
            previous_conditions.append("No prior chronic conditions recorded.")

        # 2. Recent Lab Results
        recent_lab_results = []
        has_abnormal_lab = False
        for order in lab_orders[:5]:
            test_name = order.test_catalog.test_name if order.test_catalog else "Lab Order"
            for res in order.results:
                status_str = "ABNORMAL" if res.is_abnormal else "Normal"
                if res.is_abnormal:
                    has_abnormal_lab = True
                recent_lab_results.append(f"{test_name}: {res.result_value} ({status_str})")
        if not recent_lab_results:
            recent_lab_results.append("No recent laboratory investigations.")

        # 3. Current Medications
        current_medications = []
        for rx in prescriptions[:3]:
            for med in rx.medicines:
                current_medications.append(f"{med.medicine_name} {med.dosage} ({med.frequency})")
        if not current_medications:
            current_medications.append("No active prescriptions.")

        # 4. Recent Visits
        recent_visits = []
        for apt in appointments[:3]:
            doc_name = apt.doctor.name if apt.doctor else "Doctor"
            recent_visits.append(f"{apt.appointment_date} with {doc_name} - Reason: {apt.reason or 'Consultation'}")
        if not recent_visits:
            recent_visits.append("No visit history logged.")

        # 5. Key Clinical Trends & Recommendation
        trends = []
        if has_abnormal_lab:
            trends.append("Abnormal lab parameters detected requiring physician review.")
        if len(records) > 2:
            trends.append("Multiple clinical encounters recorded over recent months.")
        if not trends:
            trends.append("Patient clinical status appears stable based on recorded parameters.")

        doctor_review_recommended = has_abnormal_lab or (len(records) >= 3)

        return AIHealthSummaryResponse(
            patient_id=patient.id,
            patient_name=patient.name,
            summary_date=datetime.now(timezone.utc),
            previous_conditions=previous_conditions,
            recent_lab_results=recent_lab_results,
            current_medications=current_medications,
            recent_visits=recent_visits,
            key_clinical_trends=trends,
            doctor_review_recommended=doctor_review_recommended,
            ai_disclaimer="AI assists doctors by summarizing records; it does not replace clinical medical judgment."
        )

    def explain_lab_result(self, req: AILabExplanationRequest) -> AILabExplanationResponse:
        test_lower = req.test_name.lower()
        val_lower = req.result_value.lower()

        explanation = ""
        clinical_context = ""
        next_steps = []

        if "hemoglobin" in test_lower or "hgb" in test_lower:
            if req.is_abnormal or "low" in val_lower or "10." in val_lower or "9." in val_lower:
                explanation = "This Hemoglobin value appears below typical adult reference ranges, which may indicate mild-to-moderate anemia or reduced oxygen-carrying capacity."
                clinical_context = "Hemoglobin reflects red blood cell count. Low values can stem from iron deficiency, chronic blood loss, or nutritional factors."
                next_steps = ["Order Serum Ferritin / Iron Profile", "Evaluate patient for fatigue or pallor", "Review dietary iron intake"]
            else:
                explanation = "Hemoglobin value falls within normal physiological parameters."
                clinical_context = "Adequate red blood cell oxygenation."
                next_steps = ["Continue routine health monitoring"]
        elif "glucose" in test_lower or "sugar" in test_lower:
            if req.is_abnormal or "high" in val_lower or "140" in val_lower or "200" in val_lower:
                explanation = "Elevated blood glucose level observed, which may suggest impaired glucose tolerance or hyperglycemia."
                clinical_context = "Sustained high glucose requires clinical assessment for metabolic conditions such as Diabetes Mellitus."
                next_steps = ["Order HbA1c test for 3-month glycemic average", "Assess fasting blood sugar", "Recommend lifestyle and dietary modifications"]
            else:
                explanation = "Blood glucose levels are within expected reference range."
                clinical_context = "Normal glycemic control."
                next_steps = ["Standard annual checkup"]
        elif "ecg" in test_lower or "tachycardia" in val_lower:
            explanation = "ECG readout shows heart rate or rhythm variation outside resting baseline."
            clinical_context = "Transient elevation in heart rate can be physiological (stress, exertion) or cardiac in origin."
            next_steps = ["Correlate with pulse & blood pressure", "Review for electrolyte imbalance", "Cardiology consultation if symptomatic"]
        else:
            if req.is_abnormal:
                explanation = f"The reported value ({req.result_value}) for {req.test_name} deviates from normal reference range ({req.reference_range or 'Standard Range'})."
                clinical_context = "Abnormal result requires clinical evaluation alongside patient symptoms and medical history."
                next_steps = ["Correlate with clinical symptoms", "Consider repeating lab test if clinically indicated", "Doctor review recommended"]
            else:
                explanation = f"{req.test_name} result ({req.result_value}) is within standard reference ranges."
                clinical_context = "Normal findings recorded."
                next_steps = ["Routine follow-up as scheduled"]

        return AILabExplanationResponse(
            test_name=req.test_name,
            result_value=req.result_value,
            reference_range=req.reference_range,
            explanation=explanation,
            clinical_context=clinical_context,
            recommended_next_steps=next_steps,
            ai_disclaimer="AI lab explanation provides clinical decision-support only; all decisions must be verified by a licensed doctor."
        )


ai_summary_engine = AISummaryEngine()
