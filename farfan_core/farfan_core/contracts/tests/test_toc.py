"""
Tests for Total Ordering Contract (TOC)
"""
import pytest
from farfan_core.contracts.total_ordering import TotalOrderingContract

class TestTotalOrderingContract:
    
    def test_tie_breaking(self):
        """Casos de empate sintéticos: mismo score_vector ⇒ desempate por κ.lexicográfico."""
        items = [
            {"score": 10, "content_hash": "b"},
            {"score": 10, "content_hash": "a"},
            {"score": 5, "content_hash": "c"}
        ]
        
        # Sort by score ascending
        sorted_items = TotalOrderingContract.stable_sort(items, key=lambda x: x["score"])
        
        # Expected: score 5 first, then score 10 'a', then score 10 'b'
        assert sorted_items[0]["content_hash"] == "c"
        assert sorted_items[1]["content_hash"] == "a"
        assert sorted_items[2]["content_hash"] == "b"

    def test_stability(self):
        items = [
            {"score": 10, "content_hash": "b"},
            {"score": 10, "content_hash": "a"}
        ]
        assert TotalOrderingContract.verify_order(items, lambda x: x["score"])

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
