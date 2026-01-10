"""
Aggregation Integration Module

Provides implementation for Phases 4-7 aggregation methods.
This module contains the actual implementations to replace orchestrator stubs.

To integrate into orchestrator:
1. Import this module
2. Replace stub methods with calls to these implementations
3. Or copy implementations directly into orchestrator
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration.orchestrator import MacroEvaluation

from farfan_pipeline.phases.Phase_4.aggregation import (
    DimensionAggregator,
    DimensionScore,
    AreaPolicyAggregator,
    AreaScore,
    ClusterAggregator,
    ClusterScore,
    MacroAggregator,
    MacroScore,
    group_by,
    validate_scored_results,
)

logger = logging.getLogger(__name__)


# Type adapter for MacroScore → MacroEvaluation
def macro_score_to_evaluation(macro_score: MacroScore) -> dict[str, Any]:
    """
    Convert MacroScore to MacroEvaluation-compatible dict.
    
    Args:
        macro_score: MacroScore from aggregation
        
    Returns:
        Dict compatible with MacroEvaluation structure
    """
    return {
        "macro_score": macro_score.score,
        "macro_score_normalized": macro_score.score / 3.0,
        "clusters": [
            {
                "cluster_id": cs.cluster_id,
                "score": cs.score,
                "coherence": cs.coherence,
            }
            for cs in macro_score.cluster_scores
        ],
    }


async def aggregate_dimensions_async(
    scored_results: list[Any],
    questionnaire: dict[str, Any],
    instrumentation: Any,
    signal_registry: Any | None = None,
) -> list[DimensionScore]:
    """
    FASE 4: Aggregate micro questions into dimension scores.
    
    Args:
        scored_results: List of ScoredMicroQuestion objects
        questionnaire: Questionnaire monolith
        instrumentation: Phase instrumentation for tracking
        signal_registry: Optional SISAS signal registry
        
    Returns:
        List of DimensionScore objects
    """
    logger.info("Phase 4: Starting dimension aggregation")
    
    # Initialize aggregator
    aggregator = DimensionAggregator(
        monolith=questionnaire,
        abort_on_insufficient=True,
        enable_sota_features=True,
        signal_registry=signal_registry,
    )
    
    # Validate input
    try:
        validated_results = validate_scored_results(scored_results)
    except Exception as e:
        logger.error(f"Failed to validate scored results: {e}")
        # Return empty if validation fails
        return []
    
    # Group by (policy_area, dimension)
    grouped = group_by(
        validated_results,
        key_func=lambda r: (r.policy_area_id, r.dimension_id)
    )
    
    logger.info(f"Phase 4: Processing {len(grouped)} dimension groups")
    instrumentation.start(items_total=len(grouped))
    
    dimension_scores = []
    for (area_id, dim_id), group_results in grouped.items():
        try:
            logger.debug(f"Aggregating dimension {dim_id} in area {area_id}")
            
            dim_score = aggregator.aggregate_dimension(
                group_results,
                group_by_values={"policy_area": area_id, "dimension": dim_id}
            )
            
            dimension_scores.append(dim_score)
            instrumentation.complete_item()
            
            logger.debug(
                f"Dimension {dim_id} in {area_id}: score={dim_score.score:.2f}, "
                f"quality={dim_score.quality_level}"
            )
            
        except Exception as e:
            logger.error(f"Failed to aggregate dimension {dim_id} in {area_id}: {e}")
            if aggregator.abort_on_insufficient:
                raise
    
    logger.info(f"Phase 4: Completed {len(dimension_scores)} dimension aggregations")
    return dimension_scores


async def aggregate_policy_areas_async(
    dimension_scores: list[DimensionScore],
    questionnaire: dict[str, Any],
    instrumentation: Any,
) -> list[AreaScore]:
    """
    FASE 5: Aggregate dimensions into policy area scores.
    
    Args:
        dimension_scores: List of DimensionScore objects
        questionnaire: Questionnaire monolith
        instrumentation: Phase instrumentation for tracking
        
    Returns:
        List of AreaScore objects
    """
    logger.info("Phase 5: Starting policy area aggregation")
    
    # Initialize aggregator
    aggregator = AreaPolicyAggregator(
        monolith=questionnaire,
        abort_on_insufficient=True,
    )
    
    # Group by area_id
    grouped = group_by(
        dimension_scores,
        key_func=lambda d: (d.policy_area_id,)
    )
    
    logger.info(f"Phase 5: Processing {len(grouped)} policy area groups")
    instrumentation.start(items_total=len(grouped))
    
    area_scores = []
    for (area_id,), group_dims in grouped.items():
        try:
            logger.debug(f"Aggregating area {area_id} with {len(group_dims)} dimensions")
            
            area_score = aggregator.aggregate_area(
                group_dims,
                group_by_values={"area_id": area_id}
            )
            
            area_scores.append(area_score)
            instrumentation.complete_item()
            
            logger.debug(
                f"Area {area_id}: score={area_score.score:.2f}, "
                f"quality={area_score.quality_level}"
            )
            
        except Exception as e:
            logger.error(f"Failed to aggregate area {area_id}: {e}")
            if aggregator.abort_on_insufficient:
                raise
    
    logger.info(f"Phase 5: Completed {len(area_scores)} policy area aggregations")
    return area_scores


def aggregate_clusters(
    policy_area_scores: list[AreaScore],
    questionnaire: dict[str, Any],
    instrumentation: Any,
) -> list[ClusterScore]:
    """
    FASE 6: Aggregate policy areas into cluster scores.
    
    Args:
        policy_area_scores: List of AreaScore objects
        questionnaire: Questionnaire monolith
        instrumentation: Phase instrumentation for tracking
        
    Returns:
        List of ClusterScore objects
    """
    logger.info("Phase 6: Starting cluster aggregation")
    
    # Initialize aggregator
    aggregator = ClusterAggregator(
        monolith=questionnaire,
        abort_on_insufficient=True,
    )
    
    # Get cluster definitions from questionnaire
    clusters = (
        questionnaire.get("blocks", {})
        .get("niveles_abstraccion", {})
        .get("clusters", [])
    )
    
    if not clusters:
        logger.warning("No cluster definitions found in questionnaire")
        return []
    
    logger.info(f"Phase 6: Processing {len(clusters)} clusters")
    instrumentation.start(items_total=len(clusters))
    
    cluster_scores = []
    for cluster_def in clusters:
        cluster_id = cluster_def.get("cluster_id", "UNKNOWN")
        expected_areas = cluster_def.get("policy_area_ids", [])
        
        logger.debug(
            f"Processing cluster {cluster_id} with expected areas: {expected_areas}"
        )
        
        # Filter areas for this cluster
        cluster_areas = [
            area for area in policy_area_scores
            if area.area_id in expected_areas
        ]
        
        if not cluster_areas:
            logger.warning(f"No areas found for cluster {cluster_id}")
            continue
        
        try:
            logger.debug(
                f"Aggregating cluster {cluster_id} with {len(cluster_areas)} areas"
            )
            
            cluster_score = aggregator.aggregate_cluster(
                cluster_areas,
                group_by_values={"cluster_id": cluster_id}
            )
            
            cluster_scores.append(cluster_score)
            instrumentation.complete_item()
            
            logger.debug(
                f"Cluster {cluster_id}: score={cluster_score.score:.2f}, "
                f"coherence={cluster_score.coherence:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Failed to aggregate cluster {cluster_id}: {e}")
            if aggregator.abort_on_insufficient:
                raise
    
    logger.info(f"Phase 6: Completed {len(cluster_scores)} cluster aggregations")
    return cluster_scores


def evaluate_macro(
    cluster_scores: list[ClusterScore],
    dimension_scores: list[DimensionScore],
    area_scores: list[AreaScore],
    questionnaire: dict[str, Any],
    instrumentation: Any,
) -> dict[str, Any]:
    """
    FASE 7: Evaluate macro holistic score.
    
    Args:
        cluster_scores: List of ClusterScore objects
        dimension_scores: List of DimensionScore objects (for strategic alignment)
        area_scores: List of AreaScore objects (for strategic alignment)
        questionnaire: Questionnaire monolith
        instrumentation: Phase instrumentation for tracking
        
    Returns:
        Dict compatible with MacroEvaluation structure
    """
    logger.info("Phase 7: Starting macro evaluation")
    
    # Initialize aggregator
    aggregator = MacroAggregator(
        monolith=questionnaire,
        abort_on_insufficient=True,
    )
    
    instrumentation.start(items_total=1)
    
    try:
        logger.debug(
            f"Aggregating macro from {len(cluster_scores)} clusters, "
            f"{len(dimension_scores)} dimensions, {len(area_scores)} areas"
        )
        
        # Aggregate to MacroScore
        macro_score = aggregator.aggregate_macro(
            cluster_scores,
            dimension_scores=dimension_scores,
            area_scores=area_scores,
        )
        
        instrumentation.complete_item()
        
        logger.info(
            f"Macro evaluation: score={macro_score.score:.2f}, "
            f"quality={macro_score.quality_level}, "
            f"coherence={macro_score.cross_cutting_coherence:.2f}, "
            f"alignment={macro_score.strategic_alignment:.2f}"
        )
        
        # Convert MacroScore to MacroEvaluation-compatible dict
        macro_eval = macro_score_to_evaluation(macro_score)
        
        # Add enriched data for later phases
        macro_eval["_macro_score_full"] = macro_score  # Store full object
        
        return macro_eval
        
    except Exception as e:
        logger.error(f"Failed to evaluate macro: {e}")
        if aggregator.abort_on_insufficient:
            raise
        
        # Return empty result on failure
        return {
            "macro_score": 0.0,
            "macro_score_normalized": 0.0,
            "clusters": [],
        }


# Integration helper to enable contract validation
def validate_with_contracts(
    phase: str,
    results: list[Any],
    contracts: dict[str, Any] | None = None,
) -> None:
    """
    Validate aggregation results with contracts.
    
    Args:
        phase: Phase name (dimension, area, cluster, macro)
        results: List of result objects to validate
        contracts: Dict of contract objects by phase
    """
    if not contracts or phase not in contracts:
        logger.debug(f"No contract validation for phase {phase}")
        return
    
    contract = contracts[phase]
    
    # Validate each result
    for result in results:
        if hasattr(result, 'score'):
            contract.validate_score_bounds(result.score)
        
        if hasattr(result, 'coherence'):
            contract.validate_coherence_bounds(result.coherence)
    
    # Check for violations
    violations = contract.get_violations()
    if violations:
        logger.warning(f"Phase {phase} aggregation violations: {len(violations)}")
        for v in violations:
            logger.warning(f"  [{v.severity}] {v.invariant_id}: {v.message}")
    
    # Clear violations for next validation
    contract.clear_violations()


# Example usage showing how to integrate into orchestrator
"""
To integrate into orchestrator.py:

1. Import this module at the top:
   from orchestration.aggregation_integration import (
       aggregate_dimensions_async,
       aggregate_policy_areas_async,
       aggregate_clusters,
       evaluate_macro,
   )

2. Replace stub methods:

   async def _aggregate_dimensions_async(
       self, scored_results: list[ScoredMicroQuestion], config: dict[str, Any]
   ) -> list[DimensionScore]:
       self._ensure_not_aborted()
       instrumentation = self._phase_instrumentation[4]
       
       return await aggregate_dimensions_async(
           scored_results,
           self._questionnaire,
           instrumentation,
           signal_registry=getattr(self, '_signal_registry', None)
       )
   
   async def _aggregate_policy_areas_async(
       self, dimension_scores: list[DimensionScore], config: dict[str, Any]
   ) -> list[AreaScore]:
       self._ensure_not_aborted()
       instrumentation = self._phase_instrumentation[5]
       
       # Cache for later use in macro
       self._cached_dimension_scores = dimension_scores
       
       return await aggregate_policy_areas_async(
           dimension_scores,
           self._questionnaire,
           instrumentation
       )
   
   def _aggregate_clusters(
       self, policy_area_scores: list[AreaScore], config: dict[str, Any]
   ) -> list[ClusterScore]:
       self._ensure_not_aborted()
       instrumentation = self._phase_instrumentation[6]
       
       # Cache for later use in macro
       self._cached_area_scores = policy_area_scores
       
       return aggregate_clusters(
           policy_area_scores,
           self._questionnaire,
           instrumentation
       )
   
   def _evaluate_macro(
       self, cluster_scores: list[ClusterScore], config: dict[str, Any]
   ) -> MacroEvaluation:
       self._ensure_not_aborted()
       instrumentation = self._phase_instrumentation[7]
       
       # Get cached scores for strategic alignment
       dimension_scores = getattr(self, '_cached_dimension_scores', [])
       area_scores = getattr(self, '_cached_area_scores', [])
       
       macro_eval_dict = evaluate_macro(
           cluster_scores,
           dimension_scores,
           area_scores,
           self._questionnaire,
           instrumentation
       )
       
       # Convert dict to MacroEvaluation object
       return MacroEvaluation(**macro_eval_dict)
"""
