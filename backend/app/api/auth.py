from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    require_role,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    Token,
    ChangePassword,
)
from app.services.auth_service import (
    register_user,
    login_user,
    change_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        return register_user(
            db,
            user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@router.post(
    "/login",
    response_model=Token,
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    try:
        return login_user(
            db,
            user.email,
            user.password,
        )

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


# --------------------------------------------------
# CURRENT USER
# --------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


# --------------------------------------------------
# ADMIN TEST
# --------------------------------------------------

@router.get(
    "/admin-test",
)
def admin_test(
    current_user: User = Depends(
        require_role("admin")
    ),
):
    return {
        "success": True,
        "message": "Admin access granted",
        "user": current_user.username,
        "role": current_user.role,
    }


# --------------------------------------------------
# CHANGE PASSWORD
# --------------------------------------------------

@router.post(
    "/change-password",
)
def change_user_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return change_password(
            db,
            current_user,
            data.current_password,
            data.new_password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )