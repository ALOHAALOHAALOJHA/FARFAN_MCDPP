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
from typing import TypeVar, Callable, Type, Sequence, Dict, Any
import random
import time
import logging

T = TypeVar('T')

logger = logging.getLogger(__name__)


class TransientError(Exception):
    """Exception indicating a temporary failure that can be retried."""
    pass


class PermanentError(Exception):
    """Exception indicating a fatal failure that should not be retried."""
    pass


class RetryConfig:
    """
    Configuration for retry behavior with metrics tracking.

    Degradation Instance: 7
    Pattern: RETRY_WITH_BACKOFF
    Fallback Behavior: After max_retries, raise or return fallback
    Recovery: Each retry waits longer with jitter to prevent thundering herd

    Args:
        max_retries: Maximum number of retry attempts (default: 4)
        base_delay_seconds: Initial delay in seconds (default: 1.0)
        multiplier: Delay multiplier for each retry (default: 2.0)
        max_delay_seconds: Maximum delay cap in seconds (default: 60.0)
        jitter_factor: Random jitter factor 0.0-1.0 (default: 0.1)
        retryable_exceptions: Exception types that trigger retry (default: (Exception,))
        on_retry: Optional callback invoked on each retry with (exception, attempt_number, delay_ms)

    Metrics Attributes:
        total_chunks: Total number of units processed
        successful_chunks: Number of units processed successfully
        failed_chunks: Number of units that failed after all retries
        total_retries: Cumulative count of retry attempts
        total_time_ms: Cumulative time spent in retries and processing
    """

    def __init__(
        self,
        max_retries: int = 4,
        base_delay_seconds: float = 1.0,
        multiplier: float = 2.0,
        max_delay_seconds: float = 60.0,
        jitter_factor: float = 0.1,
        retryable_exceptions: Sequence[Type[Exception]] = (Exception, TransientError),
        on_retry: Callable[[Exception, int, float], None] | None = None
    ):
        # Degradation metadata
        self.degradation_instance = "RETRY_PATTERN_7"
        self.fallback_strategy = "PROPAGATE_AFTER_EXHAUST"
        # Validate parameters
        if max_retries < 0:
            raise ValueError(f"max_retries must be non-negative, got {max_retries}")
        if base_delay_seconds < 0:
            raise ValueError(f"base_delay_seconds must be non-negative, got {base_delay_seconds}")
        if multiplier < 0:
            raise ValueError(f"multiplier must be non-negative, got {multiplier}")
        if max_delay_seconds < 0:
            raise ValueError(f"max_delay_seconds must be non-negative, got {max_delay_seconds}")
        if not (0.0 <= jitter_factor <= 1.0):
            raise ValueError(f"jitter_factor must be between 0.0 and 1.0, got {jitter_factor}")
        
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds
        self.multiplier = multiplier
        self.max_delay_seconds = max_delay_seconds
        self.jitter_factor = jitter_factor
        self.retryable_exceptions = tuple(retryable_exceptions)
        self.on_retry = on_retry

        # Metrics
        self.total_chunks = 0
        self.successful_chunks = 0
        self.failed_chunks = 0
        self.total_retries = 0
        self.total_time_ms = 0.0

    def get_metrics(self) -> Dict[str, Any]:
        """Return a snapshot of retry metrics."""
        return {
            "total_chunks": self.total_chunks,
            "successful_chunks": self.successful_chunks,
            "failed_chunks": self.failed_chunks,
            "total_retries": self.total_retries,
            "total_time_ms": self.total_time_ms
        }


def with_exponential_backoff(
    config: RetryConfig | None = None,
    **kwargs
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator implementing exponential backoff with jitter and metrics.

    Args:
        config: RetryConfig instance, or None to use kwargs
        **kwargs: Arguments to create a RetryConfig if config is None

    Returns:
        Decorated function with retry behavior
    """
    retry_config = config or RetryConfig(**kwargs)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.perf_counter()
            retry_config.total_chunks += 1
            last_exception: Exception | None = None

            for attempt in range(retry_config.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    retry_config.successful_chunks += 1
                    retry_config.total_time_ms += (time.perf_counter() - start_time) * 1000
                    return result
                except retry_config.retryable_exceptions as e:
                    if isinstance(e, PermanentError):
                        retry_config.failed_chunks += 1
                        retry_config.total_time_ms += (time.perf_counter() - start_time) * 1000
                        raise

                    last_exception = e

                    if attempt == retry_config.max_retries:
                        retry_config.failed_chunks += 1
                        retry_config.total_time_ms += (time.perf_counter() - start_time) * 1000
                        raise

                    retry_config.total_retries += 1
                    
                    delay = min(
                        retry_config.base_delay_seconds * (retry_config.multiplier ** attempt),
                        retry_config.max_delay_seconds
                    )

                    # Apply jitter
                    jitter_amount = delay * retry_config.jitter_factor * random.random()
                    total_delay = delay + jitter_amount

                    if retry_config.on_retry:
                        retry_config.on_retry(e, attempt + 1, total_delay * 1000)

                    logger.warning(
                        f"Retry {attempt + 1}/{retry_config.max_retries} for {func.__name__} "
                        f"after {total_delay:.2f}s due to: {e}"
                    )

                    time.sleep(total_delay)

            # Should not reach here
            retry_config.failed_chunks += 1
            retry_config.total_time_ms += (time.perf_counter() - start_time) * 1000
            if last_exception is not None:
                raise last_exception
            raise RuntimeError(f"Retry wrapper for {func.__name__} reached unexpected state.")

        return wrapper
    return decorator


class RetryPolicy:
    """
    Reusable retry policy for imperative retry control with metrics.
    """

    def __init__(self, config: RetryConfig | None = None, **kwargs):
        self.config = config or RetryConfig(**kwargs)
        self._start_time = 0.0

    def attempts(self):
        """Generator yielding retry attempt contexts."""
        self._start_time = time.perf_counter()
        self.config.total_chunks += 1
        
        for attempt_num in range(self.config.max_retries + 1):
            yield RetryAttempt(attempt_num, self.config, self._start_time)


class RetryAttempt:
    """Context for a single retry attempt."""

    def __init__(self, attempt_num: int, config: RetryConfig, start_time: float):
        self.attempt_num = attempt_num
        self.config = config
        self._start_time = start_time

    def retry_on(self, exception: Exception) -> None:
        """Signal that a retry should occur."""
        if isinstance(exception, PermanentError):
            self.config.failed_chunks += 1
            self.config.total_time_ms += (time.perf_counter() - self._start_time) * 1000
            raise exception

        if self.attempt_num >= self.config.max_retries:
            self.config.failed_chunks += 1
            self.config.total_time_ms += (time.perf_counter() - self._start_time) * 1000
            raise exception

        if not isinstance(exception, self.config.retryable_exceptions):
            self.config.failed_chunks += 1
            self.config.total_time_ms += (time.perf_counter() - self._start_time) * 1000
            raise exception

        self.config.total_retries += 1
        
        delay = min(
            self.config.base_delay_seconds * (self.config.multiplier ** self.attempt_num),
            self.config.max_delay_seconds
        )
        jitter_amount = delay * self.config.jitter_factor * random.random()
        total_delay = delay + jitter_amount

        if self.config.on_retry:
            self.config.on_retry(exception, self.attempt_num + 1, total_delay * 1000)

        logger.warning(
            f"Retry {self.attempt_num + 1}/{self.config.max_retries} "
            f"after {total_delay:.2f}s due to: {exception}"
        )

        time.sleep(total_delay)

    def mark_success(self) -> None:
        """Record successful completion of the unit."""
        self.config.successful_chunks += 1
        self.config.total_time_ms += (time.perf_counter() - self._start_time) * 1000