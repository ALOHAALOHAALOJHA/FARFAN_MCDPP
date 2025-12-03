"""
Tests for chunk_router.py - Routing logic formalization and contracts.

Validates the ExecutionMap contract, serialization/deserialization,
and deterministic behavior of routing logic.
"""

import hashlib
import json

import pytest
from pydantic import ValidationError

pytestmark = pytest.mark.obsolete

from farfan_pipeline.core.orchestrator.chunk_router import (
    ChunkRouter,
    ExecutionMap,
    deserialize_execution_map,
    serialize_execution_map,
)
from farfan_pipeline.core.types import ChunkData


@pytest.fixture
def sample_chunks():
    """Create sample chunks with policy area and dimension assignments."""
    return [
        ChunkData(
            id=1,
            text="Diagnostic text about women's rights",
            chunk_type="diagnostic",
            sentences=[0, 1, 2],
            tables=[],
            start_pos=0,
            end_pos=100,
            confidence=0.95,
            policy_area_id="PA01",
            dimension_id="DIM01",
        ),
        ChunkData(
            id=2,
            text="Activity description for violence prevention",
            chunk_type="activity",
            sentences=[3, 4, 5],
            tables=[],
            start_pos=101,
            end_pos=200,
            confidence=0.92,
            policy_area_id="PA02",
            dimension_id="DIM02",
        ),
        ChunkData(
            id=3,
            text="Indicator for environmental metrics",
            chunk_type="indicator",
            sentences=[6, 7],
            tables=[],
            start_pos=201,
            end_pos=300,
            confidence=0.88,
            policy_area_id="PA03",
            dimension_id="DIM03",
        ),
    ]


@pytest.fixture
def router():
    """Create a ChunkRouter instance."""
    return ChunkRouter()


class TestExecutionMapContract:
    """Test suite for ExecutionMap contract validation."""

    def test_valid_execution_map(self):
        """Valid ExecutionMap should be created successfully."""
        routing_rules = {
            "PA01:DIM01": "D1Q1",
            "PA02:DIM02": "D2Q1",
        }
        canonical_repr = json.dumps(
            routing_rules, sort_keys=True, separators=(",", ":")
        )
        map_hash = hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()

        execution_map = ExecutionMap(
            version="1.0.0",
            map_hash=map_hash,
            routing_rules=routing_rules,
        )

        assert execution_map.version == "1.0.0"
        assert execution_map.map_hash == map_hash
        assert execution_map.routing_rules == routing_rules

    def test_invalid_version_format(self):
        """Version must match semantic versioning format."""
        with pytest.raises(ValidationError, match="version"):
            ExecutionMap(
                version="v1",  # Invalid format
                map_hash="a" * 64,
                routing_rules={"PA01:DIM01": "D1Q1"},
            )

    def test_invalid_hash_length(self):
        """map_hash must be exactly 64 characters."""
        with pytest.raises(ValidationError, match="map_hash"):
            ExecutionMap(
                version="1.0.0",
                map_hash="abc123",  # Too short
                routing_rules={"PA01:DIM01": "D1Q1"},
            )

    def test_invalid_hash_format(self):
        """map_hash must be valid hexadecimal."""
        with pytest.raises(ValidationError, match="hexadecimal"):
            ExecutionMap(
                version="1.0.0",
                map_hash="z" * 64,  # Invalid hex characters
                routing_rules={"PA01:DIM01": "D1Q1"},
            )

    def test_empty_routing_rules(self):
        """routing_rules cannot be empty."""
        with pytest.raises(ValidationError, match="routing_rules cannot be empty"):
            ExecutionMap(
                version="1.0.0",
                map_hash="a" * 64,
                routing_rules={},
            )

    def test_invalid_routing_key_format(self):
        """Routing keys must be in 'policy_area_id:dimension_id' format."""
        with pytest.raises(ValidationError, match="policy_area_id:dimension_id"):
            ExecutionMap(
                version="1.0.0",
                map_hash="a" * 64,
                routing_rules={"INVALID_KEY": "D1Q1"},
            )

    def test_invalid_routing_key_missing_parts(self):
        """Routing keys must have both policy_area_id and dimension_id."""
        with pytest.raises(ValidationError, match="non-empty"):
            ExecutionMap(
                version="1.0.0",
                map_hash="a" * 64,
                routing_rules={"PA01:": "D1Q1"},  # Missing dimension_id
            )

    def test_empty_executor_class(self):
        """Executor class must be non-empty string."""
        with pytest.raises(ValidationError, match="non-empty string"):
            ExecutionMap(
                version="1.0.0",
                map_hash="a" * 64,
                routing_rules={"PA01:DIM01": ""},
            )

    def test_get_executor(self):
        """get_executor should retrieve correct executor for given area/dimension."""
        execution_map = ExecutionMap(
            version="1.0.0",
            map_hash="a" * 64,
            routing_rules={
                "PA01:DIM01": "D1Q1",
                "PA02:DIM02": "D2Q1",
            },
        )

        assert execution_map.get_executor("PA01", "DIM01") == "D1Q1"
        assert execution_map.get_executor("PA02", "DIM02") == "D2Q1"
        assert execution_map.get_executor("PA99", "DIM99") is None


class TestGenerateExecutionMap:
    """Test suite for generate_execution_map functionality."""

    def test_generate_execution_map_basic(self, router, sample_chunks):
        """Generate execution map from valid chunks."""
        execution_map = router.generate_execution_map(sample_chunks)

        assert execution_map.version == "1.0.0"
        expected_rules_count = 3
        assert len(execution_map.routing_rules) == expected_rules_count
        assert "PA01:DIM01" in execution_map.routing_rules
        assert "PA02:DIM02" in execution_map.routing_rules
        assert "PA03:DIM03" in execution_map.routing_rules

        assert execution_map.routing_rules["PA01:DIM01"] == "D1Q1"
        assert execution_map.routing_rules["PA02:DIM02"] == "D2Q1"
        assert execution_map.routing_rules["PA03:DIM03"] == "D3Q1"

    def test_generate_execution_map_deterministic(self, router, sample_chunks):
        """Execution map generation must be deterministic."""
        map1 = router.generate_execution_map(sample_chunks)
        map2 = router.generate_execution_map(sample_chunks)

        assert map1.version == map2.version
        assert map1.map_hash == map2.map_hash
        assert map1.routing_rules == map2.routing_rules

    def test_generate_execution_map_order_independent(self, router, sample_chunks):
        """Execution map should be same regardless of chunk order."""
        import random

        chunks_copy = sample_chunks.copy()
        random.shuffle(chunks_copy)

        map1 = router.generate_execution_map(sample_chunks)
        map2 = router.generate_execution_map(chunks_copy)

        assert map1.map_hash == map2.map_hash
        assert map1.routing_rules == map2.routing_rules

    def test_generate_execution_map_missing_policy_area(self, router):
        """Should raise error if chunk missing policy_area_id."""
        chunks = [
            ChunkData(
                id=1,
                text="Test",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id=None,  # Missing
                dimension_id="DIM01",
            )
        ]

        with pytest.raises(ValueError, match="policy_area_id"):
            router.generate_execution_map(chunks)

    def test_generate_execution_map_missing_dimension(self, router):
        """Should raise error if chunk missing dimension_id."""
        chunks = [
            ChunkData(
                id=1,
                text="Test",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id=None,  # Missing
            )
        ]

        with pytest.raises(ValueError, match="dimension_id"):
            router.generate_execution_map(chunks)

    def test_generate_execution_map_unknown_chunk_type(self, router):
        """Unknown chunk types should be marked as UNROUTED."""
        chunks = [
            ChunkData(
                id=1,
                text="Test",
                chunk_type="unknown_type",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
            )
        ]

        execution_map = router.generate_execution_map(chunks)
        assert execution_map.routing_rules["PA01:DIM01"] == "UNROUTED_UNKNOWN_TYPE"

    def test_hash_verification(self, router, sample_chunks):
        """Generated hash should match computed hash of routing rules."""
        execution_map = router.generate_execution_map(sample_chunks)

        canonical_repr = json.dumps(
            dict(sorted(execution_map.routing_rules.items())),
            sort_keys=True,
            separators=(",", ":"),
        )
        expected_hash = hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()

        assert execution_map.map_hash == expected_hash

    def test_custom_version(self, router, sample_chunks):
        """Should accept custom version string."""
        execution_map = router.generate_execution_map(sample_chunks, version="2.1.5")
        assert execution_map.version == "2.1.5"


class TestSerialization:
    """Test suite for serialization and deserialization."""

    def test_serialize_execution_map(self, router, sample_chunks):
        """Serialize ExecutionMap to JSON string."""
        execution_map = router.generate_execution_map(sample_chunks)
        serialized = serialize_execution_map(execution_map)

        assert isinstance(serialized, str)
        data = json.loads(serialized)

        assert data["version"] == execution_map.version
        assert data["map_hash"] == execution_map.map_hash
        assert data["routing_rules"] == execution_map.routing_rules

    def test_deserialize_execution_map(self, router, sample_chunks):
        """Deserialize JSON string back to ExecutionMap."""
        execution_map = router.generate_execution_map(sample_chunks)
        serialized = serialize_execution_map(execution_map)
        deserialized = deserialize_execution_map(serialized)

        assert deserialized.version == execution_map.version
        assert deserialized.map_hash == execution_map.map_hash
        assert deserialized.routing_rules == execution_map.routing_rules

    def test_roundtrip_serialization(self, router, sample_chunks):
        """Roundtrip serialization should preserve data exactly."""
        original = router.generate_execution_map(sample_chunks)
        serialized = serialize_execution_map(original)
        deserialized = deserialize_execution_map(serialized)
        reserialized = serialize_execution_map(deserialized)

        assert serialized == reserialized
        assert original.version == deserialized.version
        assert original.map_hash == deserialized.map_hash
        assert original.routing_rules == deserialized.routing_rules

    def test_deserialize_invalid_json(self):
        """Should raise error for invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            deserialize_execution_map("not valid json")

    def test_deserialize_missing_fields(self):
        """Should raise validation error for missing required fields."""
        incomplete_json = json.dumps({"version": "1.0.0"})

        with pytest.raises(ValidationError):
            deserialize_execution_map(incomplete_json)

    def test_serialization_deterministic(self, router, sample_chunks):
        """Serialization must be deterministic."""
        execution_map = router.generate_execution_map(sample_chunks)

        serialized1 = serialize_execution_map(execution_map)
        serialized2 = serialize_execution_map(execution_map)

        assert serialized1 == serialized2


class TestChunkRouterCompatibility:
    """Test suite for backward compatibility with existing ChunkRouter methods."""

    def test_route_chunk_backward_compat(self, router, sample_chunks):
        """route_chunk should continue to work as before."""
        chunk = sample_chunks[0]
        route = router.route_chunk(chunk)

        assert route.chunk_id == chunk.id
        assert route.chunk_type == chunk.chunk_type
        assert route.executor_class == "D1Q1"
        assert route.skip_reason is None

    def test_should_use_full_graph(self, router):
        """should_use_full_graph should identify graph methods correctly."""
        assert router.should_use_full_graph("construir_grafo_causal", "TeoriaCambio")
        assert router.should_use_full_graph(
            "extract_causal_hierarchy", "CausalExtractor"
        )
        assert not router.should_use_full_graph("some_regular_method")

    def test_get_relevant_executors(self, router):
        """get_relevant_executors should return executor list for chunk type."""
        assert router.get_relevant_executors("diagnostic") == ["D1Q1", "D1Q2", "D1Q5"]
        assert router.get_relevant_executors("activity") == [
            "D2Q1",
            "D2Q2",
            "D2Q3",
            "D2Q4",
            "D2Q5",
        ]
        assert router.get_relevant_executors("unknown") == []


class TestDeterminism:
    """Property-based tests for determinism guarantees."""

    def test_same_input_same_output(self, router):
        """Multiple calls with identical input must produce identical output."""
        chunks = [
            ChunkData(
                id=i,
                text=f"Chunk {i}",
                chunk_type="diagnostic",
                sentences=[i],
                tables=[],
                start_pos=i * 100,
                end_pos=(i + 1) * 100,
                confidence=0.9,
                policy_area_id=f"PA{i:02d}",
                dimension_id=f"DIM{(i % 6) + 1:02d}",
            )
            for i in range(1, 11)
        ]

        results = [router.generate_execution_map(chunks) for _ in range(10)]

        first_hash = results[0].map_hash
        first_rules = results[0].routing_rules

        for result in results[1:]:
            assert result.map_hash == first_hash
            assert result.routing_rules == first_rules

    def test_hash_collision_resistance(self, router):
        """Different routing rules should produce different hashes."""
        chunks1 = [
            ChunkData(
                id=1,
                text="Test",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
            )
        ]

        chunks2 = [
            ChunkData(
                id=1,
                text="Test",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA02",
                dimension_id="DIM01",
            )
        ]

        map1 = router.generate_execution_map(chunks1)
        map2 = router.generate_execution_map(chunks2)

        assert map1.map_hash != map2.map_hash
        assert map1.routing_rules != map2.routing_rules
