# MediMind AI — Administrator Operations Manual

This guide provides operational guidance for hospital IT system administrators managing **MediMind AI**.

---

## 🔑 Administrative Roles & Permissions

MediMind AI defines strict Role-Based Access Control (RBAC):

1. **ADMIN**: Full system control, department management, user creation, ward creation, audit log access.
2. **RECEPTIONIST**: Patient registration, appointment scheduling, triage queue assignment.
3. **DOCTOR**: Patient medical records, consultation notes, digital prescriptions, lab orders, ICU risk score reviews.
4. **LABORATORY**: Lab request processing, test result entry, status updates.
5. **PHARMACY**: Medication dispensing, inventory logging, drug stock tracking.
6. **PATIENT**: Self-service portal, medical history viewing, appointment tracking.

---

## 👤 Initial Superadmin Credentials

Upon running `python scripts/seed_db.py`, the following default administrative credentials are created:

- **Username**: `admin`
- **Email**: `admin@hospital.local`
- **Default Password**: `AdminPass2026!`
- **Role**: `ADMIN`

> **IMPORTANT**: The administrator MUST log in and change this password immediately after deployment.
