"""Validate candidate product prices against the customer's budget."""

import logging
from typing import Any, Callable

from app.tools.budget_tool import check_budget

logger = logging.getLogger(__name__)


class BudgetAgent:
    """Apply the budget tool to candidates when a budget was provided."""

    def __init__(
        self,
        budget_function: Callable[[str, int], dict[str, Any]] = check_budget,
    ) -> None:
        self.budget_function = budget_function

    def run(
        self,
        products: list[dict[str, Any]],
        intent: dict[str, Any],
    ) -> dict[str, Any]:
        budget = intent.get("budget")
        logger.info("Budget agent started; budget provided=%s", budget is not None)
        if budget is None:
            return {"budget": None, "results": {}}

        results = {
            product["id"]: self.budget_function(product["id"], budget)
            for product in products
        }
        logger.info("Budget agent validated %d products", len(results))
        return {"budget": budget, "results": results}
