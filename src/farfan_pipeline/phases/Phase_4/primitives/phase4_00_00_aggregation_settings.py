"""
Phase 4 Aggregation Settings - Pure Dataclass (Primitives Layer)

This module contains ONLY the pure dataclass definition for AggregationSettings.
NO business logic, NO factory methods, NO imports from other Phase 4 modules.

This is the foundation of the dependency hierarchy:
- primitives/ (this module) - no Phase 4 dependencies
- configuration/ - depends on primitives
- aggregation_core/ - depends on primitives + configuration
- choquet_integral/ - depends on primitives
- integration/ - depends on all above

Following Clean Architecture and Dependency Inversion Principle.

Module: src/farfan_pipeline/phases/Phase_4/primitives/phase4_00_00_aggregation_settings.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"
__layer__ = "primitives"
__dependencies__ = []  # Zero dependencies on other Phase 4 modules

from dataclasses import dataclass


@dataclass(frozen=True)
class AggregationSettings:
    """
    Pure dataclass for aggregation configuration settings.
    
    Contains only data fields, no business logic. All factory methods and 
    validation logic are in configuration/ layer.
    
    Contract:
    - Input: Configuration parameters for multi-level aggregation
    - Structure: Three aggregation levels (dimension, area, cluster, macro)
    - Weights: Normalized weights for each aggregation level
    - Provenance: SISAS source hash for reproducibility
    
    Attributes:
        dimension_group_by_keys: Keys for grouping at dimension level
        area_group_by_keys: Keys for grouping at policy area level
        cluster_group_by_keys: Keys for grouping at cluster level
        dimension_question_weights: Question weights per dimension {dim_id: {q_id: weight}}
        policy_area_dimension_weights: Dimension weights per area {area_id: {dim_id: weight}}
        cluster_policy_area_weights: Area weights per cluster {cluster_id: {area_id: weight}}
        macro_cluster_weights: Cluster weights for macro {cluster_id: weight}
        dimension_expected_counts: Expected question count per (area, dimension)
        area_expected_dimension_counts: Expected dimension count per area
        source_hash: SISAS cryptographic hash for reproducibility
        sisas_source: Source type ("sisas_registry", "legacy_monolith", "legacy")
    """

    # Grouping keys for each aggregation level
    dimension_group_by_keys: list[str]
    area_group_by_keys: list[str]
    cluster_group_by_keys: list[str]
    
    # Weights for each aggregation level
    dimension_question_weights: dict[str, dict[str, float]]
    policy_area_dimension_weights: dict[str, dict[str, float]]
    cluster_policy_area_weights: dict[str, dict[str, float]]
    macro_cluster_weights: dict[str, float]
    
    # Expected counts for validation
    dimension_expected_counts: dict[tuple[str, str], int]
    area_expected_dimension_counts: dict[str, int]
    
    # SISAS provenance
    source_hash: str | None = None
    sisas_source: str = "legacy"  # "legacy" | "sisas_registry" | "legacy_monolith"


# Module-level validation
def validate_aggregation_settings(settings: AggregationSettings) -> tuple[bool, list[str]]:
    """
    Validate aggregation settings structure (no business logic).
    
    Args:
        settings: AggregationSettings instance to validate
        
    Returns:
        Tuple of (is_valid, list of validation errors)
    """
    errors = []
    
    # Validate group_by_keys are non-empty
    if not settings.dimension_group_by_keys:
        errors.append("dimension_group_by_keys cannot be empty")
    if not settings.area_group_by_keys:
        errors.append("area_group_by_keys cannot be empty")
    if not settings.cluster_group_by_keys:
        errors.append("cluster_group_by_keys cannot be empty")
    
    # Validate weight dictionaries are proper dicts
    if not isinstance(settings.dimension_question_weights, dict):
        errors.append("dimension_question_weights must be a dict")
    if not isinstance(settings.policy_area_dimension_weights, dict):
        errors.append("policy_area_dimension_weights must be a dict")
    if not isinstance(settings.cluster_policy_area_weights, dict):
        errors.append("cluster_policy_area_weights must be a dict")
    if not isinstance(settings.macro_cluster_weights, dict):
        errors.append("macro_cluster_weights must be a dict")
    
    # Validate sisas_source is valid
    valid_sources = {"legacy", "sisas_registry", "legacy_monolith", "legacy_fallback"}
    if settings.sisas_source not in valid_sources:
        errors.append(f"sisas_source must be one of {valid_sources}, got {settings.sisas_source}")
    
    return len(errors) == 0, errors


__all__ = [
    "AggregationSettings",
    "validate_aggregation_settings",
]
