"""Load FAQ text documents from the project's FAQ knowledge directory."""

import logging
from pathlib import Path

from langchain_core.documents import Document

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FAQ_DIRECTORY = PROJECT_ROOT / "data" / "faq"


class FAQDocumentLoadError(RuntimeError):
    """Raised when the FAQ source directory is missing or has no usable documents."""


def load_faq_documents(directory: Path = FAQ_DIRECTORY) -> list[Document]:
    """Load each non-empty UTF-8 .txt file as a LangChain document."""
    if not directory.exists() or not directory.is_dir():
        logger.error("FAQ document directory is missing: %s", directory)
        raise FAQDocumentLoadError(f"FAQ document directory does not exist: {directory}")

    paths = sorted(directory.glob("*.txt"))
    if not paths:
        logger.error("No FAQ .txt files found in %s", directory)
        raise FAQDocumentLoadError(f"No FAQ .txt files found in {directory}")

    documents: list[Document] = []
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError) as exc:
            logger.exception("Could not load FAQ document: %s", path)
            raise FAQDocumentLoadError(f"Could not load FAQ document: {path.name}") from exc
        if not content:
            logger.warning("Skipping empty FAQ document: %s", path.name)
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(path.relative_to(PROJECT_ROOT)),
                    "filename": path.name,
                },
            )
        )
        logger.info("Loaded FAQ document: %s", path.name)

    if not documents:
        raise FAQDocumentLoadError(f"FAQ documents contain no usable text: {directory}")
    logger.info("Loaded %d FAQ documents", len(documents))
    return documents
