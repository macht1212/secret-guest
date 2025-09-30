from src.utils.db_manager import DBManager


class BaseService:
    _db: DBManager | None = None

    def __init__(self, db: DBManager | None = None) -> None:
        self._db = db
