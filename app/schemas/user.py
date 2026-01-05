import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.data.enums import RoleEnum


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user_id: int
    role: RoleEnum


class MessageResponse(BaseModel):
    message: str


class UserReadResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    role: RoleEnum
    created_at: datetime.datetime
    is_active: bool

    class Config:
        orm_mode = True


class UserUpdateProfile(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str
