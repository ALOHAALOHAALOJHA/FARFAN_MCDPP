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
    AggregationValidationError,
    ValidationResult,
    enforce_validation_or_fail,
    validate_full_aggregation_pipeline,
    validate_phase4_output,
    validate_phase5_output,
    validate_phase6_output,
    validate_phase7_output,
)

__all__ = [
    "AggregationValidationError",
    "ValidationResult",
    "enforce_validation_or_fail",
    "validate_full_aggregation_pipeline",
    "validate_phase4_output",
    "validate_phase5_output",
    "validate_phase6_output",
    "validate_phase7_output",
]
