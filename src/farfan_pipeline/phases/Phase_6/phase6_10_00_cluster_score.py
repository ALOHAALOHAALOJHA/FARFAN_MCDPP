from __future__ import annotations

"""
Phase 6 Data Model - ClusterScore

This module defines the ClusterScore dataclass for Phase 6 output.
Phase 6 aggregates 10 AreaScore objects into 4 ClusterScore objects.

Module: src/farfan_pipeline/phases/Phase_6/phase6_10_00_cluster_score.py
Purpose: Define ClusterScore data model for Phase 6
Owner: phase6_10
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-13
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 6
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13T00:00:00Z"
__modified__ = "2026-01-13T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_5.phase5_10_00_area_score import AreaScore


@dataclass
class ClusterScore:
    """
    MESO-Level Cluster Score - Output of Phase 6.
    
    Represents an aggregated score for one of 4 clusters (CLUSTER_MESO_1 to CLUSTER_MESO_4),
    combining 2-3 policy area scores into a single cluster-level assessment with
    adaptive penalty based on dispersion analysis.
    
    Cluster Composition:
        - CLUSTER_MESO_1: PA01, PA02, PA03 (3 areas)
        - CLUSTER_MESO_2: PA04, PA05, PA06 (3 areas)
        - CLUSTER_MESO_3: PA07, PA08 (2 areas)
        - CLUSTER_MESO_4: PA09, PA10 (2 areas)
    
    Attributes:
        cluster_id: Cluster identifier (e.g., "CLUSTER_MESO_1")
        cluster_name: Human-readable cluster name
        areas: List of policy area IDs in this cluster
        score: Aggregated cluster score [0.0, 3.0] (after adaptive penalty)
        coherence: Cluster coherence metric [0.0, 1.0]
        variance: Variance across area scores
        weakest_area: ID of the lowest-scoring area in cluster
        area_scores: List of AreaScore objects that contributed
        validation_passed: Whether validation checks passed
        validation_details: Details of validation results
        score_std: Standard deviation of the score
        confidence_interval_95: 95% confidence interval
        provenance_node_id: Provenance DAG node identifier
        aggregation_method: Method used (e.g., "weighted_average")
        dispersion_scenario: Dispersion classification (convergence/moderate/high/extreme)
        penalty_applied: Penalty amount applied for dispersion [0.0, 1.0]
    """
    
    cluster_id: str
    cluster_name: str
    areas: list[str]
    score: float
    coherence: float
    variance: float
    weakest_area: str | None
    area_scores: list[Any] = field(default_factory=list)  # List[AreaScore]
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"
    dispersion_scenario: str = "moderate"
    penalty_applied: float = 0.0
    
    def __post_init__(self):
        """Validate ClusterScore invariants."""
        # Validate score bounds
        if not (0.0 <= self.score <= 3.0):
            raise ValueError(f"ClusterScore score must be in [0.0, 3.0], got {self.score}")
        
        # Validate cluster_id format
        if not self.cluster_id.startswith("CLUSTER_MESO_"):
            raise ValueError(f"ClusterScore cluster_id must start with 'CLUSTER_MESO_', got {self.cluster_id}")
        
        # Validate coherence bounds
        if not (0.0 <= self.coherence <= 1.0):
            raise ValueError(f"ClusterScore coherence must be in [0.0, 1.0], got {self.coherence}")
        
        # Validate penalty bounds
        if not (0.0 <= self.penalty_applied <= 1.0):
            raise ValueError(f"ClusterScore penalty_applied must be in [0.0, 1.0], got {self.penalty_applied}")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "cluster_id": self.cluster_id,
            "cluster_name": self.cluster_name,
            "areas": self.areas,
            "score": self.score,
            "coherence": self.coherence,
            "variance": self.variance,
            "weakest_area": self.weakest_area,
            "area_scores": [
                {
                    "area_id": area.area_id,
                    "score": area.score,
                    "quality_level": area.quality_level,
                }
                for area in self.area_scores
            ],
            "validation_passed": self.validation_passed,
            "validation_details": self.validation_details,
            "score_std": self.score_std,
            "confidence_interval_95": self.confidence_interval_95,
            "provenance_node_id": self.provenance_node_id,
            "aggregation_method": self.aggregation_method,
            "dispersion_scenario": self.dispersion_scenario,
            "penalty_applied": self.penalty_applied,
        }
