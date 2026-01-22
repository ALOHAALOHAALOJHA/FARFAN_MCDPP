"""Tests for enhanced monitoring system."""

import pytest
from datetime import datetime
from pathlib import Path

from farfan_pipeline.dashboard_atroz_.monitoring_enhanced import (
    EnhancedPipelineMonitor,
    MetricType,
    PhaseMetrics,
    PipelineExecutionSnapshot,
    get_monitor,
)


@pytest.fixture
def monitor():
    """Create a fresh monitor instance for testing."""
    return EnhancedPipelineMonitor()


def test_monitor_initialization(monitor):
    """Test that monitor initializes correctly."""
    assert monitor is not None
    assert len(monitor.active_jobs) == 0
    assert len(monitor.completed_jobs) == 0
    assert len(monitor.active_alerts) == 0


def test_start_job_monitoring(monitor):
    """Test starting job monitoring."""
    job_id = "test_job_001"
    filename = "test_plan.pdf"
    
    snapshot = monitor.start_job_monitoring(job_id, filename)
    
    assert snapshot is not None
    assert snapshot.job_id == job_id
    assert snapshot.filename == filename
    assert snapshot.status == "INITIALIZING"
    assert snapshot.started_at is not None
    assert job_id in monitor.active_jobs


def test_start_phase(monitor):
    """Test starting phase monitoring."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    
    phase_metrics = monitor.start_phase(
        job_id=job_id,
        phase_id="P00",
        phase_name="Document Assembly"
    )
    
    assert phase_metrics is not None
    assert phase_metrics.phase_id == "P00"
    assert phase_metrics.phase_name == "Document Assembly"
    assert phase_metrics.status == "RUNNING"
    assert phase_metrics.started_at is not None
    
    snapshot = monitor.get_job_snapshot(job_id)
    assert snapshot.current_phase == "P00"
    assert "P00" in snapshot.phases


def test_complete_phase(monitor):
    """Test completing a phase."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    monitor.start_phase(job_id, "P00", "Document Assembly")
    
    artifacts = ["/path/to/artifact1.json", "/path/to/artifact2.json"]
    metrics = {"items_processed": 100}
    
    phase_metrics = monitor.complete_phase(
        job_id=job_id,
        phase_id="P00",
        artifacts=artifacts,
        metrics=metrics
    )
    
    assert phase_metrics is not None
    assert phase_metrics.status == "COMPLETED"
    assert phase_metrics.completed_at is not None
    assert phase_metrics.execution_time_ms > 0
    assert len(phase_metrics.artifacts_produced) == 2
    assert phase_metrics.custom_metrics["items_processed"] == 100
    
    snapshot = monitor.get_job_snapshot(job_id)
    assert "P00" in snapshot.completed_phases
    assert snapshot.total_artifacts == 2


def test_fail_phase(monitor):
    """Test failing a phase."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    monitor.start_phase(job_id, "P00", "Document Assembly")
    
    error = "File not found"
    error_details = {"file": "/missing/file.pdf"}
    
    phase_metrics = monitor.fail_phase(
        job_id=job_id,
        phase_id="P00",
        error=error,
        error_details=error_details
    )
    
    assert phase_metrics is not None
    assert phase_metrics.status == "FAILED"
    assert len(phase_metrics.errors) == 1
    assert phase_metrics.errors[0]["message"] == error
    
    snapshot = monitor.get_job_snapshot(job_id)
    assert "P00" in snapshot.failed_phases
    assert snapshot.status == "FAILED"
    assert snapshot.total_errors == 1
    
    # Check alert was generated
    alerts = monitor.get_active_alerts()
    assert len(alerts) > 0
    assert any(a["type"] == "PHASE_FAILURE" for a in alerts)


def test_record_sub_phase(monitor):
    """Test recording sub-phase metrics."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    monitor.start_phase(job_id, "P00", "Document Assembly")
    
    sub_phase_name = "PDF Validation"
    metrics = {
        "pages_validated": 50,
        "errors_found": 2
    }
    
    monitor.record_sub_phase(job_id, "P00", sub_phase_name, metrics)
    
    phase_metrics = monitor.get_phase_metrics(job_id, "P00")
    assert sub_phase_name in phase_metrics.sub_phases
    assert phase_metrics.sub_phases[sub_phase_name]["metrics"] == metrics


def test_record_resource_usage(monitor):
    """Test recording resource usage."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    monitor.start_phase(job_id, "P00", "Document Assembly")
    
    monitor.record_resource_usage(
        job_id=job_id,
        cpu_percent=45.5,
        memory_mb=2048.0,
        phase_id="P00"
    )
    
    snapshot = monitor.get_job_snapshot(job_id)
    assert len(snapshot.resource_timeline) == 1
    assert snapshot.resource_timeline[0]["cpu_percent"] == 45.5
    assert snapshot.resource_timeline[0]["memory_mb"] == 2048.0
    assert snapshot.total_memory_peak_mb == 2048.0
    
    # Record higher memory usage
    monitor.record_resource_usage(
        job_id=job_id,
        cpu_percent=50.0,
        memory_mb=3000.0,
        phase_id="P00"
    )
    
    snapshot = monitor.get_job_snapshot(job_id)
    assert snapshot.total_memory_peak_mb == 3000.0


def test_complete_job(monitor):
    """Test completing a job."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    monitor.start_phase(job_id, "P00", "Document Assembly")
    monitor.complete_phase(job_id, "P00")
    
    monitor.complete_job(job_id)
    
    assert job_id not in monitor.active_jobs
    assert job_id in monitor.completed_jobs
    
    snapshot = monitor.get_job_snapshot(job_id)
    assert snapshot.status == "COMPLETED"
    assert snapshot.completed_at is not None
    assert snapshot.total_execution_time_ms > 0
    assert snapshot.progress_percent == 100


def test_get_phase_history(monitor):
    """Test getting phase history."""
    # Execute same phase multiple times
    for i in range(5):
        job_id = f"test_job_{i:03d}"
        monitor.start_job_monitoring(job_id, f"test_{i}.pdf")
        monitor.start_phase(job_id, "P00", "Document Assembly")
        monitor.complete_phase(job_id, "P00")
    
    history = monitor.get_phase_history("P00", limit=10)
    assert len(history) == 5
    assert all(isinstance(m, PhaseMetrics) for m in history)
    assert all(m.phase_id == "P00" for m in history)


def test_get_performance_trends(monitor):
    """Test getting performance trends."""
    # Execute phase multiple times with varying execution times
    for i in range(3):
        job_id = f"test_job_{i:03d}"
        monitor.start_job_monitoring(job_id, f"test_{i}.pdf")
        monitor.start_phase(job_id, "P00", "Document Assembly")
        monitor.complete_phase(job_id, "P00")
    
    trends = monitor.get_performance_trends("P00", MetricType.EXECUTION_TIME)
    
    assert trends["phase_id"] == "P00"
    assert trends["metric_type"] == "execution_time"
    assert trends["count"] == 3
    assert trends["avg"] > 0
    assert trends["min"] > 0
    assert trends["max"] > 0
    assert len(trends["trend"]) == 3


def test_alert_generation_slow_phase(monitor):
    """Test alert generation for slow phases."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    
    # Set low threshold for testing
    monitor.alert_thresholds["execution_time_ms"] = 100
    
    phase_metrics = monitor.start_phase(job_id, "P00", "Document Assembly")
    
    # Artificially set high execution time
    phase_metrics.execution_time_ms = 500
    
    monitor.complete_phase(job_id, "P00")
    
    alerts = monitor.get_active_alerts()
    assert len(alerts) > 0
    assert any(a["type"] == "SLOW_PHASE" for a in alerts)


def test_acknowledge_alert(monitor):
    """Test acknowledging alerts."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    monitor.start_phase(job_id, "P00", "Document Assembly")
    monitor.fail_phase(job_id, "P00", "Test error")
    
    alerts = monitor.get_active_alerts()
    assert len(alerts) > 0
    
    alert_id = alerts[0]["id"]
    monitor.acknowledge_alert(alert_id)
    
    alerts = monitor.get_active_alerts()
    acknowledged_alert = next(a for a in alerts if a["id"] == alert_id)
    assert acknowledged_alert["acknowledged"] is True


def test_clear_acknowledged_alerts(monitor):
    """Test clearing acknowledged alerts."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    monitor.start_phase(job_id, "P00", "Document Assembly")
    monitor.fail_phase(job_id, "P00", "Test error 1")
    monitor.fail_phase(job_id, "P00", "Test error 2")
    
    alerts = monitor.get_active_alerts()
    initial_count = len(alerts)
    assert initial_count >= 2
    
    # Acknowledge first alert
    monitor.acknowledge_alert(alerts[0]["id"])
    
    # Clear acknowledged
    monitor.clear_acknowledged_alerts()
    
    remaining_alerts = monitor.get_active_alerts()
    assert len(remaining_alerts) == initial_count - 1


def test_export_snapshot(monitor):
    """Test exporting snapshot as dictionary."""
    job_id = "test_job_001"
    filename = "test_plan.pdf"
    
    monitor.start_job_monitoring(job_id, filename)
    monitor.start_phase(job_id, "P00", "Document Assembly")
    monitor.record_resource_usage(job_id, 50.0, 2048.0, "P00")
    monitor.complete_phase(job_id, "P00", artifacts=["/test/artifact.json"])
    monitor.complete_job(job_id)
    
    exported = monitor.export_snapshot(job_id)
    
    assert exported is not None
    assert exported["job_id"] == job_id
    assert exported["filename"] == filename
    assert exported["status"] == "COMPLETED"
    assert "P00" in exported["phases"]
    assert len(exported["resource_timeline"]) == 1
    assert exported["total_artifacts"] == 1
    
    # Check phase export
    phase_data = exported["phases"]["P00"]
    assert phase_data["phase_id"] == "P00"
    assert phase_data["status"] == "COMPLETED"
    assert phase_data["execution_time_ms"] > 0


def test_get_monitor_singleton():
    """Test that get_monitor returns singleton instance."""
    monitor1 = get_monitor()
    monitor2 = get_monitor()
    
    assert monitor1 is monitor2


def test_multiple_phases_in_sequence(monitor):
    """Test monitoring multiple phases in sequence."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    
    phases = [
        ("P00", "Document Assembly"),
        ("P01", "Text Extraction"),
        ("P02", "Semantic Enrichment"),
    ]
    
    for phase_id, phase_name in phases:
        monitor.start_phase(job_id, phase_id, phase_name)
        monitor.complete_phase(job_id, phase_id, artifacts=[f"/{phase_id}/output.json"])
    
    snapshot = monitor.get_job_snapshot(job_id)
    assert len(snapshot.phases) == 3
    assert len(snapshot.completed_phases) == 3
    assert snapshot.total_artifacts == 3
    
    for phase_id, _ in phases:
        assert phase_id in snapshot.phases
        assert snapshot.phases[phase_id].status == "COMPLETED"


def test_error_and_warning_tracking(monitor):
    """Test that errors and warnings are tracked correctly."""
    job_id = "test_job_001"
    monitor.start_job_monitoring(job_id, "test.pdf")
    monitor.start_phase(job_id, "P00", "Document Assembly")
    
    # Add errors
    phase_metrics = monitor.get_phase_metrics(job_id, "P00")
    phase_metrics.errors.append({
        "message": "Error 1",
        "timestamp": datetime.now().isoformat()
    })
    phase_metrics.warnings.append({
        "message": "Warning 1",
        "timestamp": datetime.now().isoformat()
    })
    
    assert len(phase_metrics.errors) == 1
    assert len(phase_metrics.warnings) == 1
    
    # Complete phase
    monitor.complete_phase(job_id, "P00")
    
    # Export and verify
    exported = monitor.export_snapshot(job_id)
    assert len(exported["phases"]["P00"]["errors"]) == 1
    assert len(exported["phases"]["P00"]["warnings"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
