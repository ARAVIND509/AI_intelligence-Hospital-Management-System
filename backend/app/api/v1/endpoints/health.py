from fastapi import APIRouter, status

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get(
    "/",
    summary="Health Check",
    description="Returns the current health status of the application.",
    response_description="Application health information",
    status_code=status.HTTP_200_OK,
)
async def health():
    return {
        "success": True,
        "message": "Application is healthy",
        "data": {
            "status": "running"
        }
    }