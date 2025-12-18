# Phase 4-7: Aggregation Pipeline

## Document Control

| Attribute | Value |
|-----------|-------|
| **Phase ID** | `PHASE-4-7-AGGREGATION-PIPELINE` |
| **Canonical Name** | `phase_4_7_aggregation_pipeline` |
| **Acronym** | AP (Aggregation Pipeline) |
| **Status** | `CANONICAL` |
| **Version** | `2025-12-18` |
| **Pipeline Position** | Phase 3 (Scoring) → **Phase 4-7** → Final Output |

---

## 1. Phase Mission

The **Aggregation Pipeline** transforms **300 scored micro-questions from Phase 3** into a **single holistic MacroScore** through four sequential aggregation stages:

| Logical Phase | Responsibility | Input | Output | Invariant |
|---------------|----------------|-------|--------|-----------|
| **Phase 4** | Dimension Aggregation | 300 ScoredMicroQuestion | 60 DimensionScore (6 dims × 10 PAs) | `len(output) == 60` |
| **Phase 5** | Policy Area Aggregation | 60 DimensionScore | 10 AreaScore | `len(output) == 10` |
| **Phase 6** | Cluster Aggregation (MESO) | 10 AreaScore | 4 ClusterScore | `len(output) == 4` |
| **Phase 7** | Macro Evaluation | 4 ClusterScore | 1 MacroScore | `output is not None` |

---

## 2. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    AGGREGATION PIPELINE DATA FLOW                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  Phase 3 Output                                                                          │
│  ══════════════                                                                          │
│  300 × ScoredMicroQuestion                                                               │
│       │                                                                                  │
│       │ PHASE 4: Dimension Aggregation                                                   │
│       │ ═══════════════════════════════                                                  │
│       │ Group by (policy_area, dimension)                                                │
│       │ Apply dimension weights from signal registry                                     │
│       │ Compute weighted average + uncertainty                                           │
│       ▼                                                                                  │
│  60 × DimensionScore (6 dimensions × 10 policy areas)                                    │
│       │                                                                                  │
│       │ PHASE 5: Policy Area Aggregation                                                 │
│       │ ═════════════════════════════════                                                │
│       │ Group by policy_area                                                             │
│       │ Validate hermeticity (all 6 dimensions present)                                  │
│       │ Apply area-dimension weights                                                     │
│       ▼                                                                                  │
│  10 × AreaScore (PA01–PA10)                                                              │
│       │                                                                                  │
│       │ PHASE 6: Cluster Aggregation (MESO)                                              │
│       │ ═══════════════════════════════════                                              │
│       │ Group by cluster (4 clusters)                                                    │
│       │ Apply adaptive penalty based on dispersion                                       │
│       │ Compute coherence metrics                                                        │
│       ▼                                                                                  │
│  4 × ClusterScore                                                                        │
│       │                                                                                  │
│       │ PHASE 7: Macro Evaluation                                                        │
│       │ ═════════════════════════════                                                    │
│       │ Aggregate all clusters                                                           │
│       │ Compute cross-cutting coherence                                                  │
│       │ Identify systemic gaps                                                           │
│       │ Assess strategic alignment                                                       │
│       ▼                                                                                  │
│  1 × MacroScore (holistic evaluation)                                                    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Constitutional Invariants

| Invariant ID | Specification | Source | Enforcement |
|--------------|---------------|--------|-------------|
| **INV-P4-60** | Phase 4 produces exactly 60 DimensionScores | `aggregation.py::DimensionAggregator.run()` | `validate_phase4_output()` |
| **INV-P5-10** | Phase 5 produces exactly 10 AreaScores | `aggregation.py::AreaPolicyAggregator.run()` | `validate_phase5_output()` |
| **INV-P6-4** | Phase 6 produces exactly 4 ClusterScores | `aggregation.py::ClusterAggregator.run()` | `validate_phase6_output()` |
| **INV-P7-1** | Phase 7 produces exactly 1 MacroScore | `aggregation.py::MacroAggregator.evaluate_macro()` | `validate_phase7_output()` |
| **INV-P4-7-BOUNDS** | All scores ∈ [0.0, 3.0] (3-point scale) | `aggregation.py::AggregationSettings` | Score validation |
| **INV-P4-7-HERMETIC** | Each aggregation level is hermetic (all expected inputs present) | `aggregation_enhancements.py::HermeticityDiagnosis` | Hermeticity validation |
| **INV-P4-7-PROVENANCE** | Every aggregation operation creates provenance node | `aggregation_provenance.py::AggregationDAG` | DAG construction |
| **INV-P4-7-CHOQUET** | Choquet aggregation satisfies boundedness: 0 ≤ Cal(I) ≤ 1 | `choquet_aggregator.py::ChoquetAggregator` | `_validate_boundedness()` |

---

## 4. File Inventory

| File | Purpose | Module Type | Criticality |
|------|---------|-------------|-------------|
| `__init__.py` | Package façade with comprehensive exports | CORE | REQUIRED |
| `aggregation.py` | Core aggregators + dataclasses (98KB) | CORE | **CRITICAL** |
| `choquet_aggregator.py` | Choquet integral implementation | CORE | **CRITICAL** |
| `aggregation_enhancements.py` | Enhanced aggregators with CI, dispersion, hermeticity | ENHANCEMENT | HIGH |
| `aggregation_validation.py` | Phase-specific validation functions | VALIDATION | HIGH |
| `aggregation_provenance.py` | DAG-based provenance tracking, Shapley attribution | PROVENANCE | HIGH |
| `signal_enriched_aggregation.py` | SISAS-aware weight adjustment | SIGNAL | HIGH |
| `adaptive_meso_scoring.py` | Adaptive penalty computation for Phase 6 | ENHANCEMENT | STANDARD |

---

## 5. Orchestrator Execution Transcript

### Entry Point

```
orchestrator._aggregate_results_async(scored_results: list[ScoredMicroQuestion])
```

The orchestrator receives **300 ScoredMicroQuestion** objects from Phase 3 and invokes the aggregation pipeline through `aggregation_integration.py`.

---

### STEP 1: Load Aggregation Settings

```python
settings = AggregationSettings.from_signal_registry(
    signal_registry=self.signal_registry
)

# IF signal_registry is None:
settings = AggregationSettings.from_monolith(
    self.questionnaire_monolith
)

# LOG: "Aggregation settings loaded, source={settings.sisas_source}"
```

**Signal Sources:**
- `sisas_registry` — Signal-driven weights from SISAS registry (preferred)
- `legacy_monolith` — Weights from questionnaire monolith (fallback)

---

### STEP 2: Initialize Aggregators

```python
dimension_aggregator = DimensionAggregator(
    settings=settings,
    signal_registry=self.signal_registry,
    enable_sota_features=True,  # Choquet, UQ, provenance
)

area_aggregator = AreaPolicyAggregator(
    settings=settings,
    signal_registry=self.signal_registry,
)

cluster_aggregator = ClusterAggregator(
    settings=settings,
    signal_registry=self.signal_registry,
)

macro_aggregator = MacroAggregator(settings=settings)
```

---

### STEP 3: Phase 4 — Dimension Aggregation

```python
dimension_scores = await aggregate_dimensions_async(
    scored_results=scored_results,
    aggregator=dimension_aggregator
)
```

**Internal Process:**
1. Convert `ScoredMicroQuestion` → `ScoredResult` (internal format)
2. Group by `(policy_area, dimension)` → 60 groups
3. For each group:
   - Resolve weights from settings
   - Calculate weighted average (or Choquet if SOTA enabled)
   - Compute uncertainty (std, CI)
   - Create `DimensionScore`
   - Add to provenance DAG

**Validation:**
```python
result = validate_phase4_output(dimension_scores, expected_count=60)
if not result.passed:
    raise AggregationValidationError(result.error_message)
```

**Invariant:** `len(dimension_scores) == 60`

---

### STEP 4: Phase 5 — Policy Area Aggregation

```python
area_scores = await aggregate_policy_areas_async(
    dimension_scores=dimension_scores,
    aggregator=area_aggregator
)
```

**Internal Process:**
1. Group by `policy_area` → 10 groups
2. For each group:
   - Validate hermeticity (all 6 dimensions present)
   - If NOT hermetic: `diagnosis = diagnose_hermeticity(...)`
   - Resolve area-dimension weights
   - Calculate weighted average
   - Create `AreaScore`
   - Add to provenance DAG with edges

**Validation:**
```python
result = validate_phase5_output(area_scores, expected_count=10)
if not result.passed:
    raise AggregationValidationError(result.error_message)
```

**Invariant:** `len(area_scores) == 10`

---

### STEP 5: Phase 6 — Cluster Aggregation (MESO)

```python
cluster_scores = aggregate_clusters(
    area_scores=area_scores,
    aggregator=cluster_aggregator
)
```

**Internal Process:**
1. Group by `cluster_id` → 4 groups
2. For each group:
   - Validate cluster hermeticity
   - Compute dispersion metrics (CV, DI, quartiles)
   - Classify scenario: `convergence | moderate | high | extreme`
   - Compute adaptive penalty factor
   - Apply cluster weights
   - Calculate weighted average WITH penalty
   - Analyze coherence
   - Identify weakest area
   - Create `ClusterScore`

**Adaptive Penalty Formula:**
```
penalty_factor = 1.0 - (normalized_std × PENALTY_WEIGHT)
adjusted_score = weighted_score × penalty_factor
```

**Validation:**
```python
result = validate_phase6_output(cluster_scores, expected_count=4)
if not result.passed:
    raise AggregationValidationError(result.error_message)
```

**Invariant:** `len(cluster_scores) == 4`

---

### STEP 6: Phase 7 — Macro Evaluation

```python
macro_score = evaluate_macro(
    cluster_scores=cluster_scores,
    aggregator=macro_aggregator
)
```

**Internal Process:**
1. Calculate macro score from cluster scores
2. Calculate cross-cutting coherence
3. Identify systemic gaps (areas with `INSUFICIENTE`)
4. Assess strategic alignment
5. Apply rubric thresholds for quality level
6. Create `MacroScore`

**Validation:**
```python
result = validate_phase7_output(macro_score)
if not result.passed:
    raise AggregationValidationError(result.error_message)
```

**Invariant:** `macro_score is not None`

---

### STEP 7: Full Pipeline Validation

```python
final_validation = validate_with_contracts(
    dimension_scores=dimension_scores,
    area_scores=area_scores,
    cluster_scores=cluster_scores,
    macro_score=macro_score
)

if not final_validation.passed:
    raise AggregationValidationError(final_validation.error_message)

# LOG: "Full aggregation pipeline validation: PASSED"
```

---

### STEP 8: Convert to Output Format

```python
evaluation_dict = macro_score_to_evaluation(macro_score)
```

**Output Format:**
```python
{
    "score": float,                         # [0.0, 3.0]
    "quality_level": str,                   # "EXCELENTE" | "BUENO" | "ACEPTABLE" | "INSUFICIENTE"
    "cross_cutting_coherence": float,       # [0.0, 1.0]
    "systemic_gaps": list[str],             # Identified gaps
    "strategic_alignment": float,           # [0.0, 1.0]
    "cluster_scores": [...],                # 4 cluster details
    "validation_passed": bool,
    "validation_details": {...}
}
```

---

## 6. Contract Signatures

### 6.1 Entry Contract (Phase 3 → Phase 4)

**Contract ID:** `CONTRACT-P4-7-ENTRY`

| Precondition | Specification | Enforcement |
|--------------|---------------|-------------|
| PRE-P4-01 | `len(scored_results) == 300` | Count check |
| PRE-P4-02 | `∀ sr: sr.score ∈ [0.0, 1.0]` | Bounds check |
| PRE-P4-03 | `∀ sr: sr.quality_level ∈ VALID_QUALITY_LEVELS` | Enum check |
| PRE-P4-04 | Signal registry available (optional) | DI check |

### 6.2 Exit Contract (Phase 7 → Output)

**Contract ID:** `CONTRACT-P4-7-EXIT`

| Postcondition | Specification | Enforcement |
|---------------|---------------|-------------|
| POST-P4-01 | `len(dimension_scores) == 60` | `validate_phase4_output()` |
| POST-P4-02 | `len(area_scores) == 10` | `validate_phase5_output()` |
| POST-P4-03 | `len(cluster_scores) == 4` | `validate_phase6_output()` |
| POST-P4-04 | `macro_score is not None` | `validate_phase7_output()` |
| POST-P4-05 | `macro_score.score ∈ [0.0, 3.0]` | Bounds check |
| POST-P4-06 | `∀ cs: cs.coherence ∈ [0.0, 1.0]` | Coherence validation |

---

## 7. Signal Wiring

### 7.1 Signal Flow

```
QuestionnaireSignalRegistry (SISAS)
        │
        │ get_assembly_signals("meso")
        ▼
AggregationSettings.from_signal_registry()
        │
        │ Constructor DI
        ▼
SignalEnrichedAggregator
        │
        │ adjust_aggregation_weights()
        │ analyze_score_dispersion()
        │ select_aggregation_method()
        ▼
Core Aggregators (signal-adjusted weights)
```

### 7.2 Signal Consumption Points

| Module | Signal Source | Consumption Function |
|--------|---------------|---------------------|
| `aggregation.py` | `AggregationSettings` | `_resolve_dimension_weights()` |
| `aggregation.py` | `signal_registry` | `from_signal_registry()` |
| `signal_enriched_aggregation.py` | `QuestionnaireSignalRegistry` | `adjust_aggregation_weights()` |
| `signal_enriched_aggregation.py` | `SignalPack.patterns` | Pattern count check |

---

## 8. Provenance Tracking

### 8.1 DAG Structure

```
LEVEL: micro              LEVEL: dimension         LEVEL: area    LEVEL: cluster   LEVEL: macro
───────────              ────────────────         ───────────    ──────────────   ────────────

┌─────────┐              ┌──────────────┐         ┌────────┐     ┌─────────────┐  ┌───────────┐
│ Q001    │──────────────│ DIM01-PA01   │─────────│ PA01   │─────│ CLUSTER_1   │──│ MACRO     │
│ Q002    │              │              │         │        │     │             │  │           │
│ Q003    │              └──────────────┘         └────────┘     └─────────────┘  │ score     │
│ ...     │                                                                       │ coherence │
└─────────┘                                                                       │ gaps      │
(300)                    (60)                     (10)           (4)              └───────────┘
                                                                                  (1)
```

### 8.2 Attribution

Shapley values computed for feature attribution:
```python
shapley = dag.compute_shapley_attribution("MACRO")
critical_path = dag.get_critical_path("MACRO", top_k=5)
```

---

## 9. Quality Rubric

| Quality Level | Normalized Score Range | Description |
|---------------|------------------------|-------------|
| **EXCELENTE** | ≥ 0.85 | Outstanding policy compliance |
| **BUENO** | ≥ 0.70 | Good compliance with minor gaps |
| **ACEPTABLE** | ≥ 0.55 | Acceptable with improvement areas |
| **INSUFICIENTE** | < 0.55 | Insufficient, requires intervention |

---

## 10. Choquet Integral

### Formula

```
Cal(I) = Σ(aₗ·xₗ) + Σ(aₗₖ·min(xₗ,xₖ))
```

Where:
- `xₗ`: Score for layer l (normalized to [0,1])
- `aₗ`: Linear weight for layer l
- `aₗₖ`: Interaction weight for layer pair (l,k)
- `Cal(I)`: Choquet-aggregated calibration score ∈ [0,1]

### Boundedness Guarantee

- Weights normalized: `Σ(aₗ) = 1.0`
- Interactions constrained: `Σ(aₗₖ) ≤ 0.5 × Σ(aₗ)`
- Result clamped: `max(0.0, min(1.0, Cal(I)))`

---

## 11. Related Documents

- [PHASE_4_7_RIA_2025-12-18.txt](./PHASE_4_7_RIA_2025-12-18.txt) — Repository Inventory Artifact
- [FORCING_ROUTE.md](./FORCING_ROUTE.md) — Execution constraints
- [../../../docs/choquet_examples/](../../../docs/choquet_examples/) — Choquet integral examples

---

## 12. Changelog

| Date | Version | Change |
|------|---------|--------|
| 2025-12-18 | 1.0.0 | Initial canonical documentation |
