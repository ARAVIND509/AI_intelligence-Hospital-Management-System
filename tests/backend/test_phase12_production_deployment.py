import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.models.user import User
from scripts.backup_db import backup_database
from scripts.restore_db import restore_database


def test_phase12_production_settings_validation():
    """Verify that settings load production attributes correctly."""
    assert hasattr(settings, "ENVIRONMENT")
    assert hasattr(settings, "DEBUG")
    assert hasattr(settings, "CORS_ORIGINS")
    assert hasattr(settings, "REDIS_URL")
    assert hasattr(settings, "DATABASE_URL")
    assert isinstance(settings.CORS_ORIGINS, list)


def test_phase12_health_and_root_endpoints(client):
    """Verify root endpoint and API response."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "MediMind AI Backend" in json_data["message"]


def test_phase12_security_headers_middleware(client):
    """Verify security headers are applied to HTTP responses."""
    response = client.get("/")
    assert response.headers.get("X-Frame-Options") in ["DENY", "SAMEORIGIN"]
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_phase12_database_backup_and_restore(tmp_path):
    """Verify database backup archive generation and restoration."""
    db_file = tmp_path / "test_backup.db"
    db_file.write_text("sample database content")

    backup_dir = tmp_path / "backups"
    backup_file = backup_database(db_path=str(db_file), backup_dir=str(backup_dir))

    assert backup_file != ""
    assert os.path.exists(backup_file)

    restore_target = tmp_path / "restored.db"
    success = restore_database(backup_filepath=backup_file, target_db_path=str(restore_target))
    assert success is True


def test_phase12_role_authorization_and_jwt_workflow(client, db_session):
    """Verify JWT authentication and role authorization for hospital workflows."""
    admin = User(
        username="admin_p12",
        email="admin_p12@hospital.local",
        password_hash=hash_password("adminpass123"),
        role="ADMIN",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    admin_token = create_access_token({"sub": str(admin.id), "username": admin.username, "role": "ADMIN"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Query departments list
    response = client.get("/api/v1/departments/", headers=headers)
    assert response.status_code in [200, 404]

    # Verify invalid token rejection
    invalid_headers = {"Authorization": "Bearer invalid_jwt_token_12345"}
    response = client.get("/api/v1/departments/", headers=invalid_headers)
    assert response.status_code == 401
