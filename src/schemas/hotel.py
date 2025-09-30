from pydantic import BaseModel, Field


class HotelSchema(BaseModel):
    name: str
    address: str
    city: str
    country: str
    lat: float | None
    lng: float | None
    partner_id: int | None


class Hotel(HotelSchema):
    id: int


class HotelPatch(BaseModel):
    name: str | None = Field(None)
    address: str | None = Field(None)
    city: str | None = Field(None)
    country: str | None = Field(None)
    lat: float | None = Field(None)
    lng: float | None = Field(None)
    partner_id: int | None = Field(None)


class HotelWithMissionStatus(BaseModel):
    hotel: Hotel
    has_mission: bool
    mission_status: str | None = None
