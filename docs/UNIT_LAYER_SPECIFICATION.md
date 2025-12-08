# Unit Layer (@u) Evaluator - Complete Specification

## Overview

The Unit Layer evaluator assesses PDT (Plan de Desarrollo Territorial) quality through four comprehensive components: **S** (Structural Compliance), **M** (Mandatory Sections), **I** (Indicator Quality), and **P** (PPI Completeness). The system includes hard gates for critical failures and anti-gaming measures to prevent manipulation.

## Architecture

```
PDTStructure → UnitLayerEvaluator → LayerScore
                      ↓
              UnitLayerConfig
```

### Components

1. **S (Structural Compliance)**: Validates PDT document structure
2. **M (Mandatory Sections)**: Checks completeness of required sections
3. **I (Indicator Quality)**: Evaluates indicator matrix quality
4. **P (PPI Completeness)**: Assesses project portfolio completeness

## Mathematical Formulation

### S (Structural Compliance)

```
S = 0.5·B_cov + 0.25·H + 0.25·O

Where:
  B_cov = valid_blocks / 4
  H = {1.0 if ratio ≥ 0.9, 0.5 if ratio ≥ 0.6, 0.0 otherwise}
  O = {1.0 if inversions = 0, 0.5 if inversions = 1, 0.0 otherwise}
```

**Components**:
- **B_cov (Block Coverage)**: Fraction of mandatory blocks present with sufficient content
- **H (Hierarchy)**: Quality of hierarchical numbering (1.x, 1.1.x format)
- **O (Order)**: Penalty for out-of-sequence blocks

**Hard Gate**: If `S < 0.5`, return `U = 0.0` immediately

### M (Mandatory Sections)

```
M = Σ(score_i · weight_i) / Σ(weight_i)

Where:
  score_i = checks_passed / checks_total for section i
  weight_i = 2.0 for critical sections, 1.0 for others
```

**Critical Sections** (2.0x weight):
- Diagnóstico
- Parte Estratégica  
- PPI

**Regular Sections** (1.0x weight):
- Seguimiento
- Marco Normativo

**Section Scoring**:
- 1.0: All criteria met
- 0.5: Partial compliance
- 0.0: Section absent or insufficient

### I (Indicator Quality)

```
I = 0.4·I_struct + 0.3·I_link + 0.3·I_logic
```

#### I_struct (Structural Completeness)

```
For each indicator row:
  critical_score = critical_fields_present / |critical_fields|
  optional_score = optional_fields_present / |optional_fields|
  placeholder_penalty = (placeholders / |critical_fields|) × 3.0
  
  row_score = (2.0·critical_score + optional_score) / 3.0 - placeholder_penalty
  
I_struct = Σ(max(0, row_score)) / |rows|
```

**Critical Fields** (2.0x weight):
- Tipo
- Línea Estratégica
- Programa
- Línea Base
- Meta Cuatrienio
- Fuente
- Unidad Medida

**Optional Fields**:
- Año LB
- Código MGA

**Placeholders** (3.0x penalty): "S/D", "N/A", "TBD", ""

**Hard Gate**: If `I_struct < 0.7`, return `U = 0.0`

#### I_link (Traceability)

```
I_link = 0.6·fuzzy_match_ratio + 0.4·mga_valid_ratio

Where:
  fuzzy_match_ratio = rows_with_programa_linea_overlap / |rows|
  mga_valid_ratio = rows_with_valid_7digit_mga / |rows|
```

#### I_logic (Temporal Validity)

```
I_logic = 1.0 - (year_violations / |rows|)

Where year_violations counts rows with:
  - Año LB < 2015 or Año LB > 2024
  - Invalid year format
```

### P (PPI Completeness)

```
P = 0.2·P_presence + 0.4·P_struct + 0.4·P_consistency
```

#### P_presence (Presence Check)

```
P_presence = {1.0 if PPI matrix exists, 0.0 otherwise}
```

**Hard Gate**: If `require_ppi_presence = true` and not present, return `U = 0.0`

#### P_struct (Structural Completeness)

```
P_struct = nonzero_rows / |rows|

Where nonzero_rows = rows with Costo Total > 0
```

**Hard Gate**: If `P_struct < 0.7`, return `U = 0.0`

#### P_consistency (Accounting Closure)

```
For each row with Costo Total > 0:
  temporal_closure = |Σ(2024..2027) - Costo Total| / Costo Total
  source_closure = |Σ(SGP, SGR, Propios, Otras) - Costo Total| / Costo Total
  
  violations += (temporal_closure > tolerance) + (source_closure > tolerance)

P_consistency = 1.0 - violations / (|rows| × 2)
```

### Aggregation

Three methods available:

#### Geometric Mean (Recommended)

```
U_base = (S · M · I · P)^(1/4)
```

**Properties**:
- Penalizes low outliers moderately
- Balanced sensitivity across components
- Natural scale preservation

#### Harmonic Mean

```
U_base = 4 / (1/S + 1/M + 1/I + 1/P)
```

**Properties**:
- Severely penalizes low outliers
- More sensitive to weak components
- Returns 0 if any component is 0

#### Weighted Average

```
U_base = 0.25·S + 0.25·M + 0.25·I + 0.25·P
```

**Properties**:
- Linear combination
- Most lenient
- Allows weak components to be compensated

### Anti-Gaming Penalties

```
penalty = min(Σ(individual_penalties), 0.3)

U_final = max(0.0, U_base - penalty)
```

#### Penalty 1: Placeholder Ratio

```
if placeholder_ratio > 0.10:
  penalty_1 = (placeholder_ratio - 0.10) × 0.5
```

Detects excessive use of "N/A", "S/D", "TBD" in indicator fields.

#### Penalty 2: Unique Values

```
if unique_ratio < 0.5:
  penalty_2 = (0.5 - unique_ratio) × 0.3
```

Detects repetitive/copied PPI cost values.

#### Penalty 3: Number Density

```
For critical sections:
  density = number_count / token_count
  
  if density < 0.02:
    penalty_3 = (0.02 - density) × 0.2
```

Detects text padding without quantitative support.

**Total Penalty**: Capped at 0.3 to prevent over-penalization.

## Quality Classification

| Level | Threshold | Description |
|-------|-----------|-------------|
| **Sobresaliente** | U ≥ 0.85 | Outstanding quality - all components excellent |
| **Robusto** | U ≥ 0.70 | Robust quality - strong performance across components |
| **Mínimo** | U ≥ 0.50 | Minimum acceptable - meets basic requirements |
| **Insuficiente** | U < 0.50 | Insufficient quality - fails to meet standards |

## Configuration

### Component Weights

```json
{
  "w_S": 0.25,  // Structural Compliance
  "w_M": 0.25,  // Mandatory Sections
  "w_I": 0.25,  // Indicator Quality
  "w_P": 0.25   // PPI Completeness
}
```

**Constraint**: Must sum to 1.0

### Hard Gates

```json
{
  "require_ppi_presence": true,
  "require_indicator_matrix": true,
  "min_structural_compliance": 0.5,
  "i_struct_hard_gate": 0.7,
  "p_struct_hard_gate": 0.7
}
```

### Anti-Gaming Thresholds

```json
{
  "max_placeholder_ratio": 0.10,
  "min_unique_values_ratio": 0.5,
  "min_number_density": 0.02,
  "gaming_penalty_cap": 0.3
}
```

## Usage

### Basic Evaluation

```python
from farfan_pipeline.core.calibration.unit_layer import (
    UnitLayerConfig,
    UnitLayerEvaluator
)
from farfan_pipeline.core.calibration.pdt_structure import PDTStructure

# Create configuration
config = UnitLayerConfig()

# Create evaluator
evaluator = UnitLayerEvaluator(config)

# Evaluate PDT
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

print(f"Score: {result.score}")
print(f"Quality: {result.metadata['quality_level']}")
print(f"Components: S={result.components['S']:.2f}, "
      f"M={result.components['M']:.2f}, "
      f"I={result.components['I']:.2f}, "
      f"P={result.components['P']:.2f}")
```

### Custom Configuration

```python
from farfan_pipeline.core.calibration.unit_layer_loader import (
    load_unit_layer_config
)

# Load from JSON
config = load_unit_layer_config("path/to/config.json")

# Or create with custom parameters
config = UnitLayerConfig(
    aggregation_type="harmonic_mean",
    min_structural_compliance=0.6,
    i_struct_hard_gate=0.75,
    gaming_penalty_cap=0.4
)

evaluator = UnitLayerEvaluator(config)
```

## Hard Gate Decision Flow

```
START
  ↓
Compute S
  ↓
S < 0.5? → YES → Return U=0.0 (structural failure)
  ↓ NO
Compute M
  ↓
Compute I (I_struct, I_link, I_logic)
  ↓
I_struct < 0.7? → YES → Return U=0.0 (indicator failure)
  ↓ NO
Compute P (P_presence, P_struct, P_consistency)
  ↓
PPI not present? → YES → Return U=0.0 (ppi absence)
  ↓ NO
Indicator matrix not present? → YES → Return U=0.0 (indicator absence)
  ↓ NO
P_struct < 0.7? → YES → Return U=0.0 (ppi structure failure)
  ↓ NO
Aggregate S, M, I, P → U_base
  ↓
Compute gaming penalties → penalty
  ↓
U_final = max(0.0, U_base - penalty)
  ↓
Classify quality level
  ↓
Return LayerScore
```

## Validation Rules

### PDT Structure Validation

1. **Mandatory blocks** must be present:
   - Diagnóstico (≥100 tokens, ≥3 numbers)
   - Parte Estratégica (≥100 tokens, ≥3 numbers)
   - PPI (≥100 tokens, ≥3 numbers)
   - Seguimiento (≥100 tokens, ≥3 numbers)

2. **Headers** should follow numbering scheme:
   - Level 1: "1.", "2.", "3.", ...
   - Level 2: "1.1", "1.2", ...
   - Level 3: "1.1.1", "1.1.2", ...

3. **Block sequence** should follow canonical order

### Section Validation

Each section checked for:
- **Token count**: Minimum word count threshold
- **Keyword matches**: Domain-specific terms present
- **Number count**: Quantitative data present
- **Sources** (Diagnóstico only): Citations present

### Indicator Matrix Validation

1. **Critical fields** must be present and non-placeholder
2. **MGA codes** must be 7-digit numeric
3. **Year values** must be in range [2015, 2024]
4. **Traceability**: Programa should overlap with Línea Estratégica

### PPI Matrix Validation

1. **Temporal closure**: `Σ(2024..2027) ≈ Costo Total`
2. **Source closure**: `SGP + SGR + Propios + Otras ≈ Costo Total`
3. **Non-zero rows**: At least 80% should have `Costo Total > 0`

## Implementation Notes

### Performance

- **Time Complexity**: O(n) where n = total indicators + PPI rows
- **Space Complexity**: O(n) for storing structures
- **Typical Runtime**: <100ms for standard PDT

### Determinism

- All computations are deterministic
- No random sampling or probabilistic elements
- Same input always produces same output

### Extensibility

To add new components:

1. Add config parameters to `UnitLayerConfig`
2. Implement computation method in `UnitLayerEvaluator`
3. Update aggregation formula
4. Add corresponding tests
5. Document in JSON config

### Logging

Structured logging at key points:
- `unit_layer_evaluation_start`: Begin evaluation
- `S_computed`: Structural compliance computed
- `M_computed`: Mandatory sections computed
- `I_computed`: Indicator quality computed
- `P_computed`: PPI completeness computed
- `U_base_computed`: Base score before penalties
- `indicator_matrix_absent`: Warning when matrix missing

## Testing

Run comprehensive test suite:

```bash
pytest tests/calibration_system/test_unit_layer.py -v
pytest tests/calibration_system/test_unit_layer_config_loader.py -v
```

Run sample evaluations:

```bash
python tests/calibration_system/sample_evaluations/run_sample_evaluations.py
```

## References

- Configuration: `system/config/calibration/unit_layer_config.json`
- Implementation: `src/farfan_pipeline/core/calibration/unit_layer.py`
- Tests: `tests/calibration_system/test_unit_layer.py`
- Samples: `tests/calibration_system/sample_evaluations/`

## Changelog

### Version 1.0.0 (2024-12-07)

- Initial implementation
- S/M/I/P components with full specification
- Hard gates for critical failures
- Anti-gaming penalties with cap
- Geometric/harmonic/weighted aggregation
- Comprehensive test coverage
- Sample evaluations and documentation
