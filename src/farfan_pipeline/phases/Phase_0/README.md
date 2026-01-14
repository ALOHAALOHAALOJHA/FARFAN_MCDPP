# Phase 0: Validation, Hardening & Bootstrap

**Document ID:** PHASE-0-README
**Version:** 2.0.0
**Date:** 2026-01-13
**Status:** STABILIZED / FROZEN
**Authors:** F.A.R.F.A.N Core Architecture Team
**Classification:** Technical Specification - Internal

---

## Abstract

Phase 0 constitutes the foundational layer of the F.A.R.F.A.N (Framework for Automated Reasoning on Fiscal, Administrative, and Regulatory Frameworks for Analytical Normalization) deterministic policy analysis pipeline. This phase implements a rigorous pre-execution validation, hardening, and bootstrap protocol that guarantees system integrity, reproducibility, and resource safety before any analytical computation commences. The architecture enforces kernel-level resource limits via `setrlimit()`, guarantees bitwise-identical reproducibility through deterministic seed management, validates all input contracts and schemas, and orchestrates the complete wiring initialization sequence. This document specifies the complete technical architecture, execution semantics, module inventory, and formal verification properties required for production deployment.

**Keywords:** deterministic execution, resource enforcement, validation pipeline, bootstrap orchestration, reproducibility guarantees, kernel-level limits

**Test Status (2026-01-13):** 
- **52/52 Tests Passed** (100% Pass Rate)
- **Topological Coverage:** 100% (Stage 00 - Stage 90)
- **Adversarial Tests:** Included (Path traversal, SQL injection, Resource limits)
- **Structural Integrity:** 0 Cycles, 0 True Orphans (Verified by `verify_phase_chain.py`)

**Status (v2.0.0):**
- **Stabilized:** All components verified and contracts frozen.
- **Refactored:** Utility modules consolidated into `primitives/`.
- **Decoupled:** Shared types extracted to `interphase/` to resolve dependency cycles.
- **Hardened:** Kernel-level resource enforcement and adversarial input validation active.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture](#2-architecture)
3. [Module Inventory](#3-module-inventory)
4. [Execution Narrative](#4-execution-narrative)
5. [Contracts and Guarantees](#5-contracts-and-guarantees)
6. [Resource Management](#6-resource-management)
7. [Determinism Guarantees](#7-determinism-guarantees)
8. [Configuration Reference](#8-configuration-reference)
9. [Testing and Verification](#9-testing-and-verification)
10. [Appendices](#10-appendices)

---

## 1. Introduction

### 1.1 Phase Overview

Phase 0 is the **pre-analytical foundation layer** of the F.A.R.F.A.N pipeline. It establishes the preconditions necessary for safe, reproducible, and validated execution. It produces no analytical outputs—its sole product is a **validated, hardened execution environment**.

### 1.2 Scope and Boundaries

**In Scope:**
- ✅ Path resolution and validation
- ✅ Runtime configuration parsing and validation
- ✅ Deterministic seed management
- ✅ Resource limit enforcement (memory, CPU, disk, FDs)
- ✅ Input document validation (PDF & Questionnaire)
- ✅ Schema monitoring and verification
- ✅ Boot checks and exit gates
- ✅ Wiring initialization and bootstrap

**Out of Scope:**
- ❌ Document ingestion (Phase 1)
- ❌ Executor orchestration (Phase 2)
- ❌ Analytical processing

---

## 2. Architecture

### 2.1 Directory Structure

The phase is organized into a strict hierarchy to prevent circular dependencies and clarify module roles:

```
src/farfan_pipeline/phases/Phase_0/
├── contracts/          # Formal Input/Output/Mission contracts
├── docs/               # Audit reports, execution flows, checklists
├── interphase/         # Shared types and protocols (leaf nodes)
├── primitives/         # Low-level utilities, constants, validators
├── tests/              # Comprehensive test suite
├── phase0_*.py         # Core logic modules (Stages 00-90)
├── PHASE_0_MANIFEST.json
└── README.md
```

### 2.2 Stage Taxonomy

| Stage | Name | Description | Key Modules |
|-------|------|-------------|-------------|
| 00 | Infrastructure | Base types, errors, protocols | `domain_errors`, `protocols` |
| 10 | Environment | Paths, config, logging | `paths`, `runtime_config` |
| 20 | Determinism | Seeding, hashing | `determinism` |
| 30 | Resources | Kernel limits, metrics | `resource_controller` |
| 40 | Validation | Inputs, schemas, signatures | `input_validation` |
| 50 | Boot | Pre-flight checks, gates | `boot_checks`, `exit_gates` |
| 90 | Integration | Main entry, wiring, bootstrap | `main`, `bootstrap`, `wiring_validator` |

### 2.3 Dependency Graph

The execution flow forms a strict Directed Acyclic Graph (DAG):

```
interphase/wiring_types ──────┐
primitives/providers ─────────┤
                              ▼
paths → runtime_config → domain_errors
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
     determinism      resource_controller   input_validation
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                         boot_checks
                              │
                              ▼
                          exit_gates
                              │
                              ▼
                          bootstrap
                              │
                              ▼
                       wiring_validator
                              │
                              ▼
                      verified_runner
```

---

## 3. Module Inventory

### 3.1 Core Logic (Root)

| Module | Stage | Criticality | Responsibility |
|--------|-------|-------------|----------------|
| `phase0_00_01_domain_errors.py` | 00 | HIGH | Exception hierarchy |
| `phase0_00_03_protocols.py` | 00 | CRITICAL | Phase contract definitions |
| `phase0_10_00_paths.py` | 10 | CRITICAL | Path resolution |
| `phase0_10_01_runtime_config.py` | 10 | CRITICAL | Configuration parsing |
| `phase0_10_01_runtime_config_typed.py` | 10 | CRITICAL | Typed config models |
| `phase0_20_02_determinism.py` | 20 | CRITICAL | Seed management |
| `phase0_30_00_resource_controller.py` | 30 | CRITICAL | Kernel resource limits |
| `phase0_40_00_input_validation.py` | 40 | CRITICAL | Input validation |
| `phase0_50_00_boot_checks.py` | 50 | CRITICAL | Pre-flight checks |
| `phase0_50_01_exit_gates.py` | 50 | HIGH | Exit gate verification |
| `phase0_90_00_main.py` | 90 | CRITICAL | CLI entry point |
| `phase0_90_01_verified_pipeline_runner.py` | 90 | CRITICAL | Execution wrapper |
| `phase0_90_02_bootstrap.py` | 90 | CRITICAL | Component wiring |
| `phase0_90_03_wiring_validator.py` | 90 | CRITICAL | Wiring validation |

### 3.2 Primitives (Helpers)

| Module | Type | Responsibility |
|--------|------|----------------|
| `primitives/constants.py` | CONST | Global constants |
| `primitives/json_logger.py` | UTIL | Structured logging |
| `primitives/performance_metrics.py` | UTIL | Timing & metrics |
| `primitives/runtime_error_fixes.py` | UTIL | Defensive coding helpers |
| `primitives/schema_monitor.py` | VAL | Schema drift detection |
| `primitives/signature_validator.py` | VAL | Function signature verification |
| `primitives/coverage_gate.py` | VAL | Code coverage enforcement |
| `primitives/providers.py` | UTIL | Shared resource providers |

### 3.3 Interphase (Types)

| Module | Type | Responsibility |
|--------|------|----------------|
| `interphase/wiring_types.py` | TYPE | Shared data structures (WiringComponents, Violations) |

---

## 4. Execution Narrative

1.  **Boot (t=0):** Load infrastructure, protocols, and primitives.
2.  **Config (t=1):** Resolve paths, load `RuntimeConfig`, initialize `json_logger`.
3.  **Determinism (t=2):** Compute deterministic seeds from Run ID, seed RNGs (`random`, `numpy`).
4.  **Resources (t=3):** Set RLIMITs (Memory, CPU), start watchdog.
5.  **Validation (t=4):** Validate PDF/JSON inputs, check schemas.
6.  **Checks (t=5):** Run `boot_checks` and verify `exit_gates`.
7.  **Integration (t=6):** Assemble `WiringComponents` via `bootstrap`, validate via `wiring_validator`.
8.  **Handoff (t=7):** Return `WiringComponents` and `CanonicalInput` to Phase 1.

---

## 5. Contracts and Guarantees

-   **Input:** `Phase0Input` (PDF Path, Run ID, Questionnaire Path).
-   **Output:** `CanonicalInput` (Validated artifacts) + `WiringComponents` (Initialized services).
-   **Invariant 1 (Determinism):** Identical inputs + same Run ID = Identical Output.
-   **Invariant 2 (Resource Safety):** Execution strictly bounded by Kernel limits.
-   **Invariant 3 (Integrity):** No component is returned unless fully validated.

---

## 6. Testing and Verification

-   **Test Suite:** `tests/`
-   **Framework:** `pytest`
-   **Coverage:** 100% of topological stages covered.
-   **Adversarial Tests:**
    -   Path traversal attacks rejected.
    -   SQL injection in Run ID rejected.
    -   Null byte injection rejected.
    -   Missing resources trigger `ResourceExhausted`.
    -   Missing mandatory seeds trigger failure.

To run tests:
```bash
PYTHONPATH=src pytest src/farfan_pipeline/phases/Phase_0/tests
```

---

## 7. Change Log

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01-13 | **STABILIZATION RELEASE**: Refactored to eliminate circular dependencies. Moved utilities to `primitives/`. Added `interphase/` for types. Full adversarial test suite added. |
| 1.4.0 | 2026-01-11 | Bug fixes for enum comparison and import paths. |
| 1.3.0 | 2026-01-07 | Security hardening release. |

---

**END OF DOCUMENT**