import time
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import app_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = round(time.time() - start_time, 4)

        app_logger.info(
            f"{request.method} {request.url.path} "
            f"Status={response.status_code} "
            f"Time={process_time}s"
        )

        return response