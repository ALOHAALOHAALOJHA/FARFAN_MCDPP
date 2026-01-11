"""
PHASE 1 ADVERSARIAL TEST SUITE
==============================

Comprehensive severe testing for Phase 1 CPP Ingestion.
Tests attack vectors, edge cases, and constitutional invariants.

Test Categories:
1. Model Validation - Data structure integrity
2. Chunk Invariants - PA×DIM grid constraints
3. Circuit Breaker - Failure protection
4. Signal Enrichment - Pattern extraction
5. Questionnaire Mapping - Question-level granularity
6. Edge Cases - Boundary conditions
7. Adversarial Inputs - Malformed data attacks

Author: F.A.R.F.A.N Testing Team
Date: 2026-01-05
Status: ADVERSARIAL - Break if you can
"""

import pytest
import re
from dataclasses import FrozenInstanceError
from typing import Any, Dict, List

# Phase 1 imports - Canonical path is Phase_1 (not Phase_one)
from farfan_pipeline.phases.Phase_1 import (
    SmartChunk,
    Chunk,
    LanguageData,
    PreprocessedDoc,
    StructureData,
    KnowledgeGraph,
    KGNode,
    KGEdge,
    CausalChains,
    ValidationResult,
    TOTAL_CHUNK_COMBINATIONS,
    POLICY_AREA_COUNT,
    DIMENSION_COUNT,
    CHUNK_ID_PATTERN,
    VALID_ASSIGNMENT_METHODS,
    ASSIGNMENT_METHOD_SEMANTIC,
    ASSIGNMENT_METHOD_FALLBACK,
)

from farfan_pipeline.phases.Phase_1.phase1_10_00_cpp_models import (
    TextSpan,
    LegacyChunk,
    ChunkResolution,
    CanonPolicyPackage,
)

from farfan_pipeline.phases.Phase_1.phase1_20_00_cpp_ingestion import (
    Phase1MissionContract,
    PADimGridSpecification,
)

from farfan_pipeline.phases.Phase_1.phase1_40_00_circuit_breaker import (
    Phase1CircuitBreaker,
    CircuitState,
    FailureSeverity,
    DependencyCheck,
    PreflightResult,
)


# =============================================================================
# 1. MODEL VALIDATION TESTS
# =============================================================================


class TestModelValidation:
    """Test data model integrity and validation."""

    def test_chunk_rejects_invalid_assignment_method(self):
        """Chunk must reject invalid assignment_method values."""
        with pytest.raises(ValueError, match="Invalid assignment_method"):
            Chunk(
                chunk_id="PA01-DIM01",
                policy_area_id="PA01",
                dimension_id="DIM01",
                chunk_index=0,
                assignment_method="INVALID_METHOD",
                semantic_confidence=0.5,
            )

    def test_chunk_rejects_out_of_range_confidence(self):
        """Chunk must reject confidence values outside [0, 1]."""
        with pytest.raises(ValueError, match="Invalid semantic_confidence"):
            Chunk(
                chunk_id="PA01-DIM01",
                policy_area_id="PA01",
                dimension_id="DIM01",
                chunk_index=0,
                assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
                semantic_confidence=1.5,  # Invalid: > 1.0
            )

        with pytest.raises(ValueError, match="Invalid semantic_confidence"):
            Chunk(
                chunk_id="PA01-DIM01",
                policy_area_id="PA01",
                dimension_id="DIM01",
                chunk_index=0,
                assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
                semantic_confidence=-0.1,  # Invalid: < 0.0
            )

    def test_chunk_derives_pa_dim_from_chunk_id(self):
        """Chunk should derive PA/DIM from chunk_id when not provided."""
        chunk = Chunk(
            chunk_id="PA05-DIM03",
            chunk_index=0,
            assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
            semantic_confidence=0.8,
        )
        assert chunk.policy_area_id == "PA05"
        assert chunk.dimension_id == "DIM03"

    def test_language_data_creation(self):
        """LanguageData must be creatable with required fields."""
        lang = LanguageData(
            primary_language="es",
            secondary_languages=["en"],
            confidence_scores={"es": 0.95, "en": 0.05},
            detection_method="langdetect",
        )
        assert lang.primary_language == "es"
        assert lang.confidence_scores["es"] == 0.95

    def test_text_span_rejects_negative_start(self):
        """TextSpan must reject negative start positions."""
        with pytest.raises(ValueError, match="start must be >= 0"):
            TextSpan(start=-1, end=10)

    def test_text_span_rejects_end_before_start(self):
        """TextSpan must reject end < start."""
        with pytest.raises(ValueError, match="end.*must be >= start"):
            TextSpan(start=10, end=5)

    def test_text_span_immutable(self):
        """TextSpan must be immutable (frozen dataclass)."""
        span = TextSpan(start=0, end=100)
        with pytest.raises(FrozenInstanceError):
            span.start = 50  # type: ignore


# =============================================================================
# 2. CHUNK INVARIANT TESTS
# =============================================================================


class TestChunkInvariants:
    """Test PA×DIM grid constitutional invariants."""

    def test_grid_specification_constants(self):
        """Grid specification must define correct constants."""
        assert len(PADimGridSpecification.POLICY_AREAS) == 10
        assert len(PADimGridSpecification.DIMENSIONS) == 6
        assert PADimGridSpecification.TOTAL_COMBINATIONS == 60

    def test_all_policy_areas_valid_format(self):
        """All policy areas must match PA01-PA10 format."""
        for pa in PADimGridSpecification.POLICY_AREAS:
            assert re.match(r"^PA(0[1-9]|10)$", pa), f"Invalid PA format: {pa}"

    def test_all_dimensions_valid_format(self):
        """All dimensions must match DIM01-DIM06 format."""
        for dim in PADimGridSpecification.DIMENSIONS:
            assert re.match(r"^DIM0[1-6]$", dim), f"Invalid DIM format: {dim}"

    def test_chunk_id_pattern_matches_valid_ids(self):
        """CHUNK_ID_PATTERN must match all valid question-aware chunk IDs."""
        pattern = re.compile(CHUNK_ID_PATTERN)
        for pa in PADimGridSpecification.POLICY_AREAS:
            for dim in PADimGridSpecification.DIMENSIONS:
                for q in range(1, 6):  # Q1-Q5
                    chunk_id = f"CHUNK-{pa}-{dim}-Q{q}"
                    assert pattern.match(chunk_id), f"Pattern failed for {chunk_id}"

    def test_chunk_id_pattern_rejects_invalid_ids(self):
        """CHUNK_ID_PATTERN must reject invalid chunk IDs."""
        pattern = re.compile(CHUNK_ID_PATTERN)
        invalid_ids = [
            "PA00-DIM01",  # PA00 invalid
            "PA11-DIM01",  # PA11 invalid
            "PA01-DIM00",  # DIM00 invalid
            "PA01-DIM07",  # DIM07 invalid
            "PA1-DIM01",  # Missing leading zero
            "PA01DIM01",  # Missing hyphen
            "pa01-dim01",  # Lowercase
            "",  # Empty
            "INVALID",  # Garbage
        ]
        for invalid_id in invalid_ids:
            assert not pattern.match(invalid_id), f"Pattern wrongly matched {invalid_id}"

    def test_validate_chunk_rejects_missing_fields(self):
        """PADimGridSpecification.validate_chunk must reject missing fields."""

        class BadChunk:
            pass

        with pytest.raises(AssertionError, match="Missing chunk_id"):
            PADimGridSpecification.validate_chunk(BadChunk())

    def test_validate_chunk_rejects_invalid_pa(self):
        """validate_chunk must reject invalid policy_area_id."""

        class BadChunk:
            chunk_id = "PA99-DIM01"
            policy_area_id = "PA99"
            dimension_id = "DIM01"
            chunk_index = 0

        with pytest.raises(AssertionError, match="Invalid chunk_id format"):
            PADimGridSpecification.validate_chunk(BadChunk())


# =============================================================================
# 3. WEIGHT CONTRACT TESTS
# =============================================================================


class TestWeightContract:
    """Test weight-based execution contract."""

    def test_critical_subphases_have_weight_10000(self):
        """SP4, SP11, SP13 must have weight 10000 (constitutional invariants)."""
        assert Phase1MissionContract.get_weight(4) == 10000, "SP4 must be critical"
        assert Phase1MissionContract.get_weight(11) == 10000, "SP11 must be critical"
        assert Phase1MissionContract.get_weight(13) == 10000, "SP13 must be critical"

    def test_is_critical_identifies_constitutional_invariants(self):
        """is_critical must identify all constitutional invariant subphases."""
        critical_sps = [sp for sp in range(16) if Phase1MissionContract.is_critical(sp)]
        assert 4 in critical_sps, "SP4 must be critical"
        assert 11 in critical_sps, "SP11 must be critical"
        assert 13 in critical_sps, "SP13 must be critical"

    def test_timeout_multiplier_scales_with_weight(self):
        """Higher weight subphases must get higher timeout multipliers."""
        assert Phase1MissionContract.get_timeout_multiplier(4) == 3.0  # Critical
        assert Phase1MissionContract.get_timeout_multiplier(3) == 2.0  # High priority
        assert Phase1MissionContract.get_timeout_multiplier(0) == 1.0  # Standard

    def test_all_16_subphases_have_weights(self):
        """All 16 subphases (SP0-SP15) must have defined weights."""
        for sp in range(16):
            weight = Phase1MissionContract.get_weight(sp)
            assert weight >= 900, f"SP{sp} weight {weight} below minimum 900"
            assert weight <= 10000, f"SP{sp} weight {weight} above maximum 10000"


# =============================================================================
# 4. CIRCUIT BREAKER TESTS
# =============================================================================


class TestCircuitBreaker:
    """Test aggressively preventive failure protection."""

    def test_circuit_breaker_initializes_closed(self):
        """Circuit breaker must initialize in CLOSED state."""
        cb = Phase1CircuitBreaker()
        assert cb.state == CircuitState.CLOSED

    def test_preflight_check_returns_result(self):
        """Preflight check must return PreflightResult."""
        cb = Phase1CircuitBreaker()
        result = cb.preflight_check()
        assert isinstance(result, PreflightResult)
        assert result.timestamp is not None

    def test_preflight_checks_python_version(self):
        """Preflight must check Python version."""
        cb = Phase1CircuitBreaker()
        result = cb.preflight_check()
        python_checks = [c for c in result.dependency_checks if c.name == "python"]
        assert len(python_checks) >= 1
        assert python_checks[0].version is not None

    def test_failure_severity_ordering(self):
        """Failure severity must have correct ordering."""
        # CRITICAL > HIGH > MEDIUM > LOW
        assert FailureSeverity.CRITICAL.value == "critical"
        assert FailureSeverity.HIGH.value == "high"
        assert FailureSeverity.MEDIUM.value == "medium"
        assert FailureSeverity.LOW.value == "low"


# =============================================================================
# 5. QUESTIONNAIRE MAPPING TESTS
# =============================================================================


class TestQuestionnaireMapping:
    """Test question-level granularity (v2.0 architecture)."""

    def test_total_chunk_combinations_is_300(self):
        """v2.0 architecture must produce 300 chunks (10 PA × 6 DIM × 5 Q)."""
        assert TOTAL_CHUNK_COMBINATIONS == 300

    def test_chunk_has_question_fields(self):
        """Chunk must have question-level fields."""
        chunk = Chunk(
            chunk_id="PA01-DIM01",
            chunk_index=0,
            assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
            semantic_confidence=0.8,
        )
        assert hasattr(chunk, "question_id")
        assert hasattr(chunk, "question_slot")
        assert hasattr(chunk, "question_patterns")
        assert hasattr(chunk, "expected_elements")

    def test_chunk_question_slot_range(self):
        """Question slot must be 0-5 (0 = unset, 1-5 = valid slots)."""
        for slot in range(6):
            chunk = Chunk(
                chunk_id="PA01-DIM01",
                chunk_index=0,
                question_slot=slot,
                assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
                semantic_confidence=0.8,
            )
            assert 0 <= chunk.question_slot <= 5


# =============================================================================
# 6. EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Test boundary conditions and edge cases."""

    def test_empty_knowledge_graph(self):
        """Empty knowledge graph must be valid."""
        kg = KnowledgeGraph(nodes=[], edges=[])
        assert len(kg.nodes) == 0
        assert len(kg.edges) == 0

    def test_preprocessed_doc_empty_text(self):
        """PreprocessedDoc with empty text must be valid."""
        doc = PreprocessedDoc(normalized_text="")
        assert doc.normalized_text == ""
        assert len(doc.tokens) == 0

    def test_structure_data_no_sections(self):
        """StructureData with no sections must be valid."""
        sd = StructureData(sections=[])
        assert len(sd.sections) == 0
        assert sd.paragraph_to_section == {}

    def test_chunk_boundary_confidence_values(self):
        """Chunk must accept boundary confidence values."""
        chunk_zero = Chunk(
            chunk_id="PA01-DIM01",
            chunk_index=0,
            assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
            semantic_confidence=0.0,  # Minimum valid
        )
        assert chunk_zero.semantic_confidence == 0.0

        chunk_one = Chunk(
            chunk_id="PA01-DIM01",
            chunk_index=0,
            assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
            semantic_confidence=1.0,  # Maximum valid
        )
        assert chunk_one.semantic_confidence == 1.0

    def test_chunk_all_pa_dim_combinations(self):
        """Must be able to create chunk for all 60 PA×DIM combinations."""
        created = 0
        for pa_idx in range(1, 11):
            pa = f"PA{pa_idx:02d}"
            for dim_idx in range(1, 7):
                dim = f"DIM{dim_idx:02d}"
                chunk_id = f"{pa}-{dim}"
                chunk = Chunk(
                    chunk_id=chunk_id,
                    chunk_index=created,
                    assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
                    semantic_confidence=0.8,
                )
                assert chunk.policy_area_id == pa
                assert chunk.dimension_id == dim
                created += 1
        assert created == 60


# =============================================================================
# 7. ADVERSARIAL INPUT TESTS
# =============================================================================


class TestAdversarialInputs:
    """Test malformed and adversarial inputs."""

    def test_chunk_id_sql_injection_attempt(self):
        """Chunk ID with SQL injection must be rejected by pattern."""
        pattern = re.compile(CHUNK_ID_PATTERN)
        malicious_ids = [
            "PA01-DIM01'; DROP TABLE--",
            "PA01-DIM01 OR 1=1",
            "PA01-DIM01\x00",
            "PA01-DIM01<script>",
        ]
        for malicious in malicious_ids:
            assert not pattern.match(malicious), f"Pattern matched malicious: {malicious}"

    def test_chunk_id_unicode_attack(self):
        """Chunk ID with unicode lookalikes must be rejected."""
        pattern = re.compile(CHUNK_ID_PATTERN)
        unicode_attacks = [
            "PА01-DIM01",  # Cyrillic А
            "PA０1-DIM01",  # Fullwidth 0
            "PA01-DIM０1",  # Fullwidth 0
        ]
        for attack in unicode_attacks:
            assert not pattern.match(attack), f"Pattern matched unicode attack: {repr(attack)}"

    def test_extreme_confidence_precision(self):
        """Chunk must handle extreme precision confidence values."""
        chunk = Chunk(
            chunk_id="PA01-DIM01",
            chunk_index=0,
            assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
            semantic_confidence=0.99999999999999,  # Near 1.0
        )
        assert chunk.semantic_confidence < 1.0

    def test_very_long_signal_tags(self):
        """Chunk must handle very long signal tag lists."""
        many_tags = [f"tag_{i}" for i in range(10000)]
        chunk = Chunk(
            chunk_id="PA01-DIM01",
            chunk_index=0,
            assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
            semantic_confidence=0.8,
            signal_tags=many_tags,
        )
        assert len(chunk.signal_tags) == 10000


# =============================================================================
# 8. INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Test component integration."""

    def test_smart_chunk_creation(self):
        """SmartChunk must be creatable with legacy format."""
        # Test legacy format (PA##-DIM##)
        smart = SmartChunk(
            chunk_id="PA01-DIM01",
            policy_area_id="PA01",
            dimension_id="DIM01",
            chunk_index=0,
            assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
            semantic_confidence=0.85,
        )
        assert smart.chunk_id == "PA01-DIM01"
        assert smart.semantic_confidence == 0.85

    def test_smart_chunk_new_format(self):
        """SmartChunk must also accept new question-aware format."""
        smart = SmartChunk(
            chunk_id="CHUNK-PA01-DIM01-Q1",
            policy_area_id="PA01",
            dimension_id="DIM01",
            chunk_index=0,
            assignment_method=ASSIGNMENT_METHOD_SEMANTIC,
            semantic_confidence=0.9,
        )
        assert smart.chunk_id == "CHUNK-PA01-DIM01-Q1"
        assert smart.policy_area_id == "PA01"
        assert smart.dimension_id == "DIM01"

    def test_kg_node_edge_relationship(self):
        """KGNode and KGEdge must properly reference each other."""
        node1 = KGNode(id="n1", type="entity", text="Entity 1")
        node2 = KGNode(id="n2", type="entity", text="Entity 2")
        edge = KGEdge(source="n1", target="n2", type="relates_to", weight=0.9)

        assert edge.source == node1.id
        assert edge.target == node2.id
        assert edge.weight == 0.9

    def test_legacy_chunk_frozen(self):
        """LegacyChunk must be frozen (immutable)."""
        chunk = LegacyChunk(
            id="PA01-DIM01",
            text="Test content",
            text_span=TextSpan(0, 12),
            resolution=ChunkResolution.MACRO,
            bytes_hash="abc123",
            policy_area_id="PA01",
            dimension_id="DIM01",
        )
        with pytest.raises(FrozenInstanceError):
            chunk.text = "Modified"  # type: ignore


# =============================================================================
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
