# MediMind AI — Troubleshooting & Diagnostics Guide

This document assists hospital IT administrators in diagnosing and resolving issues with **MediMind AI**.

---

## 🔍 Common Issues & Resolutions

### 1. Database Connection Refused (`medimind-db`)
- **Symptom**: Backend logs report `psycopg2.OperationalError: could not connect to server`.
- **Cause**: PostgreSQL container is still initializing or healthy check hasn't passed.
- **Fix**: Check PostgreSQL logs:
  ```bash
  docker compose logs database
  ```
  Ensure `POSTGRES_USER` and `POSTGRES_PASSWORD` match in `.env`.

### 2. Invalid Token / 401 Unauthorized Errors
- **Symptom**: Requests return `401 Unauthorized`.
- **Cause**: Secret key mismatch or expired token.
- **Fix**: Ensure `SECRET_KEY` in `.env` is consistent across restarts.

### 3. Nginx 502 Bad Gateway
- **Symptom**: Browser displays `502 Bad Gateway`.
- **Cause**: Backend FastAPI server container is down or starting up.
- **Fix**: Check backend status:
  ```bash
  docker compose ps backend
  docker compose logs backend
  ```

---

## 📊 System Diagnostics Commands

### Check System Logs
```bash
tail -n 100 logs/app.log
```

### Run Diagnostic Unit Tests
```bash
python -m pytest
```
