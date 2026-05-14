"""
Structured Logging Configuration
Replaces print() statements with professional logging
Uses structlog for JSON output and colorization
"""
import sys
import logging
import logging.config
import structlog
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(name: str = __name__) -> logging.Logger:
    """
    Configure structured logging for the application
    Returns a configured logger instance
    """
    # Import here to avoid circular imports
    from src.backend.core.config import settings

    # Create logs directory if it doesn't exist
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure standard logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "[%(asctime)s] %(name)s:%(lineno)d - %(levelname)s - %(message)s"
            },
            "json": {
                "()": structlog.processors.JSONRenderer,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "detailed",
                "filename": settings.LOG_FILE,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": str(log_path).replace(".log", ".errors.log"),
                "maxBytes": 10485760,
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # root logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"]
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            }
        }
    }

    # Apply configuration
    logging.config.dictConfig(logging_config)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Get logger for this module
    logger = logging.getLogger(name)

    # Log startup message
    if name == __name__:
        logger.info(f"🔧 Logging initialized - Level: {settings.LOG_LEVEL}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)


# Don't initialize at import time to avoid circular imports
# Initialize at runtime when needed
