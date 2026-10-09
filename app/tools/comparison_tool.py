"""Explainable product comparison and ranking."""

import logging
from typing import Any

from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductNotFoundError

logger = logging.getLogger(__name__)
product_repository = ProductRepository()
WEIGHTS = {
    "price": 25,
    "ram_gb": 20,
    "processor": 20,
    "storage_gb": 15,
    "battery_hours": 10,
    "rating": 10,
}


class InvalidComparisonError(ValueError):
    """Raised when the comparison does not contain distinct valid product IDs."""


def _processor_tier(processor: str) -> int:
    normalized = processor.casefold()
    if "i7" in normalized or "ryzen 7" in normalized:
        return 3
    if "i5" in normalized or "ryzen 5" in normalized:
        return 2
    if "i3" in normalized or "ryzen 3" in normalized:
        return 1
    return 0


def _normalized_scores(values: list[float], *, lower_is_better: bool = False) -> list[float]:
    best = min(values) if lower_is_better else max(values)
    worst = max(values) if lower_is_better else min(values)
    if best == worst:
        return [100.0] * len(values)

    if lower_is_better:
        return [100.0 if value == 0 else best / value * 100 for value in values]
    return [value / best * 100 if best > 0 else 100.0 for value in values]


def compare_products(product_ids: list[str]) -> list[dict[str, Any]]:
    """Rank at least two products using weighted, normalized catalog attributes.

    The weights are price 25%, RAM 20%, processor tier 20%, storage 15%,
    battery life 10%, and rating 10%. Lower price scores better; the other
    attributes score higher when their values are higher.
    """
    if len(product_ids) < 2:
        raise InvalidComparisonError("At least two product IDs are required")
    if len(set(product_ids)) != len(product_ids):
        raise InvalidComparisonError("Product IDs must be unique")

    logger.info("Comparing products: %s", product_ids)
    products = []
    for product_id in product_ids:
        product = product_repository.get_product_by_id(product_id)
        if product is None:
            logger.warning("Cannot compare missing product id=%s", product_id)
            raise ProductNotFoundError(product_id)
        products.append(product)

    metric_values = {
        "price": [float(product["price"]) for product in products],
        "ram_gb": [float(product["ram_gb"]) for product in products],
        "processor": [float(_processor_tier(product["processor"])) for product in products],
        "storage_gb": [float(product["storage_gb"]) for product in products],
        "battery_hours": [float(product["battery_hours"]) for product in products],
        "rating": [float(product["rating"]) for product in products],
    }
    normalized = {
        metric: _normalized_scores(values, lower_is_better=(metric == "price"))
        for metric, values in metric_values.items()
    }

    rankings = []
    for index, product in enumerate(products):
        breakdown = {
            metric: {
                "normalized_score": round(normalized[metric][index], 2),
                "weight_percent": weight,
                "weighted_points": round(normalized[metric][index] * weight / 100, 2),
            }
            for metric, weight in WEIGHTS.items()
        }
        score = round(sum(item["weighted_points"] for item in breakdown.values()), 2)
        rankings.append(
            {
                "product_id": product["id"],
                "score": score,
                "score_breakdown": breakdown,
                "scoring_explanation": (
                    "Each attribute is normalized against the products being compared; "
                    "the normalized scores are combined using the listed percentage weights. "
                    "Processor tiers are i3/Ryzen 3=1, i5/Ryzen 5=2, and i7/Ryzen 7=3."
                ),
            }
        )

    rankings.sort(key=lambda item: (-item["score"], item["product_id"]))
    for rank, result in enumerate(rankings, start=1):
        result["rank"] = rank
    logger.info("Product comparison completed: %s", rankings)
    return rankings
