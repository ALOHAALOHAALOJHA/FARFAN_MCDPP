"""
Tests for Phase 2 Carver - 300 micro-answer delivery contract.

Run with: pytest tests/canonic_phases/phase_2/test_phase2_carver_300_delivery.py -v
"""

from __future__ import annotations

import pytest
from typing import List

from src.canonic_phases.phase_02.phase2_b_carver import (
    Carver,
    CPPChunk,
    MicroAnswer,
    CarverError,
    carve_chunks,
)
from src.canonic_phases.phase_02.constants.phase2_constants import (
    CPP_CHUNK_COUNT,
    MICRO_ANSWER_COUNT,
    SHARDS_PER_CHUNK,
)


# === TEST FIXTURES ===


@pytest.fixture
def valid_chunks() -> List[CPPChunk]:
    """Create exactly 60 valid CPP chunks."""
    return [
        CPPChunk(
            chunk_id=f"chunk_{i:03d}",
            pa_code=f"PA{(i % 10) + 1:02d}",
            dim_code=f"D{(i % 6) + 1}",
            content=f"Content for chunk {i}",
            metadata={"index": i},
        )
        for i in range(CPP_CHUNK_COUNT)
    ]


@pytest.fixture
def carver() -> Carver:
    """Create a carver with default seed."""
    return Carver(random_seed=42)


# === TESTS ===


class TestCarverConstruction:
    """Test carver construction."""

    def test_construction_with_default_seed(self) -> None:
        """Carver constructs with default seed."""
        carver = Carver()
        assert carver is not None

    def test_construction_with_custom_seed(self) -> None:
        """Carver constructs with custom seed."""
        carver = Carver(random_seed=123)
        assert carver is not None


class TestCardinalityContract:
    """Test strict cardinality enforcement."""

    def test_exact_60_chunks_produces_300_answers(
        self, carver: Carver, valid_chunks: List[CPPChunk]
    ) -> None:
        """Exactly 60 chunks produces exactly 300 micro-answers."""
        micro_answers = carver.carve(valid_chunks)

        assert len(micro_answers) == MICRO_ANSWER_COUNT
        assert len(micro_answers) == 300

    def test_fewer_than_60_chunks_raises_error(self, carver: Carver) -> None:
        """Fewer than 60 chunks raises CarverError."""
        chunks = [
            CPPChunk(
                chunk_id=f"chunk_{i:03d}",
                pa_code="PA01",
                dim_code="D1",
                content=f"Content {i}",
            )
            for i in range(50)  # Only 50 chunks
        ]

        with pytest.raises(CarverError) as exc_info:
            carver.carve(chunks)

        error = exc_info.value
        assert error.error_code == "E2002"
        assert error.expected == CPP_CHUNK_COUNT
        assert error.actual == 50

    def test_more_than_60_chunks_raises_error(self, carver: Carver) -> None:
        """More than 60 chunks raises CarverError."""
        chunks = [
            CPPChunk(
                chunk_id=f"chunk_{i:03d}",
                pa_code="PA01",
                dim_code="D1",
                content=f"Content {i}",
            )
            for i in range(70)  # Too many chunks
        ]

        with pytest.raises(CarverError) as exc_info:
            carver.carve(chunks)

        error = exc_info.value
        assert error.error_code == "E2002"
        assert error.expected == CPP_CHUNK_COUNT
        assert error.actual == 70


class TestProvenanceContract:
    """Test provenance tracking and validation."""

    def test_every_answer_traces_to_chunk(
        self, carver: Carver, valid_chunks: List[CPPChunk]
    ) -> None:
        """Every micro-answer traces to an originating chunk."""
        micro_answers = carver.carve(valid_chunks)
        chunk_ids = {chunk.chunk_id for chunk in valid_chunks}

        for answer in micro_answers:
            assert answer.chunk_id in chunk_ids

    def test_provenance_metadata_preserved(
        self, carver: Carver, valid_chunks: List[CPPChunk]
    ) -> None:
        """PA codes and dimension codes preserved in micro-answers."""
        micro_answers = carver.carve(valid_chunks)

        for answer in micro_answers:
            # Find originating chunk
            orig_chunk = next(c for c in valid_chunks if c.chunk_id == answer.chunk_id)
            assert answer.pa_code == orig_chunk.pa_code
            assert answer.dim_code == orig_chunk.dim_code

    def test_task_ids_are_unique(self, carver: Carver, valid_chunks: List[CPPChunk]) -> None:
        """Every micro-answer has a unique task_id."""
        micro_answers = carver.carve(valid_chunks)
        task_ids = [answer.task_id for answer in micro_answers]

        assert len(task_ids) == len(set(task_ids))


class TestShardingContract:
    """Test deterministic sharding behavior."""

    def test_exactly_5_shards_per_chunk(self, carver: Carver, valid_chunks: List[CPPChunk]) -> None:
        """Each chunk produces exactly 5 micro-answer shards."""
        micro_answers = carver.carve(valid_chunks)

        for chunk in valid_chunks:
            shards = [a for a in micro_answers if a.chunk_id == chunk.chunk_id]
            assert len(shards) == SHARDS_PER_CHUNK

    def test_shard_indices_are_sequential(
        self, carver: Carver, valid_chunks: List[CPPChunk]
    ) -> None:
        """Shard indices are 0, 1, 2, 3, 4 for each chunk."""
        micro_answers = carver.carve(valid_chunks)

        for chunk in valid_chunks:
            shards = [a for a in micro_answers if a.chunk_id == chunk.chunk_id]
            shard_indices = sorted([s.shard_index for s in shards])
            assert shard_indices == list(range(SHARDS_PER_CHUNK))

    def test_content_hash_integrity(self, carver: Carver, valid_chunks: List[CPPChunk]) -> None:
        """Every micro-answer has a content hash."""
        micro_answers = carver.carve(valid_chunks)

        for answer in micro_answers:
            assert answer.content_hash
            assert len(answer.content_hash) > 0


class TestDeterminism:
    """Test deterministic behavior with seeds."""

    def test_same_seed_produces_identical_output(self, valid_chunks: List[CPPChunk]) -> None:
        """Same seed produces identical micro-answers."""
        carver1 = Carver(random_seed=42)
        carver2 = Carver(random_seed=42)

        answers1 = carver1.carve(valid_chunks)
        answers2 = carver2.carve(valid_chunks)

        assert len(answers1) == len(answers2)

        for a1, a2 in zip(answers1, answers2):
            assert a1.task_id == a2.task_id
            assert a1.chunk_id == a2.chunk_id
            assert a1.shard_index == a2.shard_index
            assert a1.content == a2.content
            assert a1.content_hash == a2.content_hash

    def test_different_seed_produces_different_task_ids(self, valid_chunks: List[CPPChunk]) -> None:
        """Different seeds produce different task IDs."""
        carver1 = Carver(random_seed=42)
        carver2 = Carver(random_seed=99)

        answers1 = carver1.carve(valid_chunks)
        answers2 = carver2.carve(valid_chunks)

        task_ids1 = {a.task_id for a in answers1}
        task_ids2 = {a.task_id for a in answers2}

        # Task IDs should be different due to seed in generation
        assert task_ids1 != task_ids2


class TestDataStructures:
    """Test data structure invariants."""

    def test_cpp_chunk_validation(self) -> None:
        """CPPChunk validates invariants."""
        # Valid chunk
        chunk = CPPChunk(
            chunk_id="test_chunk",
            pa_code="PA01",
            dim_code="D1",
            content="Test content",
        )
        assert chunk.chunk_id == "test_chunk"

        # Empty chunk_id raises
        with pytest.raises(ValueError):
            CPPChunk(
                chunk_id="",
                pa_code="PA01",
                dim_code="D1",
                content="Test content",
            )

        # Empty content raises
        with pytest.raises(ValueError):
            CPPChunk(
                chunk_id="test_chunk",
                pa_code="PA01",
                dim_code="D1",
                content="",
            )

    def test_micro_answer_validation(self) -> None:
        """MicroAnswer validates shard_index range."""
        # Valid shard index
        answer = MicroAnswer(
            task_id="task_001",
            chunk_id="chunk_001",
            shard_index=2,
            pa_code="PA01",
            dim_code="D1",
            content="Test content",
            content_hash="abc123",
        )
        assert answer.shard_index == 2

        # Invalid shard index raises
        with pytest.raises(ValueError):
            MicroAnswer(
                task_id="task_001",
                chunk_id="chunk_001",
                shard_index=5,  # Out of range
                pa_code="PA01",
                dim_code="D1",
                content="Test content",
                content_hash="abc123",
            )

        with pytest.raises(ValueError):
            MicroAnswer(
                task_id="task_001",
                chunk_id="chunk_001",
                shard_index=-1,  # Negative
                pa_code="PA01",
                dim_code="D1",
                content="Test content",
                content_hash="abc123",
            )


class TestPublicAPI:
    """Test public API function."""

    def test_carve_chunks_function(self, valid_chunks: List[CPPChunk]) -> None:
        """Public carve_chunks function works correctly."""
        micro_answers = carve_chunks(valid_chunks, random_seed=42)

        assert len(micro_answers) == MICRO_ANSWER_COUNT
        assert all(isinstance(a, MicroAnswer) for a in micro_answers)

    def test_carve_chunks_with_default_seed(self, valid_chunks: List[CPPChunk]) -> None:
        """carve_chunks uses default seed when not specified."""
        micro_answers = carve_chunks(valid_chunks)

        assert len(micro_answers) == MICRO_ANSWER_COUNT


# === INTEGRATION TESTS ===


class TestCarverIntegration:
    """Integration tests with realistic scenarios."""

    def test_full_pipeline_60_to_300(self, valid_chunks: List[CPPChunk]) -> None:
        """Full pipeline from 60 chunks to 300 micro-answers."""
        carver = Carver(random_seed=42)
        micro_answers = carver.carve(valid_chunks)

        # Verify cardinality
        assert len(micro_answers) == 300

        # Verify provenance
        chunk_ids = {c.chunk_id for c in valid_chunks}
        for answer in micro_answers:
            assert answer.chunk_id in chunk_ids

        # Verify sharding
        for chunk in valid_chunks:
            shards = [a for a in micro_answers if a.chunk_id == chunk.chunk_id]
            assert len(shards) == 5

        # Verify uniqueness
        task_ids = [a.task_id for a in micro_answers]
        assert len(task_ids) == len(set(task_ids))
