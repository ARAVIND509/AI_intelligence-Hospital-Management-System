# MediMind AI — Docker Production Deployment Guide

This guide details container architecture, service management, and Docker commands for **MediMind AI**.

---

## 🐳 Container Topology

| Container Name | Image | Port Mapping | Purpose |
|----------------|-------|--------------|---------|
| `medimind-nginx` | `nginx:alpine` | `80:80`, `443:443` | Reverse proxy, SSL termination, security headers |
| `medimind-backend` | Custom build | `8000:8000` | FastAPI application server |
| `medimind-worker` | Custom build | N/A | Async background worker service |
| `medimind-db` | `postgres:15-alpine` | `5432:5432` | Production relational database |
| `medimind-redis` | `redis:7-alpine` | `6379:6379` | In-memory cache & message broker |

---

## 🛠️ Useful Docker Commands

### Start All Services
```bash
docker compose up -d
```

### Stop All Services
```bash
docker compose stop
```

### View Live Logs
```bash
docker compose logs -f backend
```

### Inspect Container Health
```bash
docker compose ps
```

### Rebuild Containers After Code Updates
```bash
docker compose build --no-cache
docker compose up -d
```
