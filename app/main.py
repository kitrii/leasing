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
from starlette.middleware.cors import CORSMiddleware

from app.api import users, leases, payments, calculator, equipment
from app.db.database import Base, engine


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # nuxt dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)


# Подключаем роутеры
app.include_router(users.router)
app.include_router(leases.router)
app.include_router(payments.router)
app.include_router(calculator.router)
app.include_router(equipment.router)

