"""
Phase 6 Mission Contract

This contract defines the mission, invariants, and topological order for Phase 6.

Mission:
--------
Aggregate 10 Policy Area scores into 4 MESO-level Cluster scores with adaptive
penalty based on dispersion analysis.

Topological Order:
------------------
1. phase6_10_00_phase_6_constants.py - Constants and configuration
2. phase6_10_00_cluster_score.py - ClusterScore data model
3. phase6_20_00_adaptive_meso_scoring.py - Adaptive penalty logic
4. phase6_30_00_cluster_aggregator.py - Main aggregation logic

Module: src/farfan_pipeline/phases/Phase_06/contracts/phase6_mission_contract.py
Phase: 6 (Cluster Aggregation - MESO)
Owner: phase6_contracts
"""

from __future__ import annotations

__version__ = "1.0.0"
__phase__ = 6
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"

from enum import Enum
from typing import Any
import logging

logger = logging.getLogger(__name__)


class Phase6Stage(Enum):
    """Phase 6 execution stages."""
    CONSTANTS = 10  # Constants and configuration
    DATA_MODEL = 10  # ClusterScore definition
    ADAPTIVE_PENALTY = 20  # Adaptive meso-level scoring
    AGGREGATION = 30  # Main cluster aggregation


class Phase6Invariants:
    """
    Phase 6 Mission Invariants.
    
    These are the non-negotiable guarantees that Phase 6 must uphold.
    """
    
    # Cluster configuration
    CLUSTER_COUNT = 4
    CLUSTER_IDS = ["CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"]
    
    CLUSTER_COMPOSITION = {
        "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],  # 3 areas
        "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],  # 3 areas
        "CLUSTER_MESO_3": ["PA07", "PA08"],          # 2 areas
        "CLUSTER_MESO_4": ["PA09", "PA10"],          # 2 areas
    }
    
    # Score constraints
    MIN_SCORE = 0.0
    MAX_SCORE = 3.0
    
    # Dispersion thresholds
    CV_CONVERGENCE = 0.2   # CV < 0.2 = convergence
    CV_MODERATE = 0.4      # CV < 0.4 = moderate
    CV_HIGH = 0.6          # CV < 0.6 = high
    # CV >= 0.6 = extreme
    
    @classmethod
    def validate_output_count(cls, cluster_scores: list[Any]) -> bool:
        """I1: Validate exactly 4 cluster scores produced."""
        return len(cluster_scores) == cls.CLUSTER_COUNT
    
    @classmethod
    def validate_cluster_ids(cls, cluster_scores: list[Any]) -> bool:
        """I2: Validate cluster IDs are correct."""
        cluster_ids = {cs.cluster_id for cs in cluster_scores}
        return cluster_ids == set(cls.CLUSTER_IDS)
    
    @classmethod
    def validate_cluster_hermeticity(cls, cluster_score: Any) -> bool:
        """I3: Validate cluster contains all expected policy areas."""
        cluster_id = cluster_score.cluster_id
        expected_areas = set(cls.CLUSTER_COMPOSITION.get(cluster_id, []))
        actual_areas = set(cluster_score.areas)
        return actual_areas == expected_areas
    
    @classmethod
    def validate_score_bounds(cls, score: float) -> bool:
        """I4: Validate score is within [0.0, 3.0]."""
        return cls.MIN_SCORE <= score <= cls.MAX_SCORE
    
    @classmethod
    def validate_coherence_bounds(cls, coherence: float) -> bool:
        """I5: Validate coherence is within [0.0, 1.0]."""
        return 0.0 <= coherence <= 1.0
    
    @classmethod
    def validate_penalty_bounds(cls, penalty: float) -> bool:
        """I6: Validate penalty is within [0.0, 1.0]."""
        return 0.0 <= penalty <= 1.0
    
    @classmethod
    def validate_all(cls, cluster_scores: list[Any]) -> tuple[bool, dict[str, Any]]:
        """
        Validate all Phase 6 invariants.
        
        Returns:
            Tuple of (all_passed, validation_details)
        """
        validation_details = {
            "invariants_checked": [],
            "failures": []
        }
        
        # I1: Count
        if not cls.validate_output_count(cluster_scores):
            validation_details["failures"].append(
                f"I1: Expected {cls.CLUSTER_COUNT} clusters, got {len(cluster_scores)}"
            )
        else:
            validation_details["invariants_checked"].append("I1: Output count = 4")
        
        # I2: Cluster IDs
        if not cls.validate_cluster_ids(cluster_scores):
            validation_details["failures"].append(
                "I2: Invalid cluster IDs"
            )
        else:
            validation_details["invariants_checked"].append("I2: Cluster IDs valid")
        
        # I3-I6: Per-cluster validations
        for cs in cluster_scores:
            # I3: Hermeticity
            if not cls.validate_cluster_hermeticity(cs):
                validation_details["failures"].append(
                    f"I3: {cs.cluster_id} has incorrect policy areas"
                )
            
            # I4: Score bounds
            if not cls.validate_score_bounds(cs.score):
                validation_details["failures"].append(
                    f"I4: {cs.cluster_id} score {cs.score} out of bounds"
                )
            
            # I5: Coherence bounds
            if hasattr(cs, 'coherence') and not cls.validate_coherence_bounds(cs.coherence):
                validation_details["failures"].append(
                    f"I5: {cs.cluster_id} coherence {cs.coherence} out of bounds"
                )
            
            # I6: Penalty bounds
            if hasattr(cs, 'penalty_applied') and not cls.validate_penalty_bounds(cs.penalty_applied):
                validation_details["failures"].append(
                    f"I6: {cs.cluster_id} penalty {cs.penalty_applied} out of bounds"
                )
        
        if not validation_details["failures"]:
            validation_details["invariants_checked"].extend([
                "I3: All clusters hermetic",
                "I4: All scores in bounds",
                "I5: All coherence values in bounds",
                "I6: All penalties in bounds"
            ])
        
        all_passed = len(validation_details["failures"]) == 0
        validation_details["passed"] = all_passed
        
        return all_passed, validation_details


TOPOLOGICAL_ORDER = [
    {
        "file": "phase6_10_00_phase_6_constants.py",
        "stage": 10,
        "description": "Constants and cluster composition",
        "dependencies": [],
    },
    {
        "file": "phase6_10_00_cluster_score.py",
        "stage": 10,
        "description": "ClusterScore data model",
        "dependencies": [],
    },
    {
        "file": "phase6_20_00_adaptive_meso_scoring.py",
        "stage": 20,
        "description": "Adaptive penalty mechanism",
        "dependencies": ["phase6_10_00_phase_6_constants.py"],
    },
    {
        "file": "phase6_30_00_cluster_aggregator.py",
        "stage": 30,
        "description": "Main cluster aggregation logic",
        "dependencies": [
            "phase6_10_00_phase_6_constants.py",
            "phase6_10_00_cluster_score.py",
            "phase6_20_00_adaptive_meso_scoring.py",
        ],
    },
]


MISSION_STATEMENT = """
Phase 6 Mission: Aggregate 10 Policy Area scores into 4 MESO-level Cluster scores.

Compression Ratio: 10:4 (2.5:1)

Process:
1. PRECONDITION: Validate input via Phase6InputContract
2. Group 10 AreaScore objects by cluster assignment (area_id-based routing)
3. For each cluster, compute weighted average of area scores
4. Analyze dispersion within cluster (CV, DI, variance)
5. Apply adaptive penalty based on dispersion scenario
6. POSTCONDITION: Validate output via Phase6OutputContract
7. Produce 4 ClusterScore objects with full metadata

Contract Enforcement (configurable):
- Mode "strict": Raise ValueError on violation (default)
- Mode "warn": Log and continue
- Mode "disabled": Skip validation

Guarantees:
- Exactly 4 clusters produced (I1)
- All clusters hermetic (I3)
- All scores in [0.0, 3.0] (I4)
- Full provenance tracking
- Dispersion-based quality assessment
"""
