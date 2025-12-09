# Calibration Orchestrator Implementation Summary

## Overview

The **CalibrationOrchestrator** has been fully implemented as an extramodule within the Core Orchestrator, providing role-based layer activation for method calibration.

## Implementation Location

- **Main Module**: `src/orchestration/calibration_orchestrator.py`
- **Integration**: Integrated into `src/orchestration/orchestrator.py` (main Orchestrator class)
- **Tests**: `tests/orchestration/test_calibration_orchestrator.py`
- **Examples**: `tests/orchestration/orchestration_examples/`
- **Configuration**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/`

## Core Components Implemented

### 1. LayerID Enum
8 layer identifiers:
- `@b` (BASE) - Base quality
- `@chain` (CHAIN) - Chain compatibility
- `@u` (UNIT) - Unit/document quality
- `@q` (QUESTION) - Question appropriateness
- `@d` (DIMENSION) - Dimension alignment
- `@p` (POLICY) - Policy area fit
- `@C` (CONGRUENCE) - Contract compliance
- `@m` (META) - Meta/governance

### 2. Role-Based Layer Requirements

Implemented for 8 roles as specified:

```python
ROLE_LAYER_REQUIREMENTS = {
    "INGEST_PDM": {BASE, CHAIN, UNIT, META},                                    # 4 layers
    "STRUCTURE": {BASE, CHAIN, UNIT, META},                                     # 4 layers
    "EXTRACT": {BASE, CHAIN, UNIT, META},                                       # 4 layers
    "SCORE_Q": {BASE, CHAIN, QUESTION, DIMENSION, POLICY, CONGRUENCE, UNIT, META},  # 8 layers
    "AGGREGATE": {BASE, CHAIN, DIMENSION, POLICY, CONGRUENCE, META},            # 6 layers
    "REPORT": {BASE, CHAIN, CONGRUENCE, META},                                  # 4 layers
    "META_TOOL": {BASE, CHAIN, META},                                           # 3 layers
    "TRANSFORM": {BASE, CHAIN, META},                                           # 3 layers
}
```

### 3. LayerRequirementsResolver

**Purpose**: Determines required layers based on method role

**Methods**:
- `get_required_layers(method_id: str) -> Set[LayerID]`: Returns active layers for method
- `_get_method_role(method_id: str) -> str`: Extracts role from config or infers from method_id

**Features**:
- Reads role from intrinsic_calibration.json
- Falls back to intelligent role inference based on method naming
- Defaults to SCORE_Q for unknown methods

### 4. Layer Evaluators (8 Evaluators)

#### BaseLayerEvaluator (@b)
- Evaluates base quality (theory, implementation, deployment)
- Formula: `w_theory * b_theory + w_impl * b_impl + w_deploy * b_deploy`
- Input: method_id
- Output: [0.0, 1.0]

#### ChainLayerEvaluator (@chain)
- Evaluates chain compatibility
- Input: method_id
- Output: chain_compatibility_score from config

#### UnitLayerEvaluator (@u)
- Evaluates document/unit quality
- Considers: chunk_count, completeness, structure_quality
- Input: pdt_structure dict
- Output: weighted score based on document metrics

#### QuestionLayerEvaluator (@q)
- Evaluates question appropriateness
- Checks if method is listed in question's method_sets
- Input: method_id, question_id
- Output: 0.9 (matched), 0.6 (listed), 0.5 (default)

#### DimensionLayerEvaluator (@d)
- Evaluates dimension alignment
- Input: method_id, dimension_id
- Output: 0.85 (found), 0.6 (default)

#### PolicyLayerEvaluator (@p)
- Evaluates policy area fit
- Input: method_id, policy_area_id
- Output: 0.85 (found), 0.6 (default)

#### CongruenceLayerEvaluator (@C)
- Evaluates contract compliance
- Checks if method in fusion specification
- Input: method_id
- Output: 0.85 (listed), 0.6 (default)

#### MetaLayerEvaluator (@m)
- Evaluates meta/governance quality
- Input: method_id
- Output: governance_quality from catalog

### 5. ChoquetAggregator

**Purpose**: Fuses layer scores using Choquet integral

**Method**: `aggregate(subject: CalibrationSubject, layer_scores: Dict[LayerID, float]) -> float`

**Formula**:
```
final_score = Σ(linear_weights[layer] * layer_score) + 
              Σ(interaction_weights[layer1,layer2] * min(score1, score2))
```

**Features**:
- Role-specific fusion parameters from fusion_specification.json
- Supports linear weights and interaction weights
- Bounded output [0.0, 1.0]

### 6. CalibrationOrchestrator

**Main orchestrator class implementing full calibration pipeline**

#### Initialization
```python
CalibrationOrchestrator(
    intrinsic_calibration: Dict,
    questionnaire_monolith: Dict,
    fusion_specification: Dict,
    method_compatibility: Dict,
    canonical_method_catalog: Dict
)
```

**Factory Method**:
```python
CalibrationOrchestrator.from_config_dir(config_dir: Path)
```

#### Main Method: `calibrate(subject, evidence)`

**Algorithm**:
1. Determine active layers via `LayerRequirementsResolver.get_required_layers(subject.method_id)`
2. Compute layer scores for each active layer:
   - `if LayerID.BASE in active_layers: layer_scores[LayerID.BASE] = base_evaluator.evaluate(method_id)`
   - `if LayerID.CHAIN in active_layers: layer_scores[LayerID.CHAIN] = chain_evaluator.evaluate(method_id)`
   - `if LayerID.UNIT in active_layers: layer_scores[LayerID.UNIT] = unit_evaluator.evaluate(pdt_structure)`
   - `if LayerID.QUESTION in active_layers: layer_scores[LayerID.QUESTION] = question_evaluator.evaluate(method_id, question_id)`
   - Continue for all 8 layers...
3. Validate completeness: Check all required layers computed (raises ValueError if missing)
4. Apply fusion via `choquet_aggregator.aggregate(subject, layer_scores)`
5. Return CalibrationResult with final_score, layer_scores, active_layers, metadata

### 7. Data Structures

#### CalibrationSubject (TypedDict)
```python
{
    "method_id": str,
    "role": str,
    "context": Dict[str, Any]
}
```

#### EvidenceStore (TypedDict)
```python
{
    "pdt_structure": Dict[str, Any],
    "document_quality": float,
    "question_id": str | None,
    "dimension_id": str | None,
    "policy_area_id": str | None
}
```

#### CalibrationResult (Dataclass)
```python
@dataclass
class CalibrationResult:
    final_score: float              # [0.0, 1.0]
    layer_scores: Dict[LayerID, float]
    active_layers: Set[LayerID]
    role: str
    method_id: str
    metadata: Dict[str, Any]
```

## Configuration Files

All configuration files are loaded from:
`src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/`

1. **COHORT_2024_intrinsic_calibration.json**
   - Method base quality (b_theory, b_impl, b_deploy)
   - Method roles
   - Base weight configuration

2. **COHORT_2024_questionnaire_monolith.json**
   - Micro questions with method_sets
   - Dimensions
   - Policy areas

3. **COHORT_2024_fusion_weights.json**
   - Role-specific fusion parameters
   - Linear weights for each layer
   - Interaction weights for layer pairs

4. **COHORT_2024_method_compatibility.json**
   - Chain compatibility scores per method

5. **COHORT_2024_canonical_method_inventory.json**
   - Governance quality scores per method

## Integration with Main Orchestrator

The CalibrationOrchestrator is integrated into the main `Orchestrator` class:

```python
class Orchestrator:
    def __init__(self, ..., calibration_orchestrator: Any | None = None, ...):
        # Auto-loads CalibrationOrchestrator if not provided
        if calibration_orchestrator is not None:
            self.calibration_orchestrator = calibration_orchestrator
        else:
            # Attempts to auto-load from config directory
            ...
    
    def calibrate_method(self, method_id, role, context, pdt_structure) -> dict | None:
        """
        Calibrate a method using the integrated CalibrationOrchestrator.
        Returns calibration result dict or None if unavailable.
        """
        ...
```

## Tests

**File**: `tests/orchestration/test_calibration_orchestrator.py`

**Test Coverage**:
- ✓ Layer requirements resolver for all roles
- ✓ Role layer requirements definitions
- ✓ Calibration of INGEST_PDM methods
- ✓ Calibration of SCORE_Q methods
- ✓ Calibration of AGGREGATE methods
- ✓ Individual layer evaluators (all 8)
- ✓ Choquet aggregator
- ✓ Completeness validation (pass/fail)
- ✓ CalibrationResult validation
- ✓ Unknown role defaults
- ✓ All roles have BASE and CHAIN
- ✓ SCORE_Q has all 8 layers
- ✓ Metadata population

**Run Tests**:
```bash
pytest tests/orchestration/test_calibration_orchestrator.py -v
```

## Examples

**Directory**: `tests/orchestration/orchestration_examples/`

### 1. example_basic_calibration.py
Basic single-method calibration demonstration

### 2. example_role_based_activation.py
Shows role-based layer activation for different roles

### 3. example_batch_calibration.py
Batch processing of multiple methods with statistics

### 4. example_layer_evaluator_detail.py
Individual layer evaluator behavior and scoring

### 5. example_completeness_validation.py
Completeness validation and missing layer detection

**Run Examples**:
```bash
python tests/orchestration/orchestration_examples/example_basic_calibration.py
python tests/orchestration/orchestration_examples/example_role_based_activation.py
```

## Usage Example

```python
from pathlib import Path
from src.orchestration.calibration_orchestrator import (
    CalibrationOrchestrator,
    CalibrationSubject,
    EvidenceStore,
)

# Initialize orchestrator
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

# Use results
print(f"Final Score: {result.final_score:.4f}")
print(f"Active Layers: {len(result.active_layers)}")
for layer_id, score in result.layer_scores.items():
    print(f"  {layer_id.value}: {score:.4f}")
```

## Architecture Diagram

```
CalibrationOrchestrator
├── Configuration Loader
│   ├── intrinsic_calibration.json
│   ├── questionnaire_monolith.json
│   ├── fusion_specification.json
│   ├── method_compatibility.json
│   └── canonical_method_catalog.json
│
├── LayerRequirementsResolver
│   └── get_required_layers(method_id) -> Set[LayerID]
│
├── Layer Evaluators (8)
│   ├── BaseLayerEvaluator (@b)
│   ├── ChainLayerEvaluator (@chain)
│   ├── UnitLayerEvaluator (@u)
│   ├── QuestionLayerEvaluator (@q)
│   ├── DimensionLayerEvaluator (@d)
│   ├── PolicyLayerEvaluator (@p)
│   ├── CongruenceLayerEvaluator (@C)
│   └── MetaLayerEvaluator (@m)
│
├── ChoquetAggregator
│   └── aggregate(subject, layer_scores) -> float
│
└── calibrate(subject, evidence) -> CalibrationResult
    1. Determine active_layers
    2. Compute layer_scores
    3. Validate completeness
    4. Apply fusion
    5. Return result
```

## Key Features

✅ **Role-Based Activation**: Different roles activate different layer subsets
✅ **8 Layer Evaluators**: Complete coverage of all calibration dimensions
✅ **Choquet Fusion**: Non-linear aggregation with interaction terms
✅ **Completeness Validation**: Ensures all required layers computed
✅ **Config-Driven**: All parameters loaded from JSON configurations
✅ **Type-Safe**: Full type hints and TypedDict contracts
✅ **Tested**: Comprehensive test suite with 20+ test cases
✅ **Documented**: Examples and usage patterns provided
✅ **Integrated**: Seamlessly integrated into main Orchestrator

## Validation Rules

1. **Final Score Bounds**: `0.0 <= final_score <= 1.0`
2. **Completeness Check**: All role-required layers must be computed
3. **Layer Score Bounds**: All layer scores in `[0.0, 1.0]`
4. **Missing Layer Detection**: ValueError raised if required layer missing

## Status

✅ **FULLY IMPLEMENTED** - All requested functionality complete and tested
