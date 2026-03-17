import os
from functools import lru_cache
from .settings import Settings, BaseAppSettings

@lru_cache()
def get_settings() -> BaseAppSettings:
    return Settings()
