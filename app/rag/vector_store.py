"""Persistent ChromaDB storage for FAQ document chunks."""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import chromadb
from langchain_core.documents import Document

from app.core.config import PROJECT_ROOT, get_settings
from app.services.embedding_service import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)
FAQ_COLLECTION_DEFAULT = "faq_knowledge_base_fastembed_bge_small_en_v1_5"


class VectorStoreError(RuntimeError):
    """Raised when FAQ vectors cannot be stored or accessed."""


def _faq_collection_name() -> str:
    name = os.getenv("CHROMA_FAQ_COLLECTION_NAME", FAQ_COLLECTION_DEFAULT).strip()
    if not name:
        raise VectorStoreError("CHROMA_FAQ_COLLECTION_NAME must not be empty")
    return name


@lru_cache(maxsize=1)
def get_faq_collection() -> Any:
    """Get or create the persistent FAQ collection without using the product collection."""
    settings = get_settings()
    persist_directory = Path(settings.chroma_persist_directory).expanduser()
    if not persist_directory.is_absolute():
        persist_directory = PROJECT_ROOT / persist_directory

    try:
        client = chromadb.PersistentClient(path=str(persist_directory.resolve()))
        collection = client.get_or_create_collection(
            name=_faq_collection_name(),
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as exc:
        logger.exception("Could not open persistent FAQ collection")
        raise VectorStoreError("Could not open persistent FAQ collection") from exc

    logger.info("Connected to FAQ ChromaDB collection at %s", persist_directory)
    return collection


def store_faq_documents(
    documents: list[Document],
    embedding_service: EmbeddingService | None = None,
) -> int:
    """Embed and upsert chunks, then remove stale chunks from replaced source files."""
    if not documents:
        raise VectorStoreError("No FAQ chunks were provided for ingestion")

    embedder = embedding_service or get_embedding_service()
    contents = [document.page_content for document in documents]
    if any(not content.strip() for content in contents):
        raise VectorStoreError("FAQ chunks must not be empty")

    embeddings = embedder.embed_documents(contents)
    ids: list[str] = []
    metadatas: list[dict[str, str | int]] = []
    for document in documents:
        source = str(document.metadata.get("source", "unknown"))
        chunk_index = int(document.metadata.get("chunk_index", 0))
        ids.append(f"{source}::chunk-{chunk_index}")
        metadatas.append({"source": source, "chunk_index": chunk_index})

    collection = get_faq_collection()
    try:
        collection.upsert(
            ids=ids,
            documents=contents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        source_ids: dict[str, set[str]] = {}
        for source, identifier in zip(
            (metadata["source"] for metadata in metadatas), ids, strict=True
        ):
            source_ids.setdefault(source, set()).add(identifier)
        for source, current_ids in source_ids.items():
            existing = collection.get(where={"source": source}, include=[])
            stale_ids = set(existing["ids"]) - current_ids
            if stale_ids:
                collection.delete(ids=sorted(stale_ids))
    except Exception as exc:
        logger.exception("Could not store FAQ chunks in ChromaDB")
        raise VectorStoreError("Could not store FAQ chunks in ChromaDB") from exc

    logger.info("Stored %d FAQ chunks in ChromaDB", len(ids))
    return len(ids)
