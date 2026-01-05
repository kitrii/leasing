import datetime

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.data.enums import RoleEnum
from app.db.database import SessionLocal, get_db
from app.models import Payment, Lease, Equipment
from app.models.payment import PaymentStatus
from app.models.user import User
from passlib.context import CryptContext


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


class PaymentCreate(BaseModel):
    lease_id: int
    amount: float
    payment_date: datetime.datetime


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus


class PaymentsByUser(BaseModel):
    user_id: int



@router.post("/payments/create")
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db)
):
    payment = Payment(
        lease_id=payload.lease_id,
        amount=payload.amount,
        # payment_date=payload.payment_date,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.get("/leases/{lease_id}/payments")
def get_payments(lease_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(
            Payment.id.label("payment_id"),
            Payment.amount,
            Payment.status,
            Payment.created_at,
            Payment.due_date,

            Lease.id.label("lease_id"),

            Equipment.id.label("equipment_id"),
            Equipment.name.label("equipment_name"),
        )
        .join(Lease, Payment.lease_id == Lease.id)
        .join(Equipment, Lease.equipment == Equipment.id)
        .filter(Lease.id == lease_id)
        .order_by(Payment.due_date.asc())
        .all()
    )

    return {
        "payments": [
            {
                "id": r.payment_id,
                "amount": r.amount,
                "status": r.status,
                "created_at": r.created_at,
                "due_date": r.due_date,
                "lease_id": r.lease_id,
                "equipment_id": r.equipment_id,
                "equipment_name": r.equipment_name,
            }
            for r in rows
        ]
    }


@router.get("/leases/payments/list")
def get_payments_by_user_id(user_id: int, db: Session = Depends(get_db)):
    payments = (
        db.query(
            Payment.id.label("payment_id"),
            Payment.amount,
            Payment.status,
            Payment.created_at,
            Payment.due_date,

            Lease.id.label("lease_id"),

            Equipment.id.label("equipment_id"),
            Equipment.name.label("equipment_name"),
        )
        .join(Lease, Payment.lease_id == Lease.id)
        .join(Equipment, Lease.equipment == Equipment.id)
        .filter(Lease.user_id == user_id)
        .order_by(Payment.due_date.asc())
        .all()
    )

    return {
        "payments": [
            {
                "id": p.payment_id,
                "amount": p.amount,
                "status": p.status,
                "created_at": p.created_at,
                "due_date": p.due_date,
                "lease_id": p.lease_id,
                "equipment_id": p.equipment_id,
                "equipment_name": p.equipment_name,
            }
            for p in payments
        ]
    }


@router.patch("/leases/{lease_id}/payments/accept")
def accept_payments(
        lease_id: int,
        db: Session = Depends(get_db)
):
    payments = (
        db.query(Payment)
        .filter(
            Payment.lease_id == lease_id,
            Payment.status == PaymentStatus.formed
        )
        .all()
    )

    if not payments:
        raise HTTPException(status_code=400, detail="Нет платежей для подтверждения")

    for payment in payments:
        payment.status = PaymentStatus.accepted

    db.commit()

    return {
        "message": "График платежей подтверждён",
        "payments": [p.to_dict() for p in payments]
    }


from datetime import datetime, timedelta
from sqlalchemy.orm import Session


def generate_payments_for_lease(lease, db: Session):
    try:
        monthly_amount = lease.amount / lease.term

        payments = []
        for i in range(lease.term):
            payments.append(
                Payment(
                    lease_id=lease.id,
                    amount=monthly_amount,
                    due_date=datetime.utcnow() + timedelta(days=30 * (i + 1))                )
            )

        db.add_all(payments)
        db.commit()

    except Exception as e:
        db.rollback()
        print("REAL ERROR:", repr(e))
        raise e
