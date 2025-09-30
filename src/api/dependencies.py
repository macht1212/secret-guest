from typing import Annotated

from fastapi import Depends, Request, HTTPException, status

from src.database import async_sessionmaker_
from src.utils.db_manager import DBManager
from src.services.auth import AuthService
from src.schemas.user import User


async def get_db():
    async with DBManager(session_factory=async_sessionmaker_) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


auth = AuthService()


def get_token_from_request(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен доступа отсутствует.")
    return token


def get_current_user_id(token: str = Depends(get_token_from_request)) -> int:
    payload = auth.decode_token(token=token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен.")
    return user_id


async def get_current_user(user_id: int = Depends(get_current_user_id), db: DBManager = Depends(get_db)) -> User:
    user = await db.users.get_one_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
