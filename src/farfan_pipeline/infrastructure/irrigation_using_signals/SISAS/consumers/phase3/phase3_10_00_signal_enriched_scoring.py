# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase3/phase3_10_00_signal_enriched_scoring.py

from dataclasses import dataclass
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase3SignalEnrichedScoringConsumer(BaseConsumer):
    """
    Consumidor para signal-enriched scoring en Phase 3.

    Procesa señales de:
    - corpus_empirico_calibracion_extractores.json
    - corpus_empirico_integrado.json
    - corpus_empirico_normatividad.json
    - colombia_context.json
    - municipal_governance.json
    - pdet_municipalities.json

    Responsabilidad: Generar scores enriquecidos con señales,
    integrando evidencia empírica, contexto colombiano y calibraciones.
    """

    consumer_id: str = "phase3_10_00_phase3_signal_enriched_scoring.py"
    consumer_phase: str = "phase_03"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE3_SCORING",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "AnswerDeterminacySignal",
                "AnswerSpecificitySignal",
                "EmpiricalSupportSignal",
                "MethodApplicationSignal",
                "CanonicalMappingSignal",
                "EventCompletenessSignal"
            ],
            subscribed_buses=["epistemic_bus", "structural_bus", "integrity_bus"],
            context_filters={
                "phase": ["phase_03"],
                "consumer_scope": ["Phase_03"]
            },
            required_capabilities=["can_enrich", "can_transform"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales para scoring enriquecido.

        Enfoque: Combinar múltiples dimensiones de análisis:
        - Determinación y especificidad de respuestas
        - Soporte empírico y documental
        - Aplicación de métodos de calibración
        - Mapeo a contexto colombiano/PDET
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "scoring_components": {},
            "enriched_score": 0.0,
            "confidence": "INDETERMINATE"
        }

        scoring_components = {}

        if signal.signal_type == "AnswerDeterminacySignal":
            component = self._score_determinacy(signal)
            scoring_components["determinacy"] = component

        elif signal.signal_type == "AnswerSpecificitySignal":
            component = self._score_specificity(signal)
            scoring_components["specificity"] = component

        elif signal.signal_type == "EmpiricalSupportSignal":
            component = self._score_empirical_support(signal)
            scoring_components["empirical_support"] = component

        elif signal.signal_type == "MethodApplicationSignal":
            component = self._score_method_application(signal)
            scoring_components["method_application"] = component

        elif signal.signal_type == "CanonicalMappingSignal":
            component = self._score_canonical_mapping(signal)
            scoring_components["canonical_mapping"] = component

        elif signal.signal_type == "EventCompletenessSignal":
            component = self._score_completeness(signal)
            scoring_components["completeness"] = component

        result["scoring_components"] = scoring_components

        # Calculate enriched score (weighted average)
        result["enriched_score"] = self._calculate_enriched_score(scoring_components)
        result["confidence"] = self._determine_confidence(scoring_components)

        return result

    def _score_determinacy(self, signal: Signal) -> Dict[str, Any]:
        """Score basado en determinación de respuesta"""
        level = str(getattr(signal, 'determinacy_level', 'INDETERMINATE'))

        score_map = {
            "DeterminacyLevel.HIGH": 1.0,
            "DeterminacyLevel.MEDIUM": 0.6,
            "DeterminacyLevel.LOW": 0.3,
            "DeterminacyLevel.INDETERMINATE": 0.0
        }

        score = score_map.get(level, 0.0)
        weight = 0.25  # 25% del score total

        return {
            "score": score,
            "weight": weight,
            "weighted_score": score * weight,
            "level": level,
            "affirmative_markers": getattr(signal, 'affirmative_markers', []),
            "ambiguity_markers": getattr(signal, 'ambiguity_markers', [])
        }

    def _score_specificity(self, signal: Signal) -> Dict[str, Any]:
        """Score basado en especificidad"""
        level = str(getattr(signal, 'specificity_level', 'NONE'))
        score = getattr(signal, 'specificity_score', 0.0)
        weight = 0.20  # 20% del score total

        return {
            "score": score,
            "weight": weight,
            "weighted_score": score * weight,
            "level": level,
            "found_elements": getattr(signal, 'found_elements', []),
            "missing_elements": getattr(signal, 'missing_elements', [])
        }

    def _score_empirical_support(self, signal: Signal) -> Dict[str, Any]:
        """Score basado en soporte empírico"""
        level = str(getattr(signal, 'support_level', 'NONE'))

        score_map = {
            "EmpiricalSupportLevel.STRONG": 1.0,
            "EmpiricalSupportLevel.MODERATE": 0.7,
            "EmpiricalSupportLevel.WEAK": 0.4,
            "EmpiricalSupportLevel.NONE": 0.0
        }

        score = score_map.get(level, 0.0)
        weight = 0.30  # 30% del score total (muy importante)

        normative = getattr(signal, 'normative_references', [])
        document = getattr(signal, 'document_references', [])
        institutional = getattr(signal, 'institutional_references', [])

        # Bonus por cantidad de referencias
        reference_count = len(normative) + len(document) + len(institutional)
        reference_bonus = min(0.2, reference_count * 0.05)
        score = min(1.0, score + reference_bonus)

        return {
            "score": score,
            "weight": weight,
            "weighted_score": score * weight,
            "level": level,
            "normative_references": normative,
            "document_references": document,
            "institutional_references": institutional,
            "reference_bonus": reference_bonus
        }

    def _score_method_application(self, signal: Signal) -> Dict[str, Any]:
        """Score basado en aplicación de métodos"""
        successful = getattr(signal, 'extraction_successful', False)
        extracted = getattr(signal, 'extracted_values', [])
        weight = 0.15  # 15% del score total

        score = 1.0 if successful and extracted else 0.5 if successful else 0.0

        return {
            "score": score,
            "weight": weight,
            "weighted_score": score * weight,
            "method_id": getattr(signal, 'method_id', ''),
            "successful": successful,
            "extracted_count": len(extracted)
        }

    def _score_canonical_mapping(self, signal: Signal) -> Dict[str, Any]:
        """Score basado en mapeo canónico"""
        completeness = getattr(signal, 'mapping_completeness', 0.0)
        weight = 0.10  # 10% del score total

        return {
            "score": completeness,
            "weight": weight,
            "weighted_score": completeness * weight,
            "mapped_entities": getattr(signal, 'mapped_entities', {}),
            "unmapped_aspects": getattr(signal, 'unmapped_aspects', [])
        }

    def _score_completeness(self, signal: Signal) -> Dict[str, Any]:
        """Score basado en completitud de datos"""
        completeness_score = getattr(signal, 'completeness_score', 0.0)
        weight = 0.10  # 10% del score total (no tan crítico)

        return {
            "score": completeness_score,
            "weight": weight,
            "weighted_score": completeness_score * weight,
            "missing_fields": getattr(signal, 'missing_fields', [])
        }

    def _calculate_enriched_score(self, components: Dict[str, Dict[str, Any]]) -> float:
        """Calcula score enriquecido combinando componentes"""
        if not components:
            return 0.0

        total_weighted = sum(
            comp.get("weighted_score", 0.0)
            for comp in components.values()
        )

        total_weight = sum(
            comp.get("weight", 0.0)
            for comp in components.values()
        )

        if total_weight == 0:
            return 0.0

        # Normalizar al peso total actual (puede ser < 1.0 si faltan componentes)
        return total_weighted / total_weight

    def _determine_confidence(self, components: Dict[str, Dict[str, Any]]) -> str:
        """Determina nivel de confianza del scoring"""
        if not components:
            return "INDETERMINATE"

        # Contar componentes presentes
        component_count = len(components)

        # Si tenemos todos los componentes principales
        has_determinacy = "determinacy" in components
        has_specificity = "specificity" in components
        has_empirical = "empirical_support" in components

        score = self._calculate_enriched_score(components)

        if component_count >= 5 and score >= 0.8:
            return "HIGH"
        elif component_count >= 3 and score >= 0.6:
            return "MEDIUM"
        elif has_determinacy or has_specificity or has_empirical:
            return "LOW"
        else:
            return "INDETERMINATE"
