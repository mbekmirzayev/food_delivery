import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DOCKER_MODE = os.getenv("DOCKER_MODE", "false").lower() == "true"
ENV_FILE = "env/.env.prod" if DOCKER_MODE else "env/.env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    POSTGRES_DB: str = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: int = Field(...)

    REDIS_HOST: str = Field(...)
    REDIS_PORT: int = Field(...)

    SECRET_KEY: str = Field(...)
    JWT_SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = Field(...)
    JWT_ACCESS_TOKEN_EXPIRE_TIME: int = Field(...)
    JWT_REFRESH_TOKEN_EXPIRE_TIME: int = Field(...)

    @property
    def postgresql_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_postgresql_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


settings = Settings()

