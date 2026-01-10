"""
Test OT/ASC - Ordering & Total Alignment Contract
Verifies: Fixed params (λ, ε) ⇒ Fixed Plan Hash
Total order consistency guarantee
"""
import pytest
from pathlib import Path
from typing import Any

from cross_cutting_infrastructure.contractual.dura_lex.alignment_stability import (
    AlignmentStabilityContract,
)
from cross_cutting_infrastructure.contractual.dura_lex.total_ordering import (
    TotalOrderingContract,
)


class TestAlignmentStabilityContract:
    """ASC: Optimal Transport alignment is stable with fixed hyperparameters."""

    @pytest.fixture
    def policy_sections(self) -> list[str]:
        """Phase 2 document sections."""
        return [
            "Diagnóstico de género",
            "Línea base VBG",
            "Indicadores cuantitativos",
            "Metas de reducción",
        ]

    @pytest.fixture
    def dnp_standards(self) -> list[str]:
        """DNP standards to align against."""
        return [
            "Estándar diagnóstico territorial",
            "Línea base con fuentes oficiales",
            "Indicadores medibles",
            "Metas SMART",
        ]

    @pytest.fixture
    def alignment_params(self) -> dict[str, Any]:
        """Fixed alignment hyperparameters."""
        return {
            "lambda": 0.1,
            "epsilon": 0.01,
            "max_iter": 1000,
            "method": "EGW",
        }

    def test_asc_001_stability_fixed_params(
        self,
        policy_sections: list[str],
        dnp_standards: list[str],
        alignment_params: dict[str, Any],
    ) -> None:
        """ASC-001: Fixed params produce identical plan digest."""
        assert AlignmentStabilityContract.verify_stability(
            policy_sections, dnp_standards, alignment_params
        )

    def test_asc_002_plan_digest_deterministic(
        self,
        policy_sections: list[str],
        dnp_standards: list[str],
        alignment_params: dict[str, Any],
    ) -> None:
        """ASC-002: Plan digest is deterministic."""
        result1 = AlignmentStabilityContract.compute_alignment(
            policy_sections, dnp_standards, alignment_params
        )
        result2 = AlignmentStabilityContract.compute_alignment(
            policy_sections, dnp_standards, alignment_params
        )
        assert result1["plan_digest"] == result2["plan_digest"]

    def test_asc_003_different_params_different_plan(
        self,
        policy_sections: list[str],
        dnp_standards: list[str],
    ) -> None:
        """ASC-003: Different params produce different plans."""
        params1 = {"lambda": 0.1, "epsilon": 0.01}
        params2 = {"lambda": 0.2, "epsilon": 0.02}
        result1 = AlignmentStabilityContract.compute_alignment(
            policy_sections, dnp_standards, params1
        )
        result2 = AlignmentStabilityContract.compute_alignment(
            policy_sections, dnp_standards, params2
        )
        assert result1["plan_digest"] != result2["plan_digest"]

    def test_asc_004_cost_and_unmatched_mass(
        self,
        policy_sections: list[str],
        dnp_standards: list[str],
        alignment_params: dict[str, Any],
    ) -> None:
        """ASC-004: Alignment returns cost and unmatched mass."""
        result = AlignmentStabilityContract.compute_alignment(
            policy_sections, dnp_standards, alignment_params
        )
        assert "cost" in result
        assert "unmatched_mass" in result
        assert isinstance(result["cost"], float)
        assert isinstance(result["unmatched_mass"], float)


class TestTotalOrderingContract:
    """TOC: Total ordering with deterministic tie-breaking."""

    @pytest.fixture
    def phase2_results(self) -> list[dict[str, Any]]:
        """Phase 2 question results with scores."""
        return [
            {"question_id": "Q001", "score": 0.75, "content_hash": "abc123"},
            {"question_id": "Q002", "score": 0.85, "content_hash": "def456"},
            {"question_id": "Q003", "score": 0.75, "content_hash": "xyz789"},  # tie
            {"question_id": "Q004", "score": 0.65, "content_hash": "ghi012"},
        ]

    def test_toc_001_stable_sort(
        self, phase2_results: list[dict[str, Any]]
    ) -> None:
        """TOC-001: Sort is stable and deterministic."""
        assert TotalOrderingContract.verify_order(
            phase2_results, key=lambda x: -x["score"]
        )

    def test_toc_002_tie_breaker_lexicographical(
        self, phase2_results: list[dict[str, Any]]
    ) -> None:
        """TOC-002: Ties are broken lexicographically by content_hash."""
        sorted_results = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: -x["score"]
        )
        # Q001 and Q003 have same score (0.75), should be ordered by content_hash
        q75_items = [r for r in sorted_results if r["score"] == 0.75]
        assert q75_items[0]["content_hash"] < q75_items[1]["content_hash"]

    def test_toc_003_repeated_sort_identical(
        self, phase2_results: list[dict[str, Any]]
    ) -> None:
        """TOC-003: Multiple sorts produce identical results."""
        sorted1 = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: -x["score"]
        )
        sorted2 = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: -x["score"]
        )
        sorted3 = TotalOrderingContract.stable_sort(
            phase2_results, key=lambda x: -x["score"]
        )
        assert sorted1 == sorted2 == sorted3

    def test_toc_004_empty_list(self) -> None:
        """TOC-004: Empty list sorts to empty list."""
        result = TotalOrderingContract.stable_sort([], key=lambda x: x)
        assert result == []

    def test_toc_005_single_item(self) -> None:
        """TOC-005: Single item list is stable."""
        single = [{"question_id": "Q001", "score": 0.5, "content_hash": "hash"}]
        result = TotalOrderingContract.stable_sort(single, key=lambda x: -x["score"])
        assert result == single


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
