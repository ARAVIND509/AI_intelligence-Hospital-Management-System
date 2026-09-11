from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.constants import APP_DESCRIPTION
from app.core.database import Base, engine
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.core.openapi import custom_openapi
from app.models import *  # Import all models so SQLAlchemy can create tables

# ----------------------------
# Create FastAPI App
# ----------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs" if settings.DEBUG or settings.ENVIRONMENT != "production" else "/docs",
    redoc_url="/redoc" if settings.DEBUG or settings.ENVIRONMENT != "production" else "/redoc",
    contact={
        "name": "Aravind Kumar",
        "email": "admin@hospital.local",
    },
    license_info={
        "name": "Proprietary",
    },
)

# ----------------------------
# Custom OpenAPI
# ----------------------------
app.openapi = lambda: custom_openapi(app)

# ----------------------------
# Create Database Tables
# ----------------------------
Base.metadata.create_all(bind=engine)

from app.core.middleware import SecurityAndAuditMiddleware

app.add_middleware(SecurityAndAuditMiddleware)

# ----------------------------
# CORS Middleware
# ----------------------------
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Global Exception Handlers
# ----------------------------
app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)

# ----------------------------
# API Routes
# ----------------------------
app.include_router(
    api_router,
    prefix="/api/v1",
)

# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/", tags=["Root"])
async def root():
    return {
        "success": True,
        "message": "MediMind AI Backend is running successfully!"
    }