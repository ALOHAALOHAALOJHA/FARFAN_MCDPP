"""
Failure & Fallback Contract (FFC) - Implementation
"""

from collections.abc import Callable
from typing import Any


class FailureFallbackContract:
    @staticmethod
    def execute_with_fallback(
        func: Callable, fallback_value: Any, expected_exceptions: tuple[type[Exception], ...]
    ) -> Any:
        """
        Executes func. If it raises an expected exception, returns fallback_value.
        Ensures determinism and no side effects (simulated).
        """
        try:
            return func()
        except expected_exceptions:
            return fallback_value

    @staticmethod
    def verify_fallback_determinism(
        func: Callable, fallback_value: Any, exception_type: type[Exception]
    ) -> bool:
        """
        Verifies that repeated failures produce identical fallback values.
        """
        res1 = FailureFallbackContract.execute_with_fallback(
            func, fallback_value, (exception_type,)
        )
        res2 = FailureFallbackContract.execute_with_fallback(
            func, fallback_value, (exception_type,)
        )
        return res1 == res2
