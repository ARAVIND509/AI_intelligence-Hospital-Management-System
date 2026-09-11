# 🚀 MediMind AI — Hospital Management & Clinical Intelligence System

[![CI/CD Pipeline](https://github.com/ARAVIND509/AI_intelligence-Hospital-Management-System/actions/workflows/ci.yml/badge.svg)](https://github.com/ARAVIND509/AI_intelligence-Hospital-Management-System/actions)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**MediMind AI** is an enterprise-grade, HIPAA/GDPR-aligned Hospital Management & Clinical Intelligence System built for local on-premise deployment. It seamlessly connects reception, triage, doctors, laboratory, pharmacy, ward management, billing, and AI predictive clinical analytics while guaranteeing 100% data sovereignty within the hospital's local network.

---

## 🏗️ System Architecture

```text
                                Hospital Network / LAN
                                          │
                                          ▼
                                     Reverse Proxy
                                     (Nginx HTTPS)
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
            Frontend UI                                    FastAPI Backend
       (Next.js / React)                                (REST & WebSockets)
                                                                  │
                                      ┌───────────────────────────┼───────────────────────────┐
                                      ▼                           ▼                           ▼
                              PostgreSQL Database            Redis Cache               Async Worker
                            (Patients/Records/Billing)   (Task Queue & Sockets)   (AI Analytics & Jobs)
```

---

## ✨ Key Features

- 🏥 **Reception & Patient Management**: Registration, search, triage scoring, and queue allocation.
- 👨‍⚕️ **Doctor & Clinical Workflows**: EHR consultation, digital prescriptions, lab orders, and diagnosis entry.
- 🔬 **Laboratory Information System (LIS)**: Test requests, sample tracking, result entry, and doctor verification.
- 💊 **Pharmacy Management**: Inventory tracking, automated dispenses, drug interaction checking, and stock alert logs.
- 🛏️ **Bed & Admission Management**: Bed allocation, transfers, ward capacity tracking, and discharge summary generation.
- 🤖 **AI Clinical Intelligence**: Early ICU risk prediction, length-of-stay forecasting, drug-drug interaction warnings, and automated patient summary generation.
- 💳 **Billing & Financials**: Itemized invoice generation, insurance claim processing, and payment transaction logging.
- 🔒 **Security & Auditability**: Role-Based Access Control (RBAC), tamper-evident audit logging, and automated database backups.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2, Alembic
- **Database**: PostgreSQL 15 (Production) / SQLite (Local Dev)
- **Caching & Broker**: Redis 7
- **Reverse Proxy**: Nginx with SSL & Rate Limiting
- **Containerization**: Docker & Docker Compose
- **Testing & CI/CD**: Pytest, GitHub Actions

---

## ⚡ Quick Start with Docker

### Prerequisites
- Docker Engine 24.0+ & Docker Compose v2+
- Git

### Launching the System
```bash
# 1. Clone the repository
git clone https://github.com/ARAVIND509/AI_intelligence-Hospital-Management-System.git
cd AI_intelligence-Hospital-Management-System

# 2. Configure environment variables
cp .env.example .env

# 3. Launch containerized microservices
docker compose up -d

# 4. Initialize database schema and default admin accounts
docker compose exec backend python /app/scripts/seed_db.py
```

Access the system at:
- **API Base**: `https://localhost` or `http://localhost:8000`
- **Interactive API Docs**: `http://localhost:8000/docs`

---

## 🔧 Environment Configuration (.env)

Key variables in `.env`:

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `ENVIRONMENT` | `production` | Running environment mode (`production` / `development`) |
| `DEBUG` | `false` | Enable/disable debug tracebacks |
| `SECRET_KEY` | `medimind_prod_secret_key...` | 64-character JWT secret key |
| `DATABASE_URL` | `postgresql://...` | Database connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `CORS_ORIGINS` | `http://localhost:3000...` | Allowed CORS origins list |

---

## 🧪 Testing & Verification

Run the full automated unit and integration test suite:

```bash
# Run pytest test suite
python -m pytest

# Run with test coverage
python -m pytest --cov=backend/app
```

---

## 📚 Complete Documentation Index

Detailed guides are available in the [`docs/`](./docs) directory:

- 📖 [Installation Guide](./docs/INSTALLATION_GUIDE.md)
- ⚙️ [Configuration Guide](./docs/CONFIGURATION_GUIDE.md)
- 🗄️ [Database & Migration Guide](./docs/DATABASE_GUIDE.md)
- 🐳 [Docker Deployment Guide](./docs/DOCKER_GUIDE.md)
- 💾 [Backup & Restore Procedure](./docs/BACKUP_RESTORE.md)
- 🛠️ [Troubleshooting & Diagnostics](./docs/TROUBLESHOOTING.md)
- 🧑‍💼 [Administrator Manual](./docs/ADMINISTRATOR_GUIDE.md)
- 📋 [Hospital Handover Checklist](./docs/HANDOVER_CHECKLIST.md)

---

## 🤝 Support Model & Maintenance

MediMind AI is designed for 100% on-premise execution with zero cloud telemetry. For maintenance and remote support:
1. Hospital IT administrator contacts the support team.
2. Temporary SSH/VPN access is granted by the hospital IT team.
3. Support session activities are fully audited in `AuditLog`.
4. Access credentials are automatically revoked upon issue resolution.

---

## 📄 License

Proprietary Software — All Rights Reserved. MediMind AI Clinical Intelligence Team.
