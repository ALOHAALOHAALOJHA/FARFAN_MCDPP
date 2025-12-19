"""Resource-Aware Executor Wrapper.

Integrates AdaptiveResourceManager with MethodExecutor to provide:
- Automatic resource allocation before execution
- Circuit breaker checks before execution
- Degradation configuration injection
- Execution metrics tracking
- Memory and timing instrumentation
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from orchestration.orchestrator import MethodExecutor
    from orchestration.resource_manager import AdaptiveResourceManager

logger = logging.getLogger(__name__)


class ResourceAwareExecutor:
    """Wraps MethodExecutor with adaptive resource management."""
    
    def __init__(
        self,
        method_executor: MethodExecutor,
        resource_manager: AdaptiveResourceManager,
    ) -> None:
        self.method_executor = method_executor
        self.resource_manager = resource_manager
    
    async def execute_with_resource_management(
        self,
        executor_id: str,
        context: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute with full resource management integration.
        
        Args:
            executor_id: Executor identifier (e.g., "D3-Q3")
            context: Execution context
            **kwargs: Additional arguments for execution
            
        Returns:
            Execution result with resource metadata
            
        Raises:
            RuntimeError: If circuit breaker is open or execution fails
        """
        can_execute, reason = self.resource_manager.can_execute(executor_id)
        if not can_execute:
            logger.warning(
                f"Executor {executor_id} blocked by circuit breaker: {reason}"
            )
            raise RuntimeError(
                f"Executor {executor_id} unavailable: {reason}"
            )
        
        allocation = await self.resource_manager.start_executor_execution(
            executor_id
        )
        
        degradation_config = allocation["degradation"]
        enriched_context = self._apply_degradation(context, degradation_config)
        
        logger.info(
            f"Executing {executor_id} with resource allocation",
            extra={
                "max_memory_mb": allocation["max_memory_mb"],
                "max_workers": allocation["max_workers"],
                "priority": allocation["priority"],
                "degradation_applied": degradation_config["applied_strategies"],
            },
        )
        
        start_time = time.perf_counter()
        success = False
        result = None
        error = None
        
        try:
            result = await self._execute_with_timeout(
                executor_id, enriched_context, allocation, **kwargs
            )
            success = True
            return result
        except Exception as exc:
            error = str(exc)
            logger.error(
                f"Executor {executor_id} failed: {exc}",
                exc_info=True,
            )
            raise
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            memory_mb = self._estimate_memory_usage()
            
            await self.resource_manager.end_executor_execution(
                executor_id=executor_id,
                success=success,
                duration_ms=duration_ms,
                memory_mb=memory_mb,
            )
            
            logger.info(
                f"Executor {executor_id} completed",
                extra={
                    "success": success,
                    "duration_ms": duration_ms,
                    "memory_mb": memory_mb,
                    "error": error,
                },
            )
    
    async def _execute_with_timeout(
        self,
        executor_id: str,
        context: dict[str, Any],
        allocation: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute with timeout based on resource allocation."""
        timeout_seconds = self._calculate_timeout(allocation)
        
        try:
            result = await asyncio.wait_for(
                self._execute_async(executor_id, context, **kwargs),
                timeout=timeout_seconds,
            )
            return result
        except asyncio.TimeoutError as exc:
            logger.error(
                f"Executor {executor_id} timed out after {timeout_seconds}s"
            )
            raise RuntimeError(
                f"Executor {executor_id} timed out"
            ) from exc
    
    async def _execute_async(
        self,
        executor_id: str,
        context: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Async wrapper for executor execution."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._execute_sync, executor_id, context, kwargs
        )
    
    def _execute_sync(
        self,
        executor_id: str,
        context: dict[str, Any],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Synchronous execution wrapper."""
        try:
            from canonic_phases.Phase_two.executors import BaseExecutorWithContract
            
            # Extract question_id from context or executor_id
            # executor_id format could be "D3-Q3" but we need question_id like "Q013"
            question_id = context.get("question_id")
            if not question_id:
                # Try to derive from executor_id if it's in base_slot format
                if executor_id and "-" in executor_id:
                    # D3-Q3 → dimension 3, question 3 → Q013
                    parts = executor_id.split("-")
                    if len(parts) == 2 and parts[0].startswith("D") and parts[1].startswith("Q"):
                        dim = int(parts[0][1:])
                        q = int(parts[1][1:])
                        q_number = (dim - 1) * 5 + q
                        question_id = f"Q{q_number:03d}"
            
            if not question_id:
                raise ValueError(f"Cannot determine question_id from executor_id: {executor_id}")
            
            # Create BaseExecutorWithContract with question_id
            # TODO: ResourceAwareExecutor needs update to support BaseExecutorWithContract dependencies.
            # Currently missing signal_registry, config, questionnaire_provider.
            # Bypassing execution for now to maintain structure integrity.
            raise NotImplementedError("ResourceAwareExecutor update pending for Contract-Based Executors")
            
        except Exception as exc:
            logger.error(f"Sync execution failed: {exc}")
            raise
    
    def _apply_degradation(
        self,
        context: dict[str, Any],
        degradation_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply degradation strategies to context."""
        enriched = context.copy()
        
        enriched["_resource_constraints"] = {
            "entity_limit_factor": degradation_config["entity_limit_factor"],
            "disable_expensive_computations": degradation_config[
                "disable_expensive_computations"
            ],
            "use_simplified_methods": degradation_config["use_simplified_methods"],
            "skip_optional_analysis": degradation_config["skip_optional_analysis"],
            "reduce_embedding_dims": degradation_config["reduce_embedding_dims"],
        }
        
        if degradation_config["entity_limit_factor"] < 1.0:
            for key in ["max_entities", "max_chunks", "max_results"]:
                if key in enriched:
                    enriched[key] = int(
                        enriched[key] * degradation_config["entity_limit_factor"]
                    )
        
        return enriched
    
    def _calculate_timeout(self, allocation: dict[str, Any]) -> float:
        """Calculate execution timeout based on allocation."""
        base_timeout = 300.0
        
        priority = allocation["priority"]
        if priority == 1:
            return base_timeout * 1.5
        elif priority == 2:
            return base_timeout * 1.2
        else:
            return base_timeout
    
    def _estimate_memory_usage(self) -> float:
        """Estimate current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            usage = self.resource_manager.resource_limits.get_resource_usage()
            return usage.get("rss_mb", 0.0)


class ResourceConstraints:
    """Helper to extract and apply resource constraints in executors."""
    
    @staticmethod
    def get_constraints(context: dict[str, Any]) -> dict[str, Any]:
        """Extract resource constraints from context."""
        return context.get(
            "_resource_constraints",
            {
                "entity_limit_factor": 1.0,
                "disable_expensive_computations": False,
                "use_simplified_methods": False,
                "skip_optional_analysis": False,
                "reduce_embedding_dims": False,
            },
        )
    
    @staticmethod
    def should_skip_expensive_computation(context: dict[str, Any]) -> bool:
        """Check if expensive computations should be skipped."""
        constraints = ResourceConstraints.get_constraints(context)
        return constraints.get("disable_expensive_computations", False)
    
    @staticmethod
    def should_use_simplified_methods(context: dict[str, Any]) -> bool:
        """Check if simplified methods should be used."""
        constraints = ResourceConstraints.get_constraints(context)
        return constraints.get("use_simplified_methods", False)
    
    @staticmethod
    def should_skip_optional_analysis(context: dict[str, Any]) -> bool:
        """Check if optional analysis should be skipped."""
        constraints = ResourceConstraints.get_constraints(context)
        return constraints.get("skip_optional_analysis", False)
    
    @staticmethod
    def get_entity_limit(context: dict[str, Any], default: int) -> int:
        """Get entity limit with degradation applied."""
        constraints = ResourceConstraints.get_constraints(context)
        factor = constraints.get("entity_limit_factor", 1.0)
        return int(default * factor)
    
    @staticmethod
    def get_embedding_dimensions(context: dict[str, Any], default: int) -> int:
        """Get embedding dimensions with degradation applied."""
        constraints = ResourceConstraints.get_constraints(context)
        if constraints.get("reduce_embedding_dims", False):
            return int(default * 0.5)
        return default
