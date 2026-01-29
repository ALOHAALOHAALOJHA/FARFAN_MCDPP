from dataclasses import dataclass
from typing import Dict, List, FrozenSet

@dataclass(frozen=True)
class CapabilityResult:
    is_valid: bool
    missing_capabilities: FrozenSet[str]
    matched_consumers: List[str]

class CapabilityGate:
    """
    Gate 3: Validates capability matching.
    PATTERN: Set-Based Matching
    """
    
    def validate(self, required: FrozenSet[str], available: FrozenSet[str]) -> CapabilityResult:
        """Validates that required capabilities are present in available set."""
        missing = required - available
        is_valid = len(missing) == 0
        return CapabilityResult(
            is_valid=is_valid,
            missing_capabilities=missing,
            matched_consumers=[]
        )

    def find_eligible_consumers(self, required: FrozenSet[str], consumers: Dict[str, FrozenSet[str]]) -> List[str]:
        """Finds consumers that have all required capabilities."""
        eligible = []
        for consumer_id, capabilities in consumers.items():
            if required.issubset(capabilities):
                eligible.append(consumer_id)
        return eligible
