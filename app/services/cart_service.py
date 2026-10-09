"""Shopping cart persistence and business rules."""

import logging
import sqlite3
from typing import Any

from app.db.database import get_connection
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartItem, CartResponse
from app.services.product_service import ProductNotFoundError

logger = logging.getLogger(__name__)
CREATE_CART_TABLE = """
CREATE TABLE IF NOT EXISTS cart (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL UNIQUE REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""
CART_ITEMS_QUERY = """
SELECT
    cart.cart_id,
    cart.product_id,
    cart.quantity,
    cart.added_at,
    products.brand,
    products.model_name,
    products.price,
    cart.quantity * products.price AS line_total
FROM cart
JOIN products ON products.id = cart.product_id
ORDER BY cart.cart_id
"""


class InvalidCartQuantityError(ValueError):
    """Raised when a cart quantity is not a positive integer."""


class ProductOutOfStockError(ValueError):
    """Raised when a product with no available stock is added to the cart."""


class InsufficientStockError(ValueError):
    """Raised when the requested cart quantity exceeds available inventory."""


class CartItemNotFoundError(LookupError):
    """Raised when removing a product that is not in the cart."""


class CartService:
    """Manage the single shopping cart while reusing the product repository."""

    def __init__(self, product_repository: ProductRepository | None = None) -> None:
        self.product_repository = product_repository or ProductRepository()

    def _ensure_cart_table(self) -> None:
        connection = get_connection()
        try:
            with connection:
                connection.execute(CREATE_CART_TABLE)
        except sqlite3.Error:
            logger.exception("Could not create or verify shopping cart table")
            raise
        finally:
            connection.close()

    def add_product(self, product_id: str, quantity: int = 1) -> CartResponse:
        if type(quantity) is not int or quantity <= 0:
            logger.warning("Invalid cart quantity for product_id=%s: %r", product_id, quantity)
            raise InvalidCartQuantityError("quantity must be a positive integer")

        product = self.product_repository.get_product_by_id(product_id)
        if product is None:
            logger.warning("Cannot add missing product to cart: product_id=%s", product_id)
            raise ProductNotFoundError(product_id)
        if product["stock_quantity"] <= 0:
            logger.warning("Cannot add out-of-stock product to cart: product_id=%s", product_id)
            raise ProductOutOfStockError(f"Product {product_id} is out of stock")

        self._ensure_cart_table()
        connection = get_connection()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT quantity FROM cart WHERE product_id = ?", (product_id,)
            ).fetchone()
            current_quantity = existing["quantity"] if existing else 0
            requested_total = current_quantity + quantity
            if requested_total > product["stock_quantity"]:
                raise InsufficientStockError(
                    f"Requested quantity {requested_total} exceeds available stock "
                    f"({product['stock_quantity']}) for product {product_id}"
                )

            if existing:
                connection.execute(
                    "UPDATE cart SET quantity = ? WHERE product_id = ?",
                    (requested_total, product_id),
                )
            else:
                connection.execute(
                    "INSERT INTO cart (product_id, quantity) VALUES (?, ?)",
                    (product_id, quantity),
                )
            connection.commit()
        except InsufficientStockError:
            connection.rollback()
            logger.warning("Cart add exceeds stock: product_id=%s", product_id)
            raise
        except sqlite3.Error:
            connection.rollback()
            logger.exception("Could not add product to cart: product_id=%s", product_id)
            raise
        finally:
            connection.close()

        logger.info("Added product to cart: product_id=%s quantity=%d", product_id, quantity)
        return self.get_cart()

    def remove_product(self, product_id: str) -> CartResponse:
        self._ensure_cart_table()
        connection = get_connection()
        try:
            with connection:
                cursor = connection.execute(
                    "DELETE FROM cart WHERE product_id = ?", (product_id,)
                )
                if cursor.rowcount == 0:
                    raise CartItemNotFoundError(f"Product {product_id} is not in the cart")
        except CartItemNotFoundError:
            logger.warning("Cannot remove product not in cart: product_id=%s", product_id)
            raise
        except sqlite3.Error:
            logger.exception("Could not remove product from cart: product_id=%s", product_id)
            raise
        finally:
            connection.close()

        logger.info("Removed product from cart: product_id=%s", product_id)
        return self.get_cart()

    def get_cart(self) -> CartResponse:
        self._ensure_cart_table()
        connection = get_connection()
        try:
            rows = connection.execute(CART_ITEMS_QUERY).fetchall()
        except sqlite3.Error:
            logger.exception("Could not read shopping cart")
            raise
        finally:
            connection.close()

        items = [CartItem.model_validate(dict(row)) for row in rows]
        cart = CartResponse(
            total_items=sum(item.quantity for item in items),
            total_price=sum(item.line_total for item in items),
            items=items,
        )
        logger.info("Retrieved shopping cart: item_count=%d", cart.total_items)
        return cart

    def clear_cart(self) -> CartResponse:
        self._ensure_cart_table()
        connection = get_connection()
        try:
            with connection:
                deleted_count = connection.execute("DELETE FROM cart").rowcount
        except sqlite3.Error:
            logger.exception("Could not clear shopping cart")
            raise
        finally:
            connection.close()

        logger.info("Cleared shopping cart: removed_lines=%d", deleted_count)
        return self.get_cart()
