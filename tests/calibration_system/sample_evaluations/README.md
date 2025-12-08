# Unit Layer Sample Evaluations

This directory contains sample PDT structures and their expected evaluation outcomes for the Unit Layer (@u) evaluator.

## Files

### 1. `excellent_pdt.json`
**Quality Level**: Sobresaliente (U ≥ 0.85)

- Complete structure with all 4 mandatory blocks
- Excellent hierarchy with valid numbering
- Comprehensive mandatory sections meeting all criteria
- High-quality indicator matrix with complete fields
- Well-formed PPI matrix with accounting closure
- Minimal anti-gaming penalties

**Expected Scores**:
- S (Structural Compliance): 1.0
- M (Mandatory Sections): 1.0
- I (Indicator Quality): 0.92
- P (PPI Completeness): 0.96
- U_final: ~0.97

### 2. `minimal_pdt.json`
**Quality Level**: Mínimo (0.5 ≤ U < 0.7)

- Basic structure meeting minimum requirements
- Some hierarchy issues (mixed numbering)
- Sections present but with minimal content
- Indicator matrix with basic completeness
- PPI matrix with acceptable accounting
- Minor anti-gaming penalties

**Expected Scores**:
- S: 0.69
- M: 0.72
- I: 0.68
- P: 0.85
- U_final: ~0.68

### 3. `insufficient_pdt.json`
**Quality Level**: Insuficiente (U < 0.5)

- Incomplete structure (missing Seguimiento block)
- Poor hierarchy
- Sections with insufficient content
- Indicator matrix full of placeholders
- Empty PPI matrix
- Significant anti-gaming penalties

**Expected Scores**:
- S: 0.31
- M: 0.28
- I: 0.12
- P: 0.35
- U_final: ~0.09

### 4. `gaming_attempt_pdt.json`
**Quality Level**: Insuficiente (gaming detected)

Demonstrates anti-gaming detection:
- High placeholder ratio (>80% in indicators)
- Repetitive/identical values (all PPI costs identical)
- Very low number density (text padding without data)
- Penalty capped at 0.30

**Gaming Flags**:
1. Placeholder ratio: >10% threshold
2. Unique values ratio: <50% threshold
3. Number density: <0.02 threshold

**Expected Scores**:
- S: 0.88 (structure looks good)
- M: 0.65
- I: 0.05 (massive I_struct penalty)
- P: 0.75
- U_base: 0.48
- Penalty: 0.30 (capped)
- U_final: 0.18

### 5. `hard_gate_failure_pdt.json`
**Quality Level**: Hard Gate Failures (U = 0.0)

Contains multiple failure scenarios:

#### Scenario 1: Structural Hard Gate
- S < 0.5 (only 1 of 4 blocks present)
- Immediate U = 0.0

#### Scenario 2: I_struct Hard Gate
- I_struct < 0.7 (empty indicator fields)
- Immediate U = 0.0

#### Scenario 3: PPI Presence Hard Gate
- Missing PPI matrix (require_ppi_presence = true)
- Immediate U = 0.0

#### Scenario 4: P_struct Hard Gate
- P_struct < 0.7 (all zero PPI rows)
- Immediate U = 0.0

## Usage

These samples can be used to:

1. **Test the evaluator**: Load JSON and verify expected scores
2. **Understand quality levels**: See what each quality tier looks like
3. **Calibrate thresholds**: Adjust config parameters based on real cases
4. **Document behavior**: Reference examples for hard gates and penalties

## Component Formulas

### S (Structural Compliance)
```
S = 0.5·B_cov + 0.25·H + 0.25·O

Where:
- B_cov = valid_blocks / 4
- H = {1.0, 0.5, 0.0} hierarchy score
- O = inversion penalty
```

### M (Mandatory Sections)
```
M = weighted_average(section_scores)

Critical sections (Diagnóstico, Estratégica, PPI): 2.0x weight
Each section scored on criteria compliance
```

### I (Indicator Quality)
```
I = 0.4·I_struct + 0.3·I_link + 0.3·I_logic

Where:
- I_struct = field completeness with placeholder penalties
- I_link = Programa-Línea fuzzy match + MGA validation
- I_logic = temporal validity (year range check)
```

### P (PPI Completeness)
```
P = 0.2·P_presence + 0.4·P_struct + 0.4·P_consistency

Where:
- P_presence = {1.0 if exists, 0.0 otherwise}
- P_struct = non-zero row ratio
- P_consistency = accounting/source closure validation
```

### Aggregation
```
geometric_mean: U = (S·M·I·P)^(1/4)
harmonic_mean: U = 4 / (1/S + 1/M + 1/I + 1/P)
weighted_average: U = 0.25·S + 0.25·M + 0.25·I + 0.25·P
```

### Anti-Gaming Penalty
```
penalty = min(sum(individual_penalties), 0.3)

Individual penalties:
1. Placeholder ratio > 10%
2. Unique values ratio < 50%
3. Number density < 0.02

U_final = max(0.0, U_base - penalty)
```

## Quality Classification

| Level | Threshold | Description |
|-------|-----------|-------------|
| Sobresaliente | U ≥ 0.85 | Outstanding quality, all components excellent |
| Robusto | U ≥ 0.7 | Robust quality, strong performance |
| Mínimo | U ≥ 0.5 | Minimum acceptable, meets basic requirements |
| Insuficiente | U < 0.5 | Insufficient quality, fails standards |

## Hard Gates (Immediate U = 0.0)

1. **Structural**: S < 0.5
2. **Indicator Structure**: I_struct < 0.7
3. **PPI Presence**: require_ppi_presence = true but absent
4. **Indicator Matrix**: require_indicator_matrix = true but absent
5. **PPI Structure**: P_struct < 0.7
