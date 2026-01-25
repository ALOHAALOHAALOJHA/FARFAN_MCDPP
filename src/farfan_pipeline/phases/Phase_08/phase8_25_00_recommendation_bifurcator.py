# phase8_25_00_recommendation_bifurcator.py - Recommendation Bifurcation Engine
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_25_00_recommendation_bifurcator
Purpose: Transforms linear recommendations into exponential cascades via bifurcation analysis
Owner: phase8_core
Stage: 25 (Bifurcation)
Order: 00
Type: ENG
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-25

This module implements the BIFURCATOR, which takes standard recommendations from
RecommendationEngine and discovers hidden multiplicative value through four strategies:

1. DIMENSIONAL RESONANCE: When DIM01 improves, related DIMs benefit (MICRO only)
2. CROSS-POLLINATION: When fixing PA01 partially fixes PA03 (shared structure)
3. TEMPORAL CASCADES: Short-term fixes unlock long-term capabilities
4. SYNERGY DETECTION: Two interventions together > sum of parts

Author: F.A.R.F.A.N Core Team
Python: 3.10+
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 8
__stage__ = 25
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-25"
__modified__ = "2026-01-25"
__criticality__ = "MEDIUM"
__execution_pattern__ = "On-Demand"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import combinations
from typing import Any, TypeAlias

# =============================================================================
# TYPE ALIASES
# =============================================================================

RecommendationDict: TypeAlias = dict[str, Any]
ScoreKey: TypeAlias = str  # Format: "PA##-DIM##"
RuleId: TypeAlias = str
SynergyPair: TypeAlias = tuple[RuleId, RuleId]

# =============================================================================
# LOGGER
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS - Normalization
# =============================================================================

VALID_LEVELS = frozenset({"MICRO", "MESO", "MACRO"})
DEFAULT_LEVEL = "MICRO"
SCORE_KEY_PATTERN = re.compile(r"^(PA\d{2})-(DIM\d{2})$")

# =============================================================================
# CONSTANTS - Dimensional Resonance (MICRO only)
# =============================================================================

# When a dimension improves, which related dimensions benefit?
DIMENSIONAL_RESONANCE: dict[str, dict[str, float]] = {
    "DIM01": {"DIM02": 0.4, "DIM03": 0.3},  # Alignment -> Finance, Beliefs
    "DIM02": {"DIM01": 0.3, "DIM05": 0.5},  # Finance -> Alignment, Execution
    "DIM03": {"DIM01": 0.3, "DIM04": 0.4},  # Beliefs -> Alignment, Causality
    "DIM04": {"DIM03": 0.3, "DIM06": 0.5},  # Causality -> Beliefs, Evidence
    "DIM05": {"DIM02": 0.4, "DIM06": 0.3},  # Execution -> Finance, Evidence
    "DIM06": {"DIM04": 0.4, "DIM05": 0.3},  # Evidence -> Causality, Execution
}

# =============================================================================
# CONSTANTS - Cross-Pollination Patterns
# =============================================================================

# Shared structural patterns between PAs that enable cross-pollination
CROSS_POLLINATION_PATTERNS: dict[str, dict[str, float]] = {
    # PA01-PA03: Both rely on strategic planning
    "PA01": {"PA03": 0.4},
    # PA02-PA05: Financial planning connects to execution
    "PA02": {"PA05": 0.35},
    # PA03-PA04: Institutional design enables monitoring
    "PA03": {"PA04": 0.3},
}

# =============================================================================
# CONSTANTS - Temporal Cascade Patterns
# =============================================================================

# Short-term fixes that unlock long-term capabilities
TEMPORAL_CASCADE_PATTERNS: dict[str, dict[str, dict[str, Any]]] = {
    "MICRO": {
        # DIM01 improvement unlocks DIM03 capability
        "DIM01": {
            "DIM03": {
                "horizon_months": 12,
                "multiplier": 1.5,
                "effect": "Improved alignment enables better belief calibration",
            }
        },
        "DIM02": {
            "DIM05": {
                "horizon_months": 18,
                "multiplier": 1.7,
                "effect": "Financial clarity enhances execution capacity",
            }
        },
    },
    "MESO": {
        # Cluster 1 improvement unlocks Cluster 2
        "CL01": {
            "CL02": {
                "horizon_months": 24,
                "multiplier": 1.4,
                "effect": "Core capacity extends to adjacent clusters",
            }
        },
    },
}

# =============================================================================
# HELPER FUNCTIONS - Input Normalization
# =============================================================================


def _normalize_level(level: str | None) -> str:
    """Normaliza level a uno de MICRO/MESO/MACRO."""
    if level is None:
        return DEFAULT_LEVEL
    normalized = str(level).strip().upper()
    return normalized if normalized in VALID_LEVELS else DEFAULT_LEVEL


def _parse_score_key(score_key: str | None) -> tuple[str, str] | None:
    """
    Parsea score_key con formato PA##-DIM##.

    Returns:
        Tuple (pa_id, dim_id) si valido, None si invalido.
    """
    if not score_key:
        return None
    match = SCORE_KEY_PATTERN.match(str(score_key).strip().upper())
    return (match.group(1), match.group(2)) if match else None


def _safe_get_metadata(rec: dict[str, Any]) -> dict[str, Any]:
    """Extrae metadata de forma segura, siempre retorna dict."""
    meta = rec.get("metadata")
    return meta if isinstance(meta, dict) else {}


def _stable_sort_key(rec: dict[str, Any]) -> tuple[str, str]:
    """Genera clave de ordenamiento estable para recomendaciones."""
    rule_id = rec.get("rule_id", "")
    score_key = _safe_get_metadata(rec).get("score_key", "")
    return (score_key, rule_id)


def _ensure_deterministic_input(
    recommendations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Ordena recomendaciones de forma estable para garantizar determinismo."""
    return sorted(recommendations, key=_stable_sort_key)


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass(frozen=True)
class CrossPollinationNode:
    """Represents a cross-pollination opportunity between recommendations."""

    source_rule_id: str
    target_key: str
    pollination_strength: float
    mechanism: str
    estimated_bonus_score: float
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TemporalCascade:
    """Represents a temporal cascade from short-term to long-term effects."""

    root_rule_id: str
    target_key: str
    order: int  # 1 = direct, 2 = second-order, 3 = third-order
    horizon_months: int
    cascade_multiplier: float
    effect_description: str

    def get_temporal_id(self) -> str:
        """Generate unique ID for this cascade."""
        return f"{self.root_rule_id}->{self.target_key}[order={self.order}]"


@dataclass
class SynergyMatrix:
    """Tracks synergistic pairs and their combined strength."""

    _synergies: dict[SynergyPair, float] = field(default_factory=dict)
    _pair_counts: dict[SynergyPair, int] = field(default_factory=dict)

    def add_synergy(self, rule_a: str, rule_b: str, strength: float) -> None:
        """Add or update a synergy pair."""
        pair = tuple(sorted((rule_a, rule_b)))
        self._synergies[pair] = max(self._synergies.get(pair, 0.0), strength)
        self._pair_counts[pair] = self._pair_counts.get(pair, 0) + 1

    def get_synergy_multiplier(self, rule_ids: set[str]) -> float:
        """
        Calculate combined synergy multiplier for a set of rules.

        Formula: product of (1 + strength) for all synergistic pairs
        """
        if not rule_ids or len(rule_ids) < 2:
            return 1.0

        multiplier = 1.0
        for pair, strength in self._synergies.items():
            if pair[0] in rule_ids and pair[1] in rule_ids:
                multiplier *= (1.0 + strength)

        return min(multiplier, 5.0)  # Cap at 5x for sanity


@dataclass
class AmplificationConfig:
    """Configuracion para control de amplificacion."""

    max_amplification_factor: float | None = 10.0  # None = sin tope
    max_hidden_value_ratio: float = 5.0  # hidden_value <= base_value * ratio
    max_cascade_bonus: float = 2.0  # Maximo bonus de cascades
    max_synergy_multiplier: float = 3.0  # Maximo multiplicador de sinergias


@dataclass
class BifurcationResult:
    """Container for bifurcation analysis results."""

    level: str
    original_count: int
    bifurcated_count: int
    amplification_factor: float
    hidden_value_score: float
    cascade_depth: int
    cross_pollinations: list[CrossPollinationNode] = field(default_factory=list)
    temporal_cascades: list[TemporalCascade] = field(default_factory=list)
    synergy_matrix: SynergyMatrix = field(default_factory=SynergyMatrix)
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        # Ordenar cross_pollinations por (source, target)
        sorted_cps = sorted(
            self.cross_pollinations,
            key=lambda cp: (cp.source_rule_id, cp.target_key)
        )

        # Ordenar temporal_cascades por (root, order, horizon)
        sorted_cascades = sorted(
            self.temporal_cascades,
            key=lambda tc: (tc.root_rule_id, tc.order, tc.horizon_months)
        )

        return {
            "level": self.level,
            "original_count": self.original_count,
            "bifurcated_count": self.bifurcated_count,
            "amplification_factor": round(self.amplification_factor, 3),
            "hidden_value_score": round(self.hidden_value_score, 4),
            "cascade_depth": self.cascade_depth,
            "cross_pollinations": [
                {
                    "source": cp.source_rule_id,
                    "target": cp.target_key,
                    "strength": round(cp.pollination_strength, 3),
                    "mechanism": cp.mechanism,
                    "bonus": round(cp.estimated_bonus_score, 4),
                }
                for cp in sorted_cps
            ],
            "temporal_cascades": [
                {
                    "id": tc.get_temporal_id(),
                    "root": tc.root_rule_id,
                    "order": tc.order,
                    "horizon": tc.horizon_months,
                    "multiplier": round(tc.cascade_multiplier, 3),
                    "effect": tc.effect_description,
                }
                for tc in sorted_cascades
            ],
            "synergy_pairs": self.synergy_matrix._synergies.copy(),
            "generated_at": self.generated_at,
            "metadata": self.metadata,
        }


# =============================================================================
# MAIN CLASS - RecommendationBifurcator
# =============================================================================


class RecommendationBifurcator:
    """
    The BIFURCATOR: Transforms linear recommendations into exponential cascades.

    This is the heart of Phase 8's exponential injection. It takes standard
    recommendations from RecommendationEngine and discovers hidden multiplicative
    value through four strategies:

    Strategies
    ----------
    1. DIMENSIONAL RESONANCE: When DIM01 improves, related DIMs benefit (MICRO only)
    2. CROSS-POLLINATION: When fixing PA01 partially fixes PA03 (shared structure)
    3. TEMPORAL CASCADES: Short-term fixes unlock long-term capabilities
    4. SYNERGY DETECTION: Two interventions together > sum of parts

    Parameters
    ----------
    enable_resonance : bool, default=True
        Enable dimensional resonance detection (MICRO level only).
    enable_pollination : bool, default=True
        Enable cross-pollination analysis (all levels).
    enable_cascades : bool, default=True
        Enable temporal cascade identification (all levels).
    enable_synergies : bool, default=True
        Enable synergy matrix construction (all levels).
    resonance_threshold : float, default=0.3
        Minimum resonance strength to consider (0.0-1.0).
    pollination_threshold : float, default=0.25
        Minimum pollination strength to include (0.0-1.0).
    cascade_max_depth : int, default=3
        Maximum cascade depth (1, 2, or 3).
    amplification_config : AmplificationConfig | None, default=None
        Configuration for amplification calculation caps.

    Attributes
    ----------
    amplification_config : AmplificationConfig
        Configuration for amplification calculation caps.

    Examples
    --------
    >>> bifurcator = RecommendationBifurcator()
    >>> result = bifurcator.bifurcate(recommendations, "MICRO")
    >>> print(f"Amplification: {result.amplification_factor:.2f}x")
    Amplification: 2.47x

    Notes
    -----
    - Input order does not affect output (deterministic ordering applied)
    - Invalid `score_key` formats are skipped with debug logging
    - `level` is normalized to MICRO/MESO/MACRO (defaults to MICRO)
    """

    def __init__(
        self,
        enable_resonance: bool = True,
        enable_pollination: bool = True,
        enable_cascades: bool = True,
        enable_synergies: bool = True,
        resonance_threshold: float = 0.3,
        pollination_threshold: float = 0.25,
        cascade_max_depth: int = 3,
        amplification_config: AmplificationConfig | None = None,
    ) -> None:
        self.enable_resonance = enable_resonance
        self.enable_pollination = enable_pollination
        self.enable_cascades = enable_cascades
        self.enable_synergies = enable_synergies
        self.resonance_threshold = resonance_threshold
        self.pollination_threshold = pollination_threshold
        self.cascade_max_depth = min(max(1, cascade_max_depth), 3)
        self.amplification_config = amplification_config or AmplificationConfig()

        logger.info(
            f"RecommendationBifurcator initialized: "
            f"resonance={enable_resonance}, pollination={enable_pollination}, "
            f"cascades={enable_cascades}, synergies={enable_synergies}"
        )

    def bifurcate(
        self,
        recommendations: list[dict[str, Any]],
        level: str,
        score_data: dict[str, Any] | None = None,
    ) -> BifurcationResult:
        """
        Analyze recommendations for bifurcation opportunities.

        Parameters
        ----------
        recommendations : list[dict[str, Any]]
            List of recommendation dictionaries from RecommendationEngine.
        level : str
            Analysis level (MICRO/MESO/MACRO). Will be normalized.
        score_data : dict[str, Any] | None, default=None
            Optional score data for gap calculations.

        Returns
        -------
        BifurcationResult
            Complete bifurcation analysis with amplification metrics.
        """
        # Normalize level and ensure deterministic input
        level = _normalize_level(level)
        recommendations = _ensure_deterministic_input(recommendations)

        logger.info(f"Analyzing {len(recommendations)} {level} recommendations for bifurcation")

        original_count = len(recommendations)

        # Detect cross-pollinations
        cross_pollinations = []
        if self.enable_pollination:
            cross_pollinations = self._detect_cross_pollination(
                recommendations, level, score_data
            )
            logger.info(f"Found {len(cross_pollinations)} cross-pollination opportunities")

        # Detect temporal cascades
        temporal_cascades = []
        if self.enable_cascades:
            temporal_cascades = self._detect_temporal_cascades(
                recommendations, level, score_data
            )
            logger.info(f"Found {len(temporal_cascades)} temporal cascades")

        # Build synergy matrix
        synergy_matrix = SynergyMatrix()
        if self.enable_synergies:
            synergy_matrix = self._construct_synergy_matrix(
                recommendations, level, score_data
            )
            logger.info(f"Built synergy matrix with {len(synergy_matrix._synergies)} pairs")

        # Calculate amplification
        rule_ids = {rec.get("rule_id", "") for rec in recommendations}
        amplification, hidden_value, cascade_depth = self._calculate_amplification(
            original_count,
            cross_pollinations,
            temporal_cascades,
            synergy_matrix,
            rule_ids,
        )

        bifurcated_count = original_count + len(cross_pollinations) + len(temporal_cascades)

        return BifurcationResult(
            level=level,
            original_count=original_count,
            bifurcated_count=bifurcated_count,
            amplification_factor=amplification,
            hidden_value_score=hidden_value,
            cascade_depth=cascade_depth,
            cross_pollinations=cross_pollinations,
            temporal_cascades=temporal_cascades,
            synergy_matrix=synergy_matrix,
            metadata={
                "resonance_enabled": self.enable_resonance,
                "pollination_enabled": self.enable_pollination,
                "cascades_enabled": self.enable_cascades,
                "synergies_enabled": self.enable_synergies,
            },
        )

    def _detect_dimensional_resonance(
        self,
        recommendations: list[dict[str, Any]],
        score_data: dict[str, Any] | None,
    ) -> list[CrossPollinationNode]:
        """Detect dimensional resonance opportunities (MICRO level only)."""
        resonances = []

        for rec in recommendations:
            metadata = _safe_get_metadata(rec)
            parsed = _parse_score_key(metadata.get("score_key"))

            if parsed is None:
                logger.debug(f"Skipping resonance for invalid score_key: {metadata.get('score_key')}")
                continue

            pa_id, dim_id = parsed

            if dim_id not in DIMENSIONAL_RESONANCE:
                continue

            for target_dim, strength in DIMENSIONAL_RESONANCE[dim_id].items():
                if strength < self.resonance_threshold:
                    continue

                target_key = f"{pa_id}-{target_dim}"

                # Tolerancia a gap None/invalido
                raw_gap = metadata.get("gap")
                original_gap = abs(float(raw_gap)) if isinstance(raw_gap, (int, float)) else 0.0
                bonus = original_gap * strength * 0.3

                resonances.append(CrossPollinationNode(
                    source_rule_id=rec.get("rule_id", "UNKNOWN"),
                    target_key=target_key,
                    pollination_strength=strength,
                    mechanism=f"dimensional_resonance:{dim_id} -> {target_dim}",
                    estimated_bonus_score=bonus,
                    evidence={
                        "source_dim": dim_id,
                        "target_dim": target_dim,
                        "resonance_coefficient": strength,
                        "original_gap": original_gap,
                    }
                ))

        logger.debug(f"Found {len(resonances)} dimensional resonances")
        return resonances

    def _detect_cross_pollination(
        self,
        recommendations: list[dict[str, Any]],
        level: str,
        score_data: dict[str, Any] | None,
    ) -> list[CrossPollinationNode]:
        """Detect cross-pollination opportunities between recommendations."""
        pollinations = []

        # For MICRO level, include dimensional resonance
        if level == "MICRO" and self.enable_resonance:
            pollinations.extend(self._detect_dimensional_resonance(recommendations, score_data))

        # Detect PA-level cross-pollination
        for rec_a, rec_b in combinations(recommendations, 2):
            metadata_a = _safe_get_metadata(rec_a)
            metadata_b = _safe_get_metadata(rec_b)

            # Extract PA/DIM info safely
            score_key_a = metadata_a.get("score_key", "")
            score_key_b = metadata_b.get("score_key", "")

            parsed_a = _parse_score_key(score_key_a)
            parsed_b = _parse_score_key(score_key_b)

            if parsed_a is None or parsed_b is None:
                continue

            pa_a, _ = parsed_a
            pa_b, _ = parsed_b

            # Check for cross-pollination patterns
            if pa_a in CROSS_POLLINATION_PATTERNS:
                for target_pa, strength in CROSS_POLLINATION_PATTERNS[pa_a].items():
                    if pa_b == target_pa and strength >= self.pollination_threshold:
                        gap_a = metadata_a.get("gap", 0.0)
                        bonus = abs(float(gap_a)) * strength * 0.25 if isinstance(gap_a, (int, float)) else 0.0

                        pollinations.append(CrossPollinationNode(
                            source_rule_id=rec_a.get("rule_id", "UNKNOWN"),
                            target_key=score_key_b,
                            pollination_strength=strength,
                            mechanism=f"cross_pollination:{pa_a} -> {pa_b}",
                            estimated_bonus_score=bonus,
                            evidence={
                                "source_pa": pa_a,
                                "target_pa": pa_b,
                                "pattern_strength": strength,
                            }
                        ))

        logger.debug(f"Found {len(pollinations)} cross-pollinations")
        return pollinations

    def _detect_temporal_cascades(
        self,
        recommendations: list[dict[str, Any]],
        level: str,
        score_data: dict[str, Any] | None,
    ) -> list[TemporalCascade]:
        """Detect temporal cascade opportunities."""
        cascades = []
        patterns = TEMPORAL_CASCADE_PATTERNS.get(level, {})

        if not patterns:
            return cascades

        for rec in recommendations:
            metadata = _safe_get_metadata(rec)
            score_key = metadata.get("score_key", "")
            rule_id = rec.get("rule_id", "")

            # Extract the source (DIM or CL)
            source = None
            if level == "MICRO":
                parsed = _parse_score_key(score_key)
                if parsed:
                    _, source = parsed
            elif level == "MESO":
                source = metadata.get("cluster_id")

            if source is None or source not in patterns:
                continue

            # Build cascades up to max depth
            for target, config in patterns[source].items():
                horizon = config.get("horizon_months", 12)
                multiplier = config.get("multiplier", 1.0)
                effect = config.get("effect", "")

                # First-order cascade
                cascades.append(TemporalCascade(
                    root_rule_id=rule_id,
                    target_key=target,
                    order=1,
                    horizon_months=horizon,
                    cascade_multiplier=multiplier,
                    effect_description=effect,
                ))

                # Second-order cascades (if target is also a source)
                if self.cascade_max_depth >= 2 and target in patterns:
                    for second_target, second_config in patterns[target].items():
                        cascades.append(TemporalCascade(
                            root_rule_id=rule_id,
                            target_key=second_target,
                            order=2,
                            horizon_months=horizon + second_config.get("horizon_months", 12),
                            cascade_multiplier=multiplier * second_config.get("multiplier", 1.0),
                            effect_description=f"Second-order: {effect} -> {second_config.get('effect', '')}",
                        ))

                        # Third-order cascades
                        if self.cascade_max_depth >= 3 and second_target in patterns:
                            for third_target, third_config in patterns[second_target].items():
                                cascades.append(TemporalCascade(
                                    root_rule_id=rule_id,
                                    target_key=third_target,
                                    order=3,
                                    horizon_months=horizon + second_config.get("horizon_months", 12) + third_config.get("horizon_months", 12),
                                    cascade_multiplier=multiplier * second_config.get("multiplier", 1.0) * third_config.get("multiplier", 1.0),
                                    effect_description=f"Third-order: {effect} -> ... -> {third_config.get('effect', '')}",
                                ))

        logger.debug(f"Found {len(cascades)} temporal cascades")
        return cascades

    def _construct_synergy_matrix(
        self,
        recommendations: list[dict[str, Any]],
        level: str,
        score_data: dict[str, Any] | None,
    ) -> SynergyMatrix:
        """Build synergy matrix detecting pairs that work better together."""
        matrix = SynergyMatrix()

        # Analyze pairs for synergistic potential
        for rec_a, rec_b in combinations(recommendations, 2):
            rule_a = rec_a.get("rule_id", "")
            rule_b = rec_b.get("rule_id", "")

            if not rule_a or not rule_b:
                continue

            metadata_a = _safe_get_metadata(rec_a)
            metadata_b = _safe_get_metadata(rec_b)

            # Calculate synergy based on shared dimensions
            synergy = 0.0

            score_key_a = metadata_a.get("score_key", "")
            score_key_b = metadata_b.get("score_key", "")

            parsed_a = _parse_score_key(score_key_a)
            parsed_b = _parse_score_key(score_key_b)

            if parsed_a and parsed_b:
                pa_a, dim_a = parsed_a
                pa_b, dim_b = parsed_b

                # Same PA, different DIM -> moderate synergy
                if pa_a == pa_b and dim_a != dim_b:
                    synergy = 0.3
                # Different PA, same DIM -> moderate synergy
                elif pa_a != pa_b and dim_a == dim_b:
                    synergy = 0.25

            # Cluster-based synergy for MESO
            if level == "MESO":
                cluster_a = metadata_a.get("cluster_id", "")
                cluster_b = metadata_b.get("cluster_id", "")

                # Same cluster recommendations have synergy
                if cluster_a and cluster_b and cluster_a == cluster_b:
                    synergy = max(synergy, 0.4)

            if synergy > 0:
                matrix.add_synergy(rule_a, rule_b, synergy)

        logger.debug(f"Built synergy matrix with {len(matrix._synergies)} pairs")
        return matrix

    def _calculate_amplification(
        self,
        base_count: int,
        cross_pollinations: list[CrossPollinationNode],
        temporal_cascades: list[TemporalCascade],
        synergy_matrix: SynergyMatrix,
        rule_ids: set[str],
    ) -> tuple[float, float, int]:
        """
        Calculate amplification factor with documented formula.

        FORMULA
        -------
        amplification = (1 + hidden_ratio + cascade_bonus) * synergy_mult

        WHERE
        ------
        - hidden_ratio = sum(cp.bonus) / base_count, capped at max_hidden_value_ratio
        - cascade_bonus = sum(tc.multiplier - 1.0) for order > 1, capped
        - synergy_mult = product(1 + pair_strength), capped at max_synergy_multiplier

        Returns
        -------
        tuple of (amplification_factor, hidden_value_score, cascade_depth)
        """
        config = self.amplification_config

        # Base
        base_value = max(base_count, 1)

        # Component 1: Hidden Value (cross-pollinations)
        raw_hidden = sum(cp.estimated_bonus_score for cp in cross_pollinations)
        hidden_ratio = min(raw_hidden / base_value, config.max_hidden_value_ratio)

        # Component 2: Cascade Bonus (only 2nd and 3rd order contribute bonus)
        # Order 1 has multiplier=1.0, so (1.0 - 1.0) = 0 contribution
        raw_cascade = sum(
            tc.cascade_multiplier - 1.0
            for tc in temporal_cascades
            if tc.order > 1
        )
        cascade_bonus = min(raw_cascade, config.max_cascade_bonus)

        # Component 3: Synergy Multiplier
        raw_synergy = synergy_matrix.get_synergy_multiplier(rule_ids)
        synergy_mult = min(raw_synergy, config.max_synergy_multiplier)

        # Final calculation
        amplification = (1.0 + hidden_ratio + cascade_bonus) * synergy_mult

        # Apply global cap if configured
        if config.max_amplification_factor is not None:
            amplification = min(amplification, config.max_amplification_factor)

        # Derived metrics
        hidden_value_score = raw_hidden
        cascade_depth = max((tc.order for tc in temporal_cascades), default=0)

        logger.debug(
            f"Amplification breakdown: hidden_ratio={hidden_ratio:.3f}, "
            f"cascade_bonus={cascade_bonus:.3f}, synergy_mult={synergy_mult:.3f} "
            f"-> factor={amplification:.3f}"
        )

        return amplification, hidden_value_score, cascade_depth


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def bifurcate_recommendations(
    recommendations: list[dict[str, Any]],
    level: str,
    score_data: dict[str, Any] | None = None,
    **kwargs: Any,
) -> BifurcationResult:
    """
    Convenience function for quick bifurcation analysis.

    Parameters
    ----------
    recommendations : list[dict[str, Any]]
        List of recommendation dictionaries.
    level : str
        Analysis level (MICRO/MESO/MACRO).
    score_data : dict[str, Any] | None, default=None
        Optional score data.
    **kwargs : Any
        Additional arguments passed to RecommendationBifurcator.

    Returns
    -------
    BifurcationResult
        Complete bifurcation analysis.

    Examples
    --------
    >>> result = bifurcate_recommendations(recs, "MICRO")
    >>> print(f"Amplification: {result.amplification_factor:.2f}x")
    """
    bifurcator = RecommendationBifurcator(**kwargs)
    return bifurcator.bifurcate(recommendations, level, score_data)


# =============================================================================
# PUBLIC API EXPORT
# =============================================================================

__all__ = [
    "RecommendationBifurcator",
    "BifurcationResult",
    "CrossPollinationNode",
    "TemporalCascade",
    "SynergyMatrix",
    "AmplificationConfig",
    "bifurcate_recommendations",
]
