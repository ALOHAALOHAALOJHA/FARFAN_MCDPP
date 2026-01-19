# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase5/phase5_uncertainty_consumer.py

from dataclasses import dataclass
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase5UncertaintyConsumer(BaseConsumer):
    """
    Consumidor para uncertainty quantification en Phase 5.

    Responsabilidad: Procesa señales para cuantificación de incertidumbre,
    integrando outputs de Phase 4 (aggregation) para generar métricas
    de confianza y bounds de incertidumbre.

    Señales que consume:
    - DataIntegritySignal: Para validación de calidad de datos
    - EventCompletenessSignal: Para evaluación de completitud
    - EmpiricalSupportSignal: Para análisis de soporte empírico

    Señales que produce (indirectamente via vehicles):
    - UncertaintyQuantifiedSignal: Cuantificación de incertidumbre
    - ConfidenceBoundsSignal: Límites de confianza
    """

    consumer_id: str = "phase5_uncertainty_consumer"
    consumer_phase: str = "phase_5"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE5_UNCERTAINTY",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "DataIntegritySignal",
                "EventCompletenessSignal",
                "EmpiricalSupportSignal",
                "AnswerDeterminacySignal",
                "AnswerSpecificitySignal"
            ],
            subscribed_buses=["integrity_bus", "epistemic_bus"],
            context_filters={
                "phase": ["phase_4", "phase_5"],
                "consumer_scope": ["Phase_5", "Cross-Phase"]
            },
            required_capabilities=["can_validate", "can_enrich"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales para cuantificación de incertidumbre.

        Enfoque: Calcular bounds de incertidumbre y niveles de confianza
        para los agregados de Phase 4.
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "uncertainty_metrics": {},
            "confidence_level": "UNKNOWN",
            "phase": "phase_5"
        }

        if signal.signal_type == "DataIntegritySignal":
            result["uncertainty_metrics"] = self._quantify_integrity_uncertainty(signal)

        elif signal.signal_type == "EventCompletenessSignal":
            result["uncertainty_metrics"] = self._quantify_completeness_uncertainty(signal)

        elif signal.signal_type == "EmpiricalSupportSignal":
            result["uncertainty_metrics"] = self._quantify_empirical_uncertainty(signal)

        elif signal.signal_type == "AnswerDeterminacySignal":
            result["uncertainty_metrics"] = self._quantify_determinacy_uncertainty(signal)

        elif signal.signal_type == "AnswerSpecificitySignal":
            result["uncertainty_metrics"] = self._quantify_specificity_uncertainty(signal)

        # Calculate overall confidence
        result["confidence_level"] = self._calculate_confidence(result["uncertainty_metrics"])

        return result

    def _quantify_integrity_uncertainty(self, signal: Signal) -> Dict[str, Any]:
        """Cuantifica incertidumbre de integridad"""
        integrity_score = getattr(signal, 'integrity_score', 1.0)
        broken_refs = getattr(signal, 'broken_references', [])
        total_refs = getattr(signal, 'referenced_files', [])

        # Incertidumbre aumenta con referencias rotas
        if total_refs and len(total_refs) > 0:
            ref_uncertainty = len(broken_refs) / len(total_refs)
        else:
            ref_uncertainty = 0.0

        # Invertir score para obtener incertidumbre
        uncertainty = 1.0 - integrity_score

        return {
            "integrity_uncertainty": uncertainty,
            "reference_uncertainty": ref_uncertainty,
            "total_uncertainty": max(uncertainty, ref_uncertainty),
            "broken_count": len(broken_refs),
            "total_references": len(total_refs)
        }

    def _quantify_completeness_uncertainty(self, signal: Signal) -> Dict[str, Any]:
        """Cuantifica incertidumbre de completitud"""
        completeness_score = getattr(signal, 'completeness_score', 1.0)
        missing_fields = getattr(signal, 'missing_fields', [])

        # Incertidumbre basada en campos faltantes
        if missing_fields:
            field_uncertainty = len(missing_fields) * 0.1  # 10% por campo faltante
        else:
            field_uncertainty = 0.0

        # Invertir score
        uncertainty = 1.0 - completeness_score

        return {
            "completeness_uncertainty": uncertainty,
            "field_uncertainty": min(1.0, field_uncertainty),
            "total_uncertainty": max(uncertainty, field_uncertainty),
            "missing_count": len(missing_fields)
        }

    def _quantify_empirical_uncertainty(self, signal: Signal) -> Dict[str, Any]:
        """Cuantifica incertidumbre de soporte empírico"""
        support_level = str(getattr(signal, 'support_level', 'NONE'))
        normative_refs = getattr(signal, 'normative_references', [])
        document_refs = getattr(signal, 'document_references', [])

        # Mapear nivel de soporte a incertidumbre
        uncertainty_map = {
            "EmpiricalSupportLevel.STRONG": 0.0,
            "EmpiricalSupportLevel.MODERATE": 0.3,
            "EmpiricalSupportLevel.WEAK": 0.6,
            "EmpiricalSupportLevel.NONE": 1.0
        }

        base_uncertainty = uncertainty_map.get(support_level, 0.5)

        # Reducir incertidumbre con referencias adicionales
        ref_count = len(normative_refs) + len(document_refs)
        ref_reduction = min(0.3, ref_count * 0.05)

        total_uncertainty = max(0.0, base_uncertainty - ref_reduction)

        return {
            "empirical_uncertainty": total_uncertainty,
            "base_uncertainty": base_uncertainty,
            "reference_reduction": ref_reduction,
            "total_references": ref_count
        }

    def _quantify_determinacy_uncertainty(self, signal: Signal) -> Dict[str, Any]:
        """Cuantifica incertidumbre de determinación"""
        determinacy_level = str(getattr(signal, 'determinacy_level', 'INDETERMINATE'))
        ambiguity_markers = getattr(signal, 'ambiguity_markers', [])
        conditional_markers = getattr(signal, 'conditional_markers', [])

        # Mapear nivel de determinación a incertidumbre
        uncertainty_map = {
            "DeterminacyLevel.HIGH": 0.0,
            "DeterminacyLevel.MEDIUM": 0.3,
            "DeterminacyLevel.LOW": 0.7,
            "DeterminacyLevel.INDETERMINATE": 1.0
        }

        base_uncertainty = uncertainty_map.get(determinacy_level, 0.5)

        # Aumentar incertidumbre con marcadores
        marker_penalty = (len(ambiguity_markers) + len(conditional_markers)) * 0.1
        total_uncertainty = min(1.0, base_uncertainty + marker_penalty)

        return {
            "determinacy_uncertainty": total_uncertainty,
            "base_uncertainty": base_uncertainty,
            "marker_penalty": marker_penalty,
            "ambiguity_count": len(ambiguity_markers),
            "conditional_count": len(conditional_markers)
        }

    def _quantify_specificity_uncertainty(self, signal: Signal) -> Dict[str, Any]:
        """Cuantifica incertidumbre de especificidad"""
        specificity_score = getattr(signal, 'specificity_score', 0.0)
        missing_elements = getattr(signal, 'missing_elements', [])

        # Invertir score de especificidad
        base_uncertainty = 1.0 - specificity_score

        # Penalizar elementos faltantes
        missing_penalty = len(missing_elements) * 0.15
        total_uncertainty = min(1.0, base_uncertainty + missing_penalty)

        return {
            "specificity_uncertainty": total_uncertainty,
            "base_uncertainty": base_uncertainty,
            "missing_penalty": missing_penalty,
            "missing_count": len(missing_elements)
        }

    def _calculate_confidence(self, metrics: Dict[str, Any]) -> str:
        """Calcula nivel de confianza global"""
        if not metrics:
            return "UNKNOWN"

        # Obtener incertidumbres totales
        total_uncertainties = [
            m.get("total_uncertainty", 0.5)
            for m in [metrics] if isinstance(m, dict)
        ]

        if not total_uncertainties:
            return "UNKNOWN"

        avg_uncertainty = sum(total_uncertainties) / len(total_uncertainties)

        if avg_uncertainty < 0.2:
            return "HIGH"
        elif avg_uncertainty < 0.5:
            return "MEDIUM"
        else:
            return "LOW"
