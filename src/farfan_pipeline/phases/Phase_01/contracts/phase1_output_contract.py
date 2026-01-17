"""Phase 1 Output Contract - Phase 1 → Phase 2 Interface.

This contract defines the strict postconditions for Phase 1 exit.
Output is delivered to Phase 2 as CanonPolicyPackage (CPP).

Postconditions (enforced):
- POST-01: Exactly 60 chunks produced (10 PA × 6 Dim)
- POST-02: All chunks have valid PA and Dimension assignments
- POST-03: Chunk graph is acyclic (DAG)
- POST-04: CPP metadata contains complete execution trace (16 entries)
- POST-05: Quality metrics present for all chunks
- POST-06: Schema version matches CPP-2025.1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List


@dataclass(frozen=True)
class Phase1OutputPostcondition:
    """Postcondition specification for Phase 1 output."""
    postcondition_id: str
    description: str
    validation_function: str
    severity: str  # "CRITICAL", "HIGH", "STANDARD"


PHASE1_OUTPUT_POSTCONDITIONS: List[Phase1OutputPostcondition] = [
    Phase1OutputPostcondition(
        "POST-01",
        "Exactly 60 chunks must be produced (10 Policy Areas × 6 Dimensions)",
        "validate_chunk_count",
        "CRITICAL"
    ),
    Phase1OutputPostcondition(
        "POST-02",
        "All chunks must have valid Policy Area and Dimension assignments",
        "validate_chunk_assignments",
        "CRITICAL"
    ),
    Phase1OutputPostcondition(
        "POST-03",
        "Chunk graph must be acyclic (DAG property)",
        "validate_dag_acyclicity",
        "CRITICAL"
    ),
    Phase1OutputPostcondition(
        "POST-04",
        "CPP metadata must contain complete execution trace (16 subphase entries)",
        "validate_execution_trace",
        "HIGH"
    ),
    Phase1OutputPostcondition(
        "POST-05",
        "Quality metrics must be present for all chunks",
        "validate_quality_metrics",
        "HIGH"
    ),
    Phase1OutputPostcondition(
        "POST-06",
        "Schema version must match CPP-2025.1",
        "validate_schema_version",
        "STANDARD"
    ),
]


def validate_phase1_output_contract(cpp: Any) -> bool:
    """Validate Phase 1 output contract compliance.
    
    Args:
        cpp: CanonPolicyPackage from Phase 1
        
    Returns:
        True if all postconditions satisfied
        
    Raises:
        ValueError: If any postcondition fails
    """
    # POST-01: Exactly 60 chunks
    chunk_count = len(cpp.chunk_graph.chunks)
    if chunk_count != 60:
        raise ValueError(f"POST-01 failed: Expected 60 chunks, got {chunk_count}")
    
    # POST-02: All chunks have valid PA and Dimension
    from farfan_pipeline.phases.Phase_01.phase1_models import SmartChunk
    for chunk in cpp.chunk_graph.chunks:
        if not isinstance(chunk, SmartChunk):
            raise ValueError(f"POST-02 failed: Chunk {chunk.chunk_id} is not a SmartChunk")
        if chunk.policy_area is None or chunk.dimension is None:
            raise ValueError(f"POST-02 failed: Chunk {chunk.chunk_id} missing PA or Dimension")
    
    # POST-03: DAG acyclicity
    edges = cpp.chunk_graph.edges
    visited = set()
    rec_stack = set()
    
    def has_cycle(node_id: str) -> bool:
        visited.add(node_id)
        rec_stack.add(node_id)
        for edge in edges:
            if edge.source_id == node_id:
                target = edge.target_id
                if target not in visited:
                    if has_cycle(target):
                        return True
                elif target in rec_stack:
                    return True
        rec_stack.remove(node_id)
        return False
    
    for chunk in cpp.chunk_graph.chunks:
        if chunk.chunk_id not in visited:
            if has_cycle(chunk.chunk_id):
                raise ValueError(f"POST-03 failed: Chunk graph contains cycle")
    
    # POST-04: Execution trace
    if len(cpp.metadata.execution_trace) != 16:
        raise ValueError(f"POST-04 failed: Expected 16 execution trace entries, got {len(cpp.metadata.execution_trace)}")
    
    # POST-05: Quality metrics
    if not cpp.quality_metrics:
        raise ValueError(f"POST-05 failed: Quality metrics missing")
    
    # POST-06: Schema version
    if cpp.metadata.schema_version != "CPP-2025.1":
        raise ValueError(f"POST-06 failed: Expected schema version CPP-2025.1, got {cpp.metadata.schema_version}")
    
    return True


__all__ = [
    "Phase1OutputPostcondition",
    "PHASE1_OUTPUT_POSTCONDITIONS",
    "validate_phase1_output_contract",
]
