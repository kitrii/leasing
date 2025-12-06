from sqlalchemy import (create_engine)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
import os
from pathlib import Path
from app.data.constants import DATABASE_URL

# -----------------------------
# Config
# -----------------------------
# DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # week
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# -----------------------------
# DB setup
# -----------------------------
engine = create_engine(DATABASE_URL)
# connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
