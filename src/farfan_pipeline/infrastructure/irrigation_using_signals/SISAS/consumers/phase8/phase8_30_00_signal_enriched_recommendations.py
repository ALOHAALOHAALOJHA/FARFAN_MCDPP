# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase8/phase8_30_00_signal_enriched_recommendations.py

from dataclasses import dataclass
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase8SignalEnrichedRecommendationsConsumer(BaseConsumer):
    """
    Consumidor para signal-enriched recommendations en Phase 8.

    Procesa señales de:
    - macro_question.json (ya LISTO PARA IRRIGAR según spec)

    Responsabilidad: Generar recomendaciones basadas en el análisis
    completo de señales a través de todas las fases anteriores.

    Este es el consumidor final que integra todos los insights
    para producir recomendaciones accionables (NO imperativas).
    """

    consumer_id: str = "phase8_30_00_signal_enriched_recommendations.py"
    consumer_phase: str = "phase_8"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE8_RECOMMENDATIONS",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                # Señales de contraste (comparación legacy vs nuevo)
                "DecisionDivergenceSignal",
                "ConfidenceDropSignal",
                "TemporalContrastSignal",
                # Señales epistémicas (calidad de evidencia)
                "AnswerDeterminacySignal",
                "AnswerSpecificitySignal",
                "EmpiricalSupportSignal",
                # Señales de integridad
                "DataIntegritySignal",
                "EventCompletenessSignal"
            ],
            subscribed_buses=[
                "contrast_bus",
                "epistemic_bus",
                "integrity_bus"
            ],
            context_filters={
                "phase": ["phase_8"],
                "consumer_scope": ["Phase_8"]
            },
            required_capabilities=["can_enrich", "can_transform"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales para generar recomendaciones.

        Enfoque: Sintetizar insights de múltiples dimensiones:
        - Divergencias detectadas
        - Caídas de confianza
        - Cambios temporales
        - Calidad de evidencia
        - Integridad de datos

        IMPORTANTE: Las recomendaciones son sugerencias analíticas,
        NO comandos imperativos.
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "recommendations": [],
            "priority": "LOW",
            "confidence": "LOW"
        }

        recommendations = []

        if signal.signal_type == "DecisionDivergenceSignal":
            recs = self._recommend_from_divergence(signal)
            recommendations.extend(recs)

        elif signal.signal_type == "ConfidenceDropSignal":
            recs = self._recommend_from_confidence_drop(signal)
            recommendations.extend(recs)

        elif signal.signal_type == "TemporalContrastSignal":
            recs = self._recommend_from_temporal_contrast(signal)
            recommendations.extend(recs)

        elif signal.signal_type in ["AnswerDeterminacySignal", "AnswerSpecificitySignal", "EmpiricalSupportSignal"]:
            recs = self._recommend_from_epistemic(signal)
            recommendations.extend(recs)

        elif signal.signal_type in ["DataIntegritySignal", "EventCompletenessSignal"]:
            recs = self._recommend_from_integrity(signal)
            recommendations.extend(recs)

        result["recommendations"] = recommendations
        result["priority"] = self._determine_priority(recommendations, signal)
        result["confidence"] = self._determine_confidence(signal)

        return result

    def _recommend_from_divergence(self, signal: Signal) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en divergencias"""
        divergence_type = str(getattr(signal, 'divergence_type', ''))
        severity = str(getattr(signal, 'divergence_severity', ''))
        explanation = getattr(signal, 'divergence_explanation', '')
        legacy_value = getattr(signal, 'legacy_value', None)
        signal_value = getattr(signal, 'signal_based_value', None)

        recommendations = []

        if "CRITICAL" in severity:
            recommendations.append({
                "type": "INVESTIGATE",
                "priority": "HIGH",
                "title": "Critical divergence detected between legacy and signal-based systems",
                "description": explanation,
                "details": {
                    "legacy_value": legacy_value,
                    "signal_based_value": signal_value,
                    "divergence_type": divergence_type
                },
                "suggested_actions": [
                    "Review the underlying data sources",
                    "Validate signal extraction logic",
                    "Compare methodologies between systems",
                    "Consider manual review of affected items"
                ]
            })

        elif "HIGH" in severity:
            recommendations.append({
                "type": "REVIEW",
                "priority": "MEDIUM",
                "title": "Significant divergence requires attention",
                "description": explanation,
                "suggested_actions": [
                    "Analyze root cause of divergence",
                    "Validate both system outputs",
                    "Document differences for stakeholders"
                ]
            })

        return recommendations

    def _recommend_from_confidence_drop(self, signal: Signal) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en caída de confianza"""
        item_id = getattr(signal, 'item_id', '')
        previous = getattr(signal, 'previous_confidence', 0.0)
        current = getattr(signal, 'current_confidence', 0.0)
        drop = getattr(signal, 'drop_percentage', 0.0)
        factors = getattr(signal, 'contributing_factors', [])

        recommendations = []

        if drop > 30:  # Caída significativa
            recommendations.append({
                "type": "MONITOR",
                "priority": "MEDIUM",
                "title": f"Confidence drop of {drop:.1f}% detected for {item_id}",
                "description": f"Confidence decreased from {previous:.2f} to {current:.2f}",
                "contributing_factors": factors,
                "suggested_actions": [
                    "Investigate what changed in the underlying data",
                    "Review recent updates to extraction methods",
                    "Check for data quality issues",
                    "Consider additional validation"
                ]
            })

        return recommendations

    def _recommend_from_temporal_contrast(self, signal: Signal) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en cambios temporales"""
        changes = getattr(signal, 'changes_detected', [])
        stability = getattr(signal, 'stability_score', 1.0)

        recommendations = []

        if stability < 0.5:  # Sistema inestable
            recommendations.append({
                "type": "ALERT",
                "priority": "HIGH",
                "title": "High instability detected in evaluation",
                "description": f"Stability score: {stability:.2f}",
                "changes_detected": len(changes),
                "suggested_actions": [
                    "Review what caused instability",
                    "Consider freezing data for consistent analysis",
                    "Validate that changes are intentional",
                    "Document evolution of the system"
                ]
            })

        return recommendations

    def _recommend_from_epistemic(self, signal: Signal) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en señales epistémicas"""
        recommendations = []

        if signal.signal_type == "AnswerDeterminacySignal":
            level = str(getattr(signal, 'determinacy_level', ''))
            if "LOW" in level or "INDETERMINATE" in level:
                recommendations.append({
                    "type": "IMPROVE",
                    "priority": "LOW",
                    "title": "Low determinacy in answer",
                    "description": "Answer lacks clear affirmation or negation",
                    "suggested_actions": [
                        "Request more specific information",
                        "Clarify ambiguous statements",
                        "Seek additional documentation"
                    ]
                })

        elif signal.signal_type == "AnswerSpecificitySignal":
            score = getattr(signal, 'specificity_score', 0.0)
            if score < 0.5:
                missing = getattr(signal, 'missing_elements', [])
                recommendations.append({
                    "type": "ENHANCE",
                    "priority": "LOW",
                    "title": "Low specificity in answer",
                    "description": f"Specificity score: {score:.2f}",
                    "missing_elements": missing,
                    "suggested_actions": [
                        "Request specific details",
                        "Identify concrete instruments or mechanisms",
                        "Clarify institutional responsibilities"
                    ]
                })

        return recommendations

    def _recommend_from_integrity(self, signal: Signal) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en integridad"""
        recommendations = []

        if signal.signal_type == "DataIntegritySignal":
            broken = getattr(signal, 'broken_references', [])
            if broken:
                recommendations.append({
                    "type": "FIX",
                    "priority": "HIGH",
                    "title": "Broken references detected",
                    "description": f"{len(broken)} broken references found",
                    "broken_references": broken,
                    "suggested_actions": [
                        "Update references to valid paths",
                        "Remove references to non-existent files",
                        "Verify data dependencies"
                    ]
                })

        elif signal.signal_type == "EventCompletenessSignal":
            score = getattr(signal, 'completeness_score', 0.0)
            missing = getattr(signal, 'missing_fields', [])
            if score < 0.7:
                recommendations.append({
                    "type": "COMPLETE",
                    "priority": "MEDIUM",
                    "title": "Incomplete data detected",
                    "description": f"Completeness: {score:.1%}",
                    "missing_fields": missing,
                    "suggested_actions": [
                        "Fill in missing required fields",
                        "Validate data collection process",
                        "Consider data augmentation"
                    ]
                })

        return recommendations

    def _determine_priority(self, recommendations: List[Dict[str, Any]], signal: Signal) -> str:
        """Determina prioridad general basada en recomendaciones"""
        if not recommendations:
            return "LOW"

        priorities = [rec.get("priority", "LOW") for rec in recommendations]

        if "HIGH" in priorities:
            return "HIGH"
        elif "MEDIUM" in priorities:
            return "MEDIUM"
        else:
            return "LOW"

    def _determine_confidence(self, signal: Signal) -> str:
        """Determina nivel de confianza en las recomendaciones"""
        confidence = getattr(signal, 'confidence', None)

        if confidence:
            return str(confidence).replace("SignalConfidence.", "")

        # Fallback basado en tipo de señal
        if signal.signal_type in ["DecisionDivergenceSignal", "DataIntegritySignal"]:
            return "HIGH"  # Estos son hechos empíricos
        elif signal.signal_type in ["ConfidenceDropSignal", "TemporalContrastSignal"]:
            return "MEDIUM"  # Tendencias observadas
        else:
            return "LOW"  # Interpretaciones
