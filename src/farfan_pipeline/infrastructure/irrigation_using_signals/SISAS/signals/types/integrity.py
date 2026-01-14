# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/integrity.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class PresenceStatus(Enum):
    """Estados de presencia de evento"""
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    PARTIAL = "PARTIAL"


class CompletenessLevel(Enum):
    """Niveles de completitud"""
    COMPLETE = "COMPLETE"
    MOSTLY_COMPLETE = "MOSTLY_COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    EMPTY = "EMPTY"


@dataclass
class EventPresenceSignal(Signal):
    """
    Señal que indica si un evento esperado existe.

    Uso:  Verificar que AnswerSubmitted para Q147 existe.
    """

    signal_type: str = field(default="EventPresenceSignal", init=False)

    # Payload específico
    expected_event_type: str = ""
    presence_status: PresenceStatus = PresenceStatus.ABSENT
    event_count: int = 0
    first_occurrence:  Optional[str] = None  # timestamp ISO
    last_occurrence: Optional[str] = None

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.INTEGRITY


@dataclass
class EventCompletenessSignal(Signal):
    """
    Señal que indica qué tan completo es un evento.

    Uso:  Verificar que el evento tiene todos los campos requeridos.
    """

    signal_type: str = field(default="EventCompletenessSignal", init=False)

    # Payload específico
    completeness_level: CompletenessLevel = CompletenessLevel.EMPTY
    required_fields: List[str] = field(default_factory=list)
    present_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)

    completeness_score: float = 0.0  # 0.0 a 1.0

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.INTEGRITY

    def __post_init__(self):
        super().__post_init__()
        # Calcular campos faltantes
        self.missing_fields = [
            f for f in self.required_fields if f not in self.present_fields
        ]
        # Calcular score
        if self.required_fields:
            self.completeness_score = len(self.present_fields) / len(self.required_fields)


@dataclass
class DataIntegritySignal(Signal):
    """
    Señal que indica la integridad referencial de los datos.

    Uso: Verificar que las referencias entre archivos son válidas.
    """

    signal_type: str = field(default="DataIntegritySignal", init=False)

    # Payload específico
    source_file: str = ""
    referenced_files: List[str] = field(default_factory=list)
    valid_references: List[str] = field(default_factory=list)
    broken_references: List[str] = field(default_factory=list)

    integrity_score: float = 0.0

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.INTEGRITY
