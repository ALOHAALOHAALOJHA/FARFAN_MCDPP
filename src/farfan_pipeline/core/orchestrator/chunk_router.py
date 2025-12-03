"""
Chunk Router for SPC Exploitation.

Routes semantic chunks to appropriate executors based on chunk type,
enabling targeted execution and reducing redundant processing.

This module provides strict, verifiable contracts for routing logic to ensure
deterministic behavior in the policy analysis pipeline.

Example Usage:
    >>> from farfan_pipeline.core.orchestrator.chunk_router import (
    ...     ChunkRouter, serialize_execution_map, deserialize_execution_map
    ... )
    >>> from farfan_pipeline.core.types import ChunkData
    >>>
    >>> # Create router and chunks
    >>> router = ChunkRouter()
    >>> chunks = [
    ...     ChunkData(
    ...         id=1, text="Policy text", chunk_type="diagnostic",
    ...         sentences=[], tables=[], start_pos=0, end_pos=100, confidence=0.9,
    ...         policy_area_id="PA01", dimension_id="DIM01"
    ...     )
    ... ]
    >>>
    >>> # Generate execution map
    >>> execution_map = router.generate_execution_map(chunks)
    >>> print(execution_map.version)  # "1.0.0"
    >>> print(execution_map.map_hash)  # SHA256 hash
    >>>
    >>> # Serialize/deserialize for storage or transmission
    >>> serialized = serialize_execution_map(execution_map)
    >>> restored = deserialize_execution_map(serialized)
    >>> assert restored.map_hash == execution_map.map_hash
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from ..types import ChunkData

# Routing table version identifier
ROUTING_TABLE_VERSION = "v1"


@dataclass
class ChunkRoute:
    """Routing decision for a single chunk."""

    chunk_id: int
    chunk_type: str
    executor_class: str
    methods: list[tuple[str, str]]  # [(class_name, method_name), ...]
    skip_reason: str | None = None


class ExecutionMap(BaseModel):
    """
    Strict contract for chunk-to-executor routing map.

    This contract ensures deterministic, verifiable routing decisions
    for the policy analysis pipeline. All fields are required and validated.
    """

    version: str = Field(
        ...,
        description="Version string for the map format (e.g., '1.0.0')",
        pattern=r"^\d+\.\d+\.\d+$",
    )

    map_hash: str = Field(
        ...,
        description="SHA256 hash of the canonical representation of routing map contents",
        min_length=64,
        max_length=64,
    )

    routing_rules: dict[str, str] = Field(
        ...,
        description="Maps (policy_area_id, dimension_id) tuples to executor class names",
    )

    @field_validator("map_hash")
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Validate that map_hash is a valid hex string."""
        try:
            int(v, 16)
        except ValueError as e:
            raise ValueError(f"map_hash must be a valid hexadecimal string: {e}") from e
        return v.lower()

    @field_validator("routing_rules")
    @classmethod
    def validate_routing_rules(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate routing rules structure and content."""
        if not v:
            raise ValueError("routing_rules cannot be empty")

        for key, executor_class in v.items():
            if not key or not isinstance(key, str):
                raise ValueError(f"Invalid routing key: {key!r}")

            if ":" not in key:
                raise ValueError(
                    f"Routing key must be in format 'policy_area_id:dimension_id', got: {key!r}"
                )

            parts = key.split(":")
            expected_parts = 2
            if len(parts) != expected_parts:
                raise ValueError(
                    f"Routing key must have exactly 2 parts separated by ':', got: {key!r}"
                )

            policy_area_id, dimension_id = parts
            if not policy_area_id or not dimension_id:
                raise ValueError(
                    f"Both policy_area_id and dimension_id must be non-empty in key: {key!r}"
                )

            if not executor_class or not isinstance(executor_class, str):
                raise ValueError(
                    f"Executor class must be a non-empty string for key {key!r}, got: {executor_class!r}"
                )

        return v

    def get_executor(self, policy_area_id: str, dimension_id: str) -> str | None:
        """
        Get executor class name for a given policy area and dimension.

        Args:
            policy_area_id: Policy area ID (e.g., 'PA01')
            dimension_id: Dimension ID (e.g., 'DIM01')

        Returns:
            Executor class name or None if no mapping exists
        """
        key = f"{policy_area_id}:{dimension_id}"
        return self.routing_rules.get(key)


class ChunkRouter:
    """
    Routes chunks to appropriate executors based on semantic type.

    This enables chunk-aware execution, where different chunk types
    are processed by the most relevant executors, avoiding unnecessary
    full-document processing.
    """

    # TYPE-TO-EXECUTOR MAPPING
    # Maps chunk types to executor base slots (e.g., "D1Q1", "D2Q3")
    ROUTING_TABLE: dict[str, list[str]] = {
        "diagnostic": ["D1Q1", "D1Q2", "D1Q5"],  # Baseline/gap analysis executors
        "activity": [
            "D2Q1",
            "D2Q2",
            "D2Q3",
            "D2Q4",
            "D2Q5",
        ],  # Activity/intervention executors
        "indicator": ["D3Q1", "D3Q2", "D4Q1", "D5Q1"],  # Metric/indicator executors
        "resource": ["D1Q3", "D2Q4", "D5Q5"],  # Financial/resource executors
        "temporal": ["D1Q5", "D3Q4", "D5Q4"],  # Timeline/temporal executors
        "entity": ["D2Q3", "D3Q3"],  # Responsibility/entity executors
    }

    # METHODS THAT MUST SEE FULL GRAPH
    # These methods require access to the complete chunk graph
    GRAPH_METHODS: set[str] = {
        "TeoriaCambio.construir_grafo_causal",
        "CausalExtractor.extract_causal_hierarchy",
        "AdvancedDAGValidator.calculate_acyclicity_pvalue",
        "CrossReferenceValidator.validate_internal_consistency",
    }

    def route_chunk(self, chunk: ChunkData) -> ChunkRoute:
        """
        Determine executor routing for a chunk.

        Args:
            chunk: ChunkData to route

        Returns:
            ChunkRoute with executor assignment and method list
        """
        executor_classes = self.ROUTING_TABLE.get(chunk.chunk_type, [])

        if not executor_classes:
            return ChunkRoute(
                chunk_id=chunk.id,
                chunk_type=chunk.chunk_type,
                executor_class="",
                methods=[],
                skip_reason=f"No executor mapping for chunk type '{chunk.chunk_type}'",
            )

        # Get primary executor for this chunk type
        primary_executor = executor_classes[0]

        # Get method subset for this chunk type
        # Note: Actual method filtering would require loading executor configs
        # For now, we return empty list and let execute_chunk filter
        methods: list[tuple[str, str]] = []

        return ChunkRoute(
            chunk_id=chunk.id,
            chunk_type=chunk.chunk_type,
            executor_class=primary_executor,
            methods=methods,
        )

    def should_use_full_graph(self, method_name: str, class_name: str = "") -> bool:
        """
        Check if a method requires access to the full chunk graph.

        Args:
            method_name: Name of the method
            class_name: Optional class name

        Returns:
            True if method needs full graph access
        """
        full_name = f"{class_name}.{method_name}" if class_name else method_name
        return full_name in self.GRAPH_METHODS or method_name in self.GRAPH_METHODS

    def get_relevant_executors(self, chunk_type: str) -> list[str]:
        """
        Get list of executors relevant to a chunk type.

        Args:
            chunk_type: Type of chunk

        Returns:
            List of executor base slots
        """
        return self.ROUTING_TABLE.get(chunk_type, [])

    def generate_execution_map(
        self,
        chunks: list[ChunkData],
        *,
        version: str = "1.0.0",
    ) -> ExecutionMap:
        """
        Generate a deterministic execution map for a list of chunks.

        This map serves as the binding contract for the Orchestrator,
        dictating exactly which executor processes which chunk based on
        policy_area_id and dimension_id combinations.

        Args:
            chunks: List of ChunkData objects
            version: Version string for the map format (default: "1.0.0")

        Returns:
            ExecutionMap with routing rules and verification hash

        Raises:
            ValueError: If chunks have missing policy_area_id or dimension_id
        """
        routing_rules: dict[str, str] = {}

        sorted_chunks = sorted(chunks, key=lambda c: c.id)

        for chunk in sorted_chunks:
            if not chunk.policy_area_id:
                raise ValueError(
                    f"Chunk {chunk.id} missing required policy_area_id field"
                )
            if not chunk.dimension_id:
                raise ValueError(
                    f"Chunk {chunk.id} missing required dimension_id field"
                )

            key = f"{chunk.policy_area_id}:{chunk.dimension_id}"

            executor_classes = self.ROUTING_TABLE.get(chunk.chunk_type, [])
            if executor_classes:
                primary_executor = executor_classes[0]
                routing_rules[key] = primary_executor
            else:
                routing_rules[key] = f"UNROUTED_{chunk.chunk_type.upper()}"

        canonical_repr = self._compute_canonical_representation(routing_rules)
        map_hash = self._compute_hash(canonical_repr)

        return ExecutionMap(
            version=version,
            map_hash=map_hash,
            routing_rules=routing_rules,
        )

    def _compute_canonical_representation(self, routing_rules: dict[str, str]) -> str:
        """
        Compute canonical JSON representation of routing rules.

        Args:
            routing_rules: Dictionary of routing rules

        Returns:
            Canonical JSON string with sorted keys
        """
        sorted_rules = dict(sorted(routing_rules.items()))
        return json.dumps(sorted_rules, sort_keys=True, separators=(",", ":"))

    def _compute_hash(self, canonical_repr: str) -> str:
        """
        Compute SHA256 hash of canonical representation.

        Args:
            canonical_repr: Canonical JSON string

        Returns:
            Hexadecimal hash string (lowercase)
        """
        return hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()


def serialize_execution_map(execution_map: ExecutionMap) -> str:
    """
    Serialize ExecutionMap to a canonical JSON string.

    The output is deterministic and suitable for storage, transmission,
    or comparison.

    Args:
        execution_map: ExecutionMap instance to serialize

    Returns:
        Canonical JSON string representation
    """
    data = {
        "version": execution_map.version,
        "map_hash": execution_map.map_hash,
        "routing_rules": dict(sorted(execution_map.routing_rules.items())),
    }
    return json.dumps(data, sort_keys=True, indent=2)


def deserialize_execution_map(serialized_map: str) -> ExecutionMap:
    """
    Deserialize JSON string back into a validated ExecutionMap object.

    Args:
        serialized_map: JSON string representation

    Returns:
        Validated ExecutionMap instance

    Raises:
        ValueError: If JSON is invalid or validation fails
        pydantic.ValidationError: If data doesn't match ExecutionMap schema
    """
    try:
        data = json.loads(serialized_map)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in serialized execution map: {e}") from e

    return ExecutionMap(**data)
