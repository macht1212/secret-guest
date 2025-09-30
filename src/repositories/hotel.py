from .base import BaseRepository

from src.models.hotels import Hotel as Model
from src.schemas.hotel import Hotel as Schema


class HotelsRepository(BaseRepository):
    model = Model
    schema = Schema
