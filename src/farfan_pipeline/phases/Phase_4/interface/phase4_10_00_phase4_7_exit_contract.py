"""
Phase 4-7 Exit Contract
=======================

This module defines the exit contract for Phase 4-7 (Hierarchical Aggregation).
It specifies the output requirements for Phase 8 (Semantic Processing).

Exit Point (Node that delivers to outside the phase):
    - PHASE_7_MACRO_EVALUATION_OUTPUT: Delivers MacroScore to Phase 8

The exit contract validates that:
1. MacroScore is properly formatted
2. Score value is within valid range
3. Quality level is determined
4. Traceability to source micro-questions is maintained
5. Cross-cutting coherence and strategic alignment are computed

Target Phase: Phase 8 (Semantic Processing)
Target Node: phase8_semantic_input
Source Node: phase7_macro_evaluation_output

Author: F.A.R.F.A.N. Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..PHASE_4_7_CONSTANTS import (
    MIN_SCORE,
    MAX_SCORE,
    QUALITY_LEVEL_EXCELENTE,
    QUALITY_LEVEL_BUENO,
    QUALITY_LEVEL_ACEPTABLE,
    QUALITY_LEVEL_INSUFICIENTE,
    META_PROVENANCE_SOURCE_PHASE,
    META_PROVENANCE_NODE_ID,
)

logger = logging.getLogger(__name__)


class ExitContractViolationError(RuntimeError):
    """Raised when exit contract validation fails."""
    pass


@dataclass(frozen=True)
class Phase4_7ExitContract:
    """
    Immutable exit contract for Phase 4-7.

    Defines the contract for delivering data to Phase 8.

    Attributes:
        target_phase: Phase that receives the output (Phase 8)
        target_node: Specific node in target phase
        source_node: Node in this phase that delivers output
        required_fields: Required fields in output data
        validation_rules: Validation rules to apply
    """

    target_phase: str = "PHASE_8"
    target_node: str = "phase8_semantic_input"
    source_node: str = "phase7_macro_evaluation_output"
    required_fields: tuple = (
        "score",
        "quality_level",
        "cross_cutting_coherence",
        "strategic_alignment",
        "cluster_scores",
        "area_scores",
        "dimension_scores",
    )
    validation_rules: tuple = (
        "score_in_range",
        "quality_level_valid",
        "coherence_in_range",
        "alignment_in_range",
        "traceability",
    )

    def validate_output(
        self,
        macro_score: Any,
        strict_mode: bool = True,
    ) -> tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate output data against exit contract.

        Args:
            macro_score: MacroScore object from Phase 7
            strict_mode: If True, raises exception on validation failure

        Returns:
            Tuple of (is_valid, violations, metadata)

        Raises:
            ExitContractViolationError: If validation fails in strict mode
        """
        violations = []
        metadata = {
            "source_phase": "PHASE_4_7",
            "source_node": self.source_node,
            "target_phase": self.target_phase,
            "target_node": self.target_node,
        }

        # Check if macro_score is None
        if macro_score is None:
            violations.append("Output is None: No macro score produced")
            if strict_mode:
                raise ExitContractViolationError(
                    f"Exit contract violation: {violations[0]}"
                )
            return False, violations, metadata

        # Check required fields
        missing = [f for f in self.required_fields if not hasattr(macro_score, f)]
        if missing:
            violations.append(f"Missing required fields: {missing}")

        # Check score range
        if hasattr(macro_score, "score"):
            score = getattr(macro_score, "score")
            if not (MIN_SCORE <= score <= MAX_SCORE):
                violations.append(
                    f"Score {score} outside valid range [{MIN_SCORE}, {MAX_SCORE}]"
                )
            metadata["score"] = score
        else:
            violations.append("Missing 'score' field")

        # Check quality level
        if hasattr(macro_score, "quality_level"):
            quality = getattr(macro_score, "quality_level")
            valid_qualities = {
                QUALITY_LEVEL_EXCELENTE,
                QUALITY_LEVEL_BUENO,
                QUALITY_LEVEL_ACEPTABLE,
                QUALITY_LEVEL_INSUFICIENTE,
            }
            if quality not in valid_qualities:
                violations.append(
                    f"Invalid quality level '{quality}'. Must be one of {valid_qualities}"
                )
            metadata["quality_level"] = quality
        else:
            violations.append("Missing 'quality_level' field")

        # Check cross-cutting coherence [0, 1]
        if hasattr(macro_score, "cross_cutting_coherence"):
            coherence = getattr(macro_score, "cross_cutting_coherence")
            if not (0.0 <= coherence <= 1.0):
                violations.append(
                    f"Cross-cutting coherence {coherence} outside valid range [0, 1]"
                )
            metadata["cross_cutting_coherence"] = coherence
        else:
            violations.append("Missing 'cross_cutting_coherence' field")

        # Check strategic alignment [0, 1]
        if hasattr(macro_score, "strategic_alignment"):
            alignment = getattr(macro_score, "strategic_alignment")
            if not (0.0 <= alignment <= 1.0):
                violations.append(
                    f"Strategic alignment {alignment} outside valid range [0, 1]"
                )
            metadata["strategic_alignment"] = alignment
        else:
            violations.append("Missing 'strategic_alignment' field")

        # Check traceability
        if hasattr(macro_score, "cluster_scores"):
            cluster_scores = getattr(macro_score, "cluster_scores")
            if not cluster_scores or len(cluster_scores) == 0:
                violations.append("No cluster scores provided (not traceable)")
            metadata["cluster_count"] = len(cluster_scores) if cluster_scores else 0
        else:
            violations.append("Missing 'cluster_scores' field (not traceable)")

        # Check for systemic gaps
        if hasattr(macro_score, "systemic_gaps"):
            systemic_gaps = getattr(macro_score, "systemic_gaps")
            metadata["systemic_gaps_count"] = len(systemic_gaps) if systemic_gaps else 0
        else:
            metadata["systemic_gaps_count"] = 0

        # Determine validation status
        is_valid = len(violations) == 0

        # Add validation metadata
        metadata["is_valid"] = is_valid
        metadata["violations_count"] = len(violations)

        # Log validation result
        if is_valid:
            logger.info(
                f"Exit contract validation passed: MacroScore ready for Phase 8"
            )
        else:
            logger.warning(
                f"Exit contract validation failed: {len(violations)} violations detected"
            )

        # Raise exception in strict mode
        if not is_valid and strict_mode:
            raise ExitContractViolationError(
                f"Exit contract validation failed with {len(violations)} violations:\n" +
                "\n".join(violations)
            )

        return is_valid, violations, metadata

    def extract_delivery_metadata(
        self,
        macro_score: Any,
    ) -> Dict[str, Any]:
        """
        Extract delivery metadata from output data.

        Args:
            macro_score: MacroScore object

        Returns:
            Delivery metadata dict
        """
        metadata = {
            META_PROVENANCE_SOURCE_PHASE: "PHASE_4_7",
            META_PROVENANCE_NODE_ID: self.source_node,
            "target_phase": self.target_phase,
            "target_node": self.target_node,
        }

        # Extract core metrics
        if hasattr(macro_score, "score"):
            metadata["score"] = getattr(macro_score, "score")
        if hasattr(macro_score, "quality_level"):
            metadata["quality_level"] = getattr(macro_score, "quality_level")
        if hasattr(macro_score, "cross_cutting_coherence"):
            metadata["cross_cutting_coherence"] = getattr(macro_score, "cross_cutting_coherence")
        if hasattr(macro_score, "strategic_alignment"):
            metadata["strategic_alignment"] = getattr(macro_score, "strategic_alignment")

        # Extract traceability info
        if hasattr(macro_score, "cluster_scores"):
            cluster_scores = getattr(macro_score, "cluster_scores")
            metadata["cluster_count"] = len(cluster_scores) if cluster_scores else 0

            # Extract cluster IDs
            cluster_ids = []
            if cluster_scores:
                for cs in cluster_scores:
                    if hasattr(cs, "cluster_id"):
                        cluster_ids.append(getattr(cs, "cluster_id"))
            metadata["cluster_ids"] = cluster_ids

        # Extract systemic gaps
        if hasattr(macro_score, "systemic_gaps"):
            systemic_gaps = getattr(macro_score, "systemic_gaps")
            metadata["systemic_gaps"] = systemic_gaps if systemic_gaps else []

        return metadata


def validate_phase4_7_exit(
    macro_score: Any,
    strict_mode: bool = True,
) -> tuple[bool, List[str], Dict[str, Any]]:
    """
    Convenience function to validate Phase 4-7 exit.

    Args:
        macro_score: MacroScore object from Phase 7
        strict_mode: If True, raises exception on validation failure

    Returns:
        Tuple of (is_valid, violations, metadata)
    """
    contract = Phase4_7ExitContract()
    return contract.validate_output(macro_score, strict_mode)


def extract_exit_delivery_metadata(
    macro_score: Any,
) -> Dict[str, Any]:
    """
    Convenience function to extract exit delivery metadata.

    Args:
        macro_score: MacroScore object from Phase 7

    Returns:
        Delivery metadata dict
    """
    contract = Phase4_7ExitContract()
    return contract.extract_delivery_metadata(macro_score)


__all__ = [
    "ExitContractViolationError",
    "Phase4_7ExitContract",
    "validate_phase4_7_exit",
    "extract_exit_delivery_metadata",
]
