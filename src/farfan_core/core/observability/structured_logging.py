"""
Structured logging for F.A.R.F.A.N runtime observability.

This module provides standardized logging for fallbacks, degradations, and
runtime events with consistent field injection for observability.
"""

import logging
import structlog
from typing import Optional

from farfan_core.core.runtime_config import RuntimeMode
from farfan_core.core.contracts.runtime_contracts import FallbackCategory


# Configure structlog for JSON logging
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
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def log_fallback(
    component: str,
    subsystem: str,
    fallback_category: FallbackCategory,
    fallback_mode: str,
    reason: str,
    runtime_mode: RuntimeMode,
    document_id: Optional[str] = None,
    run_id: Optional[str] = None,
    logger: Optional[structlog.BoundLogger] = None,
) -> None:
    """
    Emit structured log for fallback activation.
    
    This is the standard logging function for all fallback events. It ensures
    consistent field injection and proper categorization for observability.
    
    Args:
        component: Component name (e.g., "language_detection", "calibration")
        subsystem: Subsystem name (e.g., "spc_ingestion", "orchestrator")
        fallback_category: Fallback category (A/B/C/D)
        fallback_mode: Specific fallback mode (e.g., "warn_default_es", "estimated")
        reason: Human-readable reason for fallback
        runtime_mode: Current runtime mode
        document_id: Optional document identifier
        run_id: Optional run identifier
        logger: Optional logger instance (creates new if None)
        
    Example:
        >>> log_fallback(
        ...     component="language_detection",
        ...     subsystem="spc_ingestion",
        ...     fallback_category=FallbackCategory.B,
        ...     fallback_mode="warn_default_es",
        ...     reason="LangDetectException",
        ...     runtime_mode=RuntimeMode.PROD
        ... )
    """
    if logger is None:
        logger = get_logger()
    
    # Determine log level based on category
    if fallback_category == FallbackCategory.A:
        log_level = logging.ERROR
    elif fallback_category == FallbackCategory.B:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO
    
    # Emit structured log
    logger.log(
        log_level,
        "fallback_activated",
        component=component,
        subsystem=subsystem,
        fallback_category=fallback_category.value,
        fallback_mode=fallback_mode,
        reason=reason,
        runtime_mode=runtime_mode.value,
        document_id=document_id,
        run_id=run_id,
    )


def log_boot_check_failure(
    check_name: str,
    reason: str,
    code: str,
    runtime_mode: RuntimeMode,
    logger: Optional[structlog.BoundLogger] = None,
) -> None:
    """
    Log boot check failure.
    
    Args:
        check_name: Name of failed check
        reason: Failure reason
        code: Error code
        runtime_mode: Current runtime mode
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger()
    
    logger.error(
        "boot_check_failed",
        check_name=check_name,
        reason=reason,
        code=code,
        runtime_mode=runtime_mode.value,
    )


def log_boot_check_success(
    check_name: str,
    runtime_mode: RuntimeMode,
    logger: Optional[structlog.BoundLogger] = None,
) -> None:
    """
    Log boot check success.
    
    Args:
        check_name: Name of successful check
        runtime_mode: Current runtime mode
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger()
    
    logger.info(
        "boot_check_passed",
        check_name=check_name,
        runtime_mode=runtime_mode.value,
    )


def log_runtime_config_loaded(
    config_repr: str,
    runtime_mode: RuntimeMode,
    logger: Optional[structlog.BoundLogger] = None,
) -> None:
    """
    Log runtime configuration loaded.
    
    Args:
        config_repr: String representation of config
        runtime_mode: Runtime mode
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger()
    
    logger.info(
        "runtime_config_loaded",
        config=config_repr,
        runtime_mode=runtime_mode.value,
    )
