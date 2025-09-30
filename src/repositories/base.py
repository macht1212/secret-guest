from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel

from src.database import Base


class UniqueError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BaseRepository:
    model: Base = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def add(self, data: BaseModel):
        try:
            stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(stmt)
            return self.schema.model_validate(result.scalars().first(), from_attributes=True)
        except Exception as e:
            raise Exception(f"ERROR: {e}") from e

    async def update(self, data: BaseModel, exclude_unset: bool = False, **filters):
        stmt = (
            update(self.model)
            .filter_by(**filters)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return self.schema.model_validate(result.scalars().first(), from_attributes=True)

    async def delete(self, **filters):
        stmt = delete(self.model).filter_by(**filters)
        await self.session.execute(stmt)
        return

    async def get_one_or_none(self, **filters):
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        res = result.scalars().one_or_none()
        if not res:
            return None
        return self.schema.model_validate(res, from_attributes=True)

    async def get_filtered(self, *filter, **filters):
        query = select(self.model).filter(*filter).filter_by(**filters)

        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]
