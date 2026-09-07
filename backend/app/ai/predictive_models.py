from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.admission import Admission, Bed
from app.models.pharmacy import MedicineInventory, PharmacyDispenseItem
from app.models.laboratory import LabOrder
from app.schemas.analytics import (
    NoShowPredictionRequest,
    NoShowPredictionResponse,
    ReadmissionRiskRequest,
    ReadmissionRiskResponse,
    BedOccupancyForecastResponse,
    MedicineDemandForecastItem,
    LabWorkloadForecastResponse,
)


class AIPredictiveEngine:
    def predict_appointment_no_show(
        self, db: Session, req: NoShowPredictionRequest
    ) -> NoShowPredictionResponse:
        risk_score = 0.1
        factors = []

        # 1. Lead time factor (booking date to appointment date)
        days_ahead = (req.appointment_date - date.today()).days
        if days_ahead > 14:
            risk_score += 0.25
            factors.append("Appointment booked >14 days in advance (high lead time)")
        elif days_ahead > 7:
            risk_score += 0.15
            factors.append("Appointment booked >7 days in advance")

        # 2. Patient appointment history
        past_apts = db.query(Appointment).filter(Appointment.patient_id == req.patient_id).all()
        if past_apts:
            cancelled_count = len([a for a in past_apts if a.status == "cancelled"])
            completed_count = len([a for a in past_apts if a.status == "completed"])
            if cancelled_count > 0:
                c_ratio = cancelled_count / len(past_apts)
                risk_score += min(0.4, c_ratio * 0.5)
                factors.append(f"Past cancellation rate: {round(c_ratio * 100)}%")
            if completed_count > 2:
                risk_score = max(0.05, risk_score - 0.15)
                factors.append("Good past attendance record")
        else:
            factors.append("First-time appointment (no prior history)")

        # Cap score between 0.05 and 0.95
        risk_score = round(min(0.95, max(0.05, risk_score)), 2)

        category = "LOW"
        suggested_action = "Standard automated SMS reminder 24h prior."
        if risk_score >= 0.5:
            category = "HIGH"
            suggested_action = "Send phone call confirmation & send SMS reminder 2h before slot."
        elif risk_score >= 0.3:
            category = "MEDIUM"
            suggested_action = "Send 24h and 4h SMS & WhatsApp reminders."

        return NoShowPredictionResponse(
            patient_id=req.patient_id,
            no_show_risk_score=risk_score,
            risk_category=category,
            risk_factors=factors,
            suggested_action=suggested_action,
        )

    def predict_readmission_risk(
        self, db: Session, req: ReadmissionRiskRequest
    ) -> ReadmissionRiskResponse:
        risk_score = 0.15
        factors = []
        recommendations = []

        # 1. Length of Stay Factor
        if req.length_of_stay_days >= 7:
            risk_score += 0.30
            factors.append(f"Prolonged length of stay ({req.length_of_stay_days} days)")
        elif req.length_of_stay_days <= 1 and req.admission_type == "EMERGENCY":
            risk_score += 0.20
            factors.append("Short emergency stay (potential premature discharge)")

        # 2. Admission Type
        if req.admission_type == "EMERGENCY":
            risk_score += 0.15
            factors.append("Emergency admission classification")

        # 3. Patient Age
        patient = db.query(Patient).filter(Patient.id == req.patient_id).first()
        age = req.age or (patient.age if patient else 30)
        if age and age >= 65:
            risk_score += 0.20
            factors.append("Senior age group (>= 65 years)")

        # 4. Past Admissions Count
        past_admissions = db.query(Admission).filter(Admission.patient_id == req.patient_id).count()
        if past_admissions > 1:
            risk_score += 0.20
            factors.append(f"Multiple prior hospitalizations ({past_admissions} total)")

        risk_score = round(min(0.95, max(0.05, risk_score)), 2)

        category = "LOW"
        if risk_score >= 0.6:
            category = "HIGH"
            recommendations = [
                "Schedule post-discharge nurse follow-up call within 48 hours",
                "Ensure clear medication reconciliation at discharge",
                "Arrange outpatient follow-up appointment within 7 days"
            ]
        elif risk_score >= 0.35:
            category = "MEDIUM"
            recommendations = [
                "Provide detailed discharge instructions to caregiver",
                "Schedule follow-up appointment within 14 days"
            ]
        else:
            recommendations = ["Standard post-discharge advice and medication schedule"]

        return ReadmissionRiskResponse(
            patient_id=req.patient_id,
            readmission_risk_score=risk_score,
            risk_category=category,
            contributing_factors=factors,
            prevention_recommendations=recommendations,
        )

    def forecast_bed_occupancy(self, db: Session, days: int = 7) -> BedOccupancyForecastResponse:
        total_beds = db.query(Bed).count()
        occupied_beds = db.query(Bed).filter(Bed.status == "OCCUPIED").count()
        curr_rate = round((occupied_beds / total_beds * 100), 2) if total_beds > 0 else 0.0

        daily_forecast = []
        today = date.today()
        forecasted_rate = curr_rate

        for i in range(1, days + 1):
            future_date = today + timedelta(days=i)
            # Simulated projection based on active admissions trend
            proj_occ = max(0, min(total_beds, occupied_beds + (i % 3 - 1)))
            proj_rate = round((proj_occ / total_beds * 100), 2) if total_beds > 0 else 0.0
            forecasted_rate = proj_rate
            daily_forecast.append({
                "date": str(future_date),
                "forecasted_occupied_beds": proj_occ,
                "total_beds": total_beds,
                "occupancy_rate": proj_rate
            })

        trend = "STABLE"
        if forecasted_rate > curr_rate + 5:
            trend = "INCREASING"
        elif forecasted_rate < curr_rate - 5:
            trend = "DECREASING"

        return BedOccupancyForecastResponse(
            forecast_days=days,
            current_occupancy_rate=curr_rate,
            forecasted_occupancy_rate=forecasted_rate,
            trend=trend,
            daily_forecast=daily_forecast,
        )

    def forecast_medicine_demand(self, db: Session) -> List[MedicineDemandForecastItem]:
        medicines = db.query(MedicineInventory).all()
        result = []
        for med in medicines:
            # Total quantity dispensed in last 30 days
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            total_dispensed = db.query(func.sum(PharmacyDispenseItem.quantity)).filter(
                PharmacyDispenseItem.medicine_id == med.id,
                PharmacyDispenseItem.id.in_(
                    [item.id for item in db.query(PharmacyDispenseItem).all() if item.dispense and item.dispense.dispensed_at >= thirty_days_ago]
                )
            ).scalar() or 0

            avg_daily = round(max(0.5, total_dispensed / 30.0), 2)
            days_remaining = round(med.stock_quantity / avg_daily, 1) if avg_daily > 0 else 999.0
            reorder = med.stock_quantity <= med.reorder_level or days_remaining < 7.0
            rec_qty = max(0, (med.reorder_level * 3) - med.stock_quantity) if reorder else 0

            result.append(MedicineDemandForecastItem(
                medicine_id=med.id,
                medicine_name=med.name,
                current_stock=med.stock_quantity,
                avg_daily_consumption=avg_daily,
                days_of_supply_remaining=days_remaining,
                reorder_recommended=reorder,
                recommended_order_quantity=rec_qty,
            ))
        return result

    def forecast_lab_workload(self, db: Session) -> LabWorkloadForecastResponse:
        today = date.today()
        daily_trend = []
        total_forecasted = 0
        recent_daily_avg = db.query(LabOrder).count() / 7.0

        for i in range(1, 8):
            future_date = today + timedelta(days=i)
            # Projection factor
            proj_volume = int(max(5, round(recent_daily_avg * (1.0 + (i % 2 * 0.1)))))
            total_forecasted += proj_volume
            daily_trend.append({
                "date": str(future_date),
                "forecasted_lab_orders": proj_volume
            })

        return LabWorkloadForecastResponse(
            total_forecasted_orders_next_7_days=total_forecasted,
            daily_lab_order_trend=daily_trend,
        )


ai_predictive_engine = AIPredictiveEngine()
