from fastapi import APIRouter, status

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/login",
    summary="User Login",
    description="Authenticates a user and returns an access token.",
    response_description="JWT access token",
    status_code=status.HTTP_200_OK,
)
async def login():
    return {
        "success": True,
        "message": "Login successful",
        "access_token": "dummy_token"
    }