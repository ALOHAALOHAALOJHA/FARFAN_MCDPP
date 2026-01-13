"""
Phase 0 Primitives - Canonical Type Definitions
================================================

This module defines the fundamental primitive types used throughout the F.A.R.F.A.N pipeline.
It serves as the ground truth for type definitions, ensuring consistency and type safety across all phases.

Primitives Defined:
-------------------
- **PrimitiveType**: Base types supported in contracts (str, int, float, bool, None)
- **JsonDict**: Type alias for JSON-serializable dictionaries
- **PathLike**: Type alias for path-like objects (str, Path)
- **HashStr**: Strong type for SHA-256/BLAKE3 hash strings
- **Timestamp**: Strong type for ISO 8601 timestamps
- **PolicyAreaID**: Canonical identifiers for policy areas (PA01-PA10)
- **DimensionID**: Canonical identifiers for dimensions (D01-D04)

Usage:
------
from farfan_pipeline.phases.Phase_zero.phase0_00_03_primitives import HashStr, PolicyAreaID

def validate_hash(h: HashStr) -> bool: ...

Author: F.A.R.F.A.N Architecture Team
Date: 2026-01-07
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Literal, NewType, Union, Final

# =============================================================================
# BASE TYPE ALIASES
# =============================================================================

PrimitiveType = Union[str, int, float, bool, None]
JsonDict = Dict[str, Any]  # Loosely typed dict for JSON compatibility
PathLike = Union[str, Path]

# =============================================================================
# STRONG TYPES (NewType)
# =============================================================================

# Cryptographic Hashes (expected to be hex strings)
HashStr = NewType("HashStr", str)

# ISO 8601 Timestamps
Timestamp = NewType("Timestamp", str)

# UUIDs (version 4)
UUIDStr = NewType("UUIDStr", str)

# Run Identifiers (e.g., "run_20260107_123456")
RunID = NewType("RunID", str)

# =============================================================================
# DOMAIN SPECIFIC LITERALS
# =============================================================================

# Canonical Policy Area IDs
PolicyAreaID = Literal[
    "PA01", "PA02", "PA03", "PA04", "PA05",
    "PA06", "PA07", "PA08", "PA09", "PA10"
]

# Canonical Dimension IDs
DimensionID = Literal["D01", "D02", "D03", "D04"]

# Phase Identifiers
PhaseID = Literal[
    "phase0", "phase1", "phase2", "phase3",
    "phase4", "phase5", "phase6", "phase7"
]

# Criticality Levels (matching constants)
CriticalityLevel = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]

# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def validate_hash_str(h: str, alg: str = "sha256") -> bool:
    """
    Validate that a string is a valid hex hash.
    
    Args:
        h: The hash string to validate
        alg: Algorithm used (sha256 or blake3 default to 64 chars)
        
    Returns:
        True if valid hex string of correct length
    """
    if alg in ("sha256", "blake3"):
        return bool(re.match(r"^[a-f0-9]{64}$", h, re.IGNORECASE))
    return False

def validate_policy_area_id(pa_id: str) -> bool:
    """Validate a policy area ID format."""
    return pa_id in [
        "PA01", "PA02", "PA03", "PA04", "PA05",
        "PA06", "PA07", "PA08", "PA09", "PA10"
    ]

def validate_dimension_id(dim_id: str) -> bool:
    """Validate a dimension ID format."""
    return dim_id in ["D01", "D02", "D03", "D04"]

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PrimitiveType",
    "JsonDict",
    "PathLike",
    "HashStr",
    "Timestamp",
    "UUIDStr",
    "RunID",
    "PolicyAreaID",
    "DimensionID",
    "PhaseID",
    "CriticalityLevel",
    "validate_hash_str",
    "validate_policy_area_id",
    "validate_dimension_id",
]
