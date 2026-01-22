# Canonical Architecture (as of 2026-01-21)

**Status:** AUTHORITATIVE
**Version:** 3.0
**Enforcement:** MANDATORY - All code must conform to this architecture

---

## Phase Execution & Orchestration

**Authoritative Location:** `farfan_pipeline.orchestration.orchestrator`

**Key Classes:**
- `UnifiedOrchestrator` - Main coordinator for full pipeline execution (consolidated all orchestration logic)
- `OrchestratorConfig` - Configuration for orchestrator
- `OrchestrationStateMachine` - State machine for orchestration lifecycle
- `DependencyGraph` - Phase dependency management
- `PhaseScheduler` - Phase scheduling strategies (SEQUENTIAL, PARALLEL, HYBRID, PRIORITY)
- `ExecutionContext` - Shared state and metrics across phases
- `PhaseStatus`, `PhaseID`, `PhaseResult` - Phase execution primitives

**Architecture:**
The `orchestrator.py` file is a **UNIFIED** orchestrator that consolidated all orchestration logic from previously separate files:
- Configuration management (`OrchestratorConfig`)
- State machine lifecycle (`OrchestrationStateMachine`)
- Dependency graph management (`DependencyGraph`)
- Phase scheduling (`PhaseScheduler`)
- Core orchestration logic (`UnifiedOrchestrator`)
- Signal-driven orchestration (SISAS-aware)

**Canonical Import:**
```python
from farfan_pipeline.orchestration.orchestrator import (
    UnifiedOrchestrator,
    OrchestratorConfig,
    ExecutionContext,
    PhaseID,
    PhaseStatus,
    PhaseResult,
    # etc.
)
```

**Forbidden Alternatives:**
- ❌ `orchestration.orchestrator` (missing namespace prefix - incorrect)
- ❌ `farfan_pipeline.orchestration.core_orchestrator` (file does not exist - was never created)
- ❌ Any module in `/backups/orchestration_relocation_*/` (ARCHIVED ONLY)

**Other Orchestration Modules (Canonical):**
- `farfan_pipeline.orchestration.factory` - `UnifiedFactory` for component creation
- `farfan_pipeline.orchestration.method_registry` - Method registration
- `farfan_pipeline.orchestration.sisas_integration_hub` - SISAS integration
- `farfan_pipeline.orchestration.gates.*` - Validation gates
- `farfan_pipeline.orchestration.dependency_graph` - Dependency graph utilities
- `farfan_pipeline.orchestration.cli` - CLI interface

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
- `SISAS.signal_types.types.*` - Signal type definitions
- `SISAS.validators.*` - Signal validation
- `SISAS.wiring.*` - Signal wiring configuration
- `SISAS.irrigation.*` - Signal irrigation mechanisms
- `SISAS.vocabulary.*` - Signal vocabulary definitions

**Forbidden Alternatives:**
- ❌ `cross_cutting_infrastructure.irrigation_using_signals.*` (NAMESPACE DELETED)
- ❌ `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption` (DEPRECATED)

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

---

## Bootstrap & Infrastructure

**Authoritative Location:** `farfan_pipeline.phases.Phase_00`

**Critical Modules:**
- `phase0_90_02_bootstrap` - `EnforcedBootstrap`, `WiringBootstrap`
- `phase0_90_01_verified_pipeline_runner` - Pipeline entry point
- `phase0_90_00_main` - Main execution coordinator
- `phase0_30_00_resource_controller` - Resource limits and monitoring
- `phase0_00_01_domain_errors` - Domain-specific error types
- `phase0_10_01_runtime_config` - Runtime configuration
- `phase0_40_00_input_validation` - Input validation

---

## Data Models & Types

**Authoritative Locations:**
- **Contract Types:** `farfan_pipeline.phases.Phase_XX.contracts.*`
- **Wiring Types:** `farfan_pipeline.phases.Phase_00.interphase.wiring_types`
- **Signal Types:** `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal`
- **Domain Errors:** `farfan_pipeline.phases.Phase_00.phase0_00_01_domain_errors`

---

## Import Decision Rules

### Rule 1: Canonical Module Path
All imports must use the full `farfan_pipeline.*` namespace:
```python
# Correct
from farfan_pipeline.orchestration.orchestrator import UnifiedOrchestrator
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import Signal

# Incorrect
from orchestration.orchestrator import UnifiedOrchestrator
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.core.signal import Signal
```

### Rule 2: DEAD Module → DELETE
If module path does not exist on filesystem, **DELETE** all imports and usages.

### Rule 3: DEPRECATED Module → REDIRECT
If module exists in `_deprecated/` directory or marked `ERA_DEPRECATED`, **REDIRECT** to canonical location.

### Rule 4: ERA_CROSS_CUTTING → DELETE
Any import from `cross_cutting_infrastructure.*` is **DELETED** (namespace eliminated).

### Rule 5: Phantom Classes → INVESTIGATE
Classes that never existed must be:
1. Located in canonical modules (if they exist elsewhere)
2. Deleted (if concept no longer exists)
3. Created with ≥2 call sites and real semantics (if genuinely needed)

---

## Explicitly Dead Layers

The following architectural layers are **FORBIDDEN** and must not be referenced:

### Deleted Namespaces
- `cross_cutting_infrastructure.*` - Entire namespace removed

### Deprecated Modules (Exist but Forbidden)
- `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption` - In `_deprecated/` directory
- Any module in `_deprecated/` directories

### Archived Backups (Never Import)
- `backups/orchestration_relocation_*/` - Forensic archives only

---

## Enforcement Mechanism

**Validation Script:** `scripts/stratify_imports.sh`

**Failure Conditions:**
- Any import from forbidden namespaces → Build fails
- Any file in `*_compat.py`, `*_legacy.py`, `*_shim.py` → Build fails
- Any import from `_deprecated/` directory (except intentional migration) → Warning (escalates to error)

**Success Condition:**
The canonical architecture is **enforceable by deletion alone** - removing compatibility layers does not break the system.

---

## Version History
- **v3.0** (2026-01-21): Corrected canonical architecture - `orchestrator.py` IS the canonical orchestrator (was incorrectly marked as deleted in v2.0)
- **v2.0** (2026-01-17): Post-orchestrator migration declaration (had incorrect information about orchestrator.py)
- **v1.x**: Legacy orchestrator era (deprecated)

---

**Remember:** The system has a present tense. This document defines it. Code that contradicts this document must be updated or removed.

---

## Current Architecture Summary

The FARFAN pipeline architecture is now **CONSOLIDATED**:

| Component | Canonical Location | Status |
|-----------|-------------------|--------|
| Orchestrator | `farfan_pipeline.orchestration.orchestrator` | **LIVE** - Unified orchestrator |
| Factory | `farfan_pipeline.orchestration.factory` | **LIVE** - UnifiedFactory |
| SISAS | `farfan_pipeline.infrastructure.irrigation_using_signals.SISAS` | **LIVE** - Signal infrastructure |
| Phases | `farfan_pipeline.phases.Phase_XX` | **LIVE** - Phase execution |
| Signal Registry | `canonic_questionnaire_central.core.signal_distribution_orchestrator` | **LIVE** - Signal distribution |

**Exit Criteria Status:**
- ✅ No imports from `cross_cutting_infrastructure.*` (DELETED namespace)
- ✅ `orchestrator.py` is the canonical orchestrator (83KB unified file)
- ✅ Architecture is enforceable by deletion alone - forbidden modules can be removed without breaking active code
- ✅ All imports use the canonical `farfan_pipeline.*` namespace

**The architectural timelines have collapsed. The present tense is authoritative.**
