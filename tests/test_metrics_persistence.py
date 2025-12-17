"""Unit tests for metrics persistence functionality."""

import json
import pytest
from pathlib import Path
from typing import Any

from farfan_pipeline.orchestration.metrics_persistence import (
    persist_phase_metrics,
    persist_resource_usage,
    persist_latency_histograms,
    persist_all_metrics,
    validate_metrics_schema,
)


@pytest.fixture
def sample_phase_metrics() -> dict[str, Any]:
    """Sample phase metrics data."""
    return {
        "0": {
            "phase_id": 0,
            "name": "Configuration",
            "duration_ms": 123.45,
            "items_processed": 1,
            "items_total": 1,
            "progress": 1.0,
            "throughput": 0.008,
            "warnings": [],
            "errors": [],
            "resource_snapshots": [],
            "latency_histogram": {
                "p50": 120.0,
                "p95": 123.0,
                "p99": 123.45
            },
            "anomalies": []
        },
        "1": {
            "phase_id": 1,
            "name": "Ingestion",
            "duration_ms": 456.78,
            "items_processed": 1,
            "items_total": 1,
            "progress": 1.0,
            "throughput": 0.002,
            "warnings": [],
            "errors": [],
            "resource_snapshots": [],
            "latency_histogram": {
                "p50": 450.0,
                "p95": 455.0,
                "p99": 456.78
            },
            "anomalies": []
        }
    }


@pytest.fixture
def sample_resource_usage() -> list[dict[str, float]]:
    """Sample resource usage history."""
    return [
        {
            "timestamp": "2024-01-01T00:00:00.000000",
            "cpu_percent": 45.2,
            "memory_percent": 23.5,
            "rss_mb": 512.3,
            "worker_budget": 8.0
        },
        {
            "timestamp": "2024-01-01T00:00:10.000000",
            "cpu_percent": 52.1,
            "memory_percent": 25.8,
            "rss_mb": 534.1,
            "worker_budget": 8.0
        }
    ]


@pytest.fixture
def sample_full_metrics(
    sample_phase_metrics: dict[str, Any],
    sample_resource_usage: list[dict[str, float]]
) -> dict[str, Any]:
    """Sample full orchestrator metrics."""
    return {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": sample_phase_metrics,
        "resource_usage": sample_resource_usage,
        "abort_status": {
            "is_aborted": False,
            "reason": None,
            "timestamp": None
        },
        "phase_status": {
            "0": "completed",
            "1": "completed"
        }
    }


@pytest.mark.updated
def test_persist_phase_metrics(tmp_path: Path, sample_phase_metrics: dict[str, Any]) -> None:
    """Test persisting phase metrics to JSON file."""
    output_file = persist_phase_metrics(sample_phase_metrics, tmp_path)
    
    assert output_file.exists()
    assert output_file.name == "phase_metrics.json"
    
    with open(output_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    assert loaded_data == sample_phase_metrics
    assert "0" in loaded_data
    assert "1" in loaded_data
    assert loaded_data["0"]["phase_id"] == 0
    assert loaded_data["1"]["phase_id"] == 1


@pytest.mark.updated
def test_persist_phase_metrics_custom_filename(
    tmp_path: Path,
    sample_phase_metrics: dict[str, Any]
) -> None:
    """Test persisting phase metrics with custom filename."""
    custom_name = "custom_metrics.json"
    output_file = persist_phase_metrics(sample_phase_metrics, tmp_path, custom_name)
    
    assert output_file.exists()
    assert output_file.name == custom_name


@pytest.mark.updated
def test_persist_phase_metrics_invalid_data(tmp_path: Path) -> None:
    """Test that invalid data raises ValueError."""
    with pytest.raises(ValueError, match="metrics_data must be a dictionary"):
        persist_phase_metrics("not a dict", tmp_path)


@pytest.mark.updated
def test_persist_resource_usage(
    tmp_path: Path,
    sample_resource_usage: list[dict[str, float]]
) -> None:
    """Test persisting resource usage as JSONL."""
    output_file = persist_resource_usage(sample_resource_usage, tmp_path)
    
    assert output_file.exists()
    assert output_file.name == "resource_usage.jsonl"
    
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    assert len(lines) == 2
    
    entry1 = json.loads(lines[0])
    entry2 = json.loads(lines[1])
    
    assert entry1["cpu_percent"] == 45.2
    assert entry2["cpu_percent"] == 52.1
    assert entry1["timestamp"] == "2024-01-01T00:00:00.000000"


@pytest.mark.updated
def test_persist_resource_usage_invalid_data(tmp_path: Path) -> None:
    """Test that invalid data raises ValueError."""
    with pytest.raises(ValueError, match="usage_history must be a list"):
        persist_resource_usage({"not": "a list"}, tmp_path)


@pytest.mark.updated
def test_persist_latency_histograms(
    tmp_path: Path,
    sample_phase_metrics: dict[str, Any]
) -> None:
    """Test persisting latency histograms."""
    output_file = persist_latency_histograms(sample_phase_metrics, tmp_path)
    
    assert output_file.exists()
    assert output_file.name == "latency_histograms.json"
    
    with open(output_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    assert "0" in loaded_data
    assert "1" in loaded_data
    assert loaded_data["0"]["name"] == "Configuration"
    assert loaded_data["1"]["name"] == "Ingestion"
    assert loaded_data["0"]["latency_histogram"]["p50"] == 120.0
    assert loaded_data["1"]["latency_histogram"]["p99"] == 456.78


@pytest.mark.updated
def test_persist_latency_histograms_invalid_data(tmp_path: Path) -> None:
    """Test that invalid data raises ValueError."""
    with pytest.raises(ValueError, match="phase_metrics must be a dictionary"):
        persist_latency_histograms("not a dict", tmp_path)


@pytest.mark.updated
def test_persist_all_metrics(tmp_path: Path, sample_full_metrics: dict[str, Any]) -> None:
    """Test persisting all metrics at once."""
    written_files = persist_all_metrics(sample_full_metrics, tmp_path)
    
    assert "phase_metrics" in written_files
    assert "resource_usage" in written_files
    assert "latency_histograms" in written_files
    
    phase_metrics_file = written_files["phase_metrics"]
    resource_usage_file = written_files["resource_usage"]
    latency_histograms_file = written_files["latency_histograms"]
    
    assert phase_metrics_file.exists()
    assert resource_usage_file.exists()
    assert latency_histograms_file.exists()
    
    assert phase_metrics_file.name == "phase_metrics.json"
    assert resource_usage_file.name == "resource_usage.jsonl"
    assert latency_histograms_file.name == "latency_histograms.json"


@pytest.mark.updated
def test_persist_all_metrics_creates_directory(
    tmp_path: Path,
    sample_full_metrics: dict[str, Any]
) -> None:
    """Test that persist_all_metrics creates output directory if needed."""
    nested_dir = tmp_path / "nested" / "metrics"
    assert not nested_dir.exists()
    
    written_files = persist_all_metrics(sample_full_metrics, nested_dir)
    
    assert nested_dir.exists()
    assert all(f.exists() for f in written_files.values())


@pytest.mark.updated
def test_persist_all_metrics_invalid_data(tmp_path: Path) -> None:
    """Test that invalid data raises ValueError."""
    with pytest.raises(ValueError, match="orchestrator_metrics must be a dictionary"):
        persist_all_metrics("not a dict", tmp_path)


@pytest.mark.updated
def test_validate_metrics_schema_valid(sample_full_metrics: dict[str, Any]) -> None:
    """Test validation of valid metrics schema."""
    errors = validate_metrics_schema(sample_full_metrics)
    assert errors == []


@pytest.mark.updated
def test_validate_metrics_schema_missing_keys() -> None:
    """Test validation detects missing required keys."""
    invalid_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {}
    }
    
    errors = validate_metrics_schema(invalid_metrics)
    
    assert len(errors) > 0
    assert any("resource_usage" in error for error in errors)
    assert any("abort_status" in error for error in errors)
    assert any("phase_status" in error for error in errors)


@pytest.mark.updated
def test_validate_metrics_schema_invalid_types() -> None:
    """Test validation detects invalid data types."""
    invalid_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": "not a dict",
        "resource_usage": "not a list",
        "abort_status": "not a dict",
        "phase_status": {}
    }
    
    errors = validate_metrics_schema(invalid_metrics)
    
    assert len(errors) >= 3
    assert any("phase_metrics must be a dictionary" in error for error in errors)
    assert any("resource_usage must be a list" in error for error in errors)
    assert any("abort_status must be a dictionary" in error for error in errors)


@pytest.mark.updated
def test_validate_metrics_schema_missing_phase_keys() -> None:
    """Test validation detects missing keys in phase metrics."""
    invalid_metrics = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "phase_metrics": {
            "0": {
                "phase_id": 0,
                "name": "Test"
            }
        },
        "resource_usage": [],
        "abort_status": {},
        "phase_status": {}
    }
    
    errors = validate_metrics_schema(invalid_metrics)
    
    assert len(errors) > 0
    assert any("phase_metrics[0]" in error and "duration_ms" in error for error in errors)
    assert any("phase_metrics[0]" in error and "items_processed" in error for error in errors)
    assert any("phase_metrics[0]" in error and "latency_histogram" in error for error in errors)


@pytest.mark.updated
def test_persist_metrics_idempotent(tmp_path: Path, sample_full_metrics: dict[str, Any]) -> None:
    """Test that persisting metrics twice produces identical results."""
    # First write
    written_files_1 = persist_all_metrics(sample_full_metrics, tmp_path)
    
    # Read back data
    with open(written_files_1["phase_metrics"], 'r') as f:
        data_1 = json.load(f)
    
    # Second write (should overwrite)
    written_files_2 = persist_all_metrics(sample_full_metrics, tmp_path)
    
    # Read back data again
    with open(written_files_2["phase_metrics"], 'r') as f:
        data_2 = json.load(f)
    
    # Should be identical
    assert data_1 == data_2
    assert written_files_1.keys() == written_files_2.keys()


@pytest.mark.updated
def test_persist_empty_resource_usage(tmp_path: Path) -> None:
    """Test persisting empty resource usage list."""
    output_file = persist_resource_usage([], tmp_path)
    
    assert output_file.exists()
    
    with open(output_file, 'r') as f:
        content = f.read()
    
    assert content == ""


@pytest.mark.updated
def test_json_serialization_deterministic(
    tmp_path: Path,
    sample_phase_metrics: dict[str, Any]
) -> None:
    """Test that JSON serialization is deterministic (sorted keys)."""
    output_file = persist_phase_metrics(sample_phase_metrics, tmp_path)
    
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Parse and re-serialize to check key ordering
    data = json.loads(content)
    reserialized = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
    
    assert content == reserialized
