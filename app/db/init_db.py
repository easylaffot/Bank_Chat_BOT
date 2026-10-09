"""Load the product catalog CSV into the local SQLite database."""

import logging
import math
import sqlite3
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, "") and str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.database import DatabaseConnectionError, get_connection

logger = logging.getLogger(__name__)
CATALOG_PATH = PROJECT_ROOT / "data" / "product_catalog.csv"
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
TEXT_COLUMNS = ("id", "brand", "model_name", "category", "processor")
INTEGER_COLUMNS = ("price", "ram_gb", "storage_gb", "stock_quantity", "delivery_days")
REAL_COLUMNS = ("battery_hours", "rating")

CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY NOT NULL,
    brand TEXT NOT NULL,
    model_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    ram_gb INTEGER NOT NULL CHECK (ram_gb > 0),
    processor TEXT NOT NULL,
    storage_gb INTEGER NOT NULL CHECK (storage_gb > 0),
    battery_hours REAL NOT NULL CHECK (battery_hours > 0),
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    delivery_days INTEGER NOT NULL CHECK (delivery_days >= 0),
    rating REAL NOT NULL CHECK (rating >= 0 AND rating <= 5)
)
"""
INSERT_PRODUCT = """
INSERT INTO products (
    id, brand, model_name, category, price, ram_gb, processor,
    storage_gb, battery_hours, stock_quantity, delivery_days, rating
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO NOTHING
"""


def read_product_catalog(csv_path: Path = CATALOG_PATH) -> pd.DataFrame:
    """Read and validate the CSV before any database changes are made."""
    try:
        products = pd.read_csv(csv_path, dtype={"id": "string"})
    except FileNotFoundError:
        raise
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse product catalog CSV at {csv_path}") from exc

    missing_columns = set(PRODUCT_COLUMNS) - set(products.columns)
    unexpected_columns = set(products.columns) - set(PRODUCT_COLUMNS)
    if missing_columns or unexpected_columns:
        raise ValueError(
            "Product catalog columns do not match the expected schema; "
            f"missing={sorted(missing_columns)}, unexpected={sorted(unexpected_columns)}"
        )
    if products.empty:
        raise ValueError(f"Product catalog CSV contains no records: {csv_path}")

    products = products.loc[:, PRODUCT_COLUMNS].copy()
    if products.isna().any().any():
        raise ValueError("Product catalog contains empty values in required columns")

    for column in TEXT_COLUMNS:
        products[column] = products[column].astype("string").str.strip()
        if products[column].eq("").any():
            raise ValueError(f"Product catalog contains blank values in '{column}'")

    try:
        for column in INTEGER_COLUMNS:
            values = pd.to_numeric(products[column], errors="raise")
            if (values % 1 != 0).any():
                raise ValueError(f"Product catalog column '{column}' must contain integers")
            products[column] = values.astype("int64")

        for column in REAL_COLUMNS:
            values = pd.to_numeric(products[column], errors="raise").astype("float64")
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"Product catalog column '{column}' must contain finite numbers")
            products[column] = values
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"Product catalog contains invalid numeric values: {exc}") from exc

    return products


def initialize_database(csv_path: Path = CATALOG_PATH) -> tuple[int, int]:
    """Create the products table and insert catalog rows without duplicating IDs."""
    products = read_product_catalog(csv_path)
    source_record_count = len(products)
    duplicate_count = int(products["id"].duplicated(keep="first").sum())
    if duplicate_count:
        logger.warning("Records skipped: %d duplicate IDs in the CSV", duplicate_count)
        products = products.drop_duplicates(subset="id", keep="first")

    connection = get_connection()
    try:
        with connection:
            table_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'products'"
            ).fetchone() is not None
            connection.execute(CREATE_PRODUCTS_TABLE)

            changes_before = connection.total_changes
            connection.executemany(
                INSERT_PRODUCT,
                products.loc[:, PRODUCT_COLUMNS].itertuples(index=False, name=None),
            )
            inserted_count = connection.total_changes - changes_before
    finally:
        connection.close()

    if table_exists:
        logger.info("Products table already exists")
    else:
        logger.info("Products table created")

    skipped_count = source_record_count - inserted_count
    logger.info("Records inserted: %d", inserted_count)
    logger.info("Records skipped: %d", skipped_count)
    return inserted_count, skipped_count


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        initialize_database()
    except DatabaseConnectionError:
        return 1
    except (FileNotFoundError, ValueError, OSError, sqlite3.Error):
        logger.exception("Database initialization failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
