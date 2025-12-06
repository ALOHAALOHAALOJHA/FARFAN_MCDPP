"""
Signal Intelligence: 91% Intelligence Unlock Metrics
=====================================================

Comprehensive metrics validation for the signal intelligence pipeline,
verifying the 91% intelligence unlock claim across all 4 refactorings.

Metrics Measured:
1. Refactoring #2 (Semantic Expansion): Pattern multiplier (target: 5x)
2. Refactoring #4 (Context Scoping): Precision improvement (target: +60%)
3. Refactoring #3 (Contract Validation): Coverage (target: 100% of questions)
4. Refactoring #5 (Evidence Structure): Completeness accuracy (target: measurable)

Intelligence Unlock Definition:
- Baseline: Patterns used as simple strings without metadata
- Enhanced: Full utilization of semantic_expansion, context_scope, 
  failure_contract, expected_elements, and validation_rule fields
- Target: 91% of available intelligence fields actively utilized

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-02
"""

import pytest
import statistics
from typing import Dict, Any, List
from collections import defaultdict

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_semantic_expander import expand_all_patterns
from farfan_pipeline.core.orchestrator.signal_context_scoper import (
    filter_patterns_by_context,
    create_document_context
)
from farfan_pipeline.core.orchestrator.signal_evidence_extractor import extract_structured_evidence
from farfan_pipeline.core.orchestrator.signal_contract_validator import validate_with_contract


@pytest.fixture(scope="module")
def questionnaire():
    """Load questionnaire for metrics calculation."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def all_micro_questions(questionnaire):
    """Get all micro questions."""
    return questionnaire.get_micro_questions()


class TestRefactoring2SemanticExpansion:
    """Metrics for Refactoring #2: Semantic Expansion."""
    
    def test_01_semantic_expansion_coverage(self, all_micro_questions):
        """Measure: Percentage of patterns with semantic_expansion field."""
        total_patterns = 0
        patterns_with_expansion = 0
        expansion_field_types = defaultdict(int)
        
        for q in all_micro_questions:
            for p in q.get('patterns', []):
                total_patterns += 1
                expansion = p.get('semantic_expansion')
                
                if expansion:
                    patterns_with_expansion += 1
                    if isinstance(expansion, str):
                        expansion_field_types['string'] += 1
                    elif isinstance(expansion, dict):
                        expansion_field_types['dict'] += 1
                    else:
                        expansion_field_types['other'] += 1
        
        coverage = (patterns_with_expansion / total_patterns * 100) if total_patterns > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"REFACTORING #2: SEMANTIC EXPANSION METRICS")
        print(f"{'='*70}")
        print(f"Total patterns analyzed: {total_patterns}")
        print(f"Patterns with semantic_expansion: {patterns_with_expansion}")
        print(f"Coverage: {coverage:.2f}%")
        print(f"\nExpansion field types:")
        for field_type, count in expansion_field_types.items():
            pct = (count / patterns_with_expansion * 100) if patterns_with_expansion > 0 else 0
            print(f"  - {field_type}: {count} ({pct:.1f}%)")
        
        # Store for final report
        return {
            'total_patterns': total_patterns,
            'patterns_with_expansion': patterns_with_expansion,
            'coverage_pct': coverage
        }
    
    def test_02_pattern_expansion_multiplier(self, all_micro_questions):
        """Measure: Actual pattern expansion multiplier (target: 5x)."""
        # Sample to avoid excessive computation
        sample_size = min(50, len(all_micro_questions))
        sample = all_micro_questions[:sample_size]
        
        original_counts = []
        expanded_counts = []
        multipliers = []
        
        for q in sample:
            patterns = q.get('patterns', [])
            if not patterns:
                continue
            
            original = len(patterns)
            expanded = expand_all_patterns(patterns, enable_logging=False)
            expanded_count = len(expanded)
            
            original_counts.append(original)
            expanded_counts.append(expanded_count)
            
            if original > 0:
                multipliers.append(expanded_count / original)
        
        total_original = sum(original_counts)
        total_expanded = sum(expanded_counts)
        avg_multiplier = statistics.mean(multipliers) if multipliers else 1.0
        median_multiplier = statistics.median(multipliers) if multipliers else 1.0
        
        print(f"\n{'='*70}")
        print(f"PATTERN EXPANSION MULTIPLIER")
        print(f"{'='*70}")
        print(f"Sample size: {sample_size} questions")
        print(f"Total original patterns: {total_original}")
        print(f"Total expanded patterns: {total_expanded}")
        print(f"Aggregate multiplier: {total_expanded / total_original:.2f}x" if total_original > 0 else "N/A")
        print(f"Average multiplier per question: {avg_multiplier:.2f}x")
        print(f"Median multiplier: {median_multiplier:.2f}x")
        print(f"Additional patterns generated: {total_expanded - total_original}")
        print(f"\nTarget multiplier: 5x")
        print(f"Achievement: {(avg_multiplier / 5.0 * 100):.1f}% of target")
        
        return {
            'avg_multiplier': avg_multiplier,
            'aggregate_multiplier': total_expanded / total_original if total_original > 0 else 1.0,
            'total_generated': total_expanded - total_original
        }
    
    def test_03_expansion_quality_metrics(self, all_micro_questions):
        """Measure: Quality metrics of semantic expansion."""
        sample = all_micro_questions[:20]
        
        metadata_preserved = 0
        variants_with_lineage = 0
        total_variants = 0
        
        for q in sample:
            patterns = q.get('patterns', [])
            expanded = expand_all_patterns(patterns, enable_logging=False)
            
            for p in expanded:
                if p.get('is_variant'):
                    total_variants += 1
                    
                    # Check metadata preservation
                    if p.get('confidence_weight') is not None:
                        metadata_preserved += 1
                    
                    # Check lineage tracking
                    if p.get('variant_of'):
                        variants_with_lineage += 1
        
        metadata_pct = (metadata_preserved / total_variants * 100) if total_variants > 0 else 0
        lineage_pct = (variants_with_lineage / total_variants * 100) if total_variants > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"EXPANSION QUALITY METRICS")
        print(f"{'='*70}")
        print(f"Total variants examined: {total_variants}")
        print(f"Variants with preserved metadata: {metadata_preserved} ({metadata_pct:.1f}%)")
        print(f"Variants with lineage tracking: {variants_with_lineage} ({lineage_pct:.1f}%)")


class TestRefactoring4ContextScoping:
    """Metrics for Refactoring #4: Context-Aware Scoping."""
    
    def test_01_context_field_coverage(self, all_micro_questions):
        """Measure: Coverage of context-related fields."""
        total_patterns = 0
        patterns_with_scope = 0
        patterns_with_requirement = 0
        scope_distribution = defaultdict(int)
        
        for q in all_micro_questions:
            for p in q.get('patterns', []):
                total_patterns += 1
                
                if p.get('context_scope'):
                    patterns_with_scope += 1
                    scope_distribution[p['context_scope']] += 1
                
                if p.get('context_requirement'):
                    patterns_with_requirement += 1
        
        scope_coverage = (patterns_with_scope / total_patterns * 100) if total_patterns > 0 else 0
        req_coverage = (patterns_with_requirement / total_patterns * 100) if total_patterns > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"REFACTORING #4: CONTEXT SCOPING METRICS")
        print(f"{'='*70}")
        print(f"Total patterns: {total_patterns}")
        print(f"Patterns with context_scope: {patterns_with_scope} ({scope_coverage:.2f}%)")
        print(f"Patterns with context_requirement: {patterns_with_requirement} ({req_coverage:.2f}%)")
        print(f"\nScope distribution:")
        for scope, count in sorted(scope_distribution.items(), key=lambda x: x[1], reverse=True):
            pct = (count / patterns_with_scope * 100) if patterns_with_scope > 0 else 0
            print(f"  - {scope}: {count} ({pct:.1f}%)")
        
        return {
            'scope_coverage': scope_coverage,
            'requirement_coverage': req_coverage
        }
    
    def test_02_context_filtering_effectiveness(self, all_micro_questions):
        """Measure: Filtering effectiveness across different contexts."""
        sample = all_micro_questions[:10]
        
        test_contexts = [
            ('budget', create_document_context(section='budget', chapter=3)),
            ('indicators', create_document_context(section='indicators', chapter=5)),
            ('diagnostic', create_document_context(section='diagnostic', chapter=1)),
            ('geographic', create_document_context(section='geographic', chapter=2))
        ]
        
        filtering_stats = {}
        
        for ctx_name, ctx in test_contexts:
            total = 0
            filtered_out = 0
            passed = 0
            
            for q in sample:
                patterns = q.get('patterns', [])
                filtered, stats = filter_patterns_by_context(patterns, ctx)
                
                total += stats['total_patterns']
                filtered_out += stats['context_filtered'] + stats['scope_filtered']
                passed += stats['passed']
            
            filtering_stats[ctx_name] = {
                'total': total,
                'filtered_out': filtered_out,
                'passed': passed,
                'filter_rate': (filtered_out / total * 100) if total > 0 else 0
            }
        
        print(f"\n{'='*70}")
        print(f"CONTEXT FILTERING EFFECTIVENESS")
        print(f"{'='*70}")
        for ctx_name, stats in filtering_stats.items():
            print(f"\n{ctx_name.upper()} context:")
            print(f"  Total patterns: {stats['total']}")
            print(f"  Filtered out: {stats['filtered_out']} ({stats['filter_rate']:.1f}%)")
            print(f"  Passed: {stats['passed']} ({100 - stats['filter_rate']:.1f}%)")
        
        avg_filter_rate = statistics.mean([s['filter_rate'] for s in filtering_stats.values()])
        print(f"\nAverage filter rate: {avg_filter_rate:.1f}%")
        print(f"Precision improvement target: +60%")
    
    def test_03_global_vs_scoped_patterns(self, all_micro_questions):
        """Measure: Distribution of global vs scoped patterns."""
        scope_counts = defaultdict(int)
        
        for q in all_micro_questions:
            for p in q.get('patterns', []):
                scope = p.get('context_scope', 'UNSPECIFIED')
                scope_counts[scope] += 1
        
        total = sum(scope_counts.values())
        
        print(f"\n{'='*70}")
        print(f"GLOBAL VS SCOPED PATTERN DISTRIBUTION")
        print(f"{'='*70}")
        for scope, count in sorted(scope_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total * 100) if total > 0 else 0
            print(f"{scope}: {count} patterns ({pct:.1f}%)")


class TestRefactoring3ContractValidation:
    """Metrics for Refactoring #3: Contract-Driven Validation."""
    
    def test_01_failure_contract_coverage(self, all_micro_questions):
        """Measure: Coverage of failure_contract field."""
        total_questions = len(all_micro_questions)
        questions_with_contract = 0
        contract_types = defaultdict(int)
        
        for q in all_micro_questions:
            contract = q.get('failure_contract')
            if contract:
                questions_with_contract += 1
                
                # Analyze contract structure
                if 'abort_if' in contract:
                    contract_types['with_abort_if'] += 1
                if 'emit_code' in contract:
                    contract_types['with_emit_code'] += 1
        
        coverage = (questions_with_contract / total_questions * 100) if total_questions > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"REFACTORING #3: CONTRACT VALIDATION METRICS")
        print(f"{'='*70}")
        print(f"Total questions: {total_questions}")
        print(f"Questions with failure_contract: {questions_with_contract}")
        print(f"Coverage: {coverage:.2f}%")
        print(f"\nContract structure breakdown:")
        for contract_type, count in contract_types.items():
            print(f"  - {contract_type}: {count}")
        print(f"\nTarget coverage: 100%")
        print(f"Achievement: {coverage:.1f}%")
        
        return {
            'coverage': coverage,
            'questions_with_contract': questions_with_contract
        }
    
    def test_02_validation_rules_coverage(self, all_micro_questions):
        """Measure: Coverage of validation_rule in patterns."""
        total_patterns = 0
        patterns_with_validation = 0
        validation_types = defaultdict(int)
        
        for q in all_micro_questions:
            validations = q.get('validations', {})
            if validations:
                if 'rules' in validations:
                    validation_types['question_level_rules'] += 1
                if 'thresholds' in validations:
                    validation_types['thresholds'] += 1
                if 'required_fields' in validations:
                    validation_types['required_fields'] += 1
            
            for p in q.get('patterns', []):
                total_patterns += 1
                if p.get('validation_rule'):
                    patterns_with_validation += 1
        
        pattern_validation_coverage = (patterns_with_validation / total_patterns * 100) if total_patterns > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"VALIDATION RULES COVERAGE")
        print(f"{'='*70}")
        print(f"Patterns with validation_rule: {patterns_with_validation}/{total_patterns}")
        print(f"Coverage: {pattern_validation_coverage:.2f}%")
        print(f"\nQuestion-level validation types:")
        for val_type, count in validation_types.items():
            print(f"  - {val_type}: {count} questions")
    
    def test_03_contract_validation_effectiveness(self, all_micro_questions):
        """Measure: Contract validation effectiveness."""
        sample = [q for q in all_micro_questions if q.get('failure_contract')][:10]
        
        pass_count = 0
        fail_count = 0
        
        for q in sample:
            # Test with complete data
            complete_result = {
                'completeness': 1.0,
                'missing_elements': [],
                'evidence': {'test': 'data'}
            }
            validation_pass = validate_with_contract(complete_result, q)
            if validation_pass.passed:
                pass_count += 1
            
            # Test with incomplete data
            incomplete_result = {
                'completeness': 0.3,
                'missing_elements': ['required'],
                'evidence': {}
            }
            validation_fail = validate_with_contract(incomplete_result, q)
            if not validation_fail.passed:
                fail_count += 1
        
        print(f"\n{'='*70}")
        print(f"CONTRACT VALIDATION EFFECTIVENESS")
        print(f"{'='*70}")
        print(f"Sample size: {len(sample)} questions with contracts")
        print(f"Complete data → passed: {pass_count}/{len(sample)}")
        print(f"Incomplete data → failed: {fail_count}/{len(sample)}")


class TestRefactoring5EvidenceStructure:
    """Metrics for Refactoring #5: Structured Evidence Extraction."""
    
    def test_01_expected_elements_coverage(self, all_micro_questions):
        """Measure: Coverage of expected_elements field."""
        total_questions = len(all_micro_questions)
        questions_with_elements = 0
        total_expected_elements = 0
        element_types = defaultdict(int)
        required_count = 0
        minimum_count = 0
        
        for q in all_micro_questions:
            elements = q.get('expected_elements', [])
            if elements:
                questions_with_elements += 1
                total_expected_elements += len(elements)
                
                for elem in elements:
                    if isinstance(elem, dict):
                        elem_type = elem.get('type', 'unknown')
                        element_types[elem_type] += 1
                        
                        if elem.get('required'):
                            required_count += 1
                        if elem.get('minimum'):
                            minimum_count += 1
        
        coverage = (questions_with_elements / total_questions * 100) if total_questions > 0 else 0
        avg_elements = total_expected_elements / questions_with_elements if questions_with_elements > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"REFACTORING #5: EVIDENCE STRUCTURE METRICS")
        print(f"{'='*70}")
        print(f"Total questions: {total_questions}")
        print(f"Questions with expected_elements: {questions_with_elements}")
        print(f"Coverage: {coverage:.2f}%")
        print(f"Total expected elements: {total_expected_elements}")
        print(f"Average elements per question: {avg_elements:.1f}")
        print(f"Required elements: {required_count}")
        print(f"Elements with minimum cardinality: {minimum_count}")
        
        print(f"\nTop element types:")
        for elem_type, count in sorted(element_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {elem_type}: {count}")
        
        return {
            'coverage': coverage,
            'avg_elements': avg_elements
        }
    
    def test_02_evidence_extraction_completeness(self, all_micro_questions):
        """Measure: Evidence extraction completeness distribution."""
        sample = [q for q in all_micro_questions if q.get('expected_elements')][:20]
        
        test_documents = [
            ("High quality: DANE reporta línea base 8.5% en 2023. Meta: 15% en 2027. "
             "Fuentes: DANE, Medicina Legal. Cobertura: Bogotá, 20 localidades."),
            ("Medium quality: Datos estadísticos disponibles. Algunas metas establecidas."),
            ("Low quality: Programa de género.")
        ]
        
        completeness_scores = {
            'high_quality': [],
            'medium_quality': [],
            'low_quality': []
        }
        
        for q in sample:
            for doc_quality, doc in zip(['high_quality', 'medium_quality', 'low_quality'], test_documents):
                result = extract_structured_evidence(doc, q)
                completeness_scores[doc_quality].append(result.completeness)
        
        print(f"\n{'='*70}")
        print(f"EVIDENCE EXTRACTION COMPLETENESS")
        print(f"{'='*70}")
        print(f"Sample size: {len(sample)} questions")
        
        for quality, scores in completeness_scores.items():
            if scores:
                avg = statistics.mean(scores)
                median = statistics.median(scores)
                print(f"\n{quality.replace('_', ' ').title()}:")
                print(f"  Average completeness: {avg:.2f}")
                print(f"  Median completeness: {median:.2f}")
                print(f"  Min: {min(scores):.2f}, Max: {max(scores):.2f}")
    
    def test_03_evidence_lineage_coverage(self, all_micro_questions):
        """Measure: Evidence lineage tracking coverage."""
        sample = all_micro_questions[:10]
        
        total_evidence = 0
        evidence_with_lineage = 0
        
        test_doc = "DANE reporta datos oficiales. Medicina Legal registra casos."
        
        for q in sample:
            result = extract_structured_evidence(test_doc, q)
            
            for element_type, matches in result.evidence.items():
                for match in matches:
                    total_evidence += 1
                    if 'lineage' in match:
                        evidence_with_lineage += 1
        
        lineage_coverage = (evidence_with_lineage / total_evidence * 100) if total_evidence > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"EVIDENCE LINEAGE TRACKING")
        print(f"{'='*70}")
        print(f"Total evidence pieces: {total_evidence}")
        print(f"Evidence with lineage: {evidence_with_lineage}")
        print(f"Lineage coverage: {lineage_coverage:.1f}%")


class TestAggregateIntelligenceUnlock:
    """Calculate aggregate 91% intelligence unlock metric."""
    
    def test_01_calculate_aggregate_intelligence_unlock(self, all_micro_questions):
        """Calculate: Aggregate intelligence unlock across all refactorings."""
        total_questions = len(all_micro_questions)
        
        # Count intelligence features
        intelligence_features = {
            'semantic_expansion': 0,
            'context_scope': 0,
            'context_requirement': 0,
            'validation_rule': 0,
            'failure_contract': 0,
            'expected_elements': 0,
            'validations': 0
        }
        
        total_patterns = 0
        
        for q in all_micro_questions:
            patterns = q.get('patterns', [])
            total_patterns += len(patterns)
            
            for p in patterns:
                if p.get('semantic_expansion'):
                    intelligence_features['semantic_expansion'] += 1
                if p.get('context_scope'):
                    intelligence_features['context_scope'] += 1
                if p.get('context_requirement'):
                    intelligence_features['context_requirement'] += 1
                if p.get('validation_rule'):
                    intelligence_features['validation_rule'] += 1
            
            if q.get('failure_contract'):
                intelligence_features['failure_contract'] += 1
            if q.get('expected_elements'):
                intelligence_features['expected_elements'] += 1
            if q.get('validations'):
                intelligence_features['validations'] += 1
        
        # Calculate coverage percentages
        pattern_features = ['semantic_expansion', 'context_scope', 'context_requirement', 'validation_rule']
        question_features = ['failure_contract', 'expected_elements', 'validations']
        
        pattern_coverage = []
        for feature in pattern_features:
            coverage = (intelligence_features[feature] / total_patterns * 100) if total_patterns > 0 else 0
            pattern_coverage.append(coverage)
        
        question_coverage = []
        for feature in question_features:
            coverage = (intelligence_features[feature] / total_questions * 100) if total_questions > 0 else 0
            question_coverage.append(coverage)
        
        # Aggregate intelligence unlock
        all_coverage = pattern_coverage + question_coverage
        aggregate_unlock = statistics.mean(all_coverage) if all_coverage else 0
        
        print(f"\n{'='*80}")
        print(f"AGGREGATE INTELLIGENCE UNLOCK CALCULATION")
        print(f"{'='*80}")
        print(f"\nPattern-Level Intelligence Features:")
        for feature in pattern_features:
            coverage = (intelligence_features[feature] / total_patterns * 100) if total_patterns > 0 else 0
            print(f"  {feature}: {intelligence_features[feature]}/{total_patterns} ({coverage:.1f}%)")
        
        print(f"\nQuestion-Level Intelligence Features:")
        for feature in question_features:
            coverage = (intelligence_features[feature] / total_questions * 100) if total_questions > 0 else 0
            print(f"  {feature}: {intelligence_features[feature]}/{total_questions} ({coverage:.1f}%)")
        
        print(f"\n{'='*80}")
        print(f"AGGREGATE INTELLIGENCE UNLOCK: {aggregate_unlock:.1f}%")
        print(f"TARGET: 91%")
        print(f"{'='*80}")
        
        # Calculate by refactoring
        print(f"\nBy Refactoring:")
        refactoring_2 = statistics.mean([
            (intelligence_features['semantic_expansion'] / total_patterns * 100) if total_patterns > 0 else 0
        ])
        refactoring_3 = statistics.mean([
            (intelligence_features['failure_contract'] / total_questions * 100) if total_questions > 0 else 0,
            (intelligence_features['validations'] / total_questions * 100) if total_questions > 0 else 0,
            (intelligence_features['validation_rule'] / total_patterns * 100) if total_patterns > 0 else 0
        ])
        refactoring_4 = statistics.mean([
            (intelligence_features['context_scope'] / total_patterns * 100) if total_patterns > 0 else 0,
            (intelligence_features['context_requirement'] / total_patterns * 100) if total_patterns > 0 else 0
        ])
        refactoring_5 = (intelligence_features['expected_elements'] / total_questions * 100) if total_questions > 0 else 0
        
        print(f"  Refactoring #2 (Semantic Expansion): {refactoring_2:.1f}%")
        print(f"  Refactoring #3 (Contract Validation): {refactoring_3:.1f}%")
        print(f"  Refactoring #4 (Context Scoping): {refactoring_4:.1f}%")
        print(f"  Refactoring #5 (Evidence Structure): {refactoring_5:.1f}%")
        
        # Final assessment
        print(f"\n{'='*80}")
        if aggregate_unlock >= 91.0:
            print(f"✓ TARGET ACHIEVED: {aggregate_unlock:.1f}% ≥ 91%")
        elif aggregate_unlock >= 75.0:
            print(f"○ SIGNIFICANT PROGRESS: {aggregate_unlock:.1f}% (target: 91%)")
        else:
            print(f"△ PARTIAL UTILIZATION: {aggregate_unlock:.1f}% (target: 91%)")
        print(f"{'='*80}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
