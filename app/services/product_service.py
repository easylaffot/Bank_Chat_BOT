"""Product catalog use cases and input validation."""

import logging
from typing import Any

from app.repositories.product_repository import ProductRepository

logger = logging.getLogger(__name__)


class InvalidProductFilterError(ValueError):
    """Raised when a product query contains invalid filters or pagination."""


class ProductNotFoundError(LookupError):
    """Raised when a requested product does not exist."""


class ProductService:
    """Validate product queries and coordinate product repository calls."""

    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None:
        if not 1 <= limit <= 100:
            raise InvalidProductFilterError("limit must be between 1 and 100")
        if offset < 0:
            raise InvalidProductFilterError("offset must be greater than or equal to 0")

    def list_products(self, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        self._validate_pagination(limit, offset)
        total, items = self.repository.list_products(limit=limit, offset=offset)
        return {"total": total, "count": len(items), "items": items}

    def search_products(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        brand: str | None = None,
        category: str | None = None,
        ram_gb: int | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
    ) -> dict[str, Any]:
        self._validate_pagination(limit, offset)

        normalized_brand = self._normalize_text_filter("brand", brand)
        normalized_category = self._normalize_text_filter("category", category)
        if ram_gb is not None and ram_gb <= 0:
            raise InvalidProductFilterError("ram_gb must be greater than 0")
        if min_price is not None and min_price < 0:
            raise InvalidProductFilterError("min_price must be greater than or equal to 0")
        if max_price is not None and max_price < 0:
            raise InvalidProductFilterError("max_price must be greater than or equal to 0")
        if min_price is not None and max_price is not None and max_price < min_price:
            raise InvalidProductFilterError("max_price must be greater than or equal to min_price")

        total, items = self.repository.list_products(
            limit=limit,
            offset=offset,
            brand=normalized_brand,
            category=normalized_category,
            ram_gb=ram_gb,
            min_price=min_price,
            max_price=max_price,
        )
        return {"total": total, "count": len(items), "items": items}

    def get_product(self, product_id: str) -> dict[str, Any]:
        product = self.repository.get_product_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return product

    @staticmethod
    def _normalize_text_filter(name: str, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        if not normalized_value:
            raise InvalidProductFilterError(f"{name} must not be empty")
        return normalized_value
