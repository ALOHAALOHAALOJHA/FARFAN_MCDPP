"""
Phase 7 Output Contract

Defines the output contract for Phase 7 Macro Evaluation.

Contract ID: CONTRACT-P7-OUTPUT
Phase: 7 (Macro Evaluation)
Effective Date: 2026-01-13
Version: 1.0.0
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_7.phase7_10_00_macro_score import MacroScore


class Phase7OutputContract:
    """
    Output contract specification for Phase 7.
    
    Postconditions:
        POST-7.1: Output is a valid MacroScore object
        POST-7.2: macro_score.score ∈ [0.0, 3.0]
        POST-7.3: macro_score.quality_level is a valid QualityLevel
        POST-7.4: macro_score.cross_cutting_coherence ∈ [0.0, 1.0]
        POST-7.5: macro_score.strategic_alignment ∈ [0.0, 1.0]
        POST-7.6: Provenance chain references all 4 input clusters
        POST-7.7: systemic_gaps contains only valid area identifiers
    """
    
    MIN_SCORE = 0.0
    MAX_SCORE = 3.0
    VALID_QUALITY_LEVELS = {"EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"}
    VALID_AREAS = {f"PA{i:02d}" for i in range(1, 11)}
    
    @staticmethod
    def validate(macro_score: "MacroScore", input_cluster_ids: set[str]) -> tuple[bool, str]:
        """
        Validate Phase 7 output contract.
        
        Args:
            macro_score: MacroScore object produced by Phase 7
            input_cluster_ids: Set of cluster IDs from input
            
        Returns:
            (is_valid, error_message)
        """
        # POST-7.1: Type validation
        if not hasattr(macro_score, 'score'):
            return False, "Output must be a valid MacroScore object"
        
        # POST-7.2: Score bounds
        if not (Phase7OutputContract.MIN_SCORE <= macro_score.score <= Phase7OutputContract.MAX_SCORE):
            return False, f"MacroScore score out of bounds: {macro_score.score}"
        
        # POST-7.3: Quality level validation
        if macro_score.quality_level not in Phase7OutputContract.VALID_QUALITY_LEVELS:
            return False, f"Invalid quality level: {macro_score.quality_level}"
        
        # POST-7.4: Coherence bounds
        if not (0.0 <= macro_score.cross_cutting_coherence <= 1.0):
            return False, f"Coherence out of bounds: {macro_score.cross_cutting_coherence}"
        
        # POST-7.5: Alignment bounds
        if not (0.0 <= macro_score.strategic_alignment <= 1.0):
            return False, f"Alignment out of bounds: {macro_score.strategic_alignment}"
        
        # POST-7.6: Provenance traceability
        contributing_clusters = {cs.cluster_id for cs in macro_score.cluster_scores}
        if contributing_clusters != input_cluster_ids:
            return False, f"Provenance mismatch: expected {input_cluster_ids}, got {contributing_clusters}"
        
        # POST-7.7: Gap validity
        for gap in macro_score.systemic_gaps:
            if gap not in Phase7OutputContract.VALID_AREAS:
                return False, f"Invalid area in systemic_gaps: {gap}"
        
        return True, "All postconditions satisfied"


def validate_phase7_output(macro_score: "MacroScore", input_cluster_ids: set[str]) -> None:
    """
    Validate Phase 7 output and raise exception if invalid.
    
    Args:
        macro_score: MacroScore object
        input_cluster_ids: Set of cluster IDs from input
        
    Raises:
        ValueError: If output contract is violated
    """
    is_valid, error_msg = Phase7OutputContract.validate(macro_score, input_cluster_ids)
    if not is_valid:
        raise ValueError(f"Phase 7 output contract violation: {error_msg}")
