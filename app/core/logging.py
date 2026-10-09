"""Centralized application logging configuration."""

import logging


def configure_logging(log_level: str) -> None:
    """Configure the root logger using the application's configured log level."""
    normalized_level = log_level.upper()
    numeric_level = logging.getLevelNamesMapping().get(normalized_level)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unsupported log level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger().setLevel(numeric_level)
