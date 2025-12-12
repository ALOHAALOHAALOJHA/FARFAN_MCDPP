"""Orchestrator utilities with contract validation on import."""

from __future__ import annotations

# NEW: Evidence processing - REAL PATH: canonic_phases.Phase_two.evidence_nexus
# Replaces evidence_assembler, evidence_validator, evidence_registry
from canonic_phases.Phase_two.evidence_nexus import (
    EvidenceNexus,
    EvidenceGraph,
    EvidenceNode,
    process_evidence,
)

# NEW: Narrative synthesis - REAL PATH: canonic_phases.Phase_two.carver
from canonic_phases.Phase_two.carver import (
    DoctoralCarverSynthesizer,
    CarverAnswer,
)

# Executor config - REAL PATH: canonic_phases.Phase_two.executor_config
from canonic_phases.Phase_two.executor_config import ExecutorConfig

# Resource management - REAL PATHS: orchestration.*
from orchestration.resource_alerts import (
    AlertChannel,
    AlertSeverity,
    ResourceAlert,
    ResourceAlertManager,
)
from orchestration.resource_aware_executor import (
    ResourceAwareExecutor,
    ResourceConstraints,
)
from orchestration.resource_integration import (
    create_resource_manager,
    get_resource_status,
    integrate_with_orchestrator,
    reset_circuit_breakers,
)
from orchestration.resource_manager import (
    AdaptiveResourceManager,
    CircuitBreaker,
    CircuitState,
    DegradationStrategy,
    ExecutorPriority,
    ResourceAllocationPolicy,
    ResourcePressureLevel,
)

# Signal intelligence - REAL PATH: cross_cutting_infrastrucuture.irrigation_using_signals.SISAS
from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_intelligence_layer import (
    EnrichedSignalPack,
    create_enriched_signal_pack,
)

# Signature validation - REAL PATHS: orchestration.*
from orchestration.method_signature_validator import (
    MethodSignatureValidator,
)
from orchestration.signature_runtime_validator import (
    SignatureRuntimeValidator,
    ValidationResult as SignatureValidationResult,
    get_runtime_validator,
    validate_method_call,
)
from orchestration.signature_types import (
    MethodSignature,
    ValidationReport,
)

__all__ = [
    # NEW: Evidence processing (EvidenceNexus)
    "EvidenceNexus",
    "EvidenceGraph",
    "EvidenceNode",
    "process_evidence",
    # NEW: Narrative synthesis (Carver)
    "DoctoralCarverSynthesizer",
    "CarverAnswer",
    # Resource management
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
    # Config
    "ExecutorConfig",
    # Signal intelligence
    "EnrichedSignalPack",
    "create_enriched_signal_pack",
    # Signature validation
    "MethodSignatureValidator",
    "SignatureRuntimeValidator",
    "SignatureValidationResult",
    "get_runtime_validator",
    "validate_method_call",
    "MethodSignature",
    "ValidationReport",
]
