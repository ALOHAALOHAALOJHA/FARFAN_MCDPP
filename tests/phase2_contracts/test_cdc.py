"""
Test CDC - Concurrency Determinism Contract
Verifies: 1 worker vs N workers produce identical output hash
Thread-safe deterministic execution guarantee
"""
import pytest
import hashlib
import json
from pathlib import Path
from typing import Any

from cross_cutting_infrastructure.contractual.dura_lex.concurrency_determinism import (
    ConcurrencyDeterminismContract,
)


class TestConcurrencyDeterminismContract:
    """CDC: Output hash invariant to worker count."""

    @staticmethod
    def mock_executor(inp: dict[str, Any]) -> dict[str, Any]:
        """Simulates Phase 2 executor processing."""
        content = json.dumps(inp, sort_keys=True)
        return {
            "question_id": inp.get("question_id"),
            "hash": hashlib.blake2b(content.encode()).hexdigest()[:16],
            "score": len(content) % 100 / 100.0,
        }

    @pytest.fixture
    def sample_inputs(self) -> list[dict[str, Any]]:
        """Phase 2 micro-question inputs."""
        return [
            {"question_id": f"Q{i:03d}", "policy_area": f"PA{(i % 10) + 1:02d}"}
            for i in range(1, 31)
        ]

    def test_cdc_001_determinism_1_vs_4_workers(
        self, sample_inputs: list[dict[str, Any]]
    ) -> None:
        """CDC-001: 1 worker vs 4 workers produce identical results."""
        assert ConcurrencyDeterminismContract.verify_determinism(
            self.mock_executor, sample_inputs
        )

    def test_cdc_002_result_order_preserved(
        self, sample_inputs: list[dict[str, Any]]
    ) -> None:
        """CDC-002: Results maintain input order regardless of concurrency."""
        results_1 = ConcurrencyDeterminismContract.execute_concurrently(
            self.mock_executor, sample_inputs, workers=1
        )
        results_4 = ConcurrencyDeterminismContract.execute_concurrently(
            self.mock_executor, sample_inputs, workers=4
        )
        for i, (r1, r4) in enumerate(zip(results_1, results_4)):
            assert r1["question_id"] == r4["question_id"], f"Order mismatch at {i}"

    def test_cdc_003_hash_equality(self, sample_inputs: list[dict[str, Any]]) -> None:
        """CDC-003: Output hashes are bitwise identical."""
        results_seq = ConcurrencyDeterminismContract.execute_concurrently(
            self.mock_executor, sample_inputs, workers=1
        )
        results_conc = ConcurrencyDeterminismContract.execute_concurrently(
            self.mock_executor, sample_inputs, workers=8
        )
        hash_seq = hashlib.blake2b(
            json.dumps(results_seq, sort_keys=True).encode()
        ).hexdigest()
        hash_conc = hashlib.blake2b(
            json.dumps(results_conc, sort_keys=True).encode()
        ).hexdigest()
        assert hash_seq == hash_conc

    def test_cdc_004_empty_input(self) -> None:
        """CDC-004: Empty input produces empty output deterministically."""
        results = ConcurrencyDeterminismContract.execute_concurrently(
            self.mock_executor, [], workers=4
        )
        assert results == []

    def test_cdc_005_single_item(self) -> None:
        """CDC-005: Single item deterministic across worker counts."""
        single = [{"question_id": "Q001", "policy_area": "PA01"}]
        r1 = ConcurrencyDeterminismContract.execute_concurrently(
            self.mock_executor, single, workers=1
        )
        r4 = ConcurrencyDeterminismContract.execute_concurrently(
            self.mock_executor, single, workers=4
        )
        assert r1 == r4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
