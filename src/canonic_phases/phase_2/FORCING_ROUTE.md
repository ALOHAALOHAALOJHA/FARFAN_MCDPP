# FORCING ROUTE - Phase 2 Architecture

**STATUS**: ENFORCED

This document defines the canonical architecture and routing constraints for Phase 2.

## Canonical Path Declaration

```
CANONICAL_ROOT: src/canonic_phases/phase_2/
ALTERNATIVE_PATHS: FORBIDDEN
LEGACY_PATHS: src/farfan_pipeline/phases/Phase_two/ [DEPRECATED - DELETE_ON_DISCOVERY]
```

## Architectural Invariants

### INV-P2-001: Executor Count
**Value**: Exactly 300 executor contracts (Q001-Q300)
**Rationale**: 30 base questions × 10 policy areas = 300 specialized contracts
**Enforcement**: Fail-fast validation in synchronization layer

### INV-P2-002: Chunk Count
**Value**: Exactly 60 document chunks (10 PA × 6 DIM)
**Rationale**: Constitutional PA×DIM grid from Phase 1
**Enforcement**: Chunk matrix validation in irrigation synchronizer

### INV-P2-003: Executor-Chunk Binding
**Value**: 1:1 mapping validation required
**Rationale**: Deterministic task planning with explicit bindings
**Enforcement**: JOIN table construction with uniqueness validation

### INV-P2-004: Contract Version
**Value**: v3 contract format
**Rationale**: Enhanced with epistemological foundations and assembly flow
**Enforcement**: Contract schema validation in CQVR gate

### INV-P2-005: Separation of Concerns
**Value**: Runtime config (HOW) vs Calibration (WHAT)
**Rationale**: Clear separation prevents configuration drift
**Enforcement**: Type system and schema validation

## Stage Pipeline Architecture

Phase 2 follows a strict 7-stage pipeline:

```
STAGE_A (Routing) → STAGE_B (Carving) → STAGE_C (Validation) → 
STAGE_D (Configuration) → STAGE_E (SISAS) → STAGE_F (Chunk Sync) → 
STAGE_G (Orchestration)
```

### Stage Dependencies

- STAGE_A: No dependencies (entry point)
- STAGE_B: Requires STAGE_A output
- STAGE_C: Requires STAGE_B output
- STAGE_D: Independent (configuration loading)
- STAGE_E: Requires STAGE_A, STAGE_D
- STAGE_F: Requires STAGE_E
- STAGE_G: Requires all previous stages

## Module Naming Convention

All Phase 2 modules follow the pattern:
```
phase2_{stage_letter}_{stage_name}.py
```

Examples:
- `phase2_a_arg_router.py` (STAGE_A)
- `phase2_b_carver.py` (STAGE_B)
- `phase2_g_synchronization.py` (STAGE_G)

## Import Routing Rules

### RULE-001: Canonical Imports Only
All Phase 2 imports must use canonical paths:
```python
# ✅ CORRECT
from canonic_phases.phase_2.phase2_a_arg_router import ExtendedArgRouter

# ❌ FORBIDDEN
from farfan_pipeline.phases.Phase_two.arg_router import ExtendedArgRouter
```

### RULE-002: No Circular Dependencies
Stage modules must not create circular dependencies:
- Forward dependencies only (A→B→C, never C→A)
- Shared types go in `constants/` or `schemas/`

### RULE-003: Legacy Compatibility
Legacy imports are allowed temporarily via compatibility shim:
```python
# Compatibility shim in farfan_pipeline/phases/Phase_two/__init__.py
from canonic_phases.phase_2 import *  # Re-export canonical
```

## Quality Gates

### GATE-001: CQVR Validation
All executor outputs must pass CQVR validation:
- Tier 1: ≥80% for production
- Tier 2: ≥60% for reformulation
- <60%: Requires patching

### GATE-002: Schema Validation
All data structures must validate against JSON schemas:
- `executor_config.schema.json` for runtime config
- `executor_output.schema.json` for results
- `synchronization_manifest.schema.json` for bindings

### GATE-003: Determinism Validation
All execution must be deterministic:
- Fixed random seeds
- Stable task ordering
- Reproducible plan_id generation

## Observability Requirements

### REQ-001: Correlation ID Tracking
All operations must propagate correlation_id:
- HTTP header: `X-Correlation-ID`
- Log context: `correlation_id` field
- Metrics labels: `correlation_id` tag

### REQ-002: Structured Logging
All logs must be structured JSON:
```json
{
  "timestamp": "2024-12-18T20:15:00Z",
  "level": "INFO",
  "stage": "STAGE_E",
  "correlation_id": "abc123",
  "message": "Task generation completed",
  "task_count": 300
}
```

### REQ-003: Metrics Export
All stages must export Prometheus metrics:
- Namespace: `farfan_phase2`
- Subsystem: `executor`
- Labels: stage, executor_id, policy_area, dimension

## Migration Path

### Legacy Code Deprecation
1. All new code must use canonical paths
2. Legacy paths are marked `[DEPRECATED]`
3. Compatibility shims provide temporary bridge
4. Legacy paths deleted after full migration validation

### Validation Checklist
- [ ] All imports use canonical paths
- [ ] All tests pass with canonical imports
- [ ] No circular dependencies
- [ ] Schema validation passes
- [ ] Quality gates pass
- [ ] Observability requirements met

## Enforcement

Violations of this FORCING_ROUTE are treated as **CRITICAL** errors:
- CI/CD pipeline failures
- Pre-commit hook rejections
- Code review blockers

**NO EXCEPTIONS** without architectural approval.
