from fastapi import UploadFile, HTTPException

from app.core.minio_client import client, ensure_public_bucket
from app.core.config import MINIO_HOST
import uuid



def upload_image_to_minio(file: UploadFile, bucket_name: str) -> str:
    """
    Загружает файл в MinIO и возвращает публичный URL.
    """
    ensure_public_bucket(client, bucket_name)

    # Генерация уникального имени файла
    file_ext = file.filename.split(".")[-1]
    object_name = f"{uuid.uuid4()}.{file_ext}"

    try:
        # Попытка создать бакет (если ещё не создан)
        client.make_bucket(bucket_name)
    except Exception:
        pass  # бакет уже существует

    try:
        client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type
        )
        return f"http://{MINIO_HOST}/{bucket_name}/{object_name}"
    except Exception:
        raise HTTPException(status_code=400, detail="Ошибка при загрузке изображения в MinIO!")
