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
    
    # Métricas adicionales
    retry_count: int = 0
    resources_used: Dict[str, float] = field(default_factory=dict)
    # {"cpu_percent": 45.2, "memory_mb": 128.5}

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL

    def is_successful(self) -> bool:
        """Verifica si fue exitoso"""
        return self.status == ExecutionStatus.COMPLETED

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Métricas de performance"""
        return {
            "execution_id": self.execution_id,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
            "performance_category": self._categorize_performance(),
            "resource_usage": self.resources_used,
            "was_successful": self.is_successful()
        }

    def _categorize_performance(self) -> str:
        """Categoriza el performance"""
        if self.duration_ms < 100:
            return "excellent"
        elif self.duration_ms < 500:
            return "good"
        elif self.duration_ms < 2000:
            return "acceptable"
        elif self.duration_ms < 5000:
            return "slow"
        return "very_slow"

    def requires_optimization(self) -> bool:
        """Determina si requiere optimización"""
        return (
            self.duration_ms > 2000 or
            self.retry_count > 2 or
            self.resources_used.get("cpu_percent", 0) > 80
        )


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
    
    # Análisis de recuperación
    recovery_attempted: bool = False
    recovery_successful: bool = False
    failure_impact: str = "low"  # low, medium, high, critical

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL

    def should_retry(self) -> bool:
        """Determina si debe reintentar"""
        return (
            self.recoverable and
            self.retry_count < self.max_retries and
            self.failure_mode not in [
                FailureMode.CONTRACT_VIOLATION,
                FailureMode.VALIDATION_ERROR
            ]
        )

    def get_failure_analysis(self) -> Dict[str, Any]:
        """Análisis detallado de falla"""
        return {
            "execution_id": self.execution_id,
            "failure_mode": self.failure_mode.value,
            "is_recoverable": self.recoverable,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "should_retry": self.should_retry(),
            "failure_impact": self.failure_impact,
            "has_recovery_plan": bool(self.suggested_action),
            "recovery_status": {
                "attempted": self.recovery_attempted,
                "successful": self.recovery_successful
            }
        }

    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Información para diagnóstico"""
        return {
            "error_message": self.error_message,
            "error_code": self.error_code,
            "failure_mode": self.failure_mode.value,
            "suggested_action": self.suggested_action,
            "has_stack_trace": bool(self.stack_trace)
        }

    def is_critical_failure(self) -> bool:
        """Verifica si es falla crítica"""
        return (
            self.failure_impact == "critical" or
            not self.recoverable or
            self.retry_count >= self.max_retries
        )


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
    
    # Metadatos de observación
    observation_timestamp: Optional[str] = None
    observation_method: str = ""  # "passive_monitoring", "active_probing"

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL

    def get_activity_summary(self) -> Dict[str, Any]:
        """Resumen de actividad legacy"""
        return {
            "legacy_component": self.legacy_component,
            "activity_type": self.activity_type,
            "has_input": bool(self.input_captured),
            "has_output": bool(self.output_captured),
            "observation_method": self.observation_method,
            "payload_size": len(self.raw_payload) if self.raw_payload else 0
        }

    def extract_key_patterns(self) -> Dict[str, Any]:
        """Extrae patrones clave sin interpretar"""
        # Solo estructura, no semántica
        return {
            "input_structure": list(self.input_captured.keys()) if self.input_captured else [],
            "output_structure": list(self.output_captured.keys()) if self.output_captured else [],
            "interaction_type": self.activity_type
        }


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
    
    # Análisis de impacto
    replacement_readiness: float = 0.0  # 0.0-1.0
    migration_complexity: str = "unknown"  # low, medium, high, unknown

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL

    def get_dependency_map(self) -> Dict[str, Any]:
        """Mapa completo de dependencias"""
        return {
            "component": self.legacy_component,
            "criticality": self.criticality,
            "dependencies": {
                "upstream_count": len(self.upstream_dependencies),
                "downstream_count": len(self.downstream_dependents),
                "data_count": len(self.data_dependencies),
                "service_count": len(self.service_dependencies)
            },
            "total_dependencies": (
                len(self.upstream_dependencies) +
                len(self.downstream_dependents) +
                len(self.data_dependencies) +
                len(self.service_dependencies)
            ),
            "replacement_readiness": self.replacement_readiness,
            "migration_complexity": self.migration_complexity
        }

    def is_migration_ready(self) -> bool:
        """Determina si está listo para migración"""
        return (
            self.replacement_readiness > 0.7 and
            self.migration_complexity in ["low", "medium"]
        )

    def get_migration_blockers(self) -> List[str]:
        """Identifica bloqueadores de migración"""
        blockers = []
        
        if self.criticality == "critical":
            blockers.append("Critical component - requires careful planning")
        
        if len(self.downstream_dependents) > 5:
            blockers.append(f"High downstream dependency count: {len(self.downstream_dependents)}")
        
        if self.migration_complexity == "high":
            blockers.append("High migration complexity")
        
        if self.replacement_readiness < 0.5:
            blockers.append("Replacement not ready")
        
        return blockers

    def get_migration_priority(self) -> int:
        """Calcula prioridad de migración (1-10)"""
        priority = 5  # Base
        
        if self.criticality == "optional":
            priority -= 2
        elif self.criticality == "critical":
            priority += 2
        
        if self.replacement_readiness > 0.8:
            priority += 2
        elif self.replacement_readiness < 0.3:
            priority -= 2
        
        if self.migration_complexity == "low":
            priority += 1
        elif self.migration_complexity == "high":
            priority -= 1
        
        return max(1, min(10, priority))
