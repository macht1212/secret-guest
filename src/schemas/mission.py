from datetime import datetime
from pydantic import BaseModel, Field

from .hotel import Hotel


class MissionSchema(BaseModel):
    user_id: int
    hotel_id: int
    status: str | None = "assigned"
    assigned_at: datetime
    deadline: datetime


class Mission(MissionSchema):
    id: int


class MissionPatch(BaseModel):
    user_id: int | None = Field(None)
    hotel_id: int | None = Field(None)
    status: str | None = Field(None)
    assigned_at: datetime | None = Field(None)
    complited_at: datetime | None = Field(None)
    deadline: datetime | None = Field(None)


class MissionRead(BaseModel):
    id: int
    status: str = "assigned"
    assigned_at: datetime
    completed_at: datetime | None = None
    deadline: datetime
    hotel: Hotel

    model_config = {"from_attributes": True}


class ParticipationRequestCreate(BaseModel):
    pass


class ParticipationRequestRead(BaseModel):
    id: int
    status: str
    submitted_at: datetime
    reviewed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ParticipationRequestApproveReject(BaseModel):
    request_id: int
    action: str


class Verification(BaseModel):
    is_verified: bool
