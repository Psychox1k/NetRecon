from functools import lru_cache
from .settings import BaseAppSettings, Settings, settings

__all__ = ["BaseAppSettings", "Settings", "settings"]


@lru_cache()
def get_settings() -> BaseAppSettings:
    return Settings()
