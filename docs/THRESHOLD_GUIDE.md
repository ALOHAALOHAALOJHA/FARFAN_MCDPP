# F.A.R.F.A.N Threshold Guide

**Quality Thresholds, Hard Gates, and PDT Structure Requirements**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [Layer Thresholds](#layer-thresholds)
3. [Hard Gates](#hard-gates)
4. [PDT Quality Thresholds](#pdt-quality-thresholds)
5. [Executor Thresholds](#executor-thresholds)
6. [Aggregation Thresholds](#aggregation-thresholds)
7. [Failure Modes](#failure-modes)
8. [Threshold Adjustment](#threshold-adjustment)

---

## Overview

F.A.R.F.A.N uses **quality thresholds** to classify analysis quality and **hard gates** to enforce minimum standards. Thresholds are calibrated per layer and role, with consistent bands:

- **EXCELLENT**: ≥ 0.7 (High quality)
- **GOOD**: 0.5 - 0.7 (Acceptable quality)
- **ACCEPTABLE**: 0.3 - 0.5 (Minimum viable)
- **DEFICIENT**: < 0.3 (Fails hard gate)

---

## Layer Thresholds

### @b: Intrinsic Quality

**Bands**:
- **≥ 0.7**: Production-ready, high confidence
- **0.5 - 0.7**: Acceptable, may need monitoring
- **0.3 - 0.5**: Risky, requires validation
- **< 0.3**: Unreliable, **HARD GATE** (executor fails)

**Components**:

#### b_theory (Theoretical Validity)
- **≥ 0.8**: Rigorous statistical foundation
- **0.6 - 0.8**: Sound but with minor gaps
- **0.4 - 0.6**: Weak assumptions or logic issues
- **< 0.4**: Fundamentally flawed

**Criteria**:
- Statistical tests correctly applied
- Sample sizes meet requirements
- Assumptions explicitly stated and justified
- No logical fallacies

#### b_impl (Implementation Quality)
- **≥ 0.8**: Excellent coverage, strict typing, comprehensive error handling
- **0.6 - 0.8**: Good coverage, adequate typing, basic error handling
- **0.4 - 0.6**: Partial coverage, some typing, minimal error handling
- **< 0.4**: Insufficient testing, weak typing

**Thresholds**:
```python
TEST_COVERAGE = {
    "excellent": 0.80,  # ≥80% line coverage
    "good": 0.60,       # ≥60% line coverage
    "acceptable": 0.40, # ≥40% line coverage
    "poor": 0.0,        # <40% line coverage
}

TYPE_ANNOTATION = {
    "excellent": 1.0,   # 100% annotated, mypy strict passes
    "good": 0.80,       # ≥80% annotated, some Any types
    "acceptable": 0.60, # ≥60% annotated
    "poor": 0.0,        # <60% annotated
}
```

#### b_deploy (Deployment Stability)
- **≥ 0.8**: Highly stable, ≥20 validation runs, CV < 0.05, failure rate < 1%
- **0.6 - 0.8**: Stable, ≥10 validation runs, CV < 0.10, failure rate < 5%
- **0.4 - 0.6**: Unstable, ≥5 validation runs, CV < 0.20, failure rate < 10%
- **< 0.4**: Unreliable

**Thresholds**:
```python
VALIDATION_RUNS = {
    "excellent": 20,  # ≥20 successful runs
    "good": 10,       # ≥10 successful runs
    "acceptable": 5,  # ≥5 successful runs
    "poor": 0,        # <5 successful runs
}

STABILITY_CV = {
    "excellent": 0.05,  # CV ≤ 5%
    "good": 0.10,       # CV ≤ 10%
    "acceptable": 0.20, # CV ≤ 20%
    "poor": float('inf'), # CV > 20%
}

FAILURE_RATE = {
    "excellent": 0.01,  # ≤1% failure rate
    "good": 0.05,       # ≤5% failure rate
    "acceptable": 0.10, # ≤10% failure rate
    "poor": 1.0,        # >10% failure rate
}
```

---

### @u: Unit Quality (PDT Structure)

**Bands**:
- **≥ 0.7**: Well-structured, complete PDT
- **0.5 - 0.7**: Acceptable structure with gaps
- **0.3 - 0.5**: Significant structural deficiencies
- **< 0.3**: Severely malformed PDT (analysis compromised)

**Component Thresholds** (S/M/I/P):

#### S: Structural Compliance
- **1.0**: All 4 blocks present, correct sequence, valid headers
- **0.75**: 3/4 blocks present, mostly correct sequence
- **0.50**: 2/4 blocks present or major sequence issues
- **< 0.50**: ≤1 block or completely disorganized

**Block Requirements**:
```python
BLOCK_PRESENCE = {
    "Diagnóstico": {"min_tokens": 1000},
    "Estratégica": {"min_tokens": 800},
    "PPI": {"min_tokens": 500},
    "Seguimiento": {"min_tokens": 300},
}
```

#### M: Mandatory Sections
- **≥ 0.8**: All required sections complete with rich content
- **0.6 - 0.8**: Most sections present, some content gaps
- **0.4 - 0.6**: Several missing sections or sparse content
- **< 0.4**: Critical sections missing

**Section Criteria**:
```python
DIAGNOSTICO_REQUIREMENTS = {
    "baseline_data": {"min_indicators": 5},
    "data_sources": {"min_sources": 3, "valid_sources": ["DANE", "Medicina Legal", "Defensoría"]},
    "gap_analysis": {"min_mentions": 3, "keywords": ["brecha", "déficit", "carencia"]},
}

ESTRATEGICA_REQUIREMENTS = {
    "strategic_axes": {"min_count": 3},
    "objectives_smart": True,  # Must be specific, measurable, achievable, relevant, time-bound
    "theory_of_change": {"implicit_or_explicit": True},
}
```

#### I: Indicator Quality
- **≥ 0.8**: Complete indicator matrix, all fields populated, realistic targets
- **0.6 - 0.8**: Matrix present, most fields populated, some target issues
- **0.4 - 0.6**: Matrix present but many gaps
- **< 0.4**: No matrix or severely incomplete

**Matrix Requirements**:
```python
INDICATOR_FIELDS = [
    "tipo",                  # Producto/Resultado/Impacto
    "linea_estrategica",     # Strategic line reference
    "programa",              # Program name
    "linea_base",            # Baseline value + year
    "meta_cuatrienio",       # 4-year target
    "fuente",                # Data source
    "unidad_medida",         # Measurement unit
    "codigo_mga",            # National code (optional)
]

INDICATOR_REALISM = {
    "max_increase_percent": 500,  # Targets >500% increase flagged as unrealistic
    "baseline_year_valid": True,  # Must be recent (2020-2023)
}
```

#### P: PPI Completeness
- **≥ 0.8**: Complete investment plan with detailed budgets
- **0.6 - 0.8**: Budget table present, some details missing
- **0.4 - 0.6**: Budget table present but major gaps
- **< 0.4**: No budget table or severely incomplete

**Budget Requirements**:
```python
PPI_BUDGET_FIELDS = [
    "programa",              # Program name
    "costo_total",           # Total cost (4 years)
    "año_1", "año_2", "año_3", "año_4",  # Annual breakdown
    "sgp", "sgr", "propios", "otras",    # Funding sources
]

BUDGET_COHERENCE = {
    "annual_sum_equals_total": True,
    "source_sum_equals_total": True,
    "no_negative_values": True,
}
```

---

### @q: Question Appropriateness

**Bands**:
- **≥ 0.7**: Method is appropriate for question
- **0.5 - 0.7**: Method is partially appropriate
- **0.3 - 0.5**: Weak fit, consider fallback
- **< 0.3**: Inappropriate method

**Semantic Alignment Thresholds**:
```python
SEMANTIC_SIMILARITY = {
    "high": 0.75,       # Method directly addresses question
    "medium": 0.50,     # Method partially relevant
    "low": 0.25,        # Method tangentially related
}
```

**Priority Mapping Matrix**:
```python
PRIORITY_MATRIX = {
    (1, 1): 1.0,   # P1 question, P1 method: Perfect match
    (1, 2): 0.7,   # P1 question, P2 method: Under-qualified
    (1, 3): 0.4,   # P1 question, P3 method: Significantly under-qualified
    (2, 1): 0.9,   # P2 question, P1 method: Over-qualified (acceptable)
    (2, 2): 1.0,   # P2 question, P2 method: Perfect match
    (2, 3): 0.6,   # P2 question, P3 method: Under-qualified
    (3, 1): 0.8,   # P3 question, P1 method: Over-qualified (good)
    (3, 2): 0.9,   # P3 question, P2 method: Over-qualified (acceptable)
    (3, 3): 1.0,   # P3 question, P3 method: Perfect match
}
```

---

### @d: Dimension Alignment

**Bands**:
- **≥ 0.8**: Method is well-suited for dimension
- **0.6 - 0.8**: Method is acceptable for dimension
- **0.4 - 0.6**: Method has weak fit
- **< 0.4**: Method inappropriate for dimension

**Dimension-Specific Requirements**:

#### D1: INSUMOS (Inputs)
- Statistical profiling capability
- Baseline extraction
- Data quality assessment
- **Minimum**: Quantitative analysis methods

#### D2: ACTIVIDADES (Activities)
- Logical framework analysis
- Feasibility assessment
- Resource mapping
- **Minimum**: Planning/design methods

#### D3: PRODUCTOS (Outputs)
- Output quantification
- Deliverable tracking
- Timeline validation
- **Minimum**: Concrete output analysis

#### D4: RESULTADOS (Outcomes)
- Outcome logic validation
- Attribution analysis
- Indicator-outcome alignment
- **Minimum**: Causal inference capability

#### D5: IMPACTOS (Impacts)
- Impact pathway analysis
- Long-term projection
- Sustainability assessment
- **Minimum**: Structural change detection

#### D6: CAUSALIDAD (Theory of Change)
- Causal inference methods
- Mechanism tracing
- Assumption testing
- **Minimum**: Explicit causal framework

---

### @p: Policy Area Fit

**Bands**:
- **≥ 0.7**: Method well-suited for policy area
- **0.5 - 0.7**: Method generally applicable
- **0.3 - 0.5**: Method lacks domain specificity
- **< 0.3**: Method inappropriate for domain

**Domain Knowledge Requirements** (varies by PA01-PA10):

```python
POLICY_AREA_REQUIREMENTS = {
    "PA01": {  # Gender equality
        "domain_keywords": ["género", "mujer", "violencia de género", "equidad"],
        "indicator_types": ["gender gap", "women's participation", "GBV rates"],
        "frameworks": ["gender mainstreaming", "intersectionality"],
    },
    "PA02": {  # Violence prevention
        "domain_keywords": ["violencia", "conflicto", "seguridad", "víctima"],
        "indicator_types": ["homicide rate", "displacement", "armed confrontations"],
        "frameworks": ["conflict analysis", "security metrics"],
    },
    # ... PA03-PA10
}
```

---

### @C: Contract Compliance

**Bands**:
- **≥ 0.9**: Excellent contract compliance
- **0.7 - 0.9**: Good compliance with minor issues
- **0.5 - 0.7**: Acceptable compliance with notable issues
- **< 0.5**: Poor compliance, **HARD GATE** (execution fails)

**Component Thresholds**:

#### c_scale (Scalar Conformance)
```python
SCALAR_CHECKS = {
    "numeric_range": (0.0, 1.0),  # All scores must be in [0, 1]
    "no_nan": True,
    "no_inf": True,
    "no_negatives": True,  # Unless explicitly allowed
    "precision": 4,  # 4 decimal places
}
```

#### c_sem (Semantic Conformance)
```python
SEMANTIC_CHECKS = {
    "type_matching": True,  # All fields match declared types
    "enum_validation": True,  # Enum values from allowed sets
    "format_validation": {
        "dates": "ISO-8601",
        "urls": "RFC-3986",
        "emails": "RFC-5322",
    },
}
```

#### c_fusion (Aggregation Readiness)
```python
AGGREGATION_CHECKS = {
    "missing_value_handling": True,  # Explicit None vs 0.0
    "provenance_populated": True,    # Source tracking present
    "metadata_complete": ["confidence", "uncertainty"],
}
```

---

### @chain: Data Flow Integrity

**Binary Scoring** (no gradations):
- **1.0**: Chain is intact (PASS)
- **0.0**: Chain is broken (FAIL - **HARD GATE**)

**Validation Checks**:

```python
CHAIN_CHECKS = {
    "dependency_resolution": {
        "description": "All required inputs available",
        "required": True,
    },
    "schema_validation": {
        "description": "Inputs match expected schemas",
        "required": True,
    },
    "provenance_chain": {
        "description": "Evidence traces back to source",
        "required": True,
    },
    "information_preservation": {
        "description": "Critical fields preserved",
        "required": True,
    },
    "temporal_ordering": {
        "description": "Dependencies respect execution order",
        "required": True,
    },
}
```

**Failure = Execution Abort**: If ANY check fails, @chain = 0.0 and execution aborts.

---

### @m: Governance Maturity

**Bands**:
- **≥ 0.7**: High governance maturity
- **0.5 - 0.7**: Medium governance maturity
- **0.3 - 0.5**: Low governance maturity
- **< 0.3**: Very weak governance (institutional concerns)

**Component Thresholds**:

#### m_transp (Transparency)
```python
TRANSPARENCY_CRITERIA = {
    "sources_cited": {
        "min_count": 5,
        "valid_sources": ["DANE", "Medicina Legal", "Defensoría", "Contraloría"],
    },
    "methodologies_described": {"min_count": 3},
    "assumptions_explicit": {"min_count": 5},
    "public_participation": {"documented": True},
}
```

#### m_gov (Governance Structure)
```python
GOVERNANCE_CRITERIA = {
    "roles_clarity": True,              # Responsibilities assigned
    "coordination_mechanisms": True,    # Inter-institutional coordination
    "monitoring_framework": True,       # Tracking mechanisms
    "evaluation_plan": True,            # Assessment methodology
}
```

#### m_cost (Cost Realism)
```python
COST_CRITERIA = {
    "budgets_detailed": True,           # Line-item breakdowns
    "budgets_realistic": True,          # Market-rate costs
    "funding_sources_identified": True, # SGP/SGR/Propios/Otras
    "contingency_planning": True,       # Overrun strategies
}
```

---

## Hard Gates

### Definition

A **hard gate** is a threshold that, when violated, causes execution to **fail immediately** with no fallback.

### Active Hard Gates

1. **@b < 0.3**: Method is fundamentally unreliable
   - **Action**: Executor fails, error logged
   - **Remediation**: Improve method quality or replace method

2. **@chain = 0.0**: Data flow is broken
   - **Action**: Execution aborts immediately
   - **Remediation**: Fix dependency resolution or schema validation

3. **@C < 0.5**: Contract violations compromise interoperability
   - **Action**: Executor fails, contract error logged
   - **Remediation**: Fix output schema or type errors

### Soft Thresholds (Warnings Only)

- **@u < 0.5**: PDT quality is poor (warning logged, execution continues)
- **@q < 0.5**: Method-question fit is weak (warning logged, score penalized)
- **@m < 0.3**: Governance is weak (warning logged, institutional concerns noted)

---

## PDT Quality Thresholds

### Overall PDT Score (@u)

Computed as:
```
@u = 0.30 × S + 0.25 × M + 0.25 × I + 0.20 × P
```

**Classification**:

| Score | Band | Description | Action |
|-------|------|-------------|--------|
| ≥ 0.7 | EXCELLENT | Complete, well-structured PDT | Full analysis |
| 0.5 - 0.7 | GOOD | Acceptable structure | Full analysis, note gaps |
| 0.3 - 0.5 | ACCEPTABLE | Significant gaps | Full analysis, strong caveats |
| < 0.3 | DEFICIENT | Severely malformed | Warning, limited confidence |

### Critical Block Thresholds

**Diagnóstico Block**:
- **Minimum length**: 1000 tokens
- **Minimum indicators**: 5 quantitative metrics
- **Minimum sources**: 3 data sources cited

**Estratégica Block**:
- **Minimum length**: 800 tokens
- **Minimum axes**: 3 strategic lines
- **Requirement**: SMART objectives present

**PPI Block**:
- **Minimum length**: 500 tokens
- **Requirement**: Investment plan table present
- **Requirement**: Budget totals coherent

**Seguimiento Block**:
- **Minimum length**: 300 tokens
- **Requirement**: Monitoring framework described

---

## Executor Thresholds

### Timeout Thresholds

```python
EXECUTOR_TIMEOUTS = {
    "simple": 30,      # Simple executors (< 1000 LOC)
    "moderate": 60,    # Moderate complexity (1000-5000 LOC)
    "complex": 120,    # Complex executors (> 5000 LOC or Bayesian)
    "extreme": 300,    # Extreme cases (e.g., full SCM simulation)
}
```

**Behavior**:
- If executor exceeds timeout, execution aborts
- Timeout violation penalizes @m (governance/cost layer)
- Fallback method triggered (if configured)

### Memory Thresholds

```python
EXECUTOR_MEMORY_LIMITS = {
    "minimal": 128,    # 128 MB
    "standard": 512,   # 512 MB
    "intensive": 2048, # 2 GB
    "extreme": 8192,   # 8 GB
}
```

**Behavior**:
- Memory usage monitored via circuit breaker
- If limit exceeded, execution aborts
- Memory violations logged for calibration adjustment

---

## Aggregation Thresholds

### Dimension Aggregation (Phase 4)

Aggregates 5 question scores (Q1-Q5) → 1 dimension score (D1-D6).

**Confidence Thresholds**:
```python
DIMENSION_CONFIDENCE = {
    "high": 0.85,      # All 5 questions scored ≥ 0.7
    "medium": 0.65,    # ≥3 questions scored ≥ 0.5
    "low": 0.45,       # ≥1 question scored ≥ 0.3
}
```

**Action**:
- High confidence: Full weight in policy area aggregation
- Medium confidence: Reduced weight (×0.8)
- Low confidence: Strong caveat in report

### Policy Area Aggregation (Phase 5)

Aggregates 6 dimension scores (D1-D6) → 1 policy area score (PA01-PA10).

**Choquet Integral** with interaction terms.

**Thresholds**:
- **≥ 0.7**: Policy area is well-addressed
- **0.5 - 0.7**: Policy area is partially addressed
- **0.3 - 0.5**: Policy area has gaps
- **< 0.3**: Policy area is severely underdeveloped

### Macro Evaluation (Phase 7)

Aggregates all policy areas + clusters → holistic band.

**Bands**:
- **EXCELENTE**: Overall score ≥ 0.7, no critical gaps
- **BUENO**: Overall score 0.5 - 0.7, minor gaps
- **ACEPTABLE**: Overall score 0.3 - 0.5, notable gaps
- **DEFICIENTE**: Overall score < 0.3, critical deficiencies

---

## Failure Modes

### Mode 1: Method Failure (@b < 0.3)

**Trigger**: Intrinsic quality below minimum threshold.

**Symptoms**:
- Test coverage < 40%
- Deployment stability CV > 20%
- Failure rate > 10%

**Action**:
1. Log error with method_id and @b score
2. Abort executor
3. If fallback configured, trigger fallback method
4. If no fallback, mark question as "method_unreliable"

**Report**: "Analysis unavailable due to insufficient method quality."

---

### Mode 2: Chain Failure (@chain = 0.0)

**Trigger**: Data flow integrity violation.

**Symptoms**:
- Missing required input
- Schema mismatch
- Provenance chain broken

**Action**:
1. Log chain failure with specific check that failed
2. Abort execution immediately (no fallback)
3. Generate partial report with error details

**Report**: "Execution aborted due to data flow integrity violation."

---

### Mode 3: Contract Failure (@C < 0.5)

**Trigger**: Output contract violations.

**Symptoms**:
- Scores out of range [0, 1]
- Type mismatches
- Missing required fields

**Action**:
1. Log contract violation with field details
2. Abort executor
3. Trigger fallback if configured
4. Mark output as "contract_violation"

**Report**: "Result unavailable due to contract compliance failure."

---

### Mode 4: PDT Quality Warning (@u < 0.3)

**Trigger**: Severely malformed PDT.

**Symptoms**:
- Missing critical blocks (≤1/4 present)
- No indicator matrix
- No budget table

**Action**:
1. Log PDT quality warning
2. Continue execution (warning only, not hard gate)
3. Reduce confidence in all results
4. Add prominent caveat to report

**Report**: "Results have limited confidence due to poor PDT structure."

---

## Threshold Adjustment

### When to Adjust Thresholds

**Valid reasons**:
1. **Cohort recalibration**: New validation data suggests different cutoffs
2. **Regulatory changes**: Policy requirements change (e.g., Law 152/1994 updated)
3. **Method evolution**: New methods with different score distributions
4. **Empirical validation**: Thresholds misaligned with expert assessments

**Invalid reasons**:
❌ Lowering thresholds to pass more executors
❌ Per-execution tuning
❌ Gaming specific PDTs

### Adjustment Procedure

1. **Empirical Analysis**:
   ```python
   # Analyze score distributions
   scores = [executor.score for executor in all_executors]
   percentiles = np.percentile(scores, [25, 50, 75, 90])
   
   # Compare with expert assessments
   expert_labels = ["excellent", "good", "acceptable", "deficient"]
   correlation = compare_thresholds_to_experts(scores, expert_labels)
   ```

2. **Propose New Thresholds**:
   ```python
   NEW_THRESHOLDS = {
       "excellent": percentiles[90],  # Top 10%
       "good": percentiles[75],       # Top 25%
       "acceptable": percentiles[50], # Median
       "deficient": 0.0,
   }
   ```

3. **Validate on Holdout**:
   - Test on held-out PDTs (≥50)
   - Measure classification accuracy
   - Check for boundary effects

4. **Document and Version**:
   - Update COHORT_MANIFEST.json
   - Increment cohort version
   - Record rationale

---

## Related Documentation

- [LAYER_SYSTEM.md](./LAYER_SYSTEM.md) - Detailed layer descriptions
- [FUSION_FORMULA.md](./FUSION_FORMULA.md) - Choquet integral mathematics
- [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md) - Configuration schemas
- [VALIDATION_GUIDE.md](./VALIDATION_GUIDE.md) - How to validate system integrity

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit
