from enum import Enum

from app.db.database import Base

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum as Senam, Boolean
from datetime import datetime


class PaymentStatus(str, Enum):
    pending = "Ожидает"  # Платеж запланирован, но еще не произведен
    paid = "Оплачен"  # Платеж выполнен
    overdue = "Просрочен"  # Платеж просрочен


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"))
    amount = Column(Float, nullable=False)  # Сумма платежа
    due_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # Дата платежа
    status = Column(Senam(PaymentStatus), default=PaymentStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "lease_id": self.lease_id,
            "amount": self.amount,
            "status": self.status,
            "due_date": self.due_date.strftime("%Y-%m-%d %H:%M") if self.due_date else "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
        }
