from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import auth_service
from app.schemas.auth import UserRegister, UserLogin, PasswordChange, TokenResponse, UserResponse
from app.models.user import User
from app.core.audit import log_audit_event

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    summary="User Registration",
    description="Registers a new user account with role assignment.",
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, payload)
    log_audit_event(user.id, user.role, "REGISTER", "UserAccount")
    return {
        "success": True,
        "message": "User registered successfully",
        "data": UserResponse.model_validate(user).model_dump()
    }


@router.post(
    "/login",
    summary="User Login",
    description="Authenticates credentials and returns a JWT access token.",
    status_code=status.HTTP_200_OK,
)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    token_response = auth_service.authenticate_user(db, payload)
    log_audit_event(token_response.user.id, token_response.user.role, "LOGIN", "AuthToken")
    return {
        "success": True,
        "message": "Login successful",
        "data": token_response.model_dump()
    }


@router.get(
    "/me",
    summary="Get Current User Profile",
    description="Returns the profile of the currently authenticated user.",
    status_code=status.HTTP_200_OK,
)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "message": "User profile fetched successfully",
        "data": UserResponse.model_validate(current_user).model_dump()
    }


@router.post(
    "/change-password",
    summary="Change Password",
    description="Updates the password for the current authenticated user.",
    status_code=status.HTTP_200_OK,
)
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = auth_service.change_password(db, current_user, payload)
    log_audit_event(user.id, user.role, "CHANGE_PASSWORD", "UserAccount")
    return {
        "success": True,
        "message": "Password changed successfully",
        "data": UserResponse.model_validate(user).model_dump()
    }