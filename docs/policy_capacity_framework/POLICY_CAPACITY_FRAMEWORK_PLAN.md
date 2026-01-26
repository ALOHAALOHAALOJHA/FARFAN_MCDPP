# Policy Capacity Framework Implementation Plan
## Wu, Ramesh & Howlett (2015) Analysis

**Generated:** 2026-01-26T02:48:36.417199  
**Total Methods:** 237  
**Integrated Capacity Index:** 0.7885

---

## Executive Summary

This document presents a comprehensive implementation plan for integrating the Wu, Ramesh & Howlett (2015) Policy Capacity Framework into the existing repository structure.

### Key Innovations

1. **NEW Aggregation Dimension**: Equipment Congregation × Aggregation Level
2. **Mathematical Model**: Formal equations for capacity scoring
3. **Synergy Quantification**: Congregation coefficients for skill combinations
4. **Dual Pipeline Architecture**: Capacity-based parallel to Micro→Meso→Macro

---

## 1. The Wu Framework: 3×3 Policy Capacity Matrix

### 1.1 Framework Structure

| Level / Skill | Analytical (CA) | Operational (CO) | Political (CP) |
|---------------|-----------------|------------------|----------------|
| **Individual** | CA-I | CO-I | CP-I |
| **Organizational** | CA-O | CO-O | CP-O |
| **Systemic** | CA-S | CO-S | CP-S |

### 1.2 Capacity Type Definitions

#### CA-I: Analytical @ Individual
Individual analytical capacity

#### CA-O: Analytical @ Organizational
Organizational analytical capacity

#### CA-S: Analytical @ Systemic
Systemic analytical capacity

#### CO-I: Operational @ Individual
Individual operational capacity

#### CO-O: Operational @ Organizational
Organizational operational capacity

#### CO-S: Operational @ Systemic
Systemic operational capacity

#### CP-I: Political @ Individual
Individual political capacity

#### CP-O: Political @ Organizational
Organizational political capacity

#### CP-S: Political @ Systemic
Systemic political capacity


### 1.3 Method Distribution

- **CA-I**: 64 methods (27.0%)
- **CA-O**: 42 methods (17.7%)
- **CO-O**: 41 methods (17.3%)
- **CO-S**: 48 methods (20.3%)
- **CP-O**: 42 methods (17.7%)


---

## 2. Equipment Congregation: The Synergy Dimension

Equipment Congregation refers to how different capacity skills are grouped together, creating synergistic effects.

### 2.1 Four Equipment Types

#### Evidence-Action Nexus
- **Skills**: Analytical, Operational
- **Coefficient**: 1.35
- **Description**: Synergy between analytical rigor and operational implementation

#### Strategic Intelligence
- **Skills**: Analytical, Political
- **Coefficient**: 1.42
- **Description**: Synergy between evidence-based analysis and political feasibility

#### Adaptive Governance
- **Skills**: Operational, Political
- **Coefficient**: 1.28
- **Description**: Synergy between execution capacity and political legitimacy

#### Integrated Capacity
- **Skills**: Analytical, Operational, Political
- **Coefficient**: 1.75
- **Description**: Full trinity: evidence, execution, and legitimacy


### 2.2 Congregation Mathematics

```
M_equip = 1 + δ × ln(1 + n_skills) × (ρ_congregation - 1)
```

Where δ = 0.3 (congregation sensitivity parameter)

---

## 3. Aggregation Level: Individual → Organizational → Systemic

### 3.1 Conceptual Distinction

| Dimension | Existing Pipeline | NEW Capacity Dimension |
|-----------|------------------|------------------------|
| **What** | Questions → Policy Areas → Clusters | Individual skills → Org structures → Systemic ecosystems |
| **Purpose** | Thematic aggregation | Capacity accumulation |
| **Codes** | Q001-Q300 → PA01-PA10 → CL01-CL04 | CA/CO/CP-I → -O → -S |

### 3.2 Aggregation Formulas

#### Individual to Organizational

**Formula**: `C_org = (Σ C_ind_i^p)^(1/p) × κ_org`

Parameters:
- p = 1.2 (power parameter)
- κ_org = 0.85 (organizational capacity factor)

#### Organizational to Systemic

**Formula**: `C_sys = √(C_org_mean × C_org_max) × κ_sys`

Parameters:
- κ_sys = 0.90 (systemic capacity factor)

### 3.3 Transformation Matrix

Cross-level influence coefficients:

```
         Individual  Organizational  Systemic
Individual     1.00          0.75      0.50
Organizational 0.25          1.00      0.80
Systemic       0.10          0.35      1.00
```

---

## 4. Mathematical Model

### 4.1 Base Capacity Score

```
C_base = α × E_weight + β × L_weight + γ × O_weight
```

Parameters: α=0.4, β=0.35, γ=0.25

### 4.2 Weights

**Epistemology**:
- Empirismo positivista: 0.85
- Bayesianismo subjetivista: 1.00
- Falsacionismo popperiano: 0.92

**Method Level**:
- N1-EMP: 1.0
- N2-INF: 1.5
- N3-AUD: 2.0

**Output Type**:
- FACT: 0.8
- PARAMETER: 1.0
- CONSTRAINT: 1.2

### 4.3 Aggregation Weight

```
W_agg = η × exp(-λ × Δ_level)
```

Where: η=0.85, λ=0.15

### 4.4 Integrated Capacity Index

```
ICI = (Σ(w_skill × Σ(w_level × C_type))) / 9
```

Level weights: Individual=0.25, Organizational=0.35, Systemic=0.40

**Current ICI**: {ici}

---

## 5. Mapping Rules

### 5.1 Epistemology → Skill

- Empirismo positivista → Analytical (fact-based)
- Bayesianismo subjetivista → Political (belief-based)
- Falsacionismo popperiano → Operational (testability)

### 5.2 Method Level → Capacity Level

- N1-EMP → Individual
- N2-INF → Organizational
- N3-AUD → Systemic

---

## 6. Implementation Recommendations

### 6.1 New Files to Create

#### capacity_mappings.json
- **Location**: `config/`
- **Purpose**: Store method → capacity type mappings

#### capacity_aggregation.py
- **Location**: `src/aggregation/`
- **Purpose**: Implement capacity-based aggregation functions

#### equipment_congregations.json
- **Location**: `config/`
- **Purpose**: Define equipment congregation configurations

### 6.2 Important Constraints

⚠️ **Do NOT modify**:
- Question definitions (Q001-Q300)
- Contract structures
- Existing Micro→Meso→Macro pipeline

✅ **Do add**:
- Capacity dimension as complementary
- New aggregation formulas
- Capacity metadata to methods

---

## 7. Capacity Scores

- **CA-I** (Analytical @ Individual): 1.068
- **CA-O** (Analytical @ Organizational): 1.338
- **CO-O** (Operational @ Organizational): 1.3716
- **CO-S** (Operational @ Systemic): 1.6416
- **CP-O** (Political @ Organizational): 1.41


---

## 8. Next Steps

### Immediate (Week 1-2)
1. ✅ Review capacity type mappings
2. ⬜ Create capacity_mappings.json
3. ⬜ Implement base scoring function

### Short-term (Week 3-6)
1. ⬜ Develop aggregation functions
2. ⬜ Add capacity metadata
3. ⬜ Create visualization dashboard

### Medium-term (Week 7-12)
1. ⬜ Integrate with existing pipeline
2. ⬜ Validate scores
3. ⬜ Calibrate coefficients

---

## Appendix A: Sample Mappings

First 10 methods:

| Method | Epistemology | Level | Output | Capacity | Score |
|--------|--------------|-------|--------|----------|-------|
| M001 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M002 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M003 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M004 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M005 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M006 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M007 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M008 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M009 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |
| M010 | Empirismo posit... | N1-EMP | FACT | CA-I | 0.89 |


---

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-26 02:48:36
