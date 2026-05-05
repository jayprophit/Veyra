"""
Enterprise Logging Configuration
================================
Structured logging with JSON output, correlation IDs, and monitoring integration.
Based on best practices from AWS, Google Cloud, and enterprise logging standards.
"""

import logging
import logging.config
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import structlog
from structlog.stdlib import LoggerFactory


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_json: bool = True
) -> None:
    """Setup structured logging configuration."""
    
    # Ensure logs directory exists
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if enable_json else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "console": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json" if enable_json else "console",
                "stream": sys.stdout,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    # Add file handler if log_file specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        config["root"]["handlers"].append("file")
    
    logging.config.dictConfig(config)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger."""
    return structlog.get_logger(name)


class RequestLogger:
    """Request/response logging middleware helper."""
    
    def __init__(self):
        self.logger = get_logger("request")
    
    def log_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log incoming request."""
        self.logger.info(
            "Incoming request",
            method=method,
            path=path,
            headers=self._sanitize_headers(headers),
            request_id=request_id
        )
    
    def log_response(
        self,
        status_code: int,
        headers: Dict[str, str],
        body: Optional[str] = None,
        duration_ms: Optional[float] = None,
        request_id: Optional[str] = None
    ):
        """Log outgoing response."""
        self.logger.info(
            "Request completed",
            status_code=status_code,
            duration_ms=duration_ms,
            request_id=request_id
        )
    
    def log_error(
        self,
        error: Exception,
        request_id: Optional[str] = None
    ):
        """Log error with full context."""
        self.logger.error(
            "Request failed",
            error_type=type(error).__name__,
            error_message=str(error),
            request_id=request_id
        )
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive headers from logs."""
        sensitive_headers = {"authorization", "cookie", "x-api-key"}
        return {
            k: "***" if k.lower() in sensitive_headers else v
            for k, v in headers.items()
        }


# Performance monitoring
class PerformanceLogger:
    """Performance monitoring logger."""
    
    def __init__(self):
        self.logger = get_logger("performance")
    
    def log_slow_query(
        self,
        query: str,
        duration_ms: float,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Log slow database queries."""
        self.logger.warning(
            "Slow database query detected",
            query=query[:200],  # Truncate long queries
            duration_ms=duration_ms,
            parameters=parameters
        )
    
    def log_api_latency(
        self,
        endpoint: str,
        method: str,
        duration_ms: float,
        status_code: int
    ):
        """Log API latency metrics."""
        level = "warning" if duration_ms > 1000 else "info"
        getattr(self.logger, level)(
            "API latency",
            endpoint=endpoint,
            method=method,
            duration_ms=duration_ms,
            status_code=status_code
        )
