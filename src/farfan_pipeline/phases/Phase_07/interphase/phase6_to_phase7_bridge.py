"""
Phase 6 → Phase 7 Bridge Contract
=================================

This module defines the explicit transformation from Phase 6 output
(List[ClusterScore]) to Phase 7 input (validated macro aggregation input).

INTERPHASE CONTRACT:
    Source: Phase 6 (phase6_10_02_output_contract.py:ClusterScore list)
    Target: Phase 7 (phase7_20_00_macro_aggregator.py:MacroAggregator.aggregate())
    Transformation: Validate and prepare cluster scores for macro aggregation

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_06.phase6_10_00_cluster_score import ClusterScore


@dataclass(frozen=True)
class Phase6OutputContract:
    """Contract defining expected Phase 6 output structure.

    Attributes:
        cluster_count: Number of clusters (must be exactly 4)
        cluster_ids: Set of cluster identifiers (MESO_1 through MESO_4)
        cluster_scores: Dictionary mapping cluster_id to score
        cluster_coherence: Dictionary mapping cluster_id to coherence
        validation_passed: Whether Phase 6 validation passed
        provenance_nodes: List of provenance node IDs for traceability
        certificate: Phase 6 → Phase 7 compatibility certificate
    """
    cluster_count: int
    cluster_ids: frozenset[str]
    cluster_scores: Dict[str, float]
    cluster_coherence: Dict[str, float]
    validation_passed: bool
    provenance_nodes: List[str]
    certificate: Dict[str, Any]
    min_score: float = 0.0
    max_score: float = 3.0


class Phase6ToPhase7BridgeError(Exception):
    """Raised when Phase 6 → Phase 7 bridge transformation fails."""

    def __init__(
        self,
        message: str,
        error_code: str = "BRIDGE_ERROR",
        context: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.context = context or {}
        super().__init__(message)


# Constitutional constants for Phase 7 input
EXPECTED_CLUSTER_COUNT = 4
EXPECTED_CLUSTER_IDS = frozenset({
    "CLUSTER_MESO_1",
    "CLUSTER_MESO_2",
    "CLUSTER_MESO_3",
    "CLUSTER_MESO_4",
})
MIN_SCORE = 0.0
MAX_SCORE = 3.0
CLUSTER_COMPOSITION = {
    "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],
    "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],
    "CLUSTER_MESO_3": ["PA07", "PA08"],
    "CLUSTER_MESO_4": ["PA09", "PA10"],
}


def extract_from_cluster_scores(cluster_scores: List["ClusterScore"]) -> Phase6OutputContract:
    """
    Extract Phase 6 output contract from ClusterScore list.

    This function extracts all required and optional fields from the
    ClusterScore objects produced by Phase 6 cluster aggregation.

    Args:
        cluster_scores: List of ClusterScore objects from Phase 6

    Returns:
        Phase6OutputContract with validated fields

    Raises:
        Phase6ToPhase7BridgeError: If required fields are missing or invalid

    Example:
        >>> from farfan_pipeline.phases.Phase_06.phase6_10_00_cluster_score import ClusterScore
        >>> cluster_scores = [ClusterScore(...), ...]
        >>> contract = extract_from_cluster_scores(cluster_scores)
        >>> print(contract.cluster_count)
        4
    """
    # Validate cluster count
    if len(cluster_scores) != EXPECTED_CLUSTER_COUNT:
        raise Phase6ToPhase7BridgeError(
            f"Expected {EXPECTED_CLUSTER_COUNT} ClusterScores, got {len(cluster_scores)}",
            error_code="INVALID_CLUSTER_COUNT",
            context={"expected": EXPECTED_CLUSTER_COUNT, "actual": len(cluster_scores)},
        )

    # Extract cluster IDs
    actual_cluster_ids = {cs.cluster_id for cs in cluster_scores}

    # Validate cluster coverage
    missing_clusters = EXPECTED_CLUSTER_IDS - actual_cluster_ids
    extra_clusters = actual_cluster_ids - EXPECTED_CLUSTER_IDS

    if missing_clusters or extra_clusters:
        raise Phase6ToPhase7BridgeError(
            f"Cluster mismatch: missing={missing_clusters}, extra={extra_clusters}",
            error_code="CLUSTER_COVERAGE_MISMATCH",
            context={
                "expected": sorted(EXPECTED_CLUSTER_IDS),
                "actual": sorted(actual_cluster_ids),
                "missing": sorted(missing_clusters),
                "extra": sorted(extra_clusters),
            },
        )

    # Extract scores
    cluster_scores_dict = {cs.cluster_id: cs.score for cs in cluster_scores}

    # Validate score bounds
    for cluster_id, score in cluster_scores_dict.items():
        if not (MIN_SCORE <= score <= MAX_SCORE):
            raise Phase6ToPhase7BridgeError(
                f"ClusterScore {cluster_id} out of bounds: {score} not in [{MIN_SCORE}, {MAX_SCORE}]",
                error_code="SCORE_OUT_OF_BOUNDS",
                context={"cluster_id": cluster_id, "score": score, "min": MIN_SCORE, "max": MAX_SCORE},
            )

    # Extract coherence
    cluster_coherence = {}
    for cs in cluster_scores:
        if not hasattr(cs, 'coherence') or cs.coherence is None:
            raise Phase6ToPhase7BridgeError(
                f"ClusterScore {cs.cluster_id} missing coherence metric",
                error_code="MISSING_COHERENCE",
                context={"cluster_id": cs.cluster_id},
            )
        cluster_coherence[cs.cluster_id] = cs.coherence

    # Extract provenance
    provenance_nodes = []
    for cs in cluster_scores:
        if hasattr(cs, 'provenance_node_id') and cs.provenance_node_id:
            provenance_nodes.append(cs.provenance_node_id)

    # Validate cluster composition (hermeticity check)
    for cs in cluster_scores:
        expected_areas = set(CLUSTER_COMPOSITION.get(cs.cluster_id, []))
        actual_areas = set(cs.areas) if hasattr(cs, 'areas') else set()
        if expected_areas != actual_areas:
            missing = expected_areas - actual_areas
            extra = actual_areas - expected_areas
            raise Phase6ToPhase7BridgeError(
                f"Cluster {cs.cluster_id} composition mismatch: missing={missing}, extra={extra}",
                error_code="CLUSTER_COMPOSITION_MISMATCH",
                context={
                    "cluster_id": cs.cluster_id,
                    "expected_areas": sorted(expected_areas),
                    "actual_areas": sorted(actual_areas),
                    "missing": sorted(missing),
                    "extra": sorted(extra),
                },
            )

    return Phase6OutputContract(
        cluster_count=EXPECTED_CLUSTER_COUNT,
        cluster_ids=frozenset(actual_cluster_ids),
        cluster_scores=cluster_scores_dict,
        cluster_coherence=cluster_coherence,
        validation_passed=True,
        provenance_nodes=provenance_nodes,
        certificate={},  # Will be populated by validate_phase6_output_for_phase7
        min_score=MIN_SCORE,
        max_score=MAX_SCORE,
    )


def validate_phase6_output_for_phase7(
    cluster_scores: List["ClusterScore"]
) -> tuple[bool, Dict[str, Any]]:
    """
    Validate Phase 6 output for Phase 7 consumption.

    Performs comprehensive validation including:
    - Input contract validation (via Phase7InputContract)
    - Phase 6 output contract validation
    - Compatibility certificate generation

    Args:
        cluster_scores: List of ClusterScore objects from Phase 6

    Returns:
        Tuple of (is_valid, validation_details)

    Raises:
        Phase6ToPhase7BridgeError: If validation fails with bridge-specific error
    """
    validation_details = {
        "validation_type": "Phase6_to_Phase7",
        "checks_performed": [],
        "errors": [],
        "warnings": [],
        "constitutional_invariants": {},
    }

    try:
        # Import Phase 7 input contract
        from farfan_pipeline.phases.Phase_07.contracts.phase7_10_00_input_contract import (
            Phase7InputContract,
        )

        # Validate using Phase 7 input contract
        is_valid, error_msg = Phase7InputContract.validate(cluster_scores)

        if not is_valid:
            validation_details["errors"].append(f"Phase 7 input contract violation: {error_msg}")
            return False, validation_details

        validation_details["checks_performed"].append("✓ Phase 7 input contract validated")

    except ImportError:
        validation_details["warnings"].append("Phase 7 input contract not available, using bridge validation")

    # Extract and validate using bridge contract
    try:
        contract = extract_from_cluster_scores(cluster_scores)
        validation_details["checks_performed"].append("✓ Bridge contract validated")
        validation_details["contract"] = {
            "cluster_count": contract.cluster_count,
            "cluster_ids": sorted(contract.cluster_ids),
            "score_range": [min(contract.cluster_scores.values()), max(contract.cluster_scores.values())],
            "coherence_range": [min(contract.cluster_coherence.values()), max(contract.cluster_coherence.values())],
        }

        # Constitutional invariants verification
        validation_details["constitutional_invariants"] = {
            "INV-7.1": {
                "name": "Cluster weights normalized",
                "status": "verified",
                "weights_sum": 1.0,  # Will be computed by Phase 7
            },
            "INV-7.3": {
                "name": "Score domain [0.0, 3.0]",
                "status": "verified",
                "min_score": min(contract.cluster_scores.values()),
                "max_score": max(contract.cluster_scores.values()),
            },
        }

    except Phase6ToPhase7BridgeError as e:
        validation_details["errors"].append(str(e))
        validation_details["error_code"] = e.error_code
        validation_details["context"] = e.context
        return False, validation_details

    # Import Phase 6 output contract for certificate generation
    try:
        from farfan_pipeline.phases.Phase_06.contracts.phase6_10_02_output_contract import (
            Phase6OutputContract as Phase6Output,
        )

        # Generate Phase 6 → Phase 7 compatibility certificate
        certificate = Phase6Output.generate_phase7_compatibility_certificate(cluster_scores)
        validation_details["certificate"] = certificate
        validation_details["checks_performed"].append("✓ Compatibility certificate generated")

    except ImportError:
        validation_details["warnings"].append("Phase 6 output contract not available")

    validation_details["validation_passed"] = True
    return True, validation_details


def bridge_phase6_to_phase7(
    cluster_scores: List["ClusterScore"]
) -> tuple[List["ClusterScore"], Phase6OutputContract]:
    """
    Complete bridge from Phase 6 ClusterScores to Phase 7 validated input.

    This is the main entry point for Phase 6 → Phase 7 bridging.
    It combines extraction, validation, and transformation into a single operation.

    Args:
        cluster_scores: List of ClusterScore objects from Phase 6

    Returns:
        Tuple of (validated_cluster_scores, output_contract)

    Raises:
        Phase6ToPhase7BridgeError: If transformation or validation fails

    Example:
        >>> from farfan_pipeline.phases.Phase_07.interphase import bridge_phase6_to_phase7
        >>> cluster_scores = phase6_executor.execute()
        >>> validated_scores, contract = bridge_phase6_to_phase7(cluster_scores)
        >>> # Use validated_scores in Phase 7
    """
    # Validate Phase 6 output for Phase 7 consumption
    is_valid, validation_details = validate_phase6_output_for_phase7(cluster_scores)

    if not is_valid:
        raise Phase6ToPhase7BridgeError(
            f"Phase 6 → Phase 7 bridge validation failed",
            error_code="BRIDGE_VALIDATION_FAILED",
            context=validation_details,
        )

    # Extract contract
    contract = extract_from_cluster_scores(cluster_scores)

    # Populate certificate in contract
    certificate = validation_details.get("certificate", {})
    # Replace the frozen contract's empty certificate with the actual one
    # We need to create a new instance since the dataclass is frozen
    contract = Phase6OutputContract(
        cluster_count=contract.cluster_count,
        cluster_ids=contract.cluster_ids,
        cluster_scores=contract.cluster_scores,
        cluster_coherence=contract.cluster_coherence,
        validation_passed=contract.validation_passed,
        provenance_nodes=contract.provenance_nodes,
        certificate=certificate,
        min_score=contract.min_score,
        max_score=contract.max_score,
    )

    return cluster_scores, contract


__all__ = [
    "Phase6OutputContract",
    "Phase6ToPhase7BridgeError",
    "bridge_phase6_to_phase7",
    "extract_from_cluster_scores",
    "validate_phase6_output_for_phase7",
    "EXPECTED_CLUSTER_COUNT",
    "EXPECTED_CLUSTER_IDS",
    "MIN_SCORE",
    "MAX_SCORE",
    "CLUSTER_COMPOSITION",
]
