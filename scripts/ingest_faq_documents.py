"""Chunk FAQ files, embed them, and upsert them into persistent ChromaDB."""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.document_loader import FAQDocumentLoadError, load_faq_documents
from app.rag.vector_store import VectorStoreError, store_faq_documents
from app.services.embedding_service import EmbeddingServiceError
from app.services.llm_service import LLMConfigurationError

logger = logging.getLogger(__name__)


def ingest_faq_documents() -> int:
    """Load, split, embed, and store all current FAQ documents."""
    documents = load_faq_documents()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        add_start_index=True,
    )
    chunks = []
    for document in documents:
        document_chunks = splitter.split_documents([document])
        for chunk_index, chunk in enumerate(document_chunks):
            chunk.metadata["chunk_index"] = chunk_index
            chunks.append(chunk)

    if not chunks:
        raise FAQDocumentLoadError("FAQ documents produced no text chunks")

    logger.info("Created %d chunks from %d FAQ documents", len(chunks), len(documents))
    return store_faq_documents(chunks)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        chunk_count = ingest_faq_documents()
    except (FAQDocumentLoadError, EmbeddingServiceError, LLMConfigurationError, VectorStoreError):
        logger.exception("FAQ document ingestion failed")
        return 1
    except Exception:
        logger.exception("Unexpected FAQ document ingestion failure")
        return 1

    logger.info("FAQ ingestion complete: %d chunks stored", chunk_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
