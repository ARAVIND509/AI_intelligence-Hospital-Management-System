import os
import subprocess
import tarfile
from datetime import datetime, timezone


def backup_database(db_path: str = "hospital.db", backup_dir: str = "backups", db_url_or_path: str = None) -> str:
    target_input = db_url_or_path if db_url_or_path is not None else db_path
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"medimind_db_backup_{timestamp}.tar.gz"
    backup_filepath = os.path.join(backup_dir, backup_filename)

    db_url = os.getenv("DATABASE_URL", target_input)

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

    print(f"[BACKUP SUCCESS] Archive created: {backup_filepath}")
    return backup_filepath


if __name__ == "__main__":
    backup_database()
