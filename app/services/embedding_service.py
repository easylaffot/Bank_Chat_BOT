"""Shared Ollama embedding model configuration and calls."""

import logging
from typing import Any

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class EmbeddingConfiguration(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    model_name: str = Field(
        default="BAAI/bge-small-en-v1.5",
        validation_alias="FASTEMBED_MODEL",
    )

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        model_name = value.strip()
        if not model_name:
            raise ValueError("FASTEMBED_MODEL must not be empty")
        return model_name


class EmbeddingServiceError(RuntimeError):
    """Raised when embedding model initialization or inference fails."""


class _FastEmbedAdapter:
    """Adapt FastEmbed iterators to the embedding service's list-based interface."""

    def __init__(self, model: Any) -> None:
        self._model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        vector = next(iter(self._model.query_embed(text)), None)
        if vector is None:
            raise EmbeddingServiceError("FastEmbed returned no vector for the query")
        return vector.tolist()


class EmbeddingService:
    """Lazily create and reuse the configured Ollama embeddings client."""

    def __init__(self, configuration: EmbeddingConfiguration | None = None, client_factory: Any = None) -> None:
        self._configuration = configuration
        self._client_factory = client_factory
        self._embeddings: Any = None

    def get_embeddings(self) -> Any:
        if self._embeddings is not None:
            return self._embeddings

        try:
            configuration = self._configuration or EmbeddingConfiguration()
        except ValidationError as exc:
            raise EmbeddingServiceError("FASTEMBED_MODEL is invalid") from exc

        client_factory = self._client_factory
        if client_factory is None:
            try:
                from fastembed import TextEmbedding
            except ImportError as exc:
                raise EmbeddingServiceError(
                    "FastEmbed is unavailable; install project requirements"
                ) from exc
            client_factory = TextEmbedding

        try:
            self._embeddings = _FastEmbedAdapter(
                client_factory(model_name=configuration.model_name)
            )
        except Exception as exc:
            logger.exception("Could not initialize the FastEmbed model")
            raise EmbeddingServiceError("Could not initialize the FastEmbed model") from exc

        logger.info("Initialized FastEmbed model: %s", configuration.model_name)
        return self._embeddings

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            vectors = self.get_embeddings().embed_documents(texts)
        except Exception as exc:
            logger.exception("Embedding generation failed for %d documents", len(texts))
            raise EmbeddingServiceError("Could not generate FAQ document embeddings") from exc
        if len(vectors) != len(texts):
            raise EmbeddingServiceError("Embedding provider returned an unexpected vector count")
        logger.info("Generated embeddings for %d documents", len(vectors))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Embedding query must not be empty")
        try:
            vector = self.get_embeddings().embed_query(text)
        except Exception as exc:
            logger.exception("Embedding generation failed for FAQ query")
            raise EmbeddingServiceError("Could not generate FAQ query embedding") from exc
        logger.info("Generated embedding for FAQ query")
        return vector


_embedding_service = EmbeddingService()


def get_embedding_service() -> EmbeddingService:
    """Return the shared lazy embedding service."""
    return _embedding_service
