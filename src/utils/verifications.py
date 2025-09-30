from fastapi import HTTPException, status

from src.services.auth import AuthService
from src.schemas.user import User


auth = AuthService()


async def verify_role(user: User, roles: list[str]):
    if user.role not in roles:
        print(user.role)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Необходимы права {roles}.")
    return


def verify_password(plain_password, hashed_password):
    if not auth.verify_password(plain_password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Введен некорректный пароль",
        )
    return
