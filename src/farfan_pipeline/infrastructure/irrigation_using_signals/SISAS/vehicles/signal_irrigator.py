# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_irrigator.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..signals.types.operational import (
    ExecutionAttemptSignal,
    ExecutionStatus,
    FailureModeSignal,
    FailureMode
)


@dataclass
class SignalIrrigatorVehicle(BaseVehicle):
    """
    Vehículo: signal_irrigator
    
    Responsabilidad: Ejecutar operaciones de irrigación, coordinando el flujo
    de señales a través del sistema y gestionando la ejecución de rutas.
    
    Capacidades: can_irrigate=True (único vehículo con esta capacidad)
    
    Señales que produce:
    - ExecutionAttemptSignal
    - FailureModeSignal (en caso de fallas)
    """
    
    vehicle_id: str = field(default="signal_irrigator")
    vehicle_name: str = field(default="Signal Irrigator Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=False,
        can_validate=False,
        can_irrigate=True,
        signal_types_produced=[
            "ExecutionAttemptSignal",
            "FailureModeSignal"
        ]
    ))
    
    # Estado de irrigación
    active_irrigations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    completed_irrigations: List[str] = field(default_factory=list)
    failed_irrigations: List[str] = field(default_factory=list)

    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa una solicitud de irrigación.
        """
        signals = []
        
        # Crear evento de intento de ejecución
        execution_id = f"irrigation_{context.node_id}_{datetime.utcnow().isoformat()}"
        
        event = self.create_event(
            event_type="signal_generated",
            payload={"execution_id": execution_id, "operation": "irrigate"},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # Ejecutar irrigación
        started_at = datetime.utcnow().isoformat()
        status, duration_ms, error = self._execute_irrigation(execution_id, data, context)
        completed_at = datetime.utcnow().isoformat()
        
        # 1. Señal de intento de ejecución
        execution_signal = ExecutionAttemptSignal(
            context=context,
            source=source,
            execution_id=execution_id,
            component=self.vehicle_id,
            operation="irrigate",
            status=status,
            started_at=started_at,
            completed_at=completed_at if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED] else None,
            duration_ms=duration_ms,
            input_summary={"data_keys": list(data.keys()) if isinstance(data, dict) else []},
            output_summary={"status": status.value},
            retry_count=0,
            resources_used={"memory_mb": 10.0, "cpu_percent": 5.0},
            confidence=SignalConfidence.HIGH,
            rationale=f"Irrigation execution: {status.value}, duration: {duration_ms}ms"
        )
        signals.append(execution_signal)
        
        # 2. Señal de falla (si aplica)
        if status == ExecutionStatus.FAILED and error:
            failure_signal = FailureModeSignal(
                context=context,
                source=source,
                execution_id=execution_id,
                failure_mode=error.get("mode", FailureMode.UNKNOWN),
                error_message=error.get("message", "Unknown error"),
                error_code=error.get("code", "ERR_UNKNOWN"),
                stack_trace=error.get("trace", ""),
                recoverable=error.get("recoverable", True),
                retry_count=0,
                max_retries=3,
                suggested_action=error.get("suggested_action", "Review irrigation configuration"),
                recovery_attempted=False,
                recovery_successful=False,
                failure_impact="medium",
                confidence=SignalConfidence.HIGH,
                rationale=f"Irrigation failed: {error.get('message', 'Unknown error')}"
            )
            signals.append(failure_signal)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _execute_irrigation(
        self,
        execution_id: str,
        data: Dict[str, Any],
        context: SignalContext
    ) -> tuple[ExecutionStatus, float, Optional[Dict[str, Any]]]:
        """
        Ejecuta la irrigación y retorna (status, duration_ms, error_info)
        """
        start_time = datetime.utcnow()
        
        try:
            # Registrar irrigación activa
            self.active_irrigations[execution_id] = {
                "context": context,
                "started_at": start_time,
                "status": "running"
            }
            
            # Simular ejecución de irrigación
            # En producción, aquí se coordinaría con irrigation_executor
            
            # Validar datos mínimos
            if not data or not isinstance(data, dict):
                raise ValueError("Invalid irrigation data")
            
            # Marcar como completado
            self.active_irrigations[execution_id]["status"] = "completed"
            self.completed_irrigations.append(execution_id)
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ExecutionStatus.COMPLETED, duration_ms, None
            
        except Exception as e:
            # Marcar como fallido
            if execution_id in self.active_irrigations:
                self.active_irrigations[execution_id]["status"] = "failed"
            self.failed_irrigations.append(execution_id)
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            error_info = {
                "mode": FailureMode.VALIDATION_ERROR,
                "message": str(e),
                "code": "ERR_IRRIGATION_FAILED",
                "trace": "",
                "recoverable": True,
                "suggested_action": "Validate irrigation data and retry"
            }
            
            return ExecutionStatus.FAILED, duration_ms, error_info
    
    def get_irrigation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de irrigación"""
        return {
            "active_count": len(self.active_irrigations),
            "completed_count": len(self.completed_irrigations),
            "failed_count": len(self.failed_irrigations),
            "success_rate": len(self.completed_irrigations) / max(1, len(self.completed_irrigations) + len(self.failed_irrigations))
        }
