from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


# Hospital Analytics Dashboard Schemas
class AnalyticsOverviewResponse(BaseModel):
    total_patients: int
    new_patients_today: int
    visits_today: int
    visits_this_week: int
    visits_this_month: int
    total_appointments: int
    scheduled_appointments: int
    completed_appointments: int
    total_revenue: float
    revenue_today: float
    revenue_this_month: float
    total_lab_orders: int
    completed_lab_orders: int
    total_dispenses: int
    total_dispense_revenue: float
    active_admissions: int
    discharges_today: int
    total_beds: int
    occupied_beds: int
    bed_occupancy_rate: float


class DoctorWorkloadSummary(BaseModel):
    doctor_id: int
    doctor_name: str
    specialization: str
    department_name: str
    total_appointments: int
    completed_appointments: int
    pending_appointments: int
    completion_rate: float


class DepartmentPerformanceSummary(BaseModel):
    department_id: int
    department_name: str
    total_doctors: int
    total_appointments: int
    total_admissions: int
    total_lab_orders: int
    revenue_generated: float


# Patient Analytics Schemas
class PatientTimelineEvent(BaseModel):
    event_type: str  # APPOINTMENT, MEDICAL_RECORD, LAB_ORDER, DISPENSE, ADMISSION
    timestamp: datetime
    title: str
    details: Dict[str, Any]


class PatientLabTrendItem(BaseModel):
    order_number: str
    test_name: str
    result_value: str
    reference_range: Optional[str] = None
    is_abnormal: bool
    date: datetime


class PatientAnalyticsResponse(BaseModel):
    patient_id: int
    patient_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    total_visits: int
    total_prescriptions: int
    total_lab_tests: int
    abnormal_lab_count: int
    total_admissions: int
    risk_level: str  # LOW, MODERATE, HIGH
    risk_indicators: List[str]
    lab_trends: List[PatientLabTrendItem]
    timeline: List[PatientTimelineEvent]


# AI Feature Schemas
class AIHealthSummaryRequest(BaseModel):
    patient_id: int
    doctor_notes: Optional[str] = None


class AIHealthSummaryResponse(BaseModel):
    patient_id: int
    patient_name: str
    summary_date: datetime
    previous_conditions: List[str]
    recent_lab_results: List[str]
    current_medications: List[str]
    recent_visits: List[str]
    key_clinical_trends: List[str]
    doctor_review_recommended: bool
    ai_disclaimer: str


class AILabExplanationRequest(BaseModel):
    test_name: str
    result_value: str
    reference_range: Optional[str] = None
    is_abnormal: bool = False
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None


class AILabExplanationResponse(BaseModel):
    test_name: str
    result_value: str
    reference_range: Optional[str] = None
    explanation: str
    clinical_context: str
    recommended_next_steps: List[str]
    ai_disclaimer: str


# Predictive Analytics Schemas
class NoShowPredictionRequest(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: str
    appointment_type: Optional[str] = "OP"


class NoShowPredictionResponse(BaseModel):
    patient_id: int
    no_show_risk_score: float  # 0.0 to 1.0
    risk_category: str  # LOW, MEDIUM, HIGH
    risk_factors: List[str]
    suggested_action: str


class ReadmissionRiskRequest(BaseModel):
    patient_id: int
    length_of_stay_days: int
    admission_type: str
    primary_diagnosis: Optional[str] = None
    age: Optional[int] = None


class ReadmissionRiskResponse(BaseModel):
    patient_id: int
    readmission_risk_score: float  # 0.0 to 1.0
    risk_category: str  # LOW, MEDIUM, HIGH
    contributing_factors: List[str]
    prevention_recommendations: List[str]


class BedOccupancyForecastResponse(BaseModel):
    forecast_days: int
    current_occupancy_rate: float
    forecasted_occupancy_rate: float
    trend: str  # INCREASING, STABLE, DECREASING
    daily_forecast: List[Dict[str, Any]]


class MedicineDemandForecastItem(BaseModel):
    medicine_id: int
    medicine_name: str
    current_stock: int
    avg_daily_consumption: float
    days_of_supply_remaining: float
    reorder_recommended: bool
    recommended_order_quantity: int


class LabWorkloadForecastResponse(BaseModel):
    total_forecasted_orders_next_7_days: int
    daily_lab_order_trend: List[Dict[str, Any]]


# Hospital Report Schemas
class HospitalReportResponse(BaseModel):
    report_title: str
    generated_at: datetime
    report_type: str  # DAILY, MONTHLY, DEPARTMENT, REVENUE, PHARMACY, LABORATORY, PATIENT_STATS
    summary_metrics: Dict[str, Any]
    detailed_tables: List[Dict[str, Any]]
