# Phase 6: Cluster Aggregation — MESO-Level Synthesis

> **Abstract**: Phase 6 implements the third tier of the F.A.R.F.A.N. hierarchical aggregation pipeline, synthesizing 10 Policy Area scores into 4 MESO-level cluster scores. This phase introduces the Adaptive Penalty Framework (APF), a methodological contribution that applies evidence-based score corrections when intra-cluster dispersion exceeds theoretically justified thresholds. The adaptive penalty mechanism operationalizes the principle that a cluster with internally contradictory scores signals systemic implementation inconsistencies that merit quantitative penalization. This document provides the complete theoretical foundation, Design by Contract specifications, mathematical proofs, and implementation details necessary for reproducible scientific evaluation.

**Keywords**: Hierarchical aggregation, cluster analysis, adaptive penalties, dispersion metrics, coefficient of variation, Design by Contract, policy evaluation, W3C PROV-DM.

---

## Document Control

| Attribute | Value |
|-----------|-------|
| **Phase Identifier** | `PHASE-6-CLUSTER-AGGREGATION` |
| **Canonical Name** | `phase_6_cluster_aggregation` |
| **Status** | `ACTIVE` |
| **Version** | `2.0.0` |
| **Last Updated** | 2025-01-XX |
| **Pipeline Position** | Phase 5 → **Phase 6** → Phase 7 |
| **Compression Ratio** | 10:4 (2.5× reduction) |

---

## Table of Contents

1. [Theoretical Foundation](#1-theoretical-foundation)
2. [Phase Mission and Scope](#2-phase-mission-and-scope)
3. [Design by Contract Specifications](#3-design-by-contract-specifications)
4. [Data Model Architecture](#4-data-model-architecture)
5. [Cluster Topology](#5-cluster-topology)
6. [Aggregation Algorithm](#6-aggregation-algorithm)
7. [Adaptive Penalty Framework](#7-adaptive-penalty-framework)
8. [Dispersion Analysis](#8-dispersion-analysis)
9. [Coherence Analysis](#9-coherence-analysis)
10. [Uncertainty Quantification](#10-uncertainty-quantification)
11. [Provenance Tracking](#11-provenance-tracking)
12. [Implementation Reference](#12-implementation-reference)
13. [Validation Protocol](#13-validation-protocol)
14. [Directory Structure](#14-directory-structure)
15. [References and Related Documentation](#15-references-and-related-documentation)
16. [Appendix: Quick Reference Card](#16-appendix-quick-reference-card)

---

## 1. Theoretical Foundation

### 1.1 Hierarchical Aggregation Context

Phase 6 occupies a pivotal position in the F.A.R.F.A.N. aggregation hierarchy:

```
MICRO (300 questions) 
    → Phase 4 → DIMENSION (60 scores)     [5:1 compression]
        → Phase 5 → AREA (10 scores)      [6:1 compression]
            → Phase 6 → CLUSTER (4 scores) [2.5:1 compression]  ← THIS PHASE
                → Phase 7 → MACRO (1 score) [4:1 compression]
```

The 2.5:1 compression ratio at this level reflects the semantic clustering of policy areas into functionally coherent MESO-level groupings.

### 1.2 MESO-Level Theory

The MESO level (from Greek μέσος, "middle") represents an intermediate analytical tier between detailed operational assessments (MICRO) and holistic strategic evaluation (MACRO). At this level:

**Definition 1.1 (MESO Cluster)**: A MESO cluster $C_k$ is a non-empty subset of policy areas $\{PA_i\}_{i \in I_k}$ such that:
- All areas in $C_k$ share thematic or functional coherence
- $\bigcup_{k=1}^{4} C_k = \{PA_{01}, \ldots, PA_{10}\}$ (exhaustive coverage)
- $C_i \cap C_j = \emptyset$ for $i \neq j$ (mutual exclusivity)

**Theorem 1.1 (Partition Validity)**: The cluster assignment defines a valid partition of the policy area space.

*Proof*: By construction, each of the 10 policy areas is assigned to exactly one of 4 clusters, ensuring:
1. Exhaustiveness: $|C_1| + |C_2| + |C_3| + |C_4| = 3 + 3 + 2 + 2 = 10 = |PA|$
2. Exclusivity: Assignment is functional (each PA maps to exactly one cluster)
∎

### 1.3 Adaptive Penalty Rationale

**Axiom 1.1 (Coherence Axiom)**: A policy cluster achieves meaningful implementation when its constituent areas demonstrate coherent performance levels.

**Corollary 1.1**: High dispersion within a cluster indicates systemic implementation failures that should be penalized.

The Adaptive Penalty Framework (APF) operationalizes this axiom through empirically calibrated dispersion thresholds derived from the literature on coefficient of variation interpretation (Everitt & Skrondal, 2010).

---

## 2. Phase Mission and Scope

### 2.1 Mission Statement

Phase 6 synthesizes 10 Policy Area scores into 4 MESO-level Cluster scores, applying dispersion-based adaptive penalties to produce methodologically sound aggregate assessments.

### 2.2 Input/Output Contract Summary

| Aspect | Specification |
|--------|---------------|
| **Input** | 10 `AreaScore` objects (PA01–PA10) from Phase 5 |
| **Output** | 4 `ClusterScore` objects (CLUSTER_MESO_1–4) |
| **Invariant** | $|\text{output}| = 4$ |
| **Score Domain** | $[0.0, 3.0]$ (3-point scale) |
| **Transformation** | Weighted mean + adaptive penalty |

### 2.3 Functional Decomposition

| Stage | Responsibility | Mathematical Operation |
|-------|----------------|------------------------|
| S1 | Input Validation | Contract verification |
| S2 | Cluster Routing | Area → Cluster assignment |
| S3 | Weight Resolution | Load canonical cluster weights |
| S4 | Score Aggregation | Weighted arithmetic mean |
| S5 | Dispersion Analysis | CV, DI, quartile computation |
| S6 | Penalty Application | Scenario-based adjustment |
| S7 | Coherence Analysis | Within-cluster consistency |
| S8 | Uncertainty Quantification | Variance propagation |
| S9 | Provenance Recording | W3C PROV-DM entities |
| S10 | Output Assembly | ClusterScore construction |

---

## 3. Design by Contract Specifications

### 3.1 Preconditions

```python
@contract
def phase_6_preconditions(area_scores: List[AreaScore]) -> bool:
    """
    PRE-6.1: Input contains exactly 10 AreaScore objects
    PRE-6.2: All policy areas PA01-PA10 are represented
    PRE-6.3: Each area_score.score ∈ [0.0, 3.0]
    PRE-6.4: Each area_score has valid provenance chain
    PRE-6.5: No duplicate area identifiers
    """
    # PRE-6.1: Count validation
    assert len(area_scores) == 10, "Exactly 10 AreaScores required"
    
    # PRE-6.2: Coverage validation
    expected_areas = {f"PA{i:02d}" for i in range(1, 11)}
    actual_areas = {a.area_id for a in area_scores}
    assert expected_areas == actual_areas, "Complete PA01-PA10 coverage required"
    
    # PRE-6.3: Domain validation
    for area in area_scores:
        assert 0.0 <= area.score <= 3.0, f"Score out of bounds: {area.score}"
    
    # PRE-6.4: Provenance validation
    for area in area_scores:
        assert area.provenance is not None, "Provenance required"
        assert area.provenance.source_phase == "PHASE_5", "Source must be Phase 5"
    
    # PRE-6.5: Uniqueness validation
    assert len(actual_areas) == 10, "No duplicate area identifiers allowed"
    
    return True
```

### 3.2 Postconditions

```python
@contract
def phase_6_postconditions(
    cluster_scores: List[ClusterScore],
    input_areas: List[AreaScore]
) -> bool:
    """
    POST-6.1: Output contains exactly 4 ClusterScore objects
    POST-6.2: All clusters MESO_1-MESO_4 are represented
    POST-6.3: Each cluster_score.score ∈ [0.0, 3.0]
    POST-6.4: Each cluster_score.penalty_factor ∈ [0.7, 1.0]
    POST-6.5: Provenance chains reference correct input areas
    POST-6.6: Total input area count equals total contributing areas
    """
    # POST-6.1: Output count
    assert len(cluster_scores) == 4, "Exactly 4 ClusterScores required"
    
    # POST-6.2: Coverage
    expected_clusters = {f"CLUSTER_MESO_{i}" for i in range(1, 5)}
    actual_clusters = {c.cluster_id for c in cluster_scores}
    assert expected_clusters == actual_clusters
    
    # POST-6.3: Score bounds
    for cluster in cluster_scores:
        assert 0.0 <= cluster.score <= 3.0
    
    # POST-6.4: Penalty bounds
    for cluster in cluster_scores:
        assert 0.7 <= cluster.penalty_factor <= 1.0
    
    # POST-6.5: Provenance traceability
    all_contributing_areas = set()
    for cluster in cluster_scores:
        all_contributing_areas.update(cluster.provenance.contributing_areas)
    assert all_contributing_areas == {a.area_id for a in input_areas}
    
    # POST-6.6: Area count conservation
    total_contributing = sum(len(c.contributing_areas) for c in cluster_scores)
    assert total_contributing == 10
    
    return True
```

### 3.3 Invariants

```python
class Phase6Invariants:
    """Class-level invariants maintained throughout Phase 6 execution."""
    
    # INV-6.1: Cluster partition is fixed
    CLUSTER_PARTITION = {
        "CLUSTER_MESO_1": {"PA01", "PA02", "PA03"},  # 3 areas
        "CLUSTER_MESO_2": {"PA04", "PA05", "PA06"},  # 3 areas
        "CLUSTER_MESO_3": {"PA07", "PA08"},          # 2 areas
        "CLUSTER_MESO_4": {"PA09", "PA10"},          # 2 areas
    }
    
    # INV-6.2: Weight normalization per cluster
    # For each cluster k: Σ w_i = 1.0 where i ∈ cluster_k
    
    # INV-6.3: Penalty thresholds are immutable
    PENALTY_THRESHOLDS = {
        "CONVERGENCE": (0.0, 0.2),   # factor = 1.00
        "MODERATE": (0.2, 0.4),      # factor = 0.95
        "HIGH": (0.4, 0.6),          # factor = 0.85
        "EXTREME": (0.6, float('inf'))  # factor = 0.70
    }
    
    # INV-6.4: Score domain invariant
    SCORE_MIN = 0.0
    SCORE_MAX = 3.0
```

---

## 4. Data Model Architecture

### 4.1 Input Schema: AreaScore

```python
@dataclass(frozen=True)
class AreaScore:
    """Immutable representation of a Policy Area score from Phase 5."""
    
    area_id: str                    # PA01-PA10
    score: float                    # [0.0, 3.0]
    score_std: float                # Standard deviation
    quality_level: QualityLevel     # EXCELENTE|BUENO|ACEPTABLE|INSUFICIENTE
    contributing_dimensions: List[str]  # D001-D060 subset (6 per area)
    dispersion_metrics: DispersionMetrics
    provenance: ProvenanceRecord
    
    def __post_init__(self):
        assert self.area_id.startswith("PA"), "Invalid area identifier"
        assert 0.0 <= self.score <= 3.0, "Score out of bounds"
        assert len(self.contributing_dimensions) == 6, "Exactly 6 dimensions per area"
```

### 4.2 Output Schema: ClusterScore

```python
@dataclass(frozen=True)
class ClusterScore:
    """Immutable representation of a MESO Cluster score."""
    
    # Core identification
    cluster_id: str                 # CLUSTER_MESO_1 through CLUSTER_MESO_4
    cluster_name: str               # Human-readable name
    
    # Score components
    raw_score: float                # Pre-penalty weighted mean
    score: float                    # Post-penalty adjusted score
    score_std: float                # Propagated uncertainty
    quality_level: QualityLevel     # EXCELENTE|BUENO|ACEPTABLE|INSUFICIENTE
    
    # Penalty details
    penalty_factor: float           # [0.7, 1.0]
    penalty_scenario: str           # CONVERGENCE|MODERATE|HIGH|EXTREME
    
    # Dispersion analysis
    dispersion: ClusterDispersion
    
    # Coherence metrics
    coherence: CoherenceMetrics
    
    # Composition
    contributing_areas: List[str]   # PA identifiers
    area_weights: Dict[str, float]  # Normalized weights
    
    # Traceability
    provenance: ProvenanceRecord
```

### 4.3 Auxiliary Data Structures

```python
@dataclass(frozen=True)
class ClusterDispersion:
    """Dispersion metrics for a cluster."""
    
    coefficient_of_variation: float  # CV = σ/μ
    dispersion_index: float          # DI = (max-min)/mean
    interquartile_range: float       # IQR = Q3 - Q1
    quartiles: Tuple[float, float, float]  # Q1, Q2, Q3
    min_score: float
    max_score: float
    range: float                     # max - min
    
@dataclass(frozen=True)
class CoherenceMetrics:
    """Within-cluster coherence assessment."""
    
    coherence_index: float           # [0.0, 1.0]
    weakest_area: str                # Area identifier
    weakest_area_score: float        # Score of weakest area
    gap_to_mean: float               # How far below mean
    strategic_gaps: List[str]        # Areas below threshold
```

---

## 5. Cluster Topology

### 5.1 Cluster Composition Matrix

| Cluster | Policy Areas | Area Count | Thematic Focus |
|---------|--------------|------------|----------------|
| **CLUSTER_MESO_1** | PA01, PA02, PA03 | 3 | Legal & Institutional Framework |
| **CLUSTER_MESO_2** | PA04, PA05, PA06 | 3 | Implementation & Operational Capacity |
| **CLUSTER_MESO_3** | PA07, PA08 | 2 | Monitoring & Evaluation Systems |
| **CLUSTER_MESO_4** | PA09, PA10 | 2 | Strategic Planning & Sustainability |

### 5.2 Cluster Weight Distribution

**Default (Equal) Weights Within Clusters**:

| Cluster | Weight per Area | Total |
|---------|-----------------|-------|
| CLUSTER_MESO_1 | 0.3333 each | 1.0 |
| CLUSTER_MESO_2 | 0.3333 each | 1.0 |
| CLUSTER_MESO_3 | 0.5000 each | 1.0 |
| CLUSTER_MESO_4 | 0.5000 each | 1.0 |

**Theorem 5.1 (Weight Normalization)**: For each cluster $C_k$:
$$\sum_{PA_i \in C_k} w_i = 1.0$$

### 5.3 Cluster Adjacency and Interactions

```
                    CLUSTER_MESO_1
                    (PA01-PA03)
                    Legal Framework
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
    CLUSTER_MESO_2            CLUSTER_MESO_3
    (PA04-PA06)               (PA07-PA08)
    Implementation            Monitoring
            │                         │
            └────────────┬────────────┘
                         │
                         ▼
                    CLUSTER_MESO_4
                    (PA09-PA10)
                    Strategic Planning
```

---

## 6. Aggregation Algorithm

### 6.1 Mathematical Formulation

**Definition 6.1 (Cluster Score)**: For cluster $C_k$ with areas $\{PA_i\}_{i \in I_k}$ and weights $\{w_i\}$:

$$S_{C_k}^{raw} = \sum_{i \in I_k} w_i \cdot S_{PA_i}$$

where $S_{PA_i}$ is the score of policy area $i$.

**Definition 6.2 (Adjusted Cluster Score)**: The final cluster score incorporates the penalty factor:

$$S_{C_k} = S_{C_k}^{raw} \cdot \phi(CV_k)$$

where $\phi$ is the penalty function based on coefficient of variation.

### 6.2 Algorithm Pseudocode

```python
def aggregate_cluster(cluster_id: str, area_scores: List[AreaScore]) -> ClusterScore:
    """
    Phase 6 cluster aggregation algorithm.
    
    Complexity: O(n) where n = number of areas in cluster
    Space: O(1) auxiliary
    """
    # Step 1: Filter areas belonging to this cluster
    cluster_areas = [a for a in area_scores if a.area_id in CLUSTER_PARTITION[cluster_id]]
    
    # Step 2: Load canonical weights
    weights = load_cluster_weights(cluster_id)
    
    # Step 3: Compute weighted mean (raw score)
    raw_score = sum(w * a.score for w, a in zip(weights, cluster_areas))
    
    # Step 4: Compute dispersion metrics
    scores = [a.score for a in cluster_areas]
    dispersion = compute_dispersion(scores)
    
    # Step 5: Determine penalty scenario and factor
    scenario, penalty_factor = classify_dispersion(dispersion.coefficient_of_variation)
    
    # Step 6: Apply penalty
    adjusted_score = raw_score * penalty_factor
    
    # Step 7: Compute coherence metrics
    coherence = compute_coherence(cluster_areas, adjusted_score)
    
    # Step 8: Propagate uncertainty
    score_std = propagate_uncertainty(cluster_areas, weights)
    
    # Step 9: Record provenance
    provenance = create_provenance(cluster_id, cluster_areas, "PHASE_6")
    
    # Step 10: Assemble output
    return ClusterScore(
        cluster_id=cluster_id,
        raw_score=raw_score,
        score=clamp(adjusted_score, 0.0, 3.0),
        score_std=score_std,
        penalty_factor=penalty_factor,
        penalty_scenario=scenario,
        dispersion=dispersion,
        coherence=coherence,
        contributing_areas=[a.area_id for a in cluster_areas],
        provenance=provenance
    )
```

### 6.3 Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Area filtering | O(n) | O(k) where k = cluster size |
| Weight loading | O(1) | O(k) |
| Weighted mean | O(k) | O(1) |
| Dispersion metrics | O(k log k) | O(k) |
| Penalty classification | O(1) | O(1) |
| Coherence analysis | O(k) | O(1) |
| Uncertainty propagation | O(k) | O(1) |
| **Total per cluster** | **O(n)** | **O(k)** |
| **Total Phase 6** | **O(n)** | **O(n)** |

---

## 7. Adaptive Penalty Framework

### 7.1 Theoretical Basis

The Adaptive Penalty Framework (APF) is grounded in the statistical principle that high coefficient of variation (CV) indicates measurement instability or systemic inconsistency.

**Definition 7.1 (Coefficient of Variation)**: For a sample $\{x_1, \ldots, x_n\}$:

$$CV = \frac{\sigma}{\mu} = \frac{\sqrt{\frac{1}{n}\sum_{i=1}^{n}(x_i - \mu)^2}}{\frac{1}{n}\sum_{i=1}^{n}x_i}$$

**Interpretation Thresholds** (adapted from Everitt & Skrondal, 2010):

| CV Range | Interpretation | Penalty Justification |
|----------|----------------|----------------------|
| < 0.2 | Low variability | Coherent implementation |
| 0.2–0.4 | Moderate variability | Minor inconsistencies |
| 0.4–0.6 | High variability | Significant gaps |
| ≥ 0.6 | Very high variability | Systemic failure |

### 7.2 Penalty Function

**Definition 7.2 (Penalty Function)**: The penalty function $\phi: [0, \infty) \to [0.7, 1.0]$ is defined as:

$$\phi(CV) = \begin{cases}
1.00 & \text{if } CV < 0.2 \quad (\text{CONVERGENCE}) \\
0.95 & \text{if } 0.2 \leq CV < 0.4 \quad (\text{MODERATE}) \\
0.85 & \text{if } 0.4 \leq CV < 0.6 \quad (\text{HIGH}) \\
0.70 & \text{if } CV \geq 0.6 \quad (\text{EXTREME})
\end{cases}$$

### 7.3 Implementation

```python
def classify_dispersion(cv: float) -> Tuple[str, float]:
    """
    Classify CV into penalty scenario and return penalty factor.
    
    Args:
        cv: Coefficient of variation
        
    Returns:
        (scenario_name, penalty_factor)
    """
    if cv < 0.2:
        return ("CONVERGENCE", 1.00)
    elif cv < 0.4:
        return ("MODERATE", 0.95)
    elif cv < 0.6:
        return ("HIGH", 0.85)
    else:
        return ("EXTREME", 0.70)
```

### 7.4 Penalty Impact Analysis

**Example Calculation**:

| Area | Score | Weight |
|------|-------|--------|
| PA01 | 2.5 | 0.333 |
| PA02 | 1.0 | 0.333 |
| PA03 | 2.8 | 0.333 |

- Mean: $\mu = (2.5 + 1.0 + 2.8) / 3 = 2.1$
- Std: $\sigma = \sqrt{((2.5-2.1)^2 + (1.0-2.1)^2 + (2.8-2.1)^2)/3} = 0.78$
- CV: $0.78 / 2.1 = 0.37$ → **MODERATE** scenario
- Raw Score: $0.333 \times 2.5 + 0.333 \times 1.0 + 0.333 \times 2.8 = 2.1$
- Penalty Factor: $0.95$
- **Adjusted Score**: $2.1 \times 0.95 = 1.995$

---

## 8. Dispersion Analysis

### 8.1 Comprehensive Dispersion Metrics

Phase 6 computes multiple dispersion indicators for diagnostic purposes:

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **CV** | $\sigma / \mu$ | Relative variability |
| **DI** | $(max - min) / \mu$ | Range dispersion |
| **IQR** | $Q_3 - Q_1$ | Middle-half spread |
| **Range** | $max - min$ | Total spread |

### 8.2 Dispersion Computation

```python
def compute_dispersion(scores: List[float]) -> ClusterDispersion:
    """
    Compute comprehensive dispersion metrics for a cluster.
    
    Args:
        scores: List of area scores within cluster
        
    Returns:
        ClusterDispersion object with all metrics
    """
    n = len(scores)
    sorted_scores = sorted(scores)
    
    # Central tendency
    mean = sum(scores) / n
    
    # Variance and standard deviation
    variance = sum((s - mean) ** 2 for s in scores) / n
    std = math.sqrt(variance)
    
    # Coefficient of variation
    cv = std / mean if mean > 0 else 0.0
    
    # Range metrics
    min_score = sorted_scores[0]
    max_score = sorted_scores[-1]
    score_range = max_score - min_score
    
    # Dispersion index
    di = score_range / mean if mean > 0 else 0.0
    
    # Quartiles (for n >= 2)
    q1 = sorted_scores[n // 4] if n >= 4 else min_score
    q2 = sorted_scores[n // 2] if n >= 2 else mean
    q3 = sorted_scores[3 * n // 4] if n >= 4 else max_score
    iqr = q3 - q1
    
    return ClusterDispersion(
        coefficient_of_variation=cv,
        dispersion_index=di,
        interquartile_range=iqr,
        quartiles=(q1, q2, q3),
        min_score=min_score,
        max_score=max_score,
        range=score_range
    )
```

### 8.3 Dispersion Diagnostic Output

```json
{
  "cluster_id": "CLUSTER_MESO_1",
  "dispersion": {
    "coefficient_of_variation": 0.37,
    "dispersion_index": 0.86,
    "interquartile_range": 0.75,
    "quartiles": [1.0, 2.5, 2.8],
    "min_score": 1.0,
    "max_score": 2.8,
    "range": 1.8
  },
  "penalty_scenario": "MODERATE",
  "penalty_factor": 0.95
}
```

---

## 9. Coherence Analysis

### 9.1 Within-Cluster Coherence Index

**Definition 9.1 (Coherence Index)**: The coherence index $CI$ measures internal consistency:

$$CI = 1 - \frac{CV}{CV_{max}}$$

where $CV_{max} = 1.0$ is the maximum expected CV for the 3-point scale.

For the 3-point scale [0, 3], theoretical $CV_{max} \approx 1.73$ (when half scores are 0 and half are 3).

### 9.2 Weakest Area Identification

```python
def compute_coherence(
    cluster_areas: List[AreaScore],
    cluster_score: float
) -> CoherenceMetrics:
    """
    Compute within-cluster coherence metrics.
    """
    scores = [a.score for a in cluster_areas]
    mean_score = sum(scores) / len(scores)
    
    # Find weakest area
    weakest = min(cluster_areas, key=lambda a: a.score)
    gap_to_mean = mean_score - weakest.score
    
    # Identify strategic gaps (areas below INSUFICIENTE threshold)
    INSUFICIENTE_THRESHOLD = 1.65  # 0.55 × 3.0
    strategic_gaps = [a.area_id for a in cluster_areas if a.score < INSUFICIENTE_THRESHOLD]
    
    # Compute coherence index
    cv = compute_cv(scores)
    coherence_index = max(0.0, 1.0 - cv)
    
    return CoherenceMetrics(
        coherence_index=coherence_index,
        weakest_area=weakest.area_id,
        weakest_area_score=weakest.score,
        gap_to_mean=gap_to_mean,
        strategic_gaps=strategic_gaps
    )
```

### 9.3 Strategic Gap Detection

A **strategic gap** is identified when:

1. An area scores below the INSUFICIENTE threshold (< 0.55 normalized, < 1.65 on 3-point scale)
2. Multiple areas in the same cluster are below threshold (systemic issue)
3. The gap between weakest and strongest area exceeds 1.5 points

**Output Example**:

```json
{
  "coherence": {
    "coherence_index": 0.63,
    "weakest_area": "PA02",
    "weakest_area_score": 1.0,
    "gap_to_mean": 1.1,
    "strategic_gaps": ["PA02"]
  }
}
```

---

## 10. Uncertainty Quantification

### 10.1 Variance Propagation Theory

For weighted linear combinations, variance propagates as:

$$\text{Var}(S_{C_k}) = \sum_{i \in I_k} w_i^2 \cdot \text{Var}(S_{PA_i})$$

Assuming independence between policy area scores.

### 10.2 Standard Deviation Propagation

```python
def propagate_uncertainty(
    cluster_areas: List[AreaScore],
    weights: List[float]
) -> float:
    """
    Propagate uncertainty from area scores to cluster score.
    
    Uses variance addition for independent weighted sum.
    """
    variance = sum(
        (w ** 2) * (a.score_std ** 2)
        for w, a in zip(weights, cluster_areas)
    )
    return math.sqrt(variance)
```

### 10.3 Confidence Interval Construction

For a cluster score $S$ with standard deviation $\sigma$:

- **68% CI**: $[S - \sigma, S + \sigma]$
- **95% CI**: $[S - 1.96\sigma, S + 1.96\sigma]$
- **99% CI**: $[S - 2.576\sigma, S + 2.576\sigma]$

---

## 11. Provenance Tracking

### 11.1 W3C PROV-DM Compliance

Phase 6 generates provenance records conforming to the W3C PROV Data Model:

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 6 Provenance DAG                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Entity: AreaScore[PA01]    ──┐                             │
│  Entity: AreaScore[PA02]    ──┼──▶ Activity: ClusterAgg_1   │
│  Entity: AreaScore[PA03]    ──┘           │                 │
│                                           │ wasGeneratedBy  │
│                                           ▼                 │
│                              Entity: ClusterScore[MESO_1]   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 11.2 Provenance Record Structure

```python
@dataclass(frozen=True)
class Phase6Provenance:
    """Provenance record for Phase 6 cluster aggregation."""
    
    entity_id: str              # Unique entity identifier
    entity_type: str            # "ClusterScore"
    generated_at: datetime      # ISO 8601 timestamp
    generated_by: str           # "phase_6_cluster_aggregation"
    
    # Derivation chain
    was_derived_from: List[str]  # AreaScore entity IDs
    contributing_areas: List[str]  # PA identifiers
    
    # Activity details
    activity_id: str            # Aggregation activity ID
    algorithm: str              # "weighted_mean_with_adaptive_penalty"
    algorithm_version: str      # "2.0.0"
    
    # Parameters used
    parameters: Dict[str, Any]  # Weights, penalty thresholds, etc.
```

### 11.3 Provenance JSON Example

```json
{
  "entity_id": "ent:cluster_score:CLUSTER_MESO_1:20250115T143022Z",
  "entity_type": "ClusterScore",
  "generated_at": "2025-01-15T14:30:22.456Z",
  "generated_by": "phase_6_cluster_aggregation",
  "was_derived_from": [
    "ent:area_score:PA01:20250115T143020Z",
    "ent:area_score:PA02:20250115T143020Z",
    "ent:area_score:PA03:20250115T143021Z"
  ],
  "activity_id": "act:cluster_aggregation:MESO_1:20250115T143022Z",
  "algorithm": "weighted_mean_with_adaptive_penalty",
  "algorithm_version": "2.0.0",
  "parameters": {
    "weights": {"PA01": 0.333, "PA02": 0.333, "PA03": 0.333},
    "penalty_thresholds": {"CONVERGENCE": 0.2, "MODERATE": 0.4, "HIGH": 0.6},
    "penalty_factors": {"CONVERGENCE": 1.0, "MODERATE": 0.95, "HIGH": 0.85, "EXTREME": 0.70}
  }
}
```

---

## 12. Implementation Reference

### 12.1 Core Module Structure

```python
# phase_6_cluster_aggregation.py

from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

class ClusterAggregator:
    """
    Phase 6 Cluster Aggregation Engine.
    
    Aggregates 10 Policy Area scores into 4 MESO-level Cluster scores
    with adaptive penalty based on intra-cluster dispersion.
    """
    
    def __init__(self, config: Phase6Config):
        self.config = config
        self.weight_resolver = WeightResolver()
        self.dispersion_analyzer = DispersionAnalyzer()
        self.penalty_calculator = AdaptivePenaltyCalculator()
        self.provenance_tracker = ProvenanceTracker()
    
    def aggregate(self, area_scores: List[AreaScore]) -> List[ClusterScore]:
        """
        Main aggregation entry point.
        
        Args:
            area_scores: 10 AreaScore objects from Phase 5
            
        Returns:
            4 ClusterScore objects
            
        Raises:
            PreconditionViolation: If input contracts fail
            PostconditionViolation: If output contracts fail
        """
        # Verify preconditions
        self._verify_preconditions(area_scores)
        
        # Aggregate each cluster
        cluster_scores = []
        for cluster_id in CLUSTER_IDS:
            cluster_score = self._aggregate_single_cluster(cluster_id, area_scores)
            cluster_scores.append(cluster_score)
        
        # Verify postconditions
        self._verify_postconditions(cluster_scores, area_scores)
        
        return cluster_scores
```

### 12.2 Configuration Schema

```python
@dataclass
class Phase6Config:
    """Configuration for Phase 6 execution."""
    
    # Penalty configuration
    penalty_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "CONVERGENCE": 0.2,
        "MODERATE": 0.4,
        "HIGH": 0.6
    })
    
    penalty_factors: Dict[str, float] = field(default_factory=lambda: {
        "CONVERGENCE": 1.00,
        "MODERATE": 0.95,
        "HIGH": 0.85,
        "EXTREME": 0.70
    })
    
    # Weight source
    weight_source: str = "canonical"  # "canonical" | "custom"
    custom_weights: Optional[Dict[str, Dict[str, float]]] = None
    
    # Validation strictness
    strict_validation: bool = True
```

---

## 13. Validation Protocol

### 13.1 Unit Test Coverage

| Test Category | Test Cases | Coverage Target |
|---------------|------------|-----------------|
| Precondition verification | 5 | 100% |
| Aggregation correctness | 4 | 100% |
| Penalty application | 4 | 100% |
| Dispersion computation | 6 | 100% |
| Edge cases | 8 | 100% |
| Postcondition verification | 4 | 100% |

### 13.2 Critical Test Cases

```python
def test_penalty_application_moderate_cv():
    """Verify MODERATE penalty (0.95) applied for CV in [0.2, 0.4)."""
    areas = [
        AreaScore(area_id="PA01", score=2.5, ...),
        AreaScore(area_id="PA02", score=1.5, ...),  # Creates CV ≈ 0.3
        AreaScore(area_id="PA03", score=2.0, ...),
    ]
    
    aggregator = ClusterAggregator(Phase6Config())
    result = aggregator._aggregate_single_cluster("CLUSTER_MESO_1", areas)
    
    assert result.penalty_scenario == "MODERATE"
    assert result.penalty_factor == 0.95
    assert result.score == pytest.approx(result.raw_score * 0.95, rel=1e-6)

def test_cluster_partition_exhaustive():
    """Verify all 10 areas are assigned to exactly one cluster."""
    all_assigned = set()
    for cluster_id, areas in CLUSTER_PARTITION.items():
        for area in areas:
            assert area not in all_assigned, f"{area} assigned multiple times"
            all_assigned.add(area)
    
    expected = {f"PA{i:02d}" for i in range(1, 11)}
    assert all_assigned == expected
```

### 13.3 Integration Validation

```yaml
integration_tests:
  - name: "Phase 5 → Phase 6 flow"
    input: "10 AreaScores from Phase 5"
    expected_output: "4 ClusterScores"
    validation:
      - output_count: 4
      - score_bounds: [0.0, 3.0]
      - penalty_bounds: [0.7, 1.0]
      - provenance_chain: "PHASE_5 → PHASE_6"
```

---

## 14. Directory Structure

```
Phase_6/
├── __init__.py                          # Package façade
├── README.md                            # This document
├── PHASE_6_MANIFEST.json                # Phase metadata
├── TEST_MANIFEST.json                   # Test configuration
├── phase6_10_00_phase_6_constants.py    # Constants and enums
│
├── components/                          # Core functional modules
│   ├── cluster_aggregator.py            # Main aggregation logic
│   ├── adaptive_penalty.py              # Penalty calculation
│   ├── dispersion_analyzer.py           # CV, DI, quartile computation
│   ├── coherence_analyzer.py            # Within-cluster coherence
│   ├── provenance_tracker.py            # W3C PROV-DM compliance
│   └── weight_resolver.py               # Canonical weight loading
│
├── contracts/                           # DbC specifications
│   ├── phase6_contracts.json            # Input/output contracts
│   └── certificates/                    # Compliance certificates
│
└── tests/                               # Unit and integration tests
    ├── test_cluster_aggregator.py
    ├── test_adaptive_penalty.py
    ├── test_dispersion.py
    └── test_coherence.py
```

---

## 15. References and Related Documentation

### 15.1 Internal Documentation

| Document | Description |
|----------|-------------|
| [Phase 4 README](../Phase_4/README.md) | Dimension aggregation (micro → dimension) |
| [Phase 5 README](../Phase_5/README.md) | Policy area aggregation (dimension → area) |
| [Phase 7 README](../Phase_7/README.md) | Macro evaluation (cluster → global) |
| [AGGREGATION_QUICK_REFERENCE](../../../../docs/AGGREGATION_QUICK_REFERENCE.md) | Quick reference for aggregation usage |
| [ARCHITECTURE](../../../../docs/ARCHITECTURE.md) | System architecture overview |

### 15.2 Academic References

1. Everitt, B.S., & Skrondal, A. (2010). *The Cambridge Dictionary of Statistics* (4th ed.). Cambridge University Press.

2. Belton, V., & Stewart, T.J. (2002). *Multiple Criteria Decision Analysis: An Integrated Approach*. Kluwer Academic Publishers.

3. Saaty, T.L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.

4. W3C PROV-DM (2013). "PROV-DM: The PROV Data Model". W3C Recommendation. https://www.w3.org/TR/prov-dm/

5. Meyer, B. (1992). "Applying Design by Contract". *IEEE Computer*, 25(10), 40-51.

### 15.3 Related Files

| File | Purpose |
|------|---------|
| `phase6_10_00_phase_6_constants.py` | Constants and enumerations |
| `PHASE_6_MANIFEST.json` | Phase metadata and contracts |
| `../Phase_4/contracts/certificates/` | Cross-phase compliance certificates |

---

## 16. Appendix: Quick Reference Card

### Phase 6 at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│               PHASE 6: CLUSTER AGGREGATION                  │
├─────────────────────────────────────────────────────────────┤
│  INPUT:  10 AreaScore (PA01-PA10)                           │
│  OUTPUT: 4 ClusterScore (MESO_1-4)                          │
│  RATIO:  2.5:1 compression                                  │
├─────────────────────────────────────────────────────────────┤
│  CLUSTER PARTITION:                                         │
│    MESO_1: PA01, PA02, PA03 (3 areas)                       │
│    MESO_2: PA04, PA05, PA06 (3 areas)                       │
│    MESO_3: PA07, PA08      (2 areas)                        │
│    MESO_4: PA09, PA10      (2 areas)                        │
├─────────────────────────────────────────────────────────────┤
│  PENALTY FUNCTION φ(CV):                                    │
│    CV < 0.2  → 1.00 (CONVERGENCE)                           │
│    CV < 0.4  → 0.95 (MODERATE)                              │
│    CV < 0.6  → 0.85 (HIGH)                                  │
│    CV ≥ 0.6  → 0.70 (EXTREME)                               │
├─────────────────────────────────────────────────────────────┤
│  FORMULA:                                                   │
│    S_cluster = (Σ w_i × S_area_i) × φ(CV)                   │
├─────────────────────────────────────────────────────────────┤
│  CONTRACT SUMMARY:                                          │
│    PRE:  len(input) == 10, all PA01-PA10, scores ∈ [0,3]    │
│    POST: len(output) == 4, all MESO_1-4, scores ∈ [0,3]     │
│    INV:  partition is fixed, weights sum to 1.0 per cluster │
└─────────────────────────────────────────────────────────────┘
```

---

*Document generated for F.A.R.F.A.N. Policy Evaluation Framework v2.0*
*Last updated: 2025-01*
