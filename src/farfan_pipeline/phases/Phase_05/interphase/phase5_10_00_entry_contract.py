"""
Phase 5 Entry Contract (Phase 4 → Phase 5)

Defines the interface contract between Phase 4 and Phase 5.

Entry Requirements:
- Type: List[DimensionScore]
- Count: Exactly 60 DimensionScore objects
- Structure: 6 dimensions × 10 policy areas
- Hermeticity: Each area must have exactly 6 dimensions (DIM01-DIM06)
- Bounds: All scores in [0.0, 3.0]

Module: src/farfan_pipeline/phases/Phase_05/interphase/phase5_10_00_entry_contract.py
"""
from __future__ import annotations

__version__ = "2.0.0"
__phase__ = 5
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"

import logging
from typing import Any

from farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_types import DimensionScore
from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
    DIMENSIONS_PER_AREA,
    DIMENSION_IDS,
    EXPECTED_AREA_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    POLICY_AREAS,
)

logger = logging.getLogger(__name__)


class Phase5EntryContract:
    """
    Entry contract validator for Phase 5.

    Validates that Phase 4 output meets Phase 5 input requirements.
    """

    EXPECTED_INPUT_COUNT = DIMENSIONS_PER_AREA * EXPECTED_AREA_SCORE_COUNT  # 60

    @classmethod
    def validate(
        cls,
        dimension_scores: list[DimensionScore],
    ) -> tuple[bool, dict[str, Any]]:
        """
        Validate Phase 5 entry contract.

        Args:
            dimension_scores: List of DimensionScore objects from Phase 4

        Returns:
            Tuple of (validation_passed, validation_details)
        """
        logger.info(f"Validating Phase 5 entry contract: {len(dimension_scores)} dimension scores")

        details = {
            "contract": "Phase 5 Entry (Phase 4 → Phase 5)",
            "version": __version__,
            "checks": [],
            "errors": [],
            "warnings": [],
        }

        # Check 1: Count validation
        if len(dimension_scores) != cls.EXPECTED_INPUT_COUNT:
            details["errors"].append(
                f"Expected {cls.EXPECTED_INPUT_COUNT} dimension scores, got {len(dimension_scores)}"
            )
        else:
            details["checks"].append(f"✓ Count: {len(dimension_scores)} dimension scores")

        # Check 2: Hermeticity validation
        grouped = cls._group_by_area(dimension_scores)

        for area_id in POLICY_AREAS:
            if area_id not in grouped:
                details["errors"].append(f"Missing policy area: {area_id}")
            elif len(grouped[area_id]) != DIMENSIONS_PER_AREA:
                details["errors"].append(
                    f"{area_id}: Expected {DIMENSIONS_PER_AREA} dimensions, got {len(grouped[area_id])}"
                )
            else:
                # Check exact dimension set
                dim_ids = {ds.dimension_id for ds in grouped[area_id]}
                if dim_ids != set(DIMENSION_IDS):
                    missing = set(DIMENSION_IDS) - dim_ids
                    extra = dim_ids - set(DIMENSION_IDS)
                    details["errors"].append(
                        f"{area_id}: Missing dimensions {missing}, Extra dimensions {extra}"
                    )

        if not details["errors"]:
            details["checks"].append("✓ Hermeticity: All 10 areas with 6 dimensions each")

        # Check 3: Score bounds
        out_of_bounds = []
        for ds in dimension_scores:
            if not (MIN_SCORE <= ds.score <= MAX_SCORE):
                out_of_bounds.append(f"{ds.area_id}:{ds.dimension_id}={ds.score}")

        if out_of_bounds:
            details["errors"].append(
                f"Scores out of bounds [{MIN_SCORE}, {MAX_SCORE}]: {out_of_bounds[:5]}"
            )
        else:
            details["checks"].append(f"✓ All scores in [{MIN_SCORE}, {MAX_SCORE}]")

        # Check 4: Required attributes
        sample = dimension_scores[0] if dimension_scores else None
        if sample:
            required_attrs = ["dimension_id", "area_id", "score", "quality_level"]
            missing_attrs = [attr for attr in required_attrs if not hasattr(sample, attr)]
            if missing_attrs:
                details["errors"].append(f"Missing required attributes: {missing_attrs}")
            else:
                details["checks"].append("✓ All required attributes present")

        validation_passed = len(details["errors"]) == 0
        details["passed"] = validation_passed

        if validation_passed:
            logger.info("✅ Phase 5 entry contract validated successfully")
        else:
            logger.error(f"❌ Phase 5 entry contract validation failed: {len(details['errors'])} errors")

        return validation_passed, details

    @staticmethod
    def _group_by_area(
        dimension_scores: list[DimensionScore],
    ) -> dict[str, list[DimensionScore]]:
        """Group dimension scores by area."""
        grouped: dict[str, list[DimensionScore]] = {}
        for ds in dimension_scores:
            if ds.area_id not in grouped:
                grouped[ds.area_id] = []
            grouped[ds.area_id].append(ds)
        return grouped


def validate_phase5_entry(
    dimension_scores: list[DimensionScore],
) -> tuple[bool, dict[str, Any]]:
    """
    Convenience function to validate Phase 5 entry contract.

    Args:
        dimension_scores: List of DimensionScore objects from Phase 4

    Returns:
        Tuple of (validation_passed, validation_details)
    """
    return Phase5EntryContract.validate(dimension_scores)


__all__ = [
    "Phase5EntryContract",
    "validate_phase5_entry",
]
