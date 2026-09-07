# MediMind AI — Hospital Administrator Manual

This manual provides operational instructions for Hospital IT Administrators managing **MediMind AI**.

---

## 👥 User & Role Management

MediMind AI enforces strict Role-Based Access Control (RBAC):

| Role | Permitted Actions |
| :--- | :--- |
| **ADMIN** | Full system control, audit logs, backup/restore, user management |
| **DOCTOR** | Patient medical records, consultation, lab orders, prescriptions, discharge summary |
| **LABORATORY** | Lab catalog management, sample collection, technician result entry |
| **PHARMACY** | Medicine inventory, low-stock tracking, dispensing, stock history |
| **RECEPTIONIST** | Patient registration, appointment booking, bed allocation, invoice payment |
| **DEPARTMENT_HEAD** | Department overview dashboard, doctor workload, department reports |
| **PATIENT** | Read-only access to personal appointments, billing history, and lab reports |

### Creating New Users
Administrators can register new hospital staff accounts via the Admin Dashboard or API:
```bash
POST /api/v1/auth/register
```

---

## 💾 Database Backup & Disaster Recovery

### Automatic Scheduled Backups
Run daily backups via cron or task scheduler:
```bash
python scripts/backup_db.py
```
Backups are saved to `/opt/medimind-ai/backups/medimind_db_backup_YYYYMMDD_HHMMSS.tar.gz`.

### Restoring a Database
To restore the system from a backup file:
```bash
python scripts/restore_db.py backups/medimind_db_backup_20260907_120000.tar.gz
```

---

## 📜 Audit Logging & Compliance Inspection

Every state-changing action is logged in real-time.
Administrators can query audit records via API:
```bash
GET /api/v1/audit-logs?skip=0&limit=50
```
Fields returned:
- `timestamp`: Date and time of action
- `username`: User account performing action
- `role`: Role of user
- `action`: Action description (e.g. `POST /api/v1/admissions`)
- `ip_address`: Hospital network IP address
- `status_code`: HTTP status result
