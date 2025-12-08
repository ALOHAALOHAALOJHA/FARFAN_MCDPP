# Unit Layer (@u) - Complete Implementation Index

## Quick Navigation

### 📚 Documentation
- **[Complete Specification](UNIT_LAYER_SPECIFICATION.md)** - Full mathematical formulation and implementation details
- **[Quick Reference](UNIT_LAYER_QUICK_REFERENCE.md)** - Formulas, thresholds, and usage patterns at a glance
- **[Implementation Summary](../UNIT_LAYER_IMPLEMENTATION_COMPLETE.md)** - Complete implementation status and file manifest

### 💻 Implementation
- **Main Evaluator**: `src/farfan_pipeline/core/calibration/unit_layer.py`
  - `UnitLayerConfig` - Configuration dataclass
  - `UnitLayerEvaluator` - Main evaluation engine
  - `LayerScore` - Result structure

- **Configuration Loader**: `src/farfan_pipeline/core/calibration/unit_layer_loader.py`
  - `load_unit_layer_config()` - Load from JSON
  - `save_unit_layer_config()` - Save to JSON

- **Data Structure**: `src/farfan_pipeline/core/calibration/pdt_structure.py`
  - `PDTStructure` - Input data schema

### ⚙️ Configuration
- **Default Config**: `system/config/calibration/unit_layer_config.json`
  - Component weights
  - Aggregation settings
  - Hard gates
  - Anti-gaming thresholds
  - All S/M/I/P parameters

### 🧪 Testing
- **Unit Tests**: `tests/calibration_system/test_unit_layer.py`
  - Configuration validation
  - S/M/I/P component tests
  - Aggregation tests
  - Hard gate tests
  - Anti-gaming tests
  - End-to-end tests

- **Config Tests**: `tests/calibration_system/test_unit_layer_config_loader.py`
  - Load/save tests
  - Validation tests
  - Round-trip tests

### 📊 Sample Evaluations
**Directory**: `tests/calibration_system/sample_evaluations/`

- **[README](../tests/calibration_system/sample_evaluations/README.md)** - Sample evaluation guide
- **excellent_pdt.json** - Sobresaliente quality (U ≥ 0.85)
- **minimal_pdt.json** - Mínimo quality (0.5 ≤ U < 0.7)
- **insufficient_pdt.json** - Insuficiente quality (U < 0.5)
- **gaming_attempt_pdt.json** - Gaming detection demo
- **hard_gate_failure_pdt.json** - All hard gate scenarios
- **run_sample_evaluations.py** - Interactive runner

## Component Overview

### S (Structural Compliance)
**Formula**: `S = 0.5·B_cov + 0.25·H + 0.25·O`

Validates:
- Block coverage (4 mandatory blocks)
- Hierarchy numbering quality
- Block sequence ordering

**Hard Gate**: S < 0.5 → U = 0.0

### M (Mandatory Sections)
**Formula**: `M = weighted_average(section_scores)`

Validates:
- Diagnóstico (2x weight)
- Parte Estratégica (2x weight)
- PPI (2x weight)
- Seguimiento (1x weight)
- Marco Normativo (1x weight)

### I (Indicator Quality)
**Formula**: `I = 0.4·I_struct + 0.3·I_link + 0.3·I_logic`

Validates:
- Field completeness (critical 2x weight)
- Programa-Línea linkage
- MGA code format (7-digit)
- Year range validity (2015-2024)

**Hard Gate**: I_struct < 0.7 → U = 0.0

### P (PPI Completeness)
**Formula**: `P = 0.2·P_presence + 0.4·P_struct + 0.4·P_consistency`

Validates:
- Matrix presence
- Non-zero row ratio (≥80%)
- Temporal sum closure
- Source sum closure

**Hard Gates**: 
- Not present → U = 0.0
- P_struct < 0.7 → U = 0.0

## Usage Quick Start

### 1. Basic Evaluation

```python
from farfan_pipeline.core.calibration.unit_layer import (
    UnitLayerConfig,
    UnitLayerEvaluator
)
from farfan_pipeline.core.calibration.pdt_structure import PDTStructure

# Setup
config = UnitLayerConfig()
evaluator = UnitLayerEvaluator(config)

# Evaluate
pdt = PDTStructure(
    full_text="...",
    total_tokens=5000,
    blocks_found={...},
    sections_found={...},
    indicator_matrix_present=True,
    indicator_rows=[...],
    ppi_matrix_present=True,
    ppi_rows=[...]
)

result = evaluator.evaluate(pdt)

# Results
print(f"U = {result.score:.2f}")
print(f"Quality: {result.metadata['quality_level']}")
print(f"S={result.components['S']:.2f} "
      f"M={result.components['M']:.2f} "
      f"I={result.components['I']:.2f} "
      f"P={result.components['P']:.2f}")
```

### 2. Load Configuration

```python
from farfan_pipeline.core.calibration.unit_layer_loader import (
    load_unit_layer_config
)

# Load from default location
config = load_unit_layer_config()

# Or from custom path
config = load_unit_layer_config("path/to/config.json")
```

### 3. Run Tests

```bash
# All unit layer tests
pytest tests/calibration_system/test_unit_layer.py -v

# Sample evaluations
python tests/calibration_system/sample_evaluations/run_sample_evaluations.py
```

## Key Formulas

### Aggregation Methods

| Method | Formula |
|--------|---------|
| Geometric (recommended) | `U = (S·M·I·P)^(1/4)` |
| Harmonic | `U = 4/(1/S + 1/M + 1/I + 1/P)` |
| Weighted | `U = 0.25·(S + M + I + P)` |

### Anti-Gaming

```
penalty = min(
    placeholder_penalty + 
    unique_values_penalty + 
    number_density_penalty,
    0.3
)

U_final = max(0.0, U_base - penalty)
```

## Quality Thresholds

| Level | Range | Description |
|-------|-------|-------------|
| **Sobresaliente** | U ≥ 0.85 | Outstanding quality |
| **Robusto** | 0.70 ≤ U < 0.85 | Robust quality |
| **Mínimo** | 0.50 ≤ U < 0.70 | Minimum acceptable |
| **Insuficiente** | U < 0.50 | Insufficient quality |

## Hard Gates (Immediate Failure)

1. ❌ **Structural**: S < 0.5
2. ❌ **Indicator Structure**: I_struct < 0.7
3. ❌ **PPI Presence**: Matrix missing (if required)
4. ❌ **Indicator Presence**: Matrix missing (if required)
5. ❌ **PPI Structure**: P_struct < 0.7

## File Locations

```
farfan_pipeline/
├── docs/
│   ├── UNIT_LAYER_INDEX.md              ← You are here
│   ├── UNIT_LAYER_SPECIFICATION.md      ← Full spec
│   └── UNIT_LAYER_QUICK_REFERENCE.md    ← Quick guide
│
├── src/farfan_pipeline/core/calibration/
│   ├── unit_layer.py                    ← Main implementation
│   ├── unit_layer_loader.py             ← Config loader
│   └── pdt_structure.py                 ← Input schema
│
├── system/config/calibration/
│   └── unit_layer_config.json           ← Configuration
│
├── tests/calibration_system/
│   ├── test_unit_layer.py               ← Unit tests
│   ├── test_unit_layer_config_loader.py ← Config tests
│   └── sample_evaluations/
│       ├── README.md                     ← Sample guide
│       ├── excellent_pdt.json
│       ├── minimal_pdt.json
│       ├── insufficient_pdt.json
│       ├── gaming_attempt_pdt.json
│       ├── hard_gate_failure_pdt.json
│       └── run_sample_evaluations.py
│
└── UNIT_LAYER_IMPLEMENTATION_COMPLETE.md ← Summary
```

## Common Tasks

### Customize Configuration

```python
config = UnitLayerConfig(
    # Adjust weights (must sum to 1.0)
    w_S=0.3,
    w_M=0.3,
    w_I=0.2,
    w_P=0.2,
    
    # Change aggregation
    aggregation_type="harmonic_mean",
    
    # Adjust hard gates
    min_structural_compliance=0.6,
    i_struct_hard_gate=0.75,
    
    # Tune anti-gaming
    max_placeholder_ratio=0.15,
    gaming_penalty_cap=0.4
)
```

### Disable PPI Requirement

```python
config = UnitLayerConfig(
    require_ppi_presence=False,
    require_indicator_matrix=False
)
```

### Export Custom Config

```python
from farfan_pipeline.core.calibration.unit_layer_loader import (
    save_unit_layer_config
)

config = UnitLayerConfig(...)
save_unit_layer_config(config, "custom_config.json")
```

## Troubleshooting

### Score is 0.0
1. Check `result.components` for gate failures
2. Look for `gate_failure` key
3. Read `result.rationale` for explanation

### Lower than expected score
1. Check individual components: S, M, I, P
2. Examine `result.components['penalty']`
3. Review gaming detection flags

### Configuration errors
1. Ensure component weights sum to 1.0
2. Verify aggregation_type is valid
3. Check threshold values are in [0,1]

## Testing Strategy

### Unit Tests (test_unit_layer.py)
- ✅ Config validation
- ✅ S component computation
- ✅ M component computation
- ✅ I component computation
- ✅ P component computation
- ✅ All aggregation methods
- ✅ Hard gate enforcement
- ✅ Anti-gaming detection
- ✅ End-to-end flows

### Integration Tests (sample_evaluations/)
- ✅ Excellent PDT evaluation
- ✅ Minimal PDT evaluation
- ✅ Insufficient PDT evaluation
- ✅ Gaming detection
- ✅ All hard gate scenarios

## Performance

- **Time**: O(n) where n = indicators + PPI rows
- **Space**: O(n) for data structures
- **Typical**: <100ms per evaluation
- **Deterministic**: Same input → same output

## Version History

### 1.0.0 (2024-12-07)
- ✅ Initial implementation
- ✅ S/M/I/P components
- ✅ Hard gates
- ✅ Anti-gaming measures
- ✅ Configuration system
- ✅ Comprehensive tests
- ✅ Sample evaluations
- ✅ Complete documentation

## Support

For questions or issues:
1. Read [Complete Specification](UNIT_LAYER_SPECIFICATION.md)
2. Check [Quick Reference](UNIT_LAYER_QUICK_REFERENCE.md)
3. Review sample evaluations
4. Run unit tests
5. Check [Implementation Summary](../UNIT_LAYER_IMPLEMENTATION_COMPLETE.md)

## License

Part of the F.A.R.F.A.N Mechanistic Policy Pipeline project.
