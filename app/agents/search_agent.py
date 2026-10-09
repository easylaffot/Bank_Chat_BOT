"""Interpret a shopping query and find matching catalog products."""

import logging
from typing import Any, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.services.llm_service import LLMService, get_llm_service
from app.tools.search_tool import search_products

logger = logging.getLogger(__name__)


class InvalidCustomerQueryError(ValueError):
    """Raised when a customer query is empty or has no usable preferences."""


class NoProductsFoundError(LookupError):
    """Raised when no catalog products match an interpreted customer query."""

    def __init__(self, message: str, intent: "SearchIntent") -> None:
        super().__init__(message)
        self.intent = intent


class SearchIntent(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    budget: int | None = Field(default=None, ge=0)
    category: str | None = None
    ram_gb: int | None = Field(
        default=None,
        gt=0,
        validation_alias=AliasChoices("ram_gb", "RAM"),
    )
    brand: str | None = None

    @model_validator(mode="after")
    def require_a_preference(self) -> "SearchIntent":
        if all(value is None for value in (self.budget, self.category, self.ram_gb, self.brand)):
            raise ValueError("At least one product preference must be identified")
        return self


def _normalize_category(category: str | None) -> str | None:
    if category is None:
        return None

    normalized = category.strip().casefold()
    canonical_categories = {
        "Student": ("student", "school", "college", "university", "study", "education"),
        "Programming": (
            "programming",
            "programmer",
            "coding",
            "developer",
            "software",
            "python",
            "machine learning",
            "data science",
        ),
        "Business": ("business", "office", "professional", "enterprise"),
        "Gaming": ("gaming", "gamer", "games", "game", "esports"),
        "Ultrabook": ("ultrabook", "ultra book", "lightweight", "portable", "travel"),
    }

    for canonical, keywords in canonical_categories.items():
        if normalized == canonical.casefold() or any(keyword in normalized for keyword in keywords):
            return canonical
    return None


class SearchAgent:
    """Use an LLM to extract preferences, then call the reusable search tool."""

    def __init__(
        self,
        llm_service: LLMService | None = None,
        search_function: Callable[..., dict[str, list[dict[str, Any]]]] = search_products,
    ) -> None:
        self.llm_service = llm_service or get_llm_service()
        self.search_function = search_function

    def run(self, user_query: str) -> dict[str, Any]:
        logger.info("Search agent started")
        if not isinstance(user_query, str) or not user_query.strip():
            raise InvalidCustomerQueryError("Please describe the laptop you are looking for")

        structured_model = self.llm_service.get_chat_model().with_structured_output(SearchIntent)
        try:
            intent_result = structured_model.invoke(
                [
                    SystemMessage(
                        content=(
                            "Extract only explicit or strongly implied laptop preferences from "
                            "the customer request. Return budget in INR, category, RAM in GB, "
                            "and brand where present. Use null for unspecified fields. If no "
                            "usable laptop preference exists, return all fields as null."
                        )
                    ),
                    HumanMessage(content=user_query.strip()),
                ]
            )
            intent = (
                intent_result
                if isinstance(intent_result, SearchIntent)
                else SearchIntent.model_validate(intent_result)
            )
        except (ValidationError, ValueError, TypeError) as exc:
            logger.exception("Search agent could not parse extracted preferences")
            raise InvalidCustomerQueryError(
                "Could not identify a usable laptop preference from the query"
            ) from exc

        intent = intent.model_copy(update={"category": _normalize_category(intent.category)})
        if all(value is None for value in (intent.budget, intent.category, intent.ram_gb, intent.brand)):
            raise InvalidCustomerQueryError(
                "Could not identify a supported laptop preference from the query"
            )

        logger.info(
            "Search agent extracted values: budget=%r category=%r ram_gb=%r brand=%r",
            intent.budget,
            intent.category,
            intent.ram_gb,
            intent.brand,
        )
        search_result = self.search_function(
            budget=intent.budget,
            category=intent.category,
            ram_gb=intent.ram_gb,
            brand=intent.brand,
        )
        matches = search_result["matches"]
        if not matches:
            if intent.budget is not None:
                message = "No products matched the requested preferences within budget"
            else:
                message = "No products matched the requested preferences"
            logger.info("Search agent found no products")
            raise NoProductsFoundError(message, intent)

        logger.info("Search agent found %d products", len(matches))
        return {"intent": intent.model_dump(), "matches": matches}
