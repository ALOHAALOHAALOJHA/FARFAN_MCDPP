"""
Calibration Core - Base Classes for Epistemic Calibration
===========================================================

Module: calibration_core.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Core data structures for calibration parameter bounds and validation
Lifecycle State: DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 4.0.0-epistemological

This module provides the foundational classes for the epistemic calibration
system. All calibration parameters are represented as closed intervals with
defensive validation.

CONSTITUTIONAL PRINCIPLES:
- INV-CORE-001: All bounds satisfy lower <= default <= upper
- INV-CORE-002: Interval bounds are immutable (frozen dataclass)
- INV-CORE-003: Validation errors raise ValidationError immediately

EPISTEMIC ARCHITECTURE:
    The calibration system enforces the separation between:
    - N0-INFRA: Infrastructure without analytical judgment
    - N1-EMP: Empirical extraction (positivist)
    - N2-INF: Inferential computation (Bayesian/constructivist)
    - N3-AUD: Audit and falsification (Popperian)
    - N4-META: Meta-analysis of the process

Dependencies:
    - Standard library: dataclasses, typing
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


# =============================================================================
# EXCEPTIONS
# =============================================================================


class ValidationError(Exception):
    """
    Raised when calibration validation fails.

    This indicates a configuration error that must be fixed before
    the pipeline can execute.
    """

    pass


class CalibrationBoundsError(ValidationError):
    """
    Raised when interval bounds are invalid.

    Typical causes:
    - lower > upper
    - default not in [lower, upper]
    - negative values where positive required
    """

    pass


# =============================================================================
# CLOSED INTERVAL DATA STRUCTURE
# =============================================================================


@dataclass(frozen=True, slots=True)
class ClosedInterval:
    """
    An immutable closed interval [lower, upper] for parameter bounds.

    Represents bounded constraints for a calibration parameter. The interval
    is closed (inclusive). Actual values are COMPUTED at runtime based on
    the unit of analysis, not stored as static defaults.

    DESIGN PRINCIPLE:
        This is a bounds-only structure. Values are calculated transparently
        at runtime by the calibration system based on PDM characteristics,
        not hardcoded as defaults.

    Invariants:
        INV-CI-001: lower <= upper
        INV-CI-002: All values are finite (not inf/nan)

    Attributes:
        lower: Minimum allowed value (inclusive).
        upper: Maximum allowed value (inclusive).

    Examples:
        >>> interval = ClosedInterval(lower=0.0, upper=1.0)
        >>> interval.contains(0.75)
        True
        >>> interval.midpoint()
        0.5
    """

    lower: float
    upper: float

    def __post_init__(self) -> None:
        """Validate interval bounds."""
        import math

        # Validate finite values first
        if not (math.isfinite(self.lower) and math.isfinite(self.upper)):
            raise ValidationError(
                f"Interval values must be finite: got "
                f"lower={self.lower}, upper={self.upper}"
            )

        # Validate lower <= upper
        if self.lower > self.upper:
            raise ValidationError(
                f"Malformed interval: lower bound ({self.lower}) cannot exceed "
                f"upper bound ({self.upper})"
            )

        # Check for NaN explicitly
        if math.isnan(self.lower) or math.isnan(self.upper):
            raise ValidationError(
                f"Interval bounds cannot be NaN: lower={self.lower}, upper={self.upper}"
            )

    def contains(self, value: float) -> bool:
        """
        Check if a value is within the closed interval.

        Args:
            value: Value to check.

        Returns:
            True if lower <= value <= upper, False otherwise.
        """
        return self.lower <= value <= self.upper

    def midpoint(self) -> float:
        """
        Calculate the midpoint of the interval.

        Returns:
            (lower + upper) / 2
        """
        return (self.lower + self.upper) / 2.0

    def to_canonical_dict(self) -> dict[str, float]:
        """
        Convert to canonical dictionary for serialization.

        Returns:
            Dict with keys: lower, upper
        """
        return {
            "lower": self.lower,
            "upper": self.upper,
        }

    @classmethod
    def from_canonical_dict(cls, data: dict[str, float]) -> "ClosedInterval":
        """
        Create ClosedInterval from canonical dictionary.

        Args:
            data: Dict with keys: lower, upper

        Returns:
            ClosedInterval instance

        Raises:
            ValidationError: If data is invalid
            KeyError: If required keys are missing
        """
        return cls(
            lower=float(data["lower"]),
            upper=float(data["upper"]),
        )


# =============================================================================
# EPISTEMIC LEVEL TYPE DEFINITIONS
# =============================================================================

# Literal type for epistemic levels (enforced at runtime)
EpistemicLevel: Final = frozenset({
    "N0-INFRA",  # Infrastructure without analytical judgment
    "N1-EMP",    # Empirical extraction (positivist)
    "N2-INF",    # Inferential computation (Bayesian/constructivist)
    "N3-AUD",    # Audit and falsification (Popperian)
    "N4-META",   # Meta-analysis of the process
})

# Output type mapping (invariant: level -> output_type is one-to-one)
OUTPUT_TYPE_BY_LEVEL: Final[dict[str, str]] = {
    "N0-INFRA": "INFRASTRUCTURE",
    "N1-EMP": "FACT",
    "N2-INF": "PARAMETER",
    "N3-AUD": "CONSTRAINT",
    "N4-META": "META_ANALYSIS",
}

# Fusion behavior mapping (invariant: level -> fusion_behavior is one-to-one)
FUSION_BEHAVIOR_BY_LEVEL: Final[dict[str, str]] = {
    "N0-INFRA": "none",
    "N1-EMP": "additive",      # ⊕ concatenation
    "N2-INF": "multiplicative",  # ⊗ weighting
    "N3-AUD": "gate",          # ⊘ veto
    "N4-META": "terminal",     # ⊙ synthesis
}


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_epistemic_level(level: str) -> None:
    """
    Validate that an epistemic level is recognized.

    Args:
        level: Level code (e.g., "N1-EMP")

    Raises:
        ValidationError: If level is not recognized
    """
    if level not in EpistemicLevel:
        valid_levels = ", ".join(sorted(EpistemicLevel))
        raise ValidationError(
            f"Invalid epistemic level: '{level}'. "
            f"Valid levels: {valid_levels}"
        )


def validate_output_type_for_level(output_type: str, level: str) -> None:
    """
    Validate that an output type matches the expected type for a level.

    Args:
        output_type: The output type being used
        level: The epistemic level

    Raises:
        ValidationError: If output_type doesn't match level
    """
    validate_epistemic_level(level)

    expected_type = OUTPUT_TYPE_BY_LEVEL.get(level)
    if expected_type and output_type != expected_type:
        raise ValidationError(
            f"Output type mismatch: level '{level}' expects "
            f"'{expected_type}', got '{output_type}'"
        )


def validate_fusion_behavior_for_level(fusion_behavior: str, level: str) -> None:
    """
    Validate that a fusion behavior matches the expected behavior for a level.

    Args:
        fusion_behavior: The fusion behavior being used
        level: The epistemic level

    Raises:
        ValidationError: If fusion_behavior doesn't match level
    """
    validate_epistemic_level(level)

    expected_behavior = FUSION_BEHAVIOR_BY_LEVEL.get(level)
    if expected_behavior and fusion_behavior != expected_behavior:
        raise ValidationError(
            f"Fusion behavior mismatch: level '{level}' expects "
            f"'{expected_behavior}', got '{fusion_behavior}'"
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Exceptions
    "ValidationError",
    "CalibrationBoundsError",
    # Data structures
    "ClosedInterval",
    # Type definitions
    "EpistemicLevel",
    # Mapping constants
    "OUTPUT_TYPE_BY_LEVEL",
    "FUSION_BEHAVIOR_BY_LEVEL",
    # Validation functions
    "validate_epistemic_level",
    "validate_output_type_for_level",
    "validate_fusion_behavior_for_level",
]
