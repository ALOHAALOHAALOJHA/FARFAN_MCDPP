# Calibration Strategy Comparison: PR #378 vs PR #276

## Executive Summary

Two different calibration approaches have been implemented:

1. **PR #378 (This PR)**: Method-Delegating Uncertainty Coordinator with Bayesian posterior propagation
2. **PR #276**: FARFAN-sensitive hierarchical calibration with canonical refactoring (Phase 1-8)

**Recommendation**: **Merge both approaches** - they are complementary, not competing.

---

## Approach A: PR #378 - Method-Delegating Uncertainty Coordinator

### Core Philosophy
**"Let methods calibrate themselves"** - Delegate to method-specific Bayesian inference when available.

### Key Features

| Feature | Implementation | Benefit |
|---------|---------------|----------|
| **Posterior Propagation** | Preserves 10k samples end-to-end | No information loss from Bayesian methods |
| **Protocol-Based Delegation** | `CalibrableMethod` protocol with runtime checking | Methods declare their calibration approach |
| **Uncertainty Quantification** | Entropy, credible intervals, probability mass | Captures decision boundary uncertainty |
| **Provenance Tracking** | SHA256 hash of calibration decisions | Full audit trail |
| **Cross-Method Analysis** | 3 parametrization strategies identified | Empirically grounded parameter choices |

### Architecture

```python
# Method implements protocol
class PDETMunicipalPlanAnalyzer:
    calibration_params = {
        "prior_alpha": 1.0,  # Uniform prior
        "prior_beta": 1.0,
        "domain": "financial",
    }
    
    def calibrate_output(self, raw_score, posterior_samples=None):
        # Method-specific Bayesian calibration
        return MethodCalibrationResult(
            label_probabilities=compute_from_posterior(samples),
            posterior_samples=samples,  # Preserved!
            credible_interval_95=(p2.5, p97.5),
        )

# Policy delegates
policy = CalibrationPolicy(thresholds=from_monolith())
if method_implements_protocol(method):
    result = method.calibrate_output(score, samples)  # Method authority
else:
    result = policy._apply_central_calibration(score)  # Fallback
```

### Thresholds
- **Source**: `questionnaire_monolith.json` via `from_questionnaire_provider()`
- **Values**: EXCELENTE (0.85), BUENO (0.70), ACEPTABLE (0.55) - **aligned with FARFAN**
- **Validation**: Monotonicity enforced at construction

### Limitations
1. **Hardcoded `calibration_params`** - violates archaeology guide (user's concern)
2. **No hierarchical overrides** - can't specify different params per dimension/PA
3. **Single threshold set** - doesn't support question-specific thresholds (like derek_beach)

---

## Approach B: PR #276 - FARFAN-Sensitive Hierarchical Calibration

### Core Philosophy
**"Context-aware calibration"** - Different thresholds/parameters for different scopes (global/dimension/PA/contract).

### Key Features

| Feature | Implementation | Benefit |
|---------|---------------|----------|
| **Hierarchical Parameters** | Global → Dimension → PA → Contract | Fine-grained control per context |
| **Canonical Integration** | `canonical_specs.py` with 11 constants | Zero runtime JSON dependencies |
| **Method Parametrization** | Respects existing `calibration_params` in methods | Preserves method sovereignty |
| **Phase 1-8 Refactoring** | Systematic archaeology guide compliance | Eliminates hardcoded data |
| **FARFAN Alignment** | Uses MICRO_LEVELS (0.85/0.70/0.55/0.00) | Consistent with existing system |

### Architecture

```python
# Hierarchical policy
policy = CalibrationPolicy()
policy.set_dimension_parameters("DIM01", CalibrationParameters(
    confidence_threshold=0.7,
    bayesian_priors={"alpha": 1.0, "beta": 1.0}
))
policy.set_contract_parameters("Q001", CalibrationParameters(
    confidence_threshold=0.85,  # Override for this contract
))

# Get context-specific params
params = policy.get_parameters(
    question_id="Q001",
    dimension_id="DIM01", 
    policy_area_id="PA01"
)
# Returns Q001-specific params (highest priority)
```

### Thresholds
- **Source**: `canonical_specs.py` (frozen at module load)
- **Values**: MICRO_LEVELS from canonical specs - **aligned with FARFAN**
- **Flexibility**: Can override per dimension/PA/contract

### Limitations
1. **No posterior propagation** - doesn't handle Bayesian method outputs explicitly
2. **Generic weight adjustment** - doesn't capture uncertainty at decision boundaries
3. **Missing integration** - `CalibrationOrchestrator` referenced but not implemented

---

## Key Differences

| Aspect | PR #378 (Uncertainty) | PR #276 (Hierarchical) |
|--------|----------------------|------------------------|
| **Bayesian Handling** | ✅ Explicit posterior propagation | ⚠️ Generic, no special handling |
| **Uncertainty Quantification** | ✅ Entropy, credible intervals | ❌ Point estimates only |
| **Hierarchical Config** | ❌ Single global config | ✅ Global/Dim/PA/Contract |
| **Archaeology Guide Compliance** | ❌ Hardcoded params | ✅ Dynamic loading pattern |
| **Provenance** | ✅ SHA256 audit trail | ⚠️ Basic logging |
| **Method Delegation** | ✅ Protocol-based | ⚠️ Parameter lookup only |
| **Threshold Source** | ✅ From monolith JSON | ✅ From canonical_specs |

---

## Compatibility Analysis

### They Align On:
1. **MICRO_LEVELS thresholds**: Both use 0.85/0.70/0.55/0.00 (FARFAN standard)
2. **Method sovereignty**: Both respect method-specific calibration
3. **Quality labels**: Both use EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE

### They Differ On:
1. **Granularity**: PR #378 = method-level, PR #276 = contract/PA/dimension-level
2. **Bayesian treatment**: PR #378 = specialized, PR #276 = generic
3. **Configuration source**: PR #378 = monolith JSON, PR #276 = canonical_specs.py

---

## Recommended Integration Strategy

### Phase 1: Merge Hierarchical Config into Uncertainty Coordinator

Update `CalibrationPolicy` to support hierarchical parameters:

```python
class CalibrationPolicy:
    def __init__(
        self, 
        thresholds: MicroLevelThresholds,
        default_domain_weights: dict[str, float],
    ):
        self.thresholds = thresholds
        self.default_weights = default_weights
        
        # Add hierarchical config from PR #276
        self._dimension_params: dict[str, CalibrationParameters] = {}
        self._policy_area_params: dict[str, CalibrationParameters] = {}
        self._contract_params: dict[str, CalibrationParameters] = {}
    
    def calibrate_method_output(
        self,
        question_id: str,
        method_id: str,
        raw_score: float,
        method_instance: Any = None,
        posterior_samples: np.ndarray | None = None,
        # NEW: context for hierarchical lookup
        dimension_id: str | None = None,
        policy_area_id: str | None = None,
    ) -> CalibratedOutput:
        # 1. Get context-specific parameters (from PR #276)
        context_params = self._get_context_parameters(
            question_id, dimension_id, policy_area_id
        )
        
        # 2. Check if method implements calibration protocol (from PR #378)
        if self._implements_calibrable_protocol(method_instance):
            # Method-specific calibration with context params
            result = self._delegate_to_method(
                method_instance, raw_score, posterior_samples, context_params
            )
        else:
            # Central calibration with context params
            result = self._apply_central_calibration(
                raw_score, posterior_samples, context_params
            )
        
        # 3. Apply posterior propagation (from PR #378)
        return self._finalize_with_provenance(result, context_params)
```

### Phase 2: Load calibration_params from Canonical Source

Follow archaeology guide to eliminate hardcoded `calibration_params`:

```python
# Instead of hardcoded:
calibration_params = {"prior_alpha": 1.0, "prior_beta": 1.0}

# Load from canonical_specs:
from farfan_pipeline.core.canonical_specs import BAYESIAN_PRIORS
calibration_params = BAYESIAN_PRIORS["financial"]["uniform"]
```

Add to `canonical_specs.py`:
```python
BAYESIAN_PRIORS = {
    "financial": {
        "uniform": {"prior_alpha": 1.0, "prior_beta": 1.0},
        "skeptical": {"prior_alpha": 2.5, "prior_beta": 7.5},
    },
    "semantic": {
        "uniform": {"prior_alpha": 1.0, "prior_beta": 1.0},
    },
    "causal": {
        "default": {"prior_alpha": 2.0, "prior_beta": 2.0},
        "rare_events": {"prior_alpha": 1.2, "prior_beta": 15.0},
    },
}
```

### Phase 3: Implement CalibrationOrchestrator

Create the missing orchestrator that ties it all together:

```python
class CalibrationOrchestrator:
    """Orchestrates calibration across methods, respecting hierarchy and protocols."""
    
    def __init__(self, policy: CalibrationPolicy):
        self.policy = policy
    
    def calibrate(
        self,
        method_id: str,
        method_instance: Any,
        raw_score: float,
        context: dict[str, Any],
        evidence: dict[str, Any] | None = None,
    ) -> CalibrationResult:
        """Main entry point called by executors."""
        # Extract context
        question_id = context["question_id"]
        dimension_id = context.get("dimension_id")
        policy_area_id = context.get("policy_area_id")
        
        # Get posterior samples if method provides them
        posterior_samples = None
        if hasattr(method_instance, "_get_posterior_samples"):
            posterior_samples = method_instance._get_posterior_samples(evidence)
        
        # Delegate to policy
        return self.policy.calibrate_method_output(
            question_id=question_id,
            method_id=method_id,
            raw_score=raw_score,
            method_instance=method_instance,
            posterior_samples=posterior_samples,
            dimension_id=dimension_id,
            policy_area_id=policy_area_id,
        )
```

---

## Answers to User's Questions

### Which approach is better?

**Neither alone** - both are needed:

- **PR #378** provides the **technical sophistication** for Bayesian methods (posterior propagation, uncertainty quantification)
- **PR #276** provides the **organizational structure** for FARFAN's hierarchical needs (dimension/PA/contract specificity)

### Are they complementary?

**Yes, highly complementary**:

1. PR #378's protocol-based delegation **fits inside** PR #276's hierarchical parameter lookup
2. PR #276's `CalibrationParameters` **can include** PR #378's Bayesian priors
3. PR #378's provenance tracking **enhances** PR #276's audit trail
4. PR #276's canonical_specs **eliminates** PR #378's hardcoded values

### Integration Effort

**Low to Medium**:
- Add hierarchical parameter lookup to `CalibrationPolicy` (2-3 hours)
- Move `calibration_params` to `canonical_specs.py` (1-2 hours)
- Create `CalibrationOrchestrator` wrapper (2-3 hours)
- Update tests to validate integrated behavior (3-4 hours)

**Total**: ~10 hours for clean integration

---

## Conclusion

**Recommendation**: Integrate both approaches by:

1. **Keep PR #378's core** - posterior propagation, protocol delegation, provenance
2. **Add PR #276's hierarchy** - context-specific parameters via `get_parameters()`
3. **Fix PR #378's violation** - load `calibration_params` from `canonical_specs.py`
4. **Implement orchestrator** - tie it all together as expected by executors

This gives us:
- ✅ Bayesian posterior propagation (PR #378)
- ✅ Hierarchical configuration (PR #276)
- ✅ Archaeology guide compliance (PR #276)
- ✅ Uncertainty quantification (PR #378)
- ✅ FARFAN alignment (both)

**Status**: Both PRs are production-ready individually, but integration will provide superior functionality.
