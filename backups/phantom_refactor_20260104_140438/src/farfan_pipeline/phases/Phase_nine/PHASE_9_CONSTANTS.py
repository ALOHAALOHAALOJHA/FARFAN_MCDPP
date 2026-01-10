"""
Module: src.farfan_pipeline.phases.Phase_nine.PHASE_9_CONSTANTS
Purpose: Global constants for Phase 9 - Report Generation
Owner: phase9_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-30
"""

from __future__ import annotations

from typing import Final

__version__ = "1.0.0"
__phase__ = 9

# ============================================================================
# PHASE IDENTIFICATION
# ============================================================================

PHASE_NUMBER: Final[int] = 9
PHASE_NAME: Final[str] = "Phase 9: Report Generation"
PHASE_LABEL: Final[str] = f"Phase {PHASE_NUMBER}"

# ============================================================================
# STAGE DEFINITIONS
# ============================================================================

STAGE_BASE: Final[int] = 0
STAGE_INIT: Final[int] = 10
STAGE_ASSEMBLY: Final[int] = 20
STAGE_OUTPUT: Final[int] = 30

VALID_STAGES: Final[set[int]] = {
    STAGE_BASE,
    STAGE_INIT,
    STAGE_ASSEMBLY,
    STAGE_OUTPUT,
}

# ============================================================================
# MODULE TYPES
# ============================================================================

TYPE_GENERATOR: Final[str] = "GEN"
TYPE_ASSEMBLER: Final[str] = "ASM"
TYPE_UTILITY: Final[str] = "UTIL"

# ============================================================================
# CRITICALITY LEVELS
# ============================================================================

CRITICALITY_HIGH: Final[str] = "HIGH"
CRITICALITY_MEDIUM: Final[str] = "MEDIUM"

# ============================================================================
# EXECUTION PATTERNS
# ============================================================================

PATTERN_ON_DEMAND: Final[str] = "On-Demand"

# ============================================================================
# DETERMINISM
# ============================================================================

DEFAULT_SEED: Final[int] = 42
SEED_STRATEGY: Final[str] = "FIXED"
