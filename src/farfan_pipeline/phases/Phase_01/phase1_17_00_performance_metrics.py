"""
Phase 1 Performance Metrics Collector
======================================

Comprehensive performance metrics collection for Phase 1 execution.
Tracks timing, memory usage, and resource consumption for each subphase.

Architecture:
    - Thread-safe metrics collection
    - Per-subphase timing and memory profiling
    - Aggregate statistics computation
    - Export to JSON for analysis

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
"""
from __future__ import annotations

import json
import threading
import time
import tracemalloc
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SubphaseMetrics:
    """Metrics for a single subphase execution.

    Attributes:
        subphase_id: Subphase identifier (e.g., "SP4", "SP11")
        start_time: UTC timestamp when subphase started
        end_time: UTC timestamp when subphase completed
        duration_ms: Execution duration in milliseconds
        memory_mb_start: Memory usage at start in MB
        memory_mb_peak: Peak memory usage during execution in MB
        memory_mb_end: Memory usage at end in MB
        input_size: Size of input data (approximate)
        output_size: Size of output data (approximate)
        status: Execution status (completed, failed, skipped)
        error_message: Error message if status is failed
        metadata: Additional metrics metadata
    """

    subphase_id: str
    start_time: str
    end_time: str
    duration_ms: float
    memory_mb_start: float
    memory_mb_peak: float
    memory_mb_end: float
    input_size: int = 0
    output_size: int = 0
    status: str = "completed"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "subphase_id": self.subphase_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "memory_mb_start": self.memory_mb_start,
            "memory_mb_peak": self.memory_mb_peak,
            "memory_mb_end": self.memory_mb_end,
            "input_size": self.input_size,
            "output_size": self.output_size,
            "status": self.status,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class Phase1Metrics:
    """Aggregate metrics for complete Phase 1 execution.

    Attributes:
        plan_id: Unique identifier for this execution
        phase_id: Phase identifier (always "P01")
        start_time: UTC timestamp when Phase 1 started
        end_time: UTC timestamp when Phase 1 completed
        total_duration_ms: Total execution duration in milliseconds
        subphase_metrics: List of individual subphase metrics
        aggregate_stats: Computed aggregate statistics
        metadata: Additional execution metadata
    """

    plan_id: str
    phase_id: str = "P01"
    start_time: str = ""
    end_time: str = ""
    total_duration_ms: float = 0.0
    subphase_metrics: List[SubphaseMetrics] = field(default_factory=list)
    aggregate_stats: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "plan_id": self.plan_id,
            "phase_id": self.phase_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration_ms": self.total_duration_ms,
            "subphase_metrics": [m.to_dict() for m in self.subphase_metrics],
            "aggregate_stats": self.aggregate_stats,
            "metadata": self.metadata,
        }

    def compute_aggregate_stats(self) -> None:
        """Compute aggregate statistics from subphase metrics."""
        if not self.subphase_metrics:
            self.aggregate_stats = {
                "total_subphases": 0,
                "completed_subphases": 0,
                "failed_subphases": 0,
                "skipped_subphases": 0,
                "total_duration_ms": 0.0,
                "avg_duration_ms": 0.0,
                "min_duration_ms": 0.0,
                "max_duration_ms": 0.0,
                "total_memory_mb_peak": 0.0,
                "avg_memory_mb_peak": 0.0,
                "max_memory_mb_peak": 0.0,
            }
            return

        completed = [m for m in self.subphase_metrics if m.status == "completed"]
        failed = [m for m in self.subphase_metrics if m.status == "failed"]
        skipped = [m for m in self.subphase_metrics if m.status == "skipped"]

        durations = [m.duration_ms for m in completed]
        memory_peaks = [m.memory_mb_peak for m in self.subphase_metrics]

        self.aggregate_stats = {
            "total_subphases": len(self.subphase_metrics),
            "completed_subphases": len(completed),
            "failed_subphases": len(failed),
            "skipped_subphases": len(skipped),
            "total_duration_ms": sum(durations) if durations else 0.0,
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0.0,
            "min_duration_ms": min(durations) if durations else 0.0,
            "max_duration_ms": max(durations) if durations else 0.0,
            "total_memory_mb_peak": sum(memory_peaks) if memory_peaks else 0.0,
            "avg_memory_mb_peak": sum(memory_peaks) / len(memory_peaks) if memory_peaks else 0.0,
            "max_memory_mb_peak": max(memory_peaks) if memory_peaks else 0.0,
        }


class Phase1MetricsCollector:
    """
    Collects performance metrics for Phase 1 execution.

    Usage:
        >>> collector = Phase1MetricsCollector(plan_id="20260122_120000")
        >>> with collector.track_subphase("SP4"):
        ...     # Execute SP4 logic
        ...     pass
        >>> metrics = collector.get_metrics()
        >>> metrics.compute_aggregate_stats()
        >>> collector.export_metrics("/path/to/metrics.json")
    """

    def __init__(self, plan_id: str):
        """Initialize metrics collector.

        Args:
            plan_id: Unique execution identifier
        """
        self.plan_id = plan_id
        self._metrics = Phase1Metrics(plan_id=plan_id)
        self._lock = threading.Lock()
        self._current_subphase: Optional[str] = None
        self._subphase_start_time: Optional[float] = None
        self._subphase_start_memory: Optional[float] = None
        self._enabled = True

        # Start tracing memory
        tracemalloc.start()

    def start_phase(self) -> None:
        """Mark the start of Phase 1 execution."""
        with self._lock:
            self._metrics.start_time = datetime.now(timezone.utc).isoformat()

    def end_phase(self) -> None:
        """Mark the end of Phase 1 execution."""
        with self._lock:
            self._metrics.end_time = datetime.now(timezone.utc).isoformat()

            # Calculate total duration
            if self._metrics.start_time:
                start = datetime.fromisoformat(self._metrics.start_time)
                end = datetime.fromisoformat(self._metrics.end_time)
                self._metrics.total_duration_ms = (
                    end - start
                ).total_seconds() * 1000

            # Compute aggregate stats
            self._metrics.compute_aggregate_stats()

            # Stop tracing memory
            tracemalloc.stop()

    def track_subphase(self, subphase_id: str):
        """Context manager for tracking a single subphase execution.

        Args:
            subphase_id: Subphase identifier (e.g., "SP4", "SP11")

        Returns:
            Context manager for the subphase

        Example:
            >>> with collector.track_subphase("SP4"):
            ...     # Execute SP4 logic
            ...     chunks = execute_sp4(input_data)
        """
        return _SubphaseTracker(self, subphase_id)

    def record_subphase_metrics(self, metrics: SubphaseMetrics) -> None:
        """Record metrics for a completed subphase.

        Args:
            metrics: SubphaseMetrics object to record
        """
        with self._lock:
            self._metrics.subphase_metrics.append(metrics)

    def get_metrics(self) -> Phase1Metrics:
        """Get the current metrics snapshot.

        Returns:
            Phase1Metrics object with current data
        """
        return self._metrics

    def export_metrics(self, output_path: Path) -> None:
        """Export metrics to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self._metrics.to_dict(), f, indent=2, default=str)

    def get_subphase_metrics(self, subphase_id: str) -> Optional[SubphaseMetrics]:
        """Get metrics for a specific subphase.

        Args:
            subphase_id: Subphase identifier

        Returns:
            SubphaseMetrics if found, None otherwise
        """
        for m in self._metrics.subphase_metrics:
            if m.subphase_id == subphase_id:
                return m
        return None

    def get_slowest_subphases(self, n: int = 5) -> List[SubphaseMetrics]:
        """Get the N slowest subphases by duration.

        Args:
            n: Number of subphases to return

        Returns:
            List of N slowest SubphaseMetrics objects
        """
        completed = [m for m in self._metrics.subphase_metrics if m.status == "completed"]
        return sorted(completed, key=lambda m: m.duration_ms, reverse=True)[:n]

    def get_memory_intensive_subphases(self, n: int = 5) -> List[SubphaseMetrics]:
        """Get the N most memory-intensive subphases by peak memory.

        Args:
            n: Number of subphases to return

        Returns:
            List of N most memory-intensive SubphaseMetrics objects
        """
        return sorted(
            self._metrics.subphase_metrics,
            key=lambda m: m.memory_mb_peak,
            reverse=True
        )[:n]


class _SubphaseTracker:
    """Context manager for tracking a single subphase execution."""

    def __init__(self, collector: Phase1MetricsCollector, subphase_id: str):
        """Initialize subphase tracker.

        Args:
            collector: Parent metrics collector
            subphase_id: Subphase identifier
        """
        self.collector = collector
        self.subphase_id = subphase_id
        self.start_time: Optional[float] = None
        self.start_memory: Optional[float] = None
        self.peak_memory: Optional[float] = None
        self.status: str = "completed"
        self.error_message: Optional[str] = None

    def __enter__(self):
        """Start tracking subphase execution."""
        if not self.collector._enabled:
            return self

        self.start_time = time.time()
        self.start_memory = tracemalloc.get_traced_memory()[0] / 1024 / 1024  # Convert to MB

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End tracking subphase execution and record metrics."""
        if not self.collector._enabled or self.start_time is None:
            return

        end_time = time.time()
        end_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024  # Peak in MB
        duration_ms = (end_time - self.start_time) * 1000

        # Determine status
        if exc_type is not None:
            self.status = "failed"
            self.error_message = str(exc_val)
        else:
            self.status = "completed"

        # Create metrics object
        metrics = SubphaseMetrics(
            subphase_id=self.subphase_id,
            start_time=datetime.fromtimestamp(self.start_time, timezone.utc).isoformat(),
            end_time=datetime.fromtimestamp(end_time, timezone.utc).isoformat(),
            duration_ms=duration_ms,
            memory_mb_start=self.start_memory or 0.0,
            memory_mb_peak=end_memory,
            memory_mb_end=end_memory,
            status=self.status,
            error_message=self.error_message,
        )

        # Record metrics
        self.collector.record_subphase_metrics(metrics)

        # Don't suppress exceptions
        return False


__all__ = [
    "SubphaseMetrics",
    "Phase1Metrics",
    "Phase1MetricsCollector",
]
