from fastapi import APIRouter

from app.api.v1.routes import health
from app.api.v1.endpoints import (
    auth,
    departments,
    patients,
    doctors,
    appointments,
    medical_records,
    prescriptions,
    billing,
    laboratory,
    pharmacy,
    admissions,
    department_head,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router)
api_router.include_router(departments.router)
api_router.include_router(patients.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(medical_records.router)
api_router.include_router(prescriptions.router)
api_router.include_router(billing.router)
api_router.include_router(laboratory.router)
api_router.include_router(pharmacy.router)
api_router.include_router(admissions.router)
api_router.include_router(department_head.router)
