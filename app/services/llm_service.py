"""Lazy, reusable LangChain chat model configuration for Ollama."""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import AnyHttpUrl, Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
logger = logging.getLogger(__name__)


class LLMConfigurationError(RuntimeError):
    """Raised when the configured LLM cannot be initialized."""


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    llm_provider: Literal["ollama"] = Field(validation_alias="LLM_PROVIDER")
    ollama_api_key: SecretStr | None = Field(default=None, validation_alias="OLLAMA_API_KEY")
    ollama_api_url: AnyHttpUrl = Field(validation_alias="OLLAMA_API_URL")
    ollama_model: str = Field(min_length=1, validation_alias="OLLAMA_MODEL")

    @field_validator("llm_provider", mode="before")
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        return str(value).strip().lower()

    @field_validator("ollama_api_key", mode="before")
    @classmethod
    def empty_api_key_is_optional(cls, value: str | None) -> str | None:
        if value is None or not str(value).strip():
            return None
        return value

    @field_validator("ollama_model")
    @classmethod
    def normalize_model(cls, value: str) -> str:
        model = value.strip()
        if not model:
            raise ValueError("OLLAMA_MODEL must not be empty")
        return model


class LLMService:
    """Construct and cache the configured LangChain chat model on first use."""

    def __init__(self, settings: LLMSettings | None = None, client_factory: Any = None) -> None:
        self._settings = settings
        self._client_factory = client_factory
        self._chat_model: Any = None

    def get_chat_model(self) -> Any:
        if self._chat_model is not None:
            return self._chat_model

        try:
            settings = self._settings or LLMSettings()
        except ValidationError as exc:
            raise LLMConfigurationError(
                "LLM configuration is incomplete or invalid; set LLM_PROVIDER, "
                "OLLAMA_API_URL, and OLLAMA_MODEL in .env"
            ) from exc

        client_factory = self._client_factory
        if client_factory is None:
            try:
                from langchain_ollama import ChatOllama
            except ImportError as exc:
                raise LLMConfigurationError(
                    "The Ollama integration is unavailable; install project requirements"
                ) from exc
            client_factory = ChatOllama

        client_options: dict[str, Any] = {}
        if settings.ollama_api_key is not None:
            client_options["headers"] = {
                "Authorization": f"Bearer {settings.ollama_api_key.get_secret_value()}"
            }

        try:
            self._chat_model = client_factory(
                model=settings.ollama_model,
                base_url=str(settings.ollama_api_url),
                client_kwargs=client_options,
            )
        except Exception as exc:
            logger.exception("Could not initialize the configured Ollama chat model")
            raise LLMConfigurationError("Could not initialize the configured Ollama model") from exc

        logger.info("Initialized Ollama chat model: %s", settings.ollama_model)
        return self._chat_model


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    """Return the shared lazy LLM service without loading credentials at import time."""
    return LLMService()
