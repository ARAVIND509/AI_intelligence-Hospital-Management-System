# MediMind AI — System Configuration Guide

This guide details all environment variables, security controls, and network parameters for **MediMind AI**.

---

## ⚙️ Environment Variables Reference

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `ENVIRONMENT` | string | `production` | Deployment mode (`production` / `development` / `test`) |
| `DEBUG` | boolean | `false` | Enables detailed tracebacks (must be false in production) |
| `HOST` | string | `0.0.0.0` | Bind host address for FastAPI server |
| `PORT` | integer | `8000` | Bind port number for FastAPI server |
| `SECRET_KEY` | string | REQUIRED | Secret key for signing JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | `1440` | JWT token validity duration (24 hours) |
| `DATABASE_URL` | string | `postgresql://...` | Connection URI for PostgreSQL database |
| `REDIS_URL` | string | `redis://redis:6379/0` | Connection URI for Redis cache |
| `CORS_ORIGINS` | string/list | `http://localhost:3000...` | Allowed client origins for CORS |
| `LOG_LEVEL` | string | `INFO` | System logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 🔒 Security Configuration Checklist

1. **Change Default Passwords**: Replace default `POSTGRES_PASSWORD` and `SECRET_KEY`.
2. **TLS / SSL Certificates**: Install hospital domain SSL certificate into `deployment/nginx/ssl/server.crt` and key into `server.key`.
3. **CORS Restrictions**: Limit `CORS_ORIGINS` strictly to authorized hospital workstation IPs or domain names.
