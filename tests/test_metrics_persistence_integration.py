"""Integration tests for orchestrator metrics persistence."""

import json
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import Mock, MagicMock


@pytest.mark.updated
@pytest.mark.integration
def test_metrics_persistence_integration(tmp_path: Path) -> None:
    """Test end-to-end metrics persistence from orchestrator to files."""
    from farfan_pipeline.orchestration.core_orchestrator import (
        Orchestrator,
        PhaseInstrumentation,
        ResourceLimits,
    )
    from farfan_pipeline.orchestration.metrics_persistence import persist_all_metrics

    # Create a mock orchestrator with instrumentation
    orchestrator = Mock(spec=Orchestrator)

    # Create real ResourceLimits and PhaseInstrumentation
    resource_limits = ResourceLimits(max_memory_mb=2048.0, max_cpu_percent=80.0, max_workers=16)

    # Record some usage
    resource_limits.get_resource_usage()
    resource_limits.get_resource_usage()

    # Create phase instrumentation for phase 0
    phase0_instr = PhaseInstrumentation(
        phase_id=0, name="Configuration", items_total=1, resource_limits=resource_limits
    )
    phase0_instr.start()
    phase0_instr.increment(latency=0.123)
    phase0_instr.complete()

    # Create phase instrumentation for phase 1
    phase1_instr = PhaseInstrumentation(
        phase_id=1, name="Ingestion", items_total=1, resource_limits=resource_limits
    )
    phase1_instr.start()
    phase1_instr.increment(latency=0.456)
    phase1_instr.complete()

    # Mock export_metrics to return realistic data
    def mock_export_metrics() -> dict[str, Any]:
        return {
            "timestamp": "2024-01-01T00:00:00.000000",
            "phase_metrics": {"0": phase0_instr.build_metrics(), "1": phase1_instr.build_metrics()},
            "resource_usage": resource_limits.get_usage_history(),
            "abort_status": {"is_aborted": False, "reason": None, "timestamp": None},
            "phase_status": {"0": "completed", "1": "completed"},
        }

    orchestrator.export_metrics = mock_export_metrics

    # Export and persist metrics
    metrics = orchestrator.export_metrics()
    written_files = persist_all_metrics(metrics, tmp_path)

    # Verify all expected files were created
    assert "phase_metrics" in written_files
    assert "resource_usage" in written_files
    assert "latency_histograms" in written_files

    # Verify phase_metrics.json content
    with open(written_files["phase_metrics"], "r") as f:
        phase_metrics = json.load(f)

    assert "0" in phase_metrics
    assert "1" in phase_metrics
    assert phase_metrics["0"]["phase_id"] == 0
    assert phase_metrics["0"]["name"] == "Configuration"
    assert phase_metrics["1"]["phase_id"] == 1
    assert phase_metrics["1"]["name"] == "Ingestion"
    assert phase_metrics["0"]["items_processed"] == 1
    assert phase_metrics["1"]["items_processed"] == 1

    # Verify resource_usage.jsonl content
    with open(written_files["resource_usage"], "r") as f:
        usage_lines = f.readlines()

    assert len(usage_lines) >= 2
    for line in usage_lines:
        entry = json.loads(line)
        assert "timestamp" in entry
        assert "cpu_percent" in entry
        assert "memory_percent" in entry
        assert "rss_mb" in entry
        assert "worker_budget" in entry

    # Verify latency_histograms.json content
    with open(written_files["latency_histograms"], "r") as f:
        histograms = json.load(f)

    assert "0" in histograms
    assert "1" in histograms
    assert histograms["0"]["name"] == "Configuration"
    assert histograms["1"]["name"] == "Ingestion"
    assert "latency_histogram" in histograms["0"]
    assert "latency_histogram" in histograms["1"]


@pytest.mark.updated
@pytest.mark.integration
def test_metrics_match_in_memory_structures(tmp_path: Path) -> None:
    """Test that persisted metrics match in-memory structures."""
    from farfan_pipeline.orchestration.core_orchestrator import PhaseInstrumentation, ResourceLimits
    from farfan_pipeline.orchestration.metrics_persistence import persist_all_metrics

    # Create instrumentation with specific data
    resource_limits = ResourceLimits(max_memory_mb=1024.0, max_workers=8)

    phase_instr = PhaseInstrumentation(
        phase_id=2, name="Micro Questions", items_total=300, resource_limits=resource_limits
    )

    phase_instr.start()
    for i in range(10):
        phase_instr.increment(latency=0.1 + i * 0.01)
    phase_instr.complete()

    # Build in-memory metrics
    in_memory_metrics = phase_instr.build_metrics()

    # Create full metrics structure
    full_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {"2": in_memory_metrics},
        "resource_usage": resource_limits.get_usage_history(),
        "abort_status": {"is_aborted": False, "reason": None, "timestamp": None},
        "phase_status": {"2": "completed"},
    }

    # Persist metrics
    written_files = persist_all_metrics(full_metrics, tmp_path)

    # Read back phase metrics
    with open(written_files["phase_metrics"], "r") as f:
        persisted_metrics = json.load(f)

    # Compare in-memory vs persisted
    assert persisted_metrics["2"]["phase_id"] == in_memory_metrics["phase_id"]
    assert persisted_metrics["2"]["name"] == in_memory_metrics["name"]
    assert persisted_metrics["2"]["items_processed"] == in_memory_metrics["items_processed"]
    assert persisted_metrics["2"]["items_total"] == in_memory_metrics["items_total"]
    assert persisted_metrics["2"]["duration_ms"] == in_memory_metrics["duration_ms"]
    assert persisted_metrics["2"]["throughput"] == in_memory_metrics["throughput"]
    assert persisted_metrics["2"]["latency_histogram"] == in_memory_metrics["latency_histogram"]


@pytest.mark.updated
@pytest.mark.integration
def test_metrics_files_are_valid_json(tmp_path: Path) -> None:
    """Test that all persisted metrics files are valid JSON/JSONL."""
    from farfan_pipeline.orchestration.core_orchestrator import PhaseInstrumentation, ResourceLimits
    from farfan_pipeline.orchestration.metrics_persistence import persist_all_metrics

    # Create minimal but valid metrics
    resource_limits = ResourceLimits()
    phase_instr = PhaseInstrumentation(phase_id=0, name="Test", items_total=1)
    phase_instr.start()
    phase_instr.increment()
    phase_instr.complete()

    full_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {"0": phase_instr.build_metrics()},
        "resource_usage": resource_limits.get_usage_history(),
        "abort_status": {"is_aborted": False, "reason": None, "timestamp": None},
        "phase_status": {"0": "completed"},
    }

    written_files = persist_all_metrics(full_metrics, tmp_path)

    # Validate phase_metrics.json
    with open(written_files["phase_metrics"], "r") as f:
        try:
            json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"phase_metrics.json is not valid JSON: {e}")

    # Validate resource_usage.jsonl (each line must be valid JSON)
    with open(written_files["resource_usage"], "r") as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    pytest.fail(f"resource_usage.jsonl line {line_num} is not valid JSON: {e}")

    # Validate latency_histograms.json
    with open(written_files["latency_histograms"], "r") as f:
        try:
            json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"latency_histograms.json is not valid JSON: {e}")


@pytest.mark.updated
@pytest.mark.integration
def test_metrics_persistence_handles_multiple_phases(tmp_path: Path) -> None:
    """Test metrics persistence with all 11 phases."""
    from farfan_pipeline.orchestration.core_orchestrator import PhaseInstrumentation, ResourceLimits
    from farfan_pipeline.orchestration.metrics_persistence import persist_all_metrics

    resource_limits = ResourceLimits()

    # Create instrumentation for all 11 phases
    phase_names = [
        "Configuration",
        "Ingestion",
        "Micro Questions",
        "Scoring",
        "Dimensions",
        "Policy Areas",
        "Clusters",
        "Macro",
        "Recommendations",
        "Report",
        "Export",
    ]

    phase_metrics_dict = {}
    phase_status_dict = {}

    for phase_id, phase_name in enumerate(phase_names):
        phase_instr = PhaseInstrumentation(
            phase_id=phase_id, name=phase_name, items_total=10, resource_limits=resource_limits
        )
        phase_instr.start()
        for _ in range(10):
            phase_instr.increment(latency=0.1)
        phase_instr.complete()

        phase_metrics_dict[str(phase_id)] = phase_instr.build_metrics()
        phase_status_dict[str(phase_id)] = "completed"

    full_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": phase_metrics_dict,
        "resource_usage": resource_limits.get_usage_history(),
        "abort_status": {"is_aborted": False, "reason": None, "timestamp": None},
        "phase_status": phase_status_dict,
    }

    written_files = persist_all_metrics(full_metrics, tmp_path)

    # Verify all 11 phases are in phase_metrics.json
    with open(written_files["phase_metrics"], "r") as f:
        persisted = json.load(f)

    assert len(persisted) == 11
    for i in range(11):
        assert str(i) in persisted
        assert persisted[str(i)]["phase_id"] == i
        assert persisted[str(i)]["name"] == phase_names[i]

    # Verify all 11 phases are in latency_histograms.json
    with open(written_files["latency_histograms"], "r") as f:
        histograms = json.load(f)

    assert len(histograms) == 11
    for i in range(11):
        assert str(i) in histograms
        assert histograms[str(i)]["name"] == phase_names[i]


@pytest.mark.updated
@pytest.mark.integration
def test_metrics_persistence_with_warnings_and_errors(tmp_path: Path) -> None:
    """Test that warnings and errors are properly persisted."""
    from farfan_pipeline.orchestration.core_orchestrator import PhaseInstrumentation, ResourceLimits
    from farfan_pipeline.orchestration.metrics_persistence import persist_all_metrics

    resource_limits = ResourceLimits()
    phase_instr = PhaseInstrumentation(
        phase_id=0, name="Test Phase", items_total=1, resource_limits=resource_limits
    )

    phase_instr.start()
    phase_instr.record_warning("integrity", "Test warning message", extra_field="value")
    phase_instr.record_error("execution", "Test error message", error_code=500)
    phase_instr.increment()
    phase_instr.complete()

    full_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {"0": phase_instr.build_metrics()},
        "resource_usage": resource_limits.get_usage_history(),
        "abort_status": {"is_aborted": False, "reason": None, "timestamp": None},
        "phase_status": {"0": "completed"},
    }

    written_files = persist_all_metrics(full_metrics, tmp_path)

    with open(written_files["phase_metrics"], "r") as f:
        persisted = json.load(f)

    assert len(persisted["0"]["warnings"]) == 1
    assert persisted["0"]["warnings"][0]["category"] == "integrity"
    assert persisted["0"]["warnings"][0]["message"] == "Test warning message"
    assert persisted["0"]["warnings"][0]["extra_field"] == "value"

    assert len(persisted["0"]["errors"]) == 1
    assert persisted["0"]["errors"][0]["category"] == "execution"
    assert persisted["0"]["errors"][0]["message"] == "Test error message"
    assert persisted["0"]["errors"][0]["error_code"] == 500
