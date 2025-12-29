from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from app.data.enums import LeasePaymentScheme, LeaseStatus
from app.db.database import Base


class Lease(Base):
    __tablename__ = "leases"
    id = Column(Integer, primary_key=True, index=True)
    equipment = Column(Integer)
    amount = Column(Float)
    advance = Column(Float)
    term = Column(Integer)  # в месяцах
    rate = Column(Float)
    payment_scheme = Column(SAEnum(LeasePaymentScheme), default=LeasePaymentScheme.annuity)
    status = Column(SAEnum(LeaseStatus), default=LeaseStatus.send)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="leases")

    def to_dict(self):
        return {
            "id": self.id,
            "equipment": self.equipment,
            "amount": self.amount,
            "advance": self.advance,
            "term": self.term,
            "rate": self.rate,
            "payment_scheme": self.payment_scheme,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
            "user_id": self.user_id
        }
