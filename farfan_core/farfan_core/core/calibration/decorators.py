import functools
import logging
from typing import Any, Callable
from farfan_core.core.calibration.calibration_registry import get_calibration

logger = logging.getLogger(__name__)

def calibrated_method(method_id: str) -> Callable:
    """
    Decorator to apply calibration to a method.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            calibration_params = get_calibration(method_id)
            logger.info(f"Calling calibrated method '{method_id}' with params: {calibration_params}")
            # In a real implementation, we would use the calibration_params
            # to modify the behavior of the decorated function.
            return func(*args, **kwargs)
        return wrapper
    return decorator
