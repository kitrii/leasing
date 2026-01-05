from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from app.data.enums import LeaseStatus
from app.db.database import get_db
from app.models import Equipment
from app.models.lease import Lease
from app.schemas.lease import LeaseCreateRequest
from app.utils.lease_utils import calculate_lease_amount
from app.utils.payment_utils import generate_payments_for_lease

router = APIRouter()


@router.get("/api/leases/list/{user_id}")
def list_leases(
        user_id: int,
        status: str | None = None,
        order_data: str = "desc",
        db: Session = Depends(get_db)
):
    query = (
        db.query(
            Lease.id,
            Lease.amount,
            Lease.advance,
            Lease.term,
            Lease.rate,
            Lease.payment_scheme,
            Lease.user_id,
            Lease.status,
            Lease.created_at,
            Lease.equipment.label("equipment_id"),
            Equipment.name.label("equipment_name"),
        )
        .join(Equipment, Lease.equipment == Equipment.id)
        .filter(Lease.user_id == user_id)
    )

    if status and status != "all":
        query = query.filter(Lease.status == status)

    query = query.order_by(
        desc(Lease.created_at) if order_data == "desc" else asc(Lease.created_at)
    )

    result = [{
        "id": lease[0],
        "equipment_id": lease[1],
        "amount": lease[2],
        "advance": lease[3],
        "term": lease[4],
        "rate": lease[5],
        "payment_scheme": lease[6],
        "status": lease[7],
        "created_at": lease[8].strftime("%Y-%m-%d %H:%M") if lease[8] else "",
        "user_id": lease[9],
        "equipment_name": lease[10],
    } for lease in query.all()]
    response = {"leases": result}

    return response


@router.get("/api/leases/list")
def list_all_leases(
        status: str | None = None,
        order_data: str = "desc",
        db: Session = Depends(get_db)
):
    query = db.query(Lease)

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
        lease_amount = calculate_lease_amount(
            advance=request.advance,
            rate=request.rate,
            term=request.term
        )
        lease = Lease(
            equipment=request.equipment_id,
            amount=lease_amount,
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
def get_lease_by_id(
        lease_id: int,
        db: Session = Depends(get_db),
):
    lease = db.query(Lease).filter(Lease.id == lease_id).first()

    if not lease:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    return lease.to_dict()


from pydantic import BaseModel


class LeaseStatusUpdate(BaseModel):
    status: str


@router.patch("/api/leases/{lease_id}/status")
def update_lease_status(
        lease_id: int,
        payload: LeaseStatusUpdate,
        db: Session = Depends(get_db),
):
    lease = db.query(Lease).filter(Lease.id == lease_id).first()

    if not lease:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    lease.status = payload.status
    db.commit()
    db.refresh(lease)

    if payload.status == LeaseStatus.contract_created.value:
        generate_payments_for_lease(lease, db)

    return lease.to_dict()
