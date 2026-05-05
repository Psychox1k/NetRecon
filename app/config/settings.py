from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent.parent


class BaseAppSettings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent


class Settings(BaseAppSettings):
    API_BASE_URL: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB_PORT: int
    POSTGRES_DB: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    TELEGRAM_BOT_TOKEN: str
    BOT_MODE: str

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
