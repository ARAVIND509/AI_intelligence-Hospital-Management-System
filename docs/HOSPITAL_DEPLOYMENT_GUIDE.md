# MediMind AI — Hospital Local Deployment & Self-Hosting Guide

This guide provides instructions for deploying **MediMind AI Hospital Management System** directly on a hospital's internal server network.

---

## 🔒 Data Privacy & Local Hosting Guarantee

> **100% Data Sovereignty**: All patient records, lab reports, pharmacy inventory, and billing data remain **strictly inside the hospital's local network/infrastructure**. MediMind AI does **NOT** transfer patient data to external clouds or third-party servers.

---

## 💻 System Requirements

### Recommended Server Specs
- **OS**: Ubuntu 22.04 LTS / Windows Server 2022 / Debian 12
- **CPU**: 4 Cores (8 Cores recommended for high-volume hospitals)
- **RAM**: 8 GB minimum (16 GB recommended)
- **Disk Space**: 100 GB SSD
- **Network**: Hospital Local Area Network (LAN) with Static IP

---

## 🐳 Step-by-Step Installation

### Step 1: Install Docker & Docker Compose
On Linux (Ubuntu/Debian):
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

On Windows Server:
Install **Docker Desktop for Windows** or Docker Engine.

### Step 2: Clone / Copy MediMind AI Repository
Copy the MediMind release bundle into `/opt/medimind-ai` or your installation path:
```bash
cd /opt/medimind-ai
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to set strong production credentials:
```ini
POSTGRES_USER=hospital_admin
POSTGRES_PASSWORD=SuperStrongHospitalPass2026!
SECRET_KEY=GeneratingA64CharRandomSecretKeyHere
ENVIRONMENT=production
```

### Step 4: Launch Hospital Microservices
Run:
```bash
docker compose up -d
```
This starts:
- **Backend Service** (FastAPI)
- **Database** (PostgreSQL)
- **Cache** (Redis)
- **Reverse Proxy** (Nginx with HTTPS)

### Step 5: Verify Local Access
Open any browser on a PC connected to the hospital network:
```text
https://192.168.x.x  or  https://medimind.hospital.local
```

---

## 🛡️ Remote Technical Support Procedure

If the hospital requests technical support from the MediMind AI engineering team:

```text
Hospital Admin
      │
      │ 1. Initiates support request
      ▼
Temporary Access Granted
      │
      │ 2. Limited-time SSH / VPN credential issued
      ▼
MediMind Support Engineer
      │
      │ 3. Troubleshoots issue (All actions logged in Audit Log)
      ▼
Support Session Concluded
      │
      │ 4. Access credentials automatically revoked
```

1. **No Permanent Access**: MediMind engineers have **no default access** to patient data.
2. **Session Auditing**: Every admin command and diagnostic query is recorded in `AuditLog`.
3. **Instant Revocation**: Temporary access keys expire after the support window closes.
