# Discovery Protocol - Section 1.1: Mandatory Inventory Acquisition

## Overview

The Discovery Protocol implements exhaustive repository scanning and inventory generation as specified in Section 1.1 of the triangulation phase requirements. This tool produces a comprehensive YAML inventory of all Phase 2, executor, orchestrator, and related components.

## Purpose

The discovery protocol serves as a mandatory prerequisite step that:

1. Maps the complete repository structure
2. Identifies all Phase 2 and executor-related files
3. Traces import dependencies across critical components
4. Detects legacy artifacts that may require refactoring
5. Produces a machine-readable inventory for downstream analysis

## Usage

### Execute Discovery Protocol

```bash
# Run from repository root
python3 scripts/discovery_protocol.py
```

### Output

The script generates `PHASE2_INVENTORY.yaml` in the repository root containing:

- **Inventory metadata**: timestamp, version, total file counts
- **File type statistics**: Python, JSON, Markdown counts
- **Command results**: Raw output from all 4 mandatory command sets
- **Categorized files**: Files organized by component (phase2, executor, carver, orchestrator, SISAS, etc.)
- **Import dependencies**: Import statements categorized by component
- **Legacy artifacts**: Detection of legacy patterns (batch_*.py, *_v2*, *_final*, *_old*)

## Four Mandatory Command Sets

### COMMAND_SET_1: Exhaustive File Discovery
```bash
git ls-files | grep -Ei 'phase. ?2|executor|carver|orchestrat|sisas|dura_lex|synchron|irrigation|contract|validator'
```
Identifies all files matching critical keywords across the repository.

### COMMAND_SET_2: Directory Structure Mapping
```bash
find . -type f \( -name '*.py' -o -name '*.json' -o -name '*.md' \) 2>/dev/null | sort
```
Maps all Python, JSON, and Markdown files in the repository.

### COMMAND_SET_3: Import Dependency Graph
```bash
grep -r '^from\|^import' src/ --include='*.py' | grep -Ei 'executor|carver|contract|sisas|orchestrat'
```
Traces import dependencies for critical components.

### COMMAND_SET_4: Legacy Artifact Detection
```bash
find . -type f \( -name 'executors.py' -o -name 'batch_*.py' -o -name '*_v2*' -o -name '*_final*' -o -name '*_old*' \) 2>/dev/null
```
Identifies potential legacy code that may need refactoring.

## Inventory Structure

The generated `PHASE2_INVENTORY.yaml` follows this structure:

```yaml
inventory_timestamp: "2025-12-18T20:14:39.491770+00:00"
inventory_version: "1.0.0"
total_files_scanned: 1453

file_type_counts:
  python_files: 490
  json_files: 440
  markdown_files: 523

command_results:
  command_set_1_exhaustive_discovery:
    count: 690
    files: [...]
  command_set_2_directory_mapping:
    count: 1453
    files: [...]
  command_set_3_import_dependencies:
    count: 428
    imports: [...]
  command_set_4_legacy_artifacts:
    count: 4
    files: [...]

categorized_files:
  phase2_files:
    count: 358
    files: [...]
  executor_files:
    count: 350
    files: [...]
  carver_files:
    count: 4
    files: [...]
  orchestrator_files:
    count: 68
    files: [...]
  sisas_files:
    count: 28
    files: [...]
  dura_lex_files:
    count: 63
    files: [...]
  synchronization_files:
    count: 15
    files: [...]
  irrigation_files:
    count: 40
    files: [...]
  contract_files:
    count: 526
    files: [...]
  validator_files:
    count: 26
    files: [...]

import_dependencies:
  executor_imports:
    count: 157
    imports: [...]
  carver_imports:
    count: 8
    imports: [...]
  contract_imports:
    count: 84
    imports: [...]
  sisas_imports:
    count: 38
    imports: [...]
  orchestrator_imports:
    count: 141
    imports: [...]

legacy_artifacts:
  legacy_executors_py:
    count: 0
    files: []
  legacy_batch_py:
    count: 2
    files: [batch_executor.py, batch_generate_all_configs.py]
  legacy_v2_files:
    count: 2
    files: [Rubrica_CQVR_v2.md, api_v2.py]
  legacy_final_files:
    count: 0
    files: []
  legacy_old_files:
    count: 0
    files: []
```

## Implementation Details

### Technology Stack

- **Language**: Python 3.12+
- **Dependencies**: PyYAML (included in project dependencies)
- **Execution**: subprocess for shell command execution
- **Data structures**: dataclasses for type-safe inventory representation

### Key Features

1. **Deterministic execution**: Commands always produce the same output for the same repository state
2. **Comprehensive categorization**: Files automatically categorized by multiple criteria
3. **Structured output**: Machine-readable YAML format for downstream processing
4. **Error handling**: Graceful handling of missing files or command failures
5. **Type safety**: Strong typing throughout with dataclasses and type hints

### Design Principles

The discovery protocol adheres to F.A.R.F.A.N principles:

- **Deterministic**: Same repository state produces identical inventory
- **Traceable**: Complete provenance of all discovered artifacts
- **Structured**: Formal schema for inventory output
- **Non-destructive**: Read-only operations, no repository modifications
- **Auditable**: Complete command history and results preserved

## Maintenance

### When to Run

Execute the discovery protocol:

1. **Before refactoring**: Establish baseline of repository structure
2. **After major changes**: Verify impact of structural changes
3. **During audits**: Document current state for compliance
4. **Periodic reviews**: Track evolution of repository over time

### Updating the Protocol

When modifying the discovery protocol:

1. Update `scripts/discovery_protocol.py` with new command sets
2. Add new categorization logic if needed
3. Update inventory schema if new fields are added
4. Regenerate `PHASE2_INVENTORY.yaml` to verify changes
5. Update this README with new information

## Troubleshooting

### Common Issues

**Issue**: `git ls-files` returns empty results
- **Cause**: Not running from git repository root
- **Solution**: Ensure script is executed from repository root or adjust `repo_root` path

**Issue**: Permission denied errors
- **Cause**: Script lacks execute permissions
- **Solution**: `chmod +x scripts/discovery_protocol.py`

**Issue**: Missing PyYAML module
- **Cause**: Dependencies not installed
- **Solution**: `pip install -e .` from repository root

**Issue**: Inventory counts seem incorrect
- **Cause**: Repository state changed since last run
- **Solution**: Re-run discovery protocol to get current state

## Integration

The discovery protocol integrates with F.A.R.F.A.N's broader infrastructure:

- **Phase 0 (Validation)**: Inventory used for pre-flight checks
- **Orchestrator**: Import graph informs module loading order
- **Testing**: Legacy artifact detection guides test prioritization
- **Documentation**: Inventory serves as reference for architectural decisions

## References

- **Issue**: Section 1.1 MANDATORY INVENTORY ACQUISITION
- **Related**: Phase 2 Executor Architecture
- **See also**: ORCHESTRATION_INTEGRATION_AUDIT.md, EXECUTOR_METHOD_AUDIT_REPORT.md
