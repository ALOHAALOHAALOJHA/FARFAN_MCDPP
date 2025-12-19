"""
Module: src.canonic_phases.phase_2.phase2_e_task_executor
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
    - signal_registry: SignalRegistry — SISAS signal resolution
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

from dataclasses import dataclass, field
from typing import Any, Final
import logging
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
        Derive base_slot from question_id.
        
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
        # Check cache first
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
        
        # Cache result
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
        
        TODO: INTEGRATION REQUIRED
        This is a placeholder implementation. Actual executor should:
        1. Iterate over method_sets from question_context
        2. Instantiate each method executor from methods_dispensary/
        3. Apply calibration if calibration_orchestrator is available
        4. Execute method with method_context
        5. Collect outputs from all methods
        6. Validate outputs if validation_orchestrator is available
        
        Integration Points:
        - methods_dispensary/: 40 method classes (e.g., BasicNLPExtractor, 
          SemanticAnalyzer, etc.)
        - CalibrationOrchestrator: Method parameter calibration
        - ValidationOrchestrator: Output validation tracking
        
        See PHASE_2_STABILITY_REPORT.md for detailed integration requirements.
        """
        # Placeholder implementation
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
        signal_registry: Any | None = None,
        calibration_orchestrator: Any | None = None,
        validation_orchestrator: Any | None = None,
    ) -> None:
        """
        Initialize TaskExecutor.
        
        Args:
            questionnaire_monolith: 300 questions
            preprocessed_document: 60 CPP chunks
            signal_registry: SISAS signal resolution
            calibration_orchestrator: Optional calibration
            validation_orchestrator: Optional validation tracking
        """
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
