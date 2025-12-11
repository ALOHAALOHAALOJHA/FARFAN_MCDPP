"""
Phase 1 Models - Strict Data Structures
=======================================

Data models for the Phase 1 SPC Ingestion Execution Contract.
These models enforce strict typing and validation for the pipeline.

Integration with CategoriaCausal:
- CausalNode: Typed causal nodes with category (INSUMOS→PROCESOS→PRODUCTOS→RESULTADOS→CAUSALIDAD)
- CausalGraph: Enhanced with typed nodes for DAG validation
- CausalChains (SP5): Chains with hierarchical category validation
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from farfan_pipeline.core.types import CategoriaCausal

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
    original_to_normalized_mapping: Dict[Tuple[int, int], Tuple[int, int]] = field(default_factory=dict)
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


# =============================================================================
# CAUSAL TYPES - Integration with CategoriaCausal from types.py
# =============================================================================

@dataclass
class CausalNode:
    """
    Typed causal node for Theory of Change validation.
    
    Maps to the 5-level causal hierarchy:
    1. INSUMOS (inputs/resources)
    2. PROCESOS (activities/processes)  
    3. PRODUCTOS (outputs/deliverables)
    4. RESULTADOS (outcomes/effects)
    5. CAUSALIDAD (impact/theory of change)
    
    Used by SP5 (CausalChains) and SP6 (IntegratedCausal) for DAG validation.
    """
    id: str
    text: str
    categoria: CategoriaCausal
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Source tracking
    source_span: Optional[Tuple[int, int]] = None
    chunk_id: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.categoria, CategoriaCausal):
            raise TypeError(f"categoria must be CategoriaCausal, got {type(self.categoria)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0,1], got {self.confidence}")


@dataclass 
class CausalEdge:
    """
    Typed causal edge connecting CausalNodes.
    
    Validates hierarchical ordering:
    - source.categoria.value <= target.categoria.value (forward causality)
    - Violations indicate potential theory of change inconsistencies
    """
    source_id: str
    target_id: str
    edge_type: str = "causal"  # causal, temporal, correlational
    weight: float = 1.0
    is_valid_order: bool = True  # Set by validation
    
    def validate_order(self, source_cat: CategoriaCausal, target_cat: CategoriaCausal) -> bool:
        """Validate that causal flow follows hierarchical order."""
        self.is_valid_order = source_cat.value <= target_cat.value
        return self.is_valid_order


@dataclass
class CausalGraph:
    """
    Local causal graph for a chunk.
    
    Enhanced with typed CausalNodes for Theory of Change validation.
    The graph structure follows the DNP causal hierarchy:
    INSUMOS → PROCESOS → PRODUCTOS → RESULTADOS → CAUSALIDAD
    """
    events: List[Any] = field(default_factory=list)
    causes: List[Any] = field(default_factory=list)
    effects: List[Any] = field(default_factory=list)
    
    # Enhanced typed nodes and edges (populated by TeoriaCambio)
    typed_nodes: List[CausalNode] = field(default_factory=list)
    typed_edges: List[CausalEdge] = field(default_factory=list)
    
    # Validation metadata
    is_validated: bool = False
    hierarchy_violations: List[Tuple[str, str]] = field(default_factory=list)
    missing_categories: List[CategoriaCausal] = field(default_factory=list)
    
    def get_nodes_by_category(self, categoria: CategoriaCausal) -> List[CausalNode]:
        """Get all nodes of a specific causal category."""
        return [n for n in self.typed_nodes if n.categoria == categoria]
    
    def validate_hierarchy(self) -> bool:
        """
        Validate that causal edges follow hierarchical ordering.
        Returns True if all edges respect INSUMOS→...→CAUSALIDAD order.
        """
        node_map = {n.id: n for n in self.typed_nodes}
        self.hierarchy_violations = []
        
        for edge in self.typed_edges:
            if edge.source_id in node_map and edge.target_id in node_map:
                source_cat = node_map[edge.source_id].categoria
                target_cat = node_map[edge.target_id].categoria
                if not edge.validate_order(source_cat, target_cat):
                    self.hierarchy_violations.append((edge.source_id, edge.target_id))
        
        # Check for missing categories in complete chains
        present_categories = {n.categoria for n in self.typed_nodes}
        self.missing_categories = [
            cat for cat in CategoriaCausal 
            if cat not in present_categories
        ]
        
        self.is_validated = True
        return len(self.hierarchy_violations) == 0

@dataclass
class Chunk:
    """
    Intermediate chunk representation (SP4-SP10).
    """
    chunk_id: str = ""
    policy_area_id: str = ""
    dimension_id: str = ""
    chunk_index: int = -1
    
    text_spans: List[Tuple[int, int]] = field(default_factory=list)
    sentence_ids: List[int] = field(default_factory=list)
    paragraph_ids: List[int] = field(default_factory=list)
    
    signal_tags: List[str] = field(default_factory=list)
    signal_scores: Dict[str, float] = field(default_factory=dict)
    
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

@dataclass
class CausalChains:
    """
    Output of SP5 - Causal Chain Extraction.
    
    Chains are validated against CategoriaCausal hierarchy:
    - Each chain should progress through categories in order
    - Violations are flagged for review by TeoriaCambio
    """
    chains: List[Any] = field(default_factory=list)
    
    # Enhanced typed chains with category validation
    typed_chains: List[List[CausalNode]] = field(default_factory=list)
    chain_validations: List[bool] = field(default_factory=list)
    
    @property
    def causal_chains(self) -> List[Any]:
        """Alias per FORCING ROUTE [EXEC-SP5-002]."""
        return self.chains
    
    def add_typed_chain(self, chain: List[CausalNode]) -> bool:
        """
        Add a typed chain and validate its hierarchy.
        Returns True if chain follows valid causal order.
        """
        self.typed_chains.append(chain)
        
        # Validate chain order
        is_valid = True
        for i in range(len(chain) - 1):
            if chain[i].categoria.value > chain[i+1].categoria.value:
                is_valid = False
                break
        
        self.chain_validations.append(is_valid)
        return is_valid
    
    def get_valid_chains(self) -> List[List[CausalNode]]:
        """Get only chains that pass hierarchy validation."""
        return [
            chain for chain, valid in zip(self.typed_chains, self.chain_validations)
            if valid
        ]
    
    def get_invalid_chains(self) -> List[List[CausalNode]]:
        """Get chains that violate hierarchy (for review)."""
        return [
            chain for chain, valid in zip(self.typed_chains, self.chain_validations)
            if not valid
        ]

@dataclass
class IntegratedCausal:
    """
    Output of SP6 - Integrated Causal Graph.
    
    Aggregates CausalGraphs from all chunks into a unified DAG.
    Validated by TeoriaCambio for structural consistency.
    """
    global_graph: Any = None
    
    # Enhanced: unified typed graph with all nodes/edges
    unified_nodes: List[CausalNode] = field(default_factory=list)
    unified_edges: List[CausalEdge] = field(default_factory=list)
    
    # Validation results from TeoriaCambio
    is_valid_dag: bool = False
    complete_paths: List[List[str]] = field(default_factory=list)  # Paths INSUMOS→CAUSALIDAD
    validation_score: float = 0.0
    
    @property
    def integrated_causal(self) -> Any:
        """Alias per FORCING ROUTE [EXEC-SP6-002]."""
        return self.global_graph
    
    def count_by_category(self) -> Dict[CategoriaCausal, int]:
        """Count nodes by causal category."""
        counts: Dict[CategoriaCausal, int] = {cat: 0 for cat in CategoriaCausal}
        for node in self.unified_nodes:
            counts[node.categoria] += 1
        return counts
    
    def get_category_coverage(self) -> float:
        """
        Calculate coverage score (0-1) based on represented categories.
        Full coverage = all 5 categories present.
        """
        counts = self.count_by_category()
        present = sum(1 for c in counts.values() if c > 0)
        return present / len(CategoriaCausal)

@dataclass
class Arguments:
    """Output of SP7."""
    arguments_map: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def argumentative_structure(self) -> Dict[str, Any]:
        """Alias per FORCING ROUTE [EXEC-SP7-002]."""
        return self.arguments_map

@dataclass
class Temporal:
    """Output of SP8."""
    timeline: List[Any] = field(default_factory=list)
    
    @property
    def temporal_markers(self) -> List[Any]:
        """Alias per FORCING ROUTE [EXEC-SP8-002]."""
        return self.timeline

@dataclass
class Discourse:
    """Output of SP9."""
    patterns: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def discourse_structure(self) -> Dict[str, Any]:
        """Alias per FORCING ROUTE [EXEC-SP9-002]."""
        return self.patterns

@dataclass
class Strategic:
    """Output of SP10."""
    priorities: Dict[str, float] = field(default_factory=dict)
    
    @property
    def strategic_integration(self) -> Dict[str, float]:
        """Alias per FORCING ROUTE [EXEC-SP10-002]."""
        return self.priorities

@dataclass(frozen=True)
class SmartChunk:
    """
    Final chunk representation (SP11-SP15).
    FOUNDATIONAL: chunk_id is PRIMARY identifier (PA##-DIM##)
    policy_area_id and dimension_id are AUTO-DERIVED from chunk_id
    """
    chunk_id: str
    text: str = ""
    chunk_type: str = "semantic"
    source_page: Optional[int] = None
    chunk_index: int = -1
    
    policy_area_id: str = field(default="", init=False)
    dimension_id: str = field(default="", init=False)
    
    causal_graph: CausalGraph = field(default_factory=CausalGraph)
    temporal_markers: Dict[str, Any] = field(default_factory=dict)
    arguments: Dict[str, Any] = field(default_factory=dict)
    discourse_mode: str = "unknown"
    strategic_rank: int = 0
    irrigation_links: List[Any] = field(default_factory=list)
    
    signal_tags: List[str] = field(default_factory=list)
    signal_scores: Dict[str, float] = field(default_factory=dict)
    signal_version: str = "v1.0.0"
    
    rank_score: float = 0.0
    signal_weighted_score: float = 0.0
    
    def __post_init__(self):
        CHUNK_ID_PATTERN = r'^PA(0[1-9]|10)-DIM0[1-6]$'
        if not re.match(CHUNK_ID_PATTERN, self.chunk_id):
            raise ValueError(f"Invalid chunk_id format: {self.chunk_id}. Must match {CHUNK_ID_PATTERN}")
        
        parts = self.chunk_id.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid chunk_id structure: {self.chunk_id}")
        
        pa_part, dim_part = parts
        object.__setattr__(self, 'policy_area_id', pa_part)
        object.__setattr__(self, 'dimension_id', dim_part)

@dataclass
class ValidationResult:
    """Output of SP13 - Integrity Validation."""
    status: str = "INVALID"
    chunk_count: int = 0
    violations: List[str] = field(default_factory=list)
    pa_dim_coverage: str = "INCOMPLETE"
