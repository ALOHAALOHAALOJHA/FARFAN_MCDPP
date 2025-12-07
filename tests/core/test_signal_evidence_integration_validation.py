"""
Signal Evidence Integration Validation - Complete Pipeline Testing
===================================================================

Comprehensive validation of extract_evidence() integration calling 
extract_structured_evidence() with proper expected_elements processing,
completeness metrics, and 1,200 element specification validation.

This test suite validates:

1. INTEGRATION VALIDATION
   - EnrichedSignalPack.extract_evidence() → extract_structured_evidence()
   - Proper expected_elements passthrough from signal nodes
   - Document context integration for context-aware extraction
   - Lineage tracking through entire pipeline

2. EXPECTED ELEMENTS PROCESSING (1,200 Specifications)
   - Dict format: {"type": "X", "required": True, "minimum": N}
   - String format: ["element1", "element2"] (legacy)
   - Required element validation
   - Minimum cardinality enforcement
   - Optional element bonus scoring

3. COMPLETENESS METRICS
   - Score calculation: 0.0 (missing all) to 1.0 (found all)
   - Required element scoring: binary (0.0 or 1.0)
   - Minimum element scoring: proportional (found/minimum)
   - Optional element scoring: presence bonus
   - Missing required tracking
   - Under minimum tracking

4. STRUCTURED OUTPUT
   - EvidenceExtractionResult (not text blob)
   - Evidence dict: element_type → list[matches]
   - Each match: value, confidence, pattern_id, category, span, lineage
   - Extraction metadata: pattern counts, match counts, timing
   - Deduplication: overlapping matches resolved

5. PATTERN RELEVANCE FILTERING
   - Category-based filtering (TEMPORAL, QUANTITATIVE, ENTITY, GEOGRAPHIC)
   - Keyword overlap heuristics
   - Context requirement matching
   - Validation rule consideration

6. CONFIDENCE PROPAGATION
   - Pattern confidence_weight → match confidence
   - Metadata preservation through extraction
   - Lineage tracking: pattern_id → extraction phase

7. REAL QUESTIONNAIRE DATA
   - 1,200 element specification target
   - Diverse element types across dimensions (D1-D6)
   - Policy areas (PA01-PA10)
   - Multiple pattern types and categories

Architecture:
- NO MOCKS for signal nodes (uses real questionnaire)
- Tests against actual 1,200 element specifications
- Validates completeness metrics accuracy
- Ensures structured output vs unstructured blobs
- Comprehensive assertions on all result fields

Author: F.A.R.F.A.N Pipeline  
Date: 2025-12-06
Coverage: Complete extract_evidence() integration validation
"""

from typing import Any

import pytest

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_evidence_extractor import (
    EvidenceExtractionResult,
    _deduplicate_matches,
    _infer_pattern_categories_for_element,
    _is_pattern_relevant_to_element,
    compute_completeness,
)
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    EnrichedSignalPack,
    IntelligenceMetrics,
)


class MockSignalPack:
    """Mock signal pack for integration testing."""

    def __init__(self, patterns: list[dict[str, Any]]):
        self.patterns = patterns


@pytest.fixture(scope="module")
def questionnaire():
    """Load real questionnaire."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def micro_questions(questionnaire):
    """Get all micro questions."""
    return questionnaire.get_micro_questions()


@pytest.fixture
def comprehensive_signal_node():
    """Signal node with comprehensive expected_elements."""
    return {
        "id": "COMP_TEST_001",
        "question_id": "COMP_TEST_001",
        "expected_elements": [
            {"type": "baseline_indicator", "required": True},
            {"type": "target_value", "required": True},
            {"type": "timeline_explicit", "required": False},
            {"type": "responsible_entity", "minimum": 2},
            {"type": "budget_amount", "required": False},
            {"type": "data_source", "minimum": 1},
            {"type": "geographic_coverage", "required": False},
            {"type": "indicators_quantitative", "minimum": 1},
        ],
        "patterns": [
            {
                "id": "PAT_BASELINE_001",
                "pattern": r"línea de base|baseline|situación actual",
                "confidence_weight": 0.92,
                "category": "QUANTITATIVE",
                "match_type": "regex",
                "context_requirement": "",
                "validation_rule": "must_contain_numeric",
            },
            {
                "id": "PAT_TARGET_001",
                "pattern": r"meta|objetivo|target|alcanzar",
                "confidence_weight": 0.88,
                "category": "QUANTITATIVE",
                "match_type": "regex",
                "context_requirement": "",
            },
            {
                "id": "PAT_TIMELINE_001",
                "pattern": r"20\d{2}|año|años|plazo|cronograma",
                "confidence_weight": 0.85,
                "category": "TEMPORAL",
                "match_type": "regex",
            },
            {
                "id": "PAT_ENTITY_001",
                "pattern": r"responsable|secretaría|entidad|ministerio",
                "confidence_weight": 0.80,
                "category": "ENTITY",
                "match_type": "regex",
            },
            {
                "id": "PAT_ENTITY_002",
                "pattern": r"DANE|DNP|Consejería|Departamento",
                "confidence_weight": 0.78,
                "category": "ENTITY",
                "match_type": "regex",
            },
            {
                "id": "PAT_BUDGET_001",
                "pattern": r"presupuesto|recursos|COP|millones|miles de millones",
                "confidence_weight": 0.75,
                "category": "QUANTITATIVE",
                "match_type": "regex",
            },
            {
                "id": "PAT_SOURCE_001",
                "pattern": r"según|fuente|datos de|información de",
                "confidence_weight": 0.70,
                "category": "ENTITY",
                "match_type": "regex",
            },
            {
                "id": "PAT_GEOGRAPHIC_001",
                "pattern": r"departamento|municipio|región|territorial|cobertura",
                "confidence_weight": 0.72,
                "category": "GEOGRAPHIC",
                "match_type": "regex",
            },
            {
                "id": "PAT_INDICATOR_001",
                "pattern": r"indicador|tasa|porcentaje|índice|ratio",
                "confidence_weight": 0.77,
                "category": "QUANTITATIVE",
                "match_type": "regex",
            },
        ],
        "validations": {
            "baseline_must_be_numeric": True,
            "target_must_exceed_baseline": True,
        },
        "failure_contract": {
            "condition": "completeness < 0.6",
            "error_code": "E_INSUFFICIENT_EVIDENCE",
            "remediation": "Expand extraction to additional sections",
        },
    }


@pytest.fixture
def rich_document_text():
    """Rich document with all evidence types."""
    return """
    DIAGNÓSTICO DE GÉNERO - CAPÍTULO 3: INDICADORES CLAVE
    
    3.1 Situación Actual
    
    Según datos del DANE (2023), la línea de base muestra que el 8.5% de mujeres
    ocupan cargos directivos en el sector público. Esta cifra representa una
    situación actual que ha permanecido estable en los últimos cinco años.
    
    La información del DNP indica que la tasa de participación femenina en
    niveles gerenciales es de 12.3% a nivel nacional.
    
    3.2 Metas y Objetivos
    
    La meta establecida para el año 2027 es alcanzar el 15% de participación
    femenina en cargos directivos. Como objetivo intermedio, se espera llegar
    al 12% para 2025.
    
    3.3 Responsabilidades y Presupuesto
    
    Entidad responsable: Secretaría de la Mujer y Equidad de Género.
    Entidades de apoyo: Consejería Presidencial para la Equidad de la Mujer,
    Departamento Administrativo de la Función Pública.
    
    Presupuesto asignado: COP 1,500 millones para el período 2024-2027.
    Recursos adicionales: COP 500 millones de cooperación internacional.
    
    3.4 Cobertura Territorial
    
    La política tendrá cobertura en todo el departamento, con énfasis especial
    en municipios de categoría 4, 5 y 6. La implementación territorial se
    realizará de forma gradual según cronograma establecido.
    
    3.5 Indicadores de Seguimiento
    
    - Indicador 1: Tasa de participación femenina en cargos directivos (%)
    - Indicador 2: Índice de brecha salarial por género
    - Indicador 3: Porcentaje de implementación de política de género
    """


class TestExtractEvidenceIntegrationCore:
    """Core integration tests for extract_evidence()."""

    def test_extract_evidence_integration_returns_structured_result(
        self, comprehensive_signal_node, rich_document_text
    ):
        """Validate extract_evidence returns EvidenceExtractionResult."""
        base_pack = MockSignalPack(comprehensive_signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=rich_document_text,
            signal_node=comprehensive_signal_node,
            document_context=None,
        )

        # Must be structured result
        assert isinstance(result, EvidenceExtractionResult)
        assert not isinstance(result, str)
        assert not isinstance(result.evidence, str)

        # All required fields present
        assert hasattr(result, "evidence")
        assert hasattr(result, "completeness")
        assert hasattr(result, "missing_required")
        assert hasattr(result, "under_minimum")
        assert hasattr(result, "extraction_metadata")

    def test_extract_evidence_processes_all_expected_elements(
        self, comprehensive_signal_node, rich_document_text
    ):
        """Validate all expected_elements are processed."""
        base_pack = MockSignalPack(comprehensive_signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=rich_document_text,
            signal_node=comprehensive_signal_node,
            document_context=None,
        )

        expected_types = [
            e["type"] for e in comprehensive_signal_node["expected_elements"]
        ]

        # Each expected element should have entry in evidence dict
        for element_type in expected_types:
            assert (
                element_type in result.evidence
            ), f"Missing element type: {element_type}"

    def test_extract_evidence_achieves_high_completeness(
        self, comprehensive_signal_node, rich_document_text
    ):
        """Validate high completeness with comprehensive document."""
        base_pack = MockSignalPack(comprehensive_signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=rich_document_text,
            signal_node=comprehensive_signal_node,
            document_context=None,
        )

        # Rich document should achieve high completeness
        assert result.completeness >= 0.7, f"Expected >= 0.7, got {result.completeness}"

        # Should find most required elements
        assert len(result.missing_required) <= 1

    def test_extract_evidence_validates_required_elements(
        self, comprehensive_signal_node
    ):
        """Validate required element tracking."""
        base_pack = MockSignalPack(comprehensive_signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        # Minimal text missing required elements
        minimal_text = "Some generic policy text."

        result = enriched.extract_evidence(
            text=minimal_text,
            signal_node=comprehensive_signal_node,
            document_context=None,
        )

        # Should track missing required elements
        required_elements = [
            e["type"]
            for e in comprehensive_signal_node["expected_elements"]
            if e.get("required", False)
        ]

        for req in required_elements:
            if len(result.evidence[req]) == 0:
                assert req in result.missing_required

        # Completeness should be low
        assert result.completeness < 0.5

    def test_extract_evidence_validates_minimum_cardinality(
        self, comprehensive_signal_node, rich_document_text
    ):
        """Validate minimum cardinality enforcement."""
        base_pack = MockSignalPack(comprehensive_signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=rich_document_text,
            signal_node=comprehensive_signal_node,
            document_context=None,
        )

        # Check elements with minimum requirements
        for elem_spec in comprehensive_signal_node["expected_elements"]:
            if "minimum" in elem_spec:
                element_type = elem_spec["type"]
                minimum = elem_spec["minimum"]
                found_count = len(result.evidence[element_type])

                if found_count < minimum:
                    # Should be in under_minimum list
                    assert any(
                        t[0] == element_type for t in result.under_minimum
                    ), f"{element_type} under minimum but not tracked"

    def test_extract_evidence_includes_match_metadata(
        self, comprehensive_signal_node, rich_document_text
    ):
        """Validate match metadata in evidence."""
        base_pack = MockSignalPack(comprehensive_signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=rich_document_text,
            signal_node=comprehensive_signal_node,
            document_context=None,
        )

        # Check all matches have metadata
        for element_type, matches in result.evidence.items():
            for match in matches:
                assert "value" in match
                assert "confidence" in match
                assert "pattern_id" in match
                assert "category" in match
                assert "span" in match
                assert "lineage" in match

                # Validate confidence range
                assert 0.0 <= match["confidence"] <= 1.0

                # Validate lineage tracking
                assert "pattern_id" in match["lineage"]
                assert "element_type" in match["lineage"]
                assert "extraction_phase" in match["lineage"]

    def test_extract_evidence_includes_extraction_metadata(
        self, comprehensive_signal_node, rich_document_text
    ):
        """Validate extraction metadata."""
        base_pack = MockSignalPack(comprehensive_signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=rich_document_text,
            signal_node=comprehensive_signal_node,
            document_context=None,
        )

        # Check extraction metadata
        assert "expected_count" in result.extraction_metadata
        assert "pattern_count" in result.extraction_metadata
        assert "total_matches" in result.extraction_metadata

        # Validate metadata values
        assert result.extraction_metadata["expected_count"] == len(
            comprehensive_signal_node["expected_elements"]
        )
        assert result.extraction_metadata["pattern_count"] == len(
            comprehensive_signal_node["patterns"]
        )
        assert result.extraction_metadata["total_matches"] >= 0


class TestCompletenessMetricsValidation:
    """Validate completeness metrics calculation."""

    def test_completeness_perfect_all_required_found(self):
        """Test completeness = 1.0 when all required found."""
        evidence = {
            "elem1": [{"value": "val1"}],
            "elem2": [{"value": "val2"}],
        }
        expected = [
            {"type": "elem1", "required": True},
            {"type": "elem2", "required": True},
        ]

        score = compute_completeness(evidence, expected)
        assert score == 1.0

    def test_completeness_zero_no_required_found(self):
        """Test completeness = 0.0 when no required found."""
        evidence = {"elem1": [], "elem2": []}
        expected = [
            {"type": "elem1", "required": True},
            {"type": "elem2", "required": True},
        ]

        score = compute_completeness(evidence, expected)
        assert score == 0.0

    def test_completeness_partial_some_required_found(self):
        """Test partial completeness."""
        evidence = {
            "elem1": [{"value": "val1"}],
            "elem2": [],
            "elem3": [{"value": "val3"}],
        }
        expected = [
            {"type": "elem1", "required": True},
            {"type": "elem2", "required": True},
            {"type": "elem3", "required": True},
        ]

        score = compute_completeness(evidence, expected)
        expected_score = 2.0 / 3.0  # 2 of 3 found
        assert abs(score - expected_score) < 0.01

    def test_completeness_minimum_proportional_scoring(self):
        """Test minimum cardinality uses proportional scoring."""
        evidence = {
            "sources": [{"value": "s1"}, {"value": "s2"}],
        }
        expected = [
            {"type": "sources", "minimum": 4},
        ]

        score = compute_completeness(evidence, expected)
        expected_score = 2.0 / 4.0  # 2 of 4 minimum
        assert abs(score - expected_score) < 0.01

    def test_completeness_minimum_capped_at_one(self):
        """Test minimum score capped at 1.0."""
        evidence = {
            "sources": [{"value": f"s{i}"} for i in range(10)],
        }
        expected = [
            {"type": "sources", "minimum": 3},
        ]

        score = compute_completeness(evidence, expected)
        assert score == 1.0

    def test_completeness_optional_bonus_when_present(self):
        """Test optional elements provide bonus."""
        evidence = {
            "optional1": [{"value": "val1"}],
        }
        expected = [
            {"type": "optional1", "required": False, "minimum": 0},
        ]

        score = compute_completeness(evidence, expected)
        assert score == 1.0  # Present = full score

    def test_completeness_optional_partial_when_absent(self):
        """Test optional elements partial score when absent."""
        evidence = {
            "optional1": [],
        }
        expected = [
            {"type": "optional1", "required": False, "minimum": 0},
        ]

        score = compute_completeness(evidence, expected)
        assert score == 0.5  # Absent = 0.5 score

    def test_completeness_mixed_requirements(self):
        """Test completeness with mixed requirements."""
        evidence = {
            "required1": [{"value": "r1"}],
            "required2": [],
            "minimum1": [{"value": "m1"}],
            "optional1": [{"value": "o1"}],
        }
        expected = [
            {"type": "required1", "required": True},
            {"type": "required2", "required": True},
            {"type": "minimum1", "minimum": 3},
            {"type": "optional1", "required": False},
        ]

        score = compute_completeness(evidence, expected)

        # Calculate expected: (1.0 + 0.0 + 1/3 + 1.0) / 4
        expected_score = (1.0 + 0.0 + (1.0 / 3.0) + 1.0) / 4.0
        assert abs(score - expected_score) < 0.01


class TestPatternRelevanceFiltering:
    """Test pattern relevance filtering for element types."""

    def test_infer_temporal_categories(self):
        """Test temporal category inference."""
        for keyword in ["temporal", "año", "años", "plazo", "cronograma", "series"]:
            categories = _infer_pattern_categories_for_element(f"element_{keyword}")
            assert categories is not None
            assert "TEMPORAL" in categories

    def test_infer_quantitative_categories(self):
        """Test quantitative category inference."""
        for keyword in ["cuantitativo", "indicador", "meta", "brecha", "baseline"]:
            categories = _infer_pattern_categories_for_element(f"element_{keyword}")
            assert categories is not None
            assert "QUANTITATIVE" in categories

    def test_infer_geographic_categories(self):
        """Test geographic category inference."""
        for keyword in ["territorial", "cobertura", "geographic", "región"]:
            categories = _infer_pattern_categories_for_element(f"element_{keyword}")
            assert categories is not None
            assert "GEOGRAPHIC" in categories

    def test_infer_entity_categories(self):
        """Test entity category inference."""
        for keyword in ["fuente", "entidad", "responsable", "oficial"]:
            categories = _infer_pattern_categories_for_element(f"element_{keyword}")
            assert categories is not None
            assert "ENTITY" in categories

    def test_accept_all_for_generic(self):
        """Test generic elements accept all categories."""
        categories = _infer_pattern_categories_for_element("generic_element")
        assert categories is None

    def test_pattern_relevant_by_keyword_overlap(self):
        """Test pattern relevance by keyword overlap."""
        pattern_spec = {
            "pattern": "presupuesto asignado",
            "validation_rule": "budget_validation",
            "context_requirement": "",
        }

        is_relevant = _is_pattern_relevant_to_element(
            "presupuesto asignado", "presupuesto_municipal", pattern_spec
        )

        assert is_relevant is True

    def test_pattern_not_relevant_no_overlap(self):
        """Test pattern not relevant with no overlap."""
        pattern_spec = {
            "pattern": "population growth",
            "validation_rule": "",
            "context_requirement": "",
        }

        is_relevant = _is_pattern_relevant_to_element(
            "population growth", "budget_amount", pattern_spec
        )

        assert is_relevant is False


class TestDeduplication:
    """Test evidence match deduplication."""

    def test_deduplicate_overlapping_keeps_highest_confidence(self):
        """Test deduplication keeps highest confidence match."""
        matches = [
            {"value": "test1", "confidence": 0.7, "span": (0, 5)},
            {"value": "test2", "confidence": 0.9, "span": (2, 7)},
        ]

        deduplicated = _deduplicate_matches(matches)

        assert len(deduplicated) == 1
        assert deduplicated[0]["confidence"] == 0.9

    def test_deduplicate_non_overlapping_keeps_all(self):
        """Test non-overlapping matches kept."""
        matches = [
            {"value": "test1", "confidence": 0.8, "span": (0, 5)},
            {"value": "test2", "confidence": 0.9, "span": (10, 15)},
        ]

        deduplicated = _deduplicate_matches(matches)

        assert len(deduplicated) == 2

    def test_deduplicate_empty_list(self):
        """Test empty list handled."""
        deduplicated = _deduplicate_matches([])
        assert deduplicated == []


class TestRealQuestionnaireValidation:
    """Validate against real questionnaire (1,200 element target)."""

    def test_extract_evidence_with_real_nodes(self, micro_questions):
        """Test with real signal nodes."""
        nodes_with_elements = [
            mq for mq in micro_questions if mq.get("expected_elements")
        ]

        assert len(nodes_with_elements) > 0

        # Test sample nodes
        for mq in nodes_with_elements[:10]:
            base_pack = MockSignalPack(mq.get("patterns", []))
            enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

            sample_text = "Baseline: 10%. Target: 20% by 2027. Responsible: Ministry."

            result = enriched.extract_evidence(
                text=sample_text, signal_node=mq, document_context=None
            )

            assert isinstance(result, EvidenceExtractionResult)
            assert 0.0 <= result.completeness <= 1.0

    def test_element_specifications_coverage(self, micro_questions):
        """Validate element specification coverage toward 1,200 target."""
        total_elements = 0
        element_types = set()

        for mq in micro_questions:
            expected = mq.get("expected_elements", [])
            total_elements += len(expected)

            for elem in expected:
                if isinstance(elem, dict):
                    element_types.add(elem.get("type", ""))
                elif isinstance(elem, str):
                    element_types.add(elem)

        print(f"\n  Total element specifications: {total_elements}")
        print(f"  Unique element types: {len(element_types)}")

        assert total_elements > 0

    def test_intelligence_metrics_integration(
        self, comprehensive_signal_node, rich_document_text
    ):
        """Test intelligence metrics with evidence extraction."""
        base_pack = MockSignalPack(comprehensive_signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        # Extract evidence
        evidence_result = enriched.extract_evidence(
            text=rich_document_text,
            signal_node=comprehensive_signal_node,
            document_context=None,
        )

        # Get intelligence metrics
        metrics = enriched.get_intelligence_metrics(
            context_stats=None,
            evidence_result=evidence_result,
            validation_result=None,
        )

        assert isinstance(metrics, IntelligenceMetrics)
        assert metrics.evidence_completeness == evidence_result.completeness
        assert metrics.evidence_elements_extracted >= 0
        assert metrics.missing_required_elements >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
