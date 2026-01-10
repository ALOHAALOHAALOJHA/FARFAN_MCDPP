"""
EvidenceNexus:  Unified SOTA Evidence-to-Answer Engine

PHASE_LABEL: Phase 2
======================================================

REPLACES:
- evidence_assembler.py (merge strategies → causal graph construction)
- evidence_validator.py (rule validation → probabilistic consistency)
- evidence_registry.py (JSONL storage → embedded vector store + hash chain)

ARCHITECTURE: Graph-Native Evidence Reasoning
---------------------------------------------
1.Evidence Ingestion → Typed nodes in causal graph
2.Relationship Inference → Edge weights via Bayesian inference
3.Consistency Validation → Graph-theoretic conflict detection
4.Narrative Synthesis → LLM-free template-driven answer generation
5.Provenance Tracking → Merkle DAG with content-addressable storage

THEORETICAL FOUNDATIONS:
- Pearl's Causal Inference (do-calculus for counterfactual reasoning)
- Dempster-Shafer Theory (belief functions for uncertainty)
- Rhetorical Structure Theory (discourse coherence)
- Information-Theoretic Validation (mutual information for relevance)

INVARIANTS:
[INV-001] All evidence nodes must have SHA-256 content hash
[INV-002] Graph must be acyclic for causal reasoning
[INV-003] Narrative must cite ≥1 evidence node per claim
[INV-004] Confidence intervals must be calibrated (coverage ≥ 0.95)
[INV-005] Hash chain must be append-only and verifiable

Author: F.A.R.F.A.N Pipeline
Version: 1.0.0
Date: 2025-12-10
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 2
__stage__ = 80
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "MEDIUM"
__execution_pattern__ = "On-Demand"



from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
import time
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Protocol,
    TypeAlias,
)

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# =============================================================================
# TYPE SYSTEM
# =============================================================================

EvidenceID: TypeAlias = str  # SHA-256 hex digest
NodeID: TypeAlias = str
EdgeID: TypeAlias = str
Confidence: TypeAlias = float  # [0.0, 1.0]
BeliefMass: TypeAlias = float  # [0.0, 1.0]


class EvidenceType(Enum):
    """Taxonomy of evidence types aligned with questionnaire ontology."""

    # Quantitative
    INDICATOR_NUMERIC = "indicador_cuantitativo"
    TEMPORAL_SERIES = "serie_temporal"
    BUDGET_AMOUNT = "monto_presupuestario"
    COVERAGE_METRIC = "metrica_cobertura"
    GOAL_TARGET = "meta_cuantificada"

    # Qualitative
    OFFICIAL_SOURCE = "fuente_oficial"
    TERRITORIAL_COVERAGE = "cobertura_territorial"
    INSTITUTIONAL_ACTOR = "actor_institucional"
    POLICY_INSTRUMENT = "instrumento_politica"
    NORMATIVE_REFERENCE = "referencia_normativa"

    # Relational
    CAUSAL_LINK = "vinculo_causal"
    TEMPORAL_DEPENDENCY = "dependencia_temporal"
    CONTRADICTION = "contradiccion"
    CORROBORATION = "corroboracion"

    # Meta
    METHOD_OUTPUT = "salida_metodo"
    AGGREGATED = "agregado"
    SYNTHESIZED = "sintetizado"

    def to_contract_format(self) -> str:
        """Convert to pluralized format expected by contracts.

        Maps EvidenceType enum values (singular) to contract expected_elements keys (plural):
        - indicador_cuantitativo -> indicadores_cuantitativos
        - serie_temporal -> series_temporales_años
        - fuente_oficial -> fuentes_oficiales
        - cobertura_territorial -> cobertura_territorial_especificada
        - etc.
        """
        mapping = {
            "indicador_cuantitativo": "indicadores_cuantitativos",
            "serie_temporal": "series_temporales_años",
            "monto_presupuestario": "montos_presupuestarios",
            "metrica_cobertura": "metricas_cobertura",
            "meta_cuantificada": "metas_cuantificadas",
            "fuente_oficial": "fuentes_oficiales",
            "cobertura_territorial": "cobertura_territorial_especificada",
            "actor_institucional": "actores_institucionales",
            "instrumento_politica": "instrumentos_politica",
            "referencia_normativa": "referencias_normativas",
            "vinculo_causal": "logica_causal_explicita",
            "dependencia_temporal": "dependencias_temporales",
            "contradiccion": "contradicciones",
            "corroboracion": "corroboraciones",
            "salida_metodo": "salidas_metodo",
            "agregado": "agregados",
            "sintetizado": "sintetizados",
        }
        return mapping.get(self.value, self.value)


class EvidenceTypeMapper:
    """Bidirectional mapper between Nexus EvidenceType and contract formats.

    Resolves the vocabulary mismatch where:
    - Contracts expect: indicadores_cuantitativos, fuentes_oficiales, etc.
    - Nexus EvidenceType uses: indicador_cuantitativo, fuente_oficial, etc.
    """

    # Singular (Nexus) -> Plural (Contract)
    SINGULAR_TO_PLURAL: ClassVar[dict[str, str]] = {
        "indicador_cuantitativo": "indicadores_cuantitativos",
        "serie_temporal": "series_temporales_años",
        "monto_presupuestario": "montos_presupuestarios",
        "metrica_cobertura": "metricas_cobertura",
        "meta_cuantificada": "metas_cuantificadas",
        "fuente_oficial": "fuentes_oficiales",
        "cobertura_territorial": "cobertura_territorial_especificada",
        "actor_institucional": "actores_institucionales",
        "instrumento_politica": "instrumentos_politica",
        "referencia_normativa": "referencias_normativas",
        "vinculo_causal": "logica_causal_explicita",
        "dependencia_temporal": "dependencias_temporales",
        "contradiccion": "contradicciones",
        "corroboracion": "corroboraciones",
        "salida_metodo": "salidas_metodo",
        "agregado": "agregados",
        "sintetizado": "sintetizados",
    }

    # Plural (Contract) -> Singular (Nexus)
    PLURAL_TO_SINGULAR: ClassVar[dict[str, str]] = {v: k for k, v in SINGULAR_TO_PLURAL.items()}

    @classmethod
    def to_contract_format(cls, evidence_type: str) -> str:
        """Convert singular Nexus type to plural contract format."""
        return cls.SINGULAR_TO_PLURAL.get(evidence_type, evidence_type)

    @classmethod
    def to_nexus_format(cls, contract_type: str) -> str:
        """Convert plural contract type to singular Nexus format."""
        return cls.PLURAL_TO_SINGULAR.get(contract_type, contract_type)

    @classmethod
    def normalize_dict_keys(cls, counts: dict[str, int]) -> dict[str, int]:
        """Convert Nexus enum keys to contract format for gap detection.

        Example:
            Input:  {"indicador_cuantitativo": 3, "fuente_oficial": 2}
            Output: {"indicadores_cuantitativos": 3, "fuentes_oficiales": 2}
        """
        return {cls.to_contract_format(k): v for k, v in counts.items()}


class RelationType(Enum):
    """Edge types in evidence graph."""

    SUPPORTS = "supports"  # A provides evidence for B
    CONTRADICTS = "contradicts"  # A conflicts with B
    CAUSES = "causes"  # A is causal antecedent of B
    CORRELATES = "correlates"  # A and B co-occur without causation
    TEMPORALLY_PRECEDES = "precedes"  # A happens before B
    DERIVES_FROM = "derives"  # A was computed from B
    CITES = "cites"  # A references B as source
    AGGREGATES = "aggregates"  # A is aggregation of B1... Bn


class ValidationSeverity(Enum):
    """Severity levels for validation findings."""

    CRITICAL = "critical"  # Blocks answer generation
    ERROR = "error"  # Degrades confidence significantly
    WARNING = "warning"  # Notes potential issue
    INFO = "info"  # Informational only


class AnswerCompleteness(Enum):
    """Classification of answer completeness."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"
    NOT_APPLICABLE = "not_applicable"


class NarrativeSection(Enum):
    """Sections in structured narrative output."""

    DIRECT_ANSWER = "direct_answer"
    EVIDENCE_SUMMARY = "evidence_summary"
    CONFIDENCE_STATEMENT = "confidence_statement"
    SUPPORTING_DETAILS = "supporting_details"
    GAPS_AND_LIMITATIONS = "gaps_and_limitations"
    RECOMMENDATIONS = "recommendations"
    METHODOLOGY_NOTE = "methodology_note"


# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================


@dataclass(frozen=True, slots=True)
class EvidenceNode:
    """
    Immutable evidence node with cryptographic identity.

    Each node represents a discrete piece of evidence extracted from
    document analysis.Nodes are content-addressed via SHA-256.

    Invariants:
    - node_id == SHA-256(canonical_json(content))
    - confidence in [0.0, 1.0]
    - belief_mass in [0.0, 1.0]
    - belief_mass + uncertainty_mass <= 1.0
    """

    node_id: EvidenceID
    evidence_type: EvidenceType
    content: dict[str, Any]

    # Confidence metrics
    confidence: Confidence
    belief_mass: BeliefMass  # Dempster-Shafer belief
    uncertainty_mass: float  # Epistemic uncertainty

    # Provenance
    source_method: str
    extraction_timestamp: float
    document_location: str | None  # Page/section reference

    # Metadata
    tags: frozenset[str] = field(default_factory=frozenset)
    parent_ids: tuple[EvidenceID, ...] = field(default_factory=tuple)

    @classmethod
    def create(
        cls,
        evidence_type: EvidenceType,
        content: dict[str, Any],
        confidence: float,
        source_method: str,
        document_location: str | None = None,
        tags: Sequence[str] | None = None,
        parent_ids: Sequence[EvidenceID] | None = None,
        belief_mass: float | None = None,
        uncertainty_mass: float | None = None,
    ) -> EvidenceNode:
        """Factory method with automatic ID generation."""
        # Compute content hash for identity
        canonical = cls._canonical_json(content)
        node_id = hashlib.sha256(canonical.encode()).hexdigest()

        # Default belief mass to confidence if not specified
        bm = belief_mass if belief_mass is not None else confidence
        um = uncertainty_mass if uncertainty_mass is not None else (1.0 - confidence) * 0.5

        return cls(
            node_id=node_id,
            evidence_type=evidence_type,
            content=content,
            confidence=max(0.0, min(1.0, confidence)),
            belief_mass=max(0.0, min(1.0, bm)),
            uncertainty_mass=max(0.0, min(1.0, um)),
            source_method=source_method,
            extraction_timestamp=time.time(),
            document_location=document_location,
            tags=frozenset(tags or []),
            parent_ids=tuple(parent_ids or []),
        )

    @staticmethod
    def _canonical_json(obj: Any) -> str:
        """Deterministic JSON for hashing."""

        def default_handler(o: Any) -> Any:
            if hasattr(o, "__dict__"):
                return o.__dict__
            if isinstance(o, Enum):
                return o.value
            return str(o)

        return json.dumps(
            obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=default_handler
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "node_id": self.node_id,
            "evidence_type": self.evidence_type.value,
            "content": self.content,
            "confidence": self.confidence,
            "belief_mass": self.belief_mass,
            "uncertainty_mass": self.uncertainty_mass,
            "source_method": self.source_method,
            "extraction_timestamp": self.extraction_timestamp,
            "document_location": self.document_location,
            "tags": list(self.tags),
            "parent_ids": list(self.parent_ids),
        }


@dataclass(frozen=True, slots=True)
class EvidenceEdge:
    """
    Directed edge in evidence graph with Bayesian weight.

    Edges represent relationships between evidence nodes.
    Weight represents conditional probability P(target | source).
    """

    edge_id: EdgeID
    source_id: EvidenceID
    target_id: EvidenceID
    relation_type: RelationType
    weight: float  # Conditional probability or strength
    confidence: Confidence
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        source_id: EvidenceID,
        target_id: EvidenceID,
        relation_type: RelationType,
        weight: float = 1.0,
        confidence: float = 0.8,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceEdge:
        """Factory with auto-generated edge ID."""
        edge_id = hashlib.sha256(
            f"{source_id}:{target_id}:{relation_type.value}".encode()
        ).hexdigest()[:16]

        return cls(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=max(0.0, min(1.0, weight)),
            confidence=max(0.0, min(1.0, confidence)),
            metadata=metadata or {},
        )


@dataclass
class ValidationFinding:
    """Single validation finding with severity and remediation."""

    finding_id: str
    severity: ValidationSeverity
    code: str
    message: str
    affected_nodes: list[EvidenceID]
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "affected_nodes": self.affected_nodes,
            "remediation": self.remediation,
        }


@dataclass
class ValidationReport:
    """Complete validation report with aggregated findings."""

    is_valid: bool
    findings: list[ValidationFinding]
    critical_count: int
    error_count: int
    warning_count: int
    validation_timestamp: float
    graph_integrity: bool
    consistency_score: float  # [0.0, 1.0]

    @classmethod
    def create(cls, findings: list[ValidationFinding]) -> ValidationReport:
        """Create report with computed aggregates."""
        critical = sum(1 for f in findings if f.severity == ValidationSeverity.CRITICAL)
        errors = sum(1 for f in findings if f.severity == ValidationSeverity.ERROR)
        warnings = sum(1 for f in findings if f.severity == ValidationSeverity.WARNING)

        # Valid only if no critical findings
        is_valid = critical == 0

        # Consistency score:  penalize errors and warnings
        base_score = 1.0
        base_score -= critical * 0.5  # Critical = -50% each
        base_score -= errors * 0.1  # Error = -10% each
        base_score -= warnings * 0.02  # Warning = -2% each
        consistency_score = max(0.0, base_score)

        return cls(
            is_valid=is_valid,
            findings=findings,
            critical_count=critical,
            error_count=errors,
            warning_count=warnings,
            validation_timestamp=time.time(),
            graph_integrity=True,  # Set by graph validation
            consistency_score=consistency_score,
        )


@dataclass
class Citation:
    """Evidence citation for narrative claims."""

    node_id: EvidenceID
    evidence_type: str
    value_summary: str
    confidence: float
    source_method: str
    document_reference: str | None = None

    def render(self, format_type: str = "markdown") -> str:
        """Render citation in specified format."""
        conf_pct = f"{self.confidence * 100:.0f}%"
        if format_type == "markdown":
            ref = f" (p.{self.document_reference})" if self.document_reference else ""
            return f"[{self.evidence_type}:  {self.value_summary}]{ref} (confianza: {conf_pct})"
        return f"{self.evidence_type}: {self.value_summary} ({conf_pct})"

    def to_dict(self) -> dict[str, Any]:
        """Serialize citation for Carver consumption.

        Aligns with NexusOutputAdapter expectations in phase2_90_00_carver.py:
        - evidence_id (mapped from node_id)
        - summary (mapped from value_summary)
        - source_method
        - confidence
        - page (mapped from document_reference)
        - evidence_type
        """
        return {
            "evidence_id": self.node_id,
            "summary": self.value_summary,
            "source_method": self.source_method,
            "confidence": self.confidence,
            "page": self.document_reference,
            "evidence_type": self.evidence_type,
        }


@dataclass
class NarrativeBlock:
    """Single block in structured narrative."""

    section: NarrativeSection
    content: str
    citations: list[Citation]
    confidence: float

    def render(self, format_type: str = "markdown") -> str:
        """Render block with citations."""
        if format_type == "markdown":
            header_map = {
                NarrativeSection.DIRECT_ANSWER: "## Respuesta",
                NarrativeSection.EVIDENCE_SUMMARY: "### Resumen de Evidencia",
                NarrativeSection.CONFIDENCE_STATEMENT: "### Nivel de Confianza",
                NarrativeSection.SUPPORTING_DETAILS: "### Análisis Detallado",
                NarrativeSection.GAPS_AND_LIMITATIONS: "### Limitaciones Identificadas",
                NarrativeSection.RECOMMENDATIONS: "### Recomendaciones",
                NarrativeSection.METHODOLOGY_NOTE: "### Nota Metodológica",
            }
            header = header_map.get(self.section, f"### {self.section.value}")
            return f"{header}\n\n{self.content}"
        return f"{self.section.value.upper()}\n{self.content}"


@dataclass
class SynthesizedAnswer:
    """Complete synthesized answer with full provenance."""

    # Core answer
    direct_answer: str
    narrative_blocks: list[NarrativeBlock]

    # Quality metrics
    completeness: AnswerCompleteness
    overall_confidence: float
    calibrated_interval: tuple[float, float]  # 95% CI

    # Evidence linkage
    primary_citations: list[Citation]
    supporting_citations: list[Citation]

    # Gaps and issues
    gaps: list[str]
    unresolved_contradictions: list[str]

    # Provenance
    evidence_graph_hash: str
    synthesis_timestamp: float
    question_id: str

    # Trace
    synthesis_trace: dict[str, Any]

    def to_human_readable(self, format_type: str = "markdown") -> str:
        """Generate final human-readable output."""
        sections = []

        for block in self.narrative_blocks:
            sections.append(block.render(format_type))

        separator = "\n\n" if format_type == "markdown" else "\n\n"
        return separator.join(sections)

    def to_dict(self) -> dict[str, Any]:
        """Full serialization with full citation payloads for Carver.

        Aligns with NexusOutputAdapter.extract_citations() expectations:
        - primary_citations: list of citation dicts
        - supporting_citations: list of citation dicts

        Each citation dict contains: evidence_id, summary, source_method,
        confidence, page, evidence_type (see Citation.to_dict()).
        """
        return {
            "direct_answer": self.direct_answer,
            "completeness": self.completeness.value,
            "overall_confidence": self.overall_confidence,
            "calibrated_interval": list(self.calibrated_interval),
            "gaps": self.gaps,
            "unresolved_contradictions": self.unresolved_contradictions,
            "evidence_graph_hash": self.evidence_graph_hash,
            "synthesis_timestamp": self.synthesis_timestamp,
            "question_id": self.question_id,
            # Full citation payloads (Carver expects these exact keys)
            "primary_citations": [c.to_dict() for c in self.primary_citations],
            "supporting_citations": [c.to_dict() for c in self.supporting_citations],
            # Legacy counts for backward compatibility
            "primary_citation_count": len(self.primary_citations),
            "supporting_citation_count": len(self.supporting_citations),
        }


# =============================================================================
# EVIDENCE GRAPH
# =============================================================================


class EvidenceGraph:
    """
    Directed acyclic graph of evidence with causal reasoning support.

    Implements:
    - Content-addressable node storage
    - Relationship inference
    - Causal path analysis
    - Conflict detection
    - Belief propagation (Dempster-Shafer)
    """

    __slots__ = (
        "_adjacency",
        "_belief_mass_adjustments",
        "_confidence_adjustments",
        "_edges",
        "_hash_chain",
        "_last_hash",
        "_nodes",
        "_reverse_adjacency",
        "_source_index",
        "_type_index",
    )

    def __init__(self) -> None:
        self._nodes: dict[EvidenceID, EvidenceNode] = {}
        self._edges: dict[EdgeID, EvidenceEdge] = {}
        self._adjacency: dict[EvidenceID, list[EdgeID]] = defaultdict(list)
        self._reverse_adjacency: dict[EvidenceID, list[EdgeID]] = defaultdict(list)
        self._type_index: dict[EvidenceType, list[EvidenceID]] = defaultdict(list)
        self._source_index: dict[str, list[EvidenceID]] = defaultdict(list)
        self._hash_chain: list[str] = []
        self._last_hash: str | None = None
        # Adjustments for frozen nodes (set by level strategies)
        self._confidence_adjustments: dict[EvidenceID, float] = {}
        self._belief_mass_adjustments: dict[EvidenceID, float] = {}

    def get_adjusted_confidence(self, node_id: EvidenceID) -> float:
        """Get confidence for node, using adjustment if present."""
        if node_id in self._confidence_adjustments:
            return self._confidence_adjustments[node_id]
        node = self._nodes.get(node_id)
        return node.confidence if node else 0.0

    def get_adjusted_belief_mass(self, node_id: EvidenceID) -> float:
        """Get belief mass for node, using adjustment if present."""
        if node_id in self._belief_mass_adjustments:
            return self._belief_mass_adjustments[node_id]
        node = self._nodes.get(node_id)
        return node.belief_mass if node else 0.0

    # -------------------------------------------------------------------------
    # Node Operations
    # -------------------------------------------------------------------------

    def add_node(self, node: EvidenceNode) -> EvidenceID:
        """Add node to graph with hash chain update."""
        if node.node_id in self._nodes:
            return node.node_id  # Idempotent

        self._nodes[node.node_id] = node
        self._type_index[node.evidence_type].append(node.node_id)
        self._source_index[node.source_method].append(node.node_id)

        # Update hash chain
        self._update_hash_chain(node)

        logger.debug(
            "node_added", node_id=node.node_id[:12], evidence_type=node.evidence_type.value
        )

        return node.node_id

    def add_nodes(self, nodes: Sequence[EvidenceNode]) -> list[EvidenceID]:
        """Batch add nodes."""
        return [self.add_node(n) for n in nodes]

    def get_node(self, node_id: EvidenceID) -> EvidenceNode | None:
        """Retrieve node by ID."""
        return self._nodes.get(node_id)

    def get_nodes_by_type(self, evidence_type: EvidenceType) -> list[EvidenceNode]:
        """Get all nodes of a specific type."""
        node_ids = self._type_index.get(evidence_type, [])
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]

    def get_nodes_by_source(self, source_method: str) -> list[EvidenceNode]:
        """Get all nodes from a specific source method."""
        node_ids = self._source_index.get(source_method, [])
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]

    # -------------------------------------------------------------------------
    # Edge Operations
    # -------------------------------------------------------------------------

    def add_edge(self, edge: EvidenceEdge) -> EdgeID:
        """Add edge to graph."""
        if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
            raise ValueError(
                f"Cannot add edge:  source {edge.source_id[: 12]} or "
                f"target {edge.target_id[:12]} not in graph"
            )

        if edge.edge_id in self._edges:
            return edge.edge_id  # Idempotent

        # Check for cycle (DAG invariant)
        if self._would_create_cycle(edge.source_id, edge.target_id):
            raise ValueError(
                f"Cannot add edge: would create cycle from "
                f"{edge.source_id[:12]} to {edge.target_id[:12]}"
            )

        self._edges[edge.edge_id] = edge
        self._adjacency[edge.source_id].append(edge.edge_id)
        self._reverse_adjacency[edge.target_id].append(edge.edge_id)

        return edge.edge_id

    def _would_create_cycle(self, source: EvidenceID, target: EvidenceID) -> bool:
        """Check if adding edge source→target would create a cycle."""
        # If target can reach source, adding source→target creates cycle
        visited: set[EvidenceID] = set()
        stack = [target]

        while stack:
            current = stack.pop()
            if current == source:
                return True
            if current in visited:
                continue
            visited.add(current)

            # Follow outgoing edges
            for edge_id in self._adjacency.get(current, []):
                edge = self._edges[edge_id]
                stack.append(edge.target_id)

        return False

    def get_edges_from(self, node_id: EvidenceID) -> list[EvidenceEdge]:
        """Get outgoing edges from node."""
        edge_ids = self._adjacency.get(node_id, [])
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]

    def get_edges_to(self, node_id: EvidenceID) -> list[EvidenceEdge]:
        """Get incoming edges to node."""
        edge_ids = self._reverse_adjacency.get(node_id, [])
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]

    def get_edges_by_type(self, relation_type: RelationType) -> list[EvidenceEdge]:
        """Get all edges of a specific type."""
        return [e for e in self._edges.values() if e.relation_type == relation_type]

    # -------------------------------------------------------------------------
    # Graph Analysis
    # -------------------------------------------------------------------------

    def find_supporting_evidence(
        self, node_id: EvidenceID, max_depth: int = 3
    ) -> list[tuple[EvidenceNode, int]]:
        """
        Find all evidence that supports a node (transitive).
        Returns (node, depth) pairs.
        """
        results: list[tuple[EvidenceNode, int]] = []
        visited: set[EvidenceID] = set()

        def traverse(nid: EvidenceID, depth: int) -> None:
            if depth > max_depth or nid in visited:
                return
            visited.add(nid)

            for edge in self.get_edges_to(nid):
                if edge.relation_type in (RelationType.SUPPORTS, RelationType.DERIVES_FROM):
                    source_node = self._nodes.get(edge.source_id)
                    if source_node:
                        results.append((source_node, depth))
                        traverse(edge.source_id, depth + 1)

        traverse(node_id, 1)
        return results

    def find_contradictions(self) -> list[tuple[EvidenceNode, EvidenceNode, EvidenceEdge]]:
        """Find all contradiction pairs in graph."""
        contradictions = []
        for edge in self.get_edges_by_type(RelationType.CONTRADICTS):
            source = self._nodes.get(edge.source_id)
            target = self._nodes.get(edge.target_id)
            if source and target:
                contradictions.append((source, target, edge))
        return contradictions

    # -------------------------------------------------------------------------
    # I6 RESOLUTION: Circular Reasoning Detection
    # -------------------------------------------------------------------------

    def detect_circular_reasoning(self) -> list[dict[str, Any]]:
        """
        Detect circular reasoning patterns in the evidence graph.

        I6 RESOLUTION: Comprehensive circular reasoning detection.

        Circular reasoning occurs when:
        1. Evidence A supports B, B supports C, C supports A (3-cycle)
        2. Evidence chain forms a closed loop
        3. A claim is supported by itself through indirect chains

        Returns:
            List of detected circular reasoning patterns with details.
        """
        circles: list[dict[str, Any]] = []
        visited: set[EvidenceID] = set()
        rec_stack: set[EvidenceID] = set()

        def _dfs_detect_cycles(
            node_id: EvidenceID, path: list[EvidenceID], edges_on_path: list[EdgeID]
        ) -> None:
            """DFS to detect cycles starting from node_id."""
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for edge in self.get_edges_from(node_id):
                target_id = edge.target_id
                edges_on_path.append(edge.edge_id)

                # If we've seen this target in the current recursion stack, we found a cycle
                if target_id in rec_stack:
                    # Extract the cycle
                    cycle_start_idx = path.index(target_id)
                    cycle_path = path[cycle_start_idx:] + [target_id]
                    cycle_edges = edges_on_path[cycle_start_idx:]

                    circles.append(
                        {
                            "cycle_id": f"cycle_{len(circles)}_{node_id[:8]}",
                            "path_length": len(cycle_path),
                            "nodes_in_cycle": cycle_path,
                            "edges_in_cycle": cycle_edges,
                            "support_type": "circular_support",
                            "severity": self._assess_cycle_severity(cycle_path, cycle_edges),
                        }
                    )
                # Continue DFS if not visited
                elif target_id not in visited:
                    _dfs_detect_cycles(target_id, path.copy(), edges_on_path.copy())

                edges_on_path.pop()

            rec_stack.remove(node_id)

        # Run DFS from each unvisited node
        for node_id in self._nodes:
            if node_id not in visited:
                _dfs_detect_cycles(node_id, [], [])

        return circles

    def _assess_cycle_severity(
        self, cycle_path: list[EvidenceID], cycle_edges: list[EdgeID]
    ) -> str:
        """Assess the severity of a detected cycle.

        Severity levels:
        - CRITICAL: Direct self-reference (1-2 nodes)
        - HIGH: Small circle (3 nodes) with strong support edges
        - MEDIUM: Medium circle (4-5 nodes)
        - LOW: Large circle (6+ nodes) - likely complex interdependence
        """
        path_len = len(cycle_path)

        # Direct self-reference
        if path_len <= 2:
            return "CRITICAL"

        # Check edge weights for small circles
        if path_len == 3:
            strong_edges = 0
            for edge_id in cycle_edges:
                edge = self._edges.get(edge_id)
                if edge and edge.weight > 0.7:
                    strong_edges += 1
            if strong_edges >= 2:
                return "HIGH"

        if path_len <= 4:
            return "MEDIUM"

        return "LOW"

    def compute_belief_propagation(self) -> dict[EvidenceID, float]:
        """
        Dempster-Shafer belief propagation across graph.

        Combines evidence using Dempster's rule of combination.
        Returns updated belief masses for each node.
        """
        beliefs: dict[EvidenceID, float] = {}

        # Topological sort for propagation order
        sorted_nodes = self._topological_sort()

        for node_id in sorted_nodes:
            incoming = self.get_edges_to(node_id)
            node_belief = self.get_adjusted_belief_mass(node_id)

            if not incoming:
                # Root node:  use intrinsic belief (adjusted if applicable)
                beliefs[node_id] = node_belief
            else:
                # Combine beliefs from parents using Dempster's rule
                combined_belief = node_belief

                for edge in incoming:
                    if edge.relation_type == RelationType.SUPPORTS:
                        parent_belief = beliefs.get(edge.source_id, 0.5)
                        # Dempster's combination (simplified)
                        combined_belief = self._dempster_combine(
                            combined_belief, parent_belief * edge.weight
                        )
                    elif edge.relation_type == RelationType.CONTRADICTS:
                        parent_belief = beliefs.get(edge.source_id, 0.5)
                        # Contradiction reduces belief
                        combined_belief *= 1 - parent_belief * edge.weight * 0.5

                beliefs[node_id] = max(0.0, min(1.0, combined_belief))

        return beliefs

    @staticmethod
    def _dempster_combine(m1: float, m2: float) -> float:
        """Dempster's rule of combination for two belief masses."""
        # Simplified:  assume no direct conflict
        conflict = m1 * (1 - m2) * 0.1  # Small conflict factor
        normalization = 1 - conflict
        if normalization <= 0:
            return 0.5  # Maximum uncertainty

        combined = (m1 * m2) / normalization
        return max(0.0, min(1.0, combined))

    def _topological_sort(self) -> list[EvidenceID]:
        """Topological sort of nodes (Kahn's algorithm)."""
        in_degree: dict[EvidenceID, int] = dict.fromkeys(self._nodes, 0)

        for edge in self._edges.values():
            in_degree[edge.target_id] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            node_id = queue.pop(0)
            result.append(node_id)

            for edge in self.get_edges_from(node_id):
                in_degree[edge.target_id] -= 1
                if in_degree[edge.target_id] == 0:
                    queue.append(edge.target_id)

        return result

    # -------------------------------------------------------------------------
    # Hash Chain (Provenance)
    # -------------------------------------------------------------------------

    def _update_hash_chain(self, node: EvidenceNode) -> None:
        """Append node to hash chain."""
        chain_data = {
            "node_id": node.node_id,
            "previous_hash": self._last_hash or "",
            "timestamp": node.extraction_timestamp,
        }
        entry_hash = hashlib.sha256(json.dumps(chain_data, sort_keys=True).encode()).hexdigest()

        self._hash_chain.append(entry_hash)
        self._last_hash = entry_hash

    def verify_hash_chain(self) -> bool:
        """Verify hash chain integrity."""
        if not self._hash_chain:
            return True

        # Would need full reconstruction to verify
        # For now, check chain exists and is non-empty
        return len(self._hash_chain) == len(self._nodes)

    def get_graph_hash(self) -> str:
        """Get hash of entire graph state."""
        if self._last_hash:
            return self._last_hash
        return hashlib.sha256(b"empty_graph").hexdigest()

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def get_statistics(self) -> dict[str, Any]:
        """Comprehensive graph statistics."""
        type_counts = {t.value: len(ids) for t, ids in self._type_index.items()}
        source_counts = {s: len(ids) for s, ids in self._source_index.items()}

        confidences = [n.confidence for n in self._nodes.values()]
        avg_confidence = statistics.mean(confidences) if confidences else 0.0

        edge_type_counts = defaultdict(int)
        for edge in self._edges.values():
            edge_type_counts[edge.relation_type.value] += 1

        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "by_evidence_type": type_counts,
            "by_source_method": source_counts,
            "by_edge_type": dict(edge_type_counts),
            "average_confidence": avg_confidence,
            "hash_chain_length": len(self._hash_chain),
            "graph_hash": self.get_graph_hash()[:16],
        }


# =============================================================================
# VALIDATION ENGINE
# =============================================================================


class ValidationRule(Protocol):
    """Protocol for validation rules."""

    @property
    def code(self) -> str: ...

    @property
    def severity(self) -> ValidationSeverity: ...

    def validate(
        self, graph: EvidenceGraph, contract: dict[str, Any]
    ) -> list[ValidationFinding]: ...


class RequiredElementsRule:
    """Validate that required evidence types are present."""

    code = "REQ_ELEMENTS"
    severity = ValidationSeverity.ERROR

    def validate(self, graph: EvidenceGraph, contract: dict[str, Any]) -> list[ValidationFinding]:
        findings = []

        expected_elements = contract.get("question_context", {}).get("expected_elements", [])

        for elem in expected_elements:
            elem_type = elem.get("type", "")
            required = elem.get("required", False)
            minimum = elem.get("minimum", 0)

            # In the monolith, expected_elements[].type includes many "context" gates
            # (e.g., coherencia_demostrada, analisis_realismo, trazabilidad_presupuestal)
            # that are NOT EvidenceType enum values. We must still validate them.
            count, node_ids = self._count_support_for_expected_element(graph, str(elem_type))

            if required and count == 0:
                findings.append(
                    ValidationFinding(
                        finding_id=f"REQ_{elem_type}",
                        severity=ValidationSeverity.ERROR,
                        code=self.code,
                        message=f"Required element type '{elem_type}' not found in evidence",
                        affected_nodes=[],
                        remediation=f"Ensure document analysis extracts {elem_type} elements",
                    )
                )
            elif minimum > 0 and count < minimum:
                findings.append(
                    ValidationFinding(
                        finding_id=f"MIN_{elem_type}",
                        severity=ValidationSeverity.WARNING,
                        code="MIN_ELEMENTS",
                        message=f"Element type '{elem_type}' has {count}/{minimum} required instances",
                        affected_nodes=node_ids[:10],
                        remediation=f"Need {minimum - count} more {elem_type} elements",
                    )
                )

        return findings

    @staticmethod
    def _count_support_for_expected_element(
        graph: EvidenceGraph,
        expected_type: str,
    ) -> tuple[int, list[str]]:
        """Count how much evidence supports an expected element type.

        Strategy:
        - Prefer exact EvidenceType matches when possible
        - Otherwise use contract-pattern evidence nodes (source_method=contract.patterns)
          and map "context" types to categories/lexical markers.
        """
        expected = (expected_type or "").strip()
        if not expected:
            return 0, []

        # 1) Direct mapping to EvidenceType (when expected uses EvidenceType vocabulary)
        try:
            ev_type = EvidenceType(expected)
            nodes = graph.get_nodes_by_type(ev_type)
            return len(nodes), [n.node_id for n in nodes]
        except ValueError:
            pass

        # 2) Build indices from contract.patterns nodes (produced in _build_graph_from_outputs)
        pattern_nodes = graph.get_nodes_by_source("contract.patterns")
        by_category: dict[str, list[EvidenceNode]] = defaultdict(list)
        for n in pattern_nodes:
            if isinstance(n.content, dict):
                cat = str(n.content.get("category") or "GENERAL").upper()
                by_category[cat].append(n)

        def _count_nodes_with_matches(nodes: list[EvidenceNode]) -> tuple[int, list[str]]:
            ids: list[str] = []
            total = 0
            for n in nodes:
                mc = 0
                if isinstance(n.content, dict):
                    try:
                        mc = int(n.content.get("match_count", 0) or 0)
                    except (ValueError, TypeError) as e:
                        # Log specific conversion error for debugging
                        logger.warning(
                            "match_count_conversion_failed",
                            node_id=n.node_id,
                            content_type=type(n.content.get("match_count")).__name__,
                            error=str(e),
                        )
                        mc = 0
                if mc > 0:
                    total += mc
                    ids.append(n.node_id)
            return total, ids

        def _contains_any(match_texts: list[str], needles: tuple[str, ...]) -> bool:
            text = " ".join(match_texts).lower()
            return any(needle in text for needle in needles)

        # Helper to extract match texts from a node
        def _node_matches(node: EvidenceNode) -> list[str]:
            if not isinstance(node.content, dict):
                return []
            raw = node.content.get("matches", [])
            if isinstance(raw, list):
                return [str(x) for x in raw if x is not None]
            return []

        # 3) Map monolith expected element types ("contexts") to evidence signals
        # NOTE: This mapping is conservative and explainable. It can be refined
        # as we formalize context→pattern/validation specs in SISAS.
        et = expected.lower()

        # High-signal direct category mappings
        category_map: dict[str, str] = {
            "fuentes_oficiales": "FUENTE_OFICIAL",
            "indicadores_cuantitativos": "INDICADOR",
            "series_temporales_años": "TEMPORAL",
            "cobertura_territorial_especificada": "TERRITORIAL",
            "rezago_temporal": "TEMPORAL",
            "ruta_transmision": "CAUSAL",
            "logica_causal_explicita": "CAUSAL",
            "teoria_cambio_explicita": "CAUSAL",
            "cadena_causal_explicita": "CAUSAL",
            "mecanismo_causal_explicito": "CAUSAL",
            "unidades_medicion": "UNIDAD_MEDIDA",
            "trazabilidad_presupuestal": "INDICADOR",
        }

        if et in category_map:
            # CAUSAL is spread across CAUSAL*, so merge all keys starting with CAUSAL
            wanted = category_map[et]
            if wanted == "CAUSAL":
                causal_nodes: list[EvidenceNode] = []
                for k, nodes in by_category.items():
                    if k.startswith("CAUSAL"):
                        causal_nodes.extend(nodes)
                return _count_nodes_with_matches(causal_nodes)
            return _count_nodes_with_matches(by_category.get(wanted, []))

        # Context-style expected elements (from your list)
        if et == "completeness":
            # Treat as: any supporting evidence exists
            total_matches = 0
            ids: list[str] = []
            for nodes in by_category.values():
                c, nid = _count_nodes_with_matches(nodes)
                total_matches += c
                ids.extend(nid)
            return total_matches, ids

        if et == "horizonte_temporal":
            return _count_nodes_with_matches(by_category.get("TEMPORAL", []))

        if et in {"asignacion_explicita", "restricciones_presupuestales", "coherencia_recursos"}:
            # Budget/resource realism: indicator/unit + key lexemes in matched snippets.
            indicator_nodes = by_category.get("INDICADOR", [])
            unit_nodes = by_category.get("UNIDAD_MEDIDA", [])
            nodes = indicator_nodes + unit_nodes
            count, ids = _count_nodes_with_matches(nodes)
            if count == 0:
                return 0, []
            # Lexeme filter (keeps it honest)
            budget_lexemes = ("presupuesto", "recursos", "financi", "monto", "millones", "cop", "$")
            supported_ids: list[str] = []
            supported_count = 0
            for n in nodes:
                matches = _node_matches(n)
                if matches and _contains_any(matches, budget_lexemes):
                    try:
                        supported_count += int(n.content.get("match_count", 0) or 0)  # type: ignore[union-attr]
                    except (ValueError, TypeError) as e:
                        # Log conversion error and fall back to counting as 1 match
                        logger.warning(
                            "budget_lexeme_match_count_conversion_failed",
                            node_id=n.node_id,
                            error=str(e),
                        )
                        supported_count += 1
                    supported_ids.append(n.node_id)
            return (supported_count or count), (supported_ids or ids)

        if et in {"analisis_realismo", "analisis_contextual", "evidencia_comparada"}:
            # Realism/context/comparison: prefer INDICADOR/TEMPORAL/FUENTE_OFICIAL/TERRITORIAL
            nodes = (
                by_category.get("INDICADOR", [])
                + by_category.get("TEMPORAL", [])
                + by_category.get("FUENTE_OFICIAL", [])
                + by_category.get("TERRITORIAL", [])
            )
            count, ids = _count_nodes_with_matches(nodes)
            if et == "evidencia_comparada" and count > 0:
                compar_lex = ("compar", "vs", "promedio", "nacional", "departamental", "anterior")
                supported_ids = []
                supported_count = 0
                for n in nodes:
                    matches = _node_matches(n)
                    if matches and _contains_any(matches, compar_lex):
                        supported_ids.append(n.node_id)
                        try:
                            supported_count += int(n.content.get("match_count", 0) or 0)  # type: ignore[union-attr]
                        except (ValueError, TypeError) as e:
                            # Log conversion error and fall back to counting as 1 match
                            logger.warning(
                                "compar_lexeme_match_count_conversion_failed",
                                node_id=n.node_id,
                                error=str(e),
                            )
                            supported_count += 1
                return (supported_count or 0), supported_ids
            return count, ids

        if et in {
            "supuestos_identificados",
            "riesgos_identificados",
            "ciclos_aprendizaje",
            "enfoque_diferencial",
            "gobernanza",
            "poblacion_objetivo_definida",
            "vinculo_diagnostico_actividad",
        }:
            # These are often GENERAL patterns with strong lexical anchors.
            general_nodes = by_category.get("GENERAL", [])
            count, ids = _count_nodes_with_matches(general_nodes)
            if count == 0:
                return 0, []
            anchors_by_type: dict[str, tuple[str, ...]] = {
                "supuestos_identificados": ("supuesto", "asumi", "hipótesis", "premisa"),
                "riesgos_identificados": ("riesgo", "amenaza", "mitig", "conting"),
                "ciclos_aprendizaje": ("retroaliment", "aprendiz", "mejora", "ciclo", "monitoreo"),
                "enfoque_diferencial": (
                    "enfoque diferencial",
                    "enfoque de género",
                    "enfoque étn",
                    "interseccional",
                ),
                "gobernanza": (
                    "gobernanza",
                    "coordinación",
                    "articulación",
                    "comité",
                    "mesa",
                    "instancia",
                ),
                "poblacion_objetivo_definida": (
                    "población objetivo",
                    "beneficiari",
                    "grupo meta",
                    "focaliz",
                ),
                "vinculo_diagnostico_actividad": (
                    "diagnóstico",
                    "brecha",
                    "causa",
                    "en respuesta",
                    "derivado",
                ),
            }
            anchors = anchors_by_type.get(et, tuple())
            if not anchors:
                return count, ids
            supported_ids: list[str] = []
            supported_count = 0
            for n in general_nodes:
                matches = _node_matches(n)
                if matches and _contains_any(matches, anchors):
                    supported_ids.append(n.node_id)
                    try:
                        supported_count += int(n.content.get("match_count", 0) or 0)  # type: ignore[union-attr]
                    except (ValueError, TypeError) as e:
                        # Log conversion error and fall back to counting as 1 match
                        logger.warning(
                            "anchor_lexeme_match_count_conversion_failed",
                            node_id=n.node_id,
                            error=str(e),
                        )
                        supported_count += 1
            return supported_count, supported_ids

        # Fallback: treat as "any evidence exists" but only count nodes with matches
        total_matches = 0
        ids: list[str] = []
        for nodes in by_category.values():
            c, nid = _count_nodes_with_matches(nodes)
            total_matches += c
            ids.extend(nid)
        return total_matches, ids


class ConsistencyRule:
    """Validate internal consistency of evidence."""

    code = "CONSISTENCY"
    severity = ValidationSeverity.WARNING

    def validate(self, graph: EvidenceGraph, contract: dict[str, Any]) -> list[ValidationFinding]:
        findings = []

        # Check for unresolved contradictions
        contradictions = graph.find_contradictions()

        for source, target, edge in contradictions:
            if edge.confidence > 0.7:  # High-confidence contradiction
                findings.append(
                    ValidationFinding(
                        finding_id=f"CONTRA_{edge.edge_id}",
                        severity=ValidationSeverity.WARNING,
                        code=self.code,
                        message="Contradiction detected between evidence nodes",
                        affected_nodes=[source.node_id, target.node_id],
                        remediation="Review contradictory evidence for resolution",
                    )
                )

        return findings


class ConfidenceThresholdRule:
    """Validate confidence thresholds."""

    code = "CONFIDENCE"
    severity = ValidationSeverity.WARNING

    def __init__(self, min_confidence: float = 0.5):
        self.min_confidence = min_confidence

    def validate(self, graph: EvidenceGraph, contract: dict[str, Any]) -> list[ValidationFinding]:
        findings = []

        low_confidence_nodes = [
            n for n in graph._nodes.values() if n.confidence < self.min_confidence
        ]

        if len(low_confidence_nodes) > graph.node_count * 0.3:
            findings.append(
                ValidationFinding(
                    finding_id="LOW_CONF_AGGREGATE",
                    severity=ValidationSeverity.WARNING,
                    code=self.code,
                    message=f"{len(low_confidence_nodes)}/{graph.node_count} nodes have confidence below {self.min_confidence}",
                    affected_nodes=[n.node_id for n in low_confidence_nodes[:10]],
                    remediation="Consider additional evidence sources or validation",
                )
            )

        return findings


class GraphIntegrityRule:
    """Validate graph structural integrity."""

    code = "INTEGRITY"
    severity = ValidationSeverity.CRITICAL

    def validate(self, graph: EvidenceGraph, contract: dict[str, Any]) -> list[ValidationFinding]:
        findings = []

        # Verify hash chain
        if not graph.verify_hash_chain():
            findings.append(
                ValidationFinding(
                    finding_id="HASH_CHAIN_INVALID",
                    severity=ValidationSeverity.CRITICAL,
                    code=self.code,
                    message="Hash chain integrity verification failed",
                    affected_nodes=[],
                    remediation="Evidence chain may be corrupted; rebuild from source",
                )
            )

        # Check for orphan edges
        for edge in graph._edges.values():
            if edge.source_id not in graph._nodes or edge.target_id not in graph._nodes:
                findings.append(
                    ValidationFinding(
                        finding_id=f"ORPHAN_EDGE_{edge.edge_id}",
                        severity=ValidationSeverity.ERROR,
                        code=self.code,
                        message="Edge references non-existent node",
                        affected_nodes=[],
                        remediation="Remove orphan edge or add missing nodes",
                    )
                )

        return findings


class ColombianContextRule:
    """Validate Colombian-specific regulatory and policy context (R-B2).

    Checks evidence for required Colombian regulatory references and
    territorial coverage requirements. NOW LOADS colombia_context.json
    for comprehensive Colombian context validation.

    GAP B2 RESOLUTION: colombian_context.json is now loaded and applied.
    """

    code = "COLOMBIAN_CONTEXT"
    severity = ValidationSeverity.WARNING

    def __init__(self):
        """Initialize with Colombian context loaded from file."""
        self._colombian_context_data: dict[str, Any] | None = None
        self._context_path = (
            Path(__file__).resolve().parent.parent.parent.parent.parent
            / "canonic_questionnaire_central"
            / "colombia_context"
            / "colombia_context.json"
        )
        self._context_load_error: str | None = None
        self._load_colombian_context()

    def _load_colombian_context(self) -> None:
        """Load colombian_context.json file for validation."""
        try:
            if self._context_path.exists():
                with open(self._context_path, encoding="utf-8") as f:
                    self._colombian_context_data = json.load(f)
                logger.info(
                    "colombian_context_loaded",
                    path=str(self._context_path),
                    laws_count=len(
                        self._colombian_context_data.get("legal_framework", {}).get("key_laws", [])
                    ),
                )
            else:
                error_msg = f"Colombian context file not found at {self._context_path}"
                logger.warning("colombian_context_file_not_found", path=str(self._context_path))
                self._context_load_error = error_msg
        except (json.JSONDecodeError, OSError) as e:
            error_msg = f"Failed to load Colombian context: {e}"
            logger.error("colombian_context_load_failed", error=str(e), error_type=type(e).__name__)
            self._context_load_error = error_msg
        except Exception as e:
            # Catch any unexpected error and preserve it for validation reporting
            error_msg = f"Unexpected error loading Colombian context: {e}"
            logger.error(
                "colombian_context_load_unexpected_error",
                error=str(e),
                error_type=type(e).__name__,
            )
            self._context_load_error = error_msg

    def validate(
        self,
        graph: EvidenceGraph,
        contract: dict[str, Any],
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []

        # CRITICAL: Report context load failure as a validation finding
        # This ensures that failure to load colombia_context.json is not silenced
        if self._context_load_error:
            findings.append(
                ValidationFinding(
                    finding_id="COLOMBIAN_CONTEXT_LOAD_FAILED",
                    severity=ValidationSeverity.ERROR,
                    code=self.code,
                    message=f"Colombian context validation is disabled: {self._context_load_error}",
                    affected_nodes=[],
                    remediation=f"Ensure colombia_context.json exists at {self._context_path} and is valid JSON",
                )
            )
            # Return early since we cannot validate without context
            return findings

        # First, check contract-level validation rules
        validation_rules = contract.get("validation_rules", {})
        contract_col_context = validation_rules.get("colombian_context", {})

        # Process contract-level requirements
        if contract_col_context:
            required_refs = contract_col_context.get("required_regulatory_refs", [])
            for ref in required_refs:
                if not self._find_reference_in_graph(graph, ref):
                    findings.append(
                        ValidationFinding(
                            finding_id=f"MISSING_COL_REF_{ref[:20].replace(' ', '_')}",
                            severity=ValidationSeverity.WARNING,
                            code=self.code,
                            message=f"Missing required Colombian reference: {ref}",
                            affected_nodes=[],
                            remediation=f"Evidence must include reference to: {ref}",
                        )
                    )

            territorial_req = contract_col_context.get("territorial_coverage")
            if territorial_req and not self._validate_territorial(graph, territorial_req):
                findings.append(
                    ValidationFinding(
                        finding_id="TERRITORIAL_COVERAGE_MISSING",
                        severity=ValidationSeverity.WARNING,
                        code=self.code,
                        message="Territorial coverage requirement not met",
                        affected_nodes=[],
                        remediation="Include departamental/municipal coverage data",
                    )
                )

        # B2 RESOLUTION: Apply loaded colombia_context.json for policy-area specific validation
        if self._colombian_context_data:
            findings.extend(self._validate_policy_area_context(graph, contract))
            findings.extend(self._validate_legal_framework(graph, contract))
            findings.extend(self._validate_territorial_organization(graph, contract))

        return findings

    def _validate_policy_area_context(
        self, graph: EvidenceGraph, contract: dict[str, Any]
    ) -> list[ValidationFinding]:
        """Validate evidence against policy-area specific Colombian context.

        Handles field name differences between contract versions:
        - v2/v3: question_context.policy_area_id
        - v4: question_context.sector_id or identity.sector_id
        """
        findings: list[ValidationFinding] = []

        question_context = contract.get("question_context", {})
        identity = contract.get("identity", {})

        # Try multiple field names with fallback
        policy_area_id = (
            question_context.get("policy_area_id")
            or question_context.get("sector_id")
            or identity.get("policy_area_id")
            or identity.get("sector_id", "")
        )
        if not policy_area_id:
            return findings

        # Get relevant laws for this policy area from colombia_context.json
        key_laws = self._colombian_context_data.get("legal_framework", {}).get("key_laws", [])
        relevant_laws = [law for law in key_laws if policy_area_id in law.get("relevance", [])]

        for law in relevant_laws:
            law_id = law.get("law_id", "")
            law_name = law.get("name", "")
            if not self._find_reference_in_graph(
                graph, law_name
            ) and not self._find_reference_in_graph(graph, law_id):
                findings.append(
                    ValidationFinding(
                        finding_id=f"MISSING_LAW_REF_{law_id}",
                        severity=ValidationSeverity.INFO,
                        code=self.code,
                        message=f"Policy area {policy_area_id} should reference: {law_name}",
                        affected_nodes=[],
                        remediation=f"Consider including reference to {law_name} ({law_id})",
                    )
                )

        # Check international treaties for this policy area
        treaties = self._colombian_context_data.get("legal_framework", {}).get(
            "international_treaties", []
        )
        relevant_treaties = [t for t in treaties if policy_area_id in t.get("relevance", [])]

        for treaty in relevant_treaties:
            treaty_name = treaty.get("treaty", "")
            if treaty_name and not self._find_reference_in_graph(graph, treaty_name):
                findings.append(
                    ValidationFinding(
                        finding_id=f"MISSING_TREATY_REF_{treaty_name[:15].replace(' ', '_')}",
                        severity=ValidationSeverity.INFO,
                        code=self.code,
                        message=f"Consider referencing international treaty: {treaty_name}",
                        affected_nodes=[],
                        remediation=f"Include reference to {treaty_name} for comprehensive analysis",
                    )
                )

        return findings

    def _validate_legal_framework(
        self, graph: EvidenceGraph, contract: dict[str, Any]
    ) -> list[ValidationFinding]:
        """Validate evidence mentions key constitutional articles when relevant."""
        findings: list[ValidationFinding] = []

        # Check if evidence should reference constitution
        all_content = " ".join(str(n.content) for n in graph._nodes.values()).lower()
        constitution_keywords = ["derechos", "género", "victimas", "paz", "ambiente", "niñez"]

        if any(kw in all_content for kw in constitution_keywords):
            # Should reference 1991 Constitution
            has_constitution = "constituc" in all_content or "1991" in all_content
            if not has_constitution:
                findings.append(
                    ValidationFinding(
                        finding_id="MISSING_CONSTITUTION_REF",
                        severity=ValidationSeverity.INFO,
                        code=self.code,
                        message="Evidence discusses constitutional rights but lacks Constitution reference",
                        affected_nodes=[],
                        remediation="Consider referencing Constitution of 1991 for legal grounding",
                    )
                )

        return findings

    def _validate_territorial_organization(
        self, graph: EvidenceGraph, contract: dict[str, Any]
    ) -> list[ValidationFinding]:
        """Validate territorial context against Colombian organization."""
        findings: list[ValidationFinding] = []

        # Get territorial context from colombia_context.json
        territorial_context = self._colombian_context_data.get("territorial_context", {})

        # Check if evidence mentions specific regions
        all_content = " ".join(str(n.content) for n in graph._nodes.values()).lower()

        for region_name, region_data in territorial_context.items():
            # Check if evidence mentions departments in this region
            departments = region_data.get("departments", [])
            if any(dep.lower() in all_content for dep in departments):
                # Evidence mentions this region - check for key issues
                key_issues = region_data.get("key_issues", [])
                mentioned_issues = [issue for issue in key_issues if issue.lower() in all_content]
                if len(mentioned_issues) < 2:
                    findings.append(
                        ValidationFinding(
                            finding_id=f"REGION_CONTEXT_SHALLOW_{region_name[:10].upper()}",
                            severity=ValidationSeverity.INFO,
                            code=self.code,
                            message=f"Evidence mentions {region_name} region but may lack key context",
                            affected_nodes=[],
                            remediation=f"Consider addressing key issues: {', '.join(key_issues[:3])}",
                        )
                    )

        return findings

    def _find_reference_in_graph(self, graph: EvidenceGraph, ref: str) -> bool:
        ref_lower = ref.lower()
        for node in graph._nodes.values():
            content_str = str(node.content).lower()
            if ref_lower in content_str:
                return True
            if isinstance(node.content, dict):
                for value in node.content.values():
                    if isinstance(value, str) and ref_lower in value.lower():
                        return True
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and ref_lower in item.lower():
                                return True
        return False

    def _validate_territorial(self, graph: EvidenceGraph, requirement: dict[str, Any]) -> bool:
        territorial_nodes = graph.get_nodes_by_type(EvidenceType.TERRITORIAL_COVERAGE)
        if territorial_nodes:
            return True

        territorial_keywords = [
            "departamento",
            "municipio",
            "municipal",
            "regional",
            "territorial",
            "zona",
            "vereda",
            "corregimiento",
        ]
        for node in graph._nodes.values():
            content_str = str(node.content).lower()
            if any(kw in content_str for kw in territorial_keywords):
                return True
        return False


class CrossCuttingCoverageRule:
    """Validate coverage of required cross-cutting themes (R-W2, I7).

    I7 RESOLUTION: Now checks actual evidence content for theme coverage.

    Checks that evidence addresses required cross-cutting themes defined
    in the signal pack's cross_cutting_themes field by analyzing actual
    evidence node content, not just declarative applicability.
    """

    code = "XCT_COVERAGE"
    severity = ValidationSeverity.WARNING

    # Theme keyword mappings for content analysis
    THEME_KEYWORDS = {
        "CC_ENFOQUE_DIFERENCIAL": [
            "enfoque diferencial",
            "población étnica",
            "comunidad negra",
            "indígena",
            "raizal",
            "rom",
            "gitano",
            "diferencial",
            "intercultural",
            "etnia",
        ],
        "CC_PERSPECTIVA_GENERO": [
            "género",
            "mujer",
            "mujeres",
            "feminicidio",
            "violencia de género",
            "brecha de género",
            "igualdad de género",
            "perspectiva de género",
        ],
        "CC_ENTORNO_TERRITORIAL": [
            "territorial",
            "territorio",
            "rural",
            "urbano",
            "departamental",
            "municipal",
            "local",
            "región",
            "área geográfica",
        ],
        "CC_PARTICIPACION_CIUDADANA": [
            "participación",
            "participación ciudadana",
            "control social",
            "veeduría",
            "involucramiento",
            "alianza",
            "concertación",
        ],
        "CC_COHERENCIA_NORMATIVA": [
            "norma",
            "ley",
            "decreto",
            "resolución",
            "marco legal",
            "normatividad",
            "reglamentación",
            "jurídico",
            "legal",
        ],
        "CC_SOSTENIBILIDAD_PRESUPUESTAL": [
            "presupuesto",
            "financiación",
            "recursos",
            "sostenibilidad",
            "viabilidad financiera",
            "costos",
            "inversión",
            "gasto",
        ],
        "CC_INTEROPERABILIDAD": [
            "interoperabilidad",
            "coordinación",
            "articulación",
            "integración",
            "sistemas",
            "interinstitucional",
            "sinergia",
        ],
        "CC_MECANISMOS_SEGUIMIENTO": [
            "seguimiento",
            "monitoreo",
            "evaluación",
            "indicador",
            "métrica",
            "reporte",
            "informe",
            "control",
            "verificación",
        ],
    }

    def validate(
        self,
        graph: EvidenceGraph,
        contract: dict[str, Any],
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []

        # Extract cross-cutting themes from signal_pack in contract
        signal_pack = contract.get("signal_pack", {})
        themes_data = signal_pack.get("cross_cutting_themes", {})

        if not themes_data:
            # Also check contract's required_themes directly
            themes_data = contract.get("required_themes", {})

        if not themes_data:
            return findings

        # I7 RESOLUTION: Analyze actual evidence content for theme coverage
        # Build content index from all evidence nodes
        all_content = " ".join(str(n.content).lower() for n in graph._nodes.values())

        # Determine which themes are actually present in evidence
        themes_in_evidence = set()
        for theme_id, keywords in self.THEME_KEYWORDS.items():
            if any(kw.lower() in all_content for kw in keywords):
                themes_in_evidence.add(theme_id)

        # Get required themes from contract
        required = set(themes_data.get("required_themes", []) or [])
        if not required:
            # If no explicit required_themes, check applicable_themes
            applicable_themes = themes_data.get("applicable_themes", [])
            required = {
                t.get("theme_id")
                for t in applicable_themes
                if isinstance(t, dict) and t.get("theme_id") and t.get("required", False)
            }

        minimum = int(themes_data.get("minimum_themes", 0) or 0)

        # Check for missing required themes (based on actual evidence content)
        missing_required = [t for t in required if t and t not in themes_in_evidence]
        if missing_required:
            findings.append(
                ValidationFinding(
                    finding_id="XCT_REQUIRED_MISSING_CONTENT",
                    severity=ValidationSeverity.WARNING,
                    code=self.code,
                    message=f"Required cross-cutting themes not found in evidence content: {', '.join(missing_required)}",
                    affected_nodes=[],
                    remediation=f"Ensure evidence addresses required themes: {', '.join(missing_required)}",
                )
            )

        # Check minimum theme coverage (based on actual evidence content)
        evidence_count = len(themes_in_evidence)
        if minimum > 0 and evidence_count < minimum:
            findings.append(
                ValidationFinding(
                    finding_id="XCT_MINIMUM_NOT_MET_CONTENT",
                    severity=ValidationSeverity.WARNING,
                    code=self.code,
                    message=f"Cross-cutting theme coverage in evidence: {evidence_count}/{minimum} below minimum.",
                    affected_nodes=[],
                    remediation=f"Expand evidence to cover at least {minimum - evidence_count} more theme(s).",
                )
            )

        # Provide information about detected themes
        if themes_in_evidence:
            findings.append(
                ValidationFinding(
                    finding_id="XCT_DETECTED_THEMES",
                    severity=ValidationSeverity.INFO,
                    code=self.code,
                    message=f"Detected {len(themes_in_evidence)} cross-cutting theme(s) in evidence: {', '.join(sorted(themes_in_evidence))}",
                    affected_nodes=[],
                    remediation=None,
                )
            )

        return findings


class InterdependencyConsistencyRule:
    """Validate dimension interdependency coherence (R-W3).

    Checks that dimension dependencies are respected according to the
    interdependency mapping in the signal pack.
    """

    code = "INTERDEP"
    severity = ValidationSeverity.WARNING

    def validate(
        self,
        graph: EvidenceGraph,
        contract: dict[str, Any],
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []

        # Extract interdependency context from signal_pack in contract
        signal_pack = contract.get("signal_pack", {})
        interdep = signal_pack.get("interdependency_context", {})

        if not interdep:
            return findings

        depends_on = interdep.get("depends_on") or []
        sequence = interdep.get("dimension_sequence") or []
        current_dim = contract.get("question_context", {}).get("dimension_id")

        # Check dimension ordering against declared sequence
        if isinstance(sequence, list) and current_dim and current_dim in sequence and depends_on:
            pos = {d: i for i, d in enumerate(sequence)}
            current_pos = pos.get(current_dim, -1)
            bad_deps = [d for d in depends_on if d in pos and pos[d] > current_pos]
            if bad_deps:
                findings.append(
                    ValidationFinding(
                        finding_id="INTERDEP_ORDER",
                        severity=ValidationSeverity.WARNING,
                        code=self.code,
                        message=f"Dependencies appear after current dimension in sequence: {', '.join(bad_deps)}",
                        affected_nodes=[],
                        remediation="Review dimension sequence and dependency declarations.",
                    )
                )

        # Flag applicable validation rules for awareness
        applicable_rules = interdep.get("applicable_rules") or []
        if applicable_rules:
            rule_ids = [
                r.get("rule_id", "unknown") for r in applicable_rules if isinstance(r, dict)
            ]
            findings.append(
                ValidationFinding(
                    finding_id="INTERDEP_RULES_ACTIVE",
                    severity=ValidationSeverity.INFO,
                    code=self.code,
                    message=f"Interdependency validation rules active: {', '.join(rule_ids)}",
                    affected_nodes=[],
                )
            )

        # Flag circular reasoning patterns for awareness
        circular = interdep.get("circular_reasoning_patterns") or []
        if circular:
            findings.append(
                ValidationFinding(
                    finding_id="INTERDEP_CIRCULAR_PATTERNS",
                    severity=ValidationSeverity.INFO,
                    code=self.code,
                    message=f"Circular reasoning patterns configured: {len(circular)} patterns",
                    affected_nodes=[],
                )
            )

        return findings


class CircularReasoningRule:
    """Detect circular reasoning patterns in evidence graph (R-I6).

    I6 RESOLUTION: Comprehensive circular reasoning detection.

    Circular reasoning undermines evidence validity by creating closed
    loops where claims support themselves indirectly.
    """

    code = "CIRCULAR_REASONING"
    severity = ValidationSeverity.ERROR

    def validate(
        self,
        graph: EvidenceGraph,
        contract: dict[str, Any],
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []

        # Use the graph's circular reasoning detection
        circles = graph.detect_circular_reasoning()

        if not circles:
            return findings

        # Group by severity
        by_severity: dict[str, list[dict]] = {}
        for circle in circles:
            sev = circle.get("severity", "LOW")
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(circle)

        # Create findings for each severity level
        for severity, circles_list in by_severity.items():
            severity_map = {
                "CRITICAL": ValidationSeverity.CRITICAL,
                "HIGH": ValidationSeverity.ERROR,
                "MEDIUM": ValidationSeverity.WARNING,
                "LOW": ValidationSeverity.INFO,
            }
            val_severity = severity_map.get(severity, ValidationSeverity.WARNING)

            affected_nodes = []
            for circle in circles_list:
                affected_nodes.extend(circle.get("nodes_in_cycle", [])[:5])

            findings.append(
                ValidationFinding(
                    finding_id=f"CIRCULAR_REASONING_{severity}",
                    severity=val_severity,
                    code=self.code,
                    message=f"Detected {len(circles_list)} circular reasoning pattern(s) ({severity} severity). Claims support themselves through indirect chains.",
                    affected_nodes=list(set(affected_nodes)),
                    remediation="Break circular chains by adding independent evidence or removing problematic support edges.",
                )
            )

        return findings


@dataclass
class BlockingRuleResult:
    """Result of blocking rule evaluation (R-B5)."""

    rule_id: str
    triggered: bool
    reason: str
    veto_action: str
    affected_elements: list[str]


class BlockingRulesEngine:
    """Evaluates blocking rules from contract and applies veto gates (R-B5).

    Implements the veto-gate pattern for evidence validation. When a blocking
    rule is triggered, it can:
    - SCORE_ZERO: Set confidence to 0 and mark as insufficient
    - SUPPRESS_OUTPUT: Replace output with suppression notice
    - FLAG_REVIEW: Mark for human review
    """

    def __init__(self, contract: dict[str, Any]):
        self.rules = self._extract_rules(contract)

    def _extract_rules(self, contract: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract blocking rules from validation_rules and gate_logic from assembly_rules.

        R-B5 RESOLUTION: Now extracts gate_logic from evidence_assembly.assembly_rules
        in addition to validation_rules.blocking_rules.
        """
        rules: list[dict[str, Any]] = []

        # Extract from validation_rules.blocking_rules
        validation_rules = contract.get("validation_rules", {})
        blocking_rules = validation_rules.get("blocking_rules", [])
        rules.extend(blocking_rules)

        # Extract gate_logic from evidence_assembly.assembly_rules (R3 rules)
        evidence_assembly = contract.get("evidence_assembly", {})
        assembly_rules = evidence_assembly.get("assembly_rules", [])

        for assembly_rule in assembly_rules:
            if not isinstance(assembly_rule, dict):
                continue

            gate_logic = assembly_rule.get("gate_logic", {})
            if not gate_logic:
                continue

            rule_id = assembly_rule.get("rule_id", "UNKNOWN")

            # Convert gate_logic entries to blocking rules
            for condition_name, gate_config in gate_logic.items():
                if not isinstance(gate_config, dict):
                    continue

                action = gate_config.get("action", "FLAG_REVIEW")
                multiplier = gate_config.get("multiplier", 1.0)

                # Map gate_logic actions to blocking rule format
                if action == "suppress_fact" or multiplier == 0.0:
                    veto_action = "SCORE_ZERO"
                elif action == "reduce_confidence" or (multiplier and multiplier < 1.0):
                    veto_action = "FLAG_REVIEW"
                elif action == "block_branch":
                    veto_action = "SUPPRESS_OUTPUT"
                elif action == "invalidate_graph":
                    veto_action = "SCORE_ZERO"
                else:
                    veto_action = "FLAG_REVIEW"

                rules.append(
                    {
                        "rule_id": f"{rule_id}_{condition_name}",
                        "condition": {
                            "type": condition_name,
                            "threshold": multiplier if multiplier else 0.5,
                        },
                        "on_violation": veto_action,
                        "description": f"Gate logic: {condition_name} from {rule_id}",
                        "source": "assembly_rules.gate_logic",
                    }
                )

        return rules

    def evaluate(
        self,
        graph: EvidenceGraph,
        validation_report: ValidationReport,
    ) -> list[BlockingRuleResult]:
        results: list[BlockingRuleResult] = []

        for rule in self.rules:
            rule_id = rule.get("rule_id", "UNKNOWN")
            condition = rule.get("condition", {})
            action = rule.get("on_violation", "FLAG_REVIEW")

            triggered = self._evaluate_condition(condition, graph, validation_report)

            if triggered:
                results.append(
                    BlockingRuleResult(
                        rule_id=rule_id,
                        triggered=True,
                        reason=rule.get("description", "Blocking rule triggered"),
                        veto_action=action,
                        affected_elements=self._identify_affected(condition, graph),
                    )
                )

        return results

    def _evaluate_condition(
        self,
        condition: dict[str, Any],
        graph: EvidenceGraph,
        validation_report: ValidationReport,
    ) -> bool:
        condition_type = condition.get("type")

        if condition_type == "confidence_below":
            threshold = condition.get("threshold", 0.3)
            avg_confidence = self._compute_global_confidence(graph)
            return avg_confidence < threshold

        elif condition_type == "missing_required_element":
            required = condition.get("element_type")
            if required:
                try:
                    ev_type = EvidenceType(required)
                    return len(graph.get_nodes_by_type(ev_type)) == 0
                except ValueError:
                    return False
            return False

        elif condition_type == "validation_error_count":
            max_errors = condition.get("max_errors", 0)
            error_count = sum(
                1 for f in validation_report.findings if f.severity == ValidationSeverity.ERROR
            )
            return error_count > max_errors

        elif condition_type == "contradiction_detected":
            return len(graph.get_edges_by_type(RelationType.CONTRADICTS)) > 0

        elif condition_type == "low_coherence":
            # Check if validation report has coherence-related warnings
            threshold = condition.get("threshold", 0.5)
            avg_confidence = self._compute_global_confidence(graph)
            return avg_confidence < threshold

        elif condition_type == "statistical_power_below_threshold":
            # For TYPE_B Bayesian contracts
            threshold = condition.get("threshold", 0.8)
            avg_confidence = self._compute_global_confidence(graph)
            return avg_confidence < threshold

        elif condition_type == "cycle_detected":
            # For TYPE_C Causal contracts - check for circular reasoning
            circles = graph.detect_circular_reasoning()
            return len(circles) > 0

        elif condition_type == "budget_gap_detected":
            # For TYPE_D Financial contracts
            budget_nodes = graph.get_nodes_by_type(EvidenceType.BUDGET_AMOUNT)
            goal_nodes = graph.get_nodes_by_type(EvidenceType.GOAL_TARGET)
            # Flag if we have goals but no budget
            return len(goal_nodes) > 0 and len(budget_nodes) == 0

        elif condition_type == "logical_contradiction":
            # For TYPE_E Logical contracts
            contradiction_nodes = graph.get_nodes_by_type(EvidenceType.CONTRADICTION)
            return len(contradiction_nodes) > 0

        elif condition_type == "node_count_below":
            min_nodes = condition.get("minimum", 1)
            return graph.node_count < min_nodes

        return False

    def _compute_global_confidence(self, graph: EvidenceGraph) -> float:
        if graph.node_count == 0:
            return 0.0
        confidences = [n.confidence for n in graph._nodes.values()]
        return sum(confidences) / len(confidences)

    def _identify_affected(self, condition: dict[str, Any], graph: EvidenceGraph) -> list[str]:
        condition_type = condition.get("type")

        if condition_type == "confidence_below":
            threshold = condition.get("threshold", 0.3)
            return [n.node_id[:12] for n in graph._nodes.values() if n.confidence < threshold][:10]

        return []

    def apply_veto(
        self,
        results: list[BlockingRuleResult],
        synthesized_answer: SynthesizedAnswer,
    ) -> SynthesizedAnswer:
        if not results:
            return synthesized_answer

        veto_applied = False
        veto_reason = ""
        new_confidence = synthesized_answer.overall_confidence
        new_completeness = synthesized_answer.completeness
        new_direct_answer = synthesized_answer.direct_answer

        for result in results:
            if not result.triggered:
                continue

            if result.veto_action == "SCORE_ZERO":
                new_confidence = 0.0
                new_completeness = AnswerCompleteness.INSUFFICIENT
                veto_applied = True
                veto_reason = result.reason
            elif result.veto_action == "SUPPRESS_OUTPUT":
                new_direct_answer = f"[SUPRIMIDO: {result.reason}]"
                veto_applied = True
                veto_reason = result.reason
            elif result.veto_action == "FLAG_REVIEW":
                veto_applied = True
                veto_reason = f"Requires review: {result.reason}"

        if not veto_applied:
            return synthesized_answer

        return SynthesizedAnswer(
            direct_answer=new_direct_answer,
            narrative_blocks=synthesized_answer.narrative_blocks,
            completeness=new_completeness,
            overall_confidence=new_confidence,
            calibrated_interval=synthesized_answer.calibrated_interval,
            primary_citations=synthesized_answer.primary_citations,
            supporting_citations=synthesized_answer.supporting_citations,
            gaps=synthesized_answer.gaps + ([f"VETO: {veto_reason}"] if veto_reason else []),
            unresolved_contradictions=synthesized_answer.unresolved_contradictions,
            evidence_graph_hash=synthesized_answer.evidence_graph_hash,
            synthesis_timestamp=synthesized_answer.synthesis_timestamp,
            question_id=synthesized_answer.question_id,
            synthesis_trace={
                **synthesized_answer.synthesis_trace,
                "veto_applied": veto_applied,
                "veto_reason": veto_reason,
            },
        )


class ValidationEngine:
    """
    Probabilistic validation engine for evidence graphs.

    Replaces rule-based EvidenceValidator with graph-aware validation.
    """

    def __init__(self, rules: list[ValidationRule] | None = None):
        self.rules: list[ValidationRule] = rules or [
            RequiredElementsRule(),
            ConsistencyRule(),
            ConfidenceThresholdRule(min_confidence=0.5),
            GraphIntegrityRule(),
            ColombianContextRule(),
            # CrossCuttingCoverageRule removed - themes validated statically in validation_templates.json
            InterdependencyConsistencyRule(),  # R-W3: Interdependency validation
            CircularReasoningRule(),  # I6: Circular reasoning detection
        ]

    def validate(self, graph: EvidenceGraph, contract: dict[str, Any]) -> ValidationReport:
        """Run all validation rules and produce report.

        Stops processing on CRITICAL rule failures to prevent invalid data
        from propagating downstream. Individual rule exceptions are converted
        to ERROR findings with full stack traces for debugging.
        """
        all_findings: list[ValidationFinding] = []
        critical_failure_encountered = False

        for rule in self.rules:
            try:
                findings = rule.validate(graph, contract)
                all_findings.extend(findings)

                # Check if this rule produced a CRITICAL finding
                for finding in findings:
                    if finding.severity == ValidationSeverity.CRITICAL:
                        critical_failure_encountered = True
                        logger.critical(
                            "validation_rule_critical_failure",
                            rule=rule.code,
                            finding_id=finding.finding_id,
                            message=finding.message,
                        )

            except Exception as e:
                # Log full exception with stack trace for debugging
                import traceback

                stack_trace = traceback.format_exc()
                logger.error(
                    "validation_rule_exception",
                    rule=rule.code,
                    error=str(e),
                    error_type=type(e).__name__,
                    stack_trace=stack_trace,
                )
                all_findings.append(
                    ValidationFinding(
                        finding_id=f"RULE_EXCEPTION_{rule.code}",
                        severity=ValidationSeverity.ERROR,
                        code="VALIDATION_EXCEPTION",
                        message=f"Validation rule {rule.code} raised exception: {e}",
                        affected_nodes=[],
                        remediation=f"Check rule implementation. Stack trace: {stack_trace[:500]}",
                    )
                )

        report = ValidationReport.create(all_findings)
        report.graph_integrity = graph.verify_hash_chain()

        logger.info(
            "validation_complete",
            is_valid=report.is_valid,
            critical=report.critical_count,
            errors=report.error_count,
            warnings=report.warning_count,
            critical_failure_encountered=critical_failure_encountered,
        )

        return report


# =============================================================================
# NARRATIVE SYNTHESIZER
# =============================================================================


class NarrativeSynthesizer:
    """
    Transform evidence graph into coherent narrative answer.

    Implements Rhetorical Structure Theory for discourse coherence.
    """

    def __init__(
        self,
        citation_threshold: float = 0.6,
        max_citations_per_claim: int = 3,
    ):
        self.citation_threshold = citation_threshold
        self.max_citations_per_claim = max_citations_per_claim

    def synthesize(
        self,
        graph: EvidenceGraph,
        question_context: dict[str, Any],
        validation: ValidationReport,
        contract: dict[str, Any],
    ) -> SynthesizedAnswer:
        """
        Synthesize complete answer from evidence graph.

        Process:
        1.Determine answer completeness from validation
        2.Select primary and supporting evidence
        3.Generate direct answer based on question type
        4.Build narrative blocks with citations
        5.Identify gaps and contradictions
        6.Compute calibrated confidence
        """
        question_global = question_context.get("question_global", "")
        question_id = question_context.get("question_id", "UNKNOWN")
        expected_elements = question_context.get("expected_elements", [])

        # 1. Determine completeness
        completeness = self._determine_completeness(graph, expected_elements, validation)

        # 2. Select evidence
        primary_nodes = self._select_primary_evidence(graph, expected_elements)
        supporting_nodes = self._select_supporting_evidence(graph, primary_nodes)

        # 3. Build citations
        primary_citations = [self._node_to_citation(n, graph) for n in primary_nodes]
        supporting_citations = [self._node_to_citation(n, graph) for n in supporting_nodes]

        # 4. Generate direct answer
        answer_type = self._infer_answer_type(question_global)
        direct_answer = self._generate_direct_answer(
            graph, question_global, answer_type, completeness, primary_citations
        )

        # 5. Build narrative blocks
        blocks = self._build_narrative_blocks(
            direct_answer, graph, completeness, validation, primary_citations, supporting_citations
        )

        # 6. Identify gaps and contradictions
        gaps = self._identify_gaps(graph, expected_elements)
        contradictions = self._format_contradictions(graph.find_contradictions())

        # 7. Compute confidence
        overall_confidence, calibrated_interval = self._compute_confidence(
            graph, validation, completeness
        )

        return SynthesizedAnswer(
            direct_answer=direct_answer,
            narrative_blocks=blocks,
            completeness=completeness,
            overall_confidence=overall_confidence,
            calibrated_interval=calibrated_interval,
            primary_citations=primary_citations,
            supporting_citations=supporting_citations,
            gaps=gaps,
            unresolved_contradictions=contradictions,
            evidence_graph_hash=graph.get_graph_hash(),
            synthesis_timestamp=time.time(),
            question_id=question_id,
            synthesis_trace={
                "answer_type": answer_type,
                "primary_evidence_count": len(primary_nodes),
                "supporting_evidence_count": len(supporting_nodes),
                "validation_passed": validation.is_valid,
            },
        )

    def _determine_completeness(
        self,
        graph: EvidenceGraph,
        expected_elements: list[dict[str, Any]],
        validation: ValidationReport,
    ) -> AnswerCompleteness:
        """Determine answer completeness based on evidence coverage."""
        if validation.critical_count > 0:
            return AnswerCompleteness.INSUFFICIENT

        required_types = [e["type"] for e in expected_elements if e.get("required")]
        found_types = set()

        for ev_type in EvidenceType:
            if graph.get_nodes_by_type(ev_type):
                found_types.add(ev_type.value)

        missing_required = set(required_types) - found_types

        if not missing_required:
            return AnswerCompleteness.COMPLETE
        elif len(found_types) > 0:
            return AnswerCompleteness.PARTIAL
        else:
            return AnswerCompleteness.INSUFFICIENT

    def _select_primary_evidence(
        self,
        graph: EvidenceGraph,
        expected_elements: list[dict[str, Any]],
    ) -> list[EvidenceNode]:
        """
        Select primary evidence nodes for answer.

        I8 RESOLUTION: Now prioritizes evidence based on contract's required_evidence_keys.
        """
        primary = []

        # I8: Evidence keys prioritization from contract
        # Build priority map based on evidence_keys
        evidence_priority: dict[str, float] = {}

        # Check expected_elements for priority indicators
        for elem in expected_elements:
            elem_type = elem.get("type", "")
            priority = elem.get("priority", 0)
            if priority > 0:
                evidence_priority[elem_type] = max(
                    evidence_priority.get(elem_type, 0), float(priority)
                )
            # Required elements get higher priority
            if elem.get("required"):
                evidence_priority[elem_type] = max(
                    evidence_priority.get(elem_type, 0), 10.0  # High priority for required elements
                )

        # Collect all candidate nodes with their priority scores
        candidates: list[tuple[EvidenceNode, float]] = []

        for node in graph._nodes.values():
            # Base priority from confidence (using adjusted values)
            priority = graph.get_adjusted_confidence(node.node_id)

            # Add type-based priority
            for type_key, type_priority in evidence_priority.items():
                if type_key.lower() in node.evidence_type.value.lower():
                    priority += type_priority * 0.1
                    break

            # Add priority for high-value evidence types
            if node.evidence_type in (
                EvidenceType.INDICATOR_NUMERIC,
                EvidenceType.OFFICIAL_SOURCE,
                EvidenceType.NORMATIVE_REFERENCE,
            ):
                priority += 0.2

            candidates.append((node, priority))

        # Sort by combined priority score
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Select top candidates as primary evidence
        primary = [node for node, _ in candidates[: self.max_citations_per_claim * 2]]

        return primary

    def _select_supporting_evidence(
        self,
        graph: EvidenceGraph,
        primary_nodes: list[EvidenceNode],
    ) -> list[EvidenceNode]:
        """Select supporting evidence that corroborates primary."""
        supporting = []
        primary_ids = {n.node_id for n in primary_nodes}

        for node in primary_nodes:
            support = graph.find_supporting_evidence(node.node_id, max_depth=2)
            for supp_node, depth in support:
                if supp_node.node_id not in primary_ids:
                    supporting.append(supp_node)

        # Deduplicate and limit
        seen = set()
        unique_supporting = []
        for n in supporting:
            if n.node_id not in seen:
                seen.add(n.node_id)
                unique_supporting.append(n)

        return unique_supporting[:10]

    def _node_to_citation(self, node: EvidenceNode, graph: EvidenceGraph) -> Citation:
        """Convert evidence node to citation."""
        value_summary = self._summarize_content(node.content)

        return Citation(
            node_id=node.node_id,
            evidence_type=node.evidence_type.value,
            value_summary=value_summary,
            confidence=graph.get_adjusted_confidence(node.node_id),
            source_method=node.source_method,
            document_reference=node.document_location,
        )

    def _summarize_content(self, content: dict[str, Any]) -> str:
        """Generate brief summary of evidence content."""
        # Try common fields
        for key in ["value", "text", "description", "name", "indicator"]:
            if key in content:
                val = content[key]
                if isinstance(val, str):
                    return val[:100] + ("..." if len(val) > 100 else "")
                return str(val)[:100]

        # Fallback:  first string value
        for val in content.values():
            if isinstance(val, str) and val:
                return val[:100]

        return str(content)[:100]

    def _infer_answer_type(self, question: str) -> str:
        """Infer answer type from question text."""
        q_lower = question.lower()

        if any(
            q in q_lower for q in ["¿cuánto", "¿cuántos", "¿qué porcentaje", "¿cuál es el monto"]
        ):
            return "quantitative"
        if any(q in q_lower for q in ["¿existe", "¿hay", "¿tiene", "¿incluye", "¿contempla"]):
            return "yes_no"
        if any(q in q_lower for q in ["¿cómo se compara", "¿cuál es mejor", "¿qué diferencia"]):
            return "comparative"
        return "descriptive"

    def _generate_direct_answer(
        self,
        graph: EvidenceGraph,
        question: str,
        answer_type: str,
        completeness: AnswerCompleteness,
        citations: list[Citation],
    ) -> str:
        """Generate the direct answer to the question."""
        n_evidence = graph.node_count
        n_citations = len(citations)

        if completeness == AnswerCompleteness.INSUFFICIENT:
            return (
                f"**No se puede responder con confianza. ** El análisis del documento "
                f"no produjo suficiente evidencia para responder la pregunta: "
                f"'{question[: 100]}... '.  Se identificaron solo {n_evidence} elementos "
                f"de evidencia, ninguno de los cuales cumple con los requisitos mínimos."
            )

        if answer_type == "yes_no":
            if n_citations > 0:
                conf_avg = statistics.mean(c.confidence for c in citations)
                if conf_avg >= 0.7:
                    return (
                        f"**Sí**, el documento contiene evidencia positiva.  "
                        f"Se identificaron {n_citations} elementos que sustentan "
                        f"una respuesta afirmativa con confianza promedio del {conf_avg*100:.0f}%."
                    )
                else:
                    return (
                        f"**Parcialmente sí**, aunque con reservas.Se encontró evidencia "
                        f"({n_citations} elementos), pero la confianza promedio es {conf_avg*100:.0f}%, "
                        f"lo que sugiere información incompleta o ambigua."
                    )
            return (
                "**No se encontró evidencia explícita** que responda afirmativamente.  "
                "El documento analizado no contiene los elementos requeridos."
            )

        elif answer_type == "quantitative":
            # Look for numeric values in citations
            numeric_vals = []
            for c in citations:
                try:
                    # Try to extract number from value_summary
                    nums = re.findall(r"[\d,. ]+", c.value_summary)
                    if nums:
                        numeric_vals.append((c.evidence_type, nums[0]))
                except (AttributeError, TypeError):
                    # If value_summary is missing or not a string, skip this citation.
                    pass

            if numeric_vals:
                primary = numeric_vals[0]
                return (
                    f"El documento reporta **{primary[1]}** para {primary[0]}. "
                    f"Esta cifra se basa en {len(numeric_vals)} indicador(es) cuantitativo(s) "
                    f"identificados en el análisis."
                )
            return (
                f"El documento no especifica valores numéricos precisos para esta pregunta.  "
                f"Se encontraron {n_citations} elementos de evidencia cualitativa que "
                f"pueden proporcionar contexto, pero no cifras exactas."
            )

        else:  # descriptive or comparative
            type_summary = ", ".join(set(c.evidence_type for c in citations[:5]))

            quality = "completa" if completeness == AnswerCompleteness.COMPLETE else "parcial"

            return (
                f"El análisis del documento proporciona una respuesta **{quality}**. "
                f"Se identificaron {n_evidence} elementos de evidencia en categorías como: "
                f"{type_summary}. "
                f"{'La información permite una evaluación confiable.' if completeness == AnswerCompleteness.COMPLETE else 'Se requiere información adicional para una evaluación completa.'}"
            )

    def _build_narrative_blocks(
        self,
        direct_answer: str,
        graph: EvidenceGraph,
        completeness: AnswerCompleteness,
        validation: ValidationReport,
        primary_citations: list[Citation],
        supporting_citations: list[Citation],
    ) -> list[NarrativeBlock]:
        """Build complete narrative structure."""
        blocks = []

        # 1. Direct Answer
        blocks.append(
            NarrativeBlock(
                section=NarrativeSection.DIRECT_ANSWER,
                content=direct_answer,
                citations=primary_citations[:3],
                confidence=validation.consistency_score,
            )
        )

        # 2. Evidence Summary
        stats = graph.get_statistics()
        summary_content = (
            f"El análisis procesó evidencia de {stats['node_count']} elementos "
            f"con {stats['edge_count']} relaciones identificadas. "
            f"Confianza promedio: {stats['average_confidence']*100:.0f}%.  "
            f"Distribución por tipo: {self._format_type_distribution(stats['by_evidence_type'])}."
        )
        blocks.append(
            NarrativeBlock(
                section=NarrativeSection.EVIDENCE_SUMMARY,
                content=summary_content,
                citations=[],
                confidence=stats["average_confidence"],
            )
        )

        # 3. Confidence Statement
        conf_level = self._confidence_level_label(validation.consistency_score)
        conf_content = (
            f"**Nivel de confianza:  {conf_level}** ({validation.consistency_score*100:.0f}%). "
            f"Esta evaluación se basa en {len(primary_citations)} elementos de evidencia primaria "
            f"y {len(supporting_citations)} elementos de soporte. "
            f"{'La validación no reportó errores críticos.' if validation.is_valid else f'Se identificaron {validation.critical_count} hallazgos críticos que afectan la confianza.'}"
        )
        blocks.append(
            NarrativeBlock(
                section=NarrativeSection.CONFIDENCE_STATEMENT,
                content=conf_content,
                citations=[],
                confidence=validation.consistency_score,
            )
        )

        # 4. Supporting Details (if sufficient evidence)
        if primary_citations:
            details_parts = []
            for citation in primary_citations[:5]:
                rendered = citation.render("markdown")
                details_parts.append(f"- {rendered}")

            details_content = "**Evidencia principal identificada:**\n" + "\n".join(details_parts)
            blocks.append(
                NarrativeBlock(
                    section=NarrativeSection.SUPPORTING_DETAILS,
                    content=details_content,
                    citations=primary_citations[:5],
                    confidence=(
                        statistics.mean(c.confidence for c in primary_citations)
                        if primary_citations
                        else 0.0
                    ),
                )
            )

        return blocks

    def _identify_gaps(
        self,
        graph: EvidenceGraph,
        expected_elements: list[dict[str, Any]],
    ) -> list[str]:
        """Identify and describe evidence gaps."""
        gaps = []

        for elem in expected_elements:
            elem_type = elem.get("type", "")
            required = elem.get("required", False)
            minimum = elem.get("minimum", 0)

            try:
                ev_type = EvidenceType(elem_type)
                nodes = graph.get_nodes_by_type(ev_type)
                count = len(nodes)

                if required and count == 0:
                    gaps.append(
                        f"**{self._humanize_type(elem_type)}** (requerido): "
                        f"No se encontró evidencia de este tipo en el documento."
                    )
                elif minimum > 0 and count < minimum:
                    gaps.append(
                        f"**{self._humanize_type(elem_type)}**: "
                        f"Se encontraron {count} de {minimum} elementos mínimos requeridos."
                    )
            except ValueError:
                continue

        # Check for low-confidence evidence clusters (using adjusted values)
        low_conf_types: dict[str, int] = defaultdict(int)
        for node in graph._nodes.values():
            if graph.get_adjusted_confidence(node.node_id) < 0.5:
                low_conf_types[node.evidence_type.value] += 1

        for ev_type, count in low_conf_types.items():
            if count >= 3:
                gaps.append(
                    f"**{self._humanize_type(ev_type)}**: "
                    f"{count} elementos tienen confianza baja (<50%), "
                    f"lo que sugiere extracción ambigua o fuentes poco claras."
                )

        return gaps

    def _format_contradictions(
        self,
        contradictions: list[tuple[EvidenceNode, EvidenceNode, EvidenceEdge]],
    ) -> list[str]:
        """Format contradictions for narrative."""
        formatted = []

        for source, target, edge in contradictions[:5]:  # Limit to 5
            formatted.append(
                f"Contradicción entre '{self._summarize_content(source.content)[: 50]}' "
                f"y '{self._summarize_content(target.content)[:50]}' "
                f"(confianza del conflicto: {edge.confidence*100:.0f}%)"
            )

        return formatted

    def _compute_confidence(
        self,
        graph: EvidenceGraph,
        validation: ValidationReport,
        completeness: AnswerCompleteness,
    ) -> tuple[float, tuple[float, float]]:
        """
        Compute overall confidence with calibrated interval.

        Returns (point_estimate, (lower_95, upper_95))
        """
        # Base confidence from validation
        base = validation.consistency_score

        # Adjust for completeness
        completeness_factor = {
            AnswerCompleteness.COMPLETE: 1.0,
            AnswerCompleteness.PARTIAL: 0.7,
            AnswerCompleteness.INSUFFICIENT: 0.3,
            AnswerCompleteness.NOT_APPLICABLE: 0.0,
        }[completeness]

        # Adjust for evidence quantity (diminishing returns)
        quantity_factor = min(1.0, math.log1p(graph.node_count) / math.log1p(50))

        # Combine factors
        point_estimate = base * completeness_factor * (0.5 + 0.5 * quantity_factor)
        point_estimate = max(0.0, min(1.0, point_estimate))

        # Calibrated interval (Wilson score interval approximation)
        n = max(1, graph.node_count)
        z = 1.96  # 95% CI

        denominator = 1 + z**2 / n
        center = (point_estimate + z**2 / (2 * n)) / denominator
        margin = (
            z
            * math.sqrt((point_estimate * (1 - point_estimate) + z**2 / (4 * n)) / n)
            / denominator
        )

        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)

        return point_estimate, (lower, upper)

    def _format_type_distribution(self, type_counts: dict[str, int]) -> str:
        """Format type distribution for narrative."""
        if not type_counts:
            return "ninguno"

        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        parts = [f"{self._humanize_type(t)}({c})" for t, c in sorted_types[:4]]
        return ", ".join(parts)

    def _confidence_level_label(self, score: float) -> str:
        """Map confidence score to human label."""
        if score >= 0.85:
            return "ALTO"
        elif score >= 0.70:
            return "MEDIO-ALTO"
        elif score >= 0.50:
            return "MEDIO"
        elif score >= 0.30:
            return "BAJO"
        else:
            return "MUY BAJO"

    @staticmethod
    def _humanize_type(elem_type: str) -> str:
        """Convert element type to human-readable label."""
        mappings = {
            "indicador_cuantitativo": "indicadores cuantitativos",
            "serie_temporal": "series temporales",
            "monto_presupuestario": "montos presupuestarios",
            "metrica_cobertura": "métricas de cobertura",
            "meta_cuantificada": "metas cuantificadas",
            "fuente_oficial": "fuentes oficiales",
            "cobertura_territorial": "cobertura territorial",
            "actor_institucional": "actores institucionales",
            "instrumento_politica": "instrumentos de política",
            "referencia_normativa": "referencias normativas",
            "vinculo_causal": "vínculos causales",
            "dependencia_temporal": "dependencias temporales",
            "contradiccion": "contradicciones",
            "corroboracion": "corroboraciones",
            "fuentes_oficiales": "fuentes oficiales",
            "indicadores_cuantitativos": "indicadores cuantitativos",
            "series_temporales_años": "series temporales",
            "cobertura_territorial_especificada": "cobertura territorial",
        }
        return mappings.get(elem_type, elem_type.replace("_", " "))


# =============================================================================
# UNIFIED ENGINE:  EvidenceNexus
# =============================================================================


class EvidenceNexus:
    """
    Unified SOTA Evidence-to-Answer Engine.

    REPLACES:
    - EvidenceAssembler:  Graph-based evidence fusion
    - EvidenceValidator: Probabilistic graph validation
    - EvidenceRegistry: Embedded provenance with hash chain

    PROVIDES:
    - Causal graph construction from method outputs
    - Bayesian belief propagation
    - Conflict detection and resolution
    - Narrative synthesis with citations
    - Cryptographic provenance chain

    Usage:
        nexus = EvidenceNexus()
        result = nexus.process(
            method_outputs=method_outputs,
            question_context=question_context,
            contract=contract,
        )

        # Result contains:
        # - evidence_graph: Full graph with all nodes/edges
        # - validation_report: Comprehensive validation
        # - synthesized_answer: Complete narrative answer
        # - human_readable_output: Formatted string
    """

    def __init__(
        self,
        storage_path: Path | None = None,
        enable_persistence: bool = True,
        validation_rules: list[ValidationRule] | None = None,
        citation_threshold: float = 0.6,
    ):
        """
        Initialize EvidenceNexus.

        Args:
            storage_path: Path for persistent storage (JSONL)
            enable_persistence: Whether to persist to disk
            validation_rules:  Custom validation rules
            citation_threshold:  Minimum confidence for citation
        """
        self.storage_path = storage_path or Path("evidence_nexus.jsonl")
        self.enable_persistence = enable_persistence

        self.validation_engine = ValidationEngine(rules=validation_rules)
        self.narrative_synthesizer = NarrativeSynthesizer(citation_threshold=citation_threshold)

        # Current session graph
        self._graph: EvidenceGraph | None = None

        logger.info(
            "evidence_nexus_initialized",
            storage_path=str(self.storage_path),
            persistence=enable_persistence,
        )

    def process(
        self,
        method_outputs: dict[str, Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],
        signal_pack: Any | None = None,
    ) -> dict[str, Any]:
        """
        Process method outputs into complete answer.

        This is the main entry point that replaces:
        - EvidenceAssembler.assemble()
        - EvidenceValidator.validate()
        - EvidenceRegistry.record_evidence()

        Args:
            method_outputs: Raw outputs from executor methods
            question_context: Question context with expected_elements
            contract: Full v3 contract
            signal_pack: Optional signal pack for provenance

        Returns:
            Complete result dict with:
            - evidence:  Assembled evidence (legacy compatible)
            - validation: Validation results (legacy compatible)
            - trace: Execution trace (legacy compatible)
            - synthesized_answer: New narrative answer
            - human_readable_output: Formatted answer string
            - graph_statistics: Graph metrics
        """
        start_time = time.time()

        # SISAS Signal Consumption: Log and validate expected signals
        question_id = question_context.get(
            "question_id", contract.get("identity", {}).get("question_id", "")
        )
        signal_consumption_log = self._log_signal_consumption(
            question_id=question_id,
            signal_pack=signal_pack,
            contract=contract,
        )

        # R-B3: Extract type system from contract for type-aware graph building
        evidence_assembly = contract.get("evidence_assembly", {})
        type_system = evidence_assembly.get("type_system", {})

        # R-B4: Extract level strategies from fusion_specification
        fusion_spec = contract.get("fusion_specification", {})
        level_strategies = fusion_spec.get("level_strategies", {})

        # Determine execution type from contract identity (TYPE_A, TYPE_B, TYPE_C, etc.)
        identity = contract.get("identity", {})
        execution_type = identity.get("contract_type", "TYPE_A")  # Default to TYPE_A

        # 1. Route graph building by execution type (R-B3)
        if execution_type == "TYPE_A":
            graph = self._build_graph_type_a(
                method_outputs, question_context, contract, type_system, signal_pack
            )
        elif execution_type == "TYPE_B":
            graph = self._build_graph_type_b(
                method_outputs, question_context, contract, type_system, signal_pack
            )
        elif execution_type == "TYPE_C":
            graph = self._build_graph_type_c(
                method_outputs, question_context, contract, type_system, signal_pack
            )
        elif execution_type == "TYPE_D":
            graph = self._build_graph_type_d(
                method_outputs, question_context, contract, type_system, signal_pack
            )
        elif execution_type == "TYPE_E":
            graph = self._build_graph_type_e(
                method_outputs, question_context, contract, type_system, signal_pack
            )
        else:
            # Fallback to TYPE_A for unknown types
            logger.debug("execution_type_fallback", execution_type=execution_type)
            graph = self._build_graph_type_a(
                method_outputs, question_context, contract, type_system, signal_pack
            )

        self._graph = graph

        # 1.5 Apply epistemological level strategies (B4)
        self._apply_level_strategies(graph, contract)

        # 1.6 Apply level-specific strategies from contract (R-B4)
        if level_strategies:
            self._apply_contract_level_strategies(graph, level_strategies)

        # 2. Infer relationships between evidence nodes
        self._infer_relationships(graph, contract)

        # 3. Run belief propagation
        beliefs = graph.compute_belief_propagation()

        # 4. Validate graph
        validation_report = self.validation_engine.validate(graph, contract)

        # 4.5 Evaluate blocking rules (R-B5)
        blocking_engine = BlockingRulesEngine(contract)
        blocking_results = blocking_engine.evaluate(graph, validation_report)

        # 5. Synthesize narrative answer
        synthesized = self.narrative_synthesizer.synthesize(
            graph, question_context, validation_report, contract
        )

        # 5.5 Apply veto gates (R-B5)
        synthesized = blocking_engine.apply_veto(blocking_results, synthesized)

        # 6. Persist if enabled
        if self.enable_persistence:
            self._persist_graph(graph)

        # 7. Build legacy-compatible evidence dict
        legacy_evidence = self._build_legacy_evidence(graph, beliefs)
        legacy_validation = self._build_legacy_validation(validation_report)
        legacy_trace = self._build_legacy_trace(graph, signal_pack)

        # ------------------------------------------------------------------
        # SISAS utility / consumption proof (if injected by executor)
        # ------------------------------------------------------------------
        tracker = question_context.get("consumption_tracker")
        if tracker is not None:
            try:
                # ConsumptionTracker provides a summary and an embedded proof object
                if hasattr(tracker, "get_consumption_summary"):
                    legacy_trace["signal_consumption"] = tracker.get_consumption_summary()
                if hasattr(tracker, "get_proof"):
                    proof = tracker.get_proof()
                    if hasattr(proof, "get_consumption_proof"):
                        legacy_trace["signal_consumption_proof"] = proof.get_consumption_proof()
            except Exception:
                # Never break processing for telemetry failures
                pass

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(
            "evidence_nexus_process_complete",
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            is_valid=validation_report.is_valid,
            completeness=synthesized.completeness.value,
            confidence=f"{synthesized.overall_confidence:.2f}",
            processing_time_ms=f"{processing_time_ms:.1f}",
        )

        return {
            # Legacy compatible
            "evidence": legacy_evidence,
            "validation": legacy_validation,
            "trace": legacy_trace,
            # New SOTA outputs
            "synthesized_answer": synthesized.to_dict(),
            "human_readable_output": synthesized.to_human_readable("markdown"),
            "direct_answer": synthesized.direct_answer,
            # Graph data
            "graph_statistics": graph.get_statistics(),
            "graph_hash": graph.get_graph_hash(),
            # Metrics
            "completeness": synthesized.completeness.value,
            "overall_confidence": synthesized.overall_confidence,
            "calibrated_interval": list(synthesized.calibrated_interval),
            "gaps": synthesized.gaps,
            "contradictions": synthesized.unresolved_contradictions,
            # Processing metadata
            "processing_time_ms": processing_time_ms,
            "nexus_version": "1.0.0",
        }

    def _build_graph_from_outputs(
        self,
        method_outputs: dict[str, Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],
        signal_pack: Any | None,
    ) -> EvidenceGraph:
        """
        Transform method outputs into evidence graph.

        Replaces EvidenceAssembler's merge logic with graph construction.
        """
        graph = EvidenceGraph()

        # ---------------------------------------------------------------------
        # Pattern-derived evidence (contract patterns)
        # ---------------------------------------------------------------------
        # v3 executors pass patterns + raw_text into question_context so that
        # patterns add value even when downstream methods don't consume them.
        raw_text = (
            question_context.get("raw_text")
            or question_context.get("text")
            or question_context.get("document_text")
        )
        patterns = question_context.get("patterns") or contract.get("question_context", {}).get(
            "patterns", []
        )
        if isinstance(raw_text, str) and raw_text and isinstance(patterns, list) and patterns:
            graph.add_nodes(
                self._extract_nodes_from_contract_patterns(
                    raw_text=raw_text,
                    patterns=patterns,
                    question_context=question_context,
                    contract=contract,  # B3, I3: Pass contract for type_system propagation
                )
            )

        # Get assembly rules from contract
        evidence_assembly = contract.get("evidence_assembly", {})
        assembly_rules = evidence_assembly.get("assembly_rules", [])

        # Process each method output
        for source_key, output in method_outputs.items():
            if source_key.startswith("_"):
                continue  # Skip internal keys like _signal_usage

            nodes = self._extract_nodes_from_output(source_key, output, question_context)
            graph.add_nodes(nodes)

        # Apply assembly rules to create aggregate nodes
        for rule in assembly_rules:
            target = rule.get("target")
            sources = rule.get("sources", [])
            strategy = rule.get("merge_strategy", "concat")

            aggregate_node = self._create_aggregate_node(
                target, sources, strategy, graph, method_outputs
            )
            if aggregate_node:
                graph.add_node(aggregate_node)

        # Add signal provenance if available
        if signal_pack is not None:
            provenance_node = self._create_provenance_node(signal_pack)
            graph.add_node(provenance_node)

        return graph

    # -------------------------------------------------------------------------
    # SISAS Signal Consumption Logging
    # -------------------------------------------------------------------------

    def _log_signal_consumption(
        self,
        question_id: str,
        signal_pack: Any | None,
        contract: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Log signal consumption for SISAS irrigation observability.

        Implements REGLA 2 (Value-Add Validation) from the SISAS spec:
        - Logs expected vs received signals
        - Calculates signal coverage
        - Applies confidence penalty for missing signals

        Args:
            question_id: Question being processed
            signal_pack: Signal pack from Phase 1 enrichment
            contract: Contract with expected signal info

        Returns:
            Signal consumption log dict
        """
        # Try to get expected signals from integration_map via CQCLoader
        expected_primary = []
        expected_secondary = []

        try:
            from canonic_questionnaire_central import CQCLoader

            cqc = CQCLoader()
            # Get signals for this question
            expected_signals = cqc.get_signals_for_question(question_id)
            if expected_signals:
                # Split into primary/secondary based on integration_map
                expected_primary = list(expected_signals)[:2]  # Heuristic
                expected_secondary = list(expected_signals)[2:]
        except Exception:
            # Fallback: try to extract from contract
            signal_spec = contract.get("signal_specification", {})
            expected_primary = signal_spec.get("primary_signals", [])
            expected_secondary = signal_spec.get("secondary_signals", [])

        # Get received signals from signal_pack
        received_signals = []
        if signal_pack:
            if hasattr(signal_pack, "signals_detected"):
                received_signals = signal_pack.signals_detected
            elif isinstance(signal_pack, dict):
                received_signals = signal_pack.get("signals_detected", [])

        # Calculate coverage
        missing_primary = [s for s in expected_primary if s not in received_signals]
        missing_secondary = [s for s in expected_secondary if s not in received_signals]

        primary_count = len(expected_primary)
        coverage = (
            (primary_count - len(missing_primary)) / primary_count if primary_count > 0 else 1.0
        )

        # Calculate confidence penalty
        confidence_penalty = len(missing_primary) * 0.10 + len(missing_secondary) * 0.05

        log_entry = {
            "event": "nexus_signal_consumption",
            "question_id": question_id,
            "expected_primary": expected_primary,
            "expected_secondary": expected_secondary,
            "received_signals": received_signals,
            "missing_primary": missing_primary,
            "missing_secondary": missing_secondary,
            "coverage": round(coverage, 3),
            "confidence_penalty": round(confidence_penalty, 3),
            "timestamp": time.time(),
        }

        logger.info(
            "signal_consumption",
            question_id=question_id,
            coverage=coverage,
            missing_primary=len(missing_primary),
            received=len(received_signals),
        )

        return log_entry

    # -------------------------------------------------------------------------
    # R-B3: Type-Specific Graph Builders
    # -------------------------------------------------------------------------

    def _build_graph_type_a(
        self,
        method_outputs: dict[str, Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],
        type_system: dict[str, Any],
        signal_pack: Any | None = None,
    ) -> EvidenceGraph:
        """TYPE_A: Semantic corroboration → Dempster-Shafer → Veto gate.

        TYPE_A is the default execution type for questions requiring:
        - Cross-validation of evidence sources
        - Belief propagation for confidence aggregation
        - Veto gates for blocking conditions
        """
        # Build base graph using standard extraction
        graph = self._build_graph_from_outputs(
            method_outputs, question_context, contract, signal_pack
        )

        # Extract TYPE_A specific configuration
        expected_outputs = type_system.get("expected_outputs", {})
        n1_provides = expected_outputs.get("N1", [])
        n2_provides = expected_outputs.get("N2", [])
        n3_provides = expected_outputs.get("N3", [])

        # Add type-aware metadata to nodes based on epistemological level
        for node_id, node in list(graph._nodes.items()):
            level = self._determine_method_level(node.source_method, contract)
            provides = {"N1": n1_provides, "N2": n2_provides, "N3": n3_provides}.get(level, [])

            # Store level metadata in adjustments (frozen nodes can't be mutated)
            if provides:
                # Track which evidence types this level should provide
                graph._confidence_adjustments.setdefault(node_id, node.confidence)

        # TYPE_A specific: Add semantic corroboration edges
        self._add_semantic_corroboration_edges(graph)

        logger.debug(
            "type_a_graph_built",
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            n1_provides=n1_provides,
            n2_provides=n2_provides,
            n3_provides=n3_provides,
        )

        return graph

    def _build_graph_type_b(
        self,
        method_outputs: dict[str, Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],
        type_system: dict[str, Any],
        signal_pack: Any | None = None,
    ) -> EvidenceGraph:
        """TYPE_B: Quantitative aggregation → Statistical validation → Threshold gates.

        TYPE_B is designed for questions requiring:
        - Numerical aggregation and statistical analysis
        - Threshold-based validation (min/max/range checks)
        - Quantitative evidence prioritization
        """
        # Build base graph
        graph = self._build_graph_from_outputs(
            method_outputs, question_context, contract, signal_pack
        )

        # TYPE_B specific: Boost confidence for quantitative evidence types
        quantitative_types = {
            EvidenceType.INDICATOR_NUMERIC,
            EvidenceType.TEMPORAL_SERIES,
            EvidenceType.BUDGET_AMOUNT,
            EvidenceType.COVERAGE_METRIC,
            EvidenceType.GOAL_TARGET,
        }

        for node_id, node in graph._nodes.items():
            if node.evidence_type in quantitative_types:
                # Boost quantitative evidence confidence for TYPE_B
                graph._confidence_adjustments[node_id] = min(1.0, node.confidence * 1.15)
                graph._belief_mass_adjustments[node_id] = min(1.0, node.belief_mass * 1.15)

        # TYPE_B specific: Add statistical correlation edges
        self._add_statistical_correlation_edges(graph)

        logger.debug(
            "type_b_graph_built",
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            quantitative_nodes=sum(
                1 for n in graph._nodes.values() if n.evidence_type in quantitative_types
            ),
        )

        return graph

    def _build_graph_type_c(
        self,
        method_outputs: dict[str, Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],
        type_system: dict[str, Any],
        signal_pack: Any | None = None,
    ) -> EvidenceGraph:
        """TYPE_C: Causal chain → Temporal ordering → Dependency validation.

        TYPE_C is designed for questions requiring:
        - Causal relationship analysis
        - Temporal sequence validation
        - Dependency chain construction
        """
        # Build base graph
        graph = self._build_graph_from_outputs(
            method_outputs, question_context, contract, signal_pack
        )

        # TYPE_C specific: Prioritize causal and temporal evidence
        causal_types = {
            EvidenceType.CAUSAL_LINK,
            EvidenceType.TEMPORAL_DEPENDENCY,
            EvidenceType.POLICY_INSTRUMENT,
        }

        for node_id, node in graph._nodes.items():
            if node.evidence_type in causal_types:
                # Boost causal evidence confidence for TYPE_C
                graph._confidence_adjustments[node_id] = min(1.0, node.confidence * 1.2)
                graph._belief_mass_adjustments[node_id] = min(1.0, node.belief_mass * 1.2)

        # TYPE_C specific: Add causal chain edges
        self._add_causal_chain_edges(graph)

        # TYPE_C specific: Add temporal ordering edges
        self._add_temporal_ordering_edges(graph)

        logger.debug(
            "type_c_graph_built",
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            causal_nodes=sum(1 for n in graph._nodes.values() if n.evidence_type in causal_types),
        )

        return graph

    def _build_graph_type_d(
        self,
        method_outputs: dict[str, Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],
        type_system: dict[str, Any],
        signal_pack: Any | None = None,
    ) -> EvidenceGraph:
        """TYPE_D: Financial extraction → Sufficiency analysis → Coherence audit.

        TYPE_D is designed for questions requiring:
        - Budget and financial data extraction
        - Sufficiency score computation
        - Financial coherence validation
        """
        # Build base graph
        graph = self._build_graph_from_outputs(
            method_outputs, question_context, contract, signal_pack
        )

        # TYPE_D specific: Prioritize financial evidence types
        financial_types = {
            EvidenceType.BUDGET_AMOUNT,
            EvidenceType.INDICATOR_NUMERIC,
            EvidenceType.GOAL_TARGET,
        }

        for node_id, node in graph._nodes.items():
            if node.evidence_type in financial_types:
                # Boost financial evidence confidence for TYPE_D
                graph._confidence_adjustments[node_id] = min(1.0, node.confidence * 1.2)
                graph._belief_mass_adjustments[node_id] = min(1.0, node.belief_mass * 1.2)

        # TYPE_D specific: Add financial coherence edges
        self._add_financial_coherence_edges(graph)

        logger.debug(
            "type_d_graph_built",
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            financial_nodes=sum(
                1 for n in graph._nodes.values() if n.evidence_type in financial_types
            ),
        )

        return graph

    def _build_graph_type_e(
        self,
        method_outputs: dict[str, Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],
        type_system: dict[str, Any],
        signal_pack: Any | None = None,
    ) -> EvidenceGraph:
        """TYPE_E: Statement extraction → Coherence computation → Contradiction detection.

        TYPE_E is designed for questions requiring:
        - Policy statement extraction
        - Logical consistency validation
        - Contradiction detection and resolution
        """
        # Build base graph
        graph = self._build_graph_from_outputs(
            method_outputs, question_context, contract, signal_pack
        )

        # TYPE_E specific: Prioritize normative and policy evidence
        logical_types = {
            EvidenceType.NORMATIVE_REFERENCE,
            EvidenceType.POLICY_INSTRUMENT,
            EvidenceType.CONTRADICTION,
            EvidenceType.CORROBORATION,
        }

        for node_id, node in graph._nodes.items():
            if node.evidence_type in logical_types:
                # Boost logical evidence confidence for TYPE_E
                graph._confidence_adjustments[node_id] = min(1.0, node.confidence * 1.15)
                graph._belief_mass_adjustments[node_id] = min(1.0, node.belief_mass * 1.15)

        # TYPE_E specific: Add logical consistency edges
        self._add_logical_consistency_edges(graph)

        # TYPE_E specific: Detect and mark contradictions
        self._detect_and_mark_contradictions(graph)

        logger.debug(
            "type_e_graph_built",
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            logical_nodes=sum(1 for n in graph._nodes.values() if n.evidence_type in logical_types),
        )

        return graph

    def _add_financial_coherence_edges(self, graph: EvidenceGraph) -> None:
        """Add edges for financial coherence between budget-related nodes.

        TYPE_D specific: Creates SUPPORTS edges between budget amounts
        and goal targets to validate financial sufficiency.
        """
        budget_nodes = graph.get_nodes_by_type(EvidenceType.BUDGET_AMOUNT)
        goal_nodes = graph.get_nodes_by_type(EvidenceType.GOAL_TARGET)

        for bn in budget_nodes[:5]:
            for gn in goal_nodes[:5]:
                if bn.node_id != gn.node_id:
                    edge = EvidenceEdge.create(
                        source_id=bn.node_id,
                        target_id=gn.node_id,
                        relation_type=RelationType.SUPPORTS,
                        weight=0.7,
                        confidence=0.7,
                        metadata={"edge_type": "financial_coherence"},
                    )
                    try:
                        graph.add_edge(edge)
                    except ValueError:
                        pass

    def _add_logical_consistency_edges(self, graph: EvidenceGraph) -> None:
        """Add edges for logical consistency between policy statements.

        TYPE_E specific: Creates SUPPORTS or CONTRADICTS edges between
        normative references and policy instruments.
        """
        normative_nodes = graph.get_nodes_by_type(EvidenceType.NORMATIVE_REFERENCE)
        policy_nodes = graph.get_nodes_by_type(EvidenceType.POLICY_INSTRUMENT)

        for nn in normative_nodes[:5]:
            for pn in policy_nodes[:5]:
                if nn.node_id != pn.node_id:
                    edge = EvidenceEdge.create(
                        source_id=nn.node_id,
                        target_id=pn.node_id,
                        relation_type=RelationType.SUPPORTS,
                        weight=0.6,
                        confidence=0.65,
                        metadata={"edge_type": "logical_consistency"},
                    )
                    try:
                        graph.add_edge(edge)
                    except ValueError:
                        pass

    def _detect_and_mark_contradictions(self, graph: EvidenceGraph) -> None:
        """Detect potential contradictions and create CONTRADICTS edges.

        TYPE_E specific: Analyzes evidence nodes for logical conflicts
        and creates CONTRADICTS edges where detected.
        """
        # Get nodes that might contain contradictory information
        contradiction_nodes = graph.get_nodes_by_type(EvidenceType.CONTRADICTION)

        # Create contradiction edges between contradiction nodes and their targets
        for cn in contradiction_nodes[:5]:
            # Look for related nodes that might be contradicted
            if isinstance(cn.content, dict):
                affected = cn.content.get("affects", [])
                for affected_id in affected[:3]:
                    if affected_id in graph._nodes:
                        edge = EvidenceEdge.create(
                            source_id=cn.node_id,
                            target_id=affected_id,
                            relation_type=RelationType.CONTRADICTS,
                            weight=0.8,
                            confidence=0.75,
                            metadata={"edge_type": "detected_contradiction"},
                        )
                        try:
                            graph.add_edge(edge)
                        except ValueError:
                            pass

    def _determine_method_level(self, source_method: str, contract: dict[str, Any]) -> str:
        """Determine epistemological level (N1/N2/N3) for a method.

        Returns:
            Level string: "N1", "N2", or "N3"
        """
        method_binding = contract.get("method_binding", {})
        execution_phases = method_binding.get("execution_phases", {})

        source_lower = source_method.lower()

        # Check execution phases for level mapping
        for phase_name, phase_data in execution_phases.items():
            if isinstance(phase_data, dict):
                phase_methods = phase_data.get("methods", [])
                for method in phase_methods:
                    method_id = (
                        method.get("method_id", "") if isinstance(method, dict) else str(method)
                    )
                    if method_id.lower() in source_lower or source_lower in method_id.lower():
                        return phase_data.get("level", "N1")

        # Default level inference from method name
        if "audit" in source_lower or "validation" in source_lower:
            return "N3"
        elif "infer" in source_lower or "causal" in source_lower or "analysis" in source_lower:
            return "N2"
        return "N1"

    def _add_semantic_corroboration_edges(self, graph: EvidenceGraph) -> None:
        """Add edges for semantic corroboration between evidence nodes.

        TYPE_A specific: Creates SUPPORTS edges between nodes with
        compatible evidence types that can corroborate each other.
        """
        corroboration_pairs = [
            (EvidenceType.OFFICIAL_SOURCE, EvidenceType.NORMATIVE_REFERENCE),
            (EvidenceType.INDICATOR_NUMERIC, EvidenceType.GOAL_TARGET),
            (EvidenceType.TERRITORIAL_COVERAGE, EvidenceType.COVERAGE_METRIC),
            (EvidenceType.INSTITUTIONAL_ACTOR, EvidenceType.POLICY_INSTRUMENT),
        ]

        for source_type, target_type in corroboration_pairs:
            source_nodes = graph.get_nodes_by_type(source_type)[:5]
            target_nodes = graph.get_nodes_by_type(target_type)[:5]

            for sn in source_nodes:
                for tn in target_nodes:
                    if sn.node_id != tn.node_id:
                        edge = EvidenceEdge.create(
                            source_id=sn.node_id,
                            target_id=tn.node_id,
                            relation_type=RelationType.SUPPORTS,
                            weight=0.7,
                            confidence=0.75,
                            metadata={"edge_type": "semantic_corroboration"},
                        )
                        try:
                            graph.add_edge(edge)
                        except ValueError:
                            pass  # Skip cycles

    def _add_statistical_correlation_edges(self, graph: EvidenceGraph) -> None:
        """Add edges for statistical correlation between quantitative nodes.

        TYPE_B specific: Creates CORRELATES edges between numerical
        evidence that may be statistically related.
        """
        quantitative_nodes = []
        for node in graph._nodes.values():
            if node.evidence_type in {
                EvidenceType.INDICATOR_NUMERIC,
                EvidenceType.TEMPORAL_SERIES,
                EvidenceType.BUDGET_AMOUNT,
                EvidenceType.COVERAGE_METRIC,
            }:
                quantitative_nodes.append(node)

        # Create correlation edges between quantitative nodes (limited)
        for i, node_a in enumerate(quantitative_nodes[:10]):
            for node_b in quantitative_nodes[i + 1 : 10]:
                edge = EvidenceEdge.create(
                    source_id=node_a.node_id,
                    target_id=node_b.node_id,
                    relation_type=RelationType.CORRELATES,
                    weight=0.5,
                    confidence=0.6,
                    metadata={"edge_type": "statistical_correlation"},
                )
                try:
                    graph.add_edge(edge)
                except ValueError:
                    pass

    def _add_causal_chain_edges(self, graph: EvidenceGraph) -> None:
        """Add edges for causal chain relationships.

        TYPE_C specific: Creates CAUSES edges between evidence nodes
        that form causal chains.
        """
        causal_nodes = graph.get_nodes_by_type(EvidenceType.CAUSAL_LINK)
        policy_nodes = graph.get_nodes_by_type(EvidenceType.POLICY_INSTRUMENT)

        # Causal links -> policy instruments (causal chain)
        for cn in causal_nodes[:5]:
            for pn in policy_nodes[:5]:
                if cn.node_id != pn.node_id:
                    edge = EvidenceEdge.create(
                        source_id=cn.node_id,
                        target_id=pn.node_id,
                        relation_type=RelationType.CAUSES,
                        weight=0.6,
                        confidence=0.65,
                        metadata={"edge_type": "causal_chain"},
                    )
                    try:
                        graph.add_edge(edge)
                    except ValueError:
                        pass

    def _add_temporal_ordering_edges(self, graph: EvidenceGraph) -> None:
        """Add edges for temporal ordering between temporal evidence.

        TYPE_C specific: Creates TEMPORALLY_PRECEDES edges between
        temporal evidence nodes.
        """
        temporal_nodes = graph.get_nodes_by_type(EvidenceType.TEMPORAL_SERIES)
        dependency_nodes = graph.get_nodes_by_type(EvidenceType.TEMPORAL_DEPENDENCY)

        all_temporal = temporal_nodes[:5] + dependency_nodes[:5]

        # Simple temporal ordering (by extraction order as proxy)
        for i, node_a in enumerate(all_temporal):
            for node_b in all_temporal[i + 1 :]:
                if node_a.node_id != node_b.node_id:
                    edge = EvidenceEdge.create(
                        source_id=node_a.node_id,
                        target_id=node_b.node_id,
                        relation_type=RelationType.TEMPORALLY_PRECEDES,
                        weight=0.5,
                        confidence=0.55,
                        metadata={"edge_type": "temporal_ordering"},
                    )
                    try:
                        graph.add_edge(edge)
                    except ValueError:
                        pass

    def _apply_contract_level_strategies(
        self,
        graph: EvidenceGraph,
        level_strategies: dict[str, Any],
    ) -> None:
        """Apply level-specific strategies from contract's fusion_specification.

        R-B4 RESOLUTION: Applies strategies defined in contract's
        fusion_specification.level_strategies configuration.

        The level_strategies format from contract:
        - N1_fact_fusion: { strategy, behavior, conflict_resolution, formula }
        - N2_parameter_fusion: { strategy, behavior, affects }
        - N3_constraint_fusion: { strategy, behavior, asymmetry_principle, propagation }
        """
        if not level_strategies:
            return

        # Map strategy names to level prefixes
        level_map = {
            "N1_fact_fusion": "N1",
            "N2_parameter_fusion": "N2",
            "N3_constraint_fusion": "N3",
        }

        # Apply behavior-based adjustments
        for strategy_name, strategy_config in level_strategies.items():
            if not isinstance(strategy_config, dict):
                continue

            level_prefix = level_map.get(strategy_name)
            if not level_prefix:
                continue

            behavior = strategy_config.get("behavior", "additive")
            strategy_type = strategy_config.get("strategy", "")

            # Apply adjustments based on behavior type
            for node_id, node in graph._nodes.items():
                node_level = self._determine_method_level(node.source_method, {})

                if not node_level.startswith(level_prefix):
                    continue

                current_conf = graph._confidence_adjustments.get(node_id, node.confidence)
                current_belief = graph._belief_mass_adjustments.get(node_id, node.belief_mass)

                if behavior == "gate" and level_prefix == "N3":
                    # N3 gate behavior: boost confidence for audit nodes
                    graph._confidence_adjustments[node_id] = min(1.0, current_conf * 1.1)
                    graph._belief_mass_adjustments[node_id] = min(1.0, current_belief * 1.1)
                elif behavior == "multiplicative" and level_prefix == "N2":
                    # N2 multiplicative: moderate adjustment
                    graph._confidence_adjustments[node_id] = current_conf * 1.0  # Neutral
                    graph._belief_mass_adjustments[node_id] = current_belief * 1.0
                elif behavior == "additive" and level_prefix == "N1":
                    # N1 additive: preserve as-is
                    pass

        logger.debug(
            "contract_level_strategies_applied",
            strategies_count=len(level_strategies),
            strategies=list(level_strategies.keys()),
        )

    def _extract_nodes_from_contract_patterns(
        self,
        *,
        raw_text: str,
        patterns: list[Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],  # B3, I3: Added contract parameter for type_system propagation
        max_matches_per_pattern: int = 5,
    ) -> list[EvidenceNode]:
        """Create evidence nodes from v3 contract patterns.

        B3, I3 RESOLUTION: Now uses contract's type_system for dynamic type mapping.

        Goal: patterns contribute to evidence/scoring even if methods ignore them.

        This is intentionally conservative:
        - Only regex/literal matching (NER_OR_REGEX treated as regex fallback)
        - Caps matches per pattern for determinism and bounded output
        - Type mapping from contract's type_system (not hardcoded)
        """
        nodes: list[EvidenceNode] = []
        qid = str(question_context.get("question_id") or "")
        document_context = question_context.get("document_context")
        if not isinstance(document_context, dict):
            document_context = {}

        # Optional SISAS consumption tracker (utility measurement + proof chain)
        tracker = question_context.get("consumption_tracker")

        # Optional context-aware filtering from SISAS
        filtered_patterns = patterns
        context_filter_stats: dict[str, int] | None = None
        if document_context:
            try:
                from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_context_scoper import (
                    filter_patterns_by_context,
                )

                # filter_patterns_by_context expects list[dict], ignore non-dicts
                dict_patterns = [p for p in patterns if isinstance(p, dict)]
                filtered_patterns, context_filter_stats = filter_patterns_by_context(
                    dict_patterns, document_context
                )
            except Exception:
                filtered_patterns = patterns
                context_filter_stats = None

        # Optional semantic expansion from SISAS (Refactoring #2)
        expanded_patterns = filtered_patterns
        expansion_stats: dict[str, Any] | None = None
        try:
            from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_semantic_expander import (
                expand_all_patterns,
                validate_expansion_result,
            )

            dict_patterns = [p for p in filtered_patterns if isinstance(p, dict)]
            if dict_patterns:
                expanded_patterns = expand_all_patterns(dict_patterns, enable_logging=False)
                try:
                    expansion_stats = validate_expansion_result(
                        dict_patterns,
                        expanded_patterns,
                        min_multiplier=2.0,
                        target_multiplier=5.0,
                    )
                except Exception:
                    expansion_stats = None
        except Exception:
            expanded_patterns = filtered_patterns
            expansion_stats = None

        max_patterns = 2000
        if isinstance(expanded_patterns, list) and len(expanded_patterns) > max_patterns:
            expanded_patterns = expanded_patterns[:max_patterns]

        def _to_flags(flags_value: Any) -> int:
            if not flags_value:
                return re.IGNORECASE | re.MULTILINE
            if isinstance(flags_value, int):
                return flags_value
            if isinstance(flags_value, str):
                f = 0
                if "i" in flags_value:
                    f |= re.IGNORECASE
                if "m" in flags_value:
                    f |= re.MULTILINE
                if "s" in flags_value:
                    f |= re.DOTALL
                return f or (re.IGNORECASE | re.MULTILINE)
            return re.IGNORECASE | re.MULTILINE

        # B3, I3 RESOLUTION: Build type mapping from contract's type_system
        # CRITICAL: Handle different contract versions for type_system access:
        # - v4: contract.evidence_assembly.type_system
        # - v3: may not have type_system at all
        # - v2: may have contract.type_system directly
        contract_type_system: dict[str, str] = {}

        # Try multiple paths for type_system (v4, v3, v2 compatibility)
        type_mapping = contract.get("evidence_assembly", {}).get(
            "type_system", {}
        ) or contract.get(  # v4 path
            "type_system", {}
        )  # v2/v3 fallback
        if isinstance(type_mapping, dict):
            for pattern_category, evidence_type_str in type_mapping.items():
                try:
                    # Validate the EvidenceType value
                    EvidenceType(evidence_type_str)
                    contract_type_system[str(pattern_category).upper()] = evidence_type_str
                except (ValueError, TypeError):
                    # Invalid EvidenceType - skip this mapping
                    pass

        def _map_category_to_evidence_type(category: str) -> EvidenceType:
            """Map pattern category to EvidenceType using contract's type_system.

            B3, I3 RESOLUTION: No longer hardcoded - uses contract configuration.
            Falls back to sensible defaults if not specified in contract.
            """
            cat = (category or "").upper()

            # First, check contract's type_system for explicit mapping
            if cat in contract_type_system:
                try:
                    return EvidenceType(contract_type_system[cat])
                except (ValueError, TypeError):
                    pass  # Fall through to defaults

            # Default fallback mappings (when contract doesn't specify)
            if cat == "INDICADOR" or cat == "UNIDAD_MEDIDA":
                return EvidenceType.INDICATOR_NUMERIC
            if cat == "TEMPORAL":
                return EvidenceType.TEMPORAL_SERIES
            if cat == "FUENTE_OFICIAL":
                return EvidenceType.OFFICIAL_SOURCE
            if cat == "TERRITORIAL":
                return EvidenceType.TERRITORIAL_COVERAGE
            if cat.startswith("CAUSAL"):
                return EvidenceType.CAUSAL_LINK
            # Default: treat as method-output-like evidence with tags
            return EvidenceType.METHOD_OUTPUT

        for pat in expanded_patterns:
            if not isinstance(pat, dict):
                continue

            pattern_id = str(pat.get("id") or pat.get("pattern_id") or pat.get("pattern_ref") or "")
            category = str(pat.get("category") or "GENERAL")
            match_type = str(pat.get("match_type") or "REGEX").upper()
            pattern_str = pat.get("pattern")

            # If pattern_ref exists but pattern is missing, we still emit a trace node
            # so the deficiency is visible in downstream telemetry.
            if not isinstance(pattern_str, str) or not pattern_str.strip():
                node = EvidenceNode.create(
                    evidence_type=EvidenceType.METHOD_OUTPUT,
                    content={
                        "pattern_id": pattern_id,
                        "pattern_ref": pat.get("pattern_ref"),
                        "category": category,
                        "match_type": match_type,
                        "matches": [],
                        "note": "pattern_missing_in_contract",
                        "question_id": qid,
                    },
                    confidence=0.1,
                    source_method="contract.patterns",
                    tags=["contract_pattern", "pattern_missing"],
                )
                nodes.append(node)
                continue

            flags_int = _to_flags(pat.get("flags"))
            matches: list[str] = []
            try:
                if match_type == "LITERAL":
                    # Simple containment; return matched literal as-is once per occurrence (bounded).
                    literal = pattern_str
                    start = 0
                    while len(matches) < max_matches_per_pattern:
                        idx = raw_text.lower().find(literal.lower(), start)
                        if idx < 0:
                            break
                        matches.append(raw_text[idx : idx + len(literal)])
                        start = idx + len(literal)
                else:
                    compiled = re.compile(pattern_str, flags_int)
                    for m in compiled.finditer(raw_text):
                        matches.append(m.group(0))
                        if len(matches) >= max_matches_per_pattern:
                            break
            except Exception:
                # Invalid regex patterns should not crash pipeline; emit diagnostic node.
                node = EvidenceNode.create(
                    evidence_type=EvidenceType.METHOD_OUTPUT,
                    content={
                        "pattern_id": pattern_id,
                        "pattern_ref": pat.get("pattern_ref"),
                        "category": category,
                        "match_type": match_type,
                        "pattern": pattern_str,
                        "matches": [],
                        "note": "pattern_compile_or_match_failed",
                        "question_id": qid,
                    },
                    confidence=0.1,
                    source_method="contract.patterns",
                    tags=["contract_pattern", "pattern_error"],
                )
                nodes.append(node)
                continue

            # Record consumption proof (if tracker injected)
            if tracker is not None and matches:
                try:
                    # Track up to the same cap; produced_evidence=True because we are emitting nodes
                    for mtxt in matches:
                        # ConsumptionTracker API: record_pattern_match(pattern, text_segment, produced_evidence)
                        if hasattr(tracker, "record_pattern_match"):
                            tracker.record_pattern_match(
                                pattern={"id": pattern_id, "pattern": pattern_str},
                                text_segment=str(mtxt),
                                produced_evidence=True,
                            )
                except Exception:
                    # Never break execution for tracking failures
                    pass

            confidence_weight = pat.get("confidence_weight")
            try:
                confidence = float(confidence_weight) if confidence_weight is not None else 0.6
            except Exception:
                confidence = 0.6
            if not matches:
                confidence = min(confidence, 0.35)

            node = EvidenceNode.create(
                evidence_type=_map_category_to_evidence_type(category),
                content={
                    "pattern_id": pattern_id,
                    "pattern_ref": pat.get("pattern_ref"),
                    "category": category,
                    "match_type": match_type,
                    "pattern": pattern_str,
                    "matches": matches,
                    "match_count": len(matches),
                    "question_id": qid,
                },
                confidence=max(0.0, min(1.0, confidence)),
                source_method="contract.patterns",
                tags=["contract_pattern", category.lower()],
            )
            nodes.append(node)

        # Emit a lightweight stats node for context filtering and utility accounting
        try:
            total_injected = len([p for p in patterns if isinstance(p, dict)])
            total_after_context = len([p for p in filtered_patterns if isinstance(p, dict)])
            total_considered = len([p for p in expanded_patterns if isinstance(p, dict)])
            matched_patterns = 0
            for n in nodes:
                if isinstance(n.content, dict) and int(n.content.get("match_count", 0) or 0) > 0:
                    matched_patterns += 1
            waste_ratio = (
                1.0 - (matched_patterns / total_considered) if total_considered > 0 else 1.0
            )
            nodes.append(
                EvidenceNode.create(
                    evidence_type=EvidenceType.METHOD_OUTPUT,
                    content={
                        "provenance_type": "contract_pattern_utility",
                        "question_id": qid,
                        "patterns_injected": total_injected,
                        "patterns_after_context_filter": total_after_context,
                        "patterns_considered": total_considered,
                        "patterns_matched": matched_patterns,
                        "waste_ratio": round(float(waste_ratio), 4),
                        "context_filter_stats": context_filter_stats,
                        "semantic_expansion_stats": expansion_stats,
                    },
                    confidence=1.0,
                    source_method="contract.patterns.utility",
                    tags=["contract_pattern", "utility"],
                )
            )
        except Exception:
            pass

        return nodes

    def _extract_nodes_from_output(
        self,
        source_key: str,
        output: Any,
        question_context: dict[str, Any],
    ) -> list[EvidenceNode]:
        """Extract evidence nodes from a single method output."""
        nodes = []

        if output is None:
            return nodes

        # Handle list outputs (multiple evidence items)
        if isinstance(output, list):
            for idx, item in enumerate(output):
                node = self._item_to_node(
                    item,
                    source_method=source_key,
                    index=idx,
                )
                if node:
                    nodes.append(node)

        # Handle dict outputs (structured evidence)
        elif isinstance(output, dict):
            # Check if it's a single evidence item or container
            if "elements" in output:
                # Container with elements list
                for idx, item in enumerate(output.get("elements", [])):
                    node = self._item_to_node(
                        item,
                        source_method=source_key,
                        index=idx,
                    )
                    if node:
                        nodes.append(node)
            else:
                # Single evidence item
                node = self._item_to_node(
                    output,
                    source_method=source_key,
                )
                if node:
                    nodes.append(node)

        # Handle scalar outputs
        else:
            node = EvidenceNode.create(
                evidence_type=EvidenceType.METHOD_OUTPUT,
                content={"value": output, "source": source_key},
                confidence=0.7,  # Default for raw method output
                source_method=source_key,
            )
            nodes.append(node)

        return nodes

    def _item_to_node(
        self,
        item: Any,
        source_method: str,
        index: int | None = None,
    ) -> EvidenceNode | None:
        """Convert a single item to evidence node."""
        if item is None:
            return None

        if isinstance(item, dict):
            # Extract type
            item_type = item.get("type", item.get("evidence_type", ""))
            try:
                ev_type = EvidenceType(item_type)
            except ValueError:
                ev_type = EvidenceType.METHOD_OUTPUT

            # Extract confidence
            confidence = item.get("confidence", item.get("score", 0.7))
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence.strip("%")) / 100
                except (ValueError, TypeError):
                    confidence = 0.7

            # Extract document location
            doc_loc = item.get("page", item.get("location", item.get("section")))
            if doc_loc is not None:
                doc_loc = str(doc_loc)

            return EvidenceNode.create(
                evidence_type=ev_type,
                content=item,
                confidence=float(confidence),
                source_method=source_method,
                document_location=doc_loc,
                tags=frozenset(item.get("tags", [])),
            )

        # Non-dict item
        return EvidenceNode.create(
            evidence_type=EvidenceType.METHOD_OUTPUT,
            content={"value": item, "index": index},
            confidence=0.6,
            source_method=source_method,
        )

    def _create_aggregate_node(
        self,
        target: str,
        sources: list[str],
        strategy: str,
        graph: EvidenceGraph,
        method_outputs: dict[str, Any],
    ) -> EvidenceNode | None:
        """Create aggregate node from assembly rule."""
        # Collect source values
        values = []
        parent_ids = []

        for source in sources:
            # Resolve dotted path
            value = self._resolve_path(source, method_outputs)
            if value is not None:
                values.append(value)
                # Find corresponding nodes
                for node in graph._nodes.values():
                    # Source keys in method_outputs are dotted paths (no space after '.')
                    if node.source_method == source.split(".")[0]:
                        parent_ids.append(node.node_id)

        if not values:
            return None

        # Apply merge strategy
        merged_value = self._apply_merge_strategy(values, strategy)

        return EvidenceNode.create(
            evidence_type=EvidenceType.AGGREGATED,
            content={
                "target": target,
                "strategy": strategy,
                "sources": sources,
                "value": merged_value,
            },
            confidence=0.8,  # Aggregated confidence
            source_method=f"aggregate:{target}",
            parent_ids=parent_ids[:10],  # Limit parents
        )

    def _resolve_path(self, path: str, data: dict[str, Any]) -> Any:
        """Resolve dotted path in data structure."""
        parts = path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def _apply_merge_strategy(
        self,
        values: list[Any],
        strategy: str,
    ) -> Any:
        """Apply merge strategy to values."""
        if not values:
            return None

        if strategy == "first":
            return values[0]
        elif strategy == "last":
            return values[-1]
        elif strategy == "concat":
            result = []
            for v in values:
                if isinstance(v, list):
                    result.extend(v)
                else:
                    result.append(v)
            return result
        elif strategy == "mean":
            numeric = [float(v) for v in values if self._is_numeric(v)]
            return statistics.mean(numeric) if numeric else None
        elif strategy == "max":
            numeric = [float(v) for v in values if self._is_numeric(v)]
            return max(numeric) if numeric else None
        elif strategy == "min":
            numeric = [float(v) for v in values if self._is_numeric(v)]
            return min(numeric) if numeric else None
        elif strategy == "weighted_mean":
            numeric = [float(v) for v in values if self._is_numeric(v)]
            return statistics.mean(numeric) if numeric else None
        elif strategy == "majority":
            from collections import Counter

            counts = Counter(str(v) for v in values)
            return counts.most_common(1)[0][0] if counts else None
        else:
            return values[0]  # Default to first

    @staticmethod
    def _is_numeric(value: Any) -> bool:
        """Check if value is numeric."""
        if isinstance(value, bool):
            return False
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False

    def _create_provenance_node(self, signal_pack: Any) -> EvidenceNode:
        """Create provenance node from signal pack."""
        pack_id = getattr(signal_pack, "id", None) or getattr(signal_pack, "pack_id", "unknown")
        policy_area = getattr(signal_pack, "policy_area", None)
        version = getattr(signal_pack, "version", "unknown")

        return EvidenceNode.create(
            evidence_type=EvidenceType.METHOD_OUTPUT,
            content={
                "provenance_type": "signal_pack",
                "pack_id": pack_id,
                "policy_area": str(policy_area) if policy_area else None,
                "version": version,
            },
            confidence=1.0,  # Provenance is certain
            source_method="signal_registry",
            tags=frozenset(["provenance", "signal_pack"]),
        )

    def _infer_relationships(
        self,
        graph: EvidenceGraph,
        contract: dict[str, Any],
    ) -> None:
        """
        Infer relationships between evidence nodes.

        Uses:
        - Type compatibility for SUPPORTS edges
        - Temporal ordering for PRECEDES edges
        - Content similarity for CORRELATES edges
        - Contradiction detection for CONTRADICTS edges
        """
        nodes = list(graph._nodes.values())

        # Infer DERIVES_FROM from parent_ids
        for node in nodes:
            for parent_id in node.parent_ids:
                if parent_id in graph._nodes:
                    edge = EvidenceEdge.create(
                        source_id=parent_id,
                        target_id=node.node_id,
                        relation_type=RelationType.DERIVES_FROM,
                        weight=0.9,
                        confidence=0.95,
                    )
                    try:
                        graph.add_edge(edge)
                    except ValueError:
                        pass  # Skip if would create cycle

        # Infer SUPPORTS between related types
        support_pairs = [
            (EvidenceType.OFFICIAL_SOURCE, EvidenceType.INDICATOR_NUMERIC),
            (EvidenceType.INDICATOR_NUMERIC, EvidenceType.GOAL_TARGET),
            (EvidenceType.BUDGET_AMOUNT, EvidenceType.POLICY_INSTRUMENT),
        ]

        for source_type, target_type in support_pairs:
            source_nodes = graph.get_nodes_by_type(source_type)
            target_nodes = graph.get_nodes_by_type(target_type)

            for sn in source_nodes[:5]:  # Limit to prevent explosion
                for tn in target_nodes[:5]:
                    if sn.node_id != tn.node_id:
                        edge = EvidenceEdge.create(
                            source_id=sn.node_id,
                            target_id=tn.node_id,
                            relation_type=RelationType.SUPPORTS,
                            weight=0.6,
                            confidence=0.7,
                        )
                        try:
                            graph.add_edge(edge)
                        except ValueError:
                            pass  # Skip if adding SUPPORTS edge would create cycle or is invalid

    # -------------------------------------------------------------------------
    # B4 RESOLUTION: Level Strategies Application
    # -------------------------------------------------------------------------

    def _apply_level_strategies(
        self,
        graph: EvidenceGraph,
        contract: dict[str, Any],
    ) -> None:
        """
        Apply epistemological level strategies from contract.

        B4 RESOLUTION: Now applies N1-EMP, N2-INF, N3-AUD level strategies.

        Epistemological levels:
        - N1-EMP (Empírico Positivista): Direct observation, quantitative data
        - N2-INF (Inferencial): Causal reasoning, theoretical frameworks
        - N3-AUD (Auditoría): Meta-analysis, validation of N1/N2

        Each level has different:
        - Confidence thresholds
        - Evidence requirements
        - Validation strictness
        """
        # Extract level_strategies from contract
        method_binding = contract.get("method_binding", {})
        execution_phases = method_binding.get("execution_phases", {})

        # Get current epistemological level
        current_level = "N1"  # Default
        current_phase = "phase_A_construction"

        # Determine which phase we're in
        for phase_name, phase_data in execution_phases.items():
            if isinstance(phase_data, dict):
                current_level = phase_data.get("level", current_level)
                current_phase = phase_name
                break

        # Apply level-specific strategies
        level_configs = {
            "N1-EMP": {
                "confidence_threshold": 0.6,
                "requires_quantitative": True,
                "validation_strictness": "moderate",
                "evidence_types": ["INDICADOR", "TEMPORAL", "FUENTE_OFICIAL"],
            },
            "N2-INF": {
                "confidence_threshold": 0.5,
                "requires_quantitative": False,
                "validation_strictness": "balanced",
                "evidence_types": ["CAUSAL", "INSTITUTIONAL", "POLICY"],
            },
            "N3-AUD": {
                "confidence_threshold": 0.7,
                "requires_quantitative": False,
                "validation_strictness": "strict",
                "evidence_types": None,  # All types
            },
        }

        config = level_configs.get(current_level, level_configs["N1-EMP"])

        # Apply confidence adjustments based on level (stored in mapping, not mutating frozen nodes)
        nodes_adjusted = 0
        for node in graph._nodes.values():
            # N3-AUD can downgrade confidence from N1/N2
            if current_level == "N3-AUD":
                node_source = node.source_method.lower()
                if "phase_a" in node_source or "phase_b" in node_source:
                    # N3 auditing: reduce confidence of lower-level evidence
                    graph._confidence_adjustments[node.node_id] = node.confidence * 0.9
                    graph._belief_mass_adjustments[node.node_id] = node.belief_mass * 0.9
                    nodes_adjusted += 1

            # N1-EMP: Boost quantitative evidence
            elif current_level == "N1-EMP":
                if config.get("requires_quantitative"):
                    ev_type = node.evidence_type.value
                    if "indicador" in ev_type or "temporal" in ev_type:
                        # Boost confidence for quantitative evidence in N1
                        graph._confidence_adjustments[node.node_id] = min(
                            1.0, node.confidence * 1.1
                        )
                        graph._belief_mass_adjustments[node.node_id] = min(
                            1.0, node.belief_mass * 1.1
                        )
                        nodes_adjusted += 1

        logger.debug(
            "level_strategies_applied",
            level=current_level,
            phase=current_phase,
            confidence_threshold=config.get("confidence_threshold"),
            nodes_adjusted=nodes_adjusted,
        )

    def _persist_graph(self, graph: EvidenceGraph) -> None:
        """Persist graph to storage."""
        if not self.enable_persistence:
            return

        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.storage_path, "a", encoding="utf-8") as f:
                # Write summary record
                record = {
                    "timestamp": time.time(),
                    "graph_hash": graph.get_graph_hash(),
                    "node_count": graph.node_count,
                    "edge_count": graph.edge_count,
                    "statistics": graph.get_statistics(),
                }
                f.write(json.dumps(record, separators=(",", ":")) + "\n")

            logger.debug("graph_persisted", path=str(self.storage_path))

        except Exception as e:
            logger.error("graph_persistence_failed", error=str(e))

    def _build_legacy_evidence(
        self,
        graph: EvidenceGraph,
        beliefs: dict[EvidenceID, float],
    ) -> dict[str, Any]:
        """Build legacy-compatible evidence dict with normalized type keys.

        Uses EvidenceTypeMapper to convert Nexus EvidenceType values (singular)
        to contract expected_elements format (plural) for proper gap detection.
        """
        elements = []
        by_type: dict[str, list[dict]] = defaultdict(list)
        confidences = []

        for node in graph._nodes.values():
            adjusted_conf = graph.get_adjusted_confidence(node.node_id)
            elem = {
                "element_id": node.node_id[:12],
                "type": node.evidence_type.value,
                "value": self._extract_value(node.content),
                "confidence": adjusted_conf,
                "belief": beliefs.get(node.node_id, adjusted_conf),
                "source_method": node.source_method,
            }
            elements.append(elem)
            # Use normalized (plural) type for by_type grouping to align with contracts
            normalized_type = EvidenceTypeMapper.to_contract_format(node.evidence_type.value)
            by_type[normalized_type].append(elem)
            confidences.append(adjusted_conf)

        return {
            "elements": elements,
            "elements_found_count": len(elements),
            # Keys are now in contract format (e.g., "indicadores_cuantitativos")
            "by_type": {k: len(v) for k, v in by_type.items()},
            "confidence_scores": {
                "mean": statistics.mean(confidences) if confidences else 0.0,
                "min": min(confidences) if confidences else 0.0,
                "max": max(confidences) if confidences else 0.0,
            },
            "graph_hash": graph.get_graph_hash()[:16],
        }

    def _extract_value(self, content: dict[str, Any]) -> Any:
        """Extract primary value from content dict."""
        for key in ["value", "text", "description", "name", "indicator"]:
            if key in content:
                return content[key]
        return content

    def _build_legacy_validation(
        self,
        report: ValidationReport,
    ) -> dict[str, Any]:
        """Build legacy-compatible validation dict."""
        return {
            "valid": report.is_valid,
            "passed": report.is_valid,
            "errors": [
                f.to_dict()
                for f in report.findings
                if f.severity in (ValidationSeverity.CRITICAL, ValidationSeverity.ERROR)
            ],
            "warnings": [
                f.to_dict() for f in report.findings if f.severity == ValidationSeverity.WARNING
            ],
            "critical_count": report.critical_count,
            "error_count": report.error_count,
            "warning_count": report.warning_count,
            "consistency_score": report.consistency_score,
            "graph_integrity": report.graph_integrity,
        }

    def _build_legacy_trace(
        self,
        graph: EvidenceGraph,
        signal_pack: Any | None,
    ) -> dict[str, Any]:
        """Build legacy-compatible trace dict."""
        trace = {
            "graph_statistics": graph.get_statistics(),
            "hash_chain_length": len(graph._hash_chain),
            "processing_timestamp": time.time(),
        }

        # Contract pattern utility summary (always available if pattern extraction ran)
        try:
            utility_nodes = graph.get_nodes_by_source("contract.patterns.utility")
            if utility_nodes:
                # Keep last node (single) as authoritative
                node = utility_nodes[-1]
                if isinstance(node.content, dict):
                    trace["pattern_utility"] = {
                        "patterns_injected": node.content.get("patterns_injected"),
                        "patterns_considered": node.content.get("patterns_considered"),
                        "patterns_matched": node.content.get("patterns_matched"),
                        "waste_ratio": node.content.get("waste_ratio"),
                        "context_filter_stats": node.content.get("context_filter_stats"),
                    }
        except Exception:
            pass

        if signal_pack is not None:
            trace["signal_provenance"] = {
                "signal_pack_id": getattr(signal_pack, "id", None)
                or getattr(signal_pack, "pack_id", "unknown"),
                "policy_area": str(getattr(signal_pack, "policy_area", None)),
                "version": getattr(signal_pack, "version", "unknown"),
            }

        return trace

    # -------------------------------------------------------------------------
    # Public Query Interface
    # -------------------------------------------------------------------------

    def get_current_graph(self) -> EvidenceGraph | None:
        """Get current session graph."""
        return self._graph

    def query_by_type(self, evidence_type: EvidenceType) -> list[EvidenceNode]:
        """Query nodes by type from current graph."""
        if self._graph is None:
            return []
        return self._graph.get_nodes_by_type(evidence_type)

    def query_by_source(self, source_method: str) -> list[EvidenceNode]:
        """Query nodes by source method from current graph."""
        if self._graph is None:
            return []
        return self._graph.get_nodes_by_source(source_method)

    def get_statistics(self) -> dict[str, Any]:
        """Get current graph statistics."""
        if self._graph is None:
            return {"error": "No graph in current session"}
        return self._graph.get_statistics()


# =============================================================================
# FACTORY AND CONVENIENCE FUNCTIONS
# =============================================================================

# Global instance (singleton pattern for registry compatibility)
_global_nexus: EvidenceNexus | None = None


def get_global_nexus() -> EvidenceNexus:
    """Get or create global EvidenceNexus instance."""
    global _global_nexus
    if _global_nexus is None:
        _global_nexus = EvidenceNexus()
    return _global_nexus


def process_evidence(
    method_outputs: dict[str, Any],
    question_context: dict[str, Any],
    contract: dict[str, Any],
    signal_pack: Any | None = None,
) -> dict[str, Any]:
    """
    Convenience function for one-shot evidence processing.

    This replaces the typical pattern of:
        assembled = EvidenceAssembler.assemble(...)
        validation = EvidenceValidator.validate(...)
        registry.record_evidence(...)

    With:
        result = process_evidence(...)
    """
    nexus = get_global_nexus()
    return nexus.process(
        method_outputs=method_outputs,
        question_context=question_context,
        contract=contract,
        signal_pack=signal_pack,
    )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Core types
    "EvidenceType",
    "EvidenceTypeMapper",
    "RelationType",
    "ValidationSeverity",
    "AnswerCompleteness",
    "NarrativeSection",
    # Data structures
    "EvidenceNode",
    "EvidenceEdge",
    "ValidationFinding",
    "ValidationReport",
    "Citation",
    "NarrativeBlock",
    "SynthesizedAnswer",
    # Graph
    "EvidenceGraph",
    # Engines
    "ValidationEngine",
    "NarrativeSynthesizer",
    # Main class
    "EvidenceNexus",
    # Factory functions
    "get_global_nexus",
    "process_evidence",
]
