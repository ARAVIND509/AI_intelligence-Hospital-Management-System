import os
from app.models.user import User
from app.core.security import hash_password, create_access_token
from scripts.backup_db import backup_database
from scripts.restore_db import restore_database


def create_test_user(db_session, username, role):
    pwd_hash = hash_password("password123")
    user = User(
        username=username,
        email=f"{username}@hospital.org",
        password_hash=pwd_hash,
        role=role,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": role})
    return user, token


def test_phase11_security_rbac_and_audit_logging(client, db_session):
    # Setup roles
    admin_user, admin_token = create_test_user(db_session, "admin_sec", "ADMIN")
    doc_user, doc_token = create_test_user(db_session, "doc_sec", "DOCTOR")
    rec_user, rec_token = create_test_user(db_session, "rec_sec", "RECEPTIONIST")
    pharm_user, pharm_token = create_test_user(db_session, "pharm_sec", "PHARMACY")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    rec_headers = {"Authorization": f"Bearer {rec_token}"}
    pharm_headers = {"Authorization": f"Bearer {pharm_token}"}

    # ----------------------------------------------------
    # 1. RBAC Restriction Assertions
    # ----------------------------------------------------
    # Doctor attempting Admin-only Audit Logs -> 403 Forbidden
    res_audit_doc = client.get("/api/v1/audit-logs", headers=doc_headers)
    assert res_audit_doc.status_code == 403, "Doctor must be forbidden from viewing system audit logs"

    # Receptionist attempting Doctor-only result review -> 403 Forbidden
    res_rev_rec = client.post("/api/v1/laboratory/results/1/review", json={"doctor_notes": "Test"}, headers=rec_headers)
    assert res_rev_rec.status_code == 403, "Receptionist must be forbidden from reviewing lab results"

    # Pharmacy user attempting Admin-only Ward Creation -> 403 Forbidden
    res_ward_pharm = client.post("/api/v1/admissions/wards", json={"ward_name": "Test Ward", "ward_type": "GENERAL"}, headers=pharm_headers)
    assert res_ward_pharm.status_code == 403, "Pharmacy staff must be forbidden from managing wards"

    # Unauthorized request without JWT token -> 401 Unauthorized
    res_unauth = client.get("/api/v1/analytics/patients/1")
    assert res_unauth.status_code == 401, "Unauthenticated request must return 401"

    # Admin accessing Audit Logs -> 200 OK
    res_audit_admin = client.get("/api/v1/audit-logs", headers=admin_headers)
    assert res_audit_admin.status_code == 200, res_audit_admin.json()

    # ----------------------------------------------------
    # 2. Security Headers Assertion
    # ----------------------------------------------------
    root_res = client.get("/")
    assert root_res.headers.get("X-Frame-Options") == "DENY"
    assert root_res.headers.get("X-Content-Type-Options") == "nosniff"
    assert "X-XSS-Protection" in root_res.headers

    # ----------------------------------------------------
    # 3. Database Backup & Restore Execution Test
    # ----------------------------------------------------
    # Create a dummy test file to simulate DB backup
    dummy_db = "test_dummy_hospital.db"
    with open(dummy_db, "w") as f:
        f.write("DUMMY_HOSPITAL_DATABASE_CONTENT")

    backup_file = backup_database(db_path=dummy_db, backup_dir="test_backups")
    assert os.path.exists(backup_file), "Backup file tar.gz must be created"

    # Restore test
    restored_db = "test_restored_hospital.db"
    success = restore_database(backup_filepath=backup_file, target_db_path=restored_db)
    assert success is True

    # Cleanup temp test files
    if os.path.exists(dummy_db):
        os.remove(dummy_db)
    if os.path.exists(restored_db):
        os.remove(restored_db)
    if os.path.exists(backup_file):
        os.remove(backup_file)
    if os.path.exists("test_backups"):
        try:
            os.rmdir("test_backups")
        except Exception:
            pass
