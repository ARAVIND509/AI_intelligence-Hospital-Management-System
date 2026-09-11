# MediMind AI — Database Architecture & Migration Guide

This guide covers the database schema, Alembic migration workflows, and database initialization for **MediMind AI**.

---

## 🗄️ Database Architecture

MediMind AI utilizes **PostgreSQL** in production for ACID compliance, concurrency, and relability, with **SQLite** support for lightweight local development and testing.

### Core Tables & Relationships
- `users`: User authentication, roles (`ADMIN`, `RECEPTIONIST`, `DOCTOR`, `PATIENT`), and status.
- `patients`: Patient demographics, medical history, emergency contacts.
- `doctors`: Doctor profiles, specialties, department references.
- `departments`: Clinical departments (Cardiology, ICU, Pediatrics, etc.).
- `appointments`: Patient appointments, scheduling times, and status.
- `medical_records`: Electronic Health Records (EHR), clinical notes, and diagnosis.
- `prescriptions` & `prescription_medicines`: Digital prescriptions, dosages, and fulfillment flags.
- `lab_orders` & `lab_results`: Laboratory test orders, sample tracking, and numerical/text results.
- `admissions` & `beds`: Ward admissions, bed occupancy, and patient transfers.
- `inventory_logs` & `pharmacy_dispenses`: Pharmacy stock tracking and dispensing transactions.
- `billings` & `payment_transactions`: Invoicing, itemization, and payments.
- `audit_logs`: Immutable audit trails for regulatory compliance.

---

## 🔄 Managing Migrations with Alembic

Alembic configuration resides in `backend/alembic.ini` and `backend/app/database/migrations`.

### Running Migrations
To upgrade the database to the latest revision:
```bash
cd backend
python -m alembic upgrade head
```

### Creating New Migration Revisions
When modifying SQLAlchemy models in `app/models/`:
```bash
cd backend
python -m alembic revision --autogenerate -m "describe_schema_change"
```
