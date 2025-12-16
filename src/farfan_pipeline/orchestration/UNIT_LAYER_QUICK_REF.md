# Unit Layer (@u) - Quick Reference Card

## Formula Summary

```
S = 0.5·B_cov + 0.25·H + 0.25·O
M = weighted_average(diagnostico×2.0, estrategica×2.0, ppi×2.0, seguimiento×1.0)
I = 0.4·I_struct + 0.3·I_link + 0.3·I_logic  [GATE: I ≥ 0.7]
P = 0.2·presence + 0.4·struct + 0.4·consistency  [GATE: P ≥ 0.7]

U_raw = geometric_mean(S, M, I, P)
U_final = max(0, U_raw - min(penalty, 0.3))
```

## Component Breakdown

### S (Structural Compliance)
- **B_cov**: Block coverage (4 required: Diagnóstico, Estratégica, PPI, Seguimiento)
- **H**: Header quality (valid numbering)
- **O**: Ordering quality (correct sequence)

### M (Mandatory Sections) - Critical Weights
| Section | Weight | Min Tokens |
|---------|--------|------------|
| Diagnóstico | 2.0× | 1000 |
| Estratégica | 2.0× | 1000 |
| PPI | 2.0× | 500 |
| Seguimiento | 1.0× | 300 |

### I (Indicator Quality) - Hard Gate @ 0.7
- **I_struct**: Structure completeness (min 5 indicators)
- **I_link**: Linkage to strategic lines/programs
- **I_logic**: Temporal validity (baseline 2019-2024)

### P (PPI Completeness) - Hard Gate @ 0.7
- **presence**: Matrix exists (min 3 rows)
- **struct**: All budget fields present
- **consistency**: Accounting check (1% tolerance)

## Anti-Gaming Detection

| Source | Terms | Multiplier |
|--------|-------|------------|
| Indicators | "S/D", "Sin Dato", "No especificado", "N/A" | 3.0× |
| PPI | null, 0 in critical fields | 2.0× |

**Cap**: 0.3 maximum penalty

## Quick Checks

### ✓ Pass Criteria
- [ ] All 4 blocks present
- [ ] S ≥ 0.5
- [ ] M ≥ 0.5
- [ ] I ≥ 0.7 (HARD GATE)
- [ ] P ≥ 0.7 (HARD GATE)
- [ ] Minimal placeholders
- [ ] U_final ≥ 0.6

### ✗ Reject Triggers
- Missing blocks → Low S
- < 5 indicators → I gate fail
- < 3 PPI rows → P gate fail
- Accounting error > 1% → Low P
- Heavy placeholders → High penalty
- Any component = 0 → U_final = 0

## Usage Patterns

### Standard Evaluation
```python
from src.orchestration.unit_layer import UnitLayerEvaluator, create_default_config

evaluator = UnitLayerEvaluator(create_default_config())
result = evaluator.evaluate(pdt)
print(f"U_final: {result['U_final']:.3f}")
```

### Custom Weights
```python
from src.orchestration.unit_layer import UnitLayerConfig, UnitLayerEvaluator

config = UnitLayerConfig(
    w_m_diagnostico=3.0,  # Increase diagnostic importance
    i_hard_gate=0.65,     # Relax indicator gate
    anti_gaming_cap=0.25  # Lower penalty cap
)
evaluator = UnitLayerEvaluator(config)
```

### Gate Check
```python
result = evaluator.evaluate(pdt)
if not result['indicator_quality']['gate_passed']:
    print("REJECTED: Insufficient indicator quality")
if not result['ppi_completeness']['gate_passed']:
    print("REJECTED: Insufficient PPI completeness")
```

## Scoring Rubric

| Score | Interpretation |
|-------|----------------|
| 0.9-1.0 | Excellent - Publication ready |
| 0.8-0.9 | Good - Minor improvements needed |
| 0.7-0.8 | Acceptable - Passes gates |
| 0.5-0.7 | Poor - Significant gaps |
| 0.0-0.5 | Rejected - Major deficiencies |

## Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing blocks | B_cov < 1.0 | Add required sections |
| Invalid headers | H = 0.0 | Fix numbering (1., 1.1, etc.) |
| Wrong order | O < 1.0 | Reorder: Diag→Estr→PPI→Seg |
| Gate failure | I or P = 0.0 | Add complete indicators/PPI |
| High penalty | penalty = 0.3 | Remove placeholder data |
| U_final = 0 | Any component = 0 | Check gates, fix zeros |

## Files

- **Implementation**: `src/orchestration/unit_layer.py`
- **COHORT_2024**: `calibration/COHORT_2024_unit_layer.py`
- **Examples**: `src/orchestration/unit_layer_example.py`
- **Tests**: `tests/test_unit_layer.py`
- **Docs**: `src/orchestration/UNIT_LAYER_README.md`
