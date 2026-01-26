"""
Capacity Aggregation Module
===========================

This module implements the capacity aggregation functions for the
Wu, Ramesh & Howlett (2015) Policy Capacity Framework.

Mathematical Model:
------------------

Formula 2: Aggregation Weight
    W_agg(i, j) = η × exp(-λ × Δ_level(i, j))
    
    Where:
    - Δ_level = level distance (Individual→Org = 1, Org→Systemic = 1)
    - η = 1.0 (base weight)
    - λ = 0.2 (decay parameter)

Formula 3: Individual to Organizational Aggregation
    C_org = (Σ C_ind_i^p)^(1/p) × κ_org
    
    Parameters:
    - p = 1.2 (power parameter for power mean)
    - κ_org = 0.85 (organizational capacity factor)

Formula 4: Organizational to Systemic Aggregation
    C_sys = √(C_org_mean × C_org_max) × κ_sys
    
    Parameters:
    - κ_sys = 0.90 (systemic capacity factor)

Transformation Matrix:
    Cross-level influence coefficients representing how capacities
    at different levels contribute to each other:
    
                 Individual  Organizational  Systemic
    Individual      1.00          0.75        0.50
    Organizational  0.25          1.00        0.80
    Systemic        0.10          0.35        1.00

Author: F.A.R.F.A.N. Core Team
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Any,
)

import numpy as np
from numpy.typing import NDArray

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    CapacityScore,
    MethodCapacityMapping,
    AggregatedCapacity,
)


# ============================================================================
# TRANSFORMATION MATRIX
# ============================================================================

@dataclass
class TransformationMatrix:
    """
    Cross-level influence coefficients matrix.
    
    This matrix represents how capacities at different levels
    contribute to and influence each other. The structure reflects
    the theoretical understanding that:
    
    - Individual capacities fully contribute to their own level (1.0)
    - Individual capacities partially contribute upward (0.75 to Org, 0.50 to Sys)
    - Higher levels have spillover effects downward (diminished)
    - Organizational level has strongest cross-level influence to Systemic (0.80)
    
    Matrix interpretation (row = source, column = target):
        T[i][j] = contribution weight from level i to level j
    
    Mathematical Properties:
    - Diagonal elements = 1.0 (full self-contribution)
    - Upper triangular > Lower triangular (upward aggregation stronger)
    - Row sums measure total influence capacity of a level
    - Column sums measure total dependence of a level
    """
    
    # Default matrix values
    # Row: Individual, Column: [Individual, Organizational, Systemic]
    individual_to_individual: float = 1.00
    individual_to_organizational: float = 0.75
    individual_to_systemic: float = 0.50
    
    # Row: Organizational
    organizational_to_individual: float = 0.25
    organizational_to_organizational: float = 1.00
    organizational_to_systemic: float = 0.80
    
    # Row: Systemic
    systemic_to_individual: float = 0.10
    systemic_to_organizational: float = 0.35
    systemic_to_systemic: float = 1.00
    
    def as_numpy(self) -> NDArray[np.float64]:
        """Return matrix as numpy array."""
        return np.array([
            [self.individual_to_individual, self.individual_to_organizational, self.individual_to_systemic],
            [self.organizational_to_individual, self.organizational_to_organizational, self.organizational_to_systemic],
            [self.systemic_to_individual, self.systemic_to_organizational, self.systemic_to_systemic],
        ], dtype=np.float64)
    
    def get_coefficient(self, source: PolicyLevel, target: PolicyLevel) -> float:
        """Get transformation coefficient between two levels."""
        matrix = self.as_numpy()
        source_idx = source.aggregation_order
        target_idx = target.aggregation_order
        return float(matrix[source_idx, target_idx])
    
    def get_aggregation_weights(self, target: PolicyLevel) -> Dict[PolicyLevel, float]:
        """
        Get weights for aggregating TO a target level.
        
        Returns weights from all source levels contributing to target.
        """
        return {
            source: self.get_coefficient(source, target)
            for source in PolicyLevel.all_levels()
        }
    
    def get_influence_weights(self, source: PolicyLevel) -> Dict[PolicyLevel, float]:
        """
        Get weights for influence FROM a source level.
        
        Returns how much source level influences each target level.
        """
        return {
            target: self.get_coefficient(source, target)
            for target in PolicyLevel.all_levels()
        }
    
    @property
    def eigenvalues(self) -> NDArray[np.float64]:
        """
        Compute eigenvalues of transformation matrix.
        
        Eigenvalues > 1 indicate amplifying dynamics.
        Dominant eigenvalue indicates overall capacity growth potential.
        """
        return np.linalg.eigvals(self.as_numpy())
    
    @property
    def is_stable(self) -> bool:
        """
        Check if transformation matrix produces stable dynamics.
        
        Matrix is stable if all eigenvalues have magnitude ≤ 1.
        """
        return all(abs(ev) <= 1.0 + 1e-9 for ev in self.eigenvalues)
    
    @classmethod
    def default(cls) -> "TransformationMatrix":
        """Create default transformation matrix."""
        return cls()
    
    @classmethod
    def high_upward_influence(cls) -> "TransformationMatrix":
        """Matrix emphasizing upward capacity accumulation."""
        return cls(
            individual_to_organizational=0.85,
            individual_to_systemic=0.65,
            organizational_to_systemic=0.90,
        )
    
    @classmethod
    def balanced(cls) -> "TransformationMatrix":
        """Matrix with more balanced cross-level influence."""
        return cls(
            individual_to_organizational=0.60,
            individual_to_systemic=0.40,
            organizational_to_individual=0.40,
            organizational_to_systemic=0.60,
            systemic_to_individual=0.20,
            systemic_to_organizational=0.50,
        )


# ============================================================================
# AGGREGATION CONFIG
# ============================================================================

@dataclass
class AggregationConfig:
    """
    Configuration for capacity aggregation calculations.
    
    This encapsulates all parameters for the aggregation formulas.
    """
    
    # Formula 2: Aggregation Weight parameters
    eta: float = 0.85          # Base weight (η)
    lambda_decay: float = 0.15  # Decay parameter (λ)
    
    # Formula 3: Individual→Organizational parameters
    power_mean_p: float = 1.2   # Power parameter (p)
    kappa_org: float = 0.85     # Organizational capacity factor (κ_org)
    
    # Formula 4: Organizational→Systemic parameters
    kappa_sys: float = 0.90     # Systemic capacity factor (κ_sys)
    
    # Equipment congregation sensitivity
    congregation_delta: float = 0.3  # Congregation sensitivity (δ)
    
    # Transformation matrix
    transformation_matrix: TransformationMatrix = field(default_factory=TransformationMatrix.default)
    
    # Level weights for weighted aggregation
    level_weights: Dict[PolicyLevel, float] = field(default_factory=lambda: {
        PolicyLevel.INDIVIDUAL: 0.25,
        PolicyLevel.ORGANIZATIONAL: 0.35,
        PolicyLevel.SYSTEMIC: 0.40,
    })
    
    # Skill weights for weighted aggregation
    skill_weights: Dict[PolicySkill, float] = field(default_factory=lambda: {
        PolicySkill.ANALYTICAL: 0.40,
        PolicySkill.OPERATIONAL: 0.35,
        PolicySkill.POLITICAL: 0.25,
    })
    
    def __post_init__(self):
        # Validate level weights sum to 1.0
        level_sum = sum(self.level_weights.values())
        if not math.isclose(level_sum, 1.0, rel_tol=1e-9):
            raise ValueError(f"Level weights must sum to 1.0, got {level_sum}")
        
        # Validate skill weights sum to 1.0
        skill_sum = sum(self.skill_weights.values())
        if not math.isclose(skill_sum, 1.0, rel_tol=1e-9):
            raise ValueError(f"Skill weights must sum to 1.0, got {skill_sum}")
    
    @classmethod
    def default(cls) -> "AggregationConfig":
        """Create default configuration."""
        return cls()
    
    @classmethod
    def high_synergy(cls) -> "AggregationConfig":
        """Configuration with enhanced synergy effects."""
        return cls(
            congregation_delta=0.5,
            kappa_org=0.90,
            kappa_sys=0.95,
        )


# ============================================================================
# AGGREGATION RESULT
# ============================================================================

@dataclass
class LevelAggregationResult:
    """
    Result of aggregating capacity to a specific level.
    """
    
    target_level: PolicyLevel
    skill: PolicySkill
    
    # Source contributions
    source_scores: Dict[PolicyLevel, float]
    transformation_weights: Dict[PolicyLevel, float]
    
    # Aggregation computations
    power_mean_value: Optional[float]
    geometric_mean_value: Optional[float]
    
    # Final results
    raw_aggregated_score: float
    capacity_factor_applied: float
    final_score: float
    
    # Provenance
    aggregation_method: str
    formula_parameters: Dict[str, float]
    
    @property
    def capacity_type(self) -> CapacityType:
        """Get the capacity type for this result."""
        return CapacityType.from_skill_level(self.skill, self.target_level)
    
    def to_aggregated_capacity(self) -> AggregatedCapacity:
        """Convert to AggregatedCapacity structure."""
        source_capacity_scores = [
            CapacityScore(
                capacity_type=CapacityType.from_skill_level(self.skill, level),
                raw_score=score,
                weighted_score=score * self.transformation_weights.get(level, 1.0),
                confidence=0.8,  # Default confidence for aggregated
                method_count=0,  # Unknown at aggregate level
            )
            for level, score in self.source_scores.items()
            if score > 0
        ]
        
        return AggregatedCapacity(
            level=self.target_level,
            skill=self.skill,
            source_scores=source_capacity_scores,
            aggregated_score=self.final_score,
            aggregation_method=self.aggregation_method,
            equipment_multiplier=1.0,
            cross_level_contribution=sum(
                score * self.transformation_weights.get(level, 0)
                for level, score in self.source_scores.items()
                if level != self.target_level
            ),
        )


# ============================================================================
# CAPACITY AGGREGATOR
# ============================================================================

class CapacityAggregator:
    """
    Aggregator for policy capacities across levels.
    
    Implements the three aggregation formulas from the Wu Framework:
    
    1. Aggregation Weight: W_agg = η × exp(-λ × Δ_level)
    2. Individual→Organizational: C_org = (Σ C_ind^p)^(1/p) × κ_org
    3. Organizational→Systemic: C_sys = √(C_org_mean × C_org_max) × κ_sys
    
    The aggregator supports:
    - Single skill aggregation (e.g., aggregate all Analytical capacities)
    - Cross-level aggregation (e.g., Individual → Organizational)
    - Full matrix aggregation (all skills × all levels)
    - Equipment congregation multipliers (synergy effects)
    
    Usage:
        aggregator = CapacityAggregator()
        
        # Aggregate single skill
        result = aggregator.aggregate_skill_to_level(
            skill=PolicySkill.ANALYTICAL,
            source_scores={
                PolicyLevel.INDIVIDUAL: 1.068,
                PolicyLevel.ORGANIZATIONAL: 1.338,
            },
            target_level=PolicyLevel.SYSTEMIC
        )
        
        # Aggregate all capacities
        full_results = aggregator.aggregate_all(capacity_scores)
    """
    
    def __init__(self, config: Optional[AggregationConfig] = None):
        """
        Initialize aggregator with configuration.
        
        Args:
            config: Aggregation configuration. Uses default if not provided.
        """
        self.config = config or AggregationConfig.default()
    
    # -------------------------------------------------------------------------
    # Formula 2: Aggregation Weight
    # -------------------------------------------------------------------------
    
    def calculate_aggregation_weight(
        self,
        source_level: PolicyLevel,
        target_level: PolicyLevel,
    ) -> float:
        """
        Calculate aggregation weight between two levels.
        
        Formula: W_agg = η × exp(-λ × Δ_level)
        
        Args:
            source_level: Source level being aggregated from
            target_level: Target level being aggregated to
            
        Returns:
            Aggregation weight in (0, η]
        """
        delta_level = source_level.distance_to(target_level)
        weight = self.config.eta * math.exp(-self.config.lambda_decay * delta_level)
        return weight
    
    def get_all_aggregation_weights(
        self,
        target_level: PolicyLevel,
    ) -> Dict[PolicyLevel, float]:
        """
        Get aggregation weights from all levels to a target level.
        
        Args:
            target_level: Target level for aggregation
            
        Returns:
            Dictionary mapping source levels to their weights
        """
        return {
            source: self.calculate_aggregation_weight(source, target_level)
            for source in PolicyLevel.all_levels()
        }
    
    # -------------------------------------------------------------------------
    # Formula 3: Individual → Organizational
    # -------------------------------------------------------------------------
    
    def aggregate_individual_to_organizational(
        self,
        individual_scores: List[float],
    ) -> float:
        """
        Aggregate individual capacity scores to organizational level.
        
        Formula: C_org = (Σ C_ind_i^p)^(1/p) × κ_org
        
        This uses a generalized power mean (p-norm) which:
        - For p=1: Arithmetic mean (treats all equally)
        - For p=2: Root mean square (emphasizes larger values)
        - For p=1.2: Slight emphasis on larger values
        
        Args:
            individual_scores: List of individual capacity scores
            
        Returns:
            Aggregated organizational capacity score
        """
        if not individual_scores:
            return 0.0
        
        p = self.config.power_mean_p
        kappa = self.config.kappa_org
        
        # Power mean: (Σ x_i^p / n)^(1/p)
        n = len(individual_scores)
        power_sum = sum(x ** p for x in individual_scores if x > 0)
        
        if power_sum == 0:
            return 0.0
        
        power_mean = (power_sum / n) ** (1 / p)
        return power_mean * kappa
    
    # -------------------------------------------------------------------------
    # Formula 4: Organizational → Systemic
    # -------------------------------------------------------------------------
    
    def aggregate_organizational_to_systemic(
        self,
        organizational_scores: List[float],
    ) -> float:
        """
        Aggregate organizational capacity scores to systemic level.
        
        Formula: C_sys = √(C_org_mean × C_org_max) × κ_sys
        
        This uses geometric mean of the arithmetic mean and maximum,
        which balances:
        - Average capacity (mean): Overall organizational strength
        - Peak capacity (max): Best-in-class organizational capacity
        
        The geometric mean ensures both factors must be high
        for systemic capacity to be high.
        
        Args:
            organizational_scores: List of organizational capacity scores
            
        Returns:
            Aggregated systemic capacity score
        """
        if not organizational_scores:
            return 0.0
        
        kappa = self.config.kappa_sys
        
        # Calculate mean and max
        org_mean = sum(organizational_scores) / len(organizational_scores)
        org_max = max(organizational_scores)
        
        if org_mean <= 0 or org_max <= 0:
            return 0.0
        
        # Geometric mean of mean and max
        geometric_mean = math.sqrt(org_mean * org_max)
        return geometric_mean * kappa
    
    # -------------------------------------------------------------------------
    # Combined Aggregation with Transformation Matrix
    # -------------------------------------------------------------------------
    
    def aggregate_skill_to_level(
        self,
        skill: PolicySkill,
        source_scores: Dict[PolicyLevel, float],
        target_level: PolicyLevel,
    ) -> LevelAggregationResult:
        """
        Aggregate a skill's scores to a specific level.
        
        This combines:
        1. Direct aggregation formulas (power mean, geometric mean)
        2. Cross-level transformation matrix contributions
        3. Aggregation weights based on level distance
        
        Args:
            skill: The skill being aggregated
            source_scores: Scores at each level for this skill
            target_level: Level to aggregate to
            
        Returns:
            Complete aggregation result with provenance
        """
        transformation_weights = self.config.transformation_matrix.get_aggregation_weights(target_level)
        
        # Determine aggregation method based on target level
        if target_level == PolicyLevel.INDIVIDUAL:
            # Individual level: direct score (no aggregation upward possible)
            raw_score = source_scores.get(PolicyLevel.INDIVIDUAL, 0.0)
            aggregation_method = "direct"
            power_mean_value = None
            geometric_mean_value = None
            capacity_factor = 1.0
            
        elif target_level == PolicyLevel.ORGANIZATIONAL:
            # Organizational: power mean of individual scores
            individual_score = source_scores.get(PolicyLevel.INDIVIDUAL, 0.0)
            scores_list = [individual_score] if individual_score > 0 else []
            
            # Also include own level contribution
            org_score = source_scores.get(PolicyLevel.ORGANIZATIONAL, 0.0)
            if org_score > 0:
                scores_list.append(org_score)
            
            if scores_list:
                power_mean_value = self.aggregate_individual_to_organizational(scores_list)
                raw_score = power_mean_value
            else:
                power_mean_value = 0.0
                raw_score = 0.0
            
            aggregation_method = "power_mean"
            geometric_mean_value = None
            capacity_factor = self.config.kappa_org
            
        else:  # Systemic
            # Systemic: geometric mean aggregation
            org_score = source_scores.get(PolicyLevel.ORGANIZATIONAL, 0.0)
            ind_score = source_scores.get(PolicyLevel.INDIVIDUAL, 0.0)
            
            # First aggregate to organizational if needed
            if org_score == 0 and ind_score > 0:
                org_score = self.aggregate_individual_to_organizational([ind_score])
            
            # Include existing systemic score
            sys_score = source_scores.get(PolicyLevel.SYSTEMIC, 0.0)
            
            scores_list = [s for s in [org_score, sys_score] if s > 0]
            
            if scores_list:
                geometric_mean_value = self.aggregate_organizational_to_systemic(scores_list)
                raw_score = geometric_mean_value
            else:
                geometric_mean_value = 0.0
                raw_score = 0.0
            
            aggregation_method = "geometric_mean"
            power_mean_value = None
            capacity_factor = self.config.kappa_sys
        
        # Apply transformation matrix cross-level contributions
        cross_contribution = sum(
            source_scores.get(level, 0.0) * transformation_weights.get(level, 0.0)
            for level in PolicyLevel.all_levels()
            if level != target_level
        )
        
        # Blend raw score with cross-level contributions
        # 80% from direct aggregation, 20% from transformation matrix
        final_score = 0.8 * raw_score + 0.2 * cross_contribution
        
        return LevelAggregationResult(
            target_level=target_level,
            skill=skill,
            source_scores=source_scores,
            transformation_weights=transformation_weights,
            power_mean_value=power_mean_value,
            geometric_mean_value=geometric_mean_value,
            raw_aggregated_score=raw_score,
            capacity_factor_applied=capacity_factor,
            final_score=round(final_score, 4),
            aggregation_method=aggregation_method,
            formula_parameters={
                "eta": self.config.eta,
                "lambda_decay": self.config.lambda_decay,
                "power_mean_p": self.config.power_mean_p,
                "kappa_org": self.config.kappa_org,
                "kappa_sys": self.config.kappa_sys,
            },
        )
    
    def aggregate_all_for_skill(
        self,
        skill: PolicySkill,
        source_scores: Dict[PolicyLevel, float],
    ) -> Dict[PolicyLevel, LevelAggregationResult]:
        """
        Aggregate all levels for a single skill.
        
        Args:
            skill: The skill to aggregate
            source_scores: Scores at each level
            
        Returns:
            Dictionary mapping each level to its aggregation result
        """
        return {
            level: self.aggregate_skill_to_level(skill, source_scores, level)
            for level in PolicyLevel.all_levels()
        }
    
    def aggregate_all(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
    ) -> Dict[CapacityType, LevelAggregationResult]:
        """
        Perform complete aggregation for all capacity types.
        
        Args:
            capacity_scores: All raw capacity scores
            
        Returns:
            Dictionary mapping each capacity type to its aggregation result
        """
        results = {}
        
        for skill in PolicySkill.all_skills():
            # Extract scores for this skill
            skill_scores = {
                ct.level: capacity_scores[ct].raw_score
                for ct in CapacityType.by_skill(skill)
                if ct in capacity_scores
            }
            
            # Aggregate to each level
            for level in PolicyLevel.all_levels():
                result = self.aggregate_skill_to_level(skill, skill_scores, level)
                results[result.capacity_type] = result
        
        return results
    
    # -------------------------------------------------------------------------
    # Aggregation by Skill and Level
    # -------------------------------------------------------------------------
    
    def aggregate_by_skill(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
    ) -> Dict[PolicySkill, float]:
        """
        Aggregate capacity scores by skill (across all levels).
        
        Uses weighted average with level weights.
        
        Args:
            capacity_scores: All capacity scores
            
        Returns:
            Dictionary mapping each skill to its aggregate score
        """
        results = {}
        
        for skill in PolicySkill.all_skills():
            skill_types = CapacityType.by_skill(skill)
            
            weighted_sum = 0.0
            weight_sum = 0.0
            
            for ct in skill_types:
                if ct in capacity_scores:
                    level_weight = self.config.level_weights[ct.level]
                    score = capacity_scores[ct].raw_score
                    weighted_sum += score * level_weight
                    weight_sum += level_weight
            
            results[skill] = round(weighted_sum / weight_sum, 4) if weight_sum > 0 else 0.0
        
        return results
    
    def aggregate_by_level(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
    ) -> Dict[PolicyLevel, float]:
        """
        Aggregate capacity scores by level (across all skills).
        
        Uses weighted average with skill weights.
        
        Args:
            capacity_scores: All capacity scores
            
        Returns:
            Dictionary mapping each level to its aggregate score
        """
        results = {}
        
        for level in PolicyLevel.all_levels():
            level_types = CapacityType.by_level(level)
            
            weighted_sum = 0.0
            weight_sum = 0.0
            
            for ct in level_types:
                if ct in capacity_scores:
                    skill_weight = self.config.skill_weights[ct.skill]
                    score = capacity_scores[ct].raw_score
                    weighted_sum += score * skill_weight
                    weight_sum += skill_weight
            
            results[level] = round(weighted_sum / weight_sum, 4) if weight_sum > 0 else 0.0
        
        return results
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def compute_cross_level_matrix(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
    ) -> NDArray[np.float64]:
        """
        Compute the full 3x3 cross-level contribution matrix.
        
        Each cell [i,j] represents the contribution from level i to level j.
        
        Args:
            capacity_scores: All capacity scores
            
        Returns:
            3x3 numpy array of cross-level contributions
        """
        # Aggregate by level first
        level_scores = self.aggregate_by_level(capacity_scores)
        
        # Compute contributions
        contributions = np.zeros((3, 3), dtype=np.float64)
        levels = PolicyLevel.all_levels()
        
        for i, source_level in enumerate(levels):
            for j, target_level in enumerate(levels):
                source_score = level_scores.get(source_level, 0.0)
                weight = self.config.transformation_matrix.get_coefficient(source_level, target_level)
                contributions[i, j] = source_score * weight
        
        return contributions
    
    def get_aggregation_provenance(
        self,
        results: Dict[CapacityType, LevelAggregationResult],
    ) -> Dict[str, Any]:
        """
        Generate provenance information for aggregation results.
        
        Args:
            results: Aggregation results
            
        Returns:
            Dictionary with full provenance information
        """
        return {
            "config": {
                "eta": self.config.eta,
                "lambda_decay": self.config.lambda_decay,
                "power_mean_p": self.config.power_mean_p,
                "kappa_org": self.config.kappa_org,
                "kappa_sys": self.config.kappa_sys,
                "congregation_delta": self.config.congregation_delta,
            },
            "transformation_matrix": self.config.transformation_matrix.as_numpy().tolist(),
            "results": {
                ct.code: {
                    "final_score": result.final_score,
                    "aggregation_method": result.aggregation_method,
                    "source_scores": {l.value: s for l, s in result.source_scores.items()},
                }
                for ct, result in results.items()
            },
        }


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "CapacityAggregator",
    "AggregationConfig",
    "TransformationMatrix",
    "LevelAggregationResult",
]
