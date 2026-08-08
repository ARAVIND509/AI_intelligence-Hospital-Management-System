from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserRegister
from app.utils.password import (
    hash_password,
    verify_password,
)
from app.core.security import create_access_token


# --------------------------------------------------
# REGISTER USER
# --------------------------------------------------

def register_user(
    db: Session,
    user: UserRegister,
):
    existing = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing:
        raise ValueError("Email already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        password_hash=hash_password(user.password),
        role="patient",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# --------------------------------------------------
# AUTHENTICATE USER
# --------------------------------------------------

def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


# --------------------------------------------------
# LOGIN USER
# --------------------------------------------------

def login_user(
    db: Session,
    email: str,
    password: str,
):
    user = authenticate_user(
        db,
        email,
        password,
    )

    if not user:
        raise ValueError("Invalid credentials")

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# --------------------------------------------------
# CHANGE PASSWORD
# --------------------------------------------------

def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
):
    # Verify current password
    if not verify_password(
        current_password,
        user.password_hash,
    ):
        raise ValueError(
            "Current password is incorrect"
        )

    # Prevent using the same password
    if current_password == new_password:
        raise ValueError(
            "New password must be different from current password"
        )

    # Hash the new password
    user.password_hash = hash_password(
        new_password
    )

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "Password changed successfully",
    }