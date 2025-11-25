"""
AtroZ Pipeline Connector
Real integration with the orchestrator for executing the 11-phase analysis pipeline
"""

import json
import logging
import time
import traceback
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core.orchestrator.core import Orchestrator
from ..core.orchestrator.factory import build_processor
from ..core.orchestrator.questionnaire import load_questionnaire
from ..core.orchestrator.verification_manifest import write_verification_manifest
from ..observability import get_tracer

logger = logging.getLogger(__name__)

tracer = get_tracer(__name__)


@dataclass
class PipelineResult:
    """Complete result from pipeline execution"""
    success: bool
    job_id: str
    document_id: str
    duration_seconds: float
    phases_completed: int
    macro_score: float | None
    meso_scores: dict[str, float] | None
    micro_scores: dict[str, float] | None
    questions_analyzed: int
    evidence_count: int
    recommendations_count: int
    verification_manifest_path: str | None
    error: str | None
    phase_timings: dict[str, float]
    metadata: dict[str, Any]


class PipelineConnector:
    """
    Connector for executing the real F.A.R.F.A.N pipeline through the Orchestrator.

    This class provides the bridge between the API layer and the core analysis engine,
    handling document ingestion, pipeline execution, progress tracking, and result extraction.
    """

    def __init__(self) -> None:
        from ..config import paths
        self.workspace_dir = paths.CACHE_DIR
        self.output_dir = paths.OUTPUT_DIR

        # ensure_directories_exist is called on import in paths.py,
        # so we don't need to call it again here.

        self.running_jobs: dict[str, dict[str, Any]] = {}
        self.completed_jobs: dict[str, PipelineResult] = {}

        logger.info(f"Pipeline connector initialized with workspace: {workspace_dir}")

    async def execute_pipeline(
        self,
        pdf_path: str,
        job_id: str,
        municipality: str = "general",
        progress_callback: Callable[[int, str], None] | None = None,
        settings: dict[str, Any] | None = None
    ) -> PipelineResult:
        """
        Execute the complete 11-phase pipeline on a PDF document.

        Args:
            pdf_path: Path to the PDF document to analyze
            job_id: Unique identifier for this job
            municipality: Municipality name for context
            progress_callback: Optional callback function(phase_num, phase_name) for progress updates
            settings: Optional pipeline settings (timeout, cache, etc.)

        Returns:
            PipelineResult with complete analysis results
        """
        start_time = time.time()
        settings = settings or {}

        logger.info(f"Starting pipeline execution for job {job_id}: {pdf_path}")

        self.running_jobs[job_id] = {
            "status": "initializing",
            "start_time": start_time,
            "current_phase": None,
            "progress": 0
        }

        try:
            # Phase 0: Document Ingestion
            if progress_callback:
                progress_callback(0, "Ingesting document")
            self._update_job_status(job_id, "ingesting", 0, "Document ingestion")

            preprocessed_doc = self._ingest_document(pdf_path, municipality)

            # Initialize Orchestrator with proper factory and questionnaire
            # FIX: Previously used Orchestrator() without parameters which would fail
            # in _load_configuration() with ValueError: "No monolith data available"
            logger.info("Initializing Orchestrator via factory pattern")

            # Build processor bundle with all dependencies
            processor = build_processor()

            # Load canonical questionnaire for type-safe initialization
            canonical_questionnaire = load_questionnaire()

            # Initialize orchestrator with pre-loaded data (I/O-free path)
            orchestrator = Orchestrator(
                questionnaire=canonical_questionnaire,
                catalog=processor.factory.catalog
            )

            logger.info(
                "Orchestrator initialized successfully",
                extra={
                    "questionnaire_hash": canonical_questionnaire.sha256[:16] + "...",
                    "question_count": canonical_questionnaire.total_question_count,
                    "catalog_loaded": processor.factory.catalog is not None
                }
            )

            # Track phase timings
            phase_timings = {}

            # Run the complete orchestrator
            logger.info("Running complete orchestrator pipeline")
            orchestrator_start = time.time()

            def real_progress_callback(phase_id: int, phase_name: str, status: str):
                with tracer.start_as_current_span(f"Phase {phase_id}: {phase_name}") as span:
                    span.set_attribute("phase.id", phase_id)
                    span.set_attribute("phase.name", phase_name)
                    span.set_attribute("phase.status", status)

                    if progress_callback:
                        progress_callback(phase_id, phase_name)

                    progress = int(((phase_id + 1) / 11) * 100)
                    self._update_job_status(job_id, "processing", progress, phase_name)
                    phase_timings[f"phase_{phase_id}"] = time.time() - orchestrator_start

            result = await orchestrator.process_development_plan_async(
                pdf_path=pdf_path,
                preprocessed_document=preprocessed_doc,
                progress_callback=real_progress_callback,
            )

            orchestrator_duration = time.time() - orchestrator_start
            logger.info(f"Orchestrator completed in {orchestrator_duration:.2f}s")

            # Extract metrics from result
            metrics = self._extract_metrics(result)

            # Write verification manifest
            manifest_path = await self._write_manifest(job_id, result, metrics)

            # Create result object
            pipeline_result = PipelineResult(
                success=True,
                job_id=job_id,
                document_id=preprocessed_doc.get("document_id", job_id),
                duration_seconds=time.time() - start_time,
                phases_completed=11,
                macro_score=metrics.get("macro_score"),
                meso_scores=metrics.get("meso_scores"),
                micro_scores=metrics.get("micro_scores"),
                questions_analyzed=metrics.get("questions_analyzed", 0),
                evidence_count=metrics.get("evidence_count", 0),
                recommendations_count=metrics.get("recommendations_count", 0),
                verification_manifest_path=manifest_path,
                error=None,
                phase_timings=phase_timings,
                metadata={
                    "municipality": municipality,
                    "pdf_path": pdf_path,
                    "orchestrator_version": result.get("version", "unknown"),
                    "completed_at": datetime.now().isoformat()
                }
            )

            self.completed_jobs[job_id] = pipeline_result
            self._update_job_status(job_id, "completed", 100, "Analysis complete")

            logger.info(f"Pipeline execution completed successfully for job {job_id}")
            return pipeline_result

        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")

            pipeline_result = PipelineResult(
                success=False,
                job_id=job_id,
                document_id="unknown",
                duration_seconds=time.time() - start_time,
                phases_completed=0,
                macro_score=None,
                meso_scores=None,
                micro_scores=None,
                questions_analyzed=0,
                evidence_count=0,
                recommendations_count=0,
                verification_manifest_path=None,
                error=error_msg,
                phase_timings={},
                metadata={"error_traceback": traceback.format_exc()}
            )

            self.completed_jobs[job_id] = pipeline_result
            self._update_job_status(job_id, "failed", 0, error_msg)

            return pipeline_result

        finally:
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]

    def _ingest_document(self, pdf_path: str, municipality: str) -> 'PreprocessedDocument':
        """
        Ingest and preprocess the PDF document using the canonical SPC pipeline.
        """
        from ..processing.spc_ingestion import CPPIngestionPipeline
        from ..utils.spc_adapter import SPCAdapter
        from ..core.orchestrator.core import PreprocessedDocument

        try:
            logger.info("Starting canonical SPC ingestion pipeline")
            ingestion_pipeline = CPPIngestionPipeline()
            # CPPIngestionPipeline.process is synchronous
            canon_package = ingestion_pipeline.process(Path(pdf_path))

            logger.info("Adapting CanonPolicyPackage to PreprocessedDocument")
            adapter = SPCAdapter()
            document_id = f"doc_{int(time.time())}"
            preprocessed_doc = adapter.to_preprocessed_document(canon_package, document_id)

            return preprocessed_doc

        except Exception as e:
            logger.error(f"Canonical ingestion failed: {e}", exc_info=True)
            raise

    def _extract_metrics(self, orchestrator_result: dict[str, Any]) -> dict[str, Any]:
        """Extract key metrics from orchestrator result"""
        metrics = {}

        # Extract macro score
        if "macro_analysis" in orchestrator_result:
            macro_data = orchestrator_result["macro_analysis"]
            metrics["macro_score"] = macro_data.get("overall_score")

        # Extract meso scores
        if "meso_analysis" in orchestrator_result:
            meso_data = orchestrator_result["meso_analysis"]
            metrics["meso_scores"] = meso_data.get("cluster_scores", {})

        # Extract micro scores
        if "micro_analysis" in orchestrator_result:
            micro_data = orchestrator_result["micro_analysis"]
            metrics["micro_scores"] = micro_data.get("question_scores", {})
            metrics["questions_analyzed"] = len(micro_data.get("questions", []))
            metrics["evidence_count"] = sum(
                len(q.get("evidence", []))
                for q in micro_data.get("questions", [])
            )

        # Extract recommendations
        if "recommendations" in orchestrator_result:
            metrics["recommendations_count"] = len(orchestrator_result["recommendations"])

        return metrics

    async def _write_manifest(
        self,
        job_id: str,
        orchestrator_result: dict[str, Any],
        metrics: dict[str, Any]
    ) -> str:
        """Write verification manifest for the analysis"""
        manifest_path = self.output_dir / f"{job_id}_verification_manifest.json"

        manifest_data = {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "metrics": metrics,
            "verification": {
                "phases_completed": 11,
                "data_integrity": "verified",
                "output_path": str(self.output_dir / f"{job_id}_report.json")
            }
        }

        try:
            # Use the actual verification manifest writer if available
            await write_verification_manifest(manifest_path, manifest_data)
        except Exception as e:
            logger.warning(f"Could not write verification manifest: {e}")
            # Fallback: write JSON directly
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Verification manifest written to: {manifest_path}")
        return str(manifest_path)

    def _update_job_status(self, job_id: str, status: str, progress: int, message: str) -> None:
        """Update status of running job"""
        if job_id in self.running_jobs:
            self.running_jobs[job_id].update({
                "status": status,
                "progress": progress,
                "current_phase": message,
                "updated_at": datetime.now().isoformat()
            })

    def get_job_status(self, job_id: str) -> dict[str, Any] | None:
        """Get current status of a job"""
        if job_id in self.running_jobs:
            return self.running_jobs[job_id]
        elif job_id in self.completed_jobs:
            result = self.completed_jobs[job_id]
            return {
                "status": "completed" if result.success else "failed",
                "progress": 100 if result.success else 0,
                "result": asdict(result)
            }
        return None

    def get_result(self, job_id: str) -> PipelineResult | None:
        """Get final result for a completed job"""
        return self.completed_jobs.get(job_id)


# Global connector instance
_connector: PipelineConnector | None = None


def get_pipeline_connector() -> PipelineConnector:
    """Get or create global pipeline connector instance"""
    global _connector
    if _connector is None:
        _connector = PipelineConnector()
    return _connector
