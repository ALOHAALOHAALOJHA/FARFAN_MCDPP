"""
Phase 6 Unified Scoring Configuration

Module:  src/farfan_pipeline/phases/Phase_6/phase6_10_01_scoring_config.py
Purpose: Single source of truth for all Phase 6 scoring parameters
Owner: phase6_10
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-16

This module consolidates all dispersion, penalty, and coherence thresholds
previously scattered across phase6_10_00_phase_6_constants.py and
AdaptiveScoringConfig in phase6_20_00_adaptive_meso_scoring.py.

MIGRATION NOTE:
- Old PENALTY_WEIGHT (0.3) → base_penalty_weight (0.35) [+0.05 adjustment]
- Old CV_CONVERGENCE (0.2) → cv_convergence (0.15) [-0.05 adjustment, stricter]
- Old CV_MODERATE (0.4) → cv_moderate (0.40) [unchanged]
- Old CV_HIGH (0.6) → cv_high (0.60) [unchanged]
"""
from __future__ import annotations

__version__ = "1.0.0"
__phase__ = 6
__stage__ = 10
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-16T00:00:00Z"
__modified__ = "2026-01-16T00:00:00Z"
__criticality__ = "CRITICAL"

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class DispersionScenario(Enum):
    """Dispersion classification scenarios."""

    CONVERGENCE = "convergence"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class CoherenceQuality(Enum):
    """Coherence quality classification."""

    EXCELLENT = "excellent"
    ACCEPTABLE = "acceptable"
    POOR = "poor"


@dataclass(frozen=True)
class Phase6ScoringConfig:
    """
    Immutable Phase 6 scoring configuration.

    This is the SINGLE SOURCE OF TRUTH for all scoring parameters.
    All other modules MUST import from here.

    Frozen dataclass ensures runtime immutability.
    """

    # === Score Bounds ===
    min_score: float = 0.0
    max_score: float = 3.0

    # === Dispersion CV Thresholds ===
    # CV = Coefficient of Variation = std_dev / mean
    cv_convergence: float = 0.15  # CV < 0.15 → CONVERGENCE (scores tightly clustered)
    cv_moderate: float = 0.40  # CV < 0.40 → MODERATE (normal variation)
    cv_high: float = 0.60  # CV < 0.60 → HIGH (significant spread)
    # CV >= 0.60 → EXTREME (scores wildly divergent)

    # === Dispersion Index Threshold ===
    di_convergence: float = 0.20  # DI threshold for convergence classification

    # === Penalty Weights ===
    base_penalty_weight: float = 0.35
    convergence_multiplier: float = 0.5  # Reduce penalty for convergent clusters
    moderate_multiplier: float = 1.0  # Normal penalty
    high_multiplier: float = 1.5  # Increased penalty for high dispersion
    extreme_multiplier: float = 2.0  # Strong penalty for extreme dispersion

    # === Non-linear Scaling ===
    extreme_shape_factor: float = 1.8  # Exponential scaling for extreme cases
    bimodal_penalty_boost: float = 1.3  # Additional penalty for bimodal distributions

    # === Coherence Thresholds ===
    coherence_low: float = 0.5  # Below = POOR coherence
    coherence_high: float = 0.8  # Above = EXCELLENT coherence
    # Between = ACCEPTABLE coherence

    def classify_dispersion(self, cv: float) -> DispersionScenario:
        """
        Classify coefficient of variation into dispersion scenario.
        """
        if cv < self.cv_convergence:
            return DispersionScenario.CONVERGENCE
        elif cv < self.cv_moderate:
            return DispersionScenario.MODERATE
        elif cv < self.cv_high:
            return DispersionScenario.HIGH
        else:
            return DispersionScenario.EXTREME

    def get_penalty_multiplier(self, scenario: DispersionScenario) -> float:
        """
        Get penalty multiplier for dispersion scenario.
        """
        multipliers = {
            DispersionScenario.CONVERGENCE: self.convergence_multiplier,
            DispersionScenario.MODERATE: self.moderate_multiplier,
            DispersionScenario.HIGH: self.high_multiplier,
            DispersionScenario.EXTREME: self.extreme_multiplier,
        }
        return multipliers[scenario]

    def classify_coherence(self, coherence: float):
        """
        Classify coherence value into quality tier.
        """
        if coherence >= self.coherence_high:
            return CoherenceQuality.EXCELLENT
        elif coherence >= self.coherence_low:
            return CoherenceQuality.ACCEPTABLE
        else:
            return CoherenceQuality.POOR

    def to_legacy_dispersion_thresholds(self) -> Dict[str, float]:
        """
        Export as legacy DISPERSION_THRESHOLDS dict for backwards compatibility.
        """
        return {
            "CV_CONVERGENCE": self.cv_convergence,
            "CV_MODERATE": self.cv_moderate,
            "CV_HIGH": self.cv_high,
            "CV_EXTREME": 1.0,
        }


# === SINGLETON INSTANCE ===
PHASE6_CONFIG = Phase6ScoringConfig()

# === CONVENIENCE EXPORTS ===
MIN_SCORE = PHASE6_CONFIG.min_score
MAX_SCORE = PHASE6_CONFIG.max_score
PENALTY_WEIGHT = PHASE6_CONFIG.base_penalty_weight
COHERENCE_THRESHOLD_LOW = PHASE6_CONFIG.coherence_low
COHERENCE_THRESHOLD_HIGH = PHASE6_CONFIG.coherence_high
