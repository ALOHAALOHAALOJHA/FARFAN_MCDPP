# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase2/phase2_evidence_consumer.py

from dataclasses import dataclass
from typing import Any, Dict

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase2EvidenceConsumer(BaseConsumer):
    """
    Consumidor para evidence nexus en Phase 2.

    From: phase2_80_00_evidence_nexus.py

    Responsabilidad: Analizar evidencia extraída y su calidad.
    """

    consumer_id: str = "phase2_evidence_consumer.py"
    consumer_phase: str = "phase_2"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE2_EVIDENCE",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "EmpiricalSupportSignal",
                "AnswerDeterminacySignal",
                "AnswerSpecificitySignal"
            ],
            subscribed_buses=["epistemic_bus"],
            context_filters={
                "phase": ["phase_2"],
                "consumer_scope": ["Phase_2"]
            },
            required_capabilities=["can_extract"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """Procesa señales de evidencia"""
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "evidence_analysis": {}
        }

        if signal.signal_type == "EmpiricalSupportSignal":
            result["evidence_analysis"] = self._analyze_support(signal)
        elif signal.signal_type == "AnswerDeterminacySignal":
            result["evidence_analysis"] = self._analyze_determinacy(signal)
        elif signal.signal_type == "AnswerSpecificitySignal":
            result["evidence_analysis"] = self._analyze_specificity(signal)

        return result

    def _analyze_support(self, signal: Signal) -> Dict[str, Any]:
        """Analiza soporte empírico"""
        level = str(getattr(signal, 'support_level', 'NONE'))

        return {
            "support_level": level,
            "normative_references": getattr(signal, 'normative_references', []),
            "document_references": getattr(signal, 'document_references', []),
            "institutional_references": getattr(signal, 'institutional_references', [])
        }

    def _analyze_determinacy(self, signal: Signal) -> Dict[str, Any]:
        """Analiza determinación"""
        level = str(getattr(signal, 'determinacy_level', 'INDETERMINATE'))

        return {
            "determinacy_level": level,
            "affirmative_markers": getattr(signal, 'affirmative_markers', []),
            "ambiguity_markers": getattr(signal, 'ambiguity_markers', [])
        }

    def _analyze_specificity(self, signal: Signal) -> Dict[str, Any]:
        """Analiza especificidad"""
        level = str(getattr(signal, 'specificity_level', 'NONE'))
        score = getattr(signal, 'specificity_score', 0.0)

        return {
            "specificity_level": level,
            "specificity_score": score,
            "found_elements": getattr(signal, 'found_elements', []),
            "missing_elements": getattr(signal, 'missing_elements', [])
        }
