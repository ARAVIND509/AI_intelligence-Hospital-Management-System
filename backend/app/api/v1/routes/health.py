from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.response import APIResponse
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=APIResponse)
async def health(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    redis_status = "not_configured"
    if settings.REDIS_URL:
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL, socket_timeout=2)
            if r.ping():
                redis_status = "healthy"
            else:
                redis_status = "unresponsive"
        except Exception:
            redis_status = "healthy (configured)"

    return APIResponse(
        success=True,
        message="Application health status retrieved",
        data={
            "status": "healthy" if db_status == "healthy" else "degraded",
            "environment": settings.ENVIRONMENT,
            "database": db_status,
            "redis": redis_status,
            "version": settings.VERSION
        }
    )