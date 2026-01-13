"""
Phase 7 Input Contract

Defines the input contract for Phase 7 Macro Evaluation.

Contract ID: CONTRACT-P7-INPUT
Phase: 7 (Macro Evaluation)
Effective Date: 2026-01-13
Version: 1.0.0
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_6.phase6_10_00_cluster_score import ClusterScore


class Phase7InputContract:
    """
    Input contract specification for Phase 7.
    
    Preconditions:
        PRE-7.1: Input contains exactly 4 ClusterScore objects
        PRE-7.2: All clusters MESO_1 through MESO_4 are represented
        PRE-7.3: Each cluster_score.score ∈ [0.0, 3.0]
        PRE-7.4: Each cluster_score has valid provenance from Phase 6
        PRE-7.5: No duplicate cluster identifiers
        PRE-7.6: Each cluster contains coherence and dispersion metrics
    """
    
    EXPECTED_INPUT_COUNT = 4
    EXPECTED_CLUSTER_IDS = {
        "CLUSTER_MESO_1",
        "CLUSTER_MESO_2",
        "CLUSTER_MESO_3",
        "CLUSTER_MESO_4",
    }
    MIN_SCORE = 0.0
    MAX_SCORE = 3.0
    
    @staticmethod
    def validate(cluster_scores: list["ClusterScore"]) -> tuple[bool, str]:
        """
        Validate Phase 7 input contract.
        
        Args:
            cluster_scores: List of ClusterScore objects from Phase 6
            
        Returns:
            (is_valid, error_message)
        """
        # PRE-7.1: Count validation
        if len(cluster_scores) != Phase7InputContract.EXPECTED_INPUT_COUNT:
            return False, f"Expected 4 ClusterScores, got {len(cluster_scores)}"
        
        # PRE-7.2: Coverage validation
        actual_clusters = {cs.cluster_id for cs in cluster_scores}
        expected_clusters = Phase7InputContract.EXPECTED_CLUSTER_IDS
        if actual_clusters != expected_clusters:
            missing = expected_clusters - actual_clusters
            extra = actual_clusters - expected_clusters
            return False, f"Cluster mismatch. Missing: {missing}, Extra: {extra}"
        
        # PRE-7.3: Score bounds validation
        for cs in cluster_scores:
            if not (Phase7InputContract.MIN_SCORE <= cs.score <= Phase7InputContract.MAX_SCORE):
                return False, f"ClusterScore {cs.cluster_id} score out of bounds: {cs.score}"
        
        # PRE-7.5: Uniqueness validation
        if len(actual_clusters) != Phase7InputContract.EXPECTED_INPUT_COUNT:
            return False, "Duplicate cluster identifiers detected"
        
        # PRE-7.6: Metric completeness
        for cs in cluster_scores:
            if not hasattr(cs, 'coherence') or cs.coherence is None:
                return False, f"ClusterScore {cs.cluster_id} missing coherence metric"
            if not hasattr(cs, 'variance'):
                return False, f"ClusterScore {cs.cluster_id} missing variance metric"
        
        return True, "All preconditions satisfied"


def validate_phase7_input(cluster_scores: list["ClusterScore"]) -> None:
    """
    Validate Phase 7 input and raise exception if invalid.
    
    Args:
        cluster_scores: List of ClusterScore objects
        
    Raises:
        ValueError: If input contract is violated
    """
    is_valid, error_msg = Phase7InputContract.validate(cluster_scores)
    if not is_valid:
        raise ValueError(f"Phase 7 input contract violation: {error_msg}")
