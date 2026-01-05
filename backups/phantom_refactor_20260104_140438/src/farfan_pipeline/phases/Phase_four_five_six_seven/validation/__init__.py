"""Phase 4-7 Aggregation Pipeline Validation.

This package provides strict validation for all aggregation phases to ensure:
- Non-empty outputs at each phase
- Correct counts (60/10/4/1)
- Valid score bounds [0.0, 3.0]
- Traceability to source micro-questions
- Hermeticity (all expected inputs present)
"""

from __future__ import annotations

from .phase4_7_validation import (
    ValidationResult,
    AggregationValidationError,
    validate_phase4_output,
    validate_phase5_output,
    validate_phase6_output,
    validate_phase7_output,
    validate_full_aggregation_pipeline,
    enforce_validation_or_fail,
)

__all__ = [
    "ValidationResult",
    "AggregationValidationError",
    "validate_phase4_output",
    "validate_phase5_output",
    "validate_phase6_output",
    "validate_phase7_output",
    "validate_full_aggregation_pipeline",
    "enforce_validation_or_fail",
]
