from datetime import datetime
from sqlalchemy import Integer, DateTime, Boolean, Column, Enum as SAEnum, String
from sqlalchemy.orm import relationship
from app.data.enums import RoleEnum
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    role = Column(SAEnum(RoleEnum), default=RoleEnum.client)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Связь с лизинговыми заявками
    leases = relationship("Lease", back_populates="user", cascade="all, delete-orphan")
