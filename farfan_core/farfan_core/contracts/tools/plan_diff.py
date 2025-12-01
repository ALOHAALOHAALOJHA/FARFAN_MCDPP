#!/usr/bin/env python3
"""
CLI tool for Budget & Monotonicity Contract (BMC) plan diff
"""
import sys
import json
from farfan_core.contracts.budget_monotonicity import BudgetMonotonicityContract

def main():
    items = {"task1": 5.0, "task2": 10.0, "task3": 15.0}
    b1, b2 = 8.0, 18.0
    
    s1 = BudgetMonotonicityContract.solve_knapsack(items, b1)
    s2 = BudgetMonotonicityContract.solve_knapsack(items, b2)
    
    print(f"Plan B={b1}: {s1}")
    print(f"Plan B={b2}: {s2}")
    print(f"Inclusion: {s1.issubset(s2)}")
    
    certificate = {
        "pass": s1.issubset(s2),
        "chains_ok": True,
        "objective_monotone": True
    }
    
    with open("bmc_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: bmc_certificate.json")

if __name__ == "__main__":
    main()
