"""
Permutation-Invariance Contract (PIC) - Implementation
"""
import hashlib
from typing import List, Any, Callable

class PermutationInvarianceContract:
    @staticmethod
    def aggregate(items: List[Any], transform: Callable[[Any], float]) -> float:
        """
        Implements f(S) = ϕ(Σ ψ(x)) pattern for permutation invariance.
        Here, sum is the aggregation function (symmetric).
        """
        # ψ(x) = transform(x)
        transformed = [transform(x) for x in items]
        
        # Σ ψ(x) - Sum is order-independent (within floating point limits, usually)
        # For strict bitwise invariance with floats, we might need to sort or use exact arithmetic.
        # But the requirement asks for "numerical tolerance".
        total = sum(transformed)
        
        # ϕ(x) = identity (for this example)
        return total

    @staticmethod
    def verify_invariance(items: List[Any], transform: Callable[[Any], float]) -> str:
        """
        Calculates digest of the aggregation.
        """
        result = PermutationInvarianceContract.aggregate(items, transform)
        return hashlib.blake2b(str(result).encode()).hexdigest()
