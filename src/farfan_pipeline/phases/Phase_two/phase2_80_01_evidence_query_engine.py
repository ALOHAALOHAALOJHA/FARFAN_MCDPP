"""Evidence Nexus Query Engine - GAP 7 Implementation.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Evidence Query Engine
PHASE_ROLE: SQL-like query interface for Evidence Nexus with causal chain traversal

GAP 7 Implementation: Evidence Nexus Query Engine

This module provides a query interface for the Evidence Nexus Merkle DAG:
- SQL-like SELECT syntax for evidence queries
- Filtering, ordering, and pagination
- Causal chain traversal (upstream/downstream)
- Contradiction and support relationship queries

Requirements Implemented:
    EQ-01: Query engine supports SQL-like SELECT syntax
    EQ-02: Filters support equality, comparison, and containment operators
    EQ-03: Results support ORDER BY and LIMIT clauses
    EQ-04: Causal chain traversal follows Merkle DAG links
    EQ-05: Query results include node metadata and content

Query Language:
    SELECT [fields] FROM evidence
        WHERE [conditions]
        ORDER BY [field] [ASC|DESC]
        LIMIT [n]

    Supported conditions:
        field = 'value'
        field > value
        field < value
        field IN ('value1', 'value2')
        field CONTAINS 'substring'
        contradicts(node_id='xyz')
        supports(node_id='xyz')
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Set

logger = logging.getLogger(__name__)


# === ENUMS AND TYPES ===

class QueryOperator(Enum):
    """Operators for query conditions."""
    EQ = "="
    NE = "!="
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    IN = "IN"
    CONTAINS = "CONTAINS"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"


class TraversalDirection(Enum):
    """Direction for causal chain traversal."""
    DOWNSTREAM = "downstream"  # Follow children
    UPSTREAM = "upstream"      # Follow parents
    BOTH = "both"              # Follow both directions


# === DATA MODELS ===

@dataclass
class QueryCondition:
    """A single condition in a WHERE clause.

    Attributes:
        field: Field name to filter on
        operator: Comparison operator
        value: Value to compare against
    """
    field: str
    operator: QueryOperator
    value: Any


@dataclass
class QueryAST:
    """Abstract Syntax Tree for a parsed query.

    Attributes:
        select_fields: Fields to return (* for all)
        conditions: WHERE clause conditions
        order_by: Field to order by
        order_direction: ASC or DESC
        limit: Maximum results to return
        offset: Number of results to skip
    """
    select_fields: List[str]
    conditions: List[QueryCondition] = field(default_factory=list)
    order_by: Optional[str] = None
    order_direction: str = "ASC"
    limit: Optional[int] = None
    offset: int = 0


@dataclass
class EvidenceNode:
    """Represents a node in the Evidence Nexus.

    Attributes:
        node_id: Unique identifier (SHA-256 hash)
        claim_type: Type of evidence/claim
        content: Content dictionary
        source: Source identifier
        confidence: Confidence score [0, 1]
        timestamp: ISO timestamp
        parent_ids: IDs of parent nodes
        child_ids: IDs of child nodes
        merkle_hash: Merkle DAG hash
        tags: Set of tags
    """
    node_id: str
    claim_type: str
    content: Dict[str, Any]
    source: str
    confidence: float
    timestamp: str
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    merkle_hash: str = ""
    tags: Set[str] = field(default_factory=set)


@dataclass
class CausalEdge:
    """An edge in the causal graph.

    Attributes:
        from_id: Source node ID
        to_id: Target node ID
        relationship_type: Type of relationship
        weight: Edge weight
    """
    from_id: str
    to_id: str
    relationship_type: str
    weight: float = 1.0


@dataclass
class CausalGraph:
    """Result of a causal chain traversal.

    Attributes:
        root_node: Starting node of traversal
        nodes: All nodes in the graph
        edges: All edges in the graph
    """
    root_node: Optional[EvidenceNode]
    nodes: Dict[str, EvidenceNode]
    edges: List[CausalEdge]


@dataclass
class QueryResult:
    """Result of executing a query.

    Attributes:
        nodes: Matching evidence nodes
        total_count: Total matches before LIMIT
        query: Original query string
        execution_time_ms: Query execution time
    """
    nodes: List[EvidenceNode]
    total_count: int
    query: str
    execution_time_ms: float


# === EVIDENCE NEXUS PROTOCOL ===

class EvidenceNexusProtocol(Protocol):
    """Protocol for Evidence Nexus interface."""

    def get_node(self, node_id: str) -> Optional[EvidenceNode]:
        """Get a node by ID."""
        raise NotImplementedError()

    def get_all_nodes(self) -> List[EvidenceNode]:
        """Get all nodes in the nexus."""
        raise NotImplementedError()

    def has_contradiction(self, node_id_a: str, node_id_b: str) -> bool:
        """Check if two nodes contradict each other."""
        raise NotImplementedError()

    def has_support(self, node_id_a: str, node_id_b: str) -> bool:
        """Check if one node supports another."""
        raise NotImplementedError()


# === SIMPLE IN-MEMORY NEXUS FOR STANDALONE USE ===

class SimpleEvidenceNexus:
    """Simple in-memory evidence store for standalone query engine use."""

    def __init__(self):
        self._nodes: Dict[str, EvidenceNode] = {}
        self._contradictions: Set[tuple] = set()
        self._supports: Set[tuple] = set()

    def add_node(self, node: EvidenceNode) -> None:
        """Add a node to the nexus."""
        self._nodes[node.node_id] = node

    def get_node(self, node_id: str) -> Optional[EvidenceNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def get_all_nodes(self) -> List[EvidenceNode]:
        """Get all nodes."""
        return list(self._nodes.values())

    def add_contradiction(self, node_id_a: str, node_id_b: str) -> None:
        """Mark two nodes as contradicting."""
        self._contradictions.add((node_id_a, node_id_b))
        self._contradictions.add((node_id_b, node_id_a))

    def add_support(self, node_id_a: str, node_id_b: str) -> None:
        """Mark that node_a supports node_b."""
        self._supports.add((node_id_a, node_id_b))

    def has_contradiction(self, node_id_a: str, node_id_b: str) -> bool:
        """Check if two nodes contradict."""
        return (node_id_a, node_id_b) in self._contradictions

    def has_support(self, node_id_a: str, node_id_b: str) -> bool:
        """Check if node_a supports node_b."""
        return (node_id_a, node_id_b) in self._supports


# === QUERY ENGINE ===

class EvidenceQueryEngine:
    """
    SQL-like query interface for Evidence Nexus.

    GAP 7 Implementation: Evidence Nexus Query Engine

    Features:
        - SQL-like SELECT syntax
        - Multiple filter operators
        - ORDER BY and LIMIT support
        - Causal chain traversal
        - Contradiction/support queries

    Usage:
        engine = EvidenceQueryEngine(nexus)
        results = engine.query("SELECT * FROM evidence WHERE confidence > 0.8 LIMIT 10")
    """

    def __init__(self, nexus: EvidenceNexusProtocol | SimpleEvidenceNexus):
        """
        Initialize query engine.

        Args:
            nexus: Evidence nexus to query against.
        """
        self.nexus = nexus

    def query(self, query_string: str) -> QueryResult:
        """
        Execute a SQL-like query against the Evidence Nexus.

        Implements EQ-01 through EQ-05.

        Args:
            query_string: SQL-like query string.

        Returns:
            QueryResult with matching EvidenceNode objects.
        """
        import time
        start_time = time.perf_counter()

        ast = self._parse_query(query_string)
        results = self._execute_query(ast)

        execution_time_ms = (time.perf_counter() - start_time) * 1000

        return QueryResult(
            nodes=results,
            total_count=len(results),
            query=query_string,
            execution_time_ms=execution_time_ms,
        )

    def traverse_causal_chain(
        self,
        root_node_id: str,
        max_depth: int = 5,
        direction: str | TraversalDirection = "downstream"
    ) -> CausalGraph:
        """
        Follow causal links from a root claim.

        Implements EQ-04.

        Args:
            root_node_id: Starting node ID.
            max_depth: Maximum traversal depth.
            direction: 'downstream' follows children, 'upstream' follows parents.

        Returns:
            CausalGraph containing all connected nodes.
        """
        if isinstance(direction, str):
            direction = TraversalDirection(direction)

        visited: Dict[str, EvidenceNode] = {}
        edges: List[CausalEdge] = []

        def traverse(node_id: str, depth: int) -> None:
            if depth > max_depth or node_id in visited:
                return

            node = self.nexus.get_node(node_id)
            if not node:
                return

            visited[node_id] = node

            # Determine which IDs to follow based on direction
            if direction == TraversalDirection.DOWNSTREAM:
                next_ids = node.child_ids
                rel_type = "causes"
            elif direction == TraversalDirection.UPSTREAM:
                next_ids = node.parent_ids
                rel_type = "caused_by"
            else:  # BOTH
                next_ids = list(node.child_ids) + list(node.parent_ids)
                rel_type = "related_to"

            for next_id in next_ids:
                edges.append(CausalEdge(
                    from_id=node_id,
                    to_id=next_id,
                    relationship_type=rel_type,
                ))
                traverse(next_id, depth + 1)

        root_node = self.nexus.get_node(root_node_id)
        if root_node:
            traverse(root_node_id, 0)

        return CausalGraph(
            root_node=root_node,
            nodes=visited,
            edges=edges,
        )

    def find_contradictions(self, node_id: str) -> List[EvidenceNode]:
        """
        Find all nodes that contradict a given node.

        Args:
            node_id: Node to find contradictions for.

        Returns:
            List of contradicting nodes.
        """
        return self.query(
            f"SELECT * FROM evidence WHERE contradicts(node_id='{node_id}')"
        ).nodes

    def find_supporting(self, node_id: str) -> List[EvidenceNode]:
        """
        Find all nodes that support a given node.

        Args:
            node_id: Node to find support for.

        Returns:
            List of supporting nodes.
        """
        return self.query(
            f"SELECT * FROM evidence WHERE supports(node_id='{node_id}')"
        ).nodes

    def _parse_query(self, query_string: str) -> QueryAST:
        """
        Parse a SQL-like query string into an AST.

        Implements EQ-01.

        Args:
            query_string: Query string to parse.

        Returns:
            QueryAST representing the parsed query.
        """
        query_string = query_string.strip()

        # Extract SELECT fields
        select_match = re.match(r"SELECT\s+(.+?)\s+FROM", query_string, re.IGNORECASE)
        select_fields = ["*"]
        if select_match:
            fields_str = select_match.group(1)
            select_fields = [f.strip() for f in fields_str.split(",")]

        # Extract WHERE conditions (EQ-02)
        conditions = []
        where_match = re.search(r"WHERE\s+(.+?)(?:\s+ORDER|\s+LIMIT|$)", query_string, re.IGNORECASE)
        if where_match:
            conditions = self._parse_conditions(where_match.group(1))

        # Extract ORDER BY (EQ-03)
        order_by = None
        order_direction = "ASC"
        order_match = re.search(r"ORDER\s+BY\s+(\w+)(?:\s+(ASC|DESC))?", query_string, re.IGNORECASE)
        if order_match:
            order_by = order_match.group(1)
            order_direction = (order_match.group(2) or "ASC").upper()

        # Extract LIMIT (EQ-03)
        limit = None
        limit_match = re.search(r"LIMIT\s+(\d+)", query_string, re.IGNORECASE)
        if limit_match:
            limit = int(limit_match.group(1))

        # Extract OFFSET
        offset = 0
        offset_match = re.search(r"OFFSET\s+(\d+)", query_string, re.IGNORECASE)
        if offset_match:
            offset = int(offset_match.group(1))

        return QueryAST(
            select_fields=select_fields,
            conditions=conditions,
            order_by=order_by,
            order_direction=order_direction,
            limit=limit,
            offset=offset,
        )

    def _parse_conditions(self, conditions_str: str) -> List[QueryCondition]:
        """
        Parse WHERE clause conditions.

        Implements EQ-02.

        Args:
            conditions_str: WHERE clause string.

        Returns:
            List of QueryCondition objects.
        """
        conditions = []
        # Split by AND (simplified - doesn't handle OR or nested conditions)
        parts = re.split(r"\s+AND\s+", conditions_str, flags=re.IGNORECASE)

        for part in parts:
            part = part.strip()
            condition = self._parse_single_condition(part)
            if condition:
                conditions.append(condition)

        return conditions

    def _parse_single_condition(self, condition_str: str) -> Optional[QueryCondition]:
        """
        Parse a single condition.

        Args:
            condition_str: Single condition string.

        Returns:
            QueryCondition or None if parsing fails.
        """
        # Handle function-style conditions (contradicts, supports)
        func_match = re.match(r"(contradicts|supports)\(node_id=['\"](.+?)['\"]\)", condition_str)
        if func_match:
            return QueryCondition(
                field="node_id",
                operator=QueryOperator(func_match.group(1)),
                value=func_match.group(2),
            )

        # Handle CONTAINS
        contains_match = re.match(r"(\w+)\s+CONTAINS\s+['\"](.+?)['\"]", condition_str, re.IGNORECASE)
        if contains_match:
            return QueryCondition(
                field=contains_match.group(1),
                operator=QueryOperator.CONTAINS,
                value=contains_match.group(2),
            )

        # Handle IN clause
        in_match = re.match(r"(\w+)\s+IN\s*\((.+?)\)", condition_str, re.IGNORECASE)
        if in_match:
            values_str = in_match.group(2)
            values = [v.strip().strip("'\"") for v in values_str.split(",")]
            return QueryCondition(
                field=in_match.group(1),
                operator=QueryOperator.IN,
                value=values,
            )

        # Handle comparison operators
        for op_str in [">=", "<=", "!=", ">", "<", "="]:
            if op_str in condition_str:
                parts = condition_str.split(op_str, 1)
                if len(parts) == 2:
                    return QueryCondition(
                        field=parts[0].strip(),
                        operator=QueryOperator(op_str),
                        value=self._parse_value(parts[1].strip()),
                    )

        return None

    def _parse_value(self, value_str: str) -> Any:
        """
        Parse a value string into appropriate type.

        Args:
            value_str: Value string to parse.

        Returns:
            Parsed value (str, int, float, or bool).
        """
        # Remove quotes
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]

        # Try boolean
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # Try numeric
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            return value_str

    def _execute_query(self, ast: QueryAST) -> List[EvidenceNode]:
        """
        Execute a parsed query against the nexus.

        Implements EQ-03 and EQ-05.

        Args:
            ast: Parsed query AST.

        Returns:
            List of matching EvidenceNode objects.
        """
        # Get all nodes (in production, use indices)
        all_nodes = self.nexus.get_all_nodes()

        # Filter by conditions (EQ-02)
        results = [n for n in all_nodes if self._matches_conditions(n, ast.conditions)]

        # Sort if ORDER BY specified (EQ-03)
        if ast.order_by:
            reverse = ast.order_direction == "DESC"
            results.sort(
                key=lambda n: self._get_field_value(n, ast.order_by) or "",
                reverse=reverse
            )

        # Apply OFFSET
        if ast.offset > 0:
            results = results[ast.offset:]

        # Apply LIMIT (EQ-03)
        if ast.limit is not None:
            results = results[:ast.limit]

        return results

    def _matches_conditions(
        self,
        node: EvidenceNode,
        conditions: List[QueryCondition]
    ) -> bool:
        """
        Check if a node matches all conditions.

        Args:
            node: Node to check.
            conditions: List of conditions.

        Returns:
            True if node matches all conditions.
        """
        for condition in conditions:
            if not self._matches_condition(node, condition):
                return False
        return True

    def _matches_condition(self, node: EvidenceNode, condition: QueryCondition) -> bool:
        """
        Check if a node matches a single condition.

        Implements EQ-02.

        Args:
            node: Node to check.
            condition: Condition to match.

        Returns:
            True if node matches condition.
        """
        # Handle special operators
        if condition.operator == QueryOperator.CONTRADICTS:
            return self.nexus.has_contradiction(node.node_id, condition.value)
        if condition.operator == QueryOperator.SUPPORTS:
            return self.nexus.has_support(node.node_id, condition.value)

        # Get field value
        value = self._get_field_value(node, condition.field)

        # Handle comparison operators
        if condition.operator == QueryOperator.EQ:
            return value == condition.value
        elif condition.operator == QueryOperator.NE:
            return value != condition.value
        elif condition.operator == QueryOperator.GT:
            return value is not None and value > condition.value
        elif condition.operator == QueryOperator.LT:
            return value is not None and value < condition.value
        elif condition.operator == QueryOperator.GTE:
            return value is not None and value >= condition.value
        elif condition.operator == QueryOperator.LTE:
            return value is not None and value <= condition.value
        elif condition.operator == QueryOperator.IN:
            return value in condition.value
        elif condition.operator == QueryOperator.CONTAINS:
            return value is not None and condition.value in str(value)

        return False

    def _get_field_value(self, node: EvidenceNode, field: str) -> Any:
        """
        Get field value from a node.

        Args:
            node: Node to get field from.
            field: Field name.

        Returns:
            Field value or None.
        """
        # Direct attributes
        if hasattr(node, field):
            return getattr(node, field)

        # Check content dict
        if node.content and field in node.content:
            return node.content[field]

        return None


# === CONVENIENCE FUNCTIONS ===

def create_query_engine(
    nodes: List[Dict[str, Any]] | None = None
) -> EvidenceQueryEngine:
    """
    Create a query engine with optional initial nodes.

    Args:
        nodes: Optional list of node dictionaries to populate.

    Returns:
        EvidenceQueryEngine instance.
    """
    nexus = SimpleEvidenceNexus()

    if nodes:
        for node_dict in nodes:
            node = EvidenceNode(
                node_id=node_dict.get("node_id", ""),
                claim_type=node_dict.get("claim_type", ""),
                content=node_dict.get("content", {}),
                source=node_dict.get("source", ""),
                confidence=node_dict.get("confidence", 0.0),
                timestamp=node_dict.get("timestamp", ""),
                parent_ids=node_dict.get("parent_ids", []),
                child_ids=node_dict.get("child_ids", []),
                merkle_hash=node_dict.get("merkle_hash", ""),
                tags=set(node_dict.get("tags", [])),
            )
            nexus.add_node(node)

    return EvidenceQueryEngine(nexus)


__all__ = [
    # Enums
    "QueryOperator",
    "TraversalDirection",
    # Data models
    "QueryCondition",
    "QueryAST",
    "EvidenceNode",
    "CausalEdge",
    "CausalGraph",
    "QueryResult",
    # Protocols
    "EvidenceNexusProtocol",
    # Classes
    "SimpleEvidenceNexus",
    "EvidenceQueryEngine",
    # Convenience
    "create_query_engine",
]
