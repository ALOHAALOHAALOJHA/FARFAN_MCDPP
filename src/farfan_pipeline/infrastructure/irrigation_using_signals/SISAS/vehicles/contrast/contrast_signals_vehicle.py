# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/contrast/contrast_signals_vehicle.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import re

from ..base_vehicle import BaseVehicle, VehicleCapabilities
from ...core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ...core.event import Event
from ...core.contracts import PublicationContract, ContractType, ContractStatus, SignalTypeSpec
from ...signal_types.types.contrast import (
    DecisionDivergenceSignal,
    ConfidenceDropSignal,
    TemporalContrastSignal
)


@dataclass
class ContrastSignalsVehicle(BaseVehicle):
    """
    Vehículo: contrast_signals_vehicle

    Responsabilidad: Generar señales de contraste para análisis de
    divergencias, cambios de confianza y variaciones temporales.

    Archivos que procesa:
    - Decisiones históricas y actuales para detectar divergencias
    - Métricas de confianza para detectar caídas
    - Datos temporales para análisis de tendencias

    Señales que produce:
    - DecisionDivergenceSignal: Divergencia entre decisiones
    - ConfidenceDropSignal: Caída de confianza
    - TemporalContrastSignal: Cambios temporales
    """
    vehicle_id: str = "contrast_signals_vehicle"
    vehicle_name: str = "Contrast Signals Vehicle"

    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=False,
        can_transform=True,
        can_enrich=True,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=["DecisionDivergenceSignal", "ConfidenceDropSignal", "TemporalContrastSignal"]
    ))

    # Umbrales para detección
    confidence_drop_threshold: float = 0.2  # 20% drop triggers signal
    divergence_similarity_threshold: float = 0.7  # Below 70% similarity = divergence

    def __post_init__(self):
        # Crear contrato de publicación
        self.publication_contract = PublicationContract(
            contract_id=f"pub_{self.vehicle_id}",
            publisher_vehicle=self.vehicle_id,
            status=ContractStatus.ACTIVE,
            allowed_signal_types=[
                SignalTypeSpec(signal_type="DecisionDivergenceSignal"),
                SignalTypeSpec(signal_type="ConfidenceDropSignal"),
                SignalTypeSpec(signal_type="TemporalContrastSignal")
            ],
            allowed_buses=["contrast_bus"],
            require_context=True,
            require_source=True
        )
        if self.contract_registry:
            self.contract_registry.register(self.publication_contract)

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa datos y genera señales de contraste.

        Analiza:
        - Divergencias entre decisiones baseline y actuales
        - Caídas en niveles de confianza
        - Cambios temporales en estados
        """
        signals = []

        # Crear evento
        event = self.create_event(
            event_type="contrast_analysis",
            payload={"context": context.node_id},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )

        source = self.create_signal_source(event)

        # Extraer datos para análisis
        extracted_data = self._extract_contrast_data(data)

        # 1. Detectar divergencia de decisión
        if extracted_data.get("has_baseline") and extracted_data.get("has_current"):
            divergence_signal = self._detect_decision_divergence(extracted_data, context, source)
            signals.append(divergence_signal)

        # 2. Detectar caída de confianza
        if extracted_data.get("has_confidence_history"):
            confidence_signal = self._detect_confidence_drop(extracted_data, context, source)
            signals.append(confidence_signal)

        # 3. Detectar contraste temporal
        if extracted_data.get("has_temporal_data"):
            temporal_signal = self._detect_temporal_contrast(extracted_data, context, source)
            signals.append(temporal_signal)

        self.stats["signals_generated"] += len(signals)
        return signals

    def _extract_contrast_data(self, data: Any) -> Dict[str, Any]:
        """Extrae datos relevantes para análisis de contraste"""
        if not isinstance(data, dict):
            return {}

        extracted = {}

        # Verificar datos baseline vs actual
        extracted["has_baseline"] = "baseline_decision" in data or "baseline" in data
        extracted["has_current"] = "current_decision" in data or "current" in data
        extracted["baseline_decision"] = data.get("baseline_decision") or data.get("baseline", {})
        extracted["current_decision"] = data.get("current_decision") or data.get("current", {})

        # Verificar historial de confianza
        extracted["has_confidence_history"] = "confidence_history" in data or \
                                                 ("previous_confidence" in data and "current_confidence" in data)
        extracted["confidence_history"] = data.get("confidence_history", [])
        extracted["previous_confidence"] = data.get("previous_confidence")
        extracted["current_confidence"] = data.get("current_confidence")

        # Verificar datos temporales
        extracted["has_temporal_data"] = "baseline_timestamp" in data or \
                                         "baseline_state" in data
        extracted["baseline_timestamp"] = data.get("baseline_timestamp")
        extracted["current_timestamp"] = data.get("current_timestamp", datetime.utcnow().isoformat())
        extracted["baseline_state"] = data.get("baseline_state", {})
        extracted["current_state"] = data.get("current_state", data)

        # Identificador del item
        extracted["item_id"] = data.get("item_id") or context.node_id

        return extracted

    def _detect_decision_divergence(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> DecisionDivergenceSignal:
        """Detecta divergencia entre decisiones baseline y actual"""

        baseline = data.get("baseline_decision", {})
        current = data.get("current_decision", {})

        # Calcular similitud
        similarity = self._calculate_decision_similarity(baseline, current)

        # Determinar tipo de divergencia
        if similarity >= self.divergence_similarity_threshold:
            divergence_type = "NONE"
            divergence_reason = "Decisions are similar"
        elif similarity >= 0.4:
            divergence_type = "MODERATE"
            divergence_reason = "Partial divergence in decision attributes"
        else:
            divergence_type = "SIGNIFICANT"
            divergence_reason = "Major divergence in decision logic or outcome"

        # Análisis de impacto
        impact_assessment = self._assess_divergence_impact(baseline, current, divergence_type)

        return DecisionDivergenceSignal(
            context=context,
            source=source,
            item_id=data.get("item_id", context.node_id),
            divergence_type=divergence_type,
            baseline_decision=baseline,
            current_decision=current,
            divergence_reason=divergence_reason,
            similarity_score=similarity,
            impact_assessment=impact_assessment,
            confidence=SignalConfidence.HIGH if similarity < 0.5 else SignalConfidence.MEDIUM,
            rationale=f"Divergence detected: {divergence_type} (similarity: {similarity:.2f})"
        )

    def _detect_confidence_drop(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> ConfidenceDropSignal:
        """Detecta caídas en niveles de confianza"""

        item_id = data.get("item_id", context.node_id)
        history = data.get("confidence_history", [])
        previous = data.get("previous_confidence")
        current = data.get("current_confidence")

        # Determinar valores de confianza
        if history and len(history) >= 2:
            previous_confidence = history[-2]
            current_confidence = history[-1]
        elif previous is not None and current is not None:
            previous_confidence = previous
            current_confidence = current
        else:
            # No hay datos suficientes
            previous_confidence = 1.0
            current_confidence = 1.0

        # Calcular caída
        if isinstance(previous_confidence, str):
            previous_confidence = float(previous_confidence)
        if isinstance(current_confidence, str):
            current_confidence = float(current_confidence)

        drop_percentage = max(0.0, previous_confidence - current_confidence)
        drop_is_significant = drop_percentage >= self.confidence_drop_threshold

        # Factores contribuyentes
        contributing_factors = self._analyze_confidence_factors(data, drop_percentage)

        # Tendencia
        if history and len(history) >= 3:
            recent_trend = "DECLINING" if history[-1] < history[-3] else "STABLE" if abs(history[-1] - history[-3]) < 0.1 else "IMPROVING"
        else:
            recent_trend = "UNKNOWN"

        return ConfidenceDropSignal(
            context=context,
            source=source,
            item_id=item_id,
            previous_confidence=previous_confidence,
            current_confidence=current_confidence,
            drop_percentage=drop_percentage,
            contributing_factors=contributing_factors,
            recent_trend=recent_trend,
            confidence=SignalConfidence.HIGH if drop_is_significant else SignalConfidence.LOW,
            rationale=f"Confidence drop: {drop_percentage:.1%} (from {previous_confidence:.2f} to {current_confidence:.2f})"
        )

    def _detect_temporal_contrast(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> TemporalContrastSignal:
        """Detecta cambios temporales en estados"""

        item_id = data.get("item_id", context.node_id)
        baseline_timestamp = data.get("baseline_timestamp")
        current_timestamp = data.get("current_timestamp")
        baseline_state = data.get("baseline_state", {})
        current_state = data.get("current_state", {})

        # Detectar cambios
        changes_detected = self._detect_state_changes(baseline_state, current_state)

        # Categorizar cambios
        if not changes_detected:
            change_category = "NONE"
            change_magnitude = "NONE"
        elif len(changes_detected) <= 2:
            change_category = "MINOR"
            change_magnitude = "LOW"
        elif len(changes_detected) <= 5:
            change_category = "MODERATE"
            change_magnitude = "MEDIUM"
        else:
            change_category = "SIGNIFICANT"
            change_magnitude = "HIGH"

        return TemporalContrastSignal(
            context=context,
            source=source,
            item_id=item_id,
            baseline_timestamp=baseline_timestamp or datetime.utcnow().isoformat(),
            current_timestamp=current_timestamp or datetime.utcnow().isoformat(),
            baseline_state=baseline_state,
            current_state=current_state,
            changes_detected=changes_detected,
            change_category=change_category,
            change_magnitude=change_magnitude,
            confidence=SignalConfidence.HIGH if len(changes_detected) > 0 else SignalConfidence.LOW,
            rationale=f"Temporal contrast: {change_category} ({len(changes_detected)} changes detected)"
        )

    def _calculate_decision_similarity(self, baseline: Dict, current: Dict) -> float:
        """Calcula similitud entre decisiones"""
        if not baseline or not current:
            return 1.0

        # Obtener keys comunes
        common_keys = set(baseline.keys()) & set(current.keys())

        if not common_keys:
            return 0.0

        # Calcular similitud por campo
        similar_count = 0
        for key in common_keys:
            if baseline[key] == current[key]:
                similar_count += 1
            elif isinstance(baseline[key], (int, float)) and isinstance(current[key], (int, float)):
                # Para números, considerar valores cercanos como similares
                if abs(baseline[key] - current[key]) < 0.1:
                    similar_count += 1

        return similar_count / len(common_keys) if common_keys else 1.0

    def _assess_divergence_impact(self, baseline: Dict, current: Dict, divergence_type: str) -> Dict[str, Any]:
        """Evalúa el impacto de la divergencia"""
        return {
            "severity": "HIGH" if divergence_type == "SIGNIFICANT" else "MEDIUM" if divergence_type == "MODERATE" else "LOW",
            "affected_dimensions": list(set(baseline.keys()) | set(current.keys())),
            "recommendation": "Review required" if divergence_type == "SIGNIFICANT" else "Monitor"
        }

    def _analyze_confidence_factors(self, data: Dict, drop_percentage: float) -> List[str]:
        """Analiza factores que contribuyen a la caída de confianza"""
        factors = []

        if drop_percentage > 0.3:
            factors.append("Significant confidence drop detected")

        # Verificar datos integridad
        if data.get("integrity_issues"):
            factors.append("Data integrity issues detected")

        # Verificar completitud
        if data.get("missing_fields"):
            factors.append(f"Missing fields: {data.get('missing_fields', [])}")

        return factors

    def _detect_state_changes(self, baseline: Dict, current: Dict) -> List[Dict[str, Any]]:
        """Detecta cambios entre estados"""
        if not baseline or not current:
            return []

        changes = []

        # Keys en baseline que cambiaron o desaparecieron
        for key in baseline.keys():
            if key not in current:
                changes.append({
                    "type": "REMOVED",
                    "field": key,
                    "previous_value": baseline[key],
                    "current_value": None
                })
            elif baseline[key] != current[key]:
                changes.append({
                    "type": "MODIFIED",
                    "field": key,
                    "previous_value": baseline[key],
                    "current_value": current[key]
                })

        # Keys nuevas en current
        for key in current.keys():
            if key not in baseline:
                changes.append({
                    "type": "ADDED",
                    "field": key,
                    "previous_value": None,
                    "current_value": current[key]
                })

        return changes
