"""
Test CIC - Context Immutability Contract
Verifies: QuestionContext is frozen, mutation raises FrozenInstanceError
Immutable context enforcement guarantee
"""
import pytest
import sys
from pathlib import Path
from dataclasses import dataclass, FrozenInstanceError
from types import MappingProxyType
from typing import Any


from cross_cutting_infrastructure.contractual.dura_lex.context_immutability import (
    ContextImmutabilityContract,
)


@dataclass(frozen=True)
class QuestionContext:
    """Phase 2 immutable question context."""

    traceability_id: str
    question_id: str
    policy_area_id: str
    dimension_id: str
    dnp_standards: MappingProxyType


class TestContextImmutabilityContract:
    """CIC: Context objects are immutable."""

    @pytest.fixture
    def frozen_context(self) -> QuestionContext:
        """Create frozen Phase 2 context."""
        return QuestionContext(
            traceability_id="TRACE-001",
            question_id="Q001",
            policy_area_id="PA01",
            dimension_id="DIM01",
            dnp_standards=MappingProxyType(
                {"standard_1": "value_1", "standard_2": "value_2"}
            ),
        )

    def test_cic_001_top_level_mutation_fails(
        self, frozen_context: QuestionContext
    ) -> None:
        """CIC-001: Top-level attribute mutation raises FrozenInstanceError."""
        with pytest.raises(FrozenInstanceError):
            frozen_context.traceability_id = "MUTATED"  # type: ignore[misc]

    def test_cic_002_deep_mutation_fails(
        self, frozen_context: QuestionContext
    ) -> None:
        """CIC-002: Deep mapping mutation raises TypeError."""
        with pytest.raises(TypeError):
            frozen_context.dnp_standards["__MUTATE__"] = 1  # type: ignore[index]

    def test_cic_003_canonical_digest_stable(
        self, frozen_context: QuestionContext
    ) -> None:
        """CIC-003: Canonical digest is deterministic."""
        digest1 = ContextImmutabilityContract.canonical_digest(frozen_context)
        digest2 = ContextImmutabilityContract.canonical_digest(frozen_context)
        assert digest1 == digest2
        assert len(digest1) == 64  # SHA-256 or Blake3

    def test_cic_004_verify_immutability_returns_digest(
        self, frozen_context: QuestionContext
    ) -> None:
        """CIC-004: verify_immutability returns digest after mutation attempts."""
        digest = ContextImmutabilityContract.verify_immutability(frozen_context)
        assert isinstance(digest, str)
        assert len(digest) == 64

    def test_cic_005_different_contexts_different_digests(self) -> None:
        """CIC-005: Different contexts produce different digests."""
        ctx1 = QuestionContext(
            traceability_id="TRACE-001",
            question_id="Q001",
            policy_area_id="PA01",
            dimension_id="DIM01",
            dnp_standards=MappingProxyType({"k": "v1"}),
        )
        ctx2 = QuestionContext(
            traceability_id="TRACE-002",
            question_id="Q002",
            policy_area_id="PA02",
            dimension_id="DIM02",
            dnp_standards=MappingProxyType({"k": "v2"}),
        )
        digest1 = ContextImmutabilityContract.canonical_digest(ctx1)
        digest2 = ContextImmutabilityContract.canonical_digest(ctx2)
        assert digest1 != digest2

    def test_cic_006_equivalent_contexts_same_digest(self) -> None:
        """CIC-006: Equivalent contexts produce identical digests."""
        ctx1 = QuestionContext(
            traceability_id="TRACE-001",
            question_id="Q001",
            policy_area_id="PA01",
            dimension_id="DIM01",
            dnp_standards=MappingProxyType({"a": "1", "b": "2"}),
        )
        ctx2 = QuestionContext(
            traceability_id="TRACE-001",
            question_id="Q001",
            policy_area_id="PA01",
            dimension_id="DIM01",
            dnp_standards=MappingProxyType({"b": "2", "a": "1"}),  # Different order
        )
        digest1 = ContextImmutabilityContract.canonical_digest(ctx1)
        digest2 = ContextImmutabilityContract.canonical_digest(ctx2)
        assert digest1 == digest2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
