# Configuration Governance System

**IMPLEMENTATION_WAVE:** GOVERNANCE_WAVE_2024_12_07  
**WAVE_LABEL:** CONFIG_GOVERNANCE_STRICT_FOLDERIZATION

## Overview

This directory implements strict configuration governance with:
- **Folderized structure**: Calibration, questionnaire, and environment configs
- **SHA256 hash tracking**: Integrity verification via `config_hash_registry.json`
- **Timestamped backups**: Automatic backups in `.backup/` (YYYYMMDD_HHMMSS format)
- **Pre-commit hooks**: Block hardcoded calibration values in Python files

## Directory Structure

```
system/config/
├── calibration/
│   ├── intrinsic_calibration.json          # Base layer (@b) parameters
│   ├── intrinsic_calibration_rubric.json   # Canonical rubric definitions
│   ├── unit_transforms.json                # g(U) transformation functions
│   └── runtime_layers.json                 # Runtime layer scores (@chain, @q, @d, etc.)
├── questionnaire/
│   ├── questionnaire_monolith.json         # 300-question canonical monolith
│   ├── pattern_registry.json               # Reusable pattern definitions
│   ├── pattern_deprecation.json            # Deprecated patterns tracking
│   └── questionnaire_schema.json           # JSON schema for validation
├── environments/
│   ├── production.json                     # Production environment settings
│   ├── development.json                    # Development environment settings
│   └── testing.json                        # Testing environment settings
├── .backup/                                # Timestamped backups (gitignored)
├── config_hash_registry.json               # SHA256 hash tracking
├── config_manager.py                       # Configuration management API
├── initialize_registry.py                  # Registry initialization script
├── verify_config_integrity.py              # Integrity verification script
├── list_backups.py                         # Backup management utility
└── GOVERNANCE.md                           # This file
```

## Usage

### Loading Configuration

```python
from system.config.config_manager import ConfigManager

# Initialize manager
config = ConfigManager()

# Load calibration data
intrinsic = config.load_config_json('calibration/intrinsic_calibration.json')
runtime_layers = config.load_config_json('calibration/runtime_layers.json')

# Load questionnaire
questions = config.load_config_json('questionnaire/questionnaire_monolith.json')

# Load environment config
env = config.load_config_json('environments/production.json')
```

### Saving Configuration (with automatic backup)

```python
# Save with automatic backup and hash update
config.save_config_json(
    'calibration/runtime_layers.json',
    updated_data,
    create_backup=True
)
```

### Verify Integrity

```bash
# Check if any configs have been modified
python system/config/verify_config_integrity.py

# Reinitialize registry after authorized changes
python system/config/initialize_registry.py
```

### Manage Backups

```bash
# List all backups
python system/config/list_backups.py

# List backups for specific file
python system/config/list_backups.py --file calibration/runtime_layers.json

# Show backup summary
python system/config/list_backups.py --summary
```

### Restore from Backup

```python
from pathlib import Path
from system.config.config_manager import ConfigManager

config = ConfigManager()

# List backups for a file
backups = config.list_backups('calibration/runtime_layers.json')

# Restore latest backup
if backups:
    config.restore_backup(backups[0])
```

## Pre-Commit Hook

The `.git/hooks/pre-commit` script automatically blocks commits containing hardcoded calibration values.

### Blocked Patterns

- Hardcoded scores: `0.65`, `0.75`, `1.0` (in calibration context)
- Layer assignments: `@b = 0.75`, `layer_score = 0.80`
- Direct weights: `weight = 0.5`
- Magic thresholds: `threshold = 0.3`

### Exemptions

- Test files (`test_*.py`, `*_test.py`)
- Assert statements
- Lines with `# EXEMPT` comment

### Example Violation

```python
# ❌ BLOCKED by pre-commit hook
def calculate_layer_score():
    base_score = 0.65  # Hardcoded calibration value
    return base_score * adjustment

# ✓ ALLOWED - loads from config
def calculate_layer_score():
    config = ConfigManager()
    layers = config.load_config_json('calibration/runtime_layers.json')
    return layers['layers']['chain']['base_score']
```

## Backup Format

Backups use the following naming convention:

```
YYYYMMDD_HHMMSS_microseconds_<encoded_path>
```

Example:
```
20241202_143045_123456_calibration_runtime_layers.json
```

Components:
- `20241202`: Date (YYYY-MM-DD)
- `143045`: Time (HH:MM:SS)
- `123456`: Microseconds (for uniqueness)
- `calibration_runtime_layers.json`: Original path with `/` replaced by `_`

## Hash Registry

`config_hash_registry.json` tracks SHA256 hashes for integrity verification:

```json
{
  "calibration/runtime_layers.json": {
    "hash": "a1b2c3d4...",
    "last_modified": "2024-12-02T14:30:45.123456",
    "size_bytes": 2048
  }
}
```

## Best Practices

1. **Never hardcode calibration values** in Python files
2. **Always use ConfigManager** to load/save configs
3. **Run verify_config_integrity.py** before deployments
4. **Review backups** before making bulk changes
5. **Document config changes** in commit messages
6. **Use environment configs** for environment-specific settings
7. **Keep backups** for at least 90 days (configure retention policy)

## Maintenance

### Rebuild Registry

After authorized manual edits:

```bash
python system/config/initialize_registry.py
```

### Clean Old Backups

```python
from datetime import datetime, timedelta
from pathlib import Path

backup_dir = Path('system/config/.backup')
retention_days = 90
cutoff = datetime.now() - timedelta(days=retention_days)

for backup in backup_dir.glob('*'):
    if backup.is_file():
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        if mtime < cutoff:
            backup.unlink()
```

## Troubleshooting

### Pre-commit hook not running

```bash
# Make hook executable
chmod +x .git/hooks/pre-commit

# Test hook manually
.git/hooks/pre-commit
```

### Hash mismatch after valid edit

```bash
# Update registry with new hash
python system/config/initialize_registry.py
```

### Cannot find config file

```python
from system.config.config_manager import ConfigManager

config = ConfigManager()

# Check if file exists
file_info = config.get_file_info('calibration/runtime_layers.json')
if file_info:
    print(f"File hash: {file_info['hash']}")
else:
    print("File not in registry")
```

## Migration Guide

### Moving from Hardcoded Values

1. **Identify hardcoded values** in your code
2. **Add to appropriate config** (calibration/, questionnaire/, environments/)
3. **Update code** to load from ConfigManager
4. **Test** to ensure values match
5. **Commit** - pre-commit hook will verify no hardcoded values remain

Example:

```python
# Before
LAYER_SCORE = 0.65

# After
from system.config.config_manager import ConfigManager
config = ConfigManager()
runtime = config.load_config_json('calibration/runtime_layers.json')
LAYER_SCORE = runtime['layers']['chain']['base_score']
```

## References

- `config_manager.py`: Configuration management API documentation
- `CALIBRATION_INTRINSIC_POLICY.md`: Intrinsic calibration policy
- `CALIBRATION_CONFIG_MIGRATION_SUMMARY.md`: Migration history
