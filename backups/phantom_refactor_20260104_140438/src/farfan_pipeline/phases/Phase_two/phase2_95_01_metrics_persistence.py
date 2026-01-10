"""
Module: phase2_95_01_metrics_persistence
PHASE_LABEL: Phase 2
Sequence: H

"""

"""Metrics persistence for PhaseInstrumentation telemetry.

This module provides functions to persist Orchestrator metrics and telemetry
into artifacts/ directory for CI analysis and regression detection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def persist_phase_metrics(
    metrics_data: dict[str, Any], output_dir: Path, filename: str = "phase_metrics.json"
) -> Path:
    """Persist full PhaseInstrumentation metrics for each phase.

    Args:
        metrics_data: Dictionary containing phase_metrics from export_metrics()
        output_dir: Directory to write metrics files
        filename: Name of the output file

    Returns:
        Path to the written file

    Raises:
        ValueError: If metrics_data is invalid
        OSError: If file cannot be written
    """
    if not isinstance(metrics_data, dict):
        raise ValueError("metrics_data must be a dictionary")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2, sort_keys=True, ensure_ascii=False)

    return output_path


def persist_resource_usage(
    usage_history: list[dict[str, float]], output_dir: Path, filename: str = "resource_usage.jsonl"
) -> Path:
    """Persist ResourceLimits usage history as JSONL.

    Each line is a JSON object representing a resource usage snapshot.

    Args:
        usage_history: List of usage snapshots from ResourceLimits.get_usage_history()
        output_dir: Directory to write metrics files
        filename: Name of the output file

    Returns:
        Path to the written file

    Raises:
        ValueError: If usage_history is invalid
        OSError: If file cannot be written
    """
    if not isinstance(usage_history, list):
        raise ValueError("usage_history must be a list")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    with output_path.open("w", encoding="utf-8") as f:
        for entry in usage_history:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

    return output_path


def persist_latency_histograms(
    phase_metrics: dict[str, Any], output_dir: Path, filename: str = "latency_histograms.json"
) -> Path:
    """Extract and persist per-phase latency percentiles.

    Args:
        phase_metrics: Dictionary of phase metrics from export_metrics()['phase_metrics']
        output_dir: Directory to write metrics files
        filename: Name of the output file

    Returns:
        Path to the written file

    Raises:
        ValueError: If phase_metrics is invalid
        OSError: If file cannot be written
    """
    if not isinstance(phase_metrics, dict):
        raise ValueError("phase_metrics must be a dictionary")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    histograms = {}
    for phase_id, phase_data in phase_metrics.items():
        if isinstance(phase_data, dict) and "latency_histogram" in phase_data:
            histograms[phase_id] = {
                "name": phase_data.get("name", f"phase_{phase_id}"),
                "latency_histogram": phase_data["latency_histogram"],
                "items_processed": phase_data.get("items_processed", 0),
                "duration_ms": phase_data.get("duration_ms"),
                "throughput": phase_data.get("throughput"),
            }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(histograms, f, indent=2, sort_keys=True, ensure_ascii=False)

    return output_path


def persist_all_metrics(orchestrator_metrics: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    """Persist all orchestrator metrics to output directory.

    This is the main entry point for persisting metrics. It writes:
    - phase_metrics.json: Full PhaseInstrumentation.build_metrics() for each phase
    - resource_usage.jsonl: Serialized ResourceLimits.get_usage_history() snapshots
    - latency_histograms.json: Per-phase latency percentiles

    Args:
        orchestrator_metrics: Full metrics dict from Orchestrator.export_metrics()
        output_dir: Directory to write metrics files

    Returns:
        Dictionary mapping metric type to file path

    Raises:
        ValueError: If orchestrator_metrics is invalid
        OSError: If files cannot be written
    """
    if not isinstance(orchestrator_metrics, dict):
        raise ValueError("orchestrator_metrics must be a dictionary")

    phase_metrics = orchestrator_metrics.get("phase_metrics", {})
    resource_usage = orchestrator_metrics.get("resource_usage", [])

    written_files = {}

    written_files["phase_metrics"] = persist_phase_metrics(
        phase_metrics, output_dir, "phase_metrics.json"
    )

    written_files["resource_usage"] = persist_resource_usage(
        resource_usage, output_dir, "resource_usage.jsonl"
    )

    written_files["latency_histograms"] = persist_latency_histograms(
        phase_metrics, output_dir, "latency_histograms.json"
    )

    return written_files


def validate_metrics_schema(metrics_data: dict[str, Any]) -> list[str]:
    """Validate that metrics data conforms to expected schema.

    Args:
        metrics_data: Metrics dictionary from export_metrics()

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(metrics_data, dict):
        errors.append("metrics_data must be a dictionary")
        return errors

    required_keys = ["timestamp", "phase_metrics", "resource_usage", "abort_status", "phase_status"]
    for key in required_keys:
        if key not in metrics_data:
            errors.append(f"Missing required key: {key}")

    if "phase_metrics" in metrics_data:
        if not isinstance(metrics_data["phase_metrics"], dict):
            errors.append("phase_metrics must be a dictionary")
        else:
            for phase_id, phase_data in metrics_data["phase_metrics"].items():
                if not isinstance(phase_data, dict):
                    errors.append(f"phase_metrics[{phase_id}] must be a dictionary")
                    continue

                required_phase_keys = [
                    "phase_id",
                    "name",
                    "duration_ms",
                    "items_processed",
                    "items_total",
                    "latency_histogram",
                ]
                for key in required_phase_keys:
                    if key not in phase_data:
                        errors.append(f"phase_metrics[{phase_id}] missing key: {key}")

    if "resource_usage" in metrics_data and not isinstance(metrics_data["resource_usage"], list):
        errors.append("resource_usage must be a list")

    if "abort_status" in metrics_data and not isinstance(metrics_data["abort_status"], dict):
        errors.append("abort_status must be a dictionary")

    return errors
