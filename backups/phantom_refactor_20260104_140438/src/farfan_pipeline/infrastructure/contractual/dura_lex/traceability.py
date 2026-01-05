"""
Traceability Contract (TC) - Implementation
"""
import hashlib
import json
from typing import List, Any

class MerkleTree:
    def __init__(self, items: List[str]):
        self.leaves = [self._hash(item) for item in items]
        self.root = self._build_tree(self.leaves)

    def _hash(self, data: str) -> str:
        return hashlib.blake2b(data.encode()).hexdigest()

    def _build_tree(self, nodes: List[str]) -> str:
        if not nodes:
            return ""
        if len(nodes) == 1:
            return nodes[0]
            
        new_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i+1] if i+1 < len(nodes) else left
            combined = self._hash(left + right)
            new_level.append(combined)
            
        return self._build_tree(new_level)

class TraceabilityContract:
    @staticmethod
    def verify_trace(items: List[str], expected_root: str) -> bool:
        """
        Verifies that the items reconstruct the exact Merkle root.
        """
        tree = MerkleTree(items)
        return tree.root == expected_root
