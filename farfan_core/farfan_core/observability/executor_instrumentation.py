"""Automatic instrumentation of all 30 FARFAN executors with OpenTelemetry.

This module provides automatic tracing integration for all executor classes
without modifying their source code.
"""

import logging
from typing import Any, Callable
from functools import wraps

from farfan_core.observability.opentelemetry_integration import (
    get_global_observability,
    trace_executor,
)

logger = logging.getLogger(__name__)

EXECUTOR_NAMES = [
    "D1_Q1_QuantitativeBaselineExtractor",
    "D1_Q2_ProblemDimensioningAnalyzer",
    "D1_Q3_BudgetAllocationTracer",
    "D1_Q4_InstitutionalCapacityIdentifier",
    "D1_Q5_ScopeJustificationValidator",
    "D2_Q1_StructuredPlanningValidator",
    "D2_Q2_InterventionLogicInferencer",
    "D2_Q3_RootCauseLinkageAnalyzer",
    "D2_Q4_RiskManagementAnalyzer",
    "D2_Q5_StrategicCoherenceEvaluator",
    "D3_Q1_IndicatorQualityValidator",
    "D3_Q2_TargetProportionalityAnalyzer",
    "D3_Q3_TraceabilityValidator",
    "D3_Q4_TechnicalFeasibilityEvaluator",
    "D3_Q5_OutputOutcomeLinkageAnalyzer",
    "D4_Q1_OutcomeMetricsValidator",
    "D4_Q2_CausalChainValidator",
    "D4_Q3_AmbitionJustificationAnalyzer",
    "D4_Q4_ProblemSolvencyEvaluator",
    "D4_Q5_VerticalAlignmentValidator",
    "D5_Q1_LongTermVisionAnalyzer",
    "D5_Q2_CompositeMeasurementValidator",
    "D5_Q3_IntangibleMeasurementAnalyzer",
    "D5_Q4_SystemicRiskEvaluator",
    "D5_Q5_RealismAndSideEffectsAnalyzer",
    "D6_Q1_ExplicitTheoryBuilder",
    "D6_Q2_LogicalProportionalityValidator",
    "D6_Q3_ValidationTestingAnalyzer",
    "D6_Q4_FeedbackLoopAnalyzer",
    "D6_Q5_ContextualAdaptabilityEvaluator",
]


def instrument_executor_class(executor_class: type) -> type:
    """Instrument an executor class with OpenTelemetry tracing.
    
    Args:
        executor_class: The executor class to instrument
        
    Returns:
        The instrumented class
    """
    executor_name = executor_class.__name__
    
    if not any(name in executor_name for name in EXECUTOR_NAMES):
        return executor_class
    
    original_execute = executor_class.execute
    
    @wraps(original_execute)
    def traced_execute(self, *args, **kwargs):
        decorator = trace_executor(executor_name)
        wrapped = decorator(original_execute)
        return wrapped(self, *args, **kwargs)
    
    executor_class.execute = traced_execute
    
    logger.debug(f"Instrumented executor: {executor_name}")
    
    return executor_class


def auto_instrument_executors() -> None:
    """Automatically instrument all executor classes.
    
    This function attempts to find and instrument all 30 executor classes
    from the core.orchestrator.executors module.
    """
    try:
        from farfan_core.core.orchestrator import executors
        
        instrumented_count = 0
        for name in EXECUTOR_NAMES:
            if hasattr(executors, name):
                executor_class = getattr(executors, name)
                instrument_executor_class(executor_class)
                instrumented_count += 1
        
        logger.info(f"Auto-instrumented {instrumented_count}/{len(EXECUTOR_NAMES)} executors")
        
    except Exception as e:
        logger.warning(f"Failed to auto-instrument executors: {e}")


__all__ = [
    "instrument_executor_class",
    "auto_instrument_executors",
    "EXECUTOR_NAMES",
]
