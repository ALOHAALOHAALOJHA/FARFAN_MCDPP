"""
Phase 3 Validators Package.

Validators for scoring integrity, normative compliance, and quality assurance.

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

from .normative_compliance_validator import (
    NormativeComplianceValidator,
    ValidationResult,
    validate_normative_compliance,
)

__all__ = [
    "NormativeComplianceValidator",
    "ValidationResult",
    "validate_normative_compliance",
]
