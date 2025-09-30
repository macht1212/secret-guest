from sqlalchemy import select

from .base import BaseRepository
from src.models.users import User as Model
from src.schemas.user import UserWithHashedPassword


class UsersRepository(BaseRepository):
    model = Model
    schema = UserWithHashedPassword

    async def get_user_with_hashed_password(self, **filters):
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        model = result.scalars().one()
        return self.schema.model_validate(model)
