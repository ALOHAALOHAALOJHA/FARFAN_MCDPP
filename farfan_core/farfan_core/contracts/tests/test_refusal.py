"""
Tests for Refusal Contract (RefC)
"""
import pytest
from farfan_core.contracts.refusal import RefusalContract, RefusalError

class TestRefusalContract:
    
    def test_refusal_triggers(self):
        """Dispara cada cláusula ⇒ Refusal estable y explicativo."""
        
        # Missing mandatory
        with pytest.raises(RefusalError, match="Missing mandatory"):
            RefusalContract.check_prerequisites({})
            
        # Alpha violation
        with pytest.raises(RefusalError, match="Alpha violation"):
            RefusalContract.check_prerequisites({"mandatory": True, "alpha": 0.8})
            
        # Sigma absent
        with pytest.raises(RefusalError, match="Sigma absent"):
            RefusalContract.check_prerequisites({"mandatory": True, "alpha": 0.1})

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
