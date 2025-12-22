# Phase 1 Integration Summary: Hierarchical Parameter Lookup

## Changes Made

### 1. Added CalibrationParameters Dataclass

Added `CalibrationParameters` dataclass from PR #276 to support context-aware configuration:

```python
@dataclass
class CalibrationParameters:
    """Calibration parameters for hierarchical configuration."""
    confidence_threshold: float = 0.7
    method_weights: dict[str, float] = field(default_factory=dict)
    bayesian_priors: dict[str, Any] = field(default_factory=dict)
    random_seed: int = 42
    enable_belief_propagation: bool = True
    dempster_shafer_enabled: bool = True
```

### 2. Added Hierarchical Storage to CalibrationPolicy

Updated `__init__` to include hierarchical parameter storage:

```python
# PHASE 1 INTEGRATION: Hierarchical configuration from PR #276
self._global_params = CalibrationParameters()
self._dimension_params: dict[str, CalibrationParameters] = {}
self._policy_area_params: dict[str, CalibrationParameters] = {}
self._contract_params: dict[str, CalibrationParameters] = {}
```

### 3. Added Hierarchical Parameter Methods

Implemented 5 new methods for hierarchical configuration:

- **`get_context_parameters(question_id, dimension_id?, policy_area_id?)`**: Resolution order: contract → PA → dimension → global
- **`set_global_parameters(params)`**: Set global defaults (lowest priority)
- **`set_dimension_parameters(dimension_id, params)`**: Set dimension-specific params (D1-D6)
- **`set_policy_area_parameters(policy_area_id, params)`**: Set PA-specific params (PA01-PA10)
- **`set_contract_parameters(question_id, params)`**: Set contract-specific params (Q001-Q300) - highest priority

### 4. Integrated with calibrate_method_output

Updated main entry point to:

1. Extract `dimension_id` and `policy_area_id` from context
2. Get context-specific parameters via hierarchical lookup
3. Pass parameters to delegation and central calibration
4. Log hierarchical resolution for audit trail

```python
# PHASE 1: Get context-specific calibration parameters
dimension_id = context.get("dimension_id")
policy_area_id = context.get("policy_area_id")
context_params = self.get_context_parameters(
    question_id=question_id,
    dimension_id=dimension_id,
    policy_area_id=policy_area_id,
)
```

### 5. Enhanced _delegate_to_method

Now passes hierarchical parameters to methods:

```python
context_with_params = context.copy()
context_with_params["calibration_params"] = {
    "confidence_threshold": context_params.confidence_threshold,
    "bayesian_priors": context_params.bayesian_priors,
    "method_weights": context_params.method_weights,
}
```

### 6. Enhanced _apply_central_calibration

Uses hierarchical random_seed for reproducibility:

```python
# Use random_seed from context_params for reproducibility
rng = np.random.default_rng(context_params.random_seed)
posterior_samples = np.clip(
    rng.normal(raw_score, 0.1, size=10000),
    0.0,
    1.0,
)
```

## Architecture Diagram

```
CalibrationPolicy (Phase 1 Integrated)
├─ Hierarchical Parameters
│  ├─ Global (lowest priority)
│  ├─ Dimension (DIM01-DIM06)
│  ├─ Policy Area (PA01-PA10)
│  └─ Contract (Q001-Q300) ← highest priority
│
├─ Parameter Resolution
│  └─ get_context_parameters(Q, DIM?, PA?)
│     ├─ Check contract first
│     ├─ Check PA second
│     ├─ Check dimension third
│     └─ Return global fallback
│
└─ Integration Points
   ├─ calibrate_method_output
   │  ├─ Extracts context (dimension_id, policy_area_id)
   │  ├─ Resolves hierarchical parameters
   │  └─ Passes to delegation/central paths
   │
   ├─ _delegate_to_method
   │  └─ Augments context with hierarchical params
   │
   └─ _apply_central_calibration
      └─ Uses hierarchical random_seed for reproducibility
```

## Usage Examples

### Example 1: Global Default

```python
policy = CalibrationPolicy(thresholds=..., default_domain_weights=...)

# Set global default
global_params = CalibrationParameters(confidence_threshold=0.7, random_seed=42)
policy.set_global_parameters(global_params)

# All questions use global params
output = policy.calibrate_method_output("Q999", "method", 0.8)
# Uses confidence_threshold=0.7, random_seed=42
```

### Example 2: Dimension Override

```python
# Override for diagnostic dimension (D1 = DIM01)
dim_params = CalibrationParameters(confidence_threshold=0.75)
policy.set_dimension_parameters("DIM01", dim_params)

# Q001-Q050 (D1 questions) use dimension params
output = policy.calibrate_method_output(
    "Q001", "method", 0.8,
    context={"dimension_id": "DIM01"}
)
# Uses confidence_threshold=0.75 (dimension override)
```

### Example 3: Policy Area Override

```python
# Override for education policy area
pa_params = CalibrationParameters(confidence_threshold=0.85)
policy.set_policy_area_parameters("PA02", pa_params)

# Education questions use PA params (higher priority than dimension)
output = policy.calibrate_method_output(
    "Q031", "method", 0.8,
    context={"dimension_id": "DIM01", "policy_area_id": "PA02"}
)
# Uses confidence_threshold=0.85 (PA overrides dimension)
```

### Example 4: Contract-Specific Override

```python
# Critical question needs higher confidence
contract_params = CalibrationParameters(confidence_threshold=0.95)
policy.set_contract_parameters("Q001", contract_params)

# Q001 uses contract params (highest priority)
output = policy.calibrate_method_output(
    "Q001", "method", 0.8,
    context={"dimension_id": "DIM01", "policy_area_id": "PA02"}
)
# Uses confidence_threshold=0.95 (contract overrides PA and dimension)
```

## Benefits

1. **Flexibility**: Different thresholds/parameters per context (dimension/PA/contract)
2. **Backward Compatible**: Existing code works without hierarchical config (uses global defaults)
3. **Fine-Grained Control**: Can tune calibration for specific questions that need it
4. **Reproducibility**: Hierarchical random_seed ensures deterministic posterior generation
5. **Audit Trail**: Logs hierarchical resolution for debugging

## Testing

All existing tests pass:
- ✅ 12 tests in `test_calibration_standalone.py` - ALL PASSING
- ✅ Threshold monotonicity validation
- ✅ Probability mass validation
- ✅ Protocol detection
- ✅ Method delegation
- ✅ Posterior propagation
- ✅ Audit log export

## Next Steps (Phase 2 & 3)

**Phase 2**: Move hardcoded `calibration_params` to `canonical_specs.py`
- Add `BAYESIAN_PRIORS` constant to canonical_specs
- Update methods to load from canonical_specs instead of hardcoded values
- Fixes archaeology guide violation

**Phase 3**: Implement CalibrationOrchestrator
- Create orchestrator to tie everything together
- Bridge between executors and CalibrationPolicy
- Handle method-specific posterior extraction

## Compatibility

**✅ Compatible with PR #276** (FARFAN-sensitive hierarchical calibration):
- Uses same CalibrationParameters structure
- Implements same hierarchical resolution order
- Can be merged cleanly

**✅ Compatible with PR #378** (this PR):
- Preserves all uncertainty propagation
- Keeps protocol-based delegation
- Maintains provenance tracking

## Files Modified

- `src/farfan_pipeline/phases/Phase_two/phase2_60_04_calibration_policy.py` - Added ~100 lines for Phase 1 integration
  - Added CalibrationParameters dataclass
  - Added 4 hierarchical storage dicts
  - Added 5 hierarchical parameter methods
  - Integrated with calibrate_method_output
  - Enhanced _delegate_to_method and _apply_central_calibration

## Commit

Phase 1 integration complete and tested. Ready to proceed with Phase 2 (move calibration_params to canonical_specs.py).
