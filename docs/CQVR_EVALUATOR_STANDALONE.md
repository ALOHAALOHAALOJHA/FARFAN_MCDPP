# CQVR Evaluator Standalone Script

## Overview

The CQVR Evaluator (`scripts/cqvr_evaluator_standalone.py`) is a comprehensive contract quality validation tool that implements all 10 scoring functions from the CQVR v2.0 rubric with explicit return signatures.

## Features

- ✅ **All 10 Scoring Functions**: Complete implementation of Tier 1 (55 pts), Tier 2 (30 pts), and Tier 3 (15 pts) scoring
- ✅ **Multiple Evaluation Modes**: Single contract, batch (25), range, or all 300 contracts
- ✅ **Decision Engine**: Automated triage to PRODUCCION, PARCHEAR, or REFORMULAR
- ✅ **Deterministic Scoring**: Same input always produces same output (excluding timestamps)
- ✅ **JSON Reports**: Machine-readable output with full details
- ✅ **Rich Console Output**: Human-readable tables and summaries (with fallback)
- ✅ **Error Handling**: Robust handling of malformed contracts
- ✅ **Unit Tests**: 25 comprehensive tests covering all functions

## Scoring Functions

### Tier 1: Critical Components (55 pts)

| Function | Points | Description |
|----------|--------|-------------|
| `verify_identity_schema_coherence` | 20 | Validates identity-schema field alignment |
| `verify_method_assembly_alignment` | 20 | Checks method provides vs assembly sources |
| `verify_signal_requirements` | 10 | Validates signal configuration |
| `verify_output_schema` | 5 | Ensures schema completeness |

### Tier 2: Functional Components (30 pts)

| Function | Points | Description |
|----------|--------|-------------|
| `verify_pattern_coverage` | 10 | Checks pattern coverage of expected elements |
| `verify_method_specificity` | 10 | Detects boilerplate vs specific methods |
| `verify_validation_rules` | 10 | Validates rule completeness |

### Tier 3: Quality Components (15 pts)

| Function | Points | Description |
|----------|--------|-------------|
| `verify_documentation_quality` | 5 | Checks epistemological documentation |
| `verify_human_template` | 5 | Validates human-readable templates |
| `verify_metadata_completeness` | 5 | Ensures metadata completeness |

## Usage

### Single Contract Evaluation

```bash
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json
```

**Output:**
```
================================================================================
CQVR Evaluator v2.0
================================================================================
Evaluating 1 contract(s)...
...
✓ Q001.v3.json: 82/100 - PRODUCCION

                  Contract Evaluation Results                  
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Contract ┃ Tier 1 ┃ Tier 2 ┃ Tier 3 ┃  Total ┃   Decision   ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Q001     │  52/55 │  20/30 │  10/15 │ 82/100 │ ✓ PRODUCCION │
└──────────┴────────┴────────┴────────┴────────┴──────────────┘
```

### Batch Evaluation (25 contracts)

```bash
python scripts/cqvr_evaluator_standalone.py --batch 1   # Q001-Q025
python scripts/cqvr_evaluator_standalone.py --batch 2   # Q026-Q050
# ... up to batch 12 (Q276-Q300)
```

### Range Evaluation

```bash
python scripts/cqvr_evaluator_standalone.py --range 1 30
```

### All 300 Contracts

```bash
python scripts/cqvr_evaluator_standalone.py --all
```

### Quiet Mode (JSON only)

```bash
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json --quiet
```

## Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--contract FILE` | Evaluate single contract | `--contract Q001.v3.json` |
| `--batch N` | Evaluate batch (1-12) | `--batch 1` |
| `--range START END` | Evaluate range | `--range 1 30` |
| `--all` | Evaluate all 300 contracts | `--all` |
| `--contracts-dir PATH` | Override contracts directory | `--contracts-dir ./contracts` |
| `--output-dir PATH` | Override output directory | `--output-dir ./reports` |
| `--output-json PATH` | Override JSON output path | `--output-json ./report.json` |
| `--quiet` | Suppress console output | `--quiet` |

## JSON Report Format

```json
{
  "evaluation_timestamp": "2025-12-17T18:47:15.041460",
  "cqvr_version": "2.0",
  "total_contracts": 1,
  "statistics": {
    "avg_score": 82.0,
    "production_ready": 1,
    "need_patches": 0,
    "need_reformulation": 0
  },
  "evaluations": [
    {
      "contract_id": "Q001",
      "evaluation_timestamp": "2025-12-17T18:47:15.041411",
      "cqvr_version": "2.0",
      "scores": {
        "tier1": {
          "score": 52,
          "max": 55,
          "percentage": 94.5,
          "components": {
            "A1_identity_schema": 20,
            "A2_method_assembly": 18,
            "A3_signal_requirements": 10,
            "A4_output_schema": 4
          }
        },
        "tier2": { "score": 20, "max": 30, ... },
        "tier3": { "score": 10, "max": 15, ... },
        "total": { "score": 82, "max": 100, ... }
      },
      "decision": {
        "status": "PRODUCCION",
        "rationale": "Contract approved for production: Tier 1: 52/55...",
        "remediation": ["Final quality review", "Integration testing", ...],
        "blockers": [],
        "warnings": ["A4: source_hash is placeholder or missing"]
      },
      "issues": {
        "tier1": ["A4: source_hash is placeholder or missing"],
        "tier2": ["B2: High boilerplate ratio: 17/17 methods"],
        "tier3": ["C1: No methodological_depth for documentation check"],
        "all": [...]
      }
    }
  ]
}
```

## Decision Matrix

The decision engine uses the following criteria:

### PRODUCCION (Production Ready)
- Tier 1 score ≥ 45 points
- Total score ≥ 80 points
- Ready for deployment

### PARCHEAR (Needs Patches)
- Tier 1 score ≥ 35 points
- Total score ≥ 70 points OR blockers ≤ 2
- Fixable with targeted patches

### REFORMULAR (Needs Reformulation)
- Tier 1 score < 35 points
- OR fails other criteria
- Requires substantial rework

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Evaluation errors (malformed contracts, file not found, etc.) |

## Running Tests

```bash
# Run all CQVR evaluator tests
pytest tests/test_cqvr_evaluator.py -v -m "updated"

# Run specific test
pytest tests/test_cqvr_evaluator.py::test_verify_identity_schema_coherence_perfect -v
```

All 25 tests cover:
- All 10 scoring functions (perfect and edge cases)
- Decision engine (PRODUCCION, PARCHEAR, REFORMULAR)
- Full contract evaluation
- Determinism verification

## Determinism

The evaluator is fully deterministic:

```bash
# Run twice and compare (excluding timestamps)
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json --output-json /tmp/test1.json --quiet
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json --output-json /tmp/test2.json --quiet

# Scores and decisions are identical (only timestamps differ)
```

## Error Handling

The script handles:
- ✅ Missing contract files
- ✅ Malformed JSON
- ✅ Missing required fields
- ✅ Invalid contract structures
- ✅ Evaluation exceptions

Errors are reported clearly:

```
================================================================================
ERRORS:
================================================================================
✗ Contract not found: Q999.v3.json
✗ Malformed JSON in Q123.v3.json: Expecting ',' delimiter: line 45 column 3
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Evaluate Contract Quality
  run: |
    python scripts/cqvr_evaluator_standalone.py \
      --all \
      --output-json cqvr_report.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# Evaluate modified contracts
python scripts/cqvr_evaluator_standalone.py \
  --contract modified_contract.v3.json
```

## Dependencies

- Python 3.12+
- `rich` (optional, for enhanced console output)
- No other external dependencies required

Fallback to basic console output if `rich` is not available.

## Architecture

The script is organized into functional sections:

1. **Core Scoring Functions** (Tier 1-3): Pure functions with explicit signatures
2. **Decision Engine**: `make_triage_decision()` applies decision matrix
3. **Evaluation Orchestrator**: `evaluate_contract()` coordinates full evaluation
4. **Report Generation**: JSON and console output
5. **CLI Interface**: `argparse`-based command-line handling

All functions use `Dict[str, Any]` for contracts and return `Tuple[int, List[str]]` for (score, issues).

## Examples

### Example 1: Check production readiness

```bash
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json
# ✓ Q001.v3.json: 82/100 - PRODUCCION
```

### Example 2: Identify contracts needing fixes

```bash
python scripts/cqvr_evaluator_standalone.py --batch 1 | grep "REFORMULAR"
# ✗ Q003.v3.json: 61/100 - REFORMULAR
# ✗ Q004.v3.json: 61/100 - REFORMULAR
# ...
```

### Example 3: Generate report for range

```bash
python scripts/cqvr_evaluator_standalone.py \
  --range 1 50 \
  --output-json batch1-2_report.json
```

## Troubleshooting

### Issue: Contract not found

**Solution**: Check `--contracts-dir` path or provide absolute path

```bash
python scripts/cqvr_evaluator_standalone.py \
  --contract Q001.v3.json \
  --contracts-dir /absolute/path/to/contracts
```

### Issue: Import errors

**Solution**: Ensure script is run from repository root

```bash
cd /path/to/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json
```

## See Also

- **Original CQVR Validator**: `src/farfan_pipeline/phases/Phase_two/contract_validator_cqvr.py`
- **Batch Evaluator**: `scripts/cqvr_evaluator.py` (different implementation)
- **Contract Remediator**: `scripts/contract_remediator.py`
- **Contract Schemas**: `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/`

## License

Part of the F.A.R.F.A.N Mechanistic Policy Pipeline project.
