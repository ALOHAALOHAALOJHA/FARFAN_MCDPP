# Intrinsic Calibration Report

**Generated:** 2025-12-08T01:40:02.502507+00:00

## Summary Statistics

- **Total Methods:** 2250
- **Computed:** 1375 (61.11%)
- **Excluded:** 875 (38.89%)
- **Pending:** 0 (0.00%)
- **Coverage:** 61.11%

## Calibration Status Distribution

| Status | Count | Percentage |
|--------|-------|------------|
| Computed | 1375 | 61.11% |
| Excluded | 875 | 38.89% |
| Pending | 0 | 0.00% |

## Layer Distribution

| Layer | Total | Computed | Excluded | Pending |
|-------|-------|----------|----------|---------|
| analyzer | 540 | 471 | 69 | 0 |
| ingestion | 171 | 94 | 77 | 0 |
| orchestrator | 531 | 465 | 66 | 0 |
| processor | 60 | 53 | 7 | 0 |
| utility | 948 | 292 | 656 | 0 |

## Score Statistics (Computed Methods Only)

### b_theory
- **Mean:** 0.180
- **Min:** 0.180
- **Max:** 0.180
- **Median:** 0.180

### b_impl
- **Mean:** 0.160
- **Min:** 0.160
- **Max:** 0.160
- **Median:** 0.160

### b_deploy
- **Mean:** 0.508
- **Min:** 0.424
- **Max:** 0.593
- **Median:** 0.508

## Top Exclusion Reasons

| Reason | Count |
|--------|-------|
| Non-analytical utility function | 377 |
| Constructor - non-analytical | 223 |
| Private utility function - non-analytical | 194 |
| Serialization - non-semantic | 57 |
| Logging utility - non-semantic | 9 |
| String representation - non-analytical | 6 |
| Formatting utility - non-semantic | 6 |
| Length accessor - non-analytical | 2 |
| Print utility - non-semantic | 1 |

## Methodology

This calibration was generated using the rigorous triage process:

1. **Exclusion Rules:** Methods matching exclusion patterns (e.g., `__init__`, formatters) are excluded
2. **Decision Automaton:** Three-question gate determines calibration requirement:
   - Q1: Analytically active?
   - Q2: Parametric (encodes assumptions)?
   - Q3: Safety-critical?
3. **Score Computation:** For computable methods, calculate:
   - **b_theory:** Statistical grounding, logical consistency, assumptions
   - **b_impl:** Test coverage, type annotations, error handling, documentation
   - **b_deploy:** Layer maturity baseline with validation/stability/failure factors

All scores are traceable and reproducible from the rubric and method metadata.

**Rubric Version:** 1.1.0

---

*See evidence_traces/ directory for detailed computation traces.*