"""SQLite queries for the product catalog."""

import logging
import sqlite3
from typing import Any

from app.db.database import get_connection

logger = logging.getLogger(__name__)
PRODUCT_COLUMNS = (
    "id",
    "brand",
    "model_name",
    "category",
    "price",
    "ram_gb",
    "processor",
    "storage_gb",
    "battery_hours",
    "stock_quantity",
    "delivery_days",
    "rating",
)


class ProductRepository:
    """Read product records from SQLite without applying business rules."""

    def list_products(
        self,
        limit: int,
        offset: int,
        *,
        brand: str | None = None,
        category: str | None = None,
        ram_gb: int | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
    ) -> tuple[int, list[dict[str, Any]]]:
        clauses: list[str] = []
        parameters: list[str | int] = []

        if brand is not None:
            clauses.append("brand = ?")
            parameters.append(brand)
        if category is not None:
            clauses.append("category = ?")
            parameters.append(category)
        if ram_gb is not None:
            clauses.append("ram_gb = ?")
            parameters.append(ram_gb)
        if min_price is not None:
            clauses.append("price >= ?")
            parameters.append(min_price)
        if max_price is not None:
            clauses.append("price <= ?")
            parameters.append(max_price)

        where_clause = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        selected_columns = ", ".join(PRODUCT_COLUMNS)
        connection = get_connection()
        try:
            total = connection.execute(
                f"SELECT COUNT(*) FROM products{where_clause}", parameters
            ).fetchone()[0]
            rows = connection.execute(
                f"SELECT {selected_columns} FROM products{where_clause} "
                "ORDER BY id LIMIT ? OFFSET ?",
                [*parameters, limit, offset],
            ).fetchall()
            return total, [dict(row) for row in rows]
        except sqlite3.Error:
            logger.exception("Product list query failed")
            raise
        finally:
            connection.close()

    def get_product_by_id(self, product_id: str) -> dict[str, Any] | None:
        selected_columns = ", ".join(PRODUCT_COLUMNS)
        connection = get_connection()
        try:
            row = connection.execute(
                f"SELECT {selected_columns} FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()
            return dict(row) if row is not None else None
        except sqlite3.Error:
            logger.exception("Product lookup query failed for id=%s", product_id)
            raise
        finally:
            connection.close()
