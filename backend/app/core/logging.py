"""
PriceNest — Structured Application Logging
Configures clean, consistent console logging without exposing sensitive data.
"""

import logging
import sys


def setup_logging(debug: bool = False) -> logging.Logger:
    """Initialize root and application loggers with structured format."""
    log_level = logging.DEBUG if debug else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("pricenest")
    logger.setLevel(log_level)
    if not logger.handlers:
        logger.addHandler(handler)

    # Suppress overly chatty third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)

    return logger


logger = setup_logging()
