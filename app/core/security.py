from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Хеширование пароля с проверкой длины.
    """
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
    """
    Проверка соответствия пароля и хеша.
    """
    return pwd_context.verify(password, hashed_password)
