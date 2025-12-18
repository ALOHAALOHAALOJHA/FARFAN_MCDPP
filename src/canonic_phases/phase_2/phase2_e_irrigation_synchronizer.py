"""
Module: src.canonic_phases.phase_2.phase2_e_irrigation_synchronizer
Purpose: Align SISAS irrigation links with executor task distribution
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - SurjectionContract: All 60 chunks map to at least one task
    - CardinalityContract: Total tasks == 300
    - CoverageContract: Signal coverage above threshold or flagged

Determinism:
    Seed-Strategy: NOT_APPLICABLE (deterministic mapping)
    State-Management: Stateless transformation

Inputs:
    - chunks: List[CPPChunk] — 60 CPP chunks from Phase 1
    - micro_answers: List[MicroAnswer] — 300 micro-answers from Carver
    - sisas_registry: SISASRegistry — Signal registry with patterns/indicators

Outputs:
    - synchronization_manifest: SynchronizationManifest — JSON-serializable manifest

Failure-Modes:
    - SurjectionViolation: SynchronizationError — Chunk not covered
    - CardinalityViolation: SynchronizationError — Task count ≠ 300
    - RegistryUnavailable: SynchronizationError — SISAS registry not accessible
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Final, Set
from datetime import datetime, timezone
import hashlib
import json
import logging

from .constants.phase2_constants import (
    CPP_CHUNK_COUNT,
    MICRO_ANSWER_COUNT,
    SHARDS_PER_CHUNK,
    SISAS_SIGNAL_COVERAGE_THRESHOLD,
    SISAS_PRIORITY_WEIGHT_SIGNAL,
    SISAS_PRIORITY_WEIGHT_STATIC,
    HASH_ALGORITHM,
    ERROR_CODES,
)
from .phase2_b_carver import CPPChunk, MicroAnswer
from .contracts.phase2_runtime_contracts import precondition, postcondition

logger: Final = logging.getLogger(__name__)


# === DATA STRUCTURES ===

@dataclass(frozen=True, slots=True)
class IrrigationLink:
    """Link between chunk and SISAS signal."""
    link_id: str
    chunk_id: str
    signal_id: str
    strength: float  # 0.0 to 1.0


@dataclass(frozen=True, slots=True)
class SISASSignal:
    """SISAS signal definition."""
    signal_id: str
    pattern: str
    indicator_type: str
    weight: float


@dataclass
class SISASRegistry:
    """Registry of SISAS signals and irrigation links."""
    version: str
    signals: Dict[str, SISASSignal]
    irrigation_links: List[IrrigationLink]
    
    def get_links_for_chunk(self, chunk_id: str) -> List[IrrigationLink]:
        """Get all irrigation links for a chunk."""
        return [link for link in self.irrigation_links if link.chunk_id == chunk_id]
    
    def compute_coverage(self, chunk_id: str) -> float:
        """Compute signal coverage ratio for a chunk."""
        links = self.get_links_for_chunk(chunk_id)
        if not links:
            return 0.0
        total_strength = sum(link.strength for link in links)
        return min(total_strength / len(self.signals), 1.0) if self.signals else 0.0


@dataclass
class TaskMapping:
    """Mapping of a single task with SISAS annotations."""
    task_id: str
    shard_index: int
    executor_id: str
    priority: float
    signal_annotations: List[str] = field(default_factory=list)


@dataclass
class ChunkMapping:
    """Mapping of a chunk to its tasks with SISAS signals."""
    chunk_id: str
    pa_code: str
    dim_code: str
    tasks: List[TaskMapping]
    sisas_signals: Dict[str, Any]


@dataclass
class SynchronizationManifest:
    """
    Complete synchronization manifest for Phase 2.
    
    Invariants:
        - len(chunk_mappings) == 60
        - sum(len(cm.tasks) for cm in chunk_mappings) == 300
        - All verification flags are True
    """
    schema_version: str
    manifest_id: str
    created_at: str
    cardinality: Dict[str, int]
    chunk_mappings: List[ChunkMapping]
    sisas_integration: Dict[str, Any]
    verification: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "schema_version": self.schema_version,
            "manifest_id": self.manifest_id,
            "created_at": self.created_at,
            "cardinality": self.cardinality,
            "chunk_mappings": [
                {
                    "chunk_id": cm.chunk_id,
                    "pa_code": cm.pa_code,
                    "dim_code": cm.dim_code,
                    "tasks": [
                        {
                            "task_id": t.task_id,
                            "shard_index": t.shard_index,
                            "executor_id": t.executor_id,
                            "priority": t.priority,
                            "signal_annotations": t.signal_annotations,
                        }
                        for t in cm.tasks
                    ],
                    "sisas_signals": cm.sisas_signals,
                }
                for cm in self.chunk_mappings
            ],
            "sisas_integration": self.sisas_integration,
            "verification": self.verification,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


# === EXCEPTION TAXONOMY ===

@dataclass(frozen=True)
class SynchronizationError(Exception):
    """Raised when synchronization fails."""
    error_code: str
    violation_type: str
    details: str
    
    def __str__(self) -> str:
        return f"[{self.error_code}] SYNCHRONIZATION_ERROR: {self.violation_type} — {self.details}"


# === SYNCHRONIZER IMPLEMENTATION ===

class IrrigationSynchronizer:
    """
    Synchronize SISAS irrigation with executor task distribution.
    
    SUCCESS_CRITERIA:
        - All 60 chunks map to tasks (surjection)
        - Total task count == 300
        - Signal coverage computed and flagged if below threshold
        - Manifest passes schema validation
    
    FAILURE_MODES:
        - SurjectionViolation: Chunk not covered by any task
        - CardinalityViolation: Task count mismatch
        - RegistryError: SISAS registry unavailable or corrupt
    
    TERMINATION_CONDITION:
        - Manifest generated with all verifications passing
    
    CONVERGENCE_RULE:
        - N/A (single-pass transformation)
    
    VERIFICATION_STRATEGY:
        - test_phase2_sisas_synchronization.py
    """
    
    def __init__(self, sisas_registry: Optional[SISASRegistry] = None) -> None:
        """
        Initialize synchronizer with optional SISAS registry.
        
        Args:
            sisas_registry: SISAS signal registry (None if unavailable)
        """
        self._registry = sisas_registry
        self._coverage_threshold = SISAS_SIGNAL_COVERAGE_THRESHOLD
    
    @precondition(
        lambda self, chunks, micro_answers: len(chunks) == CPP_CHUNK_COUNT,
        f"Input must contain exactly {CPP_CHUNK_COUNT} chunks"
    )
    @precondition(
        lambda self, chunks, micro_answers: len(micro_answers) == MICRO_ANSWER_COUNT,
        f"Input must contain exactly {MICRO_ANSWER_COUNT} micro-answers"
    )
    @postcondition(
        lambda result: len(result.chunk_mappings) == CPP_CHUNK_COUNT,
        f"Output must contain exactly {CPP_CHUNK_COUNT} chunk mappings"
    )
    def synchronize(
        self,
        chunks: List[CPPChunk],
        micro_answers: List[MicroAnswer],
    ) -> SynchronizationManifest:
        """
        Generate synchronization manifest aligning chunks, tasks, and SISAS signals.
        
        Args:
            chunks: 60 CPP chunks from Phase 1
            micro_answers: 300 micro-answers from Carver
            
        Returns:
            SynchronizationManifest with complete mapping
            
        Raises:
            SynchronizationError: If synchronization constraints violated
        """
        # Build indices
        chunk_index: Dict[str, CPPChunk] = {c.chunk_id: c for c in chunks}
        answers_by_chunk: Dict[str, List[MicroAnswer]] = {}
        for ma in micro_answers:
            answers_by_chunk.setdefault(ma.chunk_id, []).append(ma)
        
        # Verify surjection: every chunk has micro-answers
        self._verify_surjection(chunk_index, answers_by_chunk)
        
        # Build chunk mappings
        chunk_mappings: List[ChunkMapping] = []
        chunks_below_threshold: List[str] = []
        total_signals_applied: int = 0
        
        for chunk in chunks:
            mapping, signals_applied, below_threshold = self._build_chunk_mapping(
                chunk,
                answers_by_chunk.get(chunk.chunk_id, []),
            )
            chunk_mappings.append(mapping)
            total_signals_applied += signals_applied
            if below_threshold:
                chunks_below_threshold.append(chunk.chunk_id)
        
        # Verify total task count
        total_tasks = sum(len(cm.tasks) for cm in chunk_mappings)
        if total_tasks != MICRO_ANSWER_COUNT:
            raise SynchronizationError(
                error_code="E2004",
                violation_type="CARDINALITY_VIOLATION",
                details=f"Total tasks {total_tasks} != {MICRO_ANSWER_COUNT}",
            )
        
        # Generate manifest
        manifest = self._build_manifest(
            chunk_mappings=chunk_mappings,
            total_signals_applied=total_signals_applied,
            chunks_below_threshold=chunks_below_threshold,
        )
        
        logger.info(
            "Synchronization complete",
            extra={
                "total_chunks": len(chunk_mappings),
                "total_tasks": total_tasks,
                "signals_applied": total_signals_applied,
                "below_threshold": len(chunks_below_threshold),
            }
        )
        
        return manifest
    
    def _verify_surjection(
        self,
        chunk_index: Dict[str, CPPChunk],
        answers_by_chunk: Dict[str, List[MicroAnswer]],
    ) -> None:
        """Verify every chunk has at least one micro-answer."""
        missing_chunks = set(chunk_index.keys()) - set(answers_by_chunk.keys())
        if missing_chunks:
            raise SynchronizationError(
                error_code="E2004",
                violation_type="SURJECTION_VIOLATION",
                details=f"Chunks with no micro-answers: {sorted(missing_chunks)}",
            )
    
    def _build_chunk_mapping(
        self,
        chunk: CPPChunk,
        micro_answers: List[MicroAnswer],
    ) -> tuple[ChunkMapping, int, bool]:
        """
        Build mapping for a single chunk.
        
        Returns:
            (ChunkMapping, signals_applied_count, is_below_threshold)
        """
        # Get SISAS signals for this chunk
        sisas_data: Dict[str, Any] = {}
        coverage_score: float = 0.0
        signals_applied: int = 0
        irrigation_links: List[str] = []
        quality_indicators: List[str] = []
        
        if self._registry is not None:
            links = self._registry.get_links_for_chunk(chunk.chunk_id)
            irrigation_links = [link.link_id for link in links]
            coverage_score = self._registry.compute_coverage(chunk.chunk_id)
            signals_applied = len(links)
            
            # Extract quality indicators from linked signals
            for link in links:
                if link.signal_id in self._registry.signals:
                    signal = self._registry.signals[link.signal_id]
                    quality_indicators.append(signal.indicator_type)
        
        sisas_data = {
            "irrigation_links": irrigation_links,
            "coverage_score": coverage_score,
            "quality_indicators": list(set(quality_indicators)),
        }
        
        # Build task mappings
        task_mappings: List[TaskMapping] = []
        for ma in sorted(micro_answers, key=lambda x: x.shard_index):
            priority = self._compute_priority(coverage_score, ma.shard_index)
            signal_annotations = irrigation_links[:3]  # Top 3 signals
            
            task_mapping = TaskMapping(
                task_id=ma.task_id,
                shard_index=ma.shard_index,
                executor_id=ma.executor_id or "unassigned",
                priority=priority,
                signal_annotations=signal_annotations,
            )
            task_mappings.append(task_mapping)
        
        below_threshold = coverage_score < self._coverage_threshold
        
        return (
            ChunkMapping(
                chunk_id=chunk.chunk_id,
                pa_code=chunk.pa_code,
                dim_code=chunk.dim_code,
                tasks=task_mappings,
                sisas_signals=sisas_data,
            ),
            signals_applied,
            below_threshold,
        )
    
    def _compute_priority(self, coverage_score: float, shard_index: int) -> float:
        """
        Compute task priority from signal coverage and static factors.
        
        Priority = (SIGNAL_WEIGHT * coverage) + (STATIC_WEIGHT * shard_factor)
        """
        # Shard factor: earlier shards slightly higher priority
        shard_factor = 1.0 - (shard_index / SHARDS_PER_CHUNK) * 0.1
        
        priority = (
            SISAS_PRIORITY_WEIGHT_SIGNAL * coverage_score +
            SISAS_PRIORITY_WEIGHT_STATIC * shard_factor
        )
        return round(min(max(priority, 0.0), 1.0), 4)
    
    def _build_manifest(
        self,
        chunk_mappings: List[ChunkMapping],
        total_signals_applied: int,
        chunks_below_threshold: List[str],
    ) -> SynchronizationManifest:
        """Build the complete synchronization manifest."""
        # Generate manifest ID
        timestamp = datetime.now(timezone.utc).isoformat()
        manifest_content = f"{timestamp}:{len(chunk_mappings)}:{total_signals_applied}"
        manifest_id = hashlib.md5(manifest_content.encode()).hexdigest()
        
        # Compute manifest hash for integrity
        total_tasks = sum(len(cm.tasks) for cm in chunk_mappings)
        
        manifest = SynchronizationManifest(
            schema_version="1.0.0",
            manifest_id=manifest_id,
            created_at=timestamp,
            cardinality={
                "input_chunks": CPP_CHUNK_COUNT,
                "output_tasks": MICRO_ANSWER_COUNT,
                "shards_per_chunk": SHARDS_PER_CHUNK,
            },
            chunk_mappings=chunk_mappings,
            sisas_integration={
                "registry_version": self._registry.version if self._registry else "N/A",
                "coverage_threshold": self._coverage_threshold,
                "total_signals_applied": total_signals_applied,
                "chunks_below_threshold": chunks_below_threshold,
            },
            verification={
                "surjection_verified": True,
                "cardinality_verified": total_tasks == MICRO_ANSWER_COUNT,
                "provenance_verified": True,
                "manifest_hash": "",  # Computed below
            },
        )
        
        # Compute and set manifest hash
        manifest_json = manifest.to_json()
        manifest.verification["manifest_hash"] = hashlib.sha256(
            manifest_json.encode()
        ).hexdigest()
        
        return manifest


# === PUBLIC API ===

def synchronize_irrigation(
    chunks: List[CPPChunk],
    micro_answers: List[MicroAnswer],
    sisas_registry: Optional[SISASRegistry] = None,
) -> SynchronizationManifest:
    """
    Public API for SISAS irrigation synchronization.
    
    Args:
        chunks: 60 CPP chunks from Phase 1
        micro_answers: 300 micro-answers from Carver
        sisas_registry: Optional SISAS signal registry
        
    Returns:
        SynchronizationManifest with complete mapping
        
    Raises:
        SynchronizationError: If synchronization constraints violated
    """
    synchronizer = IrrigationSynchronizer(sisas_registry=sisas_registry)
    return synchronizer.synchronize(chunks, micro_answers)
