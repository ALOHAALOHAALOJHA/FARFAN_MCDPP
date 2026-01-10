"""
Hash utilities for deterministic content hashing.

This module provides cryptographic hashing functions used across the pipeline
for content integrity verification and change detection.

Author: Integration Team
Version: 1.0.0
Python: 3.10+
"""

import hashlib
import json
from typing import Any


def compute_hash(data: dict[str, Any]) -> str:
    """
    Compute deterministic SHA-256 hash of dictionary data.

    This function creates a canonical JSON representation with sorted keys
    and stable separators to ensure identical dictionaries always produce
    the same hash, regardless of key insertion order.

    Args:
        data: Dictionary to hash

    Returns:
        Hexadecimal SHA-256 digest (64 characters)

    Example:
        >>> data = {"b": 2, "a": 1}
        >>> hash1 = compute_hash(data)
        >>> hash2 = compute_hash({"a": 1, "b": 2})
        >>> hash1 == hash2
        True
    """
    canonical_json = json.dumps(
        data, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
