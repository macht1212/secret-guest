from minio import Minio

from src.config import settings

minio_client = Minio(
    settings.MINIO_URL,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False,
)
