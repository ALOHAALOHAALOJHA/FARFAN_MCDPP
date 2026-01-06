"""
Regression tests for datetime.utcnow() deprecation fix.

Verifies all generated timestamps are timezone-aware and use UTC timezone,
preventing DeprecationWarning in Python 3.12+.
"""

import warnings
from datetime import datetime, timezone

from farfan_pipeline.phases.Phase_two.phase2_30_00_resource_manager import (
    CircuitBreaker,
    CircuitBreakerConfig,
)
from farfan_pipeline.phases.Phase_two.phase2_30_02_resource_alerts import (
    ResourceAlert,
    ResourceAlertManager,
    AlertSeverity,
)
from farfan_pipeline.phases.Phase_two.phase2_50_00_task_executor import (
    CheckpointManager,
)


class TestDatetimeTimezoneAwareness:
    """Regression tests for datetime.utcnow() deprecation fix."""

    def test_checkpoint_timestamps_are_timezone_aware(self, tmp_path):
        """Verify checkpoint timestamps are timezone-aware."""
        manager = CheckpointManager(checkpoint_dir=tmp_path)

        checkpoint_path = manager.save_checkpoint(
            plan_id="test_plan",
            completed_tasks=["task_1"]
        )

        # Read checkpoint and verify timestamp
        import json
        with open(checkpoint_path) as f:
            data = json.load(f)

        # Parse timestamp
        timestamp_str = data["timestamp"]
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        assert timestamp.tzinfo is not None
        assert timestamp.tzinfo == timezone.utc

    def test_circuit_breaker_timestamps_are_timezone_aware(self):
        """Verify circuit breaker timestamps are timezone-aware."""
        breaker = CircuitBreaker(
            executor_id="test_executor",
            config=CircuitBreakerConfig()
        )

        # Trigger a failure to set timestamp
        breaker.record_failure()

        assert breaker.last_failure_time is not None
        assert breaker.last_failure_time.tzinfo is not None
        assert breaker.last_failure_time.tzinfo == timezone.utc

    def test_circuit_breaker_state_change_timezone_aware(self):
        """Verify circuit breaker state change timestamps are timezone-aware."""
        breaker = CircuitBreaker(
            executor_id="test_executor",
            config=CircuitBreakerConfig(failure_threshold=2)
        )

        # Trigger failures to open circuit
        breaker.record_failure()
        breaker.record_failure()

        assert breaker.last_state_change is not None
        assert breaker.last_state_change.tzinfo is not None
        assert breaker.last_state_change.tzinfo == timezone.utc

    def test_timestamp_comparison_works(self):
        """Verify timezone-aware timestamps can be compared."""
        breaker = CircuitBreaker(
            executor_id="test_executor",
            config=CircuitBreakerConfig()
        )

        breaker.record_failure()
        ts1 = breaker.last_failure_time

        import time
        time.sleep(0.01)

        breaker.record_failure()
        ts2 = breaker.last_failure_time

        # Should not raise TypeError about naive/aware comparison
        assert ts2 >= ts1
        assert ts2 > ts1

    def test_no_deprecation_warnings_checkpoint(self, tmp_path):
        """Verify no deprecation warnings are emitted from CheckpointManager."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", DeprecationWarning)

            manager = CheckpointManager(checkpoint_dir=tmp_path)
            manager.save_checkpoint(
                plan_id="test_plan",
                completed_tasks=["task_1"]
            )

            datetime_warnings = [
                warning for warning in w
                if "utcnow" in str(warning.message).lower()
            ]
            assert len(datetime_warnings) == 0

    def test_no_deprecation_warnings_circuit_breaker(self):
        """Verify no deprecation warnings from CircuitBreaker."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", DeprecationWarning)

            breaker = CircuitBreaker(
                executor_id="test_executor",
                config=CircuitBreakerConfig()
            )
            breaker.record_failure()
            breaker.record_success()

            datetime_warnings = [
                warning for warning in w
                if "utcnow" in str(warning.message).lower()
            ]
            assert len(datetime_warnings) == 0

    def test_resource_alert_timestamp_timezone_aware(self):
        """Verify resource alert timestamps are timezone-aware."""
        from farfan_pipeline.phases.Phase_two.phase2_30_00_resource_manager import (
            ResourcePressureEvent,
            ResourcePressureLevel,
        )

        event = ResourcePressureEvent(
            timestamp=datetime.now(timezone.utc),
            pressure_level=ResourcePressureLevel.NORMAL,
            cpu_percent=50.0,
            memory_mb=1024.0,
            memory_percent=50.0,
            worker_count=4,
            active_executors=2,
            degradation_applied=[],
            circuit_breakers_open=[],
            message="Test event"
        )

        alert = ResourceAlert(
            severity=AlertSeverity.INFO,
            title="Test Alert",
            message="Test message",
            event=event
        )

        assert alert.timestamp.tzinfo is not None
        assert alert.timestamp.tzinfo == timezone.utc

    def test_alert_manager_rate_limiting_timezone_aware(self):
        """Verify alert manager rate limiting uses timezone-aware timestamps."""
        from farfan_pipeline.phases.Phase_two.phase2_30_00_resource_manager import (
            ResourcePressureEvent,
            ResourcePressureLevel,
        )

        manager = ResourceAlertManager()

        event = ResourcePressureEvent(
            timestamp=datetime.now(timezone.utc),
            pressure_level=ResourcePressureLevel.HIGH,
            cpu_percent=80.0,
            memory_mb=2048.0,
            memory_percent=80.0,
            worker_count=4,
            active_executors=5,
            degradation_applied=[],
            circuit_breakers_open=[],
            message="High pressure"
        )

        # Process event
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", DeprecationWarning)

            alerts = manager.process_event(event)

            datetime_warnings = [
                warning for warning in w
                if "utcnow" in str(warning.message).lower()
            ]
            assert len(datetime_warnings) == 0

    def test_all_timestamps_have_utc_timezone(self, tmp_path):
        """Comprehensive test: verify all timestamps use UTC timezone."""
        # CheckpointManager
        checkpoint_manager = CheckpointManager(checkpoint_dir=tmp_path)
        checkpoint_path = checkpoint_manager.save_checkpoint(
            plan_id="test",
            completed_tasks=["task"]
        )

        import json
        with open(checkpoint_path) as f:
            checkpoint_data = json.load(f)

        timestamp = datetime.fromisoformat(
            checkpoint_data["timestamp"].replace("Z", "+00:00")
        )
        assert timestamp.tzinfo == timezone.utc

        # CircuitBreaker
        breaker = CircuitBreaker(
            executor_id="test",
            config=CircuitBreakerConfig()
        )
        breaker.record_failure()

        assert breaker.last_failure_time.tzinfo == timezone.utc

        # Verify timestamps can be compared across components
        assert timestamp <= breaker.last_failure_time or timestamp >= breaker.last_failure_time
