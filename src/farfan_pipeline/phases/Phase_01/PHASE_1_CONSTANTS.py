"""
Phase 1 Constants - Authoritative Configuration Values.

Purpose: Centralize all magic numbers, limits, and thresholds for Phase 1.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State: ACTIVE

All values MUST be documented with rationale and referenced by constant name in code.

ARCHITECTURE (v2.1):
Phase 1 produces 60 chunks (10 PA × 6 DIM).
Phase 2 expands to 300 tasks (60 chunks × 5 questions per chunk).
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 1
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"



from typing import Final

# =============================================================================
# QUESTIONNAIRE CONSTANTS (Phase 2 Expansion)
# =============================================================================

TOTAL_QUESTIONS: Final[int] = 300
"""
Total number of questions that Phase 2 will process.

Phase 1 produces 60 chunks (10 PA × 6 DIM).
Phase 2 expands each chunk into 5 question tasks = 300 total tasks.
"""

QUESTIONS_PER_SLOT: Final[int] = 5
"""
Number of questions per chunk slot (used in Phase 2).

Each chunk from Phase 1 (PA-DIM combination) is expanded into 5 question tasks
by Phase 2, giving us 300 total tasks (60 chunks × 5 Q/slot).
"""

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

ASSIGNMENT_METHOD_SEMANTIC: Final[str] = "semantic"
ASSIGNMENT_METHOD_FALLBACK: Final[str] = "fallback_sequential"

VALID_ASSIGNMENT_METHODS: Final[tuple[str, ...]] = (
    ASSIGNMENT_METHOD_SEMANTIC,
    ASSIGNMENT_METHOD_FALLBACK,
)

# =============================================================================
# SPEC-003: Chunk Validation (UPDATED v2.1)
# =============================================================================

# Phase 1 chunk granularity
POLICY_AREA_COUNT: Final[int] = 10
DIMENSION_COUNT: Final[int] = 6

# Phase 1: 60 chunks (PA×DIM) - CONSTITUTIONAL INVARIANT v2.1
TOTAL_CHUNK_COMBINATIONS: Final[int] = POLICY_AREA_COUNT * DIMENSION_COUNT  # 60

# Phase 2: Each chunk expanded into 5 questions
QUESTIONS_PER_DIMENSION: Final[int] = 5  # Q1-Q5 per PA×DIM combination (used in Phase 2)
PHASE2_TOTAL_TASKS: Final[int] = TOTAL_CHUNK_COMBINATIONS * QUESTIONS_PER_DIMENSION  # 300

# Chunk ID patterns (Phase 1: PA×DIM only)
CHUNK_ID_PATTERN: Final[str] = r"^PA(0[1-9]|10)-DIM0[1-6]$"
"""
Phase 1 chunk_id pattern for PA×DIM combinations.

Examples:
  - PA01-DIM01 ✅
  - PA10-DIM06 ✅
  - PA11-DIM01 ❌ (PA out of range 1-10)
  - PA01-DIM07 ❌ (DIM out of range 1-6)
"""

# Task ID patterns (Phase 2: PA×DIM×Q)
TASK_ID_PATTERN: Final[str] = r"^PA(0[1-9]|10)-DIM0[1-6]-Q[1-5]$"
"""
Phase 2 task_id pattern for question-level tasks (PA×DIM×Q).

Examples:
  - PA01-DIM01-Q1 ✅
  - PA10-DIM06-Q5 ✅
  - PA01-DIM01-Q6 ❌ (Q slot out of range 1-5)
"""

QUESTION_ID_PATTERN: Final[str] = r"^Q([1-9]|[1-9][0-9]|[12][0-9][0-9]|300)$"
"""
Pattern for valid question_id from questionnaire.

Examples:
  - Q001 ✅
  - Q056 ✅
  - Q300 ✅
  - Q301 ❌ (out of range)
"""

# =============================================================================
# SPEC-004: Subphase Configuration
# =============================================================================

SUBPHASE_COUNT: Final[int] = 16  # SP0 through SP15

# Keys in subphase_results that are NOT integer subphase indices
SUBPHASE_METADATA_KEYS: Final[tuple[str, ...]] = (
    "truncation_audit",
    "irrigation_map",
    "final_rankings",
)

# =============================================================================
# SPEC-005: Logging Configuration
# =============================================================================

PHASE1_LOGGER_NAME: Final[str] = "farfan_pipeline.phases.Phase_01"

# =============================================================================
# SPEC-006: Determinism
# =============================================================================

RANDOM_SEED: Final[int] = 42

# =============================================================================
# SPEC-007: Questionnaire Mapping (Phase 2)
# =============================================================================

# Method invocation thresholds (used in Phase 2)
MIN_METHOD_SETS_TO_INVOKE: Final[int] = 1  # At least 1 method per question
MAX_METHOD_INVOCATION_TIME: Final[float] = 30.0  # Seconds per method

# Expected elements verification (used in Phase 2)
REQUIRED_ELEMENT_VERIFICATION: Final[bool] = True  # Enforce required elements
MIN_REQUIRED_ELEMENTS_PRESENT: Final[int] = 1  # At least 1 required element
