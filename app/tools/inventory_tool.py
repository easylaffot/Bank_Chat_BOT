"""Reusable inventory and delivery lookup."""

import logging
from typing import Any

from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductNotFoundError

logger = logging.getLogger(__name__)
product_repository = ProductRepository()


def check_inventory(product_id: str) -> dict[str, Any]:
    """Return stock and delivery details for a catalog product."""
    logger.info("Inventory check requested: product_id=%s", product_id)
    product = product_repository.get_product_by_id(product_id)
    if product is None:
        logger.warning("Inventory check requested for missing product_id=%s", product_id)
        raise ProductNotFoundError(product_id)

    if product["stock_quantity"] == 0:
        return {"in_stock": False}
    return {
        "in_stock": True,
        "stock_quantity": product["stock_quantity"],
        "delivery_days": product["delivery_days"],
    }
