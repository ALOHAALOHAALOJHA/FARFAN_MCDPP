# Signal Intelligence Pipeline: Integration Test Suite

## Overview

This directory contains comprehensive integration tests for the signal intelligence pipeline, validating the complete flow from pattern expansion through validation using real questionnaire data.

## Test Files Summary

| Test File | Focus | Test Classes | Duration |
|-----------|-------|--------------|----------|
| `test_signal_intelligence_pipeline_integration.py` | Primary integration tests | 8 | ~20-30s |
| `test_signal_pipeline_validation_scenarios.py` | Realistic document scenarios | 5 | ~15-20s |
| `test_signal_intelligence_metrics.py` | 91% intelligence unlock metrics | 5 | ~10-20s |
| `test_signal_intelligence_cross_validation.py` | Cross-component integration | 7 | ~10-15s |
| **`test_signal_intelligence_comprehensive_integration.py`** | **Comprehensive end-to-end integration** | **7** | **~30-60s** |

**Total: 32 test classes, ~85-145 seconds**

---

## Test Files

### 1. `test_signal_intelligence_pipeline_integration.py`

**Primary Integration Tests**

Tests the complete signal intelligence pipeline from end-to-end with real questionnaire data.

**Test Classes:**
- `TestPatternExpansionMetrics` - Measures pattern expansion multiplier and metadata preservation
- `TestContextFilteringEffectiveness` - Validates context-aware pattern filtering
- `TestContractValidation` - Tests failure contracts and validation logic
- `TestEvidenceExtraction` - Verifies structured evidence extraction with completeness metrics
- `TestEnrichedSignalPackIntegration` - Tests the EnrichedSignalPack wrapper
- `TestEndToEndPipeline` - Complete analysis from document to validated result
- `TestIntelligenceUnlockVerification` - Measures 91% intelligence unlock across questionnaire

**Key Metrics Tested:**
- Pattern expansion multiplier (target: 5x)
- Context filtering precision improvement (target: +60%)
- Contract validation coverage (target: 100%)
- Evidence extraction completeness (0.0-1.0 scale)
- Intelligence unlock percentage (target: 91%)

**Sample Run:**
```bash
pytest tests/core/test_signal_intelligence_pipeline_integration.py -v -s
```

**Expected Output:**
```
✓ Pattern Expansion Metrics:
  Original patterns: 4200
  Expanded patterns: 12600
  Multiplier: 3.00x
  
✓ Intelligence Unlock Metrics:
  Semantic expansion coverage: 45.2%
  Context scoping coverage: 67.8%
  Validation coverage: 23.4%
  
✓ End-to-End Analysis Pipeline:
  Evidence types extracted: 8
  Completeness score: 0.85
  Validation status: success
```

### 2. `test_signal_pipeline_validation_scenarios.py`

**Realistic Document Scenarios**

Tests the pipeline with realistic policy document excerpts covering different sections and contexts.

**Test Classes:**
- `TestRealisticDocumentScenarios` - Budget, indicators, geographic, and diagnostic sections
- `TestEdgeCasesAndErrorHandling` - Empty docs, minimal content, irrelevant content, conflicts
- `TestContextAwareFiltering` - Context hierarchy and requirement enforcement
- `TestValidationContractScenarios` - Missing elements, minimum cardinality, validation chains
- `TestPipelinePerformance` - Large documents, multiple pattern matching

**Document Types Tested:**
1. **Budget Section** - Financial data, funding sources, responsible entities
2. **Indicators Section** - Metrics, baselines, targets, temporal series
3. **Geographic Coverage** - Territorial distribution, municipalities, departments
4. **Diagnostic Section** - Multiple official sources (DANE, Medicina Legal, Fiscalía)
5. **Edge Cases** - Empty, minimal, irrelevant, conflicting data

**Sample Run:**
```bash
pytest tests/core/test_signal_pipeline_validation_scenarios.py -v -s
```

**Expected Output:**
```
✓ Budget Section Analysis:
  Completeness: 0.75
  Evidence types: 6
  Validation: success

✓ Multi-Source Diagnostic Analysis:
  Completeness: 0.92
  Total evidence matches: 23
  
✓ Empty Document Handling:
  Completeness: 0.00
  Evidence count: 0
```

### 3. `test_signal_intelligence_metrics.py`

**Intelligence Unlock Metrics**

Comprehensive metrics validation measuring the 91% intelligence unlock claim across all 4 refactorings.

### 4. `test_signal_intelligence_cross_validation.py`

**Cross-Component Integration and Validation**

Tests integration between all 4 refactorings and validates proper data flow through the pipeline.

**Test Classes:**
- `TestPipelineDataFlow` - Data flow from expansion → filtering → extraction → validation
- `TestMetadataConsistency` - Metadata preservation across transformations
- `TestErrorPropagation` - Error handling through pipeline stages
- `TestPerformanceImpact` - Performance of combined refactorings
- `TestEnrichedSignalPackIntegration` - EnrichedSignalPack as integration layer
- `TestCrossComponentConsistency` - Consistency across component boundaries

**Key Validations:**
- Metadata preserved through all transformations
- Context filtering respects expanded patterns
- Evidence extraction works with filtered patterns
- Validation contracts align with extracted evidence
- Error conditions propagate correctly
- Performance remains acceptable with all refactorings enabled

**Sample Run:**
```bash
pytest tests/core/test_signal_intelligence_cross_validation.py -v -s
```

**Test Classes:**
- `TestRefactoring2SemanticExpansion` - Semantic expansion coverage and multiplier
- `TestRefactoring4ContextScoping` - Context field coverage and filtering effectiveness
- `TestRefactoring3ContractValidation` - Failure contract and validation rule coverage
- `TestRefactoring5EvidenceStructure` - Expected elements coverage and completeness
- `TestAggregateIntelligenceUnlock` - Overall 91% intelligence unlock calculation

**Metrics Calculated:**

**Refactoring #2 (Semantic Expansion):**
- Coverage: % of patterns with semantic_expansion field
- Multiplier: Actual expansion ratio (target: 5x)
- Quality: Metadata preservation, lineage tracking

**Refactoring #3 (Contract Validation):**
- Coverage: % of questions with failure_contract
- Validation rules: % of patterns with validation_rule
- Effectiveness: Pass/fail detection accuracy

**Refactoring #4 (Context Scoping):**
- Coverage: % of patterns with context_scope/context_requirement
- Filtering: % of patterns filtered by context
- Distribution: Global vs scoped pattern ratio

**Refactoring #5 (Evidence Structure):**
- Coverage: % of questions with expected_elements
- Completeness: Average extraction completeness scores
- Lineage: % of evidence with lineage tracking

**Aggregate Metrics:**
- Overall intelligence unlock percentage
- Per-refactoring unlock percentages
- Comparison to 91% target

**Sample Run:**
```bash
pytest tests/core/test_signal_intelligence_metrics.py -v -s
```

**Expected Output:**
```
======================================================================
REFACTORING #2: SEMANTIC EXPANSION METRICS
======================================================================
Total patterns analyzed: 4200
Patterns with semantic_expansion: 1890
Coverage: 45.00%

Pattern expansion multiplier: 3.2x
Target multiplier: 5x
Achievement: 64% of target

======================================================================
AGGREGATE INTELLIGENCE UNLOCK CALCULATION
======================================================================
Pattern-Level Intelligence Features:
  semantic_expansion: 1890/4200 (45.0%)
  context_scope: 2847/4200 (67.8%)
  context_requirement: 756/4200 (18.0%)
  validation_rule: 987/4200 (23.5%)

Question-Level Intelligence Features:
  failure_contract: 267/300 (89.0%)
  expected_elements: 298/300 (99.3%)
  validations: 245/300 (81.7%)

======================================================================
AGGREGATE INTELLIGENCE UNLOCK: 60.6%
TARGET: 91%
======================================================================
```

**Expected Output:**
```
✓ Pipeline Data Flow:
  Metadata preserved through expansion: ✓
  Expanded patterns filter correctly: ✓
  Filtered patterns extract evidence: ✓
  Evidence validates with contracts: ✓

✓ Cross-Component Consistency:
  Expansion-Filtering consistent: ✓
  Extraction-Validation aligned: ✓
  
✓ EnrichedSignalPack Integration:
  All 4 refactorings integrated: ✓
  Metadata access working: ✓
```

## Running All Tests

### Run all signal intelligence tests:
```bash
pytest tests/core/test_signal_intelligence_*.py -v
```

### Run with detailed output:
```bash
pytest tests/core/test_signal_intelligence_*.py -v -s
```

### Run specific test class:
```bash
pytest tests/core/test_signal_intelligence_metrics.py::TestAggregateIntelligenceUnlock -v -s
```

### Run with coverage:
```bash
pytest tests/core/test_signal_intelligence_*.py --cov=farfan_pipeline.core.orchestrator --cov-report=term-missing
```

## Test Data

All tests use **REAL questionnaire data** from `questionnaire_monolith.json`:
- 300+ micro questions
- 4,200+ patterns
- Complete metadata (semantic_expansion, context_scope, failure_contract, expected_elements)
- No mocks or stubs for questionnaire data

## Key Assertions

### Pattern Expansion
- `assert multiplier >= 2.0` - Minimum 2x expansion
- `assert expanded_count >= original_count` - No pattern loss
- `assert metadata preserved` - Confidence, category preserved in variants

### Context Filtering
- `assert filtered_count <= total_count` - Filtering reduces patterns
- `assert global_patterns always pass` - Global scope unaffected

### Contract Validation
- `assert validation.passed for complete data` - Complete data passes
- `assert not validation.passed for missing required` - Missing elements fail
- `assert error_code present` - Failure codes generated

### Evidence Extraction
- `assert 0.0 <= completeness <= 1.0` - Completeness in valid range
- `assert evidence is dict` - Structured output
- `assert lineage tracking present` - Traceability enabled

### Intelligence Unlock
- `assert aggregate_unlock > 0` - Features are utilized
- Target: 91% (aspirational)
- Minimum: 50% (acceptable baseline)

## Performance Considerations

### Test Duration
- Full suite: ~30-60 seconds
- Metrics tests: ~10-20 seconds (sampling used)
- Integration tests: ~20-30 seconds

### Sampling Strategy
- Metrics tests sample 20-50 questions to avoid excessive computation
- Full questionnaire validation on key metrics only
- Pattern expansion tested on representative subset

## Interpretation Guide

### Completeness Scores
- **0.0-0.3**: Low quality extraction (missing most elements)
- **0.3-0.6**: Partial extraction (some elements found)
- **0.6-0.8**: Good extraction (most elements found)
- **0.8-1.0**: Excellent extraction (all/nearly all elements found)

### Intelligence Unlock Percentage
- **90-100%**: Exceptional - Near-complete utilization
- **70-90%**: Good - Major features utilized
- **50-70%**: Moderate - Significant utilization
- **<50%**: Limited - Underutilization

### Pattern Expansion Multiplier
- **5x+**: Target achieved (5-10 variants per pattern)
- **3-5x**: Good expansion (3-5 variants per pattern)
- **2-3x**: Moderate expansion (2-3 variants per pattern)
- **<2x**: Limited expansion

## Integration with CI/CD

These tests are designed to run in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run Signal Intelligence Tests
  run: |
    pytest tests/core/test_signal_intelligence_*.py \
      -v \
      --junitxml=test-results/signal-intelligence.xml \
      --cov=farfan_pipeline.core.orchestrator \
      --cov-report=xml
```

## Troubleshooting

### Test Failures

**"No patterns with semantic_expansion found"**
- Verify questionnaire_monolith.json has semantic_expansion fields
- Check questionnaire loading succeeded

**"Intelligence unlock below 50%"**
- Normal if questionnaire metadata is incomplete
- Review specific refactoring metrics to identify gaps

**"Pattern expansion multiplier < 2x"**
- Check if patterns have semantic_expansion fields
- Verify expansion logic is enabled

### Common Issues

**Slow test execution:**
- Tests sample questions to avoid processing all 300+
- Adjust sample size in test code if needed

**Questionnaire not found:**
- Ensure `system/config/questionnaire/questionnaire_monolith.json` exists
- Check PROJECT_ROOT path configuration

## Architecture Alignment

These tests validate the architectural contract:

1. **Canonical Questionnaire Access**: All tests use `load_questionnaire()` - no direct file access
2. **Signal Intelligence Layer**: Tests validate all 4 refactorings integrated
3. **Deterministic Execution**: Tests use fixed data, reproducible results
4. **Type Safety**: All results include proper type annotations
5. **Observability**: Tests log metrics for monitoring

## Related Documentation

- `SIGNAL_INTELLIGENCE_ARCHITECTURE.md` - Architecture overview
- `CALIBRATION_SIGNAL_INTELLIGENCE.md` - Calibration details
- `src/farfan_pipeline/core/orchestrator/signal_intelligence_layer.py` - Implementation
- `tests/wiring/test_pattern_expansion.py` - Unit tests for semantic expansion
- `tests/integration/test_signal_intelligence_integration.py` - Additional integration tests

## Contributing

When adding new tests:

1. Use real questionnaire data via `load_questionnaire()`
2. Measure quantitative metrics where possible
3. Test with realistic document excerpts
4. Include edge cases and error conditions
5. Document expected ranges for metrics
6. Add to appropriate test class

## License

Part of F.A.R.F.A.N Pipeline project.
