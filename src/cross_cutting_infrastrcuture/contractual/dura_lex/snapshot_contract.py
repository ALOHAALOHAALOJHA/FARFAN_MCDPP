"""
Snapshot Contract (SC) - Implementation
"""
import hashlib
import json
from typing import Dict, Any

class SnapshotContract:
    @staticmethod
    def verify_snapshot(sigma: Dict[str, Any]) -> str:
        """
        Verifies that all external inputs are frozen by checksums.
        Returns the digest of the snapshot.
        Raises ValueError if sigma is missing or invalid.
        """
        if not sigma:
            raise ValueError("Refusal: Sigma (σ) is missing.")
            
        required_keys = ["standards_hash", "corpus_hash", "index_hash"]
        for key in required_keys:
            if key not in sigma:
                raise ValueError(f"Refusal: Missing required key {key} in sigma.")
                
        # Calculate digest
        return hashlib.blake2b(json.dumps(sigma, sort_keys=True).encode()).hexdigest()
