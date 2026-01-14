# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase7/phase7_meso_consumer.py

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ... core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase7MesoConsumer(BaseConsumer):
    """
    Consumidor para meso_questions.json en Phase 7.
    
    Procesa preguntas de nivel meso y genera análisis agregado.
    """
    
    consumer_id: str = "phase7_meso_consumer.py"
    consumer_phase: str = "phase_7"
    
    def __post_init__(self):
        super().__post_init__()
        
        # Configurar contrato de consumo
        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE7_MESO",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "CanonicalMappingSignal",
                "StructuralAlignmentSignal"
            ],
            subscribed_buses=["structural_bus"],
            context_filters={
                "phase":  ["phase_7"],
                "node_type": ["question"]
            },
            required_capabilities=["can_scope_context"]
        )
    
    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa una señal recibida. 
        
        NO ejecuta decisiones, solo analiza. 
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal. signal_type,
            "processed":  True,
            "analysis": {}
        }
        
        if signal.signal_type == "CanonicalMappingSignal":
            result["analysis"] = self._analyze_mapping(signal)
        elif signal.signal_type == "StructuralAlignmentSignal":
            result["analysis"] = self._analyze_alignment(signal)
        
        return result
    
    def _analyze_mapping(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de mapeo"""
        return {
            "mapped_entities": getattr(signal, 'mapped_entities', {}),
            "mapping_completeness": getattr(signal, 'mapping_completeness', 0.0),
            "unmapped":  getattr(signal, 'unmapped_aspects', [])
        }
    
    def _analyze_alignment(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de alineación"""
        return {
            "alignment_status": getattr(signal, 'alignment_status', None),
            "missing_elements": getattr(signal, 'missing_elements', [])
        }