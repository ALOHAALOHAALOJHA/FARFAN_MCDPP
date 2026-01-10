"""
Executor Instrumentation Mixin for Calibration Integration.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Executor Instrumentation
PHASE_ROLE: Adds calibration instrumentation to executors for runtime metrics capture

This mixin adds calibration instrumentation to all D[1-6]Q[1-5] executors,
capturing runtime metrics and retrieving quality scores from the calibration system.

Usage:
    # 300-contract model (preferred)
    class Q001_Executor(BaseExecutor, ExecutorInstrumentationMixin):
        def execute(self, context):
            # Instrumentation is automatically applied via wrapper
            ...
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from farfan_pipeline.phases.Phase_2.phase2_95_03_executor_calibration_integration import (
    instrument_executor,
)


class ExecutorInstrumentationMixin:
    """
    Mixin to add calibration instrumentation to executors.
    
    This mixin provides methods to:
    1. Instrument executor execution with calibration calls
    2. Capture runtime metrics (time, memory)
    3. Retrieve quality scores from calibration system
    4. Store calibration results for reporting
    
    The mixin ensures NO hardcoded calibration values in executor code.
    All quality scores are loaded from external calibration files.
    """
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._calibration_result: Optional[CalibrationResult] = None
        self._execution_start_time: float = 0.0
        self._execution_start_memory: float = 0.0
    
    def _start_calibration_tracking(self) -> None:
        """Start tracking execution metrics for calibration."""
        self._execution_start_time = time.perf_counter()
        
        if hasattr(self, '_profiler') and self._profiler and self._profiler.memory_tracking:
            self._execution_start_memory = self._profiler._get_memory_usage_mb()
        else:
            self._execution_start_memory = 0.0
    
    def _stop_calibration_tracking(self, context: Dict[str, Any]) -> CalibrationResult:
        """
        Stop tracking and instrument executor with calibration call.
        
        Args:
            context: Execution context
        
        Returns:
            CalibrationResult with quality scores and metrics
        """
        runtime_ms = (time.perf_counter() - self._execution_start_time) * 1000
        
        memory_mb = 0.0
        if hasattr(self, '_profiler') and self._profiler and self._profiler.memory_tracking:
            memory_mb = self._profiler._get_memory_usage_mb() - self._execution_start_memory
        
        methods_executed = len(self.execution_log) if hasattr(self, 'execution_log') else 0
        methods_succeeded = sum(
            1 for log_entry in (self.execution_log if hasattr(self, 'execution_log') else [])
            if log_entry.get('success', False)
        )
        
        calibration_result = instrument_executor(
            executor_id=self.executor_id,
            context=context,
            runtime_ms=runtime_ms,
            memory_mb=memory_mb,
            methods_executed=methods_executed,
            methods_succeeded=methods_succeeded
        )
        
        self._calibration_result = calibration_result
        return calibration_result
    
    def execute_with_calibration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute with automatic calibration instrumentation.
        
        This wraps the execute() method to add calibration calls before
        and after execution. Quality scores are retrieved from the
        calibration system and attached to the result.
        
        Args:
            context: Execution context
        
        Returns:
            Result dict with raw_evidence and calibration metadata
        """
        self._start_calibration_tracking()
        
        try:
            result = self.execute(context)
            
            calibration_result = self._stop_calibration_tracking(context)
            
            if not isinstance(result, dict):
                result = {"raw_evidence": result}
            
            result["calibration_metadata"] = {
                "quality_score": calibration_result.quality_score,
                "layer_scores": calibration_result.layer_scores,
                "layers_used": calibration_result.layers_used,
                "aggregation_method": calibration_result.aggregation_method,
                "runtime_ms": calibration_result.metrics.runtime_ms,
                "memory_mb": calibration_result.metrics.memory_mb,
                "methods_executed": calibration_result.metrics.methods_executed,
                "methods_succeeded": calibration_result.metrics.methods_succeeded,
            }
            
            return result
            
        except Exception as e:
            calibration_result = self._stop_calibration_tracking(context)
            
            raise
    
    def get_calibration_result(self) -> Optional[CalibrationResult]:
        """Get the most recent calibration result."""
        return self._calibration_result
    
    def get_executor_runtime_config(self) -> Dict[str, Any]:
        """
        Get runtime configuration for this executor.
        
        This loads HOW parameters (timeout, retry, etc.) from:
        1. CLI arguments
        2. Environment variables
        3. Environment file
        4. Executor config file
        5. Conservative defaults
        
        Returns:
            Runtime configuration dict
        """
        parts = self.executor_id.split("_")
        if len(parts) < 2:
            return {}
        
        dimension = parts[0]
        question = parts[1]
        
        return get_executor_config(self.executor_id, dimension, question)


__all__ = ["ExecutorInstrumentationMixin"]
