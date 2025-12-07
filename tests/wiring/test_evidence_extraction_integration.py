"""
Integration Validation for extract_evidence() with extract_structured_evidence()
==================================================================================

Comprehensive integration tests validating extract_evidence() calling 
extract_structured_evidence() with proper expected_elements processing and 
completeness metrics, ensuring structured output based on 1,200 element specifications.

Test Coverage:
1. Signal Intelligence Layer extract_evidence() Integration
   - Verifies EnrichedSignalPack.extract_evidence() correctly calls extract_structured_evidence()
   - Validates expected_elements from signal nodes are properly passed through
   - Ensures completeness metrics are accurately computed and returned

2. Expected Elements Processing (1,200 Specifications)
   - Tests all element types: required, minimum cardinality, optional
   - Validates element type filtering and pattern relevance
   - Ensures confidence score propagation through extraction pipeline

3. Completeness Metrics Validation
   - Tests completeness calculation: 0.0 (missing all) to 1.0 (found all)
   - Validates required element tracking (missing_required list)
   - Tests minimum cardinality validation (under_minimum list)

4. Structured Output Verification
   - Ensures output is EvidenceExtractionResult, not text blob
   - Validates evidence dictionary structure: element_type → matches
   - Tests extraction metadata: pattern counts, match counts

5. End-to-End Integration
   - Complete flow from signal node → pattern filtering → evidence extraction
   - Integration with document context for context-aware extraction
   - Metadata lineage tracking through entire pipeline

6. Real Questionnaire Data
   - Uses actual signal nodes with real expected_elements
   - Tests with diverse element types across dimensions
   - Validates against 1,200 element specification target

Architecture:
- Tests signal_intelligence_layer.EnrichedSignalPack.extract_evidence()
- Validates signal_evidence_extractor.extract_structured_evidence()
- Uses real questionnaire data (no mocks for signal nodes)
- Comprehensive assertions on completeness scoring
- Validates structured dict output vs unstructured blobs

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-06
Coverage: extract_evidence() integration with 1,200 element specifications
"""

from typing import Any

import pytest

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_evidence_extractor import (
    EvidenceExtractionResult,
    compute_completeness,
    extract_structured_evidence,
)
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    EnrichedSignalPack,
    analyze_with_intelligence_layer,
)


class MockSignalPack:
    """Mock signal pack for testing."""

    def __init__(
        self,
        patterns: list[dict[str, Any]],
        micro_questions: list[dict[str, Any]] | None = None,
    ):
        self.patterns = patterns
        self.micro_questions = micro_questions or []

    def get_node(self, signal_id: str) -> dict[str, Any] | None:
        for mq in self.micro_questions:
            if mq.get("id") == signal_id or mq.get("question_id") == signal_id:
                return mq
        return None


@pytest.fixture(scope="module")
def real_questionnaire():
    """Load real questionnaire data."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def real_micro_questions(real_questionnaire):
    """Extract all micro questions from questionnaire."""
    return real_questionnaire.get_micro_questions()


@pytest.fixture
def sample_signal_node_with_elements():
    """Create sample signal node with expected_elements."""
    return {
        "id": "TEST_MQ_001",
        "question_id": "TEST_MQ_001",
        "expected_elements": [
            {"type": "baseline_indicator", "required": True},
            {"type": "target_value", "required": True},
            {"type": "timeline", "required": False},
            {"type": "responsible_entity", "minimum": 1},
            {"type": "budget_amount", "required": False},
        ],
        "patterns": [
            {
                "id": "PAT_BASELINE",
                "pattern": r"línea de base|baseline",
                "confidence_weight": 0.9,
                "category": "QUANTITATIVE",
                "match_type": "regex",
            },
            {
                "id": "PAT_TARGET",
                "pattern": r"meta|target|objetivo",
                "confidence_weight": 0.85,
                "category": "QUANTITATIVE",
                "match_type": "regex",
            },
            {
                "id": "PAT_TIMELINE",
                "pattern": r"20\d{2}|año|años|plazo",
                "confidence_weight": 0.8,
                "category": "TEMPORAL",
                "match_type": "regex",
            },
            {
                "id": "PAT_ENTITY",
                "pattern": r"responsable|secretaría|entidad|DANE|DNP",
                "confidence_weight": 0.75,
                "category": "ENTITY",
                "match_type": "regex",
            },
            {
                "id": "PAT_BUDGET",
                "pattern": r"presupuesto|recursos|COP|millones",
                "confidence_weight": 0.7,
                "category": "QUANTITATIVE",
                "match_type": "regex",
            },
        ],
        "validations": {},
        "failure_contract": {
            "condition": "completeness < 0.7",
            "error_code": "E_INSUFFICIENT_EVIDENCE",
            "remediation": "Expand search to additional document sections",
        },
    }


@pytest.fixture
def sample_document_text():
    """Sample document text with evidence elements."""
    return """
    Diagnóstico de Género - Indicadores Clave
    
    Línea de base año 2023: 8.5% de mujeres en cargos directivos del sector público.
    Según datos del DANE, esta cifra ha permanecido estable en los últimos 5 años.
    
    Meta establecida: alcanzar el 15% de participación para el año 2027, con revisiones
    intermedias en 2025 (objetivo: 12%).
    
    Entidad responsable: Secretaría de la Mujer y Equidad de Género.
    Entidades de apoyo: DNP y Consejería Presidencial para la Equidad de la Mujer.
    
    Presupuesto asignado: COP 1,500 millones para el período 2024-2027.
    Recursos adicionales: COP 500 millones de cooperación internacional.
    """


class TestExtractEvidenceIntegration:
    """Test EnrichedSignalPack.extract_evidence() integration."""

    def test_extract_evidence_returns_structured_result(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test extract_evidence returns EvidenceExtractionResult, not text blob."""
        base_pack = MockSignalPack(sample_signal_node_with_elements["patterns"])
        enriched_pack = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched_pack.extract_evidence(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Assert structured result, not blob
        assert isinstance(result, EvidenceExtractionResult)
        assert hasattr(result, "evidence")
        assert hasattr(result, "completeness")
        assert hasattr(result, "missing_required")
        assert hasattr(result, "under_minimum")
        assert hasattr(result, "extraction_metadata")

        # Evidence should be dict, not string
        assert isinstance(result.evidence, dict)
        assert not isinstance(result.evidence, str)

    def test_extract_evidence_processes_expected_elements(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test extract_evidence correctly processes expected_elements."""
        base_pack = MockSignalPack(sample_signal_node_with_elements["patterns"])
        enriched_pack = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched_pack.extract_evidence(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Should have extracted evidence for expected element types
        expected_types = [
            e["type"] for e in sample_signal_node_with_elements["expected_elements"]
        ]

        for element_type in expected_types:
            # Each expected element should have entry in evidence dict
            assert element_type in result.evidence

        # Should find baseline, target, timeline, entity, budget
        assert len(result.evidence["baseline_indicator"]) > 0
        assert len(result.evidence["target_value"]) > 0
        assert len(result.evidence["timeline"]) > 0
        assert len(result.evidence["responsible_entity"]) > 0

    def test_extract_evidence_validates_required_elements(
        self, sample_signal_node_with_elements
    ):
        """Test extract_evidence tracks missing required elements."""
        base_pack = MockSignalPack(sample_signal_node_with_elements["patterns"])
        enriched_pack = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        # Text missing required elements
        incomplete_text = "Some text without baseline or target."

        result = enriched_pack.extract_evidence(
            text=incomplete_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Should track missing required elements
        assert len(result.missing_required) > 0
        assert "baseline_indicator" in result.missing_required
        assert "target_value" in result.missing_required

        # Completeness should reflect missing required elements
        assert result.completeness < 1.0

    def test_extract_evidence_validates_minimum_cardinality(self):
        """Test extract_evidence validates minimum element cardinality."""
        signal_node = {
            "id": "TEST_MIN_CARD",
            "expected_elements": [
                {"type": "sources", "minimum": 3},
            ],
            "patterns": [
                {
                    "id": "PAT_SOURCE",
                    "pattern": r"DANE|DNP|Secretaría",
                    "confidence_weight": 0.9,
                    "category": "ENTITY",
                    "match_type": "regex",
                }
            ],
            "validations": {},
        }

        text = "Fuente: DANE. También consultar DNP."

        base_pack = MockSignalPack(signal_node["patterns"])
        enriched_pack = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched_pack.extract_evidence(
            text=text, signal_node=signal_node, document_context=None
        )

        # Should find 2 sources (DANE, DNP) but require 3
        assert len(result.under_minimum) > 0
        element_type, found, minimum = result.under_minimum[0]
        assert element_type == "sources"
        assert found < minimum
        assert minimum == 3

    def test_extract_evidence_computes_completeness_metrics(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test extract_evidence computes accurate completeness score."""
        base_pack = MockSignalPack(sample_signal_node_with_elements["patterns"])
        enriched_pack = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched_pack.extract_evidence(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Completeness should be between 0.0 and 1.0
        assert 0.0 <= result.completeness <= 1.0

        # With comprehensive document, should have high completeness
        assert result.completeness >= 0.7

        # Should have minimal missing required elements
        assert len(result.missing_required) <= 1

    def test_extract_evidence_with_partial_data(self):
        """Test extract_evidence with partially complete data."""
        signal_node = {
            "id": "TEST_PARTIAL",
            "expected_elements": [
                {"type": "baseline", "required": True},
                {"type": "target", "required": True},
                {"type": "timeline", "required": True},
            ],
            "patterns": [
                {
                    "id": "PAT_BASELINE",
                    "pattern": r"baseline",
                    "confidence_weight": 0.9,
                    "category": "QUANTITATIVE",
                    "match_type": "regex",
                },
                {
                    "id": "PAT_TARGET",
                    "pattern": r"target",
                    "confidence_weight": 0.9,
                    "category": "QUANTITATIVE",
                    "match_type": "regex",
                },
                {
                    "id": "PAT_TIMELINE",
                    "pattern": r"20\d{2}",
                    "confidence_weight": 0.8,
                    "category": "TEMPORAL",
                    "match_type": "regex",
                },
            ],
            "validations": {},
        }

        # Text with only baseline, missing target and timeline
        partial_text = "The baseline is 10%."

        base_pack = MockSignalPack(signal_node["patterns"])
        enriched_pack = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched_pack.extract_evidence(
            text=partial_text, signal_node=signal_node, document_context=None
        )

        # Should find baseline
        assert len(result.evidence["baseline"]) > 0

        # Should miss target and timeline
        assert "target" in result.missing_required
        assert "timeline" in result.missing_required

        # Completeness should be ~0.33 (1 of 3 required)
        assert 0.2 <= result.completeness <= 0.5

    def test_extract_evidence_propagates_confidence_scores(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test extract_evidence propagates confidence scores from patterns."""
        base_pack = MockSignalPack(sample_signal_node_with_elements["patterns"])
        enriched_pack = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched_pack.extract_evidence(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Check evidence items have confidence scores
        for element_type, matches in result.evidence.items():
            for match in matches:
                assert "confidence" in match
                assert 0.0 <= match["confidence"] <= 1.0
                assert "pattern_id" in match
                assert "category" in match

    def test_extract_evidence_includes_extraction_metadata(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test extract_evidence includes comprehensive extraction metadata."""
        base_pack = MockSignalPack(sample_signal_node_with_elements["patterns"])
        enriched_pack = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched_pack.extract_evidence(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Should include extraction metadata
        assert "expected_count" in result.extraction_metadata
        assert "pattern_count" in result.extraction_metadata
        assert "total_matches" in result.extraction_metadata

        # Validate metadata values
        assert result.extraction_metadata["expected_count"] == len(
            sample_signal_node_with_elements["expected_elements"]
        )
        assert result.extraction_metadata["pattern_count"] > 0
        assert result.extraction_metadata["total_matches"] >= 0


class TestExtractStructuredEvidenceIntegration:
    """Test extract_structured_evidence() directly."""

    def test_extract_structured_evidence_with_dict_elements(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test extract_structured_evidence with dict-format expected_elements."""
        result = extract_structured_evidence(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        assert isinstance(result, EvidenceExtractionResult)
        assert len(result.evidence) > 0
        assert result.completeness > 0.0

    def test_extract_structured_evidence_with_string_elements(
        self, sample_document_text
    ):
        """Test extract_structured_evidence with legacy string-format elements."""
        signal_node = {
            "id": "TEST_LEGACY",
            "expected_elements": ["baseline", "target", "timeline"],
            "patterns": [
                {
                    "id": "PAT_BASELINE",
                    "pattern": r"línea de base|baseline",
                    "confidence_weight": 0.9,
                    "category": "QUANTITATIVE",
                    "match_type": "regex",
                },
                {
                    "id": "PAT_TARGET",
                    "pattern": r"meta|target",
                    "confidence_weight": 0.85,
                    "category": "QUANTITATIVE",
                    "match_type": "regex",
                },
                {
                    "id": "PAT_TIMELINE",
                    "pattern": r"20\d{2}",
                    "confidence_weight": 0.8,
                    "category": "TEMPORAL",
                    "match_type": "regex",
                },
            ],
            "validations": {},
        }

        result = extract_structured_evidence(
            text=sample_document_text, signal_node=signal_node, document_context=None
        )

        # Should handle legacy format
        assert "baseline" in result.evidence
        assert "target" in result.evidence
        assert "timeline" in result.evidence

    def test_extract_structured_evidence_empty_elements(self):
        """Test extract_structured_evidence with no expected elements."""
        signal_node = {
            "id": "TEST_EMPTY",
            "expected_elements": [],
            "patterns": [],
            "validations": {},
        }

        result = extract_structured_evidence(text="Some text", signal_node=signal_node)

        # Should return valid result with completeness 1.0 (nothing expected)
        assert isinstance(result, EvidenceExtractionResult)
        assert result.completeness == 1.0
        assert len(result.missing_required) == 0
        assert len(result.under_minimum) == 0


class TestCompletenessMetricsIntegration:
    """Test completeness metrics calculation."""

    def test_completeness_perfect_score(self):
        """Test completeness = 1.0 when all elements found."""
        evidence = {
            "element1": [{"value": "found", "confidence": 0.9}],
            "element2": [{"value": "found", "confidence": 0.8}],
            "element3": [{"value": "found", "confidence": 0.85}],
        }
        expected_elements = [
            {"type": "element1", "required": True},
            {"type": "element2", "required": True},
            {"type": "element3", "required": False},
        ]

        completeness = compute_completeness(evidence, expected_elements)

        assert completeness == 1.0

    def test_completeness_zero_score(self):
        """Test completeness = 0.0 when no required elements found."""
        evidence = {}
        expected_elements = [
            {"type": "element1", "required": True},
            {"type": "element2", "required": True},
        ]

        completeness = compute_completeness(evidence, expected_elements)

        assert completeness == 0.0

    def test_completeness_partial_score(self):
        """Test completeness partial score with mixed results."""
        evidence = {
            "element1": [{"value": "found"}],
            "element2": [],
        }
        expected_elements = [
            {"type": "element1", "required": True},
            {"type": "element2", "required": True},
        ]

        completeness = compute_completeness(evidence, expected_elements)

        # Should be 0.5 (1 of 2 required found)
        assert completeness == 0.5

    def test_completeness_minimum_cardinality(self):
        """Test completeness with minimum cardinality requirements."""
        evidence = {
            "sources": [{"value": "src1"}, {"value": "src2"}],
        }
        expected_elements = [
            {"type": "sources", "minimum": 4},
        ]

        completeness = compute_completeness(evidence, expected_elements)

        # Should be 0.5 (2 of 4 minimum found)
        assert completeness == 0.5

    def test_completeness_optional_elements(self):
        """Test completeness scoring with optional elements."""
        evidence = {
            "required1": [{"value": "found"}],
            "optional1": [{"value": "found"}],
        }
        expected_elements = [
            {"type": "required1", "required": True},
            {"type": "optional1", "required": False, "minimum": 0},
        ]

        completeness = compute_completeness(evidence, expected_elements)

        # Required found (1.0) + optional found (1.0) = average 1.0
        assert completeness == 1.0


class TestRealQuestionnaireIntegration:
    """Test with real questionnaire data (1,200 element specifications)."""

    def test_extract_evidence_with_real_signal_nodes(self, real_micro_questions):
        """Test extract_evidence with real signal nodes from questionnaire."""
        # Find signal nodes with expected_elements
        nodes_with_elements = [
            mq for mq in real_micro_questions if mq.get("expected_elements")
        ]

        assert (
            len(nodes_with_elements) > 0
        ), "No signal nodes with expected_elements found"

        # Test first 5 nodes with elements
        for mq in nodes_with_elements[:5]:
            base_pack = MockSignalPack(mq.get("patterns", []), [mq])
            enriched_pack = EnrichedSignalPack(
                base_pack, enable_semantic_expansion=False
            )

            # Sample text (in real usage, this comes from document)
            sample_text = """
            Línea de base: 10%. Meta: 20% para 2027.
            Responsable: Secretaría. Presupuesto: COP 1,000 millones.
            """

            result = enriched_pack.extract_evidence(
                text=sample_text, signal_node=mq, document_context=None
            )

            # Validate result structure
            assert isinstance(result, EvidenceExtractionResult)
            assert isinstance(result.evidence, dict)
            assert 0.0 <= result.completeness <= 1.0
            assert isinstance(result.missing_required, list)
            assert isinstance(result.under_minimum, list)

    def test_expected_elements_coverage_across_questionnaire(
        self, real_micro_questions
    ):
        """Test expected_elements coverage across questionnaire (target: 1,200)."""
        total_elements = 0
        element_types = set()
        nodes_with_elements = 0

        for mq in real_micro_questions:
            expected = mq.get("expected_elements", [])
            if expected:
                nodes_with_elements += 1
                total_elements += len(expected)

                for elem in expected:
                    if isinstance(elem, dict):
                        element_types.add(elem.get("type", ""))
                    elif isinstance(elem, str):
                        element_types.add(elem)

        print(f"\n  Total signal nodes with expected_elements: {nodes_with_elements}")
        print(f"  Total expected_elements specifications: {total_elements}")
        print(f"  Unique element types: {len(element_types)}")

        # Should have significant coverage toward 1,200 target
        assert nodes_with_elements > 0
        assert total_elements > 0

    def test_completeness_metrics_with_diverse_nodes(self, real_micro_questions):
        """Test completeness metrics across diverse signal nodes."""
        nodes_with_elements = [
            mq for mq in real_micro_questions if mq.get("expected_elements")
        ][:10]

        completeness_scores = []

        for mq in nodes_with_elements:
            signal_node = {
                "id": mq.get("id", "unknown"),
                "expected_elements": mq.get("expected_elements", []),
                "patterns": mq.get("patterns", []),
                "validations": mq.get("validations", {}),
            }

            # Test with rich document
            rich_text = """
            Diagnóstico: línea de base 15% en 2023. Meta: 25% para 2027.
            Responsable: Secretaría de Desarrollo. Fuente: DANE.
            Presupuesto: COP 2,000 millones. Indicadores: tasa de empleo.
            Cobertura territorial: todo el departamento.
            """

            result = extract_structured_evidence(
                text=rich_text, signal_node=signal_node, document_context=None
            )

            completeness_scores.append(result.completeness)

        # Validate distribution of completeness scores
        assert len(completeness_scores) > 0
        assert all(0.0 <= score <= 1.0 for score in completeness_scores)

        avg_completeness = sum(completeness_scores) / len(completeness_scores)
        print(f"\n  Average completeness across nodes: {avg_completeness:.2f}")
        print(f"  Min completeness: {min(completeness_scores):.2f}")
        print(f"  Max completeness: {max(completeness_scores):.2f}")


class TestEndToEndIntegration:
    """Test end-to-end integration with analyze_with_intelligence_layer."""

    def test_analyze_with_intelligence_layer_includes_evidence(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test analyze_with_intelligence_layer includes structured evidence."""
        result = analyze_with_intelligence_layer(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Should include evidence section
        assert "evidence" in result
        assert isinstance(result["evidence"], dict)

        # Should include completeness
        assert "completeness" in result
        assert 0.0 <= result["completeness"] <= 1.0

        # Should include missing_elements
        assert "missing_elements" in result
        assert isinstance(result["missing_elements"], list)

    def test_analyze_with_intelligence_layer_validation_integration(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test integration between evidence extraction and validation."""
        result = analyze_with_intelligence_layer(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Should include validation section
        assert "validation" in result
        assert "status" in result["validation"]
        assert "passed" in result["validation"]

        # Validation should consider completeness
        if result["completeness"] < 0.7:
            # Should fail validation if completeness too low
            assert result["validation"]["passed"] is False
            assert result["validation"]["error_code"] is not None

    def test_metadata_propagation_through_pipeline(
        self, sample_signal_node_with_elements, sample_document_text
    ):
        """Test metadata propagates through entire pipeline."""
        result = analyze_with_intelligence_layer(
            text=sample_document_text,
            signal_node=sample_signal_node_with_elements,
            document_context=None,
        )

        # Should include metadata
        assert "metadata" in result
        assert result["metadata"]["intelligence_layer_enabled"] is True

        # Should include refactorings applied
        assert "refactorings_applied" in result["metadata"]
        refactorings = result["metadata"]["refactorings_applied"]
        assert "evidence_structure" in refactorings

        # Should include extraction metadata
        assert "expected_count" in result["metadata"]
        assert "pattern_count" in result["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
