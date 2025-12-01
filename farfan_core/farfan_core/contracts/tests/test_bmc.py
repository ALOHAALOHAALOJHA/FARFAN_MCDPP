"""
Tests for Budget & Monotonicity Contract (BMC)
"""
import pytest
from farfan_core.contracts.budget_monotonicity import BudgetMonotonicityContract

class TestBudgetMonotonicityContract:
    
    def test_monotonicity_sweep(self):
        """Barrido de presupuestos B1<B2<B3 con Δf y costos fijos ⇒ S*(B1) ⊆ S*(B2) ⊆ S*(B3)."""
        items = {"a": 10, "b": 20, "c": 30, "d": 40}
        budgets = [15, 35, 65, 100]
        
        assert BudgetMonotonicityContract.verify_monotonicity(items, budgets)
        
        # Verify specific inclusions manually
        s1 = BudgetMonotonicityContract.solve_knapsack(items, 15) # {a}
        s2 = BudgetMonotonicityContract.solve_knapsack(items, 35) # {a, b}
        s3 = BudgetMonotonicityContract.solve_knapsack(items, 65) # {a, b, c}
        
        assert s1.issubset(s2)
        assert s2.issubset(s3)

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
