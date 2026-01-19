# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase2/phase2_executor_consumer.py

from dataclasses import dataclass
from typing import Any, Dict

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase2ExecutorConsumer(BaseConsumer):
    """
    Consumidor para executors en Phase 2.

    Consolidates functionality from:
    - phase2_60_00_base_executor_with_contract.py

    Responsabilidad: Validar que los executores respetan contratos
    y ejecutan correctamente.
    """

    consumer_id: str = "phase2_executor_consumer.py"
    consumer_phase: str = "phase_02"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE2_EXECUTOR",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "ExecutionAttemptSignal",
                "FailureModeSignal"
            ],
            subscribed_buses=["operational_bus"],
            context_filters={
                "phase": ["phase_02"],
                "consumer_scope": ["Phase_02"]
            },
            required_capabilities=["can_validate"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """Procesa señales de executors"""
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "executor_analysis": {}
        }

        if signal.signal_type == "ExecutionAttemptSignal":
            result["executor_analysis"] = self._analyze_execution(signal)
        elif signal.signal_type == "FailureModeSignal":
            result["executor_analysis"] = self._analyze_failure(signal)

        return result

    def _analyze_execution(self, signal: Signal) -> Dict[str, Any]:
        """Analiza ejecución"""
        return {
            "status": str(getattr(signal, 'status', 'UNKNOWN')),
            "duration_ms": getattr(signal, 'duration_ms', 0.0),
            "component": getattr(signal, 'component', ''),
            "operation": getattr(signal, 'operation', '')
        }

    def _analyze_failure(self, signal: Signal) -> Dict[str, Any]:
        """Analiza fallas"""
        return {
            "failure_mode": str(getattr(signal, 'failure_mode', 'UNKNOWN')),
            "error_message": getattr(signal, 'error_message', ''),
            "recoverable": getattr(signal, 'recoverable', False)
        }
