"""Logging configuration for nanobot."""

import sys
from loguru import logger


def configure_logging(verbose: bool = False, debug: bool = False) -> None:
    """
    Configure loguru logging.
    
    Args:
        verbose: Enable INFO level logging
        debug: Enable DEBUG level logging (overrides verbose)
    """
    # Remove default handler
    logger.remove()
    
    # Determine log level
    if debug:
        level = "DEBUG"
    elif verbose:
        level = "INFO"
    else:
        level = "WARNING"
    
    # Add console handler with formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )
    
    logger.info(f"Logging configured at {level} level")


def configure_file_logging(log_file: str, level: str = "DEBUG") -> None:
    """
    Add file logging handler.
    
    Args:
        log_file: Path to log file
        level: Log level for file handler
    """
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    logger.info(f"File logging enabled: {log_file}")

