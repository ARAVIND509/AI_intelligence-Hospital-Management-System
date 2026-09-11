# MediMind AI — Hospital On-Premise Installation Guide

This guide outlines step-by-step instructions for installing and deploying **MediMind AI** on a hospital's internal server network.

---

## 💻 Recommended Hardware & Operating System

- **OS**: Ubuntu Server 22.04 LTS / Windows Server 2022 / Debian 12
- **CPU**: 4 Cores minimum (8 Cores recommended)
- **RAM**: 8 GB minimum (16 GB recommended)
- **Disk Space**: 100 GB SSD storage
- **Network**: Static IPv4 address on Hospital Local Area Network (LAN)

---

## 🛠️ Step-by-Step Installation

### Step 1: Install Docker Engine
On Ubuntu/Debian Linux:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker
```

### Step 2: Clone or Copy Application Bundle
```bash
cd /opt
sudo git clone https://github.com/ARAVIND509/AI_intelligence-Hospital-Management-System.git medimind-ai
cd medimind-ai
```

### Step 3: Configure Environment
```bash
cp .env.example .env
nano .env
```
Ensure `SECRET_KEY`, `POSTGRES_PASSWORD`, and `DATABASE_URL` contain secure production credentials.

### Step 4: Start Container Services
```bash
docker compose up -d
```

### Step 5: Seed Database & Verify Installation
```bash
docker compose exec backend python /app/scripts/seed_db.py
```

Access the system at `https://<hospital-server-ip>` or `http://<hospital-server-ip>:8000`.
