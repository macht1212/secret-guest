import asyncio

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.utils.db_manager import DBManager
from src.schemas.user import UserAdd
from src.schemas.hotel import Hotel
from src.schemas.report import EvaluationCriterionRead
from src.services.auth import AuthService

auth = AuthService()

users = [
    {
        "id": 1,
        "email": "admin@ostrovok.ru",
        "first_name": "Валентин",
        "middle_name": "Валентинович",
        "last_name": "Валентинов",
        "phone": "+7 999 999 99 99",
        "city": "Москва",
        "country": "Россия",
        "is_verified": True,
        "password": "password",
        "role": "ADMIN",
    },
    {
        "id": 2,
        "email": "first.traveler@gmail.com",
        "first_name": "Александр",
        "middle_name": "Александрович",
        "last_name": "Александров",
        "phone": "+7 999 888 88 88",
        "city": "Москва",
        "country": "Россия",
        "is_verified": False,
        "password": "password",
        "role": "TRAVELER",
    },
    {
        "id": 3,
        "email": "second.traveler@gmail.com",
        "first_name": "Игорь",
        "middle_name": "Игоревич",
        "last_name": "Игорев",
        "phone": "+7 999 777 77 77",
        "city": "Москва",
        "country": "Россия",
        "is_verified": False,
        "password": "password",
        "role": "TRAVELER",
    },
    {
        "id": 4,
        "email": "third.traveler@gmail.com",
        "first_name": "Петр",
        "middle_name": "Петрович",
        "last_name": "Петров",
        "phone": "+7 999 666 66 66",
        "city": "Казань",
        "country": "Россия",
        "is_verified": False,
        "password": "password",
        "role": "TRAVELER",
    },
    {
        "id": 5,
        "email": "fourth.traveler@gmail.com",
        "first_name": "Иван",
        "middle_name": "Иванович",
        "last_name": "Иванов",
        "phone": "+ 7 999 555 55 55",
        "city": "Новосибирск",
        "country": "Россия",
        "is_verified": False,
        "password": "password",
        "role": "TRAVELER",
    },
    {
        "id": 6,
        "email": "hilton@hilton.com",
        "first_name": "Сергей",
        "middle_name": "Сергеевич",
        "last_name": "Сергеев",
        "phone": "+7 495 333 33 33",
        "city": "Москва",
        "country": "Россия",
        "is_verified": False,
        "password": "password",
        "role": "HOTEL_OWNER",
    },
    {
        "id": 7,
        "email": "marriot@marriot.com",
        "first_name": "Кирилл",
        "middle_name": "Кириллович",
        "last_name": "Кириллов",
        "phone": "+7 495 111 11 11",
        "city": "Москва",
        "country": "Россия",
        "is_verified": False,
        "password": "password",
        "role": "HOTEL_OWNER",
    },
]

hotels = [
    {
        "id": 1,
        "name": "Hilton",
        "address": "улица",
        "city": "Москва",
        "country": "Россия",
        "lat": 0.0,
        "lng": 0.0,
        "partner_id": 6,
    },
    {
        "id": 2,
        "name": "Hilton",
        "address": "улица",
        "city": "Новосибирск",
        "country": "Россия",
        "lat": 0.0,
        "lng": 0.0,
        "partner_id": 6,
    },
    {
        "id": 3,
        "name": "Marriot",
        "address": "улица",
        "city": "Москва",
        "country": "Россия",
        "lat": 0.0,
        "lng": 0.0,
        "partner_id": 7,
    },
    {
        "id": 4,
        "name": "Marriot",
        "address": "улица",
        "city": "Казань",
        "country": "Россия",
        "lat": 0.0,
        "lng": 0.0,
        "partner_id": 7,
    },
]

criterions = [
    {"id": 1, "name": "Чистота", "description": "Чистота в номере.", "is_required": True},
    {
        "id": 2,
        "name": "Удобства",
        "description": "Соответствие предоставляемых удобств перечисленным в карточке отеля.",
        "is_required": False,
    },
]


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    MINIO_ROOT_HOST: str
    MINIO_ROOT_PORT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ROOT_BUCKET_NAME: str

    @property
    def DB_URL_LOCAL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@localhost:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


engine_local = create_async_engine(url=settings.DB_URL_LOCAL)
async_sessionmaker_local = async_sessionmaker(bind=engine_local, expire_on_commit=False)


async def load_data_to_db():
    async with DBManager(session_factory=async_sessionmaker_local) as session:
        for user in users:
            user["hashed_password"] = auth.create_hashed_password(user.get("password"))
            await session.users.add(UserAdd(**user))
        for hotel in hotels:
            await session.hotels.add(Hotel(**hotel))
        for criterion in criterions:
            await session.criterion.add(EvaluationCriterionRead(**criterion))

        await session.commit()


if __name__ == "__main__":
    asyncio.run(load_data_to_db())
