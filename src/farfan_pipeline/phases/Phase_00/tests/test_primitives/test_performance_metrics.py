import pytest
import time
from farfan_pipeline.phases.Phase_00.primitives.performance_metrics import (
    PerformanceMetrics,
    timed_phase
)

def test_performance_metrics_recording():
    metrics = PerformanceMetrics()
    metrics.record_phase("phase1", 100)
    metrics.record_phase("phase2", 200)
    metrics.finalize()
    
    assert metrics.total_duration_ms == 300
    assert metrics.phase_timings["phase1"] == 100

def test_timed_phase_context():
    metrics = PerformanceMetrics()
    with timed_phase(metrics, "test_phase"):
        time.sleep(0.01) # Sleep 10ms
    
    assert "test_phase" in metrics.phase_timings
    assert metrics.phase_timings["test_phase"] > 0
