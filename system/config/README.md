# Configuration System

This directory contains the configuration management system with strict separation between **calibration** (WHAT quality we measure) and **parametrization** (HOW we execute).

## Directory Structure

```
system/config/
├── calibration/              # Calibration domain (WHAT)
│   ├── intrinsic_calibration.json
│   └── intrinsic_calibration_rubric.json
├── questionnaire/            # Q/D/P alignment (WHAT)
│   └── questionnaire_monolith.json
├── environments/             # Parametrization domain (HOW)
│   ├── development.json
│   ├── staging.json
│   ├── production.json
│   └── README.md
├── .backup/                  # Timestamped backups
├── config_hash_registry.json # SHA256 hash tracking
├── config_manager.py         # Configuration management API
├── config_cli.py            # CLI for config operations
└── README.md                # This file
```

## Core Concepts

### Calibration Domain (WHAT)

**Purpose**: Define intrinsic quality characteristics that are stable across deployments

**Location**: `calibration/`, `questionnaire/`

**Contains**:
- Base quality scores: `b_theory`, `b_impl`, `b_deploy`
- Fusion weights: `a_ℓ`, `a_ℓk`
- Q/D/P alignment matrices
- Scoring modalities

**Governance**: Domain experts, peer review required, quarterly updates

**See**: 
- `calibration/` directory
- `CALIBRATION_VS_PARAMETRIZATION.md` (root)

### Parametrization Domain (HOW)

**Purpose**: Define runtime execution parameters that control execution behavior

**Location**: `environments/`

**Contains**:
- Execution timeouts: `timeout_s`
- Retry attempts: `retry`
- LLM parameters: `max_tokens`, `temperature`
- Resource limits

**Governance**: Operations team, no peer review, as-needed updates

**See**:
- `environments/` directory
- `environments/README.md`

## Configuration Management

### Using ConfigManager

```python
from system.config.config_manager import ConfigManager

# Initialize
manager = ConfigManager()

# Save with automatic backup and hash tracking
manager.save_config_json(
    "environments/production.json",
    {"executor": {"timeout_s": 120.0}},
    create_backup=True
)

# Load configuration
data = manager.load_config_json("environments/production.json")

# Verify hash
is_valid = manager.verify_hash("environments/production.json")

# List backups
backups = manager.list_backups("environments/production.json")

# Restore from backup
manager.restore_backup(backups[0])
```

### Using CLI

```bash
# Save configuration
python system/config/config_cli.py save environments/production.json \
    --data '{"executor": {"timeout_s": 120.0}}'

# Load configuration
python system/config/config_cli.py load environments/production.json --json

# Verify hash
python system/config/config_cli.py verify environments/production.json

# List backups
python system/config/config_cli.py backups environments/production.json

# Restore from backup
python system/config/config_cli.py restore .backup/20250110_143000_*.json

# Show registry
python system/config/config_cli.py registry

# Rebuild registry
python system/config/config_cli.py rebuild
```

## Loading Parameters

### ExecutorConfig with Hierarchy

```python
from farfan_pipeline.core.orchestrator import load_executor_config

# Load with default hierarchy: CLI > ENV > file > defaults
config = load_executor_config(env="production")

# Load with CLI overrides
config = load_executor_config(
    env="staging",
    cli_overrides={"timeout_s": 120.0, "retry": 5}
)
```

### Loading Hierarchy

```
1. CLI Arguments         (highest)  --timeout-s=120
2. Environment Variables            FARFAN_TIMEOUT_S=120
3. Environment File                 environments/{env}.json
4. Conservative Defaults (lowest)   CONSERVATIVE_CONFIG
```

## Verification

### Verify Boundary Compliance

```bash
# Check that calibration and parametrization are properly separated
python scripts/verify_calibration_parametrization_boundary.py
```

**Checks**:
- ✓ Calibration files contain NO runtime parameters
- ✓ ExecutorConfig contains NO quality scores  
- ✓ Environment files contain ONLY runtime parameters
- ✓ No crossover between domains

### Manual Checks

```bash
# Calibration should have no runtime params
grep -r "timeout_s\|retry\|max_tokens" calibration/ questionnaire/
# Expected: no matches

# Environment should have no quality params
grep -r "b_theory\|fusion_weights" environments/
# Expected: no matches
```

## Hash Registry

The system maintains SHA256 hashes of all configuration files for integrity verification.

**Registry Location**: `config_hash_registry.json`

**Structure**:
```json
{
  "calibration/intrinsic_calibration.json": {
    "hash": "abc123...",
    "last_modified": "2025-01-10T12:00:00",
    "size_bytes": 1024
  }
}
```

## Backup System

Automatic timestamped backups are created before any modification.

**Backup Location**: `.backup/`

**Naming Convention**: `YYYYMMDD_HHMMSS_MICROSECONDS_path_to_file.json`

**Example**: `20250110_143025_123456_environments_production.json`

## Governance

### Calibration Changes

1. Propose change with methodological justification
2. Peer review by domain experts
3. Update calibration file
4. Generate SHA256 hash
5. Create backup
6. Update CHANGELOG

**Approval**: Domain expert sign-off required

### Parametrization Changes

1. Update environment file
2. Test in dev/staging
3. Deploy to production
4. Monitor

**Approval**: Operations team discretion

## Environment Characteristics

| Environment | Purpose | Timeout | Retry | Workers |
|-------------|---------|---------|-------|---------|
| development | Fast iteration | 60s | 2 | 2 |
| staging | QA validation | 180s | 4 | 4 |
| production | Reliable execution | 300s | 5 | 8 |

## Quick Commands

```bash
# Load production config
python scripts/load_executor_config.py --env production

# Load with overrides
python scripts/load_executor_config.py --env staging --timeout-s 120

# Show hierarchy
python scripts/load_executor_config.py --env production --show-hierarchy

# Verify boundary
python scripts/verify_calibration_parametrization_boundary.py

# Examples
python scripts/example_calibration_vs_parametrization.py
python scripts/example_usage_with_separation.py
```

## Documentation

### Complete Documentation
- **`CALIBRATION_VS_PARAMETRIZATION.md`** (root) - Complete specification (~600 lines)
- **`CALIBRATION_VS_PARAMETRIZATION_QUICK_REFERENCE.md`** (root) - Quick reference
- **`CALIBRATION_PARAMETRIZATION_IMPLEMENTATION_SUMMARY.md`** (root) - Implementation summary
- **`environments/README.md`** - Environment configuration guide

### Code Documentation
- `config_manager.py` - Configuration management API
- `config_cli.py` - CLI tool
- `src/farfan_pipeline/core/orchestrator/parameter_loader.py` - Parameter loading
- `src/farfan_pipeline/core/orchestrator/executor_config.py` - ExecutorConfig schema

### Scripts
- `scripts/verify_calibration_parametrization_boundary.py` - Verification
- `scripts/load_executor_config.py` - Config loading utility
- `scripts/example_calibration_vs_parametrization.py` - Comprehensive demo
- `scripts/example_usage_with_separation.py` - Practical usage

## File Inventory

### Calibration Files (WHAT)
| File | Purpose | Change Frequency |
|------|---------|------------------|
| `calibration/intrinsic_calibration.json` | Base quality scores | Quarterly |
| `calibration/intrinsic_calibration_rubric.json` | Quality rubrics | Annually |
| `questionnaire/questionnaire_monolith.json` | Q/D/P alignment | Semi-annually |
| (external) `config/json_files_ no_schemas/fusion_specification.json` | Fusion weights | Quarterly |

### Parametrization Files (HOW)
| File | Purpose | Change Frequency |
|------|---------|------------------|
| `environments/development.json` | Dev runtime config | As needed |
| `environments/staging.json` | Staging runtime config | As needed |
| `environments/production.json` | Production runtime config | As needed |

### Management Files
| File | Purpose |
|------|---------|
| `config_hash_registry.json` | SHA256 hash tracking |
| `config_manager.py` | Configuration management API |
| `config_cli.py` | CLI tool |
| `.backup/*` | Timestamped backups |

## See Also

- `README.md` (repository root) - Project overview
- `AGENTS.md` (repository root) - Agent development guide
- `ARCHITECTURE_DIAGRAM.md` (repository root) - System architecture

## Summary

This configuration system provides:
- ✓ **Separation**: Clear boundary between WHAT and HOW
- ✓ **Integrity**: SHA256 hash tracking and verification
- ✓ **Safety**: Automatic backups before modifications
- ✓ **Flexibility**: Hierarchical parameter loading
- ✓ **Governance**: Different processes for different domains
- ✓ **Traceability**: Complete audit trail
- ✓ **Validation**: Automated boundary compliance checking

**Golden Rule**: If it affects WHAT quality we measure → Calibration. If it affects HOW we execute → Parametrization.
