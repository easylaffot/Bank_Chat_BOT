"""Reusable shopping cart operations for future agent integrations."""

from app.repositories.product_repository import ProductRepository
from app.services.cart_service import CartService

cart_service = CartService(ProductRepository())


def add_to_cart(product_id: str, quantity: int = 1) -> dict:
    """Add a product quantity and return the updated cart."""
    return cart_service.add_product(product_id, quantity).model_dump(mode="json")


def remove_from_cart(product_id: str) -> dict:
    """Remove a product line and return the updated cart."""
    return cart_service.remove_product(product_id).model_dump(mode="json")


def get_cart() -> dict:
    """Return the current cart and its totals."""
    return cart_service.get_cart().model_dump(mode="json")


def clear_cart() -> dict:
    """Remove all product lines and return the empty cart."""
    return cart_service.clear_cart().model_dump(mode="json")
