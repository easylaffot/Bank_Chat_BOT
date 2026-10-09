"""Answer FAQ questions with retrieved, source-attributed context."""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from app.rag.retriever import FAQRetriever
from app.schemas.faq import FAQAnswer
from app.services.llm_service import LLMConfigurationError, get_llm_service

logger = logging.getLogger(__name__)


class FAQAnswerError(RuntimeError):
    """Raised when the LLM cannot produce a grounded FAQ answer."""


class FAQAgent:
    """Retrieve FAQ evidence and ask the configured Ollama model to answer from it."""

    def __init__(self, retriever: FAQRetriever | None = None, llm_service=None) -> None:
        self.retriever = retriever or FAQRetriever()
        self.llm_service = llm_service or get_llm_service()

    def answer(self, question: str, top_k: int = 4) -> FAQAnswer:
        if not question.strip():
            raise ValueError("FAQ question must not be empty")
        logger.info("FAQ question received")
        documents = self.retriever.retrieve(question, top_k=top_k)
        if not documents:
            raise FAQAnswerError("No relevant FAQ documents were found")

        context = "\n\n".join(
            f"Source: {document.metadata.get('source', 'unknown')}\n{document.page_content}"
            for document in documents
        )
        prompt = [
            SystemMessage(
                content=(
                    "Answer the customer's question using only the supplied FAQ context. "
                    "If the context does not contain the answer, say that the information "
                    "is not available in the FAQ. Do not invent or infer policy details. "
                    "Keep the answer concise and do not fabricate source names."
                )
            ),
            HumanMessage(content=f"FAQ context:\n{context}\n\nCustomer question: {question.strip()}"),
        ]

        try:
            result = self.llm_service.get_chat_model().invoke(prompt)
            content = result.content if hasattr(result, "content") else result
            if isinstance(content, list):
                content = "\n".join(
                    str(block.get("text", ""))
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            if not isinstance(content, str) or not content.strip():
                raise ValueError("LLM returned an empty FAQ answer")

            sources = list(
                dict.fromkeys(
                    str(document.metadata.get("source", "unknown"))
                    for document in documents
                )
            )
            answer = FAQAnswer(answer=content.strip(), sources=sources)
        except (LLMConfigurationError, ValidationError, ValueError) as exc:
            logger.exception("FAQ answer generation failed")
            raise FAQAnswerError("Could not generate a grounded FAQ answer") from exc
        except Exception as exc:
            logger.exception("Ollama FAQ response failed")
            raise FAQAnswerError("Could not generate a grounded FAQ answer") from exc

        logger.info("FAQ answer generated using %d source documents", len(answer.sources))
        return answer


def answer_faq_question(question: str, top_k: int = 4) -> dict[str, object]:
    """Convenience function returning the FAQ agent response as a dictionary."""
    return FAQAgent().answer(question, top_k=top_k).model_dump()
