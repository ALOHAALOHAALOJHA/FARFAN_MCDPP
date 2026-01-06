"""
Tests for shared retry/backoff abstraction.

Verifies the exponential backoff implementation with jitter, exception filtering,
and both decorator and imperative APIs.
"""

import pytest
import time

from farfan_pipeline.utils.retry import (
    RetryConfig,
    RetryPolicy,
    with_exponential_backoff,
    TransientError,
    PermanentError,
)


class TestRetryExponentialBackoff:
    """Tests for exponential backoff retry logic."""

    def test_decorator_succeeds_first_try(self):
        """Verify decorator returns immediately on success."""
        call_count = 0

        @with_exponential_backoff(max_retries=3)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_function()
        assert result == "success"
        assert call_count == 1

    def test_decorator_retries_on_exception(self):
        """Verify decorator retries on configured exceptions."""
        call_count = 0

        @with_exponential_backoff(
            max_retries=3,
            base_delay_seconds=0.01,
            retryable_exceptions=(TransientError,)
        )
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientError("Temporary failure")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    def test_decorator_respects_max_retries(self):
        """Verify decorator stops after max_retries."""
        call_count = 0

        @with_exponential_backoff(
            max_retries=2,
            base_delay_seconds=0.01,
            retryable_exceptions=(TransientError,)
        )
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise TransientError("Always fails")

        with pytest.raises(TransientError):
            always_fails()

        # Should be called: initial + 2 retries = 3 times
        assert call_count == 3

    def test_decorator_does_not_retry_non_retryable_exceptions(self):
        """Verify decorator raises immediately for non-retryable exceptions."""
        call_count = 0

        @with_exponential_backoff(
            max_retries=3,
            base_delay_seconds=0.01,
            retryable_exceptions=(TransientError,)
        )
        def raises_permanent_error():
            nonlocal call_count
            call_count += 1
            raise PermanentError("Permanent failure")

        with pytest.raises(PermanentError):
            raises_permanent_error()

        # Should only be called once
        assert call_count == 1

    def test_exponential_backoff_timing(self):
        """Verify exponential backoff delays increase correctly."""
        call_times = []

        @with_exponential_backoff(
            max_retries=3,
            base_delay_seconds=0.1,
            multiplier=2.0,
            jitter_factor=0.0,  # No jitter for timing test
            retryable_exceptions=(TransientError,)
        )
        def timed_function():
            call_times.append(time.time())
            if len(call_times) < 4:
                raise TransientError("Retry needed")
            return "success"

        result = timed_function()
        assert result == "success"
        assert len(call_times) == 4

        # Verify delays: ~0.1s, ~0.2s, ~0.4s
        delays = [call_times[i + 1] - call_times[i] for i in range(len(call_times) - 1)]

        # Allow 20% tolerance for timing variations
        assert 0.08 <= delays[0] <= 0.15
        assert 0.16 <= delays[1] <= 0.25
        assert 0.32 <= delays[2] <= 0.50

    def test_max_delay_cap(self):
        """Verify delays are capped at max_delay."""
        call_times = []

        @with_exponential_backoff(
            max_retries=5,
            base_delay_seconds=1.0,
            multiplier=10.0,
            max_delay_seconds=0.5,  # Cap at 0.5s
            jitter_factor=0.0,
            retryable_exceptions=(TransientError,)
        )
        def capped_function():
            call_times.append(time.time())
            if len(call_times) < 6:
                raise TransientError("Retry needed")
            return "success"

        result = capped_function()
        assert result == "success"

        delays = [call_times[i + 1] - call_times[i] for i in range(len(call_times) - 1)]

        # All delays should be <= max_delay (0.5s) + tolerance
        for delay in delays:
            assert delay <= 0.6

    def test_on_retry_callback(self):
        """Verify on_retry callback is invoked."""
        retry_events = []

        def capture_retry(exception, attempt, delay_ms):
            retry_events.append((str(exception), attempt, delay_ms))

        @with_exponential_backoff(
            max_retries=3,
            base_delay_seconds=0.01,
            retryable_exceptions=(TransientError,),
            on_retry=capture_retry
        )
        def callback_function():
            if len(retry_events) < 2:
                raise TransientError("Retry needed")
            return "success"

        result = callback_function()
        assert result == "success"
        assert len(retry_events) == 2
        assert retry_events[0][1] == 1  # First retry
        assert retry_events[1][1] == 2  # Second retry
        assert isinstance(retry_events[0][2], float)

    def test_retry_policy_imperative_api(self):
        """Verify RetryPolicy imperative API works correctly."""
        call_count = 0
        result = None
        policy = RetryPolicy(max_retries=3, base_delay_seconds=0.01)

        for attempt in policy.attempts():
            call_count += 1
            try:
                if call_count < 3:
                    raise TransientError("Retry needed")
                result = "success"
                attempt.mark_success()
                break
            except TransientError as e:
                attempt.retry_on(e)

        assert result == "success"
        assert call_count == 3
        assert policy.config.successful_chunks == 1
        assert policy.config.total_retries == 2

    def test_retry_policy_max_retries_exceeded(self):
        """Verify RetryPolicy raises after max retries."""
        policy = RetryPolicy(
            max_retries=2,
            base_delay_seconds=0.01,
            retryable_exceptions=(TransientError,)
        )

        with pytest.raises(TransientError):
            for attempt in policy.attempts():
                try:
                    raise TransientError("Always fails")
                except TransientError as e:
                    attempt.retry_on(e)

    def test_retry_config_object(self):
        """Verify RetryConfig can be used to configure policies."""
        config = RetryConfig(
            max_retries=2,
            base_delay_seconds=0.5,
            multiplier=3.0,
            max_delay_seconds=10.0,
            jitter_factor=0.2,
            retryable_exceptions=(ValueError, KeyError)
        )

        assert config.max_retries == 2
        assert config.base_delay_seconds == 0.5
        assert config.multiplier == 3.0
        assert config.max_delay_seconds == 10.0
        assert config.jitter_factor == 0.2
        assert config.retryable_exceptions == (ValueError, KeyError)

    def test_multiple_exception_types(self):
        """Verify retry handles multiple exception types."""
        call_count = 0

        @with_exponential_backoff(
            max_retries=3,
            base_delay_seconds=0.01,
            retryable_exceptions=(TransientError, ValueError, KeyError)
        )
        def multi_exception_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TransientError("First error")
            elif call_count == 2:
                raise ValueError("Second error")
            elif call_count == 3:
                raise KeyError("Third error")
            return "success"

        result = multi_exception_function()
        assert result == "success"
        assert call_count == 4

    def test_jitter_adds_randomness(self):
        """Verify jitter adds randomness to delays within expected range."""
        delays = []
        base_delay = 0.1
        jitter = 0.5

        for _ in range(5):
            call_times = []

            @with_exponential_backoff(
                max_retries=1,
                base_delay_seconds=base_delay,
                multiplier=1.0,
                jitter_factor=jitter,
                retryable_exceptions=(TransientError,)
            )
            def jittered_function():
                call_times.append(time.perf_counter())
                if len(call_times) == 1:
                    raise TransientError("Retry once")
                return "success"

            jittered_function()
            delays.append(call_times[1] - call_times[0])

        # Delays should vary (not all identical)
        assert len(set(delays)) > 1
        # All delays should be within [base_delay, base_delay * (1 + jitter) + tolerance]
        for delay in delays:
            # 0.02s tolerance for execution overhead
            assert base_delay <= delay <= base_delay * (1 + jitter) + 0.05

    def test_metrics_tracking(self):
        """Verify metrics are correctly tracked in RetryConfig."""
        config = RetryConfig(max_retries=3, base_delay_seconds=0.01)

        @with_exponential_backoff(config=config)
        def partially_flaky(fail=False):
            if fail:
                raise TransientError("Failed")
            return "ok"

        # Success first try
        partially_flaky(fail=False)
        assert config.total_chunks == 1
        assert config.successful_chunks == 1
        assert config.total_retries == 0

        # Success after retries
        call_count = 0
        @with_exponential_backoff(config=config)
        def flaky_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientError("Try again")
            return "ok"
        
        flaky_then_success()
        assert config.total_chunks == 2
        assert config.successful_chunks == 2
        assert config.total_retries == 2

        # Permanent failure
        @with_exponential_backoff(config=config)
        def always_fails():
            raise TransientError("Fatal")
        
        with pytest.raises(TransientError):
            always_fails()
        
        assert config.total_chunks == 3
        assert config.successful_chunks == 2
        assert config.failed_chunks == 1
        assert config.total_retries == 5 # 2 from previous test + 3 from always_fails

    def test_decorator_preserves_function_metadata(self):
        """Verify decorator preserves original function metadata."""
        @with_exponential_backoff(max_retries=3)
        def documented_function():
            """This is a documented function."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert "documented function" in documented_function.__doc__