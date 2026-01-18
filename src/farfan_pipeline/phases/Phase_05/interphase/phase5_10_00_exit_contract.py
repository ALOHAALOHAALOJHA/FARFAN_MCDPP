"""
Phase 5 Exit Contract (Phase 5 → Phase 6)

Defines the interface contract between Phase 5 and Phase 6.

Exit Requirements:
- Type: List[AreaScore]
- Count: Exactly 10 AreaScore objects (PA01-PA10)
- Each AreaScore must have 6 DimensionScore objects
- All scores must be in range [0.0, 3.0]
- All areas must have cluster_id assigned for Phase 6

Module: src/farfan_pipeline/phases/Phase_05/interphase/phase5_10_00_exit_contract.py
"""
from __future__ import annotations

__version__ = "2.0.0"
__phase__ = 5
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"

import logging
from typing import Any

from farfan_pipeline.phases.Phase_05.phase5_10_00_area_aggregation import AreaScore
from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
    CLUSTER_ASSIGNMENTS,
    DIMENSIONS_PER_AREA,
    EXPECTED_AREA_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    POLICY_AREAS,
)

logger = logging.getLogger(__name__)


class Phase5ExitContract:
    """
    Exit contract validator for Phase 5.

    Validates that Phase 5 output meets Phase 6 input requirements.
    """

    EXPECTED_OUTPUT_COUNT = EXPECTED_AREA_SCORE_COUNT  # 10

    @classmethod
    def validate(
        cls,
        area_scores: list[AreaScore],
    ) -> tuple[bool, dict[str, Any]]:
        """
        Validate Phase 5 exit contract.

        Args:
            area_scores: List of AreaScore objects from Phase 5

        Returns:
            Tuple of (validation_passed, validation_details)
        """
        logger.info(f"Validating Phase 5 exit contract: {len(area_scores)} area scores")

        details = {
            "contract": "Phase 5 Exit (Phase 5 → Phase 6)",
            "version": __version__,
            "checks": [],
            "errors": [],
            "warnings": [],
        }

        # Check 1: Count validation
        if len(area_scores) != cls.EXPECTED_OUTPUT_COUNT:
            details["errors"].append(
                f"Expected {cls.EXPECTED_OUTPUT_COUNT} area scores, got {len(area_scores)}"
            )
        else:
            details["checks"].append(f"✓ Count: {len(area_scores)} area scores")

        # Check 2: Policy area coverage
        area_ids = {area.area_id for area in area_scores}
        missing_areas = set(POLICY_AREAS) - area_ids
        if missing_areas:
            details["errors"].append(f"Missing policy areas: {sorted(missing_areas)}")
        else:
            details["checks"].append("✓ All 10 policy areas present")

        # Check 3: Hermeticity - each area has 6 dimensions
        for area in area_scores:
            if len(area.dimension_scores) != DIMENSIONS_PER_AREA:
                details["errors"].append(
                    f"{area.area_id}: Expected {DIMENSIONS_PER_AREA} dimensions, "
                    f"got {len(area.dimension_scores)}"
                )

        if not any("Expected" in err and "dimensions" in err for err in details["errors"]):
            details["checks"].append("✓ Hermeticity: All areas with 6 dimensions")

        # Check 4: Score bounds
        out_of_bounds = []
        for area in area_scores:
            if not (MIN_SCORE <= area.score <= MAX_SCORE):
                out_of_bounds.append(f"{area.area_id}={area.score}")

        if out_of_bounds:
            details["errors"].append(
                f"Scores out of bounds [{MIN_SCORE}, {MAX_SCORE}]: {out_of_bounds}"
            )
        else:
            details["checks"].append(f"✓ All scores in [{MIN_SCORE}, {MAX_SCORE}]")

        # Check 5: Cluster assignments (required for Phase 6)
        missing_clusters = [area.area_id for area in area_scores if not area.cluster_id]
        if missing_clusters:
            details["errors"].append(f"Areas without cluster_id: {missing_clusters}")
        else:
            details["checks"].append("✓ All areas have cluster assignments")

        # Check 6: Cluster assignment correctness
        incorrect_clusters = []
        for area in area_scores:
            if area.cluster_id:
                expected_cluster = None
                for cluster, areas in CLUSTER_ASSIGNMENTS.items():
                    if area.area_id in areas:
                        expected_cluster = cluster
                        break
                if expected_cluster and area.cluster_id != expected_cluster:
                    incorrect_clusters.append(
                        f"{area.area_id}: expected {expected_cluster}, got {area.cluster_id}"
                    )

        if incorrect_clusters:
            details["errors"].append(f"Incorrect cluster assignments: {incorrect_clusters}")
        else:
            details["checks"].append("✓ All cluster assignments correct")

        # Check 7: Required attributes for Phase 6
        sample = area_scores[0] if area_scores else None
        if sample:
            required_attrs = ["area_id", "area_name", "score", "quality_level", "cluster_id"]
            missing_attrs = [attr for attr in required_attrs if not hasattr(sample, attr)]
            if missing_attrs:
                details["errors"].append(f"Missing required attributes: {missing_attrs}")
            else:
                details["checks"].append("✓ All required attributes present")

        validation_passed = len(details["errors"]) == 0
        details["passed"] = validation_passed

        if validation_passed:
            logger.info("✅ Phase 5 exit contract validated successfully")
        else:
            logger.error(f"❌ Phase 5 exit contract validation failed: {len(details['errors'])} errors")

        return validation_passed, details


def validate_phase5_exit(
    area_scores: list[AreaScore],
) -> tuple[bool, dict[str, Any]]:
    """
    Convenience function to validate Phase 5 exit contract.

    Args:
        area_scores: List of AreaScore objects from Phase 5

    Returns:
        Tuple of (validation_passed, validation_details)
    """
    return Phase5ExitContract.validate(area_scores)


__all__ = [
    "Phase5ExitContract",
    "validate_phase5_exit",
]
