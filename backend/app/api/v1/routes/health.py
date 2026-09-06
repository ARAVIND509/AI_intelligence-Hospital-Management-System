from fastapi import APIRouter

from app.schemas.response import APIResponse

router = APIRouter()


@router.get("/health", response_model=APIResponse)
async def health():
    return APIResponse(
        success=True,
        message="Application is healthy",
        data={
            "status": "running"
        }
    )