"""
Test ReC - Retriever Determinism Contract
Verifies: Top-K is deterministic hash of query+filters+index
Deterministic retrieval guarantee
"""
import pytest
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from cross_cutting_infrastructure.contractual.dura_lex.retriever_contract import (
    RetrieverContract,
)


class TestRetrieverDeterminismContract:
    """ReC: Hybrid retrieval is deterministic."""

    @pytest.fixture
    def query(self) -> str:
        """Phase 2 evidence query."""
        return "línea base diagnóstico género VBG"

    @pytest.fixture
    def filters(self) -> dict[str, Any]:
        """Query filters."""
        return {
            "policy_area": "PA01",
            "dimension": "DIM01",
            "document_type": "PDT",
        }

    @pytest.fixture
    def index_hash(self) -> str:
        """Frozen index hash."""
        return "faiss_index_sha256_abc123def456"

    def test_rec_001_deterministic_retrieval(
        self, query: str, filters: dict[str, Any], index_hash: str
    ) -> None:
        """ReC-001: Same query produces identical results."""
        results1 = RetrieverContract.retrieve(query, filters, index_hash)
        results2 = RetrieverContract.retrieve(query, filters, index_hash)
        assert results1 == results2

    def test_rec_002_digest_deterministic(
        self, query: str, filters: dict[str, Any], index_hash: str
    ) -> None:
        """ReC-002: Retrieval digest is deterministic."""
        digest1 = RetrieverContract.verify_determinism(query, filters, index_hash)
        digest2 = RetrieverContract.verify_determinism(query, filters, index_hash)
        assert digest1 == digest2

    def test_rec_003_different_queries_different_results(
        self, filters: dict[str, Any], index_hash: str
    ) -> None:
        """ReC-003: Different queries produce different results."""
        results1 = RetrieverContract.retrieve("query_a", filters, index_hash)
        results2 = RetrieverContract.retrieve("query_b", filters, index_hash)
        assert results1 != results2

    def test_rec_004_different_filters_different_results(
        self, query: str, index_hash: str
    ) -> None:
        """ReC-004: Different filters produce different results."""
        filters1 = {"policy_area": "PA01"}
        filters2 = {"policy_area": "PA02"}
        results1 = RetrieverContract.retrieve(query, filters1, index_hash)
        results2 = RetrieverContract.retrieve(query, filters2, index_hash)
        assert results1 != results2

    def test_rec_005_different_index_different_results(
        self, query: str, filters: dict[str, Any]
    ) -> None:
        """ReC-005: Different index hash produces different results."""
        results1 = RetrieverContract.retrieve(query, filters, "index_hash_v1")
        results2 = RetrieverContract.retrieve(query, filters, "index_hash_v2")
        assert results1 != results2

    def test_rec_006_top_k_count(
        self, query: str, filters: dict[str, Any], index_hash: str
    ) -> None:
        """ReC-006: Returns exactly top_k results."""
        results_5 = RetrieverContract.retrieve(query, filters, index_hash, top_k=5)
        results_10 = RetrieverContract.retrieve(query, filters, index_hash, top_k=10)
        assert len(results_5) == 5
        assert len(results_10) == 10

    def test_rec_007_result_structure(
        self, query: str, filters: dict[str, Any], index_hash: str
    ) -> None:
        """ReC-007: Results have correct structure."""
        results = RetrieverContract.retrieve(query, filters, index_hash)
        for result in results:
            assert "id" in result
            assert "score" in result
            assert "content_hash" in result
            assert isinstance(result["score"], float)

    def test_rec_008_scores_descending(
        self, query: str, filters: dict[str, Any], index_hash: str
    ) -> None:
        """ReC-008: Results are ordered by descending score."""
        results = RetrieverContract.retrieve(query, filters, index_hash)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_rec_009_phase2_evidence_retrieval(self) -> None:
        """ReC-009: Phase 2 evidence retrieval is deterministic."""
        query = "fuentes oficiales DANE indicadores cuantitativos"
        filters = {
            "policy_area": "PA01",
            "dimension": "DIM01",
            "cluster_id": "CL02",
            "question_type": "micro",
        }
        index_hash = "sisas_signal_index_v3"

        digest1 = RetrieverContract.verify_determinism(query, filters, index_hash)
        digest2 = RetrieverContract.verify_determinism(query, filters, index_hash)
        assert digest1 == digest2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
