"""Retrieve the most relevant FAQ chunks from ChromaDB."""

import logging
from typing import Any

from langchain_core.documents import Document

from app.rag.vector_store import VectorStoreError, get_faq_collection
from app.services.embedding_service import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)


class FAQRetrievalError(RuntimeError):
    """Raised when FAQ retrieval cannot complete."""


class EmptyFAQCollectionError(FAQRetrievalError):
    """Raised when no FAQ documents have been ingested."""


class FAQRetriever:
    """Embed a question and return the nearest FAQ chunks with source metadata."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        collection: Any = None,
    ) -> None:
        self.embedding_service = embedding_service or get_embedding_service()
        self._collection = collection

    @property
    def collection(self) -> Any:
        if self._collection is None:
            self._collection = get_faq_collection()
        return self._collection

    def retrieve(self, question: str, top_k: int = 4) -> list[Document]:
        if not question.strip():
            raise ValueError("FAQ question must not be empty")
        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20")

        try:
            count = self.collection.count()
        except Exception as exc:
            logger.exception("Could not inspect FAQ collection")
            raise FAQRetrievalError("Could not inspect FAQ collection") from exc
        if count == 0:
            logger.warning("FAQ retrieval requested while the collection is empty")
            raise EmptyFAQCollectionError(
                "FAQ knowledge base is empty; run scripts/ingest_faq_documents.py first"
            )

        query_embedding = self.embedding_service.embed_query(question)
        try:
            result = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, count),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.exception("FAQ vector retrieval failed")
            raise FAQRetrievalError("Could not retrieve relevant FAQ documents") from exc

        ids = result.get("ids", [[]])[0]
        texts = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        documents = [
            Document(
                page_content=text,
                metadata={**metadata, "distance": distance},
            )
            for text, metadata, distance in zip(texts, metadatas, distances, strict=False)
            if text
        ]
        if not ids or not documents:
            logger.warning("FAQ retrieval returned no matching chunks")
            return []

        logger.info(
            "Retrieved %d FAQ chunks for question; sources=%s",
            len(documents),
            sorted({str(document.metadata.get("source", "unknown")) for document in documents}),
        )
        return documents
