"""
Tests for Phase 1 → Phase 2 Interface Adapter
==============================================

Property-based, edge case, and contraejemplo tests for the
Phase1ToPhase2Adapter as specified in the formal audit.

Version: 1.0.0
Date: 2026-01-13
"""
from __future__ import annotations

import pytest
from dataclasses import dataclass
from typing import Any

from farfan_pipeline.phases.Phase_2.interphase.phase1_phase2_adapter import (
    Phase2InputBundle,
    adapt_phase1_to_phase2,
    validate_adaptation,
    extract_chunks,
    extract_schema_version,
    DEFAULT_SCHEMA_VERSION,
)


# =============================================================================
# TEST FIXTURES (Mock Phase 1 Output Structures)
# =============================================================================

@dataclass
class MockMetadata:
    """Mock CPP metadata."""
    schema_version: str = "CPP-2025.1"


@dataclass
class MockChunkGraph:
    """Mock chunk graph."""
    chunks: list[Any] = None
    
    def __post_init__(self):
        if self.chunks is None:
            self.chunks = []


@dataclass
class MockPhase1Output:
    """Mock Phase 1 output with smart_chunks pattern."""
    smart_chunks: list[Any] = None
    enriched_signal_packs: dict[str, Any] = None
    irrigation_map: Any = None
    truncation_audit: Any = None
    structural_validation_result: Any = None
    questionnaire_mapper: Any = None
    metadata: MockMetadata = None
    
    def __post_init__(self):
        if self.smart_chunks is None:
            self.smart_chunks = []
        if self.enriched_signal_packs is None:
            self.enriched_signal_packs = {}
        if self.metadata is None:
            self.metadata = MockMetadata()


@dataclass
class MockCPPOutput:
    """Mock Phase 1 output with chunk_graph pattern (CanonPolicyPackage)."""
    chunk_graph: MockChunkGraph = None
    enriched_signal_packs: dict[str, Any] = None
    irrigation_map: Any = None
    truncation_audit: Any = None
    structural_validation_result: Any = None
    questionnaire_mapper: Any = None
    metadata: MockMetadata = None
    
    def __post_init__(self):
        if self.chunk_graph is None:
            self.chunk_graph = MockChunkGraph()
        if self.enriched_signal_packs is None:
            self.enriched_signal_packs = {}
        if self.metadata is None:
            self.metadata = MockMetadata()


def create_mock_chunks(n: int) -> list[dict]:
    """Create n mock chunks."""
    return [{"chunk_id": f"CHUNK-PA01-DIM01-Q{i}", "text": f"text_{i}"} for i in range(n)]


# =============================================================================
# PROPERTY-BASED TESTS
# =============================================================================

class TestChunkCountPreservation:
    """Tests that chunk count is preserved through adaptation."""
    
    @pytest.mark.parametrize("n_chunks", [0, 1, 10, 60, 100])
    def test_chunk_count_preserved_smart_chunks(self, n_chunks: int):
        """Adapter preserves chunk count (smart_chunks pattern)."""
        original = MockPhase1Output(smart_chunks=create_mock_chunks(n_chunks))
        adapted = adapt_phase1_to_phase2(original)
        assert len(adapted.chunks) == n_chunks
    
    @pytest.mark.parametrize("n_chunks", [0, 1, 10, 60, 100])
    def test_chunk_count_preserved_chunk_graph(self, n_chunks: int):
        """Adapter preserves chunk count (chunk_graph pattern)."""
        original = MockCPPOutput(chunk_graph=MockChunkGraph(chunks=create_mock_chunks(n_chunks)))
        adapted = adapt_phase1_to_phase2(original)
        assert len(adapted.chunks) == n_chunks


class TestSchemaVersionPreservation:
    """Tests that schema version is preserved through adaptation."""
    
    @pytest.mark.parametrize("version", ["CPP-2025.1", "CPP-2024.1", "v1.0.0", "custom"])
    def test_schema_version_preserved(self, version: str):
        """Adapter preserves schema version."""
        original = MockPhase1Output(metadata=MockMetadata(schema_version=version))
        adapted = adapt_phase1_to_phase2(original)
        assert adapted.schema_version == version


class TestDeterminism:
    """Tests that adaptation is deterministic."""
    
    def test_same_input_same_output(self):
        """Same input produces same output."""
        original = MockPhase1Output(
            smart_chunks=create_mock_chunks(60),
            enriched_signal_packs={"Q001": {"data": "test"}},
        )
        adapted1 = adapt_phase1_to_phase2(original)
        adapted2 = adapt_phase1_to_phase2(original)
        
        assert len(adapted1.chunks) == len(adapted2.chunks)
        assert adapted1.schema_version == adapted2.schema_version
        assert adapted1.enriched_signal_packs == adapted2.enriched_signal_packs


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_chunks(self):
        """Adapter handles 0 chunks."""
        original = MockPhase1Output(smart_chunks=[])
        adapted = adapt_phase1_to_phase2(original)
        assert len(adapted.chunks) == 0
    
    def test_max_expected_chunks(self):
        """Adapter handles maximum expected chunks (60)."""
        original = MockPhase1Output(smart_chunks=create_mock_chunks(60))
        adapted = adapt_phase1_to_phase2(original)
        assert len(adapted.chunks) == 60
    
    def test_none_questionnaire_mapper(self):
        """Adapter handles optional None questionnaire_mapper."""
        original = MockPhase1Output(questionnaire_mapper=None)
        adapted = adapt_phase1_to_phase2(original)
        assert adapted.questionnaire_mapper is None
    
    def test_missing_metadata_uses_default(self):
        """Adapter uses default schema version when metadata missing."""
        original = MockPhase1Output()
        original.metadata = None
        adapted = adapt_phase1_to_phase2(original)
        assert adapted.schema_version == DEFAULT_SCHEMA_VERSION
    
    def test_empty_enriched_signal_packs(self):
        """Adapter handles empty signal packs."""
        original = MockPhase1Output(enriched_signal_packs={})
        adapted = adapt_phase1_to_phase2(original)
        assert adapted.enriched_signal_packs == {}


# =============================================================================
# CONTRAEJEMPLO TESTS (INC-001, INC-002)
# =============================================================================

class TestINC001ChunksAccess:
    """Tests for INC-001: cpp.chunks vs cpp.chunk_graph.chunks."""
    
    def test_chunk_graph_access_works(self):
        """Adapter extracts chunks from chunk_graph.chunks pattern."""
        chunks = create_mock_chunks(60)
        original = MockCPPOutput(chunk_graph=MockChunkGraph(chunks=chunks))
        
        # Verify structure: chunks NOT at top level
        assert not hasattr(original, 'chunks') or original.chunks is None
        assert hasattr(original, 'chunk_graph')
        assert hasattr(original.chunk_graph, 'chunks')
        
        # Adapter should work
        adapted = adapt_phase1_to_phase2(original)
        assert len(adapted.chunks) == 60
    
    def test_smart_chunks_access_works(self):
        """Adapter extracts chunks from smart_chunks pattern."""
        chunks = create_mock_chunks(60)
        original = MockPhase1Output(smart_chunks=chunks)
        
        adapted = adapt_phase1_to_phase2(original)
        assert len(adapted.chunks) == 60


class TestINC002SchemaVersionAccess:
    """Tests for INC-002: cpp.schema_version vs cpp.metadata.schema_version."""
    
    def test_metadata_schema_version_access_works(self):
        """Adapter extracts schema_version from metadata.schema_version pattern."""
        original = MockPhase1Output(metadata=MockMetadata(schema_version="CPP-2025.1"))
        
        # Verify structure: schema_version NOT at top level
        assert not hasattr(original, 'schema_version') or getattr(original, 'schema_version', None) is None
        assert hasattr(original.metadata, 'schema_version')
        
        # Adapter should work
        adapted = adapt_phase1_to_phase2(original)
        assert adapted.schema_version == "CPP-2025.1"


# =============================================================================
# VALIDATION TESTS
# =============================================================================

class TestValidateAdaptation:
    """Tests for adaptation validation function."""
    
    def test_valid_adaptation(self):
        """Validation passes for correct adaptation."""
        original = MockPhase1Output(
            smart_chunks=create_mock_chunks(60),
            metadata=MockMetadata(schema_version="CPP-2025.1"),
        )
        adapted = adapt_phase1_to_phase2(original)
        
        is_valid, errors = validate_adaptation(original, adapted)
        assert is_valid
        assert len(errors) == 0
    
    def test_chunk_count_mismatch_detected(self):
        """Validation detects chunk count mismatch."""
        original = MockPhase1Output(smart_chunks=create_mock_chunks(60))
        
        # Create adapted with wrong chunk count
        adapted = Phase2InputBundle(
            chunks=create_mock_chunks(50),  # Wrong!
            schema_version="CPP-2025.1",
        )
        
        is_valid, errors = validate_adaptation(original, adapted)
        assert not is_valid
        assert any("Chunk count mismatch" in e for e in errors)


# =============================================================================
# EXTRACTION FUNCTION TESTS
# =============================================================================

class TestExtractChunks:
    """Tests for extract_chunks function."""
    
    def test_prefers_smart_chunks(self):
        """extract_chunks prefers smart_chunks over chunk_graph."""
        smart_chunks = create_mock_chunks(10)
        graph_chunks = create_mock_chunks(20)
        
        @dataclass
        class BothPatterns:
            smart_chunks: list = None
            chunk_graph: MockChunkGraph = None
        
        original = BothPatterns(
            smart_chunks=smart_chunks,
            chunk_graph=MockChunkGraph(chunks=graph_chunks),
        )
        
        result = extract_chunks(original)
        assert len(result) == 10  # smart_chunks preferred
    
    def test_raises_on_missing_chunks(self):
        """extract_chunks raises ValueError when no chunks found."""
        @dataclass
        class NoChunks:
            other_data: str = "test"
        
        with pytest.raises(ValueError, match="missing chunk data"):
            extract_chunks(NoChunks())


class TestExtractSchemaVersion:
    """Tests for extract_schema_version function."""
    
    def test_returns_default_when_missing(self):
        """extract_schema_version returns default when not found."""
        @dataclass
        class NoSchema:
            other_data: str = "test"
        
        result = extract_schema_version(NoSchema())
        assert result == DEFAULT_SCHEMA_VERSION


# =============================================================================
# INTEGRATION TEST
# =============================================================================

class TestFullAdaptationPipeline:
    """Integration test for complete adaptation pipeline."""
    
    def test_full_pipeline(self):
        """Complete adaptation pipeline works correctly."""
        # Create realistic Phase 1 output
        original = MockCPPOutput(
            chunk_graph=MockChunkGraph(chunks=create_mock_chunks(60)),
            enriched_signal_packs={f"Q{i:03d}": {"data": f"signal_{i}"} for i in range(1, 306)},
            irrigation_map={"coverage": 1.0},
            truncation_audit={"integrity_score": 0.98},
            structural_validation_result={"is_valid": True},
            questionnaire_mapper={"questions": 305},
            metadata=MockMetadata(schema_version="CPP-2025.1"),
        )
        
        # Adapt
        adapted = adapt_phase1_to_phase2(original)
        
        # Validate
        is_valid, errors = validate_adaptation(original, adapted)
        
        # Assertions
        assert is_valid, f"Validation errors: {errors}"
        assert len(adapted.chunks) == 60
        assert adapted.schema_version == "CPP-2025.1"
        assert len(adapted.enriched_signal_packs) == 305
        assert adapted.irrigation_map == {"coverage": 1.0}
        assert adapted.structural_validation == {"is_valid": True}
        assert adapted.adaptation_source == "Phase1Output"
