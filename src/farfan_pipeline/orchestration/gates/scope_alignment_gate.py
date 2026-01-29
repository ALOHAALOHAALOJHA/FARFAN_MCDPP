from dataclasses import dataclass
from typing import Dict, Tuple
from enum import Enum

class ScopeValidationError(str, Enum):
    INVALID_PHASE = "INVALID_PHASE"
    INVALID_POLICY_AREA = "INVALID_POLICY_AREA"
    SIGNAL_TYPE_PHASE_MISMATCH = "SIGNAL_TYPE_PHASE_MISMATCH"

@dataclass(frozen=True)
class ScopeAlignmentResult:
    is_valid: bool
    errors: Tuple[ScopeValidationError, ...]
    phase: str
    policy_area: str
    signal_type: str

class ScopeAlignmentGate: 
    """
    Gate 1: Validates signal scope alignment. 
    
    Rules:
    1. phase must be in {phase_0, phase_1, .. ., phase_9}
    2. policy_area must be in {PA01-PA10, ALL, CROSS_CUTTING}
    3. signal_type must be valid for declared phase
    """
    
    VALID_PHASES: frozenset = frozenset(f"phase_{i}" for i in range(10))
    
    VALID_POLICY_AREAS: frozenset = frozenset(
        [f"PA{i:02d}" for i in range(1, 11)] + ["ALL", "CROSS_CUTTING"]
    )
    
    PHASE_SIGNAL_ALIGNMENT: Dict[str, frozenset] = {
        "phase_0": frozenset(["SIGNAL_PACK", "STATIC_LOAD"]),
        "phase_1": frozenset(["MC01", "MC02", "MC03", "MC04", "MC05", 
                             "MC06", "MC07", "MC08", "MC09", "MC10"]),
        "phase_2": frozenset(["PATTERN_ENRICHMENT", "KEYWORD_ENRICHMENT", 
                             "ENTITY_ENRICHMENT"]),
        "phase_3": frozenset(["NORMATIVE_VALIDATION", "ENTITY_VALIDATION", 
                             "COHERENCE_VALIDATION"]),
        "phase_4": frozenset(["MICRO_SCORE"]),
        "phase_5": frozenset(["MESO_SCORE"]),
        "phase_6": frozenset(["MACRO_SCORE"]),
        "phase_7": frozenset(["MESO_AGGREGATION"]),
        "phase_8": frozenset(["MACRO_AGGREGATION"]),
        "phase_9": frozenset(["REPORT_ASSEMBLY"]),
    }
    
    def validate(self, phase: str, policy_area: str, signal_type: str) -> ScopeAlignmentResult: 
        """Validate scope alignment. Returns immutable result."""
        errors = []
        
        if phase not in self.VALID_PHASES:
            errors.append(ScopeValidationError.INVALID_PHASE)
        
        if policy_area not in self.VALID_POLICY_AREAS:
            errors.append(ScopeValidationError.INVALID_POLICY_AREA)
        
        if phase in self.VALID_PHASES: 
            allowed = self.PHASE_SIGNAL_ALIGNMENT.get(phase, frozenset())
            if signal_type not in allowed:
                errors.append(ScopeValidationError.SIGNAL_TYPE_PHASE_MISMATCH)
        
        return ScopeAlignmentResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            phase=phase,
            policy_area=policy_area,
            signal_type=signal_type
        )
