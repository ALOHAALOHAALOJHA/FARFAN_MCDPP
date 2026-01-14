# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase2/phase2_factory_consumer.py

from dataclasses import dataclass
from typing import Any, Dict

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase2FactoryConsumer(BaseConsumer):
    """
    Consumidor para factory pattern en Phase 2.

    Consolidates signals from:
    - phase2_10_00_factory.py
    - phase2_30_03_resource_aware_executor.py
    - phase2_40_03_irrigation_synchronizer.py

    Responsabilidad: Monitorear la creación y ejecución de componentes
    en Phase 2, validando que los patrones factory funcionan correctamente.
    """

    consumer_id: str = "phase2_factory_consumer.py"
    consumer_phase: str = "phase_2"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE2_FACTORY",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "ExecutionAttemptSignal",
                "FailureModeSignal",
                "FrequencySignal",
                "ConsumerHealthSignal"
            ],
            subscribed_buses=["operational_bus", "consumption_bus"],
            context_filters={
                "phase": ["phase_2"],
                "consumer_scope": ["Phase_2"]
            },
            required_capabilities=["can_transform", "can_validate"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales relacionadas con factory patterns en Phase 2.

        Enfoque:
        - Monitorear ejecuciones de factory
        - Validar resource awareness
        - Sincronización de irrigación
        - Salud de componentes
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "factory_analysis": {},
            "health_status": "UNKNOWN"
        }

        if signal.signal_type == "ExecutionAttemptSignal":
            analysis = self._analyze_factory_execution(signal)
            result["factory_analysis"] = analysis
            result["health_status"] = analysis.get("status", "UNKNOWN")

        elif signal.signal_type == "FailureModeSignal":
            analysis = self._analyze_factory_failure(signal)
            result["factory_analysis"] = analysis
            result["health_status"] = "UNHEALTHY"

        elif signal.signal_type == "FrequencySignal":
            analysis = self._analyze_factory_usage(signal)
            result["factory_analysis"] = analysis

        elif signal.signal_type == "ConsumerHealthSignal":
            analysis = self._analyze_consumer_health(signal)
            result["factory_analysis"] = analysis
            result["health_status"] = analysis.get("health_status", "UNKNOWN")

        return result

    def _analyze_factory_execution(self, signal: Signal) -> Dict[str, Any]:
        """Analiza ejecución de factory"""
        status = str(getattr(signal, 'status', 'UNKNOWN'))
        duration = getattr(signal, 'duration_ms', 0.0)
        component = getattr(signal, 'component', '')

        performance_rating = "EXCELLENT" if duration < 100 else "GOOD" if duration < 500 else "SLOW"

        return {
            "status": status,
            "component": component,
            "operation": getattr(signal, 'operation', ''),
            "duration_ms": duration,
            "performance_rating": performance_rating,
            "started_at": getattr(signal, 'started_at', None),
            "completed_at": getattr(signal, 'completed_at', None)
        }

    def _analyze_factory_failure(self, signal: Signal) -> Dict[str, Any]:
        """Analiza fallas en factory"""
        failure_mode = str(getattr(signal, 'failure_mode', 'UNKNOWN'))
        recoverable = getattr(signal, 'recoverable', False)

        return {
            "failure_mode": failure_mode,
            "recoverable": recoverable,
            "error_message": getattr(signal, 'error_message', ''),
            "suggested_action": getattr(signal, 'suggested_action', ''),
            "retry_count": getattr(signal, 'retry_count', 0)
        }

    def _analyze_factory_usage(self, signal: Signal) -> Dict[str, Any]:
        """Analiza frecuencia de uso de factory"""
        count = getattr(signal, 'access_count', 0)
        pattern = getattr(signal, 'access_pattern', '')

        return {
            "access_count": count,
            "access_pattern": pattern,
            "resource_id": getattr(signal, 'resource_id', ''),
            "period_start": getattr(signal, 'period_start', ''),
            "period_end": getattr(signal, 'period_end', ''),
            "consumers_accessing": getattr(signal, 'consumers_accessing', [])
        }

    def _analyze_consumer_health(self, signal: Signal) -> Dict[str, Any]:
        """Analiza salud de consumidores"""
        health = getattr(signal, 'health_status', 'unknown')
        error_rate = getattr(signal, 'error_rate', 0.0)

        return {
            "health_status": health,
            "consumer_id": getattr(signal, 'consumer_id', ''),
            "signals_received": getattr(signal, 'signals_received', 0),
            "signals_processed": getattr(signal, 'signals_processed', 0),
            "signals_failed": getattr(signal, 'signals_failed', 0),
            "error_rate": error_rate,
            "avg_processing_time_ms": getattr(signal, 'avg_processing_time_ms', 0.0)
        }
