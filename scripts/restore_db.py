import os
import sys
import tarfile


def restore_database(backup_filepath: str, target_db_path: str = "hospital.db") -> bool:
    if not os.path.exists(backup_filepath):
        print(f"[RESTORE ERROR] Backup file '{backup_filepath}' not found.")
        return False

    try:
        dest_dir = os.path.dirname(os.path.abspath(target_db_path)) or "."
        with tarfile.open(backup_filepath, "r:gz") as tar:
            if hasattr(tarfile, 'data_filter'):
                tar.extractall(path=dest_dir, filter='data')
            else:
                tar.extractall(path=dest_dir)

        print(f"[RESTORE SUCCESS] Database restored successfully from '{backup_filepath}' to '{target_db_path}'")
        return True
    except Exception as e:
        print(f"[RESTORE ERROR] Failed to restore database: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python restore_db.py <path_to_backup.tar.gz>")
    else:
        restore_database(sys.argv[1])
