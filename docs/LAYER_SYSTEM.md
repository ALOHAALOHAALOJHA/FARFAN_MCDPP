# F.A.R.F.A.N 8-Layer Quality System

**Detailed Explanation of Layer Architecture and Evaluation**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [Layer 1: @b - Intrinsic Quality](#layer-1-b---intrinsic-quality)
3. [Layer 2: @u - Unit Quality](#layer-2-u---unit-quality)
4. [Layer 3: @q - Question Appropriateness](#layer-3-q---question-appropriateness)
5. [Layer 4: @d - Dimension Alignment](#layer-4-d---dimension-alignment)
6. [Layer 5: @p - Policy Area Fit](#layer-5-p---policy-area-fit)
7. [Layer 6: @C - Contract Compliance](#layer-6-c---contract-compliance)
8. [Layer 7: @chain - Data Flow Integrity](#layer-7-chain---data-flow-integrity)
9. [Layer 8: @m - Governance Maturity](#layer-8-m---governance-maturity)
10. [Layer Fusion](#layer-fusion)
11. [Priority Mappings](#priority-mappings)

---

## Overview

The F.A.R.F.A.N system evaluates analytical methods and execution results through **8 independent quality layers**. Each layer captures a distinct dimension of quality, from code correctness to institutional maturity. Layers are fused using a **Choquet integral** to capture synergies and interactions between quality dimensions.

### Why 8 Layers?

The layer system emerged from empirical calibration of 584 analytical methods across 30 D×Q executors. Eight layers provide:

1. **Comprehensive Coverage**: From code quality to policy alignment
2. **Separation of Concerns**: Independent evaluation without conflation
3. **Synergy Capture**: Interaction terms reveal quality multiplicators
4. **Role Specificity**: Different method roles require different layer subsets
5. **Traceable Scoring**: Each layer has explicit formulas and thresholds

### Layer Requirements by Role

| Role | Layers Required | Count | Rationale |
|------|----------------|-------|-----------|
| **Ingest** | @b, @chain, @u, @m | 4 | Focus on data quality and governance |
| **Processor** | @b, @chain, @u, @m | 4 | Similar to ingest, emphasizes structure |
| **Analyzer** | ALL 8 layers | 8 | Full evaluation (question-method alignment) |
| **Executor** | ALL 8 layers | 8 | Complete policy analysis requires all layers |
| **Utility** | @b, @chain, @m | 3 | Core quality without contextual alignment |
| **Orchestrator** | @b, @chain, @m | 3 | Coordination quality, no domain specifics |

---

## Layer 1: @b - Intrinsic Quality

**Symbol**: `@b`  
**Focus**: Base method quality (code correctness, testing, deployment stability)  
**Weight Range**: 0.15 - 0.20 (highest priority layer)

### Purpose

Evaluates the fundamental quality of the analytical method independent of its application context. A method with low `@b` is unreliable regardless of how well it fits the policy question.

### Components

#### 1. b_theory: Theoretical Validity (0.0 - 1.0)

**Formula**:
```
b_theory = 0.4 × statistical_validity + 0.3 × logical_consistency + 0.3 × appropriate_assumptions
```

**Criteria**:

- **statistical_validity** (0.4 weight):
  - Statistical tests are correctly applied
  - Sample sizes meet minimum requirements
  - Confidence intervals are properly computed
  - P-values are interpreted correctly (no p-hacking)

- **logical_consistency** (0.3 weight):
  - Reasoning chains are sound (no logical fallacies)
  - Conclusions follow from premises
  - Edge cases are handled correctly
  - No circular dependencies

- **appropriate_assumptions** (0.3 weight):
  - Assumptions are explicitly stated
  - Assumptions are justified for the domain
  - Violations are detected and reported
  - Sensitivity analysis validates robustness

**Example**:
```python
# D6_Q5_TheoryOfChange (Bayesian causal inference)
b_theory = 0.4 × 0.92 + 0.3 × 0.88 + 0.3 × 0.85 = 0.887
# High score: uses PyMC with proper priors, explicit DAG, sensitivity checks
```

#### 2. b_impl: Implementation Quality (0.0 - 1.0)

**Formula**:
```
b_impl = 0.35 × test_coverage + 0.25 × type_annotations + 0.25 × error_handling + 0.15 × documentation
```

**Criteria**:

- **test_coverage** (0.35 weight):
  - Unit tests for core logic
  - Integration tests for data flow
  - Edge case coverage
  - Regression tests for known issues
  - Target: ≥80% line coverage

- **type_annotations** (0.25 weight):
  - All functions have type hints
  - TypedDict contracts at boundaries
  - mypy strict mode passes
  - No `Any` types except justified cases

- **error_handling** (0.25 weight):
  - Exceptions are typed and specific
  - Error messages are actionable
  - Failures are logged with context
  - Resources are properly cleaned up

- **documentation** (0.15 weight):
  - Docstrings for public functions
  - Parameter descriptions
  - Return value descriptions
  - Example usage (if complex)

**Example**:
```python
# D2_Q3_ActivityDesign (intervention planning)
b_impl = 0.35 × 0.87 + 0.25 × 0.95 + 0.25 × 0.82 + 0.15 × 0.78 = 0.862
# High coverage, strict typing, good error handling, adequate docs
```

#### 3. b_deploy: Deployment Stability (0.0 - 1.0)

**Formula**:
```
b_deploy = 0.4 × validation_runs + 0.35 × stability_coefficient + 0.25 × failure_rate
```

**Criteria**:

- **validation_runs** (0.4 weight):
  - Number of successful validation runs
  - Diversity of input data
  - Cross-validation on held-out data
  - Minimum: 10 runs on representative data

- **stability_coefficient** (0.35 weight):
  - Output variance across runs (lower is better)
  - Sensitivity to input perturbations
  - Deterministic execution (seed control)
  - Target: CV < 0.05 for key metrics

- **failure_rate** (0.25 weight):
  - Proportion of executions that fail
  - Graceful degradation behavior
  - Recovery from transient errors
  - Target: < 1% failure rate

**Example**:
```python
# D1_Q1_DiagnosticQuality (baseline analysis)
b_deploy = 0.4 × 0.98 + 0.35 × 0.91 + 0.25 × 0.95 = 0.947
# 50+ validation runs, CV=0.023, 0.3% failure rate
```

### Final @b Score

```
@b = (b_theory + b_impl + b_deploy) / 3
```

Equal weighting reflects that all three components are necessary for intrinsic quality.

### Thresholds

- **@b ≥ 0.7**: HIGH - Method is production-ready
- **0.5 ≤ @b < 0.7**: MEDIUM - Method needs improvement
- **@b < 0.5**: LOW - Method is not reliable (hard gate: executor fails)

---

## Layer 2: @u - Unit Quality

**Symbol**: `@u`  
**Focus**: Document structure quality (PDT compliance)  
**Weight Range**: 0.03 - 0.05 (context-dependent)

### Purpose

Evaluates the quality of the input document (PDT) based on its structural completeness. A well-structured PDT enables higher-quality analysis across all dimensions.

### PDT Structure Components (S/M/I/P)

The Colombian PDT standard defines four critical components:

#### S: Structural Compliance (0.0 - 1.0)

**Criteria**:
- **Block Presence**: All 4 mandatory blocks present
  - Diagnóstico (baseline analysis)
  - Parte Estratégica (strategic vision)
  - PPI (investment plan)
  - Seguimiento (monitoring)
  
- **Block Sequence**: Blocks appear in canonical order
  
- **Header Hierarchy**: Proper numbering (1., 1.1, 1.1.1, etc.)
  
- **Token Distribution**: Each block meets minimum length
  - Diagnóstico: ≥1000 tokens
  - Estratégica: ≥800 tokens
  - PPI: ≥500 tokens
  - Seguimiento: ≥300 tokens

**Scoring**:
```
S = (blocks_found / 4) × 0.5 + (sequence_valid ? 0.25 : 0.0) + (headers_valid / total_headers) × 0.25
```

**Example**:
```python
# High-quality PDT
S = (4/4) × 0.5 + 1 × 0.25 + (45/47) × 0.25 = 0.989
```

#### M: Mandatory Sections (0.0 - 1.0)

**Criteria**:
- **Diagnóstico Section**:
  - Baseline data present (≥5 quantitative indicators)
  - Data sources cited (DANE, Medicina Legal, etc.)
  - Gap analysis ("brecha") mentioned ≥3 times
  
- **Estratégica Section**:
  - Strategic axes defined (≥3 axes)
  - Objectives are SMART (measurable)
  - Theory of Change implicit or explicit
  
- **PPI Section**:
  - Programs linked to objectives
  - Budget allocations per program
  - Timeline (4-year breakdown)
  
- **Seguimiento Section**:
  - Monitoring framework described
  - Evaluation methodology specified
  - Responsible entities identified

**Scoring**:
```
M = Σ(section_score) / 4
where section_score = (criteria_met / criteria_total) per section
```

**Example**:
```python
# Medium-quality PDT
M_diag = 0.83  # 5/6 criteria
M_estra = 0.67  # 4/6 criteria
M_ppi = 0.75  # 3/4 criteria
M_seg = 0.50  # 2/4 criteria
M = (0.83 + 0.67 + 0.75 + 0.50) / 4 = 0.688
```

#### I: Indicator Quality (0.0 - 1.0)

**Criteria**:
- **Indicator Table Present**: Table detected in PDF
  
- **Indicator Completeness**: Each row has:
  - Tipo (Producto/Resultado/Impacto)
  - Línea Estratégica
  - Programa
  - Línea Base (baseline value + year)
  - Meta Cuatrienio (4-year target)
  - Fuente (data source)
  - Unidad de Medida (measurement unit)
  - Código MGA (national code, if applicable)
  
- **Indicator Coverage**: Indicators cover all strategic axes
  
- **Indicator Realism**: Targets are achievable (not >500% increase)

**Scoring**:
```
I_presence = 1.0 if table_found else 0.0
I_complete = rows_complete / total_rows
I_coverage = axes_covered / total_axes
I_realism = realistic_targets / total_targets
I = 0.4 × I_presence + 0.25 × I_complete + 0.20 × I_coverage + 0.15 × I_realism
```

**Example**:
```python
# Good indicator matrix
I = 0.4 × 1.0 + 0.25 × 0.88 + 0.20 × 0.92 + 0.15 × 0.85 = 0.931
```

#### P: PPI Completeness (0.0 - 1.0)

**Criteria**:
- **PPI Table Present**: Investment plan table detected
  
- **Budget Breakdown**:
  - Total cost per program
  - Annual breakdown (2024-2027)
  - Funding sources (SGP, SGR, Propios, Otras)
  
- **Budget Coherence**:
  - Annual budgets sum to total
  - Source budgets sum to total
  - No negative values
  
- **Realistic Costs**: Costs are in reasonable ranges for program type

**Scoring**:
```
P_presence = 1.0 if table_found else 0.0
P_breakdown = rows_with_breakdown / total_rows
P_coherence = coherent_rows / total_rows
P_realism = realistic_rows / total_rows
P = 0.4 × P_presence + 0.25 × P_breakdown + 0.20 × P_coherence + 0.15 × P_realism
```

**Example**:
```python
# Complete PPI matrix
P = 0.4 × 1.0 + 0.25 × 0.95 + 0.20 × 0.98 + 0.15 × 0.92 = 0.971
```

### Final @u Score

```
@u = 0.30 × S + 0.25 × M + 0.25 × I + 0.20 × P
```

Weighting reflects the relative importance of each component. Structure (S) is weighted highest as it enables all other analyses.

### Thresholds

- **@u ≥ 0.7**: HIGH - PDT is well-structured and complete
- **0.5 ≤ @u < 0.7**: MEDIUM - PDT has structural gaps
- **@u < 0.5**: LOW - PDT quality compromises analysis reliability

---

## Layer 3: @q - Question Appropriateness

**Symbol**: `@q`  
**Focus**: Semantic fit between method and question  
**Weight Range**: 0.06 - 0.10

### Purpose

Evaluates how well an analytical method matches the intent of the policy question. A method can be technically excellent (@b) but inappropriate for the question (@q).

### Evaluation Criteria

#### 1. Semantic Alignment (0.0 - 1.0)

**Method**: Sentence-transformer embeddings + cosine similarity

```python
# Compute embeddings
question_emb = embed(question_text)
method_capability_emb = embed(method_description)

# Cosine similarity
semantic_score = cosine_similarity(question_emb, method_capability_emb)
```

**Thresholds**:
- **≥0.75**: HIGH alignment (method directly addresses question)
- **0.50-0.75**: MEDIUM alignment (method partially relevant)
- **<0.50**: LOW alignment (method may not answer question)

**Example**:
```python
# D6_Q5: "¿El plan incluye una teoría de cambio?"
# Method: Bayesian causal inference (Falleti & Lynch framework)
semantic_score = 0.89  # High - method explicitly evaluates causal mechanisms
```

#### 2. Priority Mapping (0.0 - 1.0)

Questions have priority levels based on policy importance:

- **Priority 1**: Critical questions (mandatory by regulation)
- **Priority 2**: Important questions (best practice)
- **Priority 3**: Supplementary questions (nice-to-have)

Methods are assigned to questions based on priority matching:

```python
priority_score = {
    (1, 1): 1.0,   # P1 question, P1 method: perfect match
    (1, 2): 0.7,   # P1 question, P2 method: acceptable
    (1, 3): 0.4,   # P1 question, P3 method: poor match
    (2, 1): 0.9,   # P2 question, P1 method: over-qualified
    (2, 2): 1.0,   # P2 question, P2 method: perfect match
    (2, 3): 0.6,   # P2 question, P3 method: acceptable
    (3, 1): 0.8,   # P3 question, P1 method: over-qualified
    (3, 2): 0.9,   # P3 question, P2 method: over-qualified
    (3, 3): 1.0,   # P3 question, P3 method: perfect match
}[(question_priority, method_priority)]
```

### Final @q Score

```
@q = 0.6 × semantic_alignment + 0.4 × priority_mapping
```

### Thresholds

- **@q ≥ 0.7**: Method is appropriate for question
- **0.5 ≤ @q < 0.7**: Method is partially appropriate
- **@q < 0.5**: Method is inappropriate (consider fallback)

---

## Layer 4: @d - Dimension Alignment

**Symbol**: `@d`  
**Focus**: Method compatibility with policy dimension (D1-D6)  
**Weight Range**: 0.05 - 0.08

### Purpose

Evaluates whether a method is suitable for the policy dimension being analyzed. Different dimensions require different analytical approaches.

### Dimension Profiles

#### D1: INSUMOS (Inputs - Diagnosis & Resources)

**Focus**: Baseline data, resource availability, needs assessment

**Method Requirements**:
- Quantitative data analysis (descriptive statistics)
- Gap analysis (comparing current vs. required)
- Data quality assessment
- Source traceability

**High-scoring methods**:
- Statistical profiling
- Baseline extraction
- DANE data validation

**Example**: `D1_Q1_DiagnosticQuality` → @d = 0.95

#### D2: ACTIVIDADES (Activities - Intervention Design)

**Focus**: Program design, activity planning, resource allocation

**Method Requirements**:
- Logical framework analysis
- Feasibility assessment
- Resource mapping
- Activity sequencing

**High-scoring methods**:
- Theory of Action extraction
- Intervention design analysis
- Stakeholder mapping

**Example**: `D2_Q3_ActivityDesign` → @d = 0.91

#### D3: PRODUCTOS (Outputs - Products & Deliverables)

**Focus**: Concrete outputs, deliverables, short-term results

**Method Requirements**:
- Output quantification
- Deliverable tracking
- Timeline validation
- Responsibility assignment

**High-scoring methods**:
- Output matrix analysis
- Deliverable extraction
- Timeline coherence checks

**Example**: `D3_Q2_OutputSpecificity` → @d = 0.88

#### D4: RESULTADOS (Outcomes - Medium-term Results)

**Focus**: Behavioral change, service improvement, outcome achievement

**Method Requirements**:
- Outcome logic validation
- Indicator-outcome alignment
- Attribution analysis
- Contribution tracing

**High-scoring methods**:
- Outcome mapping
- Indicator quality assessment
- Logic model validation

**Example**: `D4_Q4_OutcomeRealism` → @d = 0.86

#### D5: IMPACTOS (Impacts - Long-term Effects)

**Focus**: Structural change, systemic effects, sustainability

**Method Requirements**:
- Impact pathway analysis
- Long-term projection
- Sustainability assessment
- Spillover detection

**High-scoring methods**:
- Impact evaluation frameworks
- Sustainability scoring
- Structural change detection

**Example**: `D5_Q3_ImpactProjection` → @d = 0.84

#### D6: CAUSALIDAD (Causality - Theory of Change)

**Focus**: Causal mechanisms, intervention logic, assumptions

**Method Requirements**:
- Causal inference methods
- Mechanism tracing (process tracing)
- Assumption testing
- Counterfactual reasoning

**High-scoring methods**:
- Bayesian causal inference
- Process tracing (Derek Beach)
- Mechanistic analysis

**Example**: `D6_Q5_TheoryOfChange` → @d = 0.97

### Scoring Formula

```
@d = capability_match × contextual_fit
```

Where:
- **capability_match**: Does the method have the required capabilities for this dimension? (0.0-1.0)
- **contextual_fit**: Is the method's output format appropriate for dimension aggregation? (0.0-1.0)

### Thresholds

- **@d ≥ 0.8**: Method is well-suited for dimension
- **0.6 ≤ @d < 0.8**: Method is acceptable for dimension
- **@d < 0.6**: Method may not be appropriate for dimension

---

## Layer 5: @p - Policy Area Fit

**Symbol**: `@p`  
**Focus**: Method relevance to policy area (PA01-PA10)  
**Weight Range**: 0.04 - 0.07

### Purpose

Evaluates whether a method can appropriately analyze the specific policy area. Different policy areas have different evidentiary requirements and domain knowledge needs.

### Policy Area Profiles

#### PA01: Gender Equality & Women's Rights

**Domain Requirements**:
- Gender-sensitive indicators
- Intersectionality awareness
- Violence prevention frameworks
- Women's empowerment metrics

**High-scoring methods**:
- Gender mainstreaming analysis
- Violence prevention assessment
- Empowerment indicator validation

#### PA02: Violence Prevention & Conflict

**Domain Requirements**:
- Conflict analysis frameworks
- Security metrics
- Victim protection strategies
- Illegal economy understanding

**High-scoring methods**:
- Conflict sensitivity analysis
- Security indicator assessment
- Protection mechanism evaluation

#### PA03: Environment & Climate

**Domain Requirements**:
- Environmental impact assessment
- Climate adaptation frameworks
- Disaster risk reduction
- Ecosystem services valuation

**High-scoring methods**:
- Environmental indicator validation
- Climate resilience assessment
- Risk reduction analysis

#### PA04: Economic, Social & Cultural Rights

**Domain Requirements**:
- Rights-based approach
- Multidimensional poverty analysis
- Social protection frameworks
- Cultural rights assessment

**High-scoring methods**:
- Rights indicator validation
- Poverty analysis
- Social protection evaluation

#### PA05: Victims' Rights & Peacebuilding

**Domain Requirements**:
- Transitional justice frameworks
- Victim reparation analysis
- Peacebuilding indicators
- Reconciliation metrics

**High-scoring methods**:
- Victim indicator assessment
- Reparation analysis
- Peacebuilding evaluation

#### PA06: Children, Youth & Protective Environments

**Domain Requirements**:
- Child protection frameworks
- Youth development indicators
- Family strengthening approaches
- Educational opportunity assessment

**High-scoring methods**:
- Protection indicator validation
- Youth development analysis
- Environment safety assessment

#### PA07: Land & Territory

**Domain Requirements**:
- Land tenure analysis
- Territorial planning frameworks
- Rural development indicators
- Indigenous rights assessment

**High-scoring methods**:
- Land indicator validation
- Territorial coherence analysis
- Rural development assessment

#### PA08: Human Rights Defenders

**Domain Requirements**:
- Protection mechanism assessment
- Risk analysis frameworks
- Defense network evaluation
- Security measure validation

**High-scoring methods**:
- Protection assessment
- Risk analysis
- Security measure validation

#### PA09: Prison Rights Crisis

**Domain Requirements**:
- Penitentiary system analysis
- Prisoner rights frameworks
- Reintegration indicators
- Judicial system assessment

**High-scoring methods**:
- Prison indicator validation
- Rights assessment
- Reintegration analysis

#### PA10: Cross-border Migration

**Domain Requirements**:
- Migration flow analysis
- Integration frameworks
- Humanitarian response assessment
- Cross-border coordination evaluation

**High-scoring methods**:
- Migration indicator validation
- Integration assessment
- Response analysis

### Scoring Formula

```
@p = domain_coverage × evidence_adequacy × method_specificity
```

Where:
- **domain_coverage**: Does method cover key concepts for this policy area? (0.0-1.0)
- **evidence_adequacy**: Can method extract relevant evidence for this area? (0.0-1.0)
- **method_specificity**: Is method calibrated for this policy domain? (0.0-1.0)

### Thresholds

- **@p ≥ 0.7**: Method is well-suited for policy area
- **0.5 ≤ @p < 0.7**: Method is generally applicable
- **@p < 0.5**: Method may lack domain specificity

---

## Layer 6: @C - Contract Compliance

**Symbol**: `@C`  
**Focus**: Formal correctness of input/output contracts  
**Weight Range**: 0.07 - 0.10

### Purpose

Evaluates whether a method correctly implements its formal contracts (type specifications, data schemas, validation rules). Contract compliance ensures interoperability and prevents runtime errors.

### Components

#### 1. c_scale: Scalar Conformance (0.0 - 1.0)

**Criteria**:
- All numeric outputs are in expected ranges (0.0-1.0 for scores)
- No NaN or Inf values
- No negative values where prohibited
- Precision requirements met (e.g., 4 decimal places)

**Scoring**:
```
c_scale = outputs_in_range / total_outputs
```

**Example**:
```python
# Method produces 15 outputs, all in [0.0, 1.0]
c_scale = 15 / 15 = 1.0
```

#### 2. c_sem: Semantic Conformance (0.0 - 1.0)

**Criteria**:
- Output types match declared types (str, int, float, list, dict)
- Enum values are from allowed sets
- String formats are correct (ISO dates, URLs, etc.)
- Nested structures match schema

**Scoring**:
```
c_sem = fields_matching_schema / total_fields
```

**Example**:
```python
# TypedDict with 12 fields, all types correct
c_sem = 12 / 12 = 1.0
```

#### 3. c_fusion: Aggregation Readiness (0.0 - 1.0)

**Criteria**:
- Outputs can be aggregated (numeric scores)
- Missing values are handled consistently (explicit None vs. 0.0)
- Provenance fields are populated (source tracking)
- Metadata is complete (confidence, uncertainty, etc.)

**Scoring**:
```
c_fusion = aggregable_outputs / total_outputs
```

**Example**:
```python
# 10 scores, all with confidence intervals and provenance
c_fusion = 10 / 10 = 1.0
```

### Final @C Score

```
@C = 0.4 × c_scale + 0.35 × c_sem + 0.25 × c_fusion
```

Weighting prioritizes scalar correctness (most common source of aggregation errors).

### Thresholds

- **@C ≥ 0.9**: Excellent contract compliance
- **0.7 ≤ @C < 0.9**: Good compliance with minor issues
- **@C < 0.7**: Poor compliance (hard gate: execution fails)

---

## Layer 7: @chain - Data Flow Integrity

**Symbol**: `@chain`  
**Focus**: Correct data flow through pipeline  
**Weight Range**: 0.10 - 0.15

### Purpose

Evaluates whether data flows correctly through the pipeline, with proper dependency resolution and no information loss. Chain integrity ensures that downstream methods receive valid inputs.

### Evaluation Criteria

#### 1. Discrete Scoring (Binary)

Chain integrity is evaluated as a binary property:

```python
@chain = 1.0 if all_checks_pass else 0.0
```

**Checks**:

1. **Dependency Resolution**: All required inputs are available
   ```python
   required_inputs = {"preprocessed_doc", "sisas_signals", "executor_config"}
   available_inputs = set(context.keys())
   dependency_check = required_inputs.issubset(available_inputs)
   ```

2. **Schema Validation**: Inputs match expected schemas
   ```python
   schema_check = validate_schema(input_data, expected_schema)
   ```

3. **Provenance Chain**: Evidence traces back to source
   ```python
   provenance_check = all(evidence.has_source() for evidence in results)
   ```

4. **No Information Loss**: Critical fields are preserved
   ```python
   loss_check = all(field in output for field in critical_fields)
   ```

5. **Temporal Ordering**: Dependencies respect execution order
   ```python
   ordering_check = all(dep.timestamp < output.timestamp for dep in dependencies)
   ```

#### 2. Chain Validation Process

```python
def validate_chain(method_id: str, inputs: dict, outputs: dict) -> bool:
    checks = [
        validate_dependencies(method_id, inputs),
        validate_input_schemas(inputs),
        validate_output_schemas(outputs),
        validate_provenance_chain(outputs),
        validate_information_preservation(inputs, outputs),
        validate_temporal_ordering(inputs, outputs),
    ]
    return all(checks)

@chain = 1.0 if validate_chain(...) else 0.0
```

### Thresholds

- **@chain = 1.0**: Chain is intact (PASS)
- **@chain = 0.0**: Chain is broken (FAIL - execution aborts)

**No partial credit**: Chain integrity is all-or-nothing. A broken chain compromises all downstream analyses.

---

## Layer 8: @m - Governance Maturity

**Symbol**: `@m`  
**Focus**: Institutional quality and governance capacity  
**Weight Range**: 0.03 - 0.05

### Purpose

Evaluates the institutional and governance quality reflected in the PDT. A plan from a mature governance system is more likely to be implemented successfully.

### Components

#### 1. m_transp: Transparency (0.0 - 1.0)

**Criteria**:
- **Data Sources Cited**: All quantitative claims have sources
  - DANE, Medicina Legal, Defensoría, etc.
  - Minimum: 5 distinct sources
  
- **Methodologies Described**: How data was collected/analyzed
  
- **Assumptions Made Explicit**: Underlying assumptions stated
  
- **Public Participation Documented**: Citizen engagement process described

**Scoring**:
```
m_transp = 0.4 × (sources_cited / 5) + 0.3 × (methodologies / 3) + 
           0.2 × (assumptions / 5) + 0.1 × (participation ? 1.0 : 0.0)
```

**Example**:
```python
# High transparency PDT
m_transp = 0.4 × (7/5) + 0.3 × (3/3) + 0.2 × (6/5) + 0.1 × 1.0 = 0.850
# Note: caps at 1.0 after normalization
```

#### 2. m_gov: Governance Structure (0.0 - 1.0)

**Criteria**:
- **Institutional Roles Clear**: Responsibilities assigned to specific entities
  
- **Coordination Mechanisms**: Inter-institutional coordination described
  
- **Monitoring Framework**: How implementation will be tracked
  
- **Evaluation Plan**: How success will be assessed

**Scoring**:
```
m_gov = 0.35 × roles_clarity + 0.30 × coordination_described + 
        0.20 × monitoring_framework + 0.15 × evaluation_plan
```

**Example**:
```python
# Medium governance PDT
m_gov = 0.35 × 0.82 + 0.30 × 0.75 + 0.20 × 0.68 + 0.15 × 0.50 = 0.728
```

#### 3. m_cost: Cost Realism (0.0 - 1.0)

**Criteria**:
- **Budgets Are Detailed**: Cost breakdowns provided
  
- **Budgets Are Realistic**: Costs align with market rates
  
- **Funding Sources Identified**: SGP, SGR, Propios, Otras specified
  
- **Contingency Planning**: Cost overrun strategies described

**Scoring**:
```
m_cost = 0.35 × budget_detail + 0.35 × budget_realism + 
         0.20 × funding_sources + 0.10 × contingency
```

**Example**:
```python
# Good cost realism
m_cost = 0.35 × 0.88 + 0.35 × 0.82 + 0.20 × 0.95 + 0.10 × 0.75 = 0.860
```

### Final @m Score

```
@m = 0.40 × m_transp + 0.35 × m_gov + 0.25 × m_cost
```

Weighting prioritizes transparency and governance structure over cost realism.

### Thresholds

- **@m ≥ 0.7**: High governance maturity
- **0.5 ≤ @m < 0.7**: Medium governance maturity
- **@m < 0.5**: Low governance maturity (institutional weaknesses)

---

## Layer Fusion

### Why Choquet Integral?

Standard weighted averages assume **independence** between quality dimensions:

```
score_simple = w1×x1 + w2×x2 + ... + w8×x8
```

But quality layers interact:
- High @b + High @u: Method can leverage rich document structure (synergy)
- Low @chain + High @q: Good question fit doesn't matter if data flow is broken (veto)

The **Choquet integral** captures these interactions through interaction terms.

### Formula

```
Cal(I) = Σ aₗ·xₗ + Σ aₗₖ·min(xₗ, xₖ)
         l∈L      (l,k)∈I
```

Where:
- `L` = Set of layers {@b, @u, @q, @d, @p, @C, @chain, @m}
- `I` = Set of interaction pairs (e.g., {@u, @chain}, {@q, @d}, {@chain, @C})
- `aₗ` = Linear weight for layer l
- `aₗₖ` = Interaction weight for pair (l, k)
- `xₗ` = Score for layer l (0.0-1.0)

### Calibrated Weights (Executor Role)

```python
# Linear weights
CHOQUET_WEIGHTS = {
    "@b": 0.17,      # Highest - intrinsic quality is foundation
    "@chain": 0.13,  # High - data flow integrity is critical
    "@q": 0.08,      # Medium - question fit matters
    "@d": 0.07,      # Medium - dimension alignment
    "@p": 0.06,      # Medium-low - policy area fit
    "@C": 0.08,      # Medium - contract compliance
    "@u": 0.04,      # Low - unit quality (context-dependent)
    "@m": 0.04,      # Low - governance (external factor)
}

# Interaction weights
CHOQUET_INTERACTION_WEIGHTS = {
    ("@u", "@chain"): 0.13,    # Strong synergy: good document + intact chain
    ("@chain", "@C"): 0.10,    # Synergy: valid chain + compliant contracts
    ("@q", "@d"): 0.10,        # Synergy: question fit + dimension alignment
}

# Verification
sum_linear = sum(CHOQUET_WEIGHTS.values()) = 0.67
sum_interaction = sum(CHOQUET_INTERACTION_WEIGHTS.values()) = 0.33
total = 0.67 + 0.33 = 1.00 ✓
```

### Example Calculation

```python
# Executor: D6_Q5_TheoryOfChange
layers = {
    "@b": 0.88,
    "@u": 0.76,
    "@q": 0.91,
    "@d": 0.95,
    "@p": 0.83,
    "@C": 0.94,
    "@chain": 1.0,
    "@m": 0.72,
}

# Linear component
linear = (
    0.17 × 0.88 +  # @b
    0.13 × 1.0 +   # @chain
    0.08 × 0.91 +  # @q
    0.07 × 0.95 +  # @d
    0.06 × 0.83 +  # @p
    0.08 × 0.94 +  # @C
    0.04 × 0.76 +  # @u
    0.04 × 0.72    # @m
) = 0.590

# Interaction component
interaction = (
    0.13 × min(0.76, 1.0) +   # @u × @chain = 0.13 × 0.76 = 0.099
    0.10 × min(1.0, 0.94) +   # @chain × @C = 0.10 × 0.94 = 0.094
    0.10 × min(0.91, 0.95)    # @q × @d = 0.10 × 0.91 = 0.091
) = 0.284

# Final Choquet score
Cal(I) = 0.590 + 0.284 = 0.874
```

**Interpretation**: This executor achieves 87.4% overall quality, with strong performance across all layers and positive synergies (especially @chain × @C).

See [FUSION_FORMULA.md](./FUSION_FORMULA.md) for detailed mathematical treatment.

---

## Priority Mappings

### Question Priority Levels

Questions are assigned priority based on regulatory requirements and policy importance:

```python
QUESTION_PRIORITIES = {
    # D1: INSUMOS (Diagnosis)
    "D1_Q1": 1,  # Baseline data (MANDATORY by Law 152/1994)
    "D1_Q2": 1,  # Quantitative indicators (MANDATORY)
    "D1_Q3": 2,  # Data sources (BEST PRACTICE)
    "D1_Q4": 2,  # Gap analysis (BEST PRACTICE)
    "D1_Q5": 3,  # Trend analysis (SUPPLEMENTARY)
    
    # D2: ACTIVIDADES (Activities)
    "D2_Q1": 1,  # Program description (MANDATORY)
    "D2_Q2": 1,  # Activity alignment (MANDATORY)
    "D2_Q3": 2,  # Intervention logic (BEST PRACTICE)
    "D2_Q4": 2,  # Stakeholder engagement (BEST PRACTICE)
    "D2_Q5": 3,  # Innovation (SUPPLEMENTARY)
    
    # D3: PRODUCTOS (Outputs)
    "D3_Q1": 1,  # Output definition (MANDATORY)
    "D3_Q2": 1,  # Output quantification (MANDATORY)
    "D3_Q3": 2,  # Timeline coherence (BEST PRACTICE)
    "D3_Q4": 2,  # Responsibility assignment (BEST PRACTICE)
    "D3_Q5": 3,  # Quality control (SUPPLEMENTARY)
    
    # D4: RESULTADOS (Outcomes)
    "D4_Q1": 1,  # Outcome indicators (MANDATORY by Decree 1082/2015)
    "D4_Q2": 1,  # Targets (MANDATORY)
    "D4_Q3": 2,  # Outcome logic (BEST PRACTICE)
    "D4_Q4": 2,  # Attribution (BEST PRACTICE)
    "D4_Q5": 3,  # Contribution analysis (SUPPLEMENTARY)
    
    # D5: IMPACTOS (Impacts)
    "D5_Q1": 2,  # Impact pathway (BEST PRACTICE)
    "D5_Q2": 2,  # Long-term targets (BEST PRACTICE)
    "D5_Q3": 2,  # Sustainability (BEST PRACTICE)
    "D5_Q4": 3,  # Spillover effects (SUPPLEMENTARY)
    "D5_Q5": 3,  # Structural change (SUPPLEMENTARY)
    
    # D6: CAUSALIDAD (Theory of Change)
    "D6_Q1": 2,  # Causal assumptions (BEST PRACTICE)
    "D6_Q2": 2,  # Mechanism description (BEST PRACTICE)
    "D6_Q3": 2,  # Assumption testing (BEST PRACTICE)
    "D6_Q4": 3,  # Alternative pathways (SUPPLEMENTARY)
    "D6_Q5": 3,  # Theory of Change (SUPPLEMENTARY but highly valued)
}
```

### Method-Question Matching

Methods are matched to questions using semantic alignment (@q) adjusted by priority:

```python
def compute_question_appropriateness(
    question_id: str,
    method_id: str,
    semantic_score: float,
    question_priority: int,
    method_priority: int,
) -> float:
    # Priority adjustment matrix
    priority_matrix = {
        (1, 1): 1.0,  # Perfect match
        (1, 2): 0.7,  # Under-qualified
        (1, 3): 0.4,  # Significantly under-qualified
        (2, 1): 0.9,  # Over-qualified (acceptable)
        (2, 2): 1.0,  # Perfect match
        (2, 3): 0.6,  # Under-qualified
        (3, 1): 0.8,  # Over-qualified (good)
        (3, 2): 0.9,  # Over-qualified (acceptable)
        (3, 3): 1.0,  # Perfect match
    }
    
    priority_adjustment = priority_matrix[(question_priority, method_priority)]
    
    # Final score
    @q = 0.6 × semantic_score + 0.4 × priority_adjustment
    
    return @q
```

**Example**:
```python
# D6_Q5 (Priority 3) matched to Theory of Change method (Priority 1)
semantic_score = 0.89
priority_adjustment = 0.8  # Over-qualified (good)
@q = 0.6 × 0.89 + 0.4 × 0.8 = 0.854
```

---

## Related Documentation

- [FUSION_FORMULA.md](./FUSION_FORMULA.md) - Mathematical details of Choquet integral
- [WEIGHT_TUNING.md](./WEIGHT_TUNING.md) - How to adjust fusion weights
- [THRESHOLD_GUIDE.md](./THRESHOLD_GUIDE.md) - Quality thresholds and hard gates
- [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md) - Configuration schemas

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit
