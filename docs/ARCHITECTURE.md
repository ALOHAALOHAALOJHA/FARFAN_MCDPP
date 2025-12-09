# F.A.R.F.A.N Architecture Overview

**Framework for Advanced Retrieval of Administrative Narratives**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Hierarchy](#component-hierarchy)
3. [8-Layer Quality Architecture](#8-layer-quality-architecture)
4. [Pipeline Phases](#pipeline-phases)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Design Principles](#design-principles)

---

## System Overview

F.A.R.F.A.N is a deterministic, mechanistic policy analysis pipeline designed for rigorous evaluation of Colombian territorial development plans (Planes de Desarrollo Territorial - PDT). The system analyzes policy documents through 300 evaluation questions across 6 dimensions and 10 policy areas, producing evidence-based assessments with complete traceability.

### Key Capabilities

- **584 Analytical Methods** distributed across 7 specialized producers + 1 aggregator
- **11-Phase Deterministic Pipeline** with zero-tolerance validation (Phase 0 gate)
- **Complete Provenance Tracking** (`provenance_completeness = 1.0`)
- **8-Layer Quality System** with Choquet integral fusion
- **SIN_CARRETA Determinism** (absolute separation of calibration/parametrization)
- **Cross-cutting Signal System** (SISAS) for transversal data irrigation

### Analysis Scope

- **Dimensions (D1-D6)**: Insumos, Actividades, Productos, Resultados, Impactos, Causalidad
- **Policy Areas (PA01-PA10)**: Gender equality, violence prevention, environment, economic/social/cultural rights, victims' rights, youth protection, land/territory, human rights defenders, prison rights, migration
- **Question Count**: 300 micro-questions (5 per dimension × 6 dimensions × 10 policy areas)
- **Aggregation Levels**: MICRO (atomic 150-300 word responses) → MESO (cluster analysis) → MACRO (holistic classification)

---

## Component Hierarchy

```
F.A.R.F.A.N/
│
├── Phase 0: Bootstrap & Validation
│   ├── Runtime Configuration
│   ├── Seed Registry (Deterministic RNG)
│   ├── Input Verification (SHA-256 hashing)
│   └── Boot Checks (Zero-tolerance gate)
│
├── Phase 1: Document Ingestion & Structural Parsing
│   ├── PDF Extraction
│   ├── Structural Analysis (CPP - Chunk Processing Pipeline)
│   ├── PDT Structure Validation (S/M/I/P components)
│   └── Semantic Chunking
│
├── Phase 2: Method Execution (30 D×Q Executors)
│   ├── Executor Pool (D1-D6 × Q1-Q5 = 30 executors)
│   ├── Evidence Assembly
│   ├── SISAS Signal Consumption
│   └── Contract Validation
│
├── Phase 3: Quality Scoring & Layer Evaluation
│   ├── Intrinsic Quality (@b: b_theory, b_impl, b_deploy)
│   ├── Unit Quality (@u: S/M/I/P structural analysis)
│   ├── Contextual Compatibility (@q/@d/@p)
│   ├── Congruence (@C: c_scale, c_sem, c_fusion)
│   ├── Chain Integrity (@chain: discrete scoring)
│   └── Governance (@m: m_transp, m_gov, m_cost)
│
├── Phase 4-7: Hierarchical Aggregation
│   ├── Phase 4: Dimension Aggregation (5 questions → 1 dimension)
│   ├── Phase 5: Policy Area Aggregation (6 dimensions → 1 area)
│   ├── Phase 6: Cluster Aggregation (areas → clusters)
│   └── Phase 7: Macro Evaluation (holistic assessment)
│
├── Phase 8: Recommendation Generation
│   ├── Strategic Recommendations
│   ├── Gap Analysis
│   └── Priority Mapping
│
├── Phase 9: Report Assembly
│   ├── MICRO Reports (per question)
│   ├── MESO Reports (per cluster)
│   ├── MACRO Report (holistic)
│   └── Verification Manifest (HMAC-SHA256)
│
└── Phase 10: Artifact Finalization & Audit Trail
    ├── Verification Manifest Generation
    ├── Certificate Issuance
    └── Integrity Signatures (HMAC)
```

---

## 8-Layer Quality Architecture

The F.A.R.F.A.N system evaluates methods and results through 8 independent quality layers, fused using a Choquet integral to capture synergies and interactions between layers.

### Layer Overview

| Layer | Symbol | Focus | Formula Components |
|-------|--------|-------|-------------------|
| **Intrinsic Quality** | `@b` | Base method quality | `b_theory`, `b_impl`, `b_deploy` |
| **Unit Quality** | `@u` | Document structure | `S` (Structure), `M` (Mandatory), `I` (Indicators), `P` (PPI) |
| **Question Appropriateness** | `@q` | Question-method fit | Semantic alignment, priority mapping |
| **Dimension Alignment** | `@d` | Dimension compatibility | D1-D6 relevance scoring |
| **Policy Area Fit** | `@p` | Policy area matching | PA01-PA10 coverage analysis |
| **Contract Compliance** | `@C` | Formal correctness | `c_scale`, `c_sem`, `c_fusion` |
| **Chain Integrity** | `@chain` | Data flow validity | Discrete scoring, dependency validation |
| **Governance Maturity** | `@m` | Institutional quality | `m_transp`, `m_gov`, `m_cost` |

### Layer Requirements by Role

```python
LAYER_REQUIREMENTS = {
    "ingest": ["@b", "@chain", "@u", "@m"],                          # 4 layers
    "processor": ["@b", "@chain", "@u", "@m"],                       # 4 layers
    "analyzer": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"], # 8 layers (ALL)
    "executor": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"], # 8 layers (ALL)
    "utility": ["@b", "@chain", "@m"],                               # 3 layers
    "orchestrator": ["@b", "@chain", "@m"],                          # 3 layers
}
```

See [LAYER_SYSTEM.md](./LAYER_SYSTEM.md) for detailed explanations.

---

## Pipeline Phases

### Phase 0: Bootstrap & Validation Gate

**Zero-tolerance validation before execution begins.**

- Verify input files exist and compute SHA-256 hashes
- Initialize deterministic seed registry
- Load and validate questionnaire monolith
- Enforce boot checks (calibration files, executor count, etc.)
- **Gate Condition**: `self.errors == []` (atomic failure on ANY error)

### Phase 1: Document Ingestion

**CPP (Chunk Processing Pipeline) - Structural parsing**

- Extract text from PDF using PyMuPDF
- Parse structural components (Diagnóstico, Estratégica, PPI, Seguimiento)
- Validate PDT structure using `@u` layer (S/M/I/P analysis)
- Semantic chunking with sentence-transformers
- Generate structural metadata

**Outputs**: `PreprocessedDocument`, chunk embeddings, structural scores

### Phase 2: Method Execution

**30 Executor Matrix (D1-D6 × Q1-Q5)**

Each executor:
1. Receives `PreprocessedDocument` + SISAS signals
2. Consumes relevant evidence via argument routing
3. Applies analytical method (Bayesian inference, causal tracing, etc.)
4. Validates output contract
5. Returns `ExecutorResult` with evidence provenance

**Key Executors**:
- `D1_Q1_DiagnosticQuality`: Baseline analysis
- `D2_Q3_ActivityDesign`: Intervention design
- `D6_Q5_TheoryOfChange`: Causal mechanism evaluation

### Phase 3: Quality Scoring

Each executor result is scored across 8 layers:

```python
# Example: Executor X
layers = {
    "@b": 0.85,      # Intrinsic quality
    "@chain": 0.92,  # Chain integrity
    "@q": 0.78,      # Question appropriateness
    "@d": 0.88,      # Dimension alignment
    "@p": 0.81,      # Policy area fit
    "@C": 0.94,      # Contract compliance
    "@u": 0.76,      # Unit quality
    "@m": 0.89       # Governance maturity
}
```

Final score computed via Choquet integral (see [FUSION_FORMULA.md](./FUSION_FORMULA.md)).

### Phase 4-7: Hierarchical Aggregation

```
Phase 4: Dimension Aggregation
  Input: 5 question scores (Q1-Q5)
  Output: 1 dimension score (D1-D6)
  Method: Weighted average with uncertainty quantification

Phase 5: Policy Area Aggregation
  Input: 6 dimension scores (D1-D6)
  Output: 1 policy area score (PA01-PA10)
  Method: Choquet integral (non-linear synergies)

Phase 6: Cluster Aggregation
  Input: Multiple policy area scores
  Output: 1 cluster score (CL01-CL04)
  Method: Bootstrap aggregation with provenance DAG

Phase 7: Macro Evaluation
  Input: All cluster scores
  Output: Holistic quality band (EXCELENTE/BUENO/ACEPTABLE/DEFICIENTE)
  Method: Multi-criteria decision analysis
```

### Phase 8: Recommendation Generation

Strategic recommendations based on:
- Gap analysis (missing components)
- Quality thresholds (hard gates at 0.3, 0.5, 0.7)
- Comparative performance (relative to cohort)
- Causal mechanisms (Theory of Change analysis)

### Phase 9: Report Assembly

Generate three report levels:
1. **MICRO**: 300 atomic responses (150-300 words each)
2. **MESO**: Cluster summaries with dimension analysis
3. **MACRO**: Holistic assessment with recommendations

All reports include:
- Evidence provenance (source documents, page numbers)
- Uncertainty metrics (confidence intervals)
- Quality scores (per layer)
- Strategic gaps and recommendations

### Phase 10: Artifact Finalization

Generate verification manifest:
```json
{
  "version": "1.0",
  "timestamp_utc": "2024-12-16T10:30:00Z",
  "execution_hash": "sha256:abc123...",
  "calibration_hash": "sha256:def456...",
  "integrity_hmac": "hmac-sha256:789...",
  "phases_completed": 11,
  "phases_failed": 0,
  "artifacts": {
    "micro_report.json": "sha256:...",
    "meso_report.json": "sha256:...",
    "macro_report.json": "sha256:..."
  }
}
```

---

## Data Flow

### End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT: PDT (PDF) + Questionnaire Monolith (JSON)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 0: Validation Gate (SHA-256 hashing, seed init)         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: CPP Pipeline (structural parsing, chunking)          │
│  → PreprocessedDocument (text, chunks, PDT structure)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: Executor Matrix (30 D×Q executors)                   │
│  → 300 ExecutorResults (1 per micro-question)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: Layer Scoring (8-layer evaluation)                   │
│  → 300 ScoredResults (with layer breakdowns)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4-7: Hierarchical Aggregation                           │
│  → 60 DimensionScores → 10 AreaScores → 4 ClusterScores       │
│  → 1 MacroScore                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 8: Recommendation Engine                                │
│  → Strategic recommendations + gap analysis                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 9: Report Assembly                                       │
│  → MICRO (300 atomic) + MESO (4 clusters) + MACRO (holistic)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 10: Finalization + Verification Manifest                │
│  → HMAC-SHA256 integrity signatures                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT: Reports + Artifacts + Verification Manifest            │
└─────────────────────────────────────────────────────────────────┘
```

### Signal Irrigation (SISAS)

Cross-cutting signals flow transversally through the pipeline:

```
SISAS Registry
     ↓
Assembly Signals ───→ Phase 2 Executors (evidence injection)
     ↓
Semantic Expansion ─→ Phase 3 Scoring (context enrichment)
     ↓
Quality Metrics ────→ Phase 4-7 Aggregation (weight adjustment)
```

Signals are immutable, content-addressed (BLAKE3 hashing), and version-tracked.

---

## Technology Stack

### Core

- **Language**: Python 3.12
- **API Framework**: FastAPI (REST + WebSocket)
- **Validation**: Pydantic v2 (strict mode)
- **Type Checking**: mypy (strict), Pyright (strict)

### Analysis

- **NLP**: sentence-transformers, spaCy, transformers
- **Bayesian Inference**: PyMC
- **Machine Learning**: scikit-learn
- **Network Analysis**: NetworkX
- **Numerical**: NumPy, SciPy

### Quality Assurance

- **Testing**: pytest (305 tests, 30 executor-specific)
- **Linting**: ruff (100-char line length)
- **Formatting**: black
- **Contracts**: TypedDict boundaries, runtime validation

### Infrastructure

- **Document Processing**: PyMuPDF, pdfplumber
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Hashing**: SHA-256 (file integrity), BLAKE3 (signals), HMAC (verification)
- **Serialization**: JSON (canonical, sorted keys)

---

## Design Principles

### 1. Deterministic Execution (SIN_CARRETA)

**Absolute separation of calibration and parametrization.**

- All stochastic operations use deterministic seeds (SHA-256 derivation)
- Calibration data is immutable and content-addressed
- Execution parameters are traceable and versioned
- Full reproducibility: same inputs → same outputs (bit-identical)

### 2. Contract-Based Architecture

**Explicit input/output contracts at all boundaries.**

- TypedDict schemas for all data structures
- Runtime validation using Pydantic v2
- Contract verification tools (verify_contracts.py)
- Hard failures on contract violations

### 3. Provenance Completeness

**Every output traces back to source evidence.**

- Evidence provenance: document → chunk → sentence → word
- Method provenance: executor → method → calibration → parameters
- Aggregation provenance: DAG tracking all dependencies
- Audit trail: complete execution history with timestamps

### 4. Zero-Tolerance Validation

**Phase 0 gate enforces strict preconditions.**

- SHA-256 hashing of all inputs
- Boot checks: file existence, executor count, calibration integrity
- Seed registry initialization (deterministic RNG)
- Atomic failure: ANY error aborts execution

### 5. Layered Quality Evaluation

**8 independent layers fused via Choquet integral.**

- Captures synergies between quality dimensions
- Non-linear aggregation (interaction terms)
- Normalization constraints (weights sum to 1.0)
- Calibrated per method role (see LAYER_REQUIREMENTS)

### 6. Signal-Driven Irrigation

**Cross-cutting signals provide transversal context.**

- SISAS (Signal Irrigation System for Analytical Structuring)
- Content-addressed with BLAKE3 hashing
- Transport: memory:// (in-process) and HTTP (distributed)
- Immutable, versioned, traceable

### 7. Hierarchical Aggregation

**Bottom-up synthesis with uncertainty quantification.**

- Bootstrap aggregation for confidence intervals
- Provenance DAG tracking dependencies
- SHAP-like attribution (kernel approximation)
- Multiple aggregation methods (weighted, Choquet, holistic)

### 8. Fail-Safe Design

**Graceful degradation with explicit fallbacks.**

- Hard thresholds (0.3, 0.5, 0.7) trigger fallback patterns
- Abortability at every phase
- Resource-aware execution (memory, timeout monitoring)
- Structured error propagation with event IDs

---

## Related Documentation

- [LAYER_SYSTEM.md](./LAYER_SYSTEM.md) - Detailed explanation of 8-layer quality system
- [FUSION_FORMULA.md](./FUSION_FORMULA.md) - Choquet integral mathematics
- [DETERMINISM.md](./DETERMINISM.md) - SIN_CARRETA doctrine and implementation
- [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md) - Configuration file schemas
- [API.md](./API.md) - API documentation (generated from docstrings)

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit
