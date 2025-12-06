from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from app.db.database import Base

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"))
    date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float)
    status = Column(String, default="Не оплачено")