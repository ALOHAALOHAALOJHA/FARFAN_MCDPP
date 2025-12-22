# Calibration Parameter Rationality Matrix

## Purpose
This document provides the authoritative mapping of all calibration parameters, their sources, and rationale.

## Parameter Sources Hierarchy

1. **Method-Dispensary Parameters** (Highest Priority)
   - Source: Individual method files in `src/farfan_pipeline/methods/`
   - Authority: Method-specific domain knowledge and empirical tuning
   - Examples: `confidence_threshold`, method-specific priors

2. **Questionnaire Monolith Defaults** (Fallback Only)
   - Source: `canonic_questionnaire_central/questionnaire_monolith.json`
   - Authority: Cross-method quality label thresholds
   - Usage: Only when method doesn't specify its own parameters

3. **CalibrationPolicy Synthetic Defaults** (Last Resort)
   - Source: `phase2_60_04_calibration_policy.py`
   - Authority: Statistical defaults for uncertainty quantification
   - Usage: Only for methods not implementing CalibrableMethod protocol

## PDETMunicipalPlanAnalyzer Parameters

### Quality Label Thresholds (READ-ONLY from monolith)
These thresholds define quality bands and should NOT be overridden by method-specific logic:

| Parameter | Value | Source | Rationale |
|-----------|-------|--------|-----------|
| `t_excelente` | 0.85 | questionnaire_monolith.json | Cross-method standard for "excellent" quality |
| `t_bueno` | 0.70 | questionnaire_monolith.json | Cross-method standard for "good" quality |
| `t_aceptable` | 0.55 | questionnaire_monolith.json | Cross-method standard for "acceptable" quality |

**Protection Mechanism**: These are hardcoded in `_compute_label_probabilities_from_posterior()` to ensure consistency across all methods.

### Method-Specific Bayesian Priors (METHOD AUTHORITY)
These parameters control the Bayesian inference specific to financial analysis:

| Parameter | Current Value | Previous Value | Source | Rationale |
|-----------|---------------|----------------|--------|-----------|
| `prior_alpha` | 1.0 | N/A (new) | Statistical best practice | Uniform prior Beta(1,1): Weakly informative, equal probability to all outcomes in [0,1]. Conservative choice without domain-specific empirical data. |
| `prior_beta` | 1.0 | N/A (new) | Statistical best practice | Uniform prior Beta(1,1): Paired with α=1.0 for uniform distribution. Alternative would be Jeffrey's prior (0.5, 0.5) for scale invariance, but uniform is more interpretable. |

**DOCUMENTED CHOICE**: The values `prior_alpha=1.0` and `prior_beta=1.0` implement a **uniform prior** over [0,1]:
- **Statistical foundation**: Beta(1,1) is the uniform distribution, giving equal probability to all scores
- **Conservative approach**: Makes minimal assumptions about financial viability distribution
- **Interpretability**: Simple to explain to domain experts (no bias toward success or failure)
- **Alternative considered**: Jeffrey's prior Beta(0.5, 0.5) would be scale-invariant but less interpretable

### Existing Method Parameters (PRESERVED)
These parameters existed before the refactor and must NOT be altered:

| Parameter | Value | Source | Usage |
|-----------|-------|--------|-------|
| `confidence_threshold` | MICRO_LEVELS["BUENO"] (0.70) | financiero_viabilidad_tablas.py:352 | Method __init__ parameter |
| `use_gpu` | True | financiero_viabilidad_tablas.py:350 | Hardware optimization |
| `language` | 'es' | financiero_viabilidad_tablas.py:351 | NLP model configuration |

## Protocol Contract

### calibration_params Dictionary
This is a **declaration** of the method's calibration approach, not a replacement for existing parameters:

```python
calibration_params: dict[str, Any] = {
    "domain": "financial",              # Domain classification for CalibrationPolicy
    "output_semantics": "bayesian_posterior",  # Signal that method produces posterior samples
    "prior_alpha": 1.0,                 # ✓ DOCUMENTED: Uniform prior, weakly informative
    "prior_beta": 1.0,                  # ✓ DOCUMENTED: Uniform prior, weakly informative
    "logit_transform": False,           # No logit transformation needed
    "thresholds_source": "questionnaire_monolith.json",  # Acknowledges threshold source
}
```

**INVARIANT**: `calibration_params` must NOT override existing instance parameters like `self.confidence_threshold`.

## Validation Checklist

- [x] All prior values documented with rationale (uniform prior Beta(1,1))
- [x] Historical parameter values preserved (confidence_threshold, use_gpu, language unchanged)
- [x] Executor-method mapping verified via `canonical_methods_triangulated.json` (57 methods intact)
- [x] No silent parameter overwrites from questionnaire monolith (calibration_params is class-level)
- [x] Parameter hierarchy documented (method > monolith > synthetic defaults)
- [ ] Unit tests validate prior behavior (TODO: add test showing Beta(1,1) posterior updates)
- [ ] Integration tests confirm existing functionality preserved (existing tests should pass)

## References

- Historical calibration notes: `archive/CALIBRATION_IMPLEMENTATION_NOTES_2024.md`
- Executor-method mapping: `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/canonical_methods_triangulated.json`
- Quality standards: `canonic_questionnaire_central/questionnaire_monolith.json`
