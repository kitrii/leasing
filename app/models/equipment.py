from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    power = Column(Float, nullable=True)
    year = Column(Integer, nullable=True)
    image_url = Column(String, nullable=True)
