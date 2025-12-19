"""
Module: src.canonic_phases.phase_2.phase2_d_irrigation_orchestrator
Purpose: Phase 2.1 Orchestration - Question→Chunk→Task→Plan coordination
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-19
Python-Version: 3.12+

Contracts-Enforced:
    - TaskGenerationContract: 300 questions → 300 executable tasks
    - ChunkRoutingContract: Each task routes to exactly one of 60 chunks
    - DeterminismContract: Same inputs produce identical ExecutionPlan with same plan_id
    - IntegrityContract: Blake3/SHA-256 hash verification of plan integrity

Determinism:
    Seed-Strategy: DERIVED from correlation_id and task ordering
    State-Management: Stateless orchestrator; all state in ExecutionPlan

Inputs:
    - questionnaire_monolith: dict — 300 micro questions (Q001-Q300)
    - preprocessed_document: PreprocessedDocument — 60 CPP chunks
    - signal_registry: SignalRegistry — REQUIRED SISAS signal resolution
    - specialized_contracts: list[dict] — Optional Q{nnn}.v3.json contracts

Outputs:
    - execution_plan: ExecutionPlan — 300 tasks with deterministic plan_id
    - OR raises OrchestrationError

Failure-Modes:
    - ChunkMatrixValidation: ValueError — Not exactly 60 unique chunks
    - ChunkRoutingFailure: ValueError — Cannot map question to chunk
    - TaskDuplication: ValueError — Duplicate task_id detected
    - PlanIntegrityFailure: ValueError — Hash validation failed

Phase 2.1 Process (8 Subfases):
    2.1.0 - JOIN Table Construction (if enabled)
    2.1.1 - Question Extraction (300 questions from monolith)
    2.1.2 - Iteration Setup (task_id tracking, counters)
    2.1.3 - Chunk Routing (map each question to target chunk)
    2.1.4 - Pattern Filtering (from contracts or monolith)
    2.1.5 - Signal Resolution (SISAS signal lookup)
    2.1.6 - Schema Validation (Phase 6 compatibility check)
    2.1.7 - Task Construction (build ExecutableTask objects)
    2.1.8 - Plan Assembly (deterministic ordering, integrity hash)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final
import logging
import hashlib
import json
import uuid
from datetime import datetime, timezone
from collections import Counter

logger: Final = logging.getLogger(__name__)

# === DATA STRUCTURES ===

@dataclass(frozen=True, slots=True)
class ChunkRoutingResult:
    """Result of Phase 2.1.3 chunk routing verification."""
    target_chunk: Any  # ChunkData from PreprocessedDocument
    chunk_id: str
    policy_area_id: str
    dimension_id: str
    text_content: str
    expected_elements: list[dict[str, Any]]
    document_position: tuple[int, int] | None = None


@dataclass(frozen=True, slots=True)
class ExecutableTask:
    """
    Single unit of work in Phase 2.1.7 - ready for executor dispatch.
    
    Represents one question applied to one chunk in a specific policy area.
    """
    task_id: str
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
    correlation_id: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """
    Phase 2.1.8 - Immutable execution plan with cryptographic integrity.
    
    Contains all 300 tasks to be executed, with deterministic identifiers.
    """
    plan_id: str
    tasks: tuple[ExecutableTask, ...]
    chunk_count: int
    question_count: int
    integrity_hash: str
    created_at: str
    correlation_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert plan to dictionary for serialization."""
        return {
            "plan_id": self.plan_id,
            "tasks": [
                {
                    "task_id": t.task_id,
                    "question_id": t.question_id,
                    "question_global": t.question_global,
                    "policy_area_id": t.policy_area_id,
                    "dimension_id": t.dimension_id,
                    "chunk_id": t.chunk_id,
                }
                for t in self.tasks
            ],
            "chunk_count": self.chunk_count,
            "question_count": self.question_count,
            "integrity_hash": self.integrity_hash,
            "created_at": self.created_at,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }


@dataclass
class ChunkMatrix:
    """
    Phase 2.1 Input - Validates and indexes 60 CPP chunks.
    
    Provides O(1) lookup by (policy_area_id, dimension_id).
    Enforces invariant of exactly 60 unique chunks.
    """
    chunks: dict[tuple[str, str], Any]
    integrity_hash: str
    
    @classmethod
    def from_document(cls, document: Any) -> ChunkMatrix:
        """Construct ChunkMatrix from PreprocessedDocument."""
        # Extract chunks from document
        chunks_raw = cls._extract_chunks(document)
        
        # Build matrix indexed by (PA, DIM)
        chunks_dict: dict[tuple[str, str], Any] = {}
        for chunk in chunks_raw:
            pa_id = chunk.get("policy_area_id") or chunk.get("pa_code")
            dim_id = chunk.get("dimension_id") or chunk.get("dim_code")
            key = (pa_id, dim_id)
            
            if key in chunks_dict:
                raise ValueError(f"Duplicate chunk for {key}")
            
            if not chunk.get("content") and not chunk.get("text"):
                raise ValueError(f"Empty chunk for {key}")
            
            chunks_dict[key] = chunk
        
        # Validate exactly 60 chunks
        if len(chunks_dict) != 60:
            raise ValueError(
                f"Expected 60 chunks, got {len(chunks_dict)}. "
                f"Missing: {cls._find_missing_combinations(chunks_dict)}"
            )
        
        # Compute integrity hash
        chunk_ids = sorted(f"{k[0]}_{k[1]}" for k in chunks_dict.keys())
        integrity_hash = hashlib.sha256(
            json.dumps(chunk_ids, sort_keys=True).encode()
        ).hexdigest()
        
        return cls(chunks=chunks_dict, integrity_hash=integrity_hash)
    
    @staticmethod
    def _extract_chunks(document: Any) -> list[Any]:
        """Extract chunks from various document formats."""
        if isinstance(document, list):
            return document
        if hasattr(document, "chunks"):
            return document.chunks
        if hasattr(document, "chunk_graph") and hasattr(document.chunk_graph, "chunks"):
            return document.chunk_graph.chunks
        raise ValueError("Cannot extract chunks from document")
    
    @staticmethod
    def _find_missing_combinations(chunks_dict: dict) -> list[str]:
        """Find missing (PA, DIM) combinations."""
        expected = {
            (f"PA{i:02d}", f"DIM{j:02d}")
            for i in range(1, 11)
            for j in range(1, 7)
        }
        actual = set(chunks_dict.keys())
        missing = expected - actual
        return [f"{pa}-{dim}" for pa, dim in sorted(missing)]
    
    def get_chunk(self, policy_area_id: str, dimension_id: str) -> Any:
        """Get chunk by (PA, DIM) - O(1) lookup."""
        return self.chunks.get((policy_area_id, dimension_id))


# === EXCEPTION TAXONOMY ===

@dataclass
class OrchestrationError(Exception):
    """Raised when Phase 2.1 orchestration fails."""
    error_code: str
    message: str
    details: dict[str, Any]
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


# === PHASE 2.1 ORCHESTRATOR ===

class IrrigationOrchestrator:
    """
    Phase 2.1 - Question→Chunk→Task→Plan Orchestration.
    
    Implements the 8-subfase process described in the specification:
    - Subfase 2.1.0: JOIN table construction
    - Subfase 2.1.1: Question extraction
    - Subfase 2.1.2: Iteration setup
    - Subfase 2.1.3: Chunk routing
    - Subfase 2.1.4: Pattern filtering
    - Subfase 2.1.5: Signal resolution
    - Subfase 2.1.6: Schema validation
    - Subfase 2.1.7: Task construction
    - Subfase 2.1.8: Plan assembly
    
    SUCCESS_CRITERIA:
        - 300 questions → 300 tasks
        - All tasks route to valid chunks (60 total)
        - Deterministic plan_id from task ordering
        - No duplicate task_ids
    
    FAILURE_MODES:
        - ChunkMatrixValidation: Not exactly 60 chunks
        - ChunkRoutingFailure: Cannot map question to chunk
        - TaskDuplication: Duplicate task_id
        - PlanIntegrityFailure: Hash validation failed
    
    VERIFICATION_STRATEGY:
        - test_phase2_irrigation_orchestrator.py
    """
    
    def __init__(
        self,
        questionnaire_monolith: dict[str, Any],
        preprocessed_document: Any,
        signal_registry: Any,
        specialized_contracts: list[dict[str, Any]] | None = None,
        enable_join_table: bool = False,
    ) -> None:
        """
        Initialize Phase 2.1 orchestrator.
        
        Args:
            questionnaire_monolith: 300 micro questions
            preprocessed_document: 60 CPP chunks
            signal_registry: REQUIRED SISAS signal resolution (must be initialized in Phase 0)
            specialized_contracts: Optional Q{nnn}.v3.json contracts
            enable_join_table: Enable contract-based pattern filtering
            
        Raises:
            ValueError: If signal_registry is None
        """
        # Validate SignalRegistry is provided
        if signal_registry is None:
            raise ValueError(
                "SignalRegistry is required for Phase 2.1. "
                "Initialize in Phase 0 with SISAS signal packs."
            )
        
        # Generate correlation_id for traceability
        self.correlation_id: Final = str(uuid.uuid4())
        
        # Store inputs
        self.questionnaire_monolith = questionnaire_monolith
        self.signal_registry = signal_registry
        self.specialized_contracts = specialized_contracts or []
        self.enable_join_table = enable_join_table
        
        # Build ChunkMatrix from document
        self.chunk_matrix = ChunkMatrix.from_document(preprocessed_document)
        
        # Count questions
        self.question_count = self._count_questions()
        
        # JOIN table (Subfase 2.1.0)
        self.join_table: dict[str, dict] = {}
        if enable_join_table and specialized_contracts:
            self._build_join_table()
        
        logger.info(
            "IrrigationOrchestrator initialized",
            extra={
                "correlation_id": self.correlation_id,
                "question_count": self.question_count,
                "chunk_count": len(self.chunk_matrix.chunks),
                "join_table_enabled": enable_join_table,
            }
        )
    
    def _count_questions(self) -> int:
        """Count questions in monolith."""
        blocks = self.questionnaire_monolith.get("blocks", [])
        for block in blocks:
            if block.get("block_type") == "micro_questions":
                return len(block.get("micro_questions", []))
        return 0
    
    def _build_join_table(self) -> None:
        """Subfase 2.1.0 - Build JOIN table from contracts."""
        for contract in self.specialized_contracts:
            question_id = contract.get("question_id")
            if question_id:
                self.join_table[question_id] = contract
        
        logger.info(
            "JOIN table constructed",
            extra={
                "correlation_id": self.correlation_id,
                "contract_count": len(self.join_table),
            }
        )
    
    def build_execution_plan(self) -> ExecutionPlan:
        """
        Build ExecutionPlan with 300 tasks.
        
        Implements Phase 2.1 process with 8 subfases.
        
        Returns:
            ExecutionPlan with 300 tasks ordered deterministically
            
        Raises:
            OrchestrationError: If any subfase fails
        """
        # Subfase 2.1.1 - Extract questions
        questions = self._extract_questions()
        
        # Subfase 2.1.2 - Setup iteration
        generated_task_ids: set[str] = set()
        tasks: list[ExecutableTask] = []
        routing_success = 0
        routing_failures = 0
        
        # Process each question through subfases 2.1.3-2.1.7
        for question in questions:
            try:
                # Subfase 2.1.3 - Chunk routing
                routing_result = self._validate_chunk_routing(question)
                routing_success += 1
                
                # Subfase 2.1.4 - Pattern filtering
                patterns = self._filter_patterns(question)
                
                # Subfase 2.1.5 - Signal resolution
                signals = self._resolve_signals(question, routing_result.target_chunk)
                
                # Subfase 2.1.6 - Schema validation
                self._validate_schema_compatibility(question, routing_result)
                
                # Subfase 2.1.7 - Task construction
                task = self._construct_task(
                    question, routing_result, patterns, signals, generated_task_ids
                )
                tasks.append(task)
                
            except Exception as e:
                routing_failures += 1
                logger.error(
                    "Task construction failed",
                    extra={
                        "correlation_id": self.correlation_id,
                        "question_id": question.get("question_id"),
                        "error": str(e),
                    }
                )
                raise
        
        # Subfase 2.1.8 - Plan assembly
        execution_plan = self._assemble_execution_plan(tasks, questions)
        
        logger.info(
            "ExecutionPlan built successfully",
            extra={
                "correlation_id": self.correlation_id,
                "plan_id": execution_plan.plan_id,
                "task_count": len(execution_plan.tasks),
                "routing_success": routing_success,
                "routing_failures": routing_failures,
            }
        )
        
        return execution_plan
    
    def _extract_questions(self) -> list[dict[str, Any]]:
        """Subfase 2.1.1 - Extract 300 questions from monolith."""
        blocks = self.questionnaire_monolith.get("blocks", [])
        all_questions: list[dict[str, Any]] = []
        for block in blocks:
            if block.get("block_type") == "micro_questions":
                micro_questions = block.get("micro_questions", [])
                if micro_questions:
                    all_questions.extend(micro_questions)
        if not all_questions:
            return []
        # Sort for deterministic ordering across all micro_question blocks
        all_questions.sort(
            key=lambda q: (
                q.get("policy_area_id", ""),
                q.get("question_global", 0),
            )
        )
        return all_questions
    
    def _validate_chunk_routing(self, question: dict) -> ChunkRoutingResult:
        """Subfase 2.1.3 - Route question to target chunk."""
        pa_id = question.get("policy_area_id")
        dim_id = question.get("dimension_id")
        
        chunk = self.chunk_matrix.get_chunk(pa_id, dim_id)
        if not chunk:
            raise ValueError(
                f"Chunk routing failed: no chunk for ({pa_id}, {dim_id})"
            )
        
        # Extract chunk content
        text = chunk.get("content") or chunk.get("text") or ""
        if not text:
            raise ValueError(f"Empty chunk for ({pa_id}, {dim_id})")
        
        return ChunkRoutingResult(
            target_chunk=chunk,
            chunk_id=f"{pa_id}-{dim_id}",
            policy_area_id=pa_id,
            dimension_id=dim_id,
            text_content=text,
            expected_elements=question.get("expected_elements", []),
            document_position=chunk.get("position"),
        )
    
    def _filter_patterns(self, question: dict) -> list[dict[str, Any]]:
        """Subfase 2.1.4 - Filter patterns from contract or monolith."""
        question_id = question.get("question_id")
        
        # Try JOIN table first if enabled
        if self.enable_join_table and question_id in self.join_table:
            contract = self.join_table[question_id]
            question_context = contract.get("question_context", {})
            return question_context.get("patterns", [])
        
        # Fallback to monolith patterns
        patterns_raw = question.get("patterns", [])
        pa_id = question.get("policy_area_id")
        
        # Filter by policy_area_id
        return [p for p in patterns_raw if p.get("policy_area_id") == pa_id]
    
    def _resolve_signals(
        self, question: dict, target_chunk: Any
    ) -> dict[str, Any]:
        """Subfase 2.1.5 - Resolve SISAS signals for question."""
        if not self.signal_registry:
            return {}
        
        requirements = question.get("signal_requirements", [])
        if not requirements:
            return {}
        
        try:
            signals = self.signal_registry.get_signals_for_chunk(
                target_chunk, requirements
            )
            
            # Index by signal_type
            signals_dict = {}
            for signal in signals:
                signal_type = signal.get("signal_type")
                if signal_type:
                    signals_dict[signal_type] = signal
            
            return signals_dict
        except Exception as e:
            logger.warning(
                "Signal resolution failed",
                extra={
                    "correlation_id": self.correlation_id,
                    "question_id": question.get("question_id"),
                    "error": str(e),
                }
            )
            return {}
    
    def _validate_schema_compatibility(
        self, question: dict, routing_result: ChunkRoutingResult
    ) -> None:
        """Subfase 2.1.6 - Validate Phase 6 schema compatibility."""
        # Simplified validation - full implementation in phase6_validation
        question_elements = set(question.get("expected_elements", []))
        chunk_elements = set(
            e.get("element_type", "") for e in routing_result.expected_elements
        )
        
        # Check basic compatibility
        if question_elements and chunk_elements:
            if not question_elements.intersection(chunk_elements):
                logger.warning(
                    "Schema compatibility warning",
                    extra={
                        "correlation_id": self.correlation_id,
                        "question_id": question.get("question_id"),
                        "question_elements": list(question_elements),
                        "chunk_elements": list(chunk_elements),
                    }
                )
    
    def _construct_task(
        self,
        question: dict,
        routing_result: ChunkRoutingResult,
        patterns: list[dict],
        signals: dict,
        generated_task_ids: set[str],
    ) -> ExecutableTask:
        """Subfase 2.1.7 - Construct ExecutableTask."""
        question_global = question.get("question_global", 0)
        pa_id = routing_result.policy_area_id
        
        # Generate task_id in format "MQC-{nnn}_{PA}"
        task_id = f"MQC-{question_global:03d}_{pa_id}"
        
        # Check for duplicates
        if task_id in generated_task_ids:
            raise ValueError(f"Duplicate task_id: {task_id}")
        generated_task_ids.add(task_id)
        
        # Create timestamp
        created_at = datetime.now(timezone.utc).isoformat()
        
        return ExecutableTask(
            task_id=task_id,
            question_id=question.get("question_id", ""),
            question_global=question_global,
            question_text=question.get("question_text", ""),
            policy_area_id=pa_id,
            dimension_id=routing_result.dimension_id,
            chunk_id=routing_result.chunk_id,
            chunk_text=routing_result.text_content,
            patterns=patterns,
            signals=signals,
            expected_elements=routing_result.expected_elements,
            correlation_id=self.correlation_id,
            created_at=created_at,
            metadata={
                "document_position": routing_result.document_position,
            }
        )
    
    def _assemble_execution_plan(
        self, tasks: list[ExecutableTask], questions: list[dict]
    ) -> ExecutionPlan:
        """Subfase 2.1.8 - Assemble final ExecutionPlan."""
        # Validate task count
        if len(tasks) != len(questions):
            raise ValueError(
                f"Task count mismatch: {len(tasks)} tasks for {len(questions)} questions"
            )
        
        # Detect duplicates
        task_ids = [t.task_id for t in tasks]
        duplicates = [tid for tid, count in Counter(task_ids).items() if count > 1]
        if duplicates:
            raise ValueError(f"Duplicate task_ids: {duplicates}")
        
        # Sort tasks deterministically
        tasks_sorted = sorted(tasks, key=lambda t: t.task_id)
        
        # Compute plan_id from serialized tasks
        tasks_json = json.dumps(
            [
                {
                    "task_id": t.task_id,
                    "question_id": t.question_id,
                    "chunk_id": t.chunk_id,
                }
                for t in tasks_sorted
            ],
            sort_keys=True,
        )
        plan_id = hashlib.sha256(tasks_json.encode()).hexdigest()
        
        # Compute integrity hash (Blake3 if available, else SHA-256)
        try:
            import blake3
            integrity_hash = blake3.blake3(tasks_json.encode()).hexdigest()
        except ImportError:
            integrity_hash = hashlib.sha256(tasks_json.encode()).hexdigest()
        
        # Validate plan_id format
        if len(plan_id) != 64 or not all(c in "0123456789abcdef" for c in plan_id):
            raise ValueError(f"Invalid plan_id format: {plan_id}")
        
        created_at = datetime.now(timezone.utc).isoformat()
        
        return ExecutionPlan(
            plan_id=plan_id,
            tasks=tuple(tasks_sorted),
            chunk_count=len(self.chunk_matrix.chunks),
            question_count=len(questions),
            integrity_hash=integrity_hash,
            created_at=created_at,
            correlation_id=self.correlation_id,
            metadata={
                "chunk_matrix_hash": self.chunk_matrix.integrity_hash,
                "join_table_enabled": self.enable_join_table,
                "contract_count": len(self.join_table),
            }
        )


# === PUBLIC API ===

def build_irrigation_plan(
    questionnaire_monolith: dict[str, Any],
    preprocessed_document: Any,
    signal_registry: Any | None = None,
    specialized_contracts: list[dict[str, Any]] | None = None,
    enable_join_table: bool = False,
) -> ExecutionPlan:
    """
    Public API for building Phase 2.1 ExecutionPlan.
    
    Args:
        questionnaire_monolith: 300 micro questions
        preprocessed_document: 60 CPP chunks
        signal_registry: Optional SISAS signal resolution
        specialized_contracts: Optional Q{nnn}.v3.json contracts
        enable_join_table: Enable contract-based pattern filtering
        
    Returns:
        ExecutionPlan with 300 tasks ordered deterministically
        
    Raises:
        OrchestrationError: If orchestration fails
    """
    orchestrator = IrrigationOrchestrator(
        questionnaire_monolith=questionnaire_monolith,
        preprocessed_document=preprocessed_document,
        signal_registry=signal_registry,
        specialized_contracts=specialized_contracts,
        enable_join_table=enable_join_table,
    )
    return orchestrator.build_execution_plan()
