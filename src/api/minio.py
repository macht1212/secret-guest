from fastapi import APIRouter, File, UploadFile

from src.services.minio import MinioService, bucket_name

router = APIRouter(prefix="/s3", tags=["API для взаимодействия с S3 хранилища."])

minio_service = MinioService()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_data = await file.read()
    return minio_service.load_bfile(bucket_name=bucket_name, file_name=file.filename, file_stream=file_data)


@router.get("/")
async def get_file_list():
    return minio_service.file_list(bucket_name=bucket_name)


@router.post("/create")
async def create_bucket(name: str):
    minio_service.create_bucket(bucket_name=name)
