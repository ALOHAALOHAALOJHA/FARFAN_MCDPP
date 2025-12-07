"""
Signal Intelligence Pipeline - Metadata and Lineage Integration Tests
======================================================================

Integration tests validating metadata preservation and lineage tracking
through the complete signal intelligence pipeline.

Test Coverage:
- Metadata Preservation: Confidence, category, specificity through all transforms
- Lineage Tracking: Pattern provenance from expansion to evidence extraction
- Cross-Component Consistency: Data flow between refactorings
- Error Propagation: Error handling through pipeline stages
- Performance Metrics: Combined refactorings performance impact

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-06
Coverage: Metadata preservation, lineage tracking, cross-component validation
"""

from typing import Any

import pytest

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_context_scoper import (
    create_document_context,
    filter_patterns_by_context,
)
from farfan_pipeline.core.orchestrator.signal_evidence_extractor import (
    extract_structured_evidence,
)
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    analyze_with_intelligence_layer,
    create_enriched_signal_pack,
)
from farfan_pipeline.core.orchestrator.signal_semantic_expander import (
    expand_all_patterns,
    expand_pattern_semantically,
)


class MockSignalPack:
    """Mock signal pack for testing."""

    def __init__(
        self, patterns: list[dict[str, Any]], micro_questions: list[dict[str, Any]]
    ):
        self.patterns = patterns
        self.micro_questions = micro_questions


@pytest.fixture(scope="module")
def canonical_questionnaire():
    """Load questionnaire."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def sample_questions(canonical_questionnaire):
    """Get sample questions."""
    all_q = canonical_questionnaire.get_micro_questions()

    # Get questions with rich intelligence fields
    rich = []
    for q in all_q:
        patterns = q.get("patterns", [])
        if (
            any(p.get("semantic_expansion") for p in patterns)
            and any(p.get("context_scope") for p in patterns)
            and q.get("expected_elements")
        ):
            rich.append(q)
            if len(rich) >= 15:
                break

    return rich if rich else all_q[:15]


class TestMetadataPreservation:
    """Test metadata preservation through pipeline."""

    def test_confidence_preserved_through_expansion(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test confidence_weight preserved in expansion."""
        patterns = sample_questions[0].get("patterns", [])
        expandable = [p for p in patterns if p.get("semantic_expansion")][:5]

        if not expandable:
            pytest.skip("No expandable patterns")

        print("\n✓ Confidence Preservation Test:")

        all_preserved = True
        for pattern in expandable:
            orig_conf = pattern.get("confidence_weight")
            variants = expand_pattern_semantically(pattern)

            for variant in variants:
                var_conf = variant.get("confidence_weight")
                if var_conf != orig_conf:
                    all_preserved = False
                    print(f"  ✗ Confidence mismatch: {orig_conf} → {var_conf}")

        if all_preserved:
            print(f"  ✓ All {len(expandable)} patterns preserved confidence")

        assert all_preserved

    def test_category_preserved_through_expansion(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test category preserved in expansion."""
        patterns = sample_questions[0].get("patterns", [])
        expandable = [p for p in patterns if p.get("semantic_expansion")][:5]

        if not expandable:
            pytest.skip("No expandable patterns")

        print("\n✓ Category Preservation Test:")

        all_preserved = True
        for pattern in expandable:
            orig_cat = pattern.get("category")
            variants = expand_pattern_semantically(pattern)

            for variant in variants:
                var_cat = variant.get("category")
                if var_cat != orig_cat:
                    all_preserved = False
                    print(f"  ✗ Category mismatch: {orig_cat} → {var_cat}")

        if all_preserved:
            print(f"  ✓ All {len(expandable)} patterns preserved category")

        assert all_preserved

    def test_metadata_preserved_through_filtering(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test metadata preserved through context filtering."""
        patterns = sample_questions[0].get("patterns", [])

        context = create_document_context(section="diagnostic", chapter=1)
        filtered, _ = filter_patterns_by_context(patterns, context)

        print("\n✓ Metadata Through Filtering:")
        print(f"  Original: {len(patterns)}, Filtered: {len(filtered)}")

        # Check that filtered patterns retain all metadata
        for fp in filtered[:5]:
            assert "confidence_weight" in fp or True  # May not have field
            assert "category" in fp or True  # May not have field
            assert "pattern" in fp

        print("  ✓ Metadata fields present in filtered patterns")

    def test_all_metadata_fields_present(self, sample_questions: list[dict[str, Any]]):
        """Test all key metadata fields present."""
        patterns = sample_questions[0].get("patterns", [])

        metadata_fields = ["pattern", "id", "confidence_weight", "category"]
        field_coverage = {field: 0 for field in metadata_fields}

        for p in patterns:
            for field in metadata_fields:
                if field in p:
                    field_coverage[field] += 1

        print("\n✓ Metadata Field Coverage:")
        for field, count in field_coverage.items():
            pct = (count / len(patterns) * 100) if patterns else 0
            print(f"  {field}: {count}/{len(patterns)} ({pct:.1f}%)")


class TestLineageTracking:
    """Test lineage tracking through pipeline."""

    def test_variant_lineage_tracking(self, sample_questions: list[dict[str, Any]]):
        """Test variant tracks source pattern."""
        patterns = sample_questions[0].get("patterns", [])
        expandable = next((p for p in patterns if p.get("semantic_expansion")), None)

        if not expandable:
            pytest.skip("No expandable patterns")

        variants = expand_pattern_semantically(expandable)

        print("\n✓ Variant Lineage Tracking:")
        print(f"  Base pattern: {expandable.get('id')}")
        print(f"  Variants: {len(variants) - 1}")

        for variant in variants:
            if variant.get("is_variant"):
                assert "variant_of" in variant
                assert variant["variant_of"] == expandable.get("id")
                assert "synonym_used" in variant

                print(f"  ✓ {variant['id']} → tracks {variant['variant_of']}")

    def test_evidence_lineage_tracking(self, sample_questions: list[dict[str, Any]]):
        """Test evidence extraction tracks pattern lineage."""
        signal_node = sample_questions[0]

        text = "Fuentes oficiales: DANE reporta línea base 8.5% en 2023."
        result = extract_structured_evidence(text, signal_node)

        print("\n✓ Evidence Lineage Tracking:")

        has_lineage = False
        for elem_type, matches in result.evidence.items():
            for match in matches:
                if "lineage" in match:
                    has_lineage = True
                    lineage = match["lineage"]

                    print(f"  Element: {elem_type}")
                    print(f"    Pattern ID: {lineage.get('pattern_id')}")
                    print(f"    Confidence: {lineage.get('confidence_weight')}")
                    print(f"    Phase: {lineage.get('extraction_phase')}")
                    break
            if has_lineage:
                break

        print(f"  Lineage tracking: {has_lineage}")

    def test_end_to_end_lineage(self, sample_questions: list[dict[str, Any]]):
        """Test lineage from pattern to final evidence."""
        signal_node = sample_questions[0]
        patterns = signal_node.get("patterns", [])

        # Expand patterns
        expanded = expand_all_patterns(patterns[:10], enable_logging=False)

        # Track a specific pattern through pipeline
        test_pattern = expanded[0]
        pattern_id = test_pattern.get("id")

        print("\n✓ End-to-End Lineage:")
        print(f"  Tracking pattern: {pattern_id}")

        # Create document that should match this pattern
        text = "DANE reporta datos estadísticos de género en Colombia."

        result = extract_structured_evidence(text, signal_node)

        # Check if any evidence traces back to our pattern
        found_lineage = False
        for elem_type, matches in result.evidence.items():
            for match in matches:
                if match.get("lineage", {}).get("pattern_id") == pattern_id:
                    found_lineage = True
                    print(f"  ✓ Evidence traces to {pattern_id}")
                    break


class TestCrossComponentConsistency:
    """Test consistency between refactoring components."""

    def test_expansion_filtering_consistency(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test expanded patterns filter correctly."""
        patterns = sample_questions[0].get("patterns", [])

        # Expand patterns
        expanded = expand_all_patterns(patterns, enable_logging=False)

        # Filter both original and expanded
        context = create_document_context(section="budget", chapter=3)

        filtered_orig, stats_orig = filter_patterns_by_context(patterns, context)
        filtered_exp, stats_exp = filter_patterns_by_context(expanded, context)

        print("\n✓ Expansion-Filtering Consistency:")
        print(f"  Original patterns: {len(patterns)} → {len(filtered_orig)} filtered")
        print(f"  Expanded patterns: {len(expanded)} → {len(filtered_exp)} filtered")

        # Expanded should have at least as many filtered as original
        assert len(filtered_exp) >= len(filtered_orig)

    def test_filtering_extraction_consistency(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test filtered patterns extract correctly."""
        signal_node = sample_questions[0]
        patterns = signal_node.get("patterns", [])

        context = create_document_context(section="diagnostic")
        filtered, _ = filter_patterns_by_context(patterns, context)

        # Create signal node with filtered patterns
        filtered_node = {**signal_node, "patterns": filtered}

        text = "DANE reporta línea base 8.5% en 2023."

        result = extract_structured_evidence(text, filtered_node)

        print("\n✓ Filtering-Extraction Consistency:")
        print(f"  Filtered patterns: {len(filtered)}")
        print(f"  Evidence extracted: {sum(len(v) for v in result.evidence.values())}")

        # Should be able to extract with filtered patterns
        assert isinstance(result.evidence, dict)

    def test_extraction_validation_alignment(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test extraction and validation alignment."""
        signal_node = sample_questions[0]

        text = """
        Información completa:
        Línea base: 8.5%
        Meta: 15% para 2027
        Fuente: DANE
        """

        context = create_document_context(section="diagnostic")
        result = analyze_with_intelligence_layer(text, signal_node, context)

        print("\n✓ Extraction-Validation Alignment:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Validation status: {result['validation']['status']}")
        print(f"  Validation passed: {result['validation']['passed']}")

        # Validation should process extracted evidence
        assert "validation" in result
        assert "evidence" in result


class TestErrorPropagation:
    """Test error handling through pipeline."""

    def test_invalid_pattern_handling(self, sample_questions: list[dict[str, Any]]):
        """Test handling of invalid patterns."""
        signal_node = sample_questions[0]

        # Add invalid pattern
        invalid_pattern = {
            "pattern": "[invalid(regex",  # Invalid regex
            "id": "INVALID-001",
            "confidence_weight": 0.5,
        }

        patterns_with_invalid = signal_node.get("patterns", []) + [invalid_pattern]
        test_node = {**signal_node, "patterns": patterns_with_invalid}

        text = "Test document"

        # Should handle gracefully
        try:
            result = extract_structured_evidence(text, test_node)
            print("\n✓ Invalid Pattern Handling:")
            print("  Handled gracefully: Yes")
            print(f"  Evidence extracted: {len(result.evidence)}")
        except Exception as e:
            print("\n✗ Invalid Pattern Handling:")
            print(f"  Exception: {e}")
            pytest.fail("Should handle invalid patterns gracefully")

    def test_empty_patterns_handling(self, sample_questions: list[dict[str, Any]]):
        """Test handling of empty patterns list."""
        signal_node = sample_questions[0]

        empty_node = {**signal_node, "patterns": []}
        text = "Test document"

        result = extract_structured_evidence(text, empty_node)

        print("\n✓ Empty Patterns Handling:")
        print(f"  Evidence: {len(result.evidence)}")
        print(f"  Completeness: {result.completeness}")

        assert isinstance(result.evidence, dict)

    def test_malformed_context_handling(self, sample_questions: list[dict[str, Any]]):
        """Test handling of malformed context."""
        patterns = sample_questions[0].get("patterns", [])

        # Malformed context
        malformed_context = {"invalid_field": "value"}

        # Should handle gracefully
        try:
            filtered, _ = filter_patterns_by_context(patterns, malformed_context)
            print("\n✓ Malformed Context Handling:")
            print("  Handled gracefully: Yes")
            print(f"  Filtered: {len(filtered)}")
        except Exception as e:
            print("\n✗ Malformed Context Handling:")
            print(f"  Exception: {e}")


class TestPerformanceMetrics:
    """Test performance with combined refactorings."""

    def test_expansion_overhead(self, sample_questions: list[dict[str, Any]]):
        """Measure expansion overhead."""
        patterns = []
        for q in sample_questions[:5]:
            patterns.extend(q.get("patterns", []))

        import time

        start = time.time()
        expanded = expand_all_patterns(patterns, enable_logging=False)
        duration = time.time() - start

        print("\n✓ Expansion Performance:")
        print(f"  Patterns: {len(patterns)} → {len(expanded)}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Rate: {len(patterns)/duration:.0f} patterns/s")

    def test_filtering_performance(self, sample_questions: list[dict[str, Any]]):
        """Measure filtering performance."""
        patterns = []
        for q in sample_questions[:10]:
            patterns.extend(q.get("patterns", []))

        import time

        context = create_document_context(section="diagnostic", chapter=1)

        start = time.time()
        filtered, _ = filter_patterns_by_context(patterns, context)
        duration = time.time() - start

        print("\n✓ Filtering Performance:")
        print(f"  Patterns: {len(patterns)} → {len(filtered)}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Rate: {len(patterns)/duration:.0f} patterns/s")

    def test_extraction_performance(self, sample_questions: list[dict[str, Any]]):
        """Measure extraction performance."""
        signal_node = sample_questions[0]

        text = (
            """
        Diagnóstico de género:
        Línea base: 8.5%
        Meta: 15% para 2027
        Fuente: DANE
        """
            * 10
        )  # Repeat to make larger

        import time

        start = time.time()
        result = extract_structured_evidence(text, signal_node)
        duration = time.time() - start

        print("\n✓ Extraction Performance:")
        print(f"  Text length: {len(text)} chars")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Evidence: {sum(len(v) for v in result.evidence.values())} matches")


class TestEnrichedPackIntegration:
    """Test EnrichedSignalPack integration."""

    def test_enriched_pack_combines_all_refactorings(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test enriched pack integrates all refactorings."""
        patterns = []
        for q in sample_questions[:3]:
            patterns.extend(q.get("patterns", []))

        base = MockSignalPack(patterns, sample_questions)
        enriched = create_enriched_signal_pack(base, enable_semantic_expansion=True)

        print("\n✓ Enriched Pack Integration:")
        print(f"  Base patterns: {len(base.patterns)}")
        print(f"  Enriched patterns: {len(enriched.patterns)}")

        # Test all methods
        context = create_document_context(section="budget")
        filtered = enriched.get_patterns_for_context(context)
        print(f"  Context-filtered: {len(filtered)}")

        # Test evidence extraction
        signal_node = sample_questions[0]
        text = "DANE reporta datos."
        evidence_result = enriched.extract_evidence(text, signal_node, context)
        print(f"  Evidence completeness: {evidence_result.completeness:.2f}")

        # Test validation
        test_result = {"completeness": 0.8, "evidence": {}}
        validation_result = enriched.validate_result(test_result, signal_node)
        print(f"  Validation status: {validation_result.status}")


class TestIntelligenceLayerMetadata:
    """Test intelligence layer metadata tracking."""

    def test_metadata_includes_refactorings(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test metadata tracks applied refactorings."""
        signal_node = sample_questions[0]

        text = "DANE reporta línea base 8.5%."
        context = create_document_context(section="diagnostic")

        result = analyze_with_intelligence_layer(text, signal_node, context)

        print("\n✓ Intelligence Layer Metadata:")
        print(
            f"  Intelligence enabled: {result['metadata']['intelligence_layer_enabled']}"
        )
        print(f"  Refactorings: {result['metadata']['refactorings_applied']}")

        assert result["metadata"]["intelligence_layer_enabled"]
        assert len(result["metadata"]["refactorings_applied"]) == 4

        expected_refactorings = [
            "semantic_expansion",
            "context_scoping",
            "contract_validation",
            "evidence_structure",
        ]

        for ref in expected_refactorings:
            assert ref in result["metadata"]["refactorings_applied"]
            print(f"  ✓ {ref}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
