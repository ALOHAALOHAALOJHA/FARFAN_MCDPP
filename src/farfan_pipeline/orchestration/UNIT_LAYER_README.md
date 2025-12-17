# Unit Layer (@u) Evaluator

## Overview

The Unit Layer (@u) evaluator assesses the quality and completeness of PDT (Plan de Desarrollo Territorial) documents through comprehensive structure analysis. It computes a final score `U_final` using a geometric mean of four components with anti-gaming penalties.

## Architecture

### Core Components

1. **S (Structural Compliance)**: `0.5·B_cov + 0.25·H + 0.25·O`
   - `B_cov`: Block coverage (presence of required sections)
   - `H`: Header quality (numbering validation)
   - `O`: Ordering quality (proper sequence)

2. **M (Mandatory Sections)**: Weighted section scoring with critical weights
   - Diagnóstico: 2.0x weight
   - Parte Estratégica: 2.0x weight
   - PPI: 2.0x weight
   - Seguimiento: 1.0x weight

3. **I (Indicator Quality)**: `0.4·I_struct + 0.3·I_link + 0.3·I_logic`
   - Hard gate: I ≥ 0.7 to pass
   - `I_struct`: Structural completeness of indicators
   - `I_link`: Linkage to strategic lines and programs
   - `I_logic`: Temporal and logical validity

4. **P (PPI Completeness)**: `0.2·presence + 0.4·struct + 0.4·consistency`
   - Hard gate: P ≥ 0.7 to pass
   - Financial accounting validation (1% tolerance)
   - Annual budget distribution checks

### Final Score Calculation

```
U_raw = geometric_mean(S, M, I, P)
U_final = max(0, U_raw - min(anti_gaming_penalty, 0.3))
```

**Geometric Mean**: Ensures no single component can compensate for deficiencies in others. If any component is 0, the entire score is 0.

**Anti-Gaming Penalty**: Detects and penalizes placeholder data:
- Indicators: 3.0x multiplier for "S/D", "Sin Dato", "No especificado"
- PPI: 2.0x multiplier for null/zero values
- Capped at 0.3 maximum penalty

## Usage

### Basic Usage

```python
from src.orchestration.unit_layer import UnitLayerEvaluator, create_default_config
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.pdt_structure import PDTStructure

# Create evaluator with default configuration
evaluator = UnitLayerEvaluator(create_default_config())

# Evaluate a PDT structure
pdt = PDTStructure(
    full_text="...",
    total_tokens=50000,
    blocks_found={...},
    # ... other fields
)

result = evaluator.evaluate(pdt)

print(f"U_final: {result['U_final']:.3f}")
print(f"S: {result['S']:.3f}")
print(f"M: {result['M']:.3f}")
print(f"I: {result['I']:.3f} [Gate: {'PASS' if result['indicator_quality']['gate_passed'] else 'FAIL'}]")
print(f"P: {result['P']:.3f} [Gate: {'PASS' if result['ppi_completeness']['gate_passed'] else 'FAIL'}]")
```

### Custom Configuration

```python
from src.orchestration.unit_layer import UnitLayerConfig, UnitLayerEvaluator

# Create custom configuration
config = UnitLayerConfig(
    w_s_b_cov=0.6,          # Increase block coverage weight
    w_s_h=0.2,              # Decrease header quality weight
    w_s_o=0.2,              # Decrease ordering weight
    w_m_diagnostico=3.0,    # Increase diagnostic weight
    i_hard_gate=0.6,        # Lower indicator gate threshold
    p_hard_gate=0.6,        # Lower PPI gate threshold
    anti_gaming_cap=0.25    # Lower penalty cap
)

evaluator = UnitLayerEvaluator(config)
result = evaluator.evaluate(pdt)
```

## Configuration Parameters

### Structural Compliance Weights
- `w_s_b_cov`: Block coverage weight (default: 0.5)
- `w_s_h`: Header quality weight (default: 0.25)
- `w_s_o`: Ordering quality weight (default: 0.25)

### Mandatory Section Weights
- `w_m_diagnostico`: Diagnostic section weight (default: 2.0)
- `w_m_estrategica`: Strategic section weight (default: 2.0)
- `w_m_ppi`: PPI section weight (default: 2.0)
- `w_m_seguimiento`: Monitoring section weight (default: 1.0)

### Indicator Quality Weights
- `w_i_struct`: Structure weight (default: 0.4)
- `w_i_link`: Linkage weight (default: 0.3)
- `w_i_logic`: Logic weight (default: 0.3)
- `i_hard_gate`: Pass threshold (default: 0.7)

### PPI Completeness Weights
- `w_p_presence`: Presence weight (default: 0.2)
- `w_p_struct`: Structure weight (default: 0.4)
- `w_p_consistency`: Consistency weight (default: 0.4)
- `p_hard_gate`: Pass threshold (default: 0.7)

### Other Parameters
- `anti_gaming_cap`: Maximum penalty (default: 0.3)
- `min_tokens_diagnostico`: Minimum tokens for diagnostic (default: 1000)
- `min_tokens_estrategica`: Minimum tokens for strategic (default: 1000)
- `min_tokens_ppi`: Minimum tokens for PPI (default: 500)
- `min_tokens_seguimiento`: Minimum tokens for monitoring (default: 300)
- `min_indicators`: Minimum indicator count (default: 5)
- `min_ppi_rows`: Minimum PPI rows (default: 3)
- `accounting_tolerance`: Budget deviation tolerance (default: 0.01 = 1%)

## Result Structure

```python
{
    "S": float,                          # Structural compliance score
    "M": float,                          # Mandatory sections score
    "I": float,                          # Indicator quality score (0.0 if gate failed)
    "P": float,                          # PPI completeness score (0.0 if gate failed)
    "U_raw": float,                      # Raw geometric mean
    "anti_gaming_penalty": float,        # Applied penalty (capped)
    "U_final": float,                    # Final score after penalty
    
    "structural_compliance": {
        "B_cov": float,                  # Block coverage [0-1]
        "H": float,                      # Header quality [0-1]
        "O": float,                      # Ordering quality [0-1]
        "S": float                       # Combined S score
    },
    
    "mandatory_sections": {
        "diagnostico_score": float,      # Diagnostic section score
        "estrategica_score": float,      # Strategic section score
        "ppi_score": float,              # PPI section score
        "seguimiento_score": float,      # Monitoring section score
        "M": float                       # Weighted combined M score
    },
    
    "indicator_quality": {
        "I_struct": float,               # Structure score [0-1]
        "I_link": float,                 # Linkage score [0-1]
        "I_logic": float,                # Logic score [0-1]
        "I": float,                      # Combined I score
        "gate_passed": bool              # Whether I ≥ 0.7
    },
    
    "ppi_completeness": {
        "presence": float,               # Presence score [0-1]
        "struct": float,                 # Structure score [0-1]
        "consistency": float,            # Accounting consistency [0-1]
        "P": float,                      # Combined P score
        "gate_passed": bool              # Whether P ≥ 0.7
    }
}
```

## Hard Gates

### Indicator Quality Gate (I ≥ 0.7)
If the indicator quality score falls below 0.7, the PDT is considered to have insufficient indicator structure. The I component is set to 0.0, which causes U_raw to become 0.0 (geometric mean property).

**Rejection Criteria:**
- Less than 5 indicators
- Missing required fields (Tipo, Línea Estratégica, Programa, Línea Base, Meta Cuatrienio, Fuente)
- Temporal invalidity (baseline year not in 2019-2024 range)
- Excessive placeholder data

### PPI Completeness Gate (P ≥ 0.7)
If the PPI completeness score falls below 0.7, the PDT is considered to have insufficient financial planning. The P component is set to 0.0.

**Rejection Criteria:**
- Less than 3 PPI rows
- Missing budget fields (Costo Total, annual distributions)
- Accounting inconsistency >1% (annual sum ≠ total cost)
- Excessive null/zero values

## Anti-Gaming Detection

The system detects and penalizes attempts to artificially inflate scores through placeholder data:

### Indicator Placeholders (3.0x multiplier)
- "S/D" (Sin Dato)
- "Sin Dato"
- "No especificado"
- "N/A"
- Empty strings

### PPI Placeholders (2.0x multiplier)
- Null values
- Zero values in critical fields

**Penalty Formula:**
```
indicator_penalty = (placeholder_count / total_fields) × 3.0
ppi_penalty = (zero_count / total_fields) × 2.0
total_penalty = min(indicator_penalty + ppi_penalty, 0.3)
```

## Integration with Calibration System

The Unit Layer is part of the 8-layer calibration system:

```python
from src.orchestration.unit_layer import UnitLayerEvaluator

# In calibration orchestrator
if LayerID.UNIT in required_layers:
    unit_evaluator = UnitLayerEvaluator(unit_config)
    layer_scores[LayerID.UNIT] = unit_evaluator.evaluate(pdt_structure)
```

## Examples

See `unit_layer_example.py` for comprehensive usage examples:

```bash
python src/orchestration/unit_layer_example.py
```

## COHORT_2024 Reference

This implementation is part of COHORT_2024 (REFACTOR_WAVE_2024_12). The reference file is located at:
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_unit_layer.py
```

## Technical Notes

### Geometric Mean Properties
- Non-compensatory: Low scores in any component severely impact final score
- Zero-intolerant: Any zero component results in zero final score
- Balanced: All components contribute multiplicatively

### Weight Normalization
All weight groups must sum to 1.0:
- S weights: w_s_b_cov + w_s_h + w_s_o = 1.0
- I weights: w_i_struct + w_i_link + w_i_logic = 1.0
- P weights: w_p_presence + w_p_struct + w_p_consistency = 1.0

M weights are normalized internally by their sum.

### Performance Considerations
- O(n) complexity for indicator analysis (n = number of indicators)
- O(m) complexity for PPI analysis (m = number of PPI rows)
- Minimal memory footprint (processes rows iteratively)

## Maintenance

### Adding New Section Types
To add a new mandatory section:

1. Update `_evaluate_mandatory_sections()` to include new section
2. Add corresponding weight parameter to `UnitLayerConfig`
3. Update weight normalization in `__post_init__`
4. Add section to `_score_section()` calls

### Modifying Gate Thresholds
Gate thresholds can be adjusted via configuration without code changes:

```python
config = UnitLayerConfig(
    i_hard_gate=0.65,  # Relax indicator gate
    p_hard_gate=0.75   # Tighten PPI gate
)
```

## References

- PDT Structure Definition: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/pdt_structure.py`
- Canonical Unit Analysis: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/canonic_description_unit_analysis.json`
- Meta Layer: `src/orchestration/meta_layer.py`
- Mathematical Foundations: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/mathematical_foundations_capax_system.md`
