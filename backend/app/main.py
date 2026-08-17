from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.patient import router as patient_router


app = FastAPI(
    title="MediMind AI Backend",
    description="AI-Powered Hospital Intelligence System",
    version="1.0.0",
)


# --------------------------------------------------
# INCLUDE ROUTERS
# --------------------------------------------------

app.include_router(auth_router)
app.include_router(patient_router)


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Welcome to MediMind AI Backend 🚀",
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
async def health():
    return {
        "success": True,
        "message": "Application is healthy",
        "data": {
            "status": "running",
        },
    }