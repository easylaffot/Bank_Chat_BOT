"""Rank search results with the reusable comparison tool."""

import logging
from typing import Any, Callable

from app.tools.comparison_tool import compare_products

logger = logging.getLogger(__name__)


class ComparisonAgent:
    """Compare matching products and preserve their ranking explanations."""

    def __init__(
        self,
        comparison_function: Callable[[list[str]], list[dict[str, Any]]] = compare_products,
    ) -> None:
        self.comparison_function = comparison_function

    def run(self, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Comparison agent started with %d products", len(products))
        product_ids = [product["id"] for product in products]
        if not product_ids:
            return []
        if len(product_ids) == 1:
            only_product = product_ids[0]
            return [
                {
                    "product_id": only_product,
                    "score": 100.0,
                    "rank": 1,
                    "score_breakdown": {},
                    "scoring_explanation": (
                        "Only one product matched, so a relative comparison was not possible."
                    ),
                }
            ]

        rankings = self.comparison_function(product_ids)
        logger.info("Comparison agent ranked %d products", len(rankings))
        return rankings
