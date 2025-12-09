# CalibrationOrchestrator Documentation

## Overview

The **CalibrationOrchestrator** is an extramodule within the core orchestrator that provides role-based layer activation for method calibration. It evaluates method quality across 8 distinct layers and fuses scores using Choquet aggregation.

## Architecture

```
CalibrationOrchestrator (extramodule in core orchestrator)
│
├── Configuration Loaders
│   ├── intrinsic_calibration.json       (method quality scores)
│   ├── questionnaire_monolith.json      (question/dimension/policy mappings)
│   ├── fusion_specification.json        (Choquet weights and interactions)
│   ├── method_compatibility.json        (chain compatibility scores)
│   └── canonical_method_catalog.json    (governance metadata)
│
├── LayerRequirementsResolver
│   └── Determines active layers based on method role
│
├── Layer Evaluators (8 total)
│   ├── BaseLayerEvaluator        (@b)  - Code quality (theory, impl, deploy)
│   ├── ChainLayerEvaluator       (@chain) - Method wiring compatibility
│   ├── UnitLayerEvaluator        (@u)  - Document/PDT quality
│   ├── QuestionLayerEvaluator    (@q)  - Question appropriateness
│   ├── DimensionLayerEvaluator   (@d)  - Dimension alignment
│   ├── PolicyLayerEvaluator      (@p)  - Policy area fit
│   ├── CongruenceLayerEvaluator  (@C)  - Contract compliance
│   └── MetaLayerEvaluator        (@m)  - Governance quality
│
├── ChoquetAggregator
│   └── Fuses layer scores using Choquet integral
│
└── Completeness Validator
    └── Ensures all required layers computed for role
```

## Role-Based Layer Requirements

The calibration system activates different layers based on method role:

| Role | Active Layers | Count | Description |
|------|--------------|-------|-------------|
| **INGEST_PDM** | @b, @chain, @u, @m | 4 | Document ingestion methods |
| **STRUCTURE** | @b, @chain, @u, @m | 4 | Document structuring methods |
| **EXTRACT** | @b, @chain, @u, @m | 4 | Content extraction methods |
| **SCORE_Q** | @b, @chain, @q, @d, @p, @C, @u, @m | 8 | Question scoring methods (all layers) |
| **AGGREGATE** | @b, @chain, @d, @p, @C, @m | 6 | Aggregation methods |
| **REPORT** | @b, @chain, @C, @m | 4 | Reporting methods |
| **META_TOOL** | @b, @chain, @m | 3 | Meta-analysis tools |
| **TRANSFORM** | @b, @chain, @m | 3 | Data transformation methods |

## Layer Descriptions

### @b - Base Quality Layer
Evaluates intrinsic code quality:
- **b_theory**: Statistical validity, logical consistency, assumptions
- **b_impl**: Test coverage, type annotations, error handling, documentation
- **b_deploy**: Validation runs, stability coefficient, failure rate

**Formula**: `x_@b = 0.4·b_theory + 0.35·b_impl + 0.25·b_deploy`

### @chain - Chain Compatibility Layer
Evaluates method wiring and orchestration compatibility:
- Type compatibility with upstream/downstream methods
- Schema alignment
- Contract compliance

### @u - Unit/Document Quality Layer
Evaluates PDT structure quality:
- Document chunk count and coverage
- Structural completeness
- Semantic structure quality

### @q - Question Appropriateness Layer
Evaluates method fit for specific question:
- Method inclusion in question's method_sets
- Historical performance on question type
- Question-method alignment score

### @d - Dimension Alignment Layer
Evaluates method alignment with analytical dimension:
- Dimension-specific method suitability
- Historical dimension performance
- Dimension context match

### @p - Policy Area Fit Layer
Evaluates method fit for policy area:
- Policy area coverage
- Domain expertise alignment
- Historical policy area performance

### @C - Contract Compliance Layer
Evaluates contract and specification compliance:
- Input/output contract adherence
- Signature validation
- Specification conformance

### @m - Meta/Governance Layer
Evaluates governance and meta-quality:
- Governance maturity
- Maintenance status
- Documentation quality
- Community support

## Calibration Flow

```python
def calibrate(subject: CalibrationSubject, evidence: EvidenceStore) -> CalibrationResult:
    # 1. Determine active layers
    active_layers = layer_resolver.get_required_layers(subject.method_id)
    
    # 2. Evaluate each active layer
    layer_scores = {}
    if LayerID.BASE in active_layers:
        layer_scores[LayerID.BASE] = base_evaluator.evaluate(subject.method_id)
    if LayerID.CHAIN in active_layers:
        layer_scores[LayerID.CHAIN] = chain_evaluator.evaluate(subject.method_id)
    if LayerID.UNIT in active_layers:
        layer_scores[LayerID.UNIT] = unit_evaluator.evaluate(evidence.pdt_structure)
    # ... (continue for all active layers)
    
    # 3. Validate completeness
    validate_completeness(active_layers, layer_scores)
    
    # 4. Apply Choquet fusion
    final_score = choquet_aggregator.aggregate(subject, layer_scores)
    
    # 5. Return result
    return CalibrationResult(
        final_score=final_score,
        layer_scores=layer_scores,
        active_layers=active_layers,
        role=subject.role,
        method_id=subject.method_id
    )
```

## Choquet Aggregation

The calibration system uses Choquet integral for non-additive aggregation:

**Formula**: `Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))`

**Components**:
- `a_ℓ`: Linear weights for individual layers
- `a_ℓk`: Interaction weights for layer pairs
- `x_ℓ`: Layer scores

**Constraints**:
- `a_ℓ ≥ 0` (non-negative weights)
- `a_ℓk ≥ 0` (non-negative interactions)
- `Σ(a_ℓ) + Σ(a_ℓk) = 1.0` (normalization)
- `Cal(I) ∈ [0,1]` (bounded output)

**Key Interactions** (for SCORE_Q role):
- `@u, @chain`: Document quality affects chain compatibility
- `@chain, @C`: Chain compatibility interacts with contract compliance
- `@q, @d`: Question appropriateness interacts with dimension alignment

## Usage

### Basic Usage

```python
from pathlib import Path
from src.orchestration.calibration_orchestrator import (
    CalibrationOrchestrator,
    CalibrationSubject,
    EvidenceStore,
)

# Load orchestrator
config_dir = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
orchestrator = CalibrationOrchestrator.from_config_dir(config_dir)

# Prepare calibration subject
subject = CalibrationSubject(
    method_id="farfan.executor.D1Q1",
    role="SCORE_Q",
    context={"phase": "scoring", "question_id": "Q001"}
)

# Prepare evidence
evidence = EvidenceStore(
    pdt_structure={
        "chunk_count": 60,
        "completeness": 0.85,
        "structure_quality": 0.9
    },
    document_quality=0.85,
    question_id="Q001",
    dimension_id="D1",
    policy_area_id="PA1"
)

# Calibrate
result = orchestrator.calibrate(subject, evidence)

# Inspect results
print(f"Final Score: {result.final_score:.4f}")
print(f"Active Layers: {len(result.active_layers)}")
for layer_id, score in result.layer_scores.items():
    print(f"  {layer_id.value}: {score:.4f}")
```

### Integration with Main Orchestrator

The CalibrationOrchestrator is automatically integrated into the main Orchestrator:

```python
from src.orchestration.orchestrator import Orchestrator

# Orchestrator auto-loads CalibrationOrchestrator if configs available
orchestrator = Orchestrator(...)

# Use calibration during execution
calibration_result = orchestrator.calibrate_method(
    method_id="farfan.executor.D1Q1",
    role="SCORE_Q",
    context={"question_id": "Q001"},
    pdt_structure=document.metadata
)

if calibration_result:
    print(f"Method calibration: {calibration_result['final_score']:.4f}")
```

### Batch Calibration

```python
methods = [
    ("farfan.executor.D1Q1", "SCORE_Q"),
    ("farfan.executor.D2Q1", "SCORE_Q"),
    ("farfan.aggregator.dimension", "AGGREGATE"),
]

results = []
for method_id, role in methods:
    subject = CalibrationSubject(method_id=method_id, role=role, context={})
    result = orchestrator.calibrate(subject, evidence)
    results.append(result)

# Aggregate statistics
avg_score = sum(r.final_score for r in results) / len(results)
print(f"Average calibration score: {avg_score:.4f}")
```

## Configuration Files

### intrinsic_calibration.json
```json
{
  "methods": {
    "farfan.executor.D1Q1": {
      "role": "SCORE_Q",
      "b_theory": 0.75,
      "b_impl": 0.85,
      "b_deploy": 0.80
    }
  },
  "_base_weights": {
    "w_theory": 0.4,
    "w_impl": 0.35,
    "w_deploy": 0.25
  }
}
```

### fusion_specification.json
```json
{
  "role_fusion_parameters": {
    "SCORE_Q": {
      "linear_weights": {
        "@b": 0.17,
        "@chain": 0.13,
        "@q": 0.08,
        "@d": 0.07,
        "@p": 0.06,
        "@C": 0.08,
        "@u": 0.04,
        "@m": 0.04
      },
      "interaction_weights": {
        "@u,@chain": 0.13,
        "@chain,@C": 0.10,
        "@q,@d": 0.10
      }
    }
  }
}
```

## Testing

```bash
# Run all calibration tests
pytest tests/orchestration/test_calibration_orchestrator.py -v

# Run specific test
pytest tests/orchestration/test_calibration_orchestrator.py::test_calibrate_score_method -v

# Run with coverage
pytest tests/orchestration/test_calibration_orchestrator.py --cov=src.orchestration.calibration_orchestrator
```

## Examples

See `tests/orchestration/orchestration_examples/` for complete examples:

1. **example_basic_calibration.py** - Basic usage
2. **example_role_based_activation.py** - Role-based layer activation
3. **example_batch_calibration.py** - Batch processing
4. **example_layer_evaluator_detail.py** - Individual layer evaluation
5. **example_completeness_validation.py** - Completeness validation

## API Reference

### CalibrationOrchestrator

**`__init__(intrinsic_calibration, questionnaire_monolith, fusion_specification, method_compatibility, canonical_method_catalog)`**

Initialize orchestrator with all configuration data.

**`from_config_dir(config_dir: Path) -> CalibrationOrchestrator`**

Class method to load orchestrator from configuration directory.

**`calibrate(subject: CalibrationSubject, evidence: EvidenceStore) -> CalibrationResult`**

Calibrate method with role-based layer activation.

### CalibrationSubject (TypedDict)

- `method_id: str` - Method identifier
- `role: str` - Method role (INGEST_PDM, SCORE_Q, etc.)
- `context: Dict[str, Any]` - Execution context

### EvidenceStore (TypedDict)

- `pdt_structure: Dict[str, Any]` - PDT structure metadata
- `document_quality: float` - Overall document quality
- `question_id: str | None` - Question identifier
- `dimension_id: str | None` - Dimension identifier
- `policy_area_id: str | None` - Policy area identifier

### CalibrationResult (dataclass)

- `final_score: float` - Final calibration score [0,1]
- `layer_scores: Dict[LayerID, float]` - Individual layer scores
- `active_layers: Set[LayerID]` - Layers activated for this role
- `role: str` - Method role
- `method_id: str` - Method identifier
- `metadata: Dict[str, Any]` - Additional metadata

## Error Handling

### Completeness Validation

If required layers are missing, raises:
```python
ValueError: Calibration completeness check failed for {method_id} (role={role}): 
            missing layers: {missing_layers}
```

### Score Bounds Validation

If final score out of bounds [0,1], raises:
```python
ValueError: Final score {score} not in [0,1]
```

## Performance Considerations

- **Layer evaluation**: O(1) for most layers, O(n) for question/dimension lookups
- **Choquet aggregation**: O(k) where k is number of active layers (max 8)
- **Batch processing**: Linear in number of methods
- **Memory**: Minimal, configs loaded once at initialization

## Future Enhancements

1. **Caching**: Cache layer scores for repeated method calibrations
2. **Parallel evaluation**: Parallelize layer evaluation for batch operations
3. **Adaptive weights**: Learn optimal Choquet weights from historical data
4. **Layer interpolation**: Interpolate missing layer scores based on similar methods
5. **Time-series tracking**: Track calibration scores over time for quality trends

## References

- Mathematical foundations: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/mathematical_foundations_capax_system.md`
- Layer assignment: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_layer_assignment.py`
- Integration: `src/orchestration/orchestrator.py`
- Tests: `tests/orchestration/test_calibration_orchestrator.py`
