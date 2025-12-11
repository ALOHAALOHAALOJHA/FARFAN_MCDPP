"""
CALIBRATION DECORATORS

@calibrated_method - Forces anchoring to central system
@calibration_required - Enforces minimum threshold

JOBFRONT 4 will implement full functionality.
"""
# STUB - Implementation in JOBFRONT 4

from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def calibrated_method(method_id: str) -> Callable[[F], F]:
    """
    OBLIGATORIO: Decorador que FUERZA anclaje al sistema central.
    
    STUB - Will be implemented in JOBFRONT 4.
    
    Workflow:
    1. Load parameters from JSON
    2. Execute method
    3. Calibrate result via orchestrator
    4. Validate and return
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # STUB - just pass through for now
            return func(*args, **kwargs)
        return wrapper  # type: ignore[return-value]
    return decorator


def calibration_required(
    threshold: float = 0.7,
    method_id: str | None = None,
) -> Callable[[F], F]:
    """
    Decorator that enforces minimum calibration threshold.
    
    STUB - Will be implemented in JOBFRONT 4.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # STUB - just pass through for now
            return func(*args, **kwargs)
        return wrapper  # type: ignore[return-value]
    return decorator
