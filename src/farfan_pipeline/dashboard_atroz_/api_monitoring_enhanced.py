"""Enhanced Monitoring API endpoints for ATROZ Dashboard.

Provides REST API endpoints for accessing granular pipeline monitoring data.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request

from .monitoring_enhanced import MetricType, get_monitor

logger = logging.getLogger(__name__)

# Create Blueprint for enhanced monitoring endpoints
monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api/v1/monitoring")


@monitoring_bp.route("/jobs/<job_id>/snapshot", methods=["GET"])
def get_job_snapshot(job_id: str):
    """Get complete execution snapshot for a job.
    
    Returns detailed information about:
    - Overall job status and progress
    - All phases with their metrics
    - Resource usage timeline
    - Errors and warnings
    - Checkpoints
    
    Args:
        job_id: Job identifier
        
    Returns:
        JSON snapshot or 404 if not found
    """
    monitor = get_monitor()
    snapshot = monitor.export_snapshot(job_id)
    
    if not snapshot:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    return jsonify(snapshot)


@monitoring_bp.route("/jobs/<job_id>/phases", methods=["GET"])
def get_job_phases(job_id: str):
    """Get all phase metrics for a job.
    
    Query params:
        - status: Filter by status (PENDING, RUNNING, COMPLETED, FAILED)
        
    Args:
        job_id: Job identifier
        
    Returns:
        JSON list of phase metrics
    """
    monitor = get_monitor()
    snapshot = monitor.get_job_snapshot(job_id)
    
    if not snapshot:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    status_filter = request.args.get("status")
    
    phases_data = {}
    for phase_id, metrics in snapshot.phases.items():
        if status_filter and metrics.status != status_filter:
            continue
        
        phases_data[phase_id] = monitor._export_phase_metrics(metrics)
    
    return jsonify({
        "job_id": job_id,
        "phases": phases_data,
        "total": len(phases_data)
    })


@monitoring_bp.route("/jobs/<job_id>/phases/<phase_id>", methods=["GET"])
def get_phase_detail(job_id: str, phase_id: str):
    """Get detailed metrics for a specific phase.
    
    Args:
        job_id: Job identifier
        phase_id: Phase identifier (e.g., P00, P01)
        
    Returns:
        JSON phase metrics or 404 if not found
    """
    monitor = get_monitor()
    metrics = monitor.get_phase_metrics(job_id, phase_id)
    
    if not metrics:
        return jsonify({
            "error": f"Phase {phase_id} not found in job {job_id}"
        }), 404
    
    return jsonify(monitor._export_phase_metrics(metrics))


@monitoring_bp.route("/jobs/<job_id>/phases/<phase_id>/sub-phases", methods=["GET"])
def get_sub_phases(job_id: str, phase_id: str):
    """Get sub-phase breakdown for a phase.
    
    Args:
        job_id: Job identifier
        phase_id: Phase identifier
        
    Returns:
        JSON sub-phase data
    """
    monitor = get_monitor()
    metrics = monitor.get_phase_metrics(job_id, phase_id)
    
    if not metrics:
        return jsonify({
            "error": f"Phase {phase_id} not found in job {job_id}"
        }), 404
    
    return jsonify({
        "job_id": job_id,
        "phase_id": phase_id,
        "sub_phases": metrics.sub_phases
    })


@monitoring_bp.route("/jobs/<job_id>/resource-usage", methods=["GET"])
def get_resource_usage(job_id: str):
    """Get resource usage timeline for a job.
    
    Query params:
        - phase_id: Filter by phase
        - limit: Limit number of data points
        
    Args:
        job_id: Job identifier
        
    Returns:
        JSON resource timeline
    """
    monitor = get_monitor()
    snapshot = monitor.get_job_snapshot(job_id)
    
    if not snapshot:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    phase_filter = request.args.get("phase_id")
    limit = request.args.get("limit", type=int)
    
    timeline = snapshot.resource_timeline
    
    if phase_filter:
        timeline = [
            entry for entry in timeline 
            if entry.get("phase_id") == phase_filter
        ]
    
    if limit and limit > 0:
        timeline = timeline[-limit:]
    
    return jsonify({
        "job_id": job_id,
        "timeline": timeline,
        "total": len(timeline),
        "peak_memory_mb": snapshot.total_memory_peak_mb,
        "avg_cpu_percent": snapshot.total_cpu_avg_percent
    })


@monitoring_bp.route("/jobs/<job_id>/errors", methods=["GET"])
def get_job_errors(job_id: str):
    """Get all errors from a job.
    
    Query params:
        - phase_id: Filter by phase
        - severity: Filter by severity
        
    Args:
        job_id: Job identifier
        
    Returns:
        JSON error list
    """
    monitor = get_monitor()
    snapshot = monitor.get_job_snapshot(job_id)
    
    if not snapshot:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    phase_filter = request.args.get("phase_id")
    
    all_errors = []
    for phase_id, metrics in snapshot.phases.items():
        if phase_filter and phase_id != phase_filter:
            continue
        
        for error in metrics.errors:
            all_errors.append({
                "phase_id": phase_id,
                "phase_name": metrics.phase_name,
                **error
            })
    
    return jsonify({
        "job_id": job_id,
        "errors": all_errors,
        "total": len(all_errors)
    })


@monitoring_bp.route("/jobs/<job_id>/warnings", methods=["GET"])
def get_job_warnings(job_id: str):
    """Get all warnings from a job.
    
    Query params:
        - phase_id: Filter by phase
        
    Args:
        job_id: Job identifier
        
    Returns:
        JSON warning list
    """
    monitor = get_monitor()
    snapshot = monitor.get_job_snapshot(job_id)
    
    if not snapshot:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    phase_filter = request.args.get("phase_id")
    
    all_warnings = []
    for phase_id, metrics in snapshot.phases.items():
        if phase_filter and phase_id != phase_filter:
            continue
        
        for warning in metrics.warnings:
            all_warnings.append({
                "phase_id": phase_id,
                "phase_name": metrics.phase_name,
                **warning
            })
    
    return jsonify({
        "job_id": job_id,
        "warnings": all_warnings,
        "total": len(all_warnings)
    })


@monitoring_bp.route("/jobs/<job_id>/artifacts", methods=["GET"])
def get_job_artifacts(job_id: str):
    """Get all artifacts produced by a job.
    
    Query params:
        - phase_id: Filter by phase
        
    Args:
        job_id: Job identifier
        
    Returns:
        JSON artifact list
    """
    monitor = get_monitor()
    snapshot = monitor.get_job_snapshot(job_id)
    
    if not snapshot:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    phase_filter = request.args.get("phase_id")
    
    artifacts_by_phase = {}
    total_artifacts = 0
    
    for phase_id, metrics in snapshot.phases.items():
        if phase_filter and phase_id != phase_filter:
            continue
        
        if metrics.artifacts_produced:
            artifacts_by_phase[phase_id] = {
                "phase_name": metrics.phase_name,
                "artifacts": metrics.artifacts_produced,
                "count": len(metrics.artifacts_produced)
            }
            total_artifacts += len(metrics.artifacts_produced)
    
    return jsonify({
        "job_id": job_id,
        "artifacts_by_phase": artifacts_by_phase,
        "total_artifacts": total_artifacts
    })


@monitoring_bp.route("/phases/<phase_id>/history", methods=["GET"])
def get_phase_history(phase_id: str):
    """Get historical execution data for a phase.
    
    Query params:
        - limit: Number of historical records (default: 10, max: 100)
        
    Args:
        phase_id: Phase identifier
        
    Returns:
        JSON historical data
    """
    monitor = get_monitor()
    limit = request.args.get("limit", default=10, type=int)
    limit = min(limit, 100)  # Cap at 100
    
    history = monitor.get_phase_history(phase_id, limit=limit)
    
    history_data = [
        monitor._export_phase_metrics(metrics)
        for metrics in history
    ]
    
    return jsonify({
        "phase_id": phase_id,
        "history": history_data,
        "count": len(history_data)
    })


@monitoring_bp.route("/phases/<phase_id>/trends", methods=["GET"])
def get_phase_trends(phase_id: str):
    """Get performance trends for a phase.
    
    Query params:
        - metric: Metric type (execution_time, memory_usage, cpu_usage, error_count)
        
    Args:
        phase_id: Phase identifier
        
    Returns:
        JSON trend data
    """
    monitor = get_monitor()
    metric_param = request.args.get("metric", "execution_time")
    
    # Map string to MetricType
    metric_map = {
        "execution_time": MetricType.EXECUTION_TIME,
        "memory_usage": MetricType.MEMORY_USAGE,
        "cpu_usage": MetricType.CPU_USAGE,
        "error_count": MetricType.ERROR_COUNT,
    }
    
    metric_type = metric_map.get(metric_param, MetricType.EXECUTION_TIME)
    trends = monitor.get_performance_trends(phase_id, metric_type)
    
    return jsonify(trends)


@monitoring_bp.route("/alerts", methods=["GET"])
def get_alerts():
    """Get all active alerts.
    
    Query params:
        - job_id: Filter by job
        - severity: Filter by severity (INFO, WARNING, ERROR)
        - acknowledged: Filter by acknowledged status (true/false)
        
    Returns:
        JSON alert list
    """
    monitor = get_monitor()
    alerts = monitor.get_active_alerts()
    
    # Apply filters
    job_filter = request.args.get("job_id")
    severity_filter = request.args.get("severity")
    acknowledged_filter = request.args.get("acknowledged")
    
    if job_filter:
        alerts = [a for a in alerts if a.get("job_id") == job_filter]
    
    if severity_filter:
        alerts = [a for a in alerts if a.get("severity") == severity_filter]
    
    if acknowledged_filter is not None:
        acknowledged = acknowledged_filter.lower() == "true"
        alerts = [a for a in alerts if a.get("acknowledged", False) == acknowledged]
    
    return jsonify({
        "alerts": alerts,
        "total": len(alerts)
    })


@monitoring_bp.route("/alerts/<alert_id>/acknowledge", methods=["POST"])
def acknowledge_alert(alert_id: str):
    """Acknowledge an alert.
    
    Args:
        alert_id: Alert identifier
        
    Returns:
        JSON success response
    """
    monitor = get_monitor()
    monitor.acknowledge_alert(alert_id)
    
    return jsonify({
        "success": True,
        "alert_id": alert_id,
        "message": "Alert acknowledged"
    })


@monitoring_bp.route("/alerts/clear-acknowledged", methods=["POST"])
def clear_acknowledged_alerts():
    """Clear all acknowledged alerts.
    
    Returns:
        JSON success response
    """
    monitor = get_monitor()
    monitor.clear_acknowledged_alerts()
    
    return jsonify({
        "success": True,
        "message": "Acknowledged alerts cleared"
    })


@monitoring_bp.route("/summary", methods=["GET"])
def get_monitoring_summary():
    """Get overall monitoring summary.
    
    Returns:
        JSON summary of all active jobs and system state
    """
    monitor = get_monitor()
    
    # Aggregate data
    active_jobs_count = len(monitor.active_jobs)
    completed_jobs_count = len(monitor.completed_jobs)
    
    active_alerts = monitor.get_active_alerts()
    unacknowledged_alerts = [
        a for a in active_alerts 
        if not a.get("acknowledged", False)
    ]
    
    # Get phase statistics
    phase_stats = {}
    for phase_id, history in monitor.phase_history.items():
        if history:
            avg_time = sum(m.execution_time_ms for m in history) / len(history)
            phase_stats[phase_id] = {
                "executions": len(history),
                "avg_time_ms": avg_time,
                "last_execution": history[-1].completed_at.isoformat() if history[-1].completed_at else None
            }
    
    return jsonify({
        "active_jobs": active_jobs_count,
        "completed_jobs": completed_jobs_count,
        "total_alerts": len(active_alerts),
        "unacknowledged_alerts": len(unacknowledged_alerts),
        "phase_statistics": phase_stats,
        "timestamp": request.environ.get("REQUEST_START_TIME")
    })


@monitoring_bp.route("/jobs/<job_id>/progress", methods=["GET"])
def get_job_progress(job_id: str):
    """Get simplified progress information for a job.
    
    Optimized endpoint for frequent polling.
    
    Args:
        job_id: Job identifier
        
    Returns:
        JSON progress data
    """
    monitor = get_monitor()
    snapshot = monitor.get_job_snapshot(job_id)
    
    if not snapshot:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    return jsonify({
        "job_id": job_id,
        "status": snapshot.status,
        "progress_percent": snapshot.progress_percent,
        "current_phase": snapshot.current_phase,
        "completed_phases": len(snapshot.completed_phases),
        "total_phases": len(snapshot.phases),
        "estimated_time_remaining_ms": snapshot.estimated_time_remaining_ms,
        "errors": snapshot.total_errors,
        "warnings": snapshot.total_warnings
    })


@monitoring_bp.route("/export/<job_id>", methods=["GET"])
def export_job_data(job_id: str):
    """Export complete job monitoring data.
    
    Args:
        job_id: Job identifier
        
    Returns:
        JSON export or 404 if not found
    """
    monitor = get_monitor()
    snapshot = monitor.export_snapshot(job_id)
    
    if not snapshot:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    return jsonify({
        "export_version": "1.0",
        "exported_at": request.environ.get("REQUEST_START_TIME"),
        "data": snapshot
    })


def register_monitoring_endpoints(app):
    """Register monitoring blueprint with Flask app.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(monitoring_bp)
    logger.info("Enhanced monitoring endpoints registered")
