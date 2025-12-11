"""
Test IDC - Idempotency Contract
Verifies: Content-hash de-duplication, 10 runs = 1 result
Duplicate detection guarantee
"""
import pytest
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cross_cutting_infrastrucuture.contractual.dura_lex.idempotency_dedup import (
    IdempotencyContract,
    EvidenceStore,
)


class TestIdempotencyContract:
    """IDC: Duplicate evidence is blocked."""

    @pytest.fixture
    def sample_evidence(self) -> list[dict[str, Any]]:
        """Phase 2 evidence items with duplicates."""
        return [
            {"question_id": "Q001", "element": "fuente_oficial", "value": "DANE"},
            {"question_id": "Q001", "element": "fuente_oficial", "value": "DANE"},  # dup
            {"question_id": "Q001", "element": "indicador", "value": "12.5%"},
            {"question_id": "Q002", "element": "serie_temporal", "value": "2020-2023"},
            {"question_id": "Q001", "element": "fuente_oficial", "value": "DANE"},  # dup
        ]

    def test_idc_001_duplicates_blocked(
        self, sample_evidence: list[dict[str, Any]]
    ) -> None:
        """IDC-001: Duplicate items are blocked."""
        result = IdempotencyContract.verify_idempotency(sample_evidence)
        assert result["duplicates_blocked"] == 2
        assert result["count"] == 3  # Only 3 unique items

    def test_idc_002_state_hash_stable(
        self, sample_evidence: list[dict[str, Any]]
    ) -> None:
        """IDC-002: State hash is identical for same inputs."""
        result1 = IdempotencyContract.verify_idempotency(sample_evidence)
        result2 = IdempotencyContract.verify_idempotency(sample_evidence)
        assert result1["state_hash"] == result2["state_hash"]

    def test_idc_003_ten_runs_one_result(self) -> None:
        """IDC-003: Processing same item 10 times = 1 stored item."""
        item = {"question_id": "Q001", "element": "test", "value": "data"}
        items = [item] * 10
        result = IdempotencyContract.verify_idempotency(items)
        assert result["count"] == 1
        assert result["duplicates_blocked"] == 9

    def test_idc_004_order_independent_hash(self) -> None:
        """IDC-004: Order of insertion doesn't affect final state hash."""
        items_a = [
            {"id": "A", "v": 1},
            {"id": "B", "v": 2},
            {"id": "C", "v": 3},
        ]
        items_b = [
            {"id": "C", "v": 3},
            {"id": "A", "v": 1},
            {"id": "B", "v": 2},
        ]
        hash_a = IdempotencyContract.verify_idempotency(items_a)["state_hash"]
        hash_b = IdempotencyContract.verify_idempotency(items_b)["state_hash"]
        assert hash_a == hash_b

    def test_idc_005_empty_store(self) -> None:
        """IDC-005: Empty input produces empty store."""
        result = IdempotencyContract.verify_idempotency([])
        assert result["count"] == 0
        assert result["duplicates_blocked"] == 0

    def test_idc_006_evidence_store_direct(self) -> None:
        """IDC-006: Direct EvidenceStore API works correctly."""
        store = EvidenceStore()
        store.add({"question_id": "Q001", "element": "test"})
        store.add({"question_id": "Q001", "element": "test"})  # duplicate
        store.add({"question_id": "Q002", "element": "test"})
        assert len(store.evidence) == 2
        assert store.duplicates_blocked == 1
        assert len(store.state_hash()) == 128  # Blake2b hex digest


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
