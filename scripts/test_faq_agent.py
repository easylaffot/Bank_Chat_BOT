"""Ask sample FAQ questions and print grounded answers with their sources."""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.faq_agent import FAQAgent, FAQAnswerError
from app.rag.retriever import FAQRetrievalError
from app.services.llm_service import LLMConfigurationError

logger = logging.getLogger(__name__)
QUESTIONS = (
    "What warranty is available?",
    "How long do refunds take?",
    "What payment methods are accepted?",
)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    agent = FAQAgent()
    failed = False

    for question in QUESTIONS:
        print(f"\nQuestion: {question}")
        try:
            result = agent.answer(question)
        except (FAQAnswerError, FAQRetrievalError, LLMConfigurationError, ValueError):
            logger.exception("Could not answer FAQ question")
            print("Answer: Unable to answer from the FAQ knowledge base.")
            print("Sources: []")
            failed = True
            continue

        print(f"Answer: {result.answer}")
        print(f"Sources: {result.sources}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
