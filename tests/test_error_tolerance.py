"""Unit tests for error tolerance and partial result handling.

Tests verify:
1. Threshold computation and classification
2. Per-phase error tracking
3. Success determination based on runtime mode
4. Manifest marking for incomplete runs
"""

from __future__ import annotations

import pytest

from canonic_phases.Phase_zero.runtime_config import RuntimeMode
from orchestration.orchestrator import ErrorTolerance


class TestErrorToleranceThresholds:
    """Test error tolerance threshold computation."""
    
    def test_empty_tracker_has_zero_failure_rate(self) -> None:
        """Empty tracker should report 0% failure rate."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10)
        assert tracker.current_failure_rate() == 0.0
        assert not tracker.threshold_exceeded()
    
    def test_all_success_has_zero_failure_rate(self) -> None:
        """All successful questions should have 0% failure rate."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(100):
            tracker.record_success()
        
        assert tracker.successful_questions == 100
        assert tracker.failed_questions == 0
        assert tracker.current_failure_rate() == 0.0
        assert not tracker.threshold_exceeded()
    
    def test_exactly_10_percent_failure_meets_threshold(self) -> None:
        """Exactly 10% failure rate should meet threshold."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(90):
            tracker.record_success()
        for _ in range(10):
            tracker.record_failure()
        
        assert tracker.successful_questions == 90
        assert tracker.failed_questions == 10
        assert tracker.current_failure_rate() == 0.10
        assert not tracker.threshold_exceeded()
    
    def test_11_percent_failure_exceeds_threshold(self) -> None:
        """11% failure rate should exceed threshold."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(89):
            tracker.record_success()
        for _ in range(11):
            tracker.record_failure()
        
        assert tracker.successful_questions == 89
        assert tracker.failed_questions == 11
        assert tracker.current_failure_rate() == 0.11
        assert tracker.threshold_exceeded()
    
    def test_5_percent_failure_below_threshold(self) -> None:
        """5% failure rate should be below threshold."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(95):
            tracker.record_success()
        for _ in range(5):
            tracker.record_failure()
        
        assert tracker.current_failure_rate() == 0.05
        assert not tracker.threshold_exceeded()


class TestErrorToleranceSuccessClassification:
    """Test success classification based on runtime mode."""
    
    def test_production_mode_requires_threshold_compliance(self) -> None:
        """PRODUCTION mode requires failure rate <= 10%."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(85):
            tracker.record_success()
        for _ in range(15):
            tracker.record_failure()
        
        assert not tracker.can_mark_success(RuntimeMode.PRODUCTION)
        assert not tracker.can_mark_success(RuntimeMode.CI)
    
    def test_production_mode_allows_success_within_threshold(self) -> None:
        """PRODUCTION mode allows success if within threshold."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(92):
            tracker.record_success()
        for _ in range(8):
            tracker.record_failure()
        
        assert tracker.can_mark_success(RuntimeMode.PRODUCTION)
        assert tracker.can_mark_success(RuntimeMode.CI)
    
    def test_dev_mode_allows_partial_success(self) -> None:
        """DEV mode allows partial success with 50%+ success rate."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(60):
            tracker.record_success()
        for _ in range(40):
            tracker.record_failure()
        
        assert tracker.can_mark_success(RuntimeMode.DEV)
        assert tracker.can_mark_success(RuntimeMode.EXPLORATORY)
    
    def test_dev_mode_rejects_below_50_percent(self) -> None:
        """DEV mode rejects below 50% success rate."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(45):
            tracker.record_success()
        for _ in range(55):
            tracker.record_failure()
        
        assert not tracker.can_mark_success(RuntimeMode.DEV)
        assert not tracker.can_mark_success(RuntimeMode.EXPLORATORY)
    
    def test_none_runtime_mode_defaults_to_strict(self) -> None:
        """None runtime mode should default to strict (PRODUCTION-like)."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(85):
            tracker.record_success()
        for _ in range(15):
            tracker.record_failure()
        
        assert not tracker.can_mark_success(None)


class TestErrorToleranceExport:
    """Test error tolerance state export."""
    
    def test_to_dict_contains_all_fields(self) -> None:
        """to_dict should export all relevant fields."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(90):
            tracker.record_success()
        for _ in range(10):
            tracker.record_failure()
        
        result = tracker.to_dict()
        
        assert result["phase_id"] == 2
        assert result["max_failure_rate"] == 0.10
        assert result["total_questions"] == 100
        assert result["failed_questions"] == 10
        assert result["successful_questions"] == 90
        assert result["current_failure_rate"] == 0.10
        assert result["threshold_exceeded"] is False
    
    def test_to_dict_reflects_threshold_exceeded(self) -> None:
        """to_dict should reflect when threshold is exceeded."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=100)
        for _ in range(85):
            tracker.record_success()
        for _ in range(15):
            tracker.record_failure()
        
        result = tracker.to_dict()
        
        assert result["current_failure_rate"] == 0.15
        assert result["threshold_exceeded"] is True


class TestErrorToleranceEdgeCases:
    """Test edge cases for error tolerance."""
    
    def test_zero_questions_does_not_crash(self) -> None:
        """Zero questions should not cause division by zero."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=0)
        
        assert tracker.current_failure_rate() == 0.0
        assert not tracker.threshold_exceeded()
        assert tracker.can_mark_success(RuntimeMode.PRODUCTION)
    
    def test_single_failure_exceeds_10_percent(self) -> None:
        """Single failure should exceed 10% threshold."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=5)
        for _ in range(4):
            tracker.record_success()
        tracker.record_failure()
        
        assert tracker.current_failure_rate() == 0.20
        assert tracker.threshold_exceeded()
    
    def test_all_failures_reports_100_percent(self) -> None:
        """All failures should report 100% failure rate."""
        tracker = ErrorTolerance(phase_id=2, max_failure_rate=0.10, total_questions=50)
        for _ in range(50):
            tracker.record_failure()
        
        assert tracker.current_failure_rate() == 1.0
        assert tracker.threshold_exceeded()
        assert not tracker.can_mark_success(RuntimeMode.PRODUCTION)
        assert not tracker.can_mark_success(RuntimeMode.DEV)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
