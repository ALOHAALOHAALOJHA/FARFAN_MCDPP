"""FARFAN Observability - Production OpenTelemetry Stack

Complete observability solution with:
- Distributed tracing across 9-phase pipeline
- Automatic instrumentation of 30 executors
- Prometheus metrics export
- Jaeger trace export
- Context propagation

Usage:
    # Initialize observability
    from farfan_core.observability import initialize_observability
    
    initialize_observability(
        enable_jaeger=True,
        enable_prometheus=True,
        prometheus_port=9090
    )
    
    # Observability is now active across all executors and phases
"""

from farfan_core.observability.opentelemetry_integration import (
    OpenTelemetryConfig,
    FARFANObservability,
    get_global_observability,
    get_tracer,
    trace_executor,
    trace_phase,
)

from farfan_core.observability.executor_instrumentation import (
    instrument_executor_class,
    auto_instrument_executors,
    EXECUTOR_NAMES,
)

from farfan_core.observability.pipeline_instrumentation import (
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
    """Initialize the complete observability stack.
    
    Args:
        service_name: Service name for tracing
        service_version: Service version
        enable_jaeger: Enable Jaeger trace export
        enable_prometheus: Enable Prometheus metrics export
        prometheus_port: Port for Prometheus metrics server
        auto_instrument: Automatically instrument executors and pipeline
        
    Returns:
        FARFANObservability instance
    """
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


__all__ = [
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
]
