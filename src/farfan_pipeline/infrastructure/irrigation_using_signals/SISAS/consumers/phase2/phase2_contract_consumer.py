# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase2/phase2_contract_consumer.py

from dataclasses import dataclass
from typing import Any, Dict

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase2ContractConsumer(BaseConsumer):
    """
    Consumidor para contract handling en Phase 2.

    Consolidates:
    - phase2_95_00_contract_hydrator.py
    - phase2_95_02_precision_tracking.py

    Responsabilidad: Monitorear hidratación de contratos y
    tracking de precisión.
    """

    consumer_id: str = "phase2_contract_consumer.py"
    consumer_phase: str = "phase_2"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE2_CONTRACT",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "StructuralAlignmentSignal",
                "DataIntegritySignal",
                "ExecutionAttemptSignal"
            ],
            subscribed_buses=["structural_bus", "integrity_bus", "operational_bus"],
            context_filters={
                "phase": ["phase_2"],
                "consumer_scope": ["Phase_2"]
            },
            required_capabilities=["can_validate", "can_enrich"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """Procesa señales de contratos"""
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "contract_analysis": {}
        }

        if signal.signal_type == "StructuralAlignmentSignal":
            result["contract_analysis"] = self._analyze_contract_structure(signal)
        elif signal.signal_type == "DataIntegritySignal":
            result["contract_analysis"] = self._analyze_contract_integrity(signal)
        elif signal.signal_type == "ExecutionAttemptSignal":
            result["contract_analysis"] = self._analyze_hydration(signal)

        return result

    def _analyze_contract_structure(self, signal: Signal) -> Dict[str, Any]:
        """Analiza estructura de contratos"""
        return {
            "alignment_status": str(getattr(signal, 'alignment_status', 'UNKNOWN')),
            "missing_elements": getattr(signal, 'missing_elements', []),
            "extra_elements": getattr(signal, 'extra_elements', [])
        }

    def _analyze_contract_integrity(self, signal: Signal) -> Dict[str, Any]:
        """Analiza integridad de contratos"""
        return {
            "integrity_score": getattr(signal, 'integrity_score', 0.0),
            "broken_references": getattr(signal, 'broken_references', [])
        }

    def _analyze_hydration(self, signal: Signal) -> Dict[str, Any]:
        """Analiza hidratación de contratos"""
        return {
            "status": str(getattr(signal, 'status', 'UNKNOWN')),
            "duration_ms": getattr(signal, 'duration_ms', 0.0),
            "operation": getattr(signal, 'operation', '')
        }
