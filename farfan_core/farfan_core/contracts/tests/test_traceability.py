"""
Tests for Traceability Contract (TC)
"""
import pytest
from farfan_core.contracts.traceability import TraceabilityContract, MerkleTree

class TestTraceabilityContract:
    
    def test_tamper_detection(self):
        """Intento de mutación ⇒ cambia Merkle root y falla verificación."""
        items = ["step1", "step2", "step3"]
        tree = MerkleTree(items)
        root = tree.root
        
        assert TraceabilityContract.verify_trace(items, root)
        
        # Tamper
        tampered_items = ["step1", "step2", "step3_hacked"]
        assert not TraceabilityContract.verify_trace(tampered_items, root)

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
