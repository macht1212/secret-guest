from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ReportStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class EvaluationCriterion(Base):
    __tablename__ = "evaluation_criteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_required: Mapped[bool] = mapped_column(default=True)

    report_scores: Mapped[list["ReportScore"]] = relationship(
        "ReportScore", back_populates="criterion", cascade="all, delete-orphan"
    )


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="chk_report_status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id", ondelete="CASCADE"), unique=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[ReportStatus] = mapped_column(default=ReportStatus.pending)
    overall_comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    mission: Mapped["Mission"] = relationship("Mission", back_populates="report")
    scores: Mapped[list["ReportScore"]] = relationship(
        "ReportScore", back_populates="report", cascade="all, delete-orphan"
    )
    photos: Mapped[list["ReportPhoto"]] = relationship(
        "ReportPhoto", back_populates="report", cascade="all, delete-orphan"
    )


class ReportScore(Base):
    __tablename__ = "report_scores"
    __table_args__ = (CheckConstraint("score >= 1 AND score <= 10", name="chk_score_range"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"))
    criterion_id: Mapped[int] = mapped_column(ForeignKey("evaluation_criteria.id", ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    report: Mapped["Report"] = relationship("Report", back_populates="scores")
    criterion: Mapped["EvaluationCriterion"] = relationship("EvaluationCriterion", back_populates="report_scores")


class ReportPhoto(Base):
    __tablename__ = "report_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"))
    photo_url: Mapped[str] = mapped_column(String(512), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(String(255))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    report: Mapped["Report"] = relationship("Report", back_populates="photos")
