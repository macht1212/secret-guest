from fastapi import APIRouter, HTTPException, status
from src.api.dependencies import CurrentUser, DBDep
from src.models.users import UserRole
from src.schemas.mission import ParticipationRequestRead, ParticipationRequestApproveReject, Verification
from src.utils.verifications import verify_role

router = APIRouter(prefix="/requests", tags=["Подача и обработка заявок."])


@router.post("/", response_model=ParticipationRequestRead, status_code=status.HTTP_200_OK)
async def submit_participation_request(
    user: CurrentUser,
    db: DBDep,
):
    await verify_role(user=user, roles=[UserRole.TRAVELER.value])
    if user.is_verified:
        raise HTTPException(400, "Вы уже участник программы.")
    return await db.requests.create_request(user_id=user.id)


@router.get("/me", response_model=ParticipationRequestRead)
async def get_my_request(
    user: CurrentUser,
    db: DBDep,
):
    await verify_role(user=user, roles=[UserRole.TRAVELER.value])
    request = await db.requests.get_user_request(user_id=user.id)
    if not request:
        raise HTTPException(404, "Заявка не найдена.")
    return request


@router.get("/pending", response_model=list[ParticipationRequestRead])
async def get_pending_requests(
    user: CurrentUser,
    db: DBDep,
):
    await verify_role(user=user, roles=[UserRole.ADMIN.value])
    return await db.requests.get_all_pending()


@router.post("/approve", response_model=ParticipationRequestRead, status_code=status.HTTP_202_ACCEPTED)
async def approve_request(
    data: ParticipationRequestApproveReject,
    user: CurrentUser,
    db: DBDep,
):
    await verify_role(user=user, roles=[UserRole.ADMIN.value])
    if data.action != "approve":
        raise HTTPException(400, "Неверное действие")

    request = await db.requests.approve_request(request_id=data.request_id, reviewer_id=user.id)

    request_obj = await db.requests.get_request_by_id(data.request_id)

    data_verification = Verification(is_verified=True)
    await db.users.update(data=data_verification, id=request_obj.user_id)
    await db.commit()

    return request


@router.post("/reject", response_model=ParticipationRequestRead, status_code=status.HTTP_202_ACCEPTED)
async def reject_request(
    data: ParticipationRequestApproveReject,
    user: CurrentUser,
    db: DBDep,
):
    await verify_role(user=user, roles=[UserRole.ADMIN.value])
    if data.action != "reject":
        raise HTTPException(400, "Неверное действие")
    return await db.requests.reject_request(request_id=data.request_id, reviewer_id=user.id)
