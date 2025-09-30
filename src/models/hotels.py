from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Text, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    lat: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    lng: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    partner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    last_inspection_date: Mapped[Optional[date]] = mapped_column(Date)
    priority_score: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    partner: Mapped[Optional["User"]] = relationship("User", back_populates="owned_hotels", foreign_keys=[partner_id])
    missions: Mapped[list["Mission"]] = relationship("Mission", back_populates="hotel", cascade="all, delete-orphan")
