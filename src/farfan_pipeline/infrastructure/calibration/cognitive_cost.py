"""
Cognitive Cost Estimation
==========================
Estimates cognitive cost of methods for calibration sensitivity.

DESIGN PRINCIPLE:
    Complex methods require stronger priors and stricter veto thresholds
    to prevent epistemic drift and maintain calibration stability.

Module: cognitive_cost.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Cognitive cost estimation for calibration sensitivity
Schema Version: 1.0.0

INVARIANTS ENFORCED:
    INV-COG-001: Cognitive cost ∈ [0.0, 1.0]
    INV-COG-002: Higher method count → higher cognitive cost
    INV-COG-003: Complexity level monotonically increases cost
    INV-COG-004: N3 methods contribute more to cost than N1/N2

SENSITIVITY FACTORS:
    - Method count (more methods → higher cost)
    - Method complexity (LOW/MEDIUM/HIGH)
    - Epistemic level distribution (N1/N2/N3 ratio)
    - Interaction patterns (dependencies, cycles)
"""

from __future__ import annotations

from enum import Enum
from typing import Final


# =============================================================================
# CONSTANTS
# =============================================================================

# Base cognitive cost per method
_BASE_COST_PER_METHOD: Final[float] = 0.05

# Complexity multipliers
_COMPLEXITY_MULTIPLIERS: Final[dict[str, float]] = {
    "LOW": 1.0,
    "MEDIUM": 1.5,
    "HIGH": 2.5,
}

# Epistemic level weights (N3 methods are cognitively heavier)
_EPISTEMIC_LEVEL_WEIGHTS: Final[dict[str, float]] = {
    "N1": 1.0,  # Empirical methods (extraction, observation)
    "N2": 1.3,  # Inference methods (computation, aggregation)
    "N3": 2.0,  # Audit methods (validation, veto)
}

# Cognitive cost caps
_MIN_COGNITIVE_COST: Final[float] = 0.0
_MAX_COGNITIVE_COST: Final[float] = 1.0


# =============================================================================
# ENUMS
# =============================================================================


class MethodComplexity(Enum):
    """
    Method complexity levels.

    LOW: Simple methods with minimal dependencies
    MEDIUM: Standard methods with moderate complexity
    HIGH: Complex methods with many dependencies or intricate logic
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# =============================================================================
# COGNITIVE COST ESTIMATOR
# =============================================================================


class CognitiveCostEstimator:
    """
    Unit of Analysis Requirements:
        - Method count > 0
        - Complexity level from {LOW, MEDIUM, HIGH}
        - Optional: Epistemic level distribution (N1/N2/N3 counts)

    Epistemic Level: N3-AUD (meta-level calibration)
    Output: Cognitive cost score ∈ [0.0, 1.0]
    Fusion Strategy: Weighted sum of factors

    Estimates cognitive cost of method sets for calibration.

    Cognitive cost reflects how mentally demanding a method set is,
    which influences calibration parameters:
    - Higher cost → stronger priors (more conservative)
    - Higher cost → stricter veto thresholds (more validation)
    - Higher cost → shorter validity windows (recalibrate more often)

    The estimator considers:
    1. Method count (more methods → higher cost)
    2. Complexity level (HIGH > MEDIUM > LOW)
    3. Epistemic level distribution (N3 > N2 > N1)
    4. Interaction patterns (optional, future enhancement)

    Example:
        >>> estimator = CognitiveCostEstimator()
        >>> cost = estimator.estimate_cost(
        ...     method_count=10,
        ...     complexity=MethodComplexity.MEDIUM,
        ... )
        >>> 0.0 <= cost <= 1.0
        True
    """

    def estimate_cost(
        self,
        method_count: int,
        complexity: MethodComplexity,
        n1_count: int = 0,
        n2_count: int = 0,
        n3_count: int = 0,
    ) -> float:
        """
        Unit of Analysis Requirements:
            - method_count > 0
            - complexity ∈ {LOW, MEDIUM, HIGH}
            - n1_count, n2_count, n3_count ≥ 0

        Epistemic Level: N3-AUD
        Output: Cognitive cost ∈ [0.0, 1.0]
        Fusion Strategy: Weighted sum with normalization

        Estimate cognitive cost of method set.

        Args:
            method_count: Total number of methods
            complexity: Complexity level
            n1_count: Number of N1-EMP methods (optional)
            n2_count: Number of N2-INF methods (optional)
            n3_count: Number of N3-AUD methods (optional)

        Returns:
            Cognitive cost score in [0.0, 1.0]

        Raises:
            ValueError: If method_count < 0 or epistemic counts are invalid
        """
        # INV-COG-002: Method count validation
        if method_count < 0:
            raise ValueError(f"method_count must be non-negative, got: {method_count}")

        # INV-COG-004: Epistemic count validation
        if n1_count < 0 or n2_count < 0 or n3_count < 0:
            raise ValueError("Epistemic counts must be non-negative")

        if method_count == 0:
            return _MIN_COGNITIVE_COST

        # Factor 1: Base cost from method count
        # INV-COG-002: Linear scaling with method count
        count_cost = min(_BASE_COST_PER_METHOD * method_count, 0.5)

        # Factor 2: Complexity multiplier
        # INV-COG-003: Complexity monotonically increases cost
        complexity_multiplier = _COMPLEXITY_MULTIPLIERS.get(
            complexity.value,
            _COMPLEXITY_MULTIPLIERS["MEDIUM"],
        )
        complexity_cost = count_cost * complexity_multiplier

        # Factor 3: Epistemic level weighting
        # INV-COG-004: N3 methods contribute more
        if n1_count + n2_count + n3_count > 0:
            epistemic_cost = (
                n1_count * _EPISTEMIC_LEVEL_WEIGHTS["N1"]
                + n2_count * _EPISTEMIC_LEVEL_WEIGHTS["N2"]
                + n3_count * _EPISTEMIC_LEVEL_WEIGHTS["N3"]
            ) / (n1_count + n2_count + n3_count)
            epistemic_cost = (epistemic_cost - 1.0) / 1.0  # Normalize to [0, 1]
        else:
            epistemic_cost = 0.0

        # Combine factors
        # Weighted combination: 60% complexity, 40% epistemic
        total_cost = 0.6 * complexity_cost + 0.4 * epistemic_cost

        # INV-COG-001: Ensure bounds
        total_cost = max(_MIN_COGNITIVE_COST, min(_MAX_COGNITIVE_COST, total_cost))

        return total_cost

    def estimate_from_epistemic_counts(
        self,
        n1_count: int,
        n2_count: int,
        n3_count: int,
    ) -> float:
        """
        Unit of Analysis Requirements:
            - n1_count, n2_count, n3_count ≥ 0
            - At least one count > 0

        Epistemic Level: N3-AUD
        Output: Cognitive cost ∈ [0.0, 1.0]
        Fusion Strategy: Weighted epistemic distribution

        Estimate cognitive cost from epistemic level counts.

        This is a convenience method that infers complexity from
        the epistemic distribution:
        - High N3 ratio → HIGH complexity
        - Balanced distribution → MEDIUM complexity
        - High N1 ratio → LOW complexity

        Args:
            n1_count: Number of N1-EMP methods
            n2_count: Number of N2-INF methods
            n3_count: Number of N3-AUD methods

        Returns:
            Cognitive cost score in [0.0, 1.0]
        """
        total = n1_count + n2_count + n3_count
        if total == 0:
            return _MIN_COGNITIVE_COST

        # Infer complexity from epistemic distribution
        n3_ratio = n3_count / total
        n2_ratio = n2_count / total

        if n3_ratio >= 0.4 or total >= 15:
            complexity = MethodComplexity.HIGH
        elif n3_ratio <= 0.15 and n2_ratio <= 0.3:
            complexity = MethodComplexity.LOW
        else:
            complexity = MethodComplexity.MEDIUM

        return self.estimate_cost(
            method_count=total,
            complexity=complexity,
            n1_count=n1_count,
            n2_count=n2_count,
            n3_count=n3_count,
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    "CognitiveCostEstimator",
    "MethodComplexity",
]
