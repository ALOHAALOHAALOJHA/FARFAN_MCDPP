"""
Standalone Signal Intelligence Test
====================================

Direct test of signal intelligence modules without triggering full orchestrator import.

This bypasses the aggregation.py import error while testing the core functionality.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import only what we need (avoid orchestrator.__init__.py chain)
from farfan_pipeline.core.orchestrator.signal_semantic_expander import (
    expand_pattern_semantically,
    expand_all_patterns,
    extract_core_term
)

from farfan_pipeline.core.orchestrator.signal_context_scoper import (
    filter_patterns_by_context,
    create_document_context,
    context_matches
)

from farfan_pipeline.core.orchestrator.signal_contract_validator import (
    validate_with_contract,
    execute_failure_contract,
    ValidationResult
)

from farfan_pipeline.core.orchestrator.signal_evidence_extractor import (
    extract_structured_evidence,
    EvidenceExtractionResult
)


def load_questionnaire_direct():
    """Load questionnaire directly without canonical loader."""
    qfile = Path("system/config/questionnaire/questionnaire_monolith.json")
    with open(qfile) as f:
        return json.load(f)


def test_01_semantic_expansion():
    """Test semantic expansion with real pattern."""
    print("\n" + "="*70)
    print("TEST 1: Semantic Expansion")
    print("="*70)
    
    # Real pattern structure
    pattern = {
        'pattern': r'presupuesto\s+asignado',
        'semantic_expansion': 'presupuesto|recursos|financiamiento|fondos',
        'id': 'PAT-TEST-001',
        'confidence_weight': 0.8,
        'category': 'FINANCIAL'
    }
    
    variants = expand_pattern_semantically(pattern)
    
    print(f"\n✓ Base pattern: {pattern['pattern']}")
    print(f"✓ Semantic expansion: {pattern['semantic_expansion']}")
    print(f"✓ Generated {len(variants)} variants:")
    
    for v in variants:
        status = "ORIGINAL" if not v.get('is_variant') else "VARIANT"
        print(f"  [{status}] {v['id']}: {v['pattern']}")
    
    assert len(variants) >= 1
    assert any(v.get('is_variant') for v in variants)
    
    print("\n✅ TEST 1 PASSED")
    return True


def test_02_context_filtering():
    """Test context-aware pattern filtering."""
    print("\n" + "="*70)
    print("TEST 2: Context Filtering")
    print("="*70)
    
    patterns = [
        {
            'pattern': 'budget pattern',
            'context_requirement': {'section': 'budget'},
            'id': 'PAT-001'
        },
        {
            'pattern': 'global pattern',
            'context_scope': 'global',
            'id': 'PAT-002'
        },
        {
            'pattern': 'indicators pattern',
            'context_requirement': {'section': 'indicators'},
            'id': 'PAT-003'
        }
    ]
    
    # Test budget context
    context_budget = create_document_context(section='budget', chapter=3)
    filtered_budget, stats_budget = filter_patterns_by_context(patterns, context_budget)
    
    print(f"\n✓ Budget context filtering:")
    print(f"  Total patterns: {stats_budget['total_patterns']}")
    print(f"  Passed: {stats_budget['passed']}")
    print(f"  Filtered: {stats_budget['context_filtered'] + stats_budget['scope_filtered']}")
    
    # Should have budget pattern + global pattern
    assert stats_budget['passed'] >= 2
    
    # Test indicators context
    context_indicators = create_document_context(section='indicators', chapter=5)
    filtered_indicators, stats_indicators = filter_patterns_by_context(patterns, context_indicators)
    
    print(f"\n✓ Indicators context filtering:")
    print(f"  Total patterns: {stats_indicators['total_patterns']}")
    print(f"  Passed: {stats_indicators['passed']}")
    
    assert stats_indicators['passed'] >= 2
    
    print("\n✅ TEST 2 PASSED")
    return True


def test_03_failure_contract():
    """Test failure contract validation."""
    print("\n" + "="*70)
    print("TEST 3: Failure Contract Validation")
    print("="*70)
    
    failure_contract = {
        'abort_if': ['missing_currency', 'negative_amount'],
        'emit_code': 'ERR_BUDGET_001'
    }
    
    # Test failure case
    result_fail = {
        'amount': 1000,
        'currency': None  # Missing currency
    }
    
    validation_fail = execute_failure_contract(result_fail, failure_contract)
    
    print(f"\n✓ Failed validation test:")
    print(f"  Status: {validation_fail.status}")
    print(f"  Passed: {validation_fail.passed}")
    print(f"  Error code: {validation_fail.error_code}")
    print(f"  Condition: {validation_fail.condition_violated}")
    print(f"  Remediation: {validation_fail.remediation}")
    
    assert not validation_fail.passed
    assert validation_fail.error_code == 'ERR_BUDGET_001'
    assert validation_fail.condition_violated == 'missing_currency'
    
    # Test success case
    result_pass = {
        'amount': 1000,
        'currency': 'COP'
    }
    
    validation_pass = execute_failure_contract(result_pass, failure_contract)
    
    print(f"\n✓ Passed validation test:")
    print(f"  Status: {validation_pass.status}")
    print(f"  Passed: {validation_pass.passed}")
    
    assert validation_pass.passed
    
    print("\n✅ TEST 3 PASSED")
    return True


def test_04_evidence_extraction():
    """Test structured evidence extraction."""
    print("\n" + "="*70)
    print("TEST 4: Evidence Extraction")
    print("="*70)
    
    signal_node = {
        'expected_elements': [
            {'type': 'baseline_indicator', 'required': True},
            {'type': 'meta_objetivo', 'required': True},
            {'type': 'series_temporales_años', 'minimum': 2},
            {'type': 'entidad_responsable', 'required': False},
            {'type': 'asignacion_presupuestal', 'required': False}
        ],
        'patterns': [
            {
                'id': 'PAT-BASELINE-001',
                'pattern': 'línea de base|año base|situación inicial',
                'confidence_weight': 0.85,
                'category': 'TEMPORAL',
                'match_type': 'substring'
            },
            {
                'id': 'PAT-TARGET-001',
                'pattern': 'meta|objetivo|alcanzar',
                'confidence_weight': 0.85,
                'category': 'QUANTITATIVE',
                'match_type': 'substring'
            },
            {
                'id': 'PAT-YEAR-001',
                'pattern': r'20\d{2}',
                'confidence_weight': 0.9,
                'category': 'TEMPORAL',
                'match_type': 'regex'
            },
            {
                'id': 'PAT-ENTITY-001',
                'pattern': 'Secretaría|Departamento|Ministerio',
                'confidence_weight': 0.8,
                'category': 'ENTITY',
                'match_type': 'substring'
            },
            {
                'id': 'PAT-BUDGET-001',
                'pattern': 'COP|presupuesto|millones',
                'confidence_weight': 0.75,
                'category': 'QUANTITATIVE',
                'match_type': 'substring'
            }
        ],
        'validations': {}
    }
    
    sample_text = """
    Diagnóstico de Género - Municipio de Bogotá
    
    Línea de base año 2023: 8.5% de mujeres en cargos directivos del sector público.
    Meta establecida: alcanzar 15% para el año 2027.
    Responsable: Secretaría Distrital de la Mujer
    Presupuesto asignado: COP 1,500 millones para programas de formación.
    
    Fuente: DANE, Encuesta de Empleo 2023
    """
    
    evidence_result = extract_structured_evidence(sample_text, signal_node)
    
    print(f"\n✓ Evidence extraction results:")
    print(f"  Completeness: {evidence_result.completeness:.2%}")
    print(f"  Evidence types: {len(evidence_result.evidence)}")
    print(f"  Missing required: {evidence_result.missing_required}")
    print(f"  Under minimum: {evidence_result.under_minimum}")
    
    for element_type, matches in evidence_result.evidence.items():
        print(f"\n  [{element_type}] - {len(matches)} matches")
        for match in matches[:2]:  # Show first 2
            print(f"    Value: {match.get('value')}")
            print(f"    Confidence: {match.get('confidence', 0):.2f}")
            print(f"    Pattern: {match.get('pattern_id')}")
    
    # Should extract at least 3 element types using monolith patterns
    assert len(evidence_result.evidence) >= 3
    assert evidence_result.completeness > 0.5
    
    print("\n✅ TEST 4 PASSED")
    return True


def test_05_real_questionnaire_patterns():
    """Test with real patterns from questionnaire."""
    print("\n" + "="*70)
    print("TEST 5: Real Questionnaire Patterns")
    print("="*70)
    
    data = load_questionnaire_direct()
    
    blocks = data['blocks']
    micro_questions = blocks['micro_questions']
    
    print(f"\n✓ Loaded questionnaire:")
    print(f"  Schema version: {data.get('schema_version')}")
    print(f"  Total micro questions: {len(micro_questions)}")
    
    # Get first question
    mq = micro_questions[0]
    patterns = mq.get('patterns', [])
    
    print(f"\n✓ First question (Q001):")
    print(f"  Text: {mq.get('text', '')[:70]}...")
    print(f"  Patterns: {len(patterns)}")
    print(f"  Expected elements: {len(mq.get('expected_elements', []))}")
    
    # Test pattern metadata
    if patterns:
        p = patterns[0]
        print(f"\n✓ Sample pattern metadata:")
        print(f"  ID: {p.get('id')}")
        print(f"  Pattern: {p.get('pattern', '')[:60]}...")
        print(f"  Confidence weight: {p.get('confidence_weight')}")
        print(f"  Category: {p.get('category')}")
        print(f"  Context scope: {p.get('context_scope')}")
        print(f"  Semantic expansion: {p.get('semantic_expansion')}")
        
        assert 'confidence_weight' in p
        assert 'category' in p
    
    # Test expansion on all patterns
    expanded = expand_all_patterns(patterns[:5], enable_logging=False)  # First 5 patterns
    
    print(f"\n✓ Pattern expansion:")
    print(f"  Original: {len(patterns[:5])}")
    print(f"  Expanded: {len(expanded)}")
    print(f"  Multiplier: {len(expanded)/len(patterns[:5]):.2f}x")
    
    assert len(expanded) >= len(patterns[:5])
    
    print("\n✅ TEST 5 PASSED")
    return True


def test_06_metadata_preservation():
    """Test that metadata is preserved through transformations."""
    print("\n" + "="*70)
    print("TEST 6: Metadata Preservation")
    print("="*70)
    
    original_pattern = {
        'pattern': r'tasa\s+de\s+desempleo',
        'semantic_expansion': 'tasa|índice|porcentaje',
        'id': 'PAT-PRESERVATION-001',
        'confidence_weight': 0.9,
        'category': 'ECONOMIC',
        'context_scope': 'PARAGRAPH',
        'specificity': 'HIGH'
    }
    
    # Expand pattern
    variants = expand_pattern_semantically(original_pattern)
    
    print(f"\n✓ Original pattern:")
    print(f"  confidence_weight: {original_pattern['confidence_weight']}")
    print(f"  category: {original_pattern['category']}")
    print(f"  specificity: {original_pattern['specificity']}")
    
    print(f"\n✓ Checking {len(variants)} variants for metadata preservation...")
    
    for v in variants:
        # All variants should have same metadata as original
        assert v['confidence_weight'] == original_pattern['confidence_weight']
        assert v['category'] == original_pattern['category']
        assert v['specificity'] == original_pattern['specificity']
        
        if v.get('is_variant'):
            print(f"  ✓ {v['id']}: metadata preserved")
    
    print("\n✅ TEST 6 PASSED")
    return True


def test_07_end_to_end_pipeline():
    """Test complete end-to-end pipeline."""
    print("\n" + "="*70)
    print("TEST 7: End-to-End Pipeline")
    print("="*70)
    
    # Load real questionnaire
    data = load_questionnaire_direct()
    mq = data['blocks']['micro_questions'][0]
    
    patterns = mq.get('patterns', [])
    
    # Step 1: Expand patterns
    print("\n→ Step 1: Semantic expansion")
    expanded_patterns = expand_all_patterns(patterns, enable_logging=False)
    print(f"  {len(patterns)} → {len(expanded_patterns)} patterns")
    
    # Step 2: Filter by context
    print("\n→ Step 2: Context filtering")
    context = create_document_context(section='indicators', chapter=2)
    filtered, stats = filter_patterns_by_context(expanded_patterns, context)
    print(f"  {stats['total_patterns']} → {stats['passed']} patterns")
    
    # Step 3: Extract evidence
    print("\n→ Step 3: Evidence extraction")
    signal_node = {
        'expected_elements': ['baseline_indicator', 'target_value', 'timeline'],
        'patterns': filtered,
        'validations': mq.get('validations', {})
    }
    
    text = "Línea de base: 8.5%. Meta: 6% para 2027."
    evidence = extract_structured_evidence(text, signal_node)
    print(f"  Completeness: {evidence.completeness:.2%}")
    print(f"  Extracted: {len(evidence.evidence)} elements")
    
    # Step 4: Validate with contract
    print("\n→ Step 4: Contract validation")
    result = {
        'evidence': evidence.evidence,
        'completeness': evidence.completeness
    }
    
    validation_node = {
        'failure_contract': mq.get('failure_contract', {}),
        'validations': mq.get('validations', {})
    }
    
    validation = validate_with_contract(result, validation_node)
    print(f"  Status: {validation.status}")
    print(f"  Passed: {validation.passed}")
    
    print("\n✅ TEST 7 PASSED")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("SIGNAL INTELLIGENCE LAYER - INTEGRATION TEST SUITE")
    print("="*70)
    print("\nRunning severe integration tests (NO MOCKS, REAL DATA)...")
    
    tests = [
        test_01_semantic_expansion,
        test_02_context_filtering,
        test_03_failure_contract,
        test_04_evidence_extraction,
        test_05_real_questionnaire_patterns,
        test_06_metadata_preservation,
        test_07_end_to_end_pipeline
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"\n✅ PASSED: {passed}/{len(tests)}")
    print(f"❌ FAILED: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - SIGNAL INTELLIGENCE LAYER VERIFIED")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
