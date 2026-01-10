# FARFAN Calibration & Parametrization System Audit Report

**Timestamp:** 2026-01-09T22:19:39.046876+00:00

## Executive Summary

- **Total Checks:** 35
- **Passed:** 32
- **Failed:** 3
- **Pass Rate:** 91.43%
- **Warnings:** 3
- **Errors:** 0
- **Critical:** 0

## Audit Results by Section

### Section 1.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Policy Areas Count | CANON_POLICY_AREAS has 10 entries (expected 10) | - |
| ✓ | Policy Areas Format | All policy area keys follow PA## format | - |
| ✓ | Dimensions Count | CANON_DIMENSIONS has 6 entries (expected 6) | - |
| ✓ | Dimensions Format | All dimension keys follow DIM## format | - |
| ✓ | Micro Levels Monotonicity | MICRO_LEVELS maintain monotonic ordering | - |
| ✓ | CDAF Domain Weights Sum | Domain weights sum to 1.0000000000 (expected 1.0) | - |
| ✓ | Causal Chain Sequential | CAUSAL_CHAIN_ORDER values are sequential | - |
| ✓ | Canonical Specs Validation Function | All canonical specs validation checks passed | - |

### Section 1.2

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✗ | Hardcoded Parameters | Found 141 hardcoded parameters outside canonical_specs | WARNING |

### Section 10.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✗ | Uncalibrated Modules | Found 132 modules with potential uncalibrated parameters | WARNING |

### Section 2.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Epistemic Ratio Sum - TYPE_A | TYPE_A: Ratio sum = 1.0000 | - |
| ✓ | Epistemic Ratio Sum - TYPE_D | TYPE_D: Ratio sum = 1.0000 | - |
| ✓ | Epistemic Ratio Sum - TYPE_C | TYPE_C: Ratio sum = 1.0000 | - |
| ✓ | Epistemic Ratio Sum - SUBTIPO_F | SUBTIPO_F: Ratio sum = 1.0000 | - |
| ✓ | Epistemic Ratio Sum - TYPE_B | TYPE_B: Ratio sum = 1.0000 | - |
| ✓ | Epistemic Ratio Sum - TYPE_E | TYPE_E: Ratio sum = 1.0000 | - |

### Section 2.3

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Operations Disjointness - TYPE_A | TYPE_A: No overlap between permitted/prohibited | - |
| ✓ | Operations Disjointness - TYPE_D | TYPE_D: No overlap between permitted/prohibited | - |
| ✓ | Operations Disjointness - TYPE_C | TYPE_C: No overlap between permitted/prohibited | - |
| ✓ | Operations Disjointness - SUBTIPO_F | SUBTIPO_F: No overlap between permitted/prohibited | - |
| ✓ | Operations Disjointness - TYPE_B | TYPE_B: No overlap between permitted/prohibited | - |
| ✓ | Operations Disjointness - TYPE_E | TYPE_E: No overlap between permitted/prohibited | - |

### Section 3.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Required Parameters Defined | Required parameters set defined: frozenset({'chunk_size', 'prior_strength', 'extraction_coverage_target', 'veto_threshold'}) | - |

### Section 3.2

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Evidence Prefixes Defined | Valid evidence prefixes: frozenset({'docs/', 'src/', 'artifacts/'}) | - |
| ✓ | Commit SHA Pattern Defined | Commit SHA pattern defined: ^[0-9a-f]{40}$ | - |

### Section 4.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Bounded Fusion Constants | Fusion bounds: [0.01, 10.0] | - |
| ✗ | Unbounded Multiplications | Found 2 potential unbounded multiplications | WARNING |

### Section 5.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Veto Threshold Range - STRICTEST | STRICTEST: [0.01, 0.05], default=0.03 | - |
| ✓ | Veto Threshold Range - STANDARD | STANDARD: [0.03, 0.07], default=0.05 | - |
| ✓ | Veto Threshold Range - LENIENT | LENIENT: [0.05, 0.1], default=0.07 | - |

### Section 6.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Prior Strength Default Bounds | Prior strength: min=0.1, default=1.0, max=10.0 | - |
| ✓ | Bayesian Prior Strength Bounds | Bayesian prior strength 2.0 within bounds | - |

### Section 7.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Complexity Score Formula Present | Complexity score formula found in unit_of_analysis.py | - |

### Section 8.1

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Verbosity Threshold | Verbosity threshold: 0.9 (expected 0.90) | - |

### Section 9

| Status | Check | Message | Severity |
|--------|-------|---------|----------|
| ✓ | Manifest Module Exists | calibration_manifest.py found | - |

## Recommendations

- 📌 Review 3 warning(s) for potential improvements
- 📋 Section 1: Migrate hardcoded parameters to canonical_specs.py
- 📋 Section 4: Replace unbounded multiplications with bounded_multiplicative_fusion()
- 📋 Section 10: Integrate uncalibrated modules into calibration framework
