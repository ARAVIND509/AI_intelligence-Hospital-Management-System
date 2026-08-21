from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User


class Doctor(Base):
    __tablename__ = "doctors"

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
    # HOSPITAL DOCTOR IDENTIFIER
    # --------------------------------------------------

    doctor_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    # --------------------------------------------------
    # USER ACCOUNT
    # --------------------------------------------------

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        unique=True,
        nullable=True,
    )

    user: Mapped[User | None] = relationship(
        "User",
        back_populates="doctor",
    )

    # --------------------------------------------------
    # PERSONAL INFORMATION
    # --------------------------------------------------

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # --------------------------------------------------
    # PROFESSIONAL INFORMATION
    # --------------------------------------------------

    specialization: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    qualification: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    experience_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    license_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    # --------------------------------------------------
    # CONTACT INFORMATION
    # --------------------------------------------------

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------
    # HOSPITAL INFORMATION
    # --------------------------------------------------

    department: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    consultation_fee: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # --------------------------------------------------
    # DOCTOR STATUS
    # --------------------------------------------------

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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
            f"Doctor(id={self.id}, "
            f"doctor_id='{self.doctor_id}', "
            f"name='{self.first_name} {self.last_name}', "
            f"specialization='{self.specialization}')"
        )