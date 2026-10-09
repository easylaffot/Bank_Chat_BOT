"""Reusable product price and customer budget validation."""

import logging
import math
from numbers import Real
from typing import Any

from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductNotFoundError

logger = logging.getLogger(__name__)
product_repository = ProductRepository()


class InvalidBudgetError(ValueError):
    """Raised when a budget is negative, non-numeric, or non-finite."""


def check_budget(product_id: str, budget: Real) -> dict[str, Any]:
    """Compare a catalog product's price against a non-negative budget."""
    logger.info("Budget validation requested: product_id=%s budget=%r", product_id, budget)
    if isinstance(budget, bool) or not isinstance(budget, Real) or not math.isfinite(budget) or budget < 0:
        logger.warning("Invalid budget value: %r", budget)
        raise InvalidBudgetError("budget must be a finite number greater than or equal to 0")

    product = product_repository.get_product_by_id(product_id)
    if product is None:
        logger.warning("Budget check requested for missing product_id=%s", product_id)
        raise ProductNotFoundError(product_id)

    remaining_budget = budget - product["price"]
    result = {
        "product_id": product_id,
        "price": product["price"],
        "budget": budget,
        "within_budget": remaining_budget >= 0,
        "remaining_budget": remaining_budget,
    }
    logger.info("Budget validation result: %s", result)
    return result
