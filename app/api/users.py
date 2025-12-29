import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.data.enums import RoleEnum
from app.db.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    full_name: str | None = None
    phone: str | None = None
    role: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class MessageResponse(BaseModel):
    message: str


class LoginResponse(BaseModel):
    message: str
    user_id: int


class UserReadResponse(BaseModel):
    id: int
    email: str
    full_name: str | None
    phone: str | None
    role: RoleEnum
    created_at: datetime.datetime
    is_active: bool

    class Config:
        from_attributes = True


def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=400,
            detail="Пароль слишком длинный (максимум 72 байта)"
        )

    return pwd_context.hash(password_bytes)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


@router.post("/register")
def register_user(
        request: RegisterRequest,
        db: Session = Depends(get_db)
):
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким email уже существует"
        )

    user = User(
        email=request.email,
        full_name=request.full_name,
        phone=request.phone,
        hashed_password=hash_password(request.password),
        role=request.role.lower()
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ошибка при создании пользователя в БД!"
        )

    return {"message": "Регистрация успешна"}


@router.post("/login")
def login_user(
        request: LoginRequest,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Пользователя с данным email не существует в БД"
        )

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Неверный пароль"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Пользователь заблокирован"
        )

    return {
        "message": "Вход выполнен успешно",
        "user_id": user.id
    }


@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return user


from typing import Optional


class UserUpdateProfile(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


@router.patch("/users/{user_id}/profile")
def update_user_profile(
        user_id: int,
        data: UserUpdateProfile,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if data.email is not None:
        user.email = data.email

    if data.full_name is not None:
        user.full_name = data.full_name

    if data.phone is not None:
        user.phone = data.phone

    db.commit()
    db.refresh(user)

    return {"message": "Профиль обновлён"}


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str


@router.post("/users/{user_id}/change-password")
def change_user_password(
        user_id: int,
        data: UserChangePassword,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный старый пароль")

    user.hashed_password = hash_password(data.new_password)

    db.commit()

    return {"message": "Пароль успешно изменён"}