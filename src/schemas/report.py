from datetime import datetime
from pydantic import BaseModel

from src.schemas.mission import MissionRead


class EvaluationCriterion(BaseModel):
    name: str
    description: str | None = None
    is_required: bool

    model_config = {"from_attributes": True}


class EvaluationCriterionRead(EvaluationCriterion):
    id: int

    model_config = {"from_attributes": True}


class ReportScoreCreate(BaseModel):
    criterion_id: int
    score: int
    comment: str | None = None


class ReportPhotoCreate(BaseModel):
    photo_url: str
    caption: str | None = None


class ReportCreate(BaseModel):
    mission_id: int
    overall_comment: str | None = None
    scores: list[ReportScoreCreate]
    photos: list[ReportPhotoCreate] = []


class ReportScoreRead(BaseModel):
    id: int
    criterion: EvaluationCriterionRead
    score: int
    comment: str | None = None

    model_config = {"from_attributes": True}


class ReportPhotoRead(BaseModel):
    id: int
    photo_url: str
    caption: str | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class ReportRead(BaseModel):
    id: int
    mission: MissionRead
    status: str
    submitted_at: datetime
    overall_comment: str | None = None
    scores: list[ReportScoreRead]
    photos: list[ReportPhotoRead]

    model_config = {"from_attributes": True}
