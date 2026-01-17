# Canonical Architecture (as of 2026-01-17)

**Status:** AUTHORITATIVE
**Version:** 2.0
**Enforcement:** MANDATORY - All code must conform to this architecture

---

## Phase Execution & Orchestration

**Authoritative Location:** `farfan_pipeline.orchestration.core_orchestrator`

**Key Classes:**
- `PipelineOrchestrator` - Main coordinator for full pipeline execution
- `MethodExecutor` - Phase method execution wrapper
- `Orchestrator` - Legacy-compatible orchestrator interface
- `ExecutionContext` - Shared state and metrics across phases
- `PhaseExecutor` - Protocol for phase execution
- `ContractEnforcer` - Pre/post execution contract validation
- `PhaseStatus`, `PhaseID`, `PhaseResult` - Phase execution primitives

**Configuration:** `farfan_pipeline.orchestration.orchestrator_config`

**Forbidden Alternatives:**
- ❌ `orchestration.orchestrator` (DELETED - no longer exists)
- ❌ `farfan_pipeline.orchestration.orchestrator` (DELETED - replaced by core_orchestrator)
- ❌ Any module in `/backups/orchestration_relocation_*/` (ARCHIVED ONLY)

---

## Signal Processing Infrastructure

**Authoritative Location:** `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS`

**Architecture:**
- `SISAS.core.signal` - Core signal definitions and types
- `SISAS.core.event` - Event processing primitives
- `SISAS.core.contracts` - Contract-based signal validation
- `SISAS.signals` - Signal registry and management (`SignalRegistry`)
- `SISAS.vehicles.*` - Signal transport and scoping mechanisms
- `SISAS.consumers/phase*/*` - Phase-specific signal consumers
- `SISAS.metadata.*` - Signal metadata and enrichment
- `SISAS.semantic.*` - Semantic signal expansion

**Forbidden Alternatives:**
- ❌ `cross_cutting_infrastructure.irrigation_using_signals.*` (NAMESPACE DELETED)
- ❌ `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption` (DEPRECATED - see Migration Path below)
- ❌ `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption_integration` (DEPRECATED)

**Migration Path for Deprecated Signal Consumption:**
- Old: `from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption import X`
- New: Classes moved to appropriate locations:
  - Signal types → `SISAS.core.signal`
  - Signal registry → `SISAS.signals`
  - Integration → Phase-specific consumers in `SISAS.consumers/phase*/`

---

## Phase-Specific Execution

**Authoritative Location:** `farfan_pipeline.phases.Phase_XX/` (where XX = 00-09)

**Structure:**
- `Phase_00/` - Bootstrap, validation, resource control, wiring
- `Phase_01/` - CPP ingestion, data loading
- `Phase_02/` - Executor factory, method dispatch
- `Phase_03/` - Layer scoring
- `Phase_04/` - Dimension aggregation
- `Phase_05/` - Policy area aggregation
- `Phase_06/` - Cluster aggregation
- `Phase_07/` - Macro aggregation
- `Phase_08/` - Recommendations engine
- `Phase_09/` - Report assembly

**Key Submodules:**
- `contracts/` - Phase contracts for validation
- `primitives/` - Shared primitives (Phase_00 only)
- `interphase/` - Cross-phase wiring (Phase_00 only)
- `phase{N}_{stage}_{substage}_{name}.py` - Phase execution modules

**Aliases:**
- `Phase_zero` → symlink to `Phase_00` (tolerated for compatibility)

---

## Bootstrap & Infrastructure

**Authoritative Location:** `farfan_pipeline.phases.Phase_00`

**Critical Modules:**
- `phase0_90_02_bootstrap` - `EnforcedBootstrap`, `WiringBootstrap`
- `phase0_90_01_verified_pipeline_runner` - Pipeline entry point
- `phase0_90_00_main` - Main execution coordinator
- `phase0_30_00_resource_controller` - Resource limits and monitoring
- `phase0_00_01_domain_errors` - Domain-specific error types
- `primitives.providers` - Data providers and configuration
- `primitives.constants` - System-wide constants
- `interphase.wiring_types` - Wiring contracts and types

---

## Resource Orchestration

**Authoritative Location:** `farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller`

**Key Classes:**
- `ResourceController` - Resource allocation and limits
- `ResourceLimits` - Resource limit definitions
- `MemorySafety` - Memory safety enforcement (also in `farfan_pipeline.orchestration.memory_safety`)

**Forbidden Alternatives:**
- ❌ `orchestration.orchestrator.ResourceLimits` (NEVER EXISTED - phantom import)

---

## Data Models & Types

**Authoritative Locations:**
- **Contract Types:** `farfan_pipeline.phases.Phase_XX.contracts.*`
- **Wiring Types:** `farfan_pipeline.phases.Phase_00.interphase.wiring_types`
- **Signal Types:** `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal`
- **Domain Errors:** `farfan_pipeline.phases.Phase_00.phase0_00_01_domain_errors`

**Classes Imported from core_orchestrator:**
- `MethodExecutor` - Phase method executor
- `Orchestrator` - Pipeline orchestrator
- `ExecutionContext` - Execution state container
- `PhaseResult`, `PhaseStatus`, `PhaseID` - Phase primitives

---

## Missing Classes Resolution (Phase 6 Adjudication)

The following classes were imported from `orchestration.orchestrator` but **NEVER EXISTED** in the deleted file. They are **PHANTOM IMPORTS** that must be resolved:

### Category A: Classes Now in core_orchestrator.py
✅ **Resolved:** Import from `farfan_pipeline.orchestration.core_orchestrator`
- `MethodExecutor` - Exists at core_orchestrator:780+
- `Orchestrator` - Exists at core_orchestrator:950+

### Category B: Classes That May Exist Elsewhere
🔍 **Requires Investigation:**
- `ScoredMicroQuestion` - Check Phase_03 (scoring) or Phase_04 (aggregation)
- `MacroEvaluation` - Check Phase_07 (macro aggregation)
- `MicroQuestionRun` - Check Phase_02 (executor) or Phase_03 (scoring)
- `Evidence` - Check contract types or Phase_01 (evidence collection)
- `QuestionnaireSignalRegistry` - Likely in Phase_02 signal registry
- `ResourceLimits` - Check phase0_30_00_resource_controller
- `PhaseInstrumentation` - Check core_orchestrator or Phase_00 monitoring
- `AbortSignal` - Check domain errors or signal core
- `execute_phase_with_timeout` - Check core_orchestrator methods

---

## Explicitly Dead Layers

The following architectural layers are **FORBIDDEN** and must not be referenced:

### Deleted Namespaces
- `orchestration.orchestrator.*` - File deleted, replaced by `farfan_pipeline.orchestration.core_orchestrator`
- `cross_cutting_infrastructure.*` - Entire namespace removed
- `farfan_pipeline.orchestration.orchestrator.*` - File renamed to core_orchestrator

### Deprecated Modules (Exist but Forbidden)
- `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption` - In `_deprecated/` directory
- `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption_integration` - In `_deprecated/` directory
- Any module in `_deprecated/` directories

### Archived Backups (Never Import)
- `backups/orchestration_relocation_*/` - Forensic archives only

---

## Concept Evolution Table

| Old Term | New Term | Rationale |
|----------|----------|-----------|
| `orchestration.orchestrator` | `farfan_pipeline.orchestration.core_orchestrator` | Namespace consolidation, explicit module name |
| `cross_cutting_infrastructure.irrigation_using_signals` | `farfan_pipeline.infrastructure.irrigation_using_signals` | Removed redundant "cross_cutting" abstraction |
| `signal_consumption` | Phase-specific consumers in `SISAS.consumers/` | Distributed responsibility to phase consumers |
| `Orchestrator` (global) | `PipelineOrchestrator` (primary) or `Orchestrator` (compat) | Explicit naming, retained compatibility alias |

---

## Import Decision Rules

### Rule 1: DEAD Module → DELETE
If module path does not exist on filesystem, **DELETE** all imports and usages.

### Rule 2: DEPRECATED Module → REDIRECT
If module exists in `_deprecated/` directory or marked `ERA_DEPRECATED`, **REDIRECT** to canonical location.

### Rule 3: ERA_CROSS_CUTTING → DELETE
Any import from `cross_cutting_infrastructure.*` is **DELETED** (namespace eliminated).

### Rule 4: ERA_ORCHESTRATOR → REDIRECT to core_orchestrator
Any import from `orchestration.orchestrator` → `farfan_pipeline.orchestration.core_orchestrator`

### Rule 5: Phantom Classes → INVESTIGATE
Classes that never existed must be:
1. Located in canonical modules (if they exist elsewhere)
2. Deleted (if concept no longer exists)
3. Created with ≥2 call sites and real semantics (if genuinely needed)

---

## Enforcement Mechanism

**Validation Script:** `scripts/validate_architecture.sh`

**Failure Conditions:**
- Any import from forbidden namespaces → Build fails
- Any file in `*_compat.py`, `*_legacy.py`, `*_shim.py` → Build fails
- Any import from `_deprecated/` directory (except intentional migration) → Warning (escalates to error)

**Success Condition:**
The canonical architecture is **enforceable by deletion alone** - removing compatibility layers does not break the system.

---

## Version History
- **v2.0** (2026-01-17): Post-orchestrator migration, canonical architecture declaration
- **v1.x**: Legacy orchestrator era (deprecated)

---

**Remember:** The system has a present tense. This document defines it. Code that contradicts this document must be updated or removed.
