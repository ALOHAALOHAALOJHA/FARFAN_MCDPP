# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase4/phase4_aggregation_consumer.py

from dataclasses import dataclass
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase4AggregationConsumer(BaseConsumer):
    """
    Consumidor para signal-enriched aggregation en Phase 4.

    Responsabilidad: Procesa señales para agregación enriquecida,
    integrando outputs de Phase 3 (scoring) para generar agregados
    dimensionales y territoriales.

    Señales que consume:
    - AnswerDeterminacySignal: Para ponderación por determinación
    - AnswerSpecificitySignal: Para agregación por especificidad
    - DataIntegritySignal: Para validación de referencias
    - EventCompletenessSignal: Para verificación de completitud

    Señales que produce (indirectamente via vehicles):
    - AggregationCompleteSignal: Cuando la agregación termina
    - UncertaintyQuantifiedSignal: Cuantificación de incertidumbre
    """

    consumer_id: str = "phase4_aggregation_consumer"
    consumer_phase: str = "phase_4"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE4_AGGREGATION",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "AnswerDeterminacySignal",
                "AnswerSpecificitySignal",
                "DataIntegritySignal",
                "EventCompletenessSignal",
                "StructuralAlignmentSignal",
                "CanonicalMappingSignal"
            ],
            subscribed_buses=["epistemic_bus", "structural_bus", "integrity_bus"],
            context_filters={
                "phase": ["phase_3", "phase_4"],
                "consumer_scope": ["Phase_4", "Cross-Phase"]
            },
            required_capabilities=["can_enrich", "can_transform", "can_validate"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales para agregación enriquecida.

        Enfoque: Agregar scores enriquecidos por dimensiones y territorios,
        aplicando métodos Choquet y cuantificando incertidumbre.
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "aggregation_components": {},
            "aggregated_value": 0.0,
            "uncertainty_bounds": {},
            "phase": "phase_4"
        }

        if signal.signal_type == "AnswerDeterminacySignal":
            result["aggregation_components"]["determinacy_weight"] = self._get_determinacy_weight(signal)

        elif signal.signal_type == "AnswerSpecificitySignal":
            result["aggregation_components"]["specificity_weight"] = self._get_specificity_weight(signal)

        elif signal.signal_type == "DataIntegritySignal":
            result["aggregation_components"]["integrity_weight"] = self._get_integrity_weight(signal)

        elif signal.signal_type == "EventCompletenessSignal":
            result["aggregation_components"]["completeness_weight"] = self._get_completeness_weight(signal)

        elif signal.signal_type == "StructuralAlignmentSignal":
            result["aggregation_components"]["alignment_weight"] = self._get_alignment_weight(signal)

        elif signal.signal_type == "CanonicalMappingSignal":
            result["aggregation_components"]["mapping_weight"] = self._get_mapping_weight(signal)

        # Calculate aggregated value
        result["aggregated_value"] = self._calculate_aggregated_value(result["aggregation_components"])

        # Quantify uncertainty
        result["uncertainty_bounds"] = self._quantify_uncertainty(result["aggregation_components"])

        return result

    def _get_determinacy_weight(self, signal: Signal) -> float:
        """Obtiene peso de determinación para agregación"""
        level = str(getattr(signal, 'determinacy_level', 'INDETERMINATE'))
        weight_map = {
            "DeterminacyLevel.HIGH": 1.0,
            "DeterminacyLevel.MEDIUM": 0.7,
            "DeterminacyLevel.LOW": 0.4,
            "DeterminacyLevel.INDETERMINATE": 0.1
        }
        return weight_map.get(level, 0.5)

    def _get_specificity_weight(self, signal: Signal) -> float:
        """Obtiene peso de especificidad para agregación"""
        return getattr(signal, 'specificity_score', 0.5)

    def _get_integrity_weight(self, signal: Signal) -> float:
        """Obtiene peso de integridad para agregación"""
        return getattr(signal, 'integrity_score', 1.0)

    def _get_completeness_weight(self, signal: Signal) -> float:
        """Obtiene peso de completitud para agregación"""
        return getattr(signal, 'completeness_score', 1.0)

    def _get_alignment_weight(self, signal: Signal) -> float:
        """Obtiene peso de alineación estructural"""
        status = str(getattr(signal, 'alignment_status', 'MISALIGNED'))
        weight_map = {
            "AlignmentStatus.ALIGNED": 1.0,
            "AlignmentStatus.PARTIAL": 0.6,
            "AlignmentStatus.MISALIGNED": 0.2
        }
        return weight_map.get(status, 0.5)

    def _get_mapping_weight(self, signal: Signal) -> float:
        """Obtiene peso de mapeo canónico"""
        return getattr(signal, 'mapping_completeness', 0.5)

    def _calculate_aggregated_value(self, components: Dict[str, float]) -> float:
        """Calcula valor agregado usando ponderación"""
        if not components:
            return 0.0

        # Pesos para el método Choquet simplificado
        choquet_weights = {
            "determinacy_weight": 0.25,
            "specificity_weight": 0.25,
            "integrity_weight": 0.20,
            "completeness_weight": 0.15,
            "alignment_weight": 0.10,
            "mapping_weight": 0.05
        }

        weighted_sum = sum(
            components.get(key, 0.0) * weight
            for key, weight in choquet_weights.items()
        )

        return min(1.0, weighted_sum)

    def _quantify_uncertainty(self, components: Dict[str, float]) -> Dict[str, Any]:
        """Cuantifica incertidumbre en la agregación"""
        if not components:
            return {"lower_bound": 0.0, "upper_bound": 0.0, "confidence_interval": "UNKNOWN"}

        # Varianza basada en dispersión de componentes
        values = list(components.values())
        if not values:
            return {"lower_bound": 0.0, "upper_bound": 0.0, "confidence_interval": "UNKNOWN"}

        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5

        # Intervalos de confianza (95%)
        margin = 1.96 * std_dev
        lower = max(0.0, mean_val - margin)
        upper = min(1.0, mean_val + margin)

        # Determinar nivel de confianza
        if std_dev < 0.1:
            confidence = "HIGH"
        elif std_dev < 0.2:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return {
            "lower_bound": lower,
            "upper_bound": upper,
            "std_dev": std_dev,
            "confidence_interval": confidence,
            "margin_of_error": margin
        }
