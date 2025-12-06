# from app.data.constants import DATABASE_URL
#
# if __name__ == "__main__":
#     from sqlalchemy import create_engine
#
#     engine = create_engine(DATABASE_URL)
#     with engine.connect() as conn:
#         print("Connected!", conn)


from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.api import users, dashboard
from app.db.database import Base, engine
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)


# Подключаем роутеры
app.include_router(users.router)
app.include_router(dashboard.router)


# Главная страница
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# GET — показать форму входа
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, message: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "message": message})

# Страница входа
# @app.post("/login", response_class=HTMLResponse)
# def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == email).first()
#     if not user or password != user.hashed_password:
#         return templates.TemplateResponse("login.html", {"request": request, "message": "Неверный email или пароль"})
#     # Успешный вход — редирект в личный кабинет
#     response = RedirectResponse(url="/dashboard", status_code=303)
#     # Тут можно добавить cookie или JWT токен
#     return response
