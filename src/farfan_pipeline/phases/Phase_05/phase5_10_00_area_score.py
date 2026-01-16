from __future__ import annotations

"""
Phase 5 Data Model - AreaScore

This module defines the AreaScore dataclass for Phase 5 output.
Phase 5 aggregates 60 DimensionScore objects into 10 AreaScore objects.

Module: src/farfan_pipeline/phases/Phase_5/phase5_10_00_area_score.py
Purpose: Define AreaScore data model for Phase 5
Owner: phase5_10
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-13
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 5
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13T00:00:00Z"
__modified__ = "2026-01-13T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

from dataclasses import dataclass, field
from typing import Any

# Import DimensionScore from Phase 4
from farfan_pipeline.phases.Phase_04 import DimensionScore


@dataclass
class AreaScore:
    """
    Policy Area Score - Output of Phase 5.
    
    Represents an aggregated score for one policy area (PA01-PA10),
    combining 6 dimension scores into a single area-level assessment.
    
    Attributes:
        area_id: Policy area identifier (e.g., "PA01")
        area_name: Human-readable policy area name
        score: Aggregated area score [0.0, 3.0]
        quality_level: Quality classification (EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE)
        dimension_scores: List of 6 DimensionScore objects that contributed
        validation_passed: Whether validation checks passed
        validation_details: Details of validation results
        cluster_id: Optional cluster assignment (used by Phase 6)
        score_std: Standard deviation of the score (from bootstrap)
        confidence_interval_95: 95% confidence interval (from bootstrap)
        provenance_node_id: Provenance DAG node identifier
        aggregation_method: Method used (e.g., "weighted_average", "choquet")
    """
    
    area_id: str
    area_name: str
    score: float
    quality_level: str
    dimension_scores: list[DimensionScore] = field(default_factory=list)
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    cluster_id: str | None = None
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"
    
    def __post_init__(self):
        """Validate AreaScore invariants."""
        # Validate score bounds
        if not (0.0 <= self.score <= 3.0):
            raise ValueError(f"AreaScore score must be in [0.0, 3.0], got {self.score}")
        
        # Validate area_id format
        if not self.area_id.startswith("PA"):
            raise ValueError(f"AreaScore area_id must start with 'PA', got {self.area_id}")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "area_id": self.area_id,
            "area_name": self.area_name,
            "score": self.score,
            "quality_level": self.quality_level,
            "dimension_scores": [
                {
                    "dimension_id": ds.dimension_id,
                    "area_id": ds.area_id,
                    "score": ds.score,
                    "quality_level": ds.quality_level,
                }
                for ds in self.dimension_scores
            ],
            "validation_passed": self.validation_passed,
            "validation_details": self.validation_details,
            "cluster_id": self.cluster_id,
            "score_std": self.score_std,
            "confidence_interval_95": self.confidence_interval_95,
            "provenance_node_id": self.provenance_node_id,
            "aggregation_method": self.aggregation_method,
        }
