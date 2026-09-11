# MediMind AI — Database Backup & Disaster Recovery Guide

This guide details the procedure for backing up and restoring the **MediMind AI Hospital Management System** database (PostgreSQL and SQLite) for on-premise hospital deployments.

---

## 💾 Automated & Manual Backup Options

MediMind AI provides built-in backup scripts (`scripts/backup_db.py`) located in the root installation directory.

### 1. Manual Backup Execution

To take an immediate snapshot of the hospital database:

```bash
python scripts/backup_db.py
```

- **Output**: Compressed and timestamped archive saved in `backups/medimind_db_backup_YYYYMMDD_HHMMSS.tar.gz`.
- **Supported Databases**:
  - **PostgreSQL**: Invokes `pg_dump` with compressed archive wrapping.
  - **SQLite**: Archives the database file directly.

### 2. Automated Scheduled Backups (Cron / Windows Task Scheduler)

#### Linux Server (Cron Job)
Add a daily cron job at 2:00 AM to perform an automated backup:
```bash
0 2 * * * cd /opt/medimind-ai && /usr/bin/python3 scripts/backup_db.py >> /var/log/medimind_backup.log 2>&1
```

#### Windows Server (Task Scheduler)
Create a Scheduled Task running:
- **Program**: `python.exe`
- **Arguments**: `scripts/backup_db.py`
- **Start in**: `C:\medimind-ai`

---

## 🔄 Disaster Recovery & Database Restoration

In the event of hardware failure, database corruption, or system migration, restore the system from the latest backup archive:

```bash
python scripts/restore_db.py backups/medimind_db_backup_YYYYMMDD_HHMMSS.tar.gz
```

### PostgreSQL Disaster Recovery Workflow

1. Stop the application services:
   ```bash
   docker compose stop backend worker
   ```
2. Run the restoration script or extract `postgres_dump.sql` from the archive and restore:
   ```bash
   docker exec -i medimind-db psql -U medimind_user -d medimind_db < postgres_dump.sql
   ```
3. Restart application microservices:
   ```bash
   docker compose start backend worker
   ```

---

## 🛡️ Data Retention & Offsite Encryption

1. **Local Archive Retention**: Retain local daily backups for at least 30 days.
2. **Encrypted Offsite Sync**: Copy `backups/*.tar.gz` to an offline storage server or internal hospital SAN storage over encrypted SSH/SFTP.
