# Configuration Governance Quick Reference

**IMPLEMENTATION_WAVE:** GOVERNANCE_WAVE_2024_12_07  
**WAVE_LABEL:** CONFIG_GOVERNANCE_STRICT_FOLDERIZATION

## Directory Structure

```
system/config/
├── calibration/              # Calibration parameters
│   ├── intrinsic_calibration.json
│   ├── intrinsic_calibration_rubric.json
│   ├── unit_transforms.json
│   └── runtime_layers.json
├── questionnaire/            # Questionnaire monolith
│   ├── questionnaire_monolith.json
│   └── pattern_registry.json
├── environments/             # Environment configs
│   ├── production.json
│   ├── development.json
│   └── testing.json
└── .backup/                  # Timestamped backups (gitignored)
```

## Common Tasks

### Load Configuration

```python
from system.config.config_manager import ConfigManager

config = ConfigManager()
data = config.load_config_json('calibration/runtime_layers.json')
```

### Save Configuration (with backup)

```python
config.save_config_json(
    'calibration/runtime_layers.json',
    updated_data,
    create_backup=True
)
```

### Verify Integrity

```bash
python system/config/verify_config_integrity.py
```

### Initialize/Rebuild Registry

```bash
python system/config/initialize_registry.py
```

### List Backups

```bash
python system/config/list_backups.py
python system/config/list_backups.py --file calibration/runtime_layers.json
python system/config/list_backups.py --summary
```

### Scan for Hardcoded Values

```bash
python system/config/migrate_hardcoded_values.py
python system/config/migrate_hardcoded_values.py --output report.md
```

## Pre-Commit Hook

### What It Blocks

- Hardcoded calibration scores: `0.65`, `0.75`, `1.0`
- Layer assignments: `@b = 0.75`
- Weight assignments: `weight = 0.5`
- Threshold values: `threshold = 0.3`

### Exemptions

- Test files (`test_*.py`, `*_test.py`)
- Lines with `# EXEMPT` comment
- Assert statements

### Test Hook

```bash
.git/hooks/pre-commit
```

## Configuration Files

### calibration/intrinsic_calibration.json

Base layer (@b) parameters:
- `b_theory`: Conceptual soundness (weight: 0.40)
- `b_impl`: Implementation quality (weight: 0.35)
- `b_deploy`: Operational stability (weight: 0.25)

### calibration/runtime_layers.json

Runtime layer scores:
- `@chain`: Chain of evidence (base: 0.65)
- `@q`: Data quality (base: 0.70)
- `@d`: Data density (base: 0.68)
- `@p`: Provenance (base: 0.75)
- `@C`: Coverage (base: 0.72)
- `@u`: Uncertainty (base: 0.68)
- `@m`: Mechanism (base: 0.65)

### calibration/unit_transforms.json

g(U) transformation functions:
- `identity`: g(U) = U
- `constant`: g(U) = 1.0
- `piecewise_linear`: g(U) = 2*U - 0.6 if U >= 0.3
- `sigmoidal`: g(U) = 1 - exp(-k*(U - x0))

### questionnaire/questionnaire_monolith.json

300-question analysis framework:
- Dimensions: D1-D6
- Policy Areas: PA01-PA10
- Question types: MACRO, MESO, MICRO

### environments/*.json

Environment-specific settings:
- API configuration
- Database settings
- Logging configuration
- Security settings
- Cache configuration

## Backup Format

```
YYYYMMDD_HHMMSS_microseconds_<encoded_path>
```

Example:
```
20241202_143045_123456_calibration_runtime_layers.json
```

## Hash Registry

`config_hash_registry.json` structure:

```json
{
  "calibration/runtime_layers.json": {
    "hash": "a1b2c3d4...",
    "last_modified": "2024-12-02T14:30:45.123456",
    "size_bytes": 2048
  }
}
```

## Migration Pattern

```python
# ❌ Before (hardcoded)
LAYER_SCORE = 0.65

# ✓ After (config-based)
from system.config.config_manager import ConfigManager
config = ConfigManager()
runtime = config.load_config_json('calibration/runtime_layers.json')
LAYER_SCORE = runtime['layers']['chain']['base_score']
```

## Error Recovery

### Hash mismatch after valid edit

```bash
python system/config/initialize_registry.py
```

### Restore from backup

```python
from system.config.config_manager import ConfigManager

config = ConfigManager()
backups = config.list_backups('calibration/runtime_layers.json')
config.restore_backup(backups[0])  # Restore latest
```

### Hook not running

```bash
chmod +x .git/hooks/pre-commit
.git/hooks/pre-commit  # Test manually
```

## Best Practices

1. ✓ Load all calibration values from config files
2. ✓ Create backups before bulk changes
3. ✓ Verify integrity before deployments
4. ✓ Document config changes in commits
5. ✓ Use environment configs for env-specific settings
6. ✗ Never hardcode calibration values in Python
7. ✗ Never commit .backup/ directory contents
8. ✗ Never manually edit config_hash_registry.json

## Resources

- Full documentation: `system/config/GOVERNANCE.md`
- Config manager: `system/config/config_manager.py`
- Tests: `system/config/test_governance_system.py`
