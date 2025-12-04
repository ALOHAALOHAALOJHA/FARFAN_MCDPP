"""Chunk matrix construction and validation for policy analysis pipeline.

This module provides deterministic construction of the 60-chunk PA×DIM matrix
with comprehensive validation, duplicate detection, and audit logging.
"""

import logging
import re
from functools import lru_cache
from collections.abc import Iterable

from farfan_pipeline.core.types import ChunkData, PreprocessedDocument
from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire

logger = logging.getLogger(__name__)

CHUNK_ID_PATTERN = re.compile(r"^PA\d{2}-DIM\d{2}$")
MAX_MISSING_KEYS_TO_DISPLAY = 10


@lru_cache
def _expected_axes_from_monolith() -> tuple[list[str], list[str]]:
    """Load unique policy areas and dimensions from questionnaire monolith."""
    questionnaire = load_questionnaire()
    micro_questions = questionnaire.get_micro_questions()

    policy_areas = sorted(
        {
            q.get("policy_area_id")
            for q in micro_questions
            if q.get("policy_area_id")
        }
    )
    dimensions = sorted(
        {
            q.get("dimension_id")
            for q in micro_questions
            if q.get("dimension_id")
        }
    )

    if not policy_areas or not dimensions:
        raise ValueError(
            "Questionnaire monolith is missing policy_area_id or dimension_id values"
        )

    return policy_areas, dimensions


POLICY_AREAS, DIMENSIONS = _expected_axes_from_monolith()
EXPECTED_CHUNK_COUNT = len(POLICY_AREAS) * len(DIMENSIONS)


def build_chunk_matrix(
    document: PreprocessedDocument,
) -> tuple[dict[tuple[str, str], ChunkData], list[tuple[str, str]]]:
    """Construct validated chunk matrix from preprocessed document.

    Builds a dictionary mapping (PA, DIM) tuples to SmartPolicyChunk instances,
    performs comprehensive validation, and returns sorted keys for deterministic
    iteration.

    Args:
        document: PreprocessedDocument containing 60 policy chunks

    Returns:
        Tuple of (chunk_matrix, sorted_keys) where:
        - chunk_matrix: dict mapping (PA, DIM) -> ChunkData
        - sorted_keys: list of (PA, DIM) tuples sorted deterministically

    Raises:
        ValueError: If validation fails (wrong count, duplicates, missing combinations,
                   null IDs, or invalid chunk_id format)

    Example:
        >>> doc = PreprocessedDocument(...)
        >>> matrix, keys = build_chunk_matrix(doc)
        >>> chunk = matrix[("PA01", "DIM01")]
        >>> assert len(keys) == 60
        >>> assert keys[0] == ("PA01", "DIM01")
    """
    logger.info(
        f"Building chunk matrix from document {document.document_id} "
        f"with {len(document.chunks)} chunks"
    )

    matrix: dict[tuple[str, str], ChunkData] = {}
    seen_keys: set[tuple[str, str]] = set()
    seen_chunk_ids: set[str] = set()
    inserted_count = len(document.chunks)

    for idx, chunk in enumerate(document.chunks):
        _validate_chunk_metadata(chunk, idx)

        assert chunk.policy_area_id is not None
        assert chunk.dimension_id is not None

        if not chunk.policy_area_id.startswith("PA"):
            raise ValueError(
                f"Chunk at index {idx} policy_area_id '{chunk.policy_area_id}' "
                "must start with 'PA'"
            )
        if not chunk.dimension_id.startswith("DIM"):
            raise ValueError(
                f"Chunk at index {idx} dimension_id '{chunk.dimension_id}' "
                "must start with 'DIM'"
            )

        chunk_id = chunk.chunk_id or f"{chunk.policy_area_id}-{chunk.dimension_id}"
        _validate_chunk_id_format(chunk_id, idx)

        key = (chunk.policy_area_id, chunk.dimension_id)
        _validate_chunk_id_matches_key(chunk_id, key, idx)

        _check_duplicate_key(key, seen_keys, chunk_id)
        _check_duplicate_chunk_id(chunk_id, seen_chunk_ids, idx)

        seen_keys.add(key)
        seen_chunk_ids.add(chunk_id)
        matrix[key] = chunk

    _validate_completeness(seen_keys)
    _validate_chunk_count(matrix, EXPECTED_CHUNK_COUNT)

    unique_count = len(matrix)
    if inserted_count != unique_count:
        logger.warning(
            "chunk_matrix_duplicate_warning",
            extra={
                "inserted_count": inserted_count,
                "unique_count": unique_count,
                "note": "Potential duplicate chunk IDs targeting same PA×DIM slot",
            },
        )

    sorted_keys = _sort_keys_deterministically(matrix.keys())

    logger.info(
        "Chunk matrix constructed successfully: %s chunks, %s unique keys",
        len(matrix),
        len(sorted_keys),
    )
    _log_audit_summary(matrix, sorted_keys)

    return matrix, sorted_keys


def _validate_chunk_metadata(chunk: ChunkData, idx: int) -> None:
    """Validate chunk has required metadata fields.

    Args:
        chunk: ChunkData to validate
        idx: Chunk index for error reporting

    Raises:
        ValueError: If policy_area_id or dimension_id is None
    """
    if chunk.policy_area_id is None:
        raise ValueError(
            f"Chunk at index {idx} (id={chunk.id}) has null policy_area_id"
        )
    if chunk.dimension_id is None:
        raise ValueError(f"Chunk at index {idx} (id={chunk.id}) has null dimension_id")


def _validate_chunk_id_format(chunk_id: str, idx: int) -> None:
    """Validate chunk_id matches PA{01-10}-DIM{01-06} pattern.

    Args:
        chunk_id: Chunk identifier to validate
        idx: Chunk index for error reporting

    Raises:
        ValueError: If chunk_id format is invalid
    """
    if not CHUNK_ID_PATTERN.match(chunk_id):
        raise ValueError(
            f"Invalid chunk_id format at index {idx}: '{chunk_id}' "
            "(expected PAxx-DIMyy pattern)"
        )


def _validate_chunk_id_matches_key(
    chunk_id: str, key: tuple[str, str], idx: int
) -> None:
    """Validate chunk_id matches dictionary key tuple."""
    expected_chunk_id = f"{key[0]}-{key[1]}"
    if chunk_id != expected_chunk_id:
        raise ValueError(
            f"Chunk ID mismatch at index {idx}: expected '{expected_chunk_id}' "
            f"from key, found '{chunk_id}'"
        )


def _check_duplicate_key(
    key: tuple[str, str],
    seen_keys: set[tuple[str, str]],
    chunk_id: str,
) -> None:
    """Check for duplicate (PA, DIM) keys.

    Args:
        key: (policy_area_id, dimension_id) tuple
        seen_keys: Set of previously seen keys
        chunk_id: Chunk identifier for error reporting

    Raises:
        ValueError: If key already exists in seen_keys
    """
    if key in seen_keys:
        raise ValueError(
            f"Duplicate (PA, DIM) combination detected: {chunk_id}. "
            f"Each PA×DIM combination must appear exactly once."
        )


def _check_duplicate_chunk_id(
    chunk_id: str,
    seen_chunk_ids: set[str],
    idx: int,
) -> None:
    """Check for duplicate chunk_id strings.

    Args:
        chunk_id: Chunk identifier to check
        seen_chunk_ids: Set of previously seen chunk IDs
        idx: Chunk index for error reporting

    Raises:
        ValueError: If chunk_id already exists
    """
    if chunk_id in seen_chunk_ids:
        raise ValueError(
            f"Duplicate chunk_id detected at index {idx}: '{chunk_id}'. "
            f"Each chunk must have a unique identifier."
        )


def _validate_chunk_count(
    matrix: dict[tuple[str, str], ChunkData],
    expected_count: int,
) -> None:
    """Validate document has exactly the expected number of chunks.

    Args:
        matrix: Chunk matrix keyed by (PA, DIM)
        expected_count: Expected number of chunks (60)

    Raises:
        ValueError: If chunk count doesn't match expectation
    """
    actual_count = len(matrix)
    if actual_count != expected_count:
        raise ValueError(
            "Chunk Matrix Invariant Violation: Expected "
            f"{expected_count} unique (PA, DIM) chunks but found {actual_count}"
        )


def _validate_completeness(seen_keys: set[tuple[str, str]]) -> None:
    """Validate all required PA×DIM combinations are present.

    Args:
        seen_keys: Set of (PA, DIM) keys found in document

    Raises:
        ValueError: If any required combinations are missing
    """
    expected_keys = {(pa, dim) for pa in POLICY_AREAS for dim in DIMENSIONS}
    missing_keys = expected_keys - seen_keys

    if missing_keys:
        missing_formatted = sorted(missing_keys)
        raise ValueError(f"Missing chunk combinations: {missing_formatted}")


def _sort_keys_deterministically(
    keys: Iterable[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Sort matrix keys deterministically by PA then DIM.

    Args:
        keys: Iterable of (PA, DIM) tuple keys

    Returns:
        Sorted list of keys for deterministic iteration
    """
    return sorted(keys, key=lambda k: (k[0], k[1]))


def _log_audit_summary(
    matrix: dict[tuple[str, str], ChunkData],
    sorted_keys: list[tuple[str, str]],
) -> None:
    """Log audit summary of constructed matrix.

    Args:
        matrix: Constructed chunk matrix
        sorted_keys: Sorted list of matrix keys
    """
    pa_counts: dict[str, int] = {pa: 0 for pa in POLICY_AREAS}
    dim_counts: dict[str, int] = {dim: 0 for dim in DIMENSIONS}

    for pa, dim in sorted_keys:
        pa_counts[pa] = pa_counts.get(pa, 0) + 1
        dim_counts[dim] = dim_counts.get(dim, 0) + 1

    total_text_length = sum(len(chunk.text) for chunk in matrix.values())
    avg_text_length = total_text_length // len(matrix) if matrix else 0

    logger.info(
        "chunk_matrix_constructed",
        extra={
            "total_chunks": len(matrix),
            "expected_chunks": EXPECTED_CHUNK_COUNT,
            "chunks_per_policy_area": pa_counts,
            "chunks_per_dimension": dim_counts,
            "total_text_chars": total_text_length,
            "avg_chunk_length": avg_text_length,
        },
    )
