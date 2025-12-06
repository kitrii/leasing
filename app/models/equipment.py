# from datetime import datetime
#
# from sqlalchemy import Integer, DateTime, Column, Text, Float, JSON, ForeignKey, String
# from sqlalchemy.orm import relationship
#
# from app.db.database import Base
#
# class Equipment(Base):
#     __tablename__ = "equipments"
#     id = Column(Integer, primary_key=True)
#     supplier_id = Column(Integer, ForeignKey('supplier_profiles.id'))
#     name = Column(String, nullable=False)
#     description = Column(Text, nullable=True)
#     price = Column(Float, nullable=False)
#     quantity = Column(Integer, default=1)
#     params = Column(JSON, nullable=True)  # e.g. {"power":"1200kW","voltage":"380V"}
#     images = Column(JSON, nullable=True)  # list of image URLs
#     created_at = Column(DateTime, default=datetime.utcnow)
#
#     supplier = relationship("SupplierProfile", back_populates="equipments")
#     applications = relationship("Application", back_populates="equipment")