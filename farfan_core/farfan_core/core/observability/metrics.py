"""
Prometheus-style metrics for F.A.R.F.A.N runtime observability.

This module provides metric counters for tracking fallbacks, degradations,
and runtime behavior. All metrics are exposed via the ATROZ dashboard's
hidden layer for centralized health monitoring.

Metrics are prefixed with 'farfan_core_' and include labels for categorization.
"""

from typing import Optional
from prometheus_client import Counter, Gauge, Histogram

from farfan_core.core.runtime_config import RuntimeMode
from farfan_core.core.contracts.runtime_contracts import (
    FallbackCategory,
    SegmentationMethod,
    CalibrationMode,
    DocumentIdSource,
)


# ============================================================================
# Fallback Metrics
# ============================================================================

fallback_activations_total = Counter(
    'farfan_core_fallback_activations_total',
    'Total number of fallback activations',
    ['component', 'fallback_category', 'fallback_mode', 'runtime_mode']
)


def increment_fallback(
    component: str,
    fallback_category: FallbackCategory,
    fallback_mode: str,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Increment fallback activation counter.
    
    Args:
        component: Component name
        fallback_category: Fallback category (A/B/C/D)
        fallback_mode: Specific fallback mode
        runtime_mode: Current runtime mode
    """
    fallback_activations_total.labels(
        component=component,
        fallback_category=fallback_category.value,
        fallback_mode=fallback_mode,
        runtime_mode=runtime_mode.value,
    ).inc()


# ============================================================================
# Segmentation Metrics
# ============================================================================

segmentation_method_total = Counter(
    'farfan_core_segmentation_method_total',
    'Total segmentation method usage',
    ['method', 'runtime_mode']
)


def increment_segmentation_method(
    method: SegmentationMethod,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Increment segmentation method counter.
    
    Args:
        method: Segmentation method used
        runtime_mode: Current runtime mode
    """
    segmentation_method_total.labels(
        method=method.value,
        runtime_mode=runtime_mode.value,
    ).inc()


# ============================================================================
# Calibration Metrics
# ============================================================================

calibration_mode_total = Counter(
    'farfan_core_calibration_mode_total',
    'Total calibration mode usage',
    ['mode', 'runtime_mode']
)


def increment_calibration_mode(
    mode: CalibrationMode,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Increment calibration mode counter.
    
    Args:
        mode: Calibration mode
        runtime_mode: Current runtime mode
    """
    calibration_mode_total.labels(
        mode=mode.value,
        runtime_mode=runtime_mode.value,
    ).inc()


# ============================================================================
# Document ID Metrics
# ============================================================================

document_id_source_total = Counter(
    'farfan_core_document_id_source_total',
    'Total document ID source usage',
    ['source', 'runtime_mode']
)


def increment_document_id_source(
    source: DocumentIdSource,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Increment document ID source counter.
    
    Args:
        source: Document ID source
        runtime_mode: Current runtime mode
    """
    document_id_source_total.labels(
        source=source.value,
        runtime_mode=runtime_mode.value,
    ).inc()


# ============================================================================
# Hash Algorithm Metrics
# ============================================================================

hash_algo_total = Counter(
    'farfan_core_hash_algo_total',
    'Total hash algorithm usage',
    ['algo', 'runtime_mode']
)


def increment_hash_algo(
    algo: str,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Increment hash algorithm counter.
    
    Args:
        algo: Hash algorithm name (e.g., "blake3", "sha256")
        runtime_mode: Current runtime mode
    """
    hash_algo_total.labels(
        algo=algo,
        runtime_mode=runtime_mode.value,
    ).inc()


# ============================================================================
# Graph Metrics
# ============================================================================

graph_metrics_skipped_total = Counter(
    'farfan_core_graph_metrics_skipped_total',
    'Total graph metrics computation skips',
    ['runtime_mode', 'reason']
)


def increment_graph_metrics_skipped(
    reason: str,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Increment graph metrics skipped counter.
    
    Args:
        reason: Reason for skip (e.g., "networkx_unavailable")
        runtime_mode: Current runtime mode
    """
    graph_metrics_skipped_total.labels(
        runtime_mode=runtime_mode.value,
        reason=reason,
    ).inc()


# ============================================================================
# Contradiction Detection Metrics
# ============================================================================

contradiction_mode_total = Counter(
    'farfan_core_contradiction_mode_total',
    'Total contradiction detection mode usage',
    ['mode', 'runtime_mode']
)


def increment_contradiction_mode(
    mode: str,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Increment contradiction mode counter.
    
    Args:
        mode: Contradiction mode ("full" or "fallback")
        runtime_mode: Current runtime mode
    """
    contradiction_mode_total.labels(
        mode=mode,
        runtime_mode=runtime_mode.value,
    ).inc()


# ============================================================================
# Boot Check Metrics
# ============================================================================

boot_check_failures_total = Counter(
    'farfan_core_boot_check_failures_total',
    'Total boot check failures',
    ['check_name', 'runtime_mode', 'code']
)


def increment_boot_check_failure(
    check_name: str,
    code: str,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Increment boot check failure counter.
    
    Args:
        check_name: Name of failed check
        code: Error code
        runtime_mode: Current runtime mode
    """
    boot_check_failures_total.labels(
        check_name=check_name,
        runtime_mode=runtime_mode.value,
        code=code,
    ).inc()


# ============================================================================
# Pipeline Execution Metrics
# ============================================================================

pipeline_executions_total = Counter(
    'farfan_core_pipeline_executions_total',
    'Total pipeline executions',
    ['runtime_mode', 'status']
)

pipeline_execution_duration_seconds = Histogram(
    'farfan_core_pipeline_execution_duration_seconds',
    'Pipeline execution duration in seconds',
    ['runtime_mode'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)


def increment_pipeline_execution(
    runtime_mode: RuntimeMode,
    status: str,
) -> None:
    """
    Increment pipeline execution counter.
    
    Args:
        runtime_mode: Current runtime mode
        status: Execution status ("success", "failure", "aborted")
    """
    pipeline_executions_total.labels(
        runtime_mode=runtime_mode.value,
        status=status,
    ).inc()


def observe_pipeline_duration(
    duration_seconds: float,
    runtime_mode: RuntimeMode,
) -> None:
    """
    Observe pipeline execution duration.
    
    Args:
        duration_seconds: Execution duration in seconds
        runtime_mode: Current runtime mode
    """
    pipeline_execution_duration_seconds.labels(
        runtime_mode=runtime_mode.value,
    ).observe(duration_seconds)


# ============================================================================
# ATROZ Dashboard Integration
# ============================================================================

# Current runtime mode gauge (for dashboard display)
current_runtime_mode = Gauge(
    'farfan_core_current_runtime_mode',
    'Current runtime mode (0=PROD, 1=DEV, 2=EXPLORATORY)',
    []
)


def set_current_runtime_mode(mode: RuntimeMode) -> None:
    """
    Set current runtime mode gauge for dashboard display.
    
    Args:
        mode: Current runtime mode
    """
    mode_value = {
        RuntimeMode.PROD: 0,
        RuntimeMode.DEV: 1,
        RuntimeMode.EXPLORATORY: 2,
    }[mode]
    current_runtime_mode.set(mode_value)


# Health status gauge (for dashboard alerts)
system_health_status = Gauge(
    'farfan_core_system_health_status',
    'System health status (0=degraded, 1=healthy)',
    []
)


def set_system_health_status(healthy: bool) -> None:
    """
    Set system health status for dashboard alerts.
    
    Args:
        healthy: Whether system is healthy (no Category A fallbacks)
    """
    system_health_status.set(1 if healthy else 0)


# ============================================================================
# Metric Export for ATROZ Dashboard
# ============================================================================

def get_all_metrics() -> dict[str, any]:
    """
    Get all metrics for ATROZ dashboard integration.
    
    Returns:
        Dictionary of all metric collectors
    """
    return {
        'fallback_activations_total': fallback_activations_total,
        'segmentation_method_total': segmentation_method_total,
        'calibration_mode_total': calibration_mode_total,
        'document_id_source_total': document_id_source_total,
        'hash_algo_total': hash_algo_total,
        'graph_metrics_skipped_total': graph_metrics_skipped_total,
        'contradiction_mode_total': contradiction_mode_total,
        'boot_check_failures_total': boot_check_failures_total,
        'pipeline_executions_total': pipeline_executions_total,
        'pipeline_execution_duration_seconds': pipeline_execution_duration_seconds,
        'current_runtime_mode': current_runtime_mode,
        'system_health_status': system_health_status,
    }
