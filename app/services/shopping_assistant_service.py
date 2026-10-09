"""Run and normalize the LangGraph shopping assistant workflow."""

import logging
from collections.abc import Callable
from typing import Any

from fastapi.encoders import jsonable_encoder

from app.graph.shopping_graph import run_shopping_workflow
from app.schemas.shopping_assistant import ShoppingAssistantResponse

logger = logging.getLogger(__name__)


class ShoppingAssistantService:
    """Coordinate the graph and return a stable JSON-safe response contract."""

    def __init__(
        self,
        workflow_runner: Callable[[str], dict[str, Any]] = run_shopping_workflow,
    ) -> None:
        self.workflow_runner = workflow_runner

    def execute(self, query: str) -> dict[str, Any]:
        normalized_query = query.strip()
        if not normalized_query:
            return ShoppingAssistantResponse(
                error={
                    "code": "invalid_query",
                    "message": "Please describe the laptop you are looking for.",
                }
            ).model_dump(mode="json")

        logger.info("Shopping assistant request received")
        try:
            state = self.workflow_runner(normalized_query)
        except Exception:
            logger.exception("Shopping assistant workflow execution failed")
            return ShoppingAssistantResponse(
                error=ShoppingAssistantErrorData(
                    code="workflow_error",
                    message="The shopping request could not be completed.",
                )
            ).model_dump(mode="json")

        recommendation_state = state.get("recommendation") or {}
        error = state.get("error")
        recommendation = recommendation_state.get("recommended_product")
        alternatives = recommendation_state.get("alternatives") or []

        if error is None and recommendation is None:
            error = {
                "code": "no_recommendation",
                "message": recommendation_state.get(
                    "reason", "No suitable products could be recommended."
                ),
            }

        response = ShoppingAssistantResponse(
            recommendation=recommendation,
            alternatives=alternatives,
            error=error,
        )
        logger.info(
            "Shopping assistant workflow response ready; recommended=%s alternatives=%d",
            recommendation is not None,
            len(alternatives),
        )
        return jsonable_encoder(response)
