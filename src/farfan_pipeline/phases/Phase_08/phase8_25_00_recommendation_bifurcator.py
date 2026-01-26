# phase8_25_00_recommendation_bifurcator.py - Recommendation Bifurcation Engine
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_25_00_recommendation_bifurcator
Purpose: Transforms linear recommendations into exponential cascades via bifurcation analysis
Owner: phase8_core
Stage: 25 (Bifurcation)
Order: 00
Type: ENG
Lifecycle: ACTIVE
Version: 2.0.0
Effective-Date: 2026-01-25

This module implements the BIFURCATOR, which takes standard recommendations from
RecommendationEngine and discovers hidden multiplicative value through four strategies:

1. DIMENSIONAL RESONANCE: When DIM01 improves, related DIMs benefit (MICRO only)
2. CROSS-POLLINATION: When fixing PA01 partially fixes PA03 (shared structure)
3. TEMPORAL CASCADES: Short-term fixes unlock long-term capabilities
4. SYNERGY DETECTION: Two interventions together > sum of parts

Enhancement Value (v2.0):
- SISAS signal integration for pattern-aware bifurcation
- Load bifurcation patterns from JSON (aligns with recommendation_rules_enhanced.json)
- Signal-based priority scoring for cascades and pollinations
- Enhanced provenance with signal metadata
- Configurable pattern source (JSON or hardcoded fallback)

Author: F.A.R.F.A.N Core Team
Python: 3.10+
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "2.0.0"
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

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    try:
        from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
            QuestionnaireSignalRegistry,
        )
    except ImportError:
        QuestionnaireSignalRegistry = Any  # type: ignore

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
# CONSTANTS - Signal-Based Priority Thresholds
# =============================================================================

# Priority scoring thresholds (aligned with signal enrichment)
CRITICAL_SCORE_THRESHOLD = 0.3  # Scores below this are critical
LOW_SCORE_THRESHOLD = 0.5  # Scores below this are low
CRITICAL_PRIORITY_BOOST = 0.3  # Priority boost for critical scores
LOW_PRIORITY_BOOST = 0.2  # Priority boost for low scores
STRONG_PATTERN_THRESHOLD = 5  # Pattern count for strong support
ACTIONABILITY_BOOST = 0.15  # Boost for high actionability

# =============================================================================
# DEFAULT FALLBACK PATTERNS (used when JSON loading fails)
# =============================================================================

# When a dimension improves, which related dimensions benefit?
DEFAULT_DIMENSIONAL_RESONANCE: dict[str, dict[str, float]] = {
    "DIM01": {"DIM02": 0.4, "DIM03": 0.3},  # Alignment -> Finance, Beliefs
    "DIM02": {"DIM01": 0.3, "DIM05": 0.5},  # Finance -> Alignment, Execution
    "DIM03": {"DIM01": 0.3, "DIM04": 0.4},  # Beliefs -> Alignment, Causality
    "DIM04": {"DIM03": 0.3, "DIM06": 0.5},  # Causality -> Beliefs, Evidence
    "DIM05": {"DIM02": 0.4, "DIM06": 0.3},  # Execution -> Finance, Evidence
    "DIM06": {"DIM04": 0.4, "DIM05": 0.3},  # Evidence -> Causality, Execution
}

# Shared structural patterns between PAs that enable cross-pollination
DEFAULT_CROSS_POLLINATION_PATTERNS: dict[str, dict[str, float]] = {
    "PA01": {"PA03": 0.4},  # Strategic planning connection
    "PA02": {"PA05": 0.35},  # Financial-exection connection
    "PA03": {"PA04": 0.3},  # Governance-monitoring connection
}

# Short-term fixes that unlock long-term capabilities
DEFAULT_TEMPORAL_CASCADE_PATTERNS: dict[str, dict[str, dict[str, Any]]] = {
    "MICRO": {
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
    # NEW: Signal-based enhancement
    signal_confidence: float = 0.0
    signal_patterns: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TemporalCascade:
    """Represents a temporal cascade from short-term to long-term effects."""

    root_rule_id: str
    target_key: str
    order: int  # 1 = direct, 2 = second-order, 3 = third-order
    horizon_months: int
    cascade_multiplier: float
    effect_description: str
    # NEW: Signal-based enhancement
    signal_confidence: float = 0.0
    prerequisite_signals: list[str] = field(default_factory=list)

    def get_temporal_id(self) -> str:
        """Generate unique ID for this cascade."""
        return f"{self.root_rule_id}->{self.target_key}[order={self.order}]"


@dataclass
class SynergyMatrix:
    """Tracks synergistic pairs and their combined strength."""

    _synergies: dict[SynergyPair, float] = field(default_factory=dict)
    _pair_counts: dict[SynergyPair, int] = field(default_factory=dict)
    # NEW: Signal-based enhancement
    _signal_support: dict[SynergyPair, float] = field(default_factory=dict)

    def add_synergy(
        self,
        rule_a: str,
        rule_b: str,
        strength: float,
        signal_confidence: float = 0.0
    ) -> None:
        """Add or update a synergy pair with optional signal confidence."""
        pair = tuple(sorted((rule_a, rule_b)))
        self._synergies[pair] = max(self._synergies.get(pair, 0.0), strength)
        self._pair_counts[pair] = self._pair_counts.get(pair, 0) + 1
        if signal_confidence > 0:
            self._signal_support[pair] = max(self._signal_support.get(pair, 0.0), signal_confidence)

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
                # Apply signal boost if available
                signal_boost = self._signal_support.get(pair, 0.0)
                effective_strength = strength * (1.0 + signal_boost)
                multiplier *= (1.0 + effective_strength)

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
    # NEW: Signal-based enrichment metadata
    signal_enrichment: dict[str, Any] = field(default_factory=dict)

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
                    "signal_confidence": round(cp.signal_confidence, 3),
                    "signal_patterns": cp.signal_patterns,
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
                    "signal_confidence": round(tc.signal_confidence, 3),
                    "prerequisite_signals": tc.prerequisite_signals,
                }
                for tc in sorted_cascades
            ],
            "synergy_pairs": self.synergy_matrix._synergies.copy(),
            "signal_support": self.synergy_matrix._signal_support.copy(),
            "generated_at": self.generated_at,
            "metadata": self.metadata,
            "signal_enrichment": self.signal_enrichment,
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

    v2.0 Enhancements
    -----------------
    - SISAS signal integration for pattern-aware bifurcation
    - Load bifurcation patterns from JSON (aligns with recommendation_rules_enhanced.json)
    - Signal-based priority scoring for cascades and pollinations
    - Enhanced provenance with signal metadata

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
    enable_signal_enrichment : bool, default=True
        Enable SISAS signal-based enrichment (v2.0).
    resonance_threshold : float, default=0.3
        Minimum resonance strength to consider (0.0-1.0).
    pollination_threshold : float, default=0.25
        Minimum pollination strength to include (0.0-1.0).
    cascade_max_depth : int, default=3
        Maximum cascade depth (1, 2, or 3).
    amplification_config : AmplificationConfig | None, default=None
        Configuration for amplification calculation caps.
    signal_registry : QuestionnaireSignalRegistry | None, default=None
        SISAS signal registry for pattern-aware bifurcation.
    rules_path : str | Path | None, default=None
        Path to JSON rules file containing bifurcation_patterns.

    Attributes
    ----------
    amplification_config : AmplificationConfig
        Configuration for amplification calculation caps.
    signal_registry : QuestionnaireSignalRegistry | None
        SISAS signal registry for signal-based enhancements.
    bifurcation_patterns : dict[str, Any]
        Loaded bifurcation patterns from JSON or defaults.

    Examples
    --------
    >>> from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
    ...     QuestionnaireSignalRegistry
    ... )
    >>> registry = QuestionnaireSignalRegistry()
    >>> bifurcator = RecommendationBifurcator(signal_registry=registry)
    >>> result = bifurcator.bifurcate(recommendations, "MICRO")
    >>> print(f"Amplification: {result.amplification_factor:.2f}x")
    Amplification: 2.47x

    Notes
    -----
    - Input order does not affect output (deterministic ordering applied)
    - Invalid `score_key` formats are skipped with debug logging
    - `level` is normalized to MICRO/MESO/MACRO (defaults to MICRO)
    - Bifurcation patterns loaded from JSON if available, otherwise uses defaults
    """

    def __init__(
        self,
        enable_resonance: bool = True,
        enable_pollination: bool = True,
        enable_cascades: bool = True,
        enable_synergies: bool = True,
        enable_signal_enrichment: bool = True,
        resonance_threshold: float = 0.3,
        pollination_threshold: float = 0.25,
        cascade_max_depth: int = 3,
        amplification_config: AmplificationConfig | None = None,
        signal_registry: QuestionnaireSignalRegistry | None = None,
        rules_path: str | Path | None = None,
    ) -> None:
        self.enable_resonance = enable_resonance
        self.enable_pollination = enable_pollination
        self.enable_cascades = enable_cascades
        self.enable_synergies = enable_synergies
        self.enable_signal_enrichment = enable_signal_enrichment
        self.resonance_threshold = resonance_threshold
        self.pollination_threshold = pollination_threshold
        self.cascade_max_depth = min(max(1, cascade_max_depth), 3)
        self.amplification_config = amplification_config or AmplificationConfig()
        self.signal_registry = signal_registry

        # Load bifurcation patterns from JSON
        self.bifurcation_patterns = self._load_bifurcation_patterns(rules_path)

        logger.info(
            f"RecommendationBifurcator v2.0 initialized: "
            f"resonance={enable_resonance}, pollination={enable_pollination}, "
            f"cascades={enable_cascades}, synergies={enable_synergies}, "
            f"signal_enrichment={enable_signal_enrichment}, "
            f"signal_registry={'enabled' if signal_registry else 'disabled'}"
        )

    def _load_bifurcation_patterns(
        self, rules_path: str | Path | None
    ) -> dict[str, Any]:
        """
        Load bifurcation patterns from JSON rules file.

        Falls back to default patterns if JSON loading fails.
        """
        if rules_path is None:
            # Try default path
            rules_path = (
                Path(__file__).resolve().parent
                / "json_phase_eight"
                / "recommendation_rules_enhanced.json"
            )

        rules_path = Path(rules_path)

        if not rules_path.exists():
            logger.warning(
                f"Bifurcation patterns file not found: {rules_path}. Using defaults."
            )
            return self._get_default_patterns()

        try:
            with open(rules_path, encoding="utf-8") as f:
                rules = json.load(f)

            patterns = rules.get("bifurcation_patterns", {})
            if not patterns:
                logger.warning(
                    "No bifurcation_patterns section found in JSON. Using defaults."
                )
                return self._get_default_patterns()

            logger.info(
                f"Loaded bifurcation patterns from JSON: "
                f"{len(patterns.get('dimensional_resonance', {}).get('mappings', {}))} resonance mappings, "
                f"{len(patterns.get('cross_pollination', {}).get('patterns', {}))} pollination patterns, "
                f"{sum(len(c) for c in patterns.get('temporal_cascades', {}).get('cascades', {}).values())} cascade patterns"
            )
            return patterns

        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load bifurcation patterns from JSON: {e}. Using defaults.")
            return self._get_default_patterns()

    def _get_default_patterns(self) -> dict[str, Any]:
        """Return default fallback patterns."""
        return {
            "dimensional_resonance": {
                "mappings": DEFAULT_DIMENSIONAL_RESONANCE,
                "threshold": self.resonance_threshold,
                "bonus_multiplier": 0.3,
            },
            "cross_pollination": {
                "patterns": DEFAULT_CROSS_POLLINATION_PATTERNS,
                "threshold": self.pollination_threshold,
                "bonus_multiplier": 0.25,
            },
            "temporal_cascades": {
                "cascades": DEFAULT_TEMPORAL_CASCADE_PATTERNS,
                "max_depth": self.cascade_max_depth,
            },
            "synergy_detection": {
                "synergy_types": {
                    "same_pa_different_dim": {"strength": 0.3},
                    "different_pa_same_dim": {"strength": 0.25},
                    "same_cluster": {"strength": 0.4},
                }
            },
        }

    def _get_dimensional_resonance_mappings(self) -> dict[str, dict[str, float]]:
        """Get dimensional resonance mappings from loaded patterns."""
        dr = self.bifurcation_patterns.get("dimensional_resonance", {})
        mappings = dr.get("mappings", {})
        if not mappings:
            return DEFAULT_DIMENSIONAL_RESONANCE

        # Convert JSON structure to simple dict
        result = {}
        for dim_id, config in mappings.items():
            if isinstance(config, dict) and "resonances" in config:
                result[dim_id] = {
                    target: r.get("strength", 0.0)
                    for target, r in config["resonances"].items()
                }
            else:
                result[dim_id] = config
        return result

    def _get_cross_pollination_patterns(self) -> dict[str, dict[str, float]]:
        """Get cross-pollination patterns from loaded patterns."""
        cp = self.bifurcation_patterns.get("cross_pollination", {})
        patterns = cp.get("patterns", {})
        if not patterns:
            return DEFAULT_CROSS_POLLINATION_PATTERNS

        # Convert JSON structure to simple dict
        result = {}
        for pattern_id, config in patterns.items():
            if isinstance(config, dict):
                source = config.get("source_pa")
                target = config.get("target_pa")
                strength = config.get("strength", 0.0)
                if source and target:
                    if source not in result:
                        result[source] = {}
                    result[source][target] = strength
        return result

    def _get_temporal_cascade_patterns(self) -> dict[str, dict[str, dict[str, Any]]]:
        """Get temporal cascade patterns from loaded patterns."""
        tc = self.bifurcation_patterns.get("temporal_cascades", {})
        cascades = tc.get("cascades", {})
        if not cascades:
            return DEFAULT_TEMPORAL_CASCADE_PATTERNS

        # Convert JSON structure to simple dict
        result = {}
        for level, level_patterns in cascades.items():
            result[level] = {}
            for cascade_id, config in level_patterns.items():
                if isinstance(config, dict):
                    source = config.get("source")
                    if source:
                        result[level][source] = {}
        return cascades if cascades else DEFAULT_TEMPORAL_CASCADE_PATTERNS

    def _get_signal_confidence(
        self,
        score_key: str,
        score_data: dict[str, Any] | None,
    ) -> tuple[float, list[str]]:
        """
        Get signal confidence score for a given score_key.

        Returns:
            Tuple of (confidence_score, pattern_names)
        """
        if not self.enable_signal_enrichment or not self.signal_registry:
            return 0.0, []

        if not score_data:
            return 0.0, []

        try:
            # Extract question ID from score_data
            question_global = score_data.get("question_global")
            if not isinstance(question_global, int):
                return 0.0, []

            question_id = f"Q{question_global:03d}"

            # Get question mapping from registry (correct method)
            question_mapping = self.signal_registry.get_question_mapping(question_id)

            if question_mapping is None:
                return 0.0, []

            # QuestionSignalMapping has expected_patterns (list of pattern IDs)
            pattern_ids = question_mapping.expected_patterns or []
            pattern_count = len(pattern_ids)

            # Calculate confidence based on pattern count
            # More patterns = higher signal confidence
            if pattern_count >= STRONG_PATTERN_THRESHOLD:
                confidence = 0.2 + (pattern_count - STRONG_PATTERN_THRESHOLD) * 0.05
            else:
                confidence = pattern_count * 0.04

            # Also consider empirical availability
            empirical_availability = question_mapping.empirical_availability or 1.0
            confidence *= empirical_availability

            # Get signal information for pattern names
            signal_names = question_mapping.all_signals or []

            return min(confidence, 0.5), signal_names

        except Exception as exc:
            logger.debug(f"Signal confidence lookup failed for {score_key}: {exc}")
            return 0.0, []

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
            Optional score data for gap calculations and signal enrichment.

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

        # Build signal enrichment metadata
        signal_enrichment = {
            "enabled": self.enable_signal_enrichment,
            "registry_available": self.signal_registry is not None,
            "patterns_source": "JSON" if self.bifurcation_patterns else "DEFAULT",
        }

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
            signal_enrichment=signal_enrichment,
        )

    def _detect_dimensional_resonance(
        self,
        recommendations: list[dict[str, Any]],
        score_data: dict[str, Any] | None,
    ) -> list[CrossPollinationNode]:
        """Detect dimensional resonance opportunities (MICRO level only)."""
        resonances = []
        mappings = self._get_dimensional_resonance_mappings()

        for rec in recommendations:
            metadata = _safe_get_metadata(rec)
            parsed = _parse_score_key(metadata.get("score_key"))

            if parsed is None:
                logger.debug(f"Skipping resonance for invalid score_key: {metadata.get('score_key')}")
                continue

            pa_id, dim_id = parsed

            if dim_id not in mappings:
                continue

            for target_dim, strength in mappings[dim_id].items():
                if strength < self.resonance_threshold:
                    continue

                target_key = f"{pa_id}-{target_dim}"

                # Tolerancia a gap None/invalido
                raw_gap = metadata.get("gap")
                original_gap = abs(float(raw_gap)) if isinstance(raw_gap, (int, float)) else 0.0

                # Get signal confidence
                signal_confidence, signal_patterns = self._get_signal_confidence(
                    metadata.get("score_key", ""), score_data
                )

                # Apply signal boost to bonus
                signal_boost = 1.0 + signal_confidence
                bonus_multiplier = self.bifurcation_patterns.get(
                    "dimensional_resonance", {}
                ).get("bonus_multiplier", 0.3)
                bonus = original_gap * strength * bonus_multiplier * signal_boost

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
                    },
                    signal_confidence=signal_confidence,
                    signal_patterns=signal_patterns,
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
        patterns = self._get_cross_pollination_patterns()

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
            if pa_a in patterns:
                for target_pa, strength in patterns[pa_a].items():
                    if pa_b == target_pa and strength >= self.pollination_threshold:
                        gap_a = metadata_a.get("gap", 0.0)
                        base_bonus = abs(float(gap_a)) if isinstance(gap_a, (int, float)) else 0.0

                        # Get signal confidence
                        signal_confidence, signal_patterns = self._get_signal_confidence(score_key_a, score_data)

                        # Apply signal boost
                        signal_boost = 1.0 + signal_confidence
                        bonus_multiplier = self.bifurcation_patterns.get(
                            "cross_pollination", {}
                        ).get("bonus_multiplier", 0.25)
                        bonus = base_bonus * strength * bonus_multiplier * signal_boost

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
                            },
                            signal_confidence=signal_confidence,
                            signal_patterns=signal_patterns,
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
        patterns = self._get_temporal_cascade_patterns()
        level_patterns = patterns.get(level, {})

        if not level_patterns:
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

            if source is None or source not in level_patterns:
                continue

            # Get signal confidence for prerequisites
            signal_confidence, prerequisite_signals = self._get_signal_confidence(score_key, score_data)

            # Build cascades up to max depth
            for target, config in level_patterns[source].items():
                horizon = config.get("horizon_months", 12)
                multiplier = config.get("multiplier", 1.0)
                effect = config.get("effect", "")

                # Apply signal boost to multiplier
                signal_boost = 1.0 + (signal_confidence * 0.5)
                enhanced_multiplier = multiplier * signal_boost

                # First-order cascade
                cascades.append(TemporalCascade(
                    root_rule_id=rule_id,
                    target_key=target,
                    order=1,
                    horizon_months=horizon,
                    cascade_multiplier=enhanced_multiplier,
                    effect_description=effect,
                    signal_confidence=signal_confidence,
                    prerequisite_signals=prerequisite_signals,
                ))

                # Second-order cascades (if target is also a source)
                if self.cascade_max_depth >= 2 and target in level_patterns:
                    for second_target, second_config in level_patterns[target].items():
                        cascades.append(TemporalCascade(
                            root_rule_id=rule_id,
                            target_key=second_target,
                            order=2,
                            horizon_months=horizon + second_config.get("horizon_months", 12),
                            cascade_multiplier=enhanced_multiplier * second_config.get("multiplier", 1.0),
                            effect_description=f"Second-order: {effect} -> {second_config.get('effect', '')}",
                            signal_confidence=signal_confidence * 0.8,  # Decay for second order
                            prerequisite_signals=prerequisite_signals,
                        ))

                        # Third-order cascades
                        if self.cascade_max_depth >= 3 and second_target in level_patterns:
                            for third_target, third_config in level_patterns[second_target].items():
                                cascades.append(TemporalCascade(
                                    root_rule_id=rule_id,
                                    target_key=third_target,
                                    order=3,
                                    horizon_months=horizon + second_config.get("horizon_months", 12) + third_config.get("horizon_months", 12),
                                    cascade_multiplier=enhanced_multiplier * second_config.get("multiplier", 1.0) * third_config.get("multiplier", 1.0),
                                    effect_description=f"Third-order: {effect} -> ... -> {third_config.get('effect', '')}",
                                    signal_confidence=signal_confidence * 0.6,  # Decay for third order
                                    prerequisite_signals=prerequisite_signals,
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
        synergy_types = self.bifurcation_patterns.get("synergy_detection", {}).get(
            "synergy_types", {}
        )

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
                    synergy = synergy_types.get("same_pa_different_dim", {}).get("strength", 0.3)
                # Different PA, same DIM -> moderate synergy
                elif pa_a != pa_b and dim_a == dim_b:
                    synergy = synergy_types.get("different_pa_same_dim", {}).get("strength", 0.25)

            # Cluster-based synergy for MESO
            if level == "MESO":
                cluster_a = metadata_a.get("cluster_id", "")
                cluster_b = metadata_b.get("cluster_id", "")

                # Same cluster recommendations have synergy
                if cluster_a and cluster_b and cluster_a == cluster_b:
                    synergy = max(synergy, synergy_types.get("same_cluster", {}).get("strength", 0.4))

            if synergy > 0:
                # Get signal confidence for this pair
                sig_conf_a, _ = self._get_signal_confidence(score_key_a, score_data)
                sig_conf_b, _ = self._get_signal_confidence(score_key_b, score_data)
                combined_signal_confidence = (sig_conf_a + sig_conf_b) / 2

                matrix.add_synergy(rule_a, rule_b, synergy, combined_signal_confidence)

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
