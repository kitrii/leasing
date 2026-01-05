from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.constants import DEFAULT_IMAGE_URL
from app.db.database import get_db
from app.models.equipment import Equipment

from app.utils.minio_utils import upload_image_to_minio
from typing import Optional
from fastapi import Query

router = APIRouter()


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
        image_url = upload_image_to_minio(image, bucket_name=type.lower())
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


@router.get("/equipment/{id}")
def get_equipment_by_id(
        id: int,
        db: Session = Depends(get_db),
):
    query = db.query(Equipment).filter(Equipment.id == id)
    result = query.first()
    if not result:
        raise HTTPException(status_code=404,
                            detail=f"Оборудование по ID = {id} не было найдено! Перепроверьте данные!")

    response = {"data": result}
    return response
