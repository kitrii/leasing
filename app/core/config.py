# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # --- GENERAL APP SETTINGS ---
    PROJECT_NAME: str = "Leasing Backend"
    API_V1_PREFIX: str = "/api/v1"

    # --- SECURITY ---
    SECRET_KEY: str = Field("supersecretkey", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # --- DATABASE ---
    POSTGRES_USER: str = Field("leasing_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("leasing_pass", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("leasing", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: str = Field("5432", env="POSTGRES_PORT")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
