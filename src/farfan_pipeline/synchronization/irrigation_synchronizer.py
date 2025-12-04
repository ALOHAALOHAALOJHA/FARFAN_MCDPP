"""Irrigation synchronization and chunk matrix validation for policy analysis."""

from farfan_pipeline.core.orchestrator.chunk_matrix_builder import (
    CHUNK_ID_PATTERN,
    DIMENSIONS,
    EXPECTED_CHUNK_COUNT,
    POLICY_AREAS,
    build_chunk_matrix,
)
from farfan_pipeline.core.types import ChunkData, PreprocessedDocument


class ChunkMatrix:
    """Validates and provides O(1) access to policy chunks organized by area × dimension.

    Delegates validation to core.orchestrator.chunk_matrix_builder to ensure a
    single source of truth aligned with questionnaire_monolith.json.
    """

    POLICY_AREAS = POLICY_AREAS
    DIMENSIONS = DIMENSIONS
    EXPECTED_CHUNK_COUNT = EXPECTED_CHUNK_COUNT
    CHUNK_ID_PATTERN = CHUNK_ID_PATTERN

    def __init__(self, document: PreprocessedDocument) -> None:
        matrix, sorted_keys = build_chunk_matrix(document)
        self.chunks: dict[tuple[str, str], ChunkData] = matrix
        self._matrix = self.chunks  # Backward compatibility for existing callers
        self.sorted_keys = tuple(sorted_keys)

    def get_chunk(self, policy_area_id: str, dimension_id: str) -> ChunkData:
        """Retrieve chunk by policy area and dimension with O(1) lookup."""
        key = (policy_area_id, dimension_id)
        if key not in self.chunks:
            raise KeyError(f"Chunk not found for key: {policy_area_id}-{dimension_id}")
        return self.chunks[key]
