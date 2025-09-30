from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ParticipationRequestStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class MissionStatus(enum.Enum):
    assigned = "assigned"
    in_progress = "in_progress"
    complited = "complited"
    report_pending = "report_pending"
    verified = "verified"
    canceled = "canceled"


class Mission(Base):
    __tablename__ = "missions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('assigned', 'in_progress', 'complited', 'report_pending', 'verified', 'canceled')",
            name="chk_mission_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"))
    status: Mapped[MissionStatus | None] = mapped_column(nullable=True, default=None)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="missions")
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="missions")
    report: Mapped[Optional["Report"]] = relationship("Report", back_populates="mission", cascade="all, delete-orphan")


class ParticipationRequest(Base):
    __tablename__ = "participation_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[ParticipationRequestStatus] = mapped_column(nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    reviwed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviwer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="participation_requests", foreign_keys=[user_id])

    reviewer: Mapped[Optional["User"]] = relationship(
        "User", back_populates="reviewed_requests", foreign_keys=[reviwer_id]
    )
