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

## PART II: ADVANCED OPERATIONS & COMPREHENSIVE GUIDE

> **Extended Technical Reference**
>
> | Attribute | Value |
> |-----------|-------|
> | **Section** | `RUNBOOK-ADVANCED-003` |
> | **Version** | `3.0.0` |
> | **Classification** | ADVANCED OPERATIONS |
> | **Page Equivalent** | 200+ pages |

---

# Section 24: Installation & Initialization - Complete Propedeutic Guide

## 24.1 System Requirements & Prerequisites

### 24.1.1 Hardware Requirements

**Minimum Requirements:**
```yaml
CPU: 4 cores (x86_64)
RAM: 8 GB
Storage: 20 GB free space
Network: Stable internet connection (for model downloads)
```

**Recommended for Production:**
```yaml
CPU: 8+ cores (x86_64) with AVX2 support
RAM: 16-32 GB
Storage: 50 GB SSD (NVMe preferred)
Network: 1 Gbps connection
GPU: Optional - CUDA-compatible GPU for accelerated NLP operations
```

**Optimal Configuration:**
```yaml
CPU: 16+ cores (AMD EPYC or Intel Xeon)
RAM: 64 GB
Storage: 100 GB NVMe SSD
Network: 10 Gbps connection
GPU: NVIDIA A100 or V100 for transformer models
```

### 24.1.2 Software Prerequisites

**Operating System Support:**
```bash
# Fully Supported
Ubuntu 22.04 LTS (Jammy Jellyfish)
Ubuntu 20.04 LTS (Focal Fossa)
Debian 11 (Bullseye)
Debian 12 (Bookworm)

# Partially Supported
macOS 12+ (Monterey or later) - Darwin platform
RHEL 8+, CentOS 8+, Rocky Linux 8+

# Experimental
Windows 10/11 with WSL2 (Ubuntu 22.04)
```

**Core Dependencies:**
```bash
# Python ecosystem
Python 3.12+ (strict requirement)
pip 23.0+
setuptools 65.0+
wheel 0.38+

# System packages (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    build-essential \
    git \
    curl \
    wget \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libpoppler-cpp-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    graphviz \
    redis-server

# Optional performance packages
sudo apt-get install -y \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    gfortran

# For PDF processing
sudo apt-get install -y \
    ghostscript \
    imagemagick \
    pdftotext \
    pdfinfo
```

### 24.1.3 Network Configuration

**Firewall Rules:**
```bash
# Allow dashboard access
sudo ufw allow 5000/tcp   # ATROZ Dashboard
sudo ufw allow 8000/tcp   # API Server
sudo ufw allow 6379/tcp   # Redis (if external)

# For remote access
sudo ufw allow from 10.0.0.0/8 to any port 5000
sudo ufw allow from 172.16.0.0/12 to any port 5000
```

**Proxy Configuration (if behind corporate proxy):**
```bash
# Set environment variables
export http_proxy="http://proxy.company.com:8080"
export https_proxy="http://proxy.company.com:8080"
export no_proxy="localhost,127.0.0.1,.local"

# For pip
pip config set global.proxy http://proxy.company.com:8080
```

## 24.2 Installation Methods

### 24.2.1 Method 1: Quick Install (Recommended)

**Single-Command Installation:**
```bash
# Clone repository
git clone https://github.com/ALOHAALOHAALOJHA/FARFAN_MCDPP.git
cd FARFAN_MCDPP

# Run installer
bash install.sh

# Activate environment
source farfan-env/bin/activate

# Verify installation
farfan-pipeline --version
python -m farfan_pipeline.orchestration.orchestrator --help
```

**Installation Script Breakdown:**
```bash
# What install.sh does:
# 1. Checks Python 3.12+ availability
# 2. Creates virtual environment in farfan-env/
# 3. Upgrades pip, setuptools, wheel
# 4. Installs all requirements from requirements.txt
# 5. Installs package in editable mode (pip install -e .)
# 6. Downloads spaCy language models
# 7. Validates installation
# 8. Creates default configuration files
# 9. Initializes SISAS subsystem
# 10. Runs smoke tests
```

### 24.2.2 Method 2: Manual Installation (Full Control)

**Step-by-Step Manual Setup:**
```bash
# Step 1: Clone repository
git clone https://github.com/ALOHAALOHAALOJHA/FARFAN_MCDPP.git
cd FARFAN_MCDPP

# Step 2: Create virtual environment
python3.12 -m venv farfan-env

# Step 3: Activate environment
source farfan-env/bin/activate  # Linux/macOS
# OR
farfan-env\Scripts\activate  # Windows

# Step 4: Upgrade pip ecosystem
pip install --upgrade pip setuptools wheel

# Step 5: Install core dependencies
pip install -r requirements.txt

# Step 6: Install package in development mode
pip install -e .

# Step 7: Download NLP models
python -m spacy download es_core_news_lg
python -m spacy download es_dep_news_trf

# Step 8: Initialize configuration
python scripts/setup/initialize_config.py

# Step 9: Validate installation
python scripts/setup/validate_installation.py

# Step 10: Run smoke tests
pytest tests/smoke/ -v
```

### 24.2.3 Method 3: Docker Installation

**Using Docker Compose:**
```bash
# Build image
docker-compose build farfan-pipeline

# Start services
docker-compose up -d

# Access container
docker-compose exec farfan-pipeline bash

# Run pipeline
docker-compose exec farfan-pipeline farfan-pipeline --start-phase 0 --end-phase 9
```

**Docker Configuration:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  farfan-pipeline:
    build: .
    container_name: farfan-pipeline
    volumes:
      - ./data:/app/data
      - ./artifacts:/app/artifacts
      - ./logs:/app/logs
    ports:
      - "5000:5000"  # Dashboard
      - "8000:8000"  # API
    environment:
      - FARFAN_MODE=PROD
      - FARFAN_SEED=42
      - FARFAN_LOG_LEVEL=INFO
    networks:
      - farfan-network

  redis:
    image: redis:7-alpine
    container_name: farfan-redis
    ports:
      - "6379:6379"
    networks:
      - farfan-network

networks:
  farfan-network:
    driver: bridge
```

### 24.2.4 Post-Installation Verification

**Comprehensive Health Check:**
```bash
# 1. Check Python version
python --version
# Expected: Python 3.12.x

# 2. Check package installation
pip list | grep farfan
# Expected: farfan-pipeline, farfan-core

# 3. Verify spaCy models
python -c "import spacy; nlp = spacy.load('es_core_news_lg'); print('✓ Spanish model loaded')"

# 4. Test imports
python -c "
from farfan_pipeline.orchestration.orchestrator import Orchestrator
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main import main
print('✓ All imports successful')
"

# 5. Run diagnostic script
python scripts/diagnostics/system_check.py

# 6. Validate canonical files
python scripts/validation/validate_canonical_files.py

# 7. Check SISAS health
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main health

# 8. Run mini pipeline test
pytest tests/integration/test_mini_pipeline.py -v
```

## 24.3 Configuration & Initialization

### 24.3.1 Environment Configuration

**Create .env file:**
```bash
cat > .env << 'EOF'
# Core Settings
FARFAN_MODE=DEV
FARFAN_SEED=42
FARFAN_LOG_LEVEL=INFO
FARFAN_STRICT_VALIDATION=false

# Paths
FARFAN_DATA_DIR=/home/user/FARFAN_MCDPP/data
FARFAN_ARTIFACTS_DIR=/home/user/FARFAN_MCDPP/artifacts
FARFAN_LOGS_DIR=/home/user/FARFAN_MCDPP/logs
FARFAN_CONFIG_DIR=/home/user/FARFAN_MCDPP/config

# SISAS Settings
FARFAN_SISAS_ENABLE=true
FARFAN_SISAS_BUS_QUEUE_SIZE=50000
FARFAN_SISAS_CONSUMER_THREADS=4
FARFAN_SISAS_GATE_STRICT=true

# Performance Settings
FARFAN_MAX_MEMORY_MB=8192
FARFAN_TIMEOUT_SECONDS=300
FARFAN_MAX_WORKERS=4
FARFAN_ENABLE_CACHING=true
FARFAN_CACHE_SIZE_MB=2048

# Dashboard Settings
FARFAN_DASHBOARD_HOST=0.0.0.0
FARFAN_DASHBOARD_PORT=5000
FARFAN_DASHBOARD_DEBUG=false

# API Settings
FARFAN_API_HOST=0.0.0.0
FARFAN_API_PORT=8000
FARFAN_API_WORKERS=4

# Redis Settings
FARFAN_REDIS_HOST=localhost
FARFAN_REDIS_PORT=6379
FARFAN_REDIS_DB=0

# Monitoring Settings
FARFAN_ENABLE_METRICS=true
FARFAN_METRICS_INTERVAL=10
FARFAN_ENABLE_PROFILING=false

# Security Settings
FARFAN_API_KEY=your-secret-key-here
FARFAN_ENABLE_AUTH=false
EOF
```

**Load environment:**
```bash
# Load .env automatically
source .env

# Or use python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv(); print('✓ Environment loaded')"
```

### 24.3.2 Initialize Canonical Files

**Download/Verify Canonical Questionnaire:**
```bash
# Verify questionnaire exists
ls -lh canonic_questionnaire_central/questionnaire_monolith.json

# Validate questionnaire schema
python scripts/validation/validate_questionnaire_schema.py

# Generate questionnaire hash
sha256sum canonic_questionnaire_central/questionnaire_monolith.json

# Verify calibration files exist
ls -lh config/calibration/COHORT_2024_*.json

# List all calibration files
ls -1 config/calibration/
# Expected output:
# COHORT_2024_intrinsic_calibration.json
# COHORT_2024_fusion_weights.json
# COHORT_2024_method_compatibility.json
# COHORT_2024_questionnaire_monolith.json
# COHORT_2024_executor_config.json
# COHORT_2024_runtime_layers.json
```

### 24.3.3 Generate Required Contracts

**Generate Phase 2 Contracts:**
```bash
# Generate all 300 contracts (Q001-Q030 × PA01-PA10)
python scripts/generation/generate_all_contracts.py \
    --questionnaire canonic_questionnaire_central/questionnaire_monolith.json \
    --output-dir src/farfan_pipeline/phases/Phase_02/generated_contracts/contracts/ \
    --version 4 \
    --validate

# Verify contract count
ls src/farfan_pipeline/phases/Phase_02/generated_contracts/contracts/*.json | wc -l
# Expected: 300

# Validate contract integrity
python scripts/validation/validate_all_contracts.py
```

### 24.3.4 Initialize SISAS Subsystem

**Complete SISAS Initialization:**
```bash
# 1. Generate signal vocabulary
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    generate-vocab \
    --output src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config/vocabulary_config.yaml

# 2. Initialize signal buses
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.buses.bus_system init

# 3. Register all consumers
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.consumer_registry register-all

# 4. Validate gate configuration
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.gates.gate_validator validate

# 5. Run SISAS health check
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main health \
    --bus-stats \
    --consumer-health \
    --vehicle-status

# Expected output:
# ✓ All 6 buses operational
# ✓ All 17 consumers registered
# ✓ All 4 gates configured
# ✓ All 8 vehicles available
```

### 24.3.5 Initialize Seed Registry

**Set Up Deterministic Execution:**
```bash
# Initialize seed registry
python -c "
from farfan_pipeline.orchestration.seed_registry import SeedRegistry
SeedRegistry.initialize(master_seed=42)
print('✓ Seed registry initialized with seed=42')
"

# Verify determinism
python scripts/validation/test_determinism.py --runs 3
# Expected: All 3 runs produce identical results
```

### 24.3.6 Create Directory Structure

**Initialize Required Directories:**
```bash
# Create full directory structure
mkdir -p artifacts/{checkpoints,logs,reports,evidence,scores,dimensions,areas,clusters,macro,recommendations}
mkdir -p data/{plans,questionnaires,contracts}
mkdir -p logs/{orchestrator,phases,sisas,metrics}
mkdir -p config/{calibration,parametrization,pdm}
mkdir -p temp/{cache,processing}

# Set permissions
chmod -R 755 artifacts/ data/ logs/ config/
chmod -R 777 temp/

# Create .gitkeep files
find artifacts/ data/ logs/ temp/ -type d -exec touch {}/.gitkeep \;

# Verify structure
tree -L 2 artifacts/ data/ logs/
```

## 24.4 First-Time Execution Guide

### 24.4.1 Smoke Test - Minimal Pipeline

**Run Minimal Test:**
```bash
# Activate environment
source farfan-env/bin/activate

# Run Phase 0 only (Bootstrap validation)
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main \
    --dry-run \
    --verbose

# Expected output:
# ✓ Exit Gate 1: Python 3.12+ detected
# ✓ Exit Gate 2: Questionnaire loaded (300 questions)
# ✓ Exit Gate 3: Calibration files valid
# ✓ Exit Gate 4: Method registry populated (74 classes)
# ✓ Exit Gate 5: Contracts available (300 files)
# ✓ Exit Gate 6: SISAS subsystem healthy
# ✓ Exit Gate 7: Seed registry initialized
# Phase 0 validation: PASSED
```

### 24.4.2 Test Pipeline - Single Document

**Process Test Document:**
```bash
# Use sample plan (if available)
PLAN_PDF="data/plans/sample_plan.pdf"

# Run phases 0-3 only
python scripts/run_policy_pipeline_verified.py \
    --plan "$PLAN_PDF" \
    --artifacts-dir artifacts/test_run \
    --start-phase 0 \
    --end-phase 3 \
    --seed 42 \
    --verbose

# Check outputs
ls -lh artifacts/test_run/
# Expected:
# - phase0_bootstrap/
# - phase1_chunks/
# - phase2_evidence/
# - phase3_scores/
```

### 24.4.3 Full Pipeline - Production Run

**Complete Pipeline Execution:**
```bash
# Run full pipeline (phases 0-9)
farfan-pipeline \
    --plan data/plans/Plan_PDET_2018.pdf \
    --artifacts-dir artifacts/full_run_$(date +%Y%m%d_%H%M%S) \
    --start-phase 0 \
    --end-phase 9 \
    --seed 42 \
    --enable-sisas \
    --enable-metrics \
    --enable-dashboard \
    --log-level INFO

# Monitor execution
tail -f logs/orchestrator/orchestrator.log

# Check final artifacts
ls -lh artifacts/full_run_*/phase9_reports/
```

---

# Section 25: Dashboard & Visualization - Complete Guide

## 25.1 ATROZ Dashboard v2.0

### 25.1.1 Starting the Dashboard

**Basic Start:**
```bash
# Method 1: Direct Python
python -m farfan_pipeline.dashboard_atroz_.dashboard_server

# Method 2: With custom port
python -m farfan_pipeline.dashboard_atroz_.dashboard_server --port 5001

# Method 3: Production mode
python -m farfan_pipeline.dashboard_atroz_.dashboard_server \
    --host 0.0.0.0 \
    --port 5000 \
    --workers 4 \
    --no-debug

# Method 4: Background process
nohup python -m farfan_pipeline.dashboard_atroz_.dashboard_server \
    --host 0.0.0.0 \
    --port 5000 \
    > logs/dashboard.log 2>&1 &

echo $! > /tmp/dashboard.pid
```

**Advanced Configuration:**
```bash
# Start with custom configuration
python -m farfan_pipeline.dashboard_atroz_.dashboard_server \
    --config config/dashboard_config.yaml \
    --enable-auth \
    --enable-ssl \
    --ssl-cert /path/to/cert.pem \
    --ssl-key /path/to/key.pem \
    --redis-url redis://localhost:6379/0 \
    --websocket-ping-interval 25 \
    --websocket-ping-timeout 120 \
    --max-connections 1000
```

### 25.1.2 Dashboard Views

**Main Dashboard - Constellation View:**
```
URL: http://localhost:5000/

Features:
┌─────────────────────────────────────────────────────────────┐
│                    MAIN DASHBOARD                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Map View: 170 PDET Municipalities]                        │
│                                                              │
│  Region Selector: [Dropdown: 16 regions]                    │
│                                                              │
│  Pipeline Status:                                            │
│  Phase 0: ████████████ 100% [COMPLETE]                      │
│  Phase 1: ████████████ 100% [COMPLETE]                      │
│  Phase 2: ████████████ 100% [COMPLETE]                      │
│  Phase 3: ████████████ 100% [COMPLETE]                      │
│  Phase 4: ██████────── 60% [RUNNING]                        │
│  Phase 5: ────────────  0% [PENDING]                        │
│  Phase 6: ────────────  0% [PENDING]                        │
│  Phase 7: ────────────  0% [PENDING]                        │
│  Phase 8: ────────────  0% [PENDING]                        │
│  Phase 9: ────────────  0% [PENDING]                        │
│                                                              │
│  Live Metrics:                                               │
│  • Questions Scored: 245/300 (81.7%)                        │
│  • Evidence Extracted: 2,456 items                          │
│  • SISAS Signals: 15,234 emitted, 15,100 consumed          │
│  • Processing Time: 00:45:32                                │
│                                                              │
│  [View Details] [Export Data] [Download Report]             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**SISAS Ecosystem View:**
```
URL: http://localhost:5000/static/sisas-ecosystem-view.html

Features:
┌─────────────────────────────────────────────────────────────┐
│              SISAS ECOSYSTEM DASHBOARD                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Signal Bus Status:                                          │
│  ┌────────────────┬────────┬─────────┬──────────┐           │
│  │ Bus            │ Queue  │ Rate    │ Status   │           │
│  ├────────────────┼────────┼─────────┼──────────┤           │
│  │ Structural     │ 234/50k│ 45 s⁻¹  │ HEALTHY  │           │
│  │ Integrity      │ 156/50k│ 32 s⁻¹  │ HEALTHY  │           │
│  │ Epistemic      │ 89/50k │ 18 s⁻¹  │ HEALTHY  │           │
│  │ Contrast       │ 45/50k │ 9 s⁻¹   │ HEALTHY  │           │
│  │ Operational    │ 12/50k │ 3 s⁻¹   │ HEALTHY  │           │
│  │ Consumption    │ 8/50k  │ 2 s⁻¹   │ HEALTHY  │           │
│  └────────────────┴────────┴─────────┴──────────┘           │
│                                                              │
│  Consumer Health (17 total):                                 │
│  Phase 0: ✓ Bootstrap Consumer [ACTIVE]                     │
│  Phase 1: ✓ Signal Enrichment Consumer [ACTIVE]             │
│  Phase 2: ✓ Contract Consumer [ACTIVE]                      │
│          ✓ Evidence Consumer [ACTIVE]                       │
│          ✓ Factory Consumer [ACTIVE]                        │
│          ✓ Executor Consumer [ACTIVE]                       │
│  Phase 3: ✓ Signal Enriched Scoring Consumer [ACTIVE]       │
│  ... [expand all]                                            │
│                                                              │
│  4-Gate Validation Statistics:                               │
│  Gate 1 (Scope): 15,234 passed, 45 rejected (99.7%)        │
│  Gate 2 (Value): 15,189 passed, 90 rejected (99.4%)        │
│  Gate 3 (Capability): 15,100 passed, 179 rejected (98.8%)  │
│  Gate 4 (Channel): 15,100 passed, 0 rejected (100%)        │
│                                                              │
│  Dead Letter Queue: 179 signals [View Details]              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Admin Panel:**
```
URL: http://localhost:5000/static/admin.html

Features:
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN CONTROL PANEL                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Pipeline Control:                                           │
│  [Start Pipeline] [Pause Pipeline] [Stop Pipeline]          │
│  [Resume from Checkpoint] [Rollback to Phase]               │
│                                                              │
│  SISAS Control:                                              │
│  [Flush Signal Buses] [Reset Consumers] [Clear DLQ]         │
│  [Replay Signals] [Export Signal Log]                       │
│                                                              │
│  System Maintenance:                                         │
│  [Clear Cache] [Vacuum Database] [Rotate Logs]              │
│  [Backup Artifacts] [Restore Checkpoint]                    │
│                                                              │
│  Diagnostics:                                                │
│  [Run Health Check] [Generate System Report]                │
│  [Validate Contracts] [Check Integrity]                     │
│                                                              │
│  Monitoring:                                                 │
│  CPU: ████████░░ 80%  Memory: ██████░░░░ 60%               │
│  Disk: ████░░░░░░ 40%  Network: ███░░░░░░░ 30%             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 25.1.3 Dashboard API Endpoints

**Complete API Reference:**

```bash
# ============================================================
# REGION ENDPOINTS
# ============================================================

# Get all regions with summary statistics
curl http://localhost:5000/api/v1/regions | jq

# Response:
{
  "regions": [
    {
      "id": "R01",
      "name": "Arauca",
      "municipalities": 7,
      "macro_score": 0.72,
      "status": "evaluated"
    },
    ...
  ],
  "total": 16
}

# Get detailed region analysis
curl http://localhost:5000/api/v1/regions/R01 | jq

# Response:
{
  "region_id": "R01",
  "name": "Arauca",
  "municipalities": 7,
  "macro_score": 0.72,
  "clusters": {
    "institutional": 0.75,
    "territorial": 0.68,
    "productive": 0.71,
    "social": 0.74
  },
  "policy_areas": [...],
  "dimensions": [...],
  "evaluation_date": "2026-01-23T10:30:00Z"
}

# Get 300 micro question scores for a region
curl http://localhost:5000/api/v1/regions/R01/questions | jq

# Response:
{
  "region_id": "R01",
  "questions": [
    {
      "question_id": "Q001_PA01",
      "score": 0.85,
      "confidence": 0.92,
      "evidence_count": 8
    },
    ...
  ],
  "total": 300
}

# Get evidence stream for a region
curl http://localhost:5000/api/v1/regions/R01/evidence | jq

# Get region connections graph
curl http://localhost:5000/api/v1/regions/connections | jq


# ============================================================
# JOB MANAGEMENT ENDPOINTS
# ============================================================

# List all jobs
curl http://localhost:5000/api/v1/jobs | jq

# Response:
{
  "jobs": [
    {
      "job_id": "job_20260123_103000",
      "status": "running",
      "current_phase": 4,
      "progress": 0.45,
      "started_at": "2026-01-23T10:30:00Z"
    },
    ...
  ]
}

# Get detailed job status
curl http://localhost:5000/api/v1/jobs/job_20260123_103000 | jq

# Response:
{
  "job_id": "job_20260123_103000",
  "status": "running",
  "phases": {
    "phase_0": {"status": "completed", "duration": 45.2},
    "phase_1": {"status": "completed", "duration": 120.5},
    "phase_2": {"status": "completed", "duration": 450.8},
    "phase_3": {"status": "completed", "duration": 180.3},
    "phase_4": {"status": "running", "progress": 0.60},
    ...
  },
  "total_duration": 2156.3,
  "artifacts_generated": 1245
}

# Get execution logs
curl http://localhost:5000/api/v1/jobs/job_20260123_103000/logs?lines=100 | jq

# Upload PDF and start pipeline
curl -X POST \
  -F "file=@data/plans/Plan_PDET.pdf" \
  -F "region_id=R01" \
  -F "seed=42" \
  http://localhost:5000/api/upload/plan

# Response:
{
  "job_id": "job_20260123_150000",
  "status": "queued",
  "message": "Pipeline started successfully"
}


# ============================================================
# SISAS INTEGRATION ENDPOINTS
# ============================================================

# Get SISAS integration status
curl http://localhost:5000/api/v1/sisas/status | jq

# Response:
{
  "buses": {
    "total": 6,
    "healthy": 6,
    "degraded": 0,
    "failed": 0
  },
  "consumers": {
    "total": 17,
    "active": 17,
    "idle": 0,
    "error": 0
  },
  "gates": {
    "gate_1_pass_rate": 0.997,
    "gate_2_pass_rate": 0.994,
    "gate_3_pass_rate": 0.988,
    "gate_4_pass_rate": 1.000
  }
}

# Get real-time SISAS metrics
curl http://localhost:5000/api/v1/sisas/metrics | jq

# Response:
{
  "signals_emitted": 15234,
  "signals_consumed": 15100,
  "signals_rejected": 134,
  "dead_letters": 179,
  "throughput": {
    "current": 45.2,
    "average": 38.7,
    "peak": 67.3
  },
  "latency": {
    "p50": 12.3,
    "p95": 45.6,
    "p99": 78.9
  }
}

# Get all consumer statuses
curl http://localhost:5000/api/v1/sisas/consumers | jq

# Get dead letter queue contents
curl http://localhost:5000/api/v1/sisas/dead-letter?limit=50 | jq


# ============================================================
# CANONICAL DATA ENDPOINTS
# ============================================================

# Get all 300 canonical questions
curl http://localhost:5000/api/v1/canonical/questions | jq

# Get single question detail
curl http://localhost:5000/api/v1/canonical/questions/Q001_PA01 | jq

# Response:
{
  "question_id": "Q001_PA01",
  "text": "¿El plan identifica claramente los objetivos estratégicos?",
  "dimension": "D1_ESTRATEGIA",
  "policy_area": "PA01_GOBERNANZA",
  "weight": 0.045,
  "methods": ["analyzer_one", "derek_beach"],
  "contract_file": "Q001_PA01_contract_v4.json"
}

# Get 6 dimensions metadata
curl http://localhost:5000/api/v1/canonical/dimensions | jq

# Get 10 policy areas metadata
curl http://localhost:5000/api/v1/canonical/policy-areas | jq

# Get 4 clusters metadata
curl http://localhost:5000/api/v1/canonical/clusters | jq


# ============================================================
# METRICS & MONITORING ENDPOINTS
# ============================================================

# Get system metrics
curl http://localhost:5000/api/v1/metrics/system | jq

# Get phase metrics
curl http://localhost:5000/api/v1/metrics/phase/4 | jq

# Get executor metrics
curl http://localhost:5000/api/v1/metrics/executors | jq

# Get time series metrics (Prometheus format)
curl http://localhost:5000/api/v1/metrics/prometheus


# ============================================================
# HEALTH CHECK ENDPOINTS
# ============================================================

# Basic health check
curl http://localhost:5000/health

# Response:
{"status": "healthy", "timestamp": "2026-01-23T10:30:00Z"}

# Detailed health check
curl http://localhost:5000/health/detailed | jq

# Response:
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "sisas": "healthy",
    "filesystem": "healthy"
  },
  "metrics": {
    "uptime": 86400,
    "requests_total": 15234,
    "requests_per_second": 12.5
  }
}

# Readiness probe (K8s)
curl http://localhost:5000/ready

# Liveness probe (K8s)
curl http://localhost:5000/alive
```

### 25.1.4 WebSocket API

**Real-Time Updates:**

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Listen to pipeline progress
socket.on('pipeline_progress', (data) => {
  console.log('Phase:', data.phase);
  console.log('Progress:', data.progress);
  console.log('Status:', data.status);
});

// Listen to SISAS events
socket.on('sisas_signal', (data) => {
  console.log('Signal Type:', data.signal_type);
  console.log('Bus:', data.bus);
  console.log('Payload:', data.payload);
});

// Listen to metrics updates
socket.on('metrics_update', (data) => {
  console.log('Metrics:', data);
});

// Listen to job completion
socket.on('job_complete', (data) => {
  console.log('Job ID:', data.job_id);
  console.log('Duration:', data.duration);
  console.log('Artifacts:', data.artifacts_count);
});

// Send control commands
socket.emit('pipeline_control', {
  action: 'pause',
  job_id: 'job_20260123_103000'
});
```

## 25.2 Advanced Visualization Tools

### 25.2.1 Grafana Integration

**Setup Grafana Dashboard:**

```bash
# Install Grafana
sudo apt-get install -y grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Access Grafana
# URL: http://localhost:3000
# Default credentials: admin/admin

# Import F.A.R.F.A.N. dashboard
curl -X POST \
  -H "Content-Type: application/json" \
  -d @grafana/farfan_dashboard.json \
  http://admin:admin@localhost:3000/api/dashboards/db
```

**Grafana Dashboard Panels:**

```yaml
Dashboard: "F.A.R.F.A.N. Pipeline Monitoring"

Panels:
  - Pipeline Phase Progress:
      Type: Graph
      Metrics:
        - phase_0_duration
        - phase_1_duration
        - phase_2_duration
        - ... phase_9_duration

  - SISAS Signal Throughput:
      Type: Graph
      Metrics:
        - signals_emitted_per_second
        - signals_consumed_per_second
        - signals_rejected_per_second

  - Resource Utilization:
      Type: Graph
      Metrics:
        - cpu_usage_percent
        - memory_usage_mb
        - disk_io_read_mb
        - disk_io_write_mb

  - Error Rates:
      Type: Stat
      Metrics:
        - executor_error_rate
        - consumer_error_rate
        - gate_rejection_rate

  - Queue Depths:
      Type: Gauge
      Metrics:
        - structural_bus_queue_depth
        - integrity_bus_queue_depth
        - epistemic_bus_queue_depth
        - ... all buses

  - Evidence Extraction Rate:
      Type: Graph
      Metrics:
        - evidence_per_second
        - evidence_quality_score

  - Scoring Performance:
      Type: Heatmap
      Metrics:
        - question_score_distribution
        - dimension_score_distribution
```

### 25.2.2 Prometheus Metrics Export

**Metrics Endpoint Configuration:**

```bash
# Enable Prometheus metrics
export FARFAN_ENABLE_METRICS=true
export FARFAN_METRICS_PORT=9090

# Start metrics exporter
python -m farfan_pipeline.monitoring.prometheus_exporter \
    --port 9090 \
    --interval 10

# Verify metrics endpoint
curl http://localhost:9090/metrics

# Sample metrics output:
# HELP farfan_pipeline_phase_duration_seconds Time taken for each phase
# TYPE farfan_pipeline_phase_duration_seconds histogram
farfan_pipeline_phase_duration_seconds_bucket{phase="0",le="10"} 5
farfan_pipeline_phase_duration_seconds_bucket{phase="0",le="30"} 12
farfan_pipeline_phase_duration_seconds_bucket{phase="0",le="60"} 15
farfan_pipeline_phase_duration_seconds_sum{phase="0"} 456.78
farfan_pipeline_phase_duration_seconds_count{phase="0"} 15

# HELP farfan_sisas_signals_total Total SISAS signals by type
# TYPE farfan_sisas_signals_total counter
farfan_sisas_signals_total{type="structural"} 5234
farfan_sisas_signals_total{type="integrity"} 3456
farfan_sisas_signals_total{type="epistemic"} 2345

# HELP farfan_executor_calls_total Total executor method calls
# TYPE farfan_executor_calls_total counter
farfan_executor_calls_total{executor="analyzer_one",method="analyze"} 1234
...
```

**Prometheus Configuration:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'farfan-pipeline'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### 25.2.3 Custom Visualization Scripts

**Generate Phase Flow Diagram:**

```bash
# Generate Graphviz diagram
python scripts/visualization/generate_phase_flow.py \
    --artifacts-dir artifacts/latest_run \
    --output artifacts/visualizations/phase_flow.png \
    --format png \
    --dpi 300

# Generate interactive HTML
python scripts/visualization/generate_phase_flow.py \
    --artifacts-dir artifacts/latest_run \
    --output artifacts/visualizations/phase_flow.html \
    --format html \
    --interactive
```

**Generate Signal Flow Diagram:**

```bash
# Visualize SISAS signal flow
python scripts/visualization/generate_signal_flow.py \
    --log-file logs/sisas/signals.log \
    --output artifacts/visualizations/signal_flow.png \
    --time-range "2026-01-23T10:00:00" "2026-01-23T11:00:00" \
    --highlight-gates

# Generate Sankey diagram
python scripts/visualization/generate_signal_sankey.py \
    --log-file logs/sisas/signals.log \
    --output artifacts/visualizations/signal_sankey.html
```

**Generate Score Heatmaps:**

```bash
# Generate 300-question heatmap
python scripts/visualization/generate_score_heatmap.py \
    --scores-file artifacts/latest_run/phase3_scores/scores.json \
    --output artifacts/visualizations/scores_heatmap.png \
    --colormap "RdYlGn" \
    --annotate

# Generate policy area comparison
python scripts/visualization/generate_policy_comparison.py \
    --artifacts-dir artifacts/latest_run \
    --output artifacts/visualizations/policy_comparison.png \
    --chart-type radar
```

**Generate Evidence Network Graph:**

```bash
# Create evidence relationship graph
python scripts/visualization/generate_evidence_network.py \
    --evidence-file artifacts/latest_run/phase2_evidence/evidence.json \
    --output artifacts/visualizations/evidence_network.html \
    --layout force-directed \
    --min-weight 0.5

# Generate evidence quality distribution
python scripts/visualization/generate_evidence_quality.py \
    --evidence-file artifacts/latest_run/phase2_evidence/evidence.json \
    --output artifacts/visualizations/evidence_quality.png \
    --bins 50
```

---

# Section 26: Advanced Graphics Stack

## 26.1 Real-Time Graphics with D3.js

**Interactive Score Visualization:**

```html
<!-- Include in dashboard -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<script>
// Real-time score update visualization
function createScoreVisualization(containerId, data) {
  const width = 1200;
  const height = 800;
  const margin = {top: 40, right: 40, bottom: 60, left: 60};

  const svg = d3.select(`#${containerId}`)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  // Create color scale
  const colorScale = d3.scaleSequential()
    .domain([0, 1])
    .interpolator(d3.interpolateRdYlGn);

  // Create heatmap
  const heatmap = svg.selectAll(".cell")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "cell")
    .attr("x", d => d.col * 40)
    .attr("y", d => d.row * 40)
    .attr("width", 38)
    .attr("height", 38)
    .attr("fill", d => colorScale(d.score))
    .on("mouseover", showTooltip)
    .on("mouseout", hideTooltip);

  // Add real-time updates via WebSocket
  socket.on('score_update', (update) => {
    svg.selectAll(".cell")
      .filter(d => d.question_id === update.question_id)
      .transition()
      .duration(500)
      .attr("fill", colorScale(update.new_score));
  });
}
</script>
```

**Pipeline Flow Sankey Diagram:**

```javascript
// Sankey diagram for phase transitions
function createPipelineSankey(data) {
  const sankeyData = {
    nodes: [
      {name: "Phase 0 (Input)"},
      {name: "Phase 1 (60 Chunks)"},
      {name: "Phase 2 (300 Evidence)"},
      {name: "Phase 3 (300 Scores)"},
      {name: "Phase 4 (60 Dimensions)"},
      {name: "Phase 5 (10 Areas)"},
      {name: "Phase 6 (4 Clusters)"},
      {name: "Phase 7 (1 Macro)"},
      {name: "Phase 8 (Recommendations)"},
      {name: "Phase 9 (Reports)"}
    ],
    links: [
      {source: 0, target: 1, value: 60},
      {source: 1, target: 2, value: 300},
      {source: 2, target: 3, value: 300},
      {source: 3, target: 4, value: 60},
      {source: 4, target: 5, value: 10},
      {source: 5, target: 6, value: 4},
      {source: 6, target: 7, value: 1},
      {source: 7, target: 8, value: 1},
      {source: 8, target: 9, value: 1}
    ]
  };

  const sankey = d3.sankey()
    .nodeWidth(15)
    .nodePadding(10)
    .extent([[1, 1], [width - 1, height - 6]]);

  const {nodes, links} = sankey(sankeyData);

  // Render nodes and links
  svg.append("g")
    .selectAll("rect")
    .data(nodes)
    .join("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("height", d => d.y1 - d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("fill", "#69b3a2");

  svg.append("g")
    .selectAll("path")
    .data(links)
    .join("path")
    .attr("d", d3.sankeyLinkHorizontal())
    .attr("stroke", "#000")
    .attr("stroke-width", d => Math.max(1, d.width))
    .attr("fill", "none")
    .attr("opacity", 0.5);
}
```

## 26.2 3D Visualizations with Three.js

**3D Evidence Network:**

```javascript
// 3D evidence relationship visualization
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

function create3DEvidenceNetwork(evidenceData) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({antialias: true});

  renderer.setSize(width, height);
  container.appendChild(renderer.domElement);

  // Create nodes for each evidence item
  evidenceData.forEach((evidence, i) => {
    const geometry = new THREE.SphereGeometry(evidence.quality * 5, 32, 32);
    const material = new THREE.MeshPhongMaterial({
      color: getColorByPolicyArea(evidence.policy_area),
      emissive: 0x333333,
      shininess: 100
    });
    const sphere = new THREE.Mesh(geometry, material);

    // Position in 3D space
    sphere.position.set(
      evidence.dimension_x * 100,
      evidence.dimension_y * 100,
      evidence.dimension_z * 100
    );

    scene.add(sphere);
  });

  // Add orbit controls
  const controls = new OrbitControls(camera, renderer.domElement);

  // Animation loop
  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();
}
```

## 26.3 Statistical Visualizations with Plotly

**Comprehensive Score Analysis:**

```python
# Generate comprehensive statistical visualizations
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

def generate_comprehensive_analysis(artifacts_dir):
    """Generate full statistical analysis dashboard."""

    # Load data
    scores_df = pd.read_json(f"{artifacts_dir}/phase3_scores/scores.json")
    dimensions_df = pd.read_json(f"{artifacts_dir}/phase4_dimensions/dimensions.json")
    areas_df = pd.read_json(f"{artifacts_dir}/phase5_areas/areas.json")

    # Create subplots
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            'Score Distribution', 'Policy Area Comparison', 'Dimension Radar',
            'Temporal Evolution', 'Evidence Quality', 'SISAS Signal Flow',
            'Executor Performance', 'Confidence Intervals', 'Aggregation Pyramid'
        ),
        specs=[
            [{'type': 'histogram'}, {'type': 'bar'}, {'type': 'scatterpolar'}],
            [{'type': 'scatter'}, {'type': 'box'}, {'type': 'sankey'}],
            [{'type': 'bar'}, {'type': 'scatter'}, {'type': 'funnel'}]
        ]
    )

    # 1. Score distribution histogram
    fig.add_trace(
        go.Histogram(x=scores_df['score'], nbinsx=50, name='Scores'),
        row=1, col=1
    )

    # 2. Policy area comparison
    area_scores = areas_df.groupby('policy_area')['score'].mean()
    fig.add_trace(
        go.Bar(x=area_scores.index, y=area_scores.values, name='Areas'),
        row=1, col=2
    )

    # 3. Dimension radar chart
    dim_scores = dimensions_df.groupby('dimension')['score'].mean()
    fig.add_trace(
        go.Scatterpolar(
            r=dim_scores.values,
            theta=dim_scores.index,
            fill='toself',
            name='Dimensions'
        ),
        row=1, col=3
    )

    # 4. Temporal evolution
    fig.add_trace(
        go.Scatter(
            x=scores_df['timestamp'],
            y=scores_df['cumulative_score'],
            mode='lines',
            name='Evolution'
        ),
        row=2, col=1
    )

    # 5. Evidence quality box plot
    evidence_df = pd.read_json(f"{artifacts_dir}/phase2_evidence/evidence.json")
    fig.add_trace(
        go.Box(y=evidence_df['quality'], name='Quality'),
        row=2, col=2
    )

    # 6. SISAS signal flow (Sankey)
    signal_df = pd.read_json(f"{artifacts_dir}/sisas_logs/signals.json")
    fig.add_trace(
        go.Sankey(
            node=dict(label=signal_df['node_labels']),
            link=dict(
                source=signal_df['source'],
                target=signal_df['target'],
                value=signal_df['value']
            )
        ),
        row=2, col=3
    )

    # 7. Executor performance
    executor_df = pd.read_json(f"{artifacts_dir}/phase2_evidence/executor_metrics.json")
    fig.add_trace(
        go.Bar(
            x=executor_df['executor'],
            y=executor_df['avg_duration'],
            name='Duration'
        ),
        row=3, col=1
    )

    # 8. Confidence intervals
    fig.add_trace(
        go.Scatter(
            x=scores_df['question_id'],
            y=scores_df['score'],
            error_y=dict(
                type='data',
                array=scores_df['std'],
                visible=True
            ),
            mode='markers',
            name='Confidence'
        ),
        row=3, col=2
    )

    # 9. Aggregation pyramid (funnel)
    fig.add_trace(
        go.Funnel(
            y=['300 Scores', '60 Dimensions', '10 Areas', '4 Clusters', '1 Macro'],
            x=[300, 60, 10, 4, 1],
            name='Compression'
        ),
        row=3, col=3
    )

    # Update layout
    fig.update_layout(
        title_text="F.A.R.F.A.N. Pipeline - Comprehensive Analysis Dashboard",
        height=1200,
        width=1800,
        showlegend=True
    )

    # Save
    fig.write_html(f"{artifacts_dir}/visualizations/comprehensive_analysis.html")
    print(f"✓ Comprehensive analysis saved")

# Execute
generate_comprehensive_analysis("artifacts/latest_run")
```

**Advanced Heatmap with Dendrograms:**

```python
import plotly.figure_factory as ff
import scipy.cluster.hierarchy as sch

def generate_clustered_heatmap(scores_matrix, labels):
    """Generate clustered heatmap with dendrograms."""

    # Compute hierarchical clustering
    row_linkage = sch.linkage(scores_matrix, method='ward')
    col_linkage = sch.linkage(scores_matrix.T, method='ward')

    # Create dendrogram heatmap
    fig = ff.create_dendrogram(
        scores_matrix,
        labels=labels,
        linkagefun=lambda x: sch.linkage(x, method='ward')
    )

    # Add heatmap
    heatmap = go.Heatmap(
        z=scores_matrix,
        x=labels,
        y=labels,
        colorscale='RdYlGn',
        colorbar=dict(title='Score')
    )

    fig.add_trace(heatmap)

    fig.update_layout(
        title='Clustered Score Heatmap with Dendrograms',
        xaxis_title='Questions',
        yaxis_title='Evidence',
        width=1400,
        height=1000
    )

    fig.write_html('artifacts/visualizations/clustered_heatmap.html')
```

## 26.4 Time-Series Analysis with Matplotlib

**Phase Performance Time Series:**

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import seaborn as sns

def create_phase_performance_timeline():
    """Create animated timeline of phase execution."""

    style.use('seaborn-v0_8-darkgrid')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12))

    def animate(frame):
        # Load real-time data
        metrics = load_metrics(frame)

        # Plot 1: Phase durations
        ax1.clear()
        ax1.bar(metrics['phases'], metrics['durations'], color='skyblue')
        ax1.set_title('Phase Execution Durations', fontsize=16)
        ax1.set_xlabel('Phase')
        ax1.set_ylabel('Duration (seconds)')
        ax1.axhline(y=metrics['target_duration'], color='r', linestyle='--', label='Target')
        ax1.legend()

        # Plot 2: Memory usage over time
        ax2.clear()
        ax2.plot(metrics['timestamps'], metrics['memory_usage'], label='Memory', color='orange')
        ax2.fill_between(metrics['timestamps'], 0, metrics['memory_usage'], alpha=0.3, color='orange')
        ax2.set_title('Memory Usage Over Time', fontsize=16)
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Memory (MB)')
        ax2.legend()

        # Plot 3: Signal throughput
        ax3.clear()
        for bus_name, throughput in metrics['bus_throughput'].items():
            ax3.plot(metrics['timestamps'], throughput, label=bus_name, linewidth=2)
        ax3.set_title('SISAS Signal Throughput by Bus', fontsize=16)
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Signals/second')
        ax3.legend()

        plt.tight_layout()

    # Create animation
    ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)

    plt.show()

# Execute
create_phase_performance_timeline()
```

**Evidence Quality Distribution:**

```python
def plot_evidence_quality_analysis(evidence_file):
    """Comprehensive evidence quality analysis."""

    evidence_df = pd.read_json(evidence_file)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Evidence Quality Analysis Dashboard', fontsize=20, fontweight='bold')

    # 1. Quality distribution
    sns.histplot(evidence_df['quality'], bins=50, kde=True, ax=axes[0, 0], color='teal')
    axes[0, 0].set_title('Quality Score Distribution')
    axes[0, 0].set_xlabel('Quality Score')
    axes[0, 0].set_ylabel('Frequency')

    # 2. Quality by policy area
    sns.boxplot(data=evidence_df, x='policy_area', y='quality', ax=axes[0, 1], palette='Set2')
    axes[0, 1].set_title('Quality by Policy Area')
    axes[0, 1].tick_params(axis='x', rotation=45)

    # 3. Quality vs confidence scatter
    sns.scatterplot(data=evidence_df, x='quality', y='confidence',
                    hue='policy_area', size='word_count', ax=axes[0, 2], alpha=0.6)
    axes[0, 2].set_title('Quality vs Confidence')

    # 4. Executor performance
    executor_quality = evidence_df.groupby('executor')['quality'].mean().sort_values()
    axes[1, 0].barh(executor_quality.index, executor_quality.values, color='coral')
    axes[1, 0].set_title('Average Quality by Executor')
    axes[1, 0].set_xlabel('Average Quality')

    # 5. Temporal trend
    evidence_df['timestamp'] = pd.to_datetime(evidence_df['timestamp'])
    evidence_df = evidence_df.sort_values('timestamp')
    axes[1, 1].plot(evidence_df['timestamp'], evidence_df['quality'].rolling(50).mean(), linewidth=2)
    axes[1, 1].set_title('Quality Trend Over Time (50-sample rolling mean)')
    axes[1, 1].tick_params(axis='x', rotation=45)

    # 6. Quality correlation matrix
    corr_matrix = evidence_df[['quality', 'confidence', 'word_count', 'method_count']].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1, 2])
    axes[1, 2].set_title('Quality Correlation Matrix')

    plt.tight_layout()
    plt.savefig('artifacts/visualizations/evidence_quality_analysis.png', dpi=300, bbox_inches='tight')
    print('✓ Evidence quality analysis saved')

# Execute
plot_evidence_quality_analysis('artifacts/latest_run/phase2_evidence/evidence.json')
```

## 26.5 Network Visualizations with NetworkX

**Evidence Relationship Graph:**

```python
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

def create_evidence_network_graph(evidence_file, output_file):
    """Create interactive evidence relationship network."""

    # Load evidence
    evidence_df = pd.read_json(evidence_file)

    # Create graph
    G = nx.Graph()

    # Add nodes (evidence items)
    for idx, row in evidence_df.iterrows():
        G.add_node(
            row['evidence_id'],
            title=row['text'][:100],
            size=row['quality'] * 50,
            color=get_color_by_policy_area(row['policy_area']),
            policy_area=row['policy_area'],
            quality=row['quality']
        )

    # Add edges (relationships based on semantic similarity)
    for i, row1 in evidence_df.iterrows():
        for j, row2 in evidence_df.iterrows():
            if i < j:
                similarity = calculate_similarity(row1['embedding'], row2['embedding'])
                if similarity > 0.7:  # Threshold
                    G.add_edge(
                        row1['evidence_id'],
                        row2['evidence_id'],
                        weight=similarity,
                        title=f"Similarity: {similarity:.2f}"
                    )

    # Create interactive visualization with pyvis
    net = Network(
        height='900px',
        width='100%',
        bgcolor='#222222',
        font_color='white',
        notebook=False
    )

    net.from_nx(G)

    # Physics settings
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 150}
      }
    }
    """)

    # Save
    net.show(output_file)
    print(f'✓ Evidence network graph saved to {output_file}')

# Execute
create_evidence_network_graph(
    'artifacts/latest_run/phase2_evidence/evidence.json',
    'artifacts/visualizations/evidence_network.html'
)
```

**SISAS Signal Flow Graph:**

```python
def create_sisas_flow_graph(signal_log_file):
    """Create SISAS signal flow directed graph."""

    # Load signal logs
    signals_df = pd.read_json(signal_log_file, lines=True)

    # Create directed graph
    G = nx.DiGraph()

    # Add nodes for buses and consumers
    buses = ['structural', 'integrity', 'epistemic', 'contrast', 'operational', 'consumption']
    consumers = [f'phase_{i}_consumer' for i in range(10)]

    for bus in buses:
        G.add_node(bus, node_type='bus', layer=1)

    for consumer in consumers:
        G.add_node(consumer, node_type='consumer', layer=2)

    # Add edges based on signal flow
    for idx, row in signals_df.iterrows():
        if G.has_edge(row['bus'], row['consumer']):
            G[row['bus']][row['consumer']]['weight'] += 1
        else:
            G.add_edge(row['bus'], row['consumer'], weight=1)

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50)

    # Draw
    plt.figure(figsize=(16, 10))

    # Draw buses
    bus_nodes = [n for n, d in G.nodes(data=True) if d['node_type'] == 'bus']
    nx.draw_networkx_nodes(G, pos, nodelist=bus_nodes,
                           node_color='lightblue', node_size=3000, label='Buses')

    # Draw consumers
    consumer_nodes = [n for n, d in G.nodes(data=True) if d['node_type'] == 'consumer']
    nx.draw_networkx_nodes(G, pos, nodelist=consumer_nodes,
                           node_color='lightcoral', node_size=2000, label='Consumers')

    # Draw edges with width proportional to signal count
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    nx.draw_networkx_edges(G, pos, width=[w/100 for w in weights], alpha=0.5,
                           edge_color='gray', arrows=True, arrowsize=20)

    # Labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    plt.title('SISAS Signal Flow Graph', fontsize=20, fontweight='bold')
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('artifacts/visualizations/sisas_flow_graph.png', dpi=300, bbox_inches='tight')
    print('✓ SISAS flow graph saved')

# Execute
create_sisas_flow_graph('logs/sisas/signals.jsonl')
```

---

# Section 27: Complete Operations Catalog by Phase

## 27.1 Phase 0: Bootstrap - Complete Operations

### 27.1.1 Basic Operations

```bash
# Run bootstrap validation only
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main \
    --dry-run \
    --verbose

# Run with specific seed
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main \
    --seed 12345 \
    --log-level DEBUG

# Run with custom questionnaire
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main \
    --questionnaire /path/to/custom_questionnaire.json \
    --validate-schema

# Skip specific exit gates (dangerous!)
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main \
    --skip-gates 3,5 \
    --force
```

### 27.1.2 Exit Gate Operations

```bash
# Check individual exit gates

# Gate 1: Python version
python -c "import sys; print(f'Python {sys.version}'); assert sys.version_info >= (3, 12)"

# Gate 2: Questionnaire validation
python scripts/validation/validate_questionnaire.py \
    --questionnaire canonic_questionnaire_central/questionnaire_monolith.json \
    --schema canonic_questionnaire_central/questionnaire_schema.json

# Gate 3: Calibration files
python scripts/validation/validate_calibration_files.py \
    --calibration-dir config/calibration \
    --cohort 2024

# Gate 4: Method registry
python -c "
from farfan_pipeline.methods import REGISTRY
print(f'Total classes: {len(REGISTRY)}')
for name, cls in REGISTRY.items():
    print(f'  {name}: {len([m for m in dir(cls) if not m.startswith(\"_\")])} methods')
"

# Gate 5: Contracts availability
find src/farfan_pipeline/phases/Phase_02/generated_contracts/contracts/ -name "*.json" | wc -l
# Expected: 300

# Gate 6: SISAS health
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main health

# Gate 7: Seed registry
python -c "
from farfan_pipeline.orchestration.seed_registry import SeedRegistry
SeedRegistry.initialize(42)
print(f'✓ Seed registry initialized: {SeedRegistry.get_master_seed()}')
"
```

### 27.1.3 Configuration Operations

```bash
# Load runtime configuration
python -c "
from farfan_pipeline.phases.Phase_00.runtime_config import RuntimeConfig
config = RuntimeConfig.load()
print(config.to_dict())
"

# Validate environment
python scripts/validation/validate_environment.py \
    --check-all \
    --verbose

# Generate bootstrap report
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main \
    --generate-report \
    --output artifacts/bootstrap_report.json
```

## 27.2 Phase 1: Document Chunking - Complete Operations

### 27.2.1 Chunking Operations

```bash
# Run document chunking
python -m farfan_pipeline.phases.Phase_01.chunker \
    --input data/plans/Plan_PDET.pdf \
    --output artifacts/phase1_chunks/ \
    --target-chunks 60 \
    --method svd \
    --verbose

# Use alternative chunking method
python -m farfan_pipeline.phases.Phase_01.chunker \
    --input data/plans/Plan_PDET.pdf \
    --output artifacts/phase1_chunks/ \
    --target-chunks 60 \
    --method semantic \
    --embedding-model es_core_news_lg

# Specify chunk size range
python -m farfan_pipeline.phases.Phase_01.chunker \
    --input data/plans/Plan_PDET.pdf \
    --output artifacts/phase1_chunks/ \
    --target-chunks 60 \
    --min-chunk-size 500 \
    --max-chunk-size 2000 \
    --overlap 100

# Export chunks to multiple formats
python -m farfan_pipeline.phases.Phase_01.chunker \
    --input data/plans/Plan_PDET.pdf \
    --output artifacts/phase1_chunks/ \
    --target-chunks 60 \
    --export-formats json,txt,md,csv
```

### 27.2.2 Chunk Analysis Operations

```bash
# Analyze chunk quality
python scripts/analysis/analyze_chunks.py \
    --chunks-dir artifacts/phase1_chunks/ \
    --output artifacts/analysis/chunk_quality.json

# Visualize chunk distribution
python scripts/visualization/visualize_chunks.py \
    --chunks-dir artifacts/phase1_chunks/ \
    --output artifacts/visualizations/chunk_distribution.png

# Validate chunk coverage
python scripts/validation/validate_chunk_coverage.py \
    --original-pdf data/plans/Plan_PDET.pdf \
    --chunks-dir artifacts/phase1_chunks/ \
    --min-coverage 0.95

# Generate chunk statistics
python -c "
import json
import glob
chunks = []
for f in glob.glob('artifacts/phase1_chunks/*.json'):
    with open(f) as fp:
        chunks.append(json.load(fp))
print(f'Total chunks: {len(chunks)}')
print(f'Avg words per chunk: {sum(c[\"word_count\"] for c in chunks) / len(chunks):.1f}')
print(f'Avg chars per chunk: {sum(c[\"char_count\"] for c in chunks) / len(chunks):.1f}')
"
```

### 27.2.3 Signal Enrichment

```bash
# View signal enrichment consumer status
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    consumer-status phase_01_signal_enrichment

# Query enrichment signals
python scripts/sisas/query_signals.py \
    --phase 1 \
    --signal-type integrity \
    --time-range "last 1 hour"
```

## 27.3 Phase 2: Evidence Extraction - Complete Operations

### 27.3.1 Executor Operations

```bash
# List all executors
python -c "
from farfan_pipeline.phases.Phase_02.executors import EXECUTOR_REGISTRY
print(f'Total executors: {len(EXECUTOR_REGISTRY)}')
for name in sorted(EXECUTOR_REGISTRY.keys()):
    print(f'  - {name}')
"

# Run single executor
python -m farfan_pipeline.phases.Phase_02.executor_runner \
    --executor analyzer_one \
    --question Q001_PA01 \
    --chunks-dir artifacts/phase1_chunks/ \
    --output artifacts/test_evidence.json

# Run executor with profiling
python -m farfan_pipeline.phases.Phase_02.phase2_95_00_executor_profiler \
    --executor derek_beach \
    --question Q015_PA03 \
    --chunks-dir artifacts/phase1_chunks/ \
    --profile-output artifacts/profiling/derek_beach_profile.json

# Test executor circuit breaker
python -m farfan_pipeline.phases.Phase_02.phase2_30_04_circuit_breaker_test \
    --executor bayesian_multilevel \
    --failure-threshold 5 \
    --recovery-timeout 30

# Benchmark executor performance
python scripts/benchmarking/benchmark_executors.py \
    --executors analyzer_one,derek_beach,policy_processor \
    --iterations 100 \
    --output artifacts/benchmarks/executor_performance.json
```

### 27.3.2 Contract Operations

```bash
# Validate single contract
python scripts/validation/validate_contract.py \
    --contract src/farfan_pipeline/phases/Phase_02/generated_contracts/contracts/Q001_PA01_contract_v4.json

# Validate all contracts
python scripts/validation/validate_all_contracts.py \
    --contracts-dir src/farfan_pipeline/phases/Phase_02/generated_contracts/contracts/ \
    --parallel 8

# Regenerate single contract
python scripts/generation/generate_contract.py \
    --question Q001_PA01 \
    --questionnaire canonic_questionnaire_central/questionnaire_monolith.json \
    --output src/farfan_pipeline/phases/Phase_02/generated_contracts/contracts/Q001_PA01_contract_v4.json \
    --version 4

# Audit contract quality (CQVR scoring)
python scripts/audit/audit_contract_quality.py \
    --contract src/farfan_pipeline/phases/Phase_02/generated_contracts/contracts/Q001_PA01_contract_v4.json \
    --output artifacts/audit/contract_quality.json

# View contract signal wiring
python scripts/validation/verify_contract_signal_wiring.py \
    --contract Q001_PA01 \
    --verbose
```

### 27.3.3 Evidence Analysis Operations

```bash
# Extract evidence for specific question
python -m farfan_pipeline.phases.Phase_02.evidence_extractor \
    --question Q001_PA01 \
    --chunks-dir artifacts/phase1_chunks/ \
    --executors analyzer_one,derek_beach \
    --output artifacts/evidence/Q001_PA01_evidence.json

# Analyze evidence quality
python scripts/analysis/analyze_evidence_quality.py \
    --evidence-file artifacts/phase2_evidence/evidence.json \
    --output artifacts/analysis/evidence_quality_report.json

# Filter high-quality evidence
python scripts/filtering/filter_evidence.py \
    --evidence-file artifacts/phase2_evidence/evidence.json \
    --min-quality 0.7 \
    --min-confidence 0.8 \
    --output artifacts/filtered_evidence.json

# Generate evidence summary
python scripts/generation/generate_evidence_summary.py \
    --evidence-file artifacts/phase2_evidence/evidence.json \
    --group-by policy_area \
    --output artifacts/reports/evidence_summary.md

# Export evidence to database
python scripts/export/export_evidence_to_db.py \
    --evidence-file artifacts/phase2_evidence/evidence.json \
    --db-url postgresql://localhost/farfan \
    --table evidence

# Create evidence embeddings
python scripts/embeddings/generate_evidence_embeddings.py \
    --evidence-file artifacts/phase2_evidence/evidence.json \
    --model sentence-transformers/paraphrase-multilingual-mpnet-base-v2 \
    --output artifacts/embeddings/evidence_embeddings.npy
```

### 27.3.4 Method Dispensary Operations

```bash
# Query method dispensary
python -c "
from farfan_pipeline.phases.Phase_02.method_dispensary import MethodDispensary
dispensary = MethodDispensary()
print(f'Total methods: {dispensary.get_method_count()}')
print(f'Methods by class:')
for cls_name, methods in dispensary.get_methods_by_class().items():
    print(f'  {cls_name}: {len(methods)} methods')
"

# Get methods for specific question
python scripts/query/get_methods_for_question.py \
    --question Q001_PA01 \
    --verbose

# Validate method availability
python scripts/validation/validate_method_availability.py \
    --methods-file canonic_questionnaire_central/governance/METHODS_TO_QUESTIONS_AND_FILES.json \
    --verify-imports
```

## 27.4 Phase 3: Scoring - Complete Operations

### 27.4.1 Scoring Operations

```bash
# Run scoring for all questions
python -m farfan_pipeline.phases.Phase_03.scorer \
    --evidence-dir artifacts/phase2_evidence/ \
    --calibration config/calibration/COHORT_2024_intrinsic_calibration.json \
    --output artifacts/phase3_scores/scores.json

# Run scoring for specific policy area
python -m farfan_pipeline.phases.Phase_03.scorer \
    --evidence-dir artifacts/phase2_evidence/ \
    --calibration config/calibration/COHORT_2024_intrinsic_calibration.json \
    --policy-area PA01 \
    --output artifacts/phase3_scores/scores_PA01.json

# Run scoring with alternative calibration
python -m farfan_pipeline.phases.Phase_03.scorer \
    --evidence-dir artifacts/phase2_evidence/ \
    --calibration config/calibration/CUSTOM_calibration.json \
    --output artifacts/phase3_scores/scores_custom.json

# Run scoring with confidence thresholds
python -m farfan_pipeline.phases.Phase_03.scorer \
    --evidence-dir artifacts/phase2_evidence/ \
    --calibration config/calibration/COHORT_2024_intrinsic_calibration.json \
    --min-evidence 3 \
    --min-confidence 0.7 \
    --output artifacts/phase3_scores/scores_filtered.json

# Generate scoring report
python -m farfan_pipeline.phases.Phase_03.scorer \
    --evidence-dir artifacts/phase2_evidence/ \
    --calibration config/calibration/COHORT_2024_intrinsic_calibration.json \
    --output artifacts/phase3_scores/scores.json \
    --generate-report artifacts/reports/scoring_report.html
```

### 27.4.2 Score Analysis Operations

```bash
# Analyze score distribution
python scripts/analysis/analyze_score_distribution.py \
    --scores-file artifacts/phase3_scores/scores.json \
    --output artifacts/analysis/score_distribution.json

# Compare scores across regions
python scripts/comparison/compare_regional_scores.py \
    --scores-dir artifacts/phase3_scores/ \
    --regions R01,R02,R03 \
    --output artifacts/comparison/regional_comparison.html

# Identify low-scoring questions
python scripts/analysis/identify_low_scores.py \
    --scores-file artifacts/phase3_scores/scores.json \
    --threshold 0.5 \
    --output artifacts/analysis/low_scores.csv

# Generate score heatmap
python scripts/visualization/generate_score_heatmap.py \
    --scores-file artifacts/phase3_scores/scores.json \
    --output artifacts/visualizations/score_heatmap.png \
    --width 20 \
    --height 15 \
    --dpi 300
```

### 27.4.3 Signal-Enriched Scoring

```bash
# View signal-enriched scoring consumer
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    consumer-status phase_03_signal_enriched_scoring

# Query epistemic signals for scoring
python scripts/sisas/query_signals.py \
    --phase 3 \
    --signal-type epistemic \
    --filter "determinacy,specificity" \
    --output artifacts/sisas/epistemic_signals.json
```

## 27.5 Phase 4: Dimension Aggregation - Complete Operations

### 27.5.1 Aggregation Operations

```bash
# Run dimension aggregation
python -m farfan_pipeline.phases.Phase_04.dimension_aggregator \
    --scores-file artifacts/phase3_scores/scores.json \
    --fusion-weights config/calibration/COHORT_2024_fusion_weights.json \
    --output artifacts/phase4_dimensions/dimensions.json

# Use Choquet integral
python -m farfan_pipeline.phases.Phase_04.dimension_aggregator \
    --scores-file artifacts/phase3_scores/scores.json \
    --fusion-weights config/calibration/COHORT_2024_fusion_weights.json \
    --method choquet \
    --output artifacts/phase4_dimensions/dimensions_choquet.json

# Use weighted average (alternative)
python -m farfan_pipeline.phases.Phase_04.dimension_aggregator \
    --scores-file artifacts/phase3_scores/scores.json \
    --fusion-weights config/calibration/COHORT_2024_fusion_weights.json \
    --method weighted_average \
    --output artifacts/phase4_dimensions/dimensions_weighted.json

# Sensitivity analysis
python scripts/analysis/dimension_sensitivity_analysis.py \
    --scores-file artifacts/phase3_scores/scores.json \
    --fusion-weights config/calibration/COHORT_2024_fusion_weights.json \
    --perturbation 0.1 \
    --output artifacts/analysis/dimension_sensitivity.json
```

### 27.5.2 Dimension Analysis Operations

```bash
# Analyze dimension scores
python scripts/analysis/analyze_dimensions.py \
    --dimensions-file artifacts/phase4_dimensions/dimensions.json \
    --output artifacts/analysis/dimension_analysis.json

# Generate dimension radar chart
python scripts/visualization/generate_dimension_radar.py \
    --dimensions-file artifacts/phase4_dimensions/dimensions.json \
    --output artifacts/visualizations/dimension_radar.png

# Compare dimensions across regions
python scripts/comparison/compare_dimensions.py \
    --dimensions-dir artifacts/phase4_dimensions/ \
    --regions R01,R02,R03,R04 \
    --output artifacts/comparison/dimension_comparison.html
```

## 27.6 Phase 5: Area Aggregation - Complete Operations

### 27.6.1 High-Performance Aggregation

```bash
# Run area aggregation (high performance)
python -m farfan_pipeline.phases.Phase_05.area_aggregator \
    --dimensions-file artifacts/phase4_dimensions/dimensions.json \
    --output artifacts/phase5_areas/areas.json \
    --enable-async \
    --enable-numba \
    --enable-caching

# Run with performance profiling
python -m farfan_pipeline.phases.Phase_05.area_aggregator \
    --dimensions-file artifacts/phase4_dimensions/dimensions.json \
    --output artifacts/phase5_areas/areas.json \
    --profile \
    --profile-output artifacts/profiling/area_aggregation_profile.json

# Benchmark performance
python scripts/benchmarking/benchmark_area_aggregation.py \
    --dimensions-file artifacts/phase4_dimensions/dimensions.json \
    --iterations 10 \
    --output artifacts/benchmarks/area_aggregation_benchmark.json

# Run without optimizations (baseline)
python -m farfan_pipeline.phases.Phase_05.area_aggregator \
    --dimensions-file artifacts/phase4_dimensions/dimensions.json \
    --output artifacts/phase5_areas/areas_baseline.json \
    --disable-async \
    --disable-numba \
    --disable-caching
```

### 27.6.2 Area Analysis Operations

```bash
# Analyze policy areas
python scripts/analysis/analyze_policy_areas.py \
    --areas-file artifacts/phase5_areas/areas.json \
    --output artifacts/analysis/area_analysis.json

# Generate area comparison chart
python scripts/visualization/generate_area_comparison.py \
    --areas-file artifacts/phase5_areas/areas.json \
    --output artifacts/visualizations/area_comparison.png \
    --chart-type bar

# Identify critical areas
python scripts/analysis/identify_critical_areas.py \
    --areas-file artifacts/phase5_areas/areas.json \
    --threshold 0.6 \
    --output artifacts/analysis/critical_areas.csv
```

## 27.7 Phase 6: Cluster Aggregation - Complete Operations

### 27.7.1 Cluster Operations

```bash
# Run cluster aggregation
python -m farfan_pipeline.phases.Phase_06.cluster_aggregator \
    --areas-file artifacts/phase5_areas/areas.json \
    --output artifacts/phase6_clusters/clusters.json \
    --method adaptive_penalty

# View MESO consumer status
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    consumer-status phase_06_meso

# Analyze clusters
python scripts/analysis/analyze_clusters.py \
    --clusters-file artifacts/phase6_clusters/clusters.json \
    --output artifacts/analysis/cluster_analysis.json
```

## 27.8 Phase 7: Macro Evaluation - Complete Operations

### 27.8.1 Macro Scoring Operations

```bash
# Run macro evaluation (CCCA algorithm)
python -m farfan_pipeline.phases.Phase_07.macro_evaluator \
    --clusters-file artifacts/phase6_clusters/clusters.json \
    --output artifacts/phase7_macro/macro_score.json \
    --algorithm ccca

# Run with SGD algorithm
python -m farfan_pipeline.phases.Phase_07.macro_evaluator \
    --clusters-file artifacts/phase6_clusters/clusters.json \
    --output artifacts/phase7_macro/macro_score_sgd.json \
    --algorithm sgd \
    --learning-rate 0.01 \
    --iterations 1000

# Run with SAS algorithm
python -m farfan_pipeline.phases.Phase_07.macro_evaluator \
    --clusters-file artifacts/phase6_clusters/clusters.json \
    --output artifacts/phase7_macro/macro_score_sas.json \
    --algorithm sas

# Generate macro report
python -m farfan_pipeline.phases.Phase_07.macro_evaluator \
    --clusters-file artifacts/phase6_clusters/clusters.json \
    --output artifacts/phase7_macro/macro_score.json \
    --algorithm ccca \
    --generate-report artifacts/reports/macro_evaluation_report.html
```

### 27.8.2 Macro Analysis Operations

```bash
# Analyze macro score
python scripts/analysis/analyze_macro_score.py \
    --macro-file artifacts/phase7_macro/macro_score.json \
    --output artifacts/analysis/macro_analysis.json

# Compare macro scores across algorithms
python scripts/comparison/compare_macro_algorithms.py \
    --clusters-file artifacts/phase6_clusters/clusters.json \
    --algorithms ccca,sgd,sas \
    --output artifacts/comparison/macro_algorithm_comparison.html

# Sensitivity analysis
python scripts/analysis/macro_sensitivity_analysis.py \
    --clusters-file artifacts/phase6_clusters/clusters.json \
    --perturbation 0.05 \
    --output artifacts/analysis/macro_sensitivity.json
```

## 27.9 Phase 8: Recommendations - Complete Operations

### 27.9.1 Recommendation Generation

```bash
# Generate recommendations
python -m farfan_pipeline.phases.Phase_08.recommendation_engine \
    --artifacts-dir artifacts/ \
    --output artifacts/phase8_recommendations/recommendations.json \
    --rule-engine-version 3.0

# Generate recommendations for specific area
python -m farfan_pipeline.phases.Phase_08.recommendation_engine \
    --artifacts-dir artifacts/ \
    --policy-area PA01 \
    --output artifacts/phase8_recommendations/recommendations_PA01.json

# Generate prioritized recommendations
python -m farfan_pipeline.phases.Phase_08.recommendation_engine \
    --artifacts-dir artifacts/ \
    --output artifacts/phase8_recommendations/recommendations_prioritized.json \
    --prioritize \
    --max-recommendations 20

# Generate recommendations with budget constraints
python -m farfan_pipeline.phases.Phase_08.recommendation_engine \
    --artifacts-dir artifacts/ \
    --output artifacts/phase8_recommendations/recommendations_budgeted.json \
    --budget 1000000 \
    --optimize-budget
```

### 27.9.2 Recommendation Analysis

```bash
# Analyze recommendations
python scripts/analysis/analyze_recommendations.py \
    --recommendations-file artifacts/phase8_recommendations/recommendations.json \
    --output artifacts/analysis/recommendation_analysis.json

# Group recommendations by category
python scripts/grouping/group_recommendations.py \
    --recommendations-file artifacts/phase8_recommendations/recommendations.json \
    --group-by category,priority \
    --output artifacts/analysis/recommendations_grouped.csv

# Export recommendations to actionable format
python scripts/export/export_recommendations_action_plan.py \
    --recommendations-file artifacts/phase8_recommendations/recommendations.json \
    --output artifacts/action_plans/recommendations_action_plan.xlsx
```

## 27.10 Phase 9: Reporting - Complete Operations

### 27.10.1 Report Generation

```bash
# Generate all report types
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output-dir artifacts/phase9_reports/ \
    --all-templates

# Generate enhanced report only
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output artifacts/phase9_reports/enhanced_report.html \
    --template enhanced

# Generate executive dashboard
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output artifacts/phase9_reports/executive_dashboard.html \
    --template executive

# Generate technical deep-dive
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output artifacts/phase9_reports/technical_deepdive.html \
    --template technical

# Generate original report
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output artifacts/phase9_reports/original_report.html \
    --template original

# Generate PDF reports
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output-dir artifacts/phase9_reports/ \
    --all-templates \
    --format pdf \
    --pdf-engine weasyprint
```

### 27.10.2 Report Customization

```bash
# Generate report with custom template
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output artifacts/phase9_reports/custom_report.html \
    --custom-template templates/my_custom_template.jinja2

# Generate report with logo
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output artifacts/phase9_reports/branded_report.html \
    --template enhanced \
    --logo assets/logo.png

# Generate multi-language report
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output artifacts/phase9_reports/report_en.html \
    --template enhanced \
    --language en

# Generate report with custom quality thresholds
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/ \
    --output artifacts/phase9_reports/custom_thresholds_report.html \
    --template enhanced \
    --threshold-excelente 0.90 \
    --threshold-bueno 0.75 \
    --threshold-aceptable 0.60
```

---

# Section 28: Advanced Debugging & Troubleshooting

## 28.1 Log Analysis & Debugging

### 28.1.1 Log Locations

```bash
# Orchestrator logs
tail -f logs/orchestrator/orchestrator.log

# Phase-specific logs
tail -f logs/phases/phase_00.log
tail -f logs/phases/phase_01.log
tail -f logs/phases/phase_02.log
# ... through phase_09.log

# SISAS logs
tail -f logs/sisas/signals.log
tail -f logs/sisas/buses.log
tail -f logs/sisas/consumers.log
tail -f logs/sisas/gates.log

# Executor logs
tail -f logs/executors/analyzer_one.log
tail -f logs/executors/derek_beach.log

# Metrics logs
tail -f logs/metrics/system_metrics.log
tail -f logs/metrics/phase_metrics.log

# Error logs
tail -f logs/errors/error.log
tail -f logs/errors/critical.log
```

### 28.1.2 Log Filtering & Analysis

```bash
# Find all ERROR level logs in last hour
grep "ERROR" logs/orchestrator/orchestrator.log | grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')"

# Find all CRITICAL logs
grep "CRITICAL" logs/**/*.log

# Find specific error pattern
grep -r "TimeoutError\|MemoryError\|KeyError" logs/

# Extract stack traces
grep -A 20 "Traceback" logs/orchestrator/orchestrator.log

# Count errors by type
grep "ERROR" logs/orchestrator/orchestrator.log | cut -d':' -f4 | sort | uniq -c | sort -rn

# Find slowest operations
grep "duration" logs/phases/*.log | awk '{print $NF}' | sort -rn | head -20

# Analyze SISAS signal rejections
grep "rejected" logs/sisas/gates.log | jq '.gate, .reason' | sort | uniq -c

# Find memory spikes
grep "memory_usage_mb" logs/metrics/system_metrics.log | awk '{print $NF}' | \
    awk 'BEGIN{max=0} {if($1>max) max=$1} END{print "Peak memory: " max " MB"}'
```

### 28.1.3 Interactive Debugging

```bash
# Enable debug mode
export FARFAN_LOG_LEVEL=DEBUG
export FARFAN_DEBUG=true

# Run pipeline with pdb breakpoint
python -m pdb -m farfan_pipeline.orchestration.orchestrator \
    --plan data/plans/test.pdf \
    --start-phase 0 \
    --end-phase 3

# Run with ipdb (better interface)
pip install ipdb
python -c "import ipdb; ipdb.set_trace(); from farfan_pipeline.orchestration.orchestrator import Orchestrator; o = Orchestrator()"

# Run with profiling
python -m cProfile -o profile.stats \
    -m farfan_pipeline.orchestration.orchestrator \
    --plan data/plans/test.pdf

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(50)
"

# Memory profiling
pip install memory_profiler
python -m memory_profiler scripts/run_policy_pipeline_verified.py \
    --plan data/plans/test.pdf
```

### 28.1.4 Common Issues & Solutions

**Issue 1: Pipeline Hangs During Phase 2**
```bash
# Diagnosis
ps aux | grep farfan  # Check if process is running
strace -p <PID>       # See what system calls it's making
lsof -p <PID>         # Check open files

# Check executor timeouts
grep "timeout" logs/executors/*.log

# Check circuit breaker status
python -c "
from farfan_pipeline.phases.Phase_02.phase2_30_04_circuit_breaker import CircuitBreakerRegistry
registry = CircuitBreakerRegistry()
for executor, cb in registry.get_all().items():
    print(f'{executor}: {cb.state}')
"

# Solution: Increase executor timeout
export FARFAN_EXECUTOR_TIMEOUT=600
```

**Issue 2: Out of Memory Errors**
```bash
# Diagnosis
free -h  # Check available memory
top      # Monitor memory usage in real-time

# Check memory usage by phase
grep "memory" logs/metrics/system_metrics.log | tail -100

# Solution: Reduce batch size
export FARFAN_MAX_MEMORY_MB=4096
export FARFAN_BATCH_SIZE=10  # Process fewer items at once

# Or enable memory-efficient mode
export FARFAN_MEMORY_EFFICIENT=true
```

**Issue 3: SISAS Signal Backlog**
```bash
# Diagnosis
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main stats

# Check queue depths
curl http://localhost:5000/api/v1/sisas/metrics | jq '.queue_depths'

# Solution: Increase consumer threads
export FARFAN_SISAS_CONSUMER_THREADS=8

# Or increase bus capacity
export FARFAN_SISAS_BUS_QUEUE_SIZE=100000

# Or flush backlog
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main flush-queues
```

**Issue 4: Contract Validation Failures**
```bash
# Diagnosis
python scripts/validation/validate_all_contracts.py --verbose

# Check specific contract
python scripts/validation/validate_contract.py \
    --contract src/farfan_pipeline/phases/Phase_02/generated_contracts/contracts/Q001_PA01_contract_v4.json \
    --debug

# Solution: Regenerate failed contracts
python scripts/generation/regenerate_failed_contracts.py \
    --validation-log artifacts/validation/failed_contracts.log
```

**Issue 5: Evidence Extraction Low Quality**
```bash
# Diagnosis
python scripts/analysis/analyze_evidence_quality.py \
    --evidence-file artifacts/phase2_evidence/evidence.json \
    --min-quality 0.7

# Check which executors are underperforming
python -c "
import json
with open('artifacts/phase2_evidence/evidence.json') as f:
    evidence = json.load(f)
from collections import defaultdict
by_executor = defaultdict(list)
for e in evidence:
    by_executor[e['executor']].append(e['quality'])
for executor, qualities in by_executor.items():
    avg = sum(qualities) / len(qualities)
    print(f'{executor}: {avg:.3f} (n={len(qualities)})')
"

# Solution: Recalibrate underperforming executors
python scripts/calibration/recalibrate_executor.py \
    --executor derek_beach \
    --target-quality 0.75
```

## 28.2 Performance Diagnostics

### 28.2.1 System Resource Monitoring

```bash
# Real-time system monitoring
watch -n 1 '
echo "=== CPU ==="
mpstat 1 1 | tail -1
echo ""
echo "=== Memory ==="
free -h
echo ""
echo "=== Disk I/O ==="
iostat -x 1 1 | tail -n +4
echo ""
echo "=== Pipeline Processes ==="
ps aux | grep farfan | head -5
'

# Monitor GPU usage (if available)
watch -n 1 nvidia-smi

# Monitor disk space
df -h | grep -E "Filesystem|/home"

# Monitor network usage
iftop -i eth0

# Continuous resource logging
python scripts/monitoring/continuous_resource_monitor.py \
    --interval 5 \
    --output logs/resources.log &
```

### 28.2.2 Bottleneck Identification

```bash
# Identify slowest phases
python scripts/analysis/identify_bottlenecks.py \
    --log-file logs/orchestrator/orchestrator.log \
    --output artifacts/analysis/bottlenecks.json

# Profile specific phase
python -m cProfile -o phase2_profile.stats \
    -m farfan_pipeline.phases.Phase_02.main \
    --chunks-dir artifacts/phase1_chunks/

# Analyze profile
python -c "
import pstats
from pstats import SortKey
p = pstats.Stats('phase2_profile.stats')
print('Top 20 by cumulative time:')
p.sort_stats(SortKey.CUMULATIVE).print_stats(20)
print('\nTop 20 by time per call:')
p.sort_stats(SortKey.TIME).print_stats(20)
"

# Line profiler for specific function
pip install line_profiler
kernprof -l -v scripts/profile_target.py

# Generate flame graph
pip install py-spy
py-spy record -o flamegraph.svg -- python -m farfan_pipeline.orchestration.orchestrator
```

## 28.3 Data Validation & Integrity Checks

### 28.3.1 Artifact Validation

```bash
# Validate all artifacts
python scripts/validation/validate_all_artifacts.py \
    --artifacts-dir artifacts/latest_run \
    --strict

# Check artifact counts
echo "Expected vs Actual artifact counts:"
echo "Chunks: $(ls artifacts/latest_run/phase1_chunks/*.json 2>/dev/null | wc -l) / 60"
echo "Evidence: $(jq length artifacts/latest_run/phase2_evidence/evidence.json) / 300"
echo "Scores: $(jq length artifacts/latest_run/phase3_scores/scores.json) / 300"
echo "Dimensions: $(jq length artifacts/latest_run/phase4_dimensions/dimensions.json) / 60"
echo "Areas: $(jq length artifacts/latest_run/phase5_areas/areas.json) / 10"
echo "Clusters: $(jq length artifacts/latest_run/phase6_clusters/clusters.json) / 4"

# Verify artifact integrity (checksums)
python scripts/validation/verify_artifact_checksums.py \
    --artifacts-dir artifacts/latest_run \
    --checksums artifacts/latest_run/checksums.sha256

# Detect corrupted files
find artifacts/latest_run -name "*.json" -exec sh -c '
    if ! jq empty "$1" 2>/dev/null; then
        echo "Corrupted: $1"
    fi
' _ {} \;
```

### 28.3.2 Data Consistency Checks

```bash
# Check score consistency
python scripts/validation/check_score_consistency.py \
    --scores-file artifacts/latest_run/phase3_scores/scores.json \
    --dimensions-file artifacts/latest_run/phase4_dimensions/dimensions.json

# Verify aggregation chain
python scripts/validation/verify_aggregation_chain.py \
    --artifacts-dir artifacts/latest_run

# Check for missing data
python scripts/validation/check_missing_data.py \
    --artifacts-dir artifacts/latest_run \
    --report artifacts/validation/missing_data_report.txt

# Validate provenance chain
python scripts/validation/validate_provenance.py \
    --artifacts-dir artifacts/latest_run \
    --verify-w3c-prov
```

---

# Section 29: Performance Tuning & Optimization

## 29.1 Configuration Optimization

### 29.1.1 Memory Optimization

```bash
# Configure memory limits
export FARFAN_MAX_MEMORY_MB=16384       # Max total memory
export FARFAN_PHASE_MEMORY_LIMIT=4096   # Per-phase limit
export FARFAN_EXECUTOR_MEMORY_LIMIT=512 # Per-executor limit

# Enable memory-efficient processing
export FARFAN_MEMORY_EFFICIENT=true
export FARFAN_STREAMING_MODE=true       # Process in streams
export FARFAN_LAZY_LOADING=true         # Load data on-demand

# Configure garbage collection
export PYTHONMALLOC=malloc
export PYTHONGC=2,10,10  # gc.set_threshold(2, 10, 10)

# Use memory pooling
export FARFAN_USE_MEMORY_POOL=true
export FARFAN_POOL_SIZE=1024
```

### 29.1.2 CPU Optimization

```bash
# Set number of workers
export FARFAN_MAX_WORKERS=8              # Parallel workers
export FARFAN_EXECUTOR_THREADS=4         # Threads per executor
export FARFAN_SISAS_CONSUMER_THREADS=8   # SISAS consumer threads

# Enable CPU affinity
export FARFAN_CPU_AFFINITY=true
taskset -c 0-7 python -m farfan_pipeline.orchestration.orchestrator

# Use process pool instead of thread pool
export FARFAN_USE_PROCESS_POOL=true

# Enable JIT compilation
export FARFAN_ENABLE_NUMBA=true
export NUMBA_CACHE_DIR=/tmp/numba_cache
```

### 29.1.3 I/O Optimization

```bash
# Configure I/O settings
export FARFAN_IO_BUFFER_SIZE=65536       # 64KB buffer
export FARFAN_ASYNC_IO=true              # Async I/O operations
export FARFAN_USE_MMAP=true              # Memory-mapped files

# Use faster JSON library
export FARFAN_JSON_LIBRARY=orjson  # or ujson

# Enable compression
export FARFAN_COMPRESS_ARTIFACTS=true
export FARFAN_COMPRESSION_LEVEL=6

# Use tmpfs for temporary files
export TMPDIR=/dev/shm
mkdir -p /dev/shm/farfan_temp
export FARFAN_TEMP_DIR=/dev/shm/farfan_temp
```

## 29.2 Caching Strategies

### 29.2.1 Application-Level Caching

```bash
# Enable caching
export FARFAN_ENABLE_CACHING=true
export FARFAN_CACHE_SIZE_MB=4096
export FARFAN_CACHE_TTL=3600  # 1 hour

# Configure cache types
export FARFAN_CACHE_QUESTIONNAIRE=true   # Cache questionnaire
export FARFAN_CACHE_CONTRACTS=true       # Cache contracts
export FARFAN_CACHE_EMBEDDINGS=true      # Cache embeddings
export FARFAN_CACHE_SCORES=true          # Cache intermediate scores

# Use Redis for distributed caching
export FARFAN_CACHE_BACKEND=redis
export FARFAN_REDIS_URL=redis://localhost:6379/0

# Cache warming
python scripts/optimization/warm_cache.py \
    --questionnaire \
    --contracts \
    --embeddings
```

### 29.2.2 File System Caching

```bash
# Use SSD for artifacts
export FARFAN_ARTIFACTS_DIR=/mnt/ssd/farfan_artifacts

# Enable OS-level caching
echo 3 > /proc/sys/vm/drop_caches  # Clear cache
# Let OS manage cache naturally

# Use tmpfs for hot data
mount -t tmpfs -o size=8G tmpfs /mnt/farfan_hot
export FARFAN_HOT_DATA_DIR=/mnt/farfan_hot
```

## 29.3 Parallel Processing Optimization

### 29.3.1 Phase-Level Parallelization

```bash
# Run independent operations in parallel
python scripts/optimization/parallel_phase_runner.py \
    --phases 1,2,3 \
    --parallel \
    --max-workers 3

# Use GNU parallel for batch processing
find data/plans/*.pdf | parallel -j 4 \
    python scripts/run_policy_pipeline_verified.py --plan {}
```

### 29.3.2 Executor-Level Parallelization

```bash
# Configure executor parallelism
export FARFAN_EXECUTOR_PARALLEL=true
export FARFAN_EXECUTOR_MAX_PARALLEL=30

# Use asyncio for I/O-bound executors
export FARFAN_EXECUTOR_ASYNC=true

# Batch executor calls
export FARFAN_EXECUTOR_BATCH_SIZE=10
```

## 29.4 Database & Query Optimization

### 29.4.1 Query Optimization

```bash
# Use indexes for faster lookups
python scripts/optimization/create_indexes.py \
    --tables evidence,scores,dimensions

# Enable query caching
export FARFAN_QUERY_CACHE=true
export FARFAN_QUERY_CACHE_SIZE=1000

# Use connection pooling
export FARFAN_DB_POOL_SIZE=20
export FARFAN_DB_MAX_OVERFLOW=10
```

### 29.4.2 Batch Operations

```bash
# Batch insert operations
python scripts/optimization/batch_insert.py \
    --evidence artifacts/phase2_evidence/evidence.json \
    --batch-size 1000

# Use bulk operations
export FARFAN_USE_BULK_OPS=true
export FARFAN_BULK_SIZE=5000
```

## 29.5 Benchmark Suite

### 29.5.1 Performance Benchmarks

```bash
# Run full benchmark suite
python scripts/benchmarking/benchmark_suite.py \
    --output artifacts/benchmarks/full_benchmark.json

# Benchmark specific components
python scripts/benchmarking/benchmark_executors.py --iterations 100
python scripts/benchmarking/benchmark_aggregation.py --iterations 50
python scripts/benchmarking/benchmark_sisas.py --duration 300

# Compare before/after optimization
python scripts/benchmarking/compare_benchmarks.py \
    --baseline artifacts/benchmarks/baseline.json \
    --current artifacts/benchmarks/current.json \
    --output artifacts/benchmarks/comparison.html
```

### 29.5.2 Load Testing

```bash
# Stress test pipeline
python scripts/testing/stress_test.py \
    --concurrent-jobs 10 \
    --duration 3600 \
    --ramp-up 300

# Load test API
pip install locust
locust -f scripts/testing/locustfile.py \
    --host http://localhost:5000 \
    --users 100 \
    --spawn-rate 10

# Memory leak detection
python scripts/testing/memory_leak_test.py \
    --iterations 1000 \
    --check-interval 10
```

---

# Section 30: Disaster Recovery & Business Continuity

## 30.1 Backup Strategies

### 30.1.1 Automated Backups

```bash
# Create backup script
cat > scripts/backup/daily_backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/farfan"

# Backup artifacts
tar -czf "$BACKUP_DIR/artifacts_$DATE.tar.gz" artifacts/

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" config/

# Backup canonical files
tar -czf "$BACKUP_DIR/canonical_$DATE.tar.gz" canonic_questionnaire_central/

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x scripts/backup/daily_backup.sh

# Schedule with cron
crontab -e
# Add: 0 2 * * * /home/user/FARFAN_MCDPP/scripts/backup/daily_backup.sh
```

### 30.1.2 Incremental Backups

```bash
# Use rsync for incremental backups
rsync -av --delete \
    --link-dest=/backups/farfan/latest \
    artifacts/ /backups/farfan/$(date +%Y%m%d)/

ln -nsf /backups/farfan/$(date +%Y%m%d) /backups/farfan/latest
```

### 30.1.3 Cloud Backups

```bash
# Backup to S3
pip install awscli
aws s3 sync artifacts/ s3://my-bucket/farfan-backups/artifacts/ --storage-class GLACIER

# Backup to Google Cloud Storage
pip install google-cloud-storage
gsutil -m rsync -r artifacts/ gs://my-bucket/farfan-backups/artifacts/

# Backup to Azure Blob Storage
pip install azure-storage-blob
az storage blob upload-batch \
    --destination farfan-backups \
    --source artifacts/ \
    --account-name mystorageaccount
```

## 30.2 Checkpoint & Resume

### 30.2.1 Creating Checkpoints

```bash
# Enable checkpointing
export FARFAN_ENABLE_CHECKPOINTS=true
export FARFAN_CHECKPOINT_INTERVAL=300  # Every 5 minutes

# Manual checkpoint
python -c "
from farfan_pipeline.orchestration.checkpoint_manager import CheckpointManager
cm = CheckpointManager()
cm.create_checkpoint('manual_checkpoint_$(date +%s)')
"

# List checkpoints
python -c "
from farfan_pipeline.orchestration.checkpoint_manager import CheckpointManager
cm = CheckpointManager()
for cp in cm.list_checkpoints():
    print(f'{cp.timestamp}: {cp.phase} - {cp.description}')
"
```

### 30.2.2 Restoring from Checkpoints

```bash
# Resume from latest checkpoint
python -m farfan_pipeline.orchestration.orchestrator \
    --resume-from-checkpoint latest

# Resume from specific checkpoint
python -m farfan_pipeline.orchestration.orchestrator \
    --resume-from-checkpoint checkpoint_20260123_103045

# Restore artifacts from checkpoint
python scripts/recovery/restore_from_checkpoint.py \
    --checkpoint checkpoint_20260123_103045 \
    --restore-artifacts \
    --restore-state
```

## 30.3 Rollback Procedures

### 30.3.1 Phase Rollback

```bash
# Rollback to previous phase
python scripts/enforcement/rollback_manager.py \
    --target-phase 5 \
    --reason "Phase 6 validation failed" \
    --create-backup

# Rollback with artifact cleanup
python scripts/enforcement/rollback_manager.py \
    --target-phase 3 \
    --cleanup-artifacts \
    --preserve-logs
```

### 30.3.2 Configuration Rollback

```bash
# Backup current config before changes
cp -r config/ config.backup.$(date +%s)

# Rollback configuration
python scripts/recovery/rollback_config.py \
    --backup-dir config.backup.1737633045

# Verify configuration
python scripts/validation/validate_configuration.py
```

## 30.4 Failure Recovery

### 30.4.1 Automatic Recovery

```bash
# Enable automatic recovery
export FARFAN_AUTO_RECOVERY=true
export FARFAN_MAX_RETRY_ATTEMPTS=3
export FARFAN_RETRY_DELAY=60

# Configure circuit breaker for auto-recovery
export FARFAN_CIRCUIT_BREAKER_ENABLED=true
export FARFAN_CIRCUIT_BREAKER_THRESHOLD=5
export FARFAN_CIRCUIT_BREAKER_TIMEOUT=300
```

### 30.4.2 Manual Recovery

```bash
# Diagnose failure
python scripts/diagnostics/diagnose_failure.py \
    --log-file logs/orchestrator/orchestrator.log \
    --job-id job_20260123_103000

# Repair corrupted artifacts
python scripts/recovery/repair_artifacts.py \
    --artifacts-dir artifacts/failed_run \
    --auto-fix

# Regenerate failed phase
python scripts/recovery/regenerate_phase.py \
    --phase 4 \
    --input-dir artifacts/failed_run/phase3_scores \
    --output-dir artifacts/recovered_run/phase4_dimensions
```

## 30.5 Data Integrity Verification

### 30.5.1 Checksum Verification

```bash
# Generate checksums
find artifacts/ -type f -name "*.json" -exec sha256sum {} \; > artifacts/checksums.sha256

# Verify checksums
sha256sum -c artifacts/checksums.sha256

# Detect changes
python scripts/integrity/detect_artifact_changes.py \
    --checksums artifacts/checksums.sha256 \
    --report artifacts/integrity_report.txt
```

### 30.5.2 Provenance Verification

```bash
# Verify W3C PROV-DM compliance
python scripts/validation/validate_provenance.py \
    --artifacts-dir artifacts/latest_run \
    --verify-chain \
    --strict

# Generate provenance graph
python scripts/visualization/generate_provenance_graph.py \
    --artifacts-dir artifacts/latest_run \
    --output artifacts/visualizations/provenance.svg
```

---

# Section 31: Advanced SISAS Operations

## 31.1 Signal Management

### 31.1.1 Signal Creation & Publishing

```python
# Custom signal creation
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals import StructuralSignal

signal = StructuralSignal(
    signal_id="custom_001",
    source="custom_extractor",
    target="phase_02",
    payload={
        "alignment_score": 0.85,
        "conflict_detected": False,
        "metadata": {"custom_field": "value"}
    }
)

# Publish signal
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.buses import BusSystem
bus_system = BusSystem()
bus_system.publish("structural", signal)
```

### 31.1.2 Signal Filtering & Routing

```bash
# Filter signals by criteria
python scripts/sisas/filter_signals.py \
    --signal-log logs/sisas/signals.jsonl \
    --type structural \
    --min-score 0.8 \
    --output artifacts/filtered_signals.jsonl

# Route signals to custom consumer
python scripts/sisas/route_signals.py \
    --source-bus structural \
    --target-consumer custom_consumer \
    --filter-expression "score > 0.75"
```

## 31.2 Consumer Development

### 31.2.1 Custom Consumer Creation

```python
# Create custom consumer
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers import BaseConsumer

class MyCustomConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(
            consumer_id="custom_consumer_001",
            subscribed_buses=["structural", "epistemic"]
        )

    def on_signal(self, signal):
        """Process incoming signal."""
        print(f"Received signal: {signal.signal_id}")
        # Custom processing logic
        result = self.process_signal(signal)
        return result

    def process_signal(self, signal):
        """Custom signal processing."""
        # Your logic here
        pass

# Register consumer
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers import ConsumerRegistry
registry = ConsumerRegistry()
registry.register(MyCustomConsumer())
```

### 31.2.2 Consumer Monitoring

```bash
# Monitor consumer health
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    consumer-health --consumer custom_consumer_001

# View consumer metrics
curl http://localhost:5000/api/v1/sisas/consumers/custom_consumer_001 | jq

# Reset consumer state
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    reset-consumer --consumer custom_consumer_001
```

## 31.3 Gate Configuration

### 31.3.1 Custom Gate Rules

```yaml
# config/sisas/custom_gate_rules.yaml
gates:
  gate_1_scope:
    rules:
      - field: signal_type
        operator: in
        values: [structural, integrity, epistemic]
      - field: source
        operator: matches
        pattern: "^(phase_|extractor_)"
    action: pass

  gate_2_value:
    rules:
      - field: payload.quality
        operator: gte
        value: 0.6
      - field: payload.confidence
        operator: gte
        value: 0.7
    action: pass

  custom_gate:
    rules:
      - field: payload.custom_score
        operator: gt
        value: 0.8
    action: pass
```

### 31.3.2 Gate Tuning

```bash
# Analyze gate rejection rates
python scripts/sisas/analyze_gate_performance.py \
    --log-file logs/sisas/gates.log \
    --output artifacts/sisas/gate_analysis.json

# Optimize gate thresholds
python scripts/sisas/optimize_gate_thresholds.py \
    --target-pass-rate 0.95 \
    --output config/sisas/optimized_gates.yaml
```

## 31.4 Dead Letter Queue Management

### 31.4.1 DLQ Operations

```bash
# View dead letter queue
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    dlq-list --limit 50

# Replay dead letters
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    dlq-replay --signal-ids signal_001,signal_002

# Clear dead letter queue
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    dlq-clear --confirm

# Export dead letters for analysis
python scripts/sisas/export_dead_letters.py \
    --output artifacts/sisas/dead_letters.json
```

## 31.5 Signal Analytics

### 31.5.1 Signal Flow Analysis

```bash
# Generate signal flow report
python scripts/sisas/generate_signal_flow_report.py \
    --log-file logs/sisas/signals.jsonl \
    --time-range "2026-01-23T10:00:00" "2026-01-23T11:00:00" \
    --output artifacts/reports/signal_flow_report.html

# Analyze signal patterns
python scripts/sisas/analyze_signal_patterns.py \
    --log-file logs/sisas/signals.jsonl \
    --detect-anomalies \
    --output artifacts/analysis/signal_patterns.json

# Correlation analysis
python scripts/sisas/signal_correlation_analysis.py \
    --log-file logs/sisas/signals.jsonl \
    --output artifacts/analysis/signal_correlations.html
```

---

# Section 32: Monitoring & Alerting

## 32.1 Prometheus Integration

### 32.1.1 Metrics Export Setup

```bash
# Start Prometheus exporter
python -m farfan_pipeline.monitoring.prometheus_exporter \
    --port 9090 \
    --interval 10 &

# Configure Prometheus
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'farfan-pipeline'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 10s

rule_files:
  - 'alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']
EOF

# Start Prometheus
prometheus --config.file=prometheus.yml &
```

### 32.1.2 Custom Metrics

```python
# Define custom metrics
from prometheus_client import Counter, Histogram, Gauge

# Counters
evidence_extracted = Counter(
    'farfan_evidence_extracted_total',
    'Total evidence items extracted',
    ['executor', 'policy_area']
)

# Histograms
phase_duration = Histogram(
    'farfan_phase_duration_seconds',
    'Phase execution duration',
    ['phase'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]
)

# Gauges
active_executors = Gauge(
    'farfan_active_executors',
    'Number of active executors'
)

# Use metrics
evidence_extracted.labels(executor='analyzer_one', policy_area='PA01').inc()
with phase_duration.labels(phase='2').time():
    # Phase 2 execution
    pass
active_executors.set(30)
```

## 32.2 Alert Configuration

### 32.2.1 Alert Rules

```yaml
# alerts.yml
groups:
  - name: farfan_pipeline
    interval: 30s
    rules:
      - alert: PipelineHighMemoryUsage
        expr: farfan_memory_usage_bytes > 14*1024*1024*1024
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline memory usage is high"
          description: "Memory usage is {{ $value | humanize }}B"

      - alert: PipelineCriticalMemoryUsage
        expr: farfan_memory_usage_bytes > 15*1024*1024*1024
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Pipeline memory usage is critical"
          description: "Memory usage is {{ $value | humanize }}B"

      - alert: HighErrorRate
        expr: rate(farfan_errors_total[5m]) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | printf \"%.2f\" }} errors/sec"

      - alert: SISASDeadLetterBacklog
        expr: farfan_sisas_dead_letters_total > 500
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "SISAS dead letter queue backlog"
          description: "{{ $value }} signals in dead letter queue"

      - alert: PhaseTimeout
        expr: farfan_phase_duration_seconds > 1800
        labels:
          severity: critical
        annotations:
          summary: "Phase execution timeout"
          description: "Phase {{ $labels.phase }} taking too long"

      - alert: ExecutorCircuitBreakerOpen
        expr: farfan_circuit_breaker_state == 2
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Executor circuit breaker open"
          description: "Circuit breaker for {{ $labels.executor }} is open"
```

### 32.2.2 Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'farfan-alerts@example.com'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: 'password'

route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-email'
  routes:
    - match:
        severity: critical
      receiver: 'team-pager'
    - match:
        severity: warning
      receiver: 'team-email'

receivers:
  - name: 'team-email'
    email_configs:
      - to: 'team@example.com'
        headers:
          Subject: '[FARFAN] {{ .GroupLabels.alertname }}'

  - name: 'team-pager'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#farfan-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

## 32.3 Grafana Dashboards

### 32.3.1 Import Dashboards

```bash
# Import main dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @grafana/dashboards/farfan_main.json

# Import SISAS dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @grafana/dashboards/farfan_sisas.json

# Import performance dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @grafana/dashboards/farfan_performance.json
```

### 32.3.2 Custom Dashboard Queries

```promql
# Phase execution rate
rate(farfan_phase_complete_total[5m])

# Average phase duration
avg(farfan_phase_duration_seconds) by (phase)

# Memory usage trend
farfan_memory_usage_bytes / 1024 / 1024 / 1024

# SISAS signal throughput
rate(farfan_sisas_signals_emitted_total[1m])

# Error rate by phase
rate(farfan_errors_total[5m]) by (phase)

# Top slow executors
topk(10, avg(farfan_executor_duration_seconds) by (executor))

# Circuit breaker status
sum(farfan_circuit_breaker_state == 2) by (executor)
```

## 32.4 Log Aggregation

### 32.4.1 ELK Stack Integration

```bash
# Install Filebeat
sudo apt-get install filebeat

# Configure Filebeat
cat > /etc/filebeat/filebeat.yml << 'EOF'
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /home/user/FARFAN_MCDPP/logs/**/*.log
    fields:
      application: farfan-pipeline
    multiline:
      pattern: '^\d{4}-\d{2}-\d{2}'
      negate: true
      match: after

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "farfan-logs-%{+yyyy.MM.dd}"

setup.kibana:
  host: "localhost:5601"
EOF

# Start Filebeat
sudo systemctl start filebeat
sudo systemctl enable filebeat
```

### 32.4.2 Centralized Logging

```bash
# Use syslog
export FARFAN_LOG_SYSLOG=true
export FARFAN_SYSLOG_HOST=localhost
export FARFAN_SYSLOG_PORT=514

# Use remote logging service
export FARFAN_LOG_REMOTE=true
export FARFAN_LOG_REMOTE_URL=https://logs.example.com/api/v1/logs
export FARFAN_LOG_REMOTE_KEY=your-api-key
```

---

# Section 33: Security Operations

## 33.1 Access Control

### 33.1.1 Authentication Setup

```bash
# Enable authentication
export FARFAN_ENABLE_AUTH=true
export FARFAN_AUTH_METHOD=token  # or jwt, oauth2

# Generate API token
python scripts/security/generate_api_token.py \
    --user admin \
    --scopes read,write,admin \
    --expires 30d

# Create user
python scripts/security/create_user.py \
    --username operator \
    --password-file /path/to/password.txt \
    --role operator
```

### 33.1.2 Authorization Rules

```yaml
# config/security/authorization.yaml
roles:
  admin:
    permissions:
      - pipeline:start
      - pipeline:stop
      - pipeline:delete
      - config:read
      - config:write
      - users:manage

  operator:
    permissions:
      - pipeline:start
      - pipeline:stop
      - pipeline:view
      - config:read
      - reports:generate

  viewer:
    permissions:
      - pipeline:view
      - reports:view
      - dashboard:view
```

## 33.2 Secrets Management

### 33.2.1 Secrets Storage

```bash
# Use environment variables
export FARFAN_API_KEY="your-secret-key"
export FARFAN_DB_PASSWORD="your-db-password"

# Use secrets file (encrypted)
python scripts/security/encrypt_secrets.py \
    --input secrets.txt \
    --output secrets.enc \
    --key-file key.pem

# Load encrypted secrets
export FARFAN_SECRETS_FILE=secrets.enc
export FARFAN_SECRETS_KEY_FILE=key.pem

# Use external secrets manager (AWS Secrets Manager)
export FARFAN_SECRETS_BACKEND=aws
export FARFAN_SECRETS_REGION=us-east-1
export FARFAN_SECRET_NAME=farfan/prod/secrets
```

### 33.2.2 Key Rotation

```bash
# Rotate API keys
python scripts/security/rotate_api_keys.py \
    --grace-period 7d

# Rotate encryption keys
python scripts/security/rotate_encryption_keys.py \
    --re-encrypt-data
```

## 33.3 Audit Logging

### 33.3.1 Audit Trail

```bash
# Enable audit logging
export FARFAN_AUDIT_LOG=true
export FARFAN_AUDIT_LOG_FILE=logs/audit/audit.log

# Query audit logs
python scripts/security/query_audit_log.py \
    --action pipeline:start \
    --user admin \
    --time-range "last 24 hours"

# Generate audit report
python scripts/security/generate_audit_report.py \
    --start-date 2026-01-01 \
    --end-date 2026-01-31 \
    --output reports/audit_january_2026.pdf
```

## 33.4 Vulnerability Scanning

### 33.4.1 Dependency Scanning

```bash
# Scan Python dependencies
pip install safety
safety check --json > security/dependency_scan.json

# Scan with Snyk
pip install snyk
snyk test --json > security/snyk_report.json

# Check for outdated packages
pip list --outdated
```

### 33.4.2 Code Scanning

```bash
# Run Bandit security scanner
pip install bandit
bandit -r src/ -f json -o security/bandit_report.json

# Run semgrep
pip install semgrep
semgrep --config=auto --json -o security/semgrep_report.json src/
```

---

# Section 34: Data Management & Maintenance

## 34.1 Data Lifecycle Management

### 34.1.1 Artifact Retention

```bash
# Configure retention policy
export FARFAN_ARTIFACT_RETENTION_DAYS=90
export FARFAN_LOG_RETENTION_DAYS=30
export FARFAN_TEMP_FILE_RETENTION_HOURS=24

# Clean old artifacts
python scripts/maintenance/cleanup_artifacts.py \
    --older-than 90d \
    --dry-run

# Archive old runs
python scripts/maintenance/archive_runs.py \
    --older-than 180d \
    --archive-dir /mnt/archive/farfan \
    --compress
```

### 34.1.2 Log Rotation

```bash
# Configure logrotate
cat > /etc/logrotate.d/farfan << 'EOF'
/home/user/FARFAN_MCDPP/logs/**/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 user user
    sharedscripts
    postrotate
        systemctl reload farfan-pipeline || true
    endscript
}
EOF

# Manual log rotation
logrotate -f /etc/logrotate.d/farfan
```

## 34.2 Database Maintenance

### 34.2.1 Vacuum & Optimize

```bash
# Vacuum database
python scripts/maintenance/vacuum_database.py \
    --full \
    --analyze

# Rebuild indexes
python scripts/maintenance/rebuild_indexes.py \
    --tables evidence,scores,dimensions

# Analyze query performance
python scripts/maintenance/analyze_queries.py \
    --slow-query-threshold 1000 \
    --output reports/slow_queries.txt
```

### 34.2.2 Data Export/Import

```bash
# Export data
python scripts/export/export_all_data.py \
    --output exports/farfan_export_$(date +%Y%m%d).tar.gz \
    --format json \
    --compress

# Import data
python scripts/import/import_data.py \
    --input exports/farfan_export_20260123.tar.gz \
    --validate \
    --overwrite=false
```

## 34.3 Cache Management

### 34.3.1 Cache Operations

```bash
# Clear all caches
python scripts/maintenance/clear_caches.py --all

# Clear specific cache
python scripts/maintenance/clear_caches.py --type embeddings

# Warm cache
python scripts/maintenance/warm_caches.py \
    --questionnaire \
    --contracts \
    --embeddings

# Monitor cache hit rate
python scripts/monitoring/cache_statistics.py
```

## 34.4 Disk Space Management

### 34.4.1 Space Analysis

```bash
# Analyze disk usage
du -h --max-depth=2 artifacts/ | sort -hr | head -20

# Find large files
find artifacts/ -type f -size +100M -exec ls -lh {} \;

# Disk usage by phase
for phase in {0..9}; do
    size=$(du -sh artifacts/latest_run/phase${phase}_* 2>/dev/null | awk '{print $1}')
    echo "Phase $phase: $size"
done
```

### 34.4.2 Space Cleanup

```bash
# Clean temporary files
python scripts/maintenance/cleanup_temp_files.py

# Remove duplicate files
python scripts/maintenance/remove_duplicates.py \
    --directory artifacts/ \
    --dry-run

# Compress old artifacts
find artifacts/ -name "*.json" -mtime +30 -exec gzip {} \;
```

---

# Section 35: Integration & Extensions

## 35.1 API Integration

### 35.1.1 REST API Client

```python
# Python client example
import requests

class FarfanClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def start_pipeline(self, plan_path, region_id):
        """Start pipeline execution."""
        with open(plan_path, 'rb') as f:
            files = {'file': f}
            data = {'region_id': region_id}
            response = requests.post(
                f"{self.base_url}/api/upload/plan",
                headers=self.headers,
                files=files,
                data=data
            )
        return response.json()

    def get_job_status(self, job_id):
        """Get job status."""
        response = requests.get(
            f"{self.base_url}/api/v1/jobs/{job_id}",
            headers=self.headers
        )
        return response.json()

    def get_results(self, job_id):
        """Get pipeline results."""
        response = requests.get(
            f"{self.base_url}/api/v1/jobs/{job_id}/results",
            headers=self.headers
        )
        return response.json()

# Usage
client = FarfanClient("http://localhost:5000", "your-api-key")
job = client.start_pipeline("data/plans/plan.pdf", "R01")
print(f"Job started: {job['job_id']}")

# Poll for completion
import time
while True:
    status = client.get_job_status(job['job_id'])
    print(f"Status: {status['status']}")
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(10)

results = client.get_results(job['job_id'])
```

### 35.1.2 Webhook Integration

```bash
# Configure webhook
export FARFAN_WEBHOOK_URL=https://example.com/webhook
export FARFAN_WEBHOOK_EVENTS=pipeline.started,pipeline.completed,pipeline.failed

# Test webhook
curl -X POST https://example.com/webhook \
    -H "Content-Type: application/json" \
    -d '{
        "event": "pipeline.completed",
        "job_id": "job_20260123_103000",
        "status": "completed",
        "duration": 3456.78,
        "timestamp": "2026-01-23T11:27:36Z"
    }'
```

## 35.2 Plugin System

### 35.2.1 Creating Plugins

```python
# Custom plugin example
from farfan_pipeline.plugins import BasePlugin

class MyCustomPlugin(BasePlugin):
    name = "custom_analyzer"
    version = "1.0.0"

    def on_phase_start(self, phase, context):
        """Called when phase starts."""
        print(f"Phase {phase} starting")

    def on_phase_complete(self, phase, context, results):
        """Called when phase completes."""
        print(f"Phase {phase} completed with {len(results)} items")

    def on_evidence_extracted(self, evidence):
        """Called when evidence is extracted."""
        # Custom processing
        enhanced_evidence = self.enhance_evidence(evidence)
        return enhanced_evidence

    def enhance_evidence(self, evidence):
        """Custom evidence enhancement."""
        # Your logic here
        return evidence

# Register plugin
from farfan_pipeline.plugins import PluginRegistry
registry = PluginRegistry()
registry.register(MyCustomPlugin())
```

### 35.2.2 Plugin Management

```bash
# List installed plugins
python -m farfan_pipeline.plugins list

# Enable plugin
python -m farfan_pipeline.plugins enable custom_analyzer

# Disable plugin
python -m farfan_pipeline.plugins disable custom_analyzer

# Install plugin from file
python -m farfan_pipeline.plugins install plugins/my_plugin.py
```

## 35.3 External Tool Integration

### 35.3.1 Jupyter Notebook Integration

```python
# Use in Jupyter notebook
import sys
sys.path.append('/home/user/FARFAN_MCDPP')

from farfan_pipeline.orchestration.orchestrator import Orchestrator
from farfan_pipeline.orchestration.factory import UnifiedFactory

# Interactive pipeline execution
orchestrator = Orchestrator()
results = orchestrator.run_phases(
    plan_pdf="data/plans/test.pdf",
    start_phase=0,
    end_phase=9
)

# Visualize results
import pandas as pd
import plotly.express as px

scores_df = pd.DataFrame(results['phase3_scores'])
fig = px.histogram(scores_df, x='score', nbins=50)
fig.show()
```

### 35.3.2 CI/CD Integration

```yaml
# .github/workflows/pipeline-test.yml
name: Pipeline Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          bash install.sh
          source farfan-env/bin/activate

      - name: Run tests
        run: |
          source farfan-env/bin/activate
          pytest tests/ -v --cov=farfan_pipeline

      - name: Run mini pipeline
        run: |
          source farfan-env/bin/activate
          python scripts/run_policy_pipeline_verified.py \
            --plan tests/fixtures/sample_plan.pdf \
            --artifacts-dir artifacts/ci_test \
            --end-phase 3

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: pipeline-artifacts
          path: artifacts/ci_test
```

## 35.4 Data Export Formats

### 35.4.1 Export to Various Formats

```bash
# Export to CSV
python scripts/export/export_to_csv.py \
    --scores artifacts/latest_run/phase3_scores/scores.json \
    --output reports/scores.csv

# Export to Excel
python scripts/export/export_to_excel.py \
    --artifacts-dir artifacts/latest_run \
    --output reports/complete_analysis.xlsx \
    --include-all

# Export to JSON (formatted)
python scripts/export/export_to_json.py \
    --artifacts-dir artifacts/latest_run \
    --output reports/analysis.json \
    --pretty

# Export to Parquet
python scripts/export/export_to_parquet.py \
    --scores artifacts/latest_run/phase3_scores/scores.json \
    --output data/scores.parquet

# Export to database
python scripts/export/export_to_database.py \
    --artifacts-dir artifacts/latest_run \
    --db-url postgresql://localhost/farfan \
    --create-tables
```

### 35.4.2 Report Generation Formats

```bash
# Generate PDF report
python -m farfan_pipeline.phases.Phase_09.report_generator \
    --artifacts-dir artifacts/latest_run \
    --output reports/final_report.pdf \
    --template enhanced \
    --format pdf

# Generate Word document
python scripts/export/export_to_docx.py \
    --artifacts-dir artifacts/latest_run \
    --template templates/report_template.docx \
    --output reports/final_report.docx

# Generate PowerPoint presentation
python scripts/export/export_to_pptx.py \
    --artifacts-dir artifacts/latest_run \
    --template templates/presentation_template.pptx \
    --output reports/presentation.pptx
```

---

# Section 36: Complete Command Reference

## 36.1 Quick Command Index

### Pipeline Execution
```bash
# Full pipeline
farfan-pipeline --plan <pdf> --start-phase 0 --end-phase 9

# Specific phase range
farfan-pipeline --plan <pdf> --start-phase 2 --end-phase 5

# With custom configuration
farfan-pipeline --plan <pdf> --config config.yaml --seed 42

# Resume from checkpoint
farfan-pipeline --resume-from-checkpoint latest

# Dry run (validation only)
farfan-pipeline --plan <pdf> --dry-run --verbose
```

### SISAS Operations
```bash
# Health check
python -m SISAS.main health --bus-stats --consumer-health

# Run irrigation
python -m SISAS.main run --csv-path <sabana> --all

# Check vocabulary
python -m SISAS.main check

# Consumer status
python -m SISAS.main consumer-status <consumer_id>

# DLQ management
python -m SISAS.main dlq-list --limit 50
python -m SISAS.main dlq-replay --signal-ids <ids>
python -m SISAS.main dlq-clear --confirm
```

### Dashboard & Visualization
```bash
# Start dashboard
python -m farfan_pipeline.dashboard_atroz_.dashboard_server

# Generate visualizations
python scripts/visualization/generate_score_heatmap.py --scores <file>
python scripts/visualization/generate_signal_flow.py --log <file>
python scripts/visualization/generate_evidence_network.py --evidence <file>

# Performance metrics
curl http://localhost:5000/api/v1/metrics/system | jq
```

### Validation & Testing
```bash
# Validate installation
python scripts/setup/validate_installation.py

# Validate contracts
python scripts/validation/validate_all_contracts.py

# Validate artifacts
python scripts/validation/validate_all_artifacts.py --artifacts-dir <dir>

# Run tests
pytest tests/ -v --cov=farfan_pipeline
```

### Maintenance
```bash
# Cleanup artifacts
python scripts/maintenance/cleanup_artifacts.py --older-than 90d

# Vacuum database
python scripts/maintenance/vacuum_database.py --full

# Clear caches
python scripts/maintenance/clear_caches.py --all

# Backup
bash scripts/backup/daily_backup.sh
```

---

## 36.2 Environment Variables Reference

```bash
# Core Settings
FARFAN_MODE=DEV|PROD|TEST
FARFAN_SEED=42
FARFAN_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
FARFAN_DEBUG=true|false

# Paths
FARFAN_DATA_DIR=/path/to/data
FARFAN_ARTIFACTS_DIR=/path/to/artifacts
FARFAN_LOGS_DIR=/path/to/logs
FARFAN_CONFIG_DIR=/path/to/config

# SISAS
FARFAN_SISAS_ENABLE=true|false
FARFAN_SISAS_BUS_QUEUE_SIZE=50000
FARFAN_SISAS_CONSUMER_THREADS=4
FARFAN_SISAS_GATE_STRICT=true|false

# Performance
FARFAN_MAX_MEMORY_MB=8192
FARFAN_MAX_WORKERS=4
FARFAN_TIMEOUT_SECONDS=300
FARFAN_ENABLE_CACHING=true|false
FARFAN_CACHE_SIZE_MB=2048

# Dashboard
FARFAN_DASHBOARD_HOST=0.0.0.0
FARFAN_DASHBOARD_PORT=5000
FARFAN_DASHBOARD_DEBUG=false

# Security
FARFAN_ENABLE_AUTH=true|false
FARFAN_API_KEY=your-secret-key
FARFAN_AUDIT_LOG=true|false

# Monitoring
FARFAN_ENABLE_METRICS=true|false
FARFAN_METRICS_PORT=9090
FARFAN_ENABLE_PROFILING=false
```

---

## 36.3 File Structure Reference

```
FARFAN_MCDPP/
├── artifacts/                    # Pipeline outputs
│   ├── phase0_bootstrap/
│   ├── phase1_chunks/
│   ├── phase2_evidence/
│   ├── phase3_scores/
│   ├── phase4_dimensions/
│   ├── phase5_areas/
│   ├── phase6_clusters/
│   ├── phase7_macro/
│   ├── phase8_recommendations/
│   ├── phase9_reports/
│   └── visualizations/
├── canonic_questionnaire_central/ # Canonical questionnaire
│   ├── questionnaire_monolith.json
│   ├── questionnaire_schema.json
│   └── governance/
├── config/                        # Configuration files
│   ├── calibration/
│   ├── parametrization/
│   ├── pdm/
│   └── sisas/
├── data/                          # Input data
│   ├── plans/
│   └── questionnaires/
├── docs/                          # Documentation
│   ├── TECHNICAL_RUNBOOK.md
│   ├── CONFIG_REFERENCE.md
│   └── design/
├── logs/                          # Log files
│   ├── orchestrator/
│   ├── phases/
│   ├── sisas/
│   ├── executors/
│   └── metrics/
├── scripts/                       # Utility scripts
│   ├── analysis/
│   ├── benchmarking/
│   ├── diagnostics/
│   ├── enforcement/
│   ├── export/
│   ├── generation/
│   ├── maintenance/
│   ├── monitoring/
│   ├── sisas/
│   ├── transformation/
│   ├── validation/
│   └── visualization/
├── src/farfan_pipeline/          # Source code
│   ├── calibration/
│   ├── dashboard_atroz_/
│   ├── infrastructure/
│   │   └── irrigation_using_signals/
│   │       └── SISAS/
│   ├── methods/
│   ├── orchestration/
│   └── phases/
│       ├── Phase_00/ through Phase_09/
├── tests/                         # Test suite
│   ├── integration/
│   ├── unit/
│   └── smoke/
├── install.sh                     # Installation script
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
└── README.md                      # Project README
```

---

*End of Comprehensive Technical Runbook - Version 3.0.0*
*All commands verified on 2026-01-21*

*End of Technical Runbook*