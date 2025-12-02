# Layer Assignment System Implementation

## Overview

Successfully implemented calibration layer assignment system with extended LAYER_REQUIREMENTS table for the F.A.R.F.A.N. mechanistic policy pipeline.

## Files Created

### 1. Core Module: `src/farfan_pipeline/core/calibration/layer_assignment.py`
- **LAYER_REQUIREMENTS**: Comprehensive table defining layer assignments for all roles
  - `ingest` → [@b, @chain, @u, @m]
  - `processor` → [@b, @chain, @u, @m]
  - `analyzer` → [@b, @chain, @q, @d, @p, @C, @u, @m] (8 layers)
  - `score` → [@b, @chain, @q, @d, @p, @C, @u, @m] (8 layers)
  - `executor` → [@b, @chain, @q, @d, @p, @C, @u, @m] (8 layers)
  - `utility` → [@b, @chain, @m]
  - `orchestrator` → [@b, @chain, @m]
  - `core` → [@b, @chain, @q, @d, @p, @C, @u, @m] (8 layers)
  - `extractor` → [@b, @chain, @u, @m]

- **CHOQUET_WEIGHTS**: Linear weights for each layer
  - @b: 0.17 (Code quality/base theory)
  - @chain: 0.13 (Method wiring/orchestration)
  - @q: 0.08 (Question appropriateness)
  - @d: 0.07 (Dimension alignment)
  - @p: 0.06 (Policy area fit)
  - @C: 0.08 (Contract compliance)
  - @u: 0.04 (Document quality)
  - @m: 0.04 (Governance maturity)

- **CHOQUET_INTERACTION_WEIGHTS**: Non-linear interaction terms
  - (@u, @chain): 0.13
  - (@chain, @C): 0.10
  - (@q, @d): 0.10

- **Functions**:
  - `identify_executors()`: Regex-based pattern matching for D[1-6]Q[1-5] executors
  - `assign_layers_and_weights()`: Layer and weight assignment with normalization
  - `generate_canonical_inventory()`: Full inventory generation with validation

### 2. Generation Script: `scripts/generate_layer_inventory.py`
- Generates `config/canonic_inventorry_methods_layers.json`
- Validates:
  - Minimum 30 executors identified
  - No numeric scores in output (metadata only)
  - All executors have 8 layers
  - Weight sums equal 1.0

### 3. Configuration Output: `config/canonic_inventorry_methods_layers.json`
- **Total Methods**: 30 executors (D1Q1-D6Q5)
- **Structure**: Pure metadata (NO SCORES)
  ```json
  {
    "_metadata": { version, description, layer_system },
    "methods": {
      "farfan_pipeline.core.orchestrator.executors.D1_Q1_...": {
        "method_id": "...",
        "role": "executor",
        "dimension": "D1",
        "question": "Q1",
        "layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
        "weights": { /* 8 layer weights */ },
        "interaction_weights": { /* Choquet interaction terms */ },
        "aggregator_type": "choquet"
      }
    }
  }
  ```

### 4. Test Suite: `tests/test_layer_assignment.py`
- **22 comprehensive tests** covering:
  - Executor count (≥30)
  - Layer mapping completeness
  - 8-layer requirement for executors
  - No numeric scores in JSON
  - Weight normalization (sum = 1.0)
  - Layer name validation
  - Metadata field requirements
  - Pattern matching (D[1-6]Q[1-5])
  - Choquet aggregator type
  - Interaction weight validation
  - LAYER_REQUIREMENTS table verification

## Verification Results

### Test Execution
```bash
pytest tests/test_layer_assignment.py -v
```
**Result**: ✅ 22/22 tests PASSED

### Lint Execution
```bash
ruff check [files]
black --check [files]
```
**Result**: ✅ Clean (minor acceptable warnings for magic numbers and E402)

### Build Execution
```bash
pip install -e .
```
**Result**: ✅ Successfully installed

## Executors Identified

Successfully identified **30 executors** via D[1-6]Q[1-5] pattern:

**Dimension 1 (D1)**: Diagnostics & Inputs
- D1_Q1_QuantitativeBaselineExtractor
- D1_Q2_ProblemDimensioningAnalyzer
- D1_Q3_BudgetAllocationTracer
- D1_Q4_InstitutionalCapacityIdentifier
- D1_Q5_ScopeJustificationValidator

**Dimension 2 (D2)**: Planning & Design
- D2_Q1_StructuredPlanningValidator
- D2_Q2_InterventionLogicInferencer
- D2_Q3_RootCauseLinkageAnalyzer
- D2_Q4_RiskManagementAnalyzer
- D2_Q5_StrategicCoherenceEvaluator

**Dimension 3 (D3)**: Operationalization
- D3_Q1_IndicatorQualityValidator
- D3_Q2_TargetProportionalityAnalyzer
- D3_Q3_TraceabilityValidator
- D3_Q4_TechnicalFeasibilityEvaluator
- D3_Q5_OutputOutcomeLinkageAnalyzer

**Dimension 4 (D4)**: Results Framework
- D4_Q1_OutcomeMetricsValidator
- D4_Q2_CausalChainValidator
- D4_Q3_AmbitionJustificationAnalyzer
- D4_Q4_ProblemSolvencyEvaluator
- D4_Q5_VerticalAlignmentValidator

**Dimension 5 (D5)**: Impact Assessment
- D5_Q1_LongTermVisionAnalyzer
- D5_Q2_CompositeMeasurementValidator
- D5_Q3_IntangibleMeasurementAnalyzer
- D5_Q4_SystemicRiskEvaluator
- D5_Q5_RealismAndSideEffectsAnalyzer

**Dimension 6 (D6)**: Theory of Change
- D6_Q1_ExplicitTheoryBuilder
- D6_Q2_LogicalProportionalityValidator
- D6_Q3_ValidationTestingAnalyzer
- D6_Q4_FeedbackLoopAnalyzer
- D6_Q5_ContextualAdaptabilityEvaluator

## Layer System

### 8 Calibration Layers
1. **@b**: Code quality (base theory) - Statistical/logical foundation
2. **@chain**: Method wiring/orchestration - Integration quality
3. **@q**: Question appropriateness - Alignment with analytical question
4. **@d**: Dimension alignment - Fit with policy dimension
5. **@p**: Policy area fit - Relevance to policy domain
6. **@C**: Contract compliance - Adherence to interface contracts
7. **@u**: Document quality - Input document reliability
8. **@m**: Governance maturity - Process stability

### Choquet Integral Aggregation
- **Linear component**: Weighted sum of individual layers (67%)
- **Interaction component**: Non-linear "weakest link" effects (33%)
- **Key interactions**:
  - Document quality (@u) × Wiring (@chain) = 0.13
  - Wiring (@chain) × Contracts (@C) = 0.10
  - Question (@q) × Dimension (@d) = 0.10

## Failure Conditions Implemented

The system **ABORTS** with 'layer assignment corrupted' error if:

1. ❌ <30 executors identified in pattern matching
2. ❌ Any method lacks layer mapping
3. ❌ Any executor has <8 layers
4. ❌ JSON contains numeric scores (outside weights/interaction_weights)
5. ❌ Sum of weights per executor ≠ 1.0 (tolerance: ±0.01)

## Usage

### Generate Configuration
```bash
python scripts/generate_layer_inventory.py
```

### Run Tests
```bash
pytest tests/test_layer_assignment.py -v
```

### Import in Code
```python
from farfan_pipeline.core.calibration.layer_assignment import (
    LAYER_REQUIREMENTS,
    CHOQUET_WEIGHTS,
    identify_executors,
    assign_layers_and_weights,
    generate_canonical_inventory
)
```

## Compliance

✅ All verification conditions met:
1. All methods have layer mappings
2. All executors have exactly 8 layers
3. JSON contains ONLY metadata (no numeric scores outside weights)
4. Sum of weights per executor = 1.0

✅ No failure conditions triggered:
- 30 executors successfully identified
- No scores in JSON output
- All weight sums normalized to 1.0

## Files Summary
- **Module**: `src/farfan_pipeline/core/calibration/layer_assignment.py` (211 lines)
- **Script**: `scripts/generate_layer_inventory.py` (64 lines)
- **Config**: `config/canonic_inventorry_methods_layers.json` (978 lines)
- **Tests**: `tests/test_layer_assignment.py` (297 lines)
- **Total**: 1,550 lines of code + configuration
