from datetime import datetime
from pydantic import BaseModel
from app.models.payment import PaymentStatus

class PaymentCreate(BaseModel):
    lease_id: int
    amount: float
    payment_date: datetime | None = None


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus


class PaymentsByUser(BaseModel):
    user_id: int
