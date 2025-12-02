# End-to-End Deterministic Pipeline Integration Tests

## Overview

The `test_pipeline_e2e_deterministic.py` module provides comprehensive end-to-end integration tests for the F.A.R.F.A.N pipeline, validating deterministic execution from Phase 0 through Phase 9 with full provenance tracking and BLAKE3 cryptographic hash validation.

## Test Coverage

### 1. Complete Phase Execution (Phase 0-9)

**Test**: `test_phase_0_to_9_execution_with_fixed_seed`

Validates the complete pipeline execution with a 150-page test document:

- **Phase 0**: Input validation (PDF + questionnaire)
- **Phase 1**: SPC (Smart Policy Chunks) ingestion with 15 subphases
- **Adapter**: CanonPolicyPackage → PreprocessedDocument transformation
- **Phase 2**: Micro-questions execution (305 questions)
- **Phases 3-9**: Scoring, aggregation, recommendations, and report generation

**Assertions**:
- Pipeline success flag is True
- At least 4 phases completed (0, 1, adapter, 2)
- No phase failures
- PDF page count = 150
- SHA256 hashes (64 chars) for PDF and questionnaire
- Chunk graph present in CanonPolicyPackage
- Chunked processing mode active
- Questions produced by Phase 2
- Manifest structure complete

### 2. BLAKE3 Hash Stability

**Test**: `test_blake3_phase_hash_stability`

Verifies cryptographic hash stability across multiple runs with the same input:

- Executes pipeline twice with identical inputs
- Computes BLAKE3 hashes of Phase 0 canonical input
- Validates hash determinism (same input → same hash)
- Ensures 64-character hex hash format

**Purpose**: Guarantees reproducibility for audit trails and regulatory compliance.

### 3. Verification Manifest Structure

**Test**: `test_verification_manifest_structure`

Validates the `verification_manifest.json` structure and completeness:

**Top-level fields**:
- `phases`: Phase execution dictionary
- `total_phases`: Total phase count
- `successful_phases`: Success count
- `failed_phases`: Failure count

**Per-phase fields**:
- `status`: "success" or "failed"
- `started_at`: ISO 8601 timestamp
- `finished_at`: ISO 8601 timestamp
- `duration_ms`: Execution duration in milliseconds
- `input_contract`: Input validation results
- `output_contract`: Output validation results
- `invariants_checked`: List of invariants validated
- `artifacts`: Phase artifacts (paths, hashes)

**Assertions**:
- All required phases present (phase0, phase1, adapter)
- Contract validation passed for all phases
- Manifest saved to `phase_manifest.json`
- Valid JSON structure

### 4. Failure Propagation (ABORT on Error)

**Test**: `test_phase_failure_propagation_abort`

Tests failure propagation and pipeline abort behavior:

- Provides non-existent PDF path to force Phase 0 failure
- Validates pipeline abort (success = False)
- Confirms error messages captured
- Verifies phase failure count > 0
- Ensures manifest generated even on failure
- Validates Phase 0 status = "failed" in manifest

**Purpose**: Ensures pipeline fails fast and propagates errors correctly.

### 5. Provenance Completeness

**Test**: `test_provenance_completeness`

Validates provenance tracking across all chunks:

**Metrics**:
- `provenance_completeness = chunks_with_provenance / total_chunks`
- **Target**: 1.0 (100% coverage)

**Per-chunk validation**:
- Provenance object exists
- Page number > 0
- Page number ≤ 150 (document bounds)
- Section headers present (where applicable)

**Purpose**: Guarantees full traceability for regulatory compliance.

### 6. Phase Hash Collection

**Test**: `test_phase_hash_collection_all_phases`

Collects and validates BLAKE3 hashes for all successful phases:

**Hash inputs**:
- Phase name
- Duration (ms)
- Start timestamp

**Assertions**:
- All hashes are 64-character hex strings
- At least 3 phases have hashes (0, 1, adapter)
- Hash format consistent across all phases

## Test Document Generation

### 150-Page Test PDF

The `generate_150_page_test_pdf` fixture creates a realistic 150-page municipal development plan with:

**Content types** (cycled every 6 pages):
1. **Diagnostic**: Gap analysis, situational assessment
2. **Activity**: Implementation programs, coordination
3. **Indicator**: Metrics, targets, baselines
4. **Resource**: Budget, personnel, equipment
5. **Temporal**: Timelines, milestones, schedules
6. **Entity**: Organizations, stakeholders, responsibilities

**Purpose**: Simulates real-world policy documents with diverse chunk types.

## Running the Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

### Execute Tests

```bash
# Run all e2e tests
pytest tests/integration/test_pipeline_e2e_deterministic.py -v

# Run specific test
pytest tests/integration/test_pipeline_e2e_deterministic.py::TestPipelineE2EDeterministic::test_blake3_phase_hash_stability -v

# Run with coverage
pytest tests/integration/test_pipeline_e2e_deterministic.py -v --cov=farfan_core --cov-report=term-missing

# Run with detailed output
pytest tests/integration/test_pipeline_e2e_deterministic.py -vv -s
```

### Test Execution Time

- **Phase 0-2 execution**: ~30-60 seconds (150-page PDF)
- **Full pipeline (Phase 0-9)**: ~2-5 minutes (depending on hardware)
- **Hash stability test**: ~1-2 minutes (2x full pipeline)

## Determinism Guarantees

### Fixed Seed (seed=42)

All tests use `seed=42` for deterministic execution:

- Random number generation
- Model initialization
- Sampling operations
- Shuffling operations

### BLAKE3 Hash Properties

- **Algorithm**: BLAKE3 (cryptographic hash function)
- **Output**: 256-bit (64 hex characters)
- **Speed**: Faster than SHA-256, similar security
- **Determinism**: Same input → same hash (guaranteed)

### Reproducibility Requirements

1. **Fixed seed**: Consistent across all components
2. **Sorted keys**: JSON serialization with `sort_keys=True`
3. **Canonical format**: `separators=(',', ':')`
4. **Immutable inputs**: No in-place mutations
5. **Platform-independent**: Works on Linux, macOS, Windows

## Manifest Schema

### Example `phase_manifest.json`

```json
{
  "phases": {
    "phase0_input_validation": {
      "status": "success",
      "started_at": "2025-01-19T10:30:00.000Z",
      "finished_at": "2025-01-19T10:30:02.500Z",
      "duration_ms": 2500.0,
      "input_contract": {
        "validation_passed": true,
        "errors": [],
        "warnings": []
      },
      "output_contract": {
        "validation_passed": true,
        "errors": [],
        "warnings": []
      },
      "invariants_checked": [
        "validation_passed",
        "pdf_page_count_positive",
        "pdf_size_positive",
        "sha256_format",
        "no_validation_errors"
      ],
      "invariants_satisfied": true,
      "artifacts": [],
      "error": null
    },
    "phase1_spc_ingestion": {
      "status": "success",
      "started_at": "2025-01-19T10:30:02.500Z",
      "finished_at": "2025-01-19T10:30:45.000Z",
      "duration_ms": 42500.0,
      "input_contract": {
        "validation_passed": true
      },
      "output_contract": {
        "validation_passed": true
      },
      "invariants_checked": [
        "chunk_count_in_range",
        "all_chunks_have_provenance",
        "policy_area_coverage"
      ],
      "invariants_satisfied": true,
      "artifacts": []
    }
  },
  "total_phases": 4,
  "successful_phases": 4,
  "failed_phases": 0
}
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run E2E Deterministic Tests
  run: |
    pytest tests/integration/test_pipeline_e2e_deterministic.py \
      -v \
      --cov=farfan_core \
      --cov-report=xml \
      --junitxml=test-results/e2e-results.xml
  
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
    flags: integration
```

## Troubleshooting

### Test Failures

**Issue**: `PyMuPDF not available`
```bash
pip install PyMuPDF
```

**Issue**: `Questionnaire not found`
```bash
# Ensure questionnaire file exists
export QUESTIONNAIRE_FILE=/path/to/questionnaire.json
```

**Issue**: `Pipeline timeout`
```bash
# Increase timeout in phase_orchestrator.py
PHASE_TIMEOUT_DEFAULT = 600  # 10 minutes
```

### Performance Optimization

- Use SSD for artifact storage
- Allocate sufficient RAM (>4GB)
- Run on machines with 4+ CPU cores
- Use `pytest-xdist` for parallel execution:
  ```bash
  pytest tests/integration/ -n auto
  ```

## References

- [BLAKE3 Specification](https://github.com/BLAKE3-team/BLAKE3-specs)
- [Phase Contract Protocol](../../farfan_core/farfan_core/core/phases/phase_protocol.py)
- [Phase Orchestrator](../../farfan_core/farfan_core/core/phases/phase_orchestrator.py)
- [Verification Manifest](../../farfan_core/farfan_core/core/orchestrator/verification_manifest.py)

## Authors

- F.A.R.F.A.N Test Team
- Date: 2025-01-19
