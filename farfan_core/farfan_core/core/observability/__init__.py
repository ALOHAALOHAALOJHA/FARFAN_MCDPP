"""Observability module for F.A.R.F.A.N runtime monitoring.

Includes both traditional logging/metrics and production OpenTelemetry integration.
"""

from farfan_core.core.observability.structured_logging import log_fallback, get_logger
from farfan_core.core.observability.metrics import (
    increment_fallback,
    increment_segmentation_method,
    increment_calibration_mode,
    increment_document_id_source,
    increment_hash_algo,
    increment_graph_metrics_skipped,
    increment_contradiction_mode,
)

try:
    from farfan_core.core.observability.opentelemetry_integration import (
        OpenTelemetryConfig,
        FARFANObservability,
        get_global_observability,
        get_tracer,
        trace_executor,
        trace_phase,
    )
    from farfan_core.core.observability.executor_instrumentation import (
        instrument_executor_class,
        auto_instrument_executors,
        EXECUTOR_NAMES,
    )
    from farfan_core.core.observability.pipeline_instrumentation import (
        instrument_phase_orchestrator,
        instrument_phase_contract,
        auto_instrument_pipeline,
        create_trace_context_carrier,
        inject_trace_context,
        PHASE_DEFINITIONS,
    )
    
    def initialize_observability(
        service_name: str = "farfan-pipeline",
        service_version: str = "1.0.0",
        enable_jaeger: bool = True,
        enable_prometheus: bool = True,
        prometheus_port: int = 9090,
        auto_instrument: bool = True,
    ) -> FARFANObservability:
        """Initialize the complete observability stack."""
        config = OpenTelemetryConfig(
            service_name=service_name,
            service_version=service_version,
            enable_jaeger=enable_jaeger,
            enable_prometheus=enable_prometheus,
            prometheus_port=prometheus_port,
        )
        
        observability = FARFANObservability(config)
        
        if auto_instrument:
            auto_instrument_executors()
            auto_instrument_pipeline()
        
        return observability
    
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    OpenTelemetryConfig = None
    FARFANObservability = None
    get_global_observability = None
    get_tracer = None
    trace_executor = None
    trace_phase = None
    instrument_executor_class = None
    auto_instrument_executors = None
    EXECUTOR_NAMES = []
    instrument_phase_orchestrator = None
    instrument_phase_contract = None
    auto_instrument_pipeline = None
    create_trace_context_carrier = None
    inject_trace_context = None
    PHASE_DEFINITIONS = []
    initialize_observability = None

__all__ = [
    "log_fallback",
    "get_logger",
    "increment_fallback",
    "increment_segmentation_method",
    "increment_calibration_mode",
    "increment_document_id_source",
    "increment_hash_algo",
    "increment_graph_metrics_skipped",
    "increment_contradiction_mode",
    "OpenTelemetryConfig",
    "FARFANObservability",
    "get_global_observability",
    "get_tracer",
    "trace_executor",
    "trace_phase",
    "instrument_executor_class",
    "auto_instrument_executors",
    "instrument_phase_orchestrator",
    "instrument_phase_contract",
    "auto_instrument_pipeline",
    "create_trace_context_carrier",
    "inject_trace_context",
    "initialize_observability",
    "EXECUTOR_NAMES",
    "PHASE_DEFINITIONS",
    "OPENTELEMETRY_AVAILABLE",
]
