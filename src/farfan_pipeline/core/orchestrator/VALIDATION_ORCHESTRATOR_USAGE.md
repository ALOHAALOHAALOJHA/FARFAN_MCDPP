# Validation Orchestrator - Complete Usage Guide

## Overview

The Validation Orchestrator ensures all 300 validation contracts are properly executed with detailed failure diagnostics and remediation suggestions. It integrates seamlessly with the contract-driven validation engine to provide comprehensive tracking and reporting.

## Key Features

1. **Complete Coverage Tracking**: Monitor validation of all 300 micro-questions
2. **Detailed Failure Diagnostics**: Each failure includes type, field, severity, and remediation
3. **Comprehensive Reporting**: Generate detailed reports with prioritized remediation steps
4. **Multiple Export Formats**: Export results as JSON, CSV, or Markdown
5. **Error Code Analysis**: Track frequency and patterns of error codes
6. **Severity Distribution**: Monitor severity levels across all failures
7. **Real-time Monitoring**: Track validation progress during execution

## Quick Start

### Automatic Integration (Recommended)

```python
from farfan_pipeline.core.orchestrator.signal_contract_validator import (
    get_global_validation_orchestrator
)

# Get global orchestrator
orchestrator = get_global_validation_orchestrator()
orchestrator.start_orchestration()

# Process all questions (validation happens automatically)
results = orchestrator_instance.process_all_questions(document)

# Complete and get report
orchestrator.complete_orchestration()
report = orchestrator.get_remediation_report()
print(report)
```

### Manual Integration

```python
from farfan_pipeline.core.orchestrator.signal_contract_validator import (
    ValidationOrchestrator,
    validate_result_with_orchestrator
)

# Create orchestrator
orchestrator = ValidationOrchestrator(expected_question_count=300)
orchestrator.start_orchestration()

# Validate each result manually
for question in all_questions:
    result = analyze_question(question)
    validation = validate_result_with_orchestrator(
        result=result,
        signal_node=question,
        orchestrator=orchestrator,
        auto_register=True
    )
    
    if not validation.passed:
        print(f"Failed: {validation.error_code}")
        print(f"Remediation: {validation.remediation}")

# Complete orchestration
orchestrator.complete_orchestration()
```

## Integration with Executors

### BaseExecutorWithContract Integration

```python
from farfan_pipeline.core.orchestrator.base_executor_with_contract import (
    BaseExecutorWithContract
)
from farfan_pipeline.core.orchestrator.signal_contract_validator import (
    ValidationOrchestrator
)

# Create validation orchestrator
orchestrator = ValidationOrchestrator(expected_question_count=300)
orchestrator.start_orchestration()

# Create executor with validation orchestrator
executor = MyExecutor(
    method_executor=method_executor,
    signal_registry=signal_registry,
    config=config,
    questionnaire_provider=questionnaire_provider,
    validation_orchestrator=orchestrator  # Pass orchestrator here
)

# Execute - validation happens automatically
result = executor.execute(document, method_executor, question_context=context)

# Check contract validation metadata in result
if not result['contract_validation']['passed']:
    print(f"Validation failed: {result['contract_validation']['error_code']}")
    print(f"Failures: {result['contract_validation']['failure_count']}")

# After all executions
orchestrator.complete_orchestration()
summary = orchestrator.get_validation_summary()
print(f"Success Rate: {summary['success_rate']:.1%}")
```

### Enriched Signal Pack Integration

```python
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    EnrichedSignalPack
)

# Create enriched pack with validation orchestrator
enriched_pack = create_enriched_signal_pack(base_pack)

# Validate with orchestrator
validation = enriched_pack.validate_result(
    result=analysis_result,
    signal_node=signal_node,
    orchestrator=orchestrator,
    auto_register=True
)
```

## Reporting and Analysis

### Comprehensive Remediation Report

```python
# Generate detailed report with all failure information
report = orchestrator.get_remediation_report(
    include_all_details=True,
    max_failures_per_question=5
)
print(report)

# Output includes:
# - Summary statistics (passed, failed, invalid, skipped, errors)
# - Success and completion rates
# - Failure breakdown by type
# - Error code frequency
# - Severity distribution
# - Detailed failure information for each question
# - Prioritized remediation recommendations
```

### Validation Summary

```python
summary = orchestrator.get_validation_summary()

print(f"Total Expected: {summary['total_questions_expected']}")
print(f"Validated: {summary['validated_count']}")
print(f"Success Rate: {summary['success_rate']:.1%}")
print(f"Completion Rate: {summary['completion_rate']:.1%}")

# Access failure breakdown
print(f"Missing Fields: {len(summary['failure_breakdown']['missing_fields'])}")
print(f"Invalid Values: {len(summary['failure_breakdown']['invalid_values'])}")
print(f"Threshold Violations: {len(summary['failure_breakdown']['threshold_violations'])}")

# Error code frequency
for code, count in summary['error_code_frequency'].items():
    print(f"{code}: {count} occurrences")
```

### Coverage Analysis

```python
# Check validation coverage
expected_ids = [f"Q{i:03d}" for i in range(1, 301)]
coverage = orchestrator.get_validation_coverage_report(expected_ids)

print(f"Coverage: {coverage['coverage_percentage']:.1f}%")
print(f"Missing Questions: {coverage['missing_count']}")

if coverage['missing_questions']:
    print("Missing question IDs:")
    for qid in coverage['missing_questions'][:20]:
        print(f"  - {qid}")
```

### Failed Questions Analysis

```python
# Get all failed questions
failed = orchestrator.get_failed_questions()

for qid, result in failed.items():
    print(f"\nQuestion: {qid}")
    print(f"Error Code: {result.error_code}")
    print(f"Status: {result.status}")
    
    # Analyze failures by severity
    errors = [f for f in result.failures_detailed if f.severity == 'error']
    warnings = [f for f in result.failures_detailed if f.severity == 'warning']
    
    print(f"Errors: {len(errors)}, Warnings: {len(warnings)}")
    
    # Get remediation
    print(f"Remediation:\n{result.remediation}")
```

## Exporting Results

### JSON Export

```python
# Export complete validation data as JSON
json_data = orchestrator.export_validation_results('json')

# Access summary
print(json_data['summary']['success_rate'])

# Access individual validation results
for qid, validation_data in json_data['validations'].items():
    if not validation_data['passed']:
        print(f"{qid}: {validation_data['error_code']}")
        for failure in validation_data['failures']:
            print(f"  - {failure['message']}")
```

### CSV Export

```python
# Export as CSV for spreadsheet analysis
csv_data = orchestrator.export_validation_results('csv')

# Save to file
with open('validation_results.csv', 'w') as f:
    f.write(csv_data)

# CSV includes: question_id, status, passed, error_code, failure_count, severity
```

### Markdown Export

```python
# Export as Markdown for documentation
markdown_data = orchestrator.export_validation_results('markdown')

# Save to file
with open('VALIDATION_REPORT.md', 'w') as f:
    f.write(markdown_data)

# Includes formatted tables and summary statistics
```

## Batch Validation

```python
from farfan_pipeline.core.orchestrator.signal_contract_validator import (
    validate_batch_results
)

# Prepare batch of (result, signal_node) tuples
results_with_nodes = [
    (result1, signal_node1),
    (result2, signal_node2),
    # ... up to 300 items
]

# Validate entire batch
orchestrator = ValidationOrchestrator(expected_question_count=300)
orchestrator.start_orchestration()

validations = validate_batch_results(
    results_with_nodes,
    orchestrator=orchestrator,
    continue_on_error=True
)

orchestrator.complete_orchestration()

# Analyze batch results
failed_count = sum(1 for v in validations if not v.passed)
print(f"Failed: {failed_count}/{len(validations)}")
```

## Ensuring Complete Coverage

```python
from farfan_pipeline.core.orchestrator.signal_contract_validator import (
    ensure_complete_validation_coverage
)

# Verify all expected questions were validated
expected_ids = [f"Q{i:03d}" for i in range(1, 301)]

coverage = ensure_complete_validation_coverage(
    expected_question_ids=expected_ids,
    orchestrator=orchestrator
)

if coverage['missing_count'] > 0:
    print(f"WARNING: {coverage['missing_count']} questions not validated")
    
    # Missing questions are automatically registered as 'skipped'
    # They will appear in the final report
```

## Validation Contract Structure

### Failure Contract (Critical Conditions)

```json
{
  "failure_contract": {
    "abort_if": ["missing_currency", "negative_amount", "invalid_format"],
    "emit_code": "ERR_BUDGET_001",
    "severity": "error"
  }
}
```

Supported conditions:
- `missing_{field}`: Field is missing or null
- `negative_{field}`: Numeric field has negative value
- `empty_{field}`: Field is empty (empty string, list, or dict)
- `invalid_format`: Format validation failed
- `low_confidence`: Confidence below threshold
- `threshold_{field}`: Field value below threshold

### Validation Rules (Validation Checks)

```json
{
  "validations": {
    "rules": [
      "currency_present",
      "amount_positive",
      "date_valid",
      "confidence_high",
      "completeness_check"
    ],
    "thresholds": {
      "confidence": 0.7,
      "completeness": 0.8
    },
    "required_fields": [
      "amount",
      "currency",
      "date"
    ]
  }
}
```

## Validation Result Structure

Each `ValidationResult` includes:

```python
@dataclass
class ValidationResult:
    status: str  # 'success', 'failed', 'invalid', 'error', 'skipped'
    passed: bool
    error_code: str | None
    condition_violated: str | None
    validation_failures: list[str] | None
    remediation: str | None
    details: dict[str, Any] | None
    failures_detailed: list[ValidationFailure]
    execution_metadata: dict[str, Any]
    diagnostics: dict[str, Any]
```

Each `ValidationFailure` includes:

```python
@dataclass
class ValidationFailure:
    failure_type: str  # 'missing_field', 'invalid_value', etc.
    field_name: str
    expected: Any
    actual: Any
    severity: str  # 'error', 'warning', 'info'
    message: str
    remediation: str
    context: dict[str, Any]
```

## Performance Monitoring

```python
# Monitor validation performance
summary = orchestrator.get_validation_summary()

if summary['duration_seconds']:
    print(f"Duration: {summary['duration_seconds']:.2f}s")
    print(f"Throughput: {summary['validations_per_second']:.1f} validations/s")

# Check execution order
print(f"Execution order: {summary['execution_order'][:10]}")
```

## Best Practices

1. **Always Start and Complete Orchestration**
   ```python
   orchestrator.start_orchestration()
   # ... validation work ...
   orchestrator.complete_orchestration()
   ```

2. **Use Global Orchestrator for Consistency**
   ```python
   orchestrator = get_global_validation_orchestrator()
   ```

3. **Check Coverage Before Finalizing**
   ```python
   ensure_complete_validation_coverage(expected_ids, orchestrator)
   ```

4. **Export Results for Analysis**
   ```python
   json_data = orchestrator.export_validation_results('json')
   # Store or analyze externally
   ```

5. **Review Remediation Priorities**
   ```python
   report = orchestrator.get_remediation_report()
   # Focus on HIGH PRIORITY items first
   ```

6. **Reset Between Runs**
   ```python
   orchestrator.reset()
   # or
   reset_global_validation_orchestrator()
   ```

## Troubleshooting

### Low Success Rate

```python
summary = orchestrator.get_validation_summary()
if summary['success_rate'] < 0.8:
    # Analyze failure patterns
    print(summary['error_code_frequency'])
    print(summary['failure_breakdown'])
    
    # Get remediation priorities
    report = orchestrator.get_remediation_report()
    # Focus on systematic issues
```

### Missing Validations

```python
coverage = orchestrator.get_validation_coverage_report(expected_ids)
if coverage['missing_count'] > 0:
    # Check execution logs
    # Verify executor integration
    # Ensure all questions are processed
    pass
```

### High Failure Rate for Specific Error Code

```python
summary = orchestrator.get_validation_summary()
for code, count in summary['error_code_frequency'].items():
    if count > 10:  # Systematic issue
        # Review pattern definitions
        # Check extraction logic
        # Adjust thresholds if needed
        pass
```

## Advanced Usage

### Custom Failure Analysis

```python
failed = orchestrator.get_failed_questions()

# Group by error code
by_error_code = {}
for qid, result in failed.items():
    code = result.error_code or 'UNKNOWN'
    if code not in by_error_code:
        by_error_code[code] = []
    by_error_code[code].append(qid)

# Find patterns
for code, questions in by_error_code.items():
    print(f"{code}: affects {len(questions)} questions")
```

### Severity-based Prioritization

```python
failed = orchestrator.get_failed_questions()

critical = []
warnings = []

for qid, result in failed.items():
    has_errors = any(f.severity == 'error' for f in result.failures_detailed)
    if has_errors:
        critical.append(qid)
    else:
        warnings.append(qid)

print(f"Critical: {len(critical)}, Warnings: {len(warnings)}")
```

### Time-based Analysis

```python
summary = orchestrator.get_validation_summary()

if summary['validations_per_second']:
    avg_time_per_validation = 1.0 / summary['validations_per_second']
    print(f"Average time per validation: {avg_time_per_validation*1000:.1f}ms")
```

## Integration Checklist

- [ ] Create or get ValidationOrchestrator
- [ ] Call `start_orchestration()` before processing
- [ ] Pass orchestrator to executors or use global instance
- [ ] Validate all 300 questions
- [ ] Call `complete_orchestration()` after processing
- [ ] Check validation coverage with `ensure_complete_validation_coverage()`
- [ ] Generate and review remediation report
- [ ] Export results for archival/analysis
- [ ] Review and address high-priority failures
- [ ] Reset orchestrator between runs

## Conclusion

The Validation Orchestrator provides comprehensive validation tracking and reporting for all 300 micro-questions. By integrating it into your pipeline, you ensure:

- Complete validation coverage
- Detailed failure diagnostics
- Actionable remediation suggestions
- Performance monitoring
- Quality assurance

Use the orchestrator to maintain high validation quality and quickly identify and address systematic issues.
