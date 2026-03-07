from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Emotion AI Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = ""

    cors_allowed_origins: List[str] = Field(default_factory=lambda: ["*"])

    face_weight: float = 0.6
    speech_weight: float = 0.4

    torch_device: str = "cpu"


@lru_cache
def get_settings() -> Settings:
    return Settings()
