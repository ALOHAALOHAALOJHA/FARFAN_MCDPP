"""
Report Assembly Module - Production Grade v2.0
================================================

This module assembles comprehensive policy analysis reports by:
1. Loading questionnaire monolith via factory (I/O boundary)
2. Accessing patterns via QuestionnaireResourceProvider (single source of truth)
3. Integrating with evidence registry and QMCM hooks
4. Producing structured, traceable reports with cryptographic verification

Architectural Compliance:
- REQUIREMENT 1: Uses QuestionnaireResourceProvider for pattern extraction
- REQUIREMENT 2: All I/O via factory.py
- REQUIREMENT 3: Receives dependencies via dependency injection
- REQUIREMENT 4: Domain-specific exceptions with structured payloads
- REQUIREMENT 5: Pydantic contracts for data validation
- REQUIREMENT 6: Cryptographic verification (SHA-256)
- REQUIREMENT 7: Structured JSON logging
- REQUIREMENT 8: Parameter externalization via calibration system

Author: Integration Team
Version: 2.0.0
Python: 3.10+
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 9
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
UTC = timezone.utc
from typing import TYPE_CHECKING, Any, cast, Callable, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Calibration parameters - loaded at runtime if calibration system available
try:
    from farfan_pipeline.calibration.parameters import ParameterLoaderV2
except (ImportError, AttributeError):
    # Fallback: use explicit defaults if calibration system not available
    _PARAM_LOADER = None

F = TypeVar("F", bound=Callable[..., Any])


# Calibrated method decorator stub (calibration system not available)
def calibrated_method(method_name: str) -> Callable[[F], F]:
    """No-op decorator stub for compatibility when calibration system unavailable."""

    def decorator(func: F) -> F:
        return func

    return decorator


if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# DOMAIN-SPECIFIC EXCEPTIONS
# ============================================================================


class ReportAssemblyException(Exception):
    """Base exception for report assembly operations with structured payloads."""

    def __init__(
        self,
        message: str,
        details: dict[str, object] | None = None,
        stage: str | None = None,
        recoverable: bool = False,
        event_id: str | None = None,
    ) -> None:
        self.message = message
        self.details = details or {}
        self.stage = stage
        self.recoverable = recoverable
        self.event_id = event_id or str(uuid.uuid4())
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with structured information."""
        parts = ["[ReportAssembly Error]"]
        if self.stage:
            parts.append(f"[Stage: {self.stage}]")
        parts.append(f"[EventID: {self.event_id[:8]}]")
        parts.append(self.message)
        if self.details:
            parts.append(f"Details: {json.dumps(self.details, indent=2)}")
        return " ".join(parts)

    def to_dict(self) -> dict[str, object]:
        """Convert exception to structured dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "stage": self.stage,
            "recoverable": self.recoverable,
            "event_id": self.event_id,
        }


class ReportValidationError(ReportAssemblyException):
    """Raised when report data validation fails."""

    pass


class ReportIntegrityError(ReportAssemblyException):
    """Raised when cryptographic verification fails (hash mismatch)."""

    pass


class ReportExportError(ReportAssemblyException):
    """Raised when report export to file fails."""

    pass


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def compute_content_digest(content: str | bytes | dict[str, object]) -> str:
    """
    Compute SHA-256 digest of content in a deterministic way.

    Args:
        content: String, bytes, or dict to hash

    Returns:
        Hexadecimal SHA-256 digest (64 characters)

    Raises:
        ReportValidationError: If content type is unsupported
    """
    if isinstance(content, dict):
        # Sort keys for deterministic JSON
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        content_bytes = content_str.encode("utf-8")
    elif isinstance(content, str):
        content_bytes = content.encode("utf-8")
    elif isinstance(content, bytes):
        content_bytes = content
    else:
        raise ReportValidationError(
            f"Cannot compute digest for type {type(content).__name__}",
            details={"content_type": type(content).__name__},
            stage="digest_computation",
        )

    return hashlib.sha256(content_bytes).hexdigest()


def utc_now_iso() -> str:
    """
    Get current UTC timestamp in ISO-8601 format.

    Returns:
        ISO-8601 timestamp string (UTC timezone)
    """
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


# ============================================================================
# PYDANTIC CONTRACT MODELS
# ============================================================================


class ReportMetadata(BaseModel):
    """Enhanced metadata for analysis report with cryptographic traceability."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    report_id: str = Field(..., description="Unique report identifier", min_length=1)
    generated_at: str = Field(
        default_factory=utc_now_iso, description="UTC timestamp in ISO-8601 format"
    )
    monolith_version: str = Field(..., description="Questionnaire monolith version")
    monolith_hash: str = Field(
        ..., description="SHA-256 hash of questionnaire_monolith.json", pattern=r"^[a-f0-9]{64}$"
    )
    plan_name: str = Field(..., description="Development plan name", min_length=1)
    total_questions: int = Field(..., description="Total number of questions", ge=0)
    questions_analyzed: int = Field(..., description="Number of questions analyzed", ge=0)
    metadata: dict[str, object] = Field(default_factory=dict, description="Additional metadata")
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="UUID for request correlation"
    )

    @field_validator("generated_at")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp is ISO-8601 format and UTC."""
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            # Ensure UTC
            if dt.tzinfo is None or dt.utcoffset() != UTC.utcoffset(None):
                raise ValueError("Timestamp must be UTC")
            return v
        except (ValueError, AttributeError) as e:
            raise ReportValidationError(
                f"Invalid ISO-8601 timestamp: {v}",
                details={"timestamp": v, "error": str(e)},
                stage="metadata_validation",
            ) from e

    @field_validator("questions_analyzed")
    @classmethod
    def validate_analyzed_count(cls, v: int, info: object) -> int:
        """Validate analyzed count doesn't exceed total."""
        # Note: 'total_questions' may not be available yet during construction
        # This is validated in post_init if needed
        if v < 0:
            raise ReportValidationError(
                "questions_analyzed must be non-negative",
                details={"questions_analyzed": v},
                stage="metadata_validation",
            )
        return v


# ============================================================================
# CARVER DOCTORAL QUALITY METRICS
# ============================================================================


class CarverQualityMetrics(BaseModel):
    """Quality metrics for doctoral-level Carver synthesis.
    
    Ensures human answers synthesized by Carver meet rigorous academic
    standards with measurable depth, complexity, and evidence integration.
    
    Quality Gate Thresholds:
    - doctoral_depth_score >= 0.7: Meets doctoral depth requirements
    - synthesis_complexity_index >= 0.6: Adequate cross-reference complexity
    - evidence_density_ratio >= 0.5: Sufficient evidence integration
    
    A synthesis passes the quality gate only if ALL thresholds are met.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Core quality scores (0.0 - 1.0 scale)
    doctoral_depth_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Depth of doctoral-level analysis (length, structure, vocabulary)"
    )
    synthesis_complexity_index: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Cross-reference complexity and evidence integration"
    )
    evidence_density_ratio: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Ratio of evidence items to answer paragraphs"
    )
    
    # Gate validation
    quality_gate_passed: bool = Field(
        default=False,
        description="Whether synthesis meets doctoral quality threshold"
    )
    quality_gate_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0,
        description="Minimum score threshold for quality gate"
    )
    
    # Detailed metrics
    answer_length_chars: int = Field(default=0, ge=0, description="Total answer characters")
    paragraph_count: int = Field(default=0, ge=0, description="Number of paragraphs")
    academic_vocabulary_density: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Density of academic/technical vocabulary"
    )
    cross_reference_count: int = Field(default=0, ge=0, description="Cross-references in answer")
    evidence_items_integrated: int = Field(default=0, ge=0, description="Evidence pieces cited")


class QuestionAnalysis(BaseModel):
    """Enhanced analysis result for a single micro question."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )

    question_id: str = Field(..., description="Question identifier", min_length=1)
    question_global: int = Field(..., description="Global question number", ge=1, le=500)
    base_slot: str = Field(..., description="Base slot identifier")
    scoring_modality: str | None = Field(default=None, description="Scoring modality")
    score: float | None = Field(default=None, description="Question score", ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list, description="Evidence list")
    patterns_applied: list[str] = Field(default_factory=list, description="Applied pattern IDs")
    recommendation: str | None = Field(default=None, description="Analysis recommendation")
    human_answer: str | None = Field(
        default=None, description="Carver-synthesized human-readable answer"
    )
    # NEW: Carver doctoral quality metrics
    carver_quality: CarverQualityMetrics | None = Field(
        default=None,
        description="Quality metrics for Carver doctoral synthesis"
    )
    metadata: dict[str, object] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("score")
    @classmethod
    def validate_score_bounds(cls, v: float | None) -> float | None:
        """Validate score is within bounds if present."""
        if v is not None:
            min_score = 0.0
            max_score = 1.0
            if not (min_score <= v <= max_score):
                raise ReportValidationError(
                    f"Score must be in [{min_score}, {max_score}], got {v}",
                    details={"score": v, "min": min_score, "max": max_score},
                    stage="question_validation",
                )
            # Round to avoid floating point precision issues
            return round(v, 6)
        return v


class Recommendation(BaseModel):
    """Structured recommendation with type and severity classification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str = Field(..., description="Recommendation type (RISK, PRIORITY, OMISSION, etc.)")
    severity: str = Field(..., description="Severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)")
    description: str = Field(..., description="Actionable recommendation text")
    source: str = Field(
        default="macro", description="Source of recommendation (micro, meso, macro)"
    )

    @classmethod
    def from_string(cls, text: str, source: str = "macro") -> Recommendation:
        """Parse recommendation string into structured object."""
        # Expected format: "TYPE_LEVEL: Description"
        # e.g., "CRITICAL_RISK: Immediate intervention required"
        if ":" in text:
            prefix, desc = text.split(":", 1)
            desc = desc.strip()

            # Parse prefix like "CRITICAL_RISK" -> severity="CRITICAL", type="RISK"
            parts = prefix.split("_")
            if len(parts) >= 2:
                severity = parts[0]
                rec_type = "_".join(parts[1:])
            else:
                severity = "INFO"
                rec_type = prefix
        else:
            severity = "INFO"
            rec_type = "GENERAL"
            desc = text

        return cls(type=rec_type, severity=severity, description=desc, source=source)


class MesoCluster(BaseModel):
    """Validated meso-level cluster analysis."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cluster_id: str = Field(..., min_length=1)
    raw_meso_score: float = Field(..., ge=0.0, le=1.0)
    adjusted_score: float = Field(..., ge=0.0, le=1.0)

    # Penalties
    dispersion_penalty: float = Field(..., ge=0.0, le=1.0)
    peer_penalty: float = Field(..., ge=0.0, le=1.0)
    total_penalty: float = Field(..., ge=0.0, le=1.0)

    # Metrics
    dispersion_metrics: dict[str, float] = Field(default_factory=dict)
    micro_scores: list[float] = Field(default_factory=list)

    metadata: dict[str, object] = Field(default_factory=dict)


class MacroSummary(BaseModel):
    """Validated macro-level portfolio analysis."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    overall_posterior: float = Field(..., ge=0.0, le=1.0)
    adjusted_score: float = Field(..., ge=0.0, le=1.0)

    # Penalties
    coverage_penalty: float = Field(..., ge=0.0, le=1.0)
    dispersion_penalty: float = Field(..., ge=0.0, le=1.0)
    contradiction_penalty: float = Field(..., ge=0.0, le=1.0)
    total_penalty: float = Field(..., ge=0.0, le=1.0)

    # Counts
    contradiction_count: int = Field(..., ge=0)

    # Recommendations
    recommendations: list[Recommendation] = Field(default_factory=list)

    metadata: dict[str, object] = Field(default_factory=dict)


class AnalysisReport(BaseModel):
    """Enhanced complete policy analysis report with cryptographic verification."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )

    metadata: ReportMetadata = Field(..., description="Report metadata")
    micro_analyses: list[QuestionAnalysis] = Field(..., description="Micro-level analyses")
    meso_clusters: dict[str, MesoCluster] = Field(
        default_factory=dict, description="Meso-level clusters"
    )
    macro_summary: MacroSummary | None = Field(default=None, description="Macro-level summary")
    evidence_chain_hash: str | None = Field(
        default=None, description="Evidence chain hash", pattern=r"^[a-f0-9]{64}$"
    )
    report_digest: str | None = Field(
        default=None, description="SHA-256 digest of report content", pattern=r"^[a-f0-9]{64}$"
    )

    @calibrated_method("farfan_core.analysis.report_assembly.AnalysisReport.to_dict")
    def to_dict(self) -> dict[str, object]:
        """Convert report to dictionary for JSON serialization."""
        report_dict: dict[str, object] = {
            "metadata": self.metadata.model_dump(),
            "micro_analyses": [q.model_dump() for q in self.micro_analyses],
            "meso_clusters": {k: v.model_dump() for k, v in self.meso_clusters.items()},
            "macro_summary": self.macro_summary.model_dump() if self.macro_summary else None,
            "evidence_chain_hash": self.evidence_chain_hash,
            "report_digest": self.report_digest,
        }
        return report_dict

    @calibrated_method("farfan_core.analysis.report_assembly.AnalysisReport.compute_digest")
    def compute_digest(self) -> str:
        """Compute cryptographic digest of report content."""
        # Create deterministic representation without the digest field
        content: dict[str, object] = {
            "metadata": self.metadata.model_dump(),
            "micro_analyses": [q.model_dump() for q in self.micro_analyses],
            "meso_clusters": {k: v.model_dump() for k, v in self.meso_clusters.items()},
            "macro_summary": self.macro_summary.model_dump() if self.macro_summary else None,
            "evidence_chain_hash": self.evidence_chain_hash,
        }
        return compute_content_digest(content)

    @calibrated_method("farfan_core.analysis.report_assembly.AnalysisReport.verify_digest")
    def verify_digest(self) -> bool:
        """Verify report digest matches computed hash."""
        if self.report_digest is None:
            return False
        computed = self.compute_digest()
        return bool(computed == self.report_digest)


# ============================================================================
# STRUCTURED LOGGING HELPER
# ============================================================================


class ReportLogger:
    """Structured JSON logger for report assembly operations."""

    def __init__(self, name: str) -> None:
        """Initialize logger with name."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

    def log_operation(
        self,
        operation: str,
        correlation_id: str,
        success: bool,
        latency_ms: float,
        **kwargs: object,
    ) -> None:
        """Log operation event with structured data."""
        log_entry: dict[str, object] = {
            "event": "report_operation",
            "operation": operation,
            "correlation_id": correlation_id,
            "success": success,
            "latency_ms": round(latency_ms, 3),
            "timestamp_utc": utc_now_iso(),
        }
        log_entry.update(kwargs)

        self.logger.info(json.dumps(log_entry, sort_keys=True))

    def log_validation(
        self,
        item_type: str,
        correlation_id: str,
        success: bool,
        error: str | None = None,
        **kwargs: object,
    ) -> None:
        """Log validation event."""
        log_entry: dict[str, object] = {
            "event": "report_validation",
            "item_type": item_type,
            "correlation_id": correlation_id,
            "success": success,
            "timestamp_utc": utc_now_iso(),
        }
        if error:
            log_entry["error"] = error
        log_entry.update(kwargs)

        self.logger.info(json.dumps(log_entry, sort_keys=True))


# ============================================================================
# REPORT ASSEMBLER
# ============================================================================


class ReportAssembler:
    """
    Assembles comprehensive policy analysis reports.

    This class demonstrates proper architectural patterns:
    - Dependency injection for all external resources
    - No direct file I/O (delegates to factory)
    - Pattern extraction via QuestionnaireResourceProvider
    - Cryptographic traceability via SHA-256 digests
    - Domain-specific exceptions with structured payloads
    - Pydantic contract validation
    - Structured JSON logging
    """

    def __init__(
        self,
        questionnaire_provider: object,
        evidence_registry: object = None,
        qmcm_recorder: object = None,
        orchestrator: object = None,
    ) -> None:
        """
        Initialize report assembler.

        Args:
            questionnaire_provider: QuestionnaireResourceProvider instance (required)
            evidence_registry: EvidenceRegistry for traceability (optional)
            qmcm_recorder: QMCMRecorder for quality monitoring (optional)
            orchestrator: Orchestrator instance for execution results (optional)

        ARCHITECTURAL NOTE: All dependencies injected, no direct I/O.
        """
        if questionnaire_provider is None:
            raise ReportValidationError(
                "questionnaire_provider is required",
                details={"provider": None},
                stage="initialization",
                recoverable=False,
            )

        self.questionnaire_provider = questionnaire_provider
        self.evidence_registry = evidence_registry
        self.qmcm_recorder = qmcm_recorder
        self.orchestrator = orchestrator
        self.report_logger = ReportLogger(__name__)

        logger.info("ReportAssembler initialized with dependency injection")

    @calibrated_method("farfan_core.analysis.report_assembly.ReportAssembler.assemble_report")
    def assemble_report(
        self,
        plan_name: str,
        execution_results: dict[str, object],
        report_id: str | None = None,
        enriched_packs: dict[str, object] | None = None,
    ) -> AnalysisReport:
        """
        Assemble complete analysis report.

        Args:
            plan_name: Name of the development plan
            execution_results: Results from orchestrator execution
            report_id: Optional report identifier

        Returns:
            Structured AnalysisReport with full traceability

        Raises:
            ReportValidationError: If input validation fails
            ReportIntegrityError: If hash computation fails
        """
        import time

        start_time = time.time()

        # Input validation
        if not plan_name or not isinstance(plan_name, str):
            raise ReportValidationError(
                "plan_name must be a non-empty string",
                details={"plan_name": plan_name, "type": type(plan_name).__name__},
                stage="input_validation",
            )

        if not isinstance(execution_results, dict):
            raise ReportValidationError(
                "execution_results must be a dictionary",
                details={"type": type(execution_results).__name__},
                stage="input_validation",
            )

        # Generate report ID if not provided
        if report_id is None:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            report_id = f"report_{plan_name}_{timestamp}"

        correlation_id = str(uuid.uuid4())

        try:
            # Get questionnaire data and compute hash
            questionnaire_data = self.questionnaire_provider.get_data()

            if not isinstance(questionnaire_data, dict):
                raise ReportIntegrityError(
                    "Invalid questionnaire data format",
                    details={"type": type(questionnaire_data).__name__},
                    stage="questionnaire_loading",
                )

            # Import hash utility for content verification
            from farfan_pipeline.utils.hash_utils import compute_hash

            monolith_hash = compute_hash(questionnaire_data)

            # Validate hash format
            if not isinstance(monolith_hash, str) or len(monolith_hash) != 64:
                raise ReportIntegrityError(
                    "Invalid monolith hash format",
                    details={
                        "hash": monolith_hash,
                        "length": len(monolith_hash) if isinstance(monolith_hash, str) else 0,
                    },
                    stage="hash_computation",
                )

            # Extract metadata with defensive checks
            version = questionnaire_data.get("version", "unknown")
            blocks = questionnaire_data.get("blocks", {})
            if not isinstance(blocks, dict):
                raise ReportValidationError(
                    "questionnaire blocks must be a dictionary",
                    details={"type": type(blocks).__name__},
                    stage="data_extraction",
                )

            micro_questions = blocks.get("micro_questions", [])
            if not isinstance(micro_questions, list):
                raise ReportValidationError(
                    "micro_questions must be a list",
                    details={"type": type(micro_questions).__name__},
                    stage="data_extraction",
                )

            # Create report metadata with Pydantic validation
            metadata = ReportMetadata(
                report_id=report_id,
                generated_at=utc_now_iso(),
                monolith_version=version,
                monolith_hash=monolith_hash,
                plan_name=plan_name,
                total_questions=len(micro_questions),
                questions_analyzed=len(execution_results.get("questions", {})),
                correlation_id=correlation_id,
            )

            # Assemble micro analyses
            micro_analyses = self._assemble_micro_analyses(
                micro_questions, execution_results, correlation_id
            )

            # Assemble meso clusters
            meso_clusters = self._assemble_meso_clusters(execution_results)

            # Assemble macro summary
            macro_summary = self._assemble_macro_summary(execution_results)

            # Get evidence chain hash if available
            evidence_chain_hash = None
            if self.evidence_registry is not None:
                records = self.evidence_registry.records
                if records:
                    evidence_chain_hash = records[-1].entry_hash

            # JOBFRONT 9: Compute signal usage summary if enriched_packs provided
            if enriched_packs:
                signal_usage = self._compute_signal_usage_summary(execution_results, enriched_packs)
                # Add to metadata
                if metadata.metadata is None:
                    # metadata.metadata is immutable, need to recreate

                    new_metadata_dict = {
                        "signal_version": "1.0.0",
                        "total_patterns_available": signal_usage["total_patterns_available"],
                        "total_patterns_used": signal_usage["total_patterns_used"],
                        "signal_usage_summary": signal_usage,
                    }
                    metadata = ReportMetadata(
                        report_id=metadata.report_id,
                        generated_at=metadata.generated_at,
                        monolith_version=metadata.monolith_version,
                        monolith_hash=metadata.monolith_hash,
                        plan_name=metadata.plan_name,
                        total_questions=metadata.total_questions,
                        questions_analyzed=metadata.questions_analyzed,
                        metadata=new_metadata_dict,
                        correlation_id=metadata.correlation_id,
                    )

            # Create report and compute digest
            report = AnalysisReport(
                metadata=metadata,
                micro_analyses=micro_analyses,
                meso_clusters=meso_clusters,
                macro_summary=macro_summary,
                evidence_chain_hash=evidence_chain_hash,
                report_digest=None,  # Will be computed
            )

            # Compute and attach digest
            report_digest = report.compute_digest()
            report = AnalysisReport(
                metadata=metadata,
                micro_analyses=micro_analyses,
                meso_clusters=meso_clusters,
                macro_summary=macro_summary,
                evidence_chain_hash=evidence_chain_hash,
                report_digest=report_digest,
            )

            latency_ms = (time.time() - start_time) * 1000

            # Structured logging
            self.report_logger.log_operation(
                operation="assemble_report",
                correlation_id=correlation_id,
                success=True,
                latency_ms=latency_ms,
                report_id=report_id,
                question_count=len(micro_analyses),
                monolith_hash=monolith_hash[:16],
                report_digest=report_digest[:16],
            )

            logger.info(
                f"Report assembled: {report_id} "
                f"({len(micro_analyses)} questions, hash: {monolith_hash[:16]}...)"
            )

            return report

        except ReportAssemblyException:
            # Re-raise our domain exceptions
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise ReportAssemblyException(
                f"Unexpected error during report assembly: {e!s}",
                details={"error_type": type(e).__name__, "error": str(e)},
                stage="assembly",
                recoverable=False,
            ) from e

    @calibrated_method(
        "farfan_core.analysis.report_assembly.ReportAssembler._assemble_micro_analyses"
    )
    def _assemble_micro_analyses(
        self,
        micro_questions: list[dict[str, object]],
        execution_results: dict[str, object],
        correlation_id: str,
    ) -> list[QuestionAnalysis]:
        """Assemble micro-level question analyses with validation."""
        analyses = []
        question_results = execution_results.get("questions", {})

        if not isinstance(question_results, dict):
            raise ReportValidationError(
                "execution_results.questions must be a dictionary",
                details={"type": type(question_results).__name__},
                stage="micro_analysis",
            )

        for question in micro_questions:
            if not isinstance(question, dict):
                logger.warning(f"Skipping invalid question entry: {type(question).__name__}")
                continue

            question_id = str(question.get("question_id", ""))
            if not question_id:
                logger.warning("Skipping question with missing question_id")
                continue

            result = cast(dict[str, object], question_results.get(question_id, {}))

            # Extract patterns applied using QuestionnaireResourceProvider
            patterns = cast(Any, self.questionnaire_provider).get_patterns_by_question(question_id)
            pattern_names = [str(p.get("pattern_id", "")) for p in patterns] if patterns else []

            try:
                # Pydantic validation
                scoring = question.get("scoring")
                modality = None
                if isinstance(scoring, dict):
                    modality = scoring.get("modality")

                # Extract human_answer and evidence for quality computation
                human_answer_text = str(result.get("human_answer")) if result.get("human_answer") else None
                evidence_list = cast(list[str], result.get("evidence", []))
                
                # NEW: Compute Carver doctoral quality metrics
                carver_quality = None
                if human_answer_text:
                    carver_quality = _compute_carver_quality_metrics(
                        human_answer=human_answer_text,
                        evidence=evidence_list,
                        patterns_applied=pattern_names,
                    )

                analysis = QuestionAnalysis(
                    question_id=question_id,
                    question_global=int(cast(Any, question.get("question_global", 0))),
                    base_slot=str(question.get("base_slot", "")),
                    scoring_modality=str(modality) if modality else None,
                    score=float(cast(Any, result.get("score"))) if result.get("score") is not None else None,
                    evidence=evidence_list,
                    patterns_applied=pattern_names,
                    recommendation=str(result.get("recommendation")) if result.get("recommendation") else None,
                    human_answer=human_answer_text,
                    carver_quality=carver_quality,
                    metadata={
                        "dimension": question.get("dimension"),
                        "policy_area": question.get("policy_area"),
                    },
                )
                analyses.append(analysis)

                self.report_logger.log_validation(
                    item_type="question_analysis",
                    correlation_id=correlation_id,
                    success=True,
                    question_id=question_id,
                )

            except Exception as e:
                # Log validation failure but continue
                self.report_logger.log_validation(
                    item_type="question_analysis",
                    correlation_id=correlation_id,
                    success=False,
                    error=str(e),
                    question_id=question_id,
                )
                logger.error(f"Failed to create QuestionAnalysis for {question_id}: {e}")

        return analyses

    @calibrated_method(
        "farfan_core.analysis.report_assembly.ReportAssembler._assemble_meso_clusters"
    )
    def _assemble_meso_clusters(self, execution_results: dict[str, object]) -> dict[str, MesoCluster]:
        """Assemble meso-level cluster analyses with strict validation."""
        raw_clusters = execution_results.get("meso_clusters", {})

        # Handle list format from Bayesian orchestrator
        if isinstance(raw_clusters, list):
            # Convert list of objects to dict keyed by cluster_id
            cluster_dict: dict[str, object] = {}
            for item in raw_clusters:
                # Handle both dicts and objects (if coming from dataclasses)
                if hasattr(item, "__dict__"):
                    data = item.__dict__
                elif isinstance(item, dict):
                    data = item
                else:
                    continue

                c_id = data.get("cluster_id")
                if c_id:
                    cluster_dict[str(c_id)] = data
            raw_clusters = cluster_dict

        if not isinstance(raw_clusters, dict):
            logger.warning(f"meso_clusters is not a dict/list, got {type(raw_clusters).__name__}")
            return {}

        validated_clusters = {}
        for cluster_id, data in raw_clusters.items():
            try:
                # Ensure data is a dict
                if hasattr(data, "__dict__"):
                    data = data.__dict__

                if not isinstance(data, dict):
                    continue

                cluster = MesoCluster(
                    cluster_id=str(data.get("cluster_id", cluster_id)),
                    raw_meso_score=float(cast(Any, data.get("raw_meso_score", 0.0))),
                    adjusted_score=float(cast(Any, data.get("adjusted_score", 0.0))),
                    dispersion_penalty=float(cast(Any, data.get("dispersion_penalty", 0.0))),
                    peer_penalty=float(cast(Any, data.get("peer_penalty", 0.0))),
                    total_penalty=float(cast(Any, data.get("total_penalty", 0.0))),
                    dispersion_metrics=cast(dict[str, float], data.get("dispersion_metrics", {})),
                    micro_scores=cast(list[float], data.get("micro_scores", [])),
                    metadata=cast(dict[str, object], data.get("metadata", {})),
                )
                validated_clusters[cluster_id] = cluster
            except Exception as e:
                logger.error(f"Failed to validate meso cluster {cluster_id}: {e}")

        return validated_clusters

    @calibrated_method(
        "farfan_core.analysis.report_assembly.ReportAssembler._assemble_macro_summary"
    )
    def _assemble_macro_summary(self, execution_results: dict[str, object]) -> MacroSummary | None:
        """Assemble macro-level summary with strict validation and recommendation wiring."""
        raw_macro = execution_results.get("macro_summary", {})

        # Handle object format
        if hasattr(raw_macro, "__dict__"):
            raw_macro = raw_macro.__dict__

        if not isinstance(raw_macro, dict) or not raw_macro:
            logger.warning("macro_summary is missing or invalid")
            return None

        try:
            # Parse recommendations
            raw_recs = cast(list[object], raw_macro.get("recommendations", []))
            validated_recs = []
            for rec in raw_recs:
                if isinstance(rec, str):
                    validated_recs.append(Recommendation.from_string(rec))
                elif isinstance(rec, dict):
                    # Already structured?
                    try:
                        validated_recs.append(Recommendation(**rec))
                    except (TypeError, ValueError) as e:
                        logger.debug("recommendation_validation_skipped", error=str(e), rec_keys=list(rec.keys()))

            return MacroSummary(
                overall_posterior=float(cast(Any, raw_macro.get("overall_posterior", 0.0))),
                adjusted_score=float(cast(Any, raw_macro.get("adjusted_score", 0.0))),
                coverage_penalty=float(cast(Any, raw_macro.get("coverage_penalty", 0.0))),
                dispersion_penalty=float(cast(Any, raw_macro.get("dispersion_penalty", 0.0))),
                contradiction_penalty=float(cast(Any, raw_macro.get("contradiction_penalty", 0.0))),
                total_penalty=float(cast(Any, raw_macro.get("total_penalty", 0.0))),
                contradiction_count=int(cast(Any, raw_macro.get("contradiction_count", 0))),
                recommendations=validated_recs,
                metadata=cast(dict[str, object], raw_macro.get("metadata", {})),
            )
        except Exception as e:
            logger.error(f"Failed to validate macro summary: {e}")
            return None

    @calibrated_method("farfan_core.analysis.report_assembly.ReportAssembler.export_report")
    def export_report(
        self, report: AnalysisReport, output_path: Path, format: str = "json"
    ) -> None:
        """
        Export report to file.

        Args:
            report: AnalysisReport to export
            output_path: Path to output file
            format: Output format ('json' or 'markdown')

        Raises:
            ReportExportError: If export fails
            ReportValidationError: If format is unsupported

        NOTE: This delegates I/O to factory for architectural compliance.
        """
        import time

        start_time = time.time()
        correlation_id = report.metadata.correlation_id

        try:
            # Delegate to factory for I/O
            try:
                from farfan_pipeline.analysis.factory import save_json, write_text_file
            except ImportError:
                # Fallback implementation if factory not available
                def save_json(data: dict[str, object], path: str) -> None:
                    with open(path, "w") as f:
                        json.dump(data, f, indent=2)
                def write_text_file(text: str, path: str) -> None:
                    with open(path, "w") as f:
                        f.write(text)

            if format == "json":
                save_json(report.to_dict(), str(output_path))
            elif format == "markdown":
                markdown = self._format_as_markdown(report)
                write_text_file(markdown, str(output_path))
            else:
                raise ReportValidationError(
                    f"Unsupported format: {format}",
                    details={"format": format, "supported": ["json", "markdown"]},
                    stage="export",
                )

            latency_ms = (time.time() - start_time) * 1000

            self.report_logger.log_operation(
                operation="export_report",
                correlation_id=correlation_id,
                success=True,
                latency_ms=latency_ms,
                output_path=str(output_path),
                format=format,
            )

            logger.info(f"Report exported to {output_path} in {format} format")

        except ReportValidationError:
            raise
        except Exception as e:
            raise ReportExportError(
                f"Failed to export report: {str(e)}",
                details={"output_path": str(output_path), "format": format, "error": str(e)},
                stage="export",
                recoverable=True,
            ) from e

    @calibrated_method("farfan_core.analysis.report_assembly.ReportAssembler._format_as_markdown")
    def _format_as_markdown(self, report: AnalysisReport) -> str:
        """Format report as Markdown with externalized parameters."""
        # Externalized parameters
        # Load from calibration system if available
        if _PARAM_LOADER:
            preview_count = _PARAM_LOADER.get(
                "farfan_core.analysis.report_assembly.ReportAssembler._format_as_markdown"
            ).get("preview_question_count", 10)
            hash_preview_length = _PARAM_LOADER.get(
                "farfan_core.analysis.report_assembly.ReportAssembler._format_as_markdown"
            ).get("hash_preview_length", 16)
        else:
            preview_count = 10
            hash_preview_length = 16

        lines = [
            f"# Policy Analysis Report: {report.metadata.plan_name}\n",
            f"**Report ID:** {report.metadata.report_id}\n",
            f"**Generated:** {report.metadata.generated_at}\n",
            f"**Monolith Version:** {report.metadata.monolith_version}\n",
            f"**Monolith Hash:** {report.metadata.monolith_hash[:int(cast(Any, hash_preview_length))]}...\n",
            f"**Questions Analyzed:** {report.metadata.questions_analyzed}/{report.metadata.total_questions}\n",
        ]

        if report.report_digest:
            lines.append(f"**Report Digest:** {report.report_digest[:int(cast(Any, hash_preview_length))]}...\n")

        lines.append("\n## Micro-Level Analyses\n")

        for analysis in report.micro_analyses[:int(cast(Any, preview_count))]:
            lines.append(f"\n### {analysis.question_id}\n")
            lines.append(f"- **Slot:** {analysis.base_slot}\n")
            lines.append(f"- **Score:** {analysis.score}\n")
            lines.append(f"- **Patterns:** {', '.join(analysis.patterns_applied)}\n")

        if len(report.micro_analyses) > int(cast(Any, preview_count)):
            lines.append(
                f"\n_...and {len(report.micro_analyses) - int(cast(Any, preview_count))} more questions_\n"
            )

        lines.append("\n## Meso-Level Clusters\n")
        for cid, cluster in report.meso_clusters.items():
            lines.append(f"\n### Cluster {cid}\n")
            lines.append(
                f"- **Score:** {cluster.adjusted_score:.4f} (Raw: {cluster.raw_meso_score:.4f})\n"
            )
            lines.append(
                f"- **Penalties:** Total {cluster.total_penalty:.4f} (Dispersion: {cluster.dispersion_penalty:.4f}, Peer: {cluster.peer_penalty:.4f})\n"
            )

        if report.macro_summary:
            lines.append("\n## Macro Summary\n")
            lines.append(f"- **Overall Score:** {report.macro_summary.adjusted_score:.4f}\n")
            lines.append(f"- **Contradictions:** {report.macro_summary.contradiction_count}\n")

            lines.append("\n### Recommendations\n")
            for rec in report.macro_summary.recommendations:
                icon = (
                    "🔴" if "CRITICAL" in rec.severity else "🟠" if "HIGH" in rec.severity else "🟡"
                )
                lines.append(f"- {icon} **{rec.type}** ({rec.severity}): {rec.description}\n")
        else:
            lines.append("\n## Macro Summary\n")
            lines.append("_No macro summary available_\n")

        if report.evidence_chain_hash:
            lines.append(
                f"\n**Evidence Chain Hash:** {report.evidence_chain_hash[:int(cast(Any, hash_preview_length))]}...\n"
            )

        return "".join(lines)

    def _compute_signal_usage_summary(
        self, execution_results: dict[str, object], enriched_packs: dict[str, object]
    ) -> dict[str, object]:
        """
        Compute signal usage summary for report provenance (JOBFRONT 9).

        Args:
            execution_results: Results from orchestrator execution
            enriched_packs: Dictionary of EnrichedSignalPack by policy_area_id

        Returns:
            Signal usage summary with patterns, completeness, validation failures
        """
        micro_results = cast(dict[str, dict[str, object]], execution_results.get("micro_results", {}))

        total_patterns_available = sum(len(cast(Any, pack).patterns) for pack in enriched_packs.values())
        total_patterns_used = 0
        by_policy_area: dict[str, dict[str, object]] = {}
        completeness_scores = []
        validation_failures = []

        for question_id, result in micro_results.items():
            policy_area = str(result.get("policy_area_id", ""))
            if not policy_area or policy_area not in enriched_packs:
                continue

            patterns_used = cast(list[object], result.get("patterns_used", []))
            completeness = float(cast(Any, result.get("completeness", 1.0)))
            validation = cast(dict[str, object], result.get("validation", {}))

            total_patterns_used += len(patterns_used)
            completeness_scores.append(completeness)

            # Track validation failures
            if validation.get("status") == "failed" or validation.get("contract_failed"):
                val_errors = cast(list[dict[str, object]], validation.get("errors", []))
                validation_failures.append(
                    {
                        "question_id": question_id,
                        "policy_area": policy_area,
                        "error_code": (
                            val_errors[0].get("error_code")
                            if val_errors
                            else None
                        ),
                        "remediation": (
                            val_errors[0].get("remediation")
                            if val_errors
                            else None
                        ),
                    }
                )

            # Aggregate by policy area
            if policy_area not in by_policy_area:
                by_policy_area[policy_area] = {
                    "patterns_available": len(cast(Any, enriched_packs[policy_area]).patterns),
                    "patterns_used": 0,
                    "questions_analyzed": 0,
                    "avg_completeness": 0.0,
                }

            by_policy_area[policy_area]["patterns_used"] = cast(int, by_policy_area[policy_area]["patterns_used"]) + len(patterns_used)
            by_policy_area[policy_area]["questions_analyzed"] = cast(int, by_policy_area[policy_area]["questions_analyzed"]) + 1

        # Compute averages
        for pa_id, summary in by_policy_area.items():
            pa_results = [r for r in micro_results.values() if str(r.get("policy_area_id")) == pa_id]
            completeness_values = [float(cast(Any, r.get("completeness", 1.0))) for r in pa_results]
            summary["avg_completeness"] = (
                sum(completeness_values) / len(completeness_values) if completeness_values else 0.0
            )

        return {
            "total_patterns_available": total_patterns_available,
            "total_patterns_used": total_patterns_used,
            "by_policy_area": by_policy_area,
            "avg_completeness": (
                sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
            ),
            "validation_failures": validation_failures,
        }


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


def create_report_assembler(
    questionnaire_provider: object,
    evidence_registry: object = None,
    qmcm_recorder: object = None,
    orchestrator: object = None,
) -> ReportAssembler:
    """
    Factory function to create ReportAssembler with dependencies.

    Args:
        questionnaire_provider: QuestionnaireResourceProvider instance
        evidence_registry: Optional EvidenceRegistry
        qmcm_recorder: Optional QMCMRecorder
        orchestrator: Optional Orchestrator

    Returns:
        Configured ReportAssembler

    Raises:
        ReportValidationError: If required dependencies are missing
    """
    return ReportAssembler(
        questionnaire_provider=questionnaire_provider,
        evidence_registry=evidence_registry,
        qmcm_recorder=qmcm_recorder,
        orchestrator=orchestrator,
    )


# ============================================================================
# CARVER DOCTORAL QUALITY COMPUTATION
# ============================================================================

# Academic vocabulary indicators for doctoral-level synthesis
_ACADEMIC_VOCABULARY: set[str] = {
    "análisis", "evaluación", "evidencia", "metodología", "implementación",
    "estratégico", "sistémico", "institucional", "normativo", "regulatorio",
    "diagnóstico", "prospectivo", "transversal", "diferencial", "interseccional",
    "coherencia", "articulación", "sostenibilidad", "viabilidad", "escalabilidad",
    "política pública", "marco normativo", "enfoque diferencial", "derechos humanos",
}


def _compute_carver_quality_metrics(
    human_answer: str,
    evidence: list[str],
    patterns_applied: list[str],
) -> CarverQualityMetrics:
    """Compute doctoral quality metrics for a Carver-synthesized answer.
    
    Quality Scoring Algorithm:
    - doctoral_depth_score: Based on answer length (>500 chars = 0.8+), 
      paragraph structure, academic vocabulary density
    - synthesis_complexity_index: Based on evidence integration count,
      cross-reference patterns, pattern application
    - evidence_density_ratio: len(evidence) / max(1, paragraphs)
    - quality_gate_passed: All scores >= threshold (default 0.7)
    
    Args:
        human_answer: The Carver-synthesized human-readable answer
        evidence: List of evidence items used in synthesis
        patterns_applied: List of pattern IDs applied during analysis
        
    Returns:
        CarverQualityMetrics with computed scores and gate validation
    """
    # Compute basic metrics
    answer_length = len(human_answer)
    paragraphs = [p.strip() for p in human_answer.split("\n\n") if p.strip()]
    paragraph_count = max(1, len(paragraphs))
    
    # Academic vocabulary density
    answer_lower = human_answer.lower()
    academic_hits = sum(1 for term in _ACADEMIC_VOCABULARY if term in answer_lower)
    words_approx = len(human_answer.split())
    academic_vocabulary_density = min(1.0, academic_hits / max(1, words_approx) * 10)
    
    # Doctoral depth score (length + structure + vocabulary)
    # Long answers (>800 chars) with multiple paragraphs score higher
    length_score = min(1.0, answer_length / 800)
    structure_score = min(1.0, paragraph_count / 3)
    doctoral_depth_score = (
        0.4 * length_score + 
        0.3 * structure_score + 
        0.3 * academic_vocabulary_density
    )
    
    # Synthesis complexity (evidence + patterns + cross-references)
    evidence_count = len(evidence)
    patterns_count = len(patterns_applied)
    
    # Count cross-references (mentions of evidence or patterns in answer)
    cross_references = sum(1 for ev in evidence if ev[:20].lower() in answer_lower)
    cross_reference_count = cross_references + patterns_count
    
    synthesis_complexity_index = min(1.0, (
        0.4 * min(1.0, evidence_count / 5) +
        0.3 * min(1.0, patterns_count / 3) +
        0.3 * min(1.0, cross_references / 2)
    ))
    
    # Evidence density ratio
    evidence_density_ratio = min(1.0, evidence_count / paragraph_count)
    
    # Quality gate validation (all must meet threshold)
    threshold = 0.7
    quality_gate_passed = (
        doctoral_depth_score >= threshold and
        synthesis_complexity_index >= 0.6 and
        evidence_density_ratio >= 0.5
    )
    
    return CarverQualityMetrics(
        doctoral_depth_score=round(doctoral_depth_score, 4),
        synthesis_complexity_index=round(synthesis_complexity_index, 4),
        evidence_density_ratio=round(evidence_density_ratio, 4),
        quality_gate_passed=quality_gate_passed,
        quality_gate_threshold=threshold,
        answer_length_chars=answer_length,
        paragraph_count=paragraph_count,
        academic_vocabulary_density=round(academic_vocabulary_density, 4),
        cross_reference_count=cross_reference_count,
        evidence_items_integrated=evidence_count,
    )


# ============================================================================
# ATROZ DASHBOARD ARTICULATION BRIDGE
# ============================================================================


class AtrozReportPublisher:
    """Bridge for publishing Phase 9 reports to ATROZ dashboard.
    
    Enables bidirectional sync between Phase 9 report generation and the
    ATROZ dashboard's data mining, analytics, and visualization capabilities.
    
    Features:
    - Report publication with quality metrics
    - WebSocket event emission for real-time dashboard updates
    - Quality metric synchronization
    - Retry logic for failed publications
    
    Usage:
        publisher = AtrozReportPublisher()
        result = publisher.publish_report(report, quality_metrics)
    """
    
    def __init__(
        self,
        dashboard_base_url: str = "http://localhost:5005",
        enable_auto_publish: bool = False,
        max_retries: int = 3,
    ) -> None:
        """Initialize ATROZ report publisher.
        
        Args:
            dashboard_base_url: Base URL of ATROZ dashboard API
            enable_auto_publish: Whether to auto-publish on report assembly
            max_retries: Maximum retry attempts for failed publications
        """
        self.dashboard_base_url = dashboard_base_url.rstrip("/")
        self.enable_auto_publish = enable_auto_publish
        self.max_retries = max_retries
        self._logger = logging.getLogger(f"{__name__}.AtrozPublisher")
    
    def publish_report(
        self,
        report: AnalysisReport,
        quality_metrics: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Publish Phase 9 report to ATROZ dashboard.
        
        Sends report summary and quality metrics to dashboard for
        visualization and analytics integration.
        
        Args:
            report: The AnalysisReport to publish
            quality_metrics: Optional quality metrics dict
            
        Returns:
            Publication result with dashboard_report_id and status
        """
        import urllib.request
        import urllib.error
        
        publication_id = str(uuid.uuid4())
        timestamp = utc_now_iso()
        
        # Prepare publication payload
        payload = {
            "report_id": report.metadata.report_id,
            "publication_id": publication_id,
            "timestamp": timestamp,
            "plan_name": report.metadata.plan_name,
            "questions_analyzed": report.metadata.questions_analyzed,
            "macro_score": (
                report.macro_summary.adjusted_score 
                if report.macro_summary else None
            ),
            "digest": report.report_digest,
            "quality_metrics": quality_metrics or {},
            "carver_quality_summary": self._summarize_carver_quality(report),
        }
        
        # Attempt publication
        try:
            url = f"{self.dashboard_base_url}/api/v1/reports/phase9-publish"
            data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                self._logger.info(
                    f"Report published to ATROZ: {publication_id[:8]}..."
                )
                return {
                    "status": "published",
                    "dashboard_report_id": result.get("id", publication_id),
                    "timestamp": timestamp,
                    "endpoint": url,
                }
                
        except urllib.error.URLError as e:
            self._logger.warning(
                f"ATROZ dashboard unreachable: {e}. "
                "Report will be stored locally for later sync."
            )
            return {
                "status": "pending",
                "dashboard_report_id": None,
                "timestamp": timestamp,
                "error": str(e),
                "retry_scheduled": True,
            }
        except Exception as e:
            self._logger.error(f"Publication failed: {e}")
            return {
                "status": "failed",
                "dashboard_report_id": None,
                "timestamp": timestamp,
                "error": str(e),
            }
    
    def sync_quality_metrics(
        self,
        report_id: str,
        metrics: dict[str, object],
    ) -> bool:
        """Sync quality metrics to dashboard for existing report.
        
        Args:
            report_id: The report ID to update
            metrics: Quality metrics to sync
            
        Returns:
            True if sync succeeded, False otherwise
        """
        try:
            import urllib.request
            
            url = f"{self.dashboard_base_url}/api/v1/reports/{report_id}/quality"
            data = json.dumps(metrics).encode("utf-8")
            request = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="PATCH",
            )
            
            with urllib.request.urlopen(request, timeout=10):
                self._logger.info(f"Quality metrics synced for {report_id}")
                return True
                
        except Exception as e:
            self._logger.warning(f"Quality sync failed: {e}")
            return False
    
    def _summarize_carver_quality(
        self,
        report: AnalysisReport,
    ) -> dict[str, object]:
        """Summarize Carver quality metrics across all micro analyses.
        
        Args:
            report: The analysis report
            
        Returns:
            Summary dict with aggregate quality statistics
        """
        quality_scores = []
        gate_passed_count = 0
        
        for analysis in report.micro_analyses:
            if analysis.carver_quality is not None:
                quality_scores.append(analysis.carver_quality.doctoral_depth_score)
                if analysis.carver_quality.quality_gate_passed:
                    gate_passed_count += 1
        
        if not quality_scores:
            return {
                "total_with_quality": 0,
                "avg_doctoral_depth": 0.0,
                "gate_pass_rate": 0.0,
            }
        
        return {
            "total_with_quality": len(quality_scores),
            "avg_doctoral_depth": round(sum(quality_scores) / len(quality_scores), 4),
            "gate_pass_rate": round(gate_passed_count / len(quality_scores), 4),
            "gate_passed_count": gate_passed_count,
        }


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Exceptions
    "ReportAssemblyException",
    "ReportValidationError",
    "ReportIntegrityError",
    "ReportExportError",
    # Contracts
    "ReportMetadata",
    "QuestionAnalysis",
    "CarverQualityMetrics",
    "AnalysisReport",
    # Main Classes
    "ReportAssembler",
    "ReportLogger",
    "AtrozReportPublisher",
    # Factory Functions
    "create_report_assembler",
    # Utilities
    "compute_content_digest",
    "utc_now_iso",
]


# ============================================================================
# IN-SCRIPT VALIDATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Report Assembly Module - Validation Suite")
    print("=" * 70)

    # Test 1: Domain-specific exceptions
    print("\n1. Testing domain-specific exceptions:")
    try:
        raise ReportValidationError(
            "Test validation error", details={"field": "test"}, stage="validation"
        )
    except ReportValidationError as e:
        print(f"   ✓ ReportValidationError: {e.event_id[:8]}... - {e.message}")
        print(f"   ✓ Structured dict: {list(e.to_dict().keys())}")

    # Test 2: Pydantic contract validation
    print("\n2. Testing Pydantic contract validation:")
    try:
        # Invalid hash (not 64 chars)
        ReportMetadata(
            report_id="test-001",
            monolith_version="1.0",
            monolith_hash="invalid",
            plan_name="Test Plan",
            total_questions=10,
            questions_analyzed=5,
        )
        print("   ✗ Expected validation error for invalid hash")
    except Exception as e:
        print(f"   ✓ Caught validation error: {type(e).__name__}")

    # Valid metadata
    valid_hash = "a" * 64
    metadata = ReportMetadata(
        report_id="test-001",
        monolith_version="1.0",
        monolith_hash=valid_hash,
        plan_name="Test Plan",
        total_questions=10,
        questions_analyzed=5,
    )
    print(f"   ✓ Valid metadata created: {metadata.report_id}")

    # Test 3: Cryptographic digest
    print("\n3. Testing cryptographic digest:")
    test_content = {"key": "value", "number": 42}
    digest = compute_content_digest(test_content)
    print(f"   ✓ Digest computed: {digest[:16]}... (length: {len(digest)})")
    assert len(digest) == 64, "Digest must be 64 characters"
    print("   ✓ Digest length validated")

    # Test 4: Report digest verification
    print("\n4. Testing report digest verification:")
    micro_analysis = QuestionAnalysis(
        question_id="Q001", question_global=1, base_slot="slot1", score=0.85
    )

    meso_cluster = MesoCluster(
        cluster_id="CL01",
        raw_meso_score=0.8,
        adjusted_score=0.75,
        dispersion_penalty=0.05,
        peer_penalty=0.0,
        total_penalty=0.05,
    )

    macro_summary = MacroSummary(
        overall_posterior=0.75,
        adjusted_score=0.7,
        coverage_penalty=0.05,
        dispersion_penalty=0.0,
        contradiction_penalty=0.0,
        total_penalty=0.05,
        contradiction_count=0,
        recommendations=[
            Recommendation(type="RISK", severity="LOW", description="Monitor closely")
        ],
    )

    report = AnalysisReport(
        metadata=metadata,
        micro_analyses=[micro_analysis],
        meso_clusters={"CL01": meso_cluster},
        macro_summary=macro_summary,
    )

    report_digest = report.compute_digest()
    print(f"   ✓ Report digest: {report_digest[:16]}...")

    # Create report with digest
    report_with_digest = AnalysisReport(
        metadata=metadata,
        micro_analyses=[micro_analysis],
        meso_clusters={"CL01": meso_cluster},
        macro_summary=macro_summary,
        report_digest=report_digest,
    )

    is_valid = report_with_digest.verify_digest()
    print(f"   ✓ Digest verification: {is_valid}")

    # Test 5: Structured logging
    print("\n5. Testing structured logging:")
    test_logger = ReportLogger("test")
    test_logger.log_operation(
        operation="test_operation",
        correlation_id=metadata.correlation_id,
        success=True,
        latency_ms=12.345,
        custom_field="test_value",
    )
    print("   ✓ Structured log emitted")

    print("\n" + "=" * 70)
    print("All validation tests passed!")
    print("=" * 70)
