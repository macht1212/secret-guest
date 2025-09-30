from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.missions import Mission
from src.repositories.base import BaseRepository
from src.models.reports import Report, ReportScore, ReportPhoto, ReportStatus, EvaluationCriterion
from src.schemas.report import ReportRead, ReportScoreCreate, EvaluationCriterionRead


class ReportRepository(BaseRepository):
    model = Report
    schema = ReportRead

    async def create_report_with_details(
        self,
        mission_id: int,
        overall_comment: str | None,
        scores: list[ReportScoreCreate],
        photo_urls: list[str],
    ):
        report = Report(
            mission_id=mission_id,
            overall_comment=overall_comment,
            status=ReportStatus.pending,
        )
        self.session.add(report)
        await self.session.flush()

        for s in scores:
            self.session.add(
                ReportScore(
                    report_id=report.id,
                    criterion_id=s.criterion_id,
                    score=s.score,
                    comment=s.comment,
                )
            )

        for url in photo_urls:
            self.session.add(
                ReportPhoto(
                    report_id=report.id,
                    photo_url=url,
                )
            )

        await self.session.commit()
        await self.session.refresh(report)

        full = await self._get_full_report(report.id)
        return self.schema.model_validate(full, from_attributes=True)

    async def _get_full_report(self, report_id: int):
        stmt = (
            select(self.model)
            .where(self.model.id == report_id)
            .options(
                selectinload(self.model.scores).selectinload(ReportScore.criterion),
                selectinload(self.model.photos),
                selectinload(self.model.mission).selectinload(Mission.hotel),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()


class EvaluationCriterionRepository(BaseRepository):
    model = EvaluationCriterion
    schema = EvaluationCriterionRead
