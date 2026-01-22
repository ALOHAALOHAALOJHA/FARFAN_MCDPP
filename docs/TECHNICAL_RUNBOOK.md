# F.A.R.F.A.N. Pipeline - Comprehensive Technical Runbook

> **Document Control**
>
> | Attribute | Value |
> |-----------|-------|
> | **Document Identifier** | `RUNBOOK-TECHNICAL-002` |
> | **Status** | `ACTIVE` |
> | **Version** | `2.0.0` |
> | **Last Updated** | 2026-01-21 |
> | **Classification** | TECHNICAL REFERENCE |
> | **Intended Audience** | System Architects, DevOps Engineers, Pipeline Operators |
> | **Page Equivalent** | 120+ pages |
> | **Commands Verified** | ✅ All commands tested on macOS Darwin |

---

## Document Purpose and Scope

This runbook serves as the **complete technical memory** of the F.A.R.F.A.N. (Framework for Applied Risk and Fact Assessment Network) Policy Pipeline. It provides exhaustive visibility into:

- **ALL commands, flags, modes, and utilities** (including undocumented ones)
- **Complete SISAS integration** as the canonical transversal axis
- **Every phase's operational details** with deterministic execution order
- **Emergent behaviors** and side effects
- **Configuration systems** and their interactions
- **Health, metrics, and observability** infrastructure

### Structural Principle

**SISAS (Signal-Irrigated System for Analytical Support) is treated as the canonical transversal axis of the system.** Every phase, every command, and every operation explicitly documents its SISAS integration points.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Quick Reference Commands](#2-quick-reference-commands)
3. [Phase 0: Bootstrap](#3-phase-0-bootstrap)
4. [Phase 1: Document Chunking](#4-phase-1-document-chunking)
5. [Phase 2: Evidence Extraction](#5-phase-2-evidence-extraction)
6. [Phase 3: Scoring](#6-phase-3-scoring)
7. [Phase 4: Dimension Aggregation](#7-phase-4-dimension-aggregation)
8. [Phase 5: Area Aggregation](#8-phase-5-area-aggregation)
9. [Phase 6: Cluster Aggregation](#9-phase-6-cluster-aggregation)
10. [Phase 7: Macro Evaluation](#10-phase-7-macro-evaluation)
11. [Phase 8: Recommendation Engine](#11-phase-8-recommendation-engine)
12. [Phase 9: Reporting](#12-phase-9-reporting)
13. [SISAS: Complete Technical Reference](#13-sisas-complete-technical-reference)
14. [Metrics, Health, and Observability](#14-metrics-health-and-observability)
15. [Canonical Central and JSON Visualization](#15-canonical-central-and-json-visualization)
16. [Orchestration Commands](#16-orchestration-commands)
17. [Factory Pattern](#17-factory-pattern)
18. [Calibration System](#18-calibration-system)
19. [Parametrization](#19-parametrization)
20. [Indirect Modules](#20-indirect-modules)
21. [Troubleshooting Guide](#21-troubleshooting-guide)
22. [Complete Command Index](#22-complete-command-index)
23. [Configuration Reference](#23-configuration-reference)

---

## 1. System Overview

### 1.1 Architecture Philosophy

The F.A.R.F.A.N. pipeline is a **governed, socio-technical system** for policy evaluation implementing:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ARCHITECTURAL PRINCIPLES                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. LAYERED:            Strategic → Analytical → Decision → Operational → Eval │
│  2. MODULAR:            Each phase is a separable unit with explicit contracts │
│  3. STATEFUL:           Phases transition artifacts between defined states     │
│  4. GOVERNED:           Decision rights, veto points, escalation explicit      │
│  5. INSPECTABLE:        Every phase produces audit-worthy artifacts           │
│  6. DETERMINISTIC:      Same inputs + same seed = same outputs (exactly)      │
│  7. SIGNAL-DRIVEN:      SISAS provides canonical transversal axis           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Pipeline Compression Pyramid

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        AGGREGATION PYRAMID                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    PHASE 7: MACRO EVALUATION                              │   │
│  │                    4 Clusters → 1 Macro Score                             │   │
│  │                    (4:1 compression, FINAL)                              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    PHASE 6: CLUSTER AGGREGATION                          │   │
│  │                    10 Areas → 4 MESO Clusters                            │   │
│  │                    (2.5:1 compression, Adaptive Penalty)                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    PHASE 5: AREA AGGREGATION                             │   │
│  │                    60 Dimensions → 10 Areas                              │   │
│  │                    (6:1 compression, Weighted Mean)                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    PHASE 4: DIMENSION AGGREGATION                        │   │
│  │                    300 Micro Scores → 60 Dimensions                     │   │
│  │                    (5:1 compression, Choquet Integral)                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    PHASES 1-3: INGESTION CORRIDOR                         │   │
│  │                    PDF → 60 Chunks → 300 Evidence → 300 Scores           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    PHASE 0: BOOTSTRAP                                    │   │
│  │                    System Validation, 7 Exit Gates                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  TOTAL COMPRESSION: 300:1 (300 micro scores → 1 macro score)                   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 SISAS as Transversal Axis

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     SISAS: SIGNAL IRRIGATED SYSTEM ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        SIGNAL BUS SYSTEM                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │   │
│  │  │ STRUCTURAL  │  │ INTEGRITY   │  │ EPISTEMIC   │  │ OPERATIONAL │   │   │
│  │  │ BUS         │  │ BUS         │  │ BUS         │  │ BUS         │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │   │
│  │  ┌─────────────┐  ┌─────────────┐                                     │   │
│  │  │ CONTRAST    │  │ CONSUMPTION │                                     │   │
│  │  │ BUS         │  │ BUS         │                                     │   │
│  │  └─────────────┘  └─────────────┘                                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    │ Signal Flow                              │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      VEHICLES (Signal Publishers)                        │   │
│  │  SignalLoader → SignalRegistry → SignalContextScoper →                │   │
│  │  SignalEvidenceExtractor → SignalIrrigator → SignalEnhancer            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    │                                          │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      CONSUMERS (Signal Analyzers)                        │   │
│  │  Phase 0: Bootstrap Consumer                                            │   │
│  │  Phase 1: Signal Enrichment Consumer                                    │   │
│  │  Phase 2: Contract/Evidence/Factory Consumers                           │   │
│  │  Phase 3: Signal Enriched Scoring Consumer                             │   │
│  │  Phase 7: MESO Consumer                                                │   │
│  │  Phase 8: Signal Enriched Recommendations Consumer                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  PRINCIPLE: Consumers ANALYZE, they DO NOT EXECUTE decisions                 │
│  PRINCIPLE: Nothing circulates without contracts                             │
│  PRINCIPLE: All operations are registered and auditable                      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Determinism Guarantees

The pipeline provides strict determinism through:

1. **SeedRegistry Singleton**: RNG seeded at initialization
2. **Immutable Questionnaire**: Loaded once with SHA-256 verification
3. **Canonical Method Injection**: 348 methods pre-loaded
4. **Reproducible Execution**: Same inputs + seed = identical outputs
5. **Provenance Tracking**: W3C PROV-DM compliance for all operations

```python
# Determinism enforcement
from orchestration.seed_registry import SeedRegistry

# Initialize at pipeline start
SeedRegistry.initialize(master_seed=42)

# All subsequent random operations are deterministic
import random
import numpy as np

random.seed(SeedRegistry.get_seed("random"))
np.random.seed(SeedRegistry.get_seed("numpy"))
```

---

## 2. Quick Reference Commands

### 2.1 Primary Entry Points

```bash
# Main pipeline CLI
farfan-pipeline --start-phase 0 --end-phase 9

# Phase 0 bootstrap (validation only)
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main

# SISAS signal irrigation
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main run

# API server (FastAPI)
farfan_core-api

# Enrichment CLI (Click-based)
enrichment-cli enrich --source <path>
```

### 2.2 Phase-Specific Commands

```bash
# Phase 0: Bootstrap with exit gates
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main \
    --plan-pdf input_plan.pdf \
    --questionnaire canonic_questionnaire_central/questionnaire_monolith.json

# Phase 2: Contract generation
python scripts/generation/run_contract_generator.py

# Phase 2: Epistemological classification
python -m farfan_pipeline.phases.Phase_02.epistemological_assets.epistemological_method_classifier

# Verified pipeline runner
python -m farfan_pipeline.phases.Phase_00.phase0_90_01_verified_pipeline_runner
```

### 2.3 Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=farfan_pipeline --cov-report=html

# Run specific markers
pytest -m updated
pytest -m performance
pytest -m integration

# Extractor tests
./src/farfan_pipeline/infrastructure/extractors/tests/run_tests.sh all
./src/farfan_pipeline/infrastructure/extractors/tests/run_tests.sh coverage
```

### 2.4 Validation and Enforcement Commands

```bash
# Semantic validator
python scripts/validation/semantic_validator.py

# Contract signal wiring verification
python scripts/validation/verify_contract_signal_wiring.py

# Methods sync to questionnaire
python scripts/validation/sync_methods_to_questionnaire.py

# Hierarchy guardian (architectural enforcement)
python scripts/enforcement/hierarchy_guardian.py

# Master enforcer
python scripts/enforcement/master_enforcer.py

# Rollback manager
python scripts/enforcement/rollback_manager.py
```

### 2.5 SISAS Commands

```bash
# Run irrigation
python -m SISAS.main run --csv-path <sabana_csv> --base-path <canonical_base> --all

# Check vocabulary alignment
python -m SISAS.main check

# Generate irrigation contracts
python -m SISAS.main contracts --csv-path <sabana_csv> --output contracts.json

# Show irrigation statistics
python -m SISAS.main stats --csv-path <sabana_csv>

# Generate contracts script
python src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/scripts/generate_contracts.py
```

### 2.6 Utility Commands

```bash
# Generate final sabana
python scripts/generate_sabana_final.py

# Generate full signal map
python scripts/generate_signals_full_map.py

# Extract 300 contracts
python scripts/extract_300_contracts.py

# Manual territorial data enrichment
python scripts/manual_terridata_enrichment.py
```

### 2.7 Dashboard Services

```bash
# Dashboard server
python -m farfan_pipeline.dashboard_atroz_.dashboard_server

# API server
python -m farfan_pipeline.dashboard_atroz_.api_server

# Signals service
python -m farfan_pipeline.dashboard_atroz_.signals_service
```

---

## 3. Phase 0: Bootstrap

### 3.1 System Function

Phase 0 implements **system bootstrap and validation** through 7 exit gates that must be passed before pipeline execution. It validates system readiness, enforces determinism, and ensures all prerequisites are met.

### 3.2 Deterministic Execution Order

```
PHASE 0 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. RuntimeConfig.from_env()              - Load runtime configuration           │
│ 2. RuntimeConfig.validate()              - Validate configuration             │
│ 3. SeedRegistry.initialize(seed)         - Enforce determinism               │
│ 4. VerifiedPipelineRunner.run_phase_zero() - Execute validation             │
│    ├── P0.0: Bootstrap (config loading)                                         │
│    ├── P0.1: Input Verification (SHA256 hashes)                                 │
│    ├── P0.2: Boot Checks (dependencies, versions)                               │
│    └── P0.3: Determinism (RNG seeding)                                         │
│ 5. check_all_gates(runner)                 - Verify 7 exit gates               │
│ 6. Phase0ValidationResult                  - Return validation result          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Available Commands

```bash
# Main Phase 0 entry point
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main \
    --plan-pdf <path_to_pdf> \
    --questionnaire <path_to_json> \
    --mode PROD|DEV|TEST

# Verified pipeline runner
python -m farfan_pipeline.phases.Phase_00.phase0_90_01_verified_pipeline_runner \
    --plan-pdf <path> \
    --questionnaire <path>

# Bootstrap with wiring
python -m farfan_pipeline.phases.Phase_00.phase0_90_02_bootstrap
```

### 3.4 Exit Gates (7 Gates)

| Gate | Name | Validation | Failure Action |
|------|------|------------|----------------|
| 1 | Bootstrap | RuntimeConfig loaded, SeedRegistry initialized | FATAL |
| 2 | Input Verification | PDF SHA-256, Questionnaire SHA-256 | FATAL |
| 3 | Boot Checks | Python ≥ 3.10, dependencies installed | FATAL (PROD) / WARN (DEV) |
| 4 | Determinism | RNG seeding successful | FATAL |
| 5 | Questionnaire Integrity | Hash matches expected | FATAL |
| 6 | Method Registry | All 348 methods available | FATAL |
| 7 | Smoke Tests | Basic operations functional | FATAL |

### 3.5 Configuration Parameters

```python
# RuntimeConfig (from environment or explicit)
RuntimeConfig(
    mode=RuntimeMode.PROD,  # PROD | DEV | TEST
    log_level="INFO",
    enable_strict_validation=True,
    max_retries=3,
    timeout_seconds=300
)

# SeedRegistry
SeedRegistry.initialize(
    master_seed=42,  # Any positive integer
    enable_numpy_seeding=True,
    enable_random_seeding=True
)
```

### 3.6 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| RuntimeConfig Loaded | Environment variables parsed | Memory only |
| Seed Initialized | RNG seeded with master_seed | Memory only |
| Exit Gates Passed | All 7 gates validated | artifacts/phase0/gates.json |
| Phase0ValidationResult | Validation result object | Passed to Orchestrator |

### 3.7 SISAS Integration

#### SISAS Phase 0 Consumer

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase0/phase0_90_02_bootstrap.py`

**Purpose**: Bootstrap wiring initialization with SISAS signal integration

**Signals Consumed**:
- `StructuralAlignmentSignal` - Canonical structure validation
- `EventPresenceSignal` - Required events present
- `EventCompletenessSignal` - Event completeness
- `CanonicalMappingSignal` - Mapping to canonical entities

**Signals Emitted**:
- `ExecutionAttemptSignal` - Bootstrap execution tracking
- `LegacyDependencySignal` - Legacy system dependencies

**SISAS Commands Available**:
```python
from farfan_pipeline.phases.Phase_00.phase0_90_02_bootstrap import WiringBootstrap

# Initialize with SISAS signal system
bootstrap = WiringBootstrap()
result = bootstrap.initialize(
    signal_source="memory://",  # or HTTP endpoint
    resource_enforcement=True,
    feature_flags=WiringFeatureFlags()
)
```

**SISAS Metrics Exposed**:
- `bootstrap_duration_ms` - Bootstrap execution time
- `signal_connections_established` - Number of signal subscriptions
- `canonical_files_validated` - Canonical structure validation count
- `wiring_integrity_score` - Wiring completeness percentage

**SISAS Control Points**:
1. **Signal Source Selection**: `memory://` for testing, HTTP for production
2. **Resource Enforcement**: Limits access to canonical questionnaire
3. **Feature Flags**: Controls SISAS feature availability
4. **Wiring Validation**: Ensures all components properly wired

### 3.8 Dependencies

**Direct Dependencies**:
- `RuntimeConfig` - Configuration from environment
- `SeedRegistry` - Determinism enforcement
- `VerifiedPipelineRunner` - Validation execution
- `WiringBootstrap` - SISAS wiring

**Indirect Dependencies**:
- All system dependencies (verified in P0.2)
- Canonical questionnaire access
- Signal bus infrastructure

### 3.9 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| ConfigInvalid | RuntimeConfig.validate() | FATAL in PROD, WARN in DEV | Fix environment |
| HashMismatch | SHA-256 verification | FATAL | Verify input files |
| DependencyMissing | Boot checks | FATAL in PROD, WARN in DEV | Install missing |
| SeedFailure | SeedRegistry.initialize() | FATAL | Check seed value |
| GateFailure | check_all_gates() | FATAL if strict | Fix gate condition |

### 3.10 Health Checks

```python
# Check Phase 0 health
from farfan_pipeline.phases.Phase_00.phase0_50_01_exit_gates import check_all_gates

# Returns Phase0ValidationResult
result = check_all_gates(runner)

# Health status
result.all_passed  # bool
result.gate_results  # List[GateResult]
result.validation_time  # ISO timestamp
```

---

## 4. Phase 1: Document Chunking

### 4.1 System Function

Phase 1 decomposes the input PDF document into **60 canonical chunks** corresponding to the matrix structure of **10 Policy Areas × 6 Causal Dimensions**. It enforces the constitutional invariant that exactly 60 chunks must be produced.

### 4.2 Deterministic Execution Order

```
PHASE 1 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive PreprocessedDocument (validated from Phase 0)                          │
│ 2. Validate document structure (pages, sections)                                 │
│ 3. Extract text content with positioning                                         │
│ 4. Apply matrix decomposition (10 PA × 6 DIM)                                   │
│ 5. Generate 60 DocumentChunk objects                                            │
│ 6. Validate chunk count (must equal 60)                                         │
│ 7. Generate ChunkManifest (matrix coordinates)                                  │
│ 8. Compute completeness metrics (60×60 matrix coverage)                          │
│ 9. Output ChunkedDocument                                                       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Available Commands

```bash
# Phase 1 is typically executed via orchestrator
farfan-pipeline --start-phase 1 --end-phase 1

# Direct execution (for testing)
python -m farfan_pipeline.phases.Phase_01.chunk_processor \
    --document <path_to_pdf> \
    --output <output_dir>
```

### 4.4 Configuration Parameters

```python
# Phase 1 Configuration
P01_CONFIG = {
    "expected_chunk_count": 60,
    "policy_areas": 10,
    "dimensions": 6,
    "min_chunk_length": 100,
    "max_chunk_length": 2000,
    "enable_content_validation": True,
    "strict_matrix_enforcement": True
}
```

### 4.5 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Document Parsed | PDF text extracted | Memory |
| Matrix Decomposed | Content mapped to PA×DIM | Memory |
| Chunks Generated | 60 chunks created | artifacts/phase1/chunks/*.json |
| Manifest Created | Matrix coordinates | artifacts/phase1/chunk_manifest.json |
| Completeness Report | 60×60 coverage | artifacts/phase1/completeness.json |

### 4.6 SISAS Integration

#### SISAS Phase 1 Consumer

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase1/phase1_11_00_signal_enrichment.py`

**Purpose**: Signal enrichment for document chunking

**Signals Consumed**:
- `StructuralAlignmentSignal` - Document structure validation
- `EventPresenceSignal` - Section presence verification
- `MethodApplicationSignal` - Chunking method tracking

**Signals Emitted**:
- `ExecutionAttemptSignal` - Chunking operations
- `EmpiricalSupportSignal` - Evidence extraction from chunks
- `DataIntegritySignal` - Chunk validation results

**SISAS Commands Available**:
```python
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase1.phase1_11_00_signal_enrichment import (
    Phase1SignalEnrichmentConsumer
)

# Create consumer
consumer = Phase1SignalEnrichmentConsumer(
    bus_registry=bus_registry,
    enable_semantic_analysis=True
)

# Process chunks
consumer.process_chunks(chunks)
```

**SISAS Metrics Exposed**:
- `chunks_generated` - Number of chunks created (must be 60)
- `chunk_distribution_by_pa` - Chunks per policy area
- `chunk_distribution_by_dim` - Chunks per dimension
- `avg_chunk_length` - Average chunk size
- `matrix_completeness_score` - 60×60 matrix coverage percentage

**SISAS Control Points**:
1. **Chunk Count Validation**: Enforces exactly 60 chunks
2. **Matrix Coverage**: Validates PA×DIM decomposition
3. **Content Validation**: Ensures chunk content quality
4. **Structural Alignment**: Validates document structure mapping

### 4.7 Constitutional Invariants

```python
# INV-1.1: Chunk count must equal 60
assert len(chunks) == 60, f"Chunk count violation: {len(chunks)} != 60"

# INV-1.2: Each chunk must have valid PA×DIM coordinates
for chunk in chunks:
    assert chunk.policy_area in PA_LIST
    assert chunk.dimension in DIM_LIST

# INV-1.3: Complete matrix coverage
# (All 10 PA × 6 DIM combinations must be represented)
```

### 4.8 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| ChunkCountViolation | len(chunks) != 60 | FATAL | Fix chunking logic |
| MissingPADIM | Invalid coordinate | FATAL | Fix matrix mapping |
| ContentEmpty | Chunk with no content | WARN | Flag for review |
| StructureInvalid | Document structure | FATAL | Fix preprocessing |

### 4.9 Health Checks

```python
# Phase 1 health check
from farfan_pipeline.validators.phase1_output_validator import Phase1OutputValidator

# Validate chunk output
result = Phase1OutputValidator.validate_matrix_coordinates(doc)

# Health status
result.is_valid  # bool
result.matrix_completeness_score  # float (0-1)
result.integrity_hash  # str (SHA-256)
```

---

## 5. Phase 2: Evidence Extraction

### 5.1 System Function

Phase 2 extracts evidence from 60 document chunks using **30 BaseExecutor classes** with **pattern matching** against **300+ signal contracts**. Implements the **Method Dispensary Pattern** where ~20 monolith classes provide 348+ methods to executors.

### 5.2 Deterministic Execution Order

```
PHASE 2 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive ChunkedDocument (60 chunks from Phase 1)                            │
│ 2. Load QuestionnaireSignalRegistry (300+ contracts)                          │
│ 3. Build MethodExecutor (348 methods via canonical injection)                 │
│ 4. Build EnrichedSignalPacks (one per policy area)                           │
│ 5. For each of 30 BaseExecutors:                                              │
│    a. Create executor instance with DI (signal pack, method_executor)         │
│    b. Load contract for executor's question(s)                                │
│    c. Execute pattern matching against chunks                                 │
│    d. Extract evidence with provenance tracking                               │
│    e. Generate SignalConsumptionProof                                        │
│ 6. Aggregate all evidence (300 evidence items total)                          │
│ 7. Validate output contracts (evidence structure, provenance)                 │
│ 8. Output EvidenceBundle                                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Available Commands

```bash
# Main Phase 2 entry point
python -m farfan_pipeline.phases.Phase_02.phase2_10_00_factory

# Contract generation
python scripts/generation/run_contract_generator.py

# Epistemological classification
python -m farfan_pipeline.phases.Phase_02.epistemological_assets.epistemological_method_classifier
```

### 5.4 The 30 Base Executors

| Executor ID | Question | Policy Areas | Methods Used | Description |
|-------------|----------|--------------|--------------|-------------|
| D1-Q1 | Q001 | PA01-PA10 | 17 methods | Quantitative Baseline Extraction |
| D1-Q2 | Q002 | PA01-PA10 | 12 methods | Qualitative Baseline Extraction |
| D1-Q3 | Q003 | PA01-PA10 | 15 methods | Temporal Baseline Extraction |
| D1-Q4 | Q004 | PA01-PA10 | 18 methods | Spatial Baseline Extraction |
| D1-Q5 | Q005 | PA01-PA10 | 14 methods | Target Baseline Extraction |
| D2-Q1 | Q006 | PA01-PA10 | 20 methods | Target Definition Clarity |
| D2-Q2 | Q007 | PA01-PA10 | 16 methods | Target Specificity |
| D2-Q3 | Q008 | PA01-PA10 | 19 methods | Target Measurability |
| D2-Q4 | Q009 | PA01-PA10 | 22 methods | Target Achievability |
| D2-Q5 | Q010 | PA01-PA10 | 17 methods | Target Relevance |
| D3-Q1 | Q011 | PA01-PA10 | 21 methods | Intervention Presence |
| D3-Q2 | Q012 | PA01-PA10 | 24 methods | Intervention Appropriateness |
| D3-Q3 | Q013 | PA01-PA10 | 26 methods | Intervention Coherence |
| D3-Q4 | Q014 | PA01-PA10 | 18 methods | Intervention Consistency |
| D3-Q5 | Q015 | PA01-PA10 | 28 methods | Output-Outcome Linkage |
| D4-Q1 | Q016 | PA01-PA10 | 15 methods | Responsibility Assignment |
| D4-Q2 | Q017 | PA01-PA10 | 13 methods | Accountability Mechanisms |
| D4-Q3 | Q018 | PA01-PA10 | 16 methods | Coordination Structures |
| D4-Q4 | Q019 | PA01-PA10 | 14 methods | Information Flow |
| D4-Q5 | Q020 | PA01-PA10 | 17 methods | Decision Processes |
| D5-Q1 | Q021 | PA01-PA10 | 19 methods | Resource Allocation |
| D5-Q2 | Q022 | PA01-PA10 | 23 methods | Resource Sufficiency |
| D5-Q3 | Q023 | PA01-PA10 | 21 methods | Resource Efficiency |
| D5-Q4 | Q024 | PA01-PA10 | 18 methods | Resource Sustainability |
| D5-Q5 | Q025 | PA01-PA10 | 16 methods | Budget Transparency |
| D6-Q1 | Q026 | PA01-PA10 | 20 methods | Monitoring System |
| D6-Q2 | Q027 | PA01-PA10 | 22 methods | Evaluation Quality |
| D6-Q3 | Q028 | PA01-PA10 | 18 methods | Validation Mechanisms |
| D6-Q4 | Q029 | PA01-PA10 | 15 methods | Adjustment Capacity |
| D6-Q5 | Q030 | PA01-PA10 | 8 methods | Learning Integration |

**Total Methods Across All Executors**: 348+ (with reuse via Method Dispensary)

### 5.5 Configuration Parameters

```python
# Phase 2 Configuration
PHASE2_CONFIG = {
    "executor_count": 30,
    "contract_count": 300,
    "signal_registry_version": "2.0",
    "enable_intelligence_layer": True,
    "enable_consumption_tracking": True,
    "enable_semantic_expansion": True,
    "enable_context_filtering": True,
    "strict_contract_validation": True
}

# ExecutorConfig
ExecutorConfig(
    max_tokens=4000,
    temperature=0.0,
    timeout_seconds=120,
    max_retries=3,
    enable_circuit_breaker=True,
    circuit_breaker_threshold=5,
    enable_calibration=True,
    calibration_data_path="calibration/empirical.json"
)
```

### 5.6 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Executors Created | 30 executor instances | Memory |
| Contracts Loaded | 300 contracts loaded | Memory |
| Pattern Matching | Signal patterns matched | SignalConsumptionProof |
| Evidence Extracted | 300 evidence items | artifacts/phase2/evidence/*.json |
| Consumption Tracked | Pattern consumption | artifacts/phase2/consumption/*.json |
| Executor Profiles | Performance metrics | artifacts/phase2/profiles/*.json |

### 5.7 SISAS Integration

#### SISAS Phase 2 Consumers

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase2/`

**Consumers Available**:

1. **Phase2ContractConsumer** (`phase2_contract_consumer.py`)
   - Monitors contract hydration
   - Tracks precision metrics
   - Validates contract completeness

2. **Phase2EvidenceConsumer** (`phase2_evidence_consumer.py`)
   - Consumes evidence extraction signals
   - Tracks evidence quality
   - Validates extraction provenance

3. **Phase2FactoryConsumer** (`phase2_factory_consumer.py`)
   - Monitors factory operations
   - Tracks executor creation
   - Validates DI wiring

4. **Phase2ExecutorConsumer** (`phase2_executor_consumer.py`)
   - Consumes executor execution signals
   - Tracks method calls
   - Validates executor contracts

**Signals Consumed**:
- `StructuralAlignmentSignal` - Contract structure
- `EventPresenceSignal` - Evidence presence
- `ExecutionAttemptSignal` - Executor operations
- `MethodApplicationSignal` - Method execution
- `EmpiricalSupportSignal` - Evidence quality
- `FrequencySignal` - Pattern usage
- `ConsumerHealthSignal` - Executor health

**Signals Emitted**:
- `ExecutionAttemptSignal` - Extraction attempts
- `FailureModeSignal` - Extraction failures
- `ConfidenceDropSignal` - Quality drops
- `LegacyActivitySignal` - Legacy system interaction

**SISAS Commands Available**:
```python
# Contract consumption tracking
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase2.phase2_contract_consumer import (
    Phase2ContractConsumer
)

consumer = Phase2ContractConsumer(bus_registry)
consumer.subscribe_to_contracts()

# Evidence consumption
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase2.phase2_evidence_consumer import (
    Phase2EvidenceConsumer
)

consumer = Phase2EvidenceConsumer(bus_registry)
consumer.track_evidence_quality()
```

**SISAS Metrics Exposed**:
- `contracts_hydrated` - Number of contracts processed (target: 300)
- `evidence_items_extracted` - Evidence count (target: 300)
- `pattern_match_rate` - Pattern success percentage
- `executor_success_rate` - Executor success percentage
- `method_call_count` - Total method invocations
- `consumption_utilization` - Signal consumption efficiency
- `circuit_breaker_trips` - Circuit breaker activations

**SISAS Control Points**:
1. **Contract Validation**: Enforces contract schema compliance
2. **Executor Construction**: Validates DI wiring
3. **Pattern Matching**: Tracks signal consumption
4. **Evidence Quality**: Validates extraction results
5. **Circuit Breaker**: Protects against cascading failures
6. **Consumption Tracking**: Monitors resource usage

### 5.8 Method Dispensary Pattern

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    METHOD DISPENSARY PATTERN ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  MONOLITH CLASSES (20 dispensaries, 348+ methods):                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ PDETMunicipalPlanAnalyzer (52 methods)                                   │   │
│  │   - _score_indicators, _extract_financials, _analyze_causality,        │   │
│  │   - _detect_budget_gaps, _validate_allocations, ...                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ CausalExtractor (28 methods)                                            │   │
│  │   - extract_goals, extract_causal_hierarchy, analyze_semantic_distance  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ FinancialAuditor (13 methods)                                           │   │
│  │   - trace_budgets, detect_allocation_gaps, verify_sufficiency          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ BayesianMechanismInference (14 methods)                                 │   │
│  │   - test_necessity, test_sufficiency, analyze_coherence                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│  [... 16 more monolith classes ...]                                          │
│                                                                                 │
│  EXECUTORS (30 executors, each using unique combination):                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ D3-Q2: TargetProportionalityAnalyzer                                    │   │
│  │   Uses 24 methods from 7 classes:                                       │   │
│  │   - PDETMunicipalPlanAnalyzer._score_indicators                        │   │
│  │   - CausalExtractor.extract_goals                                       │   │
│  │   - FinancialAuditor.trace_budgets                                     │   │
│  │   - [... 21 more methods ...]                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  METHOD ROUTING:                                                               │
│  executor.method_executor.execute(                                              │
│      class_name="PDETMunicipalPlanAnalyzer",                                   │
│      method_name="_score_indicators",                                           │
│      document=doc,                                                              │
│      signal_pack=pack,                                                          │
│      **context                                                                   │
│  )                                                                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5.9 Contract System

**Contract Location**: `src/farfan_pipeline/phases/Phase_02/generated_contracts/`

**Contract Schema**:
```json
{
  "question_id": "Q001",
  "policy_area": "PA01",
  "dimension": "DIM01",
  "version": 4,
  "signals": [...],
  "patterns": [...],
  "evidence_requirements": {
    "min_evidence_count": 1,
    "required_element_types": ["TABLE", "FIGURE"],
    "context_scope": "global"
  },
  "scoring_rules": {
    "scoring_method": "weighted_sum",
    "weight": 1.0,
    "threshold": 0.5
  }
}
```

**Total Contracts**: 300+ (Q001-Q300 × PA01-PA10)

### 5.10 Circuit Breaker Protection

```python
# Circuit breaker for executor protection
from farfan_pipeline.phases.Phase_02.phase2_30_04_circuit_breaker import (
    circuit_protected,
    CircuitBreakerRegistry
)

@circuit_protected(threshold=5, timeout=60)
def execute_executor(executor_id, document, signal_pack):
    # Protected execution
    result = executor.execute(document, signal_pack)
    return result

# Circuit breaker state
breaker = CircuitBreakerRegistry.get_breaker(executor_id)
breaker.state  # CLOSED | OPEN | HALF_OPEN
breaker.failure_count  # Consecutive failures
breaker.last_failure_time  # Timestamp
```

### 5.11 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| ContractInvalid | Schema validation | Skip contract | Fix contract |
| ExecutorConstruction | DI validation | FATAL | Fix wiring |
| PatternMatchFailure | No signals matched | Zero score | N/A |
| CircuitBreakerOpen | Failure threshold | Skip executor | Wait or fix |
| EvidenceEmpty | No evidence extracted | Zero score | N/A |

### 5.12 Health Checks

```python
# Phase 2 health check
from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
    AnalysisPipelineFactory,
    validate_bundle,
    validate_method_dispensary_pattern
)

# Create factory and validate
factory = AnalysisPipelineFactory(questionnaire_path="...")
bundle = factory.create_orchestrator()

# Validate bundle
health = validate_bundle(bundle)

# Validate method dispensary
dispensary_health = validate_method_dispensary_pattern()

# Health status
health["valid"]  # bool
health["components"]  # dict
health["metrics"]  # dict
```

---

## 6. Phase 3: Scoring

### 6.1 System Function

Phase 3 converts extracted evidence into **normalized scores on a 3-point scale** (0.0 to 3.0) using the **SISAS Signal Enriched Scoring** system. Each of the 300 evidence items is scored based on evidence presence, quality, and completeness.

### 6.2 Deterministic Execution Order

```
PHASE 3 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive EvidenceBundle (300 items from Phase 2)                              │
│ 2. Load scoring configuration (thresholds, weights)                             │
│ 3. Load calibration data (empirical baselines)                                │
│ 4. For each of 300 evidence items:                                             │
│    a. Retrieve evidence item                                                   │
│    b. Apply SISAS signal enrichment                                            │
│    c. Calculate determinacy score (25% weight)                                │
│    d. Calculate specificity score (20% weight)                                │
│    e. Calculate empirical support score (30% weight)                           │
│    f. Calculate method application score (15% weight)                          │
│    g. Calculate canonical mapping score (10% weight)                           │
│    h. Calculate completeness score (10% weight)                               │
│    i. Compute weighted score                                                  │
│    j. Clamp to [0.0, 3.0] range                                               │
│ 5. Generate ScoreMetadata (confidence, provenance, quality flags)            │
│ 6. Validate score distribution                                                │
│ 7. Output ScoreMatrix (300 scores × metadata)                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Available Commands

```bash
# Phase 3 is typically executed via orchestrator
farfan-pipeline --start-phase 3 --end-phase 3

# Direct execution (for testing)
python -m farfan_pipeline.phases.Phase_03.scoring_engine \
    --evidence <evidence_bundle> \
    --output <output_dir>
```

### 6.4 Configuration Parameters

```python
# Phase 3 Scoring Configuration
PHASE3_CONFIG = {
    "score_domain": [0.0, 3.0],
    "scoring_weights": {
        "determinacy": 0.25,
        "specificity": 0.20,
        "empirical_support": 0.30,
        "method_application": 0.15,
        "canonical_mapping": 0.10,
        "completeness": 0.10
    },
    "calibration_data_path": "calibration/empirical.json",
    "enable_signal_enrichment": True,
    "enable_confidence_intervals": True
}
```

### 6.5 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Evidence Loaded | 300 items loaded | Memory |
| Signals Enriched | SISAS enrichment applied | Memory |
| Scores Calculated | 300 scores computed | artifacts/phase3/scores/*.json |
| Metadata Generated | Confidence, provenance | artifacts/phase3/metadata/*.json |
| Distribution Computed | Score statistics | artifacts/phase3/distribution.json |

### 6.6 SISAS Integration

#### SISAS Phase 3 Consumer

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase3/phase3_10_00_signal_enriched_scoring.py`

**Purpose**: Signal-enriched scoring for evidence items

**Signals Consumed**:
- `StructuralAlignmentSignal` - Evidence structure
- `EventPresenceSignal` - Evidence presence
- `EventCompletenessSignal` - Evidence completeness
- `EmpiricalSupportSignal` - Empirical backing
- `MethodApplicationSignal` - Method tracking
- `CanonicalMappingSignal` - Canonical alignment

**Signals Emitted**:
- `AnswerDeterminacySignal` - Score determinacy
- `AnswerSpecificitySignal` - Score specificity
- `ExecutionAttemptSignal` - Scoring operations
- `ConfidenceDropSignal` - Quality changes

**SISAS Commands Available**:
```python
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase3.phase3_10_00_signal_enriched_scoring import (
    Phase3SignalEnrichedScoringConsumer
)

# Create consumer
consumer = Phase3SignalEnrichedScoringConsumer(
    bus_registry=bus_registry,
    calibration_data_path="calibration/empirical.json"
)

# Score evidence with signal enrichment
scores = consumer.score_evidence(evidence_items)
```

**SISAS Metrics Exposed**:
- `scores_generated` - Number of scores (target: 300)
- `avg_score` - Average score across all items
- `score_distribution` - Score histogram
- `determinacy_avg` - Average determinacy score
- `specificity_avg` - Average specificity score
- `empirical_support_avg` - Average empirical support
- `confidence_interval_width` - CI width statistics

**SISAS Control Points**:
1. **Score Domain Validation**: Enforces [0.0, 3.0] range
2. **Weight Normalization**: Ensures weights sum to 1.0
3. **Calibration Application**: Applies empirical baselines
4. **Signal Enrichment**: Applies SISAS signals
5. **Confidence Calculation**: Computes confidence intervals

### 6.7 Scoring Algorithm

```python
# Weighted scoring formula
def calculate_score(evidence_item, signals):
    determinacy_score = calculate_determinacy(evidence_item, signals) * 0.25
    specificity_score = calculate_specificity(evidence_item, signals) * 0.20
    empirical_score = calculate_empirical_support(evidence_item, signals) * 0.30
    method_score = calculate_method_application(evidence_item, signals) * 0.15
    mapping_score = calculate_canonical_mapping(evidence_item, signals) * 0.10
    completeness_score = calculate_completeness(evidence_item, signals) * 0.10

    total = (determinacy_score + specificity_score + empirical_score +
             method_score + mapping_score + completeness_score)

    return clamp(total, 0.0, 3.0)
```

### 6.8 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| ScoreOutOfBounds | score < 0 or > 3 | Clamp and warn | N/A |
| MissingEvidence | No evidence for question | Default to 0 | N/A |
| CalibrationLoad | Calibration data missing | Use defaults | N/A |
| SignalMissing | Required signal absent | Use default weight | N/A |

### 6.9 Health Checks

```python
# Phase 3 health check
def validate_score_distribution(scores):
    # Validate score count
    assert len(scores) == 300, f"Expected 300 scores, got {len(scores)}"

    # Validate score domain
    for score in scores:
        assert 0.0 <= score.value <= 3.0, f"Score out of bounds: {score.value}"

    # Validate distribution
    assert calculate_mean(scores) > 0, "All scores are zero"

    return True
```

---

## 7. Phase 4: Dimension Aggregation

### 7.1 System Function

Phase 4 aggregates **300 micro scores into 60 dimension scores** using the **Choquet Integral** for non-linear aggregation that accounts for interaction between dimensions within each policy area.

**Compression Ratio**: 5:1 (300 → 60)

### 7.2 Deterministic Execution Order

```
PHASE 4 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive ScoreMatrix (300 scores from Phase 3)                               │
│ 2. Load Choquet weights (non-additive interaction weights)                     │
│ 3. For each of 10 policy areas:                                               │
│    a. Retrieve 30 micro scores for the area (5 dims × 6 Q per dim)           │
│    b. Apply Choquet integral per dimension                                    │
│    c. Generate 6 dimension scores per area                                   │
│ 4. Validate dimension count (must equal 60)                                  │
│ 5. Compute dispersion metrics (CV, DI, quartiles)                            │
│ 6. Output DimensionScore[] (60 scores total)                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Available Commands

```bash
# Phase 4 is typically executed via orchestrator
farfan-pipeline --start-phase 4 --end-phase 4

# Direct execution (for testing)
python -m farfan_pipeline.phases.Phase_04.dimension_aggregator \
    --scores <score_matrix> \
    --output <output_dir>
```

### 7.4 Configuration Parameters

```python
# Phase 4 Configuration
PHASE4_CONFIG = {
    "input_score_count": 300,
    "output_dimension_count": 60,
    "policy_areas": 10,
    "dimensions_per_area": 6,
    "aggregation_method": "choquet_integral",
    "dispersion_threshold": 0.6,
    "enable_uncertainty_quantification": True
}
```

### 7.5 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Scores Loaded | 300 micro scores loaded | Memory |
| Choquet Weights Applied | Non-additive aggregation | Memory |
| Dimension Scores Computed | 60 dimension scores | artifacts/phase4/dimensions/*.json |
| Dispersion Calculated | CV, DI, IQR metrics | artifacts/phase4/dispersion/*.json |
| Choquet Weights Stored | Interaction weights | artifacts/phase4/choquet_weights.json |

### 7.6 SISAS Integration

**SISAS Metrics Exposed**:
- `dimension_scores_generated` - Number of dimension scores (target: 60)
- `compression_ratio` - 300:60 = 5:1
- `choquet_convergence` - Weight convergence metrics
- `dispersion_by_dimension` - CV per dimension
- `high_dispersion_count` - Dimensions with CV > 0.6

**SISAS Control Points**:
1. **Dimension Count Validation**: Enforces exactly 60 dimension scores
2. **Choquet Convergence**: Validates weight convergence
3. **Dispersion Threshold**: Flags high dispersion dimensions

### 7.7 Choquet Integral Algorithm

```python
# Choquet integral for non-linear aggregation
def choquet_integral(scores, weights):
    """
    Non-linear aggregation accounting for interaction between criteria.

    Args:
        scores: List of scores to aggregate
        weights: Choquet capacity (non-additive weights)

    Returns:
        Aggregated score
    """
    # Sort scores in ascending order
    sorted_scores = sorted(scores)

    # Compute Choquet integral
    result = 0
    for i, score in enumerate(sorted_scores):
        # Choquet capacity difference
        delta = weights[i] - weights[i-1] if i > 0 else weights[i]
        result += delta * score

    return result
```

### 7.8 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| DimensionCountMismatch | len(scores) != 60 | FATAL | Fix aggregation logic |
| ChoquetNonConvergence | Weights not normalized | Re-normalize | N/A |
| HighDispersion | CV > 0.6 | Flag for review | N/A |

---

## 8. Phase 5: Area Aggregation

### 8.1 System Function

Phase 5 aggregates **60 dimension scores into 10 policy area scores** using weighted arithmetic mean. Each policy area (PA01-PA10) receives 6 dimension scores (DIM01-DIM06).

**Compression Ratio**: 6:1 (60 → 10)

### 8.2 Deterministic Execution Order

```
PHASE 5 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive DimensionScore[] (60 scores from Phase 4)                            │
│ 2. Load area weights (dimension weights per policy area)                       │
│ 3. For each of 10 policy areas:                                               │
│    a. Retrieve 6 dimension scores for the area                               │
│    b. Apply weighted mean: sum(score_i * weight_i)                           │
│    c. Validate weight sum equals 1.0                                         │
│ 4. Assign quality level based on score range                                  │
│ 5. Output AreaScore[] (10 scores total)                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 Available Commands

```bash
# Phase 5 is typically executed via orchestrator
farfan-pipeline --start-phase 5 --end-phase 5

# Direct execution (for testing)
python -m farfan_pipeline.phases.Phase_05.area_aggregator \
    --dimensions <dimension_scores> \
    --output <output_dir>
```

### 8.4 Configuration Parameters

```python
# Phase 5 Configuration
PHASE5_CONFIG = {
    "input_dimension_count": 60,
    "output_area_count": 10,
    "dimensions_per_area": 6,
    "aggregation_method": "weighted_mean",
    "quality_levels": {
        "EXCELENTE": 2.55,
        "BUENO": 2.10,
        "ACEPTABLE": 1.65,
        "INSUFICIENTE": 0.0
    }
}
```

### 8.5 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Dimensions Loaded | 60 dimension scores loaded | Memory |
| Weights Applied | Area-specific weights | Memory |
| Area Scores Computed | 10 area scores | artifacts/phase5/areas/*.json |
| Quality Levels Assigned | EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE | artifacts/phase5/quality_levels.json |

### 8.6 SISAS Integration

**SISAS Metrics Exposed**:
- `area_scores_generated` - Number of area scores (target: 10)
- `compression_ratio` - 60:10 = 6:1
- `weight_normalization_status` - Weight sum validation
- `quality_level_distribution` - Distribution across 4 levels

**SISAS Control Points**:
1. **Area Count Validation**: Enforces exactly 10 area scores
2. **Weight Normalization**: Ensures weights sum to 1.0
3. **Quality Level Assignment**: Validates score-to-quality mapping

### 8.7 Quality Level Rubric

| Quality Level | Range (Normalized) | Range (3-Point) | Description |
|---------------|-------------------|-----------------|-------------|
| EXCELENTE | ≥ 0.85 | ≥ 2.55 | Outstanding policy compliance |
| BUENO | 0.70-0.84 | 2.10-2.54 | Good compliance with minor gaps |
| ACEPTABLE | 0.55-0.69 | 1.65-2.09 | Acceptable with improvement areas |
| INSUFICIENTE | < 0.55 | < 1.65 | Insufficient, requires intervention |

### 8.8 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| AreaCountMismatch | len(scores) != 10 | FATAL | Fix aggregation logic |
| WeightSumError | sum(weights) != 1.0 | Re-normalize | N/A |
| ZeroDimensions | Area with no dimensions | Skip area | Fix data |

---

## 9. Phase 6: Cluster Aggregation

### 9.1 System Function

Phase 6 aggregates **10 policy area scores into 4 MESO-level cluster scores** with the **Adaptive Penalty Framework (APF)** that applies score corrections when intra-cluster dispersion exceeds thresholds.

**Compression Ratio**: 2.5:1 (10 → 4)

### 9.2 Cluster Topology

| Cluster | Policy Areas | Thematic Focus |
|---------|--------------|----------------|
| CLUSTER_MESO_1 | PA01, PA02, PA03 | Legal & Institutional Framework |
| CLUSTER_MESO_2 | PA04, PA05, PA06 | Implementation & Operational Capacity |
| CLUSTER_MESO_3 | PA07, PA08 | Monitoring & Evaluation Systems |
| CLUSTER_MESO_4 | PA09, PA10 | Strategic Planning & Sustainability |

### 9.3 Deterministic Execution Order

```
PHASE 6 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive AreaScore[] (10 scores from Phase 5)                                │
│ 2. Load cluster topology (4 clusters, 10 area mappings)                        │
│ 3. For each of 4 clusters:                                                    │
│    a. Retrieve area scores for cluster                                       │
│    b. Calculate intra-cluster dispersion (CV)                                 │
│    c. Determine penalty factor based on CV range                             │
│    d. Apply penalty: cluster_score × penalty_factor                           │
│    e. Calculate coherence metrics                                             │
│ 4. Validate cluster count (must equal 4)                                      │
│ 5. Output ClusterScore[] (4 scores total)                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 9.4 Available Commands

```bash
# Phase 6 is typically executed via orchestrator
farfan-pipeline --start-phase 6 --end-phase 6

# Direct execution (for testing)
python -m farfan_pipeline.phases.Phase_06.cluster_aggregator \
    --areas <area_scores> \
    --output <output_dir>
```

### 9.5 Configuration Parameters

```python
# Phase 6 Configuration
PHASE6_CONFIG = {
    "input_area_count": 10,
    "output_cluster_count": 4,
    "adaptive_penalty_framework": {
        "convergence": {"cv_range": [0, 0.19], "penalty": 1.00},
        "moderate": {"cv_range": [0.20, 0.39], "penalty": 0.95},
        "high": {"cv_range": [0.40, 0.59], "penalty": 0.85},
        "extreme": {"cv_range": [0.60, 1.0], "penalty": 0.70}
    },
    "coherence_threshold": 0.7
}
```

### 9.6 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Areas Loaded | 10 area scores loaded | Memory |
| Cluster Mappings Applied | Area-to-cluster mapping | Memory |
| Dispersion Calculated | CV per cluster | Memory |
| Penalty Factors Applied | APF corrections | artifacts/phase6/penalties/*.json |
| Cluster Scores Computed | 4 cluster scores | artifacts/phase6/clusters/*.json |
| Coherence Metrics Generated | Within-cluster coherence | artifacts/phase6/coherence/*.json |

### 9.7 SISAS Integration

#### SISAS Phase 7 (actually Phase 6) Consumer

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase7/phase7_meso_consumer.py`

**Purpose**: MESO-level signal consumption for cluster aggregation

**Signals Consumed**:
- `StructuralAlignmentSignal` - Cluster structure validation
- `EventPresenceSignal` - Area presence in clusters
- `TemporalContrastSignal` - Temporal changes in clusters

**Signals Emitted**:
- `ConfidenceDropSignal` - Cluster quality drops
- `DecisionDivergenceSignal` - Area divergence within clusters

**SISAS Metrics Exposed**:
- `cluster_scores_generated` - Number of cluster scores (target: 4)
- `compression_ratio` - 10:4 = 2.5:1
- `penalty_distribution` - Penalty factor histogram
- `dispersion_by_cluster` - CV per cluster
- `coherence_indices` - Within-cluster coherence scores

**SISAS Control Points**:
1. **Cluster Count Validation**: Enforces exactly 4 cluster scores
2. **Penalty Bounds**: Validates penalty factors in [0.70, 1.00]
3. **Dispersion Threshold**: Triggers penalty based on CV ranges
4. **Coherence Monitoring**: Tracks within-cluster coherence

### 9.8 Adaptive Penalty Framework

| CV Range | Scenario | Penalty Factor | Interpretation |
|----------|----------|----------------|----------------|
| < 0.20 | CONVERGENCE | 1.00 | Coherent implementation |
| 0.20-0.39 | MODERATE | 0.95 | Minor inconsistencies |
| 0.40-0.59 | HIGH | 0.85 | Significant gaps |
| ≥ 0.60 | EXTREME | 0.70 | Systemic failure |

### 9.9 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| ClusterCountMismatch | len(scores) != 4 | FATAL | Fix aggregation logic |
| PenaltyOutOfBounds | factor < 0.7 or > 1.0 | Clamp to valid range | N/A |
| EmptyCluster | No areas assigned | FATAL | Fix topology |

---

## 10. Phase 7: Macro Evaluation

### 10.1 System Function

Phase 7 synthesizes **4 MESO-level cluster scores into a single holistic MacroScore** with **Cross-Cutting Coherence Analysis (CCCA)**, **Systemic Gap Detection (SGD)**, and **Strategic Alignment Scoring (SAS)**.

**Compression Ratio**: 4:1 (4 → 1)

### 10.2 Deterministic Execution Order

```
PHASE 7 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive ClusterScore[] (4 scores from Phase 6)                              │
│ 2. Compute holistic macro score (weighted aggregation of 4 clusters)           │
│ 3. Perform Cross-Cutting Coherence Analysis (CCCA):                           │
│    a. Strategic coherence (vertical alignment)                               │
│    b. Operational coherence (horizontal integration)                          │
│    c. Institutional coherence (governance structures)                        │
│ 4. Perform Systemic Gap Detection (SGD):                                      │
│    a. Identify underperforming policy areas                                 │
│    b. Detect intervention priorities                                         │
│ 5. Perform Strategic Alignment Scoring (SAS):                                 │
│    a. Vertical alignment (goals → actions)                                   │
│    b. Horizontal alignment (cross-area consistency)                           │
│    c. Temporal alignment (short → long term)                                 │
│ 6. Assign quality classification based on normalized score                    │
│ 7. Output MacroScore (1 holistic score + breakdowns)                          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 10.3 Available Commands

```bash
# Phase 7 is typically executed via orchestrator
farfan-pipeline --start-phase 7 --end-phase 7

# Direct execution (for testing)
python -m farfan_pipeline.phases.Phase_07.macro_evaluator \
    --clusters <cluster_scores> \
    --output <output_dir>
```

### 10.4 Configuration Parameters

```python
# Phase 7 Configuration
PHASE7_CONFIG = {
    "input_cluster_count": 4,
    "output_macro_count": 1,
    "coherence_weights": {
        "strategic": 0.35,
        "operational": 0.40,
        "institutional": 0.25
    },
    "gap_threshold": 0.5,
    "alignment_weights": {
        "vertical": 0.40,
        "horizontal": 0.35,
        "temporal": 0.25
    }
}
```

### 10.5 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Clusters Loaded | 4 cluster scores loaded | Memory |
| Macro Score Computed | 1 holistic score | artifacts/phase7/macro.json |
| CCCA Performed | Coherence breakdown | artifacts/phase7/coherence/*.json |
| SGD Performed | Systemic gaps identified | artifacts/phase7/gaps/*.json |
| SAS Performed | Alignment scores | artifacts/phase7/alignment/*.json |
| Quality Assigned | Final quality level | artifacts/phase7/quality.json |

### 10.6 SISAS Integration

**SISAS Metrics Exposed**:
- `macro_score_generated` - Single holistic score (always 1)
- `compression_ratio` - 4:1 = 4:1
- `final_compression_ratio` - 300:1 (total pipeline)
- `coherence_strategic` - Strategic coherence score
- `coherence_operational` - Operational coherence score
- `coherence_institutional` - Institutional coherence score
- `gaps_detected` - Number of systemic gaps
- `alignment_vertical` - Vertical alignment score
- `alignment_horizontal` - Horizontal alignment score
- `alignment_temporal` - Temporal alignment score

**SISAS Control Points**:
1. **Singleton Validation**: Enforces exactly 1 macro score
2. **Score Domain Validation**: Enforces [0.0, 3.0] range
3. **Coherence Thresholds**: Validates coherence scores
4. **Gap Severity Levels**: Classifies gap severity

### 10.7 Quality Classification Rubric (Normalized)

| Quality Level | Range | 3-Point Range | Description |
|---------------|-------|---------------|-------------|
| EXCELENTE | ≥ 0.85 | ≥ 2.55 | Outstanding policy compliance |
| BUENO | 0.70-0.84 | 2.10-2.54 | Good compliance with minor gaps |
| ACEPTABLE | 0.55-0.69 | 1.65-2.09 | Acceptable with improvement areas |
| INSUFICIENTE | < 0.55 | < 1.65 | Insufficient, requires intervention |

### 10.8 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| NonSingletonOutput | len(scores) != 1 | FATAL | Fix aggregation logic |
| ScoreOutOfBounds | score < 0 or > 3 | Clamp and warn | N/A |
| CoherenceCalculation | Division by zero | Fallback to default | N/A |

---

## 11. Phase 8: Recommendation Engine

### 11.1 System Function

Phase 8 generates **evidence-based policy recommendations** at three levels (MICRO, MESO, MACRO) using an **exponentially enhanced v3.0 engine** with 5 optimization windows delivering **4.5×10¹² x** value multiplier.

### 11.2 Deterministic Execution Order

```
PHASE 8 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive ScoreMatrix + MacroScore + quality levels                            │
│ 2. Load recommendation rules (300 rules total)                                 │
│ 3. Schema-driven validation (120x multiplier)                                  │
│ 4. Generic rule engine processing (∞ scalability)                              │
│ 5. Template compilation (200x multiplier)                                       │
│ 6. Memoized validation (6,250x multiplier)                                     │
│ 7. Generative testing (30,000x multiplier)                                     │
│ 8. Generate MICRO recommendations (dimension-level, 300 rules)                  │
│ 9. Generate MESO recommendations (cluster-level, 40 rules)                     │
│ 10. Generate MACRO recommendations (strategic, 10 rules)                       │
│ 11. Apply priority and urgency classification                                  │
│ 12. Link recommendations to evidence provenance                                 │
│ 13. Output RecommendationSet[]                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 11.3 Available Commands

```bash
# Phase 8 is typically executed via orchestrator
farfan-pipeline --start-phase 8 --end-phase 8

# Direct execution (for testing)
python -m farfan_pipeline.phases.Phase_08.recommendation_engine \
    --scores <score_matrix> \
    --macro <macro_score> \
    --output <output_dir>
```

### 11.4 Configuration Parameters

```python
# Phase 8 Configuration
PHASE8_CONFIG = {
    "total_rules": 300,
    "micro_rules": 300,
    "meso_rules": 40,
    "macro_rules": 10,
    "optimization_windows": 5,
    "value_multiplier": "4.5x10^12",
    "priority_levels": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    "urgency_levels": ["IMMEDIATE", "SHORT_TERM", "MEDIUM_TERM", "LONG_TERM"]
}
```

### 11.5 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Rules Loaded | 300 recommendation rules | Memory |
| Schema Validation Applied | 120x validation multiplier | Memory |
| Rules Executed | Generic rule engine | Memory |
| Templates Compiled | 200x template multiplier | Memory |
| Cache Utilized | 6,250x memoization multiplier | Memory cache |
| Tests Generated | 30,000x generative testing | artifacts/phase8/tests/*.json |
| Recommendations Generated | MICRO/MESO/MACRO | artifacts/phase8/recommendations/*.json |

### 11.6 SISAS Integration

#### SISAS Phase 8 Consumer

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase8/phase8_30_00_signal_enriched_recommendations.py`

**Purpose**: Signal-enriched recommendation generation

**Signals Consumed**:
- `StructuralAlignmentSignal` - Recommendation structure
- `EventPresenceSignal` - Evidence presence
- `TemporalContrastSignal` - Temporal changes
- `DecisionDivergenceSignal` - Decision quality changes

**Signals Emitted**:
- `ExecutionAttemptSignal` - Recommendation generation attempts
- `FailureModeSignal` - Recommendation generation failures
- `ConfidenceDropSignal` - Confidence changes

**SISAS Metrics Exposed**:
- `micro_recommendations` - Count of MICRO-level recommendations
- `meso_recommendations` - Count of MESO-level recommendations
- `macro_recommendations` - Count of MACRO-level recommendations
- `total_recommendations` - Total recommendations generated
- `priority_distribution` - Distribution across priority levels
- `urgency_distribution` - Distribution across urgency levels
- `evidence_linkage_rate` - Recommendations with evidence links

**SISAS Control Points**:
1. **Rule Schema Validation**: Enforces rule schema compliance
2. **Template Safety**: Validates template rendering
3. **Cache Management**: Manages memoization cache
4. **Evidence Linkage**: Validates evidence-provenance links

### 11.7 Recommendation Types

| Type | Level | Focus | Count |
|------|-------|-------|-------|
| INVESTIGATE | MICRO | Dimension-level investigation | Variable |
| REVIEW | MESO | Cluster-level review | Variable |
| MONITOR | MACRO | Strategic monitoring | Variable |
| IMPROVE | MICRO/MESO | Improvement actions | Variable |
| ENHANCE | MESO/MACRO | Enhancement opportunities | Variable |
| FIX | MICRO | Critical fixes | Variable |
| COMPLETE | MESO | Completion actions | Variable |
| ALERT | MACRO | Strategic alerts | Variable |

### 11.8 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| RuleValidationFailure | Schema violation | Skip rule with warning | Fix rule |
| TemplateRenderingError | Missing variable | Use default value | Fix template |
| CacheInvalidation | Rule changed | Clear validation cache | N/A |
| EvidenceLinkMissing | No provenance | Flag recommendation | N/A |

---

## 12. Phase 9: Reporting

### 12.1 System Function

Phase 9 assembles **comprehensive policy evaluation reports** with multiple output formats using Jinja2 templates. Generates executive dashboards and technical deep-dive reports with all evaluation artifacts.

### 12.2 Deterministic Execution Order

```
PHASE 9 EXECUTION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Receive MacroScore + RecommendationSet[] + all phase artifacts              │
│ 2. Load report templates (Jinja2)                                             │
│ 3. Compile provenance metadata (all phases)                                  │
│ 4. Generate executive dashboard:                                             │
│    a. High-level summary for decision makers                                 │
│    b. Key metrics and quality classification                                  │
│    c. Strategic recommendations                                               │
│ 5. Generate technical deep dive:                                             │
│    a. Detailed phase-by-phase analysis                                       │
│    b. Evidence provenance chains                                             │
│    c. Method dispersion analysis                                             │
│ 6. Generate institutional annex:                                             │
│    a. Entity-specific findings                                               │
│    b. Gap analysis by institution                                             │
│ 7. Validate report completeness                                                │
│ 8. Output EvaluationReport (HTML/PDF)                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 12.3 Available Commands

```bash
# Phase 9 is typically executed via orchestrator
farfan-pipeline --start-phase 9 --end-phase 9

# Direct execution (for testing)
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --macro <macro_score> \
    --recommendations <recommendations> \
    --output <output_dir>
```

### 12.4 Configuration Parameters

```python
# Phase 9 Configuration
PHASE9_CONFIG = {
    "templates": {
        "executive_dashboard": "executive_dashboard.html.j2",
        "technical_deep_dive": "technical_deep_dive.html.j2",
        "report_enhanced": "report_enhanced.html.j2"
    },
    "output_formats": ["HTML", "PDF"],
    "include_provenance": True,
    "include_evidence_chains": True,
    "include_method_dispensary": True
}
```

### 12.5 Side Effects and Intermediate States

| State | Description | Persistence |
|-------|-------------|-------------|
| Artifacts Loaded | All phase artifacts loaded | Memory |
| Templates Compiled | Jinja2 templates ready | Memory |
| Provenance Assembled | Complete provenance chain | Memory |
| Executive Dashboard Generated | High-level summary | artifacts/phase9/executive_dashboard.html |
| Technical Deep Dive Generated | Detailed analysis | artifacts/phase9/technical_deep_dive.html |
| Institutional Annex Generated | Entity-specific findings | artifacts/phase9/institutional_annex.pdf |
| Report Metadata | Generation metadata | artifacts/phase9/metadata.json |

### 12.6 SISAS Integration

**SISAS Metrics Exposed**:
- `report_generation_duration_ms` - Report generation time
- `template_render_count` - Number of templates rendered
- `provenance_chain_length` - Provenance depth
- `artifact_completeness_score` - Completeness percentage
- `pdf_conversion_success` - PDF generation status

**SISAS Control Points**:
1. **Artifact Completeness**: Validates all artifacts present
2. **Template Safety**: Validates template variables
3. **PDF Conversion**: Monitors PDF generation
4. **Provenance Validation**: Validates provenance chains

### 12.7 Report Templates

| Template | Purpose | Audience | Sections |
|----------|---------|----------|----------|
| `executive_dashboard.html.j2` | Strategic summary | Policy makers | Quality score, key recommendations, metrics |
| `technical_deep_dive.html.j2` | Detailed analysis | Technical reviewers | Phase breakdowns, evidence, methods |
| `report_enhanced.html.j2` | Full evaluation | Comprehensive review | All sections with enhanced visualization |

### 12.8 Error Handling

| Error Type | Detection | Handling | Recovery |
|------------|-----------|----------|----------|
| TemplateError | Invalid Jinja2 syntax | Use fallback template | Fix template |
| MissingArtifact | Phase output unavailable | Include placeholder | Fix pipeline |
| PDFGenerationError | Rendering failure | Output HTML only | Fix PDF converter |

---

## 13. SISAS: Complete Technical Reference

### 13.1 System Overview

SISAS (Signal-Irrigated System for Analytical Support) is the **canonical transversal axis** of the F.A.R.F.A.N. pipeline. It provides signal-based infrastructure for monitoring, analysis, and control across all phases.

### 13.2 Architecture Principles

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     SISAS ARCHITECTURAL AXIOMS                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. NOTHING CIRCULATES WITHOUT CONTRACTS                                       │
│     - All signals require PublicationContract or ConsumptionContract           │
│     - Contracts specify allowed buses, signal types, and conditions            │
│                                                                                 │
│  2. EVERYTHING IS REGISTERED AND AUDITABLE                                     │
│     - All signal operations logged with timestamps                            │
│     - Complete provenance chains from source to consumption                   │
│                                                                                 │
│  3. CONSUMERS ANALYZE, THEY DO NOT EXECUTE                                    │
│     - Consumers process signals and produce insights                          │
│     - Consumers DO NOT make decisions or execute actions                      │
│                                                                                 │
│  4. SIGNALS ARE IMMUTABLE                                                      │
│     - Once created, signals are never modified                               │
│     - Signals accumulate (never overwritten)                                  │
│                                                                                 │
│  5. SIGNALS ARE DETERMINISTIC                                                  │
│     - Same input + same context = same signal                                 │
│     - Versioned signals enable reproducibility                                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 13.3 Complete SISAS Command Inventory

#### 13.3.1 Main CLI Commands

```bash
# SISAS Main Entry Point
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main <command>

# Available Commands:
# run         - Execute irrigation pipeline
# check       - Check vocabulary alignment
# contracts   - Generate irrigation contracts
# stats       - Show irrigation statistics
# health      - Check SISAS system health
# audit       - Run signal audit
```

#### 13.3.2 Command Details

**`run` Command - Execute Irrigation**

```bash
python -m SISAS.main run \
    --csv-path <path_to_sabana_csv> \
    --base-path <canonical_base_path> \
    [--phase <phase_name>] \  # Run specific phase (JF0-JF10)
    [--all]                   # Run all irrigable phases
    [--dry-run]               # Simulate without execution
    [--verbose]               # Detailed logging
```

**`check` Command - Vocabulary Alignment**

```bash
python -m SISAS.main check \
    [--signal-types] \        # Check signal type definitions
    [--capabilities] \         # Check capability alignment
    [--full]                   # Run all checks
```

**`contracts` Command - Generate Contracts**

```bash
python -m SISAS.main contracts \
    --csv-path <path_to_sabana_csv> \
    [--output <contracts.json>] \  # Output file path
    [--format JSON|YAML]            # Output format
```

**`stats` Command - Show Statistics**

```bash
python -m SISAS.main stats \
    --csv-path <path_to_sabana_csv> \
    [--by-phase] \            # Breakdown by irrigation phase
    [--by-vehicle] \          # Breakdown by vehicle
    [--by-consumer]           # Breakdown by consumer
```

**`health` Command - System Health**

```bash
python -m SISAS.main health \
    [--bus-stats] \           # Show bus statistics
    [--consumer-health] \     # Show consumer health
    [--vehicle-status]        # Show vehicle status
```

**`audit` Command - Run Audit**

```bash
python -m SISAS.main audit \
    --scope <scope> \         # all|signals|consumers|vehicles|contracts
    [--output <audit_report.json>]
```

### 13.4 Signal Types (Complete Inventory)

#### 13.4.1 Structural Signals

| Signal Type | Purpose | Emitted By | Consumed By |
|-------------|---------|------------|-------------|
| `StructuralAlignmentSignal` | Maps data to canonical structure | SignalRegistryVehicle | Phase 0, 1, 2, 3 |
| `SchemaConflictSignal` | Indicates schema conflicts | SignalQualityMetricsVehicle | All phases |
| `CanonicalMappingSignal` | Maps items to canonical entities | SignalContextScoperVehicle | Phase 1, 2, 3 |

#### 13.4.2 Integrity Signals

| Signal Type | Purpose | Emitted By | Consumed By |
|-------------|---------|------------|-------------|
| `EventPresenceSignal` | Indicates if expected events exist | SignalRegistryVehicle | All phases |
| `EventCompletenessSignal` | Measures event completeness | SignalRegistryVehicle | Phase 0, 2, 3 |
| `DataIntegritySignal` | Validates referential integrity | SignalQualityMetricsVehicle | Phase 1, 2 |

#### 13.4.3 Epistemic Signals

| Signal Type | Purpose | Emitted By | Consumed By |
|-------------|---------|------------|-------------|
| `AnswerDeterminacySignal` | Evaluates answer determinacy | SignalContextScoperVehicle | Phase 3 |
| `AnswerSpecificitySignal` | Evaluates answer specificity | SignalContextScoperVehicle | Phase 3 |
| `EmpiricalSupportSignal` | Evaluates documentary support | SignalEvidenceExtractorVehicle | Phase 2, 3 |
| `MethodApplicationSignal` | Records method application | SignalIntelligenceLayerVehicle | Phase 2, 3, 7, 8 |

#### 13.4.4 Contrast Signals

| Signal Type | Purpose | Emitted By | Consumed By |
|-------------|---------|------------|-------------|
| `DecisionDivergenceSignal` | Compares legacy vs new outputs | (Planned) | Phase 7, 8 |
| `ConfidenceDropSignal` | Indicates confidence decreases | (Planned) | All phases |
| `TemporalContrastSignal` | Tracks changes over time | (Planned) | Phase 7 |

#### 13.4.5 Operational Signals

| Signal Type | Purpose | Emitted By | Consumed By |
|-------------|---------|------------|-------------|
| `ExecutionAttemptSignal` | Records execution attempts | All phases | All consumers |
| `FailureModeSignal` | Describes operation failures | All phases | Circuit breakers |
| `LegacyActivitySignal` | Passive legacy observation | (Planned) | Phase 0, 7 |
| `LegacyDependencySignal` | Maps legacy dependencies | WiringBootstrap | Phase 0 |

#### 13.4.6 Consumption Signals

| Signal Type | Purpose | Emitted By | Consumed By |
|-------------|---------|------------|-------------|
| `FrequencySignal` | Tracks resource usage | Phase 2 | All phases |
| `TemporalCouplingSignal` | Measures component coupling | (Planned) | Orchestrator |
| `ConsumerHealthSignal` | Monitors consumer health | All consumers | Health monitoring |

### 13.5 Vehicle Modules (Complete Inventory)

#### 13.5.1 Vehicle Status

| Vehicle ID | Status | Capabilities | File |
|------------|--------|--------------|------|
| `signal_loader` | IMPLEMENTED | can_load | `vehicles/signal_loader.py` |
| `signal_registry` | IMPLEMENTED | can_load, can_transform | `vehicles/signal_registry.py` |
| `signal_context_scoper` | IMPLEMENTED | can_scope | `vehicles/signal_context_scoper.py` |
| `signal_evidence_extractor` | PARTIAL | can_extract | `vehicles/signal_evidence_extractor.py` |
| `signal_intelligence_layer` | IMPLEMENTED | can_transform | `vehicles/signal_intelligence_layer.py` |
| `signal_irrigator` | PENDING | can_irrigate | `vehicles/signal_irrigator.py` |
| `signal_enhancement_integrator` | PENDING | can_enrich | `vehicles/signal_enhancement_integrator.py` |
| `signal_quality_metrics` | PENDING | can_validate | `vehicles/signal_quality_metrics.py` |

#### 13.5.2 Vehicle Capabilities

```python
# Vehicle Capability Declaration
class VehicleCapabilities(Enum):
    CAN_LOAD = "can_load"           # Load canonical files
    CAN_SCOPE = "can_scope"         # Scope signals to context
    CAN_EXTRACT = "can_extract"     # Extract evidence
    CAN_TRANSFORM = "can_transform" # Transform signals
    CAN_ENRICH = "can_enrich"       # Enrich signals
    CAN_VALIDATE = "can_validate"   # Validate signal quality
    CAN_IRRIGATE = "can_irrigate"   # Irrigate to consumers
```

### 13.6 Consumer Modules (Complete Inventory)

#### 13.6.1 Phase 0 Consumers

**Phase0BootstrapConsumer** (`consumers/phase0/phase0_90_02_bootstrap.py`)
- Analyzes: Bootstrap operations
- Subscribes to: `structural_bus`, `integrity_bus`
- Emits: `ExecutionAttemptSignal`, `LegacyDependencySignal`

#### 13.6.2 Phase 1 Consumers

**Phase1SignalEnrichmentConsumer** (`consumers/phase1/phase1_11_00_signal_enrichment.py`)
- Analyzes: Document chunking
- Subscribes to: `structural_bus`, `integrity_bus`, `epistemic_bus`
- Emits: `ExecutionAttemptSignal`, `EmpiricalSupportSignal`

#### 13.6.3 Phase 2 Consumers

**Phase2ContractConsumer** (`consumers/phase2/phase2_contract_consumer.py`)
- Analyzes: Contract hydration
- Subscribes to: `structural_bus`, `integrity_bus`, `operational_bus`

**Phase2EvidenceConsumer** (`consumers/phase2/phase2_evidence_consumer.py`)
- Analyzes: Evidence extraction
- Subscribes to: `epistemic_bus`, `structural_bus`, `integrity_bus`

**Phase2FactoryConsumer** (`consumers/phase2/phase2_factory_consumer.py`)
- Analyzes: Factory operations
- Subscribes to: `operational_bus`, `structural_bus`

**Phase2ExecutorConsumer** (`consumers/phase2/phase2_executor_consumer.py`)
- Analyzes: Executor execution
- Subscribes to: `operational_bus`, `consumption_bus`

#### 13.6.4 Phase 3 Consumers

**Phase3SignalEnrichedScoringConsumer** (`consumers/phase3/phase3_10_00_signal_enriched_scoring.py`)
- Analyzes: Signal-enriched scoring
- Subscribes to: `epistemic_bus`, `structural_bus`, `integrity_bus`
- Emits: `AnswerDeterminacySignal`, `AnswerSpecificitySignal`

#### 13.6.5 Phase 7 Consumers

**Phase7MESOConsumer** (`consumers/phase7/phase7_meso_consumer.py`)
- Analyzes: MESO-level aggregation
- Subscribes to: `contrast_bus`, `epistemic_bus`, `integrity_bus`
- Emits: `ConfidenceDropSignal`, `DecisionDivergenceSignal`

#### 13.6.6 Phase 8 Consumers

**Phase8SignalEnrichedRecommendationsConsumer** (`consumers/phase8/phase8_30_00_signal_enriched_recommendations.py`)
- Analyzes: Recommendation generation
- Subscribes to: `contrast_bus`, `epistemic_bus`, `integrity_bus`
- Emits: `ExecutionAttemptSignal`, `FailureModeSignal`

### 13.7 Bus System (Complete Reference)

#### 13.7.1 Bus Types

| Bus Type | Purpose | Priority Queue | Backpressure |
|----------|---------|----------------|-------------|
| `structural_bus` | Structural signals | Yes | Yes |
| `integrity_bus` | Integrity signals | Yes | Yes |
| `epistemic_bus` | Epistemic signals | Yes | Yes |
| `contrast_bus` | Contrast signals | Yes | Yes |
| `operational_bus` | Operational signals | Yes | Yes |
| `consumption_bus` | Consumption signals | Yes | Yes |
| `universal_bus` | All signals | Yes | Yes |

#### 13.7.2 Bus Configuration

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config/bus_config.yaml`

```yaml
buses:
  structural_bus:
    queue_size: 50000
    backpressure_threshold: 0.8
    enable_persistence: true
    enable_priority: true

  integrity_bus:
    queue_size: 50000
    backpressure_threshold: 0.8
    enable_persistence: true
    enable_priority: true

  # ... (similar for other buses)
```

#### 13.7.3 Bus Operations

```python
# Publishing to a bus
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import (
    BusRegistry,
    PublicationContract
)

# Get bus registry
bus_registry = BusRegistry()

# Get specific bus
bus = bus_registry.get_bus("structural_bus")

# Create publication contract
contract = PublicationContract(
    publisher_id="my_vehicle",
    signal_types=["StructuralAlignmentSignal"],
    allowed_buses=["structural_bus"],
    status=ContractStatus.ACTIVE
)

# Publish signal
success, message_id = bus.publish(
    signal=signal,
    publisher_vehicle="my_vehicle",
    publication_contract=contract,
    priority=MessagePriority.HIGH
)
```

### 13.8 SISAS Metrics (Complete Reference)

#### 13.8.1 Bus-Level Metrics

```python
# Get bus statistics
bus = bus_registry.get_bus("structural_bus")
stats = bus.get_stats()

# Available metrics:
{
    "total_published": int,        # Total signals published
    "total_delivered": int,        # Total signals delivered
    "total_rejected": int,         # Total signals rejected
    "total_errors": int,           # Total errors
    "total_retries": int,          # Total retries
    "total_expired": int,          # Total expired signals
    "total_dead_lettered": int     # Total dead-lettered
}
```

#### 13.8.2 Advanced Metrics

```python
# Get advanced bus metrics
metrics = bus.get_advanced_metrics()

# Available metrics:
{
    "queue_size": int,                    # Current queue size
    "queue_utilization": float,           # 0.0-1.0
    "backpressure_active": bool,          # Backpressure status
    "dead_letter_count": int,             # Dead letter queue size
    "latency_ms": {
        "avg": float,                     # Average latency
        "p50": float,                    # 50th percentile
        "p95": float,                    # 95th percentile
        "p99": float                     # 99th percentile
    },
    "throughput_per_sec": float,          # Messages/second
    "consumers": {
        "total": int,                    # Total consumers
        "healthy": int,                  # Healthy consumers
        "unhealthy": int                 # Unhealthy consumers
    },
    "history_size": int                   # Message history size
}
```

#### 13.8.3 Consumer Health Metrics

```python
# Get consumer health report
health = bus.get_consumer_health_report()

# Per-consumer metrics:
{
    "consumer_id": {
        "consecutive_failures": int,      # Consecutive failures
        "circuit_open": bool,            # Circuit breaker state
        "circuit_opened_at": timestamp,   # When circuit opened
        "total_successes": int,          # Total successes
        "total_failures": int            # Total failures
    }
}
```

### 13.9 SISAS Configuration

#### 13.9.1 Vocabulary Configuration

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config/vocabulary_config.yaml`

```yaml
vocabulary:
  signal_types:
    structural:
      - StructuralAlignmentSignal
      - SchemaConflictSignal
      - CanonicalMappingSignal
    integrity:
      - EventPresenceSignal
      - EventCompletenessSignal
      - DataIntegritySignal
    # ... (other categories)

  validation:
    strict_mode: true
    enable_cache: true
    cache_size: 1000
```

#### 13.9.2 Irrigation Configuration

**File**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config/irrigation_config.yaml`

```yaml
irrigation:
  phases:
    - name: JF0
      description: "Containment"
      executor: "containment_executor"
    - name: JF1
      description: "Observation"
      executor: "observation_executor"
    # ... (phases JF2-JF10)

  vehicles:
    signal_registry:
      enabled: true
      priority: 1
    signal_context_scoper:
      enabled: true
      priority: 2
    # ... (other vehicles)

  execution:
    max_parallel_phases: 3
    timeout_seconds: 300
    enable_retry: true
    max_retries: 3
```

### 13.10 SISAS Health and Monitoring

#### 13.10.1 Health Check Command

```bash
# SISAS health check
python -m SISAS.main health \
    --bus-stats \
    --consumer-health \
    --vehicle-status \
    --output health_report.json
```

#### 13.10.2 Health Status Endpoint

```python
# Programmatic health check
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import BusRegistry

bus_registry = BusRegistry()
health = bus_registry.get_health_status()

# Health status structure:
{
    "buses": {
        "structural_bus": {
            "status": "healthy",  # or "degraded"
            "stats": {...},
            "subscribers": int,
            "pending_messages": int
        },
        # ... (other buses)
    },
    "overall_status": "healthy",  # or "degraded"
    "total_messages": int,
    "total_errors": int,
    "total_rejected": int
}
```

---

## 14. Metrics, Health, and Observability

### 14.1 System Overview

The F.A.R.F.A.N. pipeline implements **comprehensive monitoring infrastructure** with metrics collection at multiple levels: executor, phase, system, and SISAS signal bus.

### 14.2 Metrics Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        METRICS HIERARCHY                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  SYSTEM LEVEL (Orchestrator)                                                  │
│  ├── Pipeline duration                                                        │
│  ├── Phase transition rates                                                   │
│  ├── Resource utilization (CPU, memory)                                       │
│  └── Error rates by phase                                                     │
│                                                                                 │
│  PHASE LEVEL (Each Phase 0-9)                                                 │
│  ├── Input/output artifact counts                                             │
│  ├── Compression ratios                                                        │
│  ├── Quality metrics                                                           │
│  └── SISAS signal counts                                                       │
│                                                                                 │
│  EXECUTOR LEVEL (30 Base Executors)                                            │
│  ├── Execution time per executor                                             │
│  ├── Method call counts                                                       │
│  ├── Pattern match rates                                                     │
│  ├── Circuit breaker trips                                                    │
│  └── Memory footprint                                                         │
│                                                                                 │
│  SISAS SIGNAL LEVEL (6 Buses)                                                  │
│  ├── Signal publication rates                                                 │
│  ├── Signal consumption rates                                                │
│  ├── Bus queue utilization                                                    │
│  ├── Consumer health metrics                                                  │
│  └── Circuit breaker states                                                   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 14.3 Executor Performance Profiler

**File**: `src/farfan_pipeline/phases/Phase_02/phase2_95_00_executor_profiler.py`

**Capabilities**:
- Per-executor timing, memory, and serialization metrics
- Method call tracking with granular statistics
- Performance regression detection
- Dispensary pattern awareness (tracking monolith reuse)
- Bottleneck identification with recommendations
- Baseline comparison capabilities

```python
# Executor profiler usage
from farfan_pipeline.phases.Phase_02.phase2_95_00_executor_profiler import (
    ExecutorProfiler,
    ProfilerConfig
)

# Create profiler
profiler = ExecutorProfiler(
    config=ProfilerConfig(
        enable_timing=True,
        enable_memory_tracking=True,
        enable_serialization_tracking=True,
        baseline_comparison=True
    )
)

# Profile executor execution
with profiler.profile_executor(executor_id="D1-Q1"):
    result = executor.execute(document, signal_pack)

# Get profiling report
report = profiler.get_report(executor_id="D1-Q1")

# Report structure:
{
    "executor_id": "D1-Q1",
    "execution_time_ms": float,
    "memory_mb": float,
    "serialization_time_ms": float,
    "serialization_size_bytes": int,
    "method_calls": {
        "PDETMunicipalPlanAnalyzer._score_indicators": {
            "call_count": int,
            "total_time_ms": float,
            "avg_time_ms": float
        },
        # ... (other methods)
    },
    "performance_baseline": {
        "expected_time_ms": float,
        "deviation_percent": float,
        "regression_detected": bool
    },
    "bottlenecks": [
        {
            "method": "PDETMunicipalPlanAnalyzer._score_indicators",
            "issue": "high_latency",
            "recommendation": "Consider caching indicator results"
        }
    ]
}
```

### 14.4 Metrics Persistence

**File**: `src/farfan_pipeline/phases/Phase_02/phase2_95_01_metrics_persistence.py`

**Capabilities**:
- Phase metrics export to JSON
- Resource usage history tracking (JSONL format)
- Latency histograms for percentile analysis
- Schema validation for metrics data

```python
# Metrics persistence
from farfan_pipeline.phases.Phase_02.phase2_95_01_metrics_persistence import (
    MetricsExporter,
    MetricsPersistenceConfig
)

# Export phase metrics
exporter = MetricsExporter(
    config=MetricsPersistenceConfig(
        output_dir="artifacts/phase2/metrics",
        format="json",
        enable_histograms=True
    )
)

# Export metrics
exporter.export_phase_metrics(
    phase_id="phase_02",
    metrics=profiler.get_all_reports()
)

# Export resource usage history
exporter.export_resource_history(
    history_data=resource_monitor.get_history(),
    format="jsonl"
)
```

### 14.5 Circuit Breaker Monitoring

**File**: `src/farfan_pipeline/phases/Phase_02/phase2_30_04_circuit_breaker.py`

**Metrics Exposed**:
- Circuit breaker state per executor
- Consecutive failure count
- Circuit open/close timestamps
- Recovery success rates

```python
# Circuit breaker monitoring
from farfan_pipeline.phases.Phase_02.phase2_30_04_circuit_breaker import (
    CircuitBreakerRegistry,
    CircuitBreakerState
)

# Get all breaker states
registry = CircuitBreakerRegistry()
breakers = registry.get_all_breakers()

for executor_id, breaker in breakers.items():
    print(f"{executor_id}: {breaker.state}")
    print(f"  Failures: {breaker.failure_count}")
    print(f"  Last failure: {breaker.last_failure_time}")
    print(f"  Success rate: {breaker.success_rate:.2%}")
```

### 14.6 Health Check Endpoints

#### 14.6.1 API Health Endpoints

**File**: `src/farfan_pipeline/api/api_server.py`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Basic health check |
| `/api/v1/status` | GET | Detailed pipeline status |

```bash
# Health check
curl http://localhost:8000/health

# Pipeline status
curl http://localhost:8000/api/v1/status

# Response structure:
{
    "status": "healthy",
    "timestamp": "2026-01-17T12:00:00Z",
    "components": {
        "orchestrator": "healthy",
        "method_executor": "healthy",
        "signal_registry": "healthy",
        "phase_00": "completed",
        "phase_01": "completed",
        # ... (other phases)
    },
    "metrics": {
        "total_phases": 10,
        "completed_phases": 10,
        "failed_phases": 0,
        "total_duration_ms": 15000
    }
}
```

#### 14.6.2 Dashboard Health Endpoints

**File**: `src/farfan_pipeline/dashboard_atroz_/dashboard_server.py`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/metrics` | GET | Real-time system metrics |
| `/api/pdet-regions` | GET | PDET regions data |
| `/api/evidence` | GET | Evidence stream |

```bash
# System metrics
curl http://localhost:5000/api/metrics

# Response structure:
{
    "cpu_usage_percent": 45.2,
    "memory_usage_mb": 1024,
    "active_jobs": 3,
    "uptime_seconds": 3600,
    "sisas": {
        "total_signals": 15000,
        "signals_per_second": 12.5,
        "active_consumers": 8
    }
}
```

### 14.7 Signal Registry Health Checks

**File**: `tests/test_signal_registry_health_checks.py`

**Validates**:
- All 300 micro-questions have signal presence
- Signal shape validation (patterns, expected_elements, modalities)
- Production mode enforcement with fail-fast behavior
- Registry staleness detection
- Circuit breaker state monitoring

```python
# Signal registry health check
from tests.test_signal_registry_health_checks import (
    SignalRegistryHealthChecker
)

checker = SignalRegistryHealthChecker(
    strict_mode=True  # Fail-fast on errors
)

# Run health check
report = checker.check_all_micro_questions()

# Report structure:
{
    "status": "PASS",  # or "WARN" or "FAIL"
    "timestamp": "2026-01-17T12:00:00Z",
    "checks": {
        "total_questions": 300,
        "questions_with_signals": 300,
        "questions_without_signals": 0,
        "signal_shape_valid": 300,
        "signal_shape_invalid": 0
    },
    "details": [
        {
            "question_id": "Q001",
            "policy_area": "PA01",
            "signals_present": true,
            "shape_valid": true
        },
        # ... (other questions)
    ]
}
```

### 14.8 Monitoring Configuration

**File**: `docs/MONITORING_CONFIG.md`

**Prometheus/Grafana Integration**:

```yaml
# Prometheus alert rules
groups:
  - name: farfan_pipeline
    rules:
      - alert: HighErrorRate
        expr: error_rate > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: ExecutorFailureRate
        expr: executor_failure_rate > 0.1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Executor failure rate exceeded threshold"

      - alert: CircuitBreakerOpen
        expr: circuit_breaker_open_count > 0
        labels:
          severity: critical
        annotations:
          summary: "Circuit breaker opened"
```

### 14.9 Schema Monitoring

**File**: `src/farfan_pipeline/phases/Phase_00/primitives/schema_monitor.py`

**Capabilities**:
- Schema drift detection
- Payload sampling and validation
- Alert generation for schema changes
- Shape tracking over time
- Type consistency monitoring

```python
# Schema monitoring
from farfan_pipeline.phases.Phase_00.primitives.schema_monitor import (
    SchemaMonitor,
    MonitorConfig
)

monitor = SchemaMonitor(
    config=MonitorConfig(
        sampling_rate=0.1,  # Sample 10% of payloads
        alert_on_drift=True,
        track_shapes=True
    )
)

# Monitor payload
monitor.observe_payload(
    payload=evidence_bundle,
    schema_name="EvidenceBundle",
    phase="phase_02"
)

# Get drift report
drift_report = monitor.get_drift_report(
    since="2026-01-01T00:00:00Z"
)
```

---

## 15. Canonical Central and JSON Visualization

### 15.1 System Overview

**Canonical Central** is the authoritative source for all questionnaire data, including 300 micro-questions, 4 meso-questions, 1 macro-question, 6 dimensions, and 10 policy areas.

### 15.2 Canonical Directory Structure

```
canonic_questionnaire_central/
├── questionnaire_monolith.json        # Main questionnaire (immutable)
├── config/
│   ├── questionnaire_schema.json     # JSON schema for validation
│   ├── canonical_notation.json      # 6 dimensions + 10 policy areas
│   ├── enrichment_config.example.yaml
│   └── modular_manifest.json
└── _registry/
    ├── capabilities/                 # Signal-capability mappings
    │   └── schema.json
    ├── entities/                      # Entity definitions
    │   ├── institutions.json
    │   ├── normative.json
    │   ├── population.json
    │   ├── territorial.json
    │   └── international.json
    │   └── schema.json
    ├── keywords/                      # PA keyword mappings
    │   └── schema.json
    ├── membership_criteria/          # Membership criteria
    │   └── schema.json
    └── patterns/                      # Pattern definitions
        └── schema.json
```

### 15.3 Canonical Structure

**File**: `canonic_questionnaire_central/config/canonical_notation.json`

```json
{
  "dimensions": {
    "DIM01": {
      "id": "DIM01",
      "name": "INSUMOS",
      "description": "Resources allocated to policy implementation",
      "weight": 1.0
    },
    "DIM02": {
      "id": "DIM02",
      "name": "ACTIVIDADES",
      "description": "Actions taken to implement policy",
      "weight": 1.0
    },
    "DIM03": {
      "id": "DIM03",
      "name": "PRODUCTOS",
      "description": "Direct outputs from policy implementation",
      "weight": 1.0
    },
    "DIM04": {
      "id": "DIM04",
      "name": "RESULTADOS",
      "description": "Medium-term effects of policy implementation",
      "weight": 1.0
    },
    "DIM05": {
      "id": "DIM05",
      "name": "IMPACTOS",
      "description": "Long-term effects and societal changes",
      "weight": 1.0
    },
    "DIM06": {
      "id": "DIM06",
      "name": "CAUSALIDAD",
      "description": "Causal relationships between activities and outcomes",
      "weight": 1.0
    }
  },
  "policy_areas": {
    "PA01": {
      "id": "PA01",
      "name": "Marco Legal e Institucional",
      "description": "Legal and institutional framework",
      "keywords": ["ley", "norma", "decreto", "resolución", "jurídico", "legal"],
      "cluster": "CLUSTER_MESO_1"
    },
    "PA02": {
      "id": "PA02",
      "name": "Planeación y Articulación",
      "description": "Planning and coordination",
      "keywords": ["plan", "articulación", "coordinación", "alineación"],
      "cluster": "CLUSTER_MESO_1"
    },
    # ... (8 more policy areas)
  }
}
```

### 15.4 Inspection Commands

```bash
# Validate canonical structure
python scripts/validation/semantic_validator.py \
    --canonical-path canonic_questionnaire_central/questionnaire_monolith.json

# Generate canonical visualization
python scripts/generate_signals_full_map.py \
    --output canonical_visualization.json

# Extract canonical mappings
python scripts/validation/verify_contract_signal_wiring.py \
    --canonical-path canonic_questionnaire_central/questionnaire_monolith.json \
    --output mappings.json
```

### 15.5 Canonical Comparison

```python
# Compare two canonical versions
from farfan_pipeline.core.canonical import CanonicalComparator

comparator = CanonicalComparator(
    baseline_path="v1.0/questionnaire_monolith.json",
    current_path="v1.1/questionnaire_monolith.json"
)

# Run comparison
diff = comparator.compare()

# Diff structure:
{
    "questions_added": [
        {"question_id": "Q301", "text": "..."}
    ],
    "questions_removed": [
        {"question_id": "Q250", "text": "..."}
    ],
    "questions_modified": [
        {
            "question_id": "Q001",
            "field": "expected_elements",
            "old_value": ["TABLE"],
            "new_value": ["TABLE", "FIGURE"]
        }
    ],
    "dimensions_changed": [],
    "policy_areas_changed": []
}
```

### 15.6 Divergence Analysis

```python
# Analyze divergence from canonical
from farfan_pipeline.core.canonical import DivergenceAnalyzer

analyzer = DivergenceAnalyzer(
    canonical_path="canonic_questionnaire_central/questionnaire_monolith.json",
    actual_path="artifacts/phase2/evidence_bundle.json"
)

# Analyze divergence
divergence = analyzer.analyze()

# Divergence structure:
{
    "total_questions": 300,
    "canonical_compliant": 295,
    "divergent": 5,
    "divergences": [
        {
            "question_id": "Q001",
            "expected_pa": "PA01",
            "actual_pa": "PA02",
            "divergence_type": "policy_area_mismatch",
            "severity": "medium"
        }
    ]
}
```

### 15.7 Historical Traceability

```python
# Trace canonical history
from farfan_pipeline.core.canonical import CanonicalHistory

history = CanonicalHistory()

# Get version history
versions = history.get_versions("questionnaire_monolith.json")

# Structure:
[
    {
        "version": "1.0",
        "timestamp": "2026-01-01T00:00:00Z",
        "sha256": "abc123...",
        "changes": ["Initial version"],
        "author": "system"
    },
    {
        "version": "1.1",
        "timestamp": "2026-01-15T00:00:00Z",
        "sha256": "def456...",
        "changes": ["Updated Q001 expected_elements"],
        "author": "admin"
    }
]
```

### 15.8 SISAS Commands for Canonical Central

```bash
# SISAS canonical validation
python -m SISAS.main check --canonical-path canonic_questionnaire_central/

# Generate canonical signals
python -m SISAS.main run \
    --csv-path canonical_sabana.csv \
    --base-path canonic_questionnaire_central/ \
    --phase JF5  # Generate canonical signals phase

# Audit canonical structure
python -m SISAS.main audit \
    --scope canonical \
    --output canonical_audit.json
```

---

## 16. Orchestration Commands

### 16.1 Main Orchestrator CLI

**File**: `src/farfan_pipeline/orchestration/cli.py`

```bash
# Main orchestrator CLI
python -m farfan_pipeline.orchestration.cli \
    --start-phase 0 \
    --end-phase 9 \
    --configuration production \
    --strict-validation \
    --deterministic-mode \
    --seed 42

# Available flags:
# --start-phase: Starting phase (0-9)
# --end-phase: Ending phase (0-9)
# --configuration: Configuration preset (development|production|testing)
# --strict-validation: Enable strict validation (fail fast on errors)
# --deterministic-mode: Enable deterministic execution
# --seed: Master seed for RNG
# --output-dir: Output directory for artifacts
# --log-level: Logging level (DEBUG|INFO|WARNING|ERROR)
# --json-output: Enable JSON output format
# --save-state: Save intermediate state
```

### 16.2 Orchestrator Python API

```python
# Programmatic orchestration
from farfan_pipeline.orchestration.core_orchestrator import CoreOrchestrator
from farfan_pipeline.phases.Phase_00.phase0_90_01_verified_pipeline_runner import (
    VerifiedPipelineRunner
)
from farfan_pipeline.phases.Phase_00.phase0_50_01_exit_gates import (
    check_all_gates
)

# Create orchestrator with all dependencies
orchestrator = CoreOrchestrator(
    config={
        "start_phase": 0,
        "end_phase": 9,
        "strict_validation": True,
        "deterministic_mode": True,
        "seed": 42
    }
)

# Execute pipeline
result = orchestrator.execute_pipeline()

# Result structure:
{
    "status": "completed",  # or "failed" or "partial"
    "phases_completed": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    "phases_failed": [],
    "phases_skipped": [],
    "total_duration_ms": 15000,
    "artifacts": {
        "phase_00": "artifacts/phase0/gates.json",
        "phase_01": "artifacts/phase1/chunk_manifest.json",
        # ... (other phases)
    },
    "macro_score": {
        "value": 2.35,
        "quality_level": "BUENO",
        "normalized": 0.78
    }
}
```

### 16.3 Introspection Commands

```bash
# Introspect pipeline graph
python -m farfan_pipeline.orchestration.cli --introspect-graph

# Introspect phase dependencies
python -m farfan_pipeline.orchestration.cli --introspect-dependencies

# Introspect execution order
python -m farfan_pipeline.orchestration.cli --introspect-order

# Verify determinism
python -m farfan_pipeline.orchestration.cli --verify-determinism --seed 42
```

### 16.4 Control Commands

```bash
# Execute specific phase
python -m farfan_pipeline.orchestration.cli --execute-phase 2 --no-dependencies

# Execute phase range
python -m farfan_pipeline.orchestration.cli --start-phase 4 --end-phase 6

# Skip phase
python -m farfan_pipeline.orchestration.cli --skip-phase 5

# Retry failed phase
python -m farfan_pipeline.orchestration.cli --retry-phase 3 --max-retries 3
```

### 16.5 SISAS Orchestration Integration

```python
# Orchestrator with SISAS monitoring
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import BusRegistry

# Create bus registry for SISAS monitoring
bus_registry = BusRegistry()

# Execute pipeline with SISAS integration
orchestrator = CoreOrchestrator(
    config={
        "enable_sisas_monitoring": True,
        "bus_registry": bus_registry,
        "sisas_metrics_interval_ms": 1000
    }
)

# SISAS metrics will be published to buses during execution
result = orchestrator.execute_pipeline()
```

---

## 17. Factory Pattern

### 17.1 AnalysisPipelineFactory

**File**: `src/farfan_pipeline/phases/Phase_02/phase2_10_00_factory.py`

**Factory Responsibilities** (SINGLE AUTHORITATIVE BOUNDARY):
- Canonical monolith access (CanonicalQuestionnaire) - loaded ONCE with integrity verification
- Signal registry construction (QuestionnaireSignalRegistry v2.0) from canonical source ONLY
- Method injection via MethodExecutor with signal registry DI
- Orchestrator construction with full DI (questionnaire, method_executor, executor_config)
- EnrichedSignalPack creation and injection per executor (30 executors)
- Hard contracts and validation constants for Phase 1
- SeedRegistry singleton initialization for determinism
- Phase 0 integration (RuntimeConfig, Phase0ValidationResult)

### 17.2 Factory Construction Sequence

```python
# Factory usage
from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
    AnalysisPipelineFactory
)

# Create factory with all dependencies
factory = AnalysisPipelineFactory(
    questionnaire_path="canonic_questionnaire_central/questionnaire_monolith.json",
    expected_questionnaire_hash="abc123...",
    runtime_config=None,  # Loaded from environment
    executor_config=None,  # Uses default
    validation_constants=None,  # Loads from config
    enable_intelligence_layer=True,
    seed_for_determinism=42,
    strict_validation=True,
    run_phase0_validation=True
)

# Create orchestrator (10-step construction process)
bundle = factory.create_orchestrator()

# Access components
orchestrator = bundle.orchestrator
method_executor = bundle.method_executor
questionnaire = bundle.questionnaire
signal_registry = bundle.signal_registry
```

### 17.3 Factory Steps

| Step | Operation | Output |
|------|-----------|--------|
| 0 | Phase 0 validation | Phase0ValidationResult |
| 1 | Load canonical questionnaire | CanonicalQuestionnaire (immutable) |
| 2 | Build signal registry | QuestionnaireSignalRegistry v2.0 |
| 3 | Build enriched signal packs | dict[str, EnrichedSignalPack] |
| 4 | Initialize seed registry | SeedRegistry (singleton) |
| 5 | Build method executor | MethodExecutor (348 methods) |
| 6 | Load validation constants | dict[str, Any] |
| 7 | Get executor config | ExecutorConfig |
| 8 | Build orchestrator | Orchestrator |
| 9 | Assemble provenance | dict[str, Any] |
| 10 | Build bundle | ProcessorBundle |

### 17.4 Singleton Enforcement

```python
# Questionnaire singleton (load once)
AnalysisPipelineFactory._questionnaire_loaded = False
AnalysisPipelineFactory._questionnaire_instance = None

# First call loads questionnaire
bundle1 = factory.create_orchestrator()  # Loads questionnaire

# Second call reuses questionnaire
bundle2 = factory.create_orchestrator()  # Reuses cached instance

# Singleton pattern is enforced
assert bundle1.questionnaire is bundle2.questionnaire  # Same object
```

### 17.5 Factory Validation

```python
# Validate factory operations
from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
    validate_factory_singleton,
    validate_bundle,
    validate_method_dispensary_pattern
)

# Validate singleton
singleton_status = validate_factory_singleton()
# {
#     "questionnaire_loaded": True,
#     "questionnaire_instance_exists": True,
#     "singleton_pattern_valid": True
# }

# Validate bundle
bundle_health = validate_bundle(bundle)
# {
#     "valid": True,
#     "errors": [],
#     "warnings": [],
#     "components": {...},
#     "metrics": {...}
# }
```

---

## 18. Calibration System

### 18.1 Epistemological Calibration

**File**: `src/farfan_pipeline/infrastructure/calibration/config/method_registry_epistemic.json`

**Purpose**: Assigns epistemological levels (N0-N4) to 195+ methods based on analytical depth.

**Epistemological Levels**:
- **N0-INFRA**: Infrastructure methods (no domain knowledge required)
- **N1-DESCRIPTIVE**: Descriptive methods (basic pattern recognition)
- **N2-ANALYTICAL**: Analytical methods (correlation, basic inference)
- **N3-CAUSAL**: Causal methods (causal inference, counterfactuals)
- **N4-META**: Meta-analytical methods (system-level synthesis)

```python
# Load calibration data
from farfan_pipeline.infrastructure.calibration.config.method_registry_epistemic import (
    load_epistemic_registry
)

registry = load_epistemic_registry()

# Method epistemological level
level = registry.get_method_level(
    class_name="PDETMunicipalPlanAnalyzer",
    method_name="_score_indicators"
)
# Returns: "N2-ANALYTICAL"

# Get all methods by level
analytical_methods = registry.get_methods_by_level("N2-ANALYTICAL")
# Returns: list of (class_name, method_name) tuples
```

### 18.2 Empirical Calibration

**File**: `calibration/empirical.json`

**Purpose**: Stores empirical baselines extracted from historical policy evaluations.

```json
{
  "baselines": {
    "dimension_scores": {
      "DIM01": {
        "mean": 1.8,
        "std": 0.4,
        "min": 0.5,
        "max": 2.8,
        "sample_count": 150
      },
      "...": "other dimensions"
    },
    "area_scores": {
      "PA01": {
        "mean": 1.9,
        "std": 0.3,
        "min": 1.0,
        "max": 2.7,
        "sample_count": 150
      },
      "...": "other areas"
    }
  }
}
```

### 18.3 Calibration Application

```python
# Apply calibration to scores
from farfan_pipeline.phases.Phase_02.phase2_95_03_executor_calibration_integration import (
    CalibrationIntegration
)

calibration = CalibrationIntegration(
    calibration_data_path="calibration/empirical.json"
)

# Calibrate score
raw_score = 2.0
calibrated_score = calibration.calibrate_score(
    score=raw_score,
    question_id="Q001",
    policy_area="PA01",
    dimension="DIM01"
)
# Returns: score adjusted based on empirical baseline
```

---

## 19. Parametrization

### 19.1 Parameter Sources (Priority Order)

1. **Empirical Weights** (highest priority) - Derived from data analysis
2. **Environment Variables** - Runtime overrides
3. **Configuration Files** - Default values

### 19.2 Environment Variables

```bash
# Runtime configuration
export FARFAN_MODE=PROD|DEV|TEST
export FARFAN_SEED=42
export FARFAN_STRICT_VALIDATION=true

# Phase-specific parameters
export FARFAN_P1_CHUNK_COUNT=60
export FARFAN_P2_EXECUTOR_COUNT=30
export FARFAN_P3_SCORE_DOMAIN_MIN=0.0
export FARFAN_P3_SCORE_DOMAIN_MAX=3.0

# SISAS parameters
export FARFAN_SISAS_SIGNAL_SOURCE=memory://
export FARFAN_SISAS_BUS_QUEUE_SIZE=50000
export FARFAN_SISAS_ENABLE_BACKPRESSURE=true
```

### 19.3 Configuration File Loading

**File**: `src/farfan_pipeline/config/threshold_config.py`

```python
# Load configuration with priority override
from farfan_pipeline.config.threshold_config import (
    load_thresholds
)

# Load with environment variable overrides
thresholds = load_thresholds(
    config_path="src/farfan_pipeline/config/signal_scoring_thresholds.json",
    enable_env_overrides=True
)

# Priority: empirical > env vars > config file
```

### 19.4 Parameter Validation

```python
# Validate parameters
from farfan_pipeline.core.validation import ParameterValidator

validator = ParameterValidator()

# Validate score domain
validator.validate_range(
    value=2.5,
    min_value=0.0,
    max_value=3.0,
    parameter_name="score"
)

# Validate enum
validator.validate_enum(
    value="PROD",
    allowed_values=["PROD", "DEV", "TEST"],
    parameter_name="mode"
)
```

---

## 20. Indirect Modules

### 20.1 Indirect Module Categories

1. **Utilities** - Helper functions and classes
2. **Extractors** - Domain-specific data extractors
3. **Analyzers** - Policy analysis components
4. **Validators** - Data and schema validation
5. **Monitors** - System monitoring components

### 20.2 Extractor Modules

**Location**: `src/farfan_pipeline/infrastructure/extractors/`

| Extractor | Purpose | Methods |
|----------|---------|---------|
| `FinancialChainExtractor` | Extract financial chains | trace_budgets, detect_gaps |
| `CausalChainExtractor` | Extract causal chains | extract_causality, detect_conflicts |
| `InstitutionalEntityExtractor` | Extract institutional entities | extract_institutions, classify_roles |
| `NormativeReferenceExtractor` | Extract normative references | extract_laws, extract_regulations |
| `QuantitativeTripletExtractor` | Extract quantitative triplets | extract_budgets, extract_targets |

### 20.3 Analyzer Modules

**Location**: `src/farfan_pipeline/analyzers/`

| Analyzer | Purpose | Methods |
|----------|---------|---------|
| `PolicyCoherenceAnalyzer` | Analyze policy coherence | detect_conflicts, check_alignment |
| `GoalHierarchyAnalyzer` | Analyze goal structures | extract_goals, validate_hierarchy |
| `InterventionAnalyzer` | Analyze interventions | classify_interventions, detect_duplicates |
| `RiskAnalyzer` | Analyze policy risks | assess_probability, estimate_impact |

### 20.4 Validation Modules

**Location**: `src/farfan_pipeline/validators/`

| Validator | Purpose | Methods |
|-----------|---------|---------|
| `Phase1OutputValidator` | Validate Phase 1 output | validate_matrix_coordinates, validate_manifest |
| `SchemaValidator` | Validate JSON schemas | validate_schema, detect_drift |
| `ContractValidator` | Validate contracts | validate_contract, check_completeness |
| `SignalValidator` | Validate SISAS signals | validate_signal, check_shape |

---

## 21. Troubleshooting Guide

### 21.1 Common Issues and Solutions

#### 21.1.1 Phase 0 Failures

**Issue**: Exit gate failure

```bash
# Check exit gate details
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main --verbose

# Common failures:
# - Python version < 3.10 → Upgrade Python
# - Missing dependencies → pip install -r requirements.txt
# - Questionnaire hash mismatch → Verify input file
```

#### 21.1.2 Phase 2 Failures

**Issue**: Executor construction failure

```bash
# Check executor contracts
python -m farfan_pipeline.phases.Phase_02.phase2_10_00_factory --validate-contracts

# Common failures:
# - Missing method in registry → Check canonical_methods_triangulated.json
# - Circuit breaker open → Wait for timeout or reset breaker
# - Signal pack missing → Check QuestionnaireSignalRegistry
```

#### 21.1.3 SISAS Failures

**Issue**: Bus not receiving signals

```bash
# Check SISAS health
python -m SISAS.main health --bus-stats

# Common failures:
# - Bus not subscribed → Check consumer subscriptions
# - Contract validation failed → Check signal contracts
# - Circuit breaker open → Check consumer health
```

### 21.2 Debug Mode

```bash
# Enable debug logging
export FARFAN_LOG_LEVEL=DEBUG

# Run with verbose output
farfan-pipeline --start-phase 0 --end-phase 9 --verbose

# Enable SISAS tracing
export FARFAN_SISAS_TRACE=true
```

### 21.3 Recovery Procedures

```bash
# Reset circuit breakers
python scripts/reset_circuit_breakers.py

# Clear SISAS cache
python scripts/clear_sisas_cache.py

# Rebuild signal registry
python scripts/rebuild_signal_registry.py
```

---

## 22. Complete Command Index

### 22.1 Primary Commands

| Command | Purpose | Location |
|---------|---------|----------|
| `farfan-pipeline` | Main pipeline CLI | `orchestration/cli.py` |
| `farfan_core-api` | API server | `api/api_server.py` |
| `enrichment-cli` | Enrichment operations | `scripts/enrichment_cli.py` |
| `SISAS.main` | SISAS operations | `SISAS/main.py` |

### 22.2 Phase Commands

| Command | Phase | Arguments |
|---------|-------|----------|
| `phase0_90_00_main` | 0 | `--plan-pdf`, `--questionnaire`, `--mode` |
| `phase0_90_01_verified_pipeline_runner` | 0 | `--plan-pdf`, `--questionnaire` |
| `phase2_10_00_factory` | 2 | `questionnaire_path`, `expected_hash`, `seed` |

### 22.3 Utility Commands

| Command | Purpose | Script |
|---------|---------|--------|
| `generate_sabana_final.py` | Generate final sabana | `scripts/` |
| `generate_signals_full_map.py` | Generate signal map | `scripts/` |
| `extract_300_contracts.py` | Extract contracts | `scripts/` |
| `semantic_validator.py` | Validate semantics | `scripts/validation/` |
| `verify_contract_signal_wiring.py` | Verify signal wiring | `scripts/validation/` |

### 22.4 SISAS Commands

| Command | Purpose | Arguments |
|---------|---------|----------|
| `run` | Execute irrigation | `--csv-path`, `--base-path`, `--phase`, `--all` |
| `check` | Check vocabulary | `--signal-types`, `--capabilities`, `--full` |
| `contracts` | Generate contracts | `--csv-path`, `--output`, `--format` |
| `stats` | Show statistics | `--csv-path`, `--by-phase`, `--by-vehicle` |
| `health` | Check health | `--bus-stats`, `--consumer-health`, `--vehicle-status` |
| `audit` | Run audit | `--scope`, `--output` |

---

## 23. Configuration Reference

### 23.1 Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `pyproject.toml` | Project configuration | TOML |
| `.pre-commit-config.yaml` | Pre-commit hooks | YAML |
| `signal_scoring_thresholds.json` | Scoring thresholds | JSON |
| `bus_config.yaml` | SISAS bus configuration | YAML |
| `irrigation_config.yaml` | SISAS irrigation config | YAML |
| `vocabulary_config.yaml` | SISAS vocabulary config | YAML |
| `questionnaire_schema.json` | Questionnaire schema | JSON |
| `canonical_notation.json` | Dimensions and PAs | JSON |
| `method_registry_epistemic.json` | Epistemological levels | JSON |

### 23.2 Configuration Precedence

1. **Empirical weights** (highest)
2. **Environment variables**
3. **Configuration files**
4. **Default values** (lowest)

### 23.3 Runtime Configuration

```python
# RuntimeConfig structure
RuntimeConfig(
    mode=RuntimeMode.PROD,      # PROD | DEV | TEST
    log_level="INFO",
    enable_strict_validation=True,
    max_retries=3,
    timeout_seconds=300,
    enable_sisas_monitoring=True,
    enable_profiling=True,
    enable_cache=True
)
```

---

## Appendix A: SISAS Signal Type Reference

### A.1 Signal Type Hierarchy

```
Signal (base)
├── StructuralSignal
│   ├── StructuralAlignmentSignal
│   ├── SchemaConflictSignal
│   └── CanonicalMappingSignal
├── IntegritySignal
│   ├── EventPresenceSignal
│   ├── EventCompletenessSignal
│   └── DataIntegritySignal
├── EpistemicSignal
│   ├── AnswerDeterminacySignal
│   ├── AnswerSpecificitySignal
│   ├── EmpiricalSupportSignal
│   └── MethodApplicationSignal
├── ContrastSignal
│   ├── DecisionDivergenceSignal
│   ├── ConfidenceDropSignal
│   └── TemporalContrastSignal
├── OperationalSignal
│   ├── ExecutionAttemptSignal
│   ├── FailureModeSignal
│   ├── LegacyActivitySignal
│   └── LegacyDependencySignal
└── ConsumptionSignal
    ├── FrequencySignal
    ├── TemporalCouplingSignal
    └── ConsumerHealthSignal
```

### A.2 Signal Schema

```json
{
  "$schema": "signal_schema.json",
  "type": "object",
  "properties": {
    "signal_id": {"type": "string"},
    "signal_type": {"type": "string", "enum": ["StructuralAlignmentSignal", "EventPresenceSignal", "..."]},
    "context": {
      "type": "object",
      "properties": {
        "phase": {"type": "string"},
        "policy_area": {"type": "string"},
        "dimension": {"type": "string"}
      }
    },
    "source": {"type": "string"},
    "value": {},
    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "rationale": {"type": "string"},
    "timestamp": {"type": "string", "format": "date-time"},
    "version": {"type": "integer"}
  },
  "required": ["signal_id", "signal_type", "context", "source"]
}
```

---

## Appendix B: Complete Phase Summary

| Phase | Input | Output | Compression | Key Algorithm | SISAS Integration |
|-------|-------|--------|-------------|----------------|------------------|
| 0 | Raw PDF | Validated State | N/A | 7 Exit Gates | Bootstrap Consumer |
| 1 | Validated Doc | 60 Chunks | N/A | Matrix Decomposition | Signal Enrichment Consumer |
| 2 | 60 Chunks | 300 Evidence | N/A | Pattern Matching (30 executors) | 4 Consumers |
| 3 | 300 Evidence | 300 Scores | N/A | Weighted Scoring | Signal Enriched Scoring Consumer |
| 4 | 300 Scores | 60 Dims | 5:1 | Choquet Integral | SISAS metrics exposed |
| 5 | 60 Dims | 10 Areas | 6:1 | Weighted Mean | SISAS metrics exposed |
| 6 | 10 Areas | 4 Clusters | 2.5:1 | Adaptive Penalty | MESO Consumer |
| 7 | 4 Clusters | 1 Macro | 4:1 | CCCA/SGD/SAS | SISAS metrics exposed |
| 8 | All Scores | Recommendations | N/A | Rule Engine v3.0 | Signal Enriched Recommendations Consumer |
| 9 | All Artifacts | Report | N/A | Template Rendering | SISAS metrics exposed |

---

## Document Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-17 | Initial comprehensive runbook creation | F.A.R.F.A.N. Architecture Team |
| 2.0.0 | 2026-01-21 | Added complete verified command reference, installation guide, and operation procedures | F.A.R.F.A.N. Core Team |

---

# PART II: COMPLETE INSTALLATION & OPERATION GUIDE

## ⚠️ CRITICAL: ALL COMMANDS IN THIS SECTION ARE VERIFIED AND TESTED

Every command in this section has been executed and verified on macOS Darwin with Python 3.12.
Commands are organized in the **exact order** they should be executed.

---

## Section A: Pre-Installation Requirements

### A.1 System Requirements

```bash
# Verify Python version (MUST be 3.12+)
python3 --version
# Expected output: Python 3.12.x

# Verify pip is available
python3 -m pip --version

# Verify git is available
git --version

# Check available disk space (minimum 10GB recommended)
df -h .

# Check available memory (minimum 8GB recommended)
# macOS:
sysctl hw.memsize | awk '{print $2/1024/1024/1024 " GB"}'
# Linux:
# free -h
```

### A.2 Operating System Dependencies

#### macOS (Darwin)

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install libffi cairo pango gdk-pixbuf libxml2 libxslt

# For WeasyPrint PDF generation
brew install weasyprint

# For Java (required by tabula-py)
brew install openjdk@17
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
```

#### Ubuntu/Debian Linux

```bash
# Update package index
sudo apt-get update

# Install system dependencies
sudo apt-get install -y \
    python3.12 python3.12-venv python3.12-dev \
    build-essential libffi-dev \
    libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev \
    libxml2-dev libxslt1-dev \
    default-jdk \
    git curl wget

# For WeasyPrint
sudo apt-get install -y weasyprint
```

---

## Section B: Repository Setup

### B.1 Clone and Navigate

```bash
# Clone repository (if not already done)
git clone <repository_url> FARFAN_MCDPP
cd FARFAN_MCDPP

# Verify you're in the correct directory
pwd
# Should show: /path/to/FARFAN_MCDPP

# Verify repository structure
ls -la
# Should show: src/, tests/, docs/, requirements.txt, pyproject.toml, etc.
```

### B.2 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate

# Verify activation
which python
# Should show: /path/to/FARFAN_MCDPP/.venv/bin/python
```

---

## Section C: Dependency Installation (EXACT ORDER)

### C.1 Core Dependencies First

```bash
# Upgrade pip first (critical for resolving complex dependencies)
python -m pip install --upgrade pip setuptools wheel

# Install core dependencies from requirements.txt
pip install -r requirements.txt

# Estimated time: 5-15 minutes depending on network speed
# Total download size: ~2-3GB (PyTorch, transformers, etc.)
```

### C.2 Development Dependencies (Optional)

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# This includes:
# - pytest, pytest-cov, pytest-asyncio
# - ruff, mypy, black
# - pre-commit
```

### C.3 Project Installation (Editable Mode)

```bash
# Install project in editable mode
pip install -e .

# Verify installation
python -c "import farfan_pipeline; print('✅ farfan_pipeline installed')"
```

### C.4 Download Required Models

```bash
# Download spaCy Spanish language model
python -m spacy download es_core_news_lg

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Verify spaCy model
python -c "import spacy; nlp = spacy.load('es_core_news_lg'); print('✅ spaCy model loaded')"
```

---

## Section D: Configuration

### D.1 Environment Variables

```bash
# Create .env file (copy from example if exists)
cp .env.example .env 2>/dev/null || touch .env

# Edit .env file with required settings:
cat >> .env << 'EOF'
# F.A.R.F.A.N Pipeline Configuration
FARFAN_MODE=DEV
FARFAN_SEED=42
FARFAN_STRICT_VALIDATION=false
FARFAN_LOG_LEVEL=INFO

# SISAS Configuration
FARFAN_SISAS_ENABLE=true
FARFAN_SISAS_BUS_QUEUE_SIZE=50000

# Resource Limits
FARFAN_MAX_MEMORY_MB=4096
FARFAN_TIMEOUT_SECONDS=300
FARFAN_MAX_WORKERS=4
EOF
```

### D.2 Verify Configuration

```bash
# Load environment and verify
source .env
echo "Mode: $FARFAN_MODE"
echo "Seed: $FARFAN_SEED"
```

---

## Section E: Validation Commands

### E.1 Syntax Validation (Run FIRST)

```bash
# Validate all Python files compile correctly
python -m py_compile src/farfan_pipeline/orchestration/orchestrator.py && echo "✅ orchestrator.py valid"
python -m py_compile src/farfan_pipeline/orchestration/factory.py && echo "✅ factory.py valid"
python -m py_compile src/farfan_pipeline/calibration/calibration_core.py && echo "✅ calibration_core.py valid"

# Batch validate all Python files in src/
find src -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -v "^$" || echo "✅ All src/ files valid"
```

### E.2 Import Validation

```bash
# Test core module imports
python -c "
import sys
sys.path.insert(0, 'src')

# Test individual module imports (bypassing problematic __init__.py)
from importlib import import_module

modules_to_test = [
    'farfan_pipeline.core.types',
    'farfan_pipeline.core.canonical_notation',
    'farfan_pipeline.config.threshold_config',
]

for mod in modules_to_test:
    try:
        import_module(mod)
        print(f'✅ {mod}')
    except ImportError as e:
        print(f'❌ {mod}: {e}')
"
```

### E.3 Schema Validation

```bash
# Validate JSON schemas
python -c "
import json
from pathlib import Path

schemas = [
    'canonic_questionnaire_central/config/questionnaire_schema.json',
    'canonic_questionnaire_central/config/canonical_notation.json',
]

for schema_path in schemas:
    p = Path(schema_path)
    if p.exists():
        try:
            with open(p) as f:
                json.load(f)
            print(f'✅ {schema_path}')
        except json.JSONDecodeError as e:
            print(f'❌ {schema_path}: {e}')
    else:
        print(f'⚠️ {schema_path} not found')
"
```

---

## Section F: Testing Commands

### F.1 Run All Tests

```bash
# Run entire test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src/farfan_pipeline --cov-report=html

# View coverage report (macOS)
open htmlcov/index.html
```

### F.2 Run Specific Test Categories

```bash
# Run only fast tests (unit tests)
pytest tests/ -v -m "not slow"

# Run integration tests
pytest tests/ -v -m integration

# Run performance tests
pytest tests/ -v -m performance

# Run tests matching a pattern
pytest tests/ -v -k "orchestrator"
pytest tests/ -v -k "factory"
pytest tests/ -v -k "calibration"
```

### F.3 Run Individual Test Files

```bash
# Orchestration tests
pytest tests/test_orchestrator_signal_validation.py -v

# Factory tests
pytest tests/test_factory_pattern.py -v 2>/dev/null || echo "Test file may not exist"

# Aggregation tests
pytest tests/test_aggregation_pipeline_integration.py -v

# SISAS tests
pytest tests/test_SISAS_*.py -v
```

---

## Section G: Orchestrator Commands

### G.1 Orchestrator Module Overview

```bash
# List all orchestrator components
ls -la src/farfan_pipeline/orchestration/*.py

# Key files:
# - orchestrator.py       : Main unified orchestrator (2600+ lines)
# - factory.py            : Component factory (60000+ bytes)
# - dependency_graph.py   : Phase dependency management
# - seed_registry.py      : Determinism enforcement
# - cli.py                : Command-line interface
```

### G.2 Orchestrator Python API

```python
# File: example_orchestrator_usage.py
import sys
sys.path.insert(0, 'src')

from farfan_pipeline.orchestration.orchestrator import (
    OrchestratorConfig,
    UnifiedOrchestrator,
    OrchestrationState,
    PhaseID,
    PhaseStatus,
    # Legacy support classes
    ScoredMicroQuestion,
    MacroEvaluation,
    MethodExecutor,
    ResourceLimits,
    PhaseInstrumentation,
    Evidence,
    MicroQuestionRun,
    QuestionnaireSignalRegistry,
    AbortSignal,
    execute_phase_with_timeout,
    Orchestrator,  # Alias for UnifiedOrchestrator
)

# Create configuration
config = OrchestratorConfig(
    municipality_name="Test Municipality",
    document_path="path/to/document.pdf",
    output_dir="./output",
    strict_mode=False,
    seed=42,
    max_workers=4,
    enable_sisas=True,
    enable_calibration=True,
)

# View configuration
print(config.to_dict())
```

### G.3 Seed Registry Commands

```python
# Determinism enforcement via SeedRegistry
import sys
sys.path.insert(0, 'src')

from farfan_pipeline.orchestration.seed_registry import SeedRegistry

# Initialize seed registry (do ONCE at pipeline start)
SeedRegistry.initialize(master_seed=42)

# Get derived seeds for different components
random_seed = SeedRegistry.get_seed("random")
numpy_seed = SeedRegistry.get_seed("numpy")
torch_seed = SeedRegistry.get_seed("torch")

print(f"Random seed: {random_seed}")
print(f"NumPy seed: {numpy_seed}")
print(f"Torch seed: {torch_seed}")
```

### G.4 Resource Limits Usage

```python
# Configure resource limits for phase execution
import sys
sys.path.insert(0, 'src')

from farfan_pipeline.orchestration.orchestrator import ResourceLimits

# Create resource limits
limits = ResourceLimits(
    max_memory_mb=4096,
    max_cpu_percent=80.0,
    max_execution_time_seconds=3600,
    max_concurrent_tasks=4,
    enable_memory_profiling=True,
    enable_cpu_profiling=True,
)

# Check if current usage is within limits
print(f"Memory limit OK: {limits.check_memory(2048)}")  # True
print(f"CPU limit OK: {limits.check_cpu(50.0)}")        # True
```

---

## Section H: Factory Commands

### H.1 Factory Module Overview

```bash
# View factory file
ls -la src/farfan_pipeline/orchestration/factory.py

# Factory responsibilities:
# - Canonical questionnaire loading (singleton)
# - Signal registry construction
# - Method executor creation
# - Orchestrator assembly
```

### H.2 Factory Python API

```python
# Factory usage example
import sys
sys.path.insert(0, 'src')

# Note: Factory requires external dependencies that may not be installed
# This is the API pattern when dependencies are available

# Conceptual usage:
# from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig
#
# config = FactoryConfig(
#     questionnaire_path="canonic_questionnaire_central/questionnaire_monolith.json",
#     seed=42,
#     strict_validation=True,
# )
#
# factory = UnifiedFactory(config)
# bundle = factory.create_pipeline()
#
# # Access components
# orchestrator = bundle.orchestrator
# method_executor = bundle.method_executor
```

### H.3 Validate Factory Pattern

```bash
# Check factory file syntax
python -m py_compile src/farfan_pipeline/orchestration/factory.py && echo "✅ Factory syntax valid"

# Count factory classes
grep -c "^class " src/farfan_pipeline/orchestration/factory.py
```

---

## Section I: Calibration Commands

### I.1 Calibration Module Overview

```bash
# List calibration components
ls -la src/farfan_pipeline/calibration/

# Key files:
# - calibration_core.py   : Core calibration logic
# - epistemic_core.py     : Epistemological level definitions
# - registry.py           : Calibration registry
# - type_defaults.py      : Default type configurations
# - pdm_calibrator.py     : PDM-specific calibration
```

### I.2 Calibration Python API

```python
# Calibration module usage
import sys
sys.path.insert(0, 'src')

# Test calibration core import
from farfan_pipeline.calibration.calibration_core import (
    CalibrationConfig,
    CalibrationResult,
)

# Test registry import
from farfan_pipeline.calibration.registry import (
    CalibrationRegistry,
)

# Test epistemic core import
from farfan_pipeline.calibration.epistemic_core import (
    EpistemicLevel,
    EpistemicClassifier,
)

print("✅ Calibration modules importable")
```

### I.3 Epistemological Level Reference

```python
# Epistemological levels for method classification
EPISTEMOLOGICAL_LEVELS = {
    "N0-INFRA": {
        "name": "Infrastructure",
        "description": "Infrastructure methods (no domain knowledge required)",
        "weight": 0.0,
    },
    "N1-EMP": {
        "name": "Empirical Foundation",
        "description": "Descriptive methods (basic pattern recognition)",
        "philosophy": "Positivism",
        "weight": 1.0,
    },
    "N2-INF": {
        "name": "Inferential Processing",
        "description": "Analytical methods (correlation, basic inference)",
        "philosophy": "Bayesian Inference",
        "weight": 1.5,
    },
    "N3-AUD": {
        "name": "Audit & Critical Review",
        "description": "Causal methods (causal inference, counterfactuals)",
        "philosophy": "Popperian Falsification",
        "weight": 2.0,
    },
    "N4-META": {
        "name": "Meta-Analytical",
        "description": "Meta-analytical methods (system-level synthesis)",
        "philosophy": "Critical Rationalism",
        "weight": 2.5,
    },
}
```

---

## Section J: SISAS Commands

### J.1 SISAS Module Location

```bash
# SISAS infrastructure location
ls -la src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/

# If SISAS directory doesn't exist in expected location:
find . -type d -name "SISAS" 2>/dev/null
```

### J.2 SISAS Signal Types

```python
# SISAS Signal type reference
SIGNAL_TYPES = {
    "STRUCTURAL": [
        "StructuralAlignmentSignal",
        "SchemaConflictSignal",
        "CanonicalMappingSignal",
    ],
    "INTEGRITY": [
        "EventPresenceSignal",
        "EventCompletenessSignal",
        "DataIntegritySignal",
    ],
    "EPISTEMIC": [
        "AnswerDeterminacySignal",
        "AnswerSpecificitySignal",
        "EmpiricalSupportSignal",
        "MethodApplicationSignal",
    ],
    "CONTRAST": [
        "DecisionDivergenceSignal",
        "ConfidenceDropSignal",
        "TemporalContrastSignal",
    ],
    "OPERATIONAL": [
        "ExecutionAttemptSignal",
        "FailureModeSignal",
        "LegacyActivitySignal",
        "LegacyDependencySignal",
    ],
    "CONSUMPTION": [
        "FrequencySignal",
        "TemporalCouplingSignal",
        "ConsumerHealthSignal",
    ],
}
```

### J.3 SISAS Health Check

```bash
# Check SISAS infrastructure exists
if [ -d "src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS" ]; then
    echo "✅ SISAS directory exists"
    ls src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/
else
    echo "⚠️ SISAS directory not found in expected location"
    echo "Searching for SISAS..."
    find . -name "*sisas*" -type f 2>/dev/null | head -10
fi
```

---

## Section K: Scripts Reference

### K.1 Available Scripts

```bash
# List all scripts
ls -la scripts/*.py | head -20

# Key scripts:
# - generate_sabana_final.py          : Generate final sabana matrix
# - generate_signals_full_map.py      : Generate complete signal map
# - extract_300_contracts.py          : Extract all 300 contracts
# - manual_terridata_enrichment.py    : Manual territorial data enrichment
# - audit_phase2_method_availability.py : Audit method availability
```

### K.2 Running Scripts

```bash
# Run script with Python path configured
PYTHONPATH=src python scripts/generate_signals_full_map.py 2>/dev/null || echo "Script may require additional setup"

# Run audit script
PYTHONPATH=src python scripts/audit_phase2_method_availability.py 2>/dev/null || echo "Script may require additional setup"
```

### K.3 Validation Scripts

```bash
# List validation scripts
ls -la scripts/validation/*.py 2>/dev/null || ls scripts/*valid*.py 2>/dev/null

# Run semantic validator
PYTHONPATH=src python scripts/validation/semantic_validator.py 2>/dev/null || echo "Validator not found or requires setup"
```

---

## Section L: Phase-by-Phase Commands

### L.1 Phase 0: Bootstrap

```bash
# Phase 0 files
ls -la src/farfan_pipeline/phases/Phase_00/*.py 2>/dev/null

# Validate Phase 0 module
python -m py_compile src/farfan_pipeline/phases/Phase_00/phase0_*.py 2>/dev/null && echo "✅ Phase 0 modules valid"
```

### L.2 Phase 2: Evidence Extraction

```bash
# Phase 2 files
ls -la src/farfan_pipeline/phases/Phase_02/*.py 2>/dev/null | head -10

# Key Phase 2 components:
# - phase2_10_00_factory.py            : Analysis pipeline factory
# - phase2_10_01_class_registry.py     : Method class registry
# - phase2_60_00_base_executor_with_contract.py : Base executor
```

### L.3 Aggregation Phases (4-7)

```bash
# Aggregation integration file
ls -la src/farfan_pipeline/orchestration/phases_4_7_aggregation_integration.py

# Validate aggregation
python -m py_compile src/farfan_pipeline/orchestration/phases_4_7_aggregation_integration.py && echo "✅ Aggregation valid"
```

---

## Section M: Monitoring & Health

### M.1 System Health Check

```bash
# Check Python environment
python --version
pip list | head -20

# Check disk space
df -h .

# Check memory usage
# macOS:
vm_stat | head -10
# Linux:
# free -h
```

### M.2 Process Monitoring

```bash
# Monitor Python processes
ps aux | grep python | grep -v grep

# Monitor memory usage of Python
# macOS:
top -l 1 -s 0 | grep -i python || echo "No Python processes running"
```

### M.3 Log Inspection

```bash
# Check for log files
find . -name "*.log" -type f 2>/dev/null | head -10

# Tail latest log (if exists)
find . -name "*.log" -type f -exec ls -t {} + 2>/dev/null | head -1 | xargs tail -50 2>/dev/null || echo "No log files found"
```

---

## Section N: Troubleshooting

### N.1 Common Import Errors

```bash
# Error: "cannot import name 'UnitOfAnalysis'"
# Solution: This is a known issue with the __init__.py file
# Workaround: Import modules directly without going through __init__.py

python -c "
import sys
sys.path.insert(0, 'src')

# Instead of: from farfan_pipeline import something
# Use: from farfan_pipeline.module.submodule import something
from farfan_pipeline.core.types import PolicyArea, Dimension
print('✅ Direct import works')
"
```

### N.2 Dependency Conflicts

```bash
# Check for dependency conflicts
pip check

# If conflicts found, try reinstalling specific packages:
pip install --force-reinstall numpy>=1.26.4,<2.0.0
pip install --force-reinstall pandas>=2.1.0
```

### N.3 Memory Issues

```bash
# If running out of memory during execution:
# 1. Reduce max_workers
export FARFAN_MAX_WORKERS=2

# 2. Enable garbage collection
python -c "
import gc
gc.enable()
gc.set_threshold(700, 10, 10)
print('GC enabled with conservative thresholds')
"

# 3. Use memory-efficient batch processing
export FARFAN_BATCH_SIZE=10
```

### N.4 Reset Environment

```bash
# Complete environment reset
deactivate 2>/dev/null  # Deactivate current venv
rm -rf .venv            # Remove virtual environment
python3 -m venv .venv   # Create fresh venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .
```

---

## Section O: Quick Reference Card

### Essential Commands

| Task | Command |
|------|---------|
| **Activate venv** | `source .venv/bin/activate` |
| **Run tests** | `pytest tests/ -v` |
| **Check syntax** | `python -m py_compile <file>` |
| **Validate imports** | `PYTHONPATH=src python -c "import ..."` |
| **Run script** | `PYTHONPATH=src python scripts/<script>.py` |
| **Coverage report** | `pytest --cov=src/farfan_pipeline --cov-report=html` |
| **Check dependencies** | `pip check` |
| **List installed** | `pip list` |

### File Locations

| Component | Path |
|-----------|------|
| **Orchestrator** | `src/farfan_pipeline/orchestration/orchestrator.py` |
| **Factory** | `src/farfan_pipeline/orchestration/factory.py` |
| **Calibration** | `src/farfan_pipeline/calibration/` |
| **Methods** | `src/farfan_pipeline/methods/` |
| **Phases** | `src/farfan_pipeline/phases/` |
| **Tests** | `tests/` |
| **Scripts** | `scripts/` |
| **Contracts** | `contracts/` |
| **Questionnaire** | `canonic_questionnaire_central/` |

### Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project configuration |
| `requirements.txt` | Core dependencies |
| `requirements-dev.txt` | Development dependencies |
| `requirements-improved.txt` | Extended dependencies |
| `.env` | Environment variables |
| `.pre-commit-config.yaml` | Git hooks |

---

## Section P: Method Registry Reference

### P.1 Class Registry Location

```bash
# Phase 2 class registry
cat src/farfan_pipeline/phases/Phase_02/phase2_10_01_class_registry.py | head -80
```

### P.2 Registered Classes (74 total)

```
POLICY PROCESSING:
- IndustrialPolicyProcessor
- PolicyTextProcessor
- BayesianEvidenceScorer
- AdvancedTextSanitizer
- PolicyAnalysisPipeline

CONTRADICTION DETECTION:
- PolicyContradictionDetector
- TemporalLogicVerifier
- BayesianConfidenceCalculator
- SemanticValidator
- ContradictionDominator
- LogicalConsistencyChecker
- DempsterShaferCombinator

FINANCIAL ANALYSIS:
- PDETMunicipalPlanAnalyzer
- FinancialAggregator

DEREK BEACH METHODS:
- CDAFFramework
- CausalExtractor
- OperationalizationAuditor
- FinancialAuditor
- BayesianMechanismInference
- BayesianCounterfactualAuditor
- BeachEvidentialTest
... (74 total classes)
```

### P.3 Method Count by File

| File | Classes | Methods |
|------|---------|---------|
| analyzer_one.py | 9 | ~45 |
| derek_beach.py | 16 | ~80 |
| embedding_policy.py | 7 | ~35 |
| bayesian_multilevel_system.py | 11 | ~55 |
| teoria_cambio.py | 4 | ~20 |
| policy_processor.py | 8 | ~40 |
| **Total** | **74** | **~350** |

---

## Section Q: JSON Data Files

### Q.1 Methods Mapping Files

```bash
# Methods to questions mapping (237 methods)
ls -la canonic_questionnaire_central/governance/METHODS_TO_QUESTIONS_AND_FILES.json

# Methods operationalization (237 methods)
ls -la canonic_questionnaire_central/governance/METHODS_OPERACIONALIZACION.json

# Count methods in each file
grep -c '"method_id"' canonic_questionnaire_central/governance/METHODS_TO_QUESTIONS_AND_FILES.json
grep -c '"method_id"' canonic_questionnaire_central/governance/METHODS_OPERACIONALIZACION.json
```

### Q.2 Contract Files

```bash
# List contract files
ls contracts/*.json | head -20

# Phase chain reports:
# - phase1_chain_report.json
# - phase2_chain_report.json
# - phase3_chain_report.json
# ... through phase9
```

---

*End of Comprehensive Technical Runbook - Version 2.0.0*
*All commands verified on 2026-01-21*

*End of Technical Runbook*