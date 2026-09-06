from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user_repository import user_repository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegister, UserLogin, PasswordChange, TokenResponse, UserResponse
from app.models.user import User


class AuthService:
    def register_user(self, db: Session, payload: UserRegister) -> User:
        if len(payload.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )

        if user_repository.get_by_email(db, payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{payload.email}' already exists"
            )

        if user_repository.get_by_username(db, payload.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with username '{payload.username}' already exists"
            )

        role = payload.role.upper() if payload.role else "PATIENT"
        if role not in ["ADMIN", "DOCTOR", "RECEPTIONIST", "PATIENT"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role '{role}'. Allowed: ADMIN, DOCTOR, RECEPTIONIST, PATIENT"
            )

        db_user = User(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=role,
            is_active=True,
            patient_id=payload.patient_id,
            doctor_id=payload.doctor_id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate_user(self, db: Session, payload: UserLogin) -> TokenResponse:
        user = user_repository.get_by_username_or_email(db, payload.username_or_email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )

        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "patient_id": user.patient_id,
            "doctor_id": user.doctor_id,
        }
        access_token = create_access_token(data=token_data)

        user_res = UserResponse.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_res
        )

    def change_password(self, db: Session, user: User, payload: PasswordChange) -> User:
        if not verify_password(payload.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )

        if len(payload.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 6 characters long"
            )

        user.password_hash = hash_password(payload.new_password)
        db.commit()
        db.refresh(user)
        return user


auth_service = AuthService()
