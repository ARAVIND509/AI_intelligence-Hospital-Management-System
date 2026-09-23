import os
import glob
import subprocess
import tarfile
from datetime import datetime, timezone, timedelta

DEFAULT_DB_PATH = "hospital.db"


def backup_database(db_path: str = None, backup_dir: str = "backups", db_url_or_path: str = None) -> str:
    """Creates a timestamped compressed backup of the target PostgreSQL or SQLite database."""
    if db_url_or_path is not None:
        db_url = db_url_or_path
    elif db_path is not None:
        db_url = db_path
    elif os.getenv("DATABASE_URL"):
        db_url = os.getenv("DATABASE_URL")
    else:
        db_url = DEFAULT_DB_PATH

    target_input = db_url
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"medimind_db_backup_{timestamp}.tar.gz"
    backup_filepath = os.path.join(backup_dir, backup_filename)

    if db_url.startswith("postgresql"):
        print(f"[BACKUP] Performing PostgreSQL database backup for '{db_url}'...")
        dump_file = os.path.join(backup_dir, f"postgres_dump_{timestamp}.sql")
        try:
            cmd = f"pg_dump {db_url} > {dump_file}"
            subprocess.run(cmd, shell=True, check=True)
            with tarfile.open(backup_filepath, "w:gz") as tar:
                tar.add(dump_file, arcname=os.path.basename(dump_file))
            if os.path.exists(dump_file):
                os.remove(dump_file)
            print(f"[BACKUP SUCCESS] PostgreSQL backup archive created: {backup_filepath}")
            return backup_filepath
        except Exception as e:
            print(f"[BACKUP WARNING] pg_dump failed or not in PATH: {e}. Falling back to file archive.")

    target_path = target_input
    if target_path.startswith("sqlite:///"):
        target_path = target_path.replace("sqlite:///", "")

    if not os.path.exists(target_path):
        # Check backend/hospital.db
        alt_path = os.path.join("backend", target_path)
        if os.path.exists(alt_path):
            target_path = alt_path

    if not os.path.exists(target_path):
        print(f"[BACKUP ERROR] Database file '{target_path}' does not exist.")
        return ""

    with tarfile.open(backup_filepath, "w:gz") as tar:
        tar.add(target_path, arcname=os.path.basename(target_path))

    # Verify backup non-empty payload
    if os.path.exists(backup_filepath) and os.path.getsize(backup_filepath) > 0:
        print(f"[BACKUP SUCCESS] Archive created successfully ({os.path.getsize(backup_filepath)} bytes): {backup_filepath}")
        return backup_filepath
    else:
        print(f"[BACKUP ERROR] Archive creation failed or resulting payload was empty.")
        return ""


def verify_backup_integrity(backup_filepath: str) -> bool:
    """Verifies that a backup file exists, is non-empty, and has valid tar.gz contents."""
    if not os.path.exists(backup_filepath):
        print(f"[INTEGRITY ERROR] Backup file '{backup_filepath}' does not exist.")
        return False

    if os.path.getsize(backup_filepath) == 0:
        print(f"[INTEGRITY ERROR] Backup file '{backup_filepath}' is empty (0 bytes).")
        return False

    try:
        with tarfile.open(backup_filepath, "r:gz") as tar:
            members = tar.getmembers()
            if len(members) == 0:
                print(f"[INTEGRITY ERROR] Backup archive '{backup_filepath}' contains no files.")
                return False
            print(f"[INTEGRITY OK] Backup payload contains {len(members)} archived file(s).")
            return True
    except Exception as e:
        print(f"[INTEGRITY ERROR] Failed to parse tar.gz archive '{backup_filepath}': {e}")
        return False


def rotate_backups(backup_dir: str = "backups", retention_days: int = 7, retention_weeks: int = 4) -> int:
    """Enforces backup retention policy: keeps daily backups within retention_days, purges older non-weekly backups."""
    if not os.path.exists(backup_dir):
        return 0

    backup_files = sorted(glob.glob(os.path.join(backup_dir, "medimind_db_backup_*.tar.gz")))
    now = datetime.now(timezone.utc)
    purged_count = 0

    for filepath in backup_files:
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)
            age_days = (now - mtime).days

            # Keep all daily backups within retention_days (e.g., 7 days)
            if age_days <= retention_days:
                continue

            # Keep Sunday backups for up to retention_weeks (e.g. 28 days)
            if mtime.weekday() == 6 and age_days <= (retention_weeks * 7):
                continue

            # Otherwise, purge expired backup
            os.remove(filepath)
            purged_count += 1
            print(f"[ROTATION] Purged expired backup: {filepath}")
        except Exception as e:
            print(f"[ROTATION WARNING] Could not process {filepath}: {e}")

    print(f"[ROTATION COMPLETE] Purged {purged_count} expired backup file(s).")
    return purged_count


if __name__ == "__main__":
    b_file = backup_database()
    if b_file:
        verify_backup_integrity(b_file)
        rotate_backups()
