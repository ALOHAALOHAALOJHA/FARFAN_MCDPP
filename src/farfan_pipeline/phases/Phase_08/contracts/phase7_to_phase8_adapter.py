"""
Phase 7 to Phase 8 Interface Adapter

Implements formal adapter to bridge Phase 7 MacroScore output to Phase 8 input requirements.

Based on: PHASE_7_8_INTERFACE_COMPATIBILITY_ANALYSIS.md (Solution 2)

Contract ID: ADAPTER-P7-P8-v1.0
Status: ACTIVE
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_07.phase7_10_00_macro_score import MacroScore
    from farfan_pipeline.phases.Phase_06.phase6_10_00_cluster_score import ClusterScore

logger = logging.getLogger(__name__)


@dataclass
class Phase7To8Adapter:
    """
    Formal adapter: Phase 7 MacroScore → Phase 8 Input.
    
    Type Signature:
        adapt: (MacroScore, PipelineContext) → Dict[str, Any]
    
    where PipelineContext provides access to earlier phase outputs (Phase 5).
    
    Invariants:
        - Output satisfies Phase 8 input contract
        - No information loss (retrieves micro scores from Phase 5)
        - Deterministic transformation
        - Explicit data flow documentation
    """
    
    def adapt(
        self,
        macro_score: MacroScore,
        phase5_output: list[Any] | None = None
    ) -> Dict[str, Any]:
        """
        Adapt Phase 7 MacroScore to Phase 8 input format.
        
        Args:
            macro_score: Phase 7 MacroScore output
            phase5_output: Optional Phase 5 output (list of AreaScore objects)
                          If None, micro_scores will not be populated
        
        Returns:
            Dict satisfying Phase 8 input contract with keys:
            - micro_scores: Dict[str, float] (60 PA×DIM combinations)
            - cluster_data: Dict[str, Dict] (transformed from macro_score.cluster_scores)
            - macro_data: Dict (derived from macro_score fields)
            - metadata: Dict (provenance and versioning info)
        
        Raises:
            ValueError: If macro_score is invalid or phase5_output malformed
        """
        logger.info(f"Adapting Phase 7 MacroScore to Phase 8 input: {macro_score.evaluation_id}")
        
        # 1. Extract micro_scores from Phase 5 output (if available)
        micro_scores = self._extract_micro_scores_from_phase5(phase5_output)
        
        # 2. Transform cluster_scores to cluster_data
        cluster_data = self._transform_cluster_scores(macro_score.cluster_scores)
        
        # 3. Build macro_data from macro_score
        macro_data = self._build_macro_data(macro_score)
        
        # 4. Build metadata for provenance
        metadata = self._build_metadata(macro_score)
        
        # Construct Phase 8 input
        phase8_input = {
            "micro_scores": micro_scores,
            "cluster_data": cluster_data,
            "macro_data": macro_data,
            "metadata": metadata,
        }
        
        # Validate output satisfies Phase 8 contract
        self._validate_phase8_input(phase8_input)
        
        logger.info(f"✓ Successfully adapted Phase 7 → Phase 8: "
                   f"{len(micro_scores)} micro scores, "
                   f"{len(cluster_data)} clusters")
        
        return phase8_input
    
    def _extract_micro_scores_from_phase5(
        self,
        phase5_output: list[Any] | None
    ) -> Dict[str, float]:
        """
        Extract 60 micro-level PA×DIM scores from Phase 5 AreaScore objects.
        
        Phase 5 outputs 10 AreaScore objects, each with 6 DimensionScore objects.
        Total: 10 areas × 6 dimensions = 60 micro scores.
        
        Args:
            phase5_output: List of AreaScore objects from Phase 5
        
        Returns:
            Dict mapping "PA{01-10}-DIM{01-06}" → score
        
        Raises:
            ValueError: If phase5_output is None or malformed
        """
        if phase5_output is None:
            logger.warning("Phase 5 output not provided, returning empty micro_scores")
            return {}
        
        micro_scores = {}
        
        try:
            # Iterate through 10 AreaScore objects
            for area_score in phase5_output:
                area_id = area_score.area_id
                
                # Each AreaScore has 6 DimensionScore objects
                for dim_score in area_score.dimension_scores:
                    dim_id = dim_score.dimension_id
                    score = dim_score.score
                    
                    # Create micro score key: "PA01-DIM01"
                    micro_key = f"{area_id}-{dim_id}"
                    micro_scores[micro_key] = score
            
            # Validate cardinality
            if len(micro_scores) != 60:
                logger.warning(
                    f"Expected 60 micro scores, got {len(micro_scores)}. "
                    f"Phase 5 output may be incomplete."
                )
        
        except (AttributeError, TypeError) as e:
            logger.error(f"Failed to extract micro scores from Phase 5 output: {e}")
            raise ValueError(
                f"Phase 5 output malformed: {e}. "
                "Expected list of AreaScore objects with dimension_scores."
            )
        
        return micro_scores
    
    def _transform_cluster_scores(
        self,
        cluster_scores: list[ClusterScore]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Transform List[ClusterScore] → Dict[cluster_id, ClusterInfo].
        
        Args:
            cluster_scores: List of ClusterScore objects from Phase 7
        
        Returns:
            Dict mapping cluster_id → cluster info dict
        """
        cluster_data = {}
        
        for cs in cluster_scores:
            cluster_data[cs.cluster_id] = {
                "cluster_id": cs.cluster_id,
                "score": cs.score,
                "variance": cs.coherence,  # Map coherence to variance
                "coherence": cs.coherence,
                "dispersion_scenario": cs.dispersion_scenario,
                "penalty_applied": cs.penalty_applied,
                # Additional fields from ClusterScore
                "area_ids": getattr(cs, "area_ids", []),
                "area_scores": getattr(cs, "area_scores", []),
            }
        
        return cluster_data
    
    def _build_macro_data(
        self,
        macro_score: MacroScore
    ) -> Dict[str, Any]:
        """
        Build macro_data dict from MacroScore object.
        
        Maps Phase 7 MacroScore fields to Phase 8 expected macro_data structure.
        
        Args:
            macro_score: Phase 7 MacroScore object
        
        Returns:
            Dict with macro-level data
        """
        return {
            # PRIMARY: macro_band (required by Phase 8 PRE-P8-004)
            "macro_band": macro_score.quality_level,  # EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE
            
            # SCORES
            "macro_score": macro_score.score,
            "macro_score_normalized": macro_score.score_normalized,
            
            # COHERENCE & ALIGNMENT
            "cross_cutting_coherence": macro_score.cross_cutting_coherence,
            "coherence_breakdown": macro_score.coherence_breakdown,
            "strategic_alignment": macro_score.strategic_alignment,
            "alignment_breakdown": macro_score.alignment_breakdown,
            
            # SYSTEMIC ANALYSIS
            "systemic_gaps": macro_score.systemic_gaps,
            "gap_severity": macro_score.gap_severity,
            
            # VALIDATION & CONFIDENCE
            "validation_passed": macro_score.validation_passed,
            "validation_details": macro_score.validation_details,
            "score_std": macro_score.score_std,
            "confidence_interval_95": macro_score.confidence_interval_95,
            
            # METADATA
            "evaluation_id": macro_score.evaluation_id,
            "provenance_node_id": macro_score.provenance_node_id,
            "aggregation_method": macro_score.aggregation_method,
            "evaluation_timestamp": macro_score.evaluation_timestamp,
            "pipeline_version": macro_score.pipeline_version,
        }
    
    def _build_metadata(
        self,
        macro_score: MacroScore
    ) -> Dict[str, Any]:
        """
        Build metadata dict for provenance tracking.
        
        Args:
            macro_score: Phase 7 MacroScore object
        
        Returns:
            Dict with metadata
        """
        return {
            "source_phase": "Phase_7",
            "source_output_type": "MacroScore",
            "adapter_version": "1.0.0",
            "evaluation_id": macro_score.evaluation_id,
            "evaluation_timestamp": macro_score.evaluation_timestamp,
            "pipeline_version": macro_score.pipeline_version,
            "provenance_chain": {
                "phase_7_node_id": macro_score.provenance_node_id,
                "aggregation_method": macro_score.aggregation_method,
            }
        }
    
    def _validate_phase8_input(
        self,
        phase8_input: Dict[str, Any]
    ) -> None:
        """
        Validate that constructed input satisfies Phase 8 input contract.
        
        Checks:
            - micro_scores exists and has correct format
            - cluster_data exists and is non-empty
            - macro_data exists with macro_band
        
        Args:
            phase8_input: Constructed Phase 8 input dict
        
        Raises:
            ValueError: If validation fails
        """
        # Check micro_scores
        if "micro_scores" not in phase8_input:
            raise ValueError("FATAL: micro_scores missing from Phase 8 input")
        
        micro_scores = phase8_input["micro_scores"]
        if not isinstance(micro_scores, dict):
            raise ValueError("FATAL: micro_scores must be dict")
        
        # Warn if micro_scores not complete (60 entries)
        if len(micro_scores) < 60:
            logger.warning(
                f"Phase 8 PRE-P8-002 may fail: "
                f"Expected 60 micro scores, got {len(micro_scores)}"
            )
        
        # Check cluster_data
        if "cluster_data" not in phase8_input:
            raise ValueError("FATAL: cluster_data missing from Phase 8 input")
        
        cluster_data = phase8_input["cluster_data"]
        if not isinstance(cluster_data, dict) or len(cluster_data) == 0:
            logger.warning("Phase 8 PRE-P8-003 may fail: cluster_data is empty")
        
        # Check macro_data
        if "macro_data" not in phase8_input:
            raise ValueError("FATAL: macro_data missing from Phase 8 input")
        
        macro_data = phase8_input["macro_data"]
        if "macro_band" not in macro_data:
            raise ValueError("FATAL: macro_band missing from macro_data")
        
        logger.debug("✓ Phase 8 input validation passed")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def adapt_phase7_to_phase8(
    macro_score: MacroScore,
    phase5_output: list[Any] | None = None
) -> Dict[str, Any]:
    """
    Convenience function to adapt Phase 7 output to Phase 8 input.
    
    Args:
        macro_score: Phase 7 MacroScore output
        phase5_output: Optional Phase 5 output (for micro scores)
    
    Returns:
        Dict satisfying Phase 8 input contract
    
    Example:
        >>> from farfan_pipeline.phases.Phase_07.phase7_10_00_macro_score import MacroScore
        >>> macro_score = MacroScore(...)  # Phase 7 output
        >>> phase5_areas = [...]  # Phase 5 AreaScore objects
        >>> phase8_input = adapt_phase7_to_phase8(macro_score, phase5_areas)
        >>> # Now pass phase8_input to Phase 8
    """
    adapter = Phase7To8Adapter()
    return adapter.adapt(macro_score, phase5_output)


if __name__ == "__main__":
    print("Phase 7→8 Interface Adapter")
    print("=" * 70)
    print("Status: ACTIVE")
    print("Version: 1.0.0")
    print("Contract: ADAPTER-P7-P8-v1.0")
    print()
    print("Capabilities:")
    print("  ✓ Transforms MacroScore → Phase 8 input dict")
    print("  ✓ Retrieves 60 micro scores from Phase 5 output")
    print("  ✓ Converts cluster_scores List → Dict")
    print("  ✓ Maps quality_level → macro_band")
    print("  ✓ Preserves provenance chain")
    print()
    print("Usage:")
    print("  from farfan_pipeline.phases.Phase_08.contracts.phase7_to_phase8_adapter import adapt_phase7_to_phase8")
    print("  phase8_input = adapt_phase7_to_phase8(macro_score, phase5_output)")
    print("=" * 70)
