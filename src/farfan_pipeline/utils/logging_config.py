"""
Centralized structured logging configuration for FARFAN pipeline.

This module provides:
- Structured JSON logging via structlog
- Configurable log levels and formatters
- Error context enrichment
- Integration hooks for error tracking (Sentry/Datadog)

Usage:
    from farfan_pipeline.utils.logging_config import get_logger
    
    logger = get_logger(__name__)
    logger.info("operation_started", context={"key": "value"})
    logger.error("operation_failed", error=str(e), error_type=type(e).__name__)
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

# Module-level flag to prevent re-configuration
_configured = False


def configure_logging(
    level: str = "INFO",
    json_output: bool = True,
    include_timestamps: bool = True,
) -> None:
    """
    Configure structured logging for the entire application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: If True, output JSON; if False, use console-friendly format
        include_timestamps: Include ISO timestamps in log entries
    """
    global _configured
    if _configured:
        return
    
    # Standard library logging configuration
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )
    
    # Build processor chain
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if include_timestamps:
        processors.insert(0, structlog.processors.TimeStamper(fmt="iso"))
    
    # Final renderer based on output format
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    _configured = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured structured logger.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog bound logger
    """
    # Ensure logging is configured
    if not _configured:
        configure_logging()
    
    return structlog.get_logger(name)


def log_exception(
    logger: structlog.stdlib.BoundLogger,
    error: Exception,
    operation: str,
    context: dict[str, Any] | None = None,
    *,
    reraise: bool = True,
) -> None:
    """
    Log an exception with full context.
    
    Args:
        logger: The structured logger to use
        error: The exception that occurred
        operation: Name of the operation that failed
        context: Additional context to include in the log
        reraise: If True, re-raise the exception after logging
        
    Raises:
        The original exception if reraise=True
    """
    log_context = {
        "operation": operation,
        "error": str(error),
        "error_type": type(error).__name__,
        **(context or {}),
    }
    
    logger.error(
        "operation_failed",
        exc_info=True,
        **log_context,
    )
    
    if reraise:
        raise


class ErrorRecoveryStrategy:
    """
    Strategies for handling recoverable errors.
    
    Usage:
        strategy = ErrorRecoveryStrategy(logger)
        result = strategy.with_fallback(risky_operation, fallback_value)
    """
    
    def __init__(self, logger: structlog.stdlib.BoundLogger):
        self.logger = logger
    
    def with_fallback(
        self,
        operation: callable,
        fallback: Any,
        operation_name: str = "unknown",
        *,
        exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> Any:
        """
        Execute operation with fallback on failure.
        
        Args:
            operation: Callable to execute
            fallback: Value to return on failure
            operation_name: Name for logging
            exceptions: Exception types to catch
            
        Returns:
            Operation result or fallback value
        """
        try:
            return operation()
        except exceptions as e:
            self.logger.warning(
                "operation_fallback_used",
                operation=operation_name,
                error=str(e),
                error_type=type(e).__name__,
                fallback_value=repr(fallback) if not callable(fallback) else "<callable>",
            )
            return fallback() if callable(fallback) else fallback
    
    def with_retry(
        self,
        operation: callable,
        max_attempts: int = 3,
        operation_name: str = "unknown",
        *,
        exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> Any:
        """
        Execute operation with retry on failure.
        
        Args:
            operation: Callable to execute
            max_attempts: Maximum retry attempts
            operation_name: Name for logging
            exceptions: Exception types to retry on
            
        Returns:
            Operation result
            
        Raises:
            Last exception if all retries fail
        """
        last_error: Exception | None = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                return operation()
            except exceptions as e:
                last_error = e
                self.logger.warning(
                    "operation_retry",
                    operation=operation_name,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    error=str(e),
                    error_type=type(e).__name__,
                )
        
        self.logger.error(
            "operation_failed_all_retries",
            operation=operation_name,
            attempts=max_attempts,
            error=str(last_error),
            error_type=type(last_error).__name__ if last_error else "unknown",
        )
        
        if last_error:
            raise last_error


# Initialize logging on module import
configure_logging()
