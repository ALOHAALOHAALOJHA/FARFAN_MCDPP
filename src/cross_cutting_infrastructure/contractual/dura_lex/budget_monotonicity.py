"""
Budget & Monotonicity Contract (BMC) - Implementation
"""
from typing import List, Dict, Set

class BudgetMonotonicityContract:
    @staticmethod
    def solve_knapsack(items: Dict[str, float], budget: float) -> Set[str]:
        """
        Solves a knapsack-like problem (selecting items within budget).
        To ensure monotonicity (S*(B1) ⊆ S*(B2)), we use a greedy approach based on cost/benefit
        or simply cost if benefit is uniform.
        Here we assume we want to maximize count of items, so we pick cheapest first.
        """
        sorted_items = sorted(items.items(), key=lambda x: x[1]) # Sort by cost ascending
        
        selected = set()
        current_cost = 0.0
        
        for item_id, cost in sorted_items:
            if current_cost + cost <= budget:
                selected.add(item_id)
                current_cost += cost
            else:
                break
                
        return selected

    @staticmethod
    def verify_monotonicity(items: Dict[str, float], budgets: List[float]) -> bool:
        """
        Verifies S*(B1) ⊆ S*(B2) for B1 < B2.
        """
        sorted_budgets = sorted(budgets)
        prev_solution = None
        
        for b in sorted_budgets:
            solution = BudgetMonotonicityContract.solve_knapsack(items, b)
            if prev_solution is not None:
                if not prev_solution.issubset(solution):
                    return False
            prev_solution = solution
            
        return True
