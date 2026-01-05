"""
Interaction Governor
====================
Prevents uncontrolled method interactions in Phase-2. 

DESIGN PATTERNS:
- Mediator Pattern: Coordinates method interactions
- Visitor Pattern: Traverses dependency graph for validation

INVARIANTS:
- INV-INT-001: Dependency graph must be acyclic (DAG)
- INV-INT-002: Multiplicative fusion bounded in [0.01, 10. 0]
- INV-INT-003: Veto cascade respects specificity ordering
- INV-INT-004: No level inversions (N3 cannot depend on N2 output directly)
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Final, Iterator, Sequence

logger = logging.getLogger(__name__)


# Bounds for multiplicative fusion
_MIN_PRODUCT:  Final[float] = 0.01
_MAX_PRODUCT:  Final[float] = 10.0


class InteractionViolationType(Enum):
    """Types of interaction violations."""
    CYCLE_DETECTED = auto()
    LEVEL_INVERSION = auto()
    UNBOUNDED_MULTIPLICATION = auto()
    VETO_DEADLOCK = auto()


@dataclass(frozen=True)
class InteractionViolation:
    """Record of an interaction violation."""
    violation_type: InteractionViolationType
    description: str
    involved_methods: tuple[str, ...]
    severity: str  # "FATAL" or "WARNING"


@dataclass(frozen=True)
class MethodNode:
    """Node in the method dependency graph."""
    method_id: str
    level: str  # N1-EMP, N2-INF, N3-AUD
    provides: frozenset[str]
    requires: frozenset[str]
    specificity_score: float = 1.0  # Higher = more specific


@dataclass
class DependencyGraph:
    """
    Directed graph of method dependencies.
    
    Edges point from provider to consumer: 
    A -> B means "A provides something B requires"
    """
    
    def __init__(self) -> None:
        self._nodes: dict[str, MethodNode] = {}
        self._edges: dict[str, set[str]] = {}  # source -> set of targets
        self._reverse_edges: dict[str, set[str]] = {}  # target -> set of sources
    
    def add_node(self, node: MethodNode) -> None:
        """Add a method node."""
        self._nodes[node.method_id] = node
        if node.method_id not in self._edges:
            self._edges[node.method_id] = set()
        if node.method_id not in self._reverse_edges:
            self._reverse_edges[node.method_id] = set()
    
    def add_edge(self, source: str, target: str) -> None:
        """Add dependency edge (source provides to target)."""
        if source not in self._nodes or target not in self._nodes:
            raise ValueError(f"Both nodes must exist: {source}, {target}")
        self._edges[source].add(target)
        self._reverse_edges[target].add(source)
    
    def get_node(self, method_id: str) -> MethodNode | None: 
        return self._nodes.get(method_id)
    
    def get_successors(self, method_id: str) -> Iterator[str]:
        """Methods that depend on this method."""
        yield from self._edges.get(method_id, set())
    
    def get_predecessors(self, method_id: str) -> Iterator[str]:
        """Methods this method depends on."""
        yield from self._reverse_edges.get(method_id, set())
    
    def get_in_degree(self, method_id: str) -> int:
        return len(self._reverse_edges.get(method_id, set()))
    
    def get_out_degree(self, method_id: str) -> int:
        return len(self._edges.get(method_id, set()))
    
    def get_all_nodes(self) -> Iterator[MethodNode]:
        yield from self._nodes.values()
    
    def node_count(self) -> int:
        return len(self._nodes)
    
    def edge_count(self) -> int:
        return sum(len(targets) for targets in self._edges.values())


class CycleDetector:
    """
    Detects cycles in dependency graph using DFS.
    
    INV-INT-001: Graph must be acyclic. 
    """
    
    def __init__(self, graph: DependencyGraph) -> None:
        self._graph = graph
    
    def find_cycles(self) -> list[list[str]]:
        """Find all cycles in the graph."""
        visited:  set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[list[str]] = []
        path: list[str] = []
        
        def dfs(node_id: str) -> None:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for successor in self._graph.get_successors(node_id):
                if successor not in visited:
                    dfs(successor)
                elif successor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(successor)
                    cycle = path[cycle_start: ] + [successor]
                    cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node_id)
        
        for node in self._graph.get_all_nodes():
            if node.method_id not in visited: 
                dfs(node.method_id)
        
        return cycles
    
    def is_acyclic(self) -> bool:
        """Check if graph is acyclic."""
        return len(self.find_cycles()) == 0


class LevelInversionDetector:
    """
    Detects level inversions in dependency graph.
    
    INV-INT-004: Higher levels should not depend on lower levels.
    N1 -> N2 -> N3 is valid
    N3 -> N2 is invalid (inversion)
    """
    
    _LEVEL_ORDER: Final[dict[str, int]] = {
        "N1-EMP": 1,
        "N2-INF": 2,
        "N3-AUD": 3,
    }
    
    def __init__(self, graph: DependencyGraph) -> None:
        self._graph = graph
    
    def find_inversions(self) -> list[tuple[str, str]]:
        """Find all level inversions (source level > target level)."""
        inversions: list[tuple[str, str]] = []
        
        for node in self._graph.get_all_nodes():
            source_order = self._LEVEL_ORDER.get(node.level, 0)
            
            for successor_id in self._graph.get_successors(node.method_id):
                successor = self._graph.get_node(successor_id)
                if successor: 
                    target_order = self._LEVEL_ORDER.get(successor.level, 0)
                    if source_order > target_order: 
                        inversions.append((node.method_id, successor_id))
        
        return inversions


def bounded_multiplicative_fusion(
    weights: Sequence[float],
) -> float:
    """
    Multiplicative fusion with bounds.
    
    INV-INT-002: Result in [0.01, 10.0]
    """
    if not weights:
        return 1.0
    
    raw_product = math.prod(weights)
    bounded = max(_MIN_PRODUCT, min(_MAX_PRODUCT, raw_product))
    
    if bounded != raw_product:
        logger.warning(
            f"Multiplicative fusion bounded:  {raw_product:.4f} -> {bounded:.4f}"
        )
    
    return bounded


@dataclass
class VetoResult:
    """Result of a veto check."""
    method_id: str
    veto_triggered: bool
    target_nodes: frozenset[str]
    specificity_score: float
    reason: str


@dataclass
class VetoReport:
    """Report of veto cascade execution."""
    effective_vetos: list[VetoResult] = field(default_factory=list)
    redundant_vetos: list[VetoResult] = field(default_factory=list)
    nodes_removed: set[str] = field(default_factory=set)


class VetoCoordinator:
    """
    Coordinates N3-AUD veto execution.
    
    INV-INT-003: Veto cascade respects specificity ordering.
    Most specific vetos applied first to prevent redundancy.
    """
    
    def __init__(self, graph: DependencyGraph) -> None:
        self._graph = graph
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def execute_veto_cascade(
        self,
        veto_results:  Sequence[VetoResult],
    ) -> VetoReport:
        """
        Execute veto cascade in specificity order.
        
        Args:
            veto_results:  Results from N3-AUD methods
            
        Returns:
            VetoReport with effective and redundant vetos
        """
        report = VetoReport()
        
        # Sort by specificity (highest first)
        sorted_results = sorted(
            veto_results,
            key=lambda r: r.specificity_score,
            reverse=True,
        )
        
        for result in sorted_results:
            if not result.veto_triggered:
                continue
            
            # Check if all target nodes already vetoed
            already_vetoed = result.target_nodes <= report.nodes_removed
            
            if already_vetoed:
                report.redundant_vetos.append(result)
                self._logger.debug(
                    f"Redundant veto:  {result.method_id} targets already vetoed"
                )
            else:
                report.effective_vetos.append(result)
                report.nodes_removed.update(result.target_nodes)
                self._logger.info(
                    f"Effective veto: {result.method_id} removed {result.target_nodes}"
                )
        
        return report


class InteractionGovernor: 
    """
    Main coordinator for method interaction governance.
    
    Combines all validators and coordinators. 
    """
    
    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def build_dependency_graph(
        self,
        methods:  Sequence[MethodNode],
    ) -> DependencyGraph: 
        """
        Build dependency graph from method nodes.
        
        Edges are inferred from provides/requires relationships.
        """
        graph = DependencyGraph()
        
        # Add all nodes
        for method in methods: 
            graph.add_node(method)
        
        # Build provides index
        provides_index:  dict[str, str] = {}  # capability -> method_id
        for method in methods:
            for capability in method.provides:
                provides_index[capability] = method.method_id
        
        # Add edges based on requires
        for method in methods: 
            for requirement in method.requires:
                provider = provides_index.get(requirement)
                if provider:
                    graph.add_edge(provider, method.method_id)
        
        return graph
    
    def validate_graph(
        self,
        graph: DependencyGraph,
    ) -> list[InteractionViolation]: 
        """
        Validate dependency graph for all invariants.
        
        Returns list of violations (empty = valid).
        """
        violations: list[InteractionViolation] = []
        
        # INV-INT-001: Acyclicity
        cycle_detector = CycleDetector(graph)
        cycles = cycle_detector.find_cycles()
        for cycle in cycles:
            violations.append(InteractionViolation(
                violation_type=InteractionViolationType.CYCLE_DETECTED,
                description=f"Dependency cycle:  {' -> '.join(cycle)}",
                involved_methods=tuple(cycle),
                severity="FATAL",
            ))
        
        # INV-INT-004: Level inversions
        inversion_detector = LevelInversionDetector(graph)
        inversions = inversion_detector.find_inversions()
        for source, target in inversions:
            source_node = graph.get_node(source)
            target_node = graph.get_node(target)
            violations.append(InteractionViolation(
                violation_type=InteractionViolationType.LEVEL_INVERSION,
                description=(
                    f"Level inversion: {source} ({source_node.level if source_node else '?'}) "
                    f"-> {target} ({target_node.level if target_node else '?'})"
                ),
                involved_methods=(source, target),
                severity="WARNING",
            ))
        
        return violations
    
    def has_fatal_violations(
        self,
        violations:  Sequence[InteractionViolation],
    ) -> bool:
        """Check if any violations are fatal."""
        return any(v.severity == "FATAL" for v in violations)
