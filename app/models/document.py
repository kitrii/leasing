# from datetime import datetime
#
# from sqlalchemy import Integer, DateTime, Column, ForeignKey, String
#
# from app.db.database import Base
#
#
# class Document(Base):
#     __tablename__ = "documents"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
#     application_id = Column(Integer, ForeignKey('applications.id'), nullable=True)
#     filename = Column(String, nullable=False)
#     url = Column(String, nullable=False)
#     uploaded_at = Column(DateTime, default=datetime.utcnow)
