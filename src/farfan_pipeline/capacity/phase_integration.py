"""
Phase-Capacity Integration Module
=================================

This module provides deep integration between the Wu Policy Capacity Framework
and the FARFAN canonical phases (Phase_00 through Phase_09), enabling:

1. **Phase-Aware Capacity Assessment**: Capacity scores contextualized by phase
2. **Cross-Phase Capacity Flow**: Track capacity evolution across phases
3. **Phase-Specific Aggregation**: Different aggregation strategies per phase
4. **Phase Transition Validation**: Ensure capacity coherence at phase boundaries

ARCHITECTURAL PRINCIPLES (PythonGod Trinity):
---------------------------------------------

**METACLASS LEVEL (Architect of Forms)**:
- Defines the fundamental phase-capacity type structure
- Establishes invariants that ALL phase-capacity objects must obey
- Provides universal validation and transformation rules

**CLASS LEVEL (Logos/Blueprint)**:
- Contains complete specifications for phase-capacity relationships
- Defines methods for phase-aware scoring and aggregation
- Maintains the canonical mapping between phases and capacity types

**INSTANCE LEVEL (Spirit in Action)**:
- Holds concrete capacity scores for specific phase executions
- Experiences temporal flow as data moves through phases
- Tracks actual capacity evolution and transformations

Integration with Canonical Phases:
----------------------------------
Phase_00 (Wiring): Infrastructure capacity mapping
Phase_01 (Canonical Input): Input validation capacity
Phase_02 (Evidence Collection): Empirical extraction capacity
Phase_03 (Micro Scoring): Individual analytical capacity
Phase_04 (Meso Aggregation): Organizational aggregation capacity
Phase_05 (Policy Area Synthesis): Cross-area capacity analysis
Phase_06 (Cluster Analysis): Systemic capacity patterns
Phase_07 (Macro Aggregation): Strategic capacity integration
Phase_08 (Recommendations): Operational delivery capacity
Phase_09 (Output Generation): Political communication capacity

Mathematical Extensions:
-----------------------
Formula 7: Phase-Aware Capacity Score
    C_phase(p, t) = C_base(t) × φ_phase(p) × τ_transition(p, p-1)
    
    Where:
    - p = current phase index [0..9]
    - t = capacity type
    - φ_phase(p) = phase relevance multiplier
    - τ_transition(p, p-1) = phase transition coherence factor

Formula 8: Cross-Phase Capacity Flow
    F_capacity(p1, p2) = Σ[C_phase(p2, t) × w_flow(t)] / Σ[C_phase(p1, t)]
    
    Measures how capacity transforms between phases

Formula 9: Phase Progression Index (PPI)
    PPI = Σ[w_phase(p) × C_phase(p)] / Σ[C_ideal(p)]
    
    Measures overall capacity progression through the pipeline

Author: F.A.R.F.A.N. Core Team (PythonGod Trinity Enhanced)
Version: 2.0.0 - Canonical Phase Integration
Date: 2026-01-26
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    ClassVar,
)
from datetime import datetime

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    EpistemologicalLevel,
    CapacityScore,
    MethodCapacityMapping,
    AggregatedCapacity,
)


# ============================================================================
# CANONICAL PHASE ENUMERATION
# ============================================================================

@unique
class CanonicalPhase(Enum):
    """
    FARFAN Canonical Phases - The complete pipeline workflow.
    
    Each phase represents a distinct transformation stage with specific
    capacity requirements and contribution patterns.
    """
    
    PHASE_00 = (0, "Wiring", "Infrastructure preparation and component wiring")
    PHASE_01 = (1, "Canonical Input", "Input validation and canonicalization")
    PHASE_02 = (2, "Evidence Collection", "Empirical data extraction")
    PHASE_03 = (3, "Micro Scoring", "Individual question scoring")
    PHASE_04 = (4, "Meso Aggregation", "Dimension-level aggregation")
    PHASE_05 = (5, "Policy Area Synthesis", "Cross-area integration")
    PHASE_06 = (6, "Cluster Analysis", "Pattern detection and clustering")
    PHASE_07 = (7, "Macro Aggregation", "System-level synthesis")
    PHASE_08 = (8, "Recommendations", "Strategic recommendation generation")
    PHASE_09 = (9, "Output Generation", "Final output and reporting")
    
    def __init__(self, index: int, name: str, description: str):
        self._index = index
        self._name = name
        self._description = description
    
    @property
    def index(self) -> int:
        """Phase index (0-9)."""
        return self._index
    
    @property
    def phase_name(self) -> str:
        """Human-readable phase name."""
        return self._name
    
    @property
    def description(self) -> str:
        """Phase description."""
        return self._description
    
    @property
    def code(self) -> str:
        """Phase code (e.g., 'PHASE_00')."""
        return self.name
    
    @classmethod
    def from_index(cls, index: int) -> "CanonicalPhase":
        """Get phase by index."""
        for phase in cls:
            if phase.index == index:
                return phase
        raise ValueError(f"Invalid phase index: {index}")
    
    @classmethod
    def all_phases(cls) -> List["CanonicalPhase"]:
        """Return all phases in execution order."""
        return sorted(cls, key=lambda p: p.index)
    
    def next_phase(self) -> Optional["CanonicalPhase"]:
        """Get next phase in pipeline, or None if this is the last phase."""
        if self.index < 9:
            return self.from_index(self.index + 1)
        return None
    
    def prev_phase(self) -> Optional["CanonicalPhase"]:
        """Get previous phase in pipeline, or None if this is the first phase."""
        if self.index > 0:
            return self.from_index(self.index - 1)
        return None
    
    def distance_to(self, other: "CanonicalPhase") -> int:
        """Calculate distance between phases."""
        return abs(self.index - other.index)


# ============================================================================
# PHASE-CAPACITY MAPPING
# ============================================================================

@dataclass(frozen=True)
class PhaseCapacityMapping:
    """
    Defines which capacity types are relevant for each canonical phase.
    
    This mapping captures the THEORETICAL relationship between pipeline
    phases and the Wu Framework capacity types, enabling phase-aware
    capacity assessment.
    
    Design Principles:
    - Early phases (0-2): Emphasize Operational-Individual (infrastructure)
    - Middle phases (3-5): Emphasize Analytical-Organizational (analysis)
    - Late phases (6-9): Emphasize Political-Systemic (synthesis & communication)
    """
    
    phase: CanonicalPhase
    primary_capacities: FrozenSet[CapacityType]
    secondary_capacities: FrozenSet[CapacityType]
    phase_relevance_weight: float  # [0.0, 1.0] - importance of capacity in this phase
    
    @property
    def all_relevant_capacities(self) -> FrozenSet[CapacityType]:
        """Get all relevant capacity types (primary + secondary)."""
        return self.primary_capacities | self.secondary_capacities
    
    def is_relevant(self, capacity_type: CapacityType) -> bool:
        """Check if a capacity type is relevant for this phase."""
        return capacity_type in self.all_relevant_capacities
    
    def get_capacity_weight(self, capacity_type: CapacityType) -> float:
        """
        Get weight for a capacity type in this phase.
        
        Returns:
        - 1.0 for primary capacities
        - 0.5 for secondary capacities
        - 0.0 for non-relevant capacities
        """
        if capacity_type in self.primary_capacities:
            return 1.0
        elif capacity_type in self.secondary_capacities:
            return 0.5
        else:
            return 0.0


# Default phase-capacity mappings based on theoretical analysis
DEFAULT_PHASE_CAPACITY_MAPPINGS = {
    CanonicalPhase.PHASE_00: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_00,
        primary_capacities=frozenset([CapacityType.CO_I, CapacityType.CO_O]),
        secondary_capacities=frozenset([CapacityType.CA_I]),
        phase_relevance_weight=0.7,
    ),
    CanonicalPhase.PHASE_01: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_01,
        primary_capacities=frozenset([CapacityType.CA_I, CapacityType.CO_I]),
        secondary_capacities=frozenset([CapacityType.CA_O]),
        phase_relevance_weight=0.8,
    ),
    CanonicalPhase.PHASE_02: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_02,
        primary_capacities=frozenset([CapacityType.CA_I, CapacityType.CA_O]),
        secondary_capacities=frozenset([CapacityType.CO_I, CapacityType.CO_O]),
        phase_relevance_weight=0.9,
    ),
    CanonicalPhase.PHASE_03: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_03,
        primary_capacities=frozenset([CapacityType.CA_I, CapacityType.CA_O]),
        secondary_capacities=frozenset([CapacityType.CO_O]),
        phase_relevance_weight=1.0,
    ),
    CanonicalPhase.PHASE_04: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_04,
        primary_capacities=frozenset([CapacityType.CA_O, CapacityType.CO_O]),
        secondary_capacities=frozenset([CapacityType.CA_S, CapacityType.CP_O]),
        phase_relevance_weight=1.0,
    ),
    CanonicalPhase.PHASE_05: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_05,
        primary_capacities=frozenset([CapacityType.CA_O, CapacityType.CA_S]),
        secondary_capacities=frozenset([CapacityType.CP_O, CapacityType.CO_S]),
        phase_relevance_weight=0.95,
    ),
    CanonicalPhase.PHASE_06: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_06,
        primary_capacities=frozenset([CapacityType.CA_S, CapacityType.CP_O]),
        secondary_capacities=frozenset([CapacityType.CP_S, CapacityType.CO_S]),
        phase_relevance_weight=0.95,
    ),
    CanonicalPhase.PHASE_07: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_07,
        primary_capacities=frozenset([CapacityType.CA_S, CapacityType.CP_S]),
        secondary_capacities=frozenset([CapacityType.CO_S]),
        phase_relevance_weight=1.0,
    ),
    CanonicalPhase.PHASE_08: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_08,
        primary_capacities=frozenset([CapacityType.CO_O, CapacityType.CP_O]),
        secondary_capacities=frozenset([CapacityType.CP_S, CapacityType.CA_O]),
        phase_relevance_weight=0.9,
    ),
    CanonicalPhase.PHASE_09: PhaseCapacityMapping(
        phase=CanonicalPhase.PHASE_09,
        primary_capacities=frozenset([CapacityType.CP_O, CapacityType.CP_S]),
        secondary_capacities=frozenset([CapacityType.CO_O]),
        phase_relevance_weight=0.85,
    ),
}


# ============================================================================
# PHASE-AWARE CAPACITY SCORE
# ============================================================================

@dataclass
class PhaseCapacityScore:
    """
    Capacity score contextualized for a specific canonical phase.
    
    This extends the base CapacityScore with phase-specific information,
    enabling phase-aware capacity assessment and tracking capacity
    evolution across the pipeline.
    
    Formula 7: Phase-Aware Capacity Score
        C_phase(p, t) = C_base(t) × φ_phase(p) × τ_transition(p, p-1)
    """
    
    # Core identification
    phase: CanonicalPhase
    capacity_type: CapacityType
    base_score: CapacityScore
    
    # Phase-specific adjustments
    phase_relevance_multiplier: float  # φ_phase(p) - how relevant is this capacity in this phase
    transition_coherence_factor: float  # τ_transition - how coherent is transition from prev phase
    
    # Computed phase-aware score
    phase_adjusted_score: float
    
    # Provenance
    computed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    previous_phase_score: Optional["PhaseCapacityScore"] = None
    
    @classmethod
    def from_base_score(
        cls,
        phase: CanonicalPhase,
        base_score: CapacityScore,
        mapping: PhaseCapacityMapping,
        previous_phase_score: Optional["PhaseCapacityScore"] = None,
    ) -> "PhaseCapacityScore":
        """
        Create phase-aware score from base capacity score.
        
        Applies Formula 7 to compute phase-adjusted capacity score.
        """
        # Get phase relevance multiplier from mapping
        phase_relevance = mapping.get_capacity_weight(base_score.capacity_type)
        phase_relevance_multiplier = (
            mapping.phase_relevance_weight * phase_relevance
        )
        
        # Calculate transition coherence factor
        if previous_phase_score is None:
            # First phase - no transition
            transition_coherence_factor = 1.0
        else:
            # Measure coherence: how much did capacity change between phases?
            # High coherence = small change, Low coherence = large change
            prev_score = previous_phase_score.phase_adjusted_score
            curr_base = base_score.weighted_score
            
            if prev_score > 0:
                change_ratio = abs(curr_base - prev_score) / prev_score
                # Exponential decay: 0% change = 1.0, 100% change = 0.37
                transition_coherence_factor = math.exp(-change_ratio)
            else:
                transition_coherence_factor = 1.0
        
        # Apply Formula 7
        phase_adjusted_score = (
            base_score.weighted_score
            * phase_relevance_multiplier
            * transition_coherence_factor
        )
        
        return cls(
            phase=phase,
            capacity_type=base_score.capacity_type,
            base_score=base_score,
            phase_relevance_multiplier=phase_relevance_multiplier,
            transition_coherence_factor=transition_coherence_factor,
            phase_adjusted_score=phase_adjusted_score,
            previous_phase_score=previous_phase_score,
        )
    
    def get_contribution_ratio(self) -> float:
        """
        Calculate how much this capacity contributes in this phase.
        
        Returns ratio of phase-adjusted score to base score.
        """
        if self.base_score.weighted_score > 0:
            return self.phase_adjusted_score / self.base_score.weighted_score
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "phase": self.phase.code,
            "phase_index": self.phase.index,
            "capacity_type": self.capacity_type.code,
            "base_weighted_score": self.base_score.weighted_score,
            "phase_relevance_multiplier": self.phase_relevance_multiplier,
            "transition_coherence_factor": self.transition_coherence_factor,
            "phase_adjusted_score": self.phase_adjusted_score,
            "contribution_ratio": self.get_contribution_ratio(),
            "computed_at": self.computed_at,
        }


# ============================================================================
# CROSS-PHASE CAPACITY FLOW ANALYZER
# ============================================================================

@dataclass
class CapacityFlowMetrics:
    """
    Metrics for capacity flow between two phases.
    
    Formula 8: Cross-Phase Capacity Flow
        F_capacity(p1, p2) = Σ[C_phase(p2, t) × w_flow(t)] / Σ[C_phase(p1, t)]
    """
    
    source_phase: CanonicalPhase
    target_phase: CanonicalPhase
    
    # Aggregate scores
    source_total_capacity: float
    target_total_capacity: float
    
    # Flow analysis
    capacity_flow_ratio: float  # F_capacity from Formula 8
    capacity_delta: float  # Absolute change
    capacity_growth_rate: float  # Percentage change
    
    # Per-capacity breakdown
    capacity_type_flows: Dict[CapacityType, Tuple[float, float]]  # (source, target)
    
    # Coherence metrics
    flow_coherence: float  # How coherent is the transition [0, 1]
    discontinuity_score: float  # Measure of abrupt changes
    
    @classmethod
    def analyze_flow(
        cls,
        source_scores: List[PhaseCapacityScore],
        target_scores: List[PhaseCapacityScore],
    ) -> "CapacityFlowMetrics":
        """
        Analyze capacity flow between two phases.
        
        Implements Formula 8 to compute cross-phase capacity flow metrics.
        """
        if not source_scores:
            raise ValueError("Source scores cannot be empty")
        if not target_scores:
            raise ValueError("Target scores cannot be empty")
        
        source_phase = source_scores[0].phase
        target_phase = target_scores[0].phase
        
        # Calculate total capacities
        source_total = sum(s.phase_adjusted_score for s in source_scores)
        target_total = sum(s.phase_adjusted_score for s in target_scores)
        
        # Build capacity type mapping
        source_by_type = {s.capacity_type: s for s in source_scores}
        target_by_type = {s.capacity_type: s for s in target_scores}
        
        # Calculate per-capacity flows
        capacity_type_flows = {}
        for cap_type in set(source_by_type.keys()) | set(target_by_type.keys()):
            source_val = source_by_type.get(cap_type, None)
            target_val = target_by_type.get(cap_type, None)
            
            source_score = source_val.phase_adjusted_score if source_val else 0.0
            target_score = target_val.phase_adjusted_score if target_val else 0.0
            
            capacity_type_flows[cap_type] = (source_score, target_score)
        
        # Calculate flow ratio (Formula 8)
        if source_total > 0:
            capacity_flow_ratio = target_total / source_total
        else:
            capacity_flow_ratio = float('inf') if target_total > 0 else 1.0
        
        # Calculate delta and growth rate
        capacity_delta = target_total - source_total
        if source_total > 0:
            capacity_growth_rate = (capacity_delta / source_total) * 100.0
        else:
            capacity_growth_rate = 100.0 if target_total > 0 else 0.0
        
        # Calculate flow coherence (inverse of variance in flow ratios)
        flow_ratios = []
        for source_score, target_score in capacity_type_flows.values():
            if source_score > 0:
                flow_ratios.append(target_score / source_score)
        
        if flow_ratios:
            mean_ratio = sum(flow_ratios) / len(flow_ratios)
            variance = sum((r - mean_ratio) ** 2 for r in flow_ratios) / len(flow_ratios)
            flow_coherence = math.exp(-variance)  # High variance = low coherence
        else:
            flow_coherence = 1.0
        
        # Calculate discontinuity score (sum of abrupt changes)
        discontinuity_score = sum(
            abs(target - source)
            for source, target in capacity_type_flows.values()
        )
        
        return cls(
            source_phase=source_phase,
            target_phase=target_phase,
            source_total_capacity=source_total,
            target_total_capacity=target_total,
            capacity_flow_ratio=capacity_flow_ratio,
            capacity_delta=capacity_delta,
            capacity_growth_rate=capacity_growth_rate,
            capacity_type_flows=capacity_type_flows,
            flow_coherence=flow_coherence,
            discontinuity_score=discontinuity_score,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_phase": self.source_phase.code,
            "target_phase": self.target_phase.code,
            "source_total_capacity": self.source_total_capacity,
            "target_total_capacity": self.target_total_capacity,
            "capacity_flow_ratio": self.capacity_flow_ratio,
            "capacity_delta": self.capacity_delta,
            "capacity_growth_rate": self.capacity_growth_rate,
            "flow_coherence": self.flow_coherence,
            "discontinuity_score": self.discontinuity_score,
            "capacity_type_flows": {
                ct.code: {"source": src, "target": tgt}
                for ct, (src, tgt) in self.capacity_type_flows.items()
            },
        }


# ============================================================================
# PHASE PROGRESSION INDEX CALCULATOR
# ============================================================================

@dataclass
class PhaseProgressionIndex:
    """
    Measures overall capacity progression through the pipeline.
    
    Formula 9: Phase Progression Index (PPI)
        PPI = Σ[w_phase(p) × C_phase(p)] / Σ[C_ideal(p)]
    
    Where:
    - w_phase(p) = phase importance weight
    - C_phase(p) = actual capacity in phase p
    - C_ideal(p) = ideal capacity target for phase p
    """
    
    # Overall PPI score [0, 1]
    ppi_score: float
    
    # Per-phase contributions
    phase_scores: Dict[CanonicalPhase, float]
    phase_weights: Dict[CanonicalPhase, float]
    phase_ideals: Dict[CanonicalPhase, float]
    
    # Analysis
    strongest_phases: List[CanonicalPhase]  # Top 3 phases by capacity
    weakest_phases: List[CanonicalPhase]  # Bottom 3 phases by capacity
    
    # Bottleneck detection
    bottleneck_phase: Optional[CanonicalPhase]
    bottleneck_severity: float
    
    @classmethod
    def calculate(
        cls,
        phase_scores_dict: Dict[CanonicalPhase, List[PhaseCapacityScore]],
        phase_weights: Optional[Dict[CanonicalPhase, float]] = None,
        phase_ideals: Optional[Dict[CanonicalPhase, float]] = None,
    ) -> "PhaseProgressionIndex":
        """
        Calculate Phase Progression Index across all phases.
        
        Implements Formula 9.
        """
        if not phase_scores_dict:
            raise ValueError("Phase scores cannot be empty")
        
        # Use default weights if not provided (equal weighting)
        if phase_weights is None:
            all_phases = CanonicalPhase.all_phases()
            phase_weights = {phase: 1.0 for phase in all_phases}
        
        # Use default ideals if not provided (assume 1.0 as ideal)
        if phase_ideals is None:
            all_phases = CanonicalPhase.all_phases()
            phase_ideals = {phase: 1.0 for phase in all_phases}
        
        # Calculate actual phase scores (sum of all capacity scores)
        phase_scores = {}
        for phase, scores in phase_scores_dict.items():
            phase_scores[phase] = sum(s.phase_adjusted_score for s in scores)
        
        # Apply Formula 9
        weighted_actual = sum(
            phase_weights[phase] * phase_scores[phase]
            for phase in phase_scores.keys()
        )
        weighted_ideal = sum(
            phase_weights[phase] * phase_ideals[phase]
            for phase in phase_scores.keys()
        )
        
        ppi_score = weighted_actual / weighted_ideal if weighted_ideal > 0 else 0.0
        
        # Identify strongest and weakest phases
        sorted_phases = sorted(
            phase_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        strongest_phases = [p for p, _ in sorted_phases[:3]]
        weakest_phases = [p for p, _ in sorted_phases[-3:]]
        
        # Detect bottleneck (phase with largest gap from ideal)
        gaps = {
            phase: abs(phase_ideals[phase] - phase_scores.get(phase, 0.0))
            for phase in phase_ideals.keys()
        }
        bottleneck_phase = max(gaps.items(), key=lambda x: x[1])[0] if gaps else None
        bottleneck_severity = gaps[bottleneck_phase] if bottleneck_phase else 0.0
        
        return cls(
            ppi_score=ppi_score,
            phase_scores=phase_scores,
            phase_weights=phase_weights,
            phase_ideals=phase_ideals,
            strongest_phases=strongest_phases,
            weakest_phases=weakest_phases,
            bottleneck_phase=bottleneck_phase,
            bottleneck_severity=bottleneck_severity,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "ppi_score": self.ppi_score,
            "phase_scores": {p.code: s for p, s in self.phase_scores.items()},
            "phase_weights": {p.code: w for p, w in self.phase_weights.items()},
            "phase_ideals": {p.code: i for p, i in self.phase_ideals.items()},
            "strongest_phases": [p.code for p in self.strongest_phases],
            "weakest_phases": [p.code for p in self.weakest_phases],
            "bottleneck_phase": self.bottleneck_phase.code if self.bottleneck_phase else None,
            "bottleneck_severity": self.bottleneck_severity,
        }


# ============================================================================
# PHASE-AWARE CAPACITY ADAPTER (Bridge Pattern)
# ============================================================================

class PhaseCapacityAdapter:
    """
    Adapter for integrating capacity framework with canonical phases.
    
    This class provides the PRIMARY INTERFACE for phase-aware capacity
    assessment, implementing the Bridge pattern to connect the Wu Framework
    with the FARFAN pipeline phases.
    
    Usage:
        adapter = PhaseCapacityAdapter()
        phase_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=[...],
            previous_phase_scores=[...]
        )
    """
    
    def __init__(
        self,
        phase_mappings: Optional[Dict[CanonicalPhase, PhaseCapacityMapping]] = None,
    ):
        """
        Initialize adapter with phase-capacity mappings.
        
        Args:
            phase_mappings: Custom phase-capacity mappings, or None for defaults
        """
        self.phase_mappings = phase_mappings or DEFAULT_PHASE_CAPACITY_MAPPINGS
    
    def compute_phase_capacity(
        self,
        phase: CanonicalPhase,
        base_scores: List[CapacityScore],
        previous_phase_scores: Optional[List[PhaseCapacityScore]] = None,
    ) -> List[PhaseCapacityScore]:
        """
        Compute phase-aware capacity scores for a given phase.
        
        Applies Formula 7 to transform base capacity scores into
        phase-contextualized scores.
        """
        if phase not in self.phase_mappings:
            raise ValueError(f"No mapping defined for phase: {phase}")
        
        mapping = self.phase_mappings[phase]
        
        # Build lookup for previous scores by capacity type
        prev_scores_by_type = {}
        if previous_phase_scores:
            prev_scores_by_type = {
                s.capacity_type: s for s in previous_phase_scores
            }
        
        # Compute phase-aware scores
        phase_scores = []
        for base_score in base_scores:
            prev_score = prev_scores_by_type.get(base_score.capacity_type)
            
            phase_score = PhaseCapacityScore.from_base_score(
                phase=phase,
                base_score=base_score,
                mapping=mapping,
                previous_phase_score=prev_score,
            )
            
            phase_scores.append(phase_score)
        
        return phase_scores
    
    def analyze_phase_transition(
        self,
        source_phase: CanonicalPhase,
        target_phase: CanonicalPhase,
        source_scores: List[PhaseCapacityScore],
        target_scores: List[PhaseCapacityScore],
    ) -> CapacityFlowMetrics:
        """
        Analyze capacity flow between two phases.
        
        Implements Formula 8 to compute cross-phase capacity flow.
        """
        return CapacityFlowMetrics.analyze_flow(source_scores, target_scores)
    
    def compute_progression_index(
        self,
        all_phase_scores: Dict[CanonicalPhase, List[PhaseCapacityScore]],
    ) -> PhaseProgressionIndex:
        """
        Compute Phase Progression Index across all phases.
        
        Implements Formula 9 to measure overall capacity progression.
        """
        return PhaseProgressionIndex.calculate(all_phase_scores)
    
    def get_phase_capacity_profile(
        self,
        phase: CanonicalPhase,
    ) -> PhaseCapacityMapping:
        """Get capacity profile for a specific phase."""
        if phase not in self.phase_mappings:
            raise ValueError(f"No mapping defined for phase: {phase}")
        return self.phase_mappings[phase]


# ============================================================================
# PROTOCOL FOR PHASE-AWARE COMPONENTS
# ============================================================================

class PhaseAware(Protocol):
    """
    Protocol for objects that are aware of canonical phases.
    
    Components implementing this protocol can participate in
    phase-aware capacity assessment and analysis.
    """
    
    @property
    def current_phase(self) -> CanonicalPhase:
        """Get current phase of this component."""
        ...
    
    def transition_to_phase(self, target_phase: CanonicalPhase) -> None:
        """Transition this component to a new phase."""
        ...


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Enumerations
    "CanonicalPhase",
    # Mappings
    "PhaseCapacityMapping",
    "DEFAULT_PHASE_CAPACITY_MAPPINGS",
    # Scores
    "PhaseCapacityScore",
    # Flow Analysis
    "CapacityFlowMetrics",
    # Progression
    "PhaseProgressionIndex",
    # Adapter
    "PhaseCapacityAdapter",
    # Protocol
    "PhaseAware",
]
