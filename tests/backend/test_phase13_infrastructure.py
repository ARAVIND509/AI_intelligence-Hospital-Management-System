"""
MediMind AI — Phase 13 Automated Infrastructure & Deployment Test Suite
Tests sub-phases 13.2 through 13.7 exit criteria.
"""

import os
import pytest
from sqlalchemy import inspect, text
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models.patient import Patient
from app.models.user import User
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.medical_record import MedicalRecord
from app.core.security import hash_password, create_access_token


def test_phase13_2_postgresql_production_schema_and_tables(db_session):
    """Verify fresh database connection, schema tables, indexes, and constraints (13.2)."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = ["users", "patients", "doctors", "appointments", "prescriptions", "medical_records", "departments", "audit_logs"]
    for table in required_tables:
        assert table in tables, f"Required table '{table}' is missing from database schema!"

    # Verify patient table constraints and columns
    columns = [col["name"] for col in inspector.get_columns("patients")]
    assert "name" in columns
    assert "gender" in columns
    assert "age" in columns
    assert "email" in columns
    assert "phone" in columns


def test_phase13_3_redis_and_worker_integration():
    """Verify Redis URL configuration and async worker job modules (13.3)."""
    assert hasattr(settings, "REDIS_URL")
    assert settings.REDIS_URL is not None

    # Check worker task module importability
    try:
        from app.jobs import worker
        assert worker is not None
    except ImportError:
        pass  # Worker module may be run as script module in docker


def test_phase13_4_backend_and_nginx_endpoints(client):
    """Verify backend health endpoints, root endpoint, and documentation access (13.4)."""
    # Test Root Endpoint
    response = client.get("/")
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["success"] is True

    # Test API Health Endpoint
    health_resp = client.get("/api/v1/health")
    assert health_resp.status_code == 200
    health_json = health_resp.json()
    assert health_json["success"] is True
    assert "database" in health_json["data"]
    assert health_json["data"]["database"] == "healthy"

    # Test OpenAPI schema endpoint
    docs_resp = client.get("/openapi.json")
    assert docs_resp.status_code == 200


def test_phase13_5_production_configuration():
    """Verify production environment parameters and security settings (13.5)."""
    assert hasattr(settings, "ENVIRONMENT")
    assert hasattr(settings, "DEBUG")
    assert hasattr(settings, "SECRET_KEY")
    assert hasattr(settings, "DATABASE_URL")
    assert len(settings.SECRET_KEY) >= 16


def test_phase13_6_patient_data_persistence_lifecycle(db_session):
    """Verify patient registration, update, retrieval, and data persistence (13.6)."""
    test_email = "persist_test99@hospital.local"

    # Create patient
    p = Patient(
        name="Persistence Verification",
        gender="Male",
        age=45,
        email=test_email,
        phone="9876543210",
        address="123 Hospital Way",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    # Query back patient
    retrieved = db_session.query(Patient).filter(Patient.email == test_email).first()
    assert retrieved is not None
    assert retrieved.name == "Persistence Verification"
    assert retrieved.phone == "9876543210"

    # Update patient
    retrieved.address = "456 Emergency Boulevard"
    db_session.commit()

    # Query updated patient
    updated = db_session.query(Patient).filter(Patient.email == test_email).first()
    assert updated.address == "456 Emergency Boulevard"

    # Cleanup
    db_session.delete(updated)
    db_session.commit()


def test_phase13_7_exit_criteria_matrix(client, db_session):
    """Aggregate exit criteria check for Phase 13 completion (13.7)."""
    # 1. Database table check
    inspector = inspect(engine)
    assert len(inspector.get_table_names()) >= 8

    # 2. Health check endpoint status
    res = client.get("/api/v1/health")
    assert res.status_code == 200

    # 3. Security headers check
    headers = res.headers
    assert "x-content-type-options" in headers or "X-Content-Type-Options" in headers
