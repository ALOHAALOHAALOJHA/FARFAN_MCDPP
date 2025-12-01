"""
Tests for Failure & Fallback Contract (FFC)
"""
import pytest
from farfan_core.contracts.failure_fallback import FailureFallbackContract

class TestFailureFallbackContract:
    
    def test_fault_injection(self):
        """Inyección de fallos por clase ⇒ mismo fallback."""
        def failing_func():
            raise ValueError("Simulated failure")
            
        fallback = "SAFE_MODE"
        
        res = FailureFallbackContract.execute_with_fallback(failing_func, fallback, (ValueError,))
        assert res == fallback
        
        # Verify determinism
        assert FailureFallbackContract.verify_fallback_determinism(failing_func, fallback, ValueError)

    def test_unexpected_exception(self):
        """No hay efectos secundarios (unexpected exceptions propagate)."""
        def crashing_func():
            raise RuntimeError("Unexpected")
            
        with pytest.raises(RuntimeError):
            FailureFallbackContract.execute_with_fallback(crashing_func, "fallback", (ValueError,))

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
