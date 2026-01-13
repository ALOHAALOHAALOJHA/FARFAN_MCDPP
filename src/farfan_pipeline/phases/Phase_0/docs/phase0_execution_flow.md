# Phase 0 Execution Flow

## Overview
Phase 0 establishes the validated, hardened, and deterministic environment required for the pipeline. It executes a strict sequence of stages to ensure all prerequisites are met before any data processing begins.

## Execution Sequence

### 1. Stage 00: Infrastructure (Boot)
- **Goal:** Initialize base protocols and error handling.
- **Actions:**
  - Load domain errors (`phase0_00_01_domain_errors.py`).
  - Initialize contract protocols (`phase0_00_03_protocols.py`).
  - Apply runtime error fixes for critical dependencies (`primitives/runtime_error_fixes.py`).

### 2. Stage 10: Environment Configuration
- **Goal:** Resolve paths and parse configuration.
- **Actions:**
  - Resolve absolute paths for all artifacts (`phase0_10_00_paths.py`).
  - Parse environment variables into `RuntimeConfig` (`phase0_10_01_runtime_config.py`).
  - Initialize structured JSON logging (`primitives/json_logger.py`).
  - **Exit Gate:** Configuration must be valid and conflict-free.

### 3. Stage 20: Determinism Enforcement
- **Goal:** Guarantee reproducibility.
- **Actions:**
  - Initialize global seed registry.
  - Compute deterministic seeds based on Run ID (`phase0_20_02_determinism.py`).
  - Seed Python `random` and `numpy.random`.
  - **Exit Gate:** All RNGs must be seeded.

### 4. Stage 30: Resource Control
- **Goal:** Prevent resource exhaustion.
- **Actions:**
  - Set kernel-level limits (RLIMIT) for Memory and CPU (`phase0_30_00_resource_controller.py`).
  - Initialize performance metrics tracking (`primitives/performance_metrics.py`).
  - **Exit Gate:** Resource limits must be active and verified.

### 5. Stage 40: Validation
- **Goal:** Verify input integrity.
- **Actions:**
  - Validate `Phase0Input` (PDF existence, JSON validity) (`phase0_40_00_input_validation.py`).
  - Compute SHA-256 hashes for all inputs.
  - Verify function signatures (`primitives/signature_validator.py`).
  - **Exit Gate:** `CanonicalInput` produced with `validation_passed=True`.

### 6. Stage 50: Boot Sequence
- **Goal:** Final pre-flight checks.
- **Actions:**
  - Run comprehensive boot checks (`phase0_50_00_boot_checks.py`).
  - Verify all exit gates (`phase0_50_01_exit_gates.py`).
  - **Exit Gate:** All checks passed (or allowed warnings in DEV mode).

### 7. Stage 90: Integration & Handoff
- **Goal:** Assemble components and handoff to Phase 1.
- **Actions:**
  - Wire all components (`phase0_90_02_bootstrap.py`).
  - Validate wiring integrity (`phase0_90_03_wiring_validator.py`).
  - Produce `WiringComponents` and `CanonicalInput`.
  - **Exit Gate:** Handoff complete.

## Data Flow
`User Input` -> `Phase0Input` -> **[Validation]** -> `CanonicalInput` -> **[Phase 1]**

## Handoff Artifacts
1. `CanonicalInput`: The single source of truth for input data.
2. `WiringComponents`: Initialized service objects (Provider, Registry, Factory).
3. `EnforcementMetrics`: Resource usage stats.
