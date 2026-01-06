"""
Shared Retry/Backoff Abstraction Module

Provides configurable exponential backoff with jitter for retry logic.
This module consolidates retry implementations across the codebase to ensure
consistent behavior and maintainability.

Features:
- Exponential backoff with configurable multiplier
- Jitter to prevent thundering herd
- Exception filtering for selective retry
- Metrics/logging integration
- Both decorator and imperative API
"""

from functools import wraps
from typing import TypeVar, Callable, Type, Sequence
import random
import time
import logging

T = TypeVar('T')

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior.

    Args:
        max_retries: Maximum number of retry attempts (default: 4)
        base_delay: Initial delay in seconds (default: 1.0)
        multiplier: Delay multiplier for each retry (default: 2.0)
        max_delay: Maximum delay cap in seconds (default: 60.0)
        jitter: Random jitter factor 0.0-1.0 (default: 0.1)
        retryable_exceptions: Exception types that trigger retry (default: (Exception,))
        on_retry: Optional callback invoked on each retry with (exception, attempt_number)

    Example:
        config = RetryConfig(
            max_retries=3,
            base_delay=2.0,
            retryable_exceptions=(ConnectionError, TimeoutError)
        )
    """

    def __init__(
        self,
        max_retries: int = 4,
        base_delay: float = 1.0,
        multiplier: float = 2.0,
        max_delay: float = 60.0,
        jitter: float = 0.1,
        retryable_exceptions: Sequence[Type[Exception]] = (Exception,),
        on_retry: Callable[[Exception, int], None] | None = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.multiplier = multiplier
        self.max_delay = max_delay
        self.jitter = jitter
        self.retryable_exceptions = tuple(retryable_exceptions)
        self.on_retry = on_retry


def with_exponential_backoff(
    max_retries: int = 4,
    base_delay: float = 1.0,
    multiplier: float = 2.0,
    max_delay: float = 60.0,
    jitter: float = 0.1,
    retryable_exceptions: Sequence[Type[Exception]] = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator implementing exponential backoff with jitter.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        multiplier: Delay multiplier for each retry
        max_delay: Maximum delay cap in seconds
        jitter: Random jitter factor (0.0 to 1.0)
        retryable_exceptions: Exception types that trigger retry
        on_retry: Optional callback invoked on each retry

    Returns:
        Decorated function with retry behavior

    Example:
        @with_exponential_backoff(
            max_retries=3,
            base_delay=1.0,
            retryable_exceptions=(ConnectionError,)
        )
        def fetch_data(url: str) -> dict:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        raise

                    delay = min(
                        base_delay * (multiplier ** attempt),
                        max_delay
                    )

                    # Apply jitter
                    jitter_amount = delay * jitter * random.random()
                    delay += jitter_amount

                    if on_retry:
                        on_retry(e, attempt + 1)

                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s due to: {e}"
                    )

                    time.sleep(delay)

            # Should not reach here, but add a safe fallback for robustness
            if last_exception is not None:
                raise last_exception
            raise RuntimeError(
                f"with_exponential_backoff wrapper for {func.__name__} "
                "reached an unexpected state with no recorded exception."
            )

        return wrapper
    return decorator


class RetryPolicy:
    """
    Reusable retry policy for imperative retry control.

    Provides a generator-based API for manual retry loops with automatic
    backoff calculation.

    Example:
        policy = RetryPolicy(max_retries=3, base_delay=1.0)
        for attempt in policy.attempts():
            try:
                result = risky_operation()
                break
            except TransientError as e:
                attempt.retry_on(e)
    """

    def __init__(self, config: RetryConfig | None = None, **kwargs):
        """
        Initialize retry policy.

        Args:
            config: RetryConfig instance, or None to create from kwargs
            **kwargs: Passed to RetryConfig constructor if config is None
        """
        self.config = config or RetryConfig(**kwargs)

    def attempts(self):
        """Generator yielding retry attempt contexts."""
        for attempt_num in range(self.config.max_retries + 1):
            yield RetryAttempt(attempt_num, self.config)


class RetryAttempt:
    """Context for a single retry attempt.

    This class encapsulates the logic for deciding whether to retry
    after a failure and applying the appropriate backoff.
    """

    def __init__(self, attempt_num: int, config: RetryConfig):
        """
        Initialize retry attempt.

        Args:
            attempt_num: Zero-based attempt number
            config: RetryConfig instance
        """
        self.attempt_num = attempt_num
        self.config = config
        self._should_continue = True

    def retry_on(self, exception: Exception) -> None:
        """
        Signal that a retry should occur due to the given exception.

        Args:
            exception: Exception that caused the failure

        Raises:
            The original exception if max retries exceeded or exception not retryable
        """
        if self.attempt_num >= self.config.max_retries:
            raise exception

        if not isinstance(exception, self.config.retryable_exceptions):
            raise exception

        delay = min(
            self.config.base_delay * (self.config.multiplier ** self.attempt_num),
            self.config.max_delay
        )
        jitter_amount = delay * self.config.jitter * random.random()

        if self.config.on_retry:
            self.config.on_retry(exception, self.attempt_num + 1)

        logger.warning(
            f"Retry {self.attempt_num + 1}/{self.config.max_retries} "
            f"after {delay + jitter_amount:.2f}s due to: {exception}"
        )

        time.sleep(delay + jitter_amount)
