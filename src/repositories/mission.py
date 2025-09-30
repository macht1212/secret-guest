from datetime import datetime, timedelta

from sqlalchemy import and_, insert, select, update
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException, status

from src.models.users import User
from src.schemas.hotel import HotelWithMissionStatus, Hotel as HotelSchema
from src.models.missions import Mission as MossionModel, MissionStatus, ParticipationRequest, ParticipationRequestStatus
from src.schemas.mission import Mission as MissionSchema, MissionRead, ParticipationRequestRead
from src.models.hotels import Hotel as HotelModel

from .base import BaseRepository


class MissionRepository(BaseRepository):
    model = MossionModel
    schema = MissionSchema

    async def get_hotels_with_mission_status(self, user: User, city: str, country: str):
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Миссии могут просматривать только подтвержденные пользователи.",
            )
        mission_cte = (
            select(self.model.hotel_id, self.model.status)
            .where(and_(self.model.user_id == user.id, self.model.status.in_(["assigned", "in_progress", "completed"])))
            .cte("user_missions")
        )

        stmt = (
            select(
                HotelModel,
                mission_cte.c.hotel_id.is_not(None).label("has_mission"),
                mission_cte.c.status.label("mission_status"),
            )
            .select_from(HotelModel.__table__.outerjoin(mission_cte, HotelModel.id == mission_cte.c.hotel_id))
            .where(HotelModel.city == city, HotelModel.country == country)
            .order_by(HotelModel.priority_score.desc(), HotelModel.last_inspection_date.asc())
        )

        result = await self.session.execute(stmt)
        rows = result.fetchall()
        return [
            HotelWithMissionStatus(
                hotel=HotelSchema.model_validate(hotel, from_attributes=True),
                has_mission=has_mission,
                mission_status=mission_status,
            )
            for hotel, has_mission, mission_status in rows
        ]

    async def assign_mission(self, user: User, hotel_id: int):
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Заявку оставить могут только подтвержденные пользователи.",
            )
        query = select(self.model).where(self.model.user_id == user.id, self.model.hotel_id == hotel_id)

        existing = await self.session.execute(query)
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вы уже проверяли этот отель.")

        new_mission = {
            "user_id": user.id,
            "hotel_id": hotel_id,
            "status": MissionStatus.assigned,
            "assigned_at": datetime.now(tz=None),
            "deadline": datetime.now(tz=None) + timedelta(days=14),
        }

        stmt = insert(self.model).values(**new_mission).returning(self.model)
        result = await self.session.execute(stmt)
        return self.schema.model_validate(result.scalars().first(), from_attributes=True)

    async def get_user_missions(self, user: User):
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Миссии могут просматривать только подтвержденные пользователи.",
            )
        query = (
            select(self.model)
            .where(self.model.user_id == user.id)
            .options(joinedload(self.model.hotel))
            .order_by(self.model.assigned_at.desc())
        )
        result = await self.session.execute(query)
        missions_orm = result.scalars().all()

        return [MissionRead.model_validate(mission, from_attributes=True) for mission in missions_orm]

    async def update_status(self, mission_id: int, new_status: str):
        stmt = (
            update(self.model)
            .where(self.model.id == mission_id)
            .values(status=new_status, completed_at=datetime.now(tz=None))
        )
        await self.session.execute(stmt)
        await self.session.commit()


class ParticipationRequestRepository(BaseRepository):
    model = ParticipationRequest
    schema = ParticipationRequestRead

    async def create_request(self, user_id: int):
        existing = await self.session.execute(
            select(ParticipationRequest).where(
                self.model.user_id == user_id,
                self.model.status.in_(
                    [ParticipationRequestStatus.PENDING.value, ParticipationRequestStatus.APPROVED.value]
                ),
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заявка уже подана или одобрена.")

        new_request = self.model(
            user_id=user_id,
            status=ParticipationRequestStatus.PENDING.value,
            submitted_at=datetime.now(),
        )
        self.session.add(new_request)
        await self.session.commit()
        await self.session.refresh(new_request)
        return self.schema.model_validate(new_request, from_attributes=True)

    async def approve_request(self, request_id: int, reviewer_id: int):
        stmt = (
            update(self.model)
            .where(self.model.id == request_id, self.model.status == ParticipationRequestStatus.PENDING.value)
            .values(status=ParticipationRequestStatus.APPROVED.value, reviwed_at=datetime.now(), reviwer_id=reviewer_id)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        request = result.scalar_one_or_none()
        if not request:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заявка не найдена или уже обработана.")
        return self.schema.model_validate(request, from_attributes=True)

    async def reject_request(self, request_id: int, reviewer_id: int):
        stmt = (
            update(self.model)
            .where(self.model.id == request_id, self.model.status == "pending")
            .values(
                status=ParticipationRequestStatus.REJECTED.value, reviewed_at=datetime.now(), reviewer_id=reviewer_id
            )
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        request = result.scalar_one_or_none()
        if not request:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заявка не найдена или уже обработана.")
        return self.schema.model_validate(request, from_attributes=True)

    async def get_user_request(self, user_id: int):
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        request = result.scalar_one_or_none()
        if not request:
            return None
        return self.schema.model_validate(request, from_attributes=True)

    async def get_all_pending(self):
        stmt = (
            select(self.model)
            .where(self.model.status == ParticipationRequestStatus.PENDING.value)
            .options(selectinload(self.model.user))
        )
        result = await self.session.execute(stmt)
        requests = result.scalars().all()
        return [self.schema.model_validate(r, from_attributes=True) for r in requests]

    async def get_request_by_id(self, request_id: int):
        stmt = select(ParticipationRequest).where(ParticipationRequest.id == request_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()
