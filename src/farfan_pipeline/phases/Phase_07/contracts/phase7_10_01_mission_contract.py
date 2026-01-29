"""
Phase 7 Mission Contract

Defines the mission and invariants for Phase 7 Macro Evaluation.

Contract ID: CONTRACT-P7-MISSION
Phase: 7 (Macro Evaluation)
Effective Date: 2026-01-13
Version: 1.0.0
"""


class Phase7MissionContract:
    """
    Mission contract for Phase 7.
    
    Mission Statement:
        Phase 7 synthesizes 4 MESO-level Cluster scores into a comprehensive
        MacroScore, enriched with cross-cutting coherence analysis, systemic gap
        detection, and strategic alignment metrics to enable evidence-based
        policy prioritization.
    
    Invariants:
        INV-7.1: Cluster weights are fixed and normalized (sum to 1.0)
        INV-7.2: Quality thresholds are immutable
        INV-7.3: Score domain is [0.0, 3.0]
        INV-7.4: Coherence weights sum to 1.0
        INV-7.5: Aggregation is deterministic (same inputs → same outputs)
    
    Transformation:
        4 ClusterScore → 1 MacroScore (4:1 compression, final aggregation tier)
    
    Features:
        - Weighted averaging of cluster scores
        - Cross-Cutting Coherence Analysis (CCCA)
        - Systemic Gap Detection (SGD)
        - Strategic Alignment Scoring (SAS)
        - Uncertainty propagation
        - Complete provenance tracking
    """
    
    # INV-7.1: Cluster weights (equal weights by default)
    CLUSTER_WEIGHTS = {
        "CLUSTER_MESO_1": 0.25,
        "CLUSTER_MESO_2": 0.25,
        "CLUSTER_MESO_3": 0.25,
        "CLUSTER_MESO_4": 0.25,
    }
    
    # INV-7.2: Quality thresholds (normalized scale)
    QUALITY_THRESHOLDS = {
        "EXCELENTE": 0.85,      # ≥ 85% → ≥ 2.55 on 3-point scale
        "BUENO": 0.70,          # ≥ 70% → ≥ 2.10
        "ACEPTABLE": 0.55,      # ≥ 55% → ≥ 1.65
        "INSUFICIENTE": 0.0,    # < 55% → < 1.65
    }
    
    # INV-7.3: Score domain
    SCORE_MIN = 0.0
    SCORE_MAX = 3.0
    
    # INV-7.4: Coherence weights
    COHERENCE_WEIGHTS = {
        "strategic": 0.40,      # Strategic coherence weight
        "operational": 0.30,    # Operational coherence weight
        "institutional": 0.30,  # Institutional coherence weight
    }
    
    # Transformation specification
    INPUT_COUNT = 4         # 4 ClusterScore objects
    OUTPUT_COUNT = 1        # 1 MacroScore object
    COMPRESSION_RATIO = "4:1"
    
    # Expected input cluster identifiers
    EXPECTED_CLUSTERS = [
        "CLUSTER_MESO_1",  # PA01-PA03
        "CLUSTER_MESO_2",  # PA04-PA06
        "CLUSTER_MESO_3",  # PA07-PA08
        "CLUSTER_MESO_4",  # PA09-PA10
    ]
    
    # Systemic gap detection threshold
    GAP_THRESHOLD = 1.65  # 0.55 on normalized scale
    
    @staticmethod
    def validate_invariants() -> tuple[bool, str]:
        """
        Validate mission contract invariants.
        
        Returns:
            (is_valid, error_message)
        """
        # INV-7.1: Cluster weights sum to 1.0
        weight_sum = sum(Phase7MissionContract.CLUSTER_WEIGHTS.values())
        if abs(weight_sum - 1.0) > 1e-6:
            return False, f"Cluster weights must sum to 1.0, got {weight_sum}"
        
        # INV-7.4: Coherence weights sum to 1.0
        coherence_sum = sum(Phase7MissionContract.COHERENCE_WEIGHTS.values())
        if abs(coherence_sum - 1.0) > 1e-6:
            return False, f"Coherence weights must sum to 1.0, got {coherence_sum}"
        
        # INV-7.2: Quality thresholds are properly ordered
        thresholds = Phase7MissionContract.QUALITY_THRESHOLDS
        if not (thresholds["EXCELENTE"] > thresholds["BUENO"] > thresholds["ACEPTABLE"]):
            return False, "Quality thresholds are not properly ordered"
        
        return True, "All invariants satisfied"


# Validate invariants on module load
_is_valid, _error_msg = Phase7MissionContract.validate_invariants()
if not _is_valid:
    raise RuntimeError(f"Phase 7 mission contract invariant violation: {_error_msg}")
