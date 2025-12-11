# Hardcoded Parameter Audit System

## Overview

The Hardcoded Parameter Audit System is a comprehensive AST-based scanner that detects hardcoded calibration values and parametrization values across the entire F.A.R.F.A.N codebase, cross-references them against COHORT_2024 configuration files, and generates detailed violation reports with certification status.

## Components

### 1. `hardcoded_parameter_scanner.py`

**Purpose:** Main AST-based scanner for detecting hardcoded parameters.

**Features:**
- Traverses all Python files in `src/`
- Detects hardcoded numerical values in assignments, function calls, and dictionaries
- Cross-references values against COHORT_2024 configuration registry
- Categorizes violations by severity (CRITICAL, HIGH, MEDIUM, LOW)
- Generates detailed Markdown and JSON reports

**Detection Categories:**

| Category | Examples | Severity | Config Source |
|----------|----------|----------|---------------|
| Calibration Weights | `weight = 0.35`, `weights = {"b_theory": 0.40}` | CRITICAL | `COHORT_2024_intrinsic_calibration.json`, `COHORT_2024_fusion_weights.json` |
| Calibration Scores | `base_score = 0.65`, `min_score = 0.7` | CRITICAL | `COHORT_2024_intrinsic_calibration.json`, `COHORT_2024_runtime_layers.json` |
| Thresholds | `threshold = 0.85`, `min_threshold = 0.55` | HIGH | `COHORT_2024_intrinsic_calibration.json` |
| Timeout Values | `timeout = 300`, `timeout_seconds = 60` | MEDIUM | `COHORT_2024_executor_config.json` or env vars |
| Retry Counts | `max_retries = 3`, `retry_limit = 5` | MEDIUM | `COHORT_2024_executor_config.json` |
| LLM Parameters | `temperature = 0.7`, `max_tokens = 1000` | MEDIUM | `COHORT_2024_executor_config.json` |

### 2. `executor_parameter_validator.py`

**Purpose:** Specialized validator for executor classes to ensure parameters are loaded from configuration.

**Features:**
- Identifies executor classes via naming patterns and inheritance
- Validates that runtime parameters are loaded from `ExecutorConfig` or `os.getenv()`
- Detects hardcoded timeout, retry, and concurrency values
- Generates executor-specific violation reports

**Validation Rules:**
- ✅ Correct: `self.timeout = config.get('timeout', 300)`
- ✅ Correct: `self.timeout = os.getenv('TIMEOUT_SECONDS', '300')`
- ❌ Violation: `self.timeout = 300`

### 3. `run_parameter_audit.py`

**Purpose:** Orchestrates complete audit process and generates unified certification report.

**Features:**
- Runs general parameter scan
- Runs executor-specific validation
- Generates unified certification summary
- Provides remediation guidance
- Returns exit code 0 (pass) or 1 (fail) for CI/CD integration

## Usage

### Quick Start

```bash
# Run complete audit with default settings
python src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/run_parameter_audit.py

# Run with verbose logging
python run_parameter_audit.py --verbose

# Specify custom output directory
python run_parameter_audit.py --output-dir custom/reports/

# Skip executor validation (faster scan)
python run_parameter_audit.py --no-executor-check
```

### Individual Components

```bash
# Run only parameter scanner
python hardcoded_parameter_scanner.py

# Run only executor validator
python executor_parameter_validator.py
```

### Programmatic Usage

```python
from pathlib import Path
from hardcoded_parameter_scanner import run_audit
from executor_parameter_validator import validate_executors

# Run parameter audit
src_path = Path("src")
config_path = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization")
output_dir = Path("artifacts/audit_reports")

stats = run_audit(src_path, config_path, output_dir)

# Run executor validation
executor_violations = validate_executors(src_path, output_dir / "executor_report.md")

# Check certification status
if stats.critical_violations == 0 and executor_violations == 0:
    print("✅ CERTIFICATION PASSED")
else:
    print("❌ CERTIFICATION FAILED")
```

## Generated Reports

### 1. `violations_audit_report.md`

Comprehensive Markdown report with:
- Executive summary with statistics
- Violations grouped by severity (CRITICAL, HIGH, MEDIUM, LOW)
- For each violation:
  - File path and line number
  - Variable name and hardcoded value
  - Expected configuration source
  - Source code context
  - Recommended remediation action
- Certification requirements and next steps

### 2. `violations_audit_report.json`

Machine-readable JSON report with:
- Metadata (timestamp, scanner version)
- Audit statistics
- Complete violation list with all details
- Certification status

### 3. `executor_parameter_validation.md`

Executor-specific report with:
- Violations grouped by executor class
- Hardcoded parameter details
- Recommendations for each violation
- Best practice examples

### 4. `CERTIFICATION_SUMMARY.md`

Unified certification report with:
- Overall certification status (PASS/FAIL)
- Aggregate metrics across all audits
- Violation breakdown by severity
- Remediation guidance prioritized by impact
- References to detailed reports

## Exclusion Rules

The scanner automatically excludes:

- Test files (`test_*.py`, `*_test.py`, `tests/`)
- Example files (`example*.py`, `examples/`)
- COHORT_2024 configuration modules themselves
- Python cache directories (`__pycache__`, `*.pyc`)
- Git directories (`.git/`)

This prevents false positives from test fixtures and configuration definitions.

## Certification Criteria

### Passing Requirements

✅ **PASS**: Zero CRITICAL violations

- All calibration weights must be in `COHORT_2024_fusion_weights.json` or `COHORT_2024_intrinsic_calibration.json`
- All calibration scores must be in `COHORT_2024_intrinsic_calibration.json` or `COHORT_2024_runtime_layers.json`
- All executors must load parameters from `ExecutorConfig` or environment variables

### Advisory Requirements

- HIGH violations (thresholds/gates) should be addressed
- MEDIUM violations (runtime parameters) are recommended to fix
- LOW violations are optional improvements

## Configuration Registry

The scanner recognizes these COHORT_2024 configuration files:

### Calibration Files

1. **`COHORT_2024_intrinsic_calibration.json`**
   - Base layer weights (`@b`)
   - Component weights (`b_theory`, `b_impl`, `b_deploy`)
   - Subcomponent weights
   - Thresholds for scoring
   - Score mappings
   - Role requirements

2. **`COHORT_2024_fusion_weights.json`**
   - Linear weights (`a_ℓ`) per role
   - Interaction weights (`a_ℓk`) per role
   - Fusion formula parameters

3. **`COHORT_2024_method_compatibility.json`**
   - Method-to-question compatibility scores
   - Method-to-dimension compatibility scores
   - Method-to-policy compatibility scores

4. **`COHORT_2024_runtime_layers.json`**
   - Runtime layer base scores
   - Layer-specific factors and bonuses
   - Position thresholds
   - Dimension bonuses

### Parametrization Files

1. **`COHORT_2024_executor_config.json`**
   - Timeout values
   - Concurrency limits
   - Resource limits
   - Log levels

2. **Environment Variables**
   - Loaded via `os.getenv()` or `ExecutorConfig`
   - Example: `TIMEOUT_SECONDS`, `MAX_RETRIES`

## Remediation Workflow

### For CRITICAL Violations (Calibration Values)

1. **Identify** the hardcoded value in `violations_audit_report.md`
2. **Determine** appropriate COHORT_2024 configuration file:
   - Weights → `COHORT_2024_fusion_weights.json` or `COHORT_2024_intrinsic_calibration.json`
   - Scores → `COHORT_2024_intrinsic_calibration.json` or `COHORT_2024_runtime_layers.json`
3. **Add** the value to configuration with proper metadata
4. **Refactor** code to load via:
   ```python
   from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration_orchestrator import CalibrationOrchestrator
   
   orchestrator = CalibrationOrchestrator()
   score = orchestrator.get_intrinsic_score(method_id)
   ```
5. **Re-run** audit to verify

### For HIGH Violations (Thresholds)

1. **Review** threshold usage in context
2. **Add** to `COHORT_2024_intrinsic_calibration.json` under appropriate component
3. **Load** via configuration loader:
   ```python
   from farfan_pipeline.core.calibration.parameter_loader import get_parameter_loader
   
   loader = get_parameter_loader()
   threshold = loader.get("component.subcomponent.threshold", default=0.7)
   ```
4. **Re-run** audit to verify

### For MEDIUM Violations (Runtime Parameters)

1. **Identify** executor or method using hardcoded parameter
2. **Update** `COHORT_2024_executor_config.json` or use environment variable
3. **Refactor** to load from config:
   ```python
   from canonic_phases.Phase_two.executor_config import ExecutorConfig
   
   config = ExecutorConfig.load()
   timeout = config.get('timeout', 300)
   ```
4. **Re-run** audit to verify

### For Executor Violations

1. **Review** `executor_parameter_validation.md`
2. **Update** executor `__init__` to accept `ExecutorConfig`:
   ```python
   class MyExecutor(BaseExecutor):
       def __init__(self, config: ExecutorConfig):
           super().__init__(config)
           self.timeout = config.get('timeout', 300)
           self.max_retries = config.get('max_retries', 3)
   ```
3. **Update** `COHORT_2024_executor_config.json` with values
4. **Re-run** audit to verify

## Integration with CI/CD

### Exit Codes

- `0`: Certification PASSED (zero critical violations)
- `1`: Certification FAILED (critical violations exist)

### Example CI Pipeline

```yaml
# .github/workflows/parameter-audit.yml
name: Parameter Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -e .
      - name: Run parameter audit
        run: |
          python src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/run_parameter_audit.py
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: audit-reports
          path: artifacts/audit_reports/
```

## Performance

**Typical Performance:**
- ~50-100 files/second on modern hardware
- Full codebase scan (~200 files): ~5-10 seconds
- Memory usage: <200 MB for typical codebases

**Optimization Tips:**
- Use `--no-executor-check` for faster scans during development
- Run full audit before commits or in CI/CD
- Cache audit results and re-scan only modified files

## Troubleshooting

### Issue: Scanner reports false positives

**Solution:** Add exclusion patterns to `HardcodedParameterScanner.EXCLUDE_PATTERNS`

### Issue: Configuration file not found

**Solution:** Verify COHORT_2024 files exist in `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/`

### Issue: Syntax errors during scanning

**Solution:** Files with syntax errors are automatically skipped with warnings logged

### Issue: Memory usage too high

**Solution:** Process files in batches or filter by directory

## Architecture

### AST-Based Detection

The scanner uses Python's `ast` module for precise syntax-aware detection:

```
Source Code → AST → NodeVisitor → Pattern Matching → Violation Detection
```

**Advantages:**
- Accurate detection (no regex false positives)
- Context-aware (understands Python syntax)
- Extensible (easy to add new patterns)

### Configuration Registry

Loads all COHORT_2024 files into memory for fast lookups:

```
JSON Files → Parse → Extract Values → Index by Category → Fast Lookup
```

**Indexed Categories:**
- `known_weights`: Set of all recognized weight values
- `known_thresholds`: Set of all recognized threshold values
- `known_scores`: Set of all recognized score values
- `known_timeouts`: Set of all recognized timeout values

### Violation Classification

```
Detected Value → Category Matching → Config Lookup → Severity Assignment → Violation Record
```

**Severity Logic:**
- CRITICAL: Calibration weights/scores not in config
- HIGH: Thresholds/gates not in config
- MEDIUM: Runtime parameters not in config
- LOW: Other potential issues

## Extension Points

### Adding New Detection Patterns

```python
# In HardcodedParameterVisitor
CALIBRATION_KEYWORDS = {
    "weight", "weights", "threshold", "score", "scores",
    # Add new keywords here
    "penalty", "bonus", "factor"
}
```

### Adding New Configuration Sources

```python
# In ConfigurationRegistry._load_configurations()
try:
    custom_config_path = self.calibration_path / "COHORT_2024_custom.json"
    if custom_config_path.exists():
        with open(custom_config_path, "r") as f:
            self.custom_config = json.load(f)
        self._extract_values_from_custom()
except Exception as e:
    logger.warning(f"Failed to load custom config: {e}")
```

### Adding New Severity Levels

```python
# In ParameterViolation and AuditStatistics
@dataclass
class ParameterViolation:
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
```

## Best Practices

### For Developers

1. **Run audit before committing:**
   ```bash
   python run_parameter_audit.py
   ```

2. **Address critical violations immediately**

3. **Use configuration for all calibration values:**
   ```python
   # ❌ Don't
   weight = 0.35
   
   # ✅ Do
   weight = loader.get("component.weight", 0.35)
   ```

4. **Use ExecutorConfig for runtime parameters:**
   ```python
   # ❌ Don't
   timeout = 300
   
   # ✅ Do
   timeout = config.get('timeout', 300)
   ```

### For Maintainers

1. **Update COHORT_2024 files** when adding new parameters
2. **Document all configuration changes** in CHANGELOG.md
3. **Run audit in CI/CD** to prevent regressions
4. **Review audit reports** during code reviews

## References

- **Calibration System:** `CALIBRATION_INTEGRATION.md`
- **COHORT Manifest:** `COHORT_MANIFEST.json`
- **Parameter Loading:** `parameter_loader.py`
- **Executor Config:** `executor_config.py`
- **Structural Governance:** `STRUCTURAL_GOVERNANCE.md`

---

**Last Updated:** 2024-12-15  
**Version:** 1.0.0  
**Maintainer:** F.A.R.F.A.N Core Team
