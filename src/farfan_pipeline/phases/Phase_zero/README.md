# Phase 0: Validation, Hardening & Bootstrap

**Document ID:** PHASE-0-README  
**Version:** 1.0.0  
**Date:** 2025-12-29  
**Status:** ACTIVE  
**Authors:** F.A.R.F.A.N Core Architecture Team  
**Classification:** Technical Specification - Internal

---

## Abstract

Phase 0 constitutes the foundational layer of the F.A.R.F.A.N (Framework for Automated Reasoning on Fiscal, Administrative, and Regulatory Frameworks for Analytical Normalization) deterministic policy analysis pipeline. This phase implements a rigorous pre-execution validation, hardening, and bootstrap protocol that guarantees system integrity, reproducibility, and resource safety before any analytical computation commences. The architecture comprises 21 Python modules organized into 7 canonical stages (00-90), each implementing specific validation, enforcement, or orchestration responsibilities. Phase 0 enforces kernel-level resource limits via `setrlimit()`, guarantees bitwise-identical reproducibility through deterministic seed management, validates all input contracts and schemas, and orchestrates the complete wiring initialization sequence. This document specifies the complete technical architecture, execution semantics, module inventory, and formal verification properties required for production deployment of the F.A.R.F.A.N pipeline.

**Keywords:** deterministic execution, resource enforcement, validation pipeline, bootstrap orchestration, reproducibility guarantees, kernel-level limits

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Phase Overview](#11-phase-overview)
   - 1.2 [Motivation and Rationale](#12-motivation-and-rationale)
   - 1.3 [Scope and Boundaries](#13-scope-and-boundaries)
   - 1.4 [Design Principles](#14-design-principles)
2. [Architecture](#2-architecture)
   - 2.1 [Stage Taxonomy](#21-stage-taxonomy)
   - 2.2 [Module Classification](#22-module-classification)
   - 2.3 [Execution Flow](#23-execution-flow)
   - 2.4 [Dependency Graph](#24-dependency-graph)
3. [Module Inventory](#3-module-inventory)
   - 3.1 [Stage 00: Infrastructure](#31-stage-00-infrastructure)
   - 3.2 [Stage 10: Environment Configuration](#32-stage-10-environment-configuration)
   - 3.3 [Stage 20: Determinism Enforcement](#33-stage-20-determinism-enforcement)
   - 3.4 [Stage 30: Resource Control](#34-stage-30-resource-control)
   - 3.5 [Stage 40: Validation](#35-stage-40-validation)
   - 3.6 [Stage 50: Boot Sequence](#36-stage-50-boot-sequence)
   - 3.7 [Stage 90: Integration](#37-stage-90-integration)
4. [Execution Narrative](#4-execution-narrative)
   - 4.1 [Boot Sequence Timeline](#41-boot-sequence-timeline)
   - 4.2 [Detailed Phase Progression](#42-detailed-phase-progression)
   - 4.3 [Critical Path Analysis](#43-critical-path-analysis)
5. [Contracts and Guarantees](#5-contracts-and-guarantees)
   - 5.1 [Input Contracts](#51-input-contracts)
   - 5.2 [Output Contracts](#52-output-contracts)
   - 5.3 [Invariants](#53-invariants)
   - 5.4 [Failure Modes](#54-failure-modes)
6. [Resource Management](#6-resource-management)
   - 6.1 [Kernel-Level Enforcement](#61-kernel-level-enforcement)
   - 6.2 [Memory Watchdog](#62-memory-watchdog)
   - 6.3 [Pre-flight Checks](#63-pre-flight-checks)
7. [Determinism Guarantees](#7-determinism-guarantees)
   - 7.1 [Seed Management Strategy](#71-seed-management-strategy)
   - 7.2 [Hash Computation](#72-hash-computation)
   - 7.3 [Reproducibility Verification](#73-reproducibility-verification)
8. [Configuration Reference](#8-configuration-reference)
   - 8.1 [Environment Variables](#81-environment-variables)
   - 8.2 [Runtime Configuration](#82-runtime-configuration)
   - 8.3 [Resource Limits](#83-resource-limits)
9. [Testing and Verification](#9-testing-and-verification)
   - 9.1 [Unit Tests](#91-unit-tests)
   - 9.2 [Integration Tests](#92-integration-tests)
   - 9.3 [Verification Checklist](#93-verification-checklist)
10. [Maintenance and Evolution](#10-maintenance-and-evolution)
    - 10.1 [Known Limitations](#101-known-limitations)
    - 10.2 [Future Enhancements](#102-future-enhancements)
    - 10.3 [Migration Notes](#103-migration-notes)
11. [References](#11-references)
12. [Appendices](#12-appendices)
    - A. [Glossary](#appendix-a-glossary)
    - B. [File Manifest](#appendix-b-file-manifest)
    - C. [Error Code Reference](#appendix-c-error-code-reference)

---

## 1. Introduction

### 1.1 Phase Overview

Phase 0 is the **pre-analytical foundation layer** of the F.A.R.F.A.N pipeline that executes before any policy analysis computation begins. Unlike subsequent phases (1-9) which perform analytical transformations on policy documents, Phase 0 is concerned exclusively with establishing the preconditions necessary for safe, reproducible, and validated execution.

The phase implements five core capabilities:

1. **Environment Validation**: Verification of paths, configurations, and system prerequisites
2. **Determinism Enforcement**: Seed management and hash computation for reproducibility
3. **Resource Control**: Kernel-level limits preventing OOM kills and runaway processes
4. **Input Validation**: Schema verification, signature checking, and coverage gates
5. **Bootstrap Orchestration**: Wiring initialization and component assembly

Phase 0 produces no analytical outputs—its sole product is a **validated, hardened execution environment** ready to receive policy documents for processing.

### 1.2 Motivation and Rationale

The design of Phase 0 is motivated by three critical requirements of production policy analysis systems:

**R1: Reproducibility Guarantee**

Policy analysis results must be bitwise-identical across executions given identical inputs. This requirement stems from:
- Regulatory compliance mandating audit trails
- Scientific methodology requiring reproducible experiments
- Legal defensibility of automated policy assessments

Phase 0 addresses this through deterministic seed management, controlled random state initialization, and hash-based verification of all intermediate artifacts.

**R2: Resource Safety**

Policy documents can vary dramatically in size and complexity (10KB to 100MB+). Without enforcement, memory-intensive operations can cause:
- OOM kills terminating analysis mid-execution
- Runaway CPU consumption blocking other processes
- Disk exhaustion corrupting artifacts

Phase 0 implements kernel-level resource limits via `resource.setrlimit()` that **cannot be bypassed** by Python code, providing a hard ceiling on resource consumption.

**R3: Configuration Integrity**

The F.A.R.F.A.N pipeline involves >300 executor contracts, 240+ analytical methods, and complex wiring between components. Misconfigurations can cause:
- Silent incorrect results (most dangerous)
- Cascading failures in downstream phases
- Non-deterministic behavior from uninitialized state

Phase 0 validates all configurations, contracts, and wiring before any execution begins, failing fast with explicit error messages.

### 1.3 Scope and Boundaries

**In Scope:**
- ✅ Path resolution and validation
- ✅ Runtime configuration parsing and validation
- ✅ Deterministic seed management
- ✅ Hash computation for artifact integrity
- ✅ Resource limit enforcement (memory, CPU, disk, file descriptors)
- ✅ Input document validation
- ✅ Schema monitoring and verification
- ✅ Signature validation for method bindings
- ✅ Coverage gate verification
- ✅ Boot checks and exit gates
- ✅ Wiring initialization and bootstrap

**Out of Scope:**
- ❌ Document ingestion (Phase 1)
- ❌ Executor orchestration (Phase 2)
- ❌ Semantic analysis (Phase 3)
- ❌ Score aggregation (Phases 4-7)
- ❌ Recommendations (Phase 8)
- ❌ Report generation (Phase 9)

### 1.4 Design Principles

Phase 0 adheres to the following architectural principles:

**P1: Fail-Fast**
Any validation failure terminates execution immediately with explicit error context. No partial initialization states are permitted.

**P2: Defense in Depth**
Multiple validation layers ensure that errors are caught at the earliest possible point. Schema validation precedes signature validation precedes coverage verification.

**P3: Observability**
All Phase 0 operations produce structured logs with correlation IDs enabling post-mortem analysis of initialization sequences.

**P4: Immutability**
Once Phase 0 completes, the execution environment is frozen. No further configuration changes are permitted during analytical phases.

**P5: Kernel Trust**
For critical enforcement (resource limits), Phase 0 delegates to kernel primitives that cannot be circumvented by application code.

---

## 2. Architecture

### 2.1 Stage Taxonomy

Phase 0 organizes its 21 modules into 7 canonical stages following the F.A.R.F.A.N naming convention:

```
phase0_{STAGE}_{ORDER}_{name}.py
```

| Stage | Code | Name | Description | Module Count |
|-------|------|------|-------------|--------------|
| 00 | INFRASTRUCTURE | Infrastructure | Base errors, types, initialization | 3 |
| 10 | ENVIRONMENT | Environment Configuration | Paths, config, logging | 3 |
| 20 | DETERMINISM | Determinism Enforcement | Seeds, hashing, reproducibility | 5 |
| 30 | RESOURCES | Resource Control | Limits, watchdog, enforcement | 1 |
| 40 | VALIDATION | Validation | Input, schema, signature, coverage | 4 |
| 50 | BOOT | Boot Sequence | Checks, gates, wiring verification | 2 |
| 90 | INTEGRATION | Integration | Main entry, runner, bootstrap | 3 |

**Total: 21 modules**

### 2.2 Module Classification

Modules are classified by type and criticality:

**By Type:**

| Type | Code | Description | Modules |
|------|------|-------------|---------|
| Infrastructure | INFRA | Base types and errors | 3 |
| Configuration | CFG | Environment and paths | 3 |
| Enforcer | ENF | Active enforcement mechanisms | 5 |
| Validator | VAL | Passive validation checks | 4 |
| Utility | UTIL | Helper functions | 2 |
| Orchestrator | ORCH | Coordination and sequencing | 3 |
| Entry | ENTRY | Main entry points | 1 |

**By Criticality:**

| Level | Description | Modules |
|-------|-------------|---------|
| CRITICAL | Failure prevents all execution | 11 |
| HIGH | Failure degrades functionality | 7 |
| MEDIUM | Failure affects quality metrics | 2 |
| LOW | Failure has minimal impact | 1 |

### 2.3 Execution Flow

Phase 0 execution follows a strict sequential order:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 0 EXECUTION FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │   STAGE 00   │  Infrastructure: Load error classes, base types
     │ INFRASTRUCTURE│
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │   STAGE 10   │  Environment: Resolve paths, parse config, init logger
     │ ENVIRONMENT  │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │   STAGE 20   │  Determinism: Initialize seeds, setup hash functions
     │ DETERMINISM  │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │   STAGE 30   │  Resources: Set kernel limits, start watchdog
     │  RESOURCES   │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │   STAGE 40   │  Validation: Validate inputs, schemas, signatures
     │  VALIDATION  │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │   STAGE 50   │  Boot: Run boot checks, verify exit gates
     │    BOOT      │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │   STAGE 90   │  Integration: Bootstrap wiring, initialize components
     │ INTEGRATION  │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │   PHASE 1    │  → Hand off to document ingestion
     │   READY      │
     └──────────────┘
```

### 2.4 Dependency Graph

```
                                    ┌─────────────────┐
                                    │ phase0_00_00    │
                                    │ __init__        │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
           ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
           │ phase0_00_01    │    │ phase0_10_00    │    │ phase0_10_01    │
           │ domain_errors   │    │ paths           │    │ runtime_config  │
           └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
                    │                      │                      │
                    │             ┌────────┴────────┐             │
                    │             │                 │             │
                    ▼             ▼                 ▼             ▼
           ┌─────────────────────────────────────────────────────────────┐
           │                     phase0_10_02 json_logger                 │
           └─────────────────────────────────────────────────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
           ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
           │ phase0_20_00    │    │ phase0_20_01    │    │ phase0_20_02    │
           │ seed_factory    │    │ hash_utils      │    │ determinism     │
           └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
                    │                      │                      │
                    └──────────────────────┼──────────────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │ phase0_20_03            │
                              │ determinism_helpers     │
                              └───────────┬─────────────┘
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │ phase0_20_04            │
                              │ deterministic_execution │
                              └───────────┬─────────────┘
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │ phase0_30_00            │
                              │ resource_controller     │
                              └───────────┬─────────────┘
                                          │
           ┌──────────────────────────────┼──────────────────────────────┐
           │                              │                              │
           ▼                              ▼                              ▼
  ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
  │ phase0_40_00    │          │ phase0_40_01    │          │ phase0_40_02    │
  │ input_validation│          │ schema_monitor  │          │ signature_valid │
  └────────┬────────┘          └────────┬────────┘          └────────┬────────┘
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────────────┐
                              │ phase0_40_03            │
                              │ coverage_gate           │
                              └───────────┬─────────────┘
                                          │
                         ┌────────────────┴────────────────┐
                         │                                 │
                         ▼                                 ▼
              ┌─────────────────────┐         ┌─────────────────────┐
              │ phase0_50_00        │         │ phase0_50_01        │
              │ boot_checks         │         │ exit_gates          │
              └──────────┬──────────┘         └──────────┬──────────┘
                         │                               │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                              ┌─────────────────────────┐
                              │ phase0_90_00            │
                              │ main                    │
                              └───────────┬─────────────┘
                                          │
                         ┌────────────────┴────────────────┐
                         │                                 │
                         ▼                                 ▼
              ┌─────────────────────┐         ┌─────────────────────┐
              │ phase0_90_01        │         │ phase0_90_02        │
              │ verified_runner     │         │ bootstrap           │
              └─────────────────────┘         └─────────────────────┘
```

---

## 3. Module Inventory

### 3.1 Stage 00: Infrastructure

**Purpose:** Establish base types, error classes, and package initialization required by all subsequent modules.

#### 3.1.1 phase0_00_00_init.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `__init__.py` |
| **Type** | INFRA |
| **Criticality** | LOW |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~40 |

**Responsibility:** Package initialization and public API exports for the Phase_zero module. Exposes `ResourceController`, `ResourceLimits`, `ResourceExhausted`, and other core classes.

**Key Exports:**
```python
__all__ = [
    "ResourceController",
    "ResourceLimits",
    "ResourceExhausted",
    "MemoryWatchdog",
    "EnforcementMetrics",
    "PSUTIL_AVAILABLE",
]
```

#### 3.1.2 phase0_00_01_domain_errors.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `domain_errors.py` |
| **Type** | INFRA |
| **Criticality** | HIGH |
| **Execution Pattern** | On-Demand |
| **Lines of Code** | ~137 |

**Responsibility:** Define domain-specific exception hierarchy for contract violations. Provides `ContractViolationError`, `DataContractError`, and `SystemContractError`.

**Exception Hierarchy:**
```
ContractViolationError (base)
├── DataContractError (data/payload violations)
└── SystemContractError (system/configuration violations)
```

#### 3.1.3 phase0_00_02_runtime_error_fixes.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `runtime_error_fixes.py` |
| **Type** | INFRA |
| **Criticality** | MEDIUM |
| **Execution Pattern** | On-Demand |
| **Lines of Code** | ~135 |

**Responsibility:** Utility functions for runtime error handling and type coercion. Provides `ensure_list_return()` and similar defensive programming helpers.

---

### 3.2 Stage 10: Environment Configuration

**Purpose:** Establish the execution environment including path resolution, runtime configuration, and structured logging.

#### 3.2.1 phase0_10_00_paths.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `paths.py` |
| **Type** | CFG |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Singleton |
| **Lines of Code** | ~480 |

**Responsibility:** Central path resolution for all F.A.R.F.A.N directories. Defines `PROJECT_ROOT`, `DATA_DIR`, `CONFIG_DIR`, `OUTPUT_DIR`, `CACHE_DIR`, and validates their existence.

**Key Constants:**
```python
PROJECT_ROOT: Path  # Auto-detected from file location
DATA_DIR: Path      # {PROJECT_ROOT}/data
CONFIG_DIR: Path    # {PROJECT_ROOT}/config
OUTPUT_DIR: Path    # {PROJECT_ROOT}/output
CACHE_DIR: Path     # {PROJECT_ROOT}/.cache
```

**Error Classes:**
- `PathError` - Base exception for path-related errors
- `PathNotFoundError` - Required path does not exist
- `PathPermissionError` - Insufficient permissions

#### 3.2.2 phase0_10_01_runtime_config.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `runtime_config.py` |
| **Type** | CFG |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Singleton |
| **Lines of Code** | ~584 |

**Responsibility:** Parse and validate runtime configuration from environment variables. Implements `RuntimeConfig` dataclass with strict validation and illegal combination detection.

**Runtime Modes:**
- `PROD` - Production: strict enforcement, no fallbacks
- `DEV` - Development: permissive with flags
- `EXPLORATORY` - Research: maximum flexibility

**Fallback Categories:**
- **Category A (CRITICAL):** System integrity - no fallbacks in PROD
- **Category B (QUALITY):** Quality degradation - allowed with warnings
- **Category C (DEVELOPMENT):** Development convenience - forbidden in PROD
- **Category D (OPERATIONAL):** Safe operational fallbacks

#### 3.2.3 phase0_10_02_json_logger.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `json_logger.py` |
| **Type** | CFG |
| **Criticality** | HIGH |
| **Execution Pattern** | Singleton |
| **Lines of Code** | ~259 |

**Responsibility:** Initialize structured JSON logging with correlation IDs, timestamps, and contextual metadata. Integrates with `structlog` for machine-parseable log output.

---

### 3.3 Stage 20: Determinism Enforcement

**Purpose:** Guarantee bitwise-identical reproducibility through seed management, controlled randomness, and hash verification.

#### 3.3.1 phase0_20_00_seed_factory.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `seed_factory.py` |
| **Type** | ENF |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Singleton |
| **Lines of Code** | ~198 |

**Responsibility:** Centralized seed management for all random operations. Implements `SeedFactory` class providing deterministic seed derivation for different pipeline components.

**Seed Derivation:**
```python
base_seed = 42  # Global constant
phase_seed = hash(f"{base_seed}:phase:{phase_number}")
executor_seed = hash(f"{phase_seed}:executor:{executor_id}")
```

#### 3.3.2 phase0_20_01_hash_utils.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `hash_utils.py` |
| **Type** | UTIL |
| **Criticality** | HIGH |
| **Execution Pattern** | On-Demand |
| **Lines of Code** | ~41 |

**Responsibility:** Hash computation utilities using BLAKE3 for artifact integrity verification. Provides `compute_hash()` for dictionaries and binary data.

#### 3.3.3 phase0_20_02_determinism.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `determinism.py` |
| **Type** | ENF |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~359 |

**Responsibility:** Core determinism enforcement including Python hash seed configuration, NumPy random state initialization, and environment variable enforcement.

**Enforcement Actions:**
1. Set `PYTHONHASHSEED` environment variable
2. Initialize `numpy.random` with fixed seed
3. Configure `random` module state
4. Disable non-deterministic operations

#### 3.3.4 phase0_20_03_determinism_helpers.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `determinism_helpers.py` |
| **Type** | UTIL |
| **Criticality** | HIGH |
| **Execution Pattern** | On-Demand |
| **Lines of Code** | ~192 |

**Responsibility:** Helper functions for deterministic operations including sorted dictionary iteration, stable JSON serialization, and order-independent collection handling.

#### 3.3.5 phase0_20_04_deterministic_execution.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `deterministic_execution.py` |
| **Type** | ENF |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~445 |

**Responsibility:** High-level deterministic execution context manager. Wraps entire pipeline execution in determinism guarantees with verification hooks.

---

### 3.4 Stage 30: Resource Control

**Purpose:** Enforce hard resource limits at the kernel level to prevent OOM kills and runaway processes.

#### 3.4.1 phase0_30_00_resource_controller.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `resource_controller.py` |
| **Type** | ENF |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Singleton |
| **Lines of Code** | ~503 |

**Responsibility:** Kernel-level resource enforcement using `resource.setrlimit()`. Implements `ResourceController` with context manager pattern, pre-flight checks, and memory watchdog.

**Key Components:**
- `ResourceLimits` - Immutable limits specification
- `ResourceController` - Main enforcement engine
- `MemoryWatchdog` - Background monitoring thread
- `EnforcementMetrics` - Execution metrics collection

**Kernel Limits Enforced:**
| Limit | Default | Kernel Constant |
|-------|---------|-----------------|
| Address Space | 2048 MB | `RLIMIT_AS` |
| CPU Time | 300 s | `RLIMIT_CPU` |
| File Descriptors | 1024 | `RLIMIT_NOFILE` |

---

### 3.5 Stage 40: Validation

**Purpose:** Validate all inputs, schemas, signatures, and coverage requirements before execution begins.

#### 3.5.1 phase0_40_00_input_validation.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `phase0_input_validation.py` |
| **Type** | VAL |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~540 |

**Responsibility:** Validate input documents, questionnaire monolith, and configuration files. Ensures all required fields are present and values are within acceptable ranges.

#### 3.5.2 phase0_40_01_schema_monitor.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `schema_monitor.py` |
| **Type** | VAL |
| **Criticality** | HIGH |
| **Execution Pattern** | Continuous |
| **Lines of Code** | ~396 |

**Responsibility:** Monitor schema shape evolution and detect drift. Tracks field additions, removals, and type changes across pipeline versions.

#### 3.5.3 phase0_40_02_signature_validator.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `signature_validator.py` |
| **Type** | VAL |
| **Criticality** | HIGH |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~474 |

**Responsibility:** Validate method signatures against contract specifications. Ensures method bindings in executor contracts match actual method implementations.

#### 3.5.4 phase0_40_03_coverage_gate.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `coverage_gate.py` |
| **Type** | VAL |
| **Criticality** | MEDIUM |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~252 |

**Responsibility:** Verify test coverage meets minimum thresholds. Gates pipeline execution if coverage falls below required percentage.

---

### 3.6 Stage 50: Boot Sequence

**Purpose:** Execute pre-flight checks and verify exit conditions before handing off to Phase 1.

#### 3.6.1 phase0_50_00_boot_checks.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `boot_checks.py` |
| **Type** | ORCH |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~289 |

**Responsibility:** Execute comprehensive boot-time checks including dependency verification, configuration validation, and resource availability. Raises `BootCheckError` on failure.

**Check Categories:**
1. **Environment Checks** - Python version, required packages
2. **Configuration Checks** - Valid settings, no conflicts
3. **Resource Checks** - Memory, disk, file handles available
4. **Dependency Checks** - All required modules importable

#### 3.6.2 phase0_50_01_exit_gates.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `exit_gates.py` |
| **Type** | ORCH |
| **Criticality** | HIGH |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~668 |

**Responsibility:** Define and verify exit conditions that must be satisfied before proceeding to Phase 1. Implements gate pattern with pass/fail semantics.

**Exit Gates:**
1. `ConfigurationGate` - All configurations valid
2. `DeterminismGate` - Reproducibility verified
3. `ResourceGate` - Resource limits active
4. `ValidationGate` - All inputs validated
5. `WiringGate` - Component wiring complete

---

### 3.7 Stage 90: Integration

**Purpose:** Orchestrate the complete Phase 0 execution and hand off to Phase 1.

#### 3.7.1 phase0_90_00_main.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `main.py` |
| **Type** | ENTRY |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~1829 |

**Responsibility:** Main entry point for Phase 0 execution. Coordinates all stages in sequence and produces the initialized pipeline context.

#### 3.7.2 phase0_90_01_verified_pipeline_runner.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `verified_pipeline_runner.py` |
| **Type** | ORCH |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~516 |

**Responsibility:** Verified execution wrapper that runs the pipeline with all Phase 0 guarantees active. Collects metrics and produces execution report.

#### 3.7.3 phase0_90_02_bootstrap.py

| Attribute | Value |
|-----------|-------|
| **Legacy Name** | `bootstrap.py` |
| **Type** | ORCH |
| **Criticality** | CRITICAL |
| **Execution Pattern** | Boot-Once |
| **Lines of Code** | ~1163 |

**Responsibility:** Complete wiring initialization including:
1. `QuestionnaireResourceProvider` - Load questionnaire monolith
2. `SignalClient`/`SignalRegistry` - Initialize signal system
3. `CoreModuleFactory` - Create factory with DI
4. `ExtendedArgRouter` - Initialize routing (≥30 routes)
5. `WiringComponents` - Assemble all components

**Key Classes:**
- `WiringBootstrap` - Main bootstrap engine
- `EnforcedBootstrap` - Bootstrap with resource enforcement
- `WiringComponents` - Container for all wired components

---

## 4. Execution Narrative

### 4.1 Boot Sequence Timeline

The Phase 0 execution follows a strict temporal sequence. The following timeline illustrates the progression from process start to Phase 1 handoff:

```
TIME    STAGE   ACTION
─────────────────────────────────────────────────────────────────────────
t=0     00      Python interpreter loads Phase_zero package
                ├── Import __init__.py
                ├── Load error classes from domain_errors.py
                └── Load runtime fixes from runtime_error_fixes.py

t=1     10      Environment configuration begins
                ├── Resolve PROJECT_ROOT and derived paths
                ├── Parse environment variables into RuntimeConfig
                ├── Validate configuration (detect illegal combos)
                └── Initialize structured JSON logger

t=2     20      Determinism enforcement activates
                ├── Create SeedFactory with base seed
                ├── Configure PYTHONHASHSEED
                ├── Initialize numpy/random states
                ├── Load hash utilities (BLAKE3)
                └── Activate deterministic execution context

t=3     30      Resource control engages
                ├── Execute pre-flight checks (memory, disk)
                ├── Set RLIMIT_AS (address space limit)
                ├── Set RLIMIT_CPU (CPU time limit)
                ├── Set RLIMIT_NOFILE (file descriptor limit)
                └── Start MemoryWatchdog background thread

t=4     40      Validation phase executes
                ├── Validate input documents
                ├── Verify schema conformance
                ├── Check method signature bindings
                └── Verify coverage requirements

t=5     50      Boot sequence finalizes
                ├── Execute all boot checks
                ├── Verify all exit gates pass
                └── Prepare handoff context

t=6     90      Integration completes
                ├── Load QuestionnaireResourceProvider
                ├── Initialize SignalClient (memory://)
                ├── Build CoreModuleFactory
                ├── Create ExtendedArgRouter
                ├── Assemble WiringComponents
                └── Produce Phase 1 context

t=7     →P1     HANDOFF: Phase 0 complete, Phase 1 begins
─────────────────────────────────────────────────────────────────────────
```

### 4.2 Detailed Phase Progression

#### Stage 00 → Stage 10 Transition

When the Python interpreter loads the `Phase_zero` package, it first executes `__init__.py` which imports the core infrastructure modules. The `domain_errors.py` module defines the exception hierarchy that will be used throughout the pipeline for contract violations. The `runtime_error_fixes.py` module provides defensive utilities that prevent common runtime errors.

Once infrastructure is loaded, Stage 10 begins with path resolution. The `paths.py` module auto-detects `PROJECT_ROOT` by walking up from its file location until it finds the project marker (e.g., `pyproject.toml`). All derived paths (`DATA_DIR`, `CONFIG_DIR`, etc.) are computed relative to this root and validated for existence.

With paths established, `runtime_config.py` parses all `SAAAAAA_*` and `ALLOW_*` environment variables into an immutable `RuntimeConfig` dataclass. This configuration is validated for illegal combinations—for example, `PROD` mode with `ALLOW_DEV_INGESTION_FALLBACKS=true` raises `ConfigurationError`.

Finally, `json_logger.py` initializes the structured logging system with the configuration from `RuntimeConfig`. All subsequent log entries include correlation IDs, timestamps, and contextual metadata.

#### Stage 10 → Stage 20 Transition

With the environment configured and logging active, Stage 20 begins determinism enforcement. The `seed_factory.py` module creates a `SeedFactory` instance initialized with the base seed (default: 42). This factory provides deterministic seed derivation for any component that requires randomness.

The `determinism.py` module then enforces global determinism by:
1. Setting `PYTHONHASHSEED` in the environment
2. Initializing `numpy.random.seed()`
3. Initializing `random.seed()`
4. Configuring any other random sources

The `hash_utils.py` module loads the BLAKE3 hash function for computing artifact digests. The `determinism_helpers.py` module provides utilities for deterministic iteration and serialization.

Finally, `deterministic_execution.py` creates a context manager that wraps the entire pipeline execution. This context verifies determinism invariants and can detect violations during execution.

#### Stage 20 → Stage 30 Transition

With determinism established, Stage 30 activates resource control. The `resource_controller.py` module creates a `ResourceController` instance with the configured limits.

Before setting kernel limits, pre-flight checks verify:
- Available memory exceeds 50% of the limit
- Available disk space exceeds the minimum
- Current file descriptor count is within bounds

If pre-flight checks pass, kernel limits are set via `resource.setrlimit()`. These limits cannot be bypassed by Python code—the kernel will SIGKILL the process if limits are exceeded.

A `MemoryWatchdog` thread starts in the background, monitoring memory pressure every second and logging warnings when usage exceeds 90%.

#### Stage 30 → Stage 40 Transition

With resources controlled, Stage 40 performs comprehensive validation. The `phase0_input_validation.py` module validates all input documents:
- File existence and readability
- Required fields present
- Field values within acceptable ranges
- Cross-field consistency

The `schema_monitor.py` module verifies that input schemas match expected shapes and tracks any drift from baseline.

The `signature_validator.py` module validates that method bindings in executor contracts match actual method implementations:
- Method exists in target class
- Parameter count matches
- Return type is compatible

The `coverage_gate.py` module verifies that test coverage meets the minimum threshold (default: 80%). If coverage is below threshold, execution is blocked.

#### Stage 40 → Stage 50 Transition

With all validations complete, Stage 50 executes the boot sequence. The `boot_checks.py` module runs a comprehensive checklist:

```python
BOOT_CHECKS = [
    ("python_version", check_python_version),
    ("required_packages", check_required_packages),
    ("configuration_valid", check_configuration),
    ("resources_available", check_resources),
    ("dependencies_importable", check_dependencies),
]
```

Each check returns pass/fail with detailed diagnostics on failure. Any failure raises `BootCheckError` and halts execution.

The `exit_gates.py` module then verifies exit conditions:
- `ConfigurationGate.verify()` - All configurations locked
- `DeterminismGate.verify()` - Reproducibility confirmed
- `ResourceGate.verify()` - Limits active
- `ValidationGate.verify()` - All inputs validated
- `WiringGate.verify()` - Ready for component assembly

#### Stage 50 → Stage 90 Transition

With all gates passed, Stage 90 performs final integration. The `main.py` module coordinates the entire sequence and prepares the execution context.

The `verified_pipeline_runner.py` module creates a verified execution wrapper that will be used by downstream phases.

The `bootstrap.py` module performs wiring initialization:

1. **Load Resources:** `QuestionnaireResourceProvider` loads the questionnaire monolith JSON
2. **Build Signals:** `SignalClient` and `SignalRegistry` are created (memory:// mode by default)
3. **Create Factory:** `CoreModuleFactory` is instantiated with DI
4. **Build Router:** `ExtendedArgRouter` is created with ≥30 special routes
5. **Assemble Components:** `WiringComponents` container is populated

The final `WiringComponents` object is passed to Phase 1 as the execution context.

### 4.3 Critical Path Analysis

The critical path through Phase 0 consists of the modules that must execute sequentially:

```
paths.py → runtime_config.py → determinism.py → resource_controller.py 
→ input_validation.py → boot_checks.py → bootstrap.py
```

**Total critical path modules:** 7
**Critical path estimated duration:** <1 second (on modern hardware)

Parallelization opportunities:
- Schema validation and signature validation can run in parallel (Stage 40)
- Seed factory and hash utils initialization can overlap (Stage 20)

---

## 5. Contracts and Guarantees

### 5.1 Input Contracts

Phase 0 accepts the following inputs:

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `questionnaire_path` | `Path` | Yes | Path to questionnaire monolith JSON |
| `questionnaire_hash` | `str` | Yes | Expected SHA-256 hash of monolith |
| `executor_config_path` | `Path` | Yes | Path to executor configuration |
| `calibration_profile` | `str` | Yes | Calibration profile name |
| `abort_on_insufficient` | `bool` | Yes | Abort on insufficient data |
| `resource_limits` | `dict` | No | Resource limit overrides |

### 5.2 Output Contracts

Phase 0 produces the following outputs:

| Output | Type | Description |
|--------|------|-------------|
| `WiringComponents` | `dataclass` | Container with all initialized components |
| `init_hashes` | `dict[str, str]` | Hashes of initialized components |
| `enforcement_metrics` | `EnforcementMetrics` | Resource usage during init |

**WiringComponents Structure:**
```python
@dataclass
class WiringComponents:
    provider: QuestionnaireResourceProvider
    signal_client: SignalClient
    signal_registry: SignalRegistry
    executor_config: ExecutorConfig
    factory: CoreModuleFactory
    arg_router: ExtendedArgRouter
    class_registry: dict[str, type]
    validator: WiringValidator
    calibration_orchestrator: CalibrationOrchestrator | None
    flags: WiringFeatureFlags
    init_hashes: dict[str, str]
```

### 5.3 Invariants

Phase 0 maintains the following invariants:

**INV-1: Determinism**
```
∀ identical_inputs: hash(phase0_output) = constant
```

**INV-2: Resource Bounds**
```
∀ execution: (memory_used ≤ RLIMIT_AS) ∧ (cpu_time ≤ RLIMIT_CPU)
```

**INV-3: Configuration Immutability**
```
∀ t > phase0_complete: RuntimeConfig.is_frozen() = True
```

**INV-4: Validation Completeness**
```
∀ input: validated(input) ∨ execution_blocked
```

### 5.4 Failure Modes

| Failure Mode | Exception | Recovery |
|--------------|-----------|----------|
| Path not found | `PathNotFoundError` | Verify path exists |
| Invalid configuration | `ConfigurationError` | Fix environment variables |
| Resource exhaustion | `ResourceExhausted` | Increase available resources |
| Contract violation | `ContractViolationError` | Fix contract or input |
| Boot check failure | `BootCheckError` | Address specific check |
| Gate verification failure | `GateError` | Address gate condition |

---

## 6. Resource Management

### 6.1 Kernel-Level Enforcement

Phase 0 uses `resource.setrlimit()` for non-bypassable enforcement:

```python
# Memory limit (address space)
resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

# CPU time limit
resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))

# File descriptor limit
resource.setrlimit(resource.RLIMIT_NOFILE, (fd_count, fd_count))
```

**Behavior on limit exceeded:**
- `RLIMIT_AS`: Process receives `MemoryError` on allocation
- `RLIMIT_CPU`: Process receives `SIGXCPU` signal
- `RLIMIT_NOFILE`: `open()` fails with `EMFILE`

### 6.2 Memory Watchdog

The `MemoryWatchdog` thread monitors system memory:

```python
class MemoryWatchdog(threading.Thread):
    def run(self):
        while not self._stop_event.is_set():
            mem = psutil.virtual_memory()
            if mem.percent > self.threshold_percent:
                logger.critical(f"MEMORY CRITICAL: {mem.percent}%")
                self.triggered_count += 1
            self._stop_event.wait(self.check_interval)
```

**Configuration:**
- `threshold_percent`: 90 (default)
- `check_interval`: 1.0 seconds (default)

### 6.3 Pre-flight Checks

Before setting limits, pre-flight checks verify:

```python
def preflight_checks(self) -> dict:
    checks = {
        "memory_available_mb": psutil.virtual_memory().available / (1024**2),
        "disk_available_mb": psutil.disk_usage('/tmp').free / (1024**2),
        "cpu_count": psutil.cpu_count(),
        "open_files": len(psutil.Process().open_files()),
    }
    
    if checks["memory_available_mb"] < self.limits.memory_mb * 0.5:
        raise ResourceExhausted("Insufficient memory")
    
    if checks["disk_available_mb"] < self.limits.disk_mb:
        raise ResourceExhausted("Insufficient disk")
    
    return checks
```

---

## 7. Determinism Guarantees

### 7.1 Seed Management Strategy

Phase 0 uses hierarchical seed derivation:

```
BASE_SEED (42)
    │
    ├── phase_seed = hash(BASE_SEED + phase_number)
    │       │
    │       ├── executor_seed = hash(phase_seed + executor_id)
    │       ├── method_seed = hash(phase_seed + method_name)
    │       └── sample_seed = hash(phase_seed + sample_index)
    │
    └── global_numpy_seed = hash(BASE_SEED + "numpy")
```

### 7.2 Hash Computation

All hashes use BLAKE3 for speed and security:

```python
import blake3

def compute_hash(data: dict) -> str:
    serialized = json.dumps(data, sort_keys=True).encode('utf-8')
    return blake3.blake3(serialized).hexdigest()
```

### 7.3 Reproducibility Verification

Phase 0 can verify reproducibility by:
1. Computing hash of initial configuration
2. Computing hash of all outputs
3. Comparing hashes across executions

```python
verification_hash = compute_hash({
    "config_hash": config_hash,
    "output_hash": output_hash,
    "seed": base_seed,
})
```

---

## 8. Configuration Reference

### 8.1 Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SAAAAAA_RUNTIME_MODE` | `str` | `prod` | Runtime mode (prod/dev/exploratory) |
| `ENFORCE_RESOURCES` | `bool` | `false` | Enable kernel resource enforcement |
| `RESOURCE_MEMORY_MB` | `int` | `2048` | Memory limit in MB |
| `RESOURCE_CPU_SECONDS` | `int` | `300` | CPU time limit in seconds |
| `RESOURCE_DISK_MB` | `int` | `500` | Minimum disk space in MB |
| `RESOURCE_FILE_DESCRIPTORS` | `int` | `1024` | File descriptor limit |

### 8.2 Runtime Configuration

See `phase0_10_01_runtime_config.py` for complete configuration reference.

### 8.3 Resource Limits

| Limit | Environment Variable | Default | Range |
|-------|---------------------|---------|-------|
| Memory | `RESOURCE_MEMORY_MB` | 2048 | 256-16384 |
| CPU | `RESOURCE_CPU_SECONDS` | 300 | 10-3600 |
| Disk | `RESOURCE_DISK_MB` | 500 | 50-10000 |
| FDs | `RESOURCE_FILE_DESCRIPTORS` | 1024 | 64-65536 |

---

## 9. Testing and Verification

### 9.1 Unit Tests

Each module has corresponding unit tests in `tests/unit/phase_0/`:

```
tests/unit/phase_0/
├── test_domain_errors.py
├── test_paths.py
├── test_runtime_config.py
├── test_seed_factory.py
├── test_resource_controller.py
├── test_input_validation.py
├── test_boot_checks.py
└── test_bootstrap.py
```

### 9.2 Integration Tests

Integration tests verify complete Phase 0 execution:

```
tests/integration/
├── test_phase0_full_sequence.py
├── test_phase0_resource_enforcement.py
└── test_phase0_determinism.py
```

### 9.3 Verification Checklist

- [ ] All paths resolve correctly
- [ ] Configuration parses without errors
- [ ] Determinism seed is consistent
- [ ] Resource limits are active
- [ ] All validations pass
- [ ] All boot checks pass
- [ ] All exit gates pass
- [ ] WiringComponents is fully populated
- [ ] Hash verification succeeds

---

## 10. Maintenance and Evolution

### 10.1 Known Limitations

1. **psutil Dependency:** Memory watchdog requires psutil; degrades gracefully if unavailable
2. **macOS RLIMIT_AS:** Address space limits may not work as expected on macOS
3. **Thread Safety:** MemoryWatchdog uses background thread; ensure cleanup on exceptions

### 10.2 Future Enhancements

1. **GPU Resource Limits:** Add CUDA memory monitoring
2. **Network Limits:** Add bandwidth/connection limits
3. **Distributed Verification:** Cross-node determinism verification
4. **Hot Reload:** Support configuration changes without restart

### 10.3 Migration Notes

**From legacy naming (pre-2025-12-29):**

Legacy files should be renamed according to the manifest in `PHASE_0_CONSTANTS.py`. The mapping is:

| Legacy Name | Canonical Name |
|-------------|----------------|
| `__init__.py` | `phase0_00_00_init.py` |
| `domain_errors.py` | `phase0_00_01_domain_errors.py` |
| `paths.py` | `phase0_10_00_paths.py` |
| ... | ... |

---

## 11. References

1. F.A.R.F.A.N Architecture Specification v3.0
2. GLOBAL_NAMING_POLICY.md (FPN-GLOBAL-001)
3. Python `resource` module documentation
4. BLAKE3 hash function specification
5. structlog documentation

---

## 12. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Boot Check** | Pre-flight verification before pipeline execution |
| **Exit Gate** | Condition that must be satisfied before proceeding |
| **Kernel Limit** | Resource limit enforced by OS kernel |
| **RLIMIT** | Resource limit constant from `resource` module |
| **Seed Factory** | Centralized seed management for determinism |
| **Watchdog** | Background thread monitoring system resources |
| **Wiring** | Component initialization and dependency injection |

### Appendix B: File Manifest

| Stage | Order | Canonical Name | Legacy Name | Type | Criticality | LOC |
|-------|-------|----------------|-------------|------|-------------|-----|
| 00 | 00 | phase0_00_00_init.py | \_\_init\_\_.py | INFRA | LOW | 38 |
| 00 | 01 | phase0_00_01_domain_errors.py | domain_errors.py | INFRA | HIGH | 137 |
| 00 | 02 | phase0_00_02_runtime_error_fixes.py | runtime_error_fixes.py | INFRA | MEDIUM | 135 |
| 10 | 00 | phase0_10_00_paths.py | paths.py | CFG | CRITICAL | 480 |
| 10 | 01 | phase0_10_01_runtime_config.py | runtime_config.py | CFG | CRITICAL | 584 |
| 10 | 02 | phase0_10_02_json_logger.py | json_logger.py | CFG | HIGH | 259 |
| 20 | 00 | phase0_20_00_seed_factory.py | seed_factory.py | ENF | CRITICAL | 198 |
| 20 | 01 | phase0_20_01_hash_utils.py | hash_utils.py | UTIL | HIGH | 41 |
| 20 | 02 | phase0_20_02_determinism.py | determinism.py | ENF | CRITICAL | 359 |
| 20 | 03 | phase0_20_03_determinism_helpers.py | determinism_helpers.py | UTIL | HIGH | 192 |
| 20 | 04 | phase0_20_04_deterministic_execution.py | deterministic_execution.py | ENF | CRITICAL | 445 |
| 30 | 00 | phase0_30_00_resource_controller.py | resource_controller.py | ENF | CRITICAL | 503 |
| 40 | 00 | phase0_40_00_input_validation.py | phase0_input_validation.py | VAL | CRITICAL | 540 |
| 40 | 01 | phase0_40_01_schema_monitor.py | schema_monitor.py | VAL | HIGH | 396 |
| 40 | 02 | phase0_40_02_signature_validator.py | signature_validator.py | VAL | HIGH | 474 |
| 40 | 03 | phase0_40_03_coverage_gate.py | coverage_gate.py | VAL | MEDIUM | 252 |
| 50 | 00 | phase0_50_00_boot_checks.py | boot_checks.py | ORCH | CRITICAL | 289 |
| 50 | 01 | phase0_50_01_exit_gates.py | exit_gates.py | ORCH | HIGH | 668 |
| 90 | 00 | phase0_90_00_main.py | main.py | ENTRY | CRITICAL | 157 |
| 90 | 01 | phase0_90_01_verified_pipeline_runner.py | verified_pipeline_runner.py | ORCH | CRITICAL | 516 |
| 90 | 02 | phase0_90_02_bootstrap.py | bootstrap.py | ORCH | CRITICAL | 1163 |
| 90 | 03 | phase0_90_03_wiring_validator.py | N/A (new) | VAL | CRITICAL | 848 |

**Total:** 22 modules, 8702 lines of code

### Appendix C: Error Code Reference

| Code | Exception | Description |
|------|-----------|-------------|
| `P0-CFG-001` | `ConfigurationError` | Invalid runtime mode |
| `P0-CFG-002` | `ConfigurationError` | Illegal configuration combination |
| `P0-PATH-001` | `PathNotFoundError` | Required path does not exist |
| `P0-PATH-002` | `PathPermissionError` | Insufficient path permissions |
| `P0-RES-001` | `ResourceExhausted` | Insufficient memory |
| `P0-RES-002` | `ResourceExhausted` | Insufficient disk space |
| `P0-VAL-001` | `DataContractError` | Input validation failed |
| `P0-VAL-002` | `SystemContractError` | Schema mismatch |
| `P0-BOOT-001` | `BootCheckError` | Boot check failed |
| `P0-GATE-001` | `GateError` | Exit gate verification failed |

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-29 | F.A.R.F.A.N Core Team | Initial version with complete stage taxonomy |
| 1.1.0 | 2025-12-31 | F.A.R.F.A.N Core Team | Added phase0_90_03_wiring_validator.py (7-tier structural integrity gate); Refactored phase0_90_00_main.py to thin CLI wrapper (1829→157 LOC); Updated module count (21→22) and total LOC (9498→8702) |

---

**END OF DOCUMENT**
