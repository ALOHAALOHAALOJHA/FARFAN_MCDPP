"""Orchestrator utilities with contract validation on import."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from farfan_pipeline.core.orchestrator.questionnaire import CanonicalQuestionnaire

from farfan_pipeline.core.orchestrator.core import (
    AbortRequested,
    AbortSignal,
    Evidence,
    MethodExecutor,
    MicroQuestionRun,
    Orchestrator,
    PhaseInstrumentation,
    PhaseResult,
    ResourceLimits,
    ScoredMicroQuestion,
)
from farfan_pipeline.core.orchestrator.evidence_registry import (
    EvidenceRecord,
    EvidenceRegistry,
    ProvenanceDAG,
    ProvenanceNode,
    get_global_registry,
)
from farfan_pipeline.core.orchestrator.executor_config import ExecutorConfig
from farfan_pipeline.core.orchestrator.parameter_loader import (
    CONSERVATIVE_CONFIG,
    get_conservative_defaults,
    load_executor_config,
)
from farfan_pipeline.core.orchestrator.pdt_quality_integration import (
    PDTSectionQuality,
)
from farfan_pipeline.core.orchestrator.resource_alerts import (
    AlertChannel,
    AlertSeverity,
    ResourceAlert,
    ResourceAlertManager,
)
from farfan_pipeline.core.orchestrator.resource_aware_executor import (
    ResourceAwareExecutor,
    ResourceConstraints,
)
from farfan_pipeline.core.orchestrator.resource_integration import (
    create_resource_manager,
    get_resource_status,
    integrate_with_orchestrator,
    reset_circuit_breakers,
)
from farfan_pipeline.core.orchestrator.resource_manager import (
    AdaptiveResourceManager,
    CircuitBreaker,
    CircuitState,
    DegradationStrategy,
    ExecutorPriority,
    ResourceAllocationPolicy,
    ResourcePressureLevel,
)
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    BOOST_FACTORS,
    PDT_QUALITY_THRESHOLDS,
    EnrichedSignalPack,
    PDTQualityMetrics,
    apply_pdt_quality_boost,
    compute_pdt_section_quality,
    create_enriched_signal_pack,
    track_pdt_precision_correlation,
)
from farfan_pipeline.core.types import ChunkData, PreprocessedDocument, Provenance

# Signature validation (lazy import to avoid circular dependencies)
try:
    from farfan_pipeline.core.orchestrator.method_signature_validator import (
        MethodSignatureValidator,
    )
    from farfan_pipeline.core.orchestrator.signature_runtime_validator import (
        SignatureRuntimeValidator,
        ValidationResult as SignatureValidationResult,
        get_runtime_validator,
        validate_method_call,
    )
    from farfan_pipeline.core.orchestrator.signature_mixin import (
        SignatureValidationMixin,
        ValidatedMethodDecorator,
    )
    from farfan_pipeline.core.orchestrator.signature_types import (
        MethodSignature,
        ValidationReport,
    )
    
    _SIGNATURE_VALIDATION_AVAILABLE = True
except ImportError:
    _SIGNATURE_VALIDATION_AVAILABLE = False
    MethodSignatureValidator = None  # type: ignore
    SignatureRuntimeValidator = None  # type: ignore
    SignatureValidationResult = None  # type: ignore
    get_runtime_validator = None  # type: ignore
    validate_method_call = None  # type: ignore
    SignatureValidationMixin = None  # type: ignore
    ValidatedMethodDecorator = None  # type: ignore
    MethodSignature = None  # type: ignore
    ValidationReport = None  # type: ignore

__all__ = [
    "EvidenceRecord",
    "EvidenceRegistry",
    "ProvenanceDAG",
    "ProvenanceNode",
    "get_global_registry",
    "Orchestrator",
    "MethodExecutor",
    "PreprocessedDocument",
    "ChunkData",
    "Provenance",
    "Evidence",
    "AbortSignal",
    "AbortRequested",
    "ResourceLimits",
    "PhaseInstrumentation",
    "PhaseResult",
    "MicroQuestionRun",
    "ScoredMicroQuestion",
    "AdaptiveResourceManager",
    "CircuitBreaker",
    "CircuitState",
    "DegradationStrategy",
    "ExecutorPriority",
    "ResourceAllocationPolicy",
    "ResourcePressureLevel",
    "ResourceAwareExecutor",
    "ResourceConstraints",
    "AlertChannel",
    "AlertSeverity",
    "ResourceAlert",
    "ResourceAlertManager",
    "create_resource_manager",
    "integrate_with_orchestrator",
    "get_resource_status",
    "reset_circuit_breakers",
    "ExecutorConfig",
    "load_executor_config",
    "get_conservative_defaults",
    "CONSERVATIVE_CONFIG",
    "EnrichedSignalPack",
    "create_enriched_signal_pack",
    "PDTQualityMetrics",
    "PDTSectionQuality",
    "compute_pdt_section_quality",
    "apply_pdt_quality_boost",
    "track_pdt_precision_correlation",
    "PDT_QUALITY_THRESHOLDS",
    "BOOST_FACTORS",
    # Signature validation
    "MethodSignatureValidator",
    "SignatureRuntimeValidator",
    "SignatureValidationResult",
    "get_runtime_validator",
    "validate_method_call",
    "SignatureValidationMixin",
    "ValidatedMethodDecorator",
    "MethodSignature",
    "ValidationReport",
]
