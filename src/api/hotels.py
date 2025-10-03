from fastapi import APIRouter, HTTPException, status

from src.schemas.hotel import HotelPatch, HotelSchema
from src.models.users import UserRole
from src.utils.verifications import verify_role

from .dependencies import DBDep, CurrentUser


router = APIRouter(prefix="/hotel", tags=["Создание и управление отелями"])


@router.post("/add-hotel", status_code=status.HTTP_201_CREATED)
async def add_hotel(data: HotelSchema, user: CurrentUser, db: DBDep):
    await verify_role(user=user, roles=[UserRole.ADMIN.value, UserRole.HOTEL_OWNER.value])

    data_dict = data.model_dump()
    data_dict["partner_id"] = user.id
    data = HotelSchema(**data_dict)

    result = await db.hotels.add(data=data)
    await db.commit()

    return {"data": result}


@router.patch("/patch-hotel", status_code=status.HTTP_202_ACCEPTED)
async def update_hotel(id: int, data: HotelPatch, user: CurrentUser, db: DBDep):
    await verify_role(user=user, roles=[UserRole.ADMIN.value, UserRole.HOTEL_OWNER.value])

    hotel_info = await db.hotels.get_one_or_none(id=id)
    if hotel_info.partner_id == user.id:
        result = await db.hotels.update(data=data, exclude_unset=True, id=id)
        await db.commit()
        return {"data": result}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Не хватает прав для совершения данного действия."
        )


@router.delete("/delete-hotel", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hotel(id: int, user: CurrentUser, db: DBDep):
    await verify_role(user=user, roles=[UserRole.ADMIN.value, UserRole.HOTEL_OWNER.value])

    hotel_info = await db.hotels.get_one_or_none(id=id)
    if hotel_info.partner_id == user.id:
        await db.hotels.delete(id=id)
        await db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Не хватает прав для совершения данного действия."
        )


@router.get("/all-hotels")
async def get_all_hotels(db: DBDep, user: CurrentUser):
    return await db.hotels.get_filtered(partner_id=user.id)
