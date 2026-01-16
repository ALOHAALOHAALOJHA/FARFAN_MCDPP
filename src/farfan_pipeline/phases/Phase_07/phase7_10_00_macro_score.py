from __future__ import annotations

"""
Phase 7 Data Model - MacroScore

This module defines the MacroScore dataclass for Phase 7 output.
Phase 7 aggregates 4 ClusterScore objects into 1 MacroScore object (holistic evaluation).

Module: src/farfan_pipeline/phases/Phase_7/phase7_10_00_macro_score.py
Purpose: Define MacroScore data model for Phase 7
Owner: phase7_10
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-13
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 7
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13T00:00:00Z"
__modified__ = "2026-01-13T00:00:00Z"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Per-Task"

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_06.phase6_10_00_cluster_score import ClusterScore


@dataclass
class MacroScore:
    """
    MACRO-Level Holistic Score - Output of Phase 7.
    
    Represents the final holistic evaluation combining 4 MESO-level cluster scores
    into a single comprehensive assessment with cross-cutting coherence analysis,
    systemic gap detection, and strategic alignment metrics.
    
    Cluster Aggregation:
        - CLUSTER_MESO_1 (PA01-PA03) + CLUSTER_MESO_2 (PA04-PA06) +
        - CLUSTER_MESO_3 (PA07-PA08) + CLUSTER_MESO_4 (PA09-PA10) → MacroScore
    
    Attributes:
        evaluation_id: Unique evaluation identifier
        score: Holistic macro score [0.0, 3.0]
        score_normalized: Normalized score [0.0, 1.0]
        quality_level: Quality classification (EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE)
        cross_cutting_coherence: Cross-cutting coherence metric [0.0, 1.0]
        coherence_breakdown: Detailed coherence analysis
        systemic_gaps: List of policy area IDs with systemic gaps
        gap_severity: Mapping of area ID to severity (CRITICAL/SEVERE/MODERATE)
        strategic_alignment: Strategic alignment score [0.0, 1.0]
        alignment_breakdown: Detailed alignment analysis
        cluster_scores: List of ClusterScore objects that contributed
        cluster_details: Summary details of each cluster
        validation_passed: Whether validation checks passed
        validation_details: Details of validation results
        score_std: Standard deviation of the score
        confidence_interval_95: 95% confidence interval
        provenance_node_id: Provenance DAG node identifier
        aggregation_method: Method used (e.g., "weighted_average")
        evaluation_timestamp: When the evaluation was performed
        pipeline_version: Version of the pipeline used
    """
    
    evaluation_id: str
    score: float
    score_normalized: float
    quality_level: str
    cross_cutting_coherence: float
    coherence_breakdown: dict[str, Any] = field(default_factory=dict)
    systemic_gaps: list[str] = field(default_factory=list)
    gap_severity: dict[str, str] = field(default_factory=dict)
    strategic_alignment: float = 0.0
    alignment_breakdown: dict[str, Any] = field(default_factory=dict)
    cluster_scores: list["ClusterScore"] = field(default_factory=list)
    cluster_details: dict[str, Any] = field(default_factory=dict)
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"
    evaluation_timestamp: str = ""
    pipeline_version: str = "1.0.0"
    
    def __post_init__(self):
        """Validate MacroScore invariants."""
        # Validate score bounds
        if not (0.0 <= self.score <= 3.0):
            raise ValueError(f"MacroScore score must be in [0.0, 3.0], got {self.score}")
        
        # Validate normalized score bounds
        if not (0.0 <= self.score_normalized <= 1.0):
            raise ValueError(f"MacroScore score_normalized must be in [0.0, 1.0], got {self.score_normalized}")
        
        # Validate coherence bounds
        if not (0.0 <= self.cross_cutting_coherence <= 1.0):
            raise ValueError(f"MacroScore cross_cutting_coherence must be in [0.0, 1.0], got {self.cross_cutting_coherence}")
        
        # Validate strategic alignment bounds
        if not (0.0 <= self.strategic_alignment <= 1.0):
            raise ValueError(f"MacroScore strategic_alignment must be in [0.0, 1.0], got {self.strategic_alignment}")
        
        # Validate quality level
        valid_levels = {"EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"}
        if self.quality_level not in valid_levels:
            raise ValueError(f"MacroScore quality_level must be one of {valid_levels}, got {self.quality_level}")
        
        # Set evaluation_timestamp if not provided
        if not self.evaluation_timestamp:
            self.evaluation_timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "evaluation_id": self.evaluation_id,
            "score": self.score,
            "score_normalized": self.score_normalized,
            "quality_level": self.quality_level,
            "cross_cutting_coherence": self.cross_cutting_coherence,
            "coherence_breakdown": self.coherence_breakdown,
            "systemic_gaps": self.systemic_gaps,
            "gap_severity": self.gap_severity,
            "strategic_alignment": self.strategic_alignment,
            "alignment_breakdown": self.alignment_breakdown,
            "cluster_scores": [
                {
                    "cluster_id": cs.cluster_id,
                    "score": cs.score,
                    "coherence": cs.coherence,
                    "dispersion_scenario": cs.dispersion_scenario,
                    "penalty_applied": cs.penalty_applied,
                }
                for cs in self.cluster_scores
            ],
            "cluster_details": self.cluster_details,
            "validation_passed": self.validation_passed,
            "validation_details": self.validation_details,
            "score_std": self.score_std,
            "confidence_interval_95": self.confidence_interval_95,
            "provenance_node_id": self.provenance_node_id,
            "aggregation_method": self.aggregation_method,
            "evaluation_timestamp": self.evaluation_timestamp,
            "pipeline_version": self.pipeline_version,
        }
