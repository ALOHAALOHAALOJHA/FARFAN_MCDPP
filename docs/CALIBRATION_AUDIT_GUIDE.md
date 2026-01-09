# FARFAN Calibration & Parametrization System Audit Guide

## Overview

The FARFAN Calibration & Parametrization System Audit is a comprehensive validation tool that ensures the integrity, consistency, and completeness of the calibration infrastructure. This tool performs 35+ checks across 10 major sections of the calibration system.

## Purpose

This audit tool validates the **sophisticated, multi-layered epistemic governance framework** that implements:

1. **3-Tier Epistemic Hierarchy** (N1-EMP → N2-INF → N3-AUD)
2. **Contract TYPE-Specific Calibration** (6 types: TYPE_A through TYPE_E, plus SUBTIPO_F)
3. **Immutable, Frozen Calibration Layers** (design-time frozen, runtime immutable)
4. **Canonical Specs as Single Source of Truth** (no runtime JSON loading)
5. **Bounded Interaction Governance** (cycle detection, level inversion prevention)
6. **Fact Registry with Deduplication** (verbosity ≥ 0.90)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CALIBRATION INFRASTRUCTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│  canonical_specs.py ──────┐                                              │
│  (Frozen constants)       │                                              │
│                           ▼                                              │
│  type_defaults.py ──────────────────────────────────────┐                │
│  (TYPE_A-F defaults, Flyweight cached)                  │                │
│                                                          │                │
│  unit_of_analysis.py ──────┐                             │                │
│  (Municipal characteristics)│                            │                │
│                             ▼                            ▼                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    CALIBRATION LAYER                              │   │
│  │  - ClosedInterval (bounds)                                        │   │
│  │  - EvidenceReference (commit-pinned provenance)                   │   │
│  │  - CalibrationParameter (frozen, with rationale)                  │   │
│  │  - CalibrationLayer (immutable, manifest hash, Ed25519 sig)       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                             │                                            │
│           ┌─────────────────┼─────────────────┐                          │
│           ▼                 ▼                 ▼                          │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐               │
│  │ INGESTION      │ │ PHASE-2        │ │ AUDITOR        │               │
│  │ (N1-EMP)       │ │ (N2-INF)       │ │ (N3-AUD VETO)  │               │
│  └────────────────┘ └────────────────┘ └────────────────┘               │
│           │                 │                 │                          │
│           └─────────────────┼─────────────────┘                          │
│                             ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    GOVERNANCE LAYER                               │   │
│  │  - method_binding_validator.py (Chain of Responsibility)         │   │
│  │  - interaction_governor.py (Cycle/Inversion detection)           │   │
│  │  - fact_registry.py (Deduplication, verbosity >= 0.90)           │   │
│  │  - calibration_manifest.py (Audit trail, Memento pattern)        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Installation & Usage

### Prerequisites

```bash
# Ensure you're in the repository root
cd /path/to/FARFAN_MPP

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Basic Usage

Run the full audit:

```bash
python scripts/audit_calibration_system.py
```

### Output Formats

Generate reports in different formats:

```bash
# Markdown report (recommended for documentation)
python scripts/audit_calibration_system.py --output-format markdown --output-file AUDIT_REPORT.md

# JSON report (recommended for CI/CD integration)
python scripts/audit_calibration_system.py --output-format json --output-file AUDIT_REPORT.json

# Text report (recommended for terminal viewing)
python scripts/audit_calibration_system.py --output-format text
```

### Run Specific Sections

Run only a specific audit section:

```bash
# Run Section 1: Canonical Specs Completeness
python scripts/audit_calibration_system.py --section 1

# Run Section 2: TYPE Defaults Consistency
python scripts/audit_calibration_system.py --section 2

# Run Section 4: Interaction Governance
python scripts/audit_calibration_system.py --section 4
```

## Audit Sections

### Section 1: Canonical Specs Completeness

**Purpose:** Validates that all frozen constants in `canonical_specs.py` are complete and correct.

**Checks:**
- ✅ `CANON_POLICY_AREAS` has exactly 10 entries (PA01-PA10)
- ✅ `CANON_DIMENSIONS` has exactly 6 entries (DIM01-DIM06)
- ✅ `MICRO_LEVELS` maintain monotonic ordering (EXCELENTE > BUENO > ACEPTABLE > INSUFICIENTE)
- ✅ `CDAF_DOMAIN_WEIGHTS` sum to 1.0 (semantic + temporal + financial + structural)
- ✅ `CAUSAL_CHAIN_ORDER` values are sequential (0-5)
- 🔍 Searches for hardcoded parameters that should be migrated to `canonical_specs.py`

**Expected Invariants:**
```python
len(CANON_POLICY_AREAS) == 10
len(CANON_DIMENSIONS) == 6
MICRO_LEVELS["EXCELENTE"] > MICRO_LEVELS["BUENO"] > MICRO_LEVELS["ACEPTABLE"]
abs(sum(CDAF_DOMAIN_WEIGHTS.values()) - 1.0) < 1e-9
```

### Section 2: TYPE Defaults Consistency

**Purpose:** Validates epistemic ratio consistency and operation disjointness for all 6 contract types.

**Checks:**
- ✅ Epistemic layer ratios sum to 1.0 for each TYPE (N1 + N2 + N3 ≈ 1.0)
- ✅ Permitted and prohibited operations are disjoint (no overlaps)
- ✅ All 6 contract types can be loaded (TYPE_A, TYPE_B, TYPE_C, TYPE_D, TYPE_E, SUBTIPO_F)

**Contract Type Profiles:**

| TYPE | N1-EMP | N2-INF | N3-AUD | Veto Strictness | Use Case |
|------|--------|--------|--------|-----------------|----------|
| TYPE_A | 0.20-0.40 | 0.40-0.60 | 0.10-0.30 | STANDARD | Semantic triangulation |
| TYPE_B | 0.25-0.45 | 0.30-0.50 | 0.15-0.35 | STANDARD | Bayesian inference |
| TYPE_C | 0.20-0.40 | 0.25-0.45 | 0.25-0.45 | STANDARD | Causal DAG validation |
| TYPE_D | 0.15-0.35 | 0.45-0.65 | 0.10-0.30 | LENIENT | Financial aggregation |
| TYPE_E | 0.15-0.35 | 0.30-0.50 | 0.25-0.45 | STRICTEST | Logical consistency |
| SUBTIPO_F | 0.20-0.40 | 0.30-0.50 | 0.20-0.40 | STANDARD | Hybrid/Fallback |

### Section 3: Calibration Layer Invariants

**Purpose:** Validates core calibration parameter structure and evidence reference validity.

**Checks:**
- ✅ Required parameters defined (`prior_strength`, `veto_threshold`, `chunk_size`, `extraction_coverage_target`)
- ✅ Evidence prefixes valid (`src/`, `artifacts/`, `docs/`)
- ✅ Commit SHA pattern defined (40-character hex)

**Invariants:**
```python
REQUIRED_PARAMETERS = frozenset({
    "prior_strength",
    "veto_threshold",
    "chunk_size",
    "extraction_coverage_target",
})

VALID_EVIDENCE_PREFIXES = frozenset({"src/", "artifacts/", "docs/"})
COMMIT_SHA_PATTERN = r"^[0-9a-f]{40}$"
```

### Section 4: Interaction Governance

**Purpose:** Ensures method interactions are bounded and cycle-free.

**Checks:**
- ✅ Bounded fusion constants defined (`_MIN_PRODUCT = 0.01`, `_MAX_PRODUCT = 10.0`)
- 🔍 Searches for unbounded multiplications (should use `bounded_multiplicative_fusion()`)

**Key Invariants:**
- INV-INT-001: Dependency graph must be acyclic (DAG)
- INV-INT-002: Multiplicative fusion bounded in [0.01, 10.0]
- INV-INT-003: Veto cascade respects specificity ordering
- INV-INT-004: No level inversions (N3 cannot depend on N2 output directly)

### Section 5: Veto Threshold Calibration

**Purpose:** Validates veto threshold ranges for all contract types.

**Checks:**
- ✅ STRICTEST thresholds: [0.01, 0.05], default=0.03 (TYPE_E)
- ✅ STANDARD thresholds: [0.03, 0.07], default=0.05 (TYPE_A, TYPE_B, TYPE_C)
- ✅ LENIENT thresholds: [0.05, 0.10], default=0.07 (TYPE_D)

**Veto Threshold Philosophy:**
- **Strictest (TYPE_E):** Logical consistency must be near-absolute (1-5% tolerance)
- **Standard:** Balanced strictness for most epistemic operations (3-7% tolerance)
- **Lenient (TYPE_D):** Financial aggregation tolerates more variance (5-10% tolerance)

### Section 6: Prior Strength Calibration

**Purpose:** Validates Bayesian prior strength bounds.

**Checks:**
- ✅ Prior strength minimum: 0.1 (evidence-dominant)
- ✅ Prior strength default: 1.0 (balanced)
- ✅ Prior strength maximum: 10.0 (prior-dominant)
- ✅ Bayesian prior strength: 2.0 (TYPE_B stronger prior)

**Prior-Evidence Balance:**
```
Low prior (0.1-0.5):   Evidence-dominant
Neutral prior (1.0):    Balanced (default)
High prior (2.0-10.0):  Prior-dominant (TYPE_B)
```

### Section 7: Unit of Analysis Calibration

**Purpose:** Validates complexity score formula and calibration scaling.

**Checks:**
- ✅ Complexity score formula present in `unit_of_analysis.py`
- Expected formula: `complexity = 0.3 * log_pop + 0.3 * log_budget + 0.4 * policy_diversity`
- Weights sum to 1.0 (0.3 + 0.3 + 0.4 = 1.0)

**Calibration Scaling Strategies:**
- `StandardCalibrationStrategy`: 0.5 factor (typical PDT documents)
- `AggressiveCalibrationStrategy`: 0.8 factor (large/complex documents)
- `ConservativeCalibrationStrategy`: 0.3 factor (small/simple documents)

### Section 8: Fact Registry Verbosity

**Purpose:** Validates fact deduplication and verbosity requirements.

**Checks:**
- ✅ Verbosity threshold: 0.90 (90% unique facts required)
- Formula: `verbosity_ratio = unique_facts / total_submissions >= 0.90`

**Invariants:**
- INV-FACT-001: Every fact has exactly one canonical representation
- INV-FACT-002: Duplicate content triggers provenance logging, not addition
- INV-FACT-003: Verbosity ratio ≥ 0.90

### Section 9: Manifest & Audit Trail

**Purpose:** Validates calibration manifest and audit trail completeness.

**Checks:**
- ✅ `calibration_manifest.py` module exists
- Expected features: hash determinism, decision audit, provenance tracking

**Requirements:**
- Every `CalibrationDecision` must have:
  - Non-empty `rationale`
  - Non-empty `source_evidence`
  - Valid `decision_timestamp`

### Section 10: Missing Calibration Coverage

**Purpose:** Identifies modules with uncalibrated parameters that should use the calibration framework.

**Checks:**
- 🔍 Searches for threshold/weight/prior/veto keywords outside calibration infrastructure
- Reports modules that should integrate with the calibration system

**Search Keywords:**
```python
["threshold", "weight", "prior", "veto"]
```

## Interpreting Results

### Pass Rate

The audit provides a comprehensive pass rate:

```
Total Checks: 35
Passed: 32
Failed: 3
Pass Rate: 91.43%
```

**Interpretation:**
- **90-100%:** Excellent - system is well-calibrated
- **75-90%:** Good - minor improvements needed
- **50-75%:** Concerning - significant issues to address
- **<50%:** Critical - major calibration problems

### Severity Levels

Results are classified by severity:

| Severity | Meaning | Action Required |
|----------|---------|-----------------|
| **INFO** | Informational - system working as expected | None |
| **WARNING** | Minor issue - system functional but could be improved | Review and consider fixing |
| **ERROR** | Significant issue - may cause problems in production | Fix before deployment |
| **CRITICAL** | Severe issue - system integrity compromised | Fix immediately |

### Exit Codes

```bash
0 = SUCCESS (all checks passed or only warnings)
1 = ERRORS (one or more errors detected)
2 = CRITICAL (one or more critical issues detected)
```

Use in CI/CD:
```bash
python scripts/audit_calibration_system.py || exit 1
```

## Expected Audit Results

Based on the current system architecture, the typical audit results are:

```
✅ 32/35 checks passed (91.43% pass rate)
⚠️  3 warnings:
   - Section 1.2: 141 hardcoded parameters found (expected - existing codebase)
   - Section 4.1: 2 potential unbounded multiplications (to be reviewed)
   - Section 10.1: 132 modules with uncalibrated parameters (expected - existing codebase)
```

## Recommendations

### Priority 1: Critical Issues (None found in current audit)

✅ No critical issues detected.

### Priority 2: High-Priority Improvements

1. **Migrate Hardcoded Parameters** (Section 1.2)
   - Action: Review 141 hardcoded parameters
   - Target: Migrate high-frequency thresholds to `canonical_specs.py`
   - Timeline: Next sprint

2. **Bounded Multiplications** (Section 4.1)
   - Action: Review 2 potential unbounded multiplications
   - Target: Replace with `bounded_multiplicative_fusion()`
   - Timeline: Current sprint

### Priority 3: Medium-Priority Improvements

3. **Integrate Uncalibrated Modules** (Section 10.1)
   - Action: Review 132 modules with uncalibrated parameters
   - Target: Integrate high-value modules into calibration framework
   - Timeline: Next quarter

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Calibration Audit

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run Calibration Audit
        run: |
          python scripts/audit_calibration_system.py \
            --output-format json \
            --output-file calibration_audit.json
      
      - name: Upload Audit Report
        uses: actions/upload-artifact@v3
        with:
          name: calibration-audit-report
          path: calibration_audit.json
      
      - name: Check for Critical Issues
        run: |
          python -c "
          import json, sys
          with open('calibration_audit.json') as f:
              report = json.load(f)
          if report['summary']['critical'] > 0:
              print('CRITICAL ISSUES DETECTED')
              sys.exit(2)
          if report['summary']['errors'] > 0:
              print('ERRORS DETECTED')
              sys.exit(1)
          print('All checks passed')
          "
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running calibration audit..."
python scripts/audit_calibration_system.py --section 1 --section 2 --section 3
if [ $? -ne 0 ]; then
    echo "Calibration audit failed. Commit aborted."
    exit 1
fi
```

## Maintenance & Updates

### When to Run the Audit

1. **Before every major release** - Full audit
2. **After calibration changes** - Affected sections only
3. **Weekly in CI/CD** - Full audit with reporting
4. **During code review** - Specific sections if calibration code changed

### Extending the Audit

To add new checks:

1. Add a new method to `CalibrationAuditor` class:
   ```python
   def audit_section_11_new_feature(self) -> None:
       """Section 11: New Feature Validation."""
       # Your validation logic
       self.report.add_result(AuditResult(...))
   ```

2. Call it from `run_full_audit()`:
   ```python
   def run_full_audit(self) -> AuditReport:
       # ... existing sections ...
       self.audit_section_11_new_feature()
       return self.report
   ```

3. Update this documentation with the new section.

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'farfan_pipeline'`
**Solution:** Ensure you're running from repository root with `src/` in path.

**Issue:** "Canonical contracts file not found"
**Solution:** Ensure `src/farfan_pipeline/phases/Phase_two/epistemological_assets/contratos_clasificados.json` exists.

**Issue:** High number of hardcoded parameters reported
**Solution:** This is expected in a mature codebase. Prioritize migration of high-frequency constants.

## References

- **Architectural Analysis:** See problem statement for detailed system architecture
- **Canonical Specs:** `src/farfan_pipeline/calibracion_parametrizacion/canonical_specs.py`
- **Type Defaults:** `src/farfan_pipeline/infrastructure/calibration/type_defaults.py`
- **Calibration Core:** `src/farfan_pipeline/infrastructure/calibration/calibration_core.py`

## Version History

- **v1.0.0** (2026-01-09): Initial release with 10 audit sections and 35+ checks
