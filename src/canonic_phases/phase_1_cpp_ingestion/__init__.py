"""Phase 1: CPP ingestion (CanonicalInput → CanonPolicyPackage).

Canonical phase name: `phase_1_cpp_ingestion`.
Constitutional invariant: exactly 60 chunks (10 policy areas × 6 dimensions).
"""

from __future__ import annotations

from canonic_phases.phase_0_input_validation.phase0_phase0_input_validation import CanonicalInput, Phase0Input
from canonic_phases.phase_1_cpp_ingestion.cpp_models import (
    CanonPolicyPackage,
    CanonPolicyPackageValidator,
    ChunkGraph,
    ChunkResolution,
    IntegrityIndex,
    LegacyChunk,
    PolicyManifest,
    QualityMetrics,
    TextSpan,
)
from canonic_phases.phase_1_cpp_ingestion.phase1_circuit_breaker import SubphaseCheckpoint
from canonic_phases.phase_1_cpp_ingestion.phase1_cpp_ingestion_full import (
    PADimGridSpecification,
    Phase1CPPIngestionFullContract,
    Phase1FatalError,
    Phase1FailureHandler,
    Phase1MissionContract,
    execute_phase_1_with_full_contract,
)
from canonic_phases.phase_1_cpp_ingestion.phase1_dependency_validator import validate_phase1_dependencies
from canonic_phases.phase_1_cpp_ingestion.phase1_models import (
    Arguments,
    CausalChains,
    CausalGraph,
    Chunk,
    Discourse,
    IntegratedCausal,
    KGEdge,
    KGNode,
    KnowledgeGraph,
    LanguageData,
    PreprocessedDoc,
    SmartChunk,
    Strategic,
    StructureData,
    Temporal,
    ValidationResult,
)
from canonic_phases.phase_1_cpp_ingestion.phase_protocol import (
    ContractValidationResult,
    PhaseContract,
    PhaseInvariant,
    PhaseMetadata,
)

__all__ = [
    # Phase 0 input
    "CanonicalInput",
    "Phase0Input",
    # Protocol
    "ContractValidationResult",
    "PhaseContract",
    "PhaseInvariant",
    "PhaseMetadata",
    # Phase 1 models
    "Arguments",
    "CausalChains",
    "CausalGraph",
    "Chunk",
    "Discourse",
    "IntegratedCausal",
    "KGEdge",
    "KGNode",
    "KnowledgeGraph",
    "LanguageData",
    "PreprocessedDoc",
    "SmartChunk",
    "Strategic",
    "StructureData",
    "Temporal",
    "ValidationResult",
    # Circuit breaker
    "SubphaseCheckpoint",
    # CPP models
    "CanonPolicyPackage",
    "CanonPolicyPackageValidator",
    "ChunkGraph",
    "ChunkResolution",
    "IntegrityIndex",
    "LegacyChunk",
    "PolicyManifest",
    "QualityMetrics",
    "TextSpan",
    # Execution contract
    "PADimGridSpecification",
    "Phase1CPPIngestionFullContract",
    "Phase1FatalError",
    "Phase1FailureHandler",
    "Phase1MissionContract",
    "execute_phase_1_with_full_contract",
    # Dependency validation
    "validate_phase1_dependencies",
]

