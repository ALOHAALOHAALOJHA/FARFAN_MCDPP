# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/contrast.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class DivergenceType(Enum):
    """Tipos de divergencia"""
    VALUE_MISMATCH = "VALUE_MISMATCH"
    CLASSIFICATION_MISMATCH = "CLASSIFICATION_MISMATCH"
    CONFIDENCE_MISMATCH = "CONFIDENCE_MISMATCH"
    STRUCTURE_MISMATCH = "STRUCTURE_MISMATCH"


class DivergenceSeverity(Enum):
    """Severidad de la divergencia"""
    CRITICAL = "CRITICAL"   # Afecta decisiones
    HIGH = "HIGH"           # Diferencia significativa
    MEDIUM = "MEDIUM"       # Diferencia notable
    LOW = "LOW"             # Diferencia menor


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
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONTRAST


@dataclass
class ConfidenceDropSignal(Signal):
    """
    Indica caída de confianza en una evaluación.
    """
    signal_type: str = field(default="ConfidenceDropSignal", init=False)
    
    item_id: str = ""
    previous_confidence: float = 0.0
    current_confidence: float = 0.0
    drop_percentage: float = 0.0
    contributing_factors: List[str] = field(default_factory=list)
    trend: str = "stable"

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONTRAST


@dataclass
class TemporalContrastSignal(Signal):
    """
    Indica cambios entre evaluaciones en diferentes momentos.
    """
    signal_type: str = field(default="TemporalContrastSignal", init=False)
    
    item_id: str = ""
    baseline_timestamp: datetime = field(default_factory=datetime.utcnow)
    current_timestamp: datetime = field(default_factory=datetime.utcnow)
    baseline_state: Dict[str, Any] = field(default_factory=dict)
    current_state: Dict[str, Any] = field(default_factory=dict)
    changes_detected: List[str] = field(default_factory=list)

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONTRAST