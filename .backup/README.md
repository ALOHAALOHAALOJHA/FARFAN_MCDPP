# Configuration Backups

**IMPLEMENTATION_WAVE:** GOVERNANCE_WAVE_2024_12_07  
**WAVE_LABEL:** CONFIG_GOVERNANCE_STRICT_FOLDERIZATION

This directory contains timestamped backups of configuration files from `system/config/`.

## Backup Format

```
YYYYMMDD_HHMMSS_microseconds_<encoded_path>
```

Example:
```
20241202_143045_123456_calibration_runtime_layers.json
```

## Automatic Backups

Backups are automatically created by `ConfigManager` when:
1. Saving a configuration file that already exists
2. Restoring from a backup
3. Initializing the hash registry

## Manual Management

```bash
# List all backups
python system/config/list_backups.py

# List backups for specific file
python system/config/list_backups.py --file calibration/runtime_layers.json

# Show backup summary
python system/config/list_backups.py --summary
```

## Retention Policy

- **Development**: 7 days
- **Testing**: 1 day  
- **Production**: 90 days

## Git Ignore

This directory is gitignored to prevent committing backup files. Only the directory structure is tracked.

## Recovery

To restore from backup:

```python
from pathlib import Path
from system.config.config_manager import ConfigManager

config = ConfigManager()
backups = config.list_backups('calibration/runtime_layers.json')

# Restore latest backup
if backups:
    restored_path = config.restore_backup(backups[0])
    print(f"Restored to: {restored_path}")
```

## Cleanup

Backups should be periodically cleaned based on retention policy. Consider implementing automated cleanup as part of CI/CD or scheduled tasks.
