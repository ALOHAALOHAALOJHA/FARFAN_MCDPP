# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/contrast.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class DivergenceType(Enum):
    """Tipos de divergencia"""
    VALUE_MISMATCH = "VALUE_MISMATCH"
    CLASSIFICATION_MISMATCH = "CLASSIFICATION_MISMATCH"
    CONFIDENCE_MISMATCH = "CONFIDENCE_MISMATCH"
    STRUCTURE_MISMATCH = "STRUCTURE_MISMATCH"
    LOGIC_MISMATCH = "LOGIC_MISMATCH"


class DivergenceSeverity(Enum):
    """Severidad de la divergencia"""
    CRITICAL = "CRITICAL"   # Afecta decisiones
    HIGH = "HIGH"           # Diferencia significativa
    MEDIUM = "MEDIUM"       # Diferencia notable
    LOW = "LOW"             # Diferencia menor
    NEGLIGIBLE = "NEGLIGIBLE"  # Insignificante


class TrendDirection(Enum):
    """Dirección de tendencia"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


@dataclass
class DecisionDivergenceSignal(Signal):
    """
    Señal que indica divergencia entre sistema legacy y nuevo.

    Uso: Comparar output legacy "COMPLIANT" vs señales "INDETERMINATE"
    """

    signal_type: str = field(default="DecisionDivergenceSignal", init=False)

    # Payload específico
    item_id: str = ""  # Q147, PA03, etc.

    # Valores comparados
    legacy_value: Any = None
    legacy_source: str = ""

    signal_based_value: Any = None
    supporting_signals: List[str] = field(default_factory=list)

    # Análisis de divergencia
    divergence_type: DivergenceType = DivergenceType.VALUE_MISMATCH
    divergence_severity: DivergenceSeverity = DivergenceSeverity.MEDIUM
    divergence_explanation: str = ""

    # Recomendación (NO imperativa)
    suggested_investigation: str = ""
    investigation_priority: str = "medium"  # low, medium, high, critical
    
    # Métricas de divergencia
    divergence_magnitude: float = 0.0  # 0.0-1.0
    confidence_in_analysis: float = 0.0

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONTRAST

    def compute_divergence_score(self) -> float:
        """Calcula score de divergencia"""
        severity_scores = {
            DivergenceSeverity.CRITICAL: 1.0,
            DivergenceSeverity.HIGH: 0.75,
            DivergenceSeverity.MEDIUM: 0.5,
            DivergenceSeverity.LOW: 0.25,
            DivergenceSeverity.NEGLIGIBLE: 0.1
        }
        return severity_scores.get(self.divergence_severity, 0.5)

    def get_comparison_report(self) -> Dict[str, Any]:
        """Reporte completo de comparación"""
        return {
            "item_id": self.item_id,
            "divergence_type": self.divergence_type.value,
            "divergence_severity": self.divergence_severity.value,
            "divergence_score": self.compute_divergence_score(),
            "legacy_value": self.legacy_value,
            "signal_based_value": self.signal_based_value,
            "supporting_signals_count": len(self.supporting_signals),
            "requires_investigation": self.requires_investigation(),
            "investigation_priority": self.investigation_priority
        }

    def requires_investigation(self) -> bool:
        """Determina si requiere investigación"""
        return self.divergence_severity in [
            DivergenceSeverity.CRITICAL,
            DivergenceSeverity.HIGH
        ]

    def get_reconciliation_suggestions(self) -> List[str]:
        """Sugerencias para reconciliar diferencias"""
        suggestions = []
        
        if self.divergence_type == DivergenceType.VALUE_MISMATCH:
            suggestions.append("Review data sources for both systems")
            suggestions.append("Verify calculation methods")
        elif self.divergence_type == DivergenceType.CLASSIFICATION_MISMATCH:
            suggestions.append("Align classification criteria")
            suggestions.append("Review edge cases")
        elif self.divergence_type == DivergenceType.CONFIDENCE_MISMATCH:
            suggestions.append("Calibrate confidence models")
        
        return suggestions


@dataclass
class ConfidenceDropSignal(Signal):
    """
    Señal que indica caída de confianza en una evaluación.

    Uso: Detectar cuando las señales sugieren menor confianza que antes.
    """

    signal_type: str = field(default="ConfidenceDropSignal", init=False)

    # Payload específico
    item_id: str = ""

    previous_confidence: float = 0.0
    current_confidence: float = 0.0
    drop_percentage: float = 0.0

    contributing_factors: List[str] = field(default_factory=list)
    # ["new_ambiguity_detected", "reference_invalidated", "scope_change"]

    trend:  TrendDirection = TrendDirection.DECLINING
    
    # Análisis adicional
    historical_confidence: List[float] = field(default_factory=list)
    trend_stability: float = 0.0  # 0.0-1.0

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONTRAST

    def is_significant_drop(self) -> bool:
        """Verifica si la caída es significativa"""
        return self.drop_percentage > 20  # Más de 20% de caída

    def get_trend_analysis(self) -> Dict[str, Any]:
        """Análisis de tendencia"""
        return {
            "item_id": self.item_id,
            "previous_confidence": self.previous_confidence,
            "current_confidence": self.current_confidence,
            "drop_percentage": self.drop_percentage,
            "trend": self.trend.value,
            "is_significant": self.is_significant_drop(),
            "factors_count": len(self.contributing_factors),
            "primary_factor": self.contributing_factors[0] if self.contributing_factors else "unknown",
            "trend_stability": self.trend_stability,
            "requires_attention": self.requires_attention()
        }

    def requires_attention(self) -> bool:
        """Determina si requiere atención inmediata"""
        return (
            self.is_significant_drop() or
            self.trend == TrendDirection.DECLINING or
            self.current_confidence < 0.5
        )

    def get_recovery_recommendations(self) -> List[str]:
        """Recomendaciones para recuperar confianza"""
        recommendations = []
        
        for factor in self.contributing_factors:
            if "ambiguity" in factor.lower():
                recommendations.append("Clarify ambiguous elements")
            elif "reference" in factor.lower():
                recommendations.append("Update or verify references")
            elif "scope" in factor.lower():
                recommendations.append("Redefine scope boundaries")
        
        if not recommendations:
            recommendations.append("Conduct comprehensive review")
        
        return recommendations


@dataclass
class TemporalContrastSignal(Signal):
    """
    Señal que indica cambios entre evaluaciones en diferentes momentos.

    Uso: Tracking de evolución de respuestas/evaluaciones.
    """

    signal_type: str = field(default="TemporalContrastSignal", init=False)

    # Payload específico
    item_id: str = ""

    baseline_timestamp: str = ""
    current_timestamp: str = ""

    baseline_state: Dict[str, Any] = field(default_factory=dict)
    current_state: Dict[str, Any] = field(default_factory=dict)

    changes_detected: List[Dict[str, Any]] = field(default_factory=list)
    # [{"field": "score", "old": 0.7, "new": 0.5, "delta": -0.2}]

    stability_score: float = 0.0  # 1.0 = sin cambios, 0.0 = cambio total
    
    # Análisis temporal
    time_delta_days: float = 0.0
    change_velocity: float = 0.0  # Velocidad de cambio por día

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONTRAST

    def __post_init__(self):
        super().__post_init__()
        # Calcular delta temporal
        if self.baseline_timestamp and self.current_timestamp:
            try:
                baseline_dt = datetime.fromisoformat(self.baseline_timestamp.replace('Z', '+00:00'))
                current_dt = datetime.fromisoformat(self.current_timestamp.replace('Z', '+00:00'))
                self.time_delta_days = (current_dt - baseline_dt).days
            except:
                self.time_delta_days = 0.0
        
        # Calcular velocidad de cambio
        if self.time_delta_days > 0 and len(self.changes_detected) > 0:
            self.change_velocity = len(self.changes_detected) / self.time_delta_days

    def get_temporal_analysis(self) -> Dict[str, Any]:
        """Análisis temporal completo"""
        return {
            "item_id": self.item_id,
            "time_span_days": self.time_delta_days,
            "stability_score": self.stability_score,
            "changes_count": len(self.changes_detected),
            "change_velocity": self.change_velocity,
            "is_stable": self.is_stable(),
            "trend_category": self.get_trend_category(),
            "significant_changes": self.get_significant_changes()
        }

    def is_stable(self) -> bool:
        """Verifica si es estable"""
        return self.stability_score > 0.8

    def get_trend_category(self) -> str:
        """Categoriza la tendencia"""
        if self.stability_score > 0.9:
            return "very_stable"
        elif self.stability_score > 0.7:
            return "stable"
        elif self.stability_score > 0.5:
            return "moderately_changing"
        elif self.stability_score > 0.3:
            return "rapidly_changing"
        return "highly_volatile"

    def get_significant_changes(self, threshold: float = 0.2) -> List[Dict[str, Any]]:
        """Retorna cambios significativos"""
        return [
            change for change in self.changes_detected
            if abs(change.get("delta", 0)) > threshold
        ]

    def needs_stabilization(self) -> bool:
        """Determina si necesita estabilización"""
        return self.stability_score < 0.6 or self.change_velocity > 0.5
