"""
Calibration Decorators Module
=============================

Provides decorators for calibrated methods in the pipeline.
"""

from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar('F', bound=Callable[..., Any])


def calibrated_method(
    calibration_key: str | None = None,
    fallback_value: Any = None,
    strict: bool = False,
) -> Callable[[F], F]:
    """
    Decorator that marks a method as calibration-aware.
    
    When calibration is enabled, the method may receive adjusted parameters
    based on empirical calibration data.
    
    Args:
        calibration_key: Key to look up calibration data
        fallback_value: Value to use if calibration fails
        strict: If True, raise error on calibration failure
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # For now, just pass through to the original function
            # Full calibration integration would check calibration registry here
            return func(*args, **kwargs)
        
        # Mark as calibrated for introspection
        wrapper._calibration_key = calibration_key  # type: ignore
        wrapper._calibration_fallback = fallback_value  # type: ignore
        wrapper._calibration_strict = strict  # type: ignore
        
        return wrapper  # type: ignore
    
    return decorator


def requires_calibration(calibration_keys: list[str]) -> Callable[[F], F]:
    """
    Decorator that declares calibration dependencies.
    
    Args:
        calibration_keys: List of required calibration keys
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        func._required_calibrations = calibration_keys  # type: ignore
        return func
    
    return decorator


def calibration_checkpoint(checkpoint_name: str) -> Callable[[F], F]:
    """
    Decorator that marks a calibration checkpoint.
    
    Args:
        checkpoint_name: Name of the checkpoint
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Log checkpoint entry
            result = func(*args, **kwargs)
            # Log checkpoint exit
            return result
        
        wrapper._checkpoint_name = checkpoint_name  # type: ignore
        return wrapper  # type: ignore
    
    return decorator
