# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase1/phase1_13_00_cpp_ingestion.py

from dataclasses import dataclass
from typing import Any, Dict

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase1CppIngestionConsumer(BaseConsumer):
    """
    Consumidor para CPP (Canonical Pattern Processing) ingestion en Phase 1.

    Procesa señales relacionadas con ingestión de:
    - Corpus empírico
    - Membership criteria
    - Patterns canónicos

    Responsabilidad: Validar que la ingestión de datos canónicos
    cumple con los estándares de calidad requeridos.
    """

    consumer_id: str = "phase1_13_00_cpp_ingestion.py"
    consumer_phase: str = "phase_1"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE1_CPP_INGESTION",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "EventCompletenessSignal",
                "DataIntegritySignal",
                "ExecutionAttemptSignal",
                "FailureModeSignal"
            ],
            subscribed_buses=["integrity_bus", "operational_bus"],
            context_filters={
                "phase": ["phase_1"],
                "consumer_scope": ["Phase_1"]
            },
            required_capabilities=["can_load", "can_validate"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales de ingestión CPP.

        Enfoque: Monitorear calidad de ingestión
        - Completitud de datos
        - Integridad referencial
        - Estado de ejecución
        - Modos de falla
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "ingestion_analysis": {},
            "ingestion_status": "UNKNOWN"
        }

        if signal.signal_type == "EventCompletenessSignal":
            analysis = self._analyze_ingestion_completeness(signal)
            result["ingestion_analysis"] = analysis
            result["ingestion_status"] = analysis.get("status", "UNKNOWN")

        elif signal.signal_type == "DataIntegritySignal":
            analysis = self._analyze_ingestion_integrity(signal)
            result["ingestion_analysis"] = analysis
            result["ingestion_status"] = analysis.get("status", "UNKNOWN")

        elif signal.signal_type == "ExecutionAttemptSignal":
            analysis = self._analyze_execution(signal)
            result["ingestion_analysis"] = analysis
            result["ingestion_status"] = str(analysis.get("execution_status", "UNKNOWN"))

        elif signal.signal_type == "FailureModeSignal":
            analysis = self._analyze_failure(signal)
            result["ingestion_analysis"] = analysis
            result["ingestion_status"] = "FAILED"

        return result

    def _analyze_ingestion_completeness(self, signal: Signal) -> Dict[str, Any]:
        """Analiza completitud de la ingestión"""
        completeness_level = str(getattr(signal, 'completeness_level', 'UNKNOWN'))
        score = getattr(signal, 'completeness_score', 0.0)
        missing = getattr(signal, 'missing_fields', [])

        status = "COMPLETE" if score >= 0.9 else "INCOMPLETE" if score >= 0.5 else "POOR"

        recommendations = []
        if missing:
            recommendations.append(f"Add missing fields: {', '.join(missing[:3])}")
        if score < 0.7:
            recommendations.append("Review ingestion pipeline for data quality issues")

        return {
            "status": status,
            "completeness_level": completeness_level,
            "completeness_score": score,
            "required_fields": getattr(signal, 'required_fields', []),
            "present_fields": getattr(signal, 'present_fields', []),
            "missing_fields": missing,
            "missing_count": len(missing),
            "recommendations": recommendations
        }

    def _analyze_ingestion_integrity(self, signal: Signal) -> Dict[str, Any]:
        """Analiza integridad de la ingestión"""
        score = getattr(signal, 'integrity_score', 0.0)
        broken = getattr(signal, 'broken_references', [])

        status = "VALID" if score >= 0.95 else "WARNING" if score >= 0.7 else "INVALID"

        return {
            "status": status,
            "integrity_score": score,
            "source_file": getattr(signal, 'source_file', ''),
            "referenced_files": getattr(signal, 'referenced_files', []),
            "valid_references": getattr(signal, 'valid_references', []),
            "broken_references": broken,
            "broken_count": len(broken),
            "recommendation": "Fix broken references before proceeding" if broken else "Integrity OK"
        }

    def _analyze_execution(self, signal: Signal) -> Dict[str, Any]:
        """Analiza ejecución de ingestión"""
        status = str(getattr(signal, 'status', 'UNKNOWN'))
        duration = getattr(signal, 'duration_ms', 0.0)
        component = getattr(signal, 'component', '')
        operation = getattr(signal, 'operation', '')

        insights = []
        if "COMPLETED" in status:
            insights.append("Ingestion completed successfully")
        elif "FAILED" in status:
            insights.append("Ingestion failed - check logs")
        elif "TIMEOUT" in status:
            insights.append(f"Ingestion timed out after {duration:.0f}ms")

        if duration > 5000:
            insights.append(f"Slow ingestion ({duration:.0f}ms) - consider optimization")

        return {
            "execution_status": status,
            "component": component,
            "operation": operation,
            "duration_ms": duration,
            "started_at": getattr(signal, 'started_at', None),
            "completed_at": getattr(signal, 'completed_at', None),
            "insights": insights
        }

    def _analyze_failure(self, signal: Signal) -> Dict[str, Any]:
        """Analiza modo de falla"""
        failure_mode = str(getattr(signal, 'failure_mode', 'UNKNOWN'))
        recoverable = getattr(signal, 'recoverable', False)
        retry_count = getattr(signal, 'retry_count', 0)
        max_retries = getattr(signal, 'max_retries', 0)
        error_msg = getattr(signal, 'error_message', '')

        severity = "RECOVERABLE" if recoverable else "CRITICAL"

        recommendations = [getattr(signal, 'suggested_action', 'Review logs')]
        if recoverable and retry_count < max_retries:
            recommendations.append(f"Retry possible ({retry_count}/{max_retries} attempts)")
        if "VALIDATION_ERROR" in failure_mode:
            recommendations.append("Fix data validation issues")
        elif "CONNECTION_ERROR" in failure_mode:
            recommendations.append("Check network/service connectivity")

        return {
            "severity": severity,
            "failure_mode": failure_mode,
            "recoverable": recoverable,
            "retry_count": retry_count,
            "max_retries": max_retries,
            "error_message": error_msg,
            "error_code": getattr(signal, 'error_code', ''),
            "recommendations": recommendations
        }
