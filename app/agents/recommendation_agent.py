"""Select and explain a recommendation using prior agent results."""

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.graph.state import ShoppingState
from app.services.llm_service import LLMService, get_llm_service

logger = logging.getLogger(__name__)


class RecommendationDraft(BaseModel):
    selected_product_id: str
    reason: str
    alternative_product_ids: list[str] = Field(default_factory=list)


class RecommendationAgent:
    """Choose only an in-stock, affordable result and explain the decision."""

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or get_llm_service()

    def run(self, state: ShoppingState) -> dict[str, Any]:
        search_results = state.get("search_results", {})
        products = search_results.get("matches", [])
        if not products:
            error = state.get("error")
            reason = error["message"] if error else "No products matched the request."
            return {"recommended_product": None, "reason": reason, "alternatives": []}

        comparisons = {
            result["product_id"]: result
            for result in state.get("comparison_results", [])
        }
        inventory = state.get("inventory_results", {})
        budget_state = state.get("budget_results", {})
        requested_budget = search_results.get("intent", {}).get("budget")

        eligible: list[dict[str, Any]] = []
        in_stock_count = 0
        for product in products:
            product_id = product["id"]
            stock_result = inventory.get(product_id)
            if stock_result is None:
                continue
            if not stock_result.get("in_stock", False):
                continue
            in_stock_count += 1

            affordability = None
            if requested_budget is not None:
                affordability = budget_state.get("results", {}).get(product_id)
                if affordability is None or not affordability.get("within_budget", False):
                    continue

            comparison = comparisons.get(product_id, {})
            eligible.append(
                {
                    **product,
                    "comparison_score": comparison.get("score"),
                    "comparison_rank": comparison.get("rank"),
                    "inventory": stock_result,
                    "budget_check": affordability,
                }
            )

        if not eligible:
            if in_stock_count == 0:
                reason = "No matching products are currently in stock."
            elif requested_budget is not None:
                reason = "No in-stock product fits the requested budget."
            else:
                reason = "Product availability could not be confirmed."
            return {"recommended_product": None, "reason": reason, "alternatives": []}

        eligible.sort(
            key=lambda product: (
                product["comparison_rank"] is None,
                product["comparison_rank"] or float("inf"),
                product["id"],
            )
        )
        eligible_by_id = {product["id"]: product for product in eligible}
        fallback = eligible[0]
        fallback_reason = (
            "Selected the highest-ranked product that is in stock"
            + (" and within your budget." if requested_budget is not None else ".")
        )

        try:
            model = self.llm_service.get_chat_model().with_structured_output(RecommendationDraft)
            draft_result = model.invoke(
                [
                    SystemMessage(
                        content=(
                            "Choose the best product for the customer's request from the supplied "
                            "eligible products only. Use comparison rank, price, preferences, "
                            "inventory, delivery, and budget results. Do not invent specifications. "
                            "Return the selected product ID, a concise evidence-based reason, and "
                            "alternative IDs from the eligible list."
                        )
                    ),
                    HumanMessage(
                        content=(
                            f"Customer request: {state.get('user_query', '')}\n"
                            "Eligible products and prior agent results:\n"
                            f"{json.dumps(eligible, ensure_ascii=True)}"
                        )
                    ),
                ]
            )
            draft = (
                draft_result
                if isinstance(draft_result, RecommendationDraft)
                else RecommendationDraft.model_validate(draft_result)
            )
            chosen = eligible_by_id.get(draft.selected_product_id)
            if chosen is None:
                logger.warning(
                    "Recommendation model selected an ineligible product_id=%s",
                    draft.selected_product_id,
                )
                chosen = fallback
                reason = fallback_reason
                alternative_ids = []
            else:
                reason = draft.reason.strip() or fallback_reason
                alternative_ids = list(
                    dict.fromkeys(
                        product_id
                        for product_id in draft.alternative_product_ids
                        if product_id in eligible_by_id and product_id != chosen["id"]
                    )
                )
        except Exception:
            logger.exception("Recommendation model failed; using comparison ranking")
            chosen = fallback
            reason = fallback_reason
            alternative_ids = []

        alternative_ids.extend(
            product["id"]
            for product in eligible
            if product["id"] != chosen["id"] and product["id"] not in alternative_ids
        )
        recommendation = {
            "recommended_product": chosen,
            "reason": reason,
            "alternatives": [eligible_by_id[product_id] for product_id in alternative_ids],
        }
        logger.info("Recommendation agent selected product_id=%s", chosen["id"])
        return recommendation
