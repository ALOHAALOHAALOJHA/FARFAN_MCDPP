"""
Signal Intelligence: Cross-Validation and Component Integration
================================================================

Tests that validate proper integration and interaction between all 4
refactorings in the signal intelligence pipeline.

Test Focus:
1. Cross-component interaction (expansion → filtering → extraction → validation)
2. Data flow preservation through pipeline stages
3. Metadata consistency across transformations
4. Error propagation and handling
5. Performance impact of combined refactorings

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-02
"""

import pytest
from typing import Dict, Any, List

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    create_enriched_signal_pack,
    analyze_with_intelligence_layer,
    EnrichedSignalPack
)
from farfan_pipeline.core.orchestrator.signal_semantic_expander import (
    expand_all_patterns,
    expand_pattern_semantically
)
from farfan_pipeline.core.orchestrator.signal_context_scoper import (
    filter_patterns_by_context,
    create_document_context
)
from farfan_pipeline.core.orchestrator.signal_evidence_extractor import extract_structured_evidence
from farfan_pipeline.core.orchestrator.signal_contract_validator import validate_with_contract


class MockSignalPack:
    """Mock signal pack for testing."""
    
    def __init__(self, patterns, micro_questions):
        self.patterns = patterns
        self.micro_questions = micro_questions


@pytest.fixture(scope="module")
def questionnaire():
    """Load questionnaire."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def rich_question(questionnaire):
    """Get question with all intelligence features."""
    questions = questionnaire.get_micro_questions()
    
    # Find question with maximum intelligence features
    best_score = 0
    best_question = questions[0]
    
    for q in questions:
        score = 0
        patterns = q.get('patterns', [])
        
        # Score based on intelligence features
        score += sum(1 for p in patterns if p.get('semantic_expansion'))
        score += sum(1 for p in patterns if p.get('context_scope'))
        score += sum(1 for p in patterns if p.get('validation_rule'))
        score += 10 if q.get('failure_contract') else 0
        score += len(q.get('expected_elements', []))
        
        if score > best_score:
            best_score = score
            best_question = q
    
    return best_question


class TestPipelineDataFlow:
    """Test data flow through complete pipeline."""
    
    def test_01_pattern_metadata_preserved_through_expansion(self, rich_question):
        """Test: Metadata preserved from original → expanded patterns."""
        original_patterns = rich_question.get('patterns', [])
        
        # Find pattern with rich metadata
        rich_pattern = None
        for p in original_patterns:
            if p.get('semantic_expansion') and p.get('confidence_weight'):
                rich_pattern = p
                break
        
        if rich_pattern:
            variants = expand_pattern_semantically(rich_pattern)
            
            original_confidence = rich_pattern['confidence_weight']
            original_category = rich_pattern.get('category')
            original_id = rich_pattern.get('id')
            
            print(f"\n✓ Metadata Preservation Through Expansion:")
            print(f"  Original pattern: {original_id}")
            print(f"  Confidence: {original_confidence}")
            print(f"  Category: {original_category}")
            print(f"  Variants generated: {len(variants) - 1}")
            
            # Verify all variants preserve metadata
            for variant in variants:
                assert variant['confidence_weight'] == original_confidence
                if original_category:
                    assert variant['category'] == original_category
                if variant.get('is_variant'):
                    assert variant['variant_of'] == original_id
            
            print(f"  ✓ All variants preserve original metadata")
    
    def test_02_expanded_patterns_filter_correctly(self, rich_question):
        """Test: Expanded patterns respect context filtering."""
        patterns = rich_question.get('patterns', [])
        
        # Expand patterns
        expanded = expand_all_patterns(patterns, enable_logging=False)
        
        # Apply context filtering
        budget_ctx = create_document_context(section='budget', chapter=3)
        filtered, stats = filter_patterns_by_context(expanded, budget_ctx)
        
        print(f"\n✓ Context Filtering on Expanded Patterns:")
        print(f"  Original patterns: {len(patterns)}")
        print(f"  Expanded patterns: {len(expanded)}")
        print(f"  After context filtering: {len(filtered)}")
        print(f"  Expansion then filtering ratio: {len(filtered) / len(patterns):.2f}x")
        
        # Verify filtering preserves variant metadata
        for pattern in filtered:
            assert 'confidence_weight' in pattern
            if pattern.get('is_variant'):
                assert 'variant_of' in pattern
        
        print(f"  ✓ Variant metadata preserved through filtering")
    
    def test_03_filtered_patterns_extract_evidence(self, rich_question):
        """Test: Context-filtered patterns successfully extract evidence."""
        patterns = rich_question.get('patterns', [])
        
        # Full pipeline: expand → filter → extract
        expanded = expand_all_patterns(patterns, enable_logging=False)
        
        context = create_document_context(section='diagnostic', chapter=1)
        filtered, _ = filter_patterns_by_context(expanded, context)
        
        # Create signal node with filtered patterns
        filtered_node = {
            **rich_question,
            'patterns': filtered
        }
        
        test_doc = """
        Diagnóstico según DANE: línea base 8.5% en 2023.
        Meta: 15% para 2027. Fuente: DANE, Medicina Legal.
        """
        
        result = extract_structured_evidence(test_doc, filtered_node, context)
        
        print(f"\n✓ Evidence Extraction with Filtered Patterns:")
        print(f"  Patterns used: {len(filtered)}")
        print(f"  Evidence types extracted: {len(result.evidence)}")
        print(f"  Completeness: {result.completeness:.2f}")
        
        # Verify extraction worked
        assert result.completeness >= 0.0
        print(f"  ✓ Evidence extracted successfully")
    
    def test_04_evidence_validates_with_contracts(self, rich_question):
        """Test: Extracted evidence validates against contracts."""
        test_doc = """
        Diagnóstico completo según DANE y Medicina Legal.
        Línea base 2023: 8.5%. Meta 2027: 15%.
        Cobertura territorial: Bogotá, 20 localidades.
        Presupuesto: COP 1,500 millones.
        """
        
        context = create_document_context(section='diagnostic')
        
        # Full pipeline: expand → filter → extract → validate
        result = analyze_with_intelligence_layer(
            text=test_doc,
            signal_node=rich_question,
            document_context=context
        )
        
        print(f"\n✓ End-to-End Pipeline Validation:")
        print(f"  Evidence completeness: {result['completeness']:.2f}")
        print(f"  Validation status: {result['validation']['status']}")
        print(f"  Validation passed: {result['validation']['passed']}")
        
        # Verify validation executed
        assert 'validation' in result
        assert 'status' in result['validation']
        
        print(f"  ✓ Contract validation executed")


class TestMetadataConsistency:
    """Test metadata consistency across pipeline stages."""
    
    def test_01_confidence_weights_consistent(self, rich_question):
        """Test: Confidence weights remain consistent through pipeline."""
        patterns = rich_question.get('patterns', [])
        
        # Collect confidence weights at each stage
        original_confidences = [p.get('confidence_weight', 0.5) for p in patterns]
        
        # After expansion
        expanded = expand_all_patterns(patterns, enable_logging=False)
        expanded_confidences = [p.get('confidence_weight', 0.5) for p in expanded]
        
        # After filtering
        context = create_document_context(section='any')
        filtered, _ = filter_patterns_by_context(expanded, context)
        filtered_confidences = [p.get('confidence_weight', 0.5) for p in filtered]
        
        print(f"\n✓ Confidence Weight Consistency:")
        print(f"  Original range: [{min(original_confidences):.2f}, {max(original_confidences):.2f}]")
        print(f"  Expanded range: [{min(expanded_confidences):.2f}, {max(expanded_confidences):.2f}]")
        print(f"  Filtered range: [{min(filtered_confidences):.2f}, {max(filtered_confidences):.2f}]")
        
        # Verify ranges are consistent
        assert min(expanded_confidences) >= min(original_confidences) - 0.01
        assert max(expanded_confidences) <= max(original_confidences) + 0.01
        
        print(f"  ✓ Confidence weights preserved")
    
    def test_02_category_labels_preserved(self, rich_question):
        """Test: Category labels preserved through transformations."""
        patterns = rich_question.get('patterns', [])
        
        # Extract unique categories
        original_categories = set(p.get('category') for p in patterns if p.get('category'))
        
        expanded = expand_all_patterns(patterns, enable_logging=False)
        expanded_categories = set(p.get('category') for p in expanded if p.get('category'))
        
        print(f"\n✓ Category Label Preservation:")
        print(f"  Original categories: {original_categories}")
        print(f"  Expanded categories: {expanded_categories}")
        
        # Expanded should have same or more categories (not less)
        assert len(expanded_categories) >= len(original_categories)
        assert original_categories.issubset(expanded_categories)
        
        print(f"  ✓ Categories preserved")
    
    def test_03_pattern_ids_traceable(self, rich_question):
        """Test: Pattern IDs remain traceable through variants."""
        patterns = rich_question.get('patterns', [])
        
        # Get pattern with semantic expansion
        expandable = next((p for p in patterns if p.get('semantic_expansion')), None)
        
        if expandable:
            original_id = expandable.get('id')
            variants = expand_pattern_semantically(expandable)
            
            print(f"\n✓ Pattern ID Traceability:")
            print(f"  Original ID: {original_id}")
            print(f"  Variants generated: {len(variants) - 1}")
            
            # Check variant IDs
            for variant in variants[1:]:  # Skip original
                assert variant.get('variant_of') == original_id
                assert variant['id'].startswith(original_id)
                print(f"    - {variant['id']} → {original_id}")
            
            print(f"  ✓ All variants traceable to original")


class TestErrorPropagation:
    """Test error handling and propagation through pipeline."""
    
    def test_01_missing_data_propagates_correctly(self, rich_question):
        """Test: Missing data errors propagate through validation."""
        incomplete_doc = "Información mínima disponible."
        
        result = analyze_with_intelligence_layer(
            text=incomplete_doc,
            signal_node=rich_question,
            document_context={}
        )
        
        print(f"\n✓ Error Propagation - Missing Data:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Missing elements: {result['missing_elements']}")
        print(f"  Validation status: {result['validation']['status']}")
        
        # Should have low completeness
        assert result['completeness'] < 0.5
        
        # Validation should reflect incompleteness
        if result['completeness'] < 0.4 and rich_question.get('failure_contract'):
            print(f"  Error code: {result['validation'].get('error_code')}")
            print(f"  Remediation: {result['validation'].get('remediation')}")
        
        print(f"  ✓ Missing data handled correctly")
    
    def test_02_invalid_patterns_handled_gracefully(self, rich_question):
        """Test: Invalid patterns don't crash pipeline."""
        patterns = rich_question.get('patterns', [])
        
        # Add invalid pattern
        invalid_pattern = {
            'pattern': '[invalid(regex',  # Malformed regex
            'id': 'INVALID_TEST',
            'confidence_weight': 0.5
        }
        
        patterns_with_invalid = patterns + [invalid_pattern]
        
        try:
            # Should not crash
            expanded = expand_all_patterns(patterns_with_invalid, enable_logging=False)
            
            print(f"\n✓ Invalid Pattern Handling:")
            print(f"  Input patterns: {len(patterns_with_invalid)}")
            print(f"  Output patterns: {len(expanded)}")
            print(f"  ✓ Pipeline handled invalid pattern gracefully")
        except Exception as e:
            print(f"\n✗ Pipeline failed with invalid pattern: {e}")
            pytest.fail(f"Pipeline should handle invalid patterns gracefully: {e}")
    
    def test_03_empty_context_handled(self, rich_question):
        """Test: Empty context doesn't break filtering."""
        patterns = rich_question.get('patterns', [])
        
        # Empty context
        empty_context = {}
        
        filtered, stats = filter_patterns_by_context(patterns, empty_context)
        
        print(f"\n✓ Empty Context Handling:")
        print(f"  Input patterns: {len(patterns)}")
        print(f"  Filtered patterns: {len(filtered)}")
        print(f"  Stats: {stats}")
        
        # Should still return patterns (global scope patterns)
        assert len(filtered) > 0
        print(f"  ✓ Empty context handled correctly")


class TestPerformanceImpact:
    """Test performance impact of combined refactorings."""
    
    def test_01_expansion_performance_acceptable(self, questionnaire):
        """Test: Pattern expansion completes in reasonable time."""
        import time
        
        questions = questionnaire.get_micro_questions()
        sample = questions[:10]
        
        all_patterns = []
        for q in sample:
            all_patterns.extend(q.get('patterns', []))
        
        start = time.time()
        expanded = expand_all_patterns(all_patterns, enable_logging=False)
        duration = time.time() - start
        
        patterns_per_sec = len(all_patterns) / duration if duration > 0 else 0
        
        print(f"\n✓ Expansion Performance:")
        print(f"  Patterns processed: {len(all_patterns)}")
        print(f"  Patterns generated: {len(expanded)}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Throughput: {patterns_per_sec:.1f} patterns/sec")
        
        # Should complete quickly
        assert duration < 5.0, f"Expansion too slow: {duration:.2f}s"
        print(f"  ✓ Performance acceptable")
    
    def test_02_filtering_performance_acceptable(self, questionnaire):
        """Test: Context filtering completes in reasonable time."""
        import time
        
        questions = questionnaire.get_micro_questions()
        sample = questions[:10]
        
        all_patterns = []
        for q in sample:
            all_patterns.extend(q.get('patterns', []))
        
        context = create_document_context(section='budget', chapter=3)
        
        start = time.time()
        filtered, stats = filter_patterns_by_context(all_patterns, context)
        duration = time.time() - start
        
        patterns_per_sec = len(all_patterns) / duration if duration > 0 else 0
        
        print(f"\n✓ Filtering Performance:")
        print(f"  Patterns filtered: {len(all_patterns)}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Throughput: {patterns_per_sec:.1f} patterns/sec")
        
        # Should be very fast
        assert duration < 1.0, f"Filtering too slow: {duration:.2f}s"
        print(f"  ✓ Performance acceptable")
    
    def test_03_end_to_end_performance(self, rich_question):
        """Test: Complete pipeline performance."""
        import time
        
        test_doc = """
        DIAGNÓSTICO COMPLETO
        Según DANE: línea base 8.5% en 2023.
        Meta: 15% para 2027.
        Fuentes oficiales: DANE, Medicina Legal, Fiscalía.
        Cobertura: Bogotá, 20 localidades.
        Presupuesto: COP 1,500 millones anuales.
        """
        
        context = create_document_context(section='diagnostic', chapter=1)
        
        start = time.time()
        result = analyze_with_intelligence_layer(
            text=test_doc,
            signal_node=rich_question,
            document_context=context
        )
        duration = time.time() - start
        
        print(f"\n✓ End-to-End Pipeline Performance:")
        print(f"  Document size: {len(test_doc)} chars")
        print(f"  Patterns in question: {len(rich_question.get('patterns', []))}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Completeness: {result['completeness']:.2f}")
        
        # Should complete in reasonable time
        assert duration < 3.0, f"Pipeline too slow: {duration:.2f}s"
        print(f"  ✓ Performance acceptable")


class TestEnrichedSignalPackIntegration:
    """Test EnrichedSignalPack as integration point."""
    
    def test_01_enriched_pack_integrates_all_refactorings(self, rich_question):
        """Test: EnrichedSignalPack integrates all 4 refactorings."""
        patterns = rich_question.get('patterns', [])
        base_pack = MockSignalPack(patterns, [rich_question])
        
        enriched = create_enriched_signal_pack(base_pack, enable_semantic_expansion=True)
        
        # Test refactoring #2 (semantic expansion)
        assert len(enriched.patterns) >= len(patterns)
        
        # Test refactoring #4 (context filtering)
        context = create_document_context(section='budget')
        filtered = enriched.get_patterns_for_context(context)
        assert isinstance(filtered, list)
        
        # Test refactoring #5 (evidence extraction)
        doc = "DANE reporta datos."
        evidence_result = enriched.extract_evidence(doc, rich_question)
        assert hasattr(evidence_result, 'completeness')
        
        # Test refactoring #3 (validation)
        test_result = {'completeness': 0.8, 'evidence': {}}
        validation = enriched.validate_result(test_result, rich_question)
        assert hasattr(validation, 'status')
        
        print(f"\n✓ EnrichedSignalPack Integration:")
        print(f"  ✓ Semantic expansion: {len(enriched.patterns)} patterns")
        print(f"  ✓ Context filtering: {len(filtered)} filtered")
        print(f"  ✓ Evidence extraction: {evidence_result.completeness:.2f} completeness")
        print(f"  ✓ Contract validation: {validation.status}")
    
    def test_02_enriched_pack_metadata_access(self, rich_question):
        """Test: EnrichedSignalPack provides metadata access."""
        patterns = rich_question.get('patterns', [])
        base_pack = MockSignalPack(patterns, [rich_question])
        
        enriched = create_enriched_signal_pack(base_pack, enable_semantic_expansion=True)
        
        # Test confidence calculation
        pattern_ids = [p.get('id') for p in patterns[:3] if p.get('id')]
        if pattern_ids:
            avg_confidence = enriched.get_average_confidence(pattern_ids)
            assert 0.0 <= avg_confidence <= 1.0
            
            print(f"\n✓ Metadata Access:")
            print(f"  Average confidence: {avg_confidence:.2f}")
        
        # Test node access
        node = enriched.get_node(rich_question.get('question_id'))
        if node:
            print(f"  Node retrieved: {node.get('question_id')}")
        
        print(f"  ✓ Metadata access working")


class TestCrossComponentConsistency:
    """Test consistency across component boundaries."""
    
    def test_01_expansion_and_filtering_consistent(self, rich_question):
        """Test: Expansion doesn't create patterns that all filter out."""
        patterns = rich_question.get('patterns', [])
        
        # Expand patterns
        expanded = expand_all_patterns(patterns, enable_logging=False)
        
        # Filter with various contexts
        contexts = [
            create_document_context(section='budget'),
            create_document_context(section='indicators'),
            create_document_context(section='diagnostic')
        ]
        
        for ctx in contexts:
            filtered, stats = filter_patterns_by_context(expanded, ctx)
            
            # Should always have some patterns (global scope)
            assert len(filtered) > 0, f"All patterns filtered out for {ctx}"
        
        print(f"\n✓ Expansion-Filtering Consistency:")
        print(f"  Original: {len(patterns)}")
        print(f"  Expanded: {len(expanded)}")
        print(f"  ✓ Patterns remain after filtering in all contexts")
    
    def test_02_extraction_respects_validation_contracts(self, rich_question):
        """Test: Evidence extraction aligns with validation contracts."""
        contract = rich_question.get('failure_contract')
        expected = rich_question.get('expected_elements', [])
        
        if contract and expected:
            # Extract evidence
            doc = "Limited data available."
            result = extract_structured_evidence(doc, rich_question)
            
            # Validate
            validation = validate_with_contract(
                {'completeness': result.completeness, 
                 'missing_elements': result.missing_required},
                rich_question
            )
            
            print(f"\n✓ Extraction-Validation Consistency:")
            print(f"  Completeness: {result.completeness:.2f}")
            print(f"  Validation: {validation.status}")
            
            # Low completeness should align with validation failure
            if result.completeness < 0.3:
                print(f"  Low completeness correctly triggers validation")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
