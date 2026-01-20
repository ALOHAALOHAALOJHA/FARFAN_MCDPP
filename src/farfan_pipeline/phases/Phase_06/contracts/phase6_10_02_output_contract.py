"""
Phase 6 Output Contract

This contract defines and validates the output requirements for Phase 6.

Output Specification:
- Type: List[ClusterScore]
- Count: Exactly 4 ClusterScore objects (CLUSTER_MESO_1 to CLUSTER_MESO_4)
- All scores must be in range [0.0, 3.0]
- Each cluster must contain its designated policy areas
- Coherence metrics must be computed
- Dispersion scenario must be classified

Downstream Consumer: Phase 7 (Macro Aggregation)

Module: src/farfan_pipeline/phases/Phase_06/contracts/phase6_output_contract.py
Phase: 6 (Cluster Aggregation - MESO)
Owner: phase6_contracts
"""

from __future__ import annotations

__version__ = "1.0.0"
__phase__ = 6
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"

from typing import Any
import logging

from farfan_pipeline.phases.Phase_06.phase6_10_01_scoring_config import (
    PHASE6_CONFIG,
    CoherenceQuality,
)

logger = logging.getLogger(__name__)


class Phase6OutputContract:
    """
    Phase 6 Output Contract Validator.
    
    Validates that Phase 6 output (4 ClusterScore objects) meets
    Phase 7 input requirements.
    """
    
    EXPECTED_CLUSTER_COUNT = 4
    MIN_SCORE = 0.0
    MAX_SCORE = 3.0
    
    REQUIRED_CLUSTER_IDS = [
        "CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"
    ]
    
    CLUSTER_COMPOSITION = {
        "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],
        "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],
        "CLUSTER_MESO_3": ["PA07", "PA08"],
        "CLUSTER_MESO_4": ["PA09", "PA10"],
    }

    @classmethod
    def classify_coherence_quality(cls, coherence: float) -> tuple[CoherenceQuality, str]:
        """
        Classify coherence value into quality tier using PHASE6_CONFIG thresholds.
        """
        quality = PHASE6_CONFIG.classify_coherence(coherence)
        descriptions = {
            CoherenceQuality.EXCELLENT: f"Excellent coherence ({coherence:.3f} >= {PHASE6_CONFIG.coherence_high})",
            CoherenceQuality.ACCEPTABLE: f"Acceptable coherence ({PHASE6_CONFIG.coherence_low} <= {coherence:.3f} < {PHASE6_CONFIG.coherence_high})",
            CoherenceQuality.POOR: f"Poor coherence ({coherence:.3f} < {PHASE6_CONFIG.coherence_low})",
        }
        return quality, descriptions[quality]
    
    @classmethod
    def validate(cls, cluster_scores: list[Any]) -> tuple[bool, dict[str, Any]]:
        """
        Validate Phase 6 output contract.
        
        Args:
            cluster_scores: List of ClusterScore objects from Phase 6
            
        Returns:
            Tuple of (validation_passed, validation_details)
        """
        validation_details = {
            "contract": "Phase 6 Output",
            "checks": [],
            "errors": [],
            "warnings": []
        }
        
        # Check 1: Count validation
        if len(cluster_scores) != cls.EXPECTED_CLUSTER_COUNT:
            validation_details["errors"].append(
                f"Expected {cls.EXPECTED_CLUSTER_COUNT} cluster scores, got {len(cluster_scores)}"
            )
        else:
            validation_details["checks"].append(f"✓ Count: {len(cluster_scores)} cluster scores")
        
        # Check 2: Cluster ID coverage
        cluster_ids = {cluster.cluster_id for cluster in cluster_scores}
        missing_clusters = set(cls.REQUIRED_CLUSTER_IDS) - cluster_ids
        if missing_clusters:
            validation_details["errors"].append(
                f"Missing clusters: {sorted(missing_clusters)}"
            )
        else:
            validation_details["checks"].append("✓ All 4 clusters present")
        
        # Check 3: Hermeticity - each cluster has correct policy areas
        for cluster in cluster_scores:
            expected_areas = set(cls.CLUSTER_COMPOSITION.get(cluster.cluster_id, []))
            actual_areas = set(cluster.areas)
            if expected_areas != actual_areas:
                missing = expected_areas - actual_areas
                extra = actual_areas - expected_areas
                error_msg = f"{cluster.cluster_id}: "
                if missing:
                    error_msg += f"missing areas {missing} "
                if extra:
                    error_msg += f"extra areas {extra}"
                validation_details["errors"].append(error_msg)
        
        validation_details["checks"].append("✓ Hermeticity validated")
        
        # Check 4: Score bounds
        out_of_bounds = []
        for cluster in cluster_scores:
            if not (cls.MIN_SCORE <= cluster.score <= cls.MAX_SCORE):
                out_of_bounds.append(f"{cluster.cluster_id}: {cluster.score}")
        
        if out_of_bounds:
            validation_details["errors"].append(
                f"Scores out of bounds [{cls.MIN_SCORE}, {cls.MAX_SCORE}]: {out_of_bounds}"
            )
        else:
            validation_details["checks"].append(f"✓ All scores in [{cls.MIN_SCORE}, {cls.MAX_SCORE}]")

        # Check 5: Coherence quality assessment (advisory)
        for cluster in cluster_scores:
            if hasattr(cluster, 'coherence'):
                quality, description = cls.classify_coherence_quality(cluster.coherence)
                validation_details["checks"].append(f"✓ {cluster.cluster_id}: {description}")
                if quality == CoherenceQuality.POOR:
                    validation_details["warnings"].append(
                        f"{cluster.cluster_id} has poor coherence - consider investigation"
                    )

        # Check 5: Coherence metrics present
        missing_coherence = [cluster.cluster_id for cluster in cluster_scores 
                            if not hasattr(cluster, 'coherence') or cluster.coherence is None]
        if missing_coherence:
            validation_details["warnings"].append(
                f"Clusters without coherence metrics: {missing_coherence}"
            )
        else:
            validation_details["checks"].append("✓ All clusters have coherence metrics")
        
        # Check 6: Dispersion scenario classified
        missing_scenario = [cluster.cluster_id for cluster in cluster_scores 
                           if not hasattr(cluster, 'dispersion_scenario') or not cluster.dispersion_scenario]
        if missing_scenario:
            validation_details["warnings"].append(
                f"Clusters without dispersion scenario: {missing_scenario}"
            )
        else:
            validation_details["checks"].append("✓ All clusters have dispersion classification")
        
        # Check 7: Provenance tracking
        missing_provenance = [cluster.cluster_id for cluster in cluster_scores 
                             if not hasattr(cluster, 'provenance_node_id') or not cluster.provenance_node_id]
        if missing_provenance:
            validation_details["warnings"].append(
                f"Clusters without provenance: {missing_provenance}"
            )
        else:
            validation_details["checks"].append("✓ All clusters have provenance tracking")

        coherence_values = [c.coherence for c in cluster_scores if hasattr(c, 'coherence')]
        if coherence_values:
            avg_coherence = sum(coherence_values) / len(coherence_values)
            validation_details["coherence_summary"] = {
                "average": round(avg_coherence, 3),
                "minimum": round(min(coherence_values), 3),
                "quality_distribution": {
                    q.value: sum(
                        1 for c in cluster_scores
                        if hasattr(c, 'coherence') and PHASE6_CONFIG.classify_coherence(c.coherence) == q
                    )
                    for q in CoherenceQuality
                },
            }

        validation_passed = len(validation_details["errors"]) == 0
        validation_details["passed"] = validation_passed
        
        return validation_passed, validation_details
    
    @classmethod
    def fail_fast(cls, cluster_scores: list[Any]) -> None:
        """
        Fail-fast validation - raises exception on first failure.
        
        Args:
            cluster_scores: List of ClusterScore objects
            
        Raises:
            ValueError: If any validation check fails
        """
        passed, details = cls.validate(cluster_scores)
        
        if not passed:
            error_msg = "Phase 6 Output Contract Violation:\n"
            for error in details["errors"]:
                error_msg += f"  ✗ {error}\n"
            raise ValueError(error_msg)
        
        logger.info("✅ Phase 6 output contract validated successfully")
    
    @classmethod
    def generate_phase7_compatibility_certificate(cls, cluster_scores: list[Any]) -> dict[str, Any]:
        """
        Generate a compatibility certificate for Phase 7 consumption.
        
        Args:
            cluster_scores: List of ClusterScore objects
            
        Returns:
            Certificate dictionary with validation results
        """
        passed, details = cls.validate(cluster_scores)
        
        certificate = {
            "certificate_type": "Phase 6 → Phase 7 Compatibility",
            "certificate_version": "1.0.0",
            "validation_passed": passed,
            "cluster_count": len(cluster_scores),
            "cluster_ids": [cs.cluster_id for cs in cluster_scores],
            "score_range": [
                min(cs.score for cs in cluster_scores),
                max(cs.score for cs in cluster_scores)
            ] if cluster_scores else [0.0, 0.0],
            "validation_details": details,
            "ready_for_phase7": passed and len(details["warnings"]) == 0
        }
        
        return certificate


# Convenience function
def validate_phase6_output(cluster_scores: list[Any]) -> tuple[bool, dict[str, Any]]:
    """
    Validate Phase 6 output.
    
    Args:
        cluster_scores: List of ClusterScore objects from Phase 6
        
    Returns:
        Tuple of (validation_passed, validation_details)
    """
    return Phase6OutputContract.validate(cluster_scores)
