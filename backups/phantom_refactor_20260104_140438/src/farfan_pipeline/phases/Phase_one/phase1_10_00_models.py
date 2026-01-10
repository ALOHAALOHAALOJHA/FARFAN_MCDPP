"""
Phase 1 Models - Strict Data Structures
=======================================

Data models for the Phase 1 SPC Ingestion Execution Contract.
These models enforce strict typing and validation for the pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from .PHASE_1_CONSTANTS import (
    VALID_ASSIGNMENT_METHODS,
    ASSIGNMENT_METHOD_SEMANTIC,
    ASSIGNMENT_METHOD_FALLBACK,
    CHUNK_ID_PATTERN,
)

# CANONICAL TYPE IMPORTS from farfan_pipeline.core.types
# These provide the authoritative PolicyArea and DimensionCausal enums
try:
    from farfan_pipeline.core.types import PolicyArea, DimensionCausal

    CANONICAL_TYPES_AVAILABLE = True
except ImportError:
    CANONICAL_TYPES_AVAILABLE = False
    PolicyArea = None  # type: ignore
    DimensionCausal = None  # type: ignore


@dataclass
class LanguageData:
    """
    Output of SP0 - Language Detection.
    """

    primary_language: str
    secondary_languages: List[str]
    confidence_scores: Dict[str, float]
    detection_method: str
    normalized_text: Optional[str] = None
    _sealed: bool = False


@dataclass
class PreprocessedDoc:
    """
    Output of SP1 - Advanced Preprocessing.
    """

    tokens: List[Any] = field(default_factory=list)
    sentences: List[Any] = field(default_factory=list)
    paragraphs: List[Any] = field(default_factory=list)
    normalized_text: str = ""
    original_to_normalized_mapping: Dict[Tuple[int, int], Tuple[int, int]] = field(
        default_factory=dict
    )
    _hash: str = ""


@dataclass
class StructureData:
    """
    Output of SP2 - Structural Analysis.
    """

    sections: List[Any] = field(default_factory=list)
    hierarchy: Dict[str, Optional[str]] = field(default_factory=dict)
    paragraph_mapping: Dict[int, str] = field(default_factory=dict)
    unassigned_paragraphs: List[int] = field(default_factory=list)
    tables: List[Any] = field(default_factory=list)
    lists: List[Any] = field(default_factory=list)

    @property
    def paragraph_to_section(self) -> Dict[int, str]:
        """Alias for paragraph_mapping per FORCING ROUTE [EXEC-SP2-005]."""
        return self.paragraph_mapping


@dataclass
class KGNode:
    """Node in the Knowledge Graph."""

    id: str
    type: str
    text: str
    signal_tags: List[str] = field(default_factory=list)
    signal_importance: float = 0.0
    policy_area_relevance: Dict[str, float] = field(default_factory=dict)


@dataclass
class KGEdge:
    """Edge in the Knowledge Graph."""

    source: str
    target: str
    type: str
    weight: float = 1.0


@dataclass
class KnowledgeGraph:
    """
    Output of SP3 - Knowledge Graph Construction.
    """

    nodes: List[KGNode] = field(default_factory=list)
    edges: List[KGEdge] = field(default_factory=list)
    span_to_node_mapping: Dict[Tuple[int, int], str] = field(default_factory=dict)


@dataclass
class CausalGraph:
    """Local causal graph for a chunk."""

    events: List[Any] = field(default_factory=list)
    causes: List[Any] = field(default_factory=list)
    effects: List[Any] = field(default_factory=list)


@dataclass
class Chunk:
    """
    Intermediate chunk representation (SP4-SP10).
    Type-safe enum fields added for proper value aggregation in CPP production cycle.
    """

    chunk_id: str = ""
    policy_area_id: str = ""
    dimension_id: str = ""
    chunk_index: int = -1

    # Raw chunk text (optional, used by some verifiers/tests)
    text: str = ""

    # Type-safe enum fields for value aggregation in CPP cycle
    policy_area: Optional[Any] = None  # PolicyArea enum when available
    dimension: Optional[Any] = None  # DimensionCausal enum when available

    text_spans: List[Tuple[int, int]] = field(default_factory=list)
    sentence_ids: List[int] = field(default_factory=list)
    paragraph_ids: List[int] = field(default_factory=list)

    signal_tags: List[str] = field(default_factory=list)
    signal_scores: Dict[str, float] = field(default_factory=dict)

    # Traceability fields (SPEC-002)
    assignment_method: str = "semantic"
    semantic_confidence: float = 0.0

    overlap_flag: bool = False
    segmentation_metadata: Dict[str, Any] = field(default_factory=dict)

    # Enrichment fields (populated in SP5-SP10)
    causal_graph: Optional[CausalGraph] = None
    arguments: Optional[Dict[str, Any]] = None
    temporal_markers: Optional[Dict[str, Any]] = None
    discourse_mode: str = ""
    rhetorical_strategies: List[str] = field(default_factory=list)
    signal_patterns: List[str] = field(default_factory=list)

    signal_weighted_importance: float = 0.0
    policy_area_priority: float = 0.0
    risk_weight: float = 0.0
    governance_threshold: float = 0.0

    def __post_init__(self) -> None:
        # REMEDIATION: Validate SPEC-002 Traceability (parity with SmartChunk)
        if self.assignment_method not in VALID_ASSIGNMENT_METHODS:
            raise ValueError(
                f"Invalid assignment_method: {self.assignment_method}. "
                f"Must be one of {VALID_ASSIGNMENT_METHODS}"
            )
        if not (0.0 <= self.semantic_confidence <= 1.0):
            raise ValueError(
                f"Invalid semantic_confidence: {self.semantic_confidence}. "
                f"Must be in range [0.0, 1.0]"
            )

        # Derive PA/DIM ids from chunk_id when not explicitly provided.
        if self.chunk_id and (not self.policy_area_id or not self.dimension_id):
            parts = self.chunk_id.split("-")
            if len(parts) == 2 and parts[0] and parts[1]:
                if not self.policy_area_id:
                    self.policy_area_id = parts[0]
                if not self.dimension_id:
                    self.dimension_id = parts[1]


@dataclass
class CausalChains:
    """Output of SP5."""

    chains: List[Any] = field(default_factory=list)
    mechanisms: List[str] = field(default_factory=list)
    per_chunk_causal: Dict[str, Any] = field(default_factory=dict)

    @property
    def causal_chains(self) -> List[Any]:
        """Alias per FORCING ROUTE [EXEC-SP5-002]."""
        return self.chains


@dataclass
class IntegratedCausal:
    """Output of SP6."""

    global_graph: Any = None
    validated_hierarchy: bool = False
    cross_chunk_links: List[Any] = field(default_factory=list)
    teoria_cambio_status: str = ""

    @property
    def integrated_causal(self) -> Any:
        """Alias per FORCING ROUTE [EXEC-SP6-002]."""
        return self.global_graph


@dataclass
class Arguments:
    """Output of SP7."""

    premises: List[Any] = field(default_factory=list)
    conclusions: List[Any] = field(default_factory=list)
    reasoning: List[Any] = field(default_factory=list)
    per_chunk_args: Dict[str, Any] = field(default_factory=dict)

    # Legacy field kept for backward compatibility (some modules expect a dict map).
    arguments_map: Dict[str, Any] = field(default_factory=dict)

    @property
    def argumentative_structure(self) -> Dict[str, Any]:
        """Alias per FORCING ROUTE [EXEC-SP7-002]."""
        if self.arguments_map:
            return self.arguments_map
        return {
            "premises": self.premises,
            "conclusions": self.conclusions,
            "reasoning": self.reasoning,
            "per_chunk_args": self.per_chunk_args,
        }


@dataclass
class Temporal:
    """Output of SP8."""

    time_markers: List[Any] = field(default_factory=list)
    sequences: List[Any] = field(default_factory=list)
    durations: List[Any] = field(default_factory=list)
    per_chunk_temporal: Dict[str, Any] = field(default_factory=dict)

    @property
    def temporal_markers(self) -> List[Any]:
        """Alias per FORCING ROUTE [EXEC-SP8-002]."""
        return self.time_markers


@dataclass
class Discourse:
    """Output of SP9."""

    markers: List[Any] = field(default_factory=list)
    patterns: List[Any] = field(default_factory=list)
    coherence: Dict[str, Any] = field(default_factory=dict)
    per_chunk_discourse: Dict[str, Any] = field(default_factory=dict)

    @property
    def discourse_structure(self) -> Dict[str, Any]:
        """Alias per FORCING ROUTE [EXEC-SP9-002]."""
        return {
            "markers": self.markers,
            "patterns": self.patterns,
            "coherence": self.coherence,
            "per_chunk_discourse": self.per_chunk_discourse,
        }


@dataclass
class Strategic:
    """Output of SP10."""

    strategic_rank: Dict[str, int] = field(default_factory=dict)
    priorities: List[Any] = field(default_factory=list)
    integrated_view: Dict[str, Any] = field(default_factory=dict)
    strategic_scores: Dict[str, Any] = field(default_factory=dict)

    @property
    def strategic_integration(self) -> Dict[str, float]:
        """Alias per FORCING ROUTE [EXEC-SP10-002]."""
        # Prefer integrated view if present; otherwise fall back to scores.
        return self.integrated_view or self.strategic_scores  # type: ignore[return-value]


@dataclass(frozen=True)
class SmartChunk:
    """
    Final chunk representation (SP11-SP15).
    FOUNDATIONAL: chunk_id is PRIMARY identifier (PA##-DIM##)
    policy_area_id and dimension_id are AUTO-DERIVED from chunk_id

    Type-safe enum fields added for proper value aggregation in CPP production cycle.
    """

    chunk_id: str
    text: str = ""
    chunk_type: str = "semantic"
    source_page: Optional[int] = None
    chunk_index: int = -1

    # Accept explicit IDs for compatibility/tests; they are validated/overridden from chunk_id.
    policy_area_id: str = ""
    dimension_id: str = ""

    # Type-safe enum fields for value aggregation in CPP cycle
    policy_area: Optional[Any] = field(default=None, init=False)  # PolicyArea enum when available
    dimension: Optional[Any] = field(
        default=None, init=False
    )  # DimensionCausal enum when available

    causal_graph: CausalGraph = field(default_factory=CausalGraph)
    temporal_markers: Dict[str, Any] = field(default_factory=dict)
    arguments: Dict[str, Any] = field(default_factory=dict)
    discourse_mode: str = "unknown"
    strategic_rank: int = 0
    irrigation_links: List[Any] = field(default_factory=list)

    signal_tags: List[str] = field(default_factory=list)
    signal_scores: Dict[str, float] = field(default_factory=dict)
    signal_version: str = "v1.0.0"

    # Traceability fields (SPEC-002)
    assignment_method: str = "semantic"
    semantic_confidence: float = 0.0

    rank_score: float = 0.0
    signal_weighted_score: float = 0.0

    def __post_init__(self):
        # Validate SPEC-002 Traceability
        if self.assignment_method not in VALID_ASSIGNMENT_METHODS:
            raise ValueError(f"Invalid assignment_method: {self.assignment_method}")
        if not (0.0 <= self.semantic_confidence <= 1.0):
            raise ValueError(f"Invalid semantic_confidence: {self.semantic_confidence}")

        if not re.match(CHUNK_ID_PATTERN, self.chunk_id):
            raise ValueError(
                f"Invalid chunk_id format: {self.chunk_id}. Must match {CHUNK_ID_PATTERN}"
            )

        parts = self.chunk_id.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid chunk_id structure: {self.chunk_id}")

        pa_part, dim_part = parts
        # Only auto-derive if not explicitly provided (tests may inject mismatches).
        if not self.policy_area_id:
            object.__setattr__(self, "policy_area_id", pa_part)
        if not self.dimension_id:
            object.__setattr__(self, "dimension_id", dim_part)

        # Convert string IDs to enum types when available for type-safe aggregation
        if CANONICAL_TYPES_AVAILABLE and PolicyArea is not None and DimensionCausal is not None:
            try:
                # Map PA01-PA10 to PolicyArea enum
                pa_enum = getattr(PolicyArea, pa_part, None)
                if pa_enum:
                    object.__setattr__(self, "policy_area", pa_enum)

                # Map DIM01-DIM06 to DimensionCausal enum
                dim_mapping = {
                    "DIM01": DimensionCausal.DIM01_INSUMOS,
                    "DIM02": DimensionCausal.DIM02_ACTIVIDADES,
                    "DIM03": DimensionCausal.DIM03_PRODUCTOS,
                    "DIM04": DimensionCausal.DIM04_RESULTADOS,
                    "DIM05": DimensionCausal.DIM05_IMPACTOS,
                    "DIM06": DimensionCausal.DIM06_CAUSALIDAD,
                }
                dim_enum = dim_mapping.get(dim_part)
                if dim_enum:
                    object.__setattr__(self, "dimension", dim_enum)
            except (AttributeError, KeyError):
                # If enum conversion fails, keep as None (degraded mode)
                pass


@dataclass
class ValidationResult:
    """Output of SP13 - Integrity Validation."""

    status: str = "INVALID"
    chunk_count: int = 0
    checked_count: int = 0
    passed_count: int = 0
    violations: List[str] = field(default_factory=list)
    pa_dim_coverage: str = "INCOMPLETE"
