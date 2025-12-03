# Validation and Testing Tools

This directory contains tools for validating data contracts, testing operational feasibility, and ensuring system quality.

## Directory Structure

```
tools/
├── validation/           # Contract validation tools
│   ├── validate_scoring_parity.py
│   └── validate_error_logs.py
├── testing/             # Operational testing tools
│   ├── generate_synthetic_traffic.py
│   └── boot_check.py
└── chunk_semantic_auditor.py  # Offline semantic integrity verification
```

## Semantic Integrity Tools

### Chunk Semantic Auditor

**Purpose**: Offline verification of semantic integrity for processed policy chunks. Acts as an independent verifier to ensure chunk content aligns with assigned metadata (policy_area_id, dimension_id).

**Key Features**:
- Uses sentence-transformers for semantic similarity computation
- Compares chunk text against canonical descriptions of policy areas and dimensions
- Configurable coherence threshold (default: 0.7)
- Generates detailed JSON audit reports
- Detects potential SPC model degradation or routing errors

**Usage**:

```bash
# Basic audit with default settings
python tools/chunk_semantic_auditor.py --artifacts-dir artifacts/plan1/

# Custom coherence threshold
python tools/chunk_semantic_auditor.py \
    --artifacts-dir artifacts/plan1/ \
    --threshold 0.65

# Use a different sentence transformer model
python tools/chunk_semantic_auditor.py \
    --artifacts-dir artifacts/plan1/ \
    --model-name sentence-transformers/all-mpnet-base-v2

# Verbose output for debugging
python tools/chunk_semantic_auditor.py \
    --artifacts-dir artifacts/plan1/ \
    --verbose
```

**Output**:

The tool generates:
1. **Console Summary**: Pass/fail statistics, average scores, and specific failures
2. **JSON Report**: `semantic_audit_report.json` in the artifacts directory

Sample report structure:
```json
{
  "metadata": {
    "artifacts_dir": "artifacts/plan1/",
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "threshold": 0.7,
    "total_chunks_audited": 450
  },
  "summary": {
    "passed": 442,
    "failed": 8,
    "pass_rate": 0.982,
    "average_coherence_score": 0.784,
    "min_coherence_score": 0.612,
    "max_coherence_score": 0.921
  },
  "failures": [
    {
      "chunk_id": "chunk_042",
      "file_path": "phase1/chunks.json",
      "policy_area_id": "PA03",
      "dimension_id": "DIM02",
      "coherence_score": 0.612,
      "threshold": 0.7
    }
  ]
}
```

**Interpretation**:

- **Coherence Score ≥ threshold**: Chunk content semantically aligns with metadata
- **Coherence Score < threshold**: Potential misclassification or routing error
- **Low average scores**: May indicate SPC model degradation
- **High failure rate**: Critical issue requiring pipeline investigation

**Exit Codes**:
- 0: All chunks pass semantic integrity checks
- 1: One or more chunks fail (failures listed in report)
- 2: Configuration error or runtime failure

**Canonical Descriptions**:

The tool uses canonical descriptions for 6 dimensions (DIM01-DIM06) and 10 policy areas (PA01-PA10):

- **DIM01**: Inputs (financial resources, human capital, infrastructure)
- **DIM02**: Activities (actions, programs, interventions)
- **DIM03**: Products (deliverables, outputs, services)
- **DIM04**: Results (outcomes, behavioral changes, effects)
- **DIM05**: Impacts (long-term effects, structural changes)
- **DIM06**: Causality (logical chains, causal relationships, theory of change)

- **PA01**: Economic development, business competitiveness
- **PA02**: Social welfare, health, education
- **PA03**: Urban planning, infrastructure
- **PA04**: Environmental protection, sustainability
- **PA05**: Public security, justice
- **PA06**: Cultural development, heritage
- **PA07**: Institutional capacity, governance
- **PA08**: Rural development, agriculture
- **PA09**: Digital transformation, technology
- **PA10**: Cross-sectoral integration

**When to Run**:

- After Phase 1 (SPC processing) completes
- Before Phase 2 (micro question analysis)
- During pipeline debugging/optimization
- As part of quality assurance workflow
- When investigating accuracy degradation

**Performance**:

- **Speed**: ~5-10 chunks/second (depends on model and hardware)
- **Memory**: ~500MB-2GB (depends on model size)
- **Models**: Supports any sentence-transformers model
  - Fast: `all-MiniLM-L6-v2` (default, 80MB)
  - Balanced: `all-mpnet-base-v2` (420MB)
  - Accurate: `all-mpnet-base-v2` or multilingual variants

---

## Validation Tools

### Scoring Parity Validation

Validates that scoring normalization is consistent across all modalities.

```bash
# Run parity validation
python tools/validation/validate_scoring_parity.py

# Verbose output
python tools/validation/validate_scoring_parity.py --verbose
```

**What it checks:**
- Normalization formulas are correct for each modality
- Quality thresholds are identical across all modalities
- Boundary conditions produce correct quality levels
- No modality has an unfair advantage

**Exit codes:**
- 0: All parity checks passed
- 1: One or more parity checks failed

### Error Log Validation

Validates contract error logs against the schema.

```bash
# Validate a log file
python tools/validation/validate_error_logs.py --log-file logs/errors.jsonl

# Custom schema path
python tools/validation/validate_error_logs.py \
    --log-file logs/errors.jsonl \
    --schema schemas/contract_error_log.schema.json

# Verbose output
python tools/validation/validate_error_logs.py \
    --log-file logs/errors.jsonl \
    --verbose
```

**Exit codes:**
- 0: All log entries are valid
- 1: One or more validation errors found

## Testing Tools

### Synthetic Traffic Generation

Generates synthetic policy analysis requests for testing runtime validators.

```bash
# Generate 100 synthetic requests
python tools/testing/generate_synthetic_traffic.py --volume 100

# Specific modalities
python tools/testing/generate_synthetic_traffic.py \
    --volume 100 \
    --modalities TYPE_A,TYPE_B,TYPE_C

# Specific policy areas
python tools/testing/generate_synthetic_traffic.py \
    --volume 100 \
    --policy-areas PA01,PA02,PA03

# Save to file (JSONL format)
python tools/testing/generate_synthetic_traffic.py \
    --volume 100 \
    --output traffic.jsonl

# Reproducible generation
python tools/testing/generate_synthetic_traffic.py \
    --volume 100 \
    --seed 42
```

**Output:**
- Statistics on requests by modality and policy area
- Minimum sample size check (10 per modality per policy area)
- Optional JSONL file with all requests

### Boot Check

Validates that all modules load correctly and runtime validators initialize.

```bash
# Run boot check
python tools/testing/boot_check.py

# Verbose output
python tools/testing/boot_check.py --verbose
```

**What it checks:**
- Core modules import successfully
- Optional modules import (non-fatal if missing)
- Orchestrator registry validates without ClassNotFoundError
- Runtime validators initialize successfully

**Exit codes:**
- 0: All boot checks passed
- 1: One or more boot checks failed

## Integration with CI

All validation tools are integrated into the CI pipeline:

### Data Contracts Workflow

```yaml
# .github/workflows/data-contracts.yml
- name: Scoring parity validation
  run: python tools/validation/validate_scoring_parity.py
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: scoring-parity
      name: Validate scoring parity
      entry: python tools/validation/validate_scoring_parity.py
      language: system
      pass_filenames: false
```

## Local Development Workflow

Before committing:

```bash
# Run all local validation checks
./scripts/validate_contracts_local.sh

# Generate synthetic traffic for testing
python tools/testing/generate_synthetic_traffic.py \
    --volume 100 \
    --output /tmp/test_traffic.jsonl

# Run boot check
python tools/testing/boot_check.py
```

## Testing

All tools have corresponding test suites:

```bash
# Test synthetic traffic generation
python -m pytest tests/operational/test_synthetic_traffic.py -v

# Test boot check functionality
python -m pytest tests/operational/test_boot_checks.py -v

# Run all operational tests
python -m pytest tests/operational/ -v
```

## Requirements

Minimum requirements:
- Python 3.10+
- jsonschema (for error log validation)

Full requirements in `requirements_atroz.txt`.

## Error Handling

All tools follow consistent error handling:

- **Exit code 0**: Success
- **Exit code 1**: Validation/test failure
- **Structured output**: JSON where applicable
- **Clear error messages**: Specific line numbers and remediation steps

## Contributing

When adding new validation or testing tools:

1. Follow the existing naming convention (`validate_*.py` or `*_check.py`)
2. Add command-line interface with `argparse`
3. Provide `--verbose` flag for detailed output
4. Return appropriate exit codes (0 for success, 1 for failure)
5. Add corresponding tests in `tests/operational/`
6. Update this README with usage examples
7. Integrate into CI workflow if appropriate

## Documentation

For detailed information on specific topics:

- **Data Contracts**: See `docs/DATA_CONTRACTS.md`
- **API Exemptions**: See `docs/API_EXEMPTIONS.md`
- **Contract Error Logging**: See `validation/contract_logger.py`
- **Error Log Schema**: See `schemas/contract_error_log.schema.json`
