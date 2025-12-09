"""Stub for aggregation_provenance to allow imports."""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class ProvenanceNode:
    node_id: str
    level: str
    score: float
    quality_level: str
    metadata: dict[str, Any] = field(default_factory=dict)

class AggregationDAG:
    def __init__(self):
        self.nodes = {}
    
    def add_node(self, node):
        self.nodes[node.node_id] = node
    
    def add_aggregation_edge(self, source_ids, target_id, operation, weights, metadata):
        pass
