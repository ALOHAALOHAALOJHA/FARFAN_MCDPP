"""
Tests for Idempotency & De-dup Contract (IDC)
"""
import pytest
import random
from farfan_core.contracts.idempotency_dedup import IdempotencyContract, EvidenceStore

class TestIdempotencyContract:
    
    def test_re_adds(self):
        """N re-adds del mismo content_hash ⇒ estado idéntico."""
        item = {"data": "value"}
        store = EvidenceStore()
        
        store.add(item)
        hash1 = store.state_hash()
        
        for _ in range(10):
            store.add(item)
            
        hash2 = store.state_hash()
        
        assert hash1 == hash2
        assert store.duplicates_blocked == 10

    def test_insertion_order(self):
        """Orden de inserción aleatorio ⇒ mismo agregado."""
        items = [{"id": i} for i in range(10)]
        
        res1 = IdempotencyContract.verify_idempotency(items)
        
        random.shuffle(items)
        res2 = IdempotencyContract.verify_idempotency(items)
        
        assert res1["state_hash"] == res2["state_hash"]

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
