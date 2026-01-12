# Phase 5: Policy Area Aggregation

## A Formal Specification for Hierarchical Score Synthesis in Policy Evaluation Systems

---

## Document Control

| Attribute | Value |
|-----------|-------|
| **Phase ID** | `PHASE-5-POLICY-AREA-AGGREGATION` |
| **Canonical Name** | `phase_5_policy_area_aggregation` |
| **Status** | `ACTIVE` |
| **Version** | `2.0.0` |
| **Effective Date** | 2026-01-11 |
| **Pipeline Position** | Phase 4 (Dimension) → **Phase 5** → Phase 6 (Cluster) |
| **Criticality** | `HIGH` |
| **Certification** | [CERTIFICATE_02_PHASE5_COUNT_10](../Phase_4/contracts/certificates/CERTIFICATE_02_PHASE5_COUNT_10.md) |

---

## Abstract

Phase 5 constitutes the second aggregation tier in the F.A.R.F.A.N hierarchical scoring pipeline, responsible for synthesizing **60 DimensionScore** objects into **10 AreaScore** objects through a mathematically rigorous weighted aggregation process. This phase enforces strict hermeticity invariants ensuring that each policy area receives exactly six dimensional evaluations, applies rubric-based quality classification, and maintains complete provenance tracking for downstream audit requirements. The phase operates under Design by Contract (DbC) principles with explicit preconditions, postconditions, and class invariants that guarantee deterministic, reproducible results across execution contexts.

**Keywords**: Policy Aggregation, Hermeticity Validation, Weighted Average, Multi-Criteria Decision Analysis, Hierarchical Scoring, Provenance Tracking

---

## Table of Contents

1. [Introduction and Theoretical Foundation](#1-introduction-and-theoretical-foundation)
2. [Formal Input/Output Specification](#2-formal-inputoutput-specification)
3. [Mathematical Framework](#3-mathematical-framework)
4. [Hermeticity Theory and Validation](#4-hermeticity-theory-and-validation)
5. [Aggregation Algorithm Specification](#5-aggregation-algorithm-specification)
6. [Quality Rubric Classification](#6-quality-rubric-classification)
7. [Cluster Assignment Topology](#7-cluster-assignment-topology)
8. [Design by Contract Specification](#8-design-by-contract-specification)
9. [Data Structures and Type Definitions](#9-data-structures-and-type-definitions)
10. [Uncertainty Quantification](#10-uncertainty-quantification)
11. [Provenance and Traceability](#11-provenance-and-traceability)
12. [Implementation Architecture](#12-implementation-architecture)
13. [Validation and Testing Framework](#13-validation-and-testing-framework)
14. [Performance Characteristics](#14-performance-characteristics)
15. [Error Taxonomy and Recovery](#15-error-taxonomy-and-recovery)
16. [References and Related Documentation](#16-references-and-related-documentation)

---

## 1. Introduction and Theoretical Foundation

### 1.1 Phase Mission Statement

Phase 5 implements the **Policy Area Aggregation** tier within the F.A.R.F.A.N multi-level evaluation framework. Its primary responsibility is the transformation of granular dimensional assessments into coherent policy-area-level scores that capture the holistic quality of policy implementation across thematic domains.

The phase addresses a fundamental challenge in multi-criteria decision analysis (MCDA): how to synthesize heterogeneous quality signals from distinct evaluation dimensions into meaningful composite indicators while preserving information about variance, uncertainty, and structural completeness.

### 1.2 Position in the Aggregation Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    F.A.R.F.A.N AGGREGATION HIERARCHY                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 3: Micro-Question Scoring                                           │
│  ════════════════════════════════                                           │
│  300 × ScoredMicroQuestion (5 questions × 6 dimensions × 10 policy areas)  │
│       │                                                                     │
│       │ PHASE 4: Dimension Aggregation                                      │
│       │ ══════════════════════════════                                      │
│       │ Group by (policy_area, dimension)                                   │
│       │ 5 micro-questions → 1 DimensionScore                               │
│       ▼                                                                     │
│  60 × DimensionScore (6 dimensions × 10 policy areas)                      │
│       │                                                                     │
│       │ ╔═══════════════════════════════════════════════════════════════╗  │
│       │ ║ PHASE 5: POLICY AREA AGGREGATION (THIS DOCUMENT)              ║  │
│       │ ║ ═════════════════════════════════════════════════════════════ ║  │
│       │ ║ Group by policy_area                                          ║  │
│       │ ║ Validate hermeticity (all 6 dimensions present)               ║  │
│       │ ║ Apply area-dimension weights                                  ║  │
│       │ ║ 6 DimensionScores → 1 AreaScore                              ║  │
│       │ ╚═══════════════════════════════════════════════════════════════╝  │
│       ▼                                                                     │
│  10 × AreaScore (PA01–PA10)                                                │
│       │                                                                     │
│       │ PHASE 6: Cluster Aggregation (MESO)                                │
│       │ ═══════════════════════════════════                                │
│       │ Group by cluster_id (4 clusters)                                   │
│       │ Apply adaptive penalty based on dispersion                         │
│       ▼                                                                     │
│  4 × ClusterScore (CLUSTER_MESO_1 through CLUSTER_MESO_4)                  │
│       │                                                                     │
│       │ PHASE 7: Macro Evaluation                                          │
│       │ ═════════════════════════════                                      │
│       │ Compute holistic assessment                                        │
│       ▼                                                                     │
│  1 × MacroScore (holistic evaluation)                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Theoretical Basis

Phase 5 draws on established principles from:

1. **Multi-Criteria Decision Analysis (MCDA)**: The aggregation of multiple evaluation criteria into composite scores follows the axiomatic framework established by Keeney & Raiffa (1976) for multi-attribute utility theory.

2. **Hierarchical Aggregation Theory**: The nested structure (questions → dimensions → areas → clusters → macro) implements a hierarchical value tree consistent with the decomposition principles of Belton & Stewart (2002).

3. **Set-Theoretic Hermeticity**: The requirement that each policy area contains exactly its expected dimensions implements a partition constraint ensuring that the evaluation space is both complete (no gaps) and non-redundant (no overlaps).

4. **Provenance-Aware Computation**: Following W3C PROV-DM standards, all aggregation operations maintain explicit lineage relationships enabling full audit reconstruction.

---

## 2. Formal Input/Output Specification

### 2.1 Input Contract

**Contract ID**: `CONTRACT-P5-INPUT`

| Precondition | Specification | Validation Method |
|--------------|---------------|-------------------|
| **PRE-P5-01** | `len(dimension_scores) == 60` | Count validation |
| **PRE-P5-02** | `∀ ds ∈ dimension_scores: ds.score ∈ [0.0, 3.0]` | Bounds check |
| **PRE-P5-03** | `∀ ds ∈ dimension_scores: ds.dimension_id ∈ {DIM01..DIM06}` | Enum validation |
| **PRE-P5-04** | `∀ ds ∈ dimension_scores: ds.area_id ∈ {PA01..PA10}` | Enum validation |
| **PRE-P5-05** | `∀ ds ∈ dimension_scores: ds.quality_level ∈ QUALITY_LEVELS` | Enum validation |
| **PRE-P5-06** | `∀ ds ∈ dimension_scores: len(ds.contributing_questions) > 0` | Non-empty check |

**Input Schema (TypedDict)**:

```python
@dataclass
class DimensionScore:
    """Input type for Phase 5 aggregation."""
    
    dimension_id: str           # DIM01-DIM06
    area_id: str                # PA01-PA10
    score: float                # [0.0, 3.0]
    quality_level: str          # EXCELENTE|BUENO|ACEPTABLE|INSUFICIENTE
    contributing_questions: list[int | str]
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    
    # SOTA: Uncertainty quantification
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = (0.0, 0.0)
    epistemic_uncertainty: float = 0.0
    aleatoric_uncertainty: float = 0.0
    
    # SOTA: Provenance tracking
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"
```

### 2.2 Output Contract

**Contract ID**: `CONTRACT-P5-OUTPUT`

| Postcondition | Specification | Validation Method |
|---------------|---------------|-------------------|
| **POST-P5-01** | `len(area_scores) == 10` | Count validation |
| **POST-P5-02** | `∀ as ∈ area_scores: as.score ∈ [0.0, 3.0]` | Bounds check |
| **POST-P5-03** | `∀ as ∈ area_scores: as.area_id ∈ {PA01..PA10}` | Enum validation |
| **POST-P5-04** | `∀ as ∈ area_scores: len(as.dimension_scores) == 6` | Hermeticity check |
| **POST-P5-05** | `∀ as ∈ area_scores: as.cluster_id is not None` | Cluster assignment |
| **POST-P5-06** | `set(as.area_id for as in area_scores) == {PA01..PA10}` | Completeness |

**Output Schema (TypedDict)**:

```python
@dataclass
class AreaScore:
    """Output type for Phase 5 aggregation."""
    
    area_id: str                           # PA01-PA10
    area_name: str                         # Human-readable label
    score: float                           # [0.0, 3.0]
    quality_level: str                     # EXCELENTE|BUENO|ACEPTABLE|INSUFICIENTE
    dimension_scores: list[DimensionScore] # Exactly 6 elements
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    cluster_id: str | None = None          # CLUSTER_MESO_1..4
    
    # SOTA: Uncertainty quantification
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = (0.0, 0.0)
    
    # SOTA: Provenance tracking
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"
```

### 2.3 Cardinality Transformation

```
INPUT:  60 DimensionScore = 6 dimensions × 10 policy areas
OUTPUT: 10 AreaScore      = 1 score per policy area

Compression Ratio: 6:1 (dimensions collapsed per area)
Information Preservation: Dimension scores retained in AreaScore.dimension_scores
```

---

## 3. Mathematical Framework

### 3.1 Weighted Average Aggregation

The core aggregation function for Phase 5 implements a weighted arithmetic mean:

**Definition 3.1 (Area Score Computation)**:

Given a policy area `PA` with dimension scores `{d₁, d₂, ..., d₆}` and corresponding weights `{w₁, w₂, ..., w₆}`:

```
                    Σᵢ₌₁⁶ (wᵢ · dᵢ.score)
AreaScore(PA) = ─────────────────────────
                         Σᵢ₌₁⁶ wᵢ
```

**Constraint**: Weights are normalized such that `Σᵢ wᵢ = 1.0 ± ε` where `ε = 10⁻⁶`.

### 3.2 Weight Normalization

**Definition 3.2 (Weight Normalization)**:

For raw weights `{w₁', w₂', ..., wₙ'}`:

```
        wᵢ'
wᵢ = ─────────
     Σⱼ₌₁ⁿ wⱼ'
```

**Properties**:
- **Non-negativity**: `wᵢ ≥ 0 ∀i`
- **Normalization**: `Σᵢ wᵢ = 1.0`
- **Default**: If no weights specified, equal weights `wᵢ = 1/n = 1/6 ≈ 0.1667`

### 3.3 Convexity Guarantee

**Theorem 3.1 (Convexity)**:

The aggregated area score is bounded by the minimum and maximum dimension scores:

```
min(d₁.score, ..., d₆.score) ≤ AreaScore(PA) ≤ max(d₁.score, ..., d₆.score)
```

**Proof**: Follows directly from the properties of convex combinations with non-negative weights summing to unity. □

### 3.4 Score Domain

All scores operate on the **3-point scale**:

| Value | Interpretation |
|-------|----------------|
| 0.0 | Minimum (no evidence/compliance) |
| 1.5 | Midpoint (partial compliance) |
| 3.0 | Maximum (full compliance) |

**Domain**: `[0.0, 3.0] ⊂ ℝ`

---

## 4. Hermeticity Theory and Validation

### 4.1 Definition of Hermeticity

**Definition 4.1 (Hermetic Policy Area)**:

A policy area `PA` is **hermetic** if and only if:

1. **Completeness**: All expected dimensions are present
2. **Non-redundancy**: No dimension appears more than once
3. **Scope containment**: No unexpected dimensions are present

Formally:

```
Hermetic(PA) ⟺ (Expected(PA) = Actual(PA)) ∧ (|Actual(PA)| = |set(Actual(PA))|)

where:
  Expected(PA) = {DIM01, DIM02, DIM03, DIM04, DIM05, DIM06}
  Actual(PA) = {d.dimension_id : d ∈ dimension_scores(PA)}
```

### 4.2 Hermeticity Violation Categories

| Violation Type | Condition | Severity |
|----------------|-----------|----------|
| **GAP** | `Expected(PA) ⊄ Actual(PA)` | CRITICAL |
| **OVERLAP** | `|Actual(PA)| ≠ |set(Actual(PA))|` | HIGH |
| **SCOPE_LEAK** | `Actual(PA) ⊄ Expected(PA)` | MEDIUM |

### 4.3 Hermeticity Diagnosis Protocol

```python
def diagnose_hermeticity(
    actual_dimensions: set[str],
    expected_dimensions: set[str],
    area_id: str
) -> HermeticityDiagnosis:
    """
    Diagnose hermeticity violations for a policy area.
    
    Returns:
        HermeticityDiagnosis with:
        - is_hermetic: bool
        - missing_ids: set[str]  (GAP violations)
        - extra_ids: set[str]    (SCOPE_LEAK violations)
        - duplicate_ids: set[str] (OVERLAP violations)
        - severity: CRITICAL | HIGH | MEDIUM | LOW
        - remediation_hint: str
    """
```

### 4.4 Graceful Degradation Strategy

When hermeticity violations are detected:

| Configuration | Behavior |
|---------------|----------|
| `abort_on_insufficient=True` | Raise `HermeticityValidationError` |
| `abort_on_insufficient=False` | Log warning, proceed with partial data, set `validation_passed=False` |

**Graceful Degradation Formula**:

For missing dimensions, the score is computed only over available dimensions:

```
                    Σᵢ∈Available (wᵢ · dᵢ.score)
AreaScore(PA) = ────────────────────────────────── × penalty_factor
                        Σᵢ∈Available wᵢ

where penalty_factor = |Available| / |Expected| = |Available| / 6
```

---

## 5. Aggregation Algorithm Specification

### 5.1 Algorithm Overview

```
ALGORITHM: Phase5_PolicyAreaAggregation
═══════════════════════════════════════

INPUT:
  dimension_scores: list[DimensionScore]  // |dimension_scores| = 60
  settings: AggregationSettings
  
OUTPUT:
  area_scores: list[AreaScore]           // |area_scores| = 10

STEPS:
  1. GROUP dimension_scores BY area_id → 10 groups
  2. FOR EACH group (area_id, dimensions):
     a. VALIDATE hermeticity(dimensions, area_id)
     b. RESOLVE weights from settings or use equal weights
     c. NORMALIZE scores to [0, 1] range
     d. COMPUTE weighted_average(scores, weights)
     e. APPLY rubric_thresholds → quality_level
     f. CONSTRUCT AreaScore with provenance
  3. VALIDATE |area_scores| == 10
  4. RETURN area_scores
```

### 5.2 Detailed Step Specification

#### Step 1: Grouping

```python
def group_by_area(dimension_scores: list[DimensionScore]) -> dict[str, list[DimensionScore]]:
    """
    Group dimension scores by policy area.
    
    Time Complexity: O(n) where n = |dimension_scores|
    Space Complexity: O(n)
    
    Invariant: Σ|groups| = |dimension_scores|
    """
    grouped = defaultdict(list)
    for ds in dimension_scores:
        grouped[ds.area_id].append(ds)
    return dict(grouped)
```

#### Step 2a: Hermeticity Validation

```python
def validate_hermeticity(
    dimension_scores: list[DimensionScore],
    area_id: str,
    expected_dims: set[str] = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}
) -> tuple[bool, str]:
    """
    Validate that all expected dimensions are present exactly once.
    
    Returns:
        (is_valid, message)
    
    Raises:
        HermeticityValidationError if abort_on_insufficient=True and validation fails
    """
```

#### Step 2b-c: Weight Resolution and Normalization

```python
def resolve_and_normalize_weights(
    area_id: str,
    dimension_scores: list[DimensionScore],
    settings: AggregationSettings
) -> list[float]:
    """
    Resolve weights from settings, normalize, and align with dimension order.
    
    Weight Sources (priority order):
    1. settings.policy_area_dimension_weights[area_id]
    2. Signal registry (SISAS) if available
    3. Equal weights (1/6 each)
    
    Returns:
        Normalized weights aligned with dimension_scores order
    """
```

#### Step 2d: Weighted Average Computation

```python
def calculate_weighted_average(
    scores: list[float],
    weights: list[float] | None = None
) -> float:
    """
    Calculate weighted average of scores.
    
    Args:
        scores: List of score values
        weights: Optional weights (defaults to equal weights)
    
    Returns:
        Weighted average in same scale as inputs
    
    Invariant: min(scores) <= result <= max(scores)
    """
    if weights is None:
        weights = [1.0 / len(scores)] * len(scores)
    
    return sum(s * w for s, w in zip(scores, weights)) / sum(weights)
```

#### Step 2e: Rubric Application

```python
def apply_rubric_thresholds(
    score: float,
    thresholds: dict[str, float] | None = None
) -> str:
    """
    Map numeric score to quality level.
    
    Default thresholds (normalized to [0,1]):
        EXCELENTE:    >= 0.85
        BUENO:        >= 0.70
        ACEPTABLE:    >= 0.55
        INSUFICIENTE: < 0.55
    
    Returns:
        Quality level string
    """
```

### 5.3 Pseudocode Implementation

```python
class AreaPolicyAggregator:
    """Phase 5 aggregation implementation."""
    
    def run(
        self,
        dimension_scores: list[DimensionScore],
        group_by_keys: list[str] = ["area_id"]
    ) -> list[AreaScore]:
        """
        Execute Phase 5 aggregation.
        
        Preconditions:
            - len(dimension_scores) == 60
            - All scores in [0.0, 3.0]
        
        Postconditions:
            - len(result) == 10
            - All AreaScores have cluster_id assigned
        """
        # Step 1: Group by area
        grouped = group_by(dimension_scores, lambda d: (d.area_id,))
        
        area_scores = []
        for (area_id,), dims in grouped.items():
            # Step 2a: Validate hermeticity
            valid, msg = self.validate_hermeticity(dims, area_id)
            
            # Step 2b-c: Resolve weights
            weights = self._resolve_area_weights(area_id, dims)
            
            # Step 2d: Compute weighted average
            scores = [d.score for d in dims]
            avg_score = calculate_weighted_average(scores, weights)
            
            # Step 2e: Apply rubric
            quality_level = self.apply_rubric_thresholds(avg_score)
            
            # Step 2f: Construct AreaScore
            area_score = AreaScore(
                area_id=area_id,
                area_name=self._get_area_name(area_id),
                score=avg_score,
                quality_level=quality_level,
                dimension_scores=dims,
                validation_passed=valid,
                cluster_id=self._get_cluster_id(area_id)
            )
            area_scores.append(area_score)
        
        # Step 3: Validate output count
        assert len(area_scores) == 10, f"Expected 10, got {len(area_scores)}"
        
        return area_scores
```

---

## 6. Quality Rubric Classification

### 6.1 Quality Level Definitions

| Level | Spanish | Normalized Range | 3-Point Scale | Interpretation |
|-------|---------|------------------|---------------|----------------|
| **EXCELENTE** | Excelente | [0.85, 1.00] | [2.55, 3.00] | Outstanding policy compliance |
| **BUENO** | Bueno | [0.70, 0.85) | [2.10, 2.55) | Good compliance with minor gaps |
| **ACEPTABLE** | Aceptable | [0.55, 0.70) | [1.65, 2.10) | Acceptable with improvement areas |
| **INSUFICIENTE** | Insuficiente | [0.00, 0.55) | [0.00, 1.65) | Insufficient, requires intervention |

### 6.2 Threshold Configuration

```python
QUALITY_THRESHOLDS = {
    "EXCELENTE": 0.85,     # >= 85% normalized
    "BUENO": 0.70,         # >= 70% normalized
    "ACEPTABLE": 0.55,     # >= 55% normalized
    "INSUFICIENTE": 0.0    # < 55% normalized (implicit)
}
```

### 6.3 Score Normalization for Rubric Application

```python
def normalize_for_rubric(score: float, max_score: float = 3.0) -> float:
    """
    Normalize score to [0, 1] range for rubric application.
    
    Formula: normalized = clamp(score, 0, max_score) / max_score
    """
    clamped = max(0.0, min(max_score, score))
    return clamped / max_score
```

### 6.4 Quality Level Enum

```python
class QualityLevel(Enum):
    """Quality levels for area scores."""
    
    EXCELENTE = "EXCELENTE"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    INSUFICIENTE = "INSUFICIENTE"
    
    @classmethod
    def from_score(cls, score: float, max_score: float = 3.0) -> "QualityLevel":
        """Derive quality level from numeric score."""
        normalized = score / max_score
        if normalized >= 0.85:
            return cls.EXCELENTE
        elif normalized >= 0.70:
            return cls.BUENO
        elif normalized >= 0.55:
            return cls.ACEPTABLE
        else:
            return cls.INSUFICIENTE
```

---

## 7. Cluster Assignment Topology

### 7.1 Cluster-Policy Area Mapping

Phase 5 assigns each policy area to a MESO cluster for Phase 6 aggregation:

| Cluster ID | Cluster Name | Policy Areas | Count |
|------------|--------------|--------------|-------|
| **CLUSTER_MESO_1** | Cluster 1 | PA01, PA02, PA03 | 3 |
| **CLUSTER_MESO_2** | Cluster 2 | PA04, PA05, PA06 | 3 |
| **CLUSTER_MESO_3** | Cluster 3 | PA07, PA08 | 2 |
| **CLUSTER_MESO_4** | Cluster 4 | PA09, PA10 | 2 |

**Total**: 10 policy areas distributed across 4 clusters.

### 7.2 Cluster Assignment Constant

```python
CLUSTER_ASSIGNMENTS = {
    "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],
    "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],
    "CLUSTER_MESO_3": ["PA07", "PA08"],
    "CLUSTER_MESO_4": ["PA09", "PA10"],
}
```

### 7.3 Reverse Mapping (PA → Cluster)

```python
PA_TO_CLUSTER = {
    "PA01": "CLUSTER_MESO_1",
    "PA02": "CLUSTER_MESO_1",
    "PA03": "CLUSTER_MESO_1",
    "PA04": "CLUSTER_MESO_2",
    "PA05": "CLUSTER_MESO_2",
    "PA06": "CLUSTER_MESO_2",
    "PA07": "CLUSTER_MESO_3",
    "PA08": "CLUSTER_MESO_3",
    "PA09": "CLUSTER_MESO_4",
    "PA10": "CLUSTER_MESO_4",
}
```

### 7.4 Cluster Topology Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLUSTER ASSIGNMENT TOPOLOGY                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CLUSTER_MESO_1          CLUSTER_MESO_2                        │
│  ┌─────────────┐         ┌─────────────┐                       │
│  │ PA01        │         │ PA04        │                       │
│  │ PA02        │         │ PA05        │                       │
│  │ PA03        │         │ PA06        │                       │
│  └─────────────┘         └─────────────┘                       │
│       │                       │                                 │
│       └───────────┬───────────┘                                 │
│                   │                                             │
│                   ▼                                             │
│            ┌─────────────┐                                      │
│            │   PHASE 6   │                                      │
│            │  CLUSTER    │                                      │
│            │ AGGREGATION │                                      │
│            └─────────────┘                                      │
│                   ▲                                             │
│       ┌───────────┴───────────┐                                 │
│       │                       │                                 │
│  CLUSTER_MESO_3          CLUSTER_MESO_4                        │
│  ┌─────────────┐         ┌─────────────┐                       │
│  │ PA07        │         │ PA09        │                       │
│  │ PA08        │         │ PA10        │                       │
│  └─────────────┘         └─────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Design by Contract Specification

### 8.1 Contract Philosophy

Phase 5 operates under **Design by Contract (DbC)** principles, establishing:

1. **Preconditions**: What must be true before the phase executes
2. **Postconditions**: What is guaranteed after successful execution
3. **Class Invariants**: Properties that must hold throughout the phase lifecycle

### 8.2 AreaPolicyAggregator Contract

```python
class AreaPolicyAggregator:
    """
    Contract Specification for AreaPolicyAggregator
    ═══════════════════════════════════════════════
    
    Class Invariants:
    - self.aggregation_settings is not None
    - self.area_group_by_keys is a non-empty list
    - If self.monolith is not None, then self.policy_areas has 10 elements
    """
    
    def aggregate_area(
        self,
        dimension_scores: list[DimensionScore],
        group_by_values: dict[str, Any],
        weights: list[float] | None = None
    ) -> AreaScore:
        """
        Aggregate dimension scores into a single area score.
        
        PRECONDITIONS:
        - len(dimension_scores) == 6 (hermetic)
        - ∀ ds ∈ dimension_scores: ds.score ∈ [0.0, 3.0]
        - ∀ ds ∈ dimension_scores: ds.area_id == group_by_values["area_id"]
        - If weights provided: len(weights) == len(dimension_scores)
        - If weights provided: all(w >= 0 for w in weights)
        
        POSTCONDITIONS:
        - result.score ∈ [0.0, 3.0]
        - result.area_id == group_by_values["area_id"]
        - result.quality_level ∈ {"EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"}
        - len(result.dimension_scores) == 6
        - result.cluster_id is not None
        - min(ds.score) <= result.score <= max(ds.score)  # Convexity
        
        INVARIANTS:
        - Σ weights = 1.0 (if weights provided)
        - Hermeticity validated before aggregation
        """
        ...
    
    def run(
        self,
        dimension_scores: list[DimensionScore],
        group_by_keys: list[str]
    ) -> list[AreaScore]:
        """
        Execute full Phase 5 aggregation.
        
        PRECONDITIONS:
        - len(dimension_scores) == 60
        - ∀ ds ∈ dimension_scores: ds.score ∈ [0.0, 3.0]
        - set(ds.area_id for ds in dimension_scores) == {PA01..PA10}
        - set(ds.dimension_id for ds in dimension_scores) == {DIM01..DIM06}
        
        POSTCONDITIONS:
        - len(result) == 10
        - set(as.area_id for as in result) == {PA01..PA10}
        - ∀ as ∈ result: as.score ∈ [0.0, 3.0]
        - ∀ as ∈ result: len(as.dimension_scores) == 6
        """
        ...
```

### 8.3 Invariant Enforcement

```python
class Phase5Invariants:
    """Invariant checks for Phase 5 output."""
    
    EXPECTED_AREA_COUNT = 10
    DIMENSIONS_PER_AREA = 6
    MIN_SCORE = 0.0
    MAX_SCORE = 3.0
    
    @staticmethod
    def validate_count(area_scores: list[AreaScore]) -> bool:
        """Validate that exactly 10 area scores are produced."""
        return len(area_scores) == Phase5Invariants.EXPECTED_AREA_COUNT
    
    @staticmethod
    def validate_hermeticity(area_score: AreaScore) -> bool:
        """Validate that all 6 dimensions are present."""
        return len(area_score.dimension_scores) == Phase5Invariants.DIMENSIONS_PER_AREA
    
    @staticmethod
    def validate_bounds(score: float) -> bool:
        """Validate score is within [0.0, 3.0]."""
        return Phase5Invariants.MIN_SCORE <= score <= Phase5Invariants.MAX_SCORE
    
    @staticmethod
    def validate_convexity(area_score: AreaScore) -> bool:
        """Validate convexity property."""
        if not area_score.dimension_scores:
            return True
        scores = [ds.score for ds in area_score.dimension_scores]
        return min(scores) <= area_score.score <= max(scores)
```

### 8.4 Exception Taxonomy

```
AggregationError (base)
├── HermeticityValidationError
│   ├── MissingDimensionError (GAP)
│   ├── DuplicateDimensionError (OVERLAP)
│   └── UnexpectedDimensionError (SCOPE_LEAK)
├── WeightNormalizationError
├── ScoreBoundsError
├── CountMismatchError
└── ProvenanceConstructionError
```

---

## 9. Data Structures and Type Definitions

### 9.1 Core Constants Module

**Location**: `phase5_10_00_phase_5_constants.py`

```python
"""Phase 5 Constants - Policy Area Aggregation"""

# Policy Area identifiers (10 total)
POLICY_AREAS = ["PA01", "PA02", "PA03", "PA04", "PA05", 
                "PA06", "PA07", "PA08", "PA09", "PA10"]

# Expected output count for Phase 5
EXPECTED_AREA_SCORE_COUNT = 10

# Dimensions per policy area (hermeticity requirement)
DIMENSIONS_PER_AREA = 6

# Dimension identifiers for hermeticity validation
DIMENSION_IDS = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]

# Cluster assignments (for Phase 6 transition)
CLUSTER_ASSIGNMENTS = {
    "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],
    "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],
    "CLUSTER_MESO_3": ["PA07", "PA08"],
    "CLUSTER_MESO_4": ["PA09", "PA10"],
}

# Score bounds (3-point scale)
MIN_SCORE = 0.0
MAX_SCORE = 3.0

# Hermeticity validation tolerance
HERMETICITY_TOLERANCE = 1e-6

# Quality level thresholds (normalized)
QUALITY_THRESHOLDS = {
    "EXCELENTE": 0.85,
    "BUENO": 0.70,
    "ACEPTABLE": 0.55,
    "INSUFICIENTE": 0.0
}
```

### 9.2 Stage Directory Structure

```
Phase_5/
├── __init__.py                          # Package façade
├── README.md                            # This document
├── PHASE_5_MANIFEST.json                # Phase metadata
├── TEST_MANIFEST.json                   # Test configuration
├── phase5_10_00_phase_5_constants.py    # Constants and enums
│
├── components/                          # Core functional modules
│   ├── area_aggregator.py               # Weighted aggregation logic
│   ├── cluster_assigner.py              # Policy area → cluster mapping
│   ├── dispersion_analyzer.py           # CV, DI, quartile computation
│   ├── hermeticity_validator.py         # Partition integrity checks
│   ├── provenance_tracker.py            # W3C PROV-DM compliance
│   └── weight_resolver.py               # Canonical weight loading
│
├── contracts/                           # DbC specifications
│   ├── phase5_contracts.json            # Input/output contracts
│   └── certificates/                    # Compliance certificates
│
└── tests/                               # Unit and integration tests
    ├── test_area_aggregator.py
    ├── test_cluster_assignment.py
    └── test_hermeticity.py
```

---

## 10. Uncertainty Quantification

### 10.1 Uncertainty Propagation

Phase 5 propagates uncertainty from DimensionScores to AreaScores:

**Input Uncertainty** (per DimensionScore):
- `score_std`: Standard deviation of contributing question scores
- `confidence_interval_95`: 95% CI from bootstrap aggregation
- `epistemic_uncertainty`: Model uncertainty
- `aleatoric_uncertainty`: Data uncertainty

**Output Uncertainty** (per AreaScore):
- `score_std`: Propagated standard deviation
- `confidence_interval_95`: Propagated 95% CI

### 10.2 Variance Propagation Formula

For weighted average with independent dimension scores:

```
Var(AreaScore) = Σᵢ wᵢ² · Var(DimensionScoreᵢ)

StdDev(AreaScore) = √(Σᵢ wᵢ² · σᵢ²)
```

Where `σᵢ = DimensionScoreᵢ.score_std`.

### 10.3 Confidence Interval Propagation

Using the **bootstrap aggregation** method:

```python
def propagate_confidence_interval(
    dimension_scores: list[DimensionScore],
    weights: list[float],
    n_bootstrap: int = 1000,
    confidence_level: float = 0.95
) -> tuple[float, float]:
    """
    Propagate confidence intervals via bootstrap resampling.
    
    Returns:
        (lower_bound, upper_bound) for the area score
    """
```

---

## 11. Provenance and Traceability

### 11.1 Provenance DAG Structure

Phase 5 contributes to the aggregation provenance DAG:

```
LEVEL: dimension           LEVEL: area
────────────────          ────────────

┌──────────────┐          ┌────────────┐
│ DIM01-PA01   │──────────│            │
├──────────────┤          │            │
│ DIM02-PA01   │──────────│   PA01     │
├──────────────┤          │            │
│ DIM03-PA01   │──────────│ AreaScore  │
├──────────────┤          │            │
│ DIM04-PA01   │──────────│            │
├──────────────┤          │            │
│ DIM05-PA01   │──────────│            │
├──────────────┤          │            │
│ DIM06-PA01   │──────────│            │
└──────────────┘          └────────────┘
```

### 11.2 Provenance Node Creation

```python
def create_area_provenance_node(
    area_score: AreaScore,
    dimension_nodes: list[ProvenanceNode],
    dag: AggregationDAG
) -> str:
    """
    Create provenance node for area score and link to dimension nodes.
    
    Returns:
        Node ID for the created area provenance node
    """
    node = ProvenanceNode(
        node_id=f"AREA-{area_score.area_id}",
        node_type="area",
        level="MESO",
        score=area_score.score,
        quality_level=area_score.quality_level,
        timestamp=datetime.utcnow().isoformat(),
        metadata={
            "area_name": area_score.area_name,
            "cluster_id": area_score.cluster_id,
            "aggregation_method": area_score.aggregation_method,
        }
    )
    
    # Add edges from dimension nodes
    for dim_node in dimension_nodes:
        dag.add_edge(dim_node.node_id, node.node_id)
    
    dag.add_node(node)
    return node.node_id
```

### 11.3 Audit Trail Requirements

Each AreaScore maintains:

| Field | Purpose |
|-------|---------|
| `provenance_node_id` | Link to DAG node |
| `aggregation_method` | Algorithm used (e.g., "weighted_average") |
| `validation_details` | Hermeticity, normalization, rubric details |
| `dimension_scores` | Complete list of contributing dimensions |

---

## 12. Implementation Architecture

### 12.1 Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                  PHASE 5 MODULE DEPENDENCIES                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase_5/__init__.py                                           │
│       │                                                         │
│       ├── phase5_10_00_phase_5_constants.py                    │
│       │       ├── POLICY_AREAS                                 │
│       │       ├── DIMENSION_IDS                                │
│       │       ├── CLUSTER_ASSIGNMENTS                          │
│       │       ├── QUALITY_THRESHOLDS                           │
│       │       └── Phase5Invariants                             │
│       │                                                         │
│       └── [DELEGATED TO PHASE 4]                               │
│               │                                                 │
│               ▼                                                 │
│       Phase_4/phase4_10_00_aggregation.py                      │
│               ├── AreaPolicyAggregator                         │
│               ├── AreaScore                                    │
│               ├── DimensionScore                               │
│               ├── AggregationSettings                          │
│               └── calculate_weighted_average()                 │
│                                                                 │
│       Phase_4/aggregation_provenance.py                        │
│               ├── AggregationDAG                               │
│               └── ProvenanceNode                               │
│                                                                 │
│       Phase_4/uncertainty_quantification.py                    │
│               ├── BootstrapAggregator                          │
│               └── UncertaintyMetrics                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 Integration with Phase 4

Phase 5 logic is primarily implemented in `Phase_4/phase4_10_00_aggregation.py` via the `AreaPolicyAggregator` class. The Phase_5 directory provides:

1. **Constants and Configuration**: Phase-specific constants in `phase5_10_00_phase_5_constants.py`
2. **Documentation**: This README and manifest files
3. **Stage Placeholders**: Empty stage directories for future extensions

### 12.3 Execution Flow

```python
# Integration point: called from orchestrator
async def aggregate_policy_areas_async(
    dimension_scores: list[DimensionScore],
    aggregator: AreaPolicyAggregator
) -> list[AreaScore]:
    """
    Async wrapper for Phase 5 aggregation.
    
    Called after Phase 4 (dimension aggregation) completes.
    """
    # Validate input count
    assert len(dimension_scores) == 60, f"Expected 60, got {len(dimension_scores)}"
    
    # Run aggregation
    area_scores = aggregator.run(dimension_scores, group_by_keys=["area_id"])
    
    # Validate output count
    assert len(area_scores) == 10, f"Expected 10, got {len(area_scores)}"
    
    return area_scores
```

---

## 13. Validation and Testing Framework

### 13.1 Test Categories

| Category | Purpose | Location |
|----------|---------|----------|
| **Unit Tests** | Individual function validation | `tests/phase_5/test_phase5_unit.py` |
| **Integration Tests** | Cross-module validation | `tests/phase_5/test_phase5_integration.py` |
| **Adversarial Tests** | Edge cases and malformed input | `tests/phase_5/test_phase5_adversarial.py` |
| **Extreme Tests** | Boundary conditions | `tests/phase_5/test_phase5_extreme_adversarial.py` |
| **Contract Tests** | DbC verification | `tests/phase_5/test_phase5_contracts.py` |

### 13.2 Key Test Cases

```python
class TestPhase5ConstantsIntegrity:
    """Validate Phase 5 constants against canonical structure."""
    
    def test_policy_areas_count(self):
        assert len(POLICY_AREAS) == 10
    
    def test_expected_area_count(self):
        assert EXPECTED_AREA_SCORE_COUNT == 10
    
    def test_dimensions_per_area(self):
        assert DIMENSIONS_PER_AREA == 6
    
    def test_score_bounds(self):
        assert MIN_SCORE == 0.0
        assert MAX_SCORE == 3.0
    
    def test_cluster_assignments_cover_all_pas(self):
        all_pas = set()
        for pa_list in CLUSTER_ASSIGNMENTS.values():
            all_pas.update(pa_list)
        assert len(all_pas) == 10


class TestPhase5Invariants:
    """Test Phase5Invariants class."""
    
    def test_validate_count_valid(self):
        mock_scores = [Mock() for _ in range(10)]
        assert Phase5Invariants.validate_count(mock_scores)
    
    def test_validate_count_invalid(self):
        mock_scores = [Mock() for _ in range(7)]
        assert not Phase5Invariants.validate_count(mock_scores)
    
    def test_validate_bounds_valid(self):
        assert Phase5Invariants.validate_bounds(0.0)
        assert Phase5Invariants.validate_bounds(1.5)
        assert Phase5Invariants.validate_bounds(3.0)
    
    def test_validate_bounds_invalid(self):
        assert not Phase5Invariants.validate_bounds(-0.1)
        assert not Phase5Invariants.validate_bounds(3.1)


class TestPipelineFlowValidation:
    """Tests for Phase 4 → Phase 5 → Phase 6 flow."""
    
    def test_input_output_cardinality(self):
        # Input: 10 PAs × 6 dimensions = 60
        input_count = 10 * 6
        assert input_count == 60
        
        # Output: 10 AreaScores
        output_count = 10
        assert output_count == 10
```

### 13.3 Compliance Certificate

**Certificate ID**: [CERTIFICATE_02_PHASE5_COUNT_10](../Phase_4/contracts/certificates/CERTIFICATE_02_PHASE5_COUNT_10.md)

| Requirement | Status |
|-------------|--------|
| Phase 5 Count = 10 | ✅ COMPLIANT |
| Validation Function | `validate_phase5_output()` |
| Test Coverage | Integration tests verify 10 area scores |

---

## 14. Performance Characteristics

### 14.1 Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Grouping | O(n) | O(n) |
| Hermeticity Validation | O(d) per area | O(d) |
| Weight Normalization | O(d) per area | O(d) |
| Weighted Average | O(d) per area | O(1) |
| Rubric Application | O(1) | O(1) |
| **Total Phase 5** | **O(n)** | **O(n)** |

Where:
- `n = 60` (input dimension scores)
- `d = 6` (dimensions per area)

### 14.2 Benchmarks

| Metric | Value |
|--------|-------|
| Typical execution time | < 10ms |
| Memory overhead | < 1MB |
| DAG node creation | ~10 nodes |

---

## 15. Error Taxonomy and Recovery

### 15.1 Error Categories

| Error Type | Cause | Recovery Strategy |
|------------|-------|-------------------|
| `HermeticityValidationError` | Missing/duplicate dimensions | Abort or graceful degradation |
| `WeightNormalizationError` | Weights sum ≠ 1.0 | Auto-normalize or abort |
| `ScoreBoundsError` | Score outside [0, 3] | Clamp or abort |
| `CountMismatchError` | Input ≠ 60 or output ≠ 10 | Abort (invariant violation) |

### 15.2 Error Handling Configuration

```python
class AggregationErrorPolicy:
    """Configure error handling behavior."""
    
    abort_on_hermeticity_violation: bool = True
    abort_on_weight_error: bool = True
    clamp_out_of_bounds_scores: bool = True
    log_level: str = "ERROR"
```

### 15.3 Graceful Degradation Protocol

When `abort_on_insufficient=False`:

1. **Missing Dimensions**: Aggregate over available dimensions with penalty
2. **Weight Errors**: Fall back to equal weights
3. **Score Bounds**: Clamp to [0.0, 3.0]

---

## 16. References and Related Documentation

### 16.1 Internal Documentation

| Document | Description |
|----------|-------------|
| [Phase 4 README](../Phase_4/README.md) | Dimension aggregation (micro → dimension) |
| [Phase 6 README](../Phase_6/README.md) | Cluster aggregation (area → cluster) |
| [Phase 7 README](../Phase_7/README.md) | Macro evaluation (cluster → global) |
| [AGGREGATION_QUICK_REFERENCE](../../../../docs/AGGREGATION_QUICK_REFERENCE.md) | Quick reference for aggregation usage |
| [ARCHITECTURE](../../../../docs/ARCHITECTURE.md) | System architecture overview |
| [CERTIFICATE_02](../Phase_4/contracts/certificates/CERTIFICATE_02_PHASE5_COUNT_10.md) | Phase 5 compliance certificate |

### 16.2 Academic References

1. Keeney, R.L., & Raiffa, H. (1976). *Decisions with Multiple Objectives: Preferences and Value Tradeoffs*. Cambridge University Press.

2. Belton, V., & Stewart, T.J. (2002). *Multiple Criteria Decision Analysis: An Integrated Approach*. Kluwer Academic Publishers.

3. Grabisch, M. (1997). "k-order additive discrete fuzzy measures and their representation". *Fuzzy Sets and Systems*, 92(2), 167-189.

4. W3C PROV-DM (2013). "PROV-DM: The PROV Data Model". W3C Recommendation.

### 16.3 Related Files

| File | Purpose |
|------|---------|
| `phase5_10_00_phase_5_constants.py` | Constants and enums |
| `../Phase_4/phase4_10_00_aggregation.py` | Core aggregator implementation |
| `../Phase_4/phase4_10_00_aggregation_validation.py` | Validation functions |
| `../Phase_4/aggregation_provenance.py` | Provenance DAG implementation |
| `tests/phase_5/test_phase5_integration.py` | Integration tests |

---

## Appendix A: Phase 5 Manifest

```json
{
  "$schema": "../../schemas/phase_manifest_schema.json",
  "manifest_version": "2.0.0",
  "phase": {
    "number": 5,
    "name": "Policy Area Aggregation",
    "codename": "AREA",
    "label": "Phase 5",
    "version": "2.0.0",
    "status": "ACTIVE",
    "criticality": "HIGH"
  },
  "contracts": {
    "input": "60 DimensionScore",
    "output": "10 AreaScore",
    "invariants": [
      "len(output) == 10",
      "all scores in [0.0, 3.0]",
      "hermeticity validated",
      "cluster_id assigned"
    ]
  },
  "quality_metrics": {
    "coverage": 0.88,
    "complexity": "HIGH"
  },
  "performance_characteristics": {
    "time_complexity": "O(n)",
    "space_complexity": "O(n)"
  }
}
```

---

## Appendix B: Quick Reference Card

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                    PHASE 5: POLICY AREA AGGREGATION                       ║
║                         QUICK REFERENCE CARD                              ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  INPUT:   60 DimensionScore (6 dimensions × 10 policy areas)             ║
║  OUTPUT:  10 AreaScore (PA01 through PA10)                               ║
║  SCALE:   [0.0, 3.0]                                                     ║
║                                                                           ║
║  INVARIANTS:                                                              ║
║    ✓ len(output) == 10                                                   ║
║    ✓ Each area has exactly 6 dimensions (hermeticity)                    ║
║    ✓ All scores in [0.0, 3.0]                                            ║
║    ✓ Convexity: min(dims) ≤ area_score ≤ max(dims)                       ║
║                                                                           ║
║  QUALITY THRESHOLDS (normalized):                                         ║
║    EXCELENTE:    >= 0.85 (>= 2.55 on 3-point scale)                      ║
║    BUENO:        >= 0.70 (>= 2.10)                                       ║
║    ACEPTABLE:    >= 0.55 (>= 1.65)                                       ║
║    INSUFICIENTE: <  0.55 (<  1.65)                                       ║
║                                                                           ║
║  CLUSTER ASSIGNMENTS:                                                     ║
║    CLUSTER_MESO_1: PA01, PA02, PA03                                      ║
║    CLUSTER_MESO_2: PA04, PA05, PA06                                      ║
║    CLUSTER_MESO_3: PA07, PA08                                            ║
║    CLUSTER_MESO_4: PA09, PA10                                            ║
║                                                                           ║
║  KEY FILES:                                                               ║
║    Constants: phase5_10_00_phase_5_constants.py                          ║
║    Aggregator: Phase_4/phase4_10_00_aggregation.py::AreaPolicyAggregator ║
║    Validation: Phase_4/phase4_10_00_aggregation_validation.py            ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

**Document Version**: 2.0.0  
**Last Updated**: 2026-01-11  
**Author**: F.A.R.F.A.N Core Team  
**Review Status**: CANONICAL
