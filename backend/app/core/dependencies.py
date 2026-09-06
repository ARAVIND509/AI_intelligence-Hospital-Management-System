from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import user_repository
from app.models.user import User

security_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id or not str(user_id).isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials / Invalid JWT token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_repository.get(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    return user


def require_roles(allowed_roles: List[str]) -> Callable:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.upper()
        allowed_upper = [r.upper() for r in allowed_roles]
        if user_role not in allowed_upper and "ADMIN" not in allowed_upper:
            # Allow ADMIN universally or check explicit roles
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required role in {allowed_roles}, but user has role '{current_user.role}'"
            )
        if user_role not in allowed_upper and user_role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required role in {allowed_roles}, but user has role '{current_user.role}'"
            )
        return current_user

    return role_checker


def verify_patient_access(current_user: User, target_patient_id: int):
    """
    Ensures Patients can only access their own records/data.
    ADMIN, DOCTOR, RECEPTIONIST can access patient data.
    """
    if current_user.role.upper() == "PATIENT":
        if current_user.patient_id != target_patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are only allowed to view or manage your own patient data"
            )


def verify_doctor_access(current_user: User, target_doctor_id: int):
    """
    Ensures Doctors can only manage their own doctor profile unless Admin/Receptionist.
    """
    if current_user.role.upper() == "DOCTOR":
        if current_user.doctor_id != target_doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are only allowed to view or manage your own doctor data"
            )
