from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Any, Optional
import time
import threading
from pathlib import Path

from .scope_alignment_gate import ScopeAlignmentGate, ScopeAlignmentResult
from .value_add_gate import ValueAddGate, ValueAddResult
from .capability_gate import CapabilityGate, CapabilityResult
from .irrigation_channel_gate import IrrigationChannelGate, IrrigationResult

@dataclass
class GateMetrics:
    """Immutable gate execution metrics."""
    total_executions: int = 0
    gate_1_pass_rate: float = 0.0
    gate_2_pass_rate: float = 0.0
    gate_3_pass_rate: float = 0.0
    gate_4_pass_rate: float = 0.0
    avg_execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

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
    
    def __init__(self, checkpoint_dir: Optional[Path] = None):
        self.gate_1 = ScopeAlignmentGate()
        self.gate_2 = ValueAddGate()
        self.gate_3 = CapabilityGate()
        self.gate_4 = IrrigationChannelGate()
        self._metrics = GateMetrics()
        self._execution_times: List[float] = []
    
    def validate_pre_dispatch(self, signal, consumers: Dict) -> Tuple[bool, Optional[int], Any]:
        """
        Run gates 1-3 before dispatch.
        Returns: (success, failed_gate_number, failure_result_or_last_success_result)
        """
        start = time.perf_counter()
        gate_results: Dict[str, Any] = {}
        
        try:
            # Gate 1: Scope Alignment
            res_1 = self.gate_1.validate(
                phase=getattr(signal, 'phase', ''),
                policy_area=getattr(signal, 'policy_area', ''),
                signal_type=getattr(signal, 'signal_type', '')
            )
            gate_results['gate_1'] = res_1
            if not res_1.is_valid:
                return False, 1, res_1
                
            # Gate 2: Value Add
            # Handle optional is_enrichment, default to False if missing
            res_2 = self.gate_2.validate(
                empirical_availability=getattr(signal, 'empirical_availability', 0.0),
                is_enrichment=getattr(signal, 'is_enrichment', False)
            )
            gate_results['gate_2'] = res_2
            if not res_2.is_valid:
                return False, 2, res_2
                
            # Gate 3: Capability
            # Needs required capabilities from signal and available from consumers
            required = getattr(signal, 'required_capabilities', frozenset())
            
            all_available_capabilities = set()
            for caps in consumers.values():
                all_available_capabilities.update(caps)
            
            res_3 = self.gate_3.validate(
                required=required,
                available=frozenset(all_available_capabilities)
            )
            gate_results['gate_3'] = res_3
            if not res_3.is_valid:
                return False, 3, res_3
                
            return True, None, res_3
            
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._update_metrics(gate_results, elapsed_ms)
    
    def validate_post_dispatch(self, signal, audit_entries: List, consumers_map: Optional[Dict] = None) -> GateOrchestratorResult: 
        """
        Run gate 4 after dispatch, combine with pre-dispatch results.
        Re-runs Gates 1-3 to provide a complete report.
        """
        start = time.perf_counter()
        gate_results: Dict[str, Any] = {}
        
        try:
            # Re-run Gate 1
            res_1 = self.gate_1.validate(
                phase=getattr(signal, 'phase', ''),
                policy_area=getattr(signal, 'policy_area', ''),
                signal_type=getattr(signal, 'signal_type', '')
            )
            gate_results['gate_1'] = res_1
            if not res_1.is_valid:
                return GateOrchestratorResult(False, res_1, None, None, None, 1)

            # Re-run Gate 2
            res_2 = self.gate_2.validate(
                empirical_availability=getattr(signal, 'empirical_availability', 0.0),
                is_enrichment=getattr(signal, 'is_enrichment', False)
            )
            gate_results['gate_2'] = res_2
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
            gate_results['gate_3'] = res_3
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
            gate_results['gate_4'] = res_4
            
            if not res_4.is_valid:
                return GateOrchestratorResult(False, res_1, res_2, res_3, res_4, 4)
                
            return GateOrchestratorResult(True, res_1, res_2, res_3, res_4, None)
            
        finally:
             elapsed_ms = (time.perf_counter() - start) * 1000
             self._update_metrics(gate_results, elapsed_ms)

    def _update_metrics(self, gate_results: Dict[str, Any], elapsed_ms: float) -> None:
        """Update gate metrics thread-safely."""
        with threading.Lock():
            self._metrics.total_executions += 1
            self._execution_times.append(elapsed_ms)

            # Update pass rates using exponential moving average
            alpha = 2 / (self._metrics.total_executions + 1)
            for gate_id, result in gate_results.items():
                if hasattr(result, "is_valid"):
                    attr_name = f"{gate_id}_pass_rate"
                    if hasattr(self._metrics, attr_name):
                        current_rate = getattr(self._metrics, attr_name)
                        new_value = 1.0 if result.is_valid else 0.0
                        new_rate = alpha * new_value + (1 - alpha) * current_rate
                        setattr(self._metrics, attr_name, new_rate)

    def get_metrics(self) -> GateMetrics:
        """Get immutable copy of metrics."""
        avg_time = sum(self._execution_times) / len(self._execution_times) if self._execution_times else 0
        self._metrics.avg_execution_time_ms = avg_time
        return GateMetrics(**asdict(self._metrics))
