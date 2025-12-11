# COHORT 2024 Calibration & Parametrization System - Index

## Quick Start
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - API cheat sheet
- **Usage Examples**: [USAGE_EXAMPLES.py](USAGE_EXAMPLES.py) - Runnable examples
- **Full Documentation**: [README.md](README.md) - Complete guide
- **Migration Summary**: [../COHORT_2024_MIGRATION_SUMMARY.md](../COHORT_2024_MIGRATION_SUMMARY.md) - Implementation details

## Core Files

### Audit & Metadata
- `COHORT_MANIFEST.json` - Complete migration manifest with audit trail
  - 23 calibration files tracked
  - 4 parametrization files tracked
  - Original → New path mappings
  - Cohort metadata for each file

### Structural Audit Tools
- `master_structural_audit.py` - **Complete end-to-end audit orchestration**
  - Phase 1: Initial structural audit
  - Phase 2: File reorganization
  - Phase 3: Legacy cleanup
  - Phase 4: Final verification
- `structural_audit.py` - Comprehensive structure verification
  - Verify all required files present
  - Check COHORT_2024 prefix compliance
  - Detect legacy and duplicate files
  - Generate detailed compliance report
- `cleanup_legacy_files.py` - Legacy file deletion utility
  - Remove unlabeled configuration files
  - Delete duplicate legacy versions
  - Preserve utility scripts
- `reorganize_files.py` - File reorganization and creation
  - Create missing required files
  - Validate directory structure
  - Generate configurations from data
- `STRUCTURAL_GOVERNANCE.md` - **Structural governance documentation**
- `AUDIT_QUICKSTART.md` - **Quick start guide for audits**

### Comprehensive Calibration Audit Tools (NEW)
- `run_complete_audit.py` - **Master audit runner (ONE COMMAND)**
  - Executes all audits and generates master report
  - Identifies critical gaps between claims and implementation
  - Produces concrete file paths and line numbers for findings
  - Exit codes: 0=compliant, 1=non-compliant, 2=error
- `comprehensive_calibration_audit.py` - **Comprehensive calibration audit**
  - Canonical Method Inventory (1995+ methods with calibration status)
  - Parametrized Method Inventory (executor parameters)
  - Calibration Completeness Matrix (8 layers × all methods)
  - Verification Report (gaps, missing evaluators, stubs)
- `layer_implementation_verifier.py` - **Layer evaluator verification**
  - Deep verification of all 8 layer implementations
  - AST-based method signature extraction
  - Stub detection (NotImplementedError, TODO, return 0.5)
  - Production logic verification
  - Quality scoring (0-1 scale)
- `hardcoded_parameter_scanner.py` - **Parameter compliance scanner**
  - AST-based hardcoded parameter detection
  - File:line citations for all violations
  - Severity classification (critical/high/medium/low)
  - Suggested fixes for each violation
  - Compliance percentage calculation
- `COMPREHENSIVE_AUDIT_README.md` - **Complete audit documentation**
- `AUDIT_QUICK_REFERENCE.md` - **Quick reference guide**

### Loaders & Adapters
- `cohort_loader.py` - `CohortLoader` class for configuration loading
- `import_adapters.py` - `ConfigPathAdapter` for backward compatibility
- `__init__.py` - Public API (get_calibration_config, get_parametrization_config)

### Migration Tools
- `migrate_cohort_2024.py` - Main migration script with metadata embedding
- `batch_migrate.py` - Batch migration utility

### Documentation
- `README.md` - Full documentation
- `QUICK_REFERENCE.md` - API quick reference
- `USAGE_EXAMPLES.py` - Comprehensive usage examples
- `calibration/CONTEXTUAL_LAYERS_README.md` - Contextual layers (@q, @d, @p) documentation
- `INDEX.md` - This file

## Calibration Files (23 total)

### Configuration Files (JSON)
1. `COHORT_2024_intrinsic_calibration.json` - Base layer (@b) parameters
   - Theory/Impl/Deploy components
   - Role requirements
   - Weight specifications

2. `COHORT_2024_intrinsic_calibration_rubric.json` - Canonical rubric
   - Exact formulas (b_theory, b_impl, b_deploy)
   - Q1/Q2/Q3 decision automaton
   - Exclusion criteria

3. `COHORT_2024_questionnaire_monolith.json` - 300-question structure
   - Dimensions: D1-D6 (INSUMOS → CAUSALIDAD)
   - Policy Areas: PA01-PA10
   - Question blocks and patterns

4. `COHORT_2024_method_compatibility.json` - Method compatibility scores
   - Question compatibility
   - Dimension alignment
   - Policy area fitness

5. `COHORT_2024_fusion_weights.json` - Fusion specification
   - Linear weights (a_ℓ)
   - Interaction weights (a_ℓk)
   - Role-specific parameters

6. `COHORT_2024_layer_requirements.json` - **Layer requirements and dependencies (NEW)**
   - Layer dependencies (@b → @chain → @C, etc.)
   - Required methods per layer
   - Interaction pairs and weights
   - Validation rules
   - Fusion formula specification

7. `COHORT_2024_canonical_method_inventory.json` - Method inventory
   - ~2000 methods
   - Executor catalog
   - Role assignments

### Implementation Files (Python)
8. `COHORT_2024_calibration_orchestrator.py` - **Calibration orchestrator (NEW)**
9. `COHORT_2024_calibration_orchestrator_example.py` - **Orchestrator usage examples (NEW)**
10. `COHORT_2024_layer_assignment.py` - Layer requirements and Choquet weights
11. `COHORT_2024_layer_coexistence.py` - Layer coexistence validation
12. `COHORT_2024_layer_computers.py` - Layer score computations
13. `COHORT_2024_layer_influence_model.py` - Layer influence modeling
14. `COHORT_2024_chain_layer.py` - @chain evaluator
15. `COHORT_2024_congruence_layer.py` - Congruence evaluator
16. `COHORT_2024_meta_layer.py` - @m evaluator (→ src/orchestration/meta_layer.py)
17. `COHORT_2024_unit_layer.py` - @u evaluator (→ src/orchestration/unit_layer.py) ✓ IMPLEMENTED
18. `COHORT_2024_contextual_layers.py` - **Contextual layer evaluators (@q, @d, @p)**
19. `COHORT_2024_question_layer.py` - @q evaluator (reference stub)
20. `COHORT_2024_dimension_layer.py` - @d evaluator (reference stub)
21. `COHORT_2024_policy_layer.py` - @p evaluator (reference stub)
22. `COHORT_2024_intrinsic_scoring.py` - Scoring formulas
23. `COHORT_2024_intrinsic_calibration_loader.py` - Config loader utilities

## Parametrization Files (4 total)

### Configuration Files (JSON)
1. `COHORT_2024_runtime_layers.json` - Runtime layer parameters
   - Chain/Quality/Density/Provenance/Coverage/Uncertainty/Mechanism
   - Base scores and factors

2. `COHORT_2024_executor_config.json` - Executor configuration
   - Default settings
   - Resource limits

### Implementation Files (Python)
3. `COHORT_2024_executor_config.py` - ExecutorConfig dataclass
   - max_tokens, temperature, timeout_s, retry, seed
   - Type validation

4. `COHORT_2024_executor_profiler.py` - Performance profiling
   - Executor metrics
   - Method dispensary analytics
   - Bottleneck detection

## Layer System Reference

### 8-Layer Calibration System
- **@b** - Code quality (base theory, impl, deploy)
- **@chain** - Method wiring/orchestration
- **@q** - Question appropriateness
- **@d** - Dimension alignment
- **@p** - Policy area fit
- **@C** - Contract compliance
- **@u** - Document quality
- **@m** - Governance maturity

### Role Requirements
- **SCORE_Q**: All 8 layers
- **INGEST_PDM**: @b, @chain, @u, @m
- **STRUCTURE**: @b, @chain, @u, @m
- **EXTRACT**: @b, @chain, @u, @m
- **AGGREGATE**: @b, @chain, @u, @m
- **REPORT**: @b, @chain, @u, @m
- **META_TOOL**: @b, @chain, @u, @m
- **TRANSFORM**: @b, @chain, @u, @m

## Original → COHORT_2024 Mappings

### Calibration
```
system/config/calibration/intrinsic_calibration.json
  → calibration/COHORT_2024_intrinsic_calibration.json

system/config/calibration/intrinsic_calibration_rubric.json
  → calibration/COHORT_2024_intrinsic_calibration_rubric.json

system/config/questionnaire/questionnaire_monolith.json
  → calibration/COHORT_2024_questionnaire_monolith.json

config/json_files_ no_schemas/method_compatibility.json
  → calibration/COHORT_2024_method_compatibility.json

config/json_files_ no_schemas/fusion_specification.json
  → calibration/COHORT_2024_fusion_weights.json

scripts/inventory/canonical_method_inventory.json
  → calibration/COHORT_2024_canonical_method_inventory.json

src/farfan_pipeline/core/calibration/*.py
  → calibration/COHORT_2024_*.py
```

### Parametrization
```
system/config/calibration/runtime_layers.json
  → parametrization/COHORT_2024_runtime_layers.json

config/json_files_ no_schemas/executor_config.json
  → parametrization/COHORT_2024_executor_config.json

src/farfan_pipeline/core/orchestrator/executor_config.py
  → parametrization/COHORT_2024_executor_config.py

src/farfan_pipeline/core/orchestrator/executor_profiler.py
  → parametrization/COHORT_2024_executor_profiler.py
```

## API Reference

### Load Configurations
```python
from calibration_parametrization_system import (
    get_calibration_config,        # Load calibration config
    get_parametrization_config,    # Load parametrization config
    get_cohort_metadata,            # Get cohort metadata
    list_available_configs,         # List all configs
    CohortLoader,                   # Advanced loader class
)
```

### Backward Compatibility
```python
from calibration_parametrization_system.import_adapters import ConfigPathAdapter

# Automatically redirect old paths to COHORT_2024
config = ConfigPathAdapter.load_config("system/config/calibration/intrinsic_calibration.json")
```

## Metadata Structure

All COHORT_2024 files include:
```json
{
  "_cohort_metadata": {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12"
  }
}
```

## Statistics

- **Total Files**: 35 (23 calibration + 4 parametrization + 8 audit tools)
- **JSON Files**: 10 (7 calibration + 2 parametrization + 1 manifest)
- **Python Files**: 25 (16 calibration + 1 parametrization + 8 tools)
- **Documentation Files**: 8 (README, INDEX, QUICK_REFERENCE, STRUCTURAL_GOVERNANCE, AUDIT_QUICKSTART, COMPREHENSIVE_AUDIT_README, AUDIT_QUICK_REFERENCE, USAGE_EXAMPLES)
- **Structural Audit Tools**: 4 (master_structural_audit, structural_audit, cleanup_legacy_files, reorganize_files)
- **Calibration Audit Tools**: 4 (run_complete_audit, comprehensive_calibration_audit, layer_implementation_verifier, hardcoded_parameter_scanner)
- **Migration Tools**: 2 (migrate_cohort_2024, batch_migrate)
- **Loader/Adapter Files**: 3 (cohort_loader, import_adapters, __init__)

## Future Cohorts

When creating COHORT_2025:
1. Create new `calibration_parametrization_system_2025/` directory
2. Copy this structure
3. Update prefixes: `COHORT_2024_` → `COHORT_2025_`
4. Update metadata: cohort_id, wave_version, creation_date
5. Preserve `calibration_parametrization_system/` as-is

## Quick Start Commands

### Run Comprehensive Calibration Audit (ONE COMMAND)
```bash
# Complete system audit - generates all inventories and reports
python run_complete_audit.py
```

### View Audit Results
```bash
# Human-readable summary
cat artifacts/audit_reports/LATEST_AUDIT_SUMMARY.txt

# Full JSON report
cat artifacts/audit_reports/MASTER_AUDIT_REPORT_*.json | jq '.'
```

### Run Individual Audits
```bash
# Method inventory and completeness matrix
python comprehensive_calibration_audit.py

# Layer implementation verification
python layer_implementation_verifier.py

# Hardcoded parameter scan
python hardcoded_parameter_scanner.py
```

### Run Complete Structural Audit
```bash
# Preview (dry run)
python master_structural_audit.py

# Execute (apply changes)
python master_structural_audit.py --execute
```

### Verify Compliance
```bash
python structural_audit.py
```

### Clean Legacy Files
```bash
python cleanup_legacy_files.py --execute
```

## Support

- **Calibration Audit**: See `COMPREHENSIVE_AUDIT_README.md` for complete documentation
- **Quick Audit Reference**: See `AUDIT_QUICK_REFERENCE.md` for one-page guide
- **Structural Audit**: See `AUDIT_QUICKSTART.md` for quick start guide
- **Governance Policy**: See `STRUCTURAL_GOVERNANCE.md` for detailed policies
- **Issues**: Check COHORT_MANIFEST.json for original file paths
- **Migration**: Run `batch_migrate.py` to regenerate files
- **Testing**: Run `USAGE_EXAMPLES.py` to validate system
- **Documentation**: See README.md for complete guide

---

*COHORT 2024 - Strict wave separation with auditable migration trails and comprehensive structural governance*
