# Calibration System Test Suite

Comprehensive test suite for the F.A.R.F.A.N calibration system with property-based validation, integration tests, regression tests, and performance benchmarks.

## Test Structure

### Unit Tests
- `test_base_layer.py` - Base layer (@b) computation tests
  - b_theory/b_impl/b_deploy computation
  - Weight normalization
  - Role-specific requirements
  
- `test_unit_layer.py` - Unit layer (@u) computation tests
  - S/M/I/P computation with PDT fixtures
  - Unit quality U(pdt) computation
  - Transformation functions (g_INGEST, g_STRUCT, g_QA)
  
- `test_contextual_layers.py` - Contextual layers (@q, @d, @p) tests
  - Question/dimension/policy compatibility scoring
  - Discrete scoring levels (1.0, 0.7, 0.3, 0.1, 0.0)
  - Anti-universality constraint validation
  
- `test_congruence_layer.py` - Congruence layer (@C) tests
  - c_scale/c_sem/c_fusion computation
  - Ensemble validation with examples
  - Jaccard similarity for semantic congruence
  
- `test_chain_layer.py` - Chain layer (@chain) tests
  - Signature validation with discrete scoring cases
  - Schema compatibility checking
  - Required/optional input validation
  
- `test_meta_layer.py` - Meta layer (@m) tests
  - m_transp/m_gov/m_cost with governance artifacts
  - Discrete scoring levels
  - Weighted aggregation (0.5·transp + 0.4·gov + 0.1·cost)
  
- `test_choquet_aggregation.py` - Choquet integral tests
  - Fusion formula with interaction terms
  - Linear and interaction contributions
  - Weight normalization
  
- `test_orchestrator.py` - Orchestrator tests
  - End-to-end flow with role-based layer activation
  - Certificate generation
  - Error handling

### Property-Based Tests
- `test_property_based.py` - Hypothesis-based tests
  - **Boundedness**: ∀inputs 0 ≤ output ≤ 1
  - **Monotonicity**: ∀layers increasing score → increasing Cal(I)
  - **Normalization**: ∀configs sum(weights) = 1.0
  - **Determinism**: Same inputs always produce same outputs
  - **Interaction properties**: Symmetric min operator, weakest link capture

### Integration Tests
- `integration/test_full_calibration_flow.py` - Complete calibration flow
  - Run complete calibration on sample method with all layers
  - Validate certificate structure and signature
  - Performance benchmarks
  
- `integration/test_config_loading.py` - Configuration loading
  - Verify all configs load correctly and validate
  - Weight normalization checks
  - Schema validation
  
- `integration/test_certificate_generation.py` - Certificate validation
  - Validate certificate structure and signature
  - Timestamp formatting
  - Serialization roundtrip

### Regression Tests
- `test_regression.py` - Baseline calibration results
  - Store baseline calibration results
  - Verify new runs match within tolerance
  - Edge case handling

### Performance Tests
- `test_performance.py` - Performance benchmarks
  - Single method calibration time (target <1s for @b, <5s for full)
  - Batch calibration of 1995 methods
  - Memory efficiency
  - Scalability tests

## Running Tests

### Run All Tests
```bash
pytest tests/calibration/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/calibration/ -v -m "not integration and not regression and not performance"

# Integration tests
pytest tests/calibration/ -v -m integration

# Property-based tests
pytest tests/calibration/ -v -m property

# Regression tests
pytest tests/calibration/ -v -m regression

# Performance tests (includes slow tests)
pytest tests/calibration/ -v -m performance

# Exclude slow tests
pytest tests/calibration/ -v -m "not slow"
```

### Run with Coverage
```bash
pytest tests/calibration/ --cov=src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization --cov-report=html --cov-report=term
```

### Generate HTML Report
```bash
pytest tests/calibration/ --html=tests/calibration/test_report.html --self-contained-html
```

## Test Fixtures

Test fixtures are located in `test_fixtures/`:
- `sample_methods.json` - Sample method definitions with base metrics and contexts
- `sample_pdt_data.json` - Sample PDT data with various quality levels
- `sample_ensemble_configs.json` - Sample ensemble configurations
- `sample_governance_artifacts.json` - Sample governance artifacts

## Mathematical Properties Tested

### Boundedness
All layer scores and final calibration score must satisfy: 0 ≤ score ≤ 1

### Monotonicity
For any layer ℓ: if x_ℓ increases, then Cal(I) must not decrease

### Normalization
Linear and interaction weights must sum to 1.0:
```
Σ(a_ℓ) + Σ(a_ℓk) = 1.0
```

### Choquet Integral Formula
```
Cal(I) = Σ_{ℓ ∈ L(M)} a_ℓ · x_ℓ(I) + Σ_{(ℓ,k) ∈ S_int} a_ℓk · min(x_ℓ(I), x_k(I))
```

## Coverage Goals

Target: 100% coverage of calibration system components
- Base layer computation
- Unit layer evaluation
- Contextual layer scoring
- Congruence layer validation
- Chain layer verification
- Meta layer assessment
- Choquet aggregation
- Orchestration logic

## Test Markers

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.property` - Property-based tests with Hypothesis
- `@pytest.mark.regression` - Regression tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.updated` - Updated tests compatible with current architecture
- `@pytest.mark.core` - Critical core tests

## Continuous Integration

Tests should be run on:
- Every commit to feature branches
- Before merging to main branch
- As part of release validation

## Contributing

When adding new calibration features:
1. Add unit tests for the feature
2. Add property-based tests if applicable
3. Update integration tests if it affects the full flow
4. Add regression test with baseline result
5. Consider performance impact and add benchmark if needed
6. Update this README with new test descriptions
