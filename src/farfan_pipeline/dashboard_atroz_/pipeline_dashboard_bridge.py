"""Pipeline-Dashboard Bridge: Real-time integration between orchestrator and dashboard.

This module provides the critical bridge between the UnifiedOrchestrator and the
ATROZ Dashboard, enabling real-time updates, SISAS metrics, and bidirectional state sync.

Architecture:
    UnifiedOrchestrator → Bridge → SocketIO → Frontend
                       ↓
                    SISAS SDO → Metrics → Dashboard
                       ↓
                 Enhanced Monitor → Granular Tracking
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from farfan_pipeline.dashboard_atroz_.dashboard_data_service import DashboardDataService
from farfan_pipeline.dashboard_atroz_.monitoring_enhanced import get_monitor
from farfan_pipeline.orchestration import PhaseID

logger = logging.getLogger(__name__)


@dataclass
class JobProgress:
    """Track job execution progress."""

    job_id: str
    filename: str
    status: str  # QUEUED, RUNNING, COMPLETED, FAILED
    current_phase: Optional[PhaseID] = None
    phase_progress: Dict[PhaseID, dict] = field(default_factory=dict)
    total_progress: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    sisas_metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Path] = field(default_factory=dict)


@dataclass
class PipelineEvent:
    """Pipeline event for dashboard updates."""

    event_type: str  # phase_start, phase_progress, phase_complete, phase_failed, job_complete
    job_id: str
    phase_id: Optional[PhaseID] = None
    phase_name: Optional[str] = None
    progress: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class PipelineDashboardBridge:
    """Bridge between UnifiedOrchestrator and Dashboard Server.

    Responsibilities:
        1. Listen to orchestrator phase events
        2. Transform orchestrator data for dashboard consumption
        3. Emit WebSocket events with real-time updates
        4. Integrate SISAS metrics into dashboard payloads
        5. Manage job state and artifacts
        6. Provide dashboard data service integration

    Usage:
        bridge = PipelineDashboardBridge(orchestrator, socketio)
        bridge.start()

        # Submit job
        job_id = bridge.submit_job(pdf_path, "plan.pdf")

        # Query status
        status = bridge.get_job_status(job_id)

        # Get SISAS metrics
        metrics = bridge.get_sisas_metrics()
    """

    def __init__(
        self,
        orchestrator,  # UnifiedOrchestrator instance
        socketio,  # Flask-SocketIO instance
        dashboard_data_service: Optional[DashboardDataService] = None,
    ):
        """Initialize bridge.

        Args:
            orchestrator: UnifiedOrchestrator instance
            socketio: Flask-SocketIO instance for WebSocket emissions
            dashboard_data_service: Optional DashboardDataService for data transformation
        """
        self.orchestrator = orchestrator
        self.socketio = socketio
        self.data_service = dashboard_data_service or DashboardDataService()
        
        # Get enhanced monitor
        self.monitor = get_monitor()

        # Job tracking
        self.active_jobs: Dict[str, JobProgress] = {}
        self.completed_jobs: Dict[str, JobProgress] = {}
        self.job_lock = threading.RLock()

        # Callbacks
        self.event_callbacks: List[Callable[[PipelineEvent], None]] = []

        # Metrics cache
        self.last_sisas_metrics: Dict[str, Any] = {}
        self.metrics_update_interval = 5.0  # seconds

        # Background thread for metrics updates
        self._metrics_thread: Optional[threading.Thread] = None
        self._running = False

        logger.info("PipelineDashboardBridge initialized")

    def start(self):
        """Start background monitoring and metrics collection."""
        if self._running:
            logger.warning("Bridge already running")
            return

        self._running = True

        # Start metrics collection thread
        self._metrics_thread = threading.Thread(target=self._collect_sisas_metrics, daemon=True)
        self._metrics_thread.start()

        logger.info("PipelineDashboardBridge started")

    def stop(self):
        """Stop background monitoring."""
        self._running = False
        if self._metrics_thread:
            self._metrics_thread.join(timeout=5.0)
        logger.info("PipelineDashboardBridge stopped")

    def submit_job(self, pdf_path: Path, filename: str, metadata: Optional[Dict] = None) -> str:
        """Submit new job to pipeline.

        Args:
            pdf_path: Path to PDF file
            filename: Original filename
            metadata: Optional metadata dict

        Returns:
            job_id: Unique job identifier
        """
        job_id = f"job_{int(time.time() * 1000)}"

        # Create job progress tracker
        job = JobProgress(
            job_id=job_id,
            filename=filename,
            status="QUEUED",
            started_at=datetime.now(),
        )

        with self.job_lock:
            self.active_jobs[job_id] = job
        
        # Start monitoring in enhanced monitor
        self.monitor.start_job_monitoring(job_id, filename, metadata)

        # Emit job creation event
        self._emit_event(
            PipelineEvent(
                event_type="job_created",
                job_id=job_id,
                data={"filename": filename, "metadata": metadata or {}},
            )
        )

        # Submit to orchestrator in background
        threading.Thread(
            target=self._execute_pipeline,
            args=(job_id, pdf_path, metadata),
            daemon=True,
        ).start()

        logger.info(f"Job {job_id} submitted for file: {filename}")
        return job_id

    def _execute_pipeline(self, job_id: str, pdf_path: Path, metadata: Optional[Dict]):
        """Execute pipeline with real-time updates.

        Args:
            job_id: Job identifier
            pdf_path: Path to PDF file
            metadata: Optional metadata
        """
        try:
            # Update job status
            self._update_job_status(job_id, "RUNNING")

            # Wire up phase callbacks
            original_emit = getattr(self.orchestrator, "_emit_phase_signal", None)

            def phase_callback(phase_id, event_type, payload, policy_area="ALL"):
                """Intercept phase signals and emit to dashboard."""
                # Call original if exists
                if original_emit:
                    original_emit(phase_id, event_type, payload, policy_area)

                # Transform for dashboard
                self._handle_phase_event(job_id, phase_id, event_type, payload)

            # Monkey-patch orchestrator (temporary until orchestrator natively supports callbacks)
            if hasattr(self.orchestrator, "_emit_phase_signal"):
                self.orchestrator._emit_phase_signal = phase_callback

            # Execute pipeline
            logger.info(f"Executing pipeline for job {job_id}")
            result = self.orchestrator.execute_full_pipeline(str(pdf_path))

            # Extract phase outputs for dashboard visualization (ACCURACY IMPROVEMENT)
            phase_outputs = self._extract_phase_outputs_for_dashboard()

            # Update job with results
            with self.job_lock:
                if job_id in self.active_jobs:
                    job = self.active_jobs[job_id]
                    job.status = "COMPLETED"
                    job.completed_at = datetime.now()
                    job.total_progress = 100

                    # Move to completed
                    self.completed_jobs[job_id] = job
                    del self.active_jobs[job_id]
                    
                    # Complete job in enhanced monitor
                    self.monitor.complete_job(job_id, final_artifacts=None)

            # Emit completion event with full phase data (AUTOMATICITY IMPROVEMENT)
            self._emit_event(
                PipelineEvent(
                    event_type="job_completed",
                    job_id=job_id,
                    progress=100,
                    data={
                        "status": "COMPLETED",
                        "result": self._serialize_result(result),
                        "duration": (job.completed_at - job.started_at).total_seconds()
                        if job.completed_at and job.started_at
                        else None,
                        "phase_outputs": phase_outputs,  # New: Include phase outputs
                    },
                )
            )
            
            # Emit automatic report ready event (AUTOMATICITY IMPROVEMENT)
            if phase_outputs.get("macro_score"):
                self.socketio.emit(
                    "report_ready",
                    {
                        "job_id": job_id,
                        "timestamp": datetime.now().isoformat(),
                        "macro_score": phase_outputs.get("macro_score"),
                        "cluster_scores": phase_outputs.get("cluster_scores"),
                        "report_available": True,
                    },
                )

            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.exception(f"Job {job_id} failed: {e}")

            # Update job status
            with self.job_lock:
                if job_id in self.active_jobs:
                    job = self.active_jobs[job_id]
                    job.status = "FAILED"
                    job.error = str(e)
                    job.completed_at = datetime.now()

                    # Move to completed
                    self.completed_jobs[job_id] = job
                    del self.active_jobs[job_id]

            # Emit failure event
            self._emit_event(
                PipelineEvent(
                    event_type="job_failed",
                    job_id=job_id,
                    data={"status": "FAILED", "error": str(e)},
                )
            )

    def _handle_phase_event(self, job_id: str, phase_id: PhaseID, event_type: str, payload: Dict):
        """Handle phase lifecycle event from orchestrator.

        Args:
            job_id: Job identifier
            phase_id: Phase identifier
            event_type: PHASE_START, PHASE_COMPLETE, PHASE_FAILED
            payload: Event payload
        """
        with self.job_lock:
            if job_id not in self.active_jobs:
                logger.warning(f"Job {job_id} not found in active jobs")
                return

            job = self.active_jobs[job_id]

        # Get phase name
        phase_name = self._get_phase_name(phase_id)
        
        # Handle different event types with enhanced monitoring
        if event_type == "PHASE_START":
            # Start phase in enhanced monitor
            self.monitor.start_phase(
                job_id=job_id,
                phase_id=phase_id.value,
                phase_name=phase_name,
                metadata=payload
            )
        elif event_type == "PHASE_COMPLETE":
            # Complete phase in enhanced monitor
            artifacts = payload.get("artifacts", [])
            self.monitor.complete_phase(
                job_id=job_id,
                phase_id=phase_id.value,
                artifacts=artifacts,
                metrics=payload
            )
        elif event_type == "PHASE_FAILED":
            # Fail phase in enhanced monitor
            error = payload.get("error", "Unknown error")
            self.monitor.fail_phase(
                job_id=job_id,
                phase_id=phase_id.value,
                error=error,
                error_details=payload
            )

        # Update phase progress
        phase_data = {
            "event": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat(),
        }

        with self.job_lock:
            job.phase_progress[phase_id] = phase_data

        # Calculate total progress (approximate based on phase number)
        phase_num = int(phase_id.value[1:])  # P00 -> 0, P01 -> 1, etc.
        total_phases = 10
        progress = int((phase_num / total_phases) * 100)

        if event_type == "PHASE_COMPLETE":
            progress = min(int(((phase_num + 1) / total_phases) * 100), 99)

        with self.job_lock:
            job.current_phase = phase_id
            job.total_progress = progress

        # Get SISAS metrics if available
        sisas_metrics = {}
        if hasattr(self.orchestrator, "get_sisas_metrics"):
            try:
                sisas_metrics = self.orchestrator.get_sisas_metrics()
                with self.job_lock:
                    job.sisas_metrics = sisas_metrics
            except Exception as e:
                logger.warning(f"Failed to get SISAS metrics: {e}")

        # Emit dashboard event
        event = PipelineEvent(
            event_type="pipeline_progress",
            job_id=job_id,
            phase_id=phase_id,
            phase_name=self._get_phase_name(phase_id),
            progress=progress,
            data={
                "phase_event": event_type,
                "phase_payload": payload,
                "sisas_metrics": sisas_metrics,
            },
        )
        self._emit_event(event)

    def _get_phase_name(self, phase_id: PhaseID) -> str:
        """Get human-readable phase name.

        Args:
            phase_id: Phase identifier

        Returns:
            Phase name string
        """
        phase_names = {
            PhaseID.P00: "Document Assembly",
            PhaseID.P01: "Text Extraction",
            PhaseID.P02: "Semantic Enrichment",
            PhaseID.P03: "Layer Scoring",
            PhaseID.P04: "Micro Analysis (300Q)",
            PhaseID.P05: "Meso Analysis (4CL)",
            PhaseID.P06: "Macro Analysis (6DIM)",
            PhaseID.P07: "Cross-Dimensional Aggregation",
            PhaseID.P08: "Integration & Validation",
            PhaseID.P09: "Report Generation",
        }
        return phase_names.get(phase_id, f"Phase {phase_id.value}")

    def _collect_sisas_metrics(self):
        """Background thread to collect SISAS metrics periodically."""
        while self._running:
            try:
                if hasattr(self.orchestrator, "get_sisas_metrics"):
                    metrics = self.orchestrator.get_sisas_metrics()
                    self.last_sisas_metrics = metrics

                    # Emit metrics update
                    self.socketio.emit(
                        "sisas_metrics_update",
                        {
                            "timestamp": datetime.now().isoformat(),
                            "metrics": metrics,
                        },
                    )

            except Exception as e:
                logger.warning(f"Failed to collect SISAS metrics: {e}")

            time.sleep(self.metrics_update_interval)

    def _emit_event(self, event: PipelineEvent):
        """Emit event to dashboard via WebSocket.

        Args:
            event: Pipeline event
        """
        # Convert to dict
        payload = {
            "job_id": event.job_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
        }

        if event.phase_id:
            payload["phase"] = int(event.phase_id.value[1:])  # P00 -> 0
            payload["phase_name"] = event.phase_name

        if event.progress:
            payload["progress"] = event.progress

        payload.update(event.data)

        # Emit via SocketIO
        self.socketio.emit(event.event_type, payload)

        # Call registered callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.warning(f"Callback failed: {e}")

    def register_callback(self, callback: Callable[[PipelineEvent], None]):
        """Register callback for pipeline events.

        Args:
            callback: Callback function taking PipelineEvent
        """
        self.event_callbacks.append(callback)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a job.

        Args:
            job_id: Job identifier

        Returns:
            Job status dict or None if not found
        """
        with self.job_lock:
            job = self.active_jobs.get(job_id) or self.completed_jobs.get(job_id)
            if not job:
                return None

            return {
                "job_id": job.job_id,
                "filename": job.filename,
                "status": job.status,
                "current_phase": job.current_phase.value if job.current_phase else None,
                "total_progress": job.total_progress,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error": job.error,
                "sisas_metrics": job.sisas_metrics,
                "phase_history": {
                    phase.value: data for phase, data in job.phase_progress.items()
                },
            }

    def get_all_jobs(self) -> Dict[str, Any]:
        """Get status of all jobs.

        Returns:
            Dict with active and completed jobs
        """
        with self.job_lock:
            return {
                "active_jobs": [
                    self.get_job_status(job_id) for job_id in self.active_jobs.keys()
                ],
                "completed_jobs": [
                    self.get_job_status(job_id) for job_id in self.completed_jobs.keys()
                ],
            }

    def get_sisas_metrics(self) -> Dict[str, Any]:
        """Get latest SISAS metrics.

        Returns:
            SISAS metrics dict
        """
        return self.last_sisas_metrics.copy()

    def _update_job_status(self, job_id: str, status: str):
        """Update job status.

        Args:
            job_id: Job identifier
            status: New status
        """
        with self.job_lock:
            if job_id in self.active_jobs:
                self.active_jobs[job_id].status = status

    def _serialize_result(self, result) -> Dict[str, Any]:
        """Serialize pipeline result for JSON.

        Args:
            result: Pipeline result object

        Returns:
            Serialized dict
        """
        # Handle different result types
        if hasattr(result, "to_dict"):
            return result.to_dict()
        elif hasattr(result, "__dict__"):
            return {k: str(v) for k, v in result.__dict__.items()}
        else:
            return {"result": str(result)}

    def _extract_phase_outputs_for_dashboard(self) -> Dict[str, Any]:
        """Extract relevant phase outputs for dashboard visualization.
        
        Extracts data from orchestrator context for:
        - Macro score (Phase 7) - Overall analysis score
        - Cluster scores (Phase 6) - Meso-level aggregation
        - Area scores (Phase 5) - Policy area breakdown
        - Recommendations (Phase 8) - Actionable insights
        
        Returns:
            Dict with dashboard-ready phase outputs
        """
        outputs: Dict[str, Any] = {}
        
        try:
            context = self.orchestrator.context
            
            # Extract Macro Score (Phase 7 output)
            macro_score = context.get_phase_output(PhaseID.P07) if hasattr(PhaseID, 'P07') else context.get_phase_output("P07")
            if macro_score:
                if hasattr(macro_score, "score"):
                    outputs["macro_score"] = {
                        "score": macro_score.score,
                        "quality_level": getattr(macro_score, "quality_level", "UNKNOWN"),
                        "coherence": getattr(macro_score, "cross_cutting_coherence", 0.0),
                        "alignment": getattr(macro_score, "strategic_alignment", 0.0),
                        "systemic_gaps": getattr(macro_score, "systemic_gaps", []),
                    }
                elif isinstance(macro_score, dict):
                    outputs["macro_score"] = macro_score
            
            # Extract Cluster Scores (Phase 6 output)
            cluster_scores = context.get_phase_output(PhaseID.P06) if hasattr(PhaseID, 'P06') else context.get_phase_output("P06")
            if cluster_scores:
                outputs["cluster_scores"] = []
                for cs in (cluster_scores if isinstance(cluster_scores, list) else [cluster_scores]):
                    if hasattr(cs, "cluster_id"):
                        outputs["cluster_scores"].append({
                            "cluster_id": cs.cluster_id,
                            "score": cs.score,
                            "name": getattr(cs, "cluster_name", cs.cluster_id),
                        })
                    elif isinstance(cs, dict):
                        outputs["cluster_scores"].append(cs)
            
            # Extract Area Scores (Phase 5 output)
            area_scores = context.get_phase_output(PhaseID.P05) if hasattr(PhaseID, 'P05') else context.get_phase_output("P05")
            if area_scores:
                outputs["area_scores"] = []
                for area in (area_scores if isinstance(area_scores, list) else [area_scores]):
                    if hasattr(area, "area_id"):
                        outputs["area_scores"].append({
                            "area_id": area.area_id,
                            "score": area.score,
                            "name": getattr(area, "area_name", area.area_id),
                        })
                    elif isinstance(area, dict):
                        outputs["area_scores"].append(area)
            
            # Extract Recommendations (Phase 8 output)
            recommendations = context.get_phase_output(PhaseID.P08) if hasattr(PhaseID, 'P08') else context.get_phase_output("P08")
            if recommendations:
                outputs["recommendations"] = recommendations if isinstance(recommendations, dict) else {"data": recommendations}
            
            # Add phase execution summary
            outputs["phase_summary"] = {
                "phases_completed": list(context.phase_results.keys()) if hasattr(context, "phase_results") else [],
                "total_violations": len(context.total_violations) if hasattr(context, "total_violations") else 0,
            }
            
            logger.info(
                f"Extracted phase outputs for dashboard",
                extra={
                    "macro_score": outputs.get("macro_score") is not None,
                    "cluster_count": len(outputs.get("cluster_scores", [])),
                    "area_count": len(outputs.get("area_scores", [])),
                }
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract phase outputs: {e}")
            outputs["extraction_error"] = str(e)
        
        return outputs


# Singleton instance (optional)
_bridge_instance: Optional[PipelineDashboardBridge] = None


def get_bridge() -> Optional[PipelineDashboardBridge]:
    """Get global bridge instance."""
    return _bridge_instance


def initialize_bridge(
    orchestrator, socketio, dashboard_data_service: Optional[DashboardDataService] = None
) -> PipelineDashboardBridge:
    """Initialize global bridge instance.

    Args:
        orchestrator: UnifiedOrchestrator
        socketio: Flask-SocketIO
        dashboard_data_service: Optional DashboardDataService

    Returns:
        Bridge instance
    """
    global _bridge_instance
    _bridge_instance = PipelineDashboardBridge(orchestrator, socketio, dashboard_data_service)
    _bridge_instance.start()
    return _bridge_instance
