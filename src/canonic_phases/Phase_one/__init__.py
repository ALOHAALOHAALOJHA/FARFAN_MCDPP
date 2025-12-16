"""
Phase One: CPP Ingestion - F.A.R.F.A.N Pipeline
================================================

This package contains the canonical implementation of Phase 1:

Phase 1: CPP Ingestion (CanonicalInput → CanonPolicyPackage)
    - 16 sub-phases (SP0-SP15)
    - EXACTLY 60 chunks (10 Policy Areas × 6 Dimensions)
    - Full provenance tracking
    - Constitutional invariants enforced

CANONICAL SOURCES:
- Policy Areas: canonic_questionnaire_central/questionnaire_monolith.json → canonical_notation.policy_areas
- Dimensions: canonic_questionnaire_central/questionnaire_monolith.json → canonical_notation.dimensions
- Signals: src/cross_cutting_infrastructure/irrigation_using_signals/SISAS/

INVARIANTS:
- chunk_count == 60
- execution_trace entries == 16
- schema_version == "CPP-2025.1"
"""

# Phase Protocol
from canonic_phases.Phase_one.phase_protocol import (
    ContractValidationResult,
    PhaseContract,
    PhaseInvariant,
    PhaseMetadata,
)

# Phase 0: Input Validation
from canonic_phases.Phase_one.phase0_input_validation import (
    CanonicalInput,
    Phase0Input,
)

# Phase 1: Models
from canonic_phases.Phase_one.phase1_models import (
    LanguageData,
    PreprocessedDoc,
    StructureData,
    KnowledgeGraph,
    KGNode,
    KGEdge,
    Chunk,
    SmartChunk,
    ValidationResult,
    CausalGraph,
)

# Phase 1: Main Executor
from canonic_phases.Phase_one.phase1_cpp_ingestion_full import (
    Phase1CPPIngestionFullContract,
    execute_phase_1_with_full_contract,
    PADimGridSpecification,
    Phase1FatalError,
    Phase1FailureHandler,
)

# CPP Models - PRODUCTION (NO STUBS)
from canonic_phases.Phase_one.cpp_models import (
    CanonPolicyPackage,
    CanonPolicyPackageValidator,
    ChunkGraph,
    QualityMetrics,
    IntegrityIndex,
    PolicyManifest,
    LegacyChunk,
    TextSpan,
    ChunkResolution,
)

__all__ = [
    # Protocol
    "ContractValidationResult",
    "PhaseContract",
    "PhaseInvariant",
    "PhaseMetadata",
    # Phase 0
    "CanonicalInput",
    "Phase0Input",
    # Phase 1 Models
    "LanguageData",
    "PreprocessedDoc",
    "StructureData",
    "KnowledgeGraph",
    "KGNode",
    "KGEdge",
    "Chunk",
    "SmartChunk",
    "ValidationResult",
    "CausalGraph",
    # Phase 1 Executor
    "Phase1CPPIngestionFullContract",
    "execute_phase_1_with_full_contract",
    "PADimGridSpecification",
    "Phase1FatalError",
    "Phase1FailureHandler",
    # CPP Models (PRODUCTION)
    "CanonPolicyPackage",
    "CanonPolicyPackageValidator",
    "ChunkGraph",
    "QualityMetrics",
    "IntegrityIndex",
    "PolicyManifest",
    "LegacyChunk",
    "TextSpan",
    "ChunkResolution",
]
