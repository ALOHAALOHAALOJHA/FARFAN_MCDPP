"""Enhanced Monitoring Module for ATROZ Dashboard.

Provides granular tracking, observation, monitoring, evaluation, and visualization
capabilities for pipeline execution with per-phase insights.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics that can be tracked."""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    THROUGHPUT = "throughput"
    ERROR_COUNT = "error_count"
    WARNING_COUNT = "warning_count"
    ARTIFACT_COUNT = "artifact_count"
    SIGNAL_COUNT = "signal_count"


@dataclass
class PhaseMetrics:
    """Detailed metrics for a single phase execution."""
    
    phase_id: str
    phase_name: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Detailed metrics
    sub_phases: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    artifacts_produced: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance tracking
    throughput_items_per_sec: float = 0.0
    items_processed: int = 0
    
    # SISAS integration
    signals_emitted: int = 0
    signals_consumed: int = 0
    
    # Custom metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineExecutionSnapshot:
    """Complete snapshot of pipeline execution state."""
    
    job_id: str
    filename: str
    status: str  # INITIALIZING, RUNNING, COMPLETED, FAILED, CANCELLED
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_execution_time_ms: float = 0.0
    
    # Phase tracking
    phases: Dict[str, PhaseMetrics] = field(default_factory=dict)
    current_phase: Optional[str] = None
    completed_phases: List[str] = field(default_factory=list)
    failed_phases: List[str] = field(default_factory=list)
    
    # Overall metrics
    total_memory_peak_mb: float = 0.0
    total_cpu_avg_percent: float = 0.0
    total_artifacts: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    
    # Progress
    progress_percent: int = 0
    estimated_time_remaining_ms: Optional[float] = None
    
    # Resource usage timeline
    resource_timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Checkpoints
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)


class EnhancedPipelineMonitor:
    """Enhanced monitoring system for granular pipeline tracking.
    
    Provides:
    - Real-time phase and sub-phase tracking
    - Performance metrics collection
    - Resource usage monitoring
    - Error and warning aggregation
    - Historical data collection
    - Alert generation
    """
    
    def __init__(self):
        """Initialize enhanced monitor."""
        self.active_jobs: Dict[str, PipelineExecutionSnapshot] = {}
        self.completed_jobs: Dict[str, PipelineExecutionSnapshot] = {}
        
        # Historical data
        self.phase_history: Dict[str, List[PhaseMetrics]] = defaultdict(list)
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Alert thresholds
        self.alert_thresholds = {
            "execution_time_ms": 300000,  # 5 minutes
            "memory_usage_mb": 4096,  # 4 GB
            "cpu_usage_percent": 90.0,
            "error_count": 5,
        }
        
        # Alerts
        self.active_alerts: List[Dict[str, Any]] = []
        
        logger.info("EnhancedPipelineMonitor initialized")
    
    def start_job_monitoring(
        self, 
        job_id: str, 
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PipelineExecutionSnapshot:
        """Start monitoring a new job.
        
        Args:
            job_id: Unique job identifier
            filename: Input filename
            metadata: Optional job metadata
            
        Returns:
            PipelineExecutionSnapshot for tracking
        """
        snapshot = PipelineExecutionSnapshot(
            job_id=job_id,
            filename=filename,
            status="INITIALIZING",
            started_at=datetime.now(),
        )
        
        self.active_jobs[job_id] = snapshot
        
        logger.info(f"Started monitoring job {job_id}: {filename}")
        return snapshot
    
    def start_phase(
        self,
        job_id: str,
        phase_id: str,
        phase_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[PhaseMetrics]:
        """Start monitoring a phase.
        
        Args:
            job_id: Job identifier
            phase_id: Phase identifier (e.g., P00, P01)
            phase_name: Human-readable phase name
            metadata: Optional phase metadata
            
        Returns:
            PhaseMetrics instance or None if job not found
        """
        if job_id not in self.active_jobs:
            logger.warning(f"Job {job_id} not found")
            return None
        
        snapshot = self.active_jobs[job_id]
        
        phase_metrics = PhaseMetrics(
            phase_id=phase_id,
            phase_name=phase_name,
            status="RUNNING",
            started_at=datetime.now(),
        )
        
        if metadata:
            phase_metrics.custom_metrics.update(metadata)
        
        snapshot.phases[phase_id] = phase_metrics
        snapshot.current_phase = phase_id
        snapshot.status = "RUNNING"
        
        logger.info(f"Job {job_id}: Started phase {phase_id} ({phase_name})")
        return phase_metrics
    
    def complete_phase(
        self,
        job_id: str,
        phase_id: str,
        artifacts: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[PhaseMetrics]:
        """Complete a phase and record final metrics.
        
        Args:
            job_id: Job identifier
            phase_id: Phase identifier
            artifacts: List of artifact paths produced
            metrics: Additional metrics to record
            
        Returns:
            Updated PhaseMetrics or None
        """
        if job_id not in self.active_jobs:
            return None
        
        snapshot = self.active_jobs[job_id]
        
        if phase_id not in snapshot.phases:
            logger.warning(f"Phase {phase_id} not found in job {job_id}")
            return None
        
        phase = snapshot.phases[phase_id]
        phase.status = "COMPLETED"
        phase.completed_at = datetime.now()
        
        if phase.started_at:
            elapsed = (phase.completed_at - phase.started_at).total_seconds()
            phase.execution_time_ms = elapsed * 1000
        
        if artifacts:
            phase.artifacts_produced.extend(artifacts)
        
        if metrics:
            phase.custom_metrics.update(metrics)
        
        # Update snapshot
        snapshot.completed_phases.append(phase_id)
        snapshot.total_artifacts += len(phase.artifacts_produced)
        
        # Add to history
        self.phase_history[phase_id].append(phase)
        self.performance_trends[phase_id].append(phase.execution_time_ms)
        
        # Check for alerts
        self._check_phase_alerts(job_id, phase)
        
        logger.info(
            f"Job {job_id}: Completed phase {phase_id} in {phase.execution_time_ms:.2f}ms"
        )
        return phase
    
    def fail_phase(
        self,
        job_id: str,
        phase_id: str,
        error: str,
        error_details: Optional[Dict[str, Any]] = None
    ) -> Optional[PhaseMetrics]:
        """Mark a phase as failed.
        
        Args:
            job_id: Job identifier
            phase_id: Phase identifier
            error: Error message
            error_details: Additional error details
            
        Returns:
            Updated PhaseMetrics or None
        """
        if job_id not in self.active_jobs:
            return None
        
        snapshot = self.active_jobs[job_id]
        
        if phase_id not in snapshot.phases:
            logger.warning(f"Phase {phase_id} not found in job {job_id}")
            return None
        
        phase = snapshot.phases[phase_id]
        phase.status = "FAILED"
        phase.completed_at = datetime.now()
        
        error_entry = {
            "message": error,
            "timestamp": datetime.now().isoformat(),
            "details": error_details or {}
        }
        phase.errors.append(error_entry)
        
        # Update snapshot
        snapshot.failed_phases.append(phase_id)
        snapshot.total_errors += 1
        snapshot.status = "FAILED"
        
        # Generate alert
        self._generate_alert(
            job_id=job_id,
            alert_type="PHASE_FAILURE",
            severity="ERROR",
            message=f"Phase {phase_id} failed: {error}",
            details=error_details
        )
        
        logger.error(f"Job {job_id}: Phase {phase_id} failed - {error}")
        return phase
    
    def record_sub_phase(
        self,
        job_id: str,
        phase_id: str,
        sub_phase_name: str,
        metrics: Dict[str, Any]
    ):
        """Record sub-phase metrics.
        
        Args:
            job_id: Job identifier
            phase_id: Parent phase identifier
            sub_phase_name: Sub-phase name
            metrics: Metrics to record
        """
        if job_id not in self.active_jobs:
            return
        
        snapshot = self.active_jobs[job_id]
        
        if phase_id not in snapshot.phases:
            return
        
        phase = snapshot.phases[phase_id]
        phase.sub_phases[sub_phase_name] = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
    
    def record_resource_usage(
        self,
        job_id: str,
        cpu_percent: float,
        memory_mb: float,
        phase_id: Optional[str] = None
    ):
        """Record resource usage at a point in time.
        
        Args:
            job_id: Job identifier
            cpu_percent: CPU usage percentage
            memory_mb: Memory usage in MB
            phase_id: Optional phase identifier
        """
        if job_id not in self.active_jobs:
            return
        
        snapshot = self.active_jobs[job_id]
        
        # Record in timeline
        snapshot.resource_timeline.append({
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
            "phase_id": phase_id
        })
        
        # Update peak values
        if memory_mb > snapshot.total_memory_peak_mb:
            snapshot.total_memory_peak_mb = memory_mb
        
        # Update current phase if applicable
        if phase_id and phase_id in snapshot.phases:
            phase = snapshot.phases[phase_id]
            phase.cpu_usage_percent = cpu_percent
            phase.memory_usage_mb = memory_mb
    
    def complete_job(
        self,
        job_id: str,
        final_artifacts: Optional[List[str]] = None
    ):
        """Complete job monitoring.
        
        Args:
            job_id: Job identifier
            final_artifacts: Final artifacts produced
        """
        if job_id not in self.active_jobs:
            return
        
        snapshot = self.active_jobs[job_id]
        snapshot.status = "COMPLETED"
        snapshot.completed_at = datetime.now()
        
        if snapshot.started_at:
            elapsed = (snapshot.completed_at - snapshot.started_at).total_seconds()
            snapshot.total_execution_time_ms = elapsed * 1000
        
        if final_artifacts:
            snapshot.total_artifacts += len(final_artifacts)
        
        # Calculate progress
        snapshot.progress_percent = 100
        
        # Move to completed
        self.completed_jobs[job_id] = snapshot
        del self.active_jobs[job_id]
        
        logger.info(
            f"Job {job_id} completed in {snapshot.total_execution_time_ms:.2f}ms"
        )
    
    def get_job_snapshot(self, job_id: str) -> Optional[PipelineExecutionSnapshot]:
        """Get current snapshot for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            PipelineExecutionSnapshot or None
        """
        return self.active_jobs.get(job_id) or self.completed_jobs.get(job_id)
    
    def get_phase_metrics(
        self,
        job_id: str,
        phase_id: str
    ) -> Optional[PhaseMetrics]:
        """Get metrics for a specific phase.
        
        Args:
            job_id: Job identifier
            phase_id: Phase identifier
            
        Returns:
            PhaseMetrics or None
        """
        snapshot = self.get_job_snapshot(job_id)
        if not snapshot:
            return None
        
        return snapshot.phases.get(phase_id)
    
    def get_phase_history(self, phase_id: str, limit: int = 10) -> List[PhaseMetrics]:
        """Get historical metrics for a phase.
        
        Args:
            phase_id: Phase identifier
            limit: Maximum number of historical records
            
        Returns:
            List of PhaseMetrics
        """
        history = self.phase_history.get(phase_id, [])
        return history[-limit:]
    
    def get_performance_trends(
        self,
        phase_id: str,
        metric_type: MetricType = MetricType.EXECUTION_TIME
    ) -> Dict[str, Any]:
        """Get performance trends for a phase.
        
        Args:
            phase_id: Phase identifier
            metric_type: Type of metric to analyze
            
        Returns:
            Trends data
        """
        history = self.phase_history.get(phase_id, [])
        
        if not history:
            return {
                "phase_id": phase_id,
                "metric_type": metric_type.value,
                "count": 0,
                "avg": 0.0,
                "min": 0.0,
                "max": 0.0,
                "trend": []
            }
        
        values = []
        for phase_metrics in history:
            if metric_type == MetricType.EXECUTION_TIME:
                values.append(phase_metrics.execution_time_ms)
            elif metric_type == MetricType.MEMORY_USAGE:
                values.append(phase_metrics.memory_usage_mb)
            elif metric_type == MetricType.CPU_USAGE:
                values.append(phase_metrics.cpu_usage_percent)
            elif metric_type == MetricType.ERROR_COUNT:
                values.append(len(phase_metrics.errors))
        
        return {
            "phase_id": phase_id,
            "metric_type": metric_type.value,
            "count": len(values),
            "avg": sum(values) / len(values) if values else 0.0,
            "min": min(values) if values else 0.0,
            "max": max(values) if values else 0.0,
            "trend": values[-20:]  # Last 20 data points
        }
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts.
        
        Returns:
            List of alert dictionaries
        """
        return self.active_alerts.copy()
    
    def _check_phase_alerts(self, job_id: str, phase: PhaseMetrics):
        """Check if phase metrics exceed alert thresholds.
        
        Args:
            job_id: Job identifier
            phase: Phase metrics to check
        """
        # Check execution time
        if phase.execution_time_ms > self.alert_thresholds["execution_time_ms"]:
            self._generate_alert(
                job_id=job_id,
                alert_type="SLOW_PHASE",
                severity="WARNING",
                message=f"Phase {phase.phase_id} took {phase.execution_time_ms:.0f}ms",
                details={"threshold": self.alert_thresholds["execution_time_ms"]}
            )
        
        # Check memory usage
        if phase.memory_usage_mb > self.alert_thresholds["memory_usage_mb"]:
            self._generate_alert(
                job_id=job_id,
                alert_type="HIGH_MEMORY",
                severity="WARNING",
                message=f"Phase {phase.phase_id} used {phase.memory_usage_mb:.0f}MB",
                details={"threshold": self.alert_thresholds["memory_usage_mb"]}
            )
        
        # Check error count
        if len(phase.errors) >= self.alert_thresholds["error_count"]:
            self._generate_alert(
                job_id=job_id,
                alert_type="HIGH_ERROR_COUNT",
                severity="ERROR",
                message=f"Phase {phase.phase_id} had {len(phase.errors)} errors",
                details={"errors": phase.errors}
            )
    
    def _generate_alert(
        self,
        job_id: str,
        alert_type: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Generate an alert.
        
        Args:
            job_id: Job identifier
            alert_type: Type of alert
            severity: Alert severity (INFO, WARNING, ERROR)
            message: Alert message
            details: Additional details
        """
        alert = {
            "id": f"alert_{int(time.time() * 1000)}",
            "job_id": job_id,
            "type": alert_type,
            "severity": severity,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        self.active_alerts.append(alert)
        logger.warning(f"Alert generated: {alert_type} - {message}")
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert.
        
        Args:
            alert_id: Alert identifier
        """
        for alert in self.active_alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                logger.info(f"Alert {alert_id} acknowledged")
                break
    
    def clear_acknowledged_alerts(self):
        """Remove acknowledged alerts."""
        self.active_alerts = [
            alert for alert in self.active_alerts 
            if not alert.get("acknowledged", False)
        ]
    
    def export_snapshot(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Export complete snapshot as dictionary.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dictionary representation or None
        """
        snapshot = self.get_job_snapshot(job_id)
        if not snapshot:
            return None
        
        return {
            "job_id": snapshot.job_id,
            "filename": snapshot.filename,
            "status": snapshot.status,
            "started_at": snapshot.started_at.isoformat() if snapshot.started_at else None,
            "completed_at": snapshot.completed_at.isoformat() if snapshot.completed_at else None,
            "total_execution_time_ms": snapshot.total_execution_time_ms,
            "progress_percent": snapshot.progress_percent,
            "current_phase": snapshot.current_phase,
            "completed_phases": snapshot.completed_phases,
            "failed_phases": snapshot.failed_phases,
            "phases": {
                phase_id: self._export_phase_metrics(metrics)
                for phase_id, metrics in snapshot.phases.items()
            },
            "total_memory_peak_mb": snapshot.total_memory_peak_mb,
            "total_cpu_avg_percent": snapshot.total_cpu_avg_percent,
            "total_artifacts": snapshot.total_artifacts,
            "total_errors": snapshot.total_errors,
            "total_warnings": snapshot.total_warnings,
            "resource_timeline": snapshot.resource_timeline,
            "checkpoints": snapshot.checkpoints
        }
    
    def _export_phase_metrics(self, metrics: PhaseMetrics) -> Dict[str, Any]:
        """Export phase metrics as dictionary.
        
        Args:
            metrics: PhaseMetrics instance
            
        Returns:
            Dictionary representation
        """
        return {
            "phase_id": metrics.phase_id,
            "phase_name": metrics.phase_name,
            "status": metrics.status,
            "started_at": metrics.started_at.isoformat() if metrics.started_at else None,
            "completed_at": metrics.completed_at.isoformat() if metrics.completed_at else None,
            "execution_time_ms": metrics.execution_time_ms,
            "memory_usage_mb": metrics.memory_usage_mb,
            "cpu_usage_percent": metrics.cpu_usage_percent,
            "sub_phases": metrics.sub_phases,
            "artifacts_produced": metrics.artifacts_produced,
            "errors": metrics.errors,
            "warnings": metrics.warnings,
            "throughput_items_per_sec": metrics.throughput_items_per_sec,
            "items_processed": metrics.items_processed,
            "signals_emitted": metrics.signals_emitted,
            "signals_consumed": metrics.signals_consumed,
            "custom_metrics": metrics.custom_metrics
        }


# Global monitor instance
_monitor_instance: Optional[EnhancedPipelineMonitor] = None


def get_monitor() -> EnhancedPipelineMonitor:
    """Get global monitor instance.
    
    Returns:
        EnhancedPipelineMonitor instance
    """
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = EnhancedPipelineMonitor()
    return _monitor_instance
