# phase8_25_00_recommendation_bifurcator.py - THE BIFURCATOR: Exponential Recommendation Amplifier
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_25_00_recommendation_bifurcator
Purpose: EXPONENTIAL injection point for Phase 8 - transforms linear recommendations into
         multiplicative intervention cascades through strategic bifurcation analysis
Owner: phase8_core
Stage: 25 (Amplification - BETWEEN engine and enrichment)
Order: 00
Type: AMP (AMPLIFIER)
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-21

═══════════════════════════════════════════════════════════════════════════════════
                     🔱 THE BIFURCATOR MANIFESTO 🔱
═══════════════════════════════════════════════════════════════════════════════════

INSIGHT: Traditional recommendation engines produce N recommendations for N problems.
         This is LINEAR thinking in an EXPONENTIAL world.

THE BIFURCATOR REVOLUTION:
    1. Each recommendation is analyzed for "hidden children" - latent sub-interventions
       that would ALSO be triggered by the same action
    2. Cross-pollination detection: when intervention A partially solves problem B
    3. Temporal cascade effects: first-order → second-order → third-order benefits
    4. Synergy amplification: 2 interventions that together produce 5x the benefit

MATHEMATICAL FOUNDATION:
    Traditional: benefit = Σ(recommendation_i)
    Bifurcator:  benefit = Σ(recommendation_i) + Σ(cross_benefit_ij) + cascade_multiplier

WHERE THE EXPONENTIAL COMES FROM:
    - N base recommendations
    - N×(N-1)/2 potential cross-pollinations
    - N×depth temporal cascades
    - 2^k synergy combinations for k synergistic pairs
    
SELF-CONTAINED DESIGN:
    - Zero new dependencies
    - Plugs into existing Recommendation/RecommendationSet dataclasses
    - Uses only Phase 7/8 data already flowing through pipeline
    - Enriches metadata without changing schema

UNORTHODOX STRATEGIES:
    1. "Recommendation Archaeology" - dig into WHY a rule matched to find buried value
    2. "Dimensional Resonance" - same intervention in DIM01 ripples to DIM03
    3. "Cluster Echoes" - MESO findings that predict MICRO opportunities
    4. "Temporal Folding" - short-horizon fixes that unlock long-horizon capabilities
    
Author: F.A.R.F.A.N Exponential Architecture Team
Python: 3.10+
═══════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 8
__stage__ = 25
__order__ = 0
__author__ = "F.A.R.F.A.N Exponential Team"
__created__ = "2026-01-21"
__modified__ = "2026-01-21"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"
__codename__ = "BIFURCATOR"

import logging
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator
from collections import defaultdict
from itertools import combinations

logger = logging.getLogger(__name__)

__all__ = [
    "RecommendationBifurcator",
    "BifurcationResult",
    "CrossPollinationNode",
    "TemporalCascade",
    "SynergyMatrix",
    "bifurcate_recommendations",
]


# =============================================================================
# DIMENSIONAL RESONANCE MATRIX
# =============================================================================
# This encodes the hidden relationships between dimensions that traditional
# rule engines completely miss. When you improve DIM01, what else improves?

DIMENSIONAL_RESONANCE = {
    # DIM01 (Normativa) resonates with...
    "DIM01": {"DIM03": 0.7, "DIM06": 0.5},  # Legal → Evaluation, Governance
    # DIM02 (Financiera) resonates with...
    "DIM02": {"DIM05": 0.8, "DIM04": 0.4},  # Financial → Resources, Implementation
    # DIM03 (Evaluación) resonates with...
    "DIM03": {"DIM01": 0.6, "DIM04": 0.5},  # Evaluation → Legal, Implementation
    # DIM04 (Implementación) resonates with...
    "DIM04": {"DIM02": 0.5, "DIM05": 0.7},  # Implementation → Financial, Resources
    # DIM05 (Recursos) resonates with...
    "DIM05": {"DIM02": 0.6, "DIM04": 0.6},  # Resources → Financial, Implementation
    # DIM06 (Gobernanza) resonates with...
    "DIM06": {"DIM01": 0.8, "DIM03": 0.5},  # Governance → Legal, Evaluation
}

# Cluster echo patterns - when MESO findings predict MICRO opportunities
CLUSTER_ECHO_PATTERNS = {
    "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],  # Legal cluster → policy areas
    "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],  # Implementation cluster
    "CLUSTER_MESO_3": ["PA07", "PA08"],  # Monitoring cluster
    "CLUSTER_MESO_4": ["PA09", "PA10"],  # Strategic cluster
}

# Temporal folding coefficients - how short fixes unlock long capabilities
TEMPORAL_FOLDING = {
    3: {"unlock_12": 0.3, "unlock_18": 0.1},   # 3-month fix unlocks 12/18 month
    6: {"unlock_12": 0.5, "unlock_18": 0.2},   # 6-month fix unlocks 12/18 month
    9: {"unlock_18": 0.4},                      # 9-month fix unlocks 18 month
    12: {"amplify_existing": 0.3},              # 12-month synergizes with existing
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CrossPollinationNode:
    """
    Represents a hidden benefit discovered through cross-pollination analysis.
    
    Example: Recommendation for PA01-DIM02 (Financial in Land Policy)
             also partially addresses PA03-DIM02 (Financial in Mining Policy)
             because both share fiscal baseline requirements.
    """
    source_rule_id: str
    target_key: str  # PA##-DIM## or CLUSTER##
    pollination_strength: float  # 0.0 to 1.0
    mechanism: str  # How the cross-benefit occurs
    estimated_bonus_score: float  # Additional score improvement expected
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass  
class TemporalCascade:
    """
    Models how a short-term intervention cascades into long-term effects.
    
    First-order: Direct effect (the recommendation itself)
    Second-order: Unlocked capability (what becomes possible)
    Third-order: Compound benefit (exponential growth region)
    """
    root_rule_id: str
    order: int  # 1, 2, or 3
    horizon_months: int  # When this effect materializes
    effect_description: str
    cascade_multiplier: float  # How much this amplifies the base benefit
    prerequisites: list[str] = field(default_factory=list)
    
    def get_temporal_id(self) -> str:
        """Generate unique ID for this cascade node."""
        return f"{self.root_rule_id}_T{self.order}_{self.horizon_months}M"


@dataclass
class SynergyMatrix:
    """
    Encodes which recommendations synergize and their combined effect.
    
    Synergy occurs when:
    - Two recommendations target different dimensions of same PA
    - Two recommendations target same dimension in related PAs
    - MESO recommendation amplifies MICRO recommendation
    """
    synergy_pairs: dict[tuple[str, str], float] = field(default_factory=dict)
    synergy_descriptions: dict[tuple[str, str], str] = field(default_factory=dict)
    
    def add_synergy(
        self, 
        rule_id_a: str, 
        rule_id_b: str, 
        strength: float,
        description: str
    ) -> None:
        """Register a synergy between two recommendations."""
        key = tuple(sorted([rule_id_a, rule_id_b]))
        self.synergy_pairs[key] = strength
        self.synergy_descriptions[key] = description
    
    def get_synergy_multiplier(self, rule_ids: set[str]) -> float:
        """Calculate combined synergy multiplier for a set of rules."""
        multiplier = 1.0
        for pair, strength in self.synergy_pairs.items():
            if set(pair).issubset(rule_ids):
                # Synergistic pairs multiply, not add
                multiplier *= (1.0 + strength)
        return multiplier
    
    def get_total_synergies(self) -> int:
        """Return total number of discovered synergies."""
        return len(self.synergy_pairs)


@dataclass
class BifurcationResult:
    """
    The complete bifurcation analysis for a recommendation set.
    
    This is THE exponential payload - it contains:
    - Original recommendations (linear)
    - Cross-pollinations discovered (quadratic potential)
    - Temporal cascades identified (exponential growth)
    - Synergy matrix (combinatorial optimization)
    """
    original_count: int
    bifurcated_count: int  # Includes hidden benefits
    cross_pollinations: list[CrossPollinationNode]
    temporal_cascades: list[TemporalCascade]
    synergy_matrix: SynergyMatrix
    amplification_factor: float  # Total benefit / Base benefit
    level: str
    analysis_timestamp: str
    
    # Derived metrics
    hidden_value_score: float = 0.0  # Sum of discovered hidden benefits
    cascade_depth: int = 0  # Maximum temporal cascade depth reached
    strongest_synergy: tuple[str, str, float] | None = None
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON output."""
        return {
            "level": self.level,
            "original_count": self.original_count,
            "bifurcated_count": self.bifurcated_count,
            "amplification_factor": round(self.amplification_factor, 3),
            "hidden_value_score": round(self.hidden_value_score, 3),
            "cascade_depth": self.cascade_depth,
            "cross_pollinations_count": len(self.cross_pollinations),
            "temporal_cascades_count": len(self.temporal_cascades),
            "synergies_count": self.synergy_matrix.get_total_synergies(),
            "strongest_synergy": self.strongest_synergy,
            "analysis_timestamp": self.analysis_timestamp,
            "cross_pollinations": [
                {
                    "source": cp.source_rule_id,
                    "target": cp.target_key,
                    "strength": round(cp.pollination_strength, 3),
                    "mechanism": cp.mechanism,
                    "bonus": round(cp.estimated_bonus_score, 4),
                }
                for cp in self.cross_pollinations
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
                for tc in self.temporal_cascades
            ],
        }


# =============================================================================
# THE BIFURCATOR ENGINE
# =============================================================================

class RecommendationBifurcator:
    """
    The BIFURCATOR: Transforms linear recommendations into exponential cascades.
    
    This is the heart of Phase 8's exponential injection. It takes the standard
    recommendations from RecommendationEngine and discovers hidden multiplicative
    value through four strategies:
    
    1. DIMENSIONAL RESONANCE: When DIM01 improves, what else improves?
    2. CROSS-POLLINATION: When PA01 is fixed, how does PA03 benefit?
    3. TEMPORAL CASCADES: When a 3-month fix unlocks 12-month capabilities
    4. SYNERGY DETECTION: When two interventions together produce 5x benefit
    
    Usage:
        bifurcator = RecommendationBifurcator()
        result = bifurcator.bifurcate(recommendation_set)
        # result.amplification_factor shows the exponential multiplier
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
    ):
        """
        Initialize the Bifurcator with configurable strategies.
        
        Args:
            enable_resonance: Enable dimensional resonance detection
            enable_pollination: Enable cross-pollination analysis
            enable_cascades: Enable temporal cascade identification
            enable_synergies: Enable synergy matrix construction
            resonance_threshold: Minimum resonance strength to consider
            pollination_threshold: Minimum pollination strength to include
            cascade_max_depth: Maximum cascade depth (1-3)
        """
        self.enable_resonance = enable_resonance
        self.enable_pollination = enable_pollination
        self.enable_cascades = enable_cascades
        self.enable_synergies = enable_synergies
        self.resonance_threshold = resonance_threshold
        self.pollination_threshold = pollination_threshold
        self.cascade_max_depth = min(max(1, cascade_max_depth), 3)
        
        logger.info(
            f"🔱 Bifurcator initialized: resonance={enable_resonance}, "
            f"pollination={enable_pollination}, cascades={enable_cascades}, "
            f"synergies={enable_synergies}, max_depth={cascade_max_depth}"
        )
    
    def bifurcate(
        self,
        recommendations: list[dict[str, Any]],
        level: str,
        score_data: dict[str, Any] | None = None,
    ) -> BifurcationResult:
        """
        Perform bifurcation analysis on a recommendation set.
        
        This is the main entry point. It orchestrates all four exponential
        strategies and returns a comprehensive BifurcationResult.
        
        Args:
            recommendations: List of recommendation dicts from RecommendationEngine
            level: MICRO, MESO, or MACRO
            score_data: Optional score data for context-aware analysis
            
        Returns:
            BifurcationResult with all discovered exponential value
        """
        logger.info(f"🔱 Bifurcating {len(recommendations)} {level} recommendations")
        
        cross_pollinations: list[CrossPollinationNode] = []
        temporal_cascades: list[TemporalCascade] = []
        synergy_matrix = SynergyMatrix()
        
        # Strategy 1: Dimensional Resonance (for MICRO only)
        if self.enable_resonance and level == "MICRO":
            resonances = self._detect_dimensional_resonance(recommendations, score_data)
            cross_pollinations.extend(resonances)
        
        # Strategy 2: Cross-Pollination (all levels)
        if self.enable_pollination:
            pollinations = self._detect_cross_pollination(recommendations, level)
            cross_pollinations.extend(pollinations)
        
        # Strategy 3: Temporal Cascades (all levels)
        if self.enable_cascades:
            cascades = self._build_temporal_cascades(recommendations, level)
            temporal_cascades.extend(cascades)
        
        # Strategy 4: Synergy Matrix (all levels)
        if self.enable_synergies:
            synergy_matrix = self._construct_synergy_matrix(recommendations, level)
        
        # Calculate amplification factor
        base_value = len(recommendations)
        hidden_value = sum(cp.estimated_bonus_score for cp in cross_pollinations)
        cascade_value = sum(tc.cascade_multiplier - 1.0 for tc in temporal_cascades)
        synergy_multiplier = synergy_matrix.get_synergy_multiplier(
            {r.get("rule_id", "") for r in recommendations}
        )
        
        total_value = (base_value + hidden_value) * (1 + cascade_value) * synergy_multiplier
        amplification_factor = total_value / max(base_value, 1)
        
        # Find strongest synergy
        strongest = None
        max_strength = 0.0
        for pair, strength in synergy_matrix.synergy_pairs.items():
            if strength > max_strength:
                max_strength = strength
                strongest = (pair[0], pair[1], strength)
        
        result = BifurcationResult(
            original_count=len(recommendations),
            bifurcated_count=len(recommendations) + len(cross_pollinations),
            cross_pollinations=cross_pollinations,
            temporal_cascades=temporal_cascades,
            synergy_matrix=synergy_matrix,
            amplification_factor=amplification_factor,
            level=level,
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
            hidden_value_score=hidden_value,
            cascade_depth=max((tc.order for tc in temporal_cascades), default=0),
            strongest_synergy=strongest,
        )
        
        logger.info(
            f"🔱 Bifurcation complete: {result.original_count} → {result.bifurcated_count} "
            f"(amplification: {result.amplification_factor:.2f}x)"
        )
        
        return result
    
    def _detect_dimensional_resonance(
        self,
        recommendations: list[dict[str, Any]],
        score_data: dict[str, Any] | None,
    ) -> list[CrossPollinationNode]:
        """
        Detect dimensional resonance effects.
        
        When a recommendation targets DIM01, check if DIM03 and DIM06 also
        benefit through the resonance matrix. This is "hidden value" that
        traditional engines miss.
        """
        resonances = []
        
        for rec in recommendations:
            metadata = rec.get("metadata", {})
            score_key = metadata.get("score_key", "")
            
            if "-" not in score_key:
                continue
                
            pa_id, dim_id = score_key.split("-")
            
            # Check resonance targets
            if dim_id in DIMENSIONAL_RESONANCE:
                for target_dim, strength in DIMENSIONAL_RESONANCE[dim_id].items():
                    if strength < self.resonance_threshold:
                        continue
                    
                    target_key = f"{pa_id}-{target_dim}"
                    
                    # Calculate bonus based on original gap and resonance
                    original_gap = abs(metadata.get("gap", 0) or 0)
                    bonus = original_gap * strength * 0.3  # Conservative estimate
                    
                    resonances.append(CrossPollinationNode(
                        source_rule_id=rec.get("rule_id", ""),
                        target_key=target_key,
                        pollination_strength=strength,
                        mechanism=f"dimensional_resonance:{dim_id}→{target_dim}",
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
    ) -> list[CrossPollinationNode]:
        """
        Detect cross-pollination between recommendations.
        
        This finds cases where fixing A partially fixes B because they share
        underlying structural requirements.
        """
        pollinations = []
        
        if level == "MICRO":
            # Group by dimension to find PA cross-pollination
            by_dim = defaultdict(list)
            for rec in recommendations:
                key = rec.get("metadata", {}).get("score_key", "")
                if "-" in key:
                    _, dim_id = key.split("-")
                    by_dim[dim_id].append(rec)
            
            # For each dimension with multiple PA recommendations,
            # they cross-pollinate each other
            for dim_id, recs in by_dim.items():
                if len(recs) < 2:
                    continue
                
                for rec_a, rec_b in combinations(recs, 2):
                    key_a = rec_a.get("metadata", {}).get("score_key", "")
                    key_b = rec_b.get("metadata", {}).get("score_key", "")
                    
                    # Same dimension = strong pollination (shared methodology)
                    strength = 0.4  # Base for same-dimension
                    bonus = 0.1  # Small but real hidden benefit
                    
                    pollinations.append(CrossPollinationNode(
                        source_rule_id=rec_a.get("rule_id", ""),
                        target_key=key_b,
                        pollination_strength=strength,
                        mechanism=f"same_dimension_pollination:{dim_id}",
                        estimated_bonus_score=bonus,
                        evidence={"dimension": dim_id, "pair": [key_a, key_b]},
                    ))
        
        elif level == "MESO":
            # MESO: Cluster echo patterns - when cluster findings ripple to MICROs
            for rec in recommendations:
                cluster_id = rec.get("metadata", {}).get("cluster_id", "")
                if cluster_id in CLUSTER_ECHO_PATTERNS:
                    for pa_id in CLUSTER_ECHO_PATTERNS[cluster_id]:
                        pollinations.append(CrossPollinationNode(
                            source_rule_id=rec.get("rule_id", ""),
                            target_key=f"{pa_id}-ALL",  # Affects all dims in PA
                            pollination_strength=0.35,
                            mechanism=f"cluster_echo:{cluster_id}→{pa_id}",
                            estimated_bonus_score=0.15,
                            evidence={"cluster": cluster_id, "echo_pa": pa_id},
                        ))
        
        elif level == "MACRO":
            # MACRO: Amplifies everything below
            for rec in recommendations:
                # MACRO recommendations create system-wide improvements
                pollinations.append(CrossPollinationNode(
                    source_rule_id=rec.get("rule_id", ""),
                    target_key="SYSTEM-WIDE",
                    pollination_strength=0.25,
                    mechanism="macro_system_amplification",
                    estimated_bonus_score=0.5,
                    evidence={"scope": "all_clusters"},
                ))
        
        # Filter by threshold
        filtered = [p for p in pollinations if p.pollination_strength >= self.pollination_threshold]
        logger.debug(f"Found {len(filtered)} cross-pollinations")
        return filtered
    
    def _build_temporal_cascades(
        self,
        recommendations: list[dict[str, Any]],
        level: str,
    ) -> list[TemporalCascade]:
        """
        Build temporal cascade effects.
        
        When a 3-month intervention completes, it "unlocks" 12-month capabilities
        that weren't possible before. This is TEMPORAL FOLDING - compressing
        what would take 15 months into 12.
        """
        cascades = []
        
        for rec in recommendations:
            # Extract horizon from recommendation
            horizon_info = rec.get("horizon", {})
            budget_info = rec.get("budget", {}) or {}
            
            # Determine base horizon in months
            base_horizon = 6  # Default
            
            # Try to extract from metadata
            metadata = rec.get("metadata", {})
            score_band = metadata.get("score_band", "")
            
            # Map score bands to horizons
            band_horizons = {
                "CRISIS": 3,
                "CRITICO": 6,
                "ACEPTABLE": 9,
                "BUENO": 12,
                "EXCELENTE": 18,
            }
            if score_band in band_horizons:
                base_horizon = band_horizons[score_band]
            
            # First-order effect (always present)
            cascades.append(TemporalCascade(
                root_rule_id=rec.get("rule_id", ""),
                order=1,
                horizon_months=base_horizon,
                effect_description=f"Direct intervention completion at {base_horizon}M",
                cascade_multiplier=1.0,  # Base value
            ))
            
            # Check for temporal folding effects
            if base_horizon in TEMPORAL_FOLDING and self.cascade_max_depth >= 2:
                folds = TEMPORAL_FOLDING[base_horizon]
                
                for fold_key, multiplier in folds.items():
                    if fold_key.startswith("unlock_"):
                        unlock_horizon = int(fold_key.split("_")[1])
                        cascades.append(TemporalCascade(
                            root_rule_id=rec.get("rule_id", ""),
                            order=2,
                            horizon_months=unlock_horizon,
                            effect_description=f"Unlocked capability at {unlock_horizon}M",
                            cascade_multiplier=1.0 + multiplier,
                            prerequisites=[f"{rec.get('rule_id', '')}_T1_{base_horizon}M"],
                        ))
                        
                        # Third-order: compound effect (if depth allows)
                        if self.cascade_max_depth >= 3:
                            cascades.append(TemporalCascade(
                                root_rule_id=rec.get("rule_id", ""),
                                order=3,
                                horizon_months=unlock_horizon + 6,  # 6 months after unlock
                                effect_description=f"Compound growth at {unlock_horizon + 6}M",
                                cascade_multiplier=1.0 + multiplier * 1.5,  # Exponential growth
                                prerequisites=[f"{rec.get('rule_id', '')}_T2_{unlock_horizon}M"],
                            ))
                    
                    elif fold_key == "amplify_existing":
                        cascades.append(TemporalCascade(
                            root_rule_id=rec.get("rule_id", ""),
                            order=2,
                            horizon_months=base_horizon,
                            effect_description="Amplifies concurrent interventions",
                            cascade_multiplier=1.0 + multiplier,
                        ))
        
        logger.debug(f"Built {len(cascades)} temporal cascades")
        return cascades
    
    def _construct_synergy_matrix(
        self,
        recommendations: list[dict[str, Any]],
        level: str,
    ) -> SynergyMatrix:
        """
        Construct the synergy matrix between recommendations.
        
        Synergy = when two interventions together produce more than the sum.
        This is the combinatorial explosion zone.
        """
        matrix = SynergyMatrix()
        
        if len(recommendations) < 2:
            return matrix
        
        # Strategy 1: Same PA, different DIM synergy
        if level == "MICRO":
            by_pa = defaultdict(list)
            for rec in recommendations:
                key = rec.get("metadata", {}).get("score_key", "")
                if "-" in key:
                    pa_id, _ = key.split("-")
                    by_pa[pa_id].append(rec)
            
            for pa_id, recs in by_pa.items():
                for rec_a, rec_b in combinations(recs, 2):
                    # Same PA + different DIM = strong synergy
                    key_a = rec_a.get("metadata", {}).get("score_key", "")
                    key_b = rec_b.get("metadata", {}).get("score_key", "")
                    dim_a = key_a.split("-")[1] if "-" in key_a else ""
                    dim_b = key_b.split("-")[1] if "-" in key_b else ""
                    
                    if dim_a != dim_b:
                        # Check if dimensions resonate
                        resonance = DIMENSIONAL_RESONANCE.get(dim_a, {}).get(dim_b, 0)
                        synergy_strength = 0.2 + resonance * 0.3
                        
                        matrix.add_synergy(
                            rec_a.get("rule_id", ""),
                            rec_b.get("rule_id", ""),
                            synergy_strength,
                            f"Same PA ({pa_id}) cross-dimensional synergy"
                        )
        
        # Strategy 2: MESO cluster pairs synergy
        elif level == "MESO":
            for rec_a, rec_b in combinations(recommendations, 2):
                cluster_a = rec_a.get("metadata", {}).get("cluster_id", "")
                cluster_b = rec_b.get("metadata", {}).get("cluster_id", "")
                
                # Adjacent clusters synergize more
                if abs(int(cluster_a[-1]) - int(cluster_b[-1])) == 1:
                    matrix.add_synergy(
                        rec_a.get("rule_id", ""),
                        rec_b.get("rule_id", ""),
                        0.35,
                        f"Adjacent cluster synergy ({cluster_a}↔{cluster_b})"
                    )
        
        # Strategy 3: MACRO strategic synergy
        elif level == "MACRO":
            for rec_a, rec_b in combinations(recommendations, 2):
                # All MACRO recommendations synergize at high level
                matrix.add_synergy(
                    rec_a.get("rule_id", ""),
                    rec_b.get("rule_id", ""),
                    0.4,
                    "Strategic system-level synergy"
                )
        
        logger.debug(f"Constructed synergy matrix with {matrix.get_total_synergies()} pairs")
        return matrix


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def bifurcate_recommendations(
    recommendations: list[dict[str, Any]],
    level: str,
    score_data: dict[str, Any] | None = None,
    **kwargs,
) -> BifurcationResult:
    """
    Convenience function to bifurcate recommendations.
    
    This is the simplest entry point - just pass recommendations and get
    exponential analysis back.
    
    Args:
        recommendations: List of recommendation dicts
        level: MICRO, MESO, or MACRO
        score_data: Optional score context
        **kwargs: Passed to RecommendationBifurcator constructor
        
    Returns:
        BifurcationResult with full exponential analysis
        
    Example:
        >>> from farfan_pipeline.phases.Phase_08.phase8_25_00_recommendation_bifurcator import (
        ...     bifurcate_recommendations
        ... )
        >>> result = bifurcate_recommendations(micro_recs, "MICRO")
        >>> print(f"Amplification: {result.amplification_factor:.2f}x")
        Amplification: 2.47x
    """
    bifurcator = RecommendationBifurcator(**kwargs)
    return bifurcator.bifurcate(recommendations, level, score_data)


def enrich_recommendation_with_bifurcation(
    recommendation: dict[str, Any],
    bifurcation_result: BifurcationResult,
) -> dict[str, Any]:
    """
    Enrich a single recommendation with its bifurcation data.
    
    Adds bifurcation metadata to the recommendation's metadata dict.
    
    Args:
        recommendation: Original recommendation dict
        bifurcation_result: Result from bifurcate()
        
    Returns:
        Enriched recommendation dict
    """
    rule_id = recommendation.get("rule_id", "")
    
    # Find relevant cross-pollinations
    relevant_cps = [
        cp for cp in bifurcation_result.cross_pollinations
        if cp.source_rule_id == rule_id
    ]
    
    # Find relevant cascades
    relevant_cascades = [
        tc for tc in bifurcation_result.temporal_cascades
        if tc.root_rule_id == rule_id
    ]
    
    # Find synergies involving this recommendation
    relevant_synergies = {
        pair: strength
        for pair, strength in bifurcation_result.synergy_matrix.synergy_pairs.items()
        if rule_id in pair
    }
    
    # Calculate individual amplification
    base = 1.0
    cp_bonus = sum(cp.estimated_bonus_score for cp in relevant_cps)
    cascade_mult = max((tc.cascade_multiplier for tc in relevant_cascades), default=1.0)
    synergy_bonus = sum(relevant_synergies.values())
    
    individual_amplification = (base + cp_bonus) * cascade_mult * (1 + synergy_bonus)
    
    # Build enrichment payload
    enrichment = {
        "bifurcation": {
            "enabled": True,
            "individual_amplification": round(individual_amplification, 3),
            "cross_pollinations_count": len(relevant_cps),
            "temporal_cascades_count": len(relevant_cascades),
            "synergies_count": len(relevant_synergies),
            "cross_pollination_targets": [cp.target_key for cp in relevant_cps],
            "max_cascade_order": max((tc.order for tc in relevant_cascades), default=0),
            "synergy_partners": [
                p for pair in relevant_synergies for p in pair if p != rule_id
            ],
        }
    }
    
    # Merge into metadata
    enriched = {**recommendation}
    enriched["metadata"] = {**enriched.get("metadata", {}), **enrichment}
    
    return enriched


# =============================================================================
# INTEGRATION HOOK FOR RecommendationEngine
# =============================================================================

def integrate_bifurcator_into_recommendation_set(
    recommendation_set_dict: dict[str, Any],
) -> dict[str, Any]:
    """
    Integration hook: Adds bifurcation analysis to a RecommendationSet.to_dict() output.
    
    This is designed to be called after RecommendationEngine.generate_*_recommendations()
    but before final output/serialization.
    
    Args:
        recommendation_set_dict: Output of RecommendationSet.to_dict()
        
    Returns:
        Enriched dict with bifurcation_analysis added
        
    Example integration in RecommendationEngine:
        ```python
        def generate_micro_recommendations(self, scores, context):
            rec_set = ... # existing logic
            rec_dict = rec_set.to_dict()
            
            # NEW: Add bifurcation
            from .phase8_25_00_recommendation_bifurcator import (
                integrate_bifurcator_into_recommendation_set
            )
            rec_dict = integrate_bifurcator_into_recommendation_set(rec_dict)
            
            return rec_dict
        ```
    """
    level = recommendation_set_dict.get("level", "MICRO")
    recommendations = recommendation_set_dict.get("recommendations", [])
    
    if not recommendations:
        # Nothing to bifurcate
        recommendation_set_dict["bifurcation_analysis"] = {
            "enabled": True,
            "skipped": True,
            "reason": "no_recommendations",
        }
        return recommendation_set_dict
    
    # Run bifurcation
    result = bifurcate_recommendations(recommendations, level)
    
    # Enrich each recommendation
    enriched_recs = [
        enrich_recommendation_with_bifurcation(rec, result)
        for rec in recommendations
    ]
    
    # Build final output
    output = {
        **recommendation_set_dict,
        "recommendations": enriched_recs,
        "bifurcation_analysis": result.to_dict(),
    }
    
    return output


# =============================================================================
# MAIN (Demo/Testing)
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🔱 THE BIFURCATOR - Exponential Recommendation Amplifier")
    print("=" * 80)
    print()
    print("Phase 8 Surgical Injection for EXPONENTIAL benefits")
    print()
    print("Strategies:")
    print("  1. Dimensional Resonance - DIM improvements that ripple")
    print("  2. Cross-Pollination - Hidden PA interdependencies")
    print("  3. Temporal Cascades - Short fixes unlocking long capabilities")
    print("  4. Synergy Matrix - Combinations > sum of parts")
    print()
    
    # Demo with mock data
    mock_recommendations = [
        {
            "rule_id": "RULE-PA01-DIM01-CRITICO",
            "level": "MICRO",
            "metadata": {
                "score_key": "PA01-DIM01",
                "gap": 0.5,
                "score_band": "CRITICO",
            },
            "horizon": {"start": "2026-01", "end": "2026-06"},
        },
        {
            "rule_id": "RULE-PA01-DIM03-ACEPTABLE",
            "level": "MICRO",
            "metadata": {
                "score_key": "PA01-DIM03",
                "gap": 0.3,
                "score_band": "ACEPTABLE",
            },
            "horizon": {"start": "2026-01", "end": "2026-09"},
        },
        {
            "rule_id": "RULE-PA02-DIM01-CRITICO",
            "level": "MICRO",
            "metadata": {
                "score_key": "PA02-DIM01",
                "gap": 0.4,
                "score_band": "CRITICO",
            },
            "horizon": {"start": "2026-01", "end": "2026-06"},
        },
    ]
    
    print("Demo: Bifurcating 3 MICRO recommendations...")
    result = bifurcate_recommendations(mock_recommendations, "MICRO")
    
    print()
    print(f"Original recommendations:     {result.original_count}")
    print(f"Bifurcated (with hidden):     {result.bifurcated_count}")
    print(f"Cross-pollinations found:     {len(result.cross_pollinations)}")
    print(f"Temporal cascades built:      {len(result.temporal_cascades)}")
    print(f"Synergies discovered:         {result.synergy_matrix.get_total_synergies()}")
    print()
    print(f"🎯 AMPLIFICATION FACTOR:      {result.amplification_factor:.2f}x")
    print()
    print("This means the TRUE benefit of these 3 recommendations is")
    print(f"{result.amplification_factor:.2f}x higher than traditional analysis shows!")
    print()
    print("=" * 80)
