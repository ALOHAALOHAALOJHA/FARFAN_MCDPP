"""
Tests for Retriever Contract (ReC)
"""
import pytest
from farfan_core.contracts.retriever_contract import RetrieverContract

class TestRetrieverContract:
    
    def test_determinism(self):
        """Mismos insumos ⇒ mismo top-K."""
        query = "policy impact"
        filters = {"year": 2024}
        index_hash = "idx_123"
        
        digest1 = RetrieverContract.verify_determinism(query, filters, index_hash)
        digest2 = RetrieverContract.verify_determinism(query, filters, index_hash)
        
        assert digest1 == digest2

    def test_sigma_change_diff(self):
        """Cambiado σ (index_hash) ⇒ diff documentado."""
        query = "policy impact"
        filters = {"year": 2024}
        
        digest1 = RetrieverContract.verify_determinism(query, filters, "idx_123")
        digest2 = RetrieverContract.verify_determinism(query, filters, "idx_456")
        
        assert digest1 != digest2

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
