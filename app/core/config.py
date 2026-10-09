"""Application settings loaded from environment variables and the project .env file."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Agentic AI E-Commerce Shopping Assistant API"
    app_env: str = "development"
    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
    api_v1_prefix: str = "/api/v1"
    sqlite_database_path: str = "./storage/sqlite/shopping_assistant.db"
    chroma_persist_directory: str = "./storage/chroma"
    chroma_collection_name: str = "products"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return str(value).upper()

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_v1_prefix(cls, value: str) -> str:
        prefix = value.rstrip("/")
        if not prefix.startswith("/") or prefix == "/":
            raise ValueError("API_V1_PREFIX must be a non-root path beginning with '/'")
        return prefix


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()


settings = get_settings()
