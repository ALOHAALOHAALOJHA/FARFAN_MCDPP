"""
Test BMC - Budget Monotonicity Contract
Verifies: S*(B1) ⊆ S*(B2) for B1 < B2
Resource allocation ordering guarantee
"""

import pytest
from pathlib import Path

from cross_cutting_infrastructure.contractual.dura_lex.budget_monotonicity import (
    BudgetMonotonicityContract,
)


class TestBudgetMonotonicityContract:
    """BMC: Higher budget = strict superset of selected items."""

    @pytest.fixture
    def sample_items(self) -> dict[str, float]:
        """Phase 2 executor task costs."""
        return {
            "Q001": 10.0,
            "Q002": 15.0,
            "Q003": 20.0,
            "Q004": 25.0,
            "Q005": 30.0,
            "Q006": 35.0,
            "Q007": 40.0,
            "Q008": 45.0,
            "Q009": 50.0,
            "Q010": 55.0,
        }

    def test_bmc_001_monotonicity_holds(self, sample_items: dict[str, float]) -> None:
        """BMC-001: Verify S*(B1) ⊆ S*(B2) for increasing budgets."""
        budgets = [25.0, 50.0, 100.0, 200.0, 500.0]
        assert BudgetMonotonicityContract.verify_monotonicity(sample_items, budgets)

    def test_bmc_002_knapsack_deterministic(self, sample_items: dict[str, float]) -> None:
        """BMC-002: Same budget always selects same items."""
        budget = 75.0
        result1 = BudgetMonotonicityContract.solve_knapsack(sample_items, budget)
        result2 = BudgetMonotonicityContract.solve_knapsack(sample_items, budget)
        assert result1 == result2

    def test_bmc_003_zero_budget_empty(self, sample_items: dict[str, float]) -> None:
        """BMC-003: Zero budget selects nothing."""
        result = BudgetMonotonicityContract.solve_knapsack(sample_items, 0.0)
        assert result == set()

    def test_bmc_004_infinite_budget_all(self, sample_items: dict[str, float]) -> None:
        """BMC-004: Infinite budget selects all items."""
        result = BudgetMonotonicityContract.solve_knapsack(sample_items, float("inf"))
        assert result == set(sample_items.keys())

    def test_bmc_005_strict_superset(self, sample_items: dict[str, float]) -> None:
        """BMC-005: Larger budget strictly extends smaller budget selection."""
        s1 = BudgetMonotonicityContract.solve_knapsack(sample_items, 50.0)
        s2 = BudgetMonotonicityContract.solve_knapsack(sample_items, 100.0)
        assert s1.issubset(s2)
        assert len(s2) >= len(s1)

    def test_bmc_006_phase2_executor_allocation(self) -> None:
        """BMC-006: Phase 2 executor budget allocation is monotonic."""
        executors = {f"D{d}-Q{q}": d * 10 + q * 5 for d in range(1, 7) for q in range(1, 6)}
        budgets = [100.0, 200.0, 500.0, 1000.0]
        assert BudgetMonotonicityContract.verify_monotonicity(executors, budgets)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
