"""
Structured Logging Configuration
==================================
Replaces print statements with proper structured logging
"""

import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": LOGS_DIR / f"financial_master_{datetime.now():%Y%m%d}.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": LOGS_DIR / f"financial_master_errors_{datetime.now():%Y%m%d}.log",
            "maxBytes": 10485760,
            "backupCount": 10
        },
        "performance_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": LOGS_DIR / "performance.log",
            "maxBytes": 10485760,
            "backupCount": 5
        },
        "null": {
            "class": "logging.NullHandler"
        }
    },
    "loggers": {
        "": {  # root logger
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "handlers": ["console", "file", "error_file"]
        },
        "veyra": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "sqlalchemy.engine": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        },
        "sqlalchemy.pool": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        },
        "performance": {
            "level": "DEBUG",
            "handlers": ["performance_file"],
            "propagate": False
        }
    }
}

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)

# Get loggers for different components
logger = logging.getLogger("veyra")
app_logger = logging.getLogger("app")
performance_logger = logging.getLogger("performance")


def setup_logging(name: str = "veyra") -> logging.Logger:
    """Get configured logger instance"""
    return logging.getLogger(name)


def log_exception(logger_instance: logging.Logger, exception: Exception, context: str = ""):
    """Log exception with context"""
    logger_instance.exception(f"Exception occurred{f' in {context}' if context else ''}: {str(exception)}")


def log_performance(operation: str, duration: float, status: str = "success"):
    """Log performance metric"""
    performance_logger.debug(f"{operation} - Duration: {duration:.3f}s - Status: {status}")


# Export common loggers
__all__ = ["logger", "app_logger", "performance_logger", "setup_logging", "log_exception", "log_performance"]
