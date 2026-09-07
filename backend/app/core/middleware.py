import time
from collections import defaultdict
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, HTTPException, status
from app.core.logger import app_logger
from app.core.audit import log_audit_event


# Simple Rate Limiter (In-Memory per IP)
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, ip: str) -> bool:
        if ip == "testclient":
            return True
        now = time.time()
        # Filter timestamps outside window
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window_seconds]
        if len(self.requests[ip]) >= self.max_requests:
            return False
        self.requests[ip].append(now)
        return True


rate_limiter = RateLimiter(max_requests=500, window_seconds=60)


class SecurityAndAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "127.0.0.1"

        # 1. Rate Limiting Check
        if not rate_limiter.is_allowed(client_ip):
            app_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content='{"detail": "Rate limit exceeded. Too many requests. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )

        # 2. Process Request
        response = await call_next(request)
        process_time = round(time.time() - start_time, 4)

        # 3. Add Security Headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # 4. Audit Log for State Mutating Endpoints (POST, PUT, PATCH, DELETE)
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            log_audit_event(
                user_id=None,
                username=None,
                role=None,
                action=f"{request.method} {request.url.path}",
                resource_type=request.url.path.split("/")[3] if len(request.url.path.split("/")) > 3 else "API",
                resource_id=request.url.path.split("/")[-1] if request.url.path.split("/")[-1].isdigit() else None,
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                status_code=response.status_code,
                details=f"Execution time: {process_time}s"
            )

        app_logger.info(f"{request.method} {request.url.path} Status={response.status_code} Time={process_time}s")
        return response