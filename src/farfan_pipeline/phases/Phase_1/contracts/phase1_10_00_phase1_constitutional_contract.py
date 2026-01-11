"""Phase 1 Constitutional Contract - 60-Chunk Invariant Enforcement.

This contract enforces the constitutional invariant of Phase 1:
EXACTLY 60 chunks must be produced (10 Policy Areas × 6 Causal Dimensions).

This is a CRITICAL contract that cannot be violated under any circumstances.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EXPECTED_CHUNK_COUNT = 60
EXPECTED_POLICY_AREA_COUNT = 10
EXPECTED_DIMENSION_COUNT = 6


@dataclass(frozen=True)
class PADimCoverage:
    """Policy Area × Dimension coverage specification."""

    policy_area: str
    dimension: str
    chunk_id: str


def validate_constitutional_invariant(cpp: Any) -> bool:
    """Validate Phase 1 constitutional invariant: 60 chunks.

    Args:
        cpp: CanonPolicyPackage from Phase 1

    Returns:
        True if constitutional invariant satisfied

    Raises:
        ValueError: If constitutional invariant violated
    """
    chunk_count = len(cpp.chunk_graph.chunks)

    # CRITICAL: Exactly 60 chunks
    if chunk_count != EXPECTED_CHUNK_COUNT:
        raise ValueError(
            f"CONSTITUTIONAL VIOLATION: Expected {EXPECTED_CHUNK_COUNT} chunks, "
            f"got {chunk_count}. This is a CRITICAL failure."
        )

    # Verify PA × Dimension coverage
    coverage: set[tuple[str, str]] = set()
    policy_areas: set[str] = set()
    dimensions: set[str] = set()

    for chunk in cpp.chunk_graph.chunks:
        if chunk.policy_area is None or chunk.dimension is None:
            raise ValueError(
                f"CONSTITUTIONAL VIOLATION: Chunk {chunk.chunk_id} missing "
                f"Policy Area or Dimension assignment"
            )

        coverage.add((chunk.policy_area, chunk.dimension))
        policy_areas.add(chunk.policy_area)
        dimensions.add(chunk.dimension)

    # Verify exactly 10 Policy Areas
    if len(policy_areas) != EXPECTED_POLICY_AREA_COUNT:
        raise ValueError(
            f"CONSTITUTIONAL VIOLATION: Expected {EXPECTED_POLICY_AREA_COUNT} Policy Areas, "
            f"got {len(policy_areas)}"
        )

    # Verify exactly 6 Dimensions
    if len(dimensions) != EXPECTED_DIMENSION_COUNT:
        raise ValueError(
            f"CONSTITUTIONAL VIOLATION: Expected {EXPECTED_DIMENSION_COUNT} Dimensions, "
            f"got {len(dimensions)}"
        )

    # Verify complete PA × Dimension grid coverage
    expected_coverage = EXPECTED_POLICY_AREA_COUNT * EXPECTED_DIMENSION_COUNT
    if len(coverage) != expected_coverage:
        raise ValueError(
            f"CONSTITUTIONAL VIOLATION: Expected {expected_coverage} PA×Dim combinations, "
            f"got {len(coverage)}"
        )

    return True


def get_padim_coverage_matrix(cpp: Any) -> dict[str, dict[str, str]]:
    """Get PA × Dimension coverage matrix.

    Args:
        cpp: CanonPolicyPackage from Phase 1

    Returns:
        Dict mapping PA → Dimension → chunk_id
    """
    matrix: dict[str, dict[str, str]] = {}

    for chunk in cpp.chunk_graph.chunks:
        pa = chunk.policy_area
        dim = chunk.dimension

        if pa not in matrix:
            matrix[pa] = {}

        matrix[pa][dim] = chunk.chunk_id

    return matrix


__all__ = [
    "EXPECTED_CHUNK_COUNT",
    "EXPECTED_DIMENSION_COUNT",
    "EXPECTED_POLICY_AREA_COUNT",
    "PADimCoverage",
    "get_padim_coverage_matrix",
    "validate_constitutional_invariant",
]
