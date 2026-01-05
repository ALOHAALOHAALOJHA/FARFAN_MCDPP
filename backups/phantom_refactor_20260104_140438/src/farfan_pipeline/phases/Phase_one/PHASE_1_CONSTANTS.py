"""
Phase 1 Constants - Authoritative Configuration Values. 

Purpose: Centralize all magic numbers, limits, and thresholds for Phase 1.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State: ACTIVE

All values MUST be documented with rationale and referenced by constant name in code.
"""

from typing import Final

# =============================================================================
# SPEC-001: PDF Extraction Limits
# =============================================================================

PDF_EXTRACTION_CHAR_LIMIT: Final[int] = 1_000_000
"""
Maximum characters to extract from PDF before truncation. 

Rationale: 1M chars ≈ 500 pages of dense text (2000 chars/page average).
This bounds memory usage during extraction while retaining sufficient content
for most government policy documents (typically 50-200 pages).

Trade-off: Documents exceeding this limit will be truncated.  The TruncationAudit
record captures the loss ratio for downstream decision-making.
"""

# =============================================================================
# SPEC-002: Semantic Confidence Normalization
# =============================================================================

SEMANTIC_SCORE_MAX_EXPECTED: Final[float] = 3.0
"""
Maximum expected raw semantic score for normalization.

Composition: 
  - Policy Area keyword match: 0.0 - 1.0
  - Dimension keyword match: 0.0 - 1.0
  - Signal boost (priority terms): 0.0 - 1.0
  - Total: 0.0 - 3.0

Normalization: semantic_confidence = min(1.0, raw_score / SEMANTIC_SCORE_MAX_EXPECTED)
"""

ASSIGNMENT_METHOD_SEMANTIC:  Final[str] = "semantic"
ASSIGNMENT_METHOD_FALLBACK: Final[str] = "fallback_sequential"

VALID_ASSIGNMENT_METHODS: Final[tuple[str, ...]] = (
    ASSIGNMENT_METHOD_SEMANTIC,
    ASSIGNMENT_METHOD_FALLBACK,
)

# =============================================================================
# SPEC-003: Chunk Validation
# =============================================================================

CHUNK_ID_PATTERN: Final[str] = r'^PA(0[1-9]|10)-DIM0[1-6]$'
"""
Regex pattern for valid chunk_id format.

Examples:
  - PA01-DIM01 ✅
  - PA10-DIM06 ✅
  - PA11-DIM01 ❌ (PA out of range)
  - PA01-DIM07 ❌ (DIM out of range)
"""

POLICY_AREA_COUNT:  Final[int] = 10
DIMENSION_COUNT: Final[int] = 6
TOTAL_CHUNK_COMBINATIONS: Final[int] = POLICY_AREA_COUNT * DIMENSION_COUNT  # 60

# =============================================================================
# SPEC-004: Subphase Configuration
# =============================================================================

SUBPHASE_COUNT: Final[int] = 16  # SP0 through SP15

# Keys in subphase_results that are NOT integer subphase indices
SUBPHASE_METADATA_KEYS: Final[tuple[str, ...]] = (
    'truncation_audit',
    'irrigation_map',
    'final_rankings',
)

# =============================================================================
# SPEC-005: Logging Configuration
# =============================================================================

PHASE1_LOGGER_NAME: Final[str] = "farfan_pipeline. phases.Phase_one"

# =============================================================================
# SPEC-006: Determinism
# =============================================================================

RANDOM_SEED: Final[int] = 42
