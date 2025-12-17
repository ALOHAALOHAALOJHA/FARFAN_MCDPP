# CQVR Evaluator Documentation

## Overview

The CQVR (Contract Quality Validation and Remediation) Evaluator is a comprehensive tool for evaluating executor contracts against the CQVR v2.0 rubric (100 points).

## Features

- **10 Core Scoring Functions**: All functions return `Tuple[int, List[str]]` (score, issues)
- **Decision Engine**: Deterministic triage decisions (PRODUCCION, PARCHEAR, REFORMULAR)
- **JSON Reports**: Machine-readable output with full details
- **Rich Console Output**: Human-readable tables and progress bars
- **Batch Processing**: Single contract, batches of 25, or all 300 contracts
- **Deterministic**: Same input always produces same output
- **Error Handling**: Gracefully handles malformed contracts
- **Comprehensive Tests**: 41 unit tests covering all scoring functions

## Scoring Rubric

### Tier 1: Critical Components (55 points)
- **A1**: Identity-Schema Coherence (20 pts) - Ensures critical fields match between identity and schema
- **A2**: Method-Assembly Alignment (20 pts) - Ensures methods are properly used in assembly
- **A3**: Signal Requirements (10 pts) - Ensures signal validation is properly configured
- **A4**: Output Schema (5 pts) - Ensures output schema is properly defined

### Tier 2: Functional Components (30 points)
- **B1**: Pattern Coverage (10 pts) - Ensures patterns adequately cover expected elements
- **B2**: Method Specificity (10 pts) - Ensures methods have specific, non-boilerplate documentation
- **B3**: Validation Rules (10 pts) - Ensures validation rules cover expected elements

### Tier 3: Quality Components (15 points)
- **C1**: Documentation Quality (5 pts) - Ensures epistemological foundations are documented
- **C2**: Human Template (5 pts) - Ensures human-readable output is properly configured
- **C3**: Metadata Completeness (5 pts) - Ensures metadata is complete and valid

## Decision Matrix

| Decision     | Criteria |
|-------------|----------|
| PRODUCCION  | Tier 1 ≥ 45, Total ≥ 80, 0 blockers |
| PARCHEAR    | Tier 1 ≥ 35, Total ≥ 70, ≤ 2 blockers |
| REFORMULAR  | Otherwise |

## Usage

### Single Contract

```bash
python scripts/cqvr_evaluator.py --contract path/to/contract.json --output-dir reports/cqvr
```

### Batch Processing (25 contracts)

```bash
# Batch 1: Q001-Q025
python scripts/cqvr_evaluator.py --batch 1 --output-dir reports/cqvr

# Batch 2: Q026-Q050
python scripts/cqvr_evaluator.py --batch 2 --output-dir reports/cqvr

# ... up to Batch 12: Q276-Q300
python scripts/cqvr_evaluator.py --batch 12 --output-dir reports/cqvr
```

### All Contracts (300 total)

```bash
python scripts/cqvr_evaluator.py --all --output-dir reports/cqvr
```

### JSON Only (no console output)

```bash
python scripts/cqvr_evaluator.py --all --output-dir reports/cqvr --json-only
```

### Custom Contracts Directory

```bash
python scripts/cqvr_evaluator.py --batch 1 \
  --contracts-dir custom/path/to/contracts \
  --output-dir reports/cqvr
```

## Output

### Console Output (with Rich)

The script displays:
- Summary statistics table
- Individual contract results table with color-coded decisions
- Progress bar during evaluation

Example:
```
CQVR Evaluation Summary     
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric             ┃ Value    ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Total Evaluated    │ 25       │
│ Average Score      │ 65.2/100 │
│ Production Ready   │ 2        │
│ Need Patches       │ 6        │
│ Need Reformulation │ 17       │
└────────────────────┴──────────┘
```

### JSON Output

Each evaluation produces a JSON report with:
```json
{
  "timestamp": "2025-12-17T20:15:40.222587",
  "evaluator": "CQVR Evaluator v2.0",
  "rubric": "CQVR v2.0 (100 points)",
  "contracts_evaluated": 300,
  "summary": {
    "total_evaluated": 300,
    "average_score": 66.8,
    "production_ready": 27,
    "need_patches": 61,
    "need_reformulation": 212
  },
  "contracts": [
    {
      "contract_id": "Q001",
      "decision": {
        "decision": "PRODUCCION",
        "score": {
          "tier1_score": 52.0,
          "tier2_score": 20.0,
          "tier3_score": 10.0,
          "total_score": 82.0,
          "component_scores": {
            "A1": 20.0,
            "A2": 18.0,
            ...
          }
        },
        "blockers": [],
        "warnings": ["..."],
        "recommendations": [],
        "rationale": "..."
      }
    }
  ]
}
```

## Running Tests

```bash
# Run all CQVR evaluator tests
pytest tests/test_cqvr_evaluator.py -v -m updated

# Run specific test class
pytest tests/test_cqvr_evaluator.py::TestIdentitySchemaCoherence -v

# Run with coverage
pytest tests/test_cqvr_evaluator.py --cov=scripts.cqvr_evaluator
```

## Test Coverage

- ✅ 41 unit tests
- ✅ All 10 scoring functions tested
- ✅ Decision engine tested
- ✅ End-to-end evaluation tested
- ✅ Error handling tested
- ✅ Determinism verified

## Scoring Function Signatures

All scoring functions follow the same signature:

```python
def verify_component(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify a specific component.
    
    Returns:
        Tuple of (score, issues_list)
    """
    score = 0
    issues = []
    # ... evaluation logic
    return score, issues
```

## Common Issues and Fixes

### 1. Orphan Assembly Sources
**Issue**: Assembly sources reference namespaces not in method provides  
**Fix**: Ensure all assembly `sources` match method `provides` namespaces  
**Impact**: +10 pts (A2)

### 2. Zero Signal Threshold with Mandatory Signals
**Issue**: `minimum_signal_threshold = 0` but `mandatory_signals` defined  
**Fix**: Set `minimum_signal_threshold > 0` when mandatory signals exist  
**Impact**: +10 pts (A3)  
**Severity**: CRITICAL blocker

### 3. Identity-Schema Mismatch
**Issue**: Fields like `question_id` differ between identity and schema  
**Fix**: Ensure all identity fields match schema `const` values  
**Impact**: Up to +20 pts (A1)

### 4. Required Fields Not in Properties
**Issue**: Schema `required` array contains fields not in `properties`  
**Fix**: Define all required fields in schema properties  
**Impact**: +3 pts (A4)

### 5. Boilerplate Documentation
**Issue**: Generic phrases like "Execute" or "analytical paradigm"  
**Fix**: Provide specific, detailed method documentation  
**Impact**: +10 pts (B2), +5 pts (C1)

## Dependencies

- Python 3.12+
- `rich` (optional, for console output)
- `pytest` (for running tests)

If Rich is not available, the script falls back to plain text output.

## Performance

- Single contract: ~0.01s
- 25 contracts (batch): ~0.5s
- 300 contracts (all): ~6s

## Example Workflow

```bash
# 1. Evaluate first batch
python scripts/cqvr_evaluator.py --batch 1 --output-dir reports/cqvr

# 2. Review results
cat reports/cqvr/batch_1_CQVR.json | jq '.summary'

# 3. Identify contracts needing work
cat reports/cqvr/batch_1_CQVR.json | jq '.contracts[] | select(.decision.decision == "REFORMULAR") | .contract_id'

# 4. Fix identified issues and re-evaluate
python scripts/cqvr_evaluator.py --contract path/to/Q003.v3.json --output-dir reports/cqvr
```

## Integration

The CQVR evaluator can be integrated into:
- CI/CD pipelines for automated contract validation
- Pre-commit hooks to validate changes
- Monitoring dashboards for contract quality tracking
- Remediation workflows to guide improvements

## Notes

- All scoring is deterministic: same input produces same output
- Blockers are issues that prevent production deployment
- Warnings are suggestions for improvement
- Recommendations provide actionable remediation steps
