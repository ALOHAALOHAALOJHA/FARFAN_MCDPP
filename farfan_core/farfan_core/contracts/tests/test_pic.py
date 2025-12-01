"""
Tests for Permutation-Invariance Contract (PIC)
"""
import pytest
from hypothesis import given, strategies as st
import random
from farfan_core.contracts.permutation_invariance import PermutationInvarianceContract

class TestPermutationInvarianceContract:
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6)))
    def test_shuffling_invariance(self, items):
        """Baraja entradas aleatoriamente y comprueba igualdad."""
        transform = lambda x: x * 2.0
        
        digest1 = PermutationInvarianceContract.verify_invariance(items, transform)
        
        shuffled_items = list(items)
        random.shuffle(shuffled_items)
        
        digest2 = PermutationInvarianceContract.verify_invariance(shuffled_items, transform)
        
        # Floating point addition is not associative, so exact equality might fail for large lists/values.
        # However, for the contract "verify_invariance" which returns a hash of the string representation,
        # we expect it to be stable if we sort or use a stable accumulation.
        # The current implementation uses simple sum(), which might vary slightly.
        # Let's adjust the implementation to be robust or the test to accept tolerance.
        
        # Re-implementing aggregate in test to check numerical closeness if hash fails?
        # The prompt asks for "compara con tolerancia numérica fija".
        
        val1 = PermutationInvarianceContract.aggregate(items, transform)
        val2 = PermutationInvarianceContract.aggregate(shuffled_items, transform)
        
        assert val1 == pytest.approx(val2, rel=1e-9)

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
