"""
Module: src.canonic_phases.phase_2.phase2_c_nexus_integration
Purpose: Integrate micro-answers with EvidenceNexus for graph-based evidence synthesis
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18
Python-Version: 3.12+

Contracts-Enforced:
    - IntegrationContract: All 300 micro-answers route to EvidenceNexus
    - ProvenanceContract: Evidence graph traces to originating micro-answer
    - SynthesisContract: Narrative output synthesized from evidence graph

Determinism:
    Seed-Strategy: INHERITED from carver via micro-answer content_hash
    State-Management: Stateless integration; EvidenceNexus manages graph state

Inputs:
    - micro_answers: list[MicroAnswer] — Exactly 300 micro-answers from carver
    - question_context: dict — Question context with expected_elements
    - contract: dict — Executor contract specification

Outputs:
    - nexus_result: NexusResult — Complete result with evidence graph and narrative
    - OR raises NexusIntegrationError

Failure-Modes:
    - InputCardinalityViolation: NexusIntegrationError — Input != 300 micro-answers
    - GraphConstructionFailure: NexusIntegrationError — Cannot build evidence graph
    - SynthesisFailure: NexusIntegrationError — Narrative synthesis failed
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final
import logging
from pathlib import Path

from .phase2_b_carver import MicroAnswer
from .constants.phase2_constants import MICRO_ANSWER_COUNT, ERROR_CODES

logger: Final = logging.getLogger(__name__)

# === DATA STRUCTURES ===

@dataclass(frozen=True, slots=True)
class NexusResult:
    """
    Result from EvidenceNexus processing.
    
    Invariants:
        - evidence_graph is non-empty
        - synthesized_answer contains narrative
        - provenance maps to micro-answers
    """
    evidence_graph: dict[str, Any]
    validation_report: dict[str, Any]
    synthesized_answer: str
    human_readable_output: str
    graph_statistics: dict[str, Any]
    provenance: dict[str, str]  # Maps evidence_id -> micro_answer.task_id
    
    def __post_init__(self) -> None:
        """Validate invariants."""
        if not self.evidence_graph:
            raise ValueError("evidence_graph must be non-empty")
        if not self.synthesized_answer:
            raise ValueError("synthesized_answer must be non-empty")


# === EXCEPTION TAXONOMY ===

@dataclass
class NexusIntegrationError(Exception):
    """Raised when nexus integration fails."""
    error_code: str
    message: str
    details: dict[str, Any]
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


# === NEXUS INTEGRATOR IMPLEMENTATION ===

class NexusIntegrator:
    """
    Integrate micro-answers with EvidenceNexus for evidence synthesis.
    
    SUCCESS_CRITERIA:
        - All 300 micro-answers transformed to method outputs
        - Evidence graph constructed from method outputs
        - Narrative synthesized from evidence graph
        - Provenance maintained from micro-answer to narrative
    
    FAILURE_MODES:
        - InputCardinalityViolation: len(micro_answers) != 300
        - GraphConstructionFailure: Cannot build evidence graph
        - SynthesisFailure: Narrative synthesis failed
    
    TERMINATION_CONDITION:
        - Returns NexusResult on success
        - Raises NexusIntegrationError on failure
    
    VERIFICATION_STRATEGY:
        - test_phase2_nexus_integration.py
    """
    
    def __init__(
        self,
        storage_path: Path | None = None,
        enable_persistence: bool = False,
        citation_threshold: float = 0.6,
    ) -> None:
        """
        Initialize nexus integrator.
        
        Args:
            storage_path: Path for EvidenceNexus persistent storage
            enable_persistence: Whether to persist evidence graph
            citation_threshold: Minimum confidence for citation inclusion
        """
        self._storage_path = storage_path
        self._enable_persistence = enable_persistence
        self._citation_threshold = citation_threshold
        
        # Lazy-load EvidenceNexus to avoid circular imports
        self._nexus = None
    
    def integrate(
        self,
        micro_answers: list[MicroAnswer],
        question_context: dict[str, Any],
        contract: dict[str, Any],
    ) -> NexusResult:
        """
        Integrate micro-answers with EvidenceNexus.
        
        Args:
            micro_answers: Exactly 300 micro-answers from carver
            question_context: Question context with expected_elements
            contract: Executor contract specification
            
        Returns:
            NexusResult with evidence graph and synthesized narrative
            
        Raises:
            NexusIntegrationError: If integration fails
        """
        # Validate input cardinality
        self._validate_input_cardinality(micro_answers)
        
        # Transform micro-answers to method outputs format
        method_outputs = self._transform_to_method_outputs(micro_answers)
        
        # Get or create EvidenceNexus instance
        nexus = self._get_nexus()
        
        # Process through EvidenceNexus
        try:
            result = nexus.process(
                method_outputs=method_outputs,
                question_context=question_context,
                contract=contract,
                signal_pack=None,  # Could be added for enhanced provenance
            )
        except Exception as e:
            raise NexusIntegrationError(
                error_code="E2005",
                message="EvidenceNexus processing failed",
                details={"error": str(e), "type": type(e).__name__}
            ) from e
        
        # Build provenance mapping
        provenance = self._build_provenance(micro_answers, result)
        
        # Construct and return result
        return NexusResult(
            evidence_graph=result.get("evidence_graph", {}),
            validation_report=result.get("validation", {}),
            synthesized_answer=result.get("synthesized_answer", ""),
            human_readable_output=result.get("human_readable_output", ""),
            graph_statistics=result.get("graph_statistics", {}),
            provenance=provenance,
        )
    
    def _validate_input_cardinality(self, micro_answers: list[MicroAnswer]) -> None:
        """Validate exactly 300 input micro-answers."""
        if len(micro_answers) != MICRO_ANSWER_COUNT:
            error = ERROR_CODES["E2002"]
            raise NexusIntegrationError(
                error_code=error.code,
                message=error.message_template.format(
                    expected=MICRO_ANSWER_COUNT,
                    actual=len(micro_answers),
                ),
                details={
                    "expected": MICRO_ANSWER_COUNT,
                    "actual": len(micro_answers),
                }
            )
    
    def _transform_to_method_outputs(
        self,
        micro_answers: list[MicroAnswer],
    ) -> dict[str, Any]:
        """
        Transform micro-answers to method outputs format.
        
        EvidenceNexus expects method_outputs as:
        {
            "method_name": {
                "output": <result>,
                "metadata": {...},
            },
            ...
        }
        
        We group micro-answers by chunk_id and create synthetic method outputs.
        """
        method_outputs: dict[str, Any] = {}
        
        # Group by chunk_id
        by_chunk: dict[str, list[MicroAnswer]] = {}
        for answer in micro_answers:
            if answer.chunk_id not in by_chunk:
                by_chunk[answer.chunk_id] = []
            by_chunk[answer.chunk_id].append(answer)
        
        # Create method outputs from grouped answers
        for chunk_id, answers in by_chunk.items():
            # Sort by shard_index for deterministic ordering
            sorted_answers = sorted(answers, key=lambda a: a.shard_index)
            
            method_outputs[f"carver_chunk_{chunk_id}"] = {
                "output": {
                    "content": " ".join(a.content for a in sorted_answers),
                    "shards": [
                        {
                            "task_id": a.task_id,
                            "shard_index": a.shard_index,
                            "content": a.content,
                            "content_hash": a.content_hash,
                        }
                        for a in sorted_answers
                    ],
                },
                "metadata": {
                    "chunk_id": chunk_id,
                    "pa_code": sorted_answers[0].pa_code if sorted_answers else "",
                    "dim_code": sorted_answers[0].dim_code if sorted_answers else "",
                    "shard_count": len(sorted_answers),
                },
            }
        
        logger.info(
            "Transformed micro-answers to method outputs",
            extra={
                "micro_answer_count": len(micro_answers),
                "method_output_count": len(method_outputs),
            }
        )
        
        return method_outputs
    
    def _get_nexus(self):
        """Get or create EvidenceNexus instance (lazy loading)."""
        if self._nexus is None:
            try:
                from src.farfan_pipeline.phases.Phase_two.evidence_nexus import EvidenceNexus
                
                self._nexus = EvidenceNexus(
                    storage_path=self._storage_path,
                    enable_persistence=self._enable_persistence,
                    citation_threshold=self._citation_threshold,
                )
            except ImportError as e:
                raise NexusIntegrationError(
                    error_code="E2006",
                    message="Cannot import EvidenceNexus",
                    details={"error": str(e)}
                ) from e
        
        return self._nexus
    
    def _build_provenance(
        self,
        micro_answers: list[MicroAnswer],
        nexus_result: dict[str, Any],
    ) -> dict[str, str]:
        """
        Build provenance mapping from evidence nodes to micro-answers.
        
        Maps evidence_id (from graph) -> micro_answer.task_id
        """
        provenance: dict[str, str] = {}
        
        # Build task_id -> chunk_id mapping
        task_to_chunk = {a.task_id: a.chunk_id for a in micro_answers}
        
        # Extract evidence nodes from graph
        evidence_graph = nexus_result.get("evidence_graph", {})
        nodes = evidence_graph.get("nodes", [])
        
        for node in nodes:
            node_id = node.get("node_id", "")
            source_method = node.get("source_method", "")
            
            # If source_method references a carver chunk, map to task_id
            if source_method.startswith("carver_chunk_"):
                chunk_id = source_method.replace("carver_chunk_", "")
                # Find the first task_id for this chunk
                for task_id, cid in task_to_chunk.items():
                    if cid == chunk_id:
                        provenance[node_id] = task_id
                        break
        
        return provenance


# === PUBLIC API ===

def integrate_with_nexus(
    micro_answers: list[MicroAnswer],
    question_context: dict[str, Any],
    contract: dict[str, Any],
    storage_path: Path | None = None,
    enable_persistence: bool = False,
) -> NexusResult:
    """
    Public API for integrating micro-answers with EvidenceNexus.
    
    Args:
        micro_answers: Exactly 300 micro-answers from carver
        question_context: Question context with expected_elements
        contract: Executor contract specification
        storage_path: Optional path for persistent storage
        enable_persistence: Whether to persist evidence graph
        
    Returns:
        NexusResult with evidence graph and synthesized narrative
        
    Raises:
        NexusIntegrationError: If integration fails
    """
    integrator = NexusIntegrator(
        storage_path=storage_path,
        enable_persistence=enable_persistence,
    )
    return integrator.integrate(micro_answers, question_context, contract)
