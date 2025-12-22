# Calibration Parameter Rationality Matrix

## Purpose
This document provides the authoritative mapping of all calibration parameters, their sources, and rationale **based on cross-method analysis of the entire methods/ directory**.

## Cross-Method Analysis Summary

Analysis of all 10 method files reveals three distinct Bayesian prior parametrization strategies:

### Strategy A: Uniform/Weakly Informative (α=1.0, β=1.0)
**Files**: `policy_processor.py`, `financiero_viabilidad_tablas.py`, `semantic_chunking_policy.py`
- **Pattern**: Maximum uncertainty, no directional bias
- **Use case**: Domains without empirical calibration data
- **Interpretation**: "Let the data speak" - 50% prior expectation

### Strategy B: Symmetric Non-Uniform (α=2.0, β=2.0)
**Files**: `derek_beach.py` (default configuration)
- **Pattern**: Slight regularization toward middle, but balanced
- **Use case**: General causal inference with mild regularization
- **Interpretation**: Bayesian regularization without bias

### Strategy C: Asymmetric Conservative (α << β)
**Files**: `contradiction_deteccion.py` (α=2.5, β=7.5), `derek_beach.py` question-specific (α=1.2-1.8, β=10-15)
- **Pattern**: Evidence skepticism - bias toward lower confidence
- **Use case**: High-stakes decisions where false positives are costly
- **Interpretation**: "Guilty until proven innocent" - skeptical priors

**Key Insight**: The choice of (1.0, 1.0) for financial analysis aligns with the established codebase pattern for domains without empirical calibration.

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

| Parameter | Value | Comparison to Other Methods | Source | Rationale |
|-----------|-------|----------------------------|--------|-----------|
| `prior_alpha` | 1.0 | **Matches**: policy_processor (1.0), semantic_chunking (1.0)<br>**Differs from**: contradiction_deteccion (2.5), derek_beach question-specific (1.2-1.8) | Statistical best practice | Uniform prior Beta(1,1): No bias. Financial viability is NOT inherently rare (unlike contradictions or causal failures). |
| `prior_beta` | 1.0 | **Matches**: policy_processor (1.0), semantic_chunking (1.0)<br>**Differs from**: contradiction_deteccion (7.5), derek_beach question-specific (10-15) | Statistical best practice | Uniform prior Beta(1,1): Maximum uncertainty. No evidence skepticism needed for financial domain. |

**Cross-Method Pattern Analysis**:
- **Uniform priors (1.0, 1.0)**: Standard for semantic, financial, and chunking domains
- **Asymmetric priors (α << β)**: Reserved for high-stakes domains with evidence skepticism:
  - Contradiction detection: α=2.5, β=7.5 (25% prior confidence - skeptical of claims)
  - Rare causal events (derek_beach D6-Q8): α=1.2, β=15.0 (7% prior - extremely rare)
- **Question-specific priors**: Advanced calibration in derek_beach.py based on historical performance

**Why NOT asymmetric for financial?**
1. Financial viability is NOT a rare event (unlike contradictions)
2. No need for evidence skepticism (false positives not catastrophically costly)
3. Data quality is table-based (structured), not NLP-extracted (ambiguous)
4. Consistent with parallel semantic analysis (policy_processor.py also uses 1.0, 1.0)

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
- [x] **Cross-method comparison completed** - analyzed all 10 method files
- [x] **Parametrization patterns identified** - 3 strategies documented
- [x] Historical parameter values preserved (confidence_threshold, use_gpu, language unchanged)
- [x] Executor-method mapping verified via `canonical_methods_triangulated.json` (57 methods intact)
- [x] No silent parameter overwrites from questionnaire monolith (calibration_params is class-level)
- [x] Parameter hierarchy documented (method > monolith > synthetic defaults)
- [x] **Alignment with codebase patterns confirmed** - (1.0, 1.0) matches policy_processor.py and semantic_chunking_policy.py
- [ ] Unit tests validate prior behavior (TODO: add test showing Beta(1,1) posterior updates)
- [ ] Integration tests confirm existing functionality preserved (existing tests should pass)

## Cross-Method Comparison Table

| Method File | Class | α | β | α/(α+β) | Domain | Rationale |
|-------------|-------|---|---|---------|--------|-----------|
| `policy_processor.py` | BayesianEvidenceScorer | 1.0 | 1.0 | 0.50 | Semantic | Uniform, no bias |
| `financiero_viabilidad_tablas.py` | PDETMunicipalPlanAnalyzer | 1.0 | 1.0 | 0.50 | Financial | **This file** - uniform, no bias |
| `semantic_chunking_policy.py` | DirichletBayesianScorer | 1.0 | N/A | - | Semantic | Symmetric Dirichlet |
| `derek_beach.py` | BayesianConfig (default) | 2.0 | 2.0 | 0.50 | Causal | Balanced regularization |
| `contradiction_deteccion.py` | BayesianConfidenceCalculator | 2.5 | 7.5 | 0.25 | Contradiction | Evidence skepticism |
| `derek_beach.py` | D4-Q3 (rare events) | 1.5 | 12.0 | 0.11 | Causal | Rare occurrence |
| `derek_beach.py` | D5-Q5 (effects) | 1.8 | 10.5 | 0.15 | Causal | Effects rarely documented |
| `derek_beach.py` | D6-Q8 (failures) | 1.2 | 15.0 | 0.07 | Causal | Most conservative |

**Pattern**: Prior expectation α/(α+β) decreases as:
1. Domain becomes high-stakes (contradictions: 0.25 vs. semantic: 0.50)
2. Event becomes rare (failures: 0.07 vs. general effects: 0.50)
3. Evidence quality decreases (NLP extraction vs. structured tables)

## References

- Historical calibration notes: `archive/CALIBRATION_IMPLEMENTATION_NOTES_2024.md`
- Executor-method mapping: `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/canonical_methods_triangulated.json`
- Quality standards: `canonic_questionnaire_central/questionnaire_monolith.json`
