# Calibration Orchestrator Examples

This directory contains examples demonstrating the CalibrationOrchestrator functionality.

## Examples

### 1. Basic Calibration (`example_basic_calibration.py`)
Demonstrates basic usage of CalibrationOrchestrator for single method calibration.

**Key Concepts:**
- Loading orchestrator from config directory
- Creating CalibrationSubject and EvidenceStore
- Performing calibration
- Inspecting results

**Run:**
```bash
python tests/orchestration/orchestration_examples/example_basic_calibration.py
```

### 2. Role-Based Layer Activation (`example_role_based_activation.py`)
Shows how different roles activate different layers in calibration.

**Key Concepts:**
- ROLE_LAYER_REQUIREMENTS mapping
- Layer activation by role
- Comparing layer counts across roles

**Roles Demonstrated:**
- INGEST_PDM (4 layers)
- STRUCTURE (4 layers)
- SCORE_Q (8 layers)
- AGGREGATE (6 layers)
- REPORT (4 layers)
- META_TOOL (3 layers)

**Run:**
```bash
python tests/orchestration/orchestration_examples/example_role_based_activation.py
```

### 3. Batch Calibration (`example_batch_calibration.py`)
Demonstrates calibrating multiple methods in batch with result aggregation.

**Key Concepts:**
- Batch processing multiple methods
- Result aggregation and statistics
- Grouping results by role

**Run:**
```bash
python tests/orchestration/orchestration_examples/example_batch_calibration.py
```

### 4. Layer Evaluator Details (`example_layer_evaluator_detail.py`)
Shows individual layer evaluator behavior and score computation.

**Key Concepts:**
- Individual layer evaluation
- Understanding each layer's purpose
- Layer score computation

**Layers Demonstrated:**
- @b (Base Quality)
- @chain (Chain Compatibility)
- @u (Unit/Document Quality)
- @q (Question Appropriateness)
- @d (Dimension Alignment)
- @p (Policy Area Fit)
- @C (Contract Compliance)
- @m (Meta/Governance)

**Run:**
```bash
python tests/orchestration/orchestration_examples/example_layer_evaluator_detail.py
```

### 5. Completeness Validation (`example_completeness_validation.py`)
Demonstrates completeness validation ensuring all required layers are computed.

**Key Concepts:**
- Completeness validation
- Missing layer detection
- Error handling

**Run:**
```bash
python tests/orchestration/orchestration_examples/example_completeness_validation.py
```

## Role-Based Layer Requirements

The calibration system uses role-based layer activation:

| Role | Layers | Count |
|------|--------|-------|
| INGEST_PDM | @b, @chain, @u, @m | 4 |
| STRUCTURE | @b, @chain, @u, @m | 4 |
| EXTRACT | @b, @chain, @u, @m | 4 |
| SCORE_Q | @b, @chain, @q, @d, @p, @C, @u, @m | 8 |
| AGGREGATE | @b, @chain, @d, @p, @C, @m | 6 |
| REPORT | @b, @chain, @C, @m | 4 |
| META_TOOL | @b, @chain, @m | 3 |
| TRANSFORM | @b, @chain, @m | 3 |

## Architecture

```
CalibrationOrchestrator
├── LayerRequirementsResolver
│   └── Determines active layers based on role
├── Layer Evaluators (8)
│   ├── BaseLayerEvaluator (@b)
│   ├── ChainLayerEvaluator (@chain)
│   ├── UnitLayerEvaluator (@u)
│   ├── QuestionLayerEvaluator (@q)
│   ├── DimensionLayerEvaluator (@d)
│   ├── PolicyLayerEvaluator (@p)
│   ├── CongruenceLayerEvaluator (@C)
│   └── MetaLayerEvaluator (@m)
└── ChoquetAggregator
    └── Fuses layer scores using Choquet integral
```

## Configuration Files

The orchestrator loads from:
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/
├── COHORT_2024_intrinsic_calibration.json
├── COHORT_2024_questionnaire_monolith.json
├── COHORT_2024_fusion_weights.json
├── COHORT_2024_method_compatibility.json
└── COHORT_2024_canonical_method_inventory.json
```

## Usage Pattern

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

# Prepare subject and evidence
subject = CalibrationSubject(
    method_id="farfan.executor.D1Q1",
    role="SCORE_Q",
    context={"phase": "scoring"}
)

evidence = EvidenceStore(
    pdt_structure={"chunk_count": 60, "completeness": 0.85, "structure_quality": 0.9},
    document_quality=0.85,
    question_id="Q001",
    dimension_id="D1",
    policy_area_id="PA1"
)

# Calibrate
result = orchestrator.calibrate(subject, evidence)

# Inspect results
print(f"Final Score: {result.final_score}")
print(f"Active Layers: {len(result.active_layers)}")
for layer_id, score in result.layer_scores.items():
    print(f"  {layer_id.value}: {score:.4f}")
```

## Testing

Run all tests:
```bash
pytest tests/orchestration/test_calibration_orchestrator.py -v
```

Run specific test:
```bash
pytest tests/orchestration/test_calibration_orchestrator.py::test_calibrate_score_method -v
```
