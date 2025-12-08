# Unit Layer (@u) Quick Reference

## Component Formulas (Cheat Sheet)

### S - Structural Compliance
```
S = 0.5·B_cov + 0.25·H + 0.25·O
```
- **B_cov**: valid_blocks/4
- **H**: {1.0, 0.5, 0.0} hierarchy quality
- **O**: {1.0, 0.5, 0.0} order penalty
- **Hard Gate**: S < 0.5 → U = 0.0

### M - Mandatory Sections
```
M = weighted_average(section_scores)
```
- **Critical sections** (2x): Diagnóstico, Estratégica, PPI
- **Regular sections** (1x): Seguimiento, Marco Normativo
- **Scoring**: {1.0 full, 0.5 partial, 0.0 absent}

### I - Indicator Quality
```
I = 0.4·I_struct + 0.3·I_link + 0.3·I_logic
```
- **I_struct**: Field completeness - placeholder penalty
- **I_link**: Fuzzy match (60%) + MGA validation (40%)
- **I_logic**: 1.0 - (year_violations/rows)
- **Hard Gate**: I_struct < 0.7 → U = 0.0

### P - PPI Completeness
```
P = 0.2·P_presence + 0.4·P_struct + 0.4·P_consistency
```
- **P_presence**: {1.0 exists, 0.0 absent}
- **P_struct**: nonzero_rows/total_rows
- **P_consistency**: 1.0 - (violations/(rows×2))
- **Hard Gates**: 
  - Not present → U = 0.0
  - P_struct < 0.7 → U = 0.0

### Aggregation
```
geometric_mean:    U = (S·M·I·P)^(1/4)         [Recommended]
harmonic_mean:     U = 4/(1/S + 1/M + 1/I + 1/P)
weighted_average:  U = 0.25·(S + M + I + P)
```

### Anti-Gaming
```
penalty = min(Σ penalties, 0.3)

Checks:
1. placeholder_ratio > 10%
2. unique_values_ratio < 50%
3. number_density < 0.02

U_final = max(0.0, U_base - penalty)
```

## Quality Thresholds

| Score | Level | Description |
|-------|-------|-------------|
| ≥0.85 | **Sobresaliente** | Outstanding |
| ≥0.70 | **Robusto** | Robust |
| ≥0.50 | **Mínimo** | Minimum |
| <0.50 | **Insuficiente** | Insufficient |

## Hard Gates (Immediate U=0.0)

1. ❌ S < 0.5 (structural failure)
2. ❌ I_struct < 0.7 (poor indicators)
3. ❌ PPI not present (missing matrix)
4. ❌ Indicator matrix not present
5. ❌ P_struct < 0.7 (empty PPI)

## Default Configuration

```json
{
  "weights": {"w_S": 0.25, "w_M": 0.25, "w_I": 0.25, "w_P": 0.25},
  "aggregation": "geometric_mean",
  "hard_gates": {
    "min_structural_compliance": 0.5,
    "i_struct_hard_gate": 0.7,
    "p_struct_hard_gate": 0.7
  },
  "anti_gaming": {
    "max_placeholder_ratio": 0.10,
    "min_unique_values_ratio": 0.5,
    "min_number_density": 0.02,
    "gaming_penalty_cap": 0.3
  }
}
```

## Usage Example

```python
from farfan_pipeline.core.calibration.unit_layer import (
    UnitLayerConfig, UnitLayerEvaluator
)
from farfan_pipeline.core.calibration.pdt_structure import PDTStructure

# Setup
config = UnitLayerConfig()
evaluator = UnitLayerEvaluator(config)

# Evaluate
pdt = PDTStructure(...)
result = evaluator.evaluate(pdt)

# Results
print(f"U = {result.score:.2f}")
print(f"Quality: {result.metadata['quality_level']}")
print(f"S={result.components['S']:.2f} "
      f"M={result.components['M']:.2f} "
      f"I={result.components['I']:.2f} "
      f"P={result.components['P']:.2f}")
```

## Critical Fields

### Indicator Matrix
**Critical** (2x weight): Tipo, Línea Estratégica, Programa, Línea Base, Meta Cuatrienio, Fuente, Unidad Medida  
**Optional**: Año LB, Código MGA  
**Placeholders** (3x penalty): "S/D", "N/A", "TBD", ""

### PPI Matrix
**Required**: Línea Estratégica, Programa, Costo Total, 2024, 2025, 2026, 2027, SGP, SGR, Propios, Otras  
**Validation**: Temporal sum = Source sum = Costo Total (±1%)

## Section Requirements

| Section | Tokens | Keywords | Numbers | Sources | Weight |
|---------|--------|----------|---------|---------|--------|
| Diagnóstico | ≥800 | ≥3 | ≥10 | ≥2 | 2.0x |
| Estratégica | ≥600 | ≥2 | ≥5 | - | 2.0x |
| PPI | ≥400 | ≥2 | ≥8 | - | 2.0x |
| Seguimiento | ≥300 | ≥2 | ≥3 | - | 1.0x |
| Marco Normativo | ≥200 | ≥1 | - | - | 1.0x |

## Files

- **Config**: `system/config/calibration/unit_layer_config.json`
- **Code**: `src/farfan_pipeline/core/calibration/unit_layer.py`
- **Tests**: `tests/calibration_system/test_unit_layer.py`
- **Samples**: `tests/calibration_system/sample_evaluations/`
- **Docs**: `docs/UNIT_LAYER_SPECIFICATION.md`

## Testing

```bash
# Unit tests
pytest tests/calibration_system/test_unit_layer.py -v

# Config loader tests
pytest tests/calibration_system/test_unit_layer_config_loader.py -v

# Sample evaluations
python tests/calibration_system/sample_evaluations/run_sample_evaluations.py
```

## Troubleshooting

### Score is 0.0
- Check hard gates in result.components
- Look for "gate_failure" key
- Review result.rationale

### Score lower than expected
- Check individual components (S, M, I, P)
- Look at result.components['penalty']
- Review gaming flags

### Config errors
- Ensure weights sum to 1.0
- Verify aggregation_type is valid
- Check threshold ranges [0,1]

## Common Patterns

### Disable PPI requirement
```python
config = UnitLayerConfig(require_ppi_presence=False)
```

### Use harmonic mean
```python
config = UnitLayerConfig(aggregation_type="harmonic_mean")
```

### Stricter thresholds
```python
config = UnitLayerConfig(
    min_structural_compliance=0.6,
    i_struct_hard_gate=0.75,
    p_struct_hard_gate=0.75
)
```

### Custom section weights
```python
config = UnitLayerConfig(
    w_S=0.3,
    w_M=0.3,
    w_I=0.2,
    w_P=0.2
)
```
