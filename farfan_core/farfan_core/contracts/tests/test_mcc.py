"""
Tests for Monotone Compliance Contract (MCC)
"""
import pytest
from farfan_core.contracts.monotone_compliance import MonotoneComplianceContract, Label

class TestMonotoneComplianceContract:
    
    def test_monotonicity(self):
        """Conjuntos E ⊆ E' ⇒ label(E') ≥ label(E)."""
        rules = {
            "sat_reqs": ["a", "b"],
            "partial_reqs": ["a"]
        }
        
        e1 = {"a"} # PARTIAL
        e2 = {"a", "b"} # SAT
        e3 = {"a", "c"} # PARTIAL
        
        assert MonotoneComplianceContract.verify_monotonicity(e1, e2, rules) # PARTIAL -> SAT (OK)
        assert MonotoneComplianceContract.verify_monotonicity(e1, e3, rules) # PARTIAL -> PARTIAL (OK)
        
        e_empty = set() # UNSAT
        assert MonotoneComplianceContract.verify_monotonicity(e_empty, e1, rules) # UNSAT -> PARTIAL (OK)

    def test_downgrade_check(self):
        """Obligatorio fallido ⇒ downgrade determinista (implicit in logic)."""
        # If we remove evidence, label should drop or stay same.
        rules = {"sat_reqs": ["a"]}
        l_high = MonotoneComplianceContract.evaluate({"a"}, rules)
        l_low = MonotoneComplianceContract.evaluate(set(), rules)
        assert l_low < l_high

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
