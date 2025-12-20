"""
Module: src.canonic_phases.phase_2.phase2_b_carver
Purpose: Transform 60 CPP chunks into exactly 300 micro-answers with full provenance
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18
Python-Version: 3.12+ (uses modern type hints)

Contracts-Enforced:
    - CardinalityContract: Input 60 chunks -> Output 300 micro-answers
    - ProvenanceContract: Every output traces to originating chunk
    - DeterminismContract: Same input + seed = identical output

Determinism:
    Seed-Strategy: PARAMETERIZED via random_seed argument
    State-Management: No internal mutable state; pure function

Inputs:
    - chunk_stream: Iterable[CPPChunk] — Exactly 60 CPP chunks from Phase 1
    - random_seed: int — Seed for deterministic shard generation

Outputs:
    - micro_answers: List[MicroAnswer] — Exactly 300 micro-answers with provenance

Failure-Modes:
    - InputCardinalityViolation: CarverError(E2002) — Input != 60 chunks
    - OutputCardinalityViolation: CarverError(E2002) — Output != 300 answers
    - ProvenanceLoss: ProvenanceError — Chunk_id not traceable
"""
from __future__ import annotations

import hashlib
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Final

from .constants.phase2_constants import (
    CPP_CHUNK_COUNT,
    DEFAULT_RANDOM_SEED,
    ERROR_CODES,
    HASH_ALGORITHM,
    MICRO_ANSWER_COUNT,
    SHARDS_PER_CHUNK,
)
from .contracts.phase2_runtime_contracts import postcondition, precondition

logger: Final = logging.getLogger(__name__)

# === DATA STRUCTURES ===

@dataclass(frozen=True, slots=True)
class CPPChunk:
    """
    Immutable representation of a CPP chunk from Phase 1.

    Invariants:
        - chunk_id is non-empty and unique
        - pa_code and dim_code are valid identifiers
        - content is non-empty
    """
    chunk_id: str
    pa_code: str  # Pregunta Analítica code
    dim_code: str  # Dimension code
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not self.chunk_id:
            raise ValueError("chunk_id must be non-empty")
        if not self.content:
            raise ValueError("content must be non-empty")


@dataclass(frozen=True, slots=True)
class MicroAnswer:
    """
    Immutable representation of a micro-answer produced by carving.

    Invariants:
        - task_id is globally unique
        - chunk_id traces to originating CPPChunk
        - shard_index in range [0, SHARDS_PER_CHUNK)
    """
    task_id: str
    chunk_id: str  # Provenance: originating chunk
    shard_index: int  # Which shard of the chunk (0-4)
    pa_code: str
    dim_code: str
    content: str
    content_hash: str
    executor_id: str = ""  # Assigned after routing

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not 0 <= self.shard_index < SHARDS_PER_CHUNK:
            raise ValueError(
                f"shard_index must be in [0, {SHARDS_PER_CHUNK}), got {self.shard_index}"
            )


# === EXCEPTION TAXONOMY ===

@dataclass
class CarverError(Exception):
    """Raised when carving fails."""
    error_code: str
    expected: int
    actual: int
    message: str

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


@dataclass
class ProvenanceError(Exception):
    """Raised when provenance tracking fails."""
    task_id: str
    details: str


# === CARVER IMPLEMENTATION ===

class Carver:
    """
    Transform CPP chunks into micro-answers with deterministic sharding.

    SUCCESS_CRITERIA:
        - Input: exactly 60 CPPChunk objects
        - Output: exactly 300 MicroAnswer objects
        - Every MicroAnswer.chunk_id exists in input chunks
        - Deterministic: same input + seed = identical output

    FAILURE_MODES:
        - InputCardinalityViolation: len(input) != 60
        - OutputCardinalityViolation: len(output) != 300
        - ProvenanceLoss: MicroAnswer references non-existent chunk

    TERMINATION_CONDITION:
        - All 60 chunks processed
        - 300 micro-answers generated
        - Provenance verified

    CONVERGENCE_RULE:
        - N/A (single-pass transformation)

    VERIFICATION_STRATEGY:
        - test_phase2_carver_300_delivery.py
    """

    def __init__(self, random_seed: int = DEFAULT_RANDOM_SEED) -> None:
        """
        Initialize carver with determinism seed.

        Args:
            random_seed: Seed for deterministic shard content generation
        """
        self._seed: Final = random_seed

    @precondition(
        lambda self, chunks: True,  # Actual validation inside
        "Chunks must be iterable"
    )
    @postcondition(
        lambda result: len(result) == MICRO_ANSWER_COUNT,
        f"Must produce exactly {MICRO_ANSWER_COUNT} micro-answers"
    )
    def carve(self, chunks: Iterable[CPPChunk]) -> list[MicroAnswer]:
        """
        Carve chunks into micro-answers.

        Args:
            chunks: Iterable of exactly 60 CPP chunks

        Returns:
            List of exactly 300 MicroAnswer objects

        Raises:
            CarverError: If cardinality constraints violated
        """
        # Materialize and validate input
        chunk_list = list(chunks)
        self._validate_input_cardinality(chunk_list)

        # Build chunk index for provenance verification
        chunk_index: dict[str, CPPChunk] = {c.chunk_id: c for c in chunk_list}

        # Generate micro-answers
        micro_answers: list[MicroAnswer] = []

        for chunk in chunk_list:
            shards = self._shard_chunk(chunk)
            micro_answers.extend(shards)

        # Validate output cardinality
        self._validate_output_cardinality(micro_answers)

        # Verify provenance integrity
        self._verify_provenance(micro_answers, chunk_index)

        logger.info(
            "Carving complete",
            extra={
                "chunks_processed": len(chunk_list),
                "answers_generated": len(micro_answers),
                "seed": self._seed,
            }
        )

        return micro_answers

    def _validate_input_cardinality(self, chunks: list[CPPChunk]) -> None:
        """Validate exactly 60 input chunks."""
        if len(chunks) != CPP_CHUNK_COUNT:
            error = ERROR_CODES["E2002"]
            raise CarverError(
                error_code=error.code,
                expected=CPP_CHUNK_COUNT,
                actual=len(chunks),
                message=error.message_template.format(
                    expected=CPP_CHUNK_COUNT,
                    actual=len(chunks),
                ),
            )

    def _validate_output_cardinality(self, answers: list[MicroAnswer]) -> None:
        """Validate exactly 300 output answers."""
        if len(answers) != MICRO_ANSWER_COUNT:
            error = ERROR_CODES["E2002"]
            raise CarverError(
                error_code=error.code,
                expected=MICRO_ANSWER_COUNT,
                actual=len(answers),
                message=error.message_template.format(
                    expected=MICRO_ANSWER_COUNT,
                    actual=len(answers),
                ),
            )

    def _verify_provenance(
        self,
        answers: list[MicroAnswer],
        chunk_index: dict[str, CPPChunk],
    ) -> None:
        """Verify every answer traces to a valid chunk."""
        for answer in answers:
            if answer.chunk_id not in chunk_index:
                raise ProvenanceError(
                    task_id=answer.task_id,
                    details=f"chunk_id '{answer.chunk_id}' not found in input chunks",
                )

    def _shard_chunk(self, chunk: CPPChunk) -> list[MicroAnswer]:
        """
        Generate exactly SHARDS_PER_CHUNK micro-answers from a chunk.

        Sharding is deterministic based on chunk content and seed.
        """
        shards: list[MicroAnswer] = []

        for shard_index in range(SHARDS_PER_CHUNK):
            task_id = self._generate_task_id(chunk.chunk_id, shard_index)
            content = self._generate_shard_content(chunk, shard_index)
            content_hash = self._hash_content(content)

            shard = MicroAnswer(
                task_id=task_id,
                chunk_id=chunk.chunk_id,
                shard_index=shard_index,
                pa_code=chunk.pa_code,
                dim_code=chunk.dim_code,
                content=content,
                content_hash=content_hash,
            )
            shards.append(shard)

        return shards

    def _generate_task_id(self, chunk_id: str, shard_index: int) -> str:
        """Generate deterministic task ID."""
        raw = f"{chunk_id}:{shard_index}:{self._seed}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _generate_shard_content(self, chunk: CPPChunk, shard_index: int) -> str:
        """
        Generate shard content deterministically.

        IMPLEMENTATION NOTE:
        This is a placeholder implementation for Phase 2 specification.
        The actual sharding strategy depends on domain-specific requirements:
        - Semantic segmentation using NLP
        - Fixed-size byte partitioning
        - Content-aware boundary detection
        - Question-specific extraction patterns

        The current implementation uses simple concatenation to ensure
        determinism while allowing future enhancement without changing
        the API contract.

        Args:
            chunk: Source CPP chunk
            shard_index: Index of shard within chunk (0-4)

        Returns:
            Deterministically generated shard content
        """
        # Deterministic content derivation (domain-specific implementation)
        return f"{chunk.content}::SHARD_{shard_index}"

    def _hash_content(self, content: str) -> str:
        """Compute content hash for integrity verification."""
        return hashlib.new(HASH_ALGORITHM, content.encode()).hexdigest()


# === PUBLIC API ===

def carve_chunks(
    chunk_stream: Iterable[CPPChunk],
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> list[MicroAnswer]:
    """
    Public API for carving CPP chunks into micro-answers.

    Args:
        chunk_stream: Exactly 60 CPP chunks from Phase 1
        random_seed: Seed for deterministic sharding

    Returns:
        Exactly 300 MicroAnswer objects with full provenance

    Raises:
        CarverError: If cardinality constraints violated
        ProvenanceError: If provenance tracking fails
    """
    carver = Carver(random_seed=random_seed)
    return carver.carve(chunk_stream)
