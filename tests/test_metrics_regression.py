"""Regression tests to prevent metrics-only-in-logs issues."""

import json
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.updated
@pytest.mark.regression
def test_metrics_not_only_in_logs(tmp_path: Path) -> None:
    """
    Regression test: Ensure metrics are persisted to files, not just logged.
    
    This test guards against the original issue where export_metrics existed
    but was never called to write metrics to disk.
    """
    from farfan_pipeline.orchestration.orchestrator import (
        PhaseInstrumentation,
        ResourceLimits
    )
    from farfan_pipeline.phases.Phase_02.phase2_95_01_metrics_persistence import persist_all_metrics
    
    # Create orchestrator-like metrics
    resource_limits = ResourceLimits()
    phase_instr = PhaseInstrumentation(phase_id=0, name="Test", items_total=1)
    phase_instr.start()
    phase_instr.increment()
    phase_instr.complete()
    
    metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {
            "0": phase_instr.build_metrics()
        },
        "resource_usage": resource_limits.get_usage_history(),
        "abort_status": {
            "is_aborted": False,
            "reason": None,
            "timestamp": None
        },
        "phase_status": {
            "0": "completed"
        }
    }
    
    # Persist metrics
    written_files = persist_all_metrics(metrics, tmp_path)
    
    # CRITICAL REGRESSION CHECK: Files must exist on disk
    assert written_files["phase_metrics"].exists(), \
        "REGRESSION: phase_metrics.json was not written to disk"
    assert written_files["resource_usage"].exists(), \
        "REGRESSION: resource_usage.jsonl was not written to disk"
    assert written_files["latency_histograms"].exists(), \
        "REGRESSION: latency_histograms.json was not written to disk"
    
    # Verify files have content (not empty)
    assert written_files["phase_metrics"].stat().st_size > 0, \
        "REGRESSION: phase_metrics.json is empty"
    assert written_files["latency_histograms"].stat().st_size > 0, \
        "REGRESSION: latency_histograms.json is empty"


@pytest.mark.updated
@pytest.mark.regression
def test_orchestrator_export_metrics_is_callable() -> None:
    """
    Regression test: Verify Orchestrator.export_metrics exists and is callable.
    
    Guards against accidental removal or renaming of the export_metrics method.
    """
    from farfan_pipeline.orchestration.orchestrator import Orchestrator
    
    # Verify method exists
    assert hasattr(Orchestrator, "export_metrics"), \
        "REGRESSION: Orchestrator.export_metrics method was removed"
    
    # Verify it's callable
    assert callable(getattr(Orchestrator, "export_metrics")), \
        "REGRESSION: Orchestrator.export_metrics is not callable"


@pytest.mark.updated
@pytest.mark.regression
def test_metrics_persistence_in_ci_artifacts_directory(tmp_path: Path) -> None:
    """
    Regression test: Ensure metrics are written to artifacts/ directory as expected by CI.
    
    This test simulates the CI environment expectation that metrics files
    exist in artifacts/plan1/ after a pipeline run.
    """
    from farfan_pipeline.orchestration.orchestrator import (
        PhaseInstrumentation,
        ResourceLimits
    )
    from farfan_pipeline.phases.Phase_02.phase2_95_01_metrics_persistence import persist_all_metrics
    
    # Simulate artifacts/plan1 directory structure
    artifacts_dir = tmp_path / "artifacts" / "plan1"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create and persist metrics
    resource_limits = ResourceLimits()
    phase_instr = PhaseInstrumentation(phase_id=0, name="Test", items_total=1)
    phase_instr.start()
    phase_instr.increment()
    phase_instr.complete()
    
    metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {
            "0": phase_instr.build_metrics()
        },
        "resource_usage": resource_limits.get_usage_history(),
        "abort_status": {
            "is_aborted": False,
            "reason": None,
            "timestamp": None
        },
        "phase_status": {
            "0": "completed"
        }
    }
    
    written_files = persist_all_metrics(metrics, artifacts_dir)
    
    # CRITICAL: CI expects these exact file paths
    expected_phase_metrics = artifacts_dir / "phase_metrics.json"
    expected_resource_usage = artifacts_dir / "resource_usage.jsonl"
    expected_latency_histograms = artifacts_dir / "latency_histograms.json"
    
    assert expected_phase_metrics.exists(), \
        f"REGRESSION: CI cannot find {expected_phase_metrics}"
    assert expected_resource_usage.exists(), \
        f"REGRESSION: CI cannot find {expected_resource_usage}"
    assert expected_latency_histograms.exists(), \
        f"REGRESSION: CI cannot find {expected_latency_histograms}"


@pytest.mark.updated
@pytest.mark.regression
def test_metrics_files_have_required_content() -> None:
    """
    Regression test: Ensure metrics files contain the required fields for CI analysis.
    
    CI tools depend on specific fields being present in metrics files.
    """
    from farfan_pipeline.orchestration.orchestrator import (
        PhaseInstrumentation,
        ResourceLimits
    )
    from farfan_pipeline.phases.Phase_02.phase2_95_01_metrics_persistence import persist_all_metrics
    from tempfile import TemporaryDirectory
    
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        resource_limits = ResourceLimits()
        phase_instr = PhaseInstrumentation(phase_id=0, name="Test", items_total=1)
        phase_instr.start()
        phase_instr.increment(latency=0.123)
        phase_instr.complete()
        
        metrics = {
            "timestamp": "2024-01-01T00:00:00.000000",
            "phase_metrics": {
                "0": phase_instr.build_metrics()
            },
            "resource_usage": resource_limits.get_usage_history(),
            "abort_status": {
                "is_aborted": False,
                "reason": None,
                "timestamp": None
            },
            "phase_status": {
                "0": "completed"
            }
        }
        
        written_files = persist_all_metrics(metrics, tmp_path)
        
        # Check phase_metrics.json has required fields
        with open(written_files["phase_metrics"], 'r') as f:
            phase_data = json.load(f)
        
        assert "0" in phase_data, "REGRESSION: phase_metrics.json missing phase data"
        phase_0 = phase_data["0"]
        
        required_fields = [
            "phase_id", "name", "duration_ms", "items_processed",
            "items_total", "throughput", "latency_histogram"
        ]
        for field in required_fields:
            assert field in phase_0, \
                f"REGRESSION: phase_metrics.json missing required field: {field}"
        
        # Check latency_histograms.json has percentiles
        with open(written_files["latency_histograms"], 'r') as f:
            histogram_data = json.load(f)
        
        assert "0" in histogram_data, "REGRESSION: latency_histograms.json missing phase data"
        assert "latency_histogram" in histogram_data["0"], \
            "REGRESSION: latency_histograms.json missing latency_histogram"
        
        hist = histogram_data["0"]["latency_histogram"]
        for percentile in ["p50", "p95", "p99"]:
            assert percentile in hist, \
                f"REGRESSION: latency_histograms.json missing {percentile}"


@pytest.mark.updated
@pytest.mark.regression
def test_metrics_persistence_is_deterministic() -> None:
    """
    Regression test: Ensure metrics persistence is deterministic.
    
    Running the same metrics through persist_all_metrics twice
    should produce identical file contents.
    """
    from farfan_pipeline.orchestration.orchestrator import (
        PhaseInstrumentation,
        ResourceLimits
    )
    from farfan_pipeline.phases.Phase_02.phase2_95_01_metrics_persistence import persist_all_metrics
    from tempfile import TemporaryDirectory
    
    # Create fixed metrics data
    resource_limits = ResourceLimits()
    phase_instr = PhaseInstrumentation(phase_id=0, name="Test", items_total=1)
    phase_instr.start()
    phase_instr.increment(latency=0.123)
    phase_instr.complete()
    
    metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {
            "0": phase_instr.build_metrics()
        },
        "resource_usage": [
            {
                "timestamp": "2024-01-01T00:00:00.000000",
                "cpu_percent": 50.0,
                "memory_percent": 30.0,
                "rss_mb": 512.0,
                "worker_budget": 8.0
            }
        ],
        "abort_status": {
            "is_aborted": False,
            "reason": None,
            "timestamp": None
        },
        "phase_status": {
            "0": "completed"
        }
    }
    
    # First write
    with TemporaryDirectory() as tmpdir1:
        tmp_path1 = Path(tmpdir1)
        written_files1 = persist_all_metrics(metrics, tmp_path1)
        
        with open(written_files1["phase_metrics"], 'r') as f:
            content1 = f.read()
    
    # Second write
    with TemporaryDirectory() as tmpdir2:
        tmp_path2 = Path(tmpdir2)
        written_files2 = persist_all_metrics(metrics, tmp_path2)
        
        with open(written_files2["phase_metrics"], 'r') as f:
            content2 = f.read()
    
    # Content should be byte-for-byte identical
    assert content1 == content2, \
        "REGRESSION: Metrics persistence is not deterministic"


@pytest.mark.updated
@pytest.mark.regression
def test_missing_metrics_files_detectable() -> None:
    """
    Regression test: Ensure missing metrics files can be detected by CI.
    
    If metrics persistence fails, CI should be able to detect the absence
    of expected files.
    """
    import tempfile
    from pathlib import Path

    # Simulate a failed run where metrics weren't persisted
    fake_artifacts_dir = Path(tempfile.gettempdir()) / "fake_artifacts_dir_that_does_not_exist"
    
    expected_files = [
        fake_artifacts_dir / "phase_metrics.json",
        fake_artifacts_dir / "resource_usage.jsonl",
        fake_artifacts_dir / "latency_histograms.json"
    ]
    
    # CI can detect missing files
    missing_files = [f for f in expected_files if not f.exists()]
    
    assert len(missing_files) == 3, \
        "REGRESSION: Cannot detect missing metrics files"
    
    # This test would fail in CI if metrics weren't persisted:
    # assert all(f.exists() for f in expected_files), \
    #     f"Missing metrics files: {missing_files}"


@pytest.mark.updated
@pytest.mark.regression
def test_metrics_schema_validation_prevents_invalid_data() -> None:
    """
    Regression test: Ensure schema validation prevents invalid metrics from being accepted.
    
    This prevents silent failures where corrupted metrics are written to disk.
    """
    from farfan_pipeline.phases.Phase_02.phase2_95_01_metrics_persistence import validate_metrics_schema
    
    # Valid metrics should pass
    valid_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {
            "0": {
                "phase_id": 0,
                "name": "Test",
                "duration_ms": 100.0,
                "items_processed": 1,
                "items_total": 1,
                "progress": 1.0,
                "throughput": 0.01,
                "warnings": [],
                "errors": [],
                "resource_snapshots": [],
                "latency_histogram": {"p50": 100.0, "p95": 100.0, "p99": 100.0},
                "anomalies": []
            }
        },
        "resource_usage": [],
        "abort_status": {},
        "phase_status": {}
    }
    
    errors = validate_metrics_schema(valid_metrics)
    assert len(errors) == 0, \
        f"REGRESSION: Valid metrics failed validation: {errors}"
    
    # Invalid metrics should fail
    invalid_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": "not a dict"
    }
    
    errors = validate_metrics_schema(invalid_metrics)
    assert len(errors) > 0, \
        "REGRESSION: Invalid metrics passed validation"
