from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.data.enums import LeaseStatus
from app.db.database import get_db
from app.models.lease import Lease


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


class LeaseCreateRequest(BaseModel):
    user_id: int
    equipment_id: int
    advance: int
    amount: float
    term: int
    rate: float
    payment_scheme: str | None = None


class LeaseReadResponse(BaseModel):
    id: int
    user_id: int
    equipment_id: int
    amount: float
    term: int
    rate: float
    payment_scheme: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class PaymentRead(BaseModel):
    id: int
    lease_id: int
    amount: float
    date: datetime
    status: str

    class Config:
        orm_mode = True


@router.get("/api/leases/list/{user_id}")
def list_leases(
        user_id: int,
        status: str | None = None,
        order_data: str = "desc",
        db: Session = Depends(get_db)
):
    query = db.query(Lease).filter(Lease.user_id == user_id)

    if status and status != "all":
        query = query.filter(Lease.status == status)

    if order_data == "asc":
        query = query.order_by(Lease.created_at.asc())
    else:
        query = query.order_by(Lease.created_at.desc())

    result = [lease.to_dict() for lease in query.all()]
    response = {"leases": result}

    return response


@router.post("/api/leases/create")
def create_lease(request: LeaseCreateRequest, db: Session = Depends(get_db)):
    try:
        lease = Lease(
            equipment=request.equipment_id,
            amount=request.advance + float(request.term) * float(request.rate),
            advance=request.advance,
            term=request.term,
            rate=request.rate,
            payment_scheme=request.payment_scheme,
            status=LeaseStatus.send,
            user_id=request.user_id
        )
        db.add(lease)
        db.commit()
        db.refresh(lease)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при создании заявок!")
    return {"success": True,
            "lease": lease.to_dict(),
            "message": "Заявка создана!"}


@router.get("/api/leases/{lease_id}")
def get_lease(lease_id: int, db: Session = Depends(get_db)):
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(404, "Заявка не найдена")
    return lease.to_dict()
