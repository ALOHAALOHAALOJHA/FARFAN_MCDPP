"""
Module: phase2_30_03_resource_aware_executor
PHASE_LABEL: Phase 2
Sequence: K

"""
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
import threading
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, List, Optional

if TYPE_CHECKING:
    from orchestration.orchestrator import MethodExecutor
    from orchestration.resource_manager import AdaptiveResourceManager

logger = logging.getLogger(__name__)


# === GAP 6: INTERRUPTIBLE EXECUTOR ===

class ResourceEmergencyInterrupt(Exception):
    """Raised when a resource emergency requires task interruption.

    GAP 6 Implementation: Used for cooperative task interruption.

    Attributes:
        reason: Description of why the interrupt was triggered.
        partial_results: Any partial results before interruption.
    """
    def __init__(self, reason: str, partial_results: Any = None):
        super().__init__(reason)
        self.reason = reason
        self.partial_results = partial_results


@dataclass
class InterruptState:
    """State of an interrupt signal.

    Attributes:
        is_set: Whether interrupt is currently signaled.
        reason: Reason for the interrupt.
        timestamp: When the interrupt was signaled.
    """
    is_set: bool = False
    reason: Optional[str] = None
    timestamp: Optional[float] = None


class InterruptController:
    """
    Controls interrupt signaling between ResourceManager and Executor.

    GAP 6 Implementation: Interruptible Executor (Mid-Execution Pause)

    Features:
        - Thread-safe interrupt signaling
        - Reason tracking for debugging
        - Clear/reset functionality

    Requirements Implemented:
        IE-04: Interrupt flag set by ResourceManager on emergency
        IE-05: Executor supports graceful shutdown on interrupt

    Usage:
        controller = InterruptController()
        controller.signal_interrupt("Critical memory pressure")
        if controller.should_interrupt():
            raise ResourceEmergencyInterrupt(controller.interrupt_reason)
    """

    def __init__(self):
        """Initialize interrupt controller."""
        self._interrupt_flag = threading.Event()
        self._interrupt_reason: Optional[str] = None
        self._interrupt_timestamp: Optional[float] = None
        self._lock = threading.Lock()

    def signal_interrupt(self, reason: str) -> None:
        """
        Signal that tasks should be interrupted.

        Args:
            reason: Description of why interrupt was triggered.
        """
        with self._lock:
            self._interrupt_reason = reason
            self._interrupt_timestamp = time.time()
            self._interrupt_flag.set()
            logger.warning(f"Interrupt signaled: {reason}")

    def clear_interrupt(self) -> None:
        """Clear the interrupt signal."""
        with self._lock:
            self._interrupt_flag.clear()
            self._interrupt_reason = None
            self._interrupt_timestamp = None
            logger.debug("Interrupt cleared")

    def should_interrupt(self) -> bool:
        """Check if interrupt has been signaled."""
        return self._interrupt_flag.is_set()

    @property
    def interrupt_reason(self) -> Optional[str]:
        """Get the reason for the current interrupt."""
        return self._interrupt_reason

    @property
    def interrupt_timestamp(self) -> Optional[float]:
        """Get when the interrupt was signaled."""
        return self._interrupt_timestamp

    def get_state(self) -> InterruptState:
        """Get full interrupt state."""
        with self._lock:
            return InterruptState(
                is_set=self._interrupt_flag.is_set(),
                reason=self._interrupt_reason,
                timestamp=self._interrupt_timestamp,
            )

    def wait_for_interrupt(self, timeout: Optional[float] = None) -> bool:
        """
        Block until interrupt is signaled or timeout.

        Args:
            timeout: Maximum seconds to wait (None = forever).

        Returns:
            True if interrupt was signaled, False if timeout.
        """
        return self._interrupt_flag.wait(timeout=timeout)


@dataclass
class PartialExecutionResult:
    """Result of a partially completed execution.

    Attributes:
        task_id: ID of the interrupted task.
        completed_steps: Number of steps completed.
        total_steps: Total steps in the task.
        partial_results: Results from completed steps.
        interrupt_reason: Why execution was interrupted.
        resumable: Whether execution can be resumed.
    """
    task_id: str
    completed_steps: int
    total_steps: int
    partial_results: List[Any] = field(default_factory=list)
    interrupt_reason: Optional[str] = None
    resumable: bool = True


class InterruptibleExecutor:
    """
    Executor that supports mid-execution interruption.

    GAP 6 Implementation: Interruptible Executor (Mid-Execution Pause)

    Features:
        - Cooperative interruption via periodic checks
        - Partial progress saving on interrupt
        - Configurable check intervals
        - Method wrapping for automatic checks

    Requirements Implemented:
        IE-01: Executor checks interrupt flag at configurable intervals
        IE-02: Interrupt raises ResourceEmergencyInterrupt exception
        IE-03: Interrupted tasks save partial progress if possible
        IE-04: Interrupt flag set by ResourceManager on emergency
        IE-05: Executor supports graceful shutdown on interrupt

    Usage:
        controller = InterruptController()
        executor = InterruptibleExecutor(controller)
        wrapped_method = executor.wrap_with_interrupt_check(my_method)
    """

    def __init__(
        self,
        interrupt_controller: InterruptController,
        check_interval_ms: int = 100
    ):
        """
        Initialize interruptible executor.

        Args:
            interrupt_controller: Controller for interrupt signals.
            check_interval_ms: Milliseconds between interrupt checks.
        """
        self.interrupt_controller = interrupt_controller
        self.check_interval_ms = check_interval_ms
        self._partial_results_store: dict[str, PartialExecutionResult] = {}
        self._lock = threading.Lock()

    def check_interrupt(self) -> None:
        """
        Check for interrupt and raise if signaled.

        Implements IE-01 and IE-02.

        Raises:
            ResourceEmergencyInterrupt: If interrupt is signaled.
        """
        if self.interrupt_controller.should_interrupt():
            raise ResourceEmergencyInterrupt(
                self.interrupt_controller.interrupt_reason or "Unknown interrupt"
            )

    def wrap_with_interrupt_check(self, method: Callable) -> Callable:
        """
        Wrap a method to check for interrupts before execution.

        Implements IE-01.

        Args:
            method: Method to wrap.

        Returns:
            Wrapped method that checks for interrupts.
        """
        @wraps(method)
        def wrapper(*args, **kwargs):
            self.check_interrupt()
            return method(*args, **kwargs)
        return wrapper

    def execute_with_interrupts(
        self,
        task_id: str,
        methods: List[Callable],
        context: Any = None
    ) -> PartialExecutionResult:
        """
        Execute methods with interrupt checking.

        Implements IE-01 through IE-03.

        Args:
            task_id: ID for tracking this execution.
            methods: List of methods to execute sequentially.
            context: Context to pass to each method.

        Returns:
            PartialExecutionResult with completed results.
        """
        partial_results = []
        total_steps = len(methods)

        try:
            for i, method in enumerate(methods):
                # Check for interrupt before each step
                self.check_interrupt()

                # Execute method
                if context is not None:
                    result = method(context)
                else:
                    result = method()

                partial_results.append(result)

                logger.debug(
                    f"Task {task_id}: completed step {i + 1}/{total_steps}"
                )

            return PartialExecutionResult(
                task_id=task_id,
                completed_steps=total_steps,
                total_steps=total_steps,
                partial_results=partial_results,
                resumable=False,  # Fully completed
            )

        except ResourceEmergencyInterrupt as e:
            # Save partial progress (IE-03)
            partial_result = PartialExecutionResult(
                task_id=task_id,
                completed_steps=len(partial_results),
                total_steps=total_steps,
                partial_results=partial_results,
                interrupt_reason=e.reason,
                resumable=True,
            )

            self._save_partial_progress(task_id, partial_result)

            logger.warning(
                f"Task {task_id} interrupted at step {len(partial_results)}/{total_steps}: {e.reason}"
            )

            return partial_result

    def _save_partial_progress(
        self,
        task_id: str,
        result: PartialExecutionResult
    ) -> None:
        """
        Save partial progress for later resumption.

        Implements IE-03.

        Args:
            task_id: Task identifier.
            result: Partial execution result.
        """
        with self._lock:
            self._partial_results_store[task_id] = result
            logger.debug(f"Saved partial progress for task {task_id}")

    def get_partial_progress(self, task_id: str) -> Optional[PartialExecutionResult]:
        """
        Get saved partial progress for a task.

        Args:
            task_id: Task identifier.

        Returns:
            PartialExecutionResult if exists, else None.
        """
        with self._lock:
            return self._partial_results_store.get(task_id)

    def clear_partial_progress(self, task_id: str) -> bool:
        """
        Clear saved partial progress for a task.

        Args:
            task_id: Task identifier.

        Returns:
            True if progress was cleared, False if not found.
        """
        with self._lock:
            if task_id in self._partial_results_store:
                del self._partial_results_store[task_id]
                return True
            return False

    def resume_execution(
        self,
        task_id: str,
        methods: List[Callable],
        context: Any = None
    ) -> Optional[PartialExecutionResult]:
        """
        Resume execution from saved partial progress.

        Args:
            task_id: Task identifier.
            methods: Full list of methods to execute.
            context: Context to pass to methods.

        Returns:
            PartialExecutionResult or None if no saved progress.
        """
        partial = self.get_partial_progress(task_id)
        if partial is None:
            return None

        # Skip already completed methods
        remaining_methods = methods[partial.completed_steps:]
        if not remaining_methods:
            return partial

        # Continue execution
        continuation = self.execute_with_interrupts(
            task_id=task_id,
            methods=remaining_methods,
            context=context,
        )

        # Merge results
        merged_results = partial.partial_results + continuation.partial_results

        return PartialExecutionResult(
            task_id=task_id,
            completed_steps=partial.completed_steps + continuation.completed_steps,
            total_steps=partial.total_steps,
            partial_results=merged_results,
            interrupt_reason=continuation.interrupt_reason,
            resumable=continuation.resumable,
        )


# === RESOURCE MANAGER INTEGRATION ===

class InterruptibleResourceManager:
    """
    ResourceManager extension with interrupt signaling.

    Integrates InterruptController with resource monitoring to
    automatically signal interrupts on resource emergencies.

    Usage:
        controller = InterruptController()
        manager = InterruptibleResourceManager(controller)
        manager.start_monitoring()
    """

    # Pressure levels that trigger interrupt
    INTERRUPT_THRESHOLD = 4  # CRITICAL level

    def __init__(
        self,
        interrupt_controller: InterruptController,
        check_interval_seconds: float = 0.1
    ):
        """
        Initialize interruptible resource manager.

        Args:
            interrupt_controller: Controller for signaling interrupts.
            check_interval_seconds: Seconds between pressure checks.
        """
        self.interrupt_controller = interrupt_controller
        self.check_interval_seconds = check_interval_seconds
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None

    def start_monitoring(self) -> None:
        """Start background resource monitoring."""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="InterruptibleResourceManager"
        )
        self._monitor_thread.start()
        logger.info("Started interrupt-aware resource monitoring")

    def stop_monitoring(self) -> None:
        """Stop background resource monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None
        logger.info("Stopped interrupt-aware resource monitoring")

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring:
            try:
                pressure = self._check_pressure()

                if pressure >= self.INTERRUPT_THRESHOLD:
                    self.interrupt_controller.signal_interrupt(
                        f"Critical resource pressure: level {pressure}"
                    )
                elif pressure < self.INTERRUPT_THRESHOLD - 1:
                    # Clear interrupt when pressure drops significantly
                    if self.interrupt_controller.should_interrupt():
                        self.interrupt_controller.clear_interrupt()

            except Exception as e:
                logger.error(f"Error in resource monitor: {e}")

            time.sleep(self.check_interval_seconds)

    def _check_pressure(self) -> int:
        """
        Check current resource pressure level.

        Returns:
            Pressure level (0=none, 4=critical)
        """
        try:
            import psutil

            # Check memory pressure
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Check CPU pressure
            cpu_percent = psutil.cpu_percent(interval=None)

            # Determine overall pressure level
            if memory_percent > 95 or cpu_percent > 95:
                return 4  # CRITICAL
            elif memory_percent > 85 or cpu_percent > 85:
                return 3  # HIGH
            elif memory_percent > 70 or cpu_percent > 70:
                return 2  # MEDIUM
            elif memory_percent > 50 or cpu_percent > 50:
                return 1  # LOW
            else:
                return 0  # NONE

        except ImportError:
            # psutil not available, return no pressure
            return 0
        except Exception as e:
            logger.debug(f"Error checking pressure: {e}")
            return 0


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
            from farfan_pipeline.phases.Phase_two.phase2_60_00_base_executor_with_contract import DynamicContractExecutor
            
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
            
            # Create GenericContractExecutor with question_id
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


# === MODULE EXPORTS ===

__all__ = [
    # GAP 6: Interruptible Executor
    "ResourceEmergencyInterrupt",
    "InterruptState",
    "InterruptController",
    "PartialExecutionResult",
    "InterruptibleExecutor",
    "InterruptibleResourceManager",
    # Original classes
    "ResourceAwareExecutor",
    "ResourceConstraints",
]
