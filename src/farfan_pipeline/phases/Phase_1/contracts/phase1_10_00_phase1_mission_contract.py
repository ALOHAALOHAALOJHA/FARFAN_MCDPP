"""Phase 1 Mission Contract - Weight-Based Execution Contract.

This contract governs the execution of 16 subphases in Phase 1,
enforcing weight-based criticality and execution behavior.

Constitutional Invariants:
- EXACTLY 60 chunks must be produced (10 Policy Areas × 6 Causal Dimensions)
- All 16 subphases must complete or fail gracefully according to weight tier
- Weight-based timeouts: CRITICAL (3x), HIGH (2x), STANDARD (1x)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WeightTier(Enum):
    """Weight tier classification for subphases."""

    CRITICAL = "CRITICAL"  # 10000: Constitutional invariants
    HIGH = "HIGH"  # 5000-9000: Essential processing
    STANDARD = "STANDARD"  # 900-4999: Standard processing


@dataclass(frozen=True)
class SubphaseWeight:
    """Weight specification for a subphase."""

    subphase_id: str
    weight: int
    tier: WeightTier
    timeout_multiplier: float
    abort_on_failure: bool
    description: str


# Phase 1 Subphase Weight Specification
PHASE1_SUBPHASE_WEIGHTS: dict[str, SubphaseWeight] = {
    "SP0": SubphaseWeight("SP0", 900, WeightTier.STANDARD, 1.0, False, "Input validation"),
    "SP1": SubphaseWeight("SP1", 2500, WeightTier.STANDARD, 1.0, False, "Language preprocessing"),
    "SP2": SubphaseWeight("SP2", 3000, WeightTier.STANDARD, 1.0, False, "Structural analysis"),
    "SP3": SubphaseWeight("SP3", 4000, WeightTier.STANDARD, 1.0, False, "Knowledge graph"),
    "SP4": SubphaseWeight(
        "SP4", 10000, WeightTier.CRITICAL, 3.0, True, "PA×Dim grid specification"
    ),
    "SP5": SubphaseWeight("SP5", 5000, WeightTier.HIGH, 2.0, False, "Causal extraction"),
    "SP6": SubphaseWeight("SP6", 3500, WeightTier.STANDARD, 1.0, False, "Arguments extraction"),
    "SP7": SubphaseWeight("SP7", 4500, WeightTier.STANDARD, 1.0, False, "Discourse analysis"),
    "SP8": SubphaseWeight("SP8", 3500, WeightTier.STANDARD, 1.0, False, "Temporal extraction"),
    "SP9": SubphaseWeight("SP9", 6000, WeightTier.HIGH, 2.0, False, "Causal integration"),
    "SP10": SubphaseWeight("SP10", 8000, WeightTier.HIGH, 2.0, False, "Strategic integration"),
    "SP11": SubphaseWeight(
        "SP11", 10000, WeightTier.CRITICAL, 3.0, True, "Chunk assembly (60 chunks)"
    ),
    "SP12": SubphaseWeight("SP12", 7000, WeightTier.HIGH, 2.0, False, "SISAS irrigation"),
    "SP13": SubphaseWeight("SP13", 10000, WeightTier.CRITICAL, 3.0, True, "CPP packaging"),
    "SP14": SubphaseWeight("SP14", 5000, WeightTier.HIGH, 2.0, False, "Quality metrics"),
    "SP15": SubphaseWeight("SP15", 9000, WeightTier.HIGH, 2.0, False, "Integrity verification"),
}


def validate_mission_contract() -> bool:
    """Validate Phase 1 mission contract integrity.

    Returns:
        True if contract is valid

    Raises:
        ValueError: If contract validation fails
    """
    if len(PHASE1_SUBPHASE_WEIGHTS) != 16:
        raise ValueError(
            f"Mission contract must have exactly 16 subphases, got {len(PHASE1_SUBPHASE_WEIGHTS)}"
        )

    critical_subphases = [
        sp for sp in PHASE1_SUBPHASE_WEIGHTS.values() if sp.tier == WeightTier.CRITICAL
    ]
    if len(critical_subphases) != 3:
        raise ValueError(
            f"Mission contract must have exactly 3 CRITICAL subphases, got {len(critical_subphases)}"
        )

    # Verify SP4, SP11, SP13 are critical
    if not all(sp in ["SP4", "SP11", "SP13"] for sp in [s.subphase_id for s in critical_subphases]):
        raise ValueError("CRITICAL subphases must be SP4, SP11, SP13")

    return True


__all__ = [
    "PHASE1_SUBPHASE_WEIGHTS",
    "SubphaseWeight",
    "WeightTier",
    "validate_mission_contract",
]
