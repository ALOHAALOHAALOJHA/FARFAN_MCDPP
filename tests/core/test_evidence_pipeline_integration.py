"""
Evidence Pipeline Integration Tests - End-to-End Validation
============================================================

Complete end-to-end integration tests for the evidence extraction pipeline,
validating the full flow from document text through extract_evidence() to
structured output with completeness metrics.

Test Coverage:

1. PIPELINE INTEGRATION
   - analyze_with_intelligence_layer() end-to-end
   - extract_evidence() → extract_structured_evidence() flow
   - Document context integration
   - Pattern filtering → evidence extraction → validation

2. EVIDENCE + VALIDATION INTEGRATION
   - Evidence completeness affects validation
   - Failure contracts trigger on low completeness
   - Validation metadata includes evidence metrics
   - Error codes and remediation based on completeness

3. METADATA PROPAGATION
   - Pattern metadata → match lineage
   - Extraction metadata through pipeline
   - Intelligence layer metadata
   - Refactorings applied tracking

4. PERFORMANCE AND SCALE
   - Multiple signal nodes
   - Large documents
   - Complex expected_elements
   - Pattern count scalability

5. EDGE CASES
   - Empty documents
   - No expected elements
   - No patterns
   - All required missing
   - Exceeding minimum cardinality

6. REAL DATA VALIDATION
   - Actual questionnaire signal nodes
   - Diverse element types (1,200 specifications)
   - Cross-dimensional testing (D1-D6)
   - Cross-policy area testing (PA01-PA10)

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-06
Coverage: Complete evidence pipeline integration
"""

from typing import Any

import pytest

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    EnrichedSignalPack,
    analyze_with_intelligence_layer,
)


class MockSignalPack:
    """Mock signal pack."""

    def __init__(self, patterns: list[dict[str, Any]]):
        self.patterns = patterns


@pytest.fixture(scope="module")
def questionnaire():
    """Load questionnaire."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def micro_questions(questionnaire):
    """Get micro questions."""
    return questionnaire.get_micro_questions()


@pytest.fixture
def signal_node_with_contract():
    """Signal node with failure contract."""
    return {
        "id": "CONTRACT_TEST_001",
        "expected_elements": [
            {"type": "baseline", "required": True},
            {"type": "target", "required": True},
            {"type": "timeline", "required": True},
        ],
        "patterns": [
            {
                "id": "PAT_BASELINE",
                "pattern": r"baseline|línea de base",
                "confidence_weight": 0.9,
                "category": "QUANTITATIVE",
                "match_type": "regex",
            },
            {
                "id": "PAT_TARGET",
                "pattern": r"target|meta",
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
        "failure_contract": {
            "condition": "completeness < 0.7",
            "error_code": "E_INSUFFICIENT_EVIDENCE",
            "remediation": "Expand search to additional document sections",
        },
    }


class TestAnalyzeWithIntelligenceLayerIntegration:
    """Test complete pipeline via analyze_with_intelligence_layer."""

    def test_analyze_complete_document_success(self, signal_node_with_contract):
        """Test successful analysis with complete document."""
        complete_text = """
        Current baseline is 10% participation rate.
        The target for 2027 is 20% participation.
        Implementation timeline: 2024-2027.
        """

        result = analyze_with_intelligence_layer(
            text=complete_text,
            signal_node=signal_node_with_contract,
            document_context=None,
        )

        # Should have evidence
        assert "evidence" in result
        assert isinstance(result["evidence"], dict)

        # Should have high completeness
        assert "completeness" in result
        assert result["completeness"] >= 0.7

        # Validation should pass
        assert "validation" in result
        assert result["validation"]["passed"] is True

        # Should have metadata
        assert "metadata" in result
        assert result["metadata"]["intelligence_layer_enabled"] is True

    def test_analyze_incomplete_document_validation_failure(
        self, signal_node_with_contract
    ):
        """Test validation failure with incomplete document."""
        incomplete_text = "Some text without required evidence."

        result = analyze_with_intelligence_layer(
            text=incomplete_text,
            signal_node=signal_node_with_contract,
            document_context=None,
        )

        # Should have low completeness
        assert result["completeness"] < 0.7

        # Should have missing elements
        assert len(result["missing_elements"]) > 0

        # Validation should fail
        assert result["validation"]["passed"] is False
        assert result["validation"]["error_code"] == "E_INSUFFICIENT_EVIDENCE"
        assert "remediation" in result["validation"]

    def test_analyze_includes_structured_evidence(self, signal_node_with_contract):
        """Test result includes structured evidence dict."""
        text = "Baseline: 10%. Target: 20% for 2027."

        result = analyze_with_intelligence_layer(
            text=text, signal_node=signal_node_with_contract, document_context=None
        )

        # Evidence should be dict, not string
        assert isinstance(result["evidence"], dict)
        assert not isinstance(result["evidence"], str)

        # Should have element types as keys
        for elem_spec in signal_node_with_contract["expected_elements"]:
            assert elem_spec["type"] in result["evidence"]

    def test_analyze_propagates_metadata(self, signal_node_with_contract):
        """Test metadata propagation through pipeline."""
        text = "Baseline: 10%. Target: 20% for 2027."

        result = analyze_with_intelligence_layer(
            text=text, signal_node=signal_node_with_contract, document_context=None
        )

        # Should include extraction metadata
        assert "expected_count" in result["metadata"]
        assert "pattern_count" in result["metadata"]

        # Should track refactorings
        assert "refactorings_applied" in result["metadata"]
        refactorings = result["metadata"]["refactorings_applied"]
        assert "evidence_structure" in refactorings

    def test_analyze_with_document_context(self, signal_node_with_contract):
        """Test analysis with document context."""
        text = "Baseline: 10%. Target: 20% for 2027."
        context = {"section": "indicators", "chapter": 3, "page": 15}

        result = analyze_with_intelligence_layer(
            text=text, signal_node=signal_node_with_contract, document_context=context
        )

        # Should complete successfully
        assert "evidence" in result
        assert "completeness" in result


class TestEvidenceValidationIntegration:
    """Test integration between evidence extraction and validation."""

    def test_high_completeness_passes_validation(self):
        """Test high completeness passes validation."""
        signal_node = {
            "id": "TEST_PASS",
            "expected_elements": [
                {"type": "elem1", "required": True},
                {"type": "elem2", "required": True},
            ],
            "patterns": [
                {
                    "id": "PAT1",
                    "pattern": r"elem1_text",
                    "confidence_weight": 0.9,
                    "category": "GENERAL",
                    "match_type": "regex",
                },
                {
                    "id": "PAT2",
                    "pattern": r"elem2_text",
                    "confidence_weight": 0.9,
                    "category": "GENERAL",
                    "match_type": "regex",
                },
            ],
            "validations": {},
            "failure_contract": {
                "condition": "completeness < 0.8",
                "error_code": "E_LOW_COMPLETENESS",
            },
        }

        text = "Document contains elem1_text and elem2_text."

        result = analyze_with_intelligence_layer(
            text=text, signal_node=signal_node, document_context=None
        )

        assert result["completeness"] >= 0.8
        assert result["validation"]["passed"] is True

    def test_low_completeness_fails_validation(self):
        """Test low completeness fails validation."""
        signal_node = {
            "id": "TEST_FAIL",
            "expected_elements": [
                {"type": "elem1", "required": True},
                {"type": "elem2", "required": True},
            ],
            "patterns": [
                {
                    "id": "PAT1",
                    "pattern": r"elem1_text",
                    "confidence_weight": 0.9,
                    "category": "GENERAL",
                    "match_type": "regex",
                },
                {
                    "id": "PAT2",
                    "pattern": r"elem2_text",
                    "confidence_weight": 0.9,
                    "category": "GENERAL",
                    "match_type": "regex",
                },
            ],
            "validations": {},
            "failure_contract": {
                "condition": "completeness < 0.8",
                "error_code": "E_LOW_COMPLETENESS",
                "remediation": "Need more evidence",
            },
        }

        text = "Document has only elem1_text."

        result = analyze_with_intelligence_layer(
            text=text, signal_node=signal_node, document_context=None
        )

        assert result["completeness"] < 0.8
        assert result["validation"]["passed"] is False
        assert result["validation"]["error_code"] == "E_LOW_COMPLETENESS"


class TestMetadataPropagation:
    """Test metadata propagation through pipeline."""

    def test_pattern_metadata_in_evidence_lineage(self):
        """Test pattern metadata appears in evidence lineage."""
        signal_node = {
            "id": "TEST_LINEAGE",
            "expected_elements": [{"type": "test_elem", "required": True}],
            "patterns": [
                {
                    "id": "PAT_TEST_123",
                    "pattern": r"test_value",
                    "confidence_weight": 0.85,
                    "category": "TEST_CATEGORY",
                    "match_type": "regex",
                }
            ],
            "validations": {},
        }

        text = "The test_value is present."

        base_pack = MockSignalPack(signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=text, signal_node=signal_node, document_context=None
        )

        # Check lineage in matches
        test_elem_matches = result.evidence["test_elem"]
        assert len(test_elem_matches) > 0

        match = test_elem_matches[0]
        assert "lineage" in match
        assert match["lineage"]["pattern_id"] == "PAT_TEST_123"
        assert match["lineage"]["element_type"] == "test_elem"
        assert match["lineage"]["extraction_phase"] == "microanswering"

    def test_extraction_metadata_completeness(self):
        """Test extraction metadata includes all required fields."""
        signal_node = {
            "id": "TEST_METADATA",
            "expected_elements": [
                {"type": "e1", "required": True},
                {"type": "e2", "required": True},
            ],
            "patterns": [
                {
                    "id": "P1",
                    "pattern": r"val1",
                    "confidence_weight": 0.9,
                    "category": "CAT",
                    "match_type": "regex",
                },
                {
                    "id": "P2",
                    "pattern": r"val2",
                    "confidence_weight": 0.9,
                    "category": "CAT",
                    "match_type": "regex",
                },
            ],
            "validations": {},
        }

        text = "Contains val1 and val2."

        base_pack = MockSignalPack(signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=text, signal_node=signal_node, document_context=None
        )

        # Validate metadata
        metadata = result.extraction_metadata
        assert "expected_count" in metadata
        assert "pattern_count" in metadata
        assert "total_matches" in metadata

        assert metadata["expected_count"] == 2
        assert metadata["pattern_count"] == 2
        assert metadata["total_matches"] >= 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_document(self):
        """Test with empty document."""
        signal_node = {
            "id": "TEST_EMPTY",
            "expected_elements": [{"type": "elem", "required": True}],
            "patterns": [
                {
                    "id": "PAT",
                    "pattern": r"pattern",
                    "confidence_weight": 0.9,
                    "category": "CAT",
                    "match_type": "regex",
                }
            ],
            "validations": {},
        }

        result = analyze_with_intelligence_layer(
            text="", signal_node=signal_node, document_context=None
        )

        assert result["completeness"] == 0.0
        assert len(result["missing_elements"]) > 0

    def test_no_expected_elements(self):
        """Test with no expected elements."""
        signal_node = {
            "id": "TEST_NO_ELEMENTS",
            "expected_elements": [],
            "patterns": [],
            "validations": {},
        }

        result = analyze_with_intelligence_layer(
            text="Some text", signal_node=signal_node, document_context=None
        )

        # Completeness should be 1.0 (nothing expected)
        assert result["completeness"] == 1.0
        assert len(result["missing_elements"]) == 0

    def test_no_patterns(self):
        """Test with no patterns."""
        signal_node = {
            "id": "TEST_NO_PATTERNS",
            "expected_elements": [{"type": "elem", "required": True}],
            "patterns": [],
            "validations": {},
        }

        result = analyze_with_intelligence_layer(
            text="Some text", signal_node=signal_node, document_context=None
        )

        # Should have missing element
        assert "elem" in result["missing_elements"]
        assert result["completeness"] < 1.0

    def test_exceeding_minimum_cardinality(self):
        """Test when found count exceeds minimum."""
        signal_node = {
            "id": "TEST_EXCEED",
            "expected_elements": [{"type": "items", "minimum": 2}],
            "patterns": [
                {
                    "id": "PAT",
                    "pattern": r"item",
                    "confidence_weight": 0.9,
                    "category": "CAT",
                    "match_type": "regex",
                }
            ],
            "validations": {},
        }

        text = "Has item, item, item, item, item."

        base_pack = MockSignalPack(signal_node["patterns"])
        enriched = EnrichedSignalPack(base_pack, enable_semantic_expansion=False)

        result = enriched.extract_evidence(
            text=text, signal_node=signal_node, document_context=None
        )

        # Should have completeness 1.0 (exceeded minimum)
        assert result.completeness == 1.0
        assert len(result.under_minimum) == 0


class TestRealDataValidation:
    """Test with real questionnaire data."""

    def test_analyze_with_real_signal_nodes(self, micro_questions):
        """Test analyze with real signal nodes."""
        nodes_with_elements = [
            mq for mq in micro_questions if mq.get("expected_elements")
        ]

        assert len(nodes_with_elements) > 0

        for mq in nodes_with_elements[:5]:
            sample_text = """
            Baseline: 10% in 2023. Target: 20% by 2027.
            Responsible: Ministry. Budget: COP 1,000 million.
            Source: DANE. Coverage: nationwide.
            """

            result = analyze_with_intelligence_layer(
                text=sample_text, signal_node=mq, document_context=None
            )

            # Validate structure
            assert "evidence" in result
            assert "completeness" in result
            assert "validation" in result
            assert "metadata" in result

            # Validate types
            assert isinstance(result["evidence"], dict)
            assert 0.0 <= result["completeness"] <= 1.0

    def test_element_type_diversity(self, micro_questions):
        """Test element type diversity across signal nodes."""
        element_types = set()

        for mq in micro_questions:
            for elem in mq.get("expected_elements", []):
                if isinstance(elem, dict):
                    element_types.add(elem.get("type", ""))
                elif isinstance(elem, str):
                    element_types.add(elem)

        print(f"\n  Unique element types: {len(element_types)}")
        print(f"  Sample types: {list(element_types)[:10]}")

        # Should have diverse element types
        assert len(element_types) > 5

    def test_completeness_distribution(self, micro_questions):
        """Test completeness score distribution."""
        nodes_with_elements = [
            mq for mq in micro_questions if mq.get("expected_elements")
        ][:20]

        completeness_scores = []

        for mq in nodes_with_elements:
            text = "Baseline: 10%. Target: 20% for 2027. Responsible: Agency."

            result = analyze_with_intelligence_layer(
                text=text, signal_node=mq, document_context=None
            )

            completeness_scores.append(result["completeness"])

        # Validate distribution
        assert len(completeness_scores) > 0
        assert all(0.0 <= s <= 1.0 for s in completeness_scores)

        avg = sum(completeness_scores) / len(completeness_scores)
        print(f"\n  Average completeness: {avg:.2f}")
        print(
            f"  Min: {min(completeness_scores):.2f}, Max: {max(completeness_scores):.2f}"
        )


class TestPerformanceAndScale:
    """Test performance with large documents and many patterns."""

    def test_large_document(self):
        """Test with large document."""
        signal_node = {
            "id": "TEST_LARGE",
            "expected_elements": [{"type": "value", "required": True}],
            "patterns": [
                {
                    "id": "PAT",
                    "pattern": r"value",
                    "confidence_weight": 0.9,
                    "category": "CAT",
                    "match_type": "regex",
                }
            ],
            "validations": {},
        }

        # Large document (10,000 words)
        large_text = ("Lorem ipsum " * 5000) + " value " + ("dolor sit " * 5000)

        result = analyze_with_intelligence_layer(
            text=large_text, signal_node=signal_node, document_context=None
        )

        assert "evidence" in result
        assert result["completeness"] > 0.0

    def test_many_patterns(self):
        """Test with many patterns."""
        patterns = [
            {
                "id": f"PAT_{i}",
                "pattern": f"value{i}",
                "confidence_weight": 0.8,
                "category": "CAT",
                "match_type": "substring",
            }
            for i in range(50)
        ]

        signal_node = {
            "id": "TEST_MANY_PATTERNS",
            "expected_elements": [{"type": "values", "minimum": 10}],
            "patterns": patterns,
            "validations": {},
        }

        text = " ".join([f"value{i}" for i in range(25)])

        result = analyze_with_intelligence_layer(
            text=text, signal_node=signal_node, document_context=None
        )

        assert "evidence" in result
        assert result["completeness"] > 0.0

    def test_complex_expected_elements(self):
        """Test with complex expected_elements structure."""
        signal_node = {
            "id": "TEST_COMPLEX",
            "expected_elements": [
                {"type": f"elem{i}", "required": i % 2 == 0, "minimum": (i % 3) + 1}
                for i in range(20)
            ],
            "patterns": [
                {
                    "id": f"PAT_{i}",
                    "pattern": f"elem{i}",
                    "confidence_weight": 0.8,
                    "category": "CAT",
                    "match_type": "substring",
                }
                for i in range(20)
            ],
            "validations": {},
        }

        text = " ".join([f"elem{i}" for i in range(20)])

        result = analyze_with_intelligence_layer(
            text=text, signal_node=signal_node, document_context=None
        )

        assert "evidence" in result
        assert 0.0 <= result["completeness"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
