import io
import logging

from minio import Minio, S3Error
from src.connectors.minio import minio_client
from src.config import settings


bucket_name = "documents"


class MinioService:

    def __init__(self) -> None:
        self._client: Minio = minio_client

    def create_bucket(self, bucket_name: str):
        try:
            if not self._client.bucket_exists(bucket_name):
                self._client.make_bucket(bucket_name)
            logging.info("Бакет %s создан.", bucket_name)
        except S3Error as error:
            logging.error("Ошибка %s.", error)

    def load_bfile(self, bucket_name: str, file_name: str, file_stream: bytes) -> str:
        file_stream_io = io.BytesIO(file_stream)
        try:
            self._client.put_object(
                bucket_name=bucket_name,
                object_name=file_name,
                data=file_stream_io,
                length=len(file_stream),
            )
            logging.info("Файл %s загружен в бакет %s.", file_name, bucket_name)
            return f"http://{settings.MINIO_ROOT_HOST}:{settings.MINIO_ROOT_PORT}/{bucket_name}/{file_name}"
        except S3Error as error:
            logging.error("Ошибка %s.", error)
            raise

    def get_file(self, bucket_name: str, file_name: str):
        try:
            response = self._client.get_object(bucket_name, file_name)
            buffer = io.BytesIO()
            for chunc in response.stream(32 * 1024):
                buffer.write(chunc)

            buffer.seek(0)
            logging.info("Файл %s загружен из бакета %s.", file_name, bucket_name)
            response.close()
            response.release_conn()
        except S3Error as error:
            logging.error("Ошибка %s.", error)

    def delete_file(self, bucket_name: str, file_name: str):
        try:
            self._client.remove_object(bucket_name, file_name)
            logging.info("Файл %s удален из бакета %s.", file_name, bucket_name)
        except S3Error as error:
            logging.error("Ошибка %s.", error)

    def file_list(self, bucket_name: str):
        return self._client.list_objects(bucket_name)
