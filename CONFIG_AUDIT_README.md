# Configuration Audit System

Comprehensive audit and consolidation system for calibration configuration files.

## Overview

This system provides automated tools to:

1. **Detect Hardcoded Calibration Values** - AST-based parser identifies hardcoded weights, thresholds, scores, and other calibration parameters in Python code
2. **Identify Duplicate Configurations** - Finds duplicate and legacy configuration files across the repository
3. **Archive Deprecated Files** - Safely archives legacy files with metadata and timestamps
4. **Consolidate to Canonical Structure** - Moves files to single source of truth in `system/config/`
5. **Validate Code References** - Ensures all code references use canonical configuration paths

## Architecture

### Canonical Configuration Hierarchy

```
system/config/
├── calibration/
│   ├── intrinsic_calibration.json       # PRIMARY: Method calibration scores (b_theory, b_impl, b_deploy)
│   ├── intrinsic_calibration_rubric.json # Machine-readable scoring rubric and methodology
│   ├── runtime_layers.json               # Layer maturity baselines and definitions
│   └── unit_transforms.json              # Unit transformation rules
├── questionnaire/
│   └── (questionnaire configurations)
└── executor_config.json                  # Executor runtime configuration
```

### Scripts

#### 1. `scripts/audit_calibration_config.py`

**Purpose**: AST-based audit of hardcoded calibration values

**Features**:
- Parses Python AST to detect hardcoded numeric constants
- Identifies calibration-related variable names (threshold, weight, score, etc.)
- Categorizes violations by severity (HIGH, MEDIUM, LOW)
- Generates detailed violations report with line numbers and context
- Handles syntax errors gracefully

**Usage**:
```bash
python scripts/audit_calibration_config.py
```

**Output**: `violations_audit.md`

**Detection Patterns**:
- Variable names containing: `threshold`, `weight`, `score`, `alpha`, `beta`, `prior`, `coefficient`, etc.
- Suspicious float values (0.0 < x < 1.0)
- Suspicious integer values (x > 2)
- Dictionary entries with calibration keys

**Severity Assessment**:
- **HIGH**: Critical parameters (thresholds, weights, coefficients, priors, baselines)
- **MEDIUM**: Numeric scores and ratios
- **LOW**: Other numeric values

#### 2. `scripts/consolidate_config.py`

**Purpose**: Consolidate configuration files to canonical locations

**Features**:
- Creates canonical directory structure
- Copies files to standard locations
- Detects conflicts (files exist with different content)
- Validates JSON integrity
- Supports dry-run mode

**Usage**:
```bash
# Dry run (preview changes)
python scripts/consolidate_config.py --dry-run

# Live execution
python scripts/consolidate_config.py

# Custom output path
python scripts/consolidate_config.py --output my_report.md
```

**Output**: `config_consolidation_report.md`

**Canonical Mappings**:
```python
{
    "config/intrinsic_calibration.json": 
        "system/config/calibration/intrinsic_calibration.json",
    
    "src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json": 
        "system/config/calibration/intrinsic_calibration_rubric.json",
    
    "config/json_files_ no_schemas/executor_config.json": 
        "system/config/executor_config.json",
}
```

#### 3. `scripts/validate_config_references.py`

**Purpose**: Validate that code references canonical configuration paths

**Features**:
- AST-based detection of string literals containing config paths
- Regex pattern matching for additional coverage
- Categorizes references as LEGACY, CANONICAL, or OTHER
- Provides migration guidance

**Usage**:
```bash
python scripts/validate_config_references.py
```

**Output**: `config_reference_validation.md`

**Legacy Paths** (should be updated):
- `config/intrinsic_calibration.json`
- `src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json`
- `config/json_files_ no_schemas/executor_config.json`

**Canonical Paths** (correct):
- `system/config/calibration/intrinsic_calibration.json`
- `system/config/calibration/intrinsic_calibration_rubric.json`
- `system/config/calibration/runtime_layers.json`
- `system/config/executor_config.json`

#### 4. `scripts/run_config_audit.py`

**Purpose**: Master orchestrator that runs complete audit pipeline

**Features**:
- Executes all audit steps in sequence
- Captures output and errors
- Generates unified summary report
- Supports dry-run mode

**Usage**:
```bash
# Full audit with dry-run
python scripts/run_config_audit.py --dry-run

# Full audit with actual changes
python scripts/run_config_audit.py
```

**Outputs**:
- `violations_audit.md`
- `config_consolidation_report.md`
- `config_reference_validation.md`
- `config_audit_summary.md` (unified summary)

## Workflow

### Phase 1: Audit (Current)

```bash
# Run complete audit in dry-run mode
python scripts/run_config_audit.py --dry-run
```

**Deliverables**:
1. `violations_audit.md` - List of hardcoded calibration values
2. `config_consolidation_report.md` - Configuration file analysis
3. `config_reference_validation.md` - Code reference validation
4. `config_audit_summary.md` - Unified summary

### Phase 2: Consolidation

```bash
# Execute actual consolidation (removes dry-run flag)
python scripts/run_config_audit.py
```

**Actions**:
1. Archives legacy configuration files to `.archive/legacy_configs_YYYYMMDD/`
2. Copies files to canonical `system/config/` structure
3. Creates metadata files for tracking

### Phase 3: Refactoring

**Manual Steps**:
1. Review `violations_audit.md` for hardcoded values
2. Extract hardcoded calibration values to JSON configuration files
3. Update code to load from configuration manager
4. Update imports to reference canonical paths

**Example Refactoring**:

```python
# BEFORE (hardcoded)
SEMANTIC_COHERENCE_THRESHOLD = 0.72
ENTITY_EXTRACTION_THRESHOLD = 0.55

# AFTER (configuration-driven)
from system.config.config_manager import ConfigManager

config = ConfigManager().get_config("calibration/processing_thresholds")
SEMANTIC_COHERENCE_THRESHOLD = config["semantic_coherence_threshold"]
ENTITY_EXTRACTION_THRESHOLD = config["entity_extraction_threshold"]
```

### Phase 4: Validation

```bash
# Re-run audit to verify fixes
python scripts/run_config_audit.py --dry-run

# Run integration tests
pytest tests/ -v

# Verify configuration loading
python -m farfan_pipeline.core.calibration.intrinsic_calibration_loader
```

### Phase 5: Cleanup

After validation period (e.g., 30 days):

```bash
# Remove archived files (if all systems stable)
rm -rf .archive/legacy_configs_*
```

## Archive Structure

Archived files are stored with metadata:

```
.archive/legacy_configs_20250103/
├── config/
│   └── intrinsic_calibration.json
│       └── intrinsic_calibration.json.metadata.json
└── src/
    └── farfan_pipeline/
        └── core/
            └── calibration/
                └── intrinsic_calibration_rubric.json
                    └── intrinsic_calibration_rubric.json.metadata.json
```

**Metadata Format**:
```json
{
  "original_path": "config/intrinsic_calibration.json",
  "archived_at": "2025-01-03T15:30:00.123456",
  "reason": "Superseded by system/config/calibration/",
  "hash": "sha256:a1b2c3..."
}
```

## Configuration Management Integration

### Using ConfigManager

```python
from system.config.config_manager import ConfigManager

# Initialize manager
config_mgr = ConfigManager()

# Load calibration configuration
calibration = config_mgr.get_config("calibration/intrinsic_calibration")

# Access specific method scores
method_id = "farfan_pipeline.analysis.scoring.compute_score"
if method_id in calibration:
    b_theory = calibration[method_id]["b_theory"]
    b_impl = calibration[method_id]["b_impl"]
    b_deploy = calibration[method_id]["b_deploy"]
```

### Configuration Validation

The system validates:
- JSON syntax correctness
- Required fields presence
- Schema compliance (if schemas defined)
- Hash integrity

## Violation Severity Guidelines

### HIGH Severity

Hardcoded values that directly impact analytical results:
- Threshold values for decisions
- Statistical weights and coefficients
- Prior probabilities
- Baseline scores

**Action**: MUST be moved to configuration

### MEDIUM Severity

Numeric values used in scoring or ranking:
- Normalized scores
- Ratio calculations
- Intermediate thresholds

**Action**: SHOULD be moved to configuration

### LOW Severity

Utility values with limited analytical impact:
- Initialization values (0.0, 1.0)
- Small constants (1, 2, 100)
- Formatting parameters

**Action**: MAY be left hardcoded with documentation

## Best Practices

### 1. Never Hardcode Calibration Values

```python
# ❌ BAD
def score_confidence(value):
    if value > 0.75:  # Magic number!
        return "high"
    return "low"

# ✓ GOOD
def score_confidence(value, config):
    threshold = config["confidence_threshold"]
    if value > threshold:
        return "high"
    return "low"
```

### 2. Use Configuration Manager

```python
# ❌ BAD
with open("config/intrinsic_calibration.json") as f:
    config = json.load(f)

# ✓ GOOD
from system.config.config_manager import ConfigManager
config = ConfigManager().get_config("calibration/intrinsic_calibration")
```

### 3. Document Configuration Structure

Add JSON schema or comments explaining each configuration field:

```json
{
  "_metadata": {
    "version": "2.0.0",
    "description": "Intrinsic calibration scores for all methods"
  },
  "method_id": {
    "b_theory": 0.75,  // Theoretical foundation quality (0-1)
    "b_impl": 0.82,    // Implementation quality (0-1)
    "b_deploy": 0.68   // Deployment maturity (0-1)
  }
}
```

### 4. Validate Configuration on Load

```python
def load_calibration_config():
    config = ConfigManager().get_config("calibration/intrinsic_calibration")
    
    # Validate structure
    assert "_metadata" in config
    assert "version" in config["_metadata"]
    
    # Validate score ranges
    for method_id, scores in config.items():
        if method_id.startswith("_"):
            continue
        assert 0.0 <= scores["b_theory"] <= 1.0
        assert 0.0 <= scores["b_impl"] <= 1.0
        assert 0.0 <= scores["b_deploy"] <= 1.0
    
    return config
```

## Troubleshooting

### Issue: Script fails with SyntaxError

**Cause**: Python file has syntax errors preventing AST parsing

**Solution**: Fix syntax errors first, or exclude file from audit

### Issue: Duplicate files with different content

**Cause**: Configurations diverged over time

**Solution**: 
1. Review both versions
2. Determine which is correct
3. Update references to canonical version
4. Archive/delete incorrect version

### Issue: Configuration not loading from canonical path

**Cause**: Code still references legacy paths

**Solution**: Run `validate_config_references.py` to find and update all references

## Maintenance

### Regular Audits

Schedule periodic audits to prevent configuration drift:

```bash
# Monthly audit
0 0 1 * * cd /path/to/repo && python scripts/run_config_audit.py --dry-run
```

### Version Control

- Commit all configuration changes with descriptive messages
- Tag configuration versions: `git tag config-v2.1.0`
- Document breaking changes in CHANGELOG

### Monitoring

Add monitoring for:
- Configuration load failures
- Missing configuration files
- Schema validation errors
- Unexpected configuration values

## References

- **CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md**: Calibration methodology
- **CONFIGURATION_MANAGEMENT_IMPLEMENTATION.md**: Config management architecture
- **system/config/README.md**: Configuration structure documentation

## Support

For questions or issues:
1. Review generated audit reports
2. Check existing documentation in `system/config/`
3. Examine code examples in config manager
4. Create issue with audit report attached
