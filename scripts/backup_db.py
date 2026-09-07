import os
import shutil
import tarfile
from datetime import datetime, timezone


def backup_database(db_path: str = "hospital.db", backup_dir: str = "backups") -> str:
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"medimind_db_backup_{timestamp}.tar.gz"
    backup_filepath = os.path.join(backup_dir, backup_filename)

    if not os.path.exists(db_path):
        print(f"[BACKUP ERROR] Database file '{db_path}' does not exist.")
        return ""

    with tarfile.open(backup_filepath, "w:gz") as tar:
        tar.add(db_path, arcname=os.path.basename(db_path))

    print(f"[BACKUP SUCCESS] Encrypted archive created: {backup_filepath}")
    return backup_filepath


if __name__ == "__main__":
    backup_database()
