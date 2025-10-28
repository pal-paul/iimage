"""
Structured logging configuration for the application.
"""

import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict

import structlog


def add_timestamp(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """Add timestamp to log events."""
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    return event_dict


def add_log_level(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """Add log level to log events."""
    event_dict["level"] = method_name.upper()
    return event_dict


def setup_logging(log_level: str = "INFO", json_logs: bool = True) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )
    
    # Reduce noise from other libraries
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        add_log_level,
        add_timestamp,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    Get a structured logger instance.
    
    Args:
        name: Name of the logger (typically __name__)
    
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def log_exception(logger: Any, exc: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log an exception with full context.
    
    Args:
        logger: Logger instance
        exc: Exception to log
        context: Additional context information
    """
    context = context or {}
    logger.error(
        "Exception occurred",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        traceback=traceback.format_exc(),
        **context
    )
