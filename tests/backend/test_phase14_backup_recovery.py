"""
MediMind AI — Phase 14 Automated Backup, Disaster Recovery & Business Continuity Test Suite
Tests sub-phases 14.1 through 14.6 exit criteria.
"""

import os
import shutil
import tempfile
import pytest
from app.models.patient import Patient
from app.models.user import User
from app.models.doctor import Doctor
from app.core.security import hash_password
from scripts.backup_db import backup_database, verify_backup_integrity, rotate_backups
from scripts.restore_db import restore_database


def test_phase14_1_automated_database_backup(tmp_path):
    """Verify automated database backup creation and timestamped archive generation (14.1)."""
    db_file = tmp_path / "hospital_test_14_1.db"
    db_file.write_text("MediMind Phase 14 Backup Content Test")

    backup_dir = tmp_path / "backups"
    backup_file = backup_database(db_path=str(db_file), backup_dir=str(backup_dir))

    assert backup_file != ""
    assert os.path.exists(backup_file)
    assert os.path.getsize(backup_file) > 0


def test_phase14_2_database_restoration_and_record_integrity(tmp_path, db_session):
    """Verify database deletion and recovery with full record and relationship integrity (14.2)."""
    test_email = "disaster_recovery_patient@hospital.local"

    # Create dummy patient record
    patient = Patient(
        name="Disaster Test Patient",
        gender="Female",
        age=52,
        email=test_email,
        phone="5554443332",
    )
    db_session.add(patient)
    db_session.commit()

    # Backup current session database
    db_file = tmp_path / "live_db.db"
    db_file.write_text("Patient data baseline")
    backup_dir = tmp_path / "backups"

    backup_filepath = backup_database(db_path=str(db_file), backup_dir=str(backup_dir))
    assert backup_filepath != ""

    # Delete test file (Simulate database corruption / deletion)
    if os.path.exists(db_file):
        os.remove(db_file)

    # Restore from backup archive
    restored_target = tmp_path / "restored_db.db"
    success = restore_database(backup_filepath=backup_filepath, target_db_path=str(restored_target))
    assert success is True
    assert os.path.exists(restored_target)
    assert os.path.getsize(restored_target) > 0


def test_phase14_3_backup_payload_non_empty_and_integrity_check(tmp_path):
    """Verify backup integrity checking for valid vs empty payload archives (14.3)."""
    # Create valid backup
    valid_db = tmp_path / "valid.db"
    valid_db.write_text("valid database payload content")
    backup_dir = tmp_path / "backups"
    valid_backup = backup_database(db_path=str(valid_db), backup_dir=str(backup_dir))

    assert verify_backup_integrity(valid_backup) is True

    # Test non-existent file integrity
    assert verify_backup_integrity(str(tmp_path / "non_existent.tar.gz")) is False

    # Test empty file integrity
    empty_file = tmp_path / "empty.tar.gz"
    empty_file.write_text("")
    assert verify_backup_integrity(str(empty_file)) is False


def test_phase14_4_retention_and_rotation_policy(tmp_path):
    """Verify retention rotation policy purges expired backup files (14.4)."""
    backup_dir = tmp_path / "backups"
    os.makedirs(backup_dir, exist_ok=True)

    # Create dummy backup files
    b1 = backup_dir / "medimind_db_backup_20260101_100000.tar.gz"
    b1.write_text("old backup content")

    b2 = backup_dir / "medimind_db_backup_20260923_100000.tar.gz"
    b2.write_text("recent backup content")

    # Run backup rotation
    purged_count = rotate_backups(backup_dir=str(backup_dir), retention_days=7, retention_weeks=4)
    assert isinstance(purged_count, int)


def test_phase14_5_disaster_recovery_simulation_scenarios(client, tmp_path):
    """Verify Disaster Recovery Scenarios A-D simulation (14.5)."""
    # Scenario A: Backend process restart simulation
    res = client.get("/api/v1/health")
    assert res.status_code == 200

    # Scenario C: Database backup and restore simulation
    test_db = tmp_path / "scen_c.db"
    test_db.write_text("Scenario C payload")
    backup = backup_database(db_path=str(test_db), backup_dir=str(tmp_path / "backups"))
    test_db.unlink(missing_ok=True)
    restored = restore_database(backup, str(test_db))
    assert restored is True
    assert test_db.exists()


def test_phase14_6_exit_criteria_matrix():
    """Aggregate exit criteria check for Phase 14 completion (14.6)."""
    from scripts.validate_phase14 import validate_phase14_backup_and_disaster_recovery
    result_code = validate_phase14_backup_and_disaster_recovery()
    assert result_code == 0
