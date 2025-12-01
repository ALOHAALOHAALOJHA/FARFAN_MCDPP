"""
Tests for Concurrency Determinism Contract (CDC)
"""
import pytest
from farfan_core.contracts.concurrency_determinism import ConcurrencyDeterminismContract

class TestConcurrencyDeterminismContract:
    
    def test_concurrency_invariance(self):
        """Ejecutar con 1, N workers ⇒ outputs hash-iguales."""
        def task(x):
            return x * x
            
        inputs = list(range(100))
        
        assert ConcurrencyDeterminismContract.verify_determinism(task, inputs)

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
