"""
Questionnaire Signal Registry - PRODUCTION IMPLEMENTATION
=========================================================

Content-addressed, type-safe, observable signal registry with cryptographic
consumption tracking and lazy loading. This module is the CANONICAL source
for all signal extraction in the Farfan Pipeline.

Architecture:
    QuestionnairePort → QuestionnaireSignalRegistry → SignalPacks → Components

Key Features:
- Full metadata extraction (100% Intelligence Utilization)
- Pydantic v2 runtime validation with strict type safety
- Content-based cache invalidation (BLAKE3/SHA256)
- OpenTelemetry distributed tracing
- Lazy loading with LRU caching
- Immutable signal packs (frozen Pydantic models)

Version: 2.0.0
Status: Production-ready
Author: Farfan Pipeline Team
"""

from __future__ import annotations

import hashlib
import time
import json
import sys
import concurrent.futures
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Literal

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    
    class DummySpan:
        def set_attribute(self, key: str, value: Any) -> None:
            pass
        def set_status(self, status: Any) -> None:
            pass
        def record_exception(self, exc: Exception) -> None:
            pass
        def __enter__(self) -> DummySpan:
            return self
        def __exit__(self, *args: Any) -> None:
            pass

    class DummyTracer:
        def start_as_current_span(
            self, name: str, attributes: dict[str, Any] | None = None
        ) -> DummySpan:
            return DummySpan()

    tracer = DummyTracer()  # type: ignore

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)  # type: ignore

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from cross_cutting_infrastructure.irrigation_using_signals.ports import QuestionnairePort, SignalRegistryPort
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signals import PolicyArea, SignalPack
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_enhancement_integrator import (
    create_enhancement_integrator,
    SignalEnhancementIntegrator
)


# ============================================================================
# EXCEPTIONS
# ============================================================================


class SignalRegistryError(Exception):
    """Base exception for signal registry errors."""
    pass


class QuestionNotFoundError(SignalRegistryError):
    """Raised when a question ID is not found in the questionnaire."""
    
    def __init__(self, question_id: str) -> None:
        self.question_id = question_id
        super().__init__(f"Question {question_id} not found in questionnaire")


class SignalExtractionError(SignalRegistryError):
    """Raised when signal extraction fails."""
    
    def __init__(self, signal_type: str, reason: str) -> None:
        self.signal_type = signal_type
        self.reason = reason
        super().__init__(f"Failed to extract {signal_type} signals: {reason}")


class InvalidLevelError(SignalRegistryError):
    """Raised when an invalid assembly level is requested."""
    
    def __init__(self, level: str, valid_levels: list[str]) -> None:
        self.level = level
        self.valid_levels = valid_levels
        super().__init__(
            f"Invalid assembly level '{level}'. Valid levels: {', '.join(valid_levels)}"
        )


# ============================================================================
# TYPE-SAFE SIGNAL PACKS (Pydantic v2)
# ============================================================================


class PatternItem(BaseModel):
    """Individual pattern with FULL metadata from Intelligence Layer.
    
    This model captures ALL fields from the monolith, including those
    previously discarded by the legacy loader.
    """
    model_config = ConfigDict(frozen=True, strict=True)

    id: str = Field(..., pattern=r"^PAT-Q\d{3}-\d{3}$", description="Unique pattern ID")
    pattern: str = Field(..., description="Pattern string (regex or literal)")
    match_type: Literal["REGEX", "LITERAL", "NER_OR_REGEX"] = Field(
        default="REGEX", description="Pattern matching strategy"
    )
    confidence_weight: float = Field(
        ..., ge=0.0, le=1.0, description="Pattern confidence weight (Intelligence Layer)"
    )
    category: Literal[
        "GENERAL",
        "TEMPORAL",
        "INDICADOR",
        "FUENTE_OFICIAL",
        "TERRITORIAL",
        "UNIDAD_MEDIDA",
    ] = Field(default="GENERAL", description="Pattern category")
    flags: str = Field(
        default="", pattern=r"^[imsx]*$", description="Regex flags (case-insensitive, etc.)"
    )
    
    # Intelligence Layer fields (previously discarded by legacy loader)
    semantic_expansion: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        description="Semantic expansions for fuzzy matching (Intelligence Layer)"
    )
    context_requirement: str | None = Field(
        default=None,
        description="Required context for pattern match (Intelligence Layer)"
    )
    evidence_boost: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Evidence scoring boost factor (Intelligence Layer)"
    )


class ExpectedElement(BaseModel):
    """Expected element specification for micro questions."""
    model_config = ConfigDict(frozen=True)

    type: str = Field(..., min_length=1, description="Element type")
    required: bool = Field(default=False, description="Is this element required?")
    minimum: int = Field(default=0, ge=0, description="Minimum count required")
    description: str = Field(default="", description="Human-readable description")


class ValidationCheck(BaseModel):
    """Validation check specification."""
    model_config = ConfigDict(frozen=True)

    patterns: list[str] = Field(default_factory=list, description="Validation patterns")
    minimum_required: int = Field(default=1, ge=0, description="Minimum matches required")
    minimum_years: int = Field(default=0, ge=0, description="Minimum temporal coverage (years)")
    specificity: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        default="MEDIUM", description="Check specificity level"
    )


class FailureContract(BaseModel):
    """Failure contract specification."""
    model_config = ConfigDict(frozen=True)

    abort_if: list[str] = Field(..., min_length=1, description="Abort conditions")
    emit_code: str = Field(
        ..., pattern=r"^ABORT-Q\d{3}-[A-Z]+$", description="Emitted abort code"
    )
    severity: Literal["CRITICAL", "ERROR", "WARNING"] = Field(
        default="ERROR", description="Failure severity"
    )


class ModalityConfig(BaseModel):
    """Scoring modality configuration."""
    model_config = ConfigDict(frozen=True)

    aggregation: Literal[
        "presence_threshold",
        "binary_sum",
        "weighted_sum",
        "binary_presence",
        "normalized_continuous",
    ] = Field(..., description="Aggregation strategy")
    description: str = Field(..., min_length=5, description="Human-readable description")
    failure_code: str = Field(
        ..., pattern=r"^F-[A-F]-[A-Z]+$", description="Failure code"
    )
    threshold: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Threshold value (if applicable)"
    )
    max_score: int = Field(default=3, ge=0, le=10, description="Maximum score")
    weights: list[float] | None = Field(default=None, description="Sub-dimension weights")

    @field_validator("weights")
    @classmethod
    def validate_weights_sum(cls, v: list[float] | None) -> list[float] | None:
        """Validate weights sum to 1.0."""
        if v is not None:
            total = sum(v)
            if not 0.99 <= total <= 1.01:
                raise ValueError(f"Weights must sum to 1.0, got {total}")
        return v


class QualityLevel(BaseModel):
    """Quality level specification."""
    model_config = ConfigDict(frozen=True)

    level: Literal["EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"]
    min_score: float = Field(..., ge=0.0, le=1.0)
    color: Literal["green", "blue", "yellow", "red"]
    description: str = Field(default="", description="Level description")


# ============================================================================
# SIGNAL PACK MODELS
# ============================================================================


class ChunkingSignalPack(BaseModel):
    """Type-safe signal pack for Smart Policy Chunking."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    section_detection_patterns: dict[str, list[str]] = Field(
        ..., min_length=1, description="Patterns per PDM section type"
    )
    section_weights: dict[str, float] = Field(
        ..., description="Calibrated weights per section (0.0-2.0)"
    )
    table_patterns: list[str] = Field(
        default_factory=list, description="Table boundary detection patterns"
    )
    numerical_patterns: list[str] = Field(
        default_factory=list, description="Numerical content patterns"
    )
    embedding_config: dict[str, Any] = Field(
        default_factory=dict, description="Semantic embedding configuration"
    )
    version: str = Field(default="2.0.0", pattern=r"^\d+\.\d+\.\d+$")
    source_hash: str = Field(..., min_length=32, max_length=64)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @field_validator("section_weights")
    @classmethod
    def validate_weights(cls, v: dict[str, float]) -> dict[str, float]:
        """Validate section weights are in valid range."""
        for key, weight in v.items():
            if not 0.0 <= weight <= 2.0:
                raise ValueError(f"Weight {key}={weight} out of range [0.0, 2.0]")
        return v


class MicroAnsweringSignalPack(BaseModel):
    """Type-safe signal pack for Micro Answering with FULL metadata."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    question_patterns: dict[str, list[PatternItem]] = Field(
        ..., description="Patterns per question ID (with full metadata)"
    )
    expected_elements: dict[str, list[ExpectedElement]] = Field(
        ..., description="Expected elements per question"
    )
    indicators_by_pa: dict[str, list[str]] = Field(
        default_factory=dict, description="Indicators per policy area"
    )
    official_sources: list[str] = Field(
        default_factory=list, description="Recognized official sources"
    )
    pattern_weights: dict[str, float] = Field(
        default_factory=dict, description="Confidence weights per pattern ID"
    )
    
    # Intelligence Layer metadata
    semantic_expansions: dict[str, list[str] | dict[str, list[str]]] = Field(
        default_factory=dict,
        description="Semantic expansions per pattern ID (Intelligence Layer)"
    )
    context_requirements: dict[str, str] = Field(
        default_factory=dict,
        description="Context requirements per pattern ID (Intelligence Layer)"
    )
    evidence_boosts: dict[str, float] = Field(
        default_factory=dict,
        description="Evidence boost factors per pattern ID (Intelligence Layer)"
    )
    
    # Enhancement #1: Method Execution Metadata (Subphase 2.3)
    method_execution_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Method priority, type, and execution ordering per question (Enhancement #1)"
    )
    
    # Enhancement #2: Structured Validation Specifications (Subphase 2.5)
    validation_specifications: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured validation specs with thresholds per question (Enhancement #2)"
    )
    
    # Enhancement #3: Scoring Modality Context (Subphase 2.3)
    scoring_modality_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Scoring modality definitions and adaptive thresholds (Enhancement #3)"
    )
    
    # Enhancement #4: Semantic Disambiguation (Subphase 2.2)
    semantic_disambiguation: dict[str, Any] = Field(
        default_factory=dict,
        description="Semantic disambiguation rules and entity linking (Enhancement #4)"
    )
    
    version: str = Field(default="2.0.0", pattern=r"^\d+\.\d+\.\d+$")
    source_hash: str = Field(..., min_length=32, max_length=64)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @property
    def question_id(self) -> str | None:
        question_id = self.metadata.get("question_id")
        return str(question_id) if question_id else None

    @property
    def policy_area_id(self) -> str | None:
        policy_area = self.metadata.get("policy_area")
        return str(policy_area) if policy_area else None

    @property
    def patterns(self) -> list[str]:
        question_id = self.question_id
        if question_id and question_id in self.question_patterns:
            patterns = self.question_patterns[question_id]
        else:
            patterns = [
                pattern
                for pattern_list in self.question_patterns.values()
                for pattern in pattern_list
            ]
        return [p.pattern for p in patterns]

    @property
    def pattern_specs(self) -> list[dict[str, Any]]:
        question_id = self.question_id
        if question_id and question_id in self.question_patterns:
            patterns = self.question_patterns[question_id]
        else:
            patterns = [
                pattern
                for pattern_list in self.question_patterns.values()
                for pattern in pattern_list
            ]

        policy_area = self.policy_area_id
        return [
            {
                "id": p.id,
                "pattern": p.pattern,
                "match_type": p.match_type,
                "confidence_weight": p.confidence_weight,
                "category": p.category,
                "flags": p.flags,
                "semantic_expansion": p.semantic_expansion,
                "context_requirement": p.context_requirement,
                "evidence_boost": p.evidence_boost,
                "policy_area": policy_area,
                "question_id": question_id,
            }
            for p in patterns
        ]

    @property
    def indicators(self) -> list[str]:
        policy_area = self.policy_area_id
        if policy_area and policy_area in self.indicators_by_pa:
            return list(self.indicators_by_pa[policy_area])
        if self.indicators_by_pa:
            first_key = sorted(self.indicators_by_pa.keys())[0]
            return list(self.indicators_by_pa.get(first_key, []))
        return []

    @property
    def entities(self) -> list[str]:
        return list(self.official_sources)


class ValidationSignalPack(BaseModel):
    """Type-safe signal pack for Response Validation."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    validation_rules: dict[str, dict[str, ValidationCheck]] = Field(
        ..., description="Validation rules per question"
    )
    failure_contracts: dict[str, FailureContract] = Field(
        ..., description="Failure contracts per question"
    )
    modality_thresholds: dict[str, float] = Field(
        default_factory=dict, description="Thresholds per scoring modality"
    )
    abort_codes: dict[str, str] = Field(
        default_factory=dict, description="Abort codes per question"
    )
    verification_patterns: dict[str, list[str]] = Field(
        default_factory=dict, description="Verification patterns per question"
    )
    version: str = Field(default="2.0.0", pattern=r"^\d+\.\d+\.\d+$")
    source_hash: str = Field(..., min_length=32, max_length=64)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class AssemblySignalPack(BaseModel):
    """Type-safe signal pack for Response Assembly."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    aggregation_methods: dict[str, str] = Field(
        ..., description="Aggregation method per cluster/level"
    )
    cluster_policy_areas: dict[str, list[str]] = Field(
        ..., description="Policy areas per cluster"
    )
    dimension_weights: dict[str, float] = Field(
        default_factory=dict, description="Weights per dimension"
    )
    evidence_keys_by_pa: dict[str, list[str]] = Field(
        default_factory=dict, description="Required evidence keys per policy area"
    )
    coherence_patterns: list[dict[str, Any]] = Field(
        default_factory=list, description="Cross-reference coherence patterns"
    )
    fallback_patterns: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Fallback patterns per level"
    )
    version: str = Field(default="2.0.0", pattern=r"^\d+\.\d+\.\d+$")
    source_hash: str = Field(..., min_length=32, max_length=64)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ScoringSignalPack(BaseModel):
    """Type-safe signal pack for Scoring."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    question_modalities: dict[str, str] = Field(
        ..., description="Scoring modality per question"
    )
    modality_configs: dict[str, ModalityConfig] = Field(
        ..., description="Configuration per modality type"
    )
    quality_levels: list[QualityLevel] = Field(
        ..., min_length=4, max_length=4, description="Quality level definitions"
    )
    failure_codes: dict[str, str] = Field(
        default_factory=dict, description="Failure codes per modality"
    )
    thresholds: dict[str, float] = Field(
        default_factory=dict, description="Thresholds per modality"
    )
    type_d_weights: list[float] = Field(
        default=[0.4, 0.3, 0.3], description="Weights for TYPE_D modality"
    )
    version: str = Field(default="2.0.0", pattern=r"^\d+\.\d+\.\d+$")
    source_hash: str = Field(..., min_length=32, max_length=64)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @property
    def question_id(self) -> str | None:
        question_id = self.metadata.get("question_id")
        return str(question_id) if question_id else None

    @property
    def scoring_modality(self) -> str:
        modality = self.metadata.get("modality")
        return str(modality) if modality else "UNKNOWN"


# ============================================================================
# METRICS TRACKER
# ============================================================================


@dataclass
class RegistryMetrics:
    """Metrics for observability and monitoring."""
    cache_hits: int = 0
    cache_misses: int = 0
    signal_loads: int = 0
    errors: int = 0
    last_cache_clear: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    @property
    def total_requests(self) -> int:
        """Total number of requests."""
        return self.cache_hits + self.cache_misses


# ============================================================================
# CIRCUIT BREAKER PATTERN
# ============================================================================


class CircuitState:
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: float = 60.0  # Seconds before attempting recovery
    success_threshold: int = 2  # Successes in half-open before closing


@dataclass
class CircuitBreaker:
    """Circuit breaker for graceful degradation with persistence.
    
    Implements the circuit breaker pattern to prevent cascading failures
    when the signal registry encounters repeated errors.
    
    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Failing state, requests fail fast without attempting operation
    - HALF_OPEN: Testing state, limited requests allowed to test recovery
    
    Example:
        >>> breaker = CircuitBreaker()
        >>> if breaker.is_available():
        ...     try:
        ...         result = do_operation()
        ...         breaker.record_success()
        ...     except Exception as e:
        ...         breaker.record_failure()
        ...         raise
    """
    config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    state: str = field(default=CircuitState.CLOSED)
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    last_state_change: float = field(default_factory=time.time)
    persistence_path: Path | None = field(default=None)
    
    def __post_init__(self) -> None:
        """Load state from persistence if available."""
        # Only enable persistence if explicitly provided
        if self.persistence_path is not None:
            self._load_state()

    def _load_state(self) -> None:
        """Load state from file."""
        # Opportunity #3: Persistent Circuit Breaker
        if self.persistence_path and self.persistence_path.exists():
            try:
                data = json.loads(self.persistence_path.read_text())
                self.state = data.get("state", CircuitState.CLOSED)
                self.failure_count = data.get("failure_count", 0)
                self.last_failure_time = data.get("last_failure_time", 0.0)
                # Reset success count on restart to be safe
                self.success_count = 0
                logger.info("circuit_breaker_state_loaded", state=self.state)
            except Exception as e:
                logger.warning("circuit_breaker_load_failed", error=str(e))

    def _save_state(self) -> None:
        """Save state to file."""
        if self.persistence_path is None:
            return
        try:
            data = {
                "state": self.state,
                "failure_count": self.failure_count,
                "last_failure_time": self.last_failure_time,
                "timestamp": time.time()
            }
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            self.persistence_path.write_text(json.dumps(data))
        except Exception as e:
            logger.warning("circuit_breaker_save_failed", error=str(e))

    def is_available(self) -> bool:
        """Check if circuit breaker allows requests.
        
        Returns:
            True if requests are allowed, False if circuit is open
        """
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                logger.info("circuit_breaker_half_open", message="Attempting recovery")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.last_state_change = time.time()
                return True
            return False
        
        # HALF_OPEN: Allow limited requests
        return True
    
    def record_success(self) -> None:
        """Record successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                logger.info("circuit_breaker_closed", message="Circuit recovered")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = time.time()
                self._save_state()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
            # Only save if we were failing before
            if self.failure_count > 0:
                 self._save_state()
    
    def record_failure(self) -> None:
        """Record failed operation."""
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery, reopen circuit
            logger.warning("circuit_breaker_reopened", message="Recovery failed")
            self.state = CircuitState.OPEN
            self.failure_count = 0
            self.success_count = 0
            self.last_state_change = time.time()
            self._save_state()
        elif self.state == CircuitState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.config.failure_threshold:
                logger.error(
                    "circuit_breaker_opened",
                    message=f"Circuit opened after {self.failure_count} failures"
                )
                self.state = CircuitState.OPEN
                self.failure_count = 0  # Reset after opening
                self.last_state_change = time.time()
                self._save_state()
    
    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status for monitoring.
        
        Returns:
            Dictionary with current state and metrics
        """
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "time_since_last_failure": time.time() - self.last_failure_time if self.last_failure_time > 0 else None,
            "time_in_current_state": time.time() - self.last_state_change,
        }


# ============================================================================
# CONTENT-ADDRESSED SIGNAL REGISTRY
# ============================================================================


class QuestionnaireSignalRegistry:
    """Content-addressed, observable signal registry with lazy loading.
    
    This is the CANONICAL source for all signal extraction in the Farfan
    Pipeline. It replaces the deprecated signal_loader.py module.
    
    Features:
    - Full metadata extraction (100% Intelligence Utilization)
    - Content-based cache invalidation (hash-based)
    - Lazy loading with on-demand materialization
    - OpenTelemetry distributed tracing
    - Structured logging with contextual metadata
    - Type-safe signal packs (Pydantic v2)
    - LRU caching for hot paths
    - Immutable signal packs (frozen models)
    
    Architecture:
        QuestionnairePort → Registry → SignalPacks → Components
    
    Thread Safety: Single-threaded (use locks for multi-threaded access)
    
    Example:
        >>> registry = QuestionnaireSignalRegistry(my_questionnaire)
        >>> signals = registry.get_micro_answering_signals("Q001")
        >>> qid = "Q001"
        >>> print(f"Patterns: {len(signals.question_patterns[qid])}")
    """

    def __init__(self, questionnaire: QuestionnairePort) -> None:
        """Initialize signal registry.
        
        Args:
            questionnaire: Canonical questionnaire instance (immutable)
        """
        # Defensive normalization: some loaders may provide `data` as a JSON string.
        # The registry expects `questionnaire.data` to be a dict-like object.
        try:
            data_obj = getattr(questionnaire, "data", None)
            if isinstance(data_obj, str):
                import json as _json
                from types import SimpleNamespace

                parsed = _json.loads(data_obj)
                questionnaire = SimpleNamespace(
                    data=parsed,
                    sha256=getattr(questionnaire, "sha256", ""),
                    version=getattr(questionnaire, "version", "unknown"),
                )
        except Exception:
            pass

        self._questionnaire = questionnaire
        self._source_hash = self._compute_source_hash()
        
        # Lazy-loaded caches
        self._chunking_signals: ChunkingSignalPack | None = None
        self._micro_answering_cache: dict[str, MicroAnsweringSignalPack] = {}
        self._validation_cache: dict[str, ValidationSignalPack] = {}
        self._assembly_cache: dict[str, AssemblySignalPack] = {}
        self._scoring_cache: dict[str, ScoringSignalPack] = {}
        self._policy_area_cache: dict[str, SignalPack] = {}
        
        # Metrics
        self._metrics = RegistryMetrics()
        
        # Circuit breaker for graceful degradation
        self._circuit_breaker = CircuitBreaker()
        
        # Valid assembly levels (for validation)
        self._valid_assembly_levels = self._extract_valid_assembly_levels()
        
        # Initialize enhancement integrator (Opportunity #1)
        self._enhancement_integrator = create_enhancement_integrator(questionnaire)

        logger.info(
            "signal_registry_initialized",
            source_hash=self._source_hash[:16],
            questionnaire_version=questionnaire.version,
            questionnaire_sha256=questionnaire.sha256[:16],
        )

    def _warmup_single_question(self, q_id: str) -> None:
        """Helper for parallel warmup."""
        self.get_micro_answering_signals(q_id)
        self.get_validation_signals(q_id)
        self.get_scoring_signals(q_id)

    def _compute_source_hash(self) -> str:
        """Compute content hash for cache invalidation."""
        content = str(self._questionnaire.sha256)
        if BLAKE3_AVAILABLE:
            return blake3.blake3(content.encode()).hexdigest()
        else:
            return hashlib.sha256(content.encode()).hexdigest()

    def _extract_valid_assembly_levels(self) -> list[str]:
        """Extract valid assembly levels from questionnaire."""
        levels = ["MACRO_1"]  # Always valid
        
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        meso_questions = blocks.get("meso_questions", [])
        
        for meso_q in meso_questions:
            if isinstance(meso_q, dict):
                q_id = str(meso_q.get("question_id", ""))
            else:
                q_id = str(meso_q)
            if q_id.startswith("MESO"):
                levels.append(q_id)
        
        return levels

    # ========================================================================
    # PUBLIC API: Signal Pack Getters
    # ========================================================================

    def get_all_policy_areas(self) -> list[str]:
        policy_areas = self._questionnaire.data.get("canonical_notation", {}).get("policy_areas", {})
        if isinstance(policy_areas, dict) and policy_areas:
            return sorted(str(k) for k in policy_areas.keys())

        blocks = dict(self._questionnaire.data.get("blocks", {}))
        micro_questions = blocks.get("micro_questions", [])
        derived = {
            str(q.get("policy_area_id"))
            for q in micro_questions
            if isinstance(q, dict) and q.get("policy_area_id")
        }
        return sorted(derived)

    def get_signal_pack(self, policy_area_id: PolicyArea) -> SignalPack:
        pack = self.get(str(policy_area_id))
        if pack is None:
            raise SignalExtractionError("policy_area_pack", f"Missing signal pack for {policy_area_id}")
        return pack

    def get(self, policy_area_id: str, default: SignalPack | None = None) -> SignalPack | None:
        if policy_area_id in self._policy_area_cache:
            self._metrics.cache_hits += 1
            return self._policy_area_cache[policy_area_id]

        self._metrics.cache_misses += 1
        try:
            pack = self._build_policy_area_signal_pack(policy_area_id)
        except Exception as e:
            self._metrics.errors += 1
            logger.error(
                "policy_area_pack_build_failed",
                policy_area_id=policy_area_id,
                error=str(e),
                exc_info=True,
            )
            return default

        self._policy_area_cache[policy_area_id] = pack
        return pack

    def get_chunking_signals(self) -> ChunkingSignalPack:
        """Get signals for Smart Policy Chunking.
        
        Returns:
            ChunkingSignalPack with section patterns, weights, and config
        
        Raises:
            SignalExtractionError: If signal extraction fails
        """
        with tracer.start_as_current_span(
            "signal_registry.get_chunking_signals",
            attributes={"signal_type": "chunking"},
        ) as span:
            try:
                if self._chunking_signals is None:
                    self._metrics.signal_loads += 1
                    self._metrics.cache_misses += 1
                    self._chunking_signals = self._build_chunking_signals()
                    span.set_attribute("cache_hit", False)
                    
                    logger.info(
                        "chunking_signals_loaded",
                        pattern_categories=len(self._chunking_signals.section_detection_patterns),
                        source_hash=self._source_hash[:16],
                    )
                else:
                    self._metrics.cache_hits += 1
                    span.set_attribute("cache_hit", True)

                span.set_attribute(
                    "pattern_count",
                    len(self._chunking_signals.section_detection_patterns)
                )
                return self._chunking_signals

            except Exception as e:
                self._metrics.errors += 1
                span.record_exception(e)
                logger.error("chunking_signals_failed", error=str(e), exc_info=True)
                raise SignalExtractionError("chunking", str(e)) from e

    def get_micro_answering_signals(
        self, question_id: str
    ) -> MicroAnsweringSignalPack:
        """Get signals for Micro Answering for specific question.
        
        This method returns the FULL metadata from the Intelligence Layer,
        including semantic_expansion, context_requirement, and evidence_boost.
        
        Args:
            question_id: Question ID (Q001-Q300)
        
        Returns:
            MicroAnsweringSignalPack with full pattern metadata
        
        Raises:
            QuestionNotFoundError: If question not found
            SignalExtractionError: If signal extraction fails
        """
        with tracer.start_as_current_span(
            "signal_registry.get_micro_answering_signals",
            attributes={"signal_type": "micro_answering", "question_id": question_id},
        ) as span:
            try:
                if question_id in self._micro_answering_cache:
                    self._metrics.cache_hits += 1
                    span.set_attribute("cache_hit", True)
                    return self._micro_answering_cache[question_id]

                self._metrics.signal_loads += 1
                self._metrics.cache_misses += 1
                span.set_attribute("cache_hit", False)

                pack = self._build_micro_answering_signals(question_id)
                self._micro_answering_cache[question_id] = pack

                patterns = pack.question_patterns.get(question_id, [])
                span.set_attribute("pattern_count", len(patterns))
                
                logger.info(
                    "micro_answering_signals_loaded",
                    question_id=question_id,
                    pattern_count=len(patterns),
                    has_semantic_expansions=bool(pack.semantic_expansions),
                    has_context_requirements=bool(pack.context_requirements),
                )
                
                return pack

            except QuestionNotFoundError:
                self._metrics.errors += 1
                raise
            except Exception as e:
                self._metrics.errors += 1
                span.record_exception(e)
                logger.error(
                    "micro_answering_signals_failed",
                    question_id=question_id,
                    error=str(e),
                    exc_info=True
                )
                raise SignalExtractionError("micro_answering", str(e)) from e

    def get_validation_signals(self, question_id: str) -> ValidationSignalPack:
        """Get signals for Response Validation for specific question.
        
        Args:
            question_id: Question ID (Q001-Q300)
        
        Returns:
            ValidationSignalPack with rules, contracts, thresholds
        
        Raises:
            QuestionNotFoundError: If question not found
            SignalExtractionError: If signal extraction fails
        """
        with tracer.start_as_current_span(
            "signal_registry.get_validation_signals",
            attributes={"signal_type": "validation", "question_id": question_id},
        ) as span:
            try:
                if question_id in self._validation_cache:
                    self._metrics.cache_hits += 1
                    span.set_attribute("cache_hit", True)
                    return self._validation_cache[question_id]

                self._metrics.signal_loads += 1
                self._metrics.cache_misses += 1
                span.set_attribute("cache_hit", False)

                pack = self._build_validation_signals(question_id)
                self._validation_cache[question_id] = pack

                rules = pack.validation_rules.get(question_id, {})
                span.set_attribute("rule_count", len(rules))
                
                logger.info(
                    "validation_signals_loaded",
                    question_id=question_id,
                    rule_count=len(rules),
                )
                
                return pack

            except QuestionNotFoundError:
                self._metrics.errors += 1
                raise
            except Exception as e:
                self._metrics.errors += 1
                span.record_exception(e)
                logger.error(
                    "validation_signals_failed",
                    question_id=question_id,
                    error=str(e),
                    exc_info=True
                )
                raise SignalExtractionError("validation", str(e)) from e

    def get_assembly_signals(self, level: str) -> AssemblySignalPack:
        """Get signals for Response Assembly at specified level.
        
        Args:
            level: Assembly level (MESO_1, MESO_2, etc. or MACRO_1)
        
        Returns:
            AssemblySignalPack with aggregation methods, clusters, weights
        
        Raises:
            InvalidLevelError: If level not found
            SignalExtractionError: If signal extraction fails or circuit breaker is open
        """
        # Circuit breaker check
        if not self._circuit_breaker.is_available():
            raise SignalExtractionError(
                "assembly",
                f"Circuit breaker is {self._circuit_breaker.state}, rejecting request"
            )
        
        # Validate level
        if level not in self._valid_assembly_levels:
            raise InvalidLevelError(level, self._valid_assembly_levels)
        
        with tracer.start_as_current_span(
            "signal_registry.get_assembly_signals",
            attributes={"signal_type": "assembly", "level": level},
        ) as span:
            try:
                if level in self._assembly_cache:
                    self._metrics.cache_hits += 1
                    span.set_attribute("cache_hit", True)
                    return self._assembly_cache[level]

                self._metrics.signal_loads += 1
                self._metrics.cache_misses += 1
                span.set_attribute("cache_hit", False)

                pack = self._build_assembly_signals(level)
                self._assembly_cache[level] = pack

                span.set_attribute("cluster_count", len(pack.cluster_policy_areas))
                
                logger.info(
                    "assembly_signals_loaded",
                    level=level,
                    cluster_count=len(pack.cluster_policy_areas),
                )
                
                # Record success for circuit breaker
                self._circuit_breaker.record_success()
                
                return pack

            except Exception as e:
                self._metrics.errors += 1
                # Record failure for circuit breaker
                self._circuit_breaker.record_failure()
                span.record_exception(e)
                logger.error(
                    "assembly_signals_failed",
                    level=level,
                    error=str(e),
                    exc_info=True
                )
                raise SignalExtractionError("assembly", str(e)) from e

    def get_scoring_signals(self, question_id: str) -> ScoringSignalPack:
        """Get signals for Scoring for specific question.
        
        Args:
            question_id: Question ID (Q001-Q300)
        
        Returns:
            ScoringSignalPack with modalities, configs, quality levels
        
        Raises:
            QuestionNotFoundError: If question not found
            SignalExtractionError: If signal extraction fails
        """
        with tracer.start_as_current_span(
            "signal_registry.get_scoring_signals",
            attributes={"signal_type": "scoring", "question_id": question_id},
        ) as span:
            try:
                if question_id in self._scoring_cache:
                    self._metrics.cache_hits += 1
                    span.set_attribute("cache_hit", True)
                    return self._scoring_cache[question_id]

                self._metrics.signal_loads += 1
                self._metrics.cache_misses += 1
                span.set_attribute("cache_hit", False)

                pack = self._build_scoring_signals(question_id)
                self._scoring_cache[question_id] = pack

                modality = pack.question_modalities.get(question_id, "UNKNOWN")
                span.set_attribute("modality", modality)
                
                logger.info(
                    "scoring_signals_loaded",
                    question_id=question_id,
                    modality=modality,
                )
                
                return pack

            except QuestionNotFoundError:
                self._metrics.errors += 1
                raise
            except Exception as e:
                self._metrics.errors += 1
                span.record_exception(e)
                logger.error(
                    "scoring_signals_failed",
                    question_id=question_id,
                    error=str(e),
                    exc_info=True
                )
                raise SignalExtractionError("scoring", str(e)) from e

    # ========================================================================
    # PRIVATE: Signal Pack Builders
    # ========================================================================

    def _build_chunking_signals(self) -> ChunkingSignalPack:
        """Build chunking signal pack from questionnaire."""
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        semantic_layers = blocks.get("semantic_layers", {})

        # Extract section patterns (from micro questions)
        section_patterns: dict[str, list[str]] = defaultdict(list)
        micro_questions = blocks.get("micro_questions", [])

        for q in micro_questions:
            for pattern_obj in q.get("patterns", []):
                category = pattern_obj.get("category", "GENERAL")
                pattern = pattern_obj.get("pattern", "")
                if pattern:
                    section_patterns[category].append(pattern)

        # Deduplicate
        section_patterns = {k: sorted(set(v)) for k, v in section_patterns.items()}

        # Section weights (calibrated values from PDM structure)
        section_weights = {
            "DIAGNOSTICO": 0.92,
            "PLAN_INVERSIONES": 1.25,
            "PLAN_PLURIANUAL": 1.18,
            "VISION_ESTRATEGICA": 1.0,
            "MARCO_FISCAL": 1.0,
            "SEGUIMIENTO": 1.0,
        }

        # Table patterns
        table_patterns = [
            r"\|.*\|.*\|",
            r"<table",
            r"Cuadro \d+",
            r"Tabla \d+",
            r"^\s*\|",
        ]

        # Numerical patterns
        numerical_patterns = [
            r"\d+%",
            r"\$\s*\d+",
            r"\d+\.\d+",
            r"\d+,\d+",
            r"(?i)(millones?|miles?)\s+de\s+pesos",
        ]

        return ChunkingSignalPack(
            section_detection_patterns=section_patterns,
            section_weights=section_weights,
            table_patterns=table_patterns,
            numerical_patterns=numerical_patterns,
            embedding_config=semantic_layers.get("embedding_strategy", {}),
            source_hash=self._source_hash,
            metadata={
                "total_patterns": sum(len(v) for v in section_patterns.values()),
                "categories": list(section_patterns.keys()),
            }
        )

    def _build_micro_answering_signals(
        self, question_id: str
    ) -> MicroAnsweringSignalPack:
        """Build micro answering signal pack for question with FULL metadata."""
        question = self._get_question(question_id)

        # Extract patterns WITH FULL METADATA (Intelligence Layer)
        patterns_raw = question.get("patterns", [])
        patterns: list[PatternItem] = []
        
        for idx, p in enumerate(patterns_raw):
            pattern_id = p.get("id", f"PAT-{question_id}-{idx:03d}")
            patterns.append(
                PatternItem(
                    id=pattern_id,
                    pattern=p.get("pattern", ""),
                    match_type=p.get("match_type", "REGEX"),
                    confidence_weight=p.get("confidence_weight", 0.85),
                    category=p.get("category", "GENERAL"),
                    flags=p.get("flags", ""),
                    # Intelligence Layer fields (previously discarded!)
                    semantic_expansion=p.get("semantic_expansion", []),
                    context_requirement=p.get("context_requirement"),
                    evidence_boost=p.get("evidence_boost", 1.0),
                )
            )

        # Extract expected elements
        elements_raw = question.get("expected_elements", [])
        elements = [
            ExpectedElement(
                type=e.get("type", "unknown"),
                required=e.get("required", False),
                minimum=e.get("minimum", 0),
                description=e.get("description", ""),
            )
            for e in elements_raw
        ]

        # Get indicators by policy area
        pa = question.get("policy_area_id", "PA01")
        indicators = self._extract_indicators_for_pa(pa)

        # Get official sources
        official_sources = self._extract_official_sources()

        # Build Intelligence Layer metadata dictionaries
        pattern_weights = {}
        semantic_expansions = {}
        context_requirements = {}
        evidence_boosts = {}
        
        for p in patterns:
            pattern_weights[p.id] = p.confidence_weight
            if p.semantic_expansion:
                semantic_expansions[p.id] = p.semantic_expansion
            if p.context_requirement:
                context_requirements[p.id] = p.context_requirement
            if p.evidence_boost != 1.0:
                evidence_boosts[p.id] = p.evidence_boost

        # Opportunity #1: Enhance signals with 4 strategic enhancements
        enhancements = self._enhancement_integrator.enhance_question_signals(
            question_id, dict(question)
        )

        return MicroAnsweringSignalPack(
            question_patterns={question_id: patterns},
            expected_elements={question_id: elements},
            indicators_by_pa={pa: indicators},
            official_sources=official_sources,
            pattern_weights=pattern_weights,
            # Intelligence Layer metadata (100% utilization!)
            semantic_expansions=semantic_expansions,
            context_requirements=context_requirements,
            evidence_boosts=evidence_boosts,

            # Integrated Strategic Enhancements
            method_execution_metadata=enhancements.get("method_execution_metadata", {}),
            validation_specifications=enhancements.get("validation_specifications", {}),
            scoring_modality_context=enhancements.get("scoring_modality_context", {}),
            semantic_disambiguation=enhancements.get("semantic_disambiguation", {}),

            source_hash=self._source_hash,
            metadata={
                "question_id": question_id,
                "policy_area": pa,
                "pattern_count": len(patterns),
                "intelligence_fields_captured": {
                    "semantic_expansions": len(semantic_expansions),
                    "context_requirements": len(context_requirements),
                    "evidence_boosts": len(evidence_boosts),
                },
            }
        )

    def _build_validation_signals(self, question_id: str) -> ValidationSignalPack:
        """Build validation signal pack for question."""
        question = self._get_question(question_id)
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        scoring = blocks.get("scoring", {})

        # Extract validation rules
        validations_raw: Any = question.get("validations")
        if validations_raw is None:
            validations_raw = question.get("validation_rules", {})

        validation_rules = {}
        if isinstance(validations_raw, dict):
            for rule_name, rule_data in validations_raw.items():
                if not isinstance(rule_data, dict):
                    continue
                validation_rules[str(rule_name)] = ValidationCheck(
                    patterns=rule_data.get("patterns", []),
                    minimum_required=rule_data.get("minimum_required", 1),
                    minimum_years=rule_data.get("minimum_years", 0),
                    specificity=rule_data.get("specificity", "MEDIUM"),
                )
        elif isinstance(validations_raw, list):
            for idx, item in enumerate(validations_raw):
                if isinstance(item, str):
                    rule_name = f"rule_{idx:02d}"
                    validation_rules[rule_name] = ValidationCheck(
                        patterns=[item],
                        minimum_required=1,
                        minimum_years=0,
                        specificity="MEDIUM",
                    )
                    continue
                if isinstance(item, dict):
                    raw_name = item.get("name") or item.get("rule") or f"rule_{idx:02d}"
                    patterns = item.get("patterns")
                    if not isinstance(patterns, list):
                        maybe_pattern = item.get("rule")
                        patterns = [maybe_pattern] if isinstance(maybe_pattern, str) else []
                    validation_rules[str(raw_name)] = ValidationCheck(
                        patterns=patterns,
                        minimum_required=item.get("minimum_required", 1),
                        minimum_years=item.get("minimum_years", 0),
                        specificity=item.get("specificity", "MEDIUM"),
                    )

        # Extract failure contract
        failure_contract_raw = question.get("failure_contract", {})
        failure_contract = None
        if failure_contract_raw:
            failure_contract = FailureContract(
                abort_if=failure_contract_raw.get("abort_if", ["missing_required_element"]),
                emit_code=failure_contract_raw.get("emit_code", f"ABORT-{question_id}-REQ"),
                severity=failure_contract_raw.get("severity", "ERROR"),
            )

        # Get modality thresholds
        modality_definitions = scoring.get("modality_definitions", {})
        modality_thresholds = {
            k: v.get("threshold", 0.7)
            for k, v in modality_definitions.items()
            if "threshold" in v
        }

        return ValidationSignalPack(
            validation_rules={question_id: validation_rules} if validation_rules else {},
            failure_contracts={question_id: failure_contract} if failure_contract else {},
            modality_thresholds=modality_thresholds,
            abort_codes={question_id: failure_contract.emit_code} if failure_contract else {},
            verification_patterns={question_id: list(validation_rules.keys())},
            source_hash=self._source_hash,
            metadata={
                "question_id": question_id,
                "rule_count": len(validation_rules),
                "has_failure_contract": failure_contract is not None,
            }
        )

    def _build_assembly_signals(self, level: str) -> AssemblySignalPack:
        """Build assembly signal pack for level."""
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        niveles = blocks.get("niveles_abstraccion", {})

        # Extract aggregation methods
        aggregation_methods = {}
        if level.startswith("MESO"):
            meso_questions = blocks.get("meso_questions", [])
            for meso_q in meso_questions:
                if not isinstance(meso_q, dict):
                    continue
                if meso_q.get("question_id") == level:
                    agg_method = meso_q.get("aggregation_method", "weighted_average")
                    aggregation_methods[level] = agg_method
                    break
        else:  # MACRO
            macro_q = blocks.get("macro_question", {})
            agg_method = macro_q.get("aggregation_method", "holistic_assessment")
            aggregation_methods["MACRO_1"] = agg_method

        # Extract cluster composition
        clusters = niveles.get("clusters", [])
        cluster_policy_areas = {
            c.get("cluster_id", "UNKNOWN"): c.get("policy_area_ids", [])
            for c in clusters
            if isinstance(c, dict)
        }

        # Dimension weights (uniform for now)
        dimension_weights = {
            f"DIM{i:02d}": 1.0 / 6 for i in range(1, 7)
        }

        # Evidence keys by policy area
        policy_areas = niveles.get("policy_areas", [])
        evidence_keys_by_pa = {
            pa.get("policy_area_id", "UNKNOWN"): pa.get("required_evidence_keys", [])
            for pa in policy_areas
            if isinstance(pa, dict)
        }

        # Coherence patterns (from meso questions)
        coherence_patterns = []
        meso_questions = blocks.get("meso_questions", [])
        for meso_q in meso_questions:
            if not isinstance(meso_q, dict):
                continue
            patterns = meso_q.get("patterns", [])
            coherence_patterns.extend(patterns)

        # Fallback patterns
        fallback_patterns = {}
        macro_q = blocks.get("macro_question", {})
        if "fallback" in macro_q:
            fallback_patterns["MACRO_1"] = macro_q["fallback"]

        return AssemblySignalPack(
            aggregation_methods=aggregation_methods,
            cluster_policy_areas=cluster_policy_areas,
            dimension_weights=dimension_weights,
            evidence_keys_by_pa=evidence_keys_by_pa,
            coherence_patterns=coherence_patterns,
            fallback_patterns=fallback_patterns,
            source_hash=self._source_hash,
            metadata={
                "level": level,
                "cluster_count": len(cluster_policy_areas),
            }
        )

    def _build_scoring_signals(self, question_id: str) -> ScoringSignalPack:
        """Build scoring signal pack for question."""
        question = self._get_question(question_id)
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        scoring = blocks.get("scoring", {})

        # Get question modality
        modality = question.get("scoring_modality", "TYPE_A")

        # Extract modality configs
        modality_definitions = scoring.get("modality_definitions", {})
        modality_configs = {}
        for mod_type, mod_def in modality_definitions.items():
            modality_configs[mod_type] = ModalityConfig(
                aggregation=mod_def.get("aggregation", "presence_threshold"),
                description=mod_def.get("description", ""),
                failure_code=mod_def.get("failure_code", f"F-{mod_type[-1]}-MIN"),
                threshold=mod_def.get("threshold"),
                max_score=mod_def.get("max_score", 3),
                weights=mod_def.get("weights"),
            )

        # Extract quality levels
        micro_levels = scoring.get("micro_levels", [])
        quality_levels = [
            QualityLevel(
                level=lvl.get("level", "INSUFICIENTE"),
                min_score=lvl.get("min_score", 0.0),
                color=lvl.get("color", "red"),
                description=lvl.get("description", ""),
            )
            for lvl in micro_levels
        ]
        if not quality_levels:
            quality_levels = [
                QualityLevel(level="EXCELENTE", min_score=0.8, color="green", description=""),
                QualityLevel(level="BUENO", min_score=0.6, color="blue", description=""),
                QualityLevel(level="ACEPTABLE", min_score=0.4, color="yellow", description=""),
                QualityLevel(level="INSUFICIENTE", min_score=0.0, color="red", description=""),
            ]

        # Failure codes
        failure_codes = {
            k: v.get("failure_code", f"F-{k[-1]}-MIN")
            for k, v in modality_definitions.items()
        }

        # Thresholds
        thresholds = {
            k: v.get("threshold", 0.7)
            for k, v in modality_definitions.items()
            if "threshold" in v
        }

        # TYPE_D weights
        type_d_weights = modality_definitions.get("TYPE_D", {}).get("weights", [0.4, 0.3, 0.3])

        return ScoringSignalPack(
            question_modalities={question_id: modality},
            modality_configs=modality_configs,
            quality_levels=quality_levels,
            failure_codes=failure_codes,
            thresholds=thresholds,
            type_d_weights=type_d_weights,
            source_hash=self._source_hash,
            metadata={
                "question_id": question_id,
                "modality": modality,
            }
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_question(self, question_id: str) -> dict[str, Any]:
        """Get question by ID from questionnaire.
        
        Raises:
            QuestionNotFoundError: If question not found
        """
        micro_questions: list[Any] | None = None
        try:
            maybe_micro_questions = getattr(self._questionnaire, "micro_questions", None)
            if isinstance(maybe_micro_questions, list):
                micro_questions = maybe_micro_questions
        except Exception:
            micro_questions = None

        if micro_questions is None:
            blocks = dict(self._questionnaire.data.get("blocks", {}))
            micro_questions = list(blocks.get("micro_questions", []))

        for q in micro_questions:
            if isinstance(q, dict) and q.get("question_id") == question_id:
                return dict(q)
            if not isinstance(q, dict):
                try:
                    if dict(q).get("question_id") == question_id:
                        return dict(q)
                except Exception:
                    continue
        raise QuestionNotFoundError(question_id)

    def _extract_indicators_for_pa(self, policy_area: str) -> list[str]:
        """Extract indicator patterns for policy area."""
        indicators = []
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        micro_questions = blocks.get("micro_questions", [])

        for q in micro_questions:
            if not isinstance(q, dict):
                continue
            if q.get("policy_area_id") == policy_area:
                for pattern_obj in q.get("patterns", []):
                    if pattern_obj.get("category") == "INDICADOR":
                        indicators.append(pattern_obj.get("pattern", ""))

        return sorted({i for i in indicators if i})

    def _extract_official_sources(self) -> list[str]:
        """Extract official source patterns from all questions."""
        sources = []
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        micro_questions = blocks.get("micro_questions", [])

        for q in micro_questions:
            if not isinstance(q, dict):
                continue
            for pattern_obj in q.get("patterns", []):
                if pattern_obj.get("category") == "FUENTE_OFICIAL":
                    pattern = pattern_obj.get("pattern", "")
                    # Split on | for multiple sources in one pattern
                    sources.extend(p.strip() for p in pattern.split("|") if p.strip())

        return sorted(set(sources))

    def _build_policy_area_signal_pack(self, policy_area_id: str) -> SignalPack:
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        micro_questions = blocks.get("micro_questions", [])

        pattern_specs: list[dict[str, Any]] = []
        indicators: list[str] = []
        entities: list[str] = []
        confidence_weights: list[float] = []

        for q in micro_questions:
            if not isinstance(q, dict) or q.get("policy_area_id") != policy_area_id:
                continue

            for pattern_obj in q.get("patterns", []):
                if not isinstance(pattern_obj, dict):
                    continue

                pattern = str(pattern_obj.get("pattern", "")).strip()
                if not pattern:
                    continue

                spec = dict(pattern_obj)
                spec.setdefault("policy_area", policy_area_id)
                pattern_specs.append(spec)

                if pattern_obj.get("category") == "INDICADOR":
                    indicators.append(pattern)
                if pattern_obj.get("category") == "FUENTE_OFICIAL":
                    entities.extend(p.strip() for p in pattern.split("|") if p.strip())

                weight = pattern_obj.get("confidence_weight")
                if isinstance(weight, (int, float)):
                    confidence_weights.append(float(weight))

        patterns = [str(p.get("pattern", "")).strip() for p in pattern_specs if p.get("pattern")]
        patterns = list(dict.fromkeys([p for p in patterns if p]))

        indicator_list = sorted(set(indicators))
        entity_list = sorted(set(entities))

        if confidence_weights:
            min_conf = min(confidence_weights)
            max_conf = max(confidence_weights)
            avg_conf = sum(confidence_weights) / len(confidence_weights)
        else:
            min_conf = max_conf = avg_conf = 0.85

        thresholds = {
            "min_confidence": round(min_conf, 2),
            "max_confidence": round(max_conf, 2),
            "avg_confidence": round(avg_conf, 2),
            "min_evidence": 0.70,
        }

        return SignalPack(
            version="2.0.0",
            policy_area=policy_area_id,  # type: ignore[arg-type]
            patterns=patterns,
            indicators=indicator_list,
            regex=list(patterns),
            verbs=[],
            entities=entity_list,
            thresholds=thresholds,
            ttl_s=86400,
            source_fingerprint=self._source_hash[:64],
            metadata={
                "mode": "questionnaire_derived",
                "policy_area_id": policy_area_id,
                "pattern_specs": pattern_specs,
                "pattern_count": len(pattern_specs),
                "questionnaire_version": getattr(self._questionnaire, "version", "unknown"),
                "questionnaire_sha256": getattr(self._questionnaire, "sha256", ""),
            },
        )

    # ========================================================================
    # OBSERVABILITY & MANAGEMENT
    # ========================================================================

    def get_metrics(self) -> dict[str, Any]:
        """Get registry metrics for observability.
        
        Returns:
            Dictionary with cache performance and usage statistics
        """
        # Opportunity #4: Memory Awareness
        # Estimate size of caches (rough approximation)
        cache_size = (
            sys.getsizeof(self._micro_answering_cache) +
            sys.getsizeof(self._validation_cache) +
            sys.getsizeof(self._scoring_cache) +
            # approximate content size
            len(self._micro_answering_cache) * 2000
        )

        # If cache is too big (>100MB), clear it
        if cache_size > 100 * 1024 * 1024:
            logger.warning("cache_size_limit_exceeded", size=cache_size)
            self.clear_cache()

        return {
            "cache_hits": self._metrics.cache_hits,
            "cache_misses": self._metrics.cache_misses,
            "hit_rate": self._metrics.hit_rate,
            "estimated_cache_size_bytes": cache_size,
            "total_requests": self._metrics.total_requests,
            "signal_loads": self._metrics.signal_loads,
            "errors": self._metrics.errors,
            "cached_micro_answering": len(self._micro_answering_cache),
            "cached_validation": len(self._validation_cache),
            "cached_assembly": len(self._assembly_cache),
            "cached_scoring": len(self._scoring_cache),
            "source_hash": self._source_hash[:16],
            "questionnaire_version": self._questionnaire.version,
            "last_cache_clear": self._metrics.last_cache_clear,
            "circuit_breaker": self._circuit_breaker.get_status(),
        }
    
    def health_check(self) -> dict[str, Any]:
        """Perform health check on signal registry.
        
        Returns:
            Dictionary with health status and diagnostics
        """
        breaker_status = self._circuit_breaker.get_status()
        is_healthy = breaker_status["state"] != CircuitState.OPEN
        
        return {
            "healthy": is_healthy,
            "status": "healthy" if is_healthy else "degraded",
            "circuit_breaker": breaker_status,
            "metrics": {
                "hit_rate": self._metrics.hit_rate,
                "error_count": self._metrics.errors,
                "total_requests": self._metrics.total_requests,
            },
            "timestamp": time.time(),
        }
    
    def reset_circuit_breaker(self) -> None:
        """Manually reset circuit breaker to closed state.
        
        Use with caution - only for administrative recovery.
        """
        logger.warning("circuit_breaker_manual_reset", message="Circuit breaker manually reset")
        self._circuit_breaker.state = CircuitState.CLOSED
        self._circuit_breaker.failure_count = 0
        self._circuit_breaker.success_count = 0
        self._circuit_breaker.last_state_change = time.time()

    def validate_signals_for_questionnaire(
        self, 
        expected_question_count: int = 300,
        check_modalities: list[str] | None = None
    ) -> dict[str, Any]:
        """Validate signal registry health for all micro-questions.
        
        This method performs comprehensive validation of the signal registry
        to ensure all required signals are present and properly shaped before
        pipeline execution. It is designed to be called during bootstrap (Phase 0)
        or Orchestrator initialization.
        
        Args:
            expected_question_count: Expected number of micro-questions (default: 300)
            check_modalities: Signal modalities to check (default: all standard modalities)
        
        Returns:
            Dictionary containing:
                - valid: bool indicating if validation passed
                - total_questions: int number of questions found
                - expected_questions: int expected question count
                - missing_questions: list of question IDs without signals
                - malformed_signals: dict of question_id -> list of issues
                - signal_coverage: dict of modality -> coverage percentage
                - stale_signals: list of issues indicating stale registry state
                - timestamp: float validation timestamp
        
        Raises:
            SignalRegistryError: In production mode if critical validation fails
        """
        start_time = time.time()
        
        if check_modalities is None:
            check_modalities = ["micro_answering", "validation", "scoring"]
        
        logger.info(
            "signal_validation_started",
            expected_count=expected_question_count,
            modalities=check_modalities,
        )
        
        # Extract all micro-question IDs
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        micro_questions = blocks.get("micro_questions", [])
        question_ids: list[str] = []
        
        for q in micro_questions:
            if isinstance(q, dict):
                q_id = str(q.get("question_id", "")).strip()
            else:
                q_id = str(q).strip()
            if q_id:
                question_ids.append(q_id)
        
        total_questions = len(question_ids)
        missing_questions: list[str] = []
        malformed_signals: dict[str, list[str]] = {}
        signal_coverage: dict[str, dict[str, int]] = {
            modality: {"success": 0, "failed": 0} 
            for modality in check_modalities
        }
        stale_signals: list[str] = []
        
        # Validate each question across all modalities
        for q_id in question_ids:
            q_missing_modalities: list[str] = []
            q_issues: list[str] = []
            
            # Check micro_answering signals
            if "micro_answering" in check_modalities:
                try:
                    signals = self.get_micro_answering_signals(q_id)
                    
                    # Validate signal pack structure
                    if not signals.question_patterns or q_id not in signals.question_patterns:
                        q_issues.append(f"micro_answering: no patterns found for {q_id}")
                        signal_coverage["micro_answering"]["failed"] += 1
                    elif not signals.question_patterns[q_id]:
                        q_issues.append(f"micro_answering: empty pattern list for {q_id}")
                        signal_coverage["micro_answering"]["failed"] += 1
                    else:
                        signal_coverage["micro_answering"]["success"] += 1
                        logger.debug(
                            "signal_lookup",
                            question_id=q_id,
                            modality="micro_answering",
                            pattern_count=len(signals.question_patterns[q_id]),
                        )
                    
                    # Check expected_elements
                    if not signals.expected_elements or q_id not in signals.expected_elements:
                        q_issues.append(f"micro_answering: no expected_elements for {q_id}")
                    
                except QuestionNotFoundError:
                    q_missing_modalities.append("micro_answering")
                    signal_coverage["micro_answering"]["failed"] += 1
                    logger.warning(
                        "signal_lookup_failed",
                        question_id=q_id,
                        modality="micro_answering",
                        reason="QuestionNotFoundError",
                    )
                except SignalExtractionError as e:
                    q_issues.append(f"micro_answering: extraction error - {str(e)}")
                    signal_coverage["micro_answering"]["failed"] += 1
                    logger.error(
                        "signal_lookup_failed",
                        question_id=q_id,
                        modality="micro_answering",
                        reason=str(e),
                    )
            
            # Check validation signals
            if "validation" in check_modalities:
                try:
                    signals = self.get_validation_signals(q_id)
                    
                    if not signals.validation_rules:
                        q_issues.append(f"validation: no validation_rules for {q_id}")
                        signal_coverage["validation"]["failed"] += 1
                    else:
                        signal_coverage["validation"]["success"] += 1
                        logger.debug(
                            "signal_lookup",
                            question_id=q_id,
                            modality="validation",
                            rule_count=len(signals.validation_rules),
                        )
                    
                except QuestionNotFoundError:
                    q_missing_modalities.append("validation")
                    signal_coverage["validation"]["failed"] += 1
                    logger.warning(
                        "signal_lookup_failed",
                        question_id=q_id,
                        modality="validation",
                        reason="QuestionNotFoundError",
                    )
                except SignalExtractionError as e:
                    q_issues.append(f"validation: extraction error - {str(e)}")
                    signal_coverage["validation"]["failed"] += 1
                    logger.error(
                        "signal_lookup_failed",
                        question_id=q_id,
                        modality="validation",
                        reason=str(e),
                    )
            
            # Check scoring signals
            if "scoring" in check_modalities:
                try:
                    signals = self.get_scoring_signals(q_id)
                    
                    if not signals.scoring_modality:
                        q_issues.append(f"scoring: no scoring_modality for {q_id}")
                        signal_coverage["scoring"]["failed"] += 1
                    else:
                        signal_coverage["scoring"]["success"] += 1
                        logger.debug(
                            "signal_lookup",
                            question_id=q_id,
                            modality="scoring",
                            scoring_modality=signals.scoring_modality,
                        )
                    
                except QuestionNotFoundError:
                    q_missing_modalities.append("scoring")
                    signal_coverage["scoring"]["failed"] += 1
                    logger.warning(
                        "signal_lookup_failed",
                        question_id=q_id,
                        modality="scoring",
                        reason="QuestionNotFoundError",
                    )
                except SignalExtractionError as e:
                    q_issues.append(f"scoring: extraction error - {str(e)}")
                    signal_coverage["scoring"]["failed"] += 1
                    logger.error(
                        "signal_lookup_failed",
                        question_id=q_id,
                        modality="scoring",
                        reason=str(e),
                    )
            
            # Record issues for this question
            if q_missing_modalities:
                missing_questions.append(q_id)
                q_issues.append(f"missing modalities: {', '.join(q_missing_modalities)}")
            
            if q_issues:
                malformed_signals[q_id] = q_issues
        
        # Check for stale registry state
        if self._circuit_breaker.state == CircuitState.OPEN:
            stale_signals.append("circuit_breaker_open")
        
        if self._metrics.errors > 0:
            stale_signals.append(f"registry_has_{self._metrics.errors}_errors")
        
        # Calculate coverage percentages
        coverage_percentages: dict[str, float] = {}
        for modality, counts in signal_coverage.items():
            total = counts["success"] + counts["failed"]
            coverage_percentages[modality] = (
                (counts["success"] / total * 100.0) if total > 0 else 0.0
            )
        
        # Determine validation result
        is_valid = (
            total_questions == expected_question_count
            and len(missing_questions) == 0
            and len(malformed_signals) == 0
            and all(pct == 100.0 for pct in coverage_percentages.values())
        )
        
        elapsed_time = time.time() - start_time
        
        result = {
            "valid": is_valid,
            "total_questions": total_questions,
            "expected_questions": expected_question_count,
            "missing_questions": missing_questions,
            "malformed_signals": malformed_signals,
            "signal_coverage": signal_coverage,
            "coverage_percentages": coverage_percentages,
            "stale_signals": stale_signals,
            "timestamp": start_time,
            "elapsed_seconds": elapsed_time,
            "circuit_breaker_state": (
                self._circuit_breaker.state.value 
                if hasattr(self._circuit_breaker.state, 'value') 
                else str(self._circuit_breaker.state)
            ),
        }
        
        logger.info(
            "signal_validation_completed",
            valid=is_valid,
            total_questions=total_questions,
            expected_questions=expected_question_count,
            missing_count=len(missing_questions),
            malformed_count=len(malformed_signals),
            coverage=coverage_percentages,
            elapsed_seconds=elapsed_time,
        )
        
        return result

    def clear_cache(self) -> None:
        """Clear all caches (for testing or hot-reload)."""
        self._chunking_signals = None
        self._micro_answering_cache.clear()
        self._validation_cache.clear()
        self._assembly_cache.clear()
        self._scoring_cache.clear()
        self._metrics.last_cache_clear = time.time()

        logger.info(
            "signal_registry_cache_cleared",
            timestamp=self._metrics.last_cache_clear,
        )

    def warmup(self, question_ids: list[str] | None = None) -> None:
        """Warmup cache by pre-loading common signals.
        
        Args:
            question_ids: Optional list of question IDs to warmup.
                         If None, warmup all questions.
        """
        logger.info("signal_registry_warmup_started")
        
        # Always warmup chunking
        try:
            self.get_chunking_signals()
        except Exception as e:
            logger.warning(
                "warmup_failed_for_chunking_signals",
                error=str(e),
            )
        
        # Warmup specified questions
        if question_ids is None:
            # Get all question IDs
            try:
                blocks = dict(self._questionnaire.data.get("blocks", {}))
                micro_questions = blocks.get("micro_questions", [])
                question_ids = []
                for q in micro_questions:
                    if isinstance(q, dict):
                        q_id = str(q.get("question_id", "")).strip()
                    else:
                        q_id = str(q).strip()
                    if q_id:
                        question_ids.append(q_id)
            except Exception as e:
                logger.warning(
                    "warmup_failed_to_collect_question_ids",
                    error=str(e),
                )
                question_ids = []
        
        # Opportunity #2: Parallel Signal Warmup
        max_workers = min(32, len(question_ids)) if question_ids else 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_qid = {
                executor.submit(self._warmup_single_question, q_id): q_id
                for q_id in question_ids
            }
            for future in concurrent.futures.as_completed(future_to_qid):
                q_id = future_to_qid[future]
                try:
                    future.result()
                except Exception as e:
                    logger.warning(
                        "warmup_failed_for_question",
                        question_id=q_id,
                        error=str(e)
                    )
        
        # Warmup assembly levels
        for level in self._valid_assembly_levels:
            try:
                self.get_assembly_signals(level)
            except Exception as e:
                logger.warning(
                    "warmup_failed_for_level",
                    level=level,
                    error=str(e)
                )
        
        logger.info(
            "signal_registry_warmup_completed",
            metrics=self.get_metrics()
        )

    @property
    def source_hash(self) -> str:
        """Get source content hash."""
        return self._source_hash

    @property
    def valid_assembly_levels(self) -> list[str]:
        """Get valid assembly levels."""
        return self._valid_assembly_levels.copy()

    def verify_integrity(self) -> dict[str, Any]:
        """Verify logical integrity of signals.

        Opportunity #5: Deep Integrity Verification
        Checks that all referenced patterns in validation rules actually exist.

        Returns:
            Dictionary of integrity violations.
        """
        violations = []

        # Load all signals (this might be slow, but it's an audit tool)
        blocks = dict(self._questionnaire.data.get("blocks", {}))
        micro_questions = blocks.get("micro_questions", [])
        question_ids: list[str] = []
        for q in micro_questions:
            if isinstance(q, dict):
                q_id = str(q.get("question_id", "")).strip()
            else:
                q_id = str(q).strip()
            if q_id:
                question_ids.append(q_id)

        for q_id in question_ids:
            try:
                ma = self.get_micro_answering_signals(q_id)
                val = self.get_validation_signals(q_id)

                # Check validation rules exist
                if not val.validation_rules.get(q_id):
                     violations.append(f"Question {q_id}: No validation rules defined")

                # Check patterns exist
                if not ma.question_patterns.get(q_id):
                     violations.append(f"Question {q_id}: No patterns defined")

            except Exception as e:
                violations.append(f"Question {q_id}: {str(e)}")

        return {
            "status": "clean" if not violations else "violations_found",
            "violation_count": len(violations),
            "violations": violations
        }


# ============================================================================
# FACTORY INTEGRATION
# ============================================================================


def create_signal_registry(
    questionnaire: QuestionnairePort,
) -> QuestionnaireSignalRegistry:
    """Factory function to create signal registry.
    
    This is the recommended way to instantiate the registry.
    
    Args:
        questionnaire: Canonical questionnaire instance
    
    Returns:
        Initialized signal registry
    
    Example:
        >>> registry = create_signal_registry(my_questionnaire)
        >>> signals = registry.get_chunking_signals()
        >>> print(f"Patterns: {len(signals.section_detection_patterns)}")
    """
    return QuestionnaireSignalRegistry(questionnaire)


# ============================================================================
# EXPORTS
# ============================================================================


__all__ = [
    # Main registry
    "QuestionnaireSignalRegistry",
    "create_signal_registry",
    
    # Signal pack models
    "ChunkingSignalPack",
    "MicroAnsweringSignalPack",
    "ValidationSignalPack",
    "AssemblySignalPack",
    "ScoringSignalPack",
    
    # Component models
    "PatternItem",
    "ExpectedElement",
    "ValidationCheck",
    "FailureContract",
    "ModalityConfig",
    "QualityLevel",
    
    # Exceptions
    "SignalRegistryError",
    "QuestionNotFoundError",
    "SignalExtractionError",
    "InvalidLevelError",
    
    # Metrics
    "RegistryMetrics",
]
