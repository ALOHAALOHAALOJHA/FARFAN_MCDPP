# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/operational.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class ExecutionStatus(Enum):
    """Estados de ejecución"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class FailureMode(Enum):
    """Modos de falla"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TRANSFORMATION_ERROR = "TRANSFORMATION_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    UNKNOWN = "UNKNOWN"


@dataclass
class ExecutionAttemptSignal(Signal):
    """
    Señal que registra un intento de ejecución.

    Uso: Registrar que se intentó procesar Q147, incluso si falló.
    """

    signal_type: str = field(default="ExecutionAttemptSignal", init=False)

    # Payload específico
    execution_id: str = ""
    component:  str = ""  # Qué componente ejecutó
    operation: str = ""  # Qué operación

    status: ExecutionStatus = ExecutionStatus.PENDING

    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0

    input_summary: Dict[str, Any] = field(default_factory=dict)
    output_summary: Dict[str, Any] = field(default_factory=dict)

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class FailureModeSignal(Signal):
    """
    Señal que describe cómo falló una operación.

    Uso: Diagnóstico detallado de fallas.
    """

    signal_type: str = field(default="FailureModeSignal", init=False)

    # Payload específico
    execution_id: str = ""
    failure_mode: FailureMode = FailureMode.UNKNOWN

    error_message: str = ""
    error_code: str = ""
    stack_trace: str = ""

    recoverable: bool = False
    retry_count: int = 0
    max_retries: int = 3

    suggested_action: str = ""

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class LegacyActivitySignal(Signal):
    """
    Señal que registra actividad del sistema legacy.

    Uso: Observación pasiva del legacy sin intervenir (JF-0, JF-1).
    """

    signal_type:  str = field(default="LegacyActivitySignal", init=False)

    # Payload específico
    legacy_component: str = ""
    activity_type: str = ""  # "read", "write", "transform", "decision"

    input_captured: Dict[str, Any] = field(default_factory=dict)
    output_captured: Dict[str, Any] = field(default_factory=dict)

    # NO interpretamos, solo registramos
    raw_payload: str = ""

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class LegacyDependencySignal(Signal):
    """
    Señal que mapea dependencias del sistema legacy.

    Uso: Entender de qué depende el legacy antes de reemplazarlo.
    """

    signal_type: str = field(default="LegacyDependencySignal", init=False)

    # Payload específico
    legacy_component: str = ""

    upstream_dependencies: List[str] = field(default_factory=list)
    downstream_dependents: List[str] = field(default_factory=list)

    data_dependencies: List[str] = field(default_factory=list)
    service_dependencies: List[str] = field(default_factory=list)

    criticality:  str = ""  # "critical", "important", "optional"

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL
