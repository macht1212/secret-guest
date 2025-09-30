from src.repositories.user import UsersRepository
from src.repositories.hotel import HotelsRepository
from src.repositories.mission import MissionRepository, ParticipationRequestRepository
from src.repositories.report import ReportRepository, EvaluationCriterionRepository
from src.repositories.analytics import AnalyticsRepository


class DBManager:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.hotels = HotelsRepository(self.session)
        self.mission = MissionRepository(self.session)
        self.report = ReportRepository(self.session)
        self.criterion = EvaluationCriterionRepository(self.session)
        self.analytics = AnalyticsRepository(self.session)
        self.requests = ParticipationRequestRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def flush(self):
        await self.session.flush()
