"""
Calibration Decorators - Stub for calibration system
"""

from typing import Any, Callable


def calibrated_method(method_id: str) -> Callable[[Any], Any]:
    """Decorator stub for calibrated methods"""
    def decorator(func: Any) -> Any:
        return func
    return decorator
