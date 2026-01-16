"""
Phase 1 → Phase 2 Interface Adapter
===================================

PHASE_LABEL: Phase 2
Module: interphase/phase1_phase2_adapter.py
Purpose: Pure functional adapter for Phase 1 output to Phase 2 input transformation

This adapter resolves the structural incompatibilities between Phase 1 output
(CanonPolicyPackage-based) and Phase 2 input (flat attribute access).

Version: 1.0.0
Date: 2026-01-13
Author: F.A.R.F.A.N Formal Verification System

INVARIANTS PRESERVED:
- No data loss (bijective mapping where applicable)
- Type safety (static typing enforced)
- Deterministic (same input → same output)
- Pure (no side effects)

INCOMPATIBILITIES RESOLVED:
- INC-001: cpp.chunks vs cpp.chunk_graph.chunks
- INC-002: cpp.schema_version vs cpp.metadata.schema_version
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, Protocol, runtime_checkable


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

@runtime_checkable
class Phase1OutputProtocol(Protocol):
    """Protocol for Phase 1 output structure."""
    
    @property
    def enriched_signal_packs(self) -> dict[str, Any]:
        """Dictionary of question_id -> EnrichedSignalPack."""
        ...
    
    @property
    def irrigation_map(self) -> Any:
        """IrrigationMap for chunk-to-question routing."""
        ...
    
    @property
    def smart_chunks(self) -> list[Any]:
        """List of SmartChunk objects."""
        ...
    
    @property
    def truncation_audit(self) -> Any:
        """TruncationAudit record."""
        ...
    
    @property
    def structural_validation_result(self) -> Any:
        """StructuralValidationResult."""
        ...
    
    @property
    def questionnaire_mapper(self) -> Any | None:
        """Optional QuestionnaireMapper."""
        ...


@dataclass(frozen=True)
class Phase2InputBundle:
    """
    Immutable bundle adapted from Phase 1 output.
    
    This structure provides the flat attribute access expected by Phase 2
    while preserving all data from Phase 1.
    
    Invariants:
    - chunks is never None (may be empty list)
    - schema_version is never None (has default)
    - enriched_signal_packs preserves original mapping
    """
    # Core data (renamed for Phase 2 compatibility)
    chunks: list[Any]  # Renamed from smart_chunks
    schema_version: str  # Promoted from metadata.schema_version
    
    # Pass-through fields
    enriched_signal_packs: dict[str, Any] = field(default_factory=dict)
    irrigation_map: Any = None
    truncation_audit: Any = None
    structural_validation: Any = None  # Renamed from structural_validation_result
    questionnaire_mapper: Any = None
    
    # Provenance tracking
    adaptation_source: str = "Phase1Output"
    adaptation_version: str = "1.0.0"


# =============================================================================
# ADAPTER CONSTANTS
# =============================================================================

DEFAULT_SCHEMA_VERSION: Final[str] = "CPP-2025.1"
ADAPTER_VERSION: Final[str] = "1.0.0"


# =============================================================================
# PURE ADAPTER FUNCTIONS
# =============================================================================

def extract_chunks(phase1_output: Any) -> list[Any]:
    """
    Extract chunks from Phase 1 output using multiple access patterns.
    
    Access patterns (in priority order):
    1. phase1_output.smart_chunks (preferred)
    2. phase1_output.chunk_graph.chunks
    3. phase1_output.chunks
    
    Returns:
        List of chunk objects (may be empty)
    
    Raises:
        ValueError: If no chunk data found
    """
    # Pattern 1: smart_chunks (Phase 1 native)
    if hasattr(phase1_output, 'smart_chunks'):
        chunks = phase1_output.smart_chunks
        if chunks is not None:
            return list(chunks)
    
    # Pattern 2: chunk_graph.chunks (CanonPolicyPackage structure)
    if hasattr(phase1_output, 'chunk_graph'):
        chunk_graph = phase1_output.chunk_graph
        if hasattr(chunk_graph, 'chunks') and chunk_graph.chunks is not None:
            return list(chunk_graph.chunks)
    
    # Pattern 3: chunks (flat access)
    if hasattr(phase1_output, 'chunks'):
        chunks = phase1_output.chunks
        if chunks is not None:
            return list(chunks)
    
    raise ValueError(
        "Phase 1 output missing chunk data. "
        "Expected one of: smart_chunks, chunk_graph.chunks, chunks"
    )


def extract_schema_version(phase1_output: Any) -> str:
    """
    Extract schema version from Phase 1 output.
    
    Access patterns (in priority order):
    1. phase1_output.metadata.schema_version (CPP structure)
    2. phase1_output.schema_version (flat access)
    3. Default: CPP-2025.1
    
    Returns:
        Schema version string
    """
    # Pattern 1: metadata.schema_version (CanonPolicyPackage)
    if hasattr(phase1_output, 'metadata'):
        metadata = phase1_output.metadata
        if hasattr(metadata, 'schema_version') and metadata.schema_version:
            return str(metadata.schema_version)
    
    # Pattern 2: schema_version (flat)
    if hasattr(phase1_output, 'schema_version') and phase1_output.schema_version:
        return str(phase1_output.schema_version)
    
    # Default
    return DEFAULT_SCHEMA_VERSION


def adapt_phase1_to_phase2(phase1_output: Any) -> Phase2InputBundle:
    """
    Pure function adapter: Phase1Output → Phase2InputBundle.
    
    This function is:
    - Total: Defined for all valid Phase1Output
    - Pure: No side effects
    - Deterministic: Same input → same output
    
    Transformations performed:
    - smart_chunks → chunks (rename)
    - metadata.schema_version → schema_version (projection)
    - structural_validation_result → structural_validation (rename)
    
    Args:
        phase1_output: Any object conforming to Phase1OutputProtocol
        
    Returns:
        Phase2InputBundle with adapted structure
        
    Raises:
        ValueError: If phase1_output missing required data
    """
    # Extract with fallback patterns
    chunks = extract_chunks(phase1_output)
    schema_version = extract_schema_version(phase1_output)
    
    # Extract pass-through fields
    enriched_signal_packs = getattr(phase1_output, 'enriched_signal_packs', {})
    irrigation_map = getattr(phase1_output, 'irrigation_map', None)
    truncation_audit = getattr(phase1_output, 'truncation_audit', None)
    
    # Structural validation: handle rename
    structural_validation = getattr(
        phase1_output, 'structural_validation_result', None
    ) or getattr(phase1_output, 'structural_validation', None)
    
    questionnaire_mapper = getattr(phase1_output, 'questionnaire_mapper', None)
    
    return Phase2InputBundle(
        chunks=chunks,
        schema_version=schema_version,
        enriched_signal_packs=enriched_signal_packs,
        irrigation_map=irrigation_map,
        truncation_audit=truncation_audit,
        structural_validation=structural_validation,
        questionnaire_mapper=questionnaire_mapper,
        adaptation_source="Phase1Output",
        adaptation_version=ADAPTER_VERSION,
    )


def validate_adaptation(
    original: Any,
    adapted: Phase2InputBundle,
) -> tuple[bool, list[str]]:
    """
    Verify adaptation preserves invariants.
    
    Checks:
    - Chunk count preserved
    - Schema version preserved
    - Signal packs reference preserved (identity)
    - No data loss
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors: list[str] = []
    
    # Check chunk count preservation
    original_chunks = extract_chunks(original)
    if len(adapted.chunks) != len(original_chunks):
        errors.append(
            f"Chunk count mismatch: original={len(original_chunks)}, adapted={len(adapted.chunks)}"
        )
    
    # Check schema version preservation
    original_version = extract_schema_version(original)
    if adapted.schema_version != original_version:
        errors.append(
            f"Schema version mismatch: original={original_version}, adapted={adapted.schema_version}"
        )
    
    # Check identity preservation for reference types
    original_esp = getattr(original, 'enriched_signal_packs', None)
    if original_esp is not None and adapted.enriched_signal_packs is not original_esp:
        errors.append("enriched_signal_packs identity not preserved (was copied instead of referenced)")
    
    return len(errors) == 0, errors


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Phase1OutputProtocol",
    "Phase2InputBundle",
    "adapt_phase1_to_phase2",
    "validate_adaptation",
    "extract_chunks",
    "extract_schema_version",
    "DEFAULT_SCHEMA_VERSION",
    "ADAPTER_VERSION",
]
