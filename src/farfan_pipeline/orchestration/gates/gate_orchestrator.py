from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional

from .scope_alignment_gate import ScopeAlignmentGate, ScopeAlignmentResult
from .value_add_gate import ValueAddGate, ValueAddResult
from .capability_gate import CapabilityGate, CapabilityResult
from .irrigation_channel_gate import IrrigationChannelGate, IrrigationResult

@dataclass(frozen=True)
class GateOrchestratorResult:
    all_passed: bool
    gate_1_scope: Optional[ScopeAlignmentResult]
    gate_2_value: Optional[ValueAddResult]
    gate_3_capability: Optional[CapabilityResult]
    gate_4_irrigation: Optional[IrrigationResult]
    failed_at_gate: Optional[int]

class GateOrchestrator: 
    """
    Orchestrates all 4 validation gates in sequence. 
    
    Execution order:
    1. Scope Alignment (pre-dispatch)
    2. Value Add (pre-dispatch)
    3. Capability (pre-dispatch)
    4. Irrigation Channel (post-dispatch)
    
    Fails fast: stops at first failed gate.
    """
    
    def __init__(self):
        self.gate_1 = ScopeAlignmentGate()
        self.gate_2 = ValueAddGate()
        self.gate_3 = CapabilityGate()
        self.gate_4 = IrrigationChannelGate()
    
    def validate_pre_dispatch(self, signal, consumers: Dict) -> Tuple[bool, Optional[int], Any]:
        """
        Run gates 1-3 before dispatch.
        Returns: (success, failed_gate_number, failure_result_or_last_success_result)
        """
        # Gate 1: Scope Alignment
        res_1 = self.gate_1.validate(
            phase=getattr(signal, 'phase', ''),
            policy_area=getattr(signal, 'policy_area', ''),
            signal_type=getattr(signal, 'signal_type', '')
        )
        if not res_1.is_valid:
            return False, 1, res_1
            
        # Gate 2: Value Add
        # Handle optional is_enrichment, default to False if missing
        res_2 = self.gate_2.validate(
            empirical_availability=getattr(signal, 'empirical_availability', 0.0),
            is_enrichment=getattr(signal, 'is_enrichment', False)
        )
        if not res_2.is_valid:
            return False, 2, res_2
            
        # Gate 3: Capability
        # Needs required capabilities from signal and available from consumers
        required = getattr(signal, 'required_capabilities', frozenset())
        
        # Calculate available capabilities from the provided consumers dict
        # Assuming consumers is Dict[str, FrozenSet[str]] or similar where values are capabilities
        # Wait, Gate 3 validate takes (required, available). 
        # 'available' usually means the set of capabilities available in the SYSTEM or target?
        # If consumers is Dict[ConsumerID, Capabilities], 'available' is the union of all?
        # Or does validate check if *a* consumer exists?
        # Gate 3 logic: "validate(required, available)".
        # And "find_eligible_consumers(required, consumers)".
        # Usually we want to ensure *at least one* consumer can handle it.
        # But validate(req, avail) implies checking against a set.
        # I'll assume 'available' is the union of all capabilities of provided consumers.
        
        all_available_capabilities = set()
        for caps in consumers.values():
            all_available_capabilities.update(caps)
        
        res_3 = self.gate_3.validate(
            required=required,
            available=frozenset(all_available_capabilities)
        )
        if not res_3.is_valid:
            return False, 3, res_3
            
        return True, None, res_3
    
    def validate_post_dispatch(self, signal, audit_entries: List, consumers_map: Optional[Dict] = None) -> GateOrchestratorResult: 
        """
        Run gate 4 after dispatch, combine with pre-dispatch results.
        Re-runs Gates 1-3 to provide a complete report.
        """
        # Re-run Gate 1
        res_1 = self.gate_1.validate(
            phase=getattr(signal, 'phase', ''),
            policy_area=getattr(signal, 'policy_area', ''),
            signal_type=getattr(signal, 'signal_type', '')
        )
        if not res_1.is_valid:
            return GateOrchestratorResult(False, res_1, None, None, None, 1)

        # Re-run Gate 2
        res_2 = self.gate_2.validate(
            empirical_availability=getattr(signal, 'empirical_availability', 0.0),
            is_enrichment=getattr(signal, 'is_enrichment', False)
        )
        if not res_2.is_valid:
            return GateOrchestratorResult(False, res_1, res_2, None, None, 2)
            
        # Re-run Gate 3
        if consumers_map:
            all_available_capabilities = set()
            for caps in consumers_map.values():
                all_available_capabilities.update(caps)
            available_caps = frozenset(all_available_capabilities)
        else:
            # Fallback if map not provided: assume validated if we got here?
            # Or try to construct from signal?
            available_caps = getattr(signal, 'required_capabilities', frozenset()) # Hack to pass if map missing

        res_3 = self.gate_3.validate(
            required=getattr(signal, 'required_capabilities', frozenset()),
            available=available_caps
        )
        if not res_3.is_valid:
             return GateOrchestratorResult(False, res_1, res_2, res_3, None, 3)

        # Run Gate 4
        # Assuming signal has 'routed' status and 'consumers' list of IDs
        res_4 = self.gate_4.validate_post_dispatch(
            signal_id=getattr(signal, 'id', 'unknown'),
            routed=getattr(signal, 'routed', False),
            consumers=getattr(signal, 'consumers', []),
            audit_entries=audit_entries
        )
        
        if not res_4.is_valid:
            return GateOrchestratorResult(False, res_1, res_2, res_3, res_4, 4)
            
        return GateOrchestratorResult(True, res_1, res_2, res_3, res_4, None)
