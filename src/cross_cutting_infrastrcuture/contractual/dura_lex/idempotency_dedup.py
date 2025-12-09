"""
Idempotency & De-dup Contract (IDC) - Implementation
"""
import hashlib
import json
from typing import List, Dict, Any, Set

class EvidenceStore:
    def __init__(self):
        self.evidence: Dict[str, Any] = {} # content_hash -> evidence
        self.duplicates_blocked = 0

    def add(self, item: Dict[str, Any]):
        # Calculate content hash
        content_hash = hashlib.blake2b(json.dumps(item, sort_keys=True).encode()).hexdigest()
        
        if content_hash in self.evidence:
            self.duplicates_blocked += 1
        else:
            self.evidence[content_hash] = item

    def state_hash(self) -> str:
        # Hash of sorted keys to ensure order independence
        sorted_keys = sorted(self.evidence.keys())
        return hashlib.blake2b(json.dumps(sorted_keys).encode()).hexdigest()

class IdempotencyContract:
    @staticmethod
    def verify_idempotency(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        store = EvidenceStore()
        for item in items:
            store.add(item)
            
        return {
            "state_hash": store.state_hash(),
            "duplicates_blocked": store.duplicates_blocked,
            "count": len(store.evidence)
        }
