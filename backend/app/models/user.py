from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # --------------------------------------------------
    # PRIMARY KEY
    # --------------------------------------------------

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    # --------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # --------------------------------------------------
    # AUTHORIZATION
    # --------------------------------------------------

    role: Mapped[str] = mapped_column(
        String(50),
        default="patient",
        nullable=False,
    )

    # --------------------------------------------------
    # ACCOUNT STATUS
    # --------------------------------------------------

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # --------------------------------------------------
    # DOCTOR RELATIONSHIP
    # --------------------------------------------------

    doctor: Mapped["Doctor | None"] = relationship(
        "Doctor",
        back_populates="user",
        uselist=False,
    )

    # --------------------------------------------------
    # AUDIT FIELDS
    # --------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------
    # REPRESENTATION
    # --------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, "
            f"username='{self.username}', "
            f"email='{self.email}', "
            f"role='{self.role}')"
        )