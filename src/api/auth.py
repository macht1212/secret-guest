from fastapi import APIRouter, HTTPException, status, Response

from src.models.users import UserRole
from src.schemas.user import UserRegisterAdd, UserAdd, UserIN, UserPatch, UserPasswordPatch, Password
from src.services.auth import AuthService
from src.utils.verifications import verify_password, verify_role

from .dependencies import DBDep, CurrentUser


auth = AuthService()


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterAdd, db: DBDep, hotel_owner: bool = False):
    try:
        hashed_password = auth.create_hashed_password(user_data.password)

        if hotel_owner:
            user_role = "HOTEL_OWNER"
        else:
            user_role = "TRAVELER"

        new_user_data = UserAdd(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            middle_name=user_data.middle_name,
            city=user_data.city,
            country=user_data.country,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role=user_role,
        )

        await db.users.add(new_user_data)
        await db.commit()
        return {
            "status": "ok",
            "details": {
                "username": f"{user_data.first_name} {user_data.middle_name or '-'} {user_data.last_name}",
                "email": user_data.email,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")


@router.post("/login")
async def login_user(data: UserIN, response: Response, db: DBDep):
    if data.email:
        user = await db.users.get_one_or_none(email=data.email)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не передан email",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Такого пользователя не существует",
        )

    verify_password(data.password, user.hashed_password)

    token = auth.create_auth_token({"user_id": user.id})
    response.set_cookie("access_token", token)
    return {"access_token": token}


@router.get("/me")
async def get_me(user: CurrentUser, db: DBDep):
    return await db.users.get_one_or_none(id=user.id)


@router.get("/all")
async def get_all_users(user: CurrentUser, db: DBDep):
    await verify_role(user, roles=[UserRole.ADMIN.value])
    return await db.users.get_all()


@router.patch("/password", status_code=status.HTTP_202_ACCEPTED)
async def update_user_password(data: UserPasswordPatch, user: CurrentUser, db: DBDep):
    verify_password(data.prev_password, user.hashed_password)

    hashed_password = auth.create_hashed_password(data.new_password)
    await db.users.update(Password(hashed_password=hashed_password), exclude_unset=True, id=user.id)
    await db.commit()


@router.delete("/delete-user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: CurrentUser, db: DBDep):
    await db.users.delete(id=user.id)
    await db.commit()


@router.patch("/update-user", status_code=status.HTTP_202_ACCEPTED)
async def update_user(data: UserPatch, user: CurrentUser, db: DBDep):
    await db.users.update(data=data, exclude_unset=True, id=user.id)
    await db.commit()


@router.post("/logout")
async def logout(responce: Response):
    responce.delete_cookie("access_token")
    return
