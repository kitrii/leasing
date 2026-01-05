from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import hash_password, verify_password
from app.db.database import get_db
from app.models.user import User

from app.schemas.user import RegisterRequest, LoginRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


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
        "user_id": user.id,
        "role": user.role
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
