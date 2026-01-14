# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase1/phase1_11_00_signal_enrichment.py

from dataclasses import dataclass
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase1SignalEnrichmentConsumer(BaseConsumer):
    """
    Consumidor para signal enrichment en Phase 1.

    Procesa señales de:
    - EMPIRICAL_CORPUS_INDEX.json
    - MC01_structural_markers.json
    - Membership criteria extractors

    Responsabilidad: Enriquecer datos con extracción de membership criteria
    y preparar para procesamiento en fases posteriores.
    """

    consumer_id: str = "phase1_11_00_signal_enrichment.py"
    consumer_phase: str = "phase_1"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE1_ENRICHMENT",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "StructuralAlignmentSignal",
                "EventPresenceSignal",
                "MethodApplicationSignal",
                "AnswerSpecificitySignal"
            ],
            subscribed_buses=["structural_bus", "integrity_bus", "epistemic_bus"],
            context_filters={
                "phase": ["phase_1"],
                "consumer_scope": ["Phase_1"]
            },
            required_capabilities=["can_extract", "can_enrich"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales en Phase 1.

        Enfoque: Análisis de extracción y enriquecimiento
        - Verificar que membership criteria se aplican correctamente
        - Evaluar quality metrics de extracción
        - Identificar gaps en datos empíricos
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "enrichment_analysis": {},
            "quality_score": 0.0
        }

        if signal.signal_type == "MethodApplicationSignal":
            analysis = self._analyze_method_application(signal)
            result["enrichment_analysis"] = analysis
            result["quality_score"] = analysis.get("quality_score", 0.0)

        elif signal.signal_type == "AnswerSpecificitySignal":
            analysis = self._analyze_specificity(signal)
            result["enrichment_analysis"] = analysis
            result["quality_score"] = analysis.get("specificity_score", 0.0)

        elif signal.signal_type == "StructuralAlignmentSignal":
            analysis = self._analyze_corpus_structure(signal)
            result["enrichment_analysis"] = analysis

        elif signal.signal_type == "EventPresenceSignal":
            analysis = self._analyze_extraction_presence(signal)
            result["enrichment_analysis"] = analysis

        return result

    def _analyze_method_application(self, signal: Signal) -> Dict[str, Any]:
        """Analiza aplicación de métodos de extracción"""
        method_id = getattr(signal, 'method_id', '')
        successful = getattr(signal, 'extraction_successful', False)
        extracted = getattr(signal, 'extracted_values', [])
        processing_time = getattr(signal, 'processing_time_ms', 0.0)

        quality_score = 1.0 if successful and extracted else 0.0
        if successful and not extracted:
            quality_score = 0.5  # Method ran but found nothing

        insights = []
        if not successful:
            insights.append(f"Extraction method {method_id} failed")
        if processing_time > 1000:
            insights.append(f"Slow extraction ({processing_time:.0f}ms)")
        if successful and len(extracted) > 10:
            insights.append(f"Rich extraction - {len(extracted)} values found")

        return {
            "method_id": method_id,
            "successful": successful,
            "extracted_count": len(extracted),
            "extracted_values": extracted[:5],  # Sample
            "processing_time_ms": processing_time,
            "quality_score": quality_score,
            "insights": insights
        }

    def _analyze_specificity(self, signal: Signal) -> Dict[str, Any]:
        """Analiza especificidad de respuestas"""
        level = str(getattr(signal, 'specificity_level', 'NONE'))
        score = getattr(signal, 'specificity_score', 0.0)
        expected = getattr(signal, 'expected_elements', [])
        found = getattr(signal, 'found_elements', [])
        missing = getattr(signal, 'missing_elements', [])

        insights = []
        if score < 0.3:
            insights.append("Low specificity - needs more detail")
        if missing:
            insights.append(f"Missing {len(missing)} expected elements")
        if score > 0.8:
            insights.append("High specificity - good quality data")

        return {
            "specificity_level": level,
            "specificity_score": score,
            "expected_elements": expected,
            "found_elements": found,
            "missing_elements": missing,
            "coverage": len(found) / len(expected) if expected else 0.0,
            "insights": insights
        }

    def _analyze_corpus_structure(self, signal: Signal) -> Dict[str, Any]:
        """Analiza estructura del corpus empírico"""
        alignment = str(getattr(signal, 'alignment_status', 'UNKNOWN'))
        missing = getattr(signal, 'missing_elements', [])

        return {
            "alignment_status": alignment,
            "missing_elements": missing,
            "is_complete": len(missing) == 0,
            "recommendation": "Add missing corpus elements" if missing else "Corpus structure OK"
        }

    def _analyze_extraction_presence(self, signal: Signal) -> Dict[str, Any]:
        """Analiza presencia de extracciones esperadas"""
        presence = str(getattr(signal, 'presence_status', 'UNKNOWN'))
        count = getattr(signal, 'event_count', 0)

        status = "OK" if count > 0 else "MISSING"

        return {
            "presence_status": presence,
            "event_count": count,
            "status": status,
            "expected_event": getattr(signal, 'expected_event_type', ''),
            "recommendation": "Verify extraction pipeline" if count == 0 else "OK"
        }
