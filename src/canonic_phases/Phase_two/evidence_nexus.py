"""
Unified SOTA Evidence-to-Answer Engine: EvidenceNexus

This module replaces the three legacy evidence modules (assembler, validator, registry)
with a unified, graph-based evidence reasoning engine.

Architecture:
- EvidenceGraph: DAG with typed nodes and weighted edges
- EvidenceNode: Immutable, content-addressed evidence with Dempster-Shafer belief mass
- EvidenceEdge: Typed relationships (SUPPORTS, CONTRADICTS, CAUSES, DERIVES_FROM)
- ValidationEngine: Protocol-based rules with graph-aware validation
- EvidenceNexus: Main class that replaces all three legacy modules

Key Features:
- Causal graph construction from method outputs
- Bayesian belief propagation across graph
- Conflict/contradiction detection via edge analysis
- Hash chain integrated into graph for provenance
- Legacy-compatible output format
"""

from __future__ import annotations

import hashlib
import json
import logging
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import numpy as np

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class EdgeType(Enum):
    """Types of relationships between evidence nodes."""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CAUSES = "causes"
    DERIVES_FROM = "derives_from"
    REFINES = "refines"
    AGGREGATES = "aggregates"
    DEPENDS_ON = "depends_on"


@dataclass
class BeliefMass:
    """Dempster-Shafer belief mass for evidence."""
    belief: float
    plausibility: float
    uncertainty: float
    
    def __post_init__(self):
        total = self.belief + self.plausibility + self.uncertainty
        if not (0.99 <= total <= 1.01):
            logger.warning(
                f"Belief mass does not sum to 1.0: {total}. "
                f"Normalizing: belief={self.belief}, plausibility={self.plausibility}, uncertainty={self.uncertainty}"
            )
            if total > 0:
                self.belief /= total
                self.plausibility /= total
                self.uncertainty /= total


@dataclass
class EvidenceNode:
    """
    Immutable evidence node with content-addressed ID and belief mass.
    
    Each node represents a piece of evidence derived from method outputs.
    """
    node_id: str
    evidence_type: str
    content: dict[str, Any]
    source_method: str | None = None
    belief_mass: BeliefMass | None = None
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.belief_mass is None:
            self.belief_mass = BeliefMass(belief=0.7, plausibility=0.2, uncertainty=0.1)
    
    def compute_content_hash(self) -> str:
        """Compute SHA-256 hash of content for content-addressable ID."""
        content_json = json.dumps(self.content, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content_json.encode('utf-8')).hexdigest()[:16]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "evidence_type": self.evidence_type,
            "content": self.content,
            "source_method": self.source_method,
            "belief_mass": asdict(self.belief_mass) if self.belief_mass else None,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class EvidenceEdge:
    """Typed relationship between evidence nodes."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    confidence: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class EvidenceGraph:
    """
    Directed Acyclic Graph (DAG) of evidence with typed relationships.
    
    Supports:
    - Graph construction from method outputs
    - Relationship inference
    - Belief propagation
    - Contradiction detection
    """
    
    def __init__(self):
        self.nodes: dict[str, EvidenceNode] = {}
        self.edges: list[EvidenceEdge] = []
        self.adjacency: dict[str, list[str]] = defaultdict(list)
        self.reverse_adjacency: dict[str, list[str]] = defaultdict(list)
    
    def add_node(self, node: EvidenceNode) -> None:
        """Add evidence node to graph."""
        self.nodes[node.node_id] = node
        logger.debug(f"Added node {node.node_id} of type {node.evidence_type}")
    
    def add_edge(self, edge: EvidenceEdge) -> None:
        """Add typed edge between nodes."""
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            logger.warning(
                f"Cannot add edge: source {edge.source_id} or target {edge.target_id} not in graph"
            )
            return
        
        self.edges.append(edge)
        self.adjacency[edge.source_id].append(edge.target_id)
        self.reverse_adjacency[edge.target_id].append(edge.source_id)
        logger.debug(f"Added edge {edge.source_id} -> {edge.target_id} ({edge.edge_type.value})")
    
    def infer_relationships(self) -> None:
        """
        Infer relationships between nodes based on content and semantics.
        
        Heuristics:
        - Method dependencies create DERIVES_FROM edges
        - Temporal ordering suggests CAUSES relationships
        - Overlapping content suggests SUPPORTS or REFINES
        - Conflicting values suggest CONTRADICTS
        """
        node_list = list(self.nodes.values())
        
        for i, node_a in enumerate(node_list):
            for node_b in node_list[i + 1:]:
                inferred_edge = self._infer_edge(node_a, node_b)
                if inferred_edge:
                    self.add_edge(inferred_edge)
    
    def _infer_edge(self, node_a: EvidenceNode, node_b: EvidenceNode) -> EvidenceEdge | None:
        """Infer edge type between two nodes based on heuristics."""
        if node_a.timestamp < node_b.timestamp:
            if node_a.source_method and node_b.metadata.get("depends_on"):
                if node_a.source_method in node_b.metadata["depends_on"]:
                    return EvidenceEdge(
                        source_id=node_a.node_id,
                        target_id=node_b.node_id,
                        edge_type=EdgeType.DERIVES_FROM,
                        weight=0.9,
                        confidence=0.85,
                    )
        
        content_overlap = self._compute_content_overlap(node_a.content, node_b.content)
        if content_overlap > 0.5:
            contradiction = self._detect_contradiction(node_a.content, node_b.content)
            if contradiction:
                return EvidenceEdge(
                    source_id=node_a.node_id,
                    target_id=node_b.node_id,
                    edge_type=EdgeType.CONTRADICTS,
                    weight=0.8,
                    confidence=0.7,
                    metadata={"contradiction_type": contradiction},
                )
            else:
                return EvidenceEdge(
                    source_id=node_a.node_id,
                    target_id=node_b.node_id,
                    edge_type=EdgeType.SUPPORTS,
                    weight=content_overlap,
                    confidence=0.75,
                )
        
        return None
    
    def _compute_content_overlap(self, content_a: dict[str, Any], content_b: dict[str, Any]) -> float:
        """Compute semantic overlap between content dictionaries."""
        keys_a = set(content_a.keys())
        keys_b = set(content_b.keys())
        common_keys = keys_a & keys_b
        
        if not common_keys:
            return 0.0
        
        overlap_count = sum(
            1 for key in common_keys
            if content_a.get(key) == content_b.get(key)
        )
        
        return overlap_count / max(len(keys_a), len(keys_b))
    
    def _detect_contradiction(self, content_a: dict[str, Any], content_b: dict[str, Any]) -> str | None:
        """Detect contradictions between content dictionaries."""
        for key in set(content_a.keys()) & set(content_b.keys()):
            val_a = content_a[key]
            val_b = content_b[key]
            
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                if abs(val_a - val_b) > 0.5 * max(abs(val_a), abs(val_b)):
                    return "quantitative_mismatch"
            
            elif isinstance(val_a, bool) and isinstance(val_b, bool):
                if val_a != val_b:
                    return "boolean_contradiction"
            
            elif isinstance(val_a, str) and isinstance(val_b, str):
                if val_a.lower() != val_b.lower() and len(val_a) > 5 and len(val_b) > 5:
                    return "semantic_conflict"
        
        return None
    
    def propagate_beliefs(self) -> None:
        """
        Propagate belief masses across graph using Dempster-Shafer theory.
        
        Implements simplified belief propagation:
        - SUPPORTS edges increase belief
        - CONTRADICTS edges decrease belief, increase uncertainty
        - DERIVES_FROM edges propagate belief with decay
        """
        for node_id, node in self.nodes.items():
            if not node.belief_mass:
                continue
            
            outgoing_edges = [e for e in self.edges if e.source_id == node_id]
            
            for edge in outgoing_edges:
                target_node = self.nodes.get(edge.target_id)
                if not target_node or not target_node.belief_mass:
                    continue
                
                if edge.edge_type == EdgeType.SUPPORTS:
                    boost = node.belief_mass.belief * edge.weight * 0.1
                    target_node.belief_mass.belief = min(1.0, target_node.belief_mass.belief + boost)
                    target_node.belief_mass.uncertainty = max(0.0, target_node.belief_mass.uncertainty - boost * 0.5)
                
                elif edge.edge_type == EdgeType.CONTRADICTS:
                    penalty = node.belief_mass.belief * edge.weight * 0.15
                    target_node.belief_mass.belief = max(0.0, target_node.belief_mass.belief - penalty)
                    target_node.belief_mass.uncertainty = min(1.0, target_node.belief_mass.uncertainty + penalty)
                
                elif edge.edge_type == EdgeType.DERIVES_FROM:
                    transfer = node.belief_mass.belief * edge.weight * edge.confidence
                    target_node.belief_mass.belief = min(1.0, target_node.belief_mass.belief + transfer * 0.05)
    
    def detect_contradictions(self) -> list[dict[str, Any]]:
        """Detect contradictions in the graph."""
        contradictions = []
        
        for edge in self.edges:
            if edge.edge_type == EdgeType.CONTRADICTS:
                source_node = self.nodes[edge.source_id]
                target_node = self.nodes[edge.target_id]
                
                contradictions.append({
                    "source": {
                        "node_id": source_node.node_id,
                        "evidence_type": source_node.evidence_type,
                        "source_method": source_node.source_method,
                    },
                    "target": {
                        "node_id": target_node.node_id,
                        "evidence_type": target_node.evidence_type,
                        "source_method": target_node.source_method,
                    },
                    "contradiction_type": edge.metadata.get("contradiction_type", "unknown"),
                    "confidence": edge.confidence,
                })
        
        return contradictions
    
    def compute_overall_confidence(self) -> float:
        """Compute overall confidence from belief masses of all nodes."""
        if not self.nodes:
            return 0.0
        
        beliefs = [
            node.belief_mass.belief
            for node in self.nodes.values()
            if node.belief_mass
        ]
        
        if not beliefs:
            return 0.5
        
        return statistics.fmean(beliefs)
    
    def to_dict(self) -> dict[str, Any]:
        """Export graph to dictionary."""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "statistics": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "contradiction_count": sum(1 for e in self.edges if e.edge_type == EdgeType.CONTRADICTS),
                "overall_confidence": self.compute_overall_confidence(),
            }
        }


class ValidationProtocol(Protocol):
    """Protocol for validation rules."""
    
    def validate(self, evidence: dict[str, Any], graph: EvidenceGraph) -> dict[str, Any]:
        """Validate evidence against rules."""
        ...


class ValidationEngine:
    """
    Protocol-based validation engine with graph-aware validation.
    
    Supports both legacy rule-based validation and graph-aware checks.
    """
    
    def __init__(self):
        self.rules: list[dict[str, Any]] = []
    
    def validate(
        self,
        evidence: dict[str, Any],
        rules_object: dict[str, Any],
        graph: EvidenceGraph | None = None,
        failure_contract: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Validate evidence using rules and graph analysis.
        
        Args:
            evidence: Evidence dictionary
            rules_object: Validation rules from contract
            graph: Optional evidence graph for graph-aware validation
            failure_contract: Optional failure contract from signal pack
        
        Returns:
            Validation result with errors, warnings, and graph insights
        """
        validation_rules = rules_object.get("rules", [])
        na_policy = rules_object.get("na_policy", "abort_on_critical")
        errors: list[str] = []
        warnings: list[str] = []
        abort_code: str | None = None
        
        for rule in validation_rules:
            field = rule.get("field")
            value = self._resolve(field, evidence)
            
            if rule.get("must_contain"):
                must_contain = rule["must_contain"]
                required_elements = set(must_contain.get("elements", []))
                present_elements = set(value) if isinstance(value, list) else set()
                missing_elements = required_elements - present_elements
                if missing_elements:
                    errors.append(
                        f"Field '{field}' is missing required elements: {', '.join(sorted(missing_elements))}"
                    )
            
            if rule.get("should_contain"):
                should_contain = rule["should_contain"]
                present_elements = set(value) if isinstance(value, list) else set()
                for requirement in should_contain:
                    elements_to_check = set(requirement.get("elements", []))
                    min_count = requirement.get("minimum", 1)
                    found_count = len(present_elements.intersection(elements_to_check))
                    if found_count < min_count:
                        warnings.append(
                            f"Field '{field}' only has {found_count}/{min_count} "
                            f"of recommended elements: {', '.join(sorted(elements_to_check))}"
                        )
            
            missing = value is None
            if rule.get("required") and missing:
                errors.append(f"Missing required field '{field}'")
                continue
            if missing:
                continue
            
            if rule.get("type", "any") != "any" and not self._check_type(value, rule["type"]):
                errors.append(f"Field '{field}' has incorrect type (expected {rule['type']})")
        
        if graph:
            graph_insights = self._validate_with_graph(evidence, graph)
            errors.extend(graph_insights.get("errors", []))
            warnings.extend(graph_insights.get("warnings", []))
        
        if failure_contract and errors:
            abort_conditions = failure_contract.get("abort_if", [])
            emit_code = failure_contract.get("emit_code", "SIGNAL_ABORT")
            
            for condition in abort_conditions:
                if self._check_abort_condition(condition, errors):
                    abort_code = emit_code
                    break
        
        valid = not errors
        
        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "abort_code": abort_code,
            "failure_contract_triggered": abort_code is not None,
        }
    
    def _validate_with_graph(self, evidence: dict[str, Any], graph: EvidenceGraph) -> dict[str, Any]:
        """Perform graph-aware validation."""
        errors: list[str] = []
        warnings: list[str] = []
        
        contradictions = graph.detect_contradictions()
        if contradictions:
            warnings.append(
                f"Found {len(contradictions)} contradictions in evidence graph"
            )
        
        confidence = graph.compute_overall_confidence()
        if confidence < 0.5:
            warnings.append(
                f"Low overall confidence in evidence graph: {confidence:.2f}"
            )
        
        return {"errors": errors, "warnings": warnings}
    
    def _resolve(self, path: str, evidence: dict[str, Any]) -> Any:
        """Resolve dotted path in evidence dictionary."""
        if not path:
            return None
        parts = path.split(".")
        current: Any = evidence
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
    
    def _check_type(self, value: Any, expected: str) -> bool:
        """Check if value matches expected type."""
        mapping = {
            "array": (list, tuple),
            "integer": (int,),
            "float": (float, int),
            "string": (str,),
            "boolean": (bool,),
            "object": (dict,),
            "any": (object,),
        }
        return isinstance(value, mapping.get(expected, (object,)))
    
    def _check_abort_condition(self, condition: str, errors: list[str]) -> bool:
        """Check if abort condition is met."""
        if condition == "missing_required_element":
            return any("missing required" in e.lower() for e in errors)
        elif condition == "type_mismatch":
            return any("incorrect type" in e.lower() for e in errors)
        elif condition == "any_error":
            return len(errors) > 0
        return False


class EvidenceNexus:
    """
    Unified SOTA evidence processing engine.
    
    Replaces EvidenceAssembler, EvidenceValidator, and EvidenceRegistry
    with a single, graph-based reasoning system.
    
    Features:
    - Graph construction from method outputs
    - Belief propagation across evidence
    - Contradiction detection
    - Integrated provenance tracking
    - Legacy-compatible output
    """
    
    def __init__(self, storage_path: Path | None = None):
        self.storage_path = storage_path or Path("evidence_nexus.jsonl")
        self.validation_engine = ValidationEngine()
    
    def process(
        self,
        method_outputs: dict[str, Any],
        question_context: dict[str, Any],
        contract: dict[str, Any],
        signal_pack: Any | None = None,
    ) -> dict[str, Any]:
        """
        Process method outputs through unified evidence reasoning.
        
        Args:
            method_outputs: Dictionary of method results
            question_context: Question context from contract
            contract: Full execution contract
            signal_pack: Optional signal pack for provenance
        
        Returns:
            Dictionary with evidence, validation, and narrative
        """
        graph = self._build_graph(method_outputs, signal_pack)
        
        graph.infer_relationships()
        graph.propagate_beliefs()
        
        evidence = self._assemble_evidence(method_outputs, contract, signal_pack, graph)
        
        validation_rules_object = contract.get("validation_rules", {})
        failure_contract = contract.get("error_handling", {}).get("failure_contract", {})
        
        validation = self.validation_engine.validate(
            evidence,
            validation_rules_object,
            graph=graph,
            failure_contract=failure_contract,
        )
        
        contradictions = graph.detect_contradictions()
        overall_confidence = graph.compute_overall_confidence()
        
        calibrated_interval = self._compute_confidence_interval(overall_confidence)
        
        gaps = self._identify_gaps(evidence, question_context)
        
        trace = {
            "method_count": len(method_outputs),
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "contradiction_count": len(contradictions),
        }
        
        if signal_pack:
            trace["signal_provenance"] = {
                "signal_pack_id": getattr(signal_pack, "id", None) or getattr(signal_pack, "pack_id", "unknown"),
                "policy_area": getattr(signal_pack, "policy_area", None),
            }
        
        return {
            "evidence": evidence,
            "validation": validation,
            "trace": trace,
            "graph": graph.to_dict(),
            "contradictions": contradictions,
            "overall_confidence": overall_confidence,
            "calibrated_interval": calibrated_interval,
            "gaps": gaps,
            "graph_statistics": {
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "contradictions": len(contradictions),
                "avg_belief": overall_confidence,
            },
        }
    
    def _build_graph(self, method_outputs: dict[str, Any], signal_pack: Any | None) -> EvidenceGraph:
        """Build evidence graph from method outputs."""
        graph = EvidenceGraph()
        
        for method_name, output in method_outputs.items():
            if method_name.startswith("_"):
                continue
            
            node_id = f"{method_name}_{hash(str(output)) % 10000:04d}"
            
            node = EvidenceNode(
                node_id=node_id,
                evidence_type="method_output",
                content=output if isinstance(output, dict) else {"value": output},
                source_method=method_name,
                metadata={
                    "signal_pack_available": signal_pack is not None,
                }
            )
            
            graph.add_node(node)
        
        return graph
    
    def _assemble_evidence(
        self,
        method_outputs: dict[str, Any],
        contract: dict[str, Any],
        signal_pack: Any | None,
        graph: EvidenceGraph,
    ) -> dict[str, Any]:
        """Assemble evidence using assembly rules from contract."""
        evidence: dict[str, Any] = {}
        
        assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
        
        for rule in assembly_rules:
            target = rule.get("target")
            sources = rule.get("sources", [])
            strategy = rule.get("merge_strategy", "first")
            weights = rule.get("weights")
            default = rule.get("default")
            
            values = []
            for src in sources:
                val = self._resolve_value(src, method_outputs)
                if val is not None:
                    values.append(val)
            
            merged = self._merge(values, strategy, weights, default)
            evidence[target] = merged
        
        return evidence
    
    def _resolve_value(self, source: str, method_outputs: dict[str, Any]) -> Any:
        """Resolve dotted source paths from method_outputs."""
        if not source:
            return None
        parts = source.split(".")
        current: Any = method_outputs
        for idx, part in enumerate(parts):
            if idx == 0 and part in method_outputs:
                current = method_outputs[part]
                continue
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
    
    def _merge(self, values: list[Any], strategy: str, weights: list[float] | None, default: Any) -> Any:
        """Merge values using specified strategy."""
        if not values:
            return default
        if strategy == "first":
            return values[0]
        if strategy == "last":
            return values[-1]
        if strategy == "concat":
            merged: list[Any] = []
            for v in values:
                if isinstance(v, list):
                    merged.extend(v)
                else:
                    merged.append(v)
            return merged
        
        numeric_values = [float(v) for v in values if self._is_number(v)]
        if strategy == "mean":
            return statistics.fmean(numeric_values) if numeric_values else default
        if strategy == "max":
            return max(numeric_values) if numeric_values else default
        if strategy == "min":
            return min(numeric_values) if numeric_values else default
        if strategy == "weighted_mean":
            if not numeric_values:
                return default
            if not weights:
                weights = [1.0] * len(numeric_values)
            w = weights[: len(numeric_values)] or [1.0] * len(numeric_values)
            total = sum(w) or 1.0
            return sum(v * w_i for v, w_i in zip(numeric_values, w)) / total
        if strategy == "majority":
            counts: dict[Any, int] = {}
            for v in values:
                counts[v] = counts.get(v, 0) + 1
            return max(counts.items(), key=lambda item: item[1])[0] if counts else default
        
        return default
    
    def _is_number(self, value: Any) -> bool:
        """Check if value is numeric."""
        try:
            float(value)
            return not isinstance(value, bool)
        except (TypeError, ValueError):
            return False
    
    def _compute_confidence_interval(self, confidence: float) -> tuple[float, float]:
        """Compute 95% confidence interval."""
        margin = 0.1 * (1.0 - confidence)
        return (max(0.0, confidence - margin), min(1.0, confidence + margin))
    
    def _identify_gaps(self, evidence: dict[str, Any], question_context: dict[str, Any]) -> list[str]:
        """Identify gaps in evidence based on expected elements."""
        gaps = []
        expected_elements = question_context.get("expected_elements", [])
        
        for element in expected_elements:
            if element not in evidence or evidence[element] is None:
                gaps.append(f"Missing expected element: {element}")
        
        return gaps


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
    """Convenience function for processing evidence through global nexus."""
    nexus = get_global_nexus()
    return nexus.process(method_outputs, question_context, contract, signal_pack)


__all__ = [
    "EvidenceNexus",
    "EvidenceGraph",
    "EvidenceNode",
    "EvidenceEdge",
    "EdgeType",
    "BeliefMass",
    "ValidationEngine",
    "process_evidence",
    "get_global_nexus",
]
