"""
Test PIC - Permutation Invariance Contract
Verifies: Aggregation f(S) = φ(Σ ψ(x)) is order-independent
Input order independence guarantee
"""
import pytest
import random
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cross_cutting_infrastrucuture.contractual.dura_lex.permutation_invariance import (
    PermutationInvarianceContract,
)


class TestPermutationInvarianceContract:
    """PIC: Aggregation is invariant to input order."""

    @pytest.fixture
    def evidence_scores(self) -> list[dict[str, Any]]:
        """Phase 2 evidence confidence scores."""
        return [
            {"element_id": "E001", "confidence": 0.92},
            {"element_id": "E002", "confidence": 0.85},
            {"element_id": "E003", "confidence": 0.78},
            {"element_id": "E004", "confidence": 0.95},
            {"element_id": "E005", "confidence": 0.88},
        ]

    @staticmethod
    def transform_confidence(item: dict[str, Any]) -> float:
        """ψ(x) = confidence score."""
        return item["confidence"]

    def test_pic_001_sum_invariant(
        self, evidence_scores: list[dict[str, Any]]
    ) -> None:
        """PIC-001: Sum aggregation is permutation invariant."""
        original_sum = PermutationInvarianceContract.aggregate(
            evidence_scores, self.transform_confidence
        )

        shuffled = evidence_scores.copy()
        random.seed(42)
        random.shuffle(shuffled)

        shuffled_sum = PermutationInvarianceContract.aggregate(
            shuffled, self.transform_confidence
        )

        assert abs(original_sum - shuffled_sum) < 1e-10

    def test_pic_002_digest_invariant(
        self, evidence_scores: list[dict[str, Any]]
    ) -> None:
        """PIC-002: Digest is identical regardless of order."""
        digest_original = PermutationInvarianceContract.verify_invariance(
            evidence_scores, self.transform_confidence
        )

        shuffled = evidence_scores.copy()
        random.seed(123)
        random.shuffle(shuffled)

        digest_shuffled = PermutationInvarianceContract.verify_invariance(
            shuffled, self.transform_confidence
        )

        assert digest_original == digest_shuffled

    def test_pic_003_multiple_permutations(
        self, evidence_scores: list[dict[str, Any]]
    ) -> None:
        """PIC-003: All permutations produce same digest."""
        base_digest = PermutationInvarianceContract.verify_invariance(
            evidence_scores, self.transform_confidence
        )

        for seed in range(10):
            shuffled = evidence_scores.copy()
            random.seed(seed)
            random.shuffle(shuffled)
            shuffled_digest = PermutationInvarianceContract.verify_invariance(
                shuffled, self.transform_confidence
            )
            assert base_digest == shuffled_digest, f"Failed for seed {seed}"

    def test_pic_004_empty_list(self) -> None:
        """PIC-004: Empty list produces zero sum."""
        result = PermutationInvarianceContract.aggregate([], self.transform_confidence)
        assert result == 0.0

    def test_pic_005_single_item(self) -> None:
        """PIC-005: Single item produces its own value."""
        single = [{"element_id": "E001", "confidence": 0.75}]
        result = PermutationInvarianceContract.aggregate(
            single, self.transform_confidence
        )
        assert result == 0.75

    def test_pic_006_phase2_weighted_mean(
        self, evidence_scores: list[dict[str, Any]]
    ) -> None:
        """PIC-006: Weighted mean aggregation is permutation invariant."""

        def weighted_transform(item: dict[str, Any]) -> float:
            # Simulate weighted contribution
            return item["confidence"] * 0.2  # Equal weights

        # Use random shuffle instead of reverse to test permutation invariance
        shuffled = evidence_scores.copy()
        random.seed(999)
        random.shuffle(shuffled)

        sum1 = PermutationInvarianceContract.aggregate(
            evidence_scores, weighted_transform
        )
        sum2 = PermutationInvarianceContract.aggregate(
            shuffled, weighted_transform
        )

        # Sum should be equal (within floating point tolerance)
        assert abs(sum1 - sum2) < 1e-10

    def test_pic_007_distributed_safe(
        self, evidence_scores: list[dict[str, Any]]
    ) -> None:
        """PIC-007: Safe for parallel/distributed aggregation."""
        # Simulate distributed chunks
        chunk1 = evidence_scores[:2]
        chunk2 = evidence_scores[2:]

        sum1 = PermutationInvarianceContract.aggregate(
            chunk1, self.transform_confidence
        )
        sum2 = PermutationInvarianceContract.aggregate(
            chunk2, self.transform_confidence
        )
        distributed_total = sum1 + sum2

        full_total = PermutationInvarianceContract.aggregate(
            evidence_scores, self.transform_confidence
        )

        assert abs(distributed_total - full_total) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
