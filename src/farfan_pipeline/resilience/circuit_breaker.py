"""Circuit Breaker implementation for Phase 2 micro-question execution.

Provides protection against systematic failures (e.g., LLM rate limiting) that would
otherwise burn through retry budgets inefficiently.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, TypeVar


class CircuitState(Enum):
    """Circuit breaker states."""
    
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 3          # Successes to close from half-open
    timeout_seconds: float = 60.0       # Time in OPEN before trying HALF_OPEN
    error_rate_threshold: float = 0.05  # 5% error budget (15 failures out of 300)
    window_size: int = 100              # Rolling window for error rate calculation


T = TypeVar('T')


@dataclass
class CircuitBreaker(Generic[T]):
    """Circuit breaker for protecting against cascading failures.
    
    Tracks success/failure rates over a rolling window and transitions between states:
    - CLOSED: Normal operation, all requests allowed
    - OPEN: Failing fast, rejecting all requests for timeout period
    - HALF_OPEN: Testing recovery, allowing limited requests
    """
    
    config: CircuitBreakerConfig
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    _results_window: list[bool] = field(default_factory=list)
    
    def record_success(self) -> None:
        """Record a successful execution."""
        self._results_window.append(True)
        self._trim_window()
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
    
    def record_failure(self, error: Exception) -> None:
        """Record a failed execution."""
        self._results_window.append(False)
        self._trim_window()
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        
        if self._error_rate_exceeded():
            self._transition_to(CircuitState.OPEN)
    
    def _error_rate_exceeded(self) -> bool:
        """Check if error rate exceeds threshold."""
        # Need minimum samples before calculating rate
        if len(self._results_window) < self.config.window_size // 2:
            # Use simple failure count for early stages
            return self.failure_count >= self.config.failure_threshold
        
        # Calculate error rate over rolling window
        failures = sum(1 for r in self._results_window if not r)
        error_rate = failures / len(self._results_window)
        return error_rate > self.config.error_rate_threshold
    
    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if time.monotonic() - self.last_failure_time > self.config.timeout_seconds:
                self._transition_to(CircuitState.HALF_OPEN)
                return True
            return False
        
        # HALF_OPEN allows trial executions
        return True
    
    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new circuit state."""
        old_state = self.state
        self.state = new_state
        
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0
        
        # Log state transition for observability
        if old_state != new_state:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"Circuit breaker state transition: {old_state.value} → {new_state.value}",
                extra={
                    "old_state": old_state.value,
                    "new_state": new_state.value,
                    "failure_count": self.failure_count,
                    "success_count": self.success_count,
                }
            )
    
    def _trim_window(self) -> None:
        """Trim results window to configured size."""
        while len(self._results_window) > self.config.window_size:
            self._results_window.pop(0)
    
    def get_stats(self) -> dict[str, any]:
        """Get circuit breaker statistics."""
        if not self._results_window:
            error_rate = 0.0
        else:
            failures = sum(1 for r in self._results_window if not r)
            error_rate = failures / len(self._results_window)
        
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "error_rate": error_rate,
            "window_size": len(self._results_window),
            "time_since_last_failure": time.monotonic() - self.last_failure_time if self.last_failure_time > 0 else None,
        }


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and rejecting requests."""
    
    def __init__(self, breaker_name: str, time_until_retry: float):
        self.breaker_name = breaker_name
        self.time_until_retry = time_until_retry
        super().__init__(
            f"Circuit breaker '{breaker_name}' is OPEN. "
            f"Retry in {time_until_retry:.1f}s"
        )
