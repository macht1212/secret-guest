from datetime import datetime
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status

from src.utils.verifications import verify_role
from .dependencies import DBDep, CurrentUser
from src.schemas.report import EvaluationCriterion, ReportScoreCreate
from src.models.users import UserRole
from src.services.minio import MinioService, bucket_name

router = APIRouter(prefix="/reports", tags=["Создание отчетов."])

minio_service = MinioService()


@router.post("/submit")
async def submit_report(
    user: CurrentUser,
    db: DBDep,
    mission_id: int = Form(...),
    overall_comment: str | None = Form(None),
    scores_json: str = Form(...),
    photos: list[UploadFile] = File([]),
):
    try:
        scores_data = json.loads(scores_json)
        scores = [ReportScoreCreate(**s) for s in scores_data]
    except Exception as e:
        raise HTTPException(400, f"Некорректный формат оценок: {e}")

    mission = await db.mission.get_one_or_none(id=mission_id)
    if not mission or mission.user_id != user.id:
        raise HTTPException(404, "Миссия не найдена")
    if mission.status not in ["in_progress", "completed"]:
        raise HTTPException(400, "Нельзя отправить отчёт для этой миссии")

    photo_urls = []
    for photo in photos:
        if photo.size == 0:
            continue
        timestamp = int(datetime.now().timestamp())
        safe_name = f"report_{mission_id}_{timestamp}_{photo.filename}"
        url = minio_service.load_bfile(bucket_name=bucket_name, file_name=safe_name, file_stream=await photo.read())
        photo_urls.append(url)

    report = await db.report.create_report_with_details(
        mission_id=mission_id, overall_comment=overall_comment, scores=scores, photo_urls=photo_urls
    )

    await db.mission.update_status(mission_id, "report_pending")

    return {"report_id": report.id, "status": "report_pending"}


@router.post("/create-criterion", status_code=status.HTTP_201_CREATED)
async def create_criterion(user: CurrentUser, datas: list[EvaluationCriterion], db: DBDep):
    await verify_role(user=user, roles=[UserRole.ADMIN.value])
    for data in datas:
        await db.criterion.add(data=data)
    await db.commit()
