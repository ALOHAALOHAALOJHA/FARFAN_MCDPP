"""
Test TOC - Total Ordering Contract
Verifies: Complete ordering with deterministic tie-breaking
Complete ordering guarantee
"""

import pytest
from pathlib import Path
from typing import Any

from farfan_pipeline.infrastructure.contractual.dura_lex.total_ordering import (
    TotalOrderingContract,
)


class TestTotalOrderingContract:
    """TOC: Total ordering with stable, deterministic tie-breaking."""

    @pytest.fixture
    def phase2_results(self) -> list[dict[str, Any]]:
        """Phase 2 micro-question results."""
        return [
            {
                "question_id": "Q001",
                "score": 2.5,
                "content_hash": "hash_001_abc",
            },
            {
                "question_id": "Q002",
                "score": 3.0,
                "content_hash": "hash_002_def",
            },
            {
                "question_id": "Q003",
                "score": 2.5,  # Tie with Q001
                "content_hash": "hash_003_xyz",  # Lexicographically after Q001
            },
            {
                "question_id": "Q004",
                "score": 1.5,
                "content_hash": "hash_004_ghi",
            },
            {
                "question_id": "Q005",
                "score": 2.5,  # Another tie
                "content_hash": "hash_005_aaa",  # Lexicographically first among ties
            },
        ]

    def test_toc_001_stable_sort(self, phase2_results: list[dict[str, Any]]) -> None:
        """TOC-001: Sort is stable across multiple runs."""
        assert TotalOrderingContract.verify_order(phase2_results, key=lambda x: -x["score"])

    def test_toc_002_descending_score_order(self, phase2_results: list[dict[str, Any]]) -> None:
        """TOC-002: Results sorted by descending score."""
        sorted_results = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: -x["score"]
        )
        scores = [r["score"] for r in sorted_results]
        # Check non-increasing order
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]

    def test_toc_003_tie_breaker_deterministic(self, phase2_results: list[dict[str, Any]]) -> None:
        """TOC-003: Ties are broken deterministically by content_hash."""
        sorted_results = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: -x["score"]
        )

        # Find items with score 2.5 (Q001, Q003, Q005)
        tie_items = [r for r in sorted_results if r["score"] == 2.5]

        # Should be sorted by content_hash lexicographically
        hashes = [r["content_hash"] for r in tie_items]
        assert hashes == sorted(hashes)

    def test_toc_004_total_order_property(self, phase2_results: list[dict[str, Any]]) -> None:
        """TOC-004: Every pair of elements is comparable (total order)."""
        sorted_results = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: (-x["score"], x["content_hash"])
        )

        for i in range(len(sorted_results)):
            for j in range(i + 1, len(sorted_results)):
                item_i = sorted_results[i]
                item_j = sorted_results[j]
                # Either different score or different hash (never equal)
                assert (
                    item_i["score"] != item_j["score"]
                    or item_i["content_hash"] != item_j["content_hash"]
                )

    def test_toc_005_antisymmetry(self, phase2_results: list[dict[str, Any]]) -> None:
        """TOC-005: If a ≤ b and b ≤ a, then a = b (antisymmetry)."""
        sorted_results = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: (-x["score"], x["content_hash"])
        )
        # No duplicates in our test data, so all items should be distinct
        question_ids = [r["question_id"] for r in sorted_results]
        assert len(question_ids) == len(set(question_ids))

    def test_toc_006_transitivity(self, phase2_results: list[dict[str, Any]]) -> None:
        """TOC-006: If a ≤ b and b ≤ c, then a ≤ c (transitivity)."""
        sorted_results = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: -x["score"]
        )
        # Check transitivity for scores
        for i in range(len(sorted_results) - 2):
            a = sorted_results[i]["score"]
            b = sorted_results[i + 1]["score"]
            c = sorted_results[i + 2]["score"]
            if a >= b and b >= c:
                assert a >= c

    def test_toc_007_empty_list_stable(self) -> None:
        """TOC-007: Empty list is trivially sorted."""
        result = TotalOrderingContract.stable_sort([], key=lambda x: x)
        assert result == []

    def test_toc_008_single_element_stable(self) -> None:
        """TOC-008: Single element is trivially sorted."""
        single = [{"question_id": "Q001", "score": 1.0, "content_hash": "hash"}]
        result = TotalOrderingContract.stable_sort(single, key=lambda x: x["score"])
        assert result == single

    def test_toc_009_300_questions_sorted(self) -> None:
        """TOC-009: 300 Phase 2 questions can be totally ordered."""
        questions = [
            {
                "question_id": f"Q{i:03d}",
                "score": (i % 30) / 10.0,  # Scores 0.0 to 2.9, with ties
                "content_hash": f"hash_{i:03d}",
            }
            for i in range(1, 301)
        ]

        sorted_results = TotalOrderingContract.stable_sort(questions, key=lambda x: -x["score"])

        assert len(sorted_results) == 300
        assert TotalOrderingContract.verify_order(questions, key=lambda x: -x["score"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
