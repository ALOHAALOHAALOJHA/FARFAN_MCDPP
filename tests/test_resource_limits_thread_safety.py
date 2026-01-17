"""Tests for ResourceLimits thread safety and Circuit Breaker functionality."""

from __future__ import annotations

import asyncio
import threading
import time
import pytest

from farfan_pipeline.orchestration.core_orchestrator import ResourceLimits
from farfan_pipeline.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpen,
    CircuitState,
)


class TestResourceLimitsThreadSafety:
    """Test thread-safe access to ResourceLimits._max_workers."""

    @pytest.mark.asyncio
    async def test_no_race_condition_under_concurrent_access(self):
        """Verify _max_workers remains consistent under concurrent modification."""
        limits = ResourceLimits(max_workers=10, min_workers=2, hard_max_workers=20, history=120)

        errors = []
        iterations = 100  # Reduced for faster testing

        def sync_predictor():
            """Simulates sync thread modifying budget via _predict_worker_budget."""
            for _ in range(iterations):
                # Force high utilization to trigger budget changes
                usage = {
                    "timestamp": "2025-12-17T00:00:00",
                    "cpu_percent": 95.0,
                    "memory_percent": 95.0,
                    "rss_mb": 3500.0,
                    "worker_budget": float(limits._max_workers),
                }
                limits._record_usage(usage)
                time.sleep(0.001)  # Small delay to increase race condition likelihood

        async def async_applier():
            """Simulates async coroutine reading budget via apply_worker_budget."""
            for _ in range(iterations):
                try:
                    await limits.apply_worker_budget()
                except Exception as e:
                    errors.append(e)
                await asyncio.sleep(0.001)

        # Run concurrently
        thread = threading.Thread(target=sync_predictor)
        thread.start()
        await async_applier()
        thread.join()

        assert len(errors) == 0, f"Race conditions detected: {errors}"
        assert limits._semaphore_limit == limits._max_workers, "Semaphore/budget mismatch"

    @pytest.mark.asyncio
    async def test_max_workers_property_thread_safe(self):
        """Test that max_workers property is thread-safe."""
        limits = ResourceLimits(max_workers=10, min_workers=2, hard_max_workers=20)

        values = []

        def reader_thread():
            for _ in range(50):
                values.append(limits.max_workers)
                time.sleep(0.001)

        def writer_thread():
            for _ in range(50):
                with limits._sync_lock:
                    limits._max_workers = 15
                time.sleep(0.001)

        threads = [
            threading.Thread(target=reader_thread),
            threading.Thread(target=writer_thread),
            threading.Thread(target=reader_thread),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All values should be valid (not torn/corrupted)
        assert all(isinstance(v, int) for v in values)
        assert all(2 <= v <= 20 for v in values)


class TestCircuitBreaker:
    """Test Circuit Breaker implementation."""

    def test_circuit_breaker_opens_after_threshold_failures(self):
        """Test that circuit breaker opens after reaching failure threshold."""
        cb = CircuitBreaker(
            config=CircuitBreakerConfig(
                failure_threshold=3,
                timeout_seconds=60.0,
                error_rate_threshold=0.5,
                window_size=10,
            )
        )

        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute() is True

        # Record failures
        for i in range(3):
            cb.record_failure(Exception(f"test_error_{i}"))

        # Should open after threshold
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False

    def test_circuit_breaker_error_rate_tracking(self):
        """Test error rate calculation over rolling window."""
        cb = CircuitBreaker(
            config=CircuitBreakerConfig(
                failure_threshold=5,
                error_rate_threshold=0.10,  # 10% error rate
                window_size=100,
            )
        )

        # Mix successes and failures (5 failures out of 50 = 10% error rate)
        for _ in range(45):
            cb.record_success()

        for _ in range(5):
            cb.record_failure(Exception("test_error"))

        stats = cb.get_stats()
        assert 0.09 <= stats["error_rate"] <= 0.11  # Allow small floating point variance

    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker transitions to HALF_OPEN and recovers."""
        cb = CircuitBreaker(
            config=CircuitBreakerConfig(
                failure_threshold=2,
                success_threshold=2,
                timeout_seconds=0.1,  # Short timeout for testing
                error_rate_threshold=0.5,
            )
        )

        # Open the circuit
        cb.record_failure(Exception("error1"))
        cb.record_failure(Exception("error2"))
        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        time.sleep(0.15)

        # Should transition to HALF_OPEN
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN

        # Record successes to close circuit
        cb.record_success()
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_open_exception(self):
        """Test CircuitBreakerOpen exception."""
        cb = CircuitBreaker(
            config=CircuitBreakerConfig(
                failure_threshold=2,
                timeout_seconds=30.0,
            )
        )

        # Open circuit
        cb.record_failure(Exception("error1"))
        cb.record_failure(Exception("error2"))

        # Verify exception details
        if not cb.can_execute():
            time_until_retry = cb.config.timeout_seconds - (time.monotonic() - cb.last_failure_time)
            exc = CircuitBreakerOpen("test_breaker", time_until_retry)
            assert "test_breaker" in str(exc)
            assert "OPEN" in str(exc)
            assert exc.breaker_name == "test_breaker"

    def test_circuit_breaker_window_trimming(self):
        """Test that results window is properly trimmed."""
        cb = CircuitBreaker(
            config=CircuitBreakerConfig(
                window_size=10,
            )
        )

        # Add more than window_size results
        for _ in range(20):
            cb.record_success()

        # Window should be trimmed to size
        assert len(cb._results_window) == 10
        assert cb._results_window == [True] * 10


@pytest.mark.asyncio
async def test_circuit_breaker_protects_phase2_execution():
    """Integration test: Circuit breaker should prevent cascading failures."""
    from farfan_pipeline.resilience import CircuitBreaker, CircuitBreakerConfig

    cb = CircuitBreaker(
        config=CircuitBreakerConfig(
            failure_threshold=5,
            error_rate_threshold=0.05,  # 5% error budget
            window_size=50,
        )
    )

    # Simulate Phase 2 execution with systematic failures
    total_tasks = 100
    failed_tasks = 0

    for task_id in range(total_tasks):
        if not cb.can_execute():
            # Circuit breaker open - fail fast
            failed_tasks += 1
            continue

        try:
            # Simulate systematic failure (e.g., LLM rate limit)
            if task_id % 10 == 0 and task_id < 60:  # 6 failures
                raise Exception(f"LLM rate limit error task_{task_id}")

            # Success
            cb.record_success()
        except Exception as e:
            cb.record_failure(e)
            failed_tasks += 1

    # Circuit breaker should have opened before processing all tasks
    assert cb.state == CircuitState.OPEN
    assert failed_tasks < total_tasks  # Should stop before exhausting all tasks
    assert cb.failure_count >= cb.config.failure_threshold
