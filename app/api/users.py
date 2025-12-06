from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserRead
from passlib.context import CryptContext

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# регистрация через форму
@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
def register_user(
        request: Request,
        email: str = Form(...),
        full_name: str = Form(None),
        phone: str = Form(None),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    # hashed_password = pwd_context.hash(password)
    hashed_password = password
    user = User(email=email, full_name=full_name, phone=phone, hashed_password=hashed_password)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        message = "Пользователь создан!"
    except IntegrityError:
        db.rollback()
        message = "Ошибка: пользователь с таким email уже существует."
    except SQLAlchemyError:
        db.rollback()
        message = "Ошибка при создании пользователя."
    return templates.TemplateResponse("register.html", {"request": request, "message": message})


# просмотр данных пользователя
@router.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return {"error": "User not found"}
    return user


# @router.post("/login")
# def login_user(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == email).first()
#     if not user or not password:
#         # перенаправляем обратно на login с сообщением
#         return templates.TemplateResponse("login.html", {"request": request, "message": "Неверный email или пароль"})
#     # Успешный вход — можно редиректить на главную или личный кабинет
#     response = RedirectResponse(url="/dashboard", status_code=303)
#     return response

@router.post("/login", response_class=HTMLResponse)
def login_user(request: Request,
               email: str = Form(...),
               password: str = Form(...),
               db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user or user.hashed_password != password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Неверный email или пароль"
        })

    # Успех — добавляем user_id в Session cookie
    request.session["user_id"] = user.id

    return RedirectResponse("/dashboard", status_code=303)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)