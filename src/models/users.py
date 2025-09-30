import enum
from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class UserRole(enum.Enum):
    TRAVELER = "TRAVELER"
    HOTEL_OWNER = "HOTEL_OWNER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    owned_hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel", back_populates="partner", foreign_keys="Hotel.partner_id"
    )
    participation_requests: Mapped[list["ParticipationRequest"]] = relationship(
        "ParticipationRequest",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[ParticipationRequest.user_id]",
    )

    reviewed_requests: Mapped[list["ParticipationRequest"]] = relationship(
        "ParticipationRequest", back_populates="reviewer", foreign_keys="[ParticipationRequest.reviwer_id]"
    )
    missions: Mapped[list["Mission"]] = relationship("Mission", back_populates="user", cascade="all, delete-orphan")
