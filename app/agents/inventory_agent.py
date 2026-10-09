"""Collect stock and delivery details for search results."""

import logging
from typing import Any, Callable

from app.tools.inventory_tool import check_inventory

logger = logging.getLogger(__name__)


class InventoryAgent:
    """Check inventory for each matching product using the inventory tool."""

    def __init__(
        self,
        inventory_function: Callable[[str], dict[str, Any]] = check_inventory,
    ) -> None:
        self.inventory_function = inventory_function

    def run(self, products: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        logger.info("Inventory agent started with %d products", len(products))
        results = {
            product["id"]: self.inventory_function(product["id"])
            for product in products
        }
        logger.info("Inventory agent checked %d products", len(results))
        return results
