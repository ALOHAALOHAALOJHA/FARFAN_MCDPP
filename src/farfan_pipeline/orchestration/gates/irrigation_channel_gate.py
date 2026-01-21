from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class IrrigationResult:
    is_valid: bool
    signal_id: str
    routed: bool
    consumer_count: int
    has_audit: bool
    message: str

class IrrigationChannelGate:
    """
    Gate 4: Post-dispatch validation.
    PATTERN: Post-Dispatch Validation
    """
    
    def validate_post_dispatch(self, signal_id: str, routed: bool, consumers: List[str], audit_entries: List) -> IrrigationResult:
        """
        Validates that if a signal was routed, it reached consumers and left an audit trail.
        """
        has_consumers = len(consumers) > 0
        has_audit = len(audit_entries) > 0
        
        is_valid = True
        msg = "Dispatch successful"

        if routed:
            if not has_consumers:
                is_valid = False
                msg = "Routed but no consumers found"
            elif not has_audit:
                is_valid = False 
                msg = "Routed but no audit trail"
        else:
             msg = "Not routed"
        
        return IrrigationResult(
            is_valid=is_valid,
            signal_id=signal_id,
            routed=routed,
            consumer_count=len(consumers),
            has_audit=has_audit,
            message=msg
        )
