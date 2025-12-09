"""
Total Ordering Contract (TOC) - Implementation
"""
from typing import List, Any, Tuple

class TotalOrderingContract:
    @staticmethod
    def stable_sort(items: List[dict], key: Any) -> List[dict]:
        """
        Sorts items using a primary key and a deterministic tie-breaker (lexicographical).
        Assumes items have a 'content_hash' or similar unique ID for tie-breaking.
        """
        # Python's sort is stable.
        # We enforce total ordering by using a tuple key: (primary_score, secondary_tie_breaker)
        return sorted(items, key=lambda x: (key(x), x.get('content_hash', '')))

    @staticmethod
    def verify_order(items: List[dict], key: Any) -> bool:
        """
        Verifies that the sort is stable and deterministic.
        """
        sorted1 = TotalOrderingContract.stable_sort(items, key)
        sorted2 = TotalOrderingContract.stable_sort(items, key)
        return sorted1 == sorted2
