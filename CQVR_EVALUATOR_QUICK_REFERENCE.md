# CQVR Evaluator - Quick Reference

## Usage

```bash
# Single contract
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json

# Batch (1-12, each = 25 contracts)
python scripts/cqvr_evaluator_standalone.py --batch 1

# Range
python scripts/cqvr_evaluator_standalone.py --range 1 30

# All 300
python scripts/cqvr_evaluator_standalone.py --all

# Quiet mode (JSON only)
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json --quiet
```

## Scoring Functions (Total: 100 pts)

### Tier 1: Critical (55 pts)
- **A1** (20): Identity-Schema coherence
- **A2** (20): Method-Assembly alignment  
- **A3** (10): Signal requirements
- **A4** (5): Output schema

### Tier 2: Functional (30 pts)
- **B1** (10): Pattern coverage
- **B2** (10): Method specificity
- **B3** (10): Validation rules

### Tier 3: Quality (15 pts)
- **C1** (5): Documentation quality
- **C2** (5): Human template
- **C3** (5): Metadata completeness

## Decision Logic

| Decision | Criteria |
|----------|----------|
| **PRODUCCION** | tier1 ≥ 45 AND total ≥ 80 |
| **PARCHEAR** | tier1 ≥ 35 AND (total ≥ 70 OR blockers ≤ 2) |
| **REFORMULAR** | tier1 < 35 OR other failures |

## Testing

```bash
# Run all tests
pytest tests/test_cqvr_evaluator.py -v -m updated

# Expected: 25 passed in ~0.1s
```

## Files

- **Script**: `scripts/cqvr_evaluator_standalone.py` (1,140 lines)
- **Tests**: `tests/test_cqvr_evaluator.py` (666 lines)
- **Docs**: `docs/CQVR_EVALUATOR_STANDALONE.md` (331 lines)
- **Summary**: `CQVR_EVALUATOR_IMPLEMENTATION_SUMMARY.md` (250 lines)

## Key Features

✅ Deterministic scoring  
✅ JSON + Rich console output  
✅ Error handling for malformed contracts  
✅ Zero required dependencies (Rich optional)  
✅ All 10 functions with explicit signatures  
✅ 25 comprehensive unit tests

## Exit Codes

- `0`: Success
- `1`: Errors (malformed contracts, missing files, etc.)

## Output

**JSON**: `reports/cqvr_evaluation/cqvr_evaluation.json`  
**Console**: Rich tables with summary statistics
