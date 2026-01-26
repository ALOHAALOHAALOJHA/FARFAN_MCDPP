"""
Policy Capacity Framework Module
================================

Implementation of Wu, Ramesh & Howlett (2015) Policy Capacity Framework.

This module provides a NEW aggregation dimension based on capacity types and
equipment congregation, complementary to the existing Micro→Meso→Macro pipeline.

Framework Overview:
------------------
The Wu Framework defines 9 distinct capacity types from the intersection of:

Three Skills (Competences):
    1. Analytical (CA) - Technical knowledge, evidence processing, data analysis
    2. Operational (CO) - Resource management, implementation, execution
    3. Political (CP) - Legitimacy, stakeholder engagement, political acumen

Three Levels (Capabilities):
    1. Individual - Personal skills and competences of policy professionals
    2. Organizational - Institutional resources, processes, infrastructure
    3. Systemic - Societal context, trust, legitimacy, structural preconditions

The Complete Matrix:
              Analytical    Operational    Political
Individual    CA-I          CO-I           CP-I
Organizational CA-O         CO-O           CP-O
Systemic      CA-S          CO-S           CP-S

Mathematical Model:
------------------
1. Base Capacity Score: C_base = α×E + β×L + γ×O
2. Aggregation Weight: W_agg = η × exp(-λ × Δ_level)
3. Equipment Multiplier: M_equip = 1 + δ × ln(1+n) × (ρ-1)
4. Systemic Capacity: C_sys = Σ(C_base × W_agg × M) / N
5. Integrated Capacity Index: ICI = Σ(w_skill × Σ(w_level × C)) / 9

References:
----------
Wu, X., Ramesh, M., & Howlett, M. (2015). Policy capacity: A conceptual
framework for understanding policy competences and capabilities.
Policy and Society, 34(3-4), 165-171.

Author: F.A.R.F.A.N. Core Team
Version: 1.0.0
Date: 2026-01-26
"""

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    EpistemologicalLevel,
    EquipmentCongregation,
    CapacityScore,
    MethodCapacityMapping,
    AggregatedCapacity,
    CapacityGap,
    CapacityProfile,
)

from farfan_pipeline.capacity.base_score import (
    BaseCapacityScorer,
    CapacityScoringConfig,
    EpistemologyWeights,
    LevelWeights,
    OutputTypeWeights,
)

from farfan_pipeline.capacity.aggregation import (
    CapacityAggregator,
    AggregationConfig,
    TransformationMatrix,
    LevelAggregationResult,
)

from farfan_pipeline.capacity.equipment import (
    EquipmentCongregationEngine,
    SynergyCalculator,
    CongregationResult,
)

from farfan_pipeline.capacity.ici_calculator import (
    ICICalculator,
    ICIResult,
    CapacityDiagnostics,
    GapAnalysisResult,
)

from farfan_pipeline.capacity.phase_integration import (
    CanonicalPhase,
    PhaseCapacityMapping,
    DEFAULT_PHASE_CAPACITY_MAPPINGS,
    PhaseCapacityScore,
    CapacityFlowMetrics,
    PhaseProgressionIndex,
    PhaseCapacityAdapter,
    PhaseAware,
)

__all__ = [
    # Types
    "PolicySkill",
    "PolicyLevel",
    "CapacityType",
    "EpistemologicalLevel",
    "EquipmentCongregation",
    "CapacityScore",
    "MethodCapacityMapping",
    "AggregatedCapacity",
    "CapacityGap",
    "CapacityProfile",
    # Base Scoring
    "BaseCapacityScorer",
    "CapacityScoringConfig",
    "EpistemologyWeights",
    "LevelWeights",
    "OutputTypeWeights",
    # Aggregation
    "CapacityAggregator",
    "AggregationConfig",
    "TransformationMatrix",
    "LevelAggregationResult",
    # Equipment Congregation
    "EquipmentCongregationEngine",
    "SynergyCalculator",
    "CongregationResult",
    # ICI Calculator
    "ICICalculator",
    "ICIResult",
    "CapacityDiagnostics",
    "GapAnalysisResult",
    # Phase Integration (NEW)
    "CanonicalPhase",
    "PhaseCapacityMapping",
    "DEFAULT_PHASE_CAPACITY_MAPPINGS",
    "PhaseCapacityScore",
    "CapacityFlowMetrics",
    "PhaseProgressionIndex",
    "PhaseCapacityAdapter",
    "PhaseAware",
]

__version__ = "2.0.0"  # Major version bump for phase integration
__author__ = "F.A.R.F.A.N. Core Team"
