"""HTTP endpoint for grounded FAQ answers."""

import logging

from fastapi import APIRouter, HTTPException

from app.rag.faq_agent import FAQAgent, FAQAnswerError
from app.rag.retriever import FAQRetrievalError
from app.schemas.faq import FAQAnswer, FAQQuestion
from app.services.llm_service import LLMConfigurationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/faq", tags=["FAQ"])
_faq_agent = FAQAgent()


@router.post("", response_model=FAQAnswer)
def answer_faq(request: FAQQuestion) -> FAQAnswer:
    logger.info("FAQ endpoint called")
    try:
        return _faq_agent.answer(request.question)
    except (FAQAnswerError, FAQRetrievalError, LLMConfigurationError) as exc:
        logger.exception("FAQ endpoint could not answer the question")
        raise HTTPException(
            status_code=503,
            detail="The FAQ service is temporarily unavailable.",
        ) from exc
