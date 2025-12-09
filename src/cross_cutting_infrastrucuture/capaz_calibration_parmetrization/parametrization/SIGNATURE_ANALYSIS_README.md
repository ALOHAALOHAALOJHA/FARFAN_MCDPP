# Signature-Based Parametrization Analysis

**COHORT_2024 - REFACTOR_WAVE_2024_12**

## Overview

This system provides comprehensive analysis of method signatures across the F.A.R.F.A.N codebase to support parametrization and configuration management. It scans executor methods and core scripts via AST parsing to extract metadata and detect hardcoded parameters.

## Components

### 1. `method_signature_extractor.py`

Core extraction engine that scans Python files and extracts:

- **Required inputs**: Parameters without default values
- **Optional inputs**: Parameters with default values
- **Critical optional**: Optional parameters that are configuration-critical (e.g., `threshold`, `confidence`, `alpha`)
- **Output type**: Return type annotation
- **Output range**: Inferred or documented output value ranges
- **Hardcoded parameters**: Constants and literals assigned within methods

**Output**: `method_signatures.json`

### 2. `signature_analyzer.py`

Advanced analysis layer that:

- Infers output ranges from docstrings and method names
- Detects parameter patterns (Bayesian, threshold, config, model, I/O)
- Generates migration priority scores for hardcoded parameters
- Provides confidence ratings for inferences

**Output**: `signature_analysis.json`

### 3. `extract_signatures.py`

CLI tool for running extraction with custom patterns and output locations.

**Usage**:
```bash
python extract_signatures.py
python extract_signatures.py --output-dir ./artifacts
python extract_signatures.py --patterns "**/executors.py" "**/methods_dispensary/**/*.py"
```

### 4. `run_signature_analysis.py`

Unified orchestrator that runs the complete pipeline:

1. Extract method signatures
2. Detect hardcoded parameters
3. Analyze patterns and ranges
4. Generate migration recommendations
5. Create config templates

**Usage**:
```bash
python run_signature_analysis.py
python run_signature_analysis.py --output-dir ./artifacts
```

## Output Files

### method_signatures.json

Complete signature metadata for all scanned methods:

```json
{
  "_metadata": {
    "cohort_id": "COHORT_2024",
    "total_signatures": 1250
  },
  "signatures": {
    "methods_dispensary.derek_beach.FinancialAuditor.analyze_budget": {
      "module": "methods_dispensary.derek_beach",
      "class_name": "FinancialAuditor",
      "method_name": "analyze_budget",
      "required_inputs": ["budget_data", "context"],
      "optional_inputs": ["threshold", "confidence_level"],
      "critical_optional": ["threshold", "confidence_level"],
      "output_type": "dict[str, Any]",
      "output_range": {"type": "object"},
      "hardcoded_parameters": [
        {
          "function": "analyze_budget",
          "variable": "DEFAULT_THRESHOLD",
          "value": 0.75,
          "line": 245,
          "type": "float"
        }
      ],
      "docstring": "Analyze budget allocation...",
      "line_number": 240
    }
  }
}
```

### hardcoded_migration_report.json

Prioritized list of hardcoded parameters that should be migrated to configuration:

```json
{
  "_metadata": {
    "total_candidates": 487
  },
  "migration_candidates": [
    {
      "signature": "methods_dispensary.derek_beach.FinancialAuditor.analyze_budget",
      "module": "methods_dispensary.derek_beach",
      "class": "FinancialAuditor",
      "method": "analyze_budget",
      "hardcoded_variable": "DEFAULT_THRESHOLD",
      "hardcoded_value": 0.75,
      "hardcoded_type": "float",
      "line_number": 245,
      "migration_target": "COHORT_2024_executor_config.json",
      "suggested_key": "methods_dispensary.derek_beach.FinancialAuditor.DEFAULT_THRESHOLD"
    }
  ]
}
```

### signature_analysis.json

Advanced analysis results:

```json
{
  "_metadata": {
    "cohort_id": "COHORT_2024"
  },
  "output_range_inferences": {
    "methods_dispensary.analyzer_one.calculate_probability": {
      "inferred_type": "float",
      "min_value": 0.0,
      "max_value": 1.0,
      "confidence": 0.8,
      "source": "method_name_pattern"
    }
  },
  "parameter_patterns": {
    "bayesian_params": [
      "methods_dispensary.derek_beach.BayesianUpdater.update.prior",
      "methods_dispensary.derek_beach.BayesianUpdater.update.likelihood"
    ],
    "threshold_params": [
      "methods_dispensary.analyzer_one.filter_results.min_confidence",
      "methods_dispensary.analyzer_one.filter_results.max_uncertainty"
    ]
  },
  "migration_priorities": [
    {
      "signature": "methods_dispensary.derek_beach.FinancialAuditor.analyze_budget",
      "parameter": "DEFAULT_THRESHOLD",
      "value": 0.75,
      "priority_score": 15,
      "suggested_config_key": "methods_dispensary.derek_beach.FinancialAuditor.DEFAULT_THRESHOLD"
    }
  ]
}
```

### analysis_summary.txt

Human-readable summary report with statistics and top priorities.

### COHORT_2024_executor_config_template.json

Template for migrating hardcoded parameters to executor configuration:

```json
{
  "_cohort_metadata": {
    "cohort_id": "COHORT_2024",
    "description": "Template for migrating hardcoded parameters to configuration"
  },
  "parameters": {
    "methods_dispensary.derek_beach.FinancialAuditor.DEFAULT_THRESHOLD": {
      "value": null,
      "original_value": 0.75,
      "type": "float",
      "source": {
        "module": "methods_dispensary.derek_beach",
        "class": "FinancialAuditor",
        "method": "analyze_budget",
        "line": 245
      }
    }
  }
}
```

## Signature Notation

All method signatures use normalized notation:

- **Module functions**: `module.function_name`
- **Class methods**: `module.ClassName.method_name`
- **Nested classes**: `module.OuterClass.InnerClass.method_name`

Examples:
- `methods_dispensary.analyzer_one.process_document`
- `methods_dispensary.derek_beach.FinancialAuditor.analyze_budget`
- `canonic_phases.Phase_two.executors.D1Q1_Executor.execute`

## Critical Optional Parameters

The system identifies parameters as "critical optional" if they match common configuration patterns:

- Bayesian parameters: `prior`, `posterior`, `alpha`, `beta`
- Thresholds: `threshold`, `min_*`, `max_*`, `cutoff`
- Model parameters: `temperature`, `max_tokens`, `seed`
- Performance: `timeout`, `max_iter`, `tol`
- Sampling: `n_samples`, `min_samples`

## Migration Workflow

1. **Extract**: Run `run_signature_analysis.py` to generate all reports
2. **Review**: Examine `hardcoded_migration_report.json` for migration candidates
3. **Prioritize**: Use `migration_priorities` in `signature_analysis.json` to identify high-priority parameters
4. **Migrate**: Update `COHORT_2024_executor_config.json` with parameter values
5. **Refactor**: Update source code to read from configuration instead of hardcoded values
6. **Validate**: Re-run analysis to verify migration completeness

## Integration with Existing Systems

This system complements the existing calibration infrastructure:

- **ParameterLoaderV2**: Reads runtime parameters from configuration
- **calibrated_method decorator**: Marks methods for parameter injection
- **COHORT_2024_executor_config.json**: Central configuration repository

The signature analysis identifies which parameters should be moved to the configuration system managed by these components.

## Extending the Analysis

To add custom pattern detection:

1. Edit `critical_params` in `MethodSignatureExtractor.__init__`
2. Add new pattern categories in `SignatureAnalyzer.detect_parameter_patterns`
3. Adjust priority scoring in `SignatureAnalyzer.generate_migration_priority`

To customize output range inference:

1. Extend `SignatureAnalyzer._infer_output_range_from_context`
2. Add new heuristics based on method names, docstrings, or type annotations

## Technical Details

### AST Parsing

The system uses Python's `ast` module for robust source code analysis:

- Handles both `def` and `async def` functions
- Preserves type annotations via `ast.unparse`
- Detects literals in assignments (numbers, strings, lists, dicts)
- Supports class methods, instance methods, and module-level functions

### Hardcoded Parameter Detection

The `HardcodedParameterDetector` visitor identifies:

- Direct assignments: `threshold = 0.75`
- Annotated assignments: `threshold: float = 0.75`
- Complex literals: `config = {"alpha": 0.5, "beta": 1.0}`
- Negative numbers: `min_value = -100`

### Output Range Inference

The analyzer uses multiple strategies:

1. **Method name patterns**: `calculate_probability` → [0, 1]
2. **Docstring ranges**: "returns score from 0 to 100" → [0, 100]
3. **Type annotations**: `-> bool` → [True, False]
4. **Semantic keywords**: "confidence", "score", "probability"

## Example Workflow

```bash
# Run complete analysis
cd src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/parametrization
python run_signature_analysis.py

# Review outputs
cat method_signatures.json
cat hardcoded_migration_report.json
cat signature_analysis.json
cat analysis_summary.txt

# Use template to update executor config
cp COHORT_2024_executor_config_template.json COHORT_2024_executor_config.json
# Edit COHORT_2024_executor_config.json with actual values

# Re-run to verify
python run_signature_analysis.py
```

## Troubleshooting

**Issue**: Syntax errors during scanning

**Solution**: Check Python version compatibility. Requires Python 3.12+

**Issue**: Missing signatures for certain methods

**Solution**: Verify file patterns include target files. Use `--patterns` flag.

**Issue**: Low confidence in output range inference

**Solution**: Add docstring documentation with explicit ranges or return value descriptions.

## Future Enhancements

Potential improvements:

- Integration with type checking tools (mypy, pyright)
- Call graph analysis to track parameter flow
- Automatic detection of configuration hierarchies
- Machine learning-based pattern recognition
- Real-time IDE integration for migration suggestions
