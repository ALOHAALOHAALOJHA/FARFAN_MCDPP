import pytest
from farfan_core.farfan_core.core.performance_metrics import (
    PerformanceMetrics,
    timed_phase,
    PhaseTimer,
)


class TestPhaseTimer:
    def test_timer_records_positive_duration(self) -> None:
        timer = PhaseTimer(phase_id="test")
        # Introduce measurable delay
        _ = sum(range(10000))
        duration = timer.stop()
        assert duration >= 0
        assert timer.end_time_ns is not None

    def test_timer_raises_if_duration_accessed_before_stop(self) -> None:
        timer = PhaseTimer(phase_id="test")
        with pytest.raises(ValueError, match="not stopped"):
            _ = timer.duration_ms


class TestPerformanceMetrics:
    def test_finalize_computes_total(self) -> None:
        metrics = PerformanceMetrics()
        metrics.record_phase("P0.0", 100)
        metrics.record_phase("P0.1", 200)
        metrics.finalize()
        assert metrics.total_duration_ms == 300

    def test_to_dict_schema(self) -> None:
        metrics = PerformanceMetrics()
        metrics.record_phase("P0.0", 50)
        metrics.finalize()
        result = metrics.to_dict()
        assert "total_duration_ms" in result
        assert "phase_breakdown" in result
        assert result["phase_breakdown"]["P0.0"] == 50


class TestTimedPhaseContextManager:
    def test_context_manager_records_timing(self) -> None:
        metrics = PerformanceMetrics()
        with timed_phase(metrics, "test_phase"):
            _ = sum(range(1000))
        assert "test_phase" in metrics.phase_timings
        assert metrics.phase_timings["test_phase"] >= 0
