"""
Phase Ingestion Shim
=====================

This module provides compatibility mapping from legacy phase names to
the new canonical phase system.

Legacy auditors expect `ingestion`, `generation`, and `synthesis` modules.
This shim maps `ingestion` to the modern `phase1_spc_ingestion`.

For new code, use the canonical phase modules directly:
- phase0_input_validation
- phase1_spc_ingestion
- phase2_types
"""

# Re-export Phase 1 SPC Ingestion as "ingestion"
from saaaaaa.core.phases.phase1_spc_ingestion import (
    Phase1SPCIngestionContract,
    PHASE1_VERSION,
    EXPECTED_CHUNK_COUNT,
    POLICY_AREAS,
    DIMENSIONS,
    SubfaseMetadata,
)

__all__ = [
    "Phase1SPCIngestionContract",
    "PHASE1_VERSION",
    "EXPECTED_CHUNK_COUNT",
    "POLICY_AREAS",
    "DIMENSIONS",
    "SubfaseMetadata",
]
