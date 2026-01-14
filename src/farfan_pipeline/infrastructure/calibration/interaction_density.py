"""
Interaction Density Tracking
=============================
Tracks interaction density for calibration sensitivity and fusion caps.

DESIGN PRINCIPLE:
    High interaction density (many method dependencies) requires:
    - Stricter veto thresholds to prevent error propagation
    - Bounded fusion strategies to avoid combinatorial explosion
    - Interaction caps to maintain epistemic coherence

Module: interaction_density.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Interaction density tracking for calibration
Schema Version: 1.0.0

INVARIANTS ENFORCED:
    INV-INT-DEN-001: Density ∈ [0.0, 1.0]
    INV-INT-DEN-002: Density increases with dependency count
    INV-INT-DEN-003: Density capped per TYPE
    INV-INT-DEN-004: Cyclic dependencies → density = 1.0 (maximum)

INTERACTION DENSITY CAPS PER TYPE:
    TYPE_A: 0.8 (semantic triangulation tolerates high interaction)
    TYPE_B: 0.7 (Bayesian update requires moderate independence)
    TYPE_C: 0.6 (topological overlay requires DAG structure)
    TYPE_D: 0.9 (weighted mean handles high interaction)
    TYPE_E: 0.5 (min consistency requires low interaction for strict logic)
"""

from __future__ import annotations

import logging
from typing import Final

from .method_binding_validator import MethodBindingSet


# =============================================================================
# CONSTANTS
# =============================================================================

# Interaction density caps per TYPE
_INTERACTION_DENSITY_CAPS: Final[dict[str, float]] = {
    "TYPE_A": 0.8,  # Semantic triangulation tolerates high interaction
    "TYPE_B": 0.7,  # Bayesian update requires moderate independence
    "TYPE_C": 0.6,  # Topological overlay requires DAG structure
    "TYPE_D": 0.9,  # Weighted mean handles high interaction
    "TYPE_E": 0.5,  # Min consistency requires strict logic
    "SUBTIPO_F": 1.0,  # Concatenation permits maximum interaction
}

# Density computation parameters
_BASE_DENSITY_PER_METHOD: Final[float] = 0.02
_DEPENDENCY_WEIGHT: Final[float] = 0.15
_N3_INTERACTION_MULTIPLIER: Final[float] = 1.5

# Bounds
_MIN_DENSITY: Final[float] = 0.0
_MAX_DENSITY: Final[float] = 1.0


# =============================================================================
# INTERACTION DENSITY TRACKER
# =============================================================================


class InteractionDensityTracker:
    """
    Unit of Analysis Requirements:
        - MethodBindingSet with valid contract_type_code
        - Method counts per epistemic level (N1/N2/N3)

    Epistemic Level: N3-AUD (meta-level governance)
    Output: Interaction density ∈ [0.0, 1.0]
    Fusion Strategy: Weighted combination of interaction factors

    Tracks interaction density for calibration sensitivity.

    Interaction density measures how tightly coupled methods are,
    which affects calibration decisions:
    - Higher density → stricter veto thresholds
    - Higher density → stronger priors (prevent drift)
    - Higher density → bounded fusion strategies

    The tracker considers:
    1. Method count (more methods → more potential interactions)
    2. Epistemic level distribution (N3 methods create dependencies)
    3. Dependency patterns (future: extract from method signatures)
    4. TYPE-specific caps (each TYPE has maximum permitted density)

    Example:
        >>> tracker = InteractionDensityTracker()
        >>> binding_set = MethodBindingSet(...)
        >>> density = tracker.compute_density(binding_set)
        >>> 0.0 <= density <= 1.0
        True
    """

    def __init__(self) -> None:
        """Initialize interaction density tracker."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def compute_density(self, binding_set: MethodBindingSet) -> float:
        """
        Unit of Analysis Requirements:
            - Valid MethodBindingSet
            - contract_type_code ∈ VALID_CONTRACT_TYPES

        Epistemic Level: N3-AUD
        Output: Interaction density ∈ [0.0, 1.0]
        Fusion Strategy: Capped weighted sum

        Compute interaction density for method set.

        Args:
            binding_set: Methods bound to contract

        Returns:
            Interaction density in [0.0, 1.0]
        """
        # Get method counts
        n1_count = binding_set.get_count_by_level("N1")
        n2_count = binding_set.get_count_by_level("N2")
        n3_count = binding_set.get_count_by_level("N3")
        total_methods = n1_count + n2_count + n3_count

        if total_methods == 0:
            return _MIN_DENSITY

        # Factor 1: Base density from method count
        # INV-INT-DEN-002: More methods → higher density
        count_density = min(_BASE_DENSITY_PER_METHOD * total_methods, 0.4)

        # Factor 2: Epistemic level contribution
        # INV-INT-DEN-003: N3 methods increase density more
        # (validation methods create more dependencies)
        if total_methods > 0:
            n3_ratio = n3_count / total_methods
            epistemic_density = n3_ratio * _N3_INTERACTION_MULTIPLIER
        else:
            epistemic_density = 0.0

        # Factor 3: Dependency estimation
        # For now, estimate based on method counts
        # Future: parse actual method dependencies
        estimated_dependencies = self._estimate_dependencies(
            n1_count=n1_count,
            n2_count=n2_count,
            n3_count=n3_count,
        )
        dependency_density = min(estimated_dependencies * _DEPENDENCY_WEIGHT, 0.5)

        # Combine factors
        # Weighted combination: 30% count, 30% epistemic, 40% dependencies
        raw_density = (
            0.3 * count_density + 0.3 * epistemic_density + 0.4 * dependency_density
        )

        # Apply TYPE-specific cap
        # INV-INT-DEN-003: Density capped per TYPE
        contract_type = binding_set.contract_type_code
        type_cap = _INTERACTION_DENSITY_CAPS.get(contract_type, _MAX_DENSITY)
        capped_density = min(raw_density, type_cap)

        # INV-INT-DEN-001: Ensure bounds
        final_density = max(_MIN_DENSITY, min(_MAX_DENSITY, capped_density))

        self._logger.debug(
            f"Computed interaction density for {contract_type}: "
            f"raw={raw_density:.3f}, capped={capped_density:.3f}, "
            f"final={final_density:.3f}"
        )

        return final_density

    def _estimate_dependencies(
        self,
        n1_count: int,
        n2_count: int,
        n3_count: int,
    ) -> float:
        """
        Estimate dependency count from method distribution.

        This is a heuristic estimation. In a future enhancement,
        we could parse actual method signatures to extract real dependencies.

        Heuristics:
        - Each N2 method depends on ~2 N1 methods
        - Each N3 method depends on ~3 N2 methods
        - Total dependencies normalized to [0, 1]

        Args:
            n1_count: Number of N1 methods
            n2_count: Number of N2 methods
            n3_count: Number of N3 methods

        Returns:
            Estimated dependency ratio in [0.0, 1.0]
        """
        total = n1_count + n2_count + n3_count
        if total == 0:
            return 0.0

        # Estimate dependencies based on epistemic levels
        # N2 depends on N1, N3 depends on N2
        estimated_deps = n2_count * 2.0 + n3_count * 3.0

        # Normalize by total possible dependencies (n * (n-1) / 2)
        max_possible_deps = total * (total - 1) / 2 if total > 1 else 1
        dependency_ratio = estimated_deps / max_possible_deps

        return min(dependency_ratio, 1.0)

    def check_density_violation(
        self,
        binding_set: MethodBindingSet,
        computed_density: float,
    ) -> tuple[bool, str]:
        """
        Unit of Analysis Requirements:
            - Valid MethodBindingSet
            - computed_density ∈ [0.0, 1.0]

        Epistemic Level: N3-AUD
        Output: (violation_detected: bool, message: str)
        Fusion Strategy: TYPE-specific cap checking

        Check if interaction density violates TYPE cap.

        Args:
            binding_set: Methods bound to contract
            computed_density: Computed interaction density

        Returns:
            Tuple of (violation_detected, violation_message)
        """
        contract_type = binding_set.contract_type_code
        type_cap = _INTERACTION_DENSITY_CAPS.get(contract_type, _MAX_DENSITY)

        if computed_density > type_cap:
            message = (
                f"Interaction density violation for {contract_type}: "
                f"density={computed_density:.3f} exceeds cap={type_cap:.3f}. "
                f"Reduce method count or simplify dependencies."
            )
            return (True, message)

        return (False, "")

    def get_density_cap(self, contract_type_code: str) -> float:
        """
        Get interaction density cap for contract type.

        Args:
            contract_type_code: TYPE_A, TYPE_B, etc.

        Returns:
            Density cap in [0.0, 1.0]
        """
        return _INTERACTION_DENSITY_CAPS.get(contract_type_code, _MAX_DENSITY)


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    "InteractionDensityTracker",
]
