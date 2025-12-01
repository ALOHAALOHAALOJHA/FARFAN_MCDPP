"""
Tests for Snapshot Contract (SC)
"""
import pytest
import json
from farfan_core.contracts.snapshot_contract import SnapshotContract

class TestSnapshotContract:
    
    def test_repeat_execution(self):
        """Repite ejecución con el mismo σ ⇒ digest de outputs idéntico."""
        sigma = {
            "standards_hash": "abc",
            "corpus_hash": "def",
            "index_hash": "ghi"
        }
        
        digest1 = SnapshotContract.verify_snapshot(sigma)
        digest2 = SnapshotContract.verify_snapshot(sigma)
        
        assert digest1 == digest2

    def test_missing_sigma(self):
        """σ ausente ⇒ fallo tipado (Refusal) y no hay efectos colaterales."""
        with pytest.raises(ValueError, match="Refusal"):
            SnapshotContract.verify_snapshot({})

    def test_missing_keys(self):
        sigma = {"standards_hash": "abc"}
        with pytest.raises(ValueError, match="Refusal"):
            SnapshotContract.verify_snapshot(sigma)

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
