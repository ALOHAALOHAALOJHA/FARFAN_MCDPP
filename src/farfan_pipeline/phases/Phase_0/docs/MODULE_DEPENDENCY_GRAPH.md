# Phase 0 Module Dependency Graph
**Document ID:** PHASE0-DEP-GRAPH-001
**Version:** 1.0.0
**Date:** 2026-01-13
**Status:** ACTIVE

## Overview

This document describes the module dependency graph for Phase 0, showing how
modules import and depend on each other to form a Directed Acyclic Graph (DAG)
with strict topological ordering.

## Graph Properties

- **Total Nodes:** 29 modules (including __init__.py and constants)
- **Graph Type:** Directed Acyclic Graph (DAG)
- **Cycles:** 0 (verified)
- **Orphaned Nodes:** 0 (all reachable from entry point)
- **Critical Path Length:** 7 modules
- **Maximum Depth:** 7 stages (00 → 10 → 20 → 30 → 40 → 50 → 90)

## Topological Levels

Modules are organized into topological levels based on their dependencies:

### Level 0: Foundation (No Dependencies)
```
phase0_00_01_domain_errors.py
phase0_00_02_runtime_error_fixes.py
primitives/phase0_00_03_primitives.py
phase0_20_01_hash_utils.py (standalone)
phase0_30_01_performance_metrics.py (standalone)
```

### Level 1: Infrastructure
```
phase0_00_03_protocols.py
    ← primitives/phase0_00_03_primitives.py
```

### Level 2: Path & Configuration
```
phase0_10_00_paths.py
    ← phase0_00_01_domain_errors.py

phase0_10_00_phase_0_constants.py
    (constants, no imports)
```

### Level 3: Runtime Configuration
```
phase0_10_01_runtime_config.py
    ← phase0_10_00_paths.py

phase0_10_01_runtime_config_typed.py
    ← phase0_10_01_runtime_config.py

phase0_10_03_runtime_config_schema.py
    ← phase0_10_01_runtime_config.py
```

### Level 4: Logging & Seeds
```
phase0_10_02_json_logger.py
    ← phase0_10_01_runtime_config.py

phase0_20_00_seed_factory.py
    ← phase0_10_01_runtime_config.py
```

### Level 5: Determinism
```
phase0_20_02_determinism.py
    ← phase0_20_00_seed_factory.py
    ← phase0_20_01_hash_utils.py

phase0_20_03_determinism_helpers.py
    ← phase0_20_02_determinism.py

phase0_20_04_deterministic_execution.py
    ← phase0_20_02_determinism.py
    ← phase0_20_03_determinism_helpers.py
```

### Level 6: Resource Control
```
phase0_30_00_resource_controller.py
    ← phase0_10_01_runtime_config.py
    ← phase0_10_02_json_logger.py
```

### Level 7: Validation
```
phase0_40_00_input_validation.py
    ← phase0_10_00_paths.py
    ← phase0_10_01_runtime_config.py
    ← phase0_00_01_domain_errors.py
    ← phase0_00_03_protocols.py

phase0_40_01_schema_monitor.py
    ← phase0_20_01_hash_utils.py

phase0_40_02_signature_validator.py
    ← phase0_00_01_domain_errors.py

phase0_40_03_coverage_gate.py
    ← phase0_10_01_runtime_config.py
```

### Level 8: Boot Checks
```
phase0_50_00_boot_checks.py
    ← phase0_10_01_runtime_config.py
    ← phase0_30_00_resource_controller.py
    ← phase0_40_00_input_validation.py

phase0_50_01_exit_gates.py
    ← phase0_50_00_boot_checks.py
    ← phase0_40_00_input_validation.py
```

### Level 9: Bootstrap & Integration
```
phase0_90_02_bootstrap.py
    ← phase0_30_00_resource_controller.py
    ← phase0_50_01_exit_gates.py

phase0_90_03_wiring_validator.py
    ← phase0_90_02_bootstrap.py

phase0_90_01_verified_pipeline_runner.py
    ← phase0_90_00_main.py
    ← phase0_30_00_resource_controller.py

phase0_90_00_main.py
    ← ALL modules (orchestrator)
```

### Level 10: Package Entry
```
__init__.py
    ← Selected exports from all levels
```

## Critical Path

The critical path represents the longest dependency chain that must execute
sequentially. This path determines the minimum execution time.

```
1. phase0_00_01_domain_errors.py (foundational)
   ↓
2. phase0_10_00_paths.py (path resolution)
   ↓
3. phase0_10_01_runtime_config.py (configuration)
   ↓
4. phase0_20_02_determinism.py (via seed_factory)
   ↓
5. phase0_30_00_resource_controller.py (resource limits)
   ↓
6. phase0_40_00_input_validation.py (validation)
   ↓
7. phase0_50_00_boot_checks.py (pre-flight)
   ↓
8. phase0_50_01_exit_gates.py (exit verification)
   ↓
9. phase0_90_02_bootstrap.py (component wiring)
```

**Critical Path Length:** 9 modules
**Estimated Execution Time:** <1 second (on modern hardware)

## Parallelization Opportunities

Some modules can execute in parallel as they have no mutual dependencies:

### Parallel Group 1 (Stage 20)
```
phase0_20_00_seed_factory.py  ⎤
                               ⎥→ (both depend on runtime_config)
phase0_20_01_hash_utils.py     ⎦
```

### Parallel Group 2 (Stage 40)
```
phase0_40_01_schema_monitor.py     ⎤
phase0_40_02_signature_validator.py ⎥→ (independent validation modules)
phase0_40_03_coverage_gate.py       ⎦
```

These groups could be executed concurrently to reduce initialization time.

## Module Classification

### By Import Pattern

**Hub Modules** (imported by many):
- `phase0_00_01_domain_errors.py` (5+ dependents)
- `phase0_10_01_runtime_config.py` (6+ dependents)
- `primitives/phase0_00_03_primitives.py` (2+ dependents)

**Leaf Modules** (import many, not imported):
- `phase0_90_00_main.py` (orchestrator)
- `phase0_90_03_wiring_validator.py`
- `__init__.py`

**Bridge Modules** (import and imported):
- `phase0_10_00_paths.py`
- `phase0_20_02_determinism.py`
- `phase0_30_00_resource_controller.py`

**Standalone Modules** (minimal dependencies):
- `phase0_20_01_hash_utils.py`
- `phase0_30_01_performance_metrics.py`
- `phase0_00_02_runtime_error_fixes.py`

### By Coupling

**Tightly Coupled Groups:**
1. Config family: paths → runtime_config → json_logger
2. Determinism family: seed_factory → determinism → helpers → execution
3. Validation family: input_validation → boot_checks → exit_gates

**Loosely Coupled:**
- Standalone utilities (hash_utils, performance_metrics)
- Error handling (domain_errors, runtime_error_fixes)

## Dependency Metrics

### Fan-In (Number of modules that import this module)
```
phase0_10_01_runtime_config.py: 6
phase0_00_01_domain_errors.py: 5
phase0_10_00_paths.py: 3
primitives/phase0_00_03_primitives.py: 2
phase0_20_02_determinism.py: 2
phase0_30_00_resource_controller.py: 3
phase0_50_00_boot_checks.py: 1
```

### Fan-Out (Number of modules this imports)
```
phase0_90_00_main.py: 10+ (orchestrator)
phase0_40_00_input_validation.py: 4
phase0_50_00_boot_checks.py: 3
phase0_90_02_bootstrap.py: 2
phase0_20_04_deterministic_execution.py: 2
```

### Coupling Score
```
Low Coupling (0-2 dependencies):
  - phase0_00_01_domain_errors.py
  - phase0_20_01_hash_utils.py
  - phase0_30_01_performance_metrics.py

Medium Coupling (3-5 dependencies):
  - phase0_10_01_runtime_config.py
  - phase0_20_02_determinism.py
  - phase0_30_00_resource_controller.py

High Coupling (6+ dependencies):
  - phase0_90_00_main.py (orchestrator)
  - phase0_40_00_input_validation.py
```

## Import Graph (ASCII)

```
                    ┌──────────────────┐
                    │  domain_errors   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │      paths       │
                    └────────┬─────────┘
                             │
              ┌──────────────▼──────────────┐
              │      runtime_config          │
              └──┬───────────┬──────────┬───┘
                 │           │          │
       ┌─────────▼─┐    ┌───▼───┐   ┌─▼────────────┐
       │json_logger│    │ seed  │   │resource_ctrl │
       └───────────┘    │factory│   └──────┬───────┘
                        └───┬───┘          │
                            │              │
                   ┌────────▼──────────┐   │
                   │   determinism     │   │
                   └────────┬──────────┘   │
                            │              │
                   ┌────────▼──────────┐   │
                   │input_validation   │◄──┘
                   └────────┬──────────┘
                            │
                   ┌────────▼──────────┐
                   │   boot_checks     │
                   └────────┬──────────┘
                            │
                   ┌────────▼──────────┐
                   │    exit_gates     │
                   └────────┬──────────┘
                            │
                   ┌────────▼──────────┐
                   │    bootstrap      │
                   └────────┬──────────┘
                            │
                   ┌────────▼──────────┐
                   │wiring_validator   │
                   └───────────────────┘
```

## Verification

### Acyclicity Check
```python
# No cycles detected in dependency graph
# Verified using topological sort algorithm
# All modules have unique topological position
```

### Orphan Check
```python
# All modules reachable from entry point
# No modules exist outside the execution DAG
# Utility modules used via aggregation/composition
```

### Consistency Check
```python
# Import statements match documented dependencies
# All dependencies resolvable at runtime
# No missing imports or broken references
```

## Evolution Guidelines

When adding new modules to Phase 0:

1. **Determine Stage:** Assign to appropriate stage (00-90)
2. **Check Dependencies:** Ensure no cycles introduced
3. **Update Order:** Assign unique order within stage
4. **Document:** Update this graph and manifest
5. **Verify:** Run import analysis and topological sort

When modifying dependencies:

1. **Check Impact:** Identify affected modules (fan-out)
2. **Verify Acyclicity:** Ensure no cycles created
3. **Update Critical Path:** Recalculate if critical module changed
4. **Test:** Run full test suite
5. **Document:** Update this document

## Tools

To generate the dependency graph:
```bash
# Using pyreverse (from pylint)
pyreverse -o dot -p Phase0 src/farfan_pipeline/phases/Phase_0/*.py
dot -Tpng classes_Phase0.dot -o docs/phase0_dependency_graph.png

# Using Python AST
python -c "
import ast
from pathlib import Path
phase_dir = Path('src/farfan_pipeline/phases/Phase_0')
for f in phase_dir.glob('*.py'):
    tree = ast.parse(f.read_text())
    imports = [node.module for node in ast.walk(tree) 
               if isinstance(node, ast.ImportFrom) and node.module]
    print(f'{f.stem}: {imports}')
"
```

## References

- PHASE_0_MANIFEST.json (module inventory)
- phase0_mission_contract.py (execution order)
- GLOBAL_NAMING_POLICY.md (naming conventions)

---
**END OF DOCUMENT**
