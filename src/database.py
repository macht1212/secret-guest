from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


engine = create_async_engine(url=settings.DB_URL)
engine_local = create_async_engine(url=settings.DB_URL_LOCAL)
async_sessionmaker_ = async_sessionmaker(bind=engine, expire_on_commit=False)
async_sessionmaker_local = async_sessionmaker(bind=engine_local, expire_on_commit=False)


class Base(DeclarativeBase): ...
