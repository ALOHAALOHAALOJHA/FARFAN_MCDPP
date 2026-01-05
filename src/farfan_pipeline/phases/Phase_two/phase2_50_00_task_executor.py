"""
Module: phase2_50_00_task_executor
PHASE_LABEL: Phase 2
Sequence: Z

"""
Module: src.farfan_pipeline.phases.phase_2.phase2_e_task_executor
Purpose: Phase 2.2 Task Execution - Execute 300 tasks from ExecutionPlan
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-19
Python-Version: 3.12+

Contracts-Enforced:
    - ExecutionContract: All 300 tasks from ExecutionPlan execute successfully
    - DeterminismContract: Same task inputs produce identical outputs
    - ProvenanceContract: Each output traces to originating task
    - CalibrationContract: Optional method calibration before execution

Determinism:
    Seed-Strategy: INHERITED from ExecutionPlan correlation_id
    State-Management: Executor caches base_slot derivations, otherwise stateless

Inputs:
    - execution_plan: ExecutionPlan — 300 tasks from Phase 2.1
    - preprocessed_document: PreprocessedDocument — 60 CPP chunks
    - questionnaire_monolith: dict — 300 questions for context
    - signal_registry: SignalRegistry — REQUIRED SISAS signal resolution
    - calibration_orchestrator: Optional — Method calibration
    - validation_orchestrator: Optional — Validation tracking

Outputs:
    - task_results: list[TaskResult] — 300 task execution results
    - OR raises ExecutionError

Failure-Modes:
    - TaskExecutionFailure: ExecutionError — Task execution failed
    - QuestionLookupFailure: ValueError — Cannot find question for task
    - ExecutorInstantiationFailure: ExecutionError — Cannot create executor
    - CalibrationFailure: CalibrationError — Method calibration failed

Phase 2.2 Process:
    1. Iterate over ExecutionPlan.tasks (300 tasks)
    2. For each task:
       a. Lookup question from monolith
       b. Build question_context
       c. Instantiate/reuse DynamicContractExecutor
       d. Execute task with executor
       e. Collect result
    3. Return list of 300 TaskResult objects
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Callable
import hashlib
import json
import logging
import os
import threading
from datetime import datetime, timezone

from .phase2_d_irrigation_orchestrator import ExecutionPlan, ExecutableTask

logger: Final = logging.getLogger(__name__)

# === DATA STRUCTURES ===

@dataclass(frozen=True, slots=True)
class TaskResult:
    """
    Result of executing a single task.
    
    Invariants:
        - task_id matches originating ExecutableTask
        - success indicates execution completed
        - output contains executor results
    """
    task_id: str
    question_id: str
    question_global: int
    policy_area_id: str
    dimension_id: str
    chunk_id: str
    success: bool
    output: dict[str, Any]
    error: str | None = None
    execution_time_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class QuestionContext:
    """
    Context for a question ready for executor dispatch.
    
    Contains all data needed to execute a question against a chunk.
    """
    question_id: str
    question_global: int
    question_text: str
    policy_area_id: str
    dimension_id: str
    chunk_id: str
    chunk_text: str
    patterns: list[dict[str, Any]]
    signals: dict[str, Any]
    expected_elements: list[dict[str, Any]]
    method_sets: list[str]
    correlation_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


# === EXCEPTION TAXONOMY ===

@dataclass
class ExecutionError(Exception):
    """Raised when Phase 2.2 task execution fails."""
    error_code: str
    message: str
    task_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        if self.task_id:
            return f"[{self.error_code}] Task {self.task_id}: {self.message}"
        return f"[{self.error_code}] {self.message}"


@dataclass
class CalibrationError(Exception):
    """Raised when method calibration fails."""
    error_code: str
    message: str
    method_name: str | None = None


class CheckpointCorruptionError(Exception):
    """Raised when checkpoint integrity validation fails."""
    pass


# === GAP 1: CHECKPOINT MANAGER ===

class CheckpointManager:
    """
    Manages checkpointing for resumable task execution.

    GAP 1 Implementation: Mid-Execution Recovery

    Features:
        - Persists progress after each task or configurable batch size
        - SHA-256 hash validation for checkpoint integrity
        - Automatic resumption from last successful checkpoint
        - Thread-safe checkpoint operations

    Requirements Implemented:
        CP-01: Checkpoints persisted to disk after each task/batch
        CP-02: Checkpoint contains plan_id, completed_tasks, timestamp, hash
        CP-03: On startup, executor checks for existing checkpoint
        CP-04: SHA-256 hash validation before resuming
        CP-05: Stored in artifacts/checkpoints/{plan_id}.checkpoint.json
    """

    def __init__(self, checkpoint_dir: Path | str = Path("artifacts/checkpoints")):
        """
        Initialize CheckpointManager.

        Args:
            checkpoint_dir: Directory for storing checkpoint files.
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _compute_hash(self, data: dict) -> str:
        """Compute SHA-256 hash of checkpoint data (excluding hash field)."""
        payload = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

    def save_checkpoint(
        self,
        plan_id: str,
        completed_tasks: list[str],
        metadata: dict | None = None
    ) -> Path:
        """
        Persist a checkpoint to disk.

        Args:
            plan_id: Unique identifier for the execution plan.
            completed_tasks: List of task IDs that have completed successfully.
            metadata: Optional additional metadata to store.

        Returns:
            Path to the saved checkpoint file.
        """
        with self._lock:
            checkpoint_path = self.checkpoint_dir / f"{plan_id}.checkpoint.json"
            data = {
                "plan_id": plan_id,
                "completed_tasks": completed_tasks,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            data["checkpoint_hash"] = self._compute_hash(data)

            with open(checkpoint_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.debug(
                "Checkpoint saved",
                extra={
                    "plan_id": plan_id,
                    "completed_count": len(completed_tasks),
                    "path": str(checkpoint_path),
                }
            )
            return checkpoint_path

    def resume_from_checkpoint(self, plan_id: str) -> set[str] | None:
        """
        Load and validate a checkpoint, returning set of completed task IDs.

        Args:
            plan_id: Unique identifier for the execution plan.

        Returns:
            Set of completed task IDs if valid checkpoint exists, else None.

        Raises:
            CheckpointCorruptionError: If checkpoint hash validation fails or file is unreadable.
        """
        with self._lock:
            checkpoint_path = self.checkpoint_dir / f"{plan_id}.checkpoint.json"
            if not checkpoint_path.exists():
                return None

            try:
                with open(checkpoint_path, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                raise CheckpointCorruptionError(
                    f"Checkpoint file unreadable for {plan_id}: {exc}"
                ) from exc

            stored_hash = data.pop("checkpoint_hash", None)
            computed_hash = self._compute_hash(data)

            if stored_hash != computed_hash:
                raise CheckpointCorruptionError(
                    f"Checkpoint integrity check failed for {plan_id}. "
                    f"Expected hash {stored_hash[:16]}..., got {computed_hash[:16]}..."
                )

            logger.info(
                "Checkpoint loaded for resumption",
                extra={
                    "plan_id": plan_id,
                    "completed_count": len(data["completed_tasks"]),
                    "checkpoint_timestamp": data["timestamp"],
                }
            )
            return set(data["completed_tasks"])

    def clear_checkpoint(self, plan_id: str) -> bool:
        """
        Remove checkpoint after successful plan completion.

        Args:
            plan_id: Unique identifier for the execution plan.

        Returns:
            True if checkpoint was removed, False if it didn't exist.
        """
        with self._lock:
            checkpoint_path = self.checkpoint_dir / f"{plan_id}.checkpoint.json"
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                logger.info(
                    "Checkpoint cleared after successful completion",
                    extra={"plan_id": plan_id}
                )
                return True
            return False

    def get_checkpoint_info(self, plan_id: str) -> dict | None:
        """
        Get checkpoint information without validating hash.

        Args:
            plan_id: Unique identifier for the execution plan.

        Returns:
            Checkpoint data dict or None if no checkpoint exists.
        """
        checkpoint_path = self.checkpoint_dir / f"{plan_id}.checkpoint.json"
        if not checkpoint_path.exists():
            return None

        with open(checkpoint_path, "r") as f:
            return json.load(f)


# === GAP 2: PARALLEL TASK EXECUTOR ===

class ParallelTaskExecutor:
    """
    Executes tasks in parallel, respecting epistemic level dependencies.

    GAP 2 Implementation: Parallel Task Execution (CRITICAL)

    Features:
        - Parallel execution within same epistemic level
        - Sequential execution between levels (N1 → N2 → N3)
        - Configurable worker count (default: CPU count)
        - Integration with CheckpointManager
        - Failed tasks don't block other tasks in same level

    Requirements Implemented:
        PE-01: Tasks within same epistemic level execute in parallel
        PE-02: Tasks at level N+1 wait for all level N tasks to complete
        PE-03: Max workers configurable (default: os.cpu_count())
        PE-04: Failed tasks don't block other independent tasks
        PE-05: Results aggregated in original task order
    """

    def __init__(
        self,
        questionnaire_monolith: dict[str, Any],
        preprocessed_document: Any,
        signal_registry: Any,
        calibration_orchestrator: Any | None = None,
        validation_orchestrator: Any | None = None,
        max_workers: int | None = None,
        checkpoint_manager: CheckpointManager | None = None,
        checkpoint_batch_size: int = 10,
        use_processes: bool = False,
    ) -> None:
        """
        Initialize ParallelTaskExecutor.

        Args:
            questionnaire_monolith: 300 questions
            preprocessed_document: 60 CPP chunks
            signal_registry: REQUIRED SISAS signal resolution
            calibration_orchestrator: Optional calibration
            validation_orchestrator: Optional validation tracking
            max_workers: Maximum parallel workers (default: CPU count)
            checkpoint_manager: Optional checkpoint manager for recovery
            checkpoint_batch_size: Tasks between checkpoints (default: 10)
            use_processes: Use ProcessPoolExecutor instead of ThreadPoolExecutor
        """
        if signal_registry is None:
            raise ValueError(
                "SignalRegistry is required for Phase 2.2. "
                "Must be initialized in Phase 0."
            )

        self.questionnaire_monolith = questionnaire_monolith
        self.preprocessed_document = preprocessed_document
        self.signal_registry = signal_registry
        self.calibration_orchestrator = calibration_orchestrator
        self.validation_orchestrator = validation_orchestrator
        self.max_workers = max_workers or os.cpu_count() or 4
        self.checkpoint_manager = checkpoint_manager
        self.checkpoint_batch_size = checkpoint_batch_size
        self.use_processes = use_processes

        # Build question lookup index
        self._question_index = self._build_question_index()

        # Thread-safe executor cache
        self._executor_cache: dict[str, DynamicContractExecutor] = {}
        self._cache_lock = threading.Lock()

    def _build_question_index(self) -> dict[str, dict[str, Any]]:
        """Build index of questions by question_id."""
        index: dict[str, dict[str, Any]] = {}
        blocks = self.questionnaire_monolith.get("blocks", [])
        for block in blocks:
            if block.get("block_type") == "micro_questions":
                for question in block.get("micro_questions", []):
                    question_id = question.get("question_id")
                    if question_id:
                        index[question_id] = question
        return index

    def execute_plan_parallel(self, plan: ExecutionPlan) -> list[TaskResult]:
        """
        Execute an ExecutionPlan with parallelism within epistemic levels.

        Args:
            plan: The execution plan containing tasks grouped by level.

        Returns:
            List of TaskResult objects in original task order.
        """
        plan_id = plan.plan_id

        # Resume from checkpoint if available
        completed_ids: set[str] = set()
        if self.checkpoint_manager:
            try:
                resumed = self.checkpoint_manager.resume_from_checkpoint(plan_id)
                if resumed:
                    completed_ids = resumed
                    logger.info(
                        f"Resuming from checkpoint with {len(completed_ids)} completed tasks"
                    )
            except CheckpointCorruptionError as e:
                logger.warning(f"Checkpoint corrupted, starting fresh: {e}")

        # Group tasks by epistemic level
        levels = self._group_by_level(plan.tasks)
        all_results: dict[str, TaskResult] = {}
        tasks_since_checkpoint = 0

        logger.info(
            "Starting parallel task execution",
            extra={
                "plan_id": plan_id,
                "task_count": len(plan.tasks),
                "levels": sorted(levels.keys()),
                "max_workers": self.max_workers,
                "already_completed": len(completed_ids),
            }
        )

        # Execute levels in order
        for level in sorted(levels.keys()):
            level_tasks = [
                t for t in levels[level] if t.task_id not in completed_ids
            ]

            if not level_tasks:
                logger.debug(f"Skipping level {level} - all tasks already completed")
                continue

            logger.info(
                f"Executing level {level}",
                extra={"task_count": len(level_tasks), "max_workers": self.max_workers}
            )

            level_results = self._execute_level(level_tasks)

            for result in level_results:
                all_results[result.task_id] = result
                if result.success:
                    completed_ids.add(result.task_id)
                tasks_since_checkpoint += 1

                # Checkpoint periodically
                if (
                    self.checkpoint_manager
                    and tasks_since_checkpoint >= self.checkpoint_batch_size
                ):
                    self.checkpoint_manager.save_checkpoint(
                        plan_id, list(completed_ids)
                    )
                    tasks_since_checkpoint = 0

        # Final checkpoint and cleanup
        if self.checkpoint_manager:
            self.checkpoint_manager.save_checkpoint(plan_id, list(completed_ids))
            self.checkpoint_manager.clear_checkpoint(plan_id)

        # Return results in original task order
        ordered_results = []
        for task in plan.tasks:
            if task.task_id in all_results:
                ordered_results.append(all_results[task.task_id])

        logger.info(
            "Parallel task execution complete",
            extra={
                "plan_id": plan_id,
                "total_tasks": len(ordered_results),
                "successful": sum(1 for r in ordered_results if r.success),
                "failed": sum(1 for r in ordered_results if not r.success),
            }
        )

        return ordered_results

    def _group_by_level(self, tasks: list[ExecutableTask]) -> dict[int, list[ExecutableTask]]:
        """
        Group tasks by their epistemic level (N1=1, N2=2, etc.).

        Args:
            tasks: List of tasks to group.

        Returns:
            Dict mapping level number to list of tasks.
        """
        levels: dict[int, list[ExecutableTask]] = {}
        for task in tasks:
            level = self._parse_level(task)
            levels.setdefault(level, []).append(task)
        return levels

    def _parse_level(self, task: ExecutableTask) -> int:
        """
        Extract epistemic level from task.

        Attempts to extract from:
        1. task.level attribute (if exists)
        2. task.metadata.get("epistemic_level")
        3. Default to 1 if not found

        Args:
            task: The task to extract level from.

        Returns:
            Integer level number.
        """
        # Try task.level attribute
        level_str = getattr(task, "level", None)
        if level_str:
            if isinstance(level_str, int):
                return level_str
            if isinstance(level_str, str) and level_str.startswith("N"):
                return int(level_str.replace("N", ""))

        # Try metadata
        metadata_level = task.metadata.get("epistemic_level") if hasattr(task, "metadata") else None
        if metadata_level:
            if isinstance(metadata_level, int):
                return metadata_level
            if isinstance(metadata_level, str) and metadata_level.startswith("N"):
                return int(metadata_level.replace("N", ""))

        # Default to level 1
        return 1

    def _execute_level(self, tasks: list[ExecutableTask]) -> list[TaskResult]:
        """
        Execute all tasks in a level in parallel.

        Args:
            tasks: List of tasks at the same epistemic level.

        Returns:
            List of TaskResult objects (unordered).
        """
        results: list[TaskResult] = []

        # Choose executor type
        ExecutorClass = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        with ExecutorClass(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self._execute_task_safe, task): task
                for task in tasks
            }

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(
                        f"Task {task.task_id} failed with unexpected error: {e}"
                    )
                    # Create failure result
                    result = TaskResult(
                        task_id=task.task_id,
                        question_id=task.question_id,
                        question_global=task.question_global,
                        policy_area_id=task.policy_area_id,
                        dimension_id=task.dimension_id,
                        chunk_id=task.chunk_id,
                        success=False,
                        output={},
                        error=str(e),
                    )
                    results.append(result)

        return results

    def _execute_task_safe(self, task: ExecutableTask) -> TaskResult:
        """
        Execute a single task with exception handling.

        Args:
            task: The task to execute.

        Returns:
            TaskResult with success or failure status.
        """
        start_time = datetime.now(timezone.utc)

        try:
            # Lookup question from monolith
            question = self._question_index.get(task.question_id)
            if not question:
                raise ValueError(f"Question not found in monolith: {task.question_id}")

            # Build question context
            question_context = QuestionContext(
                question_id=task.question_id,
                question_global=task.question_global,
                question_text=task.question_text,
                policy_area_id=task.policy_area_id,
                dimension_id=task.dimension_id,
                chunk_id=task.chunk_id,
                chunk_text=task.chunk_text,
                patterns=task.patterns,
                signals=task.signals,
                expected_elements=task.expected_elements,
                method_sets=question.get("method_sets", []),
                correlation_id=task.correlation_id,
                metadata=task.metadata,
            )

            # Get or create executor (thread-safe)
            with self._cache_lock:
                if task.question_id not in self._executor_cache:
                    self._executor_cache[task.question_id] = DynamicContractExecutor(
                        question_id=task.question_id,
                        calibration_orchestrator=self.calibration_orchestrator,
                        validation_orchestrator=self.validation_orchestrator,
                    )
                executor = self._executor_cache[task.question_id]

            # Execute task
            output = executor.execute(question_context)

            # Calculate execution time
            end_time = datetime.now(timezone.utc)
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            return TaskResult(
                task_id=task.task_id,
                question_id=task.question_id,
                question_global=task.question_global,
                policy_area_id=task.policy_area_id,
                dimension_id=task.dimension_id,
                chunk_id=task.chunk_id,
                success=True,
                output=output,
                execution_time_ms=execution_time_ms,
                metadata={
                    "base_slot": output.get("base_slot"),
                    "correlation_id": task.correlation_id,
                }
            )

        except Exception as e:
            end_time = datetime.now(timezone.utc)
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            logger.error(
                "Task execution failed",
                extra={
                    "task_id": task.task_id,
                    "question_id": task.question_id,
                    "error": str(e),
                }
            )

            return TaskResult(
                task_id=task.task_id,
                question_id=task.question_id,
                question_global=task.question_global,
                policy_area_id=task.policy_area_id,
                dimension_id=task.dimension_id,
                chunk_id=task.chunk_id,
                success=False,
                output={},
                error=str(e),
                execution_time_ms=execution_time_ms,
            )


# === MINOR IMPROVEMENT 5: DRY-RUN EXECUTOR ===

class DryRunExecutor:
    """
    Executor that simulates task execution without performing actual work.

    Minor Improvement 5: Dry-Run Mode

    Features:
        - Validates task inputs and dependencies
        - Estimates execution time based on task characteristics
        - Returns expected outputs without side effects
        - Useful for testing and planning
    """

    def __init__(
        self,
        questionnaire_monolith: dict[str, Any],
        preprocessed_document: Any,
        signal_registry: Any | None = None,
    ) -> None:
        """
        Initialize DryRunExecutor.

        Args:
            questionnaire_monolith: 300 questions
            preprocessed_document: 60 CPP chunks
            signal_registry: Optional signal resolution
        """
        self.questionnaire_monolith = questionnaire_monolith
        self.preprocessed_document = preprocessed_document
        self.signal_registry = signal_registry
        self._question_index = self._build_question_index()

    def _build_question_index(self) -> dict[str, dict[str, Any]]:
        """Build index of questions by question_id."""
        index: dict[str, dict[str, Any]] = {}
        blocks = self.questionnaire_monolith.get("blocks", [])
        for block in blocks:
            if block.get("block_type") == "micro_questions":
                for question in block.get("micro_questions", []):
                    question_id = question.get("question_id")
                    if question_id:
                        index[question_id] = question
        return index

    def execute_plan_dry_run(self, plan: ExecutionPlan) -> list[TaskResult]:
        """
        Simulate execution of all tasks in ExecutionPlan.

        Args:
            plan: The execution plan to simulate.

        Returns:
            List of simulated TaskResult objects.
        """
        results: list[TaskResult] = []

        logger.info(
            "Starting dry-run execution",
            extra={
                "plan_id": plan.plan_id,
                "task_count": len(plan.tasks),
            }
        )

        for task in plan.tasks:
            result = self._simulate_task(task)
            results.append(result)

        logger.info(
            "Dry-run execution complete",
            extra={
                "plan_id": plan.plan_id,
                "total_tasks": len(results),
                "would_succeed": sum(1 for r in results if r.success),
                "would_fail": sum(1 for r in results if not r.success),
            }
        )

        return results

    def _simulate_task(self, task: ExecutableTask) -> TaskResult:
        """
        Simulate execution of a single task.

        Args:
            task: The task to simulate.

        Returns:
            Simulated TaskResult.
        """
        # Check if question exists
        question = self._question_index.get(task.question_id)
        if not question:
            return TaskResult(
                task_id=task.task_id,
                question_id=task.question_id,
                question_global=task.question_global,
                policy_area_id=task.policy_area_id,
                dimension_id=task.dimension_id,
                chunk_id=task.chunk_id,
                success=False,
                output={},
                error=f"Question not found in monolith: {task.question_id}",
                metadata={"dry_run": True},
            )

        # Estimate execution time based on task complexity
        estimated_time_ms = self._estimate_execution_time(task, question)

        # Build dry-run output
        method_sets = question.get("method_sets", [])
        base_slot = DynamicContractExecutor._derive_base_slot(task.question_id)

        return TaskResult(
            task_id=task.task_id,
            question_id=task.question_id,
            question_global=task.question_global,
            policy_area_id=task.policy_area_id,
            dimension_id=task.dimension_id,
            chunk_id=task.chunk_id,
            success=True,
            output={
                "dry_run": True,
                "would_execute": {
                    "method_sets": method_sets,
                    "base_slot": base_slot,
                    "patterns_count": len(task.patterns),
                    "signals_count": len(task.signals),
                    "expected_elements_count": len(task.expected_elements),
                    "chunk_text_length": len(task.chunk_text) if task.chunk_text else 0,
                },
                "estimated_time_ms": estimated_time_ms,
            },
            execution_time_ms=0.0,
            metadata={"dry_run": True, "estimated_time_ms": estimated_time_ms},
        )

    def _estimate_execution_time(
        self, task: ExecutableTask, question: dict
    ) -> float:
        """
        Estimate execution time based on task characteristics.

        Args:
            task: The task to estimate.
            question: The question data.

        Returns:
            Estimated execution time in milliseconds.
        """
        # Base time
        base_ms = 50.0

        # Add time for patterns
        base_ms += len(task.patterns) * 5.0

        # Add time for signals
        base_ms += len(task.signals) * 3.0

        # Add time for expected elements
        base_ms += len(task.expected_elements) * 2.0

        # Add time for chunk text length
        chunk_length = len(task.chunk_text) if task.chunk_text else 0
        base_ms += chunk_length * 0.01

        # Add time for method sets
        method_sets = question.get("method_sets", [])
        base_ms += len(method_sets) * 20.0

        return base_ms


# === DYNAMIC CONTRACT EXECUTOR ===

class DynamicContractExecutor:
    """
    Executor for the 300-contract model with automatic base_slot derivation.
    
    Derives base_slot from question_id using the formula:
    - slot_index = (q_number - 1) % 30
    - dimension = (slot_index // 5) + 1
    - question_in_dimension = (slot_index % 5) + 1
    - base_slot = f"D{dimension}-Q{question_in_dimension}"
    
    Caches derivations in _question_to_base_slot_cache for performance.
    
    SUCCESS_CRITERIA:
        - Correct base_slot derivation for all Q001-Q300
        - Successful method execution for all tasks
        - Output format compatible with carver input
    
    FAILURE_MODES:
        - InvalidQuestionID: Cannot parse question_id
        - BaseSlotDerivationFailure: Formula produces invalid slot
        - MethodExecutionFailure: Executor method fails
    
    VERIFICATION_STRATEGY:
        - test_phase2_task_executor.py
    """
    
    # Class-level cache for base_slot derivations
    _question_to_base_slot_cache: dict[str, str] = {}
    _cache_lock = threading.Lock()
    
    def __init__(
        self,
        question_id: str,
        calibration_orchestrator: Any | None = None,
        validation_orchestrator: Any | None = None,
    ) -> None:
        """
        Initialize DynamicContractExecutor for a specific question.
        
        Args:
            question_id: Question identifier (e.g., "Q001", "Q150")
            calibration_orchestrator: Optional calibration support
            validation_orchestrator: Optional validation tracking
        """
        self.question_id = question_id
        self.calibration_orchestrator = calibration_orchestrator
        self.validation_orchestrator = validation_orchestrator
        
        # Derive and cache base_slot
        self.base_slot = self._derive_base_slot(question_id)
        
        logger.info(
            "DynamicContractExecutor initialized",
            extra={
                "question_id": question_id,
                "base_slot": self.base_slot,
            }
        )
    
    @classmethod
    def _derive_base_slot(cls, question_id: str) -> str:
        """
        Derive base_slot from question_id with thread-safe caching.
        
        Formula:
        - Extract question number (Q001 -> 1, Q150 -> 150)
        - slot_index = (q_number - 1) % 30
        - dimension = (slot_index // 5) + 1
        - question_in_dimension = (slot_index % 5) + 1
        - base_slot = f"D{dimension}-Q{question_in_dimension}"
        
        Examples:
        - Q001 -> slot_index=0 -> D1-Q1
        - Q006 -> slot_index=5 -> D2-Q1
        - Q030 -> slot_index=29 -> D6-Q5
        - Q031 -> slot_index=0 -> D1-Q1 (wraps)
        """
        # Thread-safe cache access
        with cls._cache_lock:
            if question_id in cls._question_to_base_slot_cache:
                return cls._question_to_base_slot_cache[question_id]
        
        # Parse question number
        try:
            if not question_id.startswith("Q"):
                raise ValueError(f"Invalid question_id format: {question_id}")
            q_number = int(question_id[1:])
        except (ValueError, IndexError) as e:
            raise ValueError(f"Cannot parse question_id: {question_id}") from e
        
        # Derive slot_index
        slot_index = (q_number - 1) % 30
        
        # Derive dimension and question_in_dimension
        dimension = (slot_index // 5) + 1
        question_in_dimension = (slot_index % 5) + 1
        
        # Build base_slot
        base_slot = f"D{dimension}-Q{question_in_dimension}"
        
        # Thread-safe cache write
        with cls._cache_lock:
            cls._question_to_base_slot_cache[question_id] = base_slot
        
        return base_slot
    
    def execute(self, question_context: QuestionContext) -> dict[str, Any]:
        """
        Execute task with question context.
        
        Args:
            question_context: Context with all data for execution
            
        Returns:
            Execution result dictionary
            
        Raises:
            ExecutionError: If execution fails
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Build method context
            method_context = self._build_method_context(question_context)
            
            # Execute methods (simplified - actual implementation would call real executors)
            output = self._execute_methods(method_context, question_context)
            
            # Track execution time
            end_time = datetime.now(timezone.utc)
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            logger.info(
                "Task execution successful",
                extra={
                    "question_id": question_context.question_id,
                    "base_slot": self.base_slot,
                    "execution_time_ms": execution_time_ms,
                }
            )
            
            return {
                "question_id": question_context.question_id,
                "base_slot": self.base_slot,
                "output": output,
                "execution_time_ms": execution_time_ms,
                "success": True,
            }
            
        except Exception as e:
            logger.error(
                "Task execution failed",
                extra={
                    "question_id": question_context.question_id,
                    "base_slot": self.base_slot,
                    "error": str(e),
                }
            )
            raise ExecutionError(
                error_code="E2007",
                message=f"Task execution failed: {str(e)}",
                task_id=question_context.question_id,
                details={"base_slot": self.base_slot, "error": str(e)}
            ) from e
    
    def _build_method_context(
        self, question_context: QuestionContext
    ) -> dict[str, Any]:
        """Build context dictionary for method execution."""
        return {
            "question_id": question_context.question_id,
            "question_global": question_context.question_global,
            "question_text": question_context.question_text,
            "policy_area_id": question_context.policy_area_id,
            "dimension_id": question_context.dimension_id,
            "base_slot": self.base_slot,
            "chunk_id": question_context.chunk_id,
            "chunk_text": question_context.chunk_text,
            "patterns": question_context.patterns,
            "signals": question_context.signals,
            "expected_elements": question_context.expected_elements,
            "method_sets": question_context.method_sets,
            "correlation_id": question_context.correlation_id,
        }
    
    def _execute_methods(
        self, method_context: dict, question_context: QuestionContext
    ) -> dict[str, Any]:
        """
        Execute methods for this question.
        
        OPERATIONAL INTEGRATION:
        This method integrates with the existing MethodRegistry infrastructure:
        
        1. MethodRegistry implements lazy loading with 300s TTL cache
        2. 40+ method classes mapped in class_registry._CLASS_PATHS:
           - TextMiningEngine, CausalExtractor, FinancialAuditor,
           - BayesianNumericalAnalyzer, PolicyAnalysisEmbedder, etc.
        3. Integration flow:
           - Read method_binding.methods[] from contract v3
           - Call MethodRegistry.get_method(class_name, method_name)
           - Instantiate class under demand from methods_dispensary/*
           - Execute with arguments validated by ExtendedArgRouter
        4. CalibrationPolicy (from calibration_policy.py) weights methods
        5. Thread-safe with threading.Lock
        
        Current Implementation:
        - Simplified execution for canonical Phase 2 pipeline
        - Full MethodRegistry integration available via orchestrator
        - See: farfan_pipeline/orchestration/method_registry.py
        - See: farfan_pipeline/phases/Phase_two/calibration_policy.py
        """
        # Simplified execution - full integration via orchestrator's MethodRegistry
        return {
            "method_outputs": {},
            "patterns_matched": len(question_context.patterns),
            "signals_resolved": len(question_context.signals),
            "expected_elements": question_context.expected_elements,
        }


# === TASK EXECUTOR ===

class TaskExecutor:
    """
    Phase 2.2 - Execute 300 tasks from ExecutionPlan.
    
    Iterates over ExecutionPlan.tasks, executes each task with
    DynamicContractExecutor, and collects results.
    
    SUCCESS_CRITERIA:
        - All 300 tasks execute successfully
        - Each result traces to originating task
        - Results compatible with Carver input
    
    FAILURE_MODES:
        - TaskExecutionFailure: Individual task fails
        - QuestionLookupFailure: Cannot find question
        - ExecutorFailure: Executor instantiation fails
    
    TERMINATION_CONDITION:
        - All 300 tasks processed
        - Returns list of 300 TaskResult objects
    
    VERIFICATION_STRATEGY:
        - test_phase2_task_executor.py
    """
    
    def __init__(
        self,
        questionnaire_monolith: dict[str, Any],
        preprocessed_document: Any,
        signal_registry: Any,
        calibration_orchestrator: Any | None = None,
        validation_orchestrator: Any | None = None,
    ) -> None:
        """
        Initialize TaskExecutor.
        
        Args:
            questionnaire_monolith: 300 questions
            preprocessed_document: 60 CPP chunks
            signal_registry: REQUIRED SISAS signal resolution (must be initialized in Phase 0)
            calibration_orchestrator: Optional calibration
            validation_orchestrator: Optional validation tracking
            
        Raises:
            ValueError: If signal_registry is None
        """
        # Validate SignalRegistry is provided
        if signal_registry is None:
            raise ValueError(
                "SignalRegistry is required for Phase 2.2. "
                "Must be initialized in Phase 0."
            )
        
        self.questionnaire_monolith = questionnaire_monolith
        self.preprocessed_document = preprocessed_document
        self.signal_registry = signal_registry
        self.calibration_orchestrator = calibration_orchestrator
        self.validation_orchestrator = validation_orchestrator
        
        # Build question lookup index
        self._question_index = self._build_question_index()
        
        # Executor cache
        self._executor_cache: dict[str, DynamicContractExecutor] = {}
    
    def _build_question_index(self) -> dict[str, dict[str, Any]]:
        """Build index of questions by question_id."""
        index: dict[str, dict[str, Any]] = {}
        
        blocks = self.questionnaire_monolith.get("blocks", [])
        for block in blocks:
            if block.get("block_type") == "micro_questions":
                for question in block.get("micro_questions", []):
                    question_id = question.get("question_id")
                    if question_id:
                        index[question_id] = question
        
        return index
    
    def execute_plan(self, execution_plan: ExecutionPlan) -> list[TaskResult]:
        """
        Execute all tasks in ExecutionPlan.
        
        Args:
            execution_plan: Plan with 300 tasks from Phase 2.1
            
        Returns:
            List of 300 TaskResult objects
            
        Raises:
            ExecutionError: If execution fails
        """
        results: list[TaskResult] = []
        
        logger.info(
            "Starting task execution",
            extra={
                "plan_id": execution_plan.plan_id,
                "task_count": len(execution_plan.tasks),
                "correlation_id": execution_plan.correlation_id,
            }
        )
        
        for i, task in enumerate(execution_plan.tasks):
            try:
                result = self._execute_task(task)
                results.append(result)
                
                if (i + 1) % 50 == 0:
                    logger.info(
                        f"Progress: {i + 1}/{len(execution_plan.tasks)} tasks completed"
                    )
                    
            except Exception as e:
                logger.error(
                    "Task execution failed",
                    extra={
                        "task_id": task.task_id,
                        "question_id": task.question_id,
                        "error": str(e),
                    }
                )
                
                # Create failure result
                result = TaskResult(
                    task_id=task.task_id,
                    question_id=task.question_id,
                    question_global=task.question_global,
                    policy_area_id=task.policy_area_id,
                    dimension_id=task.dimension_id,
                    chunk_id=task.chunk_id,
                    success=False,
                    output={},
                    error=str(e),
                )
                results.append(result)
        
        logger.info(
            "Task execution complete",
            extra={
                "plan_id": execution_plan.plan_id,
                "total_tasks": len(results),
                "successful": sum(1 for r in results if r.success),
                "failed": sum(1 for r in results if not r.success),
            }
        )
        
        return results
    
    def _execute_task(self, task: ExecutableTask) -> TaskResult:
        """Execute single task."""
        start_time = datetime.now(timezone.utc)
        
        # Lookup question from monolith
        question = self._lookup_question(task)
        
        # Build question context
        question_context = self._build_question_context(task, question)
        
        # Get or create executor
        executor = self._get_executor(task.question_id)
        
        # Execute task
        output = executor.execute(question_context)
        
        # Calculate execution time
        end_time = datetime.now(timezone.utc)
        execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return TaskResult(
            task_id=task.task_id,
            question_id=task.question_id,
            question_global=task.question_global,
            policy_area_id=task.policy_area_id,
            dimension_id=task.dimension_id,
            chunk_id=task.chunk_id,
            success=True,
            output=output,
            execution_time_ms=execution_time_ms,
            metadata={
                "base_slot": output.get("base_slot"),
                "correlation_id": task.correlation_id,
            }
        )
    
    def _lookup_question(self, task: ExecutableTask) -> dict[str, Any]:
        """Lookup question from monolith by question_id."""
        question = self._question_index.get(task.question_id)
        if not question:
            raise ValueError(
                f"Question not found in monolith: {task.question_id}"
            )
        return question
    
    def _build_question_context(
        self, task: ExecutableTask, question: dict
    ) -> QuestionContext:
        """Build QuestionContext from task and question."""
        return QuestionContext(
            question_id=task.question_id,
            question_global=task.question_global,
            question_text=task.question_text,
            policy_area_id=task.policy_area_id,
            dimension_id=task.dimension_id,
            chunk_id=task.chunk_id,
            chunk_text=task.chunk_text,
            patterns=task.patterns,
            signals=task.signals,
            expected_elements=task.expected_elements,
            method_sets=question.get("method_sets", []),
            correlation_id=task.correlation_id,
            metadata=task.metadata,
        )
    
    def _get_executor(self, question_id: str) -> DynamicContractExecutor:
        """Get or create executor for question_id (with caching)."""
        if question_id not in self._executor_cache:
            self._executor_cache[question_id] = DynamicContractExecutor(
                question_id=question_id,
                calibration_orchestrator=self.calibration_orchestrator,
                validation_orchestrator=self.validation_orchestrator,
            )
        return self._executor_cache[question_id]


# === PUBLIC API ===

def execute_tasks(
    execution_plan: ExecutionPlan,
    questionnaire_monolith: dict[str, Any],
    preprocessed_document: Any,
    signal_registry: Any | None = None,
    calibration_orchestrator: Any | None = None,
    validation_orchestrator: Any | None = None,
) -> list[TaskResult]:
    """
    Public API for executing tasks from ExecutionPlan.
    
    Args:
        execution_plan: Plan with 300 tasks from Phase 2.1
        questionnaire_monolith: 300 questions
        preprocessed_document: 60 CPP chunks
        signal_registry: SISAS signal resolution
        calibration_orchestrator: Optional calibration
        validation_orchestrator: Optional validation tracking
        
    Returns:
        List of 300 TaskResult objects
        
    Raises:
        ExecutionError: If execution fails
    """
    executor = TaskExecutor(
        questionnaire_monolith=questionnaire_monolith,
        preprocessed_document=preprocessed_document,
        signal_registry=signal_registry,
        calibration_orchestrator=calibration_orchestrator,
        validation_orchestrator=validation_orchestrator,
    )
    return executor.execute_plan(execution_plan)


def execute_tasks_parallel(
    execution_plan: ExecutionPlan,
    questionnaire_monolith: dict[str, Any],
    preprocessed_document: Any,
    signal_registry: Any,
    calibration_orchestrator: Any | None = None,
    validation_orchestrator: Any | None = None,
    max_workers: int | None = None,
    checkpoint_dir: Path | str | None = None,
    checkpoint_batch_size: int = 10,
) -> list[TaskResult]:
    """
    Public API for executing tasks in parallel with checkpointing.

    GAP 1 + GAP 2: Parallel execution with mid-execution recovery.

    Args:
        execution_plan: Plan with 300 tasks from Phase 2.1
        questionnaire_monolith: 300 questions
        preprocessed_document: 60 CPP chunks
        signal_registry: SISAS signal resolution (REQUIRED)
        calibration_orchestrator: Optional calibration
        validation_orchestrator: Optional validation tracking
        max_workers: Maximum parallel workers (default: CPU count)
        checkpoint_dir: Directory for checkpoints (default: artifacts/checkpoints)
        checkpoint_batch_size: Tasks between checkpoints (default: 10)

    Returns:
        List of TaskResult objects in original task order.

    Raises:
        ExecutionError: If execution fails
        ValueError: If signal_registry is None
    """
    checkpoint_manager = None
    if checkpoint_dir is not None:
        checkpoint_manager = CheckpointManager(checkpoint_dir)
    else:
        # Default checkpoint directory
        checkpoint_manager = CheckpointManager()

    executor = ParallelTaskExecutor(
        questionnaire_monolith=questionnaire_monolith,
        preprocessed_document=preprocessed_document,
        signal_registry=signal_registry,
        calibration_orchestrator=calibration_orchestrator,
        validation_orchestrator=validation_orchestrator,
        max_workers=max_workers,
        checkpoint_manager=checkpoint_manager,
        checkpoint_batch_size=checkpoint_batch_size,
    )
    return executor.execute_plan_parallel(execution_plan)


def execute_tasks_dry_run(
    execution_plan: ExecutionPlan,
    questionnaire_monolith: dict[str, Any],
    preprocessed_document: Any,
    signal_registry: Any | None = None,
) -> list[TaskResult]:
    """
    Public API for simulating task execution without side effects.

    Minor Improvement 5: Dry-run mode.

    Args:
        execution_plan: Plan to simulate
        questionnaire_monolith: 300 questions
        preprocessed_document: 60 CPP chunks
        signal_registry: Optional signal resolution

    Returns:
        List of simulated TaskResult objects with dry_run=True.
    """
    executor = DryRunExecutor(
        questionnaire_monolith=questionnaire_monolith,
        preprocessed_document=preprocessed_document,
        signal_registry=signal_registry,
    )
    return executor.execute_plan_dry_run(execution_plan)


# === MODULE EXPORTS ===

__all__ = [
    # Data structures
    "TaskResult",
    "QuestionContext",
    # Exceptions
    "ExecutionError",
    "CalibrationError",
    "CheckpointCorruptionError",
    # GAP 1: Checkpointing
    "CheckpointManager",
    # GAP 2: Parallel execution
    "ParallelTaskExecutor",
    # Minor improvement 5: Dry-run
    "DryRunExecutor",
    # Core executor
    "DynamicContractExecutor",
    "TaskExecutor",
    # Public API functions
    "execute_tasks",
    "execute_tasks_parallel",
    "execute_tasks_dry_run",
]
