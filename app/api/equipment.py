
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.minio_client import client, MINIO_BUCKET, ensure_public_bucket
from app.db.database import get_db
from app.models.equipment import Equipment
import uuid

router = APIRouter()

DEFAULT_IMAGE_URL = "https://placehold.co/300x300?text=No+Image"


@router.post("/equipment/create")
def create_equipment(
        type: str = Form(...),
        name: str = Form(...),
        description: str = Form(None),
        price: float = Form(...),
        power: float = Form(None),
        year: int = Form(None),
        image: UploadFile = File(None),
        db: Session = Depends(get_db),
):
    if image:
        # Генерация уникального имени файла
        file_ext = image.filename.split(".")[-1]
        object_name = f"{uuid.uuid4()}.{file_ext}"

        bucket_name = type.lower()  # тип оборудования
        ensure_public_bucket(client, bucket_name)

        try:
            client.make_bucket(bucket_name)
        except Exception:
            pass  # бакет уже есть, ничего не делаем

        # Загрузка в MinIO
        try:
            client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=image.file,
                length=-1,
                part_size=10 * 1024 * 1024,  # 10MB
                content_type=image.content_type
            )

            MINIO_HOST = "localhost:9000"
            image_url = f"http://{MINIO_HOST}/{bucket_name}/{object_name}"
        except Exception as error:
            raise HTTPException(status_code=400, detail="Ошибка при загрузке в MINIO!")
    else:
        image_url = DEFAULT_IMAGE_URL

    equipment = Equipment(
        type=type,
        name=name,
        description=description,
        price=price,
        power=power,
        year=year,
        image_url=image_url
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


from typing import List, Optional
from fastapi import Query


@router.get("/equipment/")
def get_equipment(
        type: Optional[str] = None,
        min_price: Optional[float] = Query(None),
        max_price: Optional[float] = Query(None),
        min_power: Optional[float] = Query(None),
        max_power: Optional[float] = Query(None),
        min_year: Optional[int] = Query(None),
        max_year: Optional[int] = Query(None),
        db: Session = Depends(get_db),
):
    query = db.query(Equipment)

    if type:
        query = query.filter(Equipment.type == type)
    if min_price:
        query = query.filter(Equipment.price >= min_price)
    if max_price:
        query = query.filter(Equipment.price <= max_price)
    if min_power:
        query = query.filter(Equipment.power >= min_power)
    if max_power:
        query = query.filter(Equipment.power <= max_power)
    if min_year:
        query = query.filter(Equipment.year >= min_year)
    if max_year:
        query = query.filter(Equipment.year <= max_year)

    response = {"data": query.all()}

    return response
