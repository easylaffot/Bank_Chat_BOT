"""Reusable catalog search function for future agent integrations."""

import logging
from typing import Any

from app.repositories.product_repository import ProductRepository
from app.services.product_service import InvalidProductFilterError, ProductService

logger = logging.getLogger(__name__)
product_service = ProductService(ProductRepository())


def search_products(
    *,
    category: str | None = None,
    brand: str | None = None,
    ram_gb: int | None = None,
    budget: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, list[dict[str, Any]]]:
    """Search the SQLite catalog and return matching product records."""
    filters = {
        "category": category,
        "brand": brand,
        "ram_gb": ram_gb,
        "budget": budget,
    }
    logger.info("Product search requested: %s", filters)

    if isinstance(budget, bool) or (budget is not None and budget < 0):
        logger.warning("Invalid product search budget: %r", budget)
        raise InvalidProductFilterError("budget must be greater than or equal to 0")

    try:
        result = product_service.search_products(
            category=category,
            brand=brand,
            ram_gb=ram_gb,
            max_price=budget,
            limit=limit,
            offset=offset,
        )
    except InvalidProductFilterError:
        logger.exception("Product search rejected for filters %s", filters)
        raise

    return {"matches": result["items"]}
