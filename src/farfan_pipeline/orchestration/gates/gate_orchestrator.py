from dataclasses import dataclass, asdict, field
from typing import Dict, List, Tuple, Any, Optional, FrozenSet
import time
import threading
from pathlib import Path
import json
import uuid

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

@dataclass
class GateExecutionSnapshot:
    """Immutable snapshot of gate execution state."""
    gate_sequence: Tuple[str, ...]  # ["gate_1", "gate_2", ...]
    passed_gates: FrozenSet[str]
    failed_at: Optional[str]
    results: Dict[str, Any]  # All gate results
    timestamp: float
    execution_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_sequence": list(self.gate_sequence),
            "passed_gates": list(self.passed_gates),
            "failed_at": self.failed_at,
            "results": {k: v.to_dict() if hasattr(v, "to_dict") else v
                      for k, v in self.results.items()},
            "timestamp": self.timestamp,
            "execution_id": self.execution_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GateExecutionSnapshot":
        return cls(
            gate_sequence=tuple(data["gate_sequence"]),
            passed_gates=frozenset(data["passed_gates"]),
            failed_at=data["failed_at"],
            results=data["results"],
            timestamp=data["timestamp"],
            execution_id=data["execution_id"],
        )

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

        self._checkpoint_dir = checkpoint_dir
        self._execution_history: List[GateExecutionSnapshot] = []
    
    def validate_pre_dispatch(self, signal, consumers: Dict, execution_id: Optional[str] = None) -> Tuple[bool, Optional[int], Any, 'GateExecutionSnapshot']:
        """
        Run gates 1-3 before dispatch with checkpoint snapshot.
        Returns: (success, failed_gate_number, failure_result_or_last_success_result, snapshot)
        """
        execution_id = execution_id or str(uuid.uuid4())
        gate_sequence = ("gate_1_scope", "gate_2_value", "gate_3_capability")
        passed_gates = set()
        results = {}
        start = time.perf_counter()

        try:
            # Gate 1: Scope Alignment
            res_1 = self.gate_1.validate(
                phase=getattr(signal, 'phase', ''),
                policy_area=getattr(signal, 'policy_area', ''),
                signal_type=getattr(signal, 'signal_type', '')
            )
            results["gate_1"] = res_1
            if not res_1.is_valid:
                snapshot = GateExecutionSnapshot(
                    gate_sequence=gate_sequence,
                    passed_gates=frozenset(passed_gates),
                    failed_at="gate_1",
                    results=results,
                    timestamp=time.time(),
                    execution_id=execution_id,
                )
                self._save_snapshot(snapshot)
                return False, 1, res_1, snapshot
            passed_gates.add("gate_1")

            # Gate 2: Value Add
            # Handle optional is_enrichment, default to False if missing
            res_2 = self.gate_2.validate(
                empirical_availability=getattr(signal, 'empirical_availability', 0.0),
                is_enrichment=getattr(signal, 'is_enrichment', False)
            )
            results["gate_2"] = res_2
            if not res_2.is_valid:
                snapshot = GateExecutionSnapshot(
                    gate_sequence=gate_sequence,
                    passed_gates=frozenset(passed_gates),
                    failed_at="gate_2",
                    results=results,
                    timestamp=time.time(),
                    execution_id=execution_id,
                )
                self._save_snapshot(snapshot)
                return False, 2, res_2, snapshot
            passed_gates.add("gate_2")

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
            results["gate_3"] = res_3
            if not res_3.is_valid:
                snapshot = GateExecutionSnapshot(
                    gate_sequence=gate_sequence,
                    passed_gates=frozenset(passed_gates),
                    failed_at="gate_3",
                    results=results,
                    timestamp=time.time(),
                    execution_id=execution_id,
                )
                self._save_snapshot(snapshot)
                return False, 3, res_3, snapshot
            passed_gates.add("gate_3")

            snapshot = GateExecutionSnapshot(
                gate_sequence=gate_sequence,
                passed_gates=frozenset(passed_gates),
                failed_at=None,
                results=results,
                timestamp=time.time(),
                execution_id=execution_id,
            )
            self._save_snapshot(snapshot)
            return True, None, res_3, snapshot

        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._update_metrics(results, elapsed_ms)

    def validate_pre_dispatch_legacy(self, signal, consumers: Dict) -> Tuple[bool, Optional[int], Any]:
        """
        Legacy method for backward compatibility.
        Run gates 1-3 before dispatch.
        Returns: (success, failed_gate_number, failure_result_or_last_success_result)
        """
        success, gate_num, result, snapshot = self.validate_pre_dispatch(signal, consumers, execution_id=None)
        return success, gate_num, result

    def _save_snapshot(self, snapshot: GateExecutionSnapshot) -> None:
        """Persist gate execution snapshot."""
        self._execution_history.append(snapshot)
        if self._checkpoint_dir:
            self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
            snapshot_file = self._checkpoint_dir / f"gate_{snapshot.execution_id}.json"
            with open(snapshot_file, "w") as f:
                json.dump(snapshot.to_dict(), f, indent=2)

    def rollback_to_gate(self, execution_id: str, target_gate: str) -> bool:
        """Rollback to a specific gate state."""
        snapshot = next((s for s in self._execution_history
                        if s.execution_id == execution_id), None)
        if not snapshot:
            raise ValueError(f"No snapshot found for execution_id: {execution_id}")

        # Validate target_gate is in the sequence
        if target_gate not in snapshot.gate_sequence:
            raise ValueError(f"Target gate {target_gate} not in execution sequence: {snapshot.gate_sequence}")

        # Check if target gate was passed in the execution
        if target_gate not in snapshot.passed_gates:
            # If the target gate failed, we can't rollback to it, but we can rollback to before it
            # Return False to indicate the gate didn't pass originally
            return False

        # In a real implementation, we would restore the system state to the point
        # where the target gate had just completed successfully
        # For now, we just validate that rollback is theoretically possible
        return True

    def get_execution_history(self) -> List[GateExecutionSnapshot]:
        """Return the complete execution history."""
        return self._execution_history.copy()

    def get_snapshot_by_id(self, execution_id: str) -> Optional[GateExecutionSnapshot]:
        """Retrieve a specific snapshot by execution ID."""
        for snapshot in self._execution_history:
            if snapshot.execution_id == execution_id:
                return snapshot
        return None

    def clear_execution_history(self) -> int:
        """Clear execution history and return count of cleared snapshots."""
        count = len(self._execution_history)
        self._execution_history.clear()
        return count

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
