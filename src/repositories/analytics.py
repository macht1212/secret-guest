from fastapi import HTTPException, status
from sqlalchemy import func, select

from src.models.hotels import Hotel
from src.schemas.hotel import Hotel as HotelSchema
from src.schemas.report import ReportRead
from src.models.missions import Mission
from src.models.users import User, UserRole
from src.models.reports import EvaluationCriterion, Report, ReportScore


from .base import BaseRepository


class AnalyticsRepository(BaseRepository):

    model = Report
    schema = ReportRead

    async def get_user_analytics(self, user: User):
        query = select(func.count(Mission.id)).where(Mission.user_id == user.id)
        total_missions = await self.session.execute(query)
        total = total_missions.scalar()

        query = select(func.count(Mission.id)).where(
            Mission.user_id == user.id, Mission.status.in_(["completed", "report_pending", "verified"])
        )
        completed_missions = await self.session.execute(query)
        completed = completed_missions.scalar()

        query = (
            select(func.avg(ReportScore.score))
            .join(Report, Report.id == ReportScore.report_id)
            .join(Mission, Mission.id == Report.mission_id)
            .where(Mission.user_id == user.id)
        )
        avg_score = await self.session.execute(query)
        average_score = avg_score.scalar()

        return {
            "total_missions": total,
            "completed_missions": completed,
            "average_score": round(average_score, 2) if average_score else None,
            "badges": ["Ветеран", "Только Тсс..."] if total >= 10 else ["Только Тсс..."] if user.is_verified else [],
        }

    async def get_hotel_analytics(self, user: User, hotel_id: int):

        query = select(Hotel).filter_by(id=hotel_id)
        result = await self.session.execute(query)
        hotel = HotelSchema.model_validate(result.scalars().one_or_none(), from_attributes=True)

        if not hotel or hotel.partner_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому отелю")

        query = (
            select(
                EvaluationCriterion.name,
                EvaluationCriterion.description,
                func.avg(ReportScore.score).label("avg_score"),
                func.count(ReportScore.id).label("total_reviews"),
            )
            .select_from(ReportScore)
            .join(self.model, self.model.id == ReportScore.report_id)
            .join(Mission, Mission.id == Report.mission_id)
            .join(EvaluationCriterion, EvaluationCriterion.id == ReportScore.criterion_id)
            .where(Mission.hotel_id == hotel_id)
            .group_by(EvaluationCriterion.id, EvaluationCriterion.name)
        )
        scores = await self.session.execute(query)

        criteria_stats = [
            {
                "criterion": row.name,
                "description": row.description,
                "average_score": round(row.avg_score, 2),
                "total_reviews": row.total_reviews,
            }
            for row in scores
        ]

        query = (
            select(Mission.completed_at)
            .where(Mission.hotel_id == hotel_id)
            .order_by(Mission.completed_at.desc())
            .limit(1)
        )
        last_check = await self.session.execute(query)
        last_inspection = last_check.scalar()

        return {
            "hotel_name": hotel.name,
            "criteria_stats": criteria_stats,
            "last_inspection_date": last_inspection,
            "total_inspections": sum(c["total_reviews"] for c in criteria_stats),
        }

    async def get_admin_hotels_analytics(self):
        stats = await self.session.execute(
            select(
                Hotel.name,
                Hotel.city,
                func.count(Mission.id).label("total_missions"),
                func.avg(ReportScore.score).label("avg_score"),
            )
            .select_from(Hotel)
            .outerjoin(Mission, Mission.hotel_id == Hotel.id)
            .outerjoin(self.model, self.model.mission_id == Mission.id)
            .outerjoin(ReportScore, ReportScore.report_id == Report.id)
            .group_by(Hotel.id)
            .order_by(func.avg(ReportScore.score).desc().nulls_last())
        )

        return [
            {
                "hotel": row.name,
                "city": row.city,
                "total_missions": row.total_missions,
                "average_score": round(row.avg_score, 2) if row.avg_score else None,
            }
            for row in stats
        ]

    async def get_admin_users_analytics(self):
        user_stats = await self.session.execute(
            select(
                User.email,
                User.role,
                func.count(Mission.id).label("missions_count"),
                func.avg(ReportScore.score).label("avg_report_quality"),
            )
            .select_from(User)
            .outerjoin(Mission, Mission.user_id == User.id)
            .outerjoin(self.model, self.model.mission_id == Mission.id)
            .outerjoin(ReportScore, ReportScore.report_id == Report.id)
            .where(User.role == UserRole.TRAVELER.value)
            .group_by(User.id)
            .order_by(func.avg(ReportScore.score).desc().nulls_last())
        )

        return [
            {
                "email": row.email,
                "role": row.role,
                "missions_completed": row.missions_count,
                "avg_report_quality": round(row.avg_report_quality, 2) if row.avg_report_quality else None,
            }
            for row in user_stats
        ]
