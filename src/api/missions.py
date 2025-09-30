from fastapi import APIRouter, HTTPException, status

from src.models.users import UserRole
from src.schemas.mission import MissionRead
from src.models.missions import MissionStatus
from src.utils.verifications import verify_role
from .dependencies import CurrentUser, DBDep


router = APIRouter(prefix="/mission", tags=["Управдение миссиями."])


@router.get("/available-missions")
async def get_available_mission(user: CurrentUser, db: DBDep):
    await verify_role(user=user, roles=[UserRole.TRAVELER.value])

    if not user.city or not user.country:
        raise HTTPException(400, "Укажите город и страну в профиле")
    return await db.mission.get_hotels_with_mission_status(user=user, city=user.city, country=user.country)


@router.post("/assign_mission", status_code=status.HTTP_202_ACCEPTED)
async def assign_mission(hotel_id: int, user: CurrentUser, db: DBDep):
    mission = await db.mission.assign_mission(user=user, hotel_id=hotel_id)
    await db.commit()
    return {"mission_id": mission.id, "status": mission.status, "deadline": mission.deadline}


@router.get("/my-missions", response_model=list[MissionRead])
async def get_my_missions(user: CurrentUser, db: DBDep):
    return await db.mission.get_user_missions(user=user)


@router.post("/start-mission", status_code=status.HTTP_202_ACCEPTED)
async def start_mission(mission_id: int, db: DBDep):
    await db.mission.update_status(mission_id=mission_id, new_status=MissionStatus.in_progress.value)
    await db.commit()
