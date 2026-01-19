# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase9/phase9_reporting_consumer.py

from dataclasses import dataclass
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase9ReportingConsumer(BaseConsumer):
    """
    Consumidor para signal-enriched reporting en Phase 9.

    Responsabilidad: Procesa señales para generación de reportes,
    integrando outputs de todas las fases anteriores para generar
    reportes finales enriquecidos con señales.

    Señales que consume:
    - AnswerDeterminacySignal: Para reportes de determinación
    - AnswerSpecificitySignal: Para reportes de especificidad
    - EmpiricalSupportSignal: Para reportes de evidencia
    - DataIntegritySignal: Para reportes de calidad
    - DecisionDivergenceSignal: Para reportes de divergencias

    Señales que produce (indirectamente via vehicles):
    - ReportGeneratedSignal: Cuando un reporte se genera
    - SignalEnrichedReportSignal: Reporte enriquecido con señales
    """

    consumer_id: str = "phase9_reporting_consumer"
    consumer_phase: str = "phase_09"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE9_REPORTING",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "AnswerDeterminacySignal",
                "AnswerSpecificitySignal",
                "EmpiricalSupportSignal",
                "DataIntegritySignal",
                "DecisionDivergenceSignal",
                "ConfidenceDropSignal",
                "TemporalContrastSignal"
            ],
            subscribed_buses=["epistemic_bus", "integrity_bus", "contrast_bus"],
            context_filters={
                "phase": ["phase_03", "phase_04", "phase_05", "phase_08", "phase_09"],
                "consumer_scope": ["Phase_09", "Cross-Phase"]
            },
            required_capabilities=["can_enrich", "can_validate", "can_transform"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales para generación de reportes.

        Enfoque: Acumular señales para generar reportes finales
        enriquecidos con toda la información del pipeline.
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "report_components": {},
            "report_section": self._determine_report_section(signal),
            "phase": "phase_09"
        }

        if signal.signal_type == "AnswerDeterminacySignal":
            result["report_components"]["determinacy_section"] = self._generate_determinacy_section(signal)

        elif signal.signal_type == "AnswerSpecificitySignal":
            result["report_components"]["specificity_section"] = self._generate_specificity_section(signal)

        elif signal.signal_type == "EmpiricalSupportSignal":
            result["report_components"]["empirical_section"] = self._generate_empirical_section(signal)

        elif signal.signal_type == "DataIntegritySignal":
            result["report_components"]["integrity_section"] = self._generate_integrity_section(signal)

        elif signal.signal_type == "DecisionDivergenceSignal":
            result["report_components"]["divergence_section"] = self._generate_divergence_section(signal)

        elif signal.signal_type == "ConfidenceDropSignal":
            result["report_components"]["confidence_section"] = self._generate_confidence_section(signal)

        elif signal.signal_type == "TemporalContrastSignal":
            result["report_components"]["temporal_section"] = self._generate_temporal_section(signal)

        return result

    def _determine_report_section(self, signal: Signal) -> str:
        """Determina a qué sección del reporte pertenece la señal"""
        signal_type = signal.signal_type

        section_map = {
            "AnswerDeterminacySignal": "EPIDEMIOLOGICAL_ANALYSIS",
            "AnswerSpecificitySignal": "SPECIFICITY_ANALYSIS",
            "EmpiricalSupportSignal": "EMPIRICAL_EVIDENCE",
            "DataIntegritySignal": "DATA_QUALITY",
            "DecisionDivergenceSignal": "DIVERGENCE_ANALYSIS",
            "ConfidenceDropSignal": "CONFIDENCE_ANALYSIS",
            "TemporalContrastSignal": "TEMPORAL_ANALYSIS"
        }

        return section_map.get(signal_type, "GENERAL")

    def _generate_determinacy_section(self, signal: Signal) -> Dict[str, Any]:
        """Genera sección de determinación para reporte"""
        return {
            "section_title": "Answer Determinacy Analysis",
            "determinacy_level": str(getattr(signal, 'determinacy_level', 'UNKNOWN')),
            "affirmative_markers": getattr(signal, 'affirmative_markers', []),
            "ambiguity_markers": getattr(signal, 'ambiguity_markers', []),
            "negation_markers": getattr(signal, 'negation_markers', []),
            "conditional_markers": getattr(signal, 'conditional_markers', []),
            "confidence": str(getattr(signal, 'confidence', 'UNKNOWN'))
        }

    def _generate_specificity_section(self, signal: Signal) -> Dict[str, Any]:
        """Genera sección de especificidad para reporte"""
        return {
            "section_title": "Answer Specificity Analysis",
            "specificity_level": str(getattr(signal, 'specificity_level', 'NONE')),
            "specificity_score": getattr(signal, 'specificity_score', 0.0),
            "expected_elements": getattr(signal, 'expected_elements', []),
            "found_elements": getattr(signal, 'found_elements', []),
            "missing_elements": getattr(signal, 'missing_elements', []),
            "confidence": str(getattr(signal, 'confidence', 'UNKNOWN'))
        }

    def _generate_empirical_section(self, signal: Signal) -> Dict[str, Any]:
        """Genera sección de evidencia empírica para reporte"""
        return {
            "section_title": "Empirical Support Analysis",
            "support_level": str(getattr(signal, 'support_level', 'NONE')),
            "normative_references": getattr(signal, 'normative_references', []),
            "document_references": getattr(signal, 'document_references', []),
            "institutional_references": getattr(signal, 'institutional_references', []),
            "confidence": str(getattr(signal, 'confidence', 'UNKNOWN'))
        }

    def _generate_integrity_section(self, signal: Signal) -> Dict[str, Any]:
        """Genera sección de integridad para reporte"""
        return {
            "section_title": "Data Integrity Analysis",
            "integrity_score": getattr(signal, 'integrity_score', 0.0),
            "referenced_files": getattr(signal, 'referenced_files', []),
            "valid_references": getattr(signal, 'valid_references', []),
            "broken_references": getattr(signal, 'broken_references', []),
            "confidence": str(getattr(signal, 'confidence', 'UNKNOWN'))
        }

    def _generate_divergence_section(self, signal: Signal) -> Dict[str, Any]:
        """Genera sección de divergencia para reporte"""
        return {
            "section_title": "Decision Divergence Analysis",
            "divergence_type": getattr(signal, 'divergence_type', 'UNKNOWN'),
            "baseline_decision": getattr(signal, 'baseline_decision', {}),
            "current_decision": getattr(signal, 'current_decision', {}),
            "divergence_reason": getattr(signal, 'divergence_reason', ''),
            "impact_assessment": getattr(signal, 'impact_assessment', {})
        }

    def _generate_confidence_section(self, signal: Signal) -> Dict[str, Any]:
        """Genera sección de confianza para reporte"""
        return {
            "section_title": "Confidence Drop Analysis",
            "item_id": getattr(signal, 'item_id', ''),
            "previous_confidence": getattr(signal, 'previous_confidence', 0.0),
            "current_confidence": getattr(signal, 'current_confidence', 0.0),
            "drop_percentage": getattr(signal, 'drop_percentage', 0.0),
            "contributing_factors": getattr(signal, 'contributing_factors', [])
        }

    def _generate_temporal_section(self, signal: Signal) -> Dict[str, Any]:
        """Genera sección de análisis temporal para reporte"""
        return {
            "section_title": "Temporal Contrast Analysis",
            "item_id": getattr(signal, 'item_id', ''),
            "baseline_timestamp": getattr(signal, 'baseline_timestamp', ''),
            "current_timestamp": getattr(signal, 'current_timestamp', ''),
            "baseline_state": getattr(signal, 'baseline_state', {}),
            "current_state": getattr(signal, 'current_state', {}),
            "changes_detected": getattr(signal, 'changes_detected', [])
        }
