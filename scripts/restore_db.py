import os
import sys
import tarfile
import shutil


def restore_database(backup_filepath: str, target_db_path: str = "hospital.db") -> bool:
    """Restores database payload from tar.gz backup archive to the specified target file/path."""
    if not os.path.exists(backup_filepath):
        print(f"[RESTORE ERROR] Backup file '{backup_filepath}' not found.")
        return False

    try:
        dest_dir = os.path.dirname(os.path.abspath(target_db_path)) or "."
        os.makedirs(dest_dir, exist_ok=True)

        with tarfile.open(backup_filepath, "r:gz") as tar:
            members = tar.getmembers()
            if not members:
                print(f"[RESTORE ERROR] Backup archive is empty.")
                return False

            # Extract archive contents to dest_dir
            if hasattr(tarfile, 'data_filter'):
                tar.extractall(path=dest_dir, filter='data')
            else:
                tar.extractall(path=dest_dir)

            # If extracted filename differs from target_db_path basename, relocate/copy
            extracted_name = os.path.basename(members[0].name)
            extracted_path = os.path.join(dest_dir, extracted_name)
            target_abs = os.path.abspath(target_db_path)

            if os.path.exists(extracted_path) and os.path.abspath(extracted_path) != target_abs:
                shutil.copy2(extracted_path, target_abs)

        if os.path.exists(target_db_path) and os.path.getsize(target_db_path) > 0:
            print(f"[RESTORE SUCCESS] Database restored successfully from '{backup_filepath}' to '{target_db_path}' ({os.path.getsize(target_db_path)} bytes).")
            return True
        else:
            print(f"[RESTORE ERROR] Restored target database file '{target_db_path}' does not exist or is empty.")
            return False
    except Exception as e:
        print(f"[RESTORE ERROR] Failed to restore database: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python restore_db.py <path_to_backup.tar.gz> [target_db_path]")
    else:
        target = sys.argv[2] if len(sys.argv) > 2 else "hospital.db"
        restore_database(sys.argv[1], target)
