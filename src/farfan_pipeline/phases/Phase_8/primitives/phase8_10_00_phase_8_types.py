"""
Module: src.farfan_pipeline.phases.Phase_8.primitives.PHASE_8_TYPES
Purpose: Type definitions and type aliases for Phase 8 - Recommendation Engine
Owner: phase8_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-05

This module provides type definitions used throughout Phase 8 for type safety
and documentation purposes.
"""

from __future__ import annotations

from typing import Any, TypedDict, NewType, Literal

# ============================================================================
# NEW TYPES (Semantic Type Aliases)
# ============================================================================

# Score key in format "PA##-DIM##" (e.g., "PA01-DIM03")
MicroScoreKey = NewType("MicroScoreKey", str)

# Cluster key in format "CL##" (e.g., "CL01")
ClusterKey = NewType("ClusterKey", str)

# Recommendation rule ID (e.g., "REC-MICRO-PA01-DIM01-LB01")
RuleId = NewType("RuleId", str)

# Question ID in format "Q###" (e.g., "Q001")
QuestionId = NewType("QuestionId", str)

# Policy Area ID in format "PA##" (e.g., "PA01")
PolicyAreaId = NewType("PolicyAreaId", str)

# Dimension ID in format "DIM##" (e.g., "DIM01")
DimensionId = NewType("DimensionId", str)

# Score threshold value (0.0 - 3.0 for MICRO, 0.0 - 100.0 for MESO/MACRO)
ScoreThreshold = NewType("ScoreThreshold", float)


# ============================================================================
# LITERAL TYPES
# ============================================================================

RecommendationLevel = Literal["MICRO", "MESO", "MACRO"]

ScoreBandType = Literal["BAJO", "MEDIO", "ALTO", "SATISFACTORIO", "INSUFICIENTE"]

VarianceLevelType = Literal["BAJA", "MEDIA", "ALTA"]

VerificationType = Literal["DOCUMENT", "SYSTEM_STATE", "METRIC", "ATTESTATION"]

HorizonType = Literal["T0", "T1", "T2", "T3"]

VerificationFormat = Literal["PDF", "DATABASE_QUERY", "JSON", "XML"]


# ============================================================================
# TYPED DICTIONARIES - Input Contracts
# ============================================================================


class AnalysisResultsInput(TypedDict, total=True):
    """
    P8-IN-001: Analysis results from Phase 7.

    Contains aggregated scoring results at all three levels.
    """

    micro_scores: dict[str, float]  # PA##-DIM## -> score (0.0-3.0)
    cluster_data: dict[str, "ClusterDataEntry"]
    macro_data: "MacroDataEntry"


class ClusterDataEntry(TypedDict, total=False):
    """Entry for a single cluster in cluster_data."""

    score: float
    variance: float
    weak_pa: str | None


class MacroDataEntry(TypedDict, total=False):
    """Macro-level aggregated data."""

    macro_band: str
    clusters_below_target: list[str]
    variance_alert: str
    priority_micro_gaps: list[str]


class PolicyContextInput(TypedDict, total=False):
    """
    P8-IN-002: Policy context information.
    """

    policy_area_id: str
    dimension_id: str
    question_global: int
    question_id: str


class SignalDataInput(TypedDict, total=False):
    """
    P8-IN-003: Optional signal enrichment data.
    """

    patterns: list[Any]
    indicators: list[Any]


# ============================================================================
# TYPED DICTIONARIES - Recommendation Structure
# ============================================================================


class IndicatorSpec(TypedDict, total=False):
    """Indicator specification in a recommendation."""

    name: str
    baseline: float | None
    target: float
    unit: str
    formula: str
    acceptable_range: list[float]
    baseline_measurement_date: str
    measurement_frequency: str
    data_source: str
    data_source_query: str
    responsible_measurement: str
    escalation_if_below: float


class ResponsibleSpec(TypedDict, total=False):
    """Responsible entity specification."""

    entity: str
    role: str
    partners: list[str]
    legal_mandate: str
    approval_chain: list["ApprovalLevel"]
    escalation_path: "EscalationPath"


class ApprovalLevel(TypedDict, total=True):
    """Single level in approval chain."""

    level: int
    role: str
    decision: str


class EscalationPath(TypedDict, total=False):
    """Escalation path specification."""

    threshold_days_delay: int
    escalate_to: str
    final_escalation: str
    consequences: list[str]


class HorizonSpec(TypedDict, total=False):
    """Time horizon specification."""

    start: str
    end: str
    start_type: str
    duration_months: int
    milestones: list["Milestone"]
    dependencies: list[str]
    critical_path: bool


class Milestone(TypedDict, total=False):
    """Milestone within a horizon."""

    name: str
    offset_months: int
    deliverables: list[str]
    verification_required: bool


class VerificationArtifact(TypedDict, total=False):
    """Verification artifact specification."""

    id: str
    type: str  # VerificationType
    artifact: str
    format: str
    required_sections: list[str]
    approval_required: bool
    approver: str
    due_date: str
    automated_check: bool
    validation_query: str
    pass_condition: str


class ExecutionSpec(TypedDict, total=False):
    """Execution logic specification."""

    trigger_condition: str
    blocking: bool
    auto_apply: bool
    requires_approval: bool
    approval_roles: list[str]


class BudgetSpec(TypedDict, total=False):
    """Budget specification."""

    estimated_cost_cop: int
    cost_breakdown: dict[str, int]
    funding_sources: list["FundingSource"]
    fiscal_year: int


class FundingSource(TypedDict, total=True):
    """Single funding source."""

    source: str
    amount: int
    confirmed: bool


class RecommendationTemplate(TypedDict, total=False):
    """Full recommendation template structure."""

    problem: str
    intervention: str
    indicator: IndicatorSpec
    responsible: ResponsibleSpec
    horizon: HorizonSpec
    verification: list[VerificationArtifact]
    template_id: str
    template_params: dict[str, str]


class RuleCondition(TypedDict, total=False):
    """Rule condition (when clause)."""

    # MICRO
    pa_id: str
    dim_id: str
    score_lt: float
    # MESO
    cluster_id: str
    score_band: str
    variance_level: str
    variance_threshold: float
    weak_pa_id: str
    # MACRO
    macro_band: str
    clusters_below_target: list[str]
    variance_alert: str
    priority_micro_gaps: list[str]


class RecommendationRule(TypedDict, total=False):
    """Full recommendation rule structure."""

    rule_id: str
    level: str  # RecommendationLevel
    when: RuleCondition
    template: RecommendationTemplate
    execution: ExecutionSpec
    budget: BudgetSpec


# ============================================================================
# TYPED DICTIONARIES - Output Contracts
# ============================================================================


class RecommendationOutput(TypedDict, total=False):
    """Single recommendation output."""

    rule_id: str
    level: str
    problem: str
    intervention: str
    indicator: IndicatorSpec
    responsible: ResponsibleSpec
    horizon: HorizonSpec
    verification: list[VerificationArtifact]
    metadata: dict[str, Any]
    execution: ExecutionSpec | None
    budget: BudgetSpec | None
    template_id: str | None
    template_params: dict[str, str] | None


class RecommendationSetOutput(TypedDict, total=True):
    """Recommendation set output for a single level."""

    level: str
    recommendations: list[RecommendationOutput]
    generated_at: str
    total_rules_evaluated: int
    rules_matched: int
    metadata: dict[str, Any]


class RecommendationMetadata(TypedDict, total=False):
    """P8-OUT-002: Recommendation generation metadata."""

    generated_at: str
    total_rules_evaluated: int
    rules_matched: int
    engine_version: str
    rules_version: str
    levels_processed: list[str]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # New Types
    "MicroScoreKey",
    "ClusterKey",
    "RuleId",
    "QuestionId",
    "PolicyAreaId",
    "DimensionId",
    "ScoreThreshold",
    # Literal Types
    "RecommendationLevel",
    "ScoreBandType",
    "VarianceLevelType",
    "VerificationType",
    "HorizonType",
    "VerificationFormat",
    # Input TypedDicts
    "AnalysisResultsInput",
    "ClusterDataEntry",
    "MacroDataEntry",
    "PolicyContextInput",
    "SignalDataInput",
    # Recommendation Structure TypedDicts
    "IndicatorSpec",
    "ResponsibleSpec",
    "ApprovalLevel",
    "EscalationPath",
    "HorizonSpec",
    "Milestone",
    "VerificationArtifact",
    "ExecutionSpec",
    "BudgetSpec",
    "FundingSource",
    "RecommendationTemplate",
    "RuleCondition",
    "RecommendationRule",
    # Output TypedDicts
    "RecommendationOutput",
    "RecommendationSetOutput",
    "RecommendationMetadata",
]
