from typing import List, Optional
from pydantic import BaseModel


class DepartmentOverviewStats(BaseModel):
    department_id: int
    department_name: str
    doctors_count: int
    patients_count: int
    total_appointments: int
    scheduled_appointments: int
    completed_appointments: int
    lab_orders_count: int
    pharmacy_dispenses_count: int
    active_admissions_count: int
    total_beds: int
    occupied_beds: int
    bed_occupancy_rate: float


class DepartmentDoctorSummary(BaseModel):
    id: int
    name: str
    specialization: str
    doctor_id_code: str
    contact: Optional[str] = None
    is_available: bool


class DepartmentOverviewResponse(BaseModel):
    stats: DepartmentOverviewStats
    doctors: List[DepartmentDoctorSummary]
