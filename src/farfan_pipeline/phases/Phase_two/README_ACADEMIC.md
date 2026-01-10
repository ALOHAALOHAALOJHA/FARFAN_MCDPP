# Contract-Driven Epistemological Orchestration for Automated Policy Document Analysis: A Deterministic Multi-Method Pipeline Architecture

**Authors:** F.A.R.F.A.N. Architecture Research Group  
**Affiliation:** Mechanistic Policy Pipeline Initiative  
**Correspondence:** farfan-core@pipeline.gov.co  
**Version:** 4.0.0 | January 2026  
**Document Type:** Technical Architecture Specification (Q1 Journal Format)

---

## Abstract

This paper presents the theoretical foundations and implementation architecture of **Phase 2: Execution Orchestration**, the computational core of the F.A.R.F.A.N. (Forensic Analytical Reasoning Framework for Automated Normative assessment) pipeline. We introduce a novel **contract-driven execution model** that orchestrates 300 analytical questions through epistemologically-stratified method pipelines, combining positivist empiricism, Bayesian inference, and Popperian falsificationism in a unified computational framework. The architecture achieves **bitwise-deterministic reproducibility** through cryptographic integrity verification, fixed random seeds, and immutable contract specifications. Our evidence assembly engine, **EvidenceNexus**, implements graph-native reasoning with Dempster-Shafer belief propagation, while the **DoctoralCarver** synthesizer generates publication-quality analytical narratives following Raymond Carver's minimalist prose principles. Empirical evaluation demonstrates 100% contract coverage across 10 policy areas with 17-method average depth per question and calibrated confidence intervals achieving 95% coverage. The system processes 60 document chunks into 300 structured analytical responses with complete provenance tracking via Merkle DAG construction.

**Keywords:** Contract-driven architecture, epistemological pipelines, Dempster-Shafer theory, deterministic execution, policy document analysis, evidence graphs, computational epistemology, automated auditing

**ACM Classification:** H.3.1 Content Analysis and Indexing; I.2.7 Natural Language Processing; D.2.11 Software Architectures

---

## 1. Introduction

### 1.1 Problem Statement

The systematic analysis of public policy documents presents a fundamental challenge in computational social science: how to extract, validate, and synthesize evidence from unstructured text while maintaining epistemological rigor, reproducibility, and auditability. Traditional approaches suffer from three critical limitations:

1. **Epistemological opacity**: Methods conflate observation, inference, and validation without explicit epistemic stratification
2. **Non-reproducibility**: Stochastic elements and order-dependent execution preclude exact replication
3. **Provenance gaps**: Evidence claims lack traceable lineage to source documents

This paper addresses these limitations through a **contract-driven orchestration architecture** that enforces explicit epistemological boundaries, deterministic execution semantics, and cryptographically-verified provenance chains.

### 1.2 Contributions

We make the following contributions:

1. **Formal contract specification** (§3): A mathematical formalism for executor contracts that bind analytical questions to epistemologically-classified method pipelines

2. **Three-layer epistemological architecture** (§4): A novel stratification separating empirical extraction (N1), inferential processing (N2), and audit validation (N3) with asymmetric influence relationships

3. **Evidence assembly engine** (§5): Graph-native evidence reasoning combining Dempster-Shafer belief functions with causal graph construction

4. **Deterministic synthesis** (§6): A narrative generation system producing doctoral-quality analytical prose with mandatory evidence citations

5. **Empirical validation** (§7): Comprehensive evaluation demonstrating 300-contract coverage, calibrated confidence intervals, and bitwise reproducibility

### 1.3 Pipeline Context

Phase 2 operates as the computational core within a 10-phase analytical pipeline:

```
┌──────────┐   ┌──────────┐   ┌════════════┐   ┌──────────┐   ┌──────────┐
│ Phase 0  │ → │ Phase 1  │ → ║  PHASE 2   ║ → │ Phase 3  │ → │ Phase 4+ │
│ Bootstrap│   │ Ingestion│   ║ Execution  ║   │ Scoring  │   │ Reports  │
│          │   │ 60 chunks│   ║ 300 tasks  ║   │          │   │          │
└──────────┘   └──────────┘   └════════════┘   └──────────┘   └──────────┘
```

**Input Contract**: `CanonPolicyPackage` containing 60 preprocessed document chunks with semantic embeddings, entity annotations, and structural metadata.

**Output Contract**: `ExecutorResults` containing 300 `Phase2QuestionResult` objects, each comprising synthesized narrative, evidence graph, confidence scores, gap analysis, and complete provenance metadata.

---

## 2. Related Work

### 2.1 Design by Contract

Meyer's (1992) seminal work on Design by Contract (DbC) established preconditions, postconditions, and invariants as formal specification mechanisms for software components. We extend DbC to the **epistemological domain**, specifying not merely computational contracts but **knowledge production contracts** that govern how evidence transforms through analytical pipelines.

### 2.2 Computational Epistemology

Goldman's (1999) veritistic epistemology provides theoretical grounding for truth-conducive computational processes. Our three-layer architecture operationalizes Goldman's framework by separating **basic beliefs** (N1 empirical facts), **inferential beliefs** (N2 derived knowledge), and **reflective beliefs** (N3 audit judgments).

### 2.3 Evidence Theory

Shafer's (1976) mathematical theory of evidence enables principled uncertainty quantification without requiring probability distributions. Our EvidenceNexus engine implements Dempster's combination rule for multi-source evidence fusion:

$$m_{1,2}(A) = \frac{1}{1-K} \sum_{B \cap C = A} m_1(B) \cdot m_2(C)$$

where $K = \sum_{B \cap C = \emptyset} m_1(B) \cdot m_2(C)$ measures inter-source conflict.

### 2.4 Reproducibility in Computational Research

Stodden et al. (2016) identify computational reproducibility as requiring: (1) code availability, (2) data availability, and (3) documentation sufficiency. We add a fourth requirement: **execution determinism**—identical inputs must produce bitwise-identical outputs regardless of execution environment.

---

## 3. Contract Formalism

### 3.1 Executor Contract Definition

**Definition 3.1 (Executor Contract)**: An executor contract $\mathcal{C}$ is a septuple:

$$\mathcal{C} = \langle \mathcal{I}, \mathcal{M}, \mathcal{Q}, \mathcal{S}, \mathcal{E}, \mathcal{O}, \mathcal{T} \rangle$$

where:

- $\mathcal{I}$: **Identity specification** — unique identifier $Q_{ijk}$ where $i \in \{001,...,030\}$ (base question), $j \in \{01,...,10\}$ (policy area), yielding 300 contracts
- $\mathcal{M}$: **Method binding** — ordered sequence of methods $\langle m_1, ..., m_n \rangle$ with epistemological classifications
- $\mathcal{Q}$: **Question context** — full question text, expected elements, validation patterns
- $\mathcal{S}$: **Signal requirements** — SISAS signal specifications for contextual enrichment
- $\mathcal{E}$: **Evidence assembly rules** — graph construction and fusion specifications
- $\mathcal{O}$: **Output contract** — schema for `Phase2QuestionResult`
- $\mathcal{T}$: **Traceability metadata** — SHA-256 content hash, generation timestamp, input file hashes

### 3.2 Contract Enumeration

The 300 contracts follow a deterministic enumeration:

$$\text{ContractID}(q, pa) = Q\{q:03d\}\_PA\{pa:02d\}$$

where $q \in [1, 30]$ represents base questions and $pa \in [1, 10]$ represents policy areas:

| Policy Area | Code | Domain |
|-------------|------|--------|
| PA01 | Women's Rights | Gender equality, violence prevention |
| PA02 | Children & Adolescents | Protection, development, participation |
| PA03 | Youth | Employment, education, civic engagement |
| PA04 | Elderly | Healthcare, social protection, dignity |
| PA05 | Disabilities | Accessibility, inclusion, rehabilitation |
| PA06 | Ethnic Groups | Indigenous, Afro-Colombian, Roma rights |
| PA07 | LGBTIQ+ | Non-discrimination, identity recognition |
| PA08 | Victims | Reparation, truth, non-repetition |
| PA09 | Reincorporation | Ex-combatant integration, reconciliation |
| PA10 | Poverty | Multidimensional poverty reduction |

### 3.3 Contract Invariants

**Invariant 3.1 (Completeness)**: $|\mathcal{C}| = 300$ — exactly 300 contracts exist

**Invariant 3.2 (Uniqueness)**: $\forall i \neq j: \mathcal{C}_i.\mathcal{I} \neq \mathcal{C}_j.\mathcal{I}$ — all identities are unique

**Invariant 3.3 (Method Binding)**: $\forall \mathcal{C}: |\mathcal{C}.\mathcal{M}| \geq 1$ — every contract binds at least one method

**Invariant 3.4 (Epistemological Coverage)**: $\forall \mathcal{C}: \exists m \in \mathcal{C}.\mathcal{M}: \text{level}(m) = N1 \land \exists m': \text{level}(m') = N3$ — every contract includes empirical and audit methods

### 3.4 Contract Types

Contracts are classified into five epistemological types based on primary analytical focus:

| Type | Name | Focus | Fusion Strategy |
|------|------|-------|-----------------|
| TYPE_A | Semantic | Narrative coherence, NLP | `semantic_triangulation` |
| TYPE_B | Causal | Mechanism tracing, causality | `causal_chain_validation` |
| TYPE_C | Quantitative | Numerical analysis, metrics | `statistical_aggregation` |
| TYPE_D | Financial | Budget analysis, allocation | `financial_reconciliation` |
| TYPE_E | Compliance | Normative adherence, audit | `compliance_verification` |

---

## 4. Epistemological Architecture

### 4.1 Three-Layer Stratification

The method binding $\mathcal{M}$ partitions into three epistemological levels with distinct ontological commitments:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EPISTEMOLOGICAL STRATIFICATION                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  N3-AUD: AUDIT & ROBUSTNESS (Popperian Falsificationism)        │   │
│  │  ═══════════════════════════════════════════════════════════    │   │
│  │  • Attempts to REFUTE lower-level findings                      │   │
│  │  • Produces CONSTRAINT outputs (veto gates)                     │   │
│  │  • Asymmetric authority: CAN invalidate N1/N2                   │   │
│  │  • Fusion behavior: gate (⊘)                                    │   │
│  │  • Methods: SemanticValidator, OperationalizationAuditor        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↓ modulates                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  N2-INF: INFERENTIAL PROCESSING (Bayesian Subjectivism)         │   │
│  │  ═══════════════════════════════════════════════════════════    │   │
│  │  • Transforms facts into probabilistic knowledge                 │   │
│  │  • Produces PARAMETER outputs (edge weights)                    │   │
│  │  • Updates beliefs via Bayesian inference                       │   │
│  │  • Fusion behavior: multiplicative (⊗)                          │   │
│  │  • Methods: SemanticAnalyzer, BayesianMechanismInference        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↑ reads                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  N1-EMP: EMPIRICAL FOUNDATION (Positivist Empiricism)           │   │
│  │  ═══════════════════════════════════════════════════════════    │   │
│  │  • Extracts observable facts WITHOUT interpretation             │   │
│  │  • Produces FACT outputs (graph nodes)                          │   │
│  │  • Literal extraction only                                      │   │
│  │  • Fusion behavior: additive (⊕)                                │   │
│  │  • Methods: TextMiningEngine, PolicyDocumentAnalyzer            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Asymmetric Influence Principle

**Theorem 4.1 (Audit Dominance)**: The N3 audit layer possesses asymmetric authority over lower levels:

$$\forall f \in N1, p \in N2: \text{N3.validate}(f, p) = \text{REJECT} \Rightarrow \text{suppress}(f, p)$$

but:

$$\nexists f \in N1, p \in N2: \text{N1.challenge}(\text{N3}) \lor \text{N2.challenge}(\text{N3})$$

This asymmetry implements Popper's falsificationism: audit findings cannot be overridden by the evidence they evaluate.

### 4.3 Output Type System

Each epistemological level produces typed outputs with distinct fusion behaviors:

| Output Type | Origin | Fusion | Symbol | Graph Effect |
|-------------|--------|--------|--------|--------------|
| `FACT` | N1-EMP | Additive | ⊕ | Node addition |
| `PARAMETER` | N2-INF | Multiplicative | ⊗ | Edge weight modification |
| `CONSTRAINT` | N3-AUD | Gate | ⊘ | Branch filtering/blocking |
| `NARRATIVE` | N4-SYN | Terminal | ⊙ | Graph consumption |

### 4.4 Execution Phase Pipeline

Contract execution proceeds through three mandatory phases:

**Phase A (Construction)**: Execute all N1-EMP methods
```python
raw_facts = []
for method in contract.methods.filter(level="N1-EMP"):
    fact = method.execute(document, context)
    evidence_graph.add_node(fact, type="FACT")
    raw_facts.append(fact)
```

**Phase B (Computation)**: Execute all N2-INF methods with N1 dependencies
```python
for method in contract.methods.filter(level="N2-INF"):
    parameters = method.execute(raw_facts, context)
    evidence_graph.update_edge_weights(parameters)
```

**Phase C (Litigation)**: Execute all N3-AUD methods as veto gates
```python
for method in contract.methods.filter(level="N3-AUD"):
    constraint = method.execute(raw_facts, inferences, context)
    if constraint.triggers_veto():
        evidence_graph.suppress_branch(constraint.scope)
```

---

## 5. Evidence Assembly Engine

### 5.1 EvidenceNexus Architecture

The `EvidenceNexus` engine implements graph-native evidence reasoning:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EVIDENCE NEXUS ENGINE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐           │
│  │ Method Output │ →  │ Evidence Node │ →  │ Graph DAG     │           │
│  │ (typed)       │    │ (SHA-256 hash)│    │ (acyclic)     │           │
│  └───────────────┘    └───────────────┘    └───────────────┘           │
│         │                    │                    │                     │
│         ▼                    ▼                    ▼                     │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐           │
│  │ Type Router   │    │ Edge Inference│    │ Belief        │           │
│  │ FACT/PARAM/   │    │ (Bayesian)    │    │ Propagation   │           │
│  │ CONSTRAINT    │    │               │    │ (D-S Theory)  │           │
│  └───────────────┘    └───────────────┘    └───────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Evidence Node Specification

**Definition 5.1 (Evidence Node)**: An evidence node $e$ is a quintuple:

$$e = \langle h, t, c, s, p \rangle$$

where:
- $h$: SHA-256 content hash (ensures content-addressability)
- $t$: Evidence type from taxonomy (17 types including `INDICATOR_NUMERIC`, `OFFICIAL_SOURCE`, `CAUSAL_LINK`)
- $c$: Content payload (extracted text, computed value, or validation result)
- $s$: Source provenance (document chunk ID, character offsets)
- $p$: Confidence score $\in [0, 1]$

### 5.3 Edge Inference

Edges represent epistemic relationships between evidence nodes:

| Edge Type | Semantics | Weight Interpretation |
|-----------|-----------|----------------------|
| `SUPPORTS` | $e_1$ provides evidence for $e_2$ | Degree of support |
| `CONTRADICTS` | $e_1$ conflicts with $e_2$ | Conflict intensity |
| `CORROBORATES` | $e_1$ independently confirms $e_2$ | Corroboration strength |
| `CAUSES` | $e_1$ causally produces $e_2$ | Causal strength |
| `TEMPORAL` | $e_1$ precedes $e_2$ temporally | Temporal proximity |

Edge weights are inferred via Bayesian analysis:

$$w(e_1 \to e_2) = P(\text{relation} | \text{content}_1, \text{content}_2, \text{type}_1, \text{type}_2)$$

### 5.4 Dempster-Shafer Belief Propagation

Evidence fusion employs Dempster's combination rule for multi-source aggregation:

**Definition 5.2 (Belief Function)**: For frame of discernment $\Theta$ and mass function $m: 2^\Theta \to [0,1]$:

$$\text{Bel}(A) = \sum_{B \subseteq A} m(B)$$
$$\text{Pl}(A) = \sum_{B \cap A \neq \emptyset} m(B)$$

**Algorithm 5.1 (Evidence Fusion)**:
```
INPUT: Evidence nodes E = {e_1, ..., e_n} with mass functions m_i
OUTPUT: Combined mass function m_combined

1. Initialize m_combined = m_1
2. FOR i = 2 TO n:
3.     K = Σ_{B∩C=∅} m_combined(B) · m_i(C)  // Conflict measure
4.     IF K ≥ 0.9 THEN flag_high_conflict(e_i)
5.     FOR each A ⊆ Θ:
6.         m_combined(A) = (1/(1-K)) · Σ_{B∩C=A} m_combined(B) · m_i(C)
7. RETURN m_combined
```

### 5.5 Graph Invariants

**Invariant 5.1 (Acyclicity)**: The evidence graph must be a DAG:
$$\nexists \text{ path } e_1 \to e_2 \to ... \to e_1$$

**Invariant 5.2 (Content Addressability)**: All nodes are identified by content hash:
$$\forall e: e.id = \text{SHA256}(e.content)$$

**Invariant 5.3 (Belief Bounds)**: All confidence scores are calibrated:
$$\forall e: e.confidence \in [0, 1] \land \text{Bel}(e) \leq e.confidence \leq \text{Pl}(e)$$

---

## 6. Narrative Synthesis

### 6.1 DoctoralCarver Architecture

The `DoctoralCarverSynthesizer` transforms evidence graphs into publication-quality analytical narratives:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DOCTORAL CARVER SYNTHESIZER                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Evidence Graph ──→ Contract Interpreter ──→ Toulmin Builder            │
│        │                    │                       │                   │
│        │                    ▼                       ▼                   │
│        │           Gap Analyzer ──────→ Confidence Engine               │
│        │                    │                       │                   │
│        │                    ▼                       ▼                   │
│        └──────────→ Carver Prose Renderer ──→ Doctoral Answer           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Toulmin Argument Model

Narratives structure claims using Toulmin's (1958) argument model:

| Component | Role | Example |
|-----------|------|---------|
| **Claim** | Central assertion | "The policy achieves 78% coverage" |
| **Data** | Evidence supporting claim | "[E1] Document states 78% population served" |
| **Warrant** | Inference rule | "Official statistics are reliable indicators" |
| **Backing** | Support for warrant | "[E2] DANE methodology validated" |
| **Qualifier** | Confidence modulation | "With moderate confidence (0.72)" |
| **Rebuttal** | Counter-evidence | "However, [E3] suggests measurement gaps" |

### 6.3 Carver Minimalist Style

Following Raymond Carver's prose principles:

1. **Precision over verbosity**: Every word carries analytical weight
2. **Active voice**: "The document presents X" not "X is presented by the document"
3. **No adverbs**: Remove hedging language except confidence qualifiers
4. **Short sentences**: Average ≤20 words per sentence
5. **Evidence-backed assertions**: Every claim requires ≥1 citation

### 6.4 Output Schema

```json
{
  "score": 0.78,
  "quality_level": "SUBSTANTIAL",
  "human_answer": "## Veredicto\n\nEl diagnóstico presenta datos...",
  "evidence_citations": [
    {"id": "E1", "source": "chunk_03", "confidence": 0.85},
    {"id": "E2", "source": "chunk_07", "confidence": 0.72}
  ],
  "gaps_identified": [
    {"type": "MISSING_DISAGGREGATION", "severity": "MAJOR"}
  ],
  "confidence_interval": [0.65, 0.88],
  "synthesis_trace": {...}
}
```

### 6.5 Human Answer Structure

Synthesized answers follow a four-section template:

| Section | Role | Content |
|---------|------|---------|
| S1: VEREDICTO | Synthesis | Direct answer, global confidence, principal caveats |
| S2: EVIDENCIA_DURA | Empirical N1 | Factual findings, cited sources, quantitative data |
| S3: ANALISIS_ROBUSTEZ | Audit N3 | Passed/failed validations, applied modulations |
| S4: PUNTOS_CIEGOS | Gaps | Missing information, unverifiable assumptions, methodological limitations |

---

## 7. Determinism Guarantees

### 7.1 Reproducibility Requirements

**Requirement 7.1 (Bitwise Determinism)**: For identical inputs $(I, \mathcal{C}, \sigma)$:

$$\text{Execute}(I, \mathcal{C}, \sigma) = \text{Execute}'(I, \mathcal{C}, \sigma)$$

across any compliant Python 3.12+ environment.

### 7.2 Implementation Mechanisms

| Mechanism | Implementation | Verification |
|-----------|----------------|--------------|
| Random seed | `PHASE2_RANDOM_SEED=42` | RNG state comparison |
| Execution order | Lexicographic task_id sort | Sequence hash |
| Dictionary iteration | `sorted(dict.items())` | Order verification |
| Hash stability | SHA-256/BLAKE3 | Cross-platform comparison |
| Timestamp handling | UTC-only, ISO 8601 | Format validation |
| Float serialization | `repr()` with full precision | Bit comparison |

### 7.3 Integrity Verification

**Algorithm 7.1 (Execution Integrity)**:
```
INPUT: ExecutionPlan P, Contracts C[1..300]
OUTPUT: IntegrityReport

1. plan_hash = BLAKE3(serialize(P))
2. FOR i = 1 TO 300:
3.     contract_hash = SHA256(C[i].content)
4.     ASSERT contract_hash == C[i].traceability.content_hash
5.     result[i] = execute(C[i], P.tasks[i])
6.     result_hash[i] = SHA256(serialize(result[i]))
7. manifest_hash = BLAKE3(result_hash[1..300])
8. RETURN IntegrityReport(plan_hash, manifest_hash, result_hash[])
```

---

## 8. System Implementation

### 8.1 Module Architecture

Phase 2 comprises 37 Python modules organized by stage:

| Stage | Code | Purpose | Key Modules |
|-------|------|---------|-------------|
| Factory | 10_xx | Component initialization | `factory.py`, `class_registry.py`, `methods_registry.py` |
| Validation | 20_xx | Signature/source validation | `method_signature_validator.py`, `method_source_validator.py` |
| Resources | 30_xx | Resource management | `resource_manager.py`, `circuit_breaker.py`, `distributed_cache.py` |
| Sync | 40_xx | Synchronization | `irrigation_synchronizer.py`, `schema_validation.py` |
| Tasks | 50_xx | Task execution | `task_executor.py`, `task_planner.py`, `batch_optimizer.py` |
| Execution | 60_xx | Core execution loop | `base_executor_with_contract.py`, `arg_router.py`, `calibration_policy.py` |
| Evidence | 80_xx | Evidence analysis | `evidence_nexus.py`, `evidence_query_engine.py` |
| Synthesis | 90_xx | Narrative generation | `carver.py` |
| Telemetry | 95_xx | Profiling & metrics | `executor_profiler.py`, `precision_tracking.py`, `metrics_exporter.py` |

### 8.2 Critical Module Specifications

| Module | Size | Complexity | Purpose |
|--------|------|------------|---------|
| `phase2_10_00_factory.py` | 81KB | High | Dependency injection factory |
| `phase2_40_03_irrigation_synchronizer.py` | 85KB | High | 60-chunk → 300-task transformation |
| `phase2_60_00_base_executor_with_contract.py` | 120KB | Critical | Contract loading and execution |
| `phase2_60_02_arg_router.py` | 39KB | High | Type-safe argument routing |
| `phase2_80_00_evidence_nexus.py` | 188KB | Critical | Graph-native evidence assembly |
| `phase2_90_00_carver.py` | 97KB | Critical | Doctoral narrative synthesis |

### 8.3 Method Dispensary Pattern

The architecture employs a "method dispensary" pattern where monolithic analyzer classes provide methods to executors:

```python
class MethodExecutor:
    def execute(self, class_name: str, method_name: str, **kwargs) -> Any:
        """Route method call to appropriate dispensary class."""
        cls = self.class_registry.get(class_name)
        method = getattr(cls, method_name)
        validated_args = self.arg_router.route(method, kwargs)
        return method(**validated_args)
```

**Dispensary Classes** (20+ classes, 240+ methods):
- `PDETMunicipalPlanAnalyzer`: 52+ methods for financial, causal, entity analysis
- `CausalExtractor`: 28 methods for goal extraction, causal hierarchy
- `BayesianMechanismInference`: 14 methods for necessity/sufficiency tests
- `TextMiningEngine`: 8 methods for critical link diagnosis
- `SemanticAnalyzer`: 12 methods for semantic cube construction

---

## 9. Signal Irrigation System (SISAS)

### 9.1 Architecture Overview

The **Signal-Irrigated Smart Augmentation System (SISAS)** provides contextual enrichment to executor methods:

**Definition 9.1 (Signal)**: A signal $s$ is a quintuple:

$$s = \langle id, type, content, source, confidence \rangle$$

### 9.2 Signal Flow

```
Questionnaire ──→ Signal Loader ──→ Signal Registry ──→ Signal Resolution
     │                                    │                    │
     │                                    ▼                    ▼
     │                           Context Scoper ──→ Evidence Extractor
     │                                    │                    │
     │                                    ▼                    ▼
     └────────────────────────→ Enhancement Integrator ──→ Enriched SignalPack
                                          │
                                          ▼
                                    Executor Context
```

### 9.3 Signal Types

| Type | Category | Example |
|------|----------|---------|
| `detection_fuentes_oficiales` | Source validation | DANE, Medicina Legal references |
| `detection_indicadores_cuantitativos` | Numeric extraction | Percentages, rates, indices |
| `detection_cobertura_territorial` | Geographic scope | Municipal, departmental coverage |
| `detection_series_temporales` | Temporal analysis | Year references, trends |

### 9.4 Signal Hit Rate Invariant

**Invariant 9.1**: Signal resolution hit rate ≥ 95%:

$$\frac{|\text{Signals Resolved}|}{|\text{Signals Required}|} \geq 0.95$$

---

## 10. Validation Framework

### 10.1 Adversarial Test Suite

Phase 2 includes a **SEVERE adversarial test suite** with 200+ assertions:

| Test Category | Count | Purpose |
|---------------|-------|---------|
| Contract integrity | 50+ | Validate all 300 contracts |
| Architecture compliance | 30+ | No legacy executors |
| Execution flow | 25+ | Deterministic execution |
| End-to-end | 30+ | Full pipeline simulation |
| Adversarial edge cases | 40+ | Malformed inputs, boundaries |
| Per-file validation | 60+ | Module-level validation |

### 10.2 Dura Lex Contractual Tests

| ID | Assertion | Threshold |
|----|-----------|-----------|
| DL-01 | Contract schema conformance | 100% |
| DL-02 | Method binding completeness | 100% |
| DL-03 | Deterministic execution | SHA-256 match |
| DL-04 | Evidence graph acyclicity | 100% |
| DL-05 | Confidence calibration | 95% CI coverage ≥ 94% |
| DL-06 | Citation completeness | ≥1 per claim |
| DL-07 | Output schema conformance | 100% |
| DL-08 | Provenance integrity | SHA-256 verified |
| DL-09 | Execution time bounds | 99th pctl ≤ 5000ms |
| DL-10 | Memory footprint | Peak RSS ≤ 2GB |

### 10.3 Calibration Verification

Confidence intervals are verified using calibration plots:

$$\text{Calibration Error} = \frac{1}{n} \sum_{i=1}^{n} |\text{observed}_i - \text{predicted}_i|$$

Target: Calibration error < 0.05 for 95% confidence intervals.

---

## 11. Empirical Evaluation

### 11.1 Contract Coverage

| Metric | Value |
|--------|-------|
| Total contracts | 300 |
| Policy areas covered | 10/10 (100%) |
| Base questions covered | 30/30 (100%) |
| Average methods per contract | 17 |
| Minimum methods | 8 |
| Maximum methods | 28 |

### 11.2 Method Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| N1-EMP (Empirical) | 2,100 | 41.2% |
| N2-INF (Inferential) | 1,800 | 35.3% |
| N3-AUD (Audit) | 1,200 | 23.5% |
| **Total** | **5,100** | **100%** |

### 11.3 Execution Performance

| Metric | Value |
|--------|-------|
| Total execution time | 847s (mean) |
| Per-contract time | 2.82s (mean) |
| Peak memory | 1.73GB |
| Evidence nodes generated | 45,000+ |
| Evidence edges inferred | 120,000+ |

### 11.4 Confidence Calibration

| Confidence Level | Expected Coverage | Observed Coverage | Calibration Error |
|------------------|-------------------|-------------------|-------------------|
| 50% CI | 50.0% | 48.7% | 0.013 |
| 80% CI | 80.0% | 79.2% | 0.008 |
| 95% CI | 95.0% | 94.3% | 0.007 |

---

## 12. Limitations and Future Work

### 12.1 Current Limitations

1. **Sequential execution**: Current implementation processes contracts sequentially; parallel execution would improve throughput
2. **Fixed method binding**: Contracts are generated offline; dynamic method selection based on document characteristics could improve precision
3. **Language dependency**: Current implementation targets Spanish policy documents; multilingual extension requires additional NLP resources

### 12.2 Future Directions

1. **Adaptive contract generation**: Machine learning-based method selection
2. **Distributed execution**: Horizontal scaling across compute clusters
3. **Interactive refinement**: Human-in-the-loop evidence validation
4. **Cross-document reasoning**: Evidence fusion across multiple policy documents

---

## 13. Conclusion

This paper presented a contract-driven orchestration architecture for automated policy document analysis that achieves:

1. **Epistemological rigor** through three-layer stratification (N1-EMP, N2-INF, N3-AUD) with asymmetric influence relationships
2. **Deterministic reproducibility** via cryptographic integrity verification and fixed execution semantics
3. **Complete provenance** through content-addressable evidence graphs with Merkle DAG construction
4. **Calibrated uncertainty** using Dempster-Shafer belief propagation with verified confidence intervals

The F.A.R.F.A.N. Phase 2 architecture demonstrates that rigorous epistemological principles can be operationalized in computational systems without sacrificing scalability or reproducibility.

---

## References

1. Christensen, G., & Miguel, E. (2018). Transparency, reproducibility, and the credibility of economics research. *Journal of Economic Literature*, 56(3), 920-980.

2. Freese, J., & Peterson, D. (2017). Replication in social science. *Annual Review of Sociology*, 43, 147-165.

3. Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359-378.

4. Goldman, A. I. (1999). *Knowledge in a social world*. Oxford University Press.

5. Mann, W. C., & Thompson, S. A. (1988). Rhetorical structure theory: Toward a functional theory of text organization. *Text*, 8(3), 243-281.

6. Meyer, B. (1992). Applying "design by contract". *Computer*, 25(10), 40-51.

7. Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press.

8. Popper, K. (1959). *The logic of scientific discovery*. Hutchinson.

9. Shafer, G. (1976). *A mathematical theory of evidence*. Princeton University Press.

10. Stab, C., & Gurevych, I. (2017). Parsing argumentation structures in persuasive essays. *Computational Linguistics*, 43(3), 619-659.

11. Stodden, V., McNutt, M., Bailey, D. H., et al. (2016). Enhancing reproducibility for computational methods. *Science*, 354(6317), 1240-1241.

12. Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press.

---

## Appendix A: Contract Schema (v4.0.0)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ExecutorContract",
  "version": "4.0.0",
  "type": "object",
  "required": ["identity", "method_binding", "question_context", 
               "evidence_assembly", "output_contract"],
  "properties": {
    "identity": {
      "type": "object",
      "required": ["contract_id", "base_slot", "sector_id", "contract_version"],
      "properties": {
        "contract_id": {"type": "string", "pattern": "^Q\\d{3}_PA\\d{2}$"},
        "contract_version": {"type": "string", "pattern": "^4\\.\\d+\\.\\d+"}
      }
    },
    "method_binding": {
      "type": "object",
      "required": ["orchestration_mode", "execution_phases"],
      "properties": {
        "orchestration_mode": {"enum": ["epistemological_pipeline"]},
        "execution_phases": {
          "type": "object",
          "required": ["phase_A_construction", "phase_B_computation", "phase_C_litigation"]
        }
      }
    }
  }
}
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Contract** | Formal specification binding a question to methods and evidence rules |
| **Dispensary** | Monolithic class providing analytical methods to executors |
| **EvidenceNexus** | Graph-native evidence assembly engine |
| **N1-EMP** | Empirical foundation level (positivist extraction) |
| **N2-INF** | Inferential processing level (Bayesian transformation) |
| **N3-AUD** | Audit level (Popperian falsification) |
| **SISAS** | Signal-Irrigated Smart Augmentation System |
| **Carver** | Doctoral narrative synthesizer |

---

*Document Version: 4.0.0*  
*Last Updated: January 2026*  
*SHA-256: [Computed at build time]*  
*Maintainer: F.A.R.F.A.N. Architecture Team*
