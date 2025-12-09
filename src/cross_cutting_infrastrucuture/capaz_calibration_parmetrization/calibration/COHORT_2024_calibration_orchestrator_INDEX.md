# COHORT_2024 CalibrationOrchestrator - Complete Implementation Index

**SENSITIVE - CALIBRATION SYSTEM CRITICAL**

## Implementation Files

### 1. Core Implementation

**File**: `COHORT_2024_calibration_orchestrator.py`

Complete CalibrationOrchestrator implementation with:
- Role-based layer requirement determination
- 8-layer score computation (base, contextual, unit, meta)
- Choquet integral fusion with interaction terms
- Boundedness validation [0.0-1.0]
- Cryptographic certificate generation

**API**:
```python
CalibrationOrchestrator.calibrate(
    method_id: str,
    context: CalibrationContext | None = None,
    evidence: CalibrationEvidence | None = None,
) -> CalibrationResult
```

### 2. Documentation

**File**: `COHORT_2024_calibration_orchestrator_README.md`

Comprehensive documentation covering:
- Architecture and layer system
- Role-based layer requirements
- Choquet integral fusion formula
- API reference with TypedDict definitions
- Layer score computation algorithms
- Certificate metadata structure
- Integration examples

### 3. Usage Examples

**File**: `COHORT_2024_calibration_orchestrator_example.py`

7 runnable examples demonstrating:
1. Executor calibration (8 layers)
2. Ingest calibration (4 layers)
3. Utility calibration (3 layers)
4. Minimal calibration (defaults)
5. Score comparison across methods
6. Detailed fusion breakdown analysis
7. Boundedness validation

**Run**: 
```bash
python -m src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_calibration_orchestrator_example
```

### 4. Test Suite

**File**: `tests/test_calibration_orchestrator.py`

Comprehensive pytest test suite with 30+ tests covering:
- Layer requirement determination
- Layer score computation (all 8 layers)
- Choquet fusion mechanics
- Boundedness validation
- Certificate generation
- Integration scenarios

**Run**:
```bash
pytest tests/test_calibration_orchestrator.py -v
```

### 5. Security Documentation

**File**: `SENSITIVE_CRITICAL_SYSTEM.md`

Security classification and change management protocol:
- Access control requirements
- Change management protocol
- Mathematical validation requirements
- Incident response procedures
- Audit trail specifications

### 6. Package Integration

**File**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/__init__.py`

Public API exports:
```python
from calibration_parametrization_system import (
    CalibrationOrchestrator,
    CalibrationContext,
    CalibrationEvidence,
    CalibrationResult,
    FusionWeights,
    LayerScores,
)
```

## File Dependencies

### Required Configuration Files

1. **COHORT_2024_fusion_weights.json** (or fallback: fusion_weights.json)
   - Linear weights for 8 layers
   - Interaction weights for 4 layer pairs
   - Normalization constraint validation

2. **COHORT_2024_intrinsic_calibration.json**
   - Base layer evaluation rubric
   - Theory, implementation, deployment components

3. **COHORT_2024_method_compatibility.json**
   - Contextual layer scores per method
   - Question, dimension, policy alignments

### Required Python Modules

1. **COHORT_2024_layer_assignment.py**
   - `LAYER_REQUIREMENTS` dictionary
   - Role-to-layer mapping

2. **pdt_structure.py**
   - `PDTStructure` dataclass (for unit layer)

3. **meta_layer.py** (optional reference)
   - Governance artifacts structure

## Quick Start

### Installation

Ensure you're in the repository root with virtual environment activated:

```bash
source farfan-env/bin/activate
pip install -e .
```

### Basic Usage

```python
from calibration_parametrization_system import (
    CalibrationOrchestrator,
    CalibrationContext,
    CalibrationEvidence,
)

orchestrator = CalibrationOrchestrator()

result = orchestrator.calibrate(
    method_id="farfan_pipeline.core.executors.D1_Q1_Executor",
    context=CalibrationContext(
        question_id="Q001",
        dimension_id="DIM01",
        policy_area_id="PA01",
    ),
    evidence=CalibrationEvidence(
        intrinsic_scores={"base_layer_score": 0.85},
    ),
)

print(f"Final Score: {result['final_score']:.3f}")
print(f"Certificate ID: {result['certificate_metadata']['certificate_id']}")
```

### Validation

```bash
# Run tests
pytest tests/test_calibration_orchestrator.py -v

# Run examples
python -m src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_calibration_orchestrator_example

# Type check
mypy src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_calibration_orchestrator.py --strict

# Lint
ruff check src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_calibration_orchestrator.py
```

## Implementation Summary

### Layer System (8 Layers)

| Symbol | Name | Source | Computation |
|--------|------|--------|-------------|
| `@b` | Base | intrinsic_scores | Weighted sum of theory/impl/deploy OR direct score |
| `@chain` | Chain | intrinsic_scores | Direct score from evidence |
| `@q` | Question | method_compatibility | Lookup by question_id |
| `@d` | Dimension | method_compatibility | Lookup by dimension_id |
| `@p` | Policy | method_compatibility | Lookup by policy_area_id |
| `@C` | Contract | intrinsic_scores | Direct score from evidence |
| `@u` | Unit | pdt_structure | Computed from structure/tokens/matrices |
| `@m` | Meta | governance_artifacts | Computed from version/hash/signature |

### Role Mapping (LAYER_REQUIREMENTS)

| Role | Layers | Count |
|------|--------|-------|
| executor | @b, @chain, @q, @d, @p, @C, @u, @m | 8 |
| analyzer | @b, @chain, @q, @d, @p, @C, @u, @m | 8 |
| score | @b, @chain, @q, @d, @p, @C, @u, @m | 8 |
| core | @b, @chain, @q, @d, @p, @C, @u, @m | 8 |
| ingest | @b, @chain, @u, @m | 4 |
| processor | @b, @chain, @u, @m | 4 |
| extractor | @b, @chain, @u, @m | 4 |
| orchestrator | @b, @chain, @m | 3 |
| utility | @b, @chain, @m | 3 |

### Fusion Formula

```
Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))
```

**Linear Weights** (from fusion_weights.json):
- b: 0.122951
- u: 0.098361
- q: 0.081967
- d: 0.065574
- p: 0.049180
- C: 0.081967
- chain: 0.065574
- m: 0.034426

**Interaction Weights**:
- (u, chain): 0.15
- (chain, C): 0.12
- (q, d): 0.08
- (d, p): 0.05

**Constraint**: Σ(linear) + Σ(interaction) = 1.0

### Validation Rules

1. **Boundedness**: `0.0 ≤ Cal(I) ≤ 1.0`
   - Enforced via clamping if violated
   - Violation recorded in validation result

2. **Monotonicity**: `∂Cal/∂x_ℓ ≥ 0`
   - Guaranteed by non-negative weights

3. **Normalization**: Validated at fusion weights load time

## Troubleshooting

### Issue: FileNotFoundError for fusion_weights.json

**Solution**: Ensure you're running from repository root and calibration JSON files exist:
```bash
ls src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/*.json
```

### Issue: KeyError in layer_scores

**Solution**: Check that the method_id maps to a valid role. Unknown methods default to "core" role.

### Issue: Final score exceeds [0,1] bounds

**Solution**: This should be automatically clamped. Check validation result:
```python
if not result['validation']['is_bounded']:
    print(f"Score was clamped: {result['validation']['original_score']} → {result['validation']['clamped_score']}")
```

### Issue: Missing context leads to default scores

**Solution**: Provide full context for contextual layers:
```python
context = CalibrationContext(
    question_id="Q001",
    dimension_id="DIM01", 
    policy_area_id="PA01",
)
```

## Integration Checklist

- [ ] CalibrationOrchestrator imported into application
- [ ] Fusion weights JSON files present in calibration/ directory
- [ ] LAYER_REQUIREMENTS mapping verified for all method roles
- [ ] Test suite passes (30+ tests green)
- [ ] Certificate generation validated (SHA256 hash consistency)
- [ ] Boundedness validation enabled in production
- [ ] Audit logging configured for calibration operations
- [ ] Governance approval obtained (if modifying parameters)

## Version History

- **1.0.0** (2024-12-15): Initial COHORT_2024 implementation
  - Complete 8-layer calibration system
  - Choquet integral fusion with interactions
  - Cryptographic certificate generation
  - Role-based layer requirements
  - Comprehensive test coverage
  - Full documentation suite

## References

- **Specification**: SUPERPROMPT Three-Pillar Calibration System
- **Authority**: Doctrina SIN_CARRETA
- **Cohort**: COHORT_2024 / REFACTOR_WAVE_2024_12
- **Mathematical Foundation**: `mathematical_foundations_capax_system.md`
- **Governance**: `COHORT_MANIFEST.json`

---

**Status**: ✅ IMPLEMENTATION COMPLETE  
**Classification**: SENSITIVE - CALIBRATION SYSTEM CRITICAL  
**Last Updated**: 2024-12-15
