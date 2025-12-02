"""Pipeline-wide distributed tracing for the 9-phase FARFAN pipeline.

This module instruments the PhaseOrchestrator and individual phases with
OpenTelemetry tracing to provide end-to-end visibility across the entire
pipeline execution.
"""

import logging
from typing import Any, Optional
from functools import wraps

from farfan_core.observability.opentelemetry_integration import (
    get_global_observability,
    trace_phase,
)

logger = logging.getLogger(__name__)

PHASE_DEFINITIONS = [
    ("input_validation", 0),
    ("spc_ingestion", 1),
    ("phase1_to_phase2_adapter", 2),
    ("microquestions", 3),
    ("aggregation", 4),
    ("scoring", 5),
    ("recommendation", 6),
    ("visualization", 7),
    ("export", 8),
]


def instrument_phase_orchestrator(orchestrator_class: type) -> type:
    """Instrument PhaseOrchestrator with distributed tracing.
    
    Args:
        orchestrator_class: The PhaseOrchestrator class
        
    Returns:
        Instrumented class
    """
    if not hasattr(orchestrator_class, "run_pipeline"):
        logger.warning("PhaseOrchestrator missing run_pipeline method")
        return orchestrator_class
    
    original_run_pipeline = orchestrator_class.run_pipeline
    
    @wraps(original_run_pipeline)
    async def traced_run_pipeline(self, *args, **kwargs):
        obs = get_global_observability()
        
        with obs.start_span(
            "pipeline.full_execution",
            attributes={
                "pipeline.type": "farfan_9_phase",
                "pipeline.version": "1.0.0",
            }
        ) as root_span:
            try:
                result = await original_run_pipeline(self, *args, **kwargs)
                
                if root_span and hasattr(result, "success"):
                    root_span.set_attribute("pipeline.success", result.success)
                    root_span.set_attribute("pipeline.phases_completed", result.phases_completed)
                    if hasattr(result, "total_duration_ms"):
                        root_span.set_attribute("pipeline.total_duration_ms", result.total_duration_ms)
                
                return result
            except Exception as e:
                if root_span:
                    root_span.record_exception(e)
                raise
    
    orchestrator_class.run_pipeline = traced_run_pipeline
    logger.info("Instrumented PhaseOrchestrator.run_pipeline")
    
    return orchestrator_class


def instrument_phase_contract(contract_class: type, phase_name: str, phase_number: int) -> type:
    """Instrument a phase contract with tracing.
    
    Args:
        contract_class: The phase contract class
        phase_name: Name of the phase
        phase_number: Phase number
        
    Returns:
        Instrumented class
    """
    if not hasattr(contract_class, "run"):
        return contract_class
    
    original_run = contract_class.run
    
    @wraps(original_run)
    async def traced_run(self, *args, **kwargs):
        decorator = trace_phase(phase_name, phase_number)
        wrapped = decorator(original_run)
        return await wrapped(self, *args, **kwargs)
    
    contract_class.run = traced_run
    logger.debug(f"Instrumented phase contract: {phase_name} (Phase {phase_number})")
    
    return contract_class


def auto_instrument_pipeline() -> None:
    """Automatically instrument the entire pipeline with distributed tracing.
    
    This includes:
    - PhaseOrchestrator.run_pipeline
    - All phase contracts (Phase0, Phase1, Adapter, etc.)
    - Context propagation between phases
    """
    instrumented = []
    
    try:
        from farfan_core.core.phases.phase_orchestrator import PhaseOrchestrator
        instrument_phase_orchestrator(PhaseOrchestrator)
        instrumented.append("PhaseOrchestrator")
    except Exception as e:
        logger.warning(f"Failed to instrument PhaseOrchestrator: {e}")
    
    try:
        from farfan_core.core.phases.phase0_input_validation import Phase0ValidationContract
        instrument_phase_contract(Phase0ValidationContract, "input_validation", 0)
        instrumented.append("Phase0ValidationContract")
    except Exception as e:
        logger.warning(f"Failed to instrument Phase0: {e}")
    
    try:
        from farfan_core.core.phases.phase1_spc_ingestion import Phase1SPCIngestionContract
        instrument_phase_contract(Phase1SPCIngestionContract, "spc_ingestion", 1)
        instrumented.append("Phase1SPCIngestionContract")
    except Exception as e:
        logger.warning(f"Failed to instrument Phase1: {e}")
    
    try:
        from farfan_core.core.phases.phase1_to_phase2_adapter import AdapterContract
        instrument_phase_contract(AdapterContract, "phase1_to_phase2_adapter", 2)
        instrumented.append("AdapterContract")
    except Exception as e:
        logger.warning(f"Failed to instrument Adapter: {e}")
    
    logger.info(f"Auto-instrumented pipeline components: {', '.join(instrumented)}")


def create_trace_context_carrier(run_id: str, phase: str) -> dict[str, str]:
    """Create a trace context carrier for cross-phase propagation.
    
    Args:
        run_id: Pipeline run identifier
        phase: Current phase name
        
    Returns:
        Dictionary with trace context
    """
    obs = get_global_observability()
    carrier = obs.propagate_context()
    carrier["run_id"] = run_id
    carrier["phase"] = phase
    return carrier


def inject_trace_context(carrier: dict[str, str]) -> None:
    """Inject trace context from carrier.
    
    Args:
        carrier: Dictionary with trace context
    """
    obs = get_global_observability()
    obs.inject_context(carrier)


__all__ = [
    "instrument_phase_orchestrator",
    "instrument_phase_contract",
    "auto_instrument_pipeline",
    "create_trace_context_carrier",
    "inject_trace_context",
    "PHASE_DEFINITIONS",
]
