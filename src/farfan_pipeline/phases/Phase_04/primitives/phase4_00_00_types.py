"""
Phase 4 Aggregation Types - Shared Type Definitions (Primitives Layer)

This module contains shared type definitions and type aliases used across Phase 4.
NO dependencies on other Phase 4 modules.

Module: src/farfan_pipeline/phases/Phase_04/primitives/phase4_00_00_types.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"
__layer__ = "primitives"
__dependencies__ = []

from typing import Protocol, TypeAlias, runtime_checkable

# Type aliases for clarity
PolicyAreaID: TypeAlias = str  # e.g., "PA01", "PA02"
DimensionID: TypeAlias = str  # e.g., "D01", "D02" 
QuestionID: TypeAlias = str  # e.g., "Q001", "Q002"
ClusterID: TypeAlias = str  # e.g., "CLUSTER_MESO_1"
Score: TypeAlias = float  # Range [0.0, 3.0]
Weight: TypeAlias = float  # Range [0.0, 1.0], normalized weights sum to 1.0

# Aggregation method types
AggregationMethod: TypeAlias = str  # "weighted_average" | "choquet" | "geometric_mean"

# Quality level types
QualityLevel: TypeAlias = str  # "EXCELENTE" | "BUENO" | "ACEPTABLE" | "INSUFICIENTE"


@runtime_checkable
class IAggregator(Protocol):
    """
    Protocol for aggregator implementations.
    
    All aggregators (weighted, Choquet, etc.) must implement this interface.
    """
    
    def aggregate(
        self, 
        scores: list[Score], 
        weights: list[Weight] | None = None
    ) -> Score:
        """
        Aggregate multiple scores into a single score.
        
        Args:
            scores: List of scores to aggregate
            weights: Optional weights for each score (must sum to 1.0 if provided)
            
        Returns:
            Aggregated score in range [0.0, 3.0]
        """
        ...
    
    def validate_inputs(
        self, 
        scores: list[Score], 
        weights: list[Weight] | None = None
    ) -> tuple[bool, str]:
        """
        Validate that inputs are suitable for aggregation.
        
        Args:
            scores: List of scores to validate
            weights: Optional weights to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        ...


@runtime_checkable
class IConfigBuilder(Protocol):
    """
    Protocol for configuration builders.
    
    Builders create AggregationSettings from various sources.
    """
    
    def build(self) -> AggregationSettings:  # type: ignore[name-defined]
        """
        Build and return AggregationSettings.
        
        Returns:
            Validated AggregationSettings instance
        """
        ...
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate the configuration can be built.
        
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        ...


# Constants for validation
MIN_SCORE = 0.0
MAX_SCORE = 3.0
MIN_WEIGHT = 0.0
MAX_WEIGHT = 1.0
WEIGHT_SUM_TOLERANCE = 1e-6  # Tolerance for weight sum == 1.0


def is_valid_score(score: Score) -> bool:
    """Check if score is in valid range [0.0, 3.0]."""
    return MIN_SCORE <= score <= MAX_SCORE


def is_valid_weight(weight: Weight) -> bool:
    """Check if weight is in valid range [0.0, 1.0]."""
    return MIN_WEIGHT <= weight <= MAX_WEIGHT


def are_weights_normalized(weights: list[Weight]) -> bool:
    """Check if weights sum to 1.0 (within tolerance)."""
    if not weights:
        return False
    weight_sum = sum(weights)
    return abs(weight_sum - 1.0) < WEIGHT_SUM_TOLERANCE


__all__ = [
    # Type aliases
    "PolicyAreaID",
    "DimensionID",
    "QuestionID",
    "ClusterID",
    "Score",
    "Weight",
    "AggregationMethod",
    "QualityLevel",
    # Protocols
    "IAggregator",
    "IConfigBuilder",
    # Constants
    "MIN_SCORE",
    "MAX_SCORE",
    "MIN_WEIGHT",
    "MAX_WEIGHT",
    "WEIGHT_SUM_TOLERANCE",
    # Validation functions
    "is_valid_score",
    "is_valid_weight",
    "are_weights_normalized",
]
