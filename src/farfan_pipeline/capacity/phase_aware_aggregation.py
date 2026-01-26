"""
Phase-Aware Capacity Aggregation Module
=======================================

This module extends the base capacity aggregation with phase-aware functionality,
enabling aggregation strategies that adapt based on the current canonical phase.

ARCHITECTURAL ENHANCEMENTS:
--------------------------
1. **Phase-Sensitive Aggregation**: Different aggregation parameters per phase
2. **Cross-Phase Aggregation**: Aggregate capacity across phase boundaries
3. **Phase Transition Smoothing**: Smooth discontinuities at phase transitions
4. **Phase-Specific Weights**: Adjust transformation matrices per phase

Mathematical Extensions:
-----------------------
Formula 10: Phase-Aware Power Mean
    C_phase_org(p) = [(Σ C_ind^p(phase))^(1/p)] × κ_org(p) × ψ_phase(p)
    
    Where ψ_phase(p) = phase-specific organizational factor

Formula 11: Cross-Phase Aggregation
    C_cross(p1, p2) = √[C(p1) × C(p2)] × ρ_transition(p1, p2)
    
    Aggregates capacity across phase boundaries

Formula 12: Phase Transition Smoothing
    C_smooth(p) = α×C(p) + (1-α)×C(p-1) with α = sigmoid(coherence)
    
    Smooths discontinuities between phases

Integration with Base Aggregation:
----------------------------------
This module EXTENDS (not replaces) farfan_pipeline.capacity.aggregation.
The base aggregation provides capacity-type aggregation; this module adds
phase-aware orchestration on top.

Author: F.A.R.F.A.N. Core Team (PythonGod Trinity Enhanced)
Version: 2.0.0
Date: 2026-01-26
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from numpy.typing import NDArray

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    CapacityScore,
    AggregatedCapacity,
)

from farfan_pipeline.capacity.aggregation import (
    CapacityAggregator,
    AggregationConfig,
    TransformationMatrix,
    LevelAggregationResult,
)

from farfan_pipeline.capacity.phase_integration import (
    CanonicalPhase,
    PhaseCapacityScore,
    PhaseCapacityMapping,
    CapacityFlowMetrics,
)


# ============================================================================
# PHASE-SPECIFIC AGGREGATION CONFIGURATION
# ============================================================================

@dataclass
class PhaseAggregationConfig:
    """
    Configuration for phase-aware aggregation.
    
    This extends the base AggregationConfig with phase-specific parameters
    that allow aggregation strategies to adapt based on pipeline phase.
    """
    
    # Base configuration
    base_config: AggregationConfig
    
    # Phase-specific organizational factors (Formula 10)
    # Maps phase index to organizational capacity factor
    phase_kappa_org: Dict[int, float] = field(default_factory=lambda: {
        0: 0.80,  # PHASE_00: Infrastructure - lower org factor
        1: 0.82,
        2: 0.85,
        3: 0.87,  # PHASE_03: Micro scoring - standard
        4: 0.85,  # PHASE_04: Meso aggregation - standard
        5: 0.88,
        6: 0.90,
        7: 0.92,  # PHASE_07: Macro aggregation - higher org factor
        8: 0.90,
        9: 0.88,  # PHASE_09: Output - slightly reduced
    })
    
    # Phase-specific systemic factors
    phase_kappa_sys: Dict[int, float] = field(default_factory=lambda: {
        0: 0.85,
        1: 0.87,
        2: 0.88,
        3: 0.89,
        4: 0.90,
        5: 0.91,
        6: 0.93,
        7: 0.95,  # Peak systemic capacity at macro aggregation
        8: 0.93,
        9: 0.90,
    })
    
    # Cross-phase transition factors (Formula 11)
    # How well capacity transfers between phases
    transition_factors: Dict[Tuple[int, int], float] = field(default_factory=dict)
    
    # Transition smoothing alpha (Formula 12)
    # Higher = rely more on current phase, lower = smoother transition
    smoothing_sensitivity: float = 0.7
    
    def get_kappa_org(self, phase: CanonicalPhase) -> float:
        """Get organizational factor for a phase."""
        return self.phase_kappa_org.get(phase.index, self.base_config.kappa_org)
    
    def get_kappa_sys(self, phase: CanonicalPhase) -> float:
        """Get systemic factor for a phase."""
        return self.phase_kappa_sys.get(phase.index, self.base_config.kappa_sys)
    
    def get_transition_factor(
        self,
        source_phase: CanonicalPhase,
        target_phase: CanonicalPhase,
    ) -> float:
        """
        Get transition factor between two phases.
        
        Higher values indicate better capacity transfer.
        Default is 0.95 for adjacent phases, lower for distant phases.
        """
        key = (source_phase.index, target_phase.index)
        if key in self.transition_factors:
            return self.transition_factors[key]
        
        # Default: exponential decay based on phase distance
        distance = abs(target_phase.index - source_phase.index)
        return 0.95 * math.exp(-0.1 * (distance - 1)) if distance > 0 else 1.0


# ============================================================================
# PHASE-AWARE AGGREGATION RESULT
# ============================================================================

@dataclass
class PhaseAwareAggregationResult:
    """
    Result of phase-aware capacity aggregation.
    
    Extends base aggregation result with phase-specific information.
    """
    
    phase: CanonicalPhase
    capacity_type: CapacityType
    
    # Base aggregation result
    base_result: LevelAggregationResult
    
    # Phase-adjusted scores (Formula 10)
    phase_adjusted_org_score: float
    phase_adjusted_sys_score: float
    
    # Phase factors applied
    kappa_org_used: float
    kappa_sys_used: float
    phase_org_factor: float  # ψ_phase(p) from Formula 10
    
    # Smoothing information (if applicable)
    was_smoothed: bool = False
    smoothing_alpha: Optional[float] = None
    previous_phase_contribution: Optional[float] = None
    
    # Cross-phase aggregation (if applicable)
    cross_phase_aggregated: bool = False
    cross_phase_partner: Optional[CanonicalPhase] = None
    transition_factor_used: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "phase": self.phase.code,
            "capacity_type": self.capacity_type.code,
            "base_final_score": self.base_result.final_score,
            "phase_adjusted_org_score": self.phase_adjusted_org_score,
            "phase_adjusted_sys_score": self.phase_adjusted_sys_score,
            "kappa_org_used": self.kappa_org_used,
            "kappa_sys_used": self.kappa_sys_used,
            "phase_org_factor": self.phase_org_factor,
            "was_smoothed": self.was_smoothed,
            "smoothing_alpha": self.smoothing_alpha,
            "cross_phase_aggregated": self.cross_phase_aggregated,
        }


# ============================================================================
# PHASE-AWARE CAPACITY AGGREGATOR
# ============================================================================

class PhaseAwareCapacityAggregator:
    """
    Phase-aware capacity aggregator that extends base aggregation with
    phase-specific strategies.
    
    This class implements the Trinity pattern:
    - METACLASS: Defines aggregation invariants across all phases
    - CLASS: Contains phase-specific aggregation strategies
    - INSTANCE: Executes actual aggregation for specific phases
    """
    
    def __init__(
        self,
        config: Optional[PhaseAggregationConfig] = None,
    ):
        """
        Initialize phase-aware aggregator.
        
        Args:
            config: Phase aggregation configuration, or None for defaults
        """
        if config is None:
            config = PhaseAggregationConfig(
                base_config=AggregationConfig()
            )
        
        self.config = config
        self.base_aggregator = CapacityAggregator(config.base_config)
    
    def aggregate_phase_capacity(
        self,
        phase: CanonicalPhase,
        phase_scores: List[PhaseCapacityScore],
        previous_phase_results: Optional[List[PhaseAwareAggregationResult]] = None,
    ) -> List[PhaseAwareAggregationResult]:
        """
        Aggregate capacity scores with phase-aware adjustments.
        
        Implements Formula 10 for phase-aware power mean aggregation.
        
        Args:
            phase: Current canonical phase
            phase_scores: Phase-aware capacity scores to aggregate
            previous_phase_results: Results from previous phase for smoothing
            
        Returns:
            List of phase-aware aggregation results
        """
        # Group scores by capacity type
        scores_by_type: Dict[CapacityType, List[PhaseCapacityScore]] = {}
        for score in phase_scores:
            if score.capacity_type not in scores_by_type:
                scores_by_type[score.capacity_type] = []
            scores_by_type[score.capacity_type].append(score)
        
        # Perform phase-aware aggregation for each capacity type
        results = []
        for capacity_type, type_scores in scores_by_type.items():
            result = self._aggregate_single_capacity_type(
                phase=phase,
                capacity_type=capacity_type,
                phase_scores=type_scores,
                previous_phase_results=previous_phase_results,
            )
            results.append(result)
        
        return results
    
    def _aggregate_single_capacity_type(
        self,
        phase: CanonicalPhase,
        capacity_type: CapacityType,
        phase_scores: List[PhaseCapacityScore],
        previous_phase_results: Optional[List[PhaseAwareAggregationResult]],
    ) -> PhaseAwareAggregationResult:
        """
        Aggregate a single capacity type with phase awareness.
        
        Applies Formula 10 with phase-specific factors.
        """
        # Convert phase scores to base scores for aggregation
        base_scores = [ps.base_score for ps in phase_scores]
        
        # Use base aggregator to get standard aggregation
        base_results = self.base_aggregator.aggregate_by_capacity_type(base_scores)
        base_result = base_results.get(capacity_type)
        
        if base_result is None:
            raise ValueError(f"No aggregation result for capacity type: {capacity_type}")
        
        # Apply phase-specific adjustments (Formula 10)
        kappa_org = self.config.get_kappa_org(phase)
        kappa_sys = self.config.get_kappa_sys(phase)
        
        # Calculate phase organizational factor ψ_phase(p)
        # This increases with phase index (later phases have better organization)
        phase_org_factor = 1.0 + (0.15 * (phase.index / 9.0))
        
        # Apply Formula 10 adjustments
        org_score_base = base_result.organizational_score
        sys_score_base = base_result.systemic_score
        
        phase_adjusted_org = org_score_base * (kappa_org / self.config.base_config.kappa_org) * phase_org_factor
        phase_adjusted_sys = sys_score_base * (kappa_sys / self.config.base_config.kappa_sys)
        
        # Apply transition smoothing if previous results available (Formula 12)
        was_smoothed = False
        smoothing_alpha = None
        previous_contribution = None
        
        if previous_phase_results:
            # Find matching previous result
            prev_result = next(
                (r for r in previous_phase_results if r.capacity_type == capacity_type),
                None
            )
            
            if prev_result:
                # Calculate coherence-based smoothing
                # Use flow coherence if available from phase transition
                coherence = self._estimate_coherence(phase_scores)
                smoothing_alpha = self._calculate_smoothing_alpha(coherence)
                
                # Apply Formula 12: weighted blend of current and previous
                phase_adjusted_org = (
                    smoothing_alpha * phase_adjusted_org +
                    (1 - smoothing_alpha) * prev_result.phase_adjusted_org_score
                )
                phase_adjusted_sys = (
                    smoothing_alpha * phase_adjusted_sys +
                    (1 - smoothing_alpha) * prev_result.phase_adjusted_sys_score
                )
                
                was_smoothed = True
                previous_contribution = 1 - smoothing_alpha
        
        return PhaseAwareAggregationResult(
            phase=phase,
            capacity_type=capacity_type,
            base_result=base_result,
            phase_adjusted_org_score=phase_adjusted_org,
            phase_adjusted_sys_score=phase_adjusted_sys,
            kappa_org_used=kappa_org,
            kappa_sys_used=kappa_sys,
            phase_org_factor=phase_org_factor,
            was_smoothed=was_smoothed,
            smoothing_alpha=smoothing_alpha,
            previous_phase_contribution=previous_contribution,
        )
    
    def aggregate_cross_phase(
        self,
        source_phase: CanonicalPhase,
        target_phase: CanonicalPhase,
        source_results: List[PhaseAwareAggregationResult],
        target_results: List[PhaseAwareAggregationResult],
    ) -> List[PhaseAwareAggregationResult]:
        """
        Aggregate capacity across phase boundaries.
        
        Implements Formula 11 for cross-phase aggregation.
        
        Args:
            source_phase: Source phase
            target_phase: Target phase
            source_results: Aggregation results from source phase
            target_results: Aggregation results from target phase
            
        Returns:
            Updated target results with cross-phase aggregation applied
        """
        transition_factor = self.config.get_transition_factor(source_phase, target_phase)
        
        # Build lookup for source results
        source_by_type = {r.capacity_type: r for r in source_results}
        
        # Apply cross-phase aggregation to target results
        updated_results = []
        for target_result in target_results:
            source_result = source_by_type.get(target_result.capacity_type)
            
            if source_result:
                # Apply Formula 11: geometric mean with transition factor
                cross_org = math.sqrt(
                    source_result.phase_adjusted_org_score *
                    target_result.phase_adjusted_org_score
                ) * transition_factor
                
                cross_sys = math.sqrt(
                    source_result.phase_adjusted_sys_score *
                    target_result.phase_adjusted_sys_score
                ) * transition_factor
                
                # Create updated result
                updated = PhaseAwareAggregationResult(
                    phase=target_result.phase,
                    capacity_type=target_result.capacity_type,
                    base_result=target_result.base_result,
                    phase_adjusted_org_score=cross_org,
                    phase_adjusted_sys_score=cross_sys,
                    kappa_org_used=target_result.kappa_org_used,
                    kappa_sys_used=target_result.kappa_sys_used,
                    phase_org_factor=target_result.phase_org_factor,
                    was_smoothed=target_result.was_smoothed,
                    smoothing_alpha=target_result.smoothing_alpha,
                    previous_phase_contribution=target_result.previous_phase_contribution,
                    cross_phase_aggregated=True,
                    cross_phase_partner=source_phase,
                    transition_factor_used=transition_factor,
                )
                
                updated_results.append(updated)
            else:
                # No matching source result, keep target as-is
                updated_results.append(target_result)
        
        return updated_results
    
    def _estimate_coherence(self, phase_scores: List[PhaseCapacityScore]) -> float:
        """
        Estimate coherence from phase scores.
        
        Higher coherence = scores are consistent with previous phase.
        """
        # Use transition coherence factors from phase scores
        coherence_factors = [
            ps.transition_coherence_factor
            for ps in phase_scores
            if ps.previous_phase_score is not None
        ]
        
        if coherence_factors:
            return sum(coherence_factors) / len(coherence_factors)
        else:
            return 1.0  # Perfect coherence if no previous phase
    
    def _calculate_smoothing_alpha(self, coherence: float) -> float:
        """
        Calculate smoothing alpha from coherence using sigmoid.
        
        Formula 12: α = sigmoid((coherence - 0.5) × sensitivity)
        
        High coherence → high alpha → rely more on current phase
        Low coherence → low alpha → blend more with previous phase
        """
        # Sigmoid function centered at coherence=0.5
        x = (coherence - 0.5) * self.config.smoothing_sensitivity * 10
        return 1.0 / (1.0 + math.exp(-x))
    
    def compute_phase_aggregation_metrics(
        self,
        results: List[PhaseAwareAggregationResult],
    ) -> Dict[str, Any]:
        """
        Compute metrics about phase-aware aggregation results.
        
        Returns:
            Dictionary with aggregation quality metrics
        """
        if not results:
            return {}
        
        phase = results[0].phase
        
        # Count smoothed results
        smoothed_count = sum(1 for r in results if r.was_smoothed)
        
        # Count cross-phase aggregated
        cross_phase_count = sum(1 for r in results if r.cross_phase_aggregated)
        
        # Average phase adjustments
        avg_org_adjustment = np.mean([
            r.phase_adjusted_org_score / r.base_result.organizational_score
            if r.base_result.organizational_score > 0 else 1.0
            for r in results
        ])
        
        avg_sys_adjustment = np.mean([
            r.phase_adjusted_sys_score / r.base_result.systemic_score
            if r.base_result.systemic_score > 0 else 1.0
            for r in results
        ])
        
        # Average phase org factor
        avg_phase_org_factor = np.mean([r.phase_org_factor for r in results])
        
        return {
            "phase": phase.code,
            "total_results": len(results),
            "smoothed_count": smoothed_count,
            "smoothed_percentage": (smoothed_count / len(results)) * 100,
            "cross_phase_count": cross_phase_count,
            "cross_phase_percentage": (cross_phase_count / len(results)) * 100,
            "avg_org_adjustment_factor": float(avg_org_adjustment),
            "avg_sys_adjustment_factor": float(avg_sys_adjustment),
            "avg_phase_org_factor": float(avg_phase_org_factor),
        }


# ============================================================================
# PHASE-AWARE AGGREGATION PIPELINE
# ============================================================================

class PhaseAggregationPipeline:
    """
    Complete pipeline for phase-aware capacity aggregation.
    
    Orchestrates aggregation across multiple phases with proper
    transition handling and cross-phase analysis.
    """
    
    def __init__(
        self,
        config: Optional[PhaseAggregationConfig] = None,
    ):
        """Initialize phase aggregation pipeline."""
        self.aggregator = PhaseAwareCapacityAggregator(config)
        self.phase_results: Dict[CanonicalPhase, List[PhaseAwareAggregationResult]] = {}
    
    def process_phase(
        self,
        phase: CanonicalPhase,
        phase_scores: List[PhaseCapacityScore],
    ) -> List[PhaseAwareAggregationResult]:
        """
        Process a single phase in the pipeline.
        
        Args:
            phase: Current phase
            phase_scores: Phase-aware capacity scores
            
        Returns:
            Phase-aware aggregation results
        """
        # Get previous phase results if available
        prev_phase = phase.prev_phase()
        previous_results = self.phase_results.get(prev_phase) if prev_phase else None
        
        # Aggregate with phase awareness
        results = self.aggregator.aggregate_phase_capacity(
            phase=phase,
            phase_scores=phase_scores,
            previous_phase_results=previous_results,
        )
        
        # Store results
        self.phase_results[phase] = results
        
        return results
    
    def analyze_phase_transition(
        self,
        source_phase: CanonicalPhase,
        target_phase: CanonicalPhase,
    ) -> Dict[str, Any]:
        """
        Analyze aggregation transition between two phases.
        
        Returns:
            Analysis of how aggregated capacity changed between phases
        """
        if source_phase not in self.phase_results:
            raise ValueError(f"No results for source phase: {source_phase}")
        if target_phase not in self.phase_results:
            raise ValueError(f"No results for target phase: {target_phase}")
        
        source_results = self.phase_results[source_phase]
        target_results = self.phase_results[target_phase]
        
        # Calculate aggregate capacity for each phase
        source_org_total = sum(r.phase_adjusted_org_score for r in source_results)
        target_org_total = sum(r.phase_adjusted_org_score for r in target_results)
        
        source_sys_total = sum(r.phase_adjusted_sys_score for r in source_results)
        target_sys_total = sum(r.phase_adjusted_sys_score for r in target_results)
        
        # Calculate changes
        org_delta = target_org_total - source_org_total
        sys_delta = target_sys_total - source_sys_total
        
        return {
            "source_phase": source_phase.code,
            "target_phase": target_phase.code,
            "organizational_capacity": {
                "source": source_org_total,
                "target": target_org_total,
                "delta": org_delta,
                "growth_rate": (org_delta / source_org_total * 100) if source_org_total > 0 else 0,
            },
            "systemic_capacity": {
                "source": source_sys_total,
                "target": target_sys_total,
                "delta": sys_delta,
                "growth_rate": (sys_delta / source_sys_total * 100) if source_sys_total > 0 else 0,
            },
        }
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """
        Get summary of entire pipeline aggregation.
        
        Returns:
            Comprehensive summary of aggregation across all phases
        """
        if not self.phase_results:
            return {"phases_processed": 0}
        
        phases_processed = sorted(self.phase_results.keys(), key=lambda p: p.index)
        
        # Calculate total capacity progression
        org_progression = [
            sum(r.phase_adjusted_org_score for r in self.phase_results[p])
            for p in phases_processed
        ]
        
        sys_progression = [
            sum(r.phase_adjusted_sys_score for r in self.phase_results[p])
            for p in phases_processed
        ]
        
        return {
            "phases_processed": len(phases_processed),
            "phase_sequence": [p.code for p in phases_processed],
            "organizational_progression": org_progression,
            "systemic_progression": sys_progression,
            "final_org_capacity": org_progression[-1] if org_progression else 0,
            "final_sys_capacity": sys_progression[-1] if sys_progression else 0,
        }


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "PhaseAggregationConfig",
    "PhaseAwareAggregationResult",
    "PhaseAwareCapacityAggregator",
    "PhaseAggregationPipeline",
]
