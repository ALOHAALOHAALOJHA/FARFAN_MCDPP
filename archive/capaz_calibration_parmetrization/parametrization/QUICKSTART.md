# Signature-Based Parametrization Analysis - Quick Start

**COHORT_2024 - REFACTOR_WAVE_2024_12**

## What is This?

A comprehensive system for analyzing method signatures across the F.A.R.F.A.N codebase to:
- Extract method signatures via AST parsing
- Detect hardcoded parameters
- Generate migration recommendations
- Support configuration management

## Quick Start (5 minutes)

### Step 1: Run the Analysis

```bash
cd src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/parametrization
python run_signature_analysis.py
```

This generates:
- `method_signatures.json` - All method signatures
- `hardcoded_migration_report.json` - Parameters to migrate
- `signature_analysis.json` - Advanced analysis results
- `analysis_summary.txt` - Human-readable summary
- `COHORT_2024_executor_config_template.json` - Migration template

### Step 2: Review the Results

```bash
# View summary
cat analysis_summary.txt

# Check how many hardcoded parameters were found
python -c "import json; data=json.load(open('hardcoded_migration_report.json')); print(f'Found {len(data[\"migration_candidates\"])} parameters to migrate')"

# View top priorities
head -50 analysis_summary.txt
```

### Step 3: Query Specific Patterns

```bash
# Find all Bayesian methods
python example_analysis.py bayesian

# Find all methods with threshold parameters
python example_analysis.py threshold

# Find all executor methods
python example_analysis.py executor
```

### Step 4: Use Programmatically

```python
from signature_query_api import SignatureDatabase

# Load the database
db = SignatureDatabase.load()

# Query by method name
methods = db.find_by_method_name("calculate_probability")
for sig in methods:
    print(f"{sig.normalized_name}")
    print(f"  Required: {sig.required_inputs}")
    print(f"  Optional: {sig.optional_inputs}")
    print(f"  Critical: {sig.critical_optional}")

# Find methods with hardcoded parameters
hardcoded = db.find_with_hardcoded_params()
print(f"Found {len(hardcoded)} methods with hardcoded parameters")

# Get statistics
stats = db.get_statistics()
print(f"Total methods: {stats['total_signatures']}")
print(f"With critical params: {stats['with_critical_params']}")
```

## Common Use Cases

### Use Case 1: Find All Bayesian Methods

```bash
python example_analysis.py bayesian
```

Or programmatically:
```python
db = SignatureDatabase.load()
bayesian = db.find_by_method_name("bayesian", exact=False)
```

### Use Case 2: Identify Configuration Parameters

```bash
# View analysis results
cat signature_analysis.json | python -m json.tool | grep -A 5 "parameter_patterns"
```

Or programmatically:
```python
import json
with open("signature_analysis.json") as f:
    data = json.load(f)
    patterns = data["parameter_patterns"]
    for pattern_type, params in patterns.items():
        print(f"{pattern_type}: {len(params)} parameters")
```

### Use Case 3: Prepare Configuration Migration

```bash
# Use the template
cp COHORT_2024_executor_config_template.json COHORT_2024_executor_config.json

# Edit with actual values
# Then update source code to read from config instead of hardcoded values
```

### Use Case 4: Validate Signatures

```bash
python validate_signatures.py
```

Expected output:
```
✅ No errors found
✅ No warnings
VALIDATION PASSED
```

## What Gets Extracted?

For each method, the system extracts:

1. **Required Inputs**: Parameters without defaults
   - Example: `data`, `context`, `text`

2. **Optional Inputs**: Parameters with defaults
   - Example: `threshold=0.5`, `confidence=0.7`

3. **Critical Optional**: Optional params that are configuration-critical
   - Example: `alpha`, `beta`, `temperature`, `max_tokens`

4. **Output Type**: Return type annotation
   - Example: `Dict[str, Any]`, `float`, `List[str]`

5. **Output Range**: Inferred or documented value ranges
   - Example: `[0.0, 1.0]` for probabilities

6. **Hardcoded Parameters**: Constants in the method body
   - Example: `threshold = 0.75` on line 245

## File Descriptions

| File | Purpose | Run Directly? |
|------|---------|---------------|
| `method_signature_extractor.py` | Core extraction engine | No (import) |
| `signature_analyzer.py` | Advanced analysis layer | No (import) |
| `signature_query_api.py` | Query interface | No (import) |
| `extract_signatures.py` | CLI extraction tool | Yes |
| `run_signature_analysis.py` | **Main orchestrator** | **Yes** ⭐ |
| `validate_signatures.py` | Validation tool | Yes |
| `example_analysis.py` | Usage examples | Yes |
| `test_signature_system.py` | Integration tests | Yes |

## Testing the System

Run the integration tests:

```bash
python test_signature_system.py
```

Expected output:
```
✅ Extraction test passed
✅ Analysis test passed
✅ Export and validation test passed
✅ Query API test passed
✅ ALL TESTS PASSED
```

## Common Patterns in Output

### method_signatures.json Structure

```json
{
  "methods_dispensary.derek_beach.FinancialAuditor.analyze_budget": {
    "module": "methods_dispensary.derek_beach",
    "class_name": "FinancialAuditor",
    "method_name": "analyze_budget",
    "required_inputs": ["budget_data", "context"],
    "optional_inputs": ["threshold", "confidence_level"],
    "critical_optional": ["threshold", "confidence_level"],
    "output_type": "dict[str, Any]",
    "hardcoded_parameters": [
      {
        "variable": "DEFAULT_THRESHOLD",
        "value": 0.75,
        "line": 245
      }
    ]
  }
}
```

### Migration Report Structure

```json
{
  "migration_candidates": [
    {
      "signature": "methods_dispensary.derek_beach.FinancialAuditor.analyze_budget",
      "hardcoded_variable": "DEFAULT_THRESHOLD",
      "hardcoded_value": 0.75,
      "suggested_key": "methods_dispensary.derek_beach.FinancialAuditor.DEFAULT_THRESHOLD",
      "line_number": 245
    }
  ]
}
```

## Advanced Usage

### Custom Scan Patterns

```bash
# Scan only executors
python extract_signatures.py --patterns "**/executors.py" "**/executor*.py"

# Scan specific module
python extract_signatures.py --patterns "**/derek_beach.py"

# Custom output location
python extract_signatures.py --output-dir ./custom_analysis
```

### Programmatic Analysis

```python
from method_signature_extractor import MethodSignatureExtractor
from pathlib import Path

# Create extractor
extractor = MethodSignatureExtractor(Path.cwd())

# Scan with custom patterns
extractor.scan_repository(include_patterns=["**/methods_dispensary/**/*.py"])

# Access signatures
for name, sig in extractor.signatures.items():
    if sig.has_critical_params:
        print(f"{name}: {sig.critical_optional}")

# Export
extractor.export_signatures(Path("custom_signatures.json"))
```

### Custom Queries

```python
from signature_query_api import SignatureDatabase

db = SignatureDatabase.load()

# Complex query: Methods with both required and critical params
results = [
    sig for sig in db.signatures.values()
    if sig.has_required_inputs and sig.has_critical_params
]

# Find methods by return type
dict_methods = db.find_by_output_type("dict")
list_methods = db.find_by_output_type("list")

# Find methods in specific module with specific parameter
derek_beach = db.find_by_module("derek_beach", exact=False)
with_threshold = [s for s in derek_beach if "threshold" in s.optional_inputs]
```

## Troubleshooting

**Problem**: No signatures found
**Solution**: Check that you're in the correct directory and patterns match your files

**Problem**: Syntax errors during scan
**Solution**: Verify Python 3.12+ compatibility of source files

**Problem**: Missing critical parameters
**Solution**: Check if parameter names match patterns in `critical_params` set

**Problem**: Validation fails
**Solution**: Re-run extraction to generate fresh output

## Next Steps

1. Run `python run_signature_analysis.py` to generate all files
2. Review `analysis_summary.txt` for overview
3. Use `example_analysis.py` to explore specific patterns
4. Migrate hardcoded parameters using the template
5. Integrate with existing configuration system

## Documentation

- **SIGNATURE_ANALYSIS_README.md** - Complete documentation
- **SIGNATURE_SYSTEM_MANIFEST.md** - System overview and file manifest
- **QUICKSTART.md** - This file

## Support

Run tests to verify installation:
```bash
python test_signature_system.py
```

Check documentation:
```bash
cat SIGNATURE_ANALYSIS_README.md
```
