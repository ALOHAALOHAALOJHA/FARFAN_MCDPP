"""
Phase 4-7 Entry Contract
========================

This module defines the entry contract for Phase 4-7 (Hierarchical Aggregation).
It specifies the input requirements from Phase 3 (Quality-Based Scoring).

Entry Point (Node that receives from outside the phase):
    - PHASE_4_AGGREGATION_ENTRY: Receives ScoredResult[] from Phase 3

The entry contract validates that:
1. Input data comes from Phase 3 output
2. All scored results are properly formatted
3. Micro-question traceability is maintained
4. Score values are within valid ranges

Source Phase: Phase 3 (Quality-Based Scoring)
Source Node: phase3_quality_scoring_output
Target Node: phase4_dimension_aggregation_input

Author: F.A.R.F.A.N. Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..phase4_10_00_phase_4_7_constants import (
    MIN_SCORE,
    MAX_SCORE,
    META_PROVENANCE_SOURCE_PHASE,
    META_PROVENANCE_NODE_ID,
    META_PROVENANCE_PARENT_ID,
)

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_3.primitives.scoring_modalities import ScoredResult

logger = logging.getLogger(__name__)


class EntryContractViolationError(RuntimeError):
    """Raised when entry contract validation fails."""
    pass


@dataclass(frozen=True)
class Phase4_7EntryContract:
    """
    Immutable entry contract for Phase 4-7.

    Defines the contract for receiving data from Phase 3.

    Attributes:
        source_phase: Phase that delivers the input (Phase 3)
        source_node: Specific node in source phase
        target_node: Node in this phase that receives input
        required_fields: Required fields in input data
        validation_rules: Validation rules to apply
    """

    source_phase: str = "PHASE_3"
    source_node: str = "phase3_quality_scoring_output"
    target_node: str = "phase4_dimension_aggregation_input"
    required_fields: tuple = (
        "question_id",
        "dimension_id",
        "policy_area_id",
        "score",
        "quality_level",
    )
    validation_rules: tuple = (
        "score_in_range",
        "traceability",
        "quality_level_valid",
    )

    def validate_input(
        self,
        scored_results: List[Any],
        strict_mode: bool = True,
    ) -> tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate input data against entry contract.

        Args:
            scored_results: List of ScoredResult objects from Phase 3
            strict_mode: If True, raises exception on validation failure

        Returns:
            Tuple of (is_valid, violations, metadata)

        Raises:
            EntryContractViolationError: If validation fails in strict mode
        """
        violations = []
        metadata = {
            "source_phase": self.source_phase,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "input_count": len(scored_results),
        }

        # Check if input is empty
        if not scored_results:
            violations.append("Empty input: No scored results received from Phase 3")
            if strict_mode:
                raise EntryContractViolationError(
                    f"Entry contract violation: {violations[0]}"
                )
            return False, violations, metadata

        # Validate each scored result
        invalid_scores = []
        missing_fields = []
        invalid_quality = []
        non_traceable = []

        for idx, result in enumerate(scored_results):
            # Check required fields
            missing = [f for f in self.required_fields if not hasattr(result, f)]
            if missing:
                missing_fields.append(f"Result {idx}: Missing fields {missing}")

            # Check score range
            if hasattr(result, "score"):
                score = getattr(result, "score")
                if not (MIN_SCORE <= score <= MAX_SCORE):
                    invalid_scores.append(
                        f"Result {idx}: Score {score} outside range [{MIN_SCORE}, {MAX_SCORE}]"
                    )

            # Check quality level
            if hasattr(result, "quality_level"):
                quality = getattr(result, "quality_level")
                valid_qualities = {"EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"}
                if quality not in valid_qualities:
                    invalid_quality.append(
                        f"Result {idx}: Invalid quality level '{quality}'"
                    )

            # Check traceability
            if hasattr(result, "question_id"):
                qid = getattr(result, "question_id")
                if not qid or qid == "":
                    non_traceable.append(f"Result {idx}: Missing or empty question_id")

        # Collect all violations
        if missing_fields:
            violations.extend(missing_fields[:5])  # Limit to first 5
            metadata["missing_fields_count"] = len(missing_fields)

        if invalid_scores:
            violations.extend(invalid_scores[:5])
            metadata["invalid_scores_count"] = len(invalid_scores)

        if invalid_quality:
            violations.extend(invalid_quality[:5])
            metadata["invalid_quality_count"] = len(invalid_quality)

        if non_traceable:
            violations.extend(non_traceable[:5])
            metadata["non_traceable_count"] = len(non_traceable)

        # Determine validation status
        is_valid = len(violations) == 0

        # Add validation metadata
        metadata["is_valid"] = is_valid
        metadata["violations_count"] = len(violations)

        # Log validation result
        if is_valid:
            logger.info(
                f"Entry contract validation passed: {len(scored_results)} scored results from Phase 3"
            )
        else:
            logger.warning(
                f"Entry contract validation failed: {len(violations)} violations detected"
            )

        # Raise exception in strict mode
        if not is_valid and strict_mode:
            raise EntryContractViolationError(
                f"Entry contract validation failed with {len(violations)} violations:\n" +
                "\n".join(violations[:10])
            )

        return is_valid, violations, metadata

    def extract_provenance_metadata(
        self,
        scored_results: List[Any],
    ) -> Dict[str, Any]:
        """
        Extract provenance metadata from input data.

        Args:
            scored_results: List of ScoredResult objects

        Returns:
            Provenance metadata dict
        """
        provenance = {
            META_PROVENANCE_SOURCE_PHASE: self.source_phase,
            META_PROVENANCE_NODE_ID: self.target_node,
            META_PROVENANCE_PARENT_ID: self.source_node,
            "input_count": len(scored_results),
        }

        # Extract dimension/area coverage
        dimensions = set()
        areas = set()
        questions = []

        for result in scored_results:
            # ScoredResult uses 'dimension', not 'dimension_id'
            if hasattr(result, "dimension"):
                dimensions.add(getattr(result, "dimension"))
            elif hasattr(result, "dimension_id"):
                dimensions.add(getattr(result, "dimension_id"))
            # ScoredResult uses 'policy_area', not 'policy_area_id'
            if hasattr(result, "policy_area"):
                areas.add(getattr(result, "policy_area"))
            elif hasattr(result, "policy_area_id"):
                areas.add(getattr(result, "policy_area_id"))
            # ScoredResult uses 'question_global', not 'question_id'
            if hasattr(result, "question_global"):
                questions.append(getattr(result, "question_global"))
            elif hasattr(result, "question_id"):
                questions.append(getattr(result, "question_id"))

        provenance["dimensions_covered"] = list(dimensions)
        provenance["areas_covered"] = list(areas)
        provenance["questions_processed"] = questions

        return provenance


def validate_phase4_7_entry(
    scored_results: List[Any],
    strict_mode: bool = True,
) -> tuple[bool, List[str], Dict[str, Any]]:
    """
    Convenience function to validate Phase 4-7 entry.

    Args:
        scored_results: List of ScoredResult objects from Phase 3
        strict_mode: If True, raises exception on validation failure

    Returns:
        Tuple of (is_valid, violations, metadata)
    """
    contract = Phase4_7EntryContract()
    return contract.validate_input(scored_results, strict_mode)


def extract_entry_provenance(
    scored_results: List[Any],
) -> Dict[str, Any]:
    """
    Convenience function to extract entry provenance.

    Args:
        scored_results: List of ScoredResult objects from Phase 3

    Returns:
        Provenance metadata dict
    """
    contract = Phase4_7EntryContract()
    return contract.extract_provenance_metadata(scored_results)


__all__ = [
    "EntryContractViolationError",
    "Phase4_7EntryContract",
    "validate_phase4_7_entry",
    "extract_entry_provenance",
]
