"""Circuit Breaker with State Persistence - Minor Improvement 1.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Circuit Breaker
PHASE_ROLE: Provides fault tolerance with persistent state across restarts

Minor Improvement 1: Circuit Breaker State Persistence

This module provides a circuit breaker implementation with:
- State persistence to disk for recovery across restarts
- Configurable failure thresholds and recovery windows
- Thread-safe state management
- Metrics and monitoring support

Circuit Breaker States:
    CLOSED: Normal operation, requests flow through
    OPEN: Failures exceeded threshold, requests blocked
    HALF_OPEN: Testing recovery, limited requests allowed
"""

from __future__ import annotations

import json
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """States of the circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """
    Circuit breaker configuration with graceful degradation support.

    Degradation Instance: 5, 6, 6a
    Pattern:  CIRCUIT_BREAKER
    Fallback Behavior: When circuit OPEN, requests fail-fast with fallback
    Recovery: Half-open state tests limited requests before closing

    Attributes:
        failure_threshold:  Failures before opening circuit (default: 5)
        recovery_timeout_s: Seconds before half-open test (default: 60.0)
        success_threshold: Successes in half-open to close (default: 3)
        half_open_max_calls: Max concurrent calls in half-open (default: 3)
    """

    failure_threshold: int = 5
    success_threshold: int = 3
    recovery_timeout_s: float = 60.0
    half_open_max_calls: int = 3

    # Degradation metadata
    degradation_instance: str = "CIRCUIT_BREAKER_5_6_6a"
    fallback_strategy: str = "FAIL_FAST_WITH_CACHED"


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring.

    Attributes:
        total_calls: Total number of calls
        successful_calls: Number of successful calls
        failed_calls: Number of failed calls
        rejected_calls: Calls rejected due to open circuit
        state_changes: Number of state transitions
    """

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_changes: int = 0


class CircuitBreaker:
    """
    Basic circuit breaker implementation.

    Provides fault isolation by tracking failures and temporarily
    blocking requests when failures exceed a threshold.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        """
        Initialize circuit breaker.

        Args:
            name: Identifier for this circuit breaker.
            config: Circuit breaker configuration.
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.half_open_calls = 0
        self._lock = threading.Lock()
        self._metrics = CircuitBreakerMetrics()

    def can_execute(self) -> tuple[bool, str]:
        """
        Check if a request can be executed.

        Returns:
            Tuple of (can_execute, reason).
        """
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True, "Circuit closed - normal operation"

            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self._recovery_timeout_elapsed():
                    self._transition_to(CircuitState.HALF_OPEN)
                    return True, "Circuit half-open - testing recovery"
                self._metrics.rejected_calls += 1
                return False, f"Circuit open - blocked until {self._time_until_recovery():.1f}s"

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls < self.config.half_open_max_calls:
                    return True, "Circuit half-open - limited calls allowed"
                self._metrics.rejected_calls += 1
                return False, "Circuit half-open - max calls reached"

            return False, "Unknown state"

    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            self._metrics.total_calls += 1
            self._metrics.successful_calls += 1

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                self.half_open_calls += 1

                if self.success_count >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._metrics.total_calls += 1
            self._metrics.failed_calls += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open reopens the circuit
                self._transition_to(CircuitState.OPEN)
            elif self.state == CircuitState.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.half_open_calls = 0
            self._metrics.state_changes += 1
            logger.info(f"Circuit breaker {self.name} reset to CLOSED")

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self.state
        self.state = new_state
        self._metrics.state_changes += 1

        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0
            self.half_open_calls = 0
        elif new_state == CircuitState.OPEN:
            self.half_open_calls = 0

        logger.info(
            f"Circuit breaker {self.name} state change: {old_state.value} -> {new_state.value}"
        )

    def _recovery_timeout_elapsed(self) -> bool:
        """Check if recovery timeout has elapsed."""
        if self.last_failure_time is None:
            return True
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.recovery_timeout_s

    def _time_until_recovery(self) -> float:
        """Get seconds until recovery timeout."""
        if self.last_failure_time is None:
            return 0.0
        elapsed = time.time() - self.last_failure_time
        return max(0.0, self.config.recovery_timeout_s - elapsed)

    def get_metrics(self) -> dict[str, Any]:
        """Get circuit breaker metrics."""
        with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "total_calls": self._metrics.total_calls,
                "successful_calls": self._metrics.successful_calls,
                "failed_calls": self._metrics.failed_calls,
                "rejected_calls": self._metrics.rejected_calls,
                "state_changes": self._metrics.state_changes,
            }


class PersistentCircuitBreaker(CircuitBreaker):
    """
    Circuit breaker with persistent state.

    Minor Improvement 1: Circuit Breaker State Persistence

    Extends CircuitBreaker with:
    - State persistence to disk
    - Recovery across process restarts
    - Automatic state loading on initialization
    """

    def __init__(
        self, name: str, state_file: Path | str, config: CircuitBreakerConfig | None = None
    ):
        """
        Initialize persistent circuit breaker.

        Args:
            name: Identifier for this circuit breaker.
            state_file: Path to state persistence file.
            config: Circuit breaker configuration.
        """
        super().__init__(name, config)
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        """Load persisted state from disk."""
        if not self.state_file.exists():
            logger.debug(f"No persisted state for {self.name}, starting fresh")
            return

        try:
            with open(self.state_file) as f:
                state = json.load(f)

            self.state = CircuitState(state["state"])
            self.failure_count = state["failure_count"]
            self.success_count = state.get("success_count", 0)
            self.last_failure_time = state.get("last_failure_time")
            self.half_open_calls = state.get("half_open_calls", 0)

            logger.info(
                f"Loaded persisted state for {self.name}: "
                f"state={self.state.value}, failures={self.failure_count}"
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to load persisted state for {self.name}: {e}")
            # Start fresh on load failure
            self.reset()

    def _save_state(self) -> None:
        """Persist current state to disk."""
        state = {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "half_open_calls": self.half_open_calls,
            "saved_at": time.time(),
        }

        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)
            logger.debug(f"Saved state for {self.name}")
        except OSError as e:
            logger.error(f"Failed to save state for {self.name}: {e}")

    def record_failure(self) -> None:
        """Record failure and persist state."""
        super().record_failure()
        self._save_state()

    def record_success(self) -> None:
        """Record success and persist state."""
        super().record_success()
        self._save_state()

    def reset(self) -> None:
        """Reset and persist state."""
        super().reset()
        self._save_state()

    def delete_persisted_state(self) -> bool:
        """
        Delete the persisted state file.

        Returns:
            True if file was deleted, False if it didn't exist.
        """
        if self.state_file.exists():
            self.state_file.unlink()
            logger.info(f"Deleted persisted state for {self.name}")
            return True
        return False


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    Provides centralized access and management of circuit breakers.
    """

    def __init__(self, state_dir: Path | str = Path("artifacts/circuit_breakers")):
        """
        Initialize circuit breaker registry.

        Args:
            state_dir: Directory for state persistence files.
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_or_create(
        self, name: str, config: CircuitBreakerConfig | None = None, persistent: bool = True
    ) -> CircuitBreaker:
        """
        Get existing or create new circuit breaker.

        Args:
            name: Circuit breaker name.
            config: Configuration for new breaker.
            persistent: Whether to create persistent breaker.

        Returns:
            CircuitBreaker instance.
        """
        with self._lock:
            if name not in self._breakers:
                if persistent:
                    state_file = self.state_dir / f"{name}.state.json"
                    self._breakers[name] = PersistentCircuitBreaker(
                        name=name,
                        state_file=state_file,
                        config=config,
                    )
                else:
                    self._breakers[name] = CircuitBreaker(
                        name=name,
                        config=config,
                    )
            return self._breakers[name]

    def get_all_metrics(self) -> dict[str, dict[str, Any]]:
        """Get metrics for all circuit breakers."""
        with self._lock:
            return {name: breaker.get_metrics() for name, breaker in self._breakers.items()}

    def reset_all(self) -> int:
        """
        Reset all circuit breakers.

        Returns:
            Number of breakers reset.
        """
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()
            return len(self._breakers)


# === DECORATOR FOR CIRCUIT BREAKER PROTECTION ===


def circuit_protected(
    breaker: CircuitBreaker, fallback: Callable[..., T] | None = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to protect a function with a circuit breaker.

    Args:
        breaker: Circuit breaker to use.
        fallback: Optional fallback function when circuit is open.

    Returns:
        Decorated function.

    Usage:
        breaker = CircuitBreaker("my_service")

        @circuit_protected(breaker)
        def call_external_service():
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            can_execute, reason = breaker.can_execute()

            if not can_execute:
                if fallback:
                    logger.warning(f"Circuit {breaker.name} open, using fallback: {reason}")
                    return fallback(*args, **kwargs)
                raise RuntimeError(f"Circuit {breaker.name} open: {reason}")

            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception:
                breaker.record_failure()
                raise

        return wrapper

    return decorator


# === MODULE EXPORTS ===

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerMetrics",
    "CircuitBreakerRegistry",
    "CircuitState",
    "PersistentCircuitBreaker",
    "circuit_protected",
]
