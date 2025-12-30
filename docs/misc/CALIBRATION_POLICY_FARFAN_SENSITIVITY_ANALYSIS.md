# Calibration Policy FARFAN Sensitivity Analysis

## Executive Summary

This document analyzes the compatibility between the newly implemented `CalibrationPolicy` system and the existing FARFAN methodology, particularly focusing on the parametrized methods in the methods_dispensary.

## Key Findings

### 1. Calibration System Mismatch

**Issue**: The `CalibrationPolicy` implements generic quality bands that don't align with FARFAN's existing calibration system.

| System | Thresholds | Source |
|--------|-----------|--------|
| **CalibrationPolicy (New)** | EXCELLENT: 0.8-1.0<br>GOOD: 0.6-0.8<br>ACCEPTABLE: 0.4-0.6<br>POOR: 0.0-0.4 | `src/farfan_pipeline/phases/Phase_two/calibration_policy.py` |
| **DEREK_BEACH (Existing)** | EXCELENTE: 0.85<br>BUENO: 0.70<br>ACEPTABLE: 0.55<br>INSUFICIENTE: 0.00 | `src/farfan_pipeline/methods/derek_beach.py` line 97-102 |
| **ALIGNMENT_THRESHOLD** | 0.625 (computed as average of ACEPTABLE and BUENO) | `src/farfan_pipeline/methods/derek_beach.py` line 108 |

**Problem**: The new policy would classify a score of 0.7 as "GOOD" when the DEREK_BEACH system considers it exactly "BUENO" threshold.

### 2. Missing CalibrationOrchestrator Implementation

**Issue**: The executor code references a non-existent module:
```python
from cross_cutting_infrastructure.capaz_calibration_parmetrization.calibration_orchestrator import (
    MethodBelowThresholdError,
)
```

**Current State**:
- `src/cross_cutting_infrastructure/` exists but has no `capaz_calibration_parmetrization` subdirectory
- `CalibrationOrchestrator` is referenced but never implemented
- My `CalibrationPolicy` acts on calibration scores that don't exist yet

**Evidence**: 
- `src/farfan_pipeline/phases/Phase_two/base_executor_with_contract.py` lines 798-802, 1225-1229
- No implementation found in repository

### 3. Method-Specific Calibration Already Exists

**Finding**: DEREK_BEACH methods have sophisticated built-in calibration:

#### CDAFFramework Calibration (lines 6570-6650)
```python
calibration_params = {
    'alpha': -2.0,  # Intercept for logit transformation
    'beta': 4.0     # Slope for logit transformation
}

# Transforms scores using: p = 1/(1+exp(-(α+β·score)))
```

This logistic calibration is fundamentally different from the linear weight adjustment in `CalibrationPolicy`.

#### Domain-Specific Weights
```python
default_domain_weights = {
    'semantic': 0.35,
    'temporal': 0.25,
    'financial': 0.25,
    'structural': 0.15
}
```

These are **already parametrized** for FARFAN's methodological structure.

### 4. Executor Contract Integration

**Example**: Q233.v3.json (D5-Q3 executor)
```json
{
  "method_binding": {
    "methods": [
      {
        "class_name": "CausalExtractor",
        "method_name": "_calculate_semantic_distance",
        "priority": 1
      },
      {
        "class_name": "BayesianMechanismInference",
        "method_name": "_quantify_uncertainty",
        "priority": 3
      }
    ]
  }
}
```

**Problem**: My `CalibrationPolicy` applies uniform weight adjustments (1.0, 0.9, 0.7, 0.4) without considering:
- Method-specific calibration parameters already in the class
- Priority ordering in contracts
- Domain-specific weights
- The parametrization guided by `GUIA_ARQUEOLOGIA_INVERSA_REFACTORIZACION.md`

## Impact Analysis

### What My Implementation Does

1. **Generic Weight Adjustment**: Applies 1.0x, 0.9x, 0.7x, or 0.4x based on quality band
2. **Execution Blocking**: In strict mode, blocks methods with calibration < 0.3
3. **Drift Detection**: Monitors calibration scores over time
4. **Metrics Tracking**: Records all calibration decisions

### What It Should Do (FARFAN-Sensitive)

1. **Respect Method Parametrization**: Use calibration_params from each method class
2. **Align with MICRO_LEVELS**: Match the 0.85/0.70/0.55/0.00 thresholds
3. **Integrate with Existing System**: Work with the parametrization in methods_dispensary
4. **Contract-Aware**: Consider method priority and role in executor contracts
5. **Domain-Weighted**: Respect semantic/temporal/financial/structural domain weights

## Compatibility Issues

### Issue 1: Threshold Misalignment

```python
# Current CalibrationPolicy
if 0.6 <= score < 0.8:
    return "GOOD", 0.9  # 10% downweight

# DEREK_BEACH expectation
if score == 0.70:
    return "BUENO"  # Exact threshold, not a range
```

**Impact**: Methods calibrated to DEREK_BEACH thresholds would be misclassified.

### Issue 2: Missing Integration Point

```python
# base_executor_with_contract.py line 802
calibration_result = self.calibration_orchestrator.calibrate(
    method_id=method_id,
    context=payload,
    evidence=None
)
# Returns: calibration_result.final_score

# CalibrationPolicy expects this score but:
# 1. CalibrationOrchestrator doesn't exist
# 2. Don't know what .calibrate() should return
# 3. Don't know if it should use method-specific calibration_params
```

### Issue 3: Parametrization Ignored

The `GUIA_ARQUEOLOGIA_INVERSA_REFACTORIZACION.md` documents a process for aligning method parameters with:
- questionnaire_monolith.json structure
- 30 base questions (D1-Q1 through D6-Q5)
- 10 policy areas
- expected_elements types

My implementation doesn't reference this structure at all.

## Recommendations

### Option A: Defer to Method-Specific Calibration (Recommended)

Make `CalibrationPolicy` a **coordinator** rather than a **dictator**:

```python
class CalibrationPolicy:
    def compute_adjusted_weight(self, base_weight, calibration_score, method_class=None):
        # If method has its own calibration system, use it
        if method_class and hasattr(method_class, 'calibration_params'):
            return method_class.apply_calibration(calibration_score)
        
        # Otherwise, use FARFAN MICRO_LEVELS
        if calibration_score >= 0.85:
            return "EXCELENTE", 1.0
        elif calibration_score >= 0.70:
            return "BUENO", 0.90
        elif calibration_score >= 0.55:
            return "ACEPTABLE", 0.75
        else:
            return "INSUFICIENTE", 0.40
```

### Option B: Implement CalibrationOrchestrator First

Create the missing `CalibrationOrchestrator` that:
1. Reads method-specific `calibration_params` from each class
2. Applies appropriate transformation (logit for Bayesian methods, linear for others)
3. Returns structured calibration results that my policy can consume

### Option C: Integrate with Existing Parametrization

Modify `CalibrationPolicy` to read from:
- `questionnaire_monolith.json` for threshold definitions
- Method class `calibration_params` for transformations
- Executor contracts for priority/role context

## Questions for User

1. **Should CalibrationPolicy be method-agnostic or method-aware?**
   - Agnostic: Apply same rules to all methods (current implementation)
   - Aware: Delegate to method-specific calibration (recommended)

2. **What should CalibrationOrchestrator.calibrate() return?**
   - Just a score (0.0-1.0)?
   - Structured result with layer_scores, final_score, metadata?
   - Method-specific calibration transformed scores?

3. **How to handle methods without built-in calibration?**
   - Fall back to generic CalibrationPolicy bands?
   - Require all methods to define calibration_params?
   - Use MICRO_LEVELS as default?

4. **Should calibration be per-method-instance or per-method-class?**
   - Instance: CausalExtractor instance A has different calibration than instance B
   - Class: All CausalExtractor instances share calibration_params

## Next Steps

1. **Immediate**: Await user clarification on questions above
2. **Short-term**: Align CalibrationPolicy thresholds with MICRO_LEVELS
3. **Medium-term**: Implement CalibrationOrchestrator with method awareness
4. **Long-term**: Integrate with questionnaire_monolith.json structure

## References

- `src/farfan_pipeline/methods/derek_beach.py` - MICRO_LEVELS, CDAFFramework calibration
- `GUIA_ARQUEOLOGIA_INVERSA_REFACTORIZACION.md` - Parametrization methodology
- `src/farfan_pipeline/phases/Phase_two/base_executor_with_contract.py` - CalibrationOrchestrator references
- `src/farfan_pipeline/phases/Phase_two/calibration_policy.py` - Current implementation
- `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q233.v3.json` - Example contract
