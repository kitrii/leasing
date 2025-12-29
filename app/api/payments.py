import datetime

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.data.enums import RoleEnum
from app.db.database import SessionLocal, get_db
from app.models import Payment
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
    payments = db.query(Payment).filter(Payment.lease_id == lease_id).all()
    return {"payments": [payment.to_dict() for payment in payments]}
