"""Metrics Aggregation & Real-Time Dashboarding - GAP 5 Implementation.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Metrics Exporter
PHASE_ROLE: Export metrics to Prometheus/OpenTelemetry for real-time monitoring

GAP 5 Implementation: Metrics Aggregation & Real-Time Dashboarding

This module provides real-time metrics export for Phase 2 pipeline monitoring:
- Task execution duration histograms
- Success/failure counters
- Resource pressure gauges
- Calibration quality scores

Requirements Implemented:
    ME-01: Metrics exported in Prometheus format
    ME-02: Histogram tracks task duration by executor and level
    ME-03: Counter tracks successful and failed task completions
    ME-04: Gauge tracks current resource pressure level
    ME-05: HTTP endpoint exposes /metrics for scraping

Design Considerations:
- Prometheus client library for metric types
- Thread-safe metric operations
- Configurable HTTP server port (default: 8000)
- Graceful degradation if prometheus_client unavailable
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 2
__stage__ = 95
__order__ = 4
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "MEDIUM"
__execution_pattern__ = "On-Demand"



from __future__ import annotations

import logging
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import prometheus_client, provide mock implementation if unavailable
try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        start_http_server,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning(
        "prometheus_client not installed. Metrics will be collected but not exported. "
        "Install with: pip install prometheus_client"
    )


# === DATA MODELS ===


@dataclass
class TaskMetricEvent:
    """Event data for task completion metrics.

    Attributes:
        task_id: Unique task identifier
        executor_id: Executor that ran the task
        epistemic_level: Level of the task (N1, N2, N3)
        success: Whether task completed successfully
        execution_time_ms: Execution duration in milliseconds
        error: Error message if failed
    """

    task_id: str
    executor_id: str
    epistemic_level: str
    success: bool
    execution_time_ms: float
    error: str | None = None


@dataclass
class ResourcePressureEvent:
    """Event data for resource pressure updates.

    Attributes:
        resource_type: Type of resource (cpu, memory, io)
        level: Pressure level (0=none, 1=low, 2=medium, 3=high, 4=critical)
        utilization_percent: Current utilization percentage
    """

    resource_type: str
    level: int
    utilization_percent: float


@dataclass
class CalibrationQualityEvent:
    """Event data for calibration quality updates.

    Attributes:
        executor_id: Executor identifier
        quality_score: Quality score [0.0, 1.0]
        confidence: Confidence in the score [0.0, 1.0]
        regression_detected: Whether regression was detected
    """

    executor_id: str
    quality_score: float
    confidence: float
    regression_detected: bool


# === MOCK IMPLEMENTATIONS FOR FALLBACK ===


class MockMetric:
    """Mock metric for when prometheus_client is not available."""

    def __init__(self, *args, **kwargs):
        self._values: dict[tuple, float] = {}

    def labels(self, **kwargs) -> MockMetric:
        return self

    def inc(self, amount: float = 1) -> None:
        pass

    def dec(self, amount: float = 1) -> None:
        pass

    def set(self, value: float) -> None:
        pass

    def observe(self, value: float) -> None:
        pass


# === METRICS DEFINITIONS ===

if PROMETHEUS_AVAILABLE:
    # Task execution duration histogram (ME-02)
    TASK_DURATION = Histogram(
        "phase2_task_duration_seconds",
        "Task execution duration in seconds",
        ["executor_id", "epistemic_level", "status"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
    )

    # Task completion counters (ME-03)
    TASK_SUCCESS = Counter(
        "phase2_task_success_total",
        "Total successful task completions",
        ["executor_id", "epistemic_level"],
    )

    TASK_FAILURE = Counter(
        "phase2_task_failure_total",
        "Total failed task completions",
        ["executor_id", "epistemic_level"],
    )

    # Resource pressure gauge (ME-04)
    RESOURCE_PRESSURE = Gauge(
        "phase2_resource_pressure_level",
        "Current resource pressure level (0=none, 4=critical)",
        ["resource_type"],
    )

    RESOURCE_UTILIZATION = Gauge(
        "phase2_resource_utilization_percent",
        "Current resource utilization percentage",
        ["resource_type"],
    )

    # Active tasks gauge
    ACTIVE_TASKS = Gauge(
        "phase2_active_tasks",
        "Number of currently executing tasks",
        ["executor_id"],
    )

    # Calibration quality gauge
    CALIBRATION_QUALITY = Gauge(
        "phase2_calibration_quality_score",
        "Latest calibration quality score",
        ["executor_id"],
    )

    CALIBRATION_CONFIDENCE = Gauge(
        "phase2_calibration_confidence",
        "Latest calibration confidence score",
        ["executor_id"],
    )

    CALIBRATION_REGRESSION = Gauge(
        "phase2_calibration_regression_detected",
        "Whether regression was detected (1=yes, 0=no)",
        ["executor_id"],
    )

    # Checkpoint metrics
    CHECKPOINT_SAVED = Counter(
        "phase2_checkpoint_saved_total",
        "Total checkpoints saved",
        ["plan_id"],
    )

    CHECKPOINT_RESUMED = Counter(
        "phase2_checkpoint_resumed_total",
        "Total checkpoints resumed from",
        ["plan_id"],
    )

    # Parallel execution metrics
    PARALLEL_LEVEL_DURATION = Histogram(
        "phase2_parallel_level_duration_seconds",
        "Duration to execute all tasks in an epistemic level",
        ["epistemic_level", "task_count_bucket"],
        buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0),
    )

else:
    # Mock metrics when prometheus_client is not available
    TASK_DURATION = MockMetric()
    TASK_SUCCESS = MockMetric()
    TASK_FAILURE = MockMetric()
    RESOURCE_PRESSURE = MockMetric()
    RESOURCE_UTILIZATION = MockMetric()
    ACTIVE_TASKS = MockMetric()
    CALIBRATION_QUALITY = MockMetric()
    CALIBRATION_CONFIDENCE = MockMetric()
    CALIBRATION_REGRESSION = MockMetric()
    CHECKPOINT_SAVED = MockMetric()
    CHECKPOINT_RESUMED = MockMetric()
    PARALLEL_LEVEL_DURATION = MockMetric()


# === METRICS EXPORTER CLASS ===


class MetricsExporter:
    """
    Exports Phase 2 metrics to Prometheus.

    GAP 5 Implementation: Metrics Aggregation & Real-Time Dashboarding

    Features:
        - Task duration histograms by executor and level
        - Success/failure counters
        - Resource pressure gauges
        - Calibration quality tracking
        - HTTP endpoint for Prometheus scraping

    Usage:
        exporter = MetricsExporter(port=8000)
        exporter.start_server()
        exporter.record_task_result(task_result)
    """

    def __init__(self, port: int = 8000, auto_start: bool = False):
        """
        Initialize MetricsExporter.

        Args:
            port: HTTP port for /metrics endpoint (default: 8000)
            auto_start: Whether to start HTTP server automatically
        """
        self.port = port
        self._server_started = False
        self._lock = threading.Lock()

        if auto_start and PROMETHEUS_AVAILABLE:
            self.start_server()

    def start_server(self) -> bool:
        """
        Start the Prometheus metrics HTTP server.

        Returns:
            True if server started successfully, False otherwise.
        """
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Cannot start metrics server: prometheus_client not installed")
            return False

        with self._lock:
            if not self._server_started:
                try:
                    start_http_server(self.port)
                    self._server_started = True
                    logger.info(f"Prometheus metrics server started on port {self.port}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to start metrics server: {e}")
                    return False
            return True

    @property
    def server_running(self) -> bool:
        """Check if metrics server is running."""
        return self._server_started

    # === Task Metrics ===

    def record_task_result(self, event: TaskMetricEvent) -> None:
        """
        Record metrics for a completed task.

        Implements ME-02 and ME-03.

        Args:
            event: TaskMetricEvent with task completion data.
        """
        status = "success" if event.success else "failure"

        # Record duration histogram (ME-02)
        TASK_DURATION.labels(
            executor_id=event.executor_id,
            epistemic_level=event.epistemic_level,
            status=status,
        ).observe(event.execution_time_ms / 1000.0)

        # Increment counters (ME-03)
        if event.success:
            TASK_SUCCESS.labels(
                executor_id=event.executor_id,
                epistemic_level=event.epistemic_level,
            ).inc()
        else:
            TASK_FAILURE.labels(
                executor_id=event.executor_id,
                epistemic_level=event.epistemic_level,
            ).inc()

        logger.debug(
            f"Recorded task metric: {event.task_id} "
            f"executor={event.executor_id} level={event.epistemic_level} "
            f"status={status} duration={event.execution_time_ms:.1f}ms"
        )

    def update_active_tasks(self, executor_id: str, count: int) -> None:
        """
        Update the count of active tasks for an executor.

        Args:
            executor_id: Executor identifier.
            count: Current number of active tasks.
        """
        ACTIVE_TASKS.labels(executor_id=executor_id).set(count)

    def increment_active_tasks(self, executor_id: str) -> None:
        """Increment active task count for an executor."""
        ACTIVE_TASKS.labels(executor_id=executor_id).inc()

    def decrement_active_tasks(self, executor_id: str) -> None:
        """Decrement active task count for an executor."""
        ACTIVE_TASKS.labels(executor_id=executor_id).dec()

    # === Resource Metrics ===

    def update_resource_pressure(self, event: ResourcePressureEvent) -> None:
        """
        Update the current resource pressure level.

        Implements ME-04.

        Args:
            event: ResourcePressureEvent with resource data.
        """
        RESOURCE_PRESSURE.labels(resource_type=event.resource_type).set(event.level)
        RESOURCE_UTILIZATION.labels(resource_type=event.resource_type).set(
            event.utilization_percent
        )

        logger.debug(
            f"Updated resource pressure: {event.resource_type} "
            f"level={event.level} utilization={event.utilization_percent:.1f}%"
        )

    def set_resource_pressure(self, resource_type: str, level: int) -> None:
        """
        Set resource pressure level directly.

        Args:
            resource_type: Type of resource ('cpu', 'memory', 'io').
            level: Pressure level (0-4).
        """
        RESOURCE_PRESSURE.labels(resource_type=resource_type).set(level)

    # === Calibration Metrics ===

    def update_calibration_quality(self, event: CalibrationQualityEvent) -> None:
        """
        Update the calibration quality score for an executor.

        Args:
            event: CalibrationQualityEvent with calibration data.
        """
        CALIBRATION_QUALITY.labels(executor_id=event.executor_id).set(event.quality_score)
        CALIBRATION_CONFIDENCE.labels(executor_id=event.executor_id).set(event.confidence)
        CALIBRATION_REGRESSION.labels(executor_id=event.executor_id).set(
            1 if event.regression_detected else 0
        )

        logger.debug(
            f"Updated calibration metric: {event.executor_id} "
            f"quality={event.quality_score:.3f} confidence={event.confidence:.3f} "
            f"regression={event.regression_detected}"
        )

    def set_calibration_quality(self, executor_id: str, quality: float) -> None:
        """
        Set calibration quality score directly.

        Args:
            executor_id: Executor identifier.
            quality: Quality score [0.0, 1.0].
        """
        CALIBRATION_QUALITY.labels(executor_id=executor_id).set(quality)

    # === Checkpoint Metrics ===

    def record_checkpoint_saved(self, plan_id: str) -> None:
        """Record that a checkpoint was saved."""
        CHECKPOINT_SAVED.labels(plan_id=plan_id).inc()

    def record_checkpoint_resumed(self, plan_id: str) -> None:
        """Record that execution was resumed from a checkpoint."""
        CHECKPOINT_RESUMED.labels(plan_id=plan_id).inc()

    # === Parallel Execution Metrics ===

    def record_level_execution(
        self, epistemic_level: str, task_count: int, duration_seconds: float
    ) -> None:
        """
        Record the duration to execute all tasks in an epistemic level.

        Args:
            epistemic_level: Level identifier (e.g., "N1", "N2").
            task_count: Number of tasks in the level.
            duration_seconds: Total duration in seconds.
        """
        # Bucket task counts for cardinality control
        if task_count <= 10:
            task_bucket = "1-10"
        elif task_count <= 50:
            task_bucket = "11-50"
        elif task_count <= 100:
            task_bucket = "51-100"
        else:
            task_bucket = "100+"

        PARALLEL_LEVEL_DURATION.labels(
            epistemic_level=epistemic_level,
            task_count_bucket=task_bucket,
        ).observe(duration_seconds)


# === SINGLETON EXPORTER INSTANCE ===

_metrics_exporter: MetricsExporter | None = None
_exporter_lock = threading.Lock()


def get_metrics_exporter(port: int = 8000) -> MetricsExporter:
    """
    Get or create the global metrics exporter instance.

    Args:
        port: HTTP port for metrics endpoint (only used on first call).

    Returns:
        MetricsExporter singleton instance.
    """
    global _metrics_exporter
    with _exporter_lock:
        if _metrics_exporter is None:
            _metrics_exporter = MetricsExporter(port=port)
        return _metrics_exporter


# === CONVENIENCE FUNCTIONS ===


def record_task_completion(
    task_id: str,
    executor_id: str,
    epistemic_level: str,
    success: bool,
    execution_time_ms: float,
    error: str | None = None,
) -> None:
    """
    Record task completion metrics (convenience function).

    Args:
        task_id: Unique task identifier.
        executor_id: Executor that ran the task.
        epistemic_level: Level of the task.
        success: Whether task completed successfully.
        execution_time_ms: Execution duration in milliseconds.
        error: Error message if failed.
    """
    exporter = get_metrics_exporter()
    exporter.record_task_result(
        TaskMetricEvent(
            task_id=task_id,
            executor_id=executor_id,
            epistemic_level=epistemic_level,
            success=success,
            execution_time_ms=execution_time_ms,
            error=error,
        )
    )


def update_resource_status(
    resource_type: str, level: int, utilization_percent: float = 0.0
) -> None:
    """
    Update resource pressure status (convenience function).

    Args:
        resource_type: Type of resource ('cpu', 'memory', 'io').
        level: Pressure level (0-4).
        utilization_percent: Current utilization percentage.
    """
    exporter = get_metrics_exporter()
    exporter.update_resource_pressure(
        ResourcePressureEvent(
            resource_type=resource_type,
            level=level,
            utilization_percent=utilization_percent,
        )
    )


def update_calibration_status(
    executor_id: str,
    quality_score: float,
    confidence: float = 0.5,
    regression_detected: bool = False,
) -> None:
    """
    Update calibration quality status (convenience function).

    Args:
        executor_id: Executor identifier.
        quality_score: Quality score [0.0, 1.0].
        confidence: Confidence in the score [0.0, 1.0].
        regression_detected: Whether regression was detected.
    """
    exporter = get_metrics_exporter()
    exporter.update_calibration_quality(
        CalibrationQualityEvent(
            executor_id=executor_id,
            quality_score=quality_score,
            confidence=confidence,
            regression_detected=regression_detected,
        )
    )


# === GRAFANA DASHBOARD TEMPLATE ===

GRAFANA_DASHBOARD_TEMPLATE = {
    "dashboard": {
        "title": "Phase 2 Pipeline Metrics",
        "uid": "phase2-metrics",
        "panels": [
            {
                "title": "Task Duration (p95)",
                "type": "graph",
                "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(phase2_task_duration_seconds_bucket[5m]))",
                        "legendFormat": "{{executor_id}} - {{epistemic_level}}",
                    }
                ],
            },
            {
                "title": "Task Success Rate",
                "type": "gauge",
                "gridPos": {"x": 12, "y": 0, "w": 6, "h": 8},
                "targets": [
                    {
                        "expr": (
                            "sum(rate(phase2_task_success_total[5m])) / "
                            "(sum(rate(phase2_task_success_total[5m])) + "
                            "sum(rate(phase2_task_failure_total[5m])))"
                        )
                    }
                ],
            },
            {
                "title": "Resource Pressure",
                "type": "heatmap",
                "gridPos": {"x": 18, "y": 0, "w": 6, "h": 8},
                "targets": [
                    {"expr": "phase2_resource_pressure_level", "legendFormat": "{{resource_type}}"}
                ],
            },
            {
                "title": "Calibration Quality",
                "type": "timeseries",
                "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
                "targets": [
                    {"expr": "phase2_calibration_quality_score", "legendFormat": "{{executor_id}}"}
                ],
            },
            {
                "title": "Active Tasks",
                "type": "stat",
                "gridPos": {"x": 12, "y": 8, "w": 6, "h": 8},
                "targets": [{"expr": "sum(phase2_active_tasks)"}],
            },
            {
                "title": "Task Throughput",
                "type": "graph",
                "gridPos": {"x": 18, "y": 8, "w": 6, "h": 8},
                "targets": [
                    {
                        "expr": "sum(rate(phase2_task_success_total[1m]))",
                        "legendFormat": "Success/min",
                    },
                    {
                        "expr": "sum(rate(phase2_task_failure_total[1m]))",
                        "legendFormat": "Failure/min",
                    },
                ],
            },
        ],
    }
}


def get_grafana_dashboard_json() -> str:
    """
    Get Grafana dashboard configuration as JSON.

    Returns:
        JSON string with dashboard configuration.
    """
    import json

    return json.dumps(GRAFANA_DASHBOARD_TEMPLATE, indent=2)


__all__ = [
    # Data models
    "TaskMetricEvent",
    "ResourcePressureEvent",
    "CalibrationQualityEvent",
    # Main class
    "MetricsExporter",
    "get_metrics_exporter",
    # Convenience functions
    "record_task_completion",
    "update_resource_status",
    "update_calibration_status",
    # Dashboard
    "get_grafana_dashboard_json",
    "GRAFANA_DASHBOARD_TEMPLATE",
    # Availability flag
    "PROMETHEUS_AVAILABLE",
]
