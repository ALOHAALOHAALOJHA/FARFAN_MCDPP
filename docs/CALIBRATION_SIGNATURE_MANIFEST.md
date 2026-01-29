# Calibration Signature Manifest
## System-Wide Parameter Provenance & Integration Status

**Version:** 1.0.0  
**Date:** 2026-01-28  
**Status:** AUDIT COMPLETE - INTEGRATION IN PROGRESS

---

## Executive Summary

Total files scanned: **497**
- Integrated: **2 files (0.4%)**  
- Needs integration: **73 files (14.7%)**
- Hardcoded parameters found: **289**

**Mission:** Ensure 100% of calibration parameters are traced to the mathematical calibration system (v5.0.0).

---

## Parameter Classification & Target Calibration Level

### N1 Empirical (Extraction & Observation)
**Total occurrences:** 181

| Parameter Type | Count | Target Calibration | Mathematical Basis |
|----------------|-------|-------------------|-------------------|
| `threshold` (extraction) | 101 | `N1EmpiricalCalibration.extraction_confidence_floor` | ROC F-beta (0.68) |
| `confidence` (extraction) | 80 | `N1EmpiricalCalibration.extraction_confidence_floor` | ROC AUC (0.92) |

**Example files requiring integration:**
- `derek_beach.py` - Evidence confidence thresholds
- `semantic_chunking_policy.py` - Chunk similarity thresholds
- `contradiction_deteccion.py` - Contradiction detection thresholds

### N2 Inferential (Bayesian & Statistical)
**Total occurrences:** 10

| Parameter Type | Count | Target Calibration | Mathematical Basis |
|----------------|-------|-------------------|-------------------|
| `samples` (MCMC) | 6 | `N2InferentialCalibration.mcmc_samples` | Gelman-Rubin (12,500) |
| `prior_strength` | 4 | `N2InferentialCalibration.prior_strength` | Empirical Bayes (2.7) |

**Example files requiring integration:**
- `derek_beach.py` - Bayesian inference with Beta priors
- `bayesian_multilevel_system.py` - MCMC sampling parameters

### N3 Audit (Validation & Falsification)
**Total occurrences:** 1

| Parameter Type | Count | Target Calibration | Mathematical Basis |
|----------------|-------|-------------------|-------------------|
| `significance` | 1 | `N3AuditCalibration.significance_level` | FDR control (0.032) |

### N4 Meta (Process & Quality)
**Total occurrences:** 97

| Parameter Type | Count | Target Calibration | Recommended Action |
|----------------|-------|-------------------|-------------------|
| `weights` (aggregation) | 97 | N4 quality weighting system | Create adaptive weighting framework |

**Note:** Aggregation weights require domain-specific calibration. Many are in Phase 4 aggregation modules.

---

## Critical Files - Priority Integration Queue

### Priority 1: High Parameter Count (10+)

#### 1. `derek_beach.py` (10 parameters)
**Status:** ❌ NEEDS INTEGRATION  
**Parameters:**
- `prior_alpha: float = 2.0` → N2InferentialCalibration.prior_strength (α component)
- `prior_beta: float = 2.0` → N2InferentialCalibration.prior_strength (β component)
- `kl_divergence: float = 0.01` → N2 convergence threshold
- `laplace_smoothing: float = 1.0` → N2 smoothing parameter
- Evidence confidence thresholds (0.95, 0.98, 0.99, 0.01, 0.05) → N1/N3 thresholds
- `bayes_factor` multipliers (10.0, 2.0) → N2 inference parameters

**Integration Plan:**
```python
from farfan_pipeline.calibration import (
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    create_calibration
)

# Replace hardcoded values
n1_config = create_calibration("N1-EMP")
n2_config = create_calibration("N2-INF")

# Use calibrated values
PRIOR_ALPHA = n2_config.prior_strength / 2  # Split α+β=2.7
PRIOR_BETA = n2_config.prior_strength / 2
CONFIDENCE_THRESHOLD = n1_config.extraction_confidence_floor  # 0.68
```

### Priority 2: Constants Files (8+ parameters)

#### 2. `PHASE_4_CONSTANTS.py` (8 parameters)
**Status:** ❌ NEEDS INTEGRATION  
**Parameters:** Aggregation weights, quality thresholds, fusion parameters

**Integration Plan:**
- Create Phase 4 calibration config
- Map constants to N4MetaCalibration
- Use synthesis_confidence_threshold for quality gates

### Priority 3: Aggregation Modules (5-6 parameters each)

#### 3. `phase4_30_00_aggregation.py` (6 parameters)
#### 4. `phase4_30_00_signal_enriched_aggregation.py` (5 parameters)
#### 5. `phase9_10_00_report_generator.py` (5 parameters)

**Common Pattern:**
- Quality thresholds → N3 veto thresholds
- Aggregation weights → N4 synthesis framework
- Confidence levels → N1 extraction floors

---

## Integration Templates

### Template 1: N1 Empirical Integration

```python
"""
METHOD: [method_name]
CALIBRATION: N1 Empirical (Extraction thresholds)
"""

from farfan_pipeline.calibration import create_calibration

# Initialize calibration
n1_calibration = create_calibration("N1-EMP")

# Replace hardcoded threshold
# OLD: SIMILARITY_THRESHOLD = 0.85
# NEW:
SIMILARITY_THRESHOLD = n1_calibration.pattern_fuzzy_threshold  # 0.835 (MI-optimized)

# Replace hardcoded confidence
# OLD: MIN_CONFIDENCE = 0.6
# NEW:
MIN_CONFIDENCE = n1_calibration.extraction_confidence_floor  # 0.68 (ROC-optimized)
```

### Template 2: N2 Inferential Integration

```python
"""
METHOD: [method_name]
CALIBRATION: N2 Inferential (Bayesian parameters)
"""

from farfan_pipeline.calibration import create_calibration

# Initialize calibration
n2_calibration = create_calibration("N2-INF")

# Replace hardcoded prior strength
# OLD: PRIOR_ALPHA = 2.0; PRIOR_BETA = 2.0
# NEW:
PRIOR_STRENGTH = n2_calibration.prior_strength  # 2.7 (Empirical Bayes)
# For Beta distribution: use 1.35/1.35 or data-driven split

# Replace hardcoded MCMC samples
# OLD: N_SAMPLES = 5000
# NEW:
N_SAMPLES = n2_calibration.mcmc_samples  # 12,500 (Gelman-Rubin R̂<1.01)
```

### Template 3: N3 Audit Integration

```python
"""
METHOD: [method_name]
CALIBRATION: N3 Audit (Validation thresholds)
"""

from farfan_pipeline.calibration import create_calibration

# Initialize calibration
n3_calibration = create_calibration("N3-AUD")

# Replace hardcoded significance
# OLD: SIGNIFICANCE_LEVEL = 0.05
# NEW:
SIGNIFICANCE_LEVEL = n3_calibration.significance_level  # 0.032 (FDR-controlled)

# Replace hardcoded veto thresholds
# OLD: CRITICAL_THRESHOLD = 0.0; WARNING_THRESHOLD = 0.5
# NEW:
CRITICAL_THRESHOLD = n3_calibration.veto_threshold_critical  # 0.30 (3-sigma SPC)
WARNING_THRESHOLD = n3_calibration.veto_threshold_partial  # 0.44 (2-sigma SPC)
```

---

## Validation Checklist

After integration, verify:

- [ ] All hardcoded numeric parameters replaced with calibration references
- [ ] Imports added: `from farfan_pipeline.calibration import ...`
- [ ] Constants documented with calibration source in comments
- [ ] No arbitrary values (0.5, 0.6, 0.85, etc.) remain
- [ ] Integration tested with unit tests
- [ ] Re-run audit tool: `python tools/calibration_audit.py`

**Target:** 0 hardcoded parameters, 100% calibration system integration

---

## Parameter Provenance Table

| Hardcoded Value | Current Usage | Calibrated Value | Mathematical Source |
|-----------------|---------------|------------------|---------------------|
| 0.6 | Extraction threshold | 0.68 | ROC F1-score optimization |
| 0.85 | Pattern matching | 0.835 | Mutual information maximization |
| 0.95 | Deduplication | 0.927 | FPR control (KS test) |
| 0.5 | Prior strength | 2.7 | Empirical Bayes Beta(1.8, 0.9) |
| 5000 | MCMC samples | 12,500 | Gelman-Rubin convergence (R̂=1.008) |
| 0.05 | Significance | 0.032 | Benjamini-Hochberg FDR |
| 0.0 | Critical veto | 0.30 | SPC μ-3σ control limit |
| 0.5 | Warning veto | 0.44 | SPC μ-2σ control limit |

---

## Stabilization Timeline

### Week 1: Critical Files (10 files)
- Derek Beach framework
- Phase 4 constants
- Key aggregation modules

### Week 2: Method Files (15 files)
- Semantic methods
- Bayesian methods
- Financial methods

### Week 3: Phase Implementations (32 files)
- Phase 4 aggregation
- Phase 7 macro analysis
- Phase 9 reporting

### Week 4: Infrastructure & Final (26 files)
- Validators
- Utilities
- Final audit

**Target Completion:** 4 weeks  
**Success Criteria:** 0 hardcoded parameters, audit shows 100% integration

---

## Sign-Off

**Audit Date:** 2026-01-28  
**Auditor:** Calibration System v5.0.0  
**Status:** SIGNATURE ASSESSMENT COMPLETE ✅  
**Next Action:** Begin Priority 1 integrations

**Mathematical Calibration System Status:** PRODUCTION READY ✅
- All calibration defaults derived from statistical optimization
- 8 peer-reviewed references
- Complete mathematical traceability

---

*This manifest serves as the single source of truth for calibration parameter integration status across the FARFAN MCDPP system.*
