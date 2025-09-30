from fastapi import APIRouter

from src.models.users import UserRole
from src.utils.verifications import verify_role

from .dependencies import DBDep, CurrentUser


router = APIRouter(prefix="/analytics", tags=["Аналитика по пользователям и отчетам"])


@router.get("/traveler")
async def get_traveler_analytics(user: CurrentUser, db: DBDep):
    await verify_role(user, [UserRole.TRAVELER.value])
    return await db.analytics.get_user_analytics(user=user)


@router.get("/hotels/{hotel_id}")
async def get_hotel_analytics(hotel_id: int, user: CurrentUser, db: DBDep):
    return await db.analytics.get_hotel_analytics(user=user, hotel_id=hotel_id)


@router.get("/admin/hotels")
async def get_admin_hotel_analytics(user: CurrentUser, db: DBDep):
    await verify_role(user, [UserRole.ADMIN.value])
    return await db.analytics.get_admin_hotels_analytics()


@router.get("/admin/users")
async def get_admin_user_analytics(user: CurrentUser, db: DBDep):
    await verify_role(user, [UserRole.ADMIN.value])
    return await db.analytics.get_admin_users_analytics()


@router.get("/criteria")
async def get_evaluation_criteria(db: DBDep):
    return await db.criterion.get_all()
