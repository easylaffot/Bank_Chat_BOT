"""Shared SQLite connection management."""

import logging
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "storage" / "sqlite" / "shopping_assistant.db"

load_dotenv(PROJECT_ROOT / ".env", override=False)


class DatabaseConnectionError(RuntimeError):
    """Raised when the configured SQLite database cannot be opened."""


def get_database_path() -> Path:
    """Return the configured SQLite path, resolving relative paths from the project root."""
    configured_path = os.getenv("SQLITE_DATABASE_PATH")
    database_path = Path(configured_path).expanduser() if configured_path else DEFAULT_DATABASE_PATH
    if not database_path.is_absolute():
        database_path = PROJECT_ROOT / database_path
    return database_path.resolve()


def get_connection() -> sqlite3.Connection:
    """Create a repository-ready SQLite connection using the configured database path."""
    database_path = get_database_path()
    connection = None

    try:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
    except (OSError, sqlite3.Error) as exc:
        if connection is not None:
            connection.close()
        logger.exception("Could not connect to SQLite database at %s", database_path)
        raise DatabaseConnectionError(
            f"Could not connect to SQLite database at {database_path}"
        ) from exc

    logger.info("Database connected: %s", database_path)
    return connection
