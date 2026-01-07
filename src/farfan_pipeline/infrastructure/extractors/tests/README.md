# Extractor Tests - Auto-Generated from Empirical Corpus

## Overview

This test suite provides comprehensive validation for the empirically-calibrated extractors:

- **FinancialChainExtractor (MC05)**: Budget chains, funding sources, PPI tables
- **CausalVerbExtractor (MC08)**: Causal relationships, action verbs, theory of change
- **InstitutionalNERExtractor (MC09)**: Colombian institutions, entity networks

All tests are auto-generated from **empirical corpus gold standards** derived from 14 real PDT plans (2,956 pages analyzed).

## Test Structure

```
tests/
├── conftest.py                              # Shared fixtures and test data
├── pytest.ini                               # Pytest configuration
├── test_financial_chain_extractor.py        # 40+ tests for MC05
├── test_causal_verb_extractor.py            # 50+ tests for MC08
├── test_institutional_ner_extractor.py      # 45+ tests for MC09
└── README.md                                # This file
```

## Running Tests

### Run All Extractor Tests

```bash
cd /home/user/FARFAN_MPP
pytest src/farfan_pipeline/infrastructure/extractors/tests/ -v
```

### Run Specific Extractor Tests

```bash
# Financial Chain Extractor only
pytest src/farfan_pipeline/infrastructure/extractors/tests/test_financial_chain_extractor.py -v

# Causal Verb Extractor only
pytest src/farfan_pipeline/infrastructure/extractors/tests/test_causal_verb_extractor.py -v

# Institutional NER only
pytest src/farfan_pipeline/infrastructure/extractors/tests/test_institutional_ner_extractor.py -v
```

### Run Tests by Category

```bash
# Empirical validation tests only
pytest -m empirical -v

# Unit tests only
pytest -m unit -v

# Integration tests
pytest -m integration -v
```

### Run with Coverage

```bash
pytest src/farfan_pipeline/infrastructure/extractors/tests/ \
    --cov=farfan_pipeline.infrastructure.extractors \
    --cov-report=html \
    --cov-report=term
```

Coverage report will be generated in `htmlcov/index.html`.

## Test Categories

### 1. Empirical Gold Standard Tests

Tests based on real examples from the 14-plan corpus:

- **Cajibío Plan PPI**: $288,087 millones total budget
- **Bosconia Hierarchy**: 57 programs, 352 metas
- **Corinto Triplets**: Complete LB→Meta chains
- **Quibdó Institutions**: Highest institutional network density

### 2. Pattern Extraction Tests

Validate regex patterns and extraction logic:

- Currency normalization (millones, billones)
- Verb conjugations (fortalecer → fortalece, fortalecerá)
- Entity matching (exact, acronym, fuzzy)

### 3. Confidence Scoring Tests

Verify confidence thresholds align with empirical calibration:

- Complete chains: confidence ≥ 0.85
- Partial chains: confidence ≥ 0.65
- Strong causal verbs: confidence ≥ 0.75

### 4. Validation Tests

Auto-validation against empirical rules:

- Frequency ranges (e.g., 285±98 montos/plan)
- Completeness requirements
- Metadata generation

### 5. Edge Case & Robustness Tests

Handle edge cases gracefully:

- Empty text
- Text without target signals
- Special characters and accents
- Case-insensitive matching

## Empirical Baseline Metrics

Tests validate extractors against these empirical baselines:

### Financial Chain (MC05)
- **Montos/plan**: 285 ± 98 (range: 20-377)
- **Fuentes/plan**: 7 ± 2 (range: 5-13)
- **Pattern confidence**: 0.90 (monto), 0.92 (fuente)

### Causal Verbs (MC08)
- **Top verb frequency**: fortalecer (52±23), implementar (51±21)
- **Causal connectors**: mediante (22/plan), para lograr (15/plan)
- **Pattern confidence**: 0.82 (with context validation)

### Institutional Network (MC09)
- **DNP mentions**: 15 ± 8 (range: 5-24)
- **DANE mentions**: 10 ± 5 (range: 3-13)
- **Alcaldía mentions**: 420 ± 180 (very high frequency)
- **Pattern confidence**: 0.94 (national), 0.89 (territorial)

## Test Fixtures

Key fixtures provided in `conftest.py`:

- `calibration_data`: Full empirical calibration JSON
- `gold_standards`: Gold standard examples by signal type
- `financial_chain_examples`: Cajibío, Corinto PPI examples
- `causal_verb_text_samples`: Real PDT plan causal texts
- `institutional_entities_samples`: Entity mention examples

## Expected Test Results

### Passing Criteria

- **Financial Chain**: 38/40+ tests pass (≥95%)
- **Causal Verb**: 48/50+ tests pass (≥96%)
- **Institutional NER**: 43/45+ tests pass (≥95%)

### Known Limitations

Some tests may require adjustments based on:

- Extractor implementation details (e.g., argument extraction depth)
- Pattern coverage (some edge cases may need additional patterns)
- Context window sizes (proximity-based linking)

## Continuous Validation

These tests serve as:

1. **Regression prevention**: Ensure extractors don't degrade
2. **Empirical alignment**: Validate against real-world data
3. **Performance benchmarks**: Track precision/recall over time
4. **Documentation**: Executable specification of extractor behavior

## Updating Tests

When empirical corpus is updated:

1. Update `extractor_calibration.json` with new gold standards
2. Re-run test generation (if automated)
3. Verify new tests pass with current extractors
4. Adjust extractors if empirical patterns change

## Integration with CI/CD

Recommended CI pipeline:

```yaml
test_extractors:
  script:
    - pytest src/farfan_pipeline/infrastructure/extractors/tests/ -v --tb=short
  coverage:
    - pytest --cov=farfan_pipeline.infrastructure.extractors --cov-report=term
  artifacts:
    - htmlcov/
```

## Contact

For questions about extractor tests:

- **Framework**: CQC Extractor Excellence Framework v2.0.0
- **Author**: Empirical Corpus Integration Team
- **Date**: 2026-01-06
- **Version**: 2.0.0

---

**Excellence Through Empirical Validation** 🎯
