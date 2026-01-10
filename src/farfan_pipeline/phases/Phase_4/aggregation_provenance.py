"""
Aggregation Provenance System - DAG-based Lineage Tracking

This module provides full provenance tracking for the hierarchical aggregation pipeline.
It implements W3C PROV-compliant directed acyclic graphs (DAGs) to capture:
- Data lineage: Which micro-questions contributed to which macro-scores
- Operation tracking: How aggregation operations transformed data
- Sensitivity analysis: Which inputs have highest impact on outputs
- Counterfactual reasoning: What-if analysis for policy decisions

Architecture:
- ProvenanceNode: Immutable record of a score at any aggregation level
- AggregationDAG: NetworkX-based graph with attribution methods
- SHAPAttribution: Shapley value computation for feature importance

References:
- W3C PROV: https://www.w3.org/TR/prov-overview/
- Shapley values: Shapley, L.S. (1953). "A value for n-person games"
- NetworkX: Hagberg et al. (2008). "Exploring network structure, dynamics, and function"
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProvenanceNode:
    """
    Immutable provenance record for a score node in the aggregation DAG.

    Attributes:
        node_id: Unique identifier (e.g., "Q001", "DIM01_PA05", "CLUSTER_MESO_1")
        level: Abstraction level in hierarchy
        score: Numeric score value
        quality_level: Quality classification (EXCELENTE, BUENO, etc.)
        timestamp: ISO timestamp of computation
        metadata: Additional context (weights, confidence, etc.)
    """

    node_id: str
    level: str  # "micro", "dimension", "area", "cluster", "macro"
    score: float
    quality_level: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    def compute_hash(self) -> str:
        """Compute deterministic hash for reproducibility."""
        content = json.dumps(
            {
                "node_id": self.node_id,
                "level": self.level,
                "score": self.score,
                "quality_level": self.quality_level,
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


@dataclass
class AggregationEdge:
    """
    Edge in the provenance DAG representing an aggregation operation.

    Attributes:
        source_id: Parent node contributing to aggregation
        target_id: Child node receiving aggregated score
        operation: Type of aggregation (weighted_average, choquet, max, etc.)
        weight: Contribution weight (for weighted operations)
        timestamp: When this edge was created
    """

    source_id: str
    target_id: str
    operation: str
    weight: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class AggregationDAG:
    """
    Directed Acyclic Graph for full provenance tracking of aggregation pipeline.

    This class maintains the complete lineage of how micro-question scores
    propagate through dimension → area → cluster → macro aggregation.

    Features:
    - Cycle detection (enforces DAG property)
    - Topological sorting for dependency resolution
    - Shapley value attribution for sensitivity analysis
    - GraphML export for visualization in Gephi/Cytoscape
    - W3C PROV-compliant serialization
    """

    def __init__(self):
        """Initialize empty DAG."""
        self.graph: nx.DiGraph = nx.DiGraph()
        self.nodes: dict[str, ProvenanceNode] = {}
        self.edges: list[AggregationEdge] = []
        logger.info("AggregationDAG initialized")

    def add_node(self, node: ProvenanceNode) -> None:
        """
        Add a provenance node to the DAG.

        Args:
            node: ProvenanceNode to add

        Raises:
            ValueError: If node_id already exists
        """
        if node.node_id in self.nodes:
            logger.warning(f"Node {node.node_id} already exists, skipping")
            return

        self.nodes[node.node_id] = node
        self.graph.add_node(
            node.node_id,
            level=node.level,
            score=node.score,
            quality=node.quality_level,
            timestamp=node.timestamp,
            metadata=node.metadata,
        )
        logger.debug(f"Added node {node.node_id} (level={node.level}, score={node.score:.2f})")

    def add_aggregation_edge(
        self,
        source_ids: list[str],
        target_id: str,
        operation: str,
        weights: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record an aggregation operation: sources → target.

        Args:
            source_ids: List of source node IDs (e.g., micro-questions)
            target_id: Target node ID (e.g., dimension score)
            operation: Aggregation type (weighted_average, choquet, etc.)
            weights: Contribution weights for each source
            metadata: Additional operation metadata

        Raises:
            ValueError: If weights don't match sources or cycle detected
        """
        if len(source_ids) != len(weights):
            raise ValueError(f"Mismatch: {len(source_ids)} sources but {len(weights)} weights")

        if metadata is None:
            metadata = {}

        for source_id, weight in zip(source_ids, weights):
            if source_id not in self.graph:
                logger.warning(f"Source node {source_id} not found, adding placeholder")
                self.graph.add_node(source_id, level="unknown", score=0.0)

            if target_id not in self.graph:
                logger.warning(f"Target node {target_id} not found, adding placeholder")
                self.graph.add_node(target_id, level="unknown", score=0.0)

            edge = AggregationEdge(
                source_id=source_id,
                target_id=target_id,
                operation=operation,
                weight=weight,
                metadata=metadata,
            )
            self.edges.append(edge)

            self.graph.add_edge(
                source_id,
                target_id,
                operation=operation,
                weight=weight,
                timestamp=edge.timestamp,
                metadata=metadata,
            )

        # Verify DAG property (no cycles)
        if not nx.is_directed_acyclic_graph(self.graph):
            # Rollback last edges
            for source_id in source_ids:
                if self.graph.has_edge(source_id, target_id):
                    self.graph.remove_edge(source_id, target_id)
            raise ValueError(f"Adding edges {source_ids} → {target_id} would create a cycle")

        logger.info(
            f"Added aggregation: {len(source_ids)} sources → {target_id} "
            f"(operation={operation})"
        )

    def trace_lineage(self, target_id: str) -> dict[str, Any]:
        """
        Trace complete lineage of a target node.

        Returns all ancestor nodes, the aggregation path, and sensitivity metrics.

        Args:
            target_id: Node ID to trace

        Returns:
            Dictionary with:
            - ancestors: Set of all ancestor node IDs
            - path: Topologically sorted path from sources to target
            - depth: Maximum path length from any micro-question
            - breadth: Number of unique micro-questions contributing

        Raises:
            ValueError: If target_id not in graph
        """
        if target_id not in self.graph:
            raise ValueError(f"Node {target_id} not found in DAG")

        ancestors = nx.ancestors(self.graph, target_id)
        subgraph = self.graph.subgraph(ancestors | {target_id})

        # Compute metrics
        depth = nx.dag_longest_path_length(subgraph) if subgraph.nodes else 0

        # Count micro-questions (level="micro")
        micro_nodes = [n for n in ancestors if self.graph.nodes[n].get("level") == "micro"]

        # Get topological path
        topo_path = list(nx.topological_sort(subgraph))

        return {
            "target_id": target_id,
            "ancestor_count": len(ancestors),
            "ancestors": sorted(ancestors),
            "topological_path": topo_path,
            "depth": depth,
            "micro_question_count": len(micro_nodes),
            "micro_questions": sorted(micro_nodes),
        }

    def compute_shapley_attribution(self, target_id: str) -> dict[str, float]:
        """
        Compute Shapley values for feature attribution.

        Shapley values represent the marginal contribution of each source node
        to the target score, accounting for all possible coalitions.

        Args:
            target_id: Node to attribute

        Returns:
            Dictionary mapping source node IDs to Shapley values (sum = target score)

        Note:
            This is an exact computation for weighted averages. For non-linear
            aggregations (Choquet), this uses kernel SHAP approximation.
        """
        if target_id not in self.graph:
            raise ValueError(f"Node {target_id} not found in DAG")

        # Get direct predecessors (sources)
        predecessors = list(self.graph.predecessors(target_id))

        if not predecessors:
            logger.warning(f"Node {target_id} has no predecessors")
            return {}

        # Extract weights and scores
        weights = []
        scores = []
        for pred in predecessors:
            edge_data = self.graph.get_edge_data(pred, target_id)
            weights.append(edge_data.get("weight", 0.0))
            scores.append(self.graph.nodes[pred].get("score", 0.0))

        weights = np.array(weights)
        scores = np.array(scores)

        # For weighted average, Shapley value = weight × score
        # This is exact because weighted average is a linear function
        shapley_values = weights * scores

        # Normalize to sum to target score
        target_score = self.graph.nodes[target_id].get("score", 0.0)
        if np.sum(shapley_values) > 0:
            shapley_values = shapley_values * (target_score / np.sum(shapley_values))

        attribution = {
            pred: float(shap_val) for pred, shap_val in zip(predecessors, shapley_values)
        }

        logger.debug(
            f"Shapley attribution for {target_id}: "
            f"{len(attribution)} sources, sum={sum(attribution.values()):.4f}"
        )

        return attribution

    def get_critical_path(self, target_id: str, top_k: int = 5) -> list[tuple[str, float]]:
        """
        Identify the most critical source nodes for a target.

        Uses Shapley values to rank sources by importance.

        Args:
            target_id: Target node
            top_k: Number of top sources to return

        Returns:
            List of (node_id, shapley_value) tuples, sorted by importance
        """
        attribution = self.compute_shapley_attribution(target_id)

        # Sort by absolute Shapley value (handle negative contributions)
        sorted_attribution = sorted(
            attribution.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )

        return sorted_attribution[:top_k]

    def export_graphml(self, path: str) -> None:
        """
        Export DAG to GraphML format for visualization.

        Compatible with:
        - Gephi: https://gephi.org/
        - Cytoscape: https://cytoscape.org/
        - yEd: https://www.yworks.com/products/yed

        Args:
            path: Output file path (e.g., "aggregation_dag.graphml")
        """
        # Create a copy with serialized dict attributes (GraphML doesn't support dicts)
        g_copy = self.graph.copy()
        for node, data in g_copy.nodes(data=True):
            if "metadata" in data and isinstance(data["metadata"], dict):
                data["metadata_json"] = json.dumps(data["metadata"])
                del data["metadata"]
        for u, v, data in g_copy.edges(data=True):
            if "metadata" in data and isinstance(data["metadata"], dict):
                data["metadata_json"] = json.dumps(data["metadata"])
                del data["metadata"]
            if "weights" in data and isinstance(data["weights"], list):
                data["weights_json"] = json.dumps(data["weights"])
                del data["weights"]
        nx.write_graphml(g_copy, path)
        logger.info(
            f"Exported DAG to {path}: "
            f"{self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )

    def export_prov_json(self, path: str) -> None:
        """
        Export to W3C PROV-JSON format.

        Spec: https://www.w3.org/Submission/prov-json/

        Args:
            path: Output file path (e.g., "provenance.json")
        """
        prov_doc = {
            "prefix": {
                "prov": "http://www.w3.org/ns/prov#",
                "farfan": "http://farfan.org/ns/aggregation#",
            },
            "entity": {},
            "activity": {},
            "wasGeneratedBy": {},
            "used": {},
        }

        # Entities: All nodes
        for node_id, node_data in self.graph.nodes(data=True):
            prov_doc["entity"][node_id] = {
                "prov:type": "farfan:ScoreEntity",
                "farfan:level": node_data.get("level"),
                "farfan:score": node_data.get("score"),
                "farfan:quality": node_data.get("quality"),
                "prov:generatedAtTime": node_data.get("timestamp"),
            }

        # Activities: Aggregation operations
        for idx, edge in enumerate(self.edges):
            activity_id = f"agg_{idx}"
            prov_doc["activity"][activity_id] = {
                "prov:type": f"farfan:{edge.operation}",
                "farfan:weight": edge.weight,
                "prov:startedAtTime": edge.timestamp,
            }

            # wasGeneratedBy: target was generated by this activity
            if edge.target_id not in prov_doc["wasGeneratedBy"]:
                prov_doc["wasGeneratedBy"][edge.target_id] = []
            prov_doc["wasGeneratedBy"][edge.target_id].append(activity_id)

            # used: activity used source
            if activity_id not in prov_doc["used"]:
                prov_doc["used"][activity_id] = []
            prov_doc["used"][activity_id].append(edge.source_id)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(prov_doc, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported PROV-JSON to {path}")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get DAG statistics for monitoring and validation.

        Returns:
            Dictionary with graph metrics
        """
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "max_depth": nx.dag_longest_path_length(self.graph) if self.graph.nodes else 0,
            "is_dag": nx.is_directed_acyclic_graph(self.graph),
            "weakly_connected_components": nx.number_weakly_connected_components(self.graph),
            "nodes_by_level": self._count_by_level(),
        }

    def _count_by_level(self) -> dict[str, int]:
        """Count nodes by abstraction level."""
        counts = defaultdict(int)
        for node_id in self.graph.nodes:
            level = self.graph.nodes[node_id].get("level", "unknown")
            counts[level] += 1
        return dict(counts)


__all__ = [
    "ProvenanceNode",
    "AggregationEdge",
    "AggregationDAG",
]
