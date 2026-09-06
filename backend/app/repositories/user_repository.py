from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserRegister
from app.repositories.base_repository import CRUDBase


class CRUDUser(CRUDBase[User, UserRegister, dict]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_username_or_email(self, db: Session, username_or_email: str) -> Optional[User]:
        return db.query(User).filter(
            (User.email == username_or_email) | (User.username == username_or_email)
        ).first()


user_repository = CRUDUser(User)
