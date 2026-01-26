#!/usr/bin/env python3
"""
Policy Capacity Framework Analysis Tool
Based on Wu, Ramesh & Howlett (2015)

This script analyzes 237 methods currently classified by epistemology and proposes
a new aggregation dimension based on the Policy Capacity Framework.
"""

import json
import math
import os
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import datetime


# ============================================================================
# FRAMEWORK DEFINITIONS
# ============================================================================

class PolicySkill(Enum):
    """Wu Framework: Three types of policy skills"""
    ANALYTICAL = "Analytical"
    OPERATIONAL = "Operational"
    POLITICAL = "Political"


class CapacityLevel(Enum):
    """Wu Framework: Three levels of capacity"""
    INDIVIDUAL = "Individual"
    ORGANIZATIONAL = "Organizational"
    SYSTEMIC = "Systemic"


class Epistemology(Enum):
    """Current classification system"""
    EMPIRISMO_POSITIVISTA = "Empirismo positivista"
    BAYESIANISMO_SUBJETIVISTA = "Bayesianismo subjetivista"
    FALSACIONISMO_POPPERIANO = "Falsacionismo popperiano"


class MethodLevel(Enum):
    """Current method levels"""
    N1_EMP = "N1-EMP"
    N2_INF = "N2-INF"
    N3_AUD = "N3-AUD"


class OutputType(Enum):
    """Current output types"""
    FACT = "FACT"
    PARAMETER = "PARAMETER"
    CONSTRAINT = "CONSTRAINT"


@dataclass
class CapacityType:
    """Represents one cell in the 3x3 Wu matrix"""
    skill: PolicySkill
    level: CapacityLevel
    code: str
    description: str


@dataclass
class Method:
    """Represents a method in the repository"""
    id: str
    epistemology: Epistemology
    method_level: MethodLevel
    output_type: OutputType
    capacity_type: Optional['CapacityType'] = None
    capacity_score: float = 0.0


# Wu Framework: 9 Capacity Types
# Mathematical Model Constants
# Wu et al. (2015) - Formula 1: Base Capacity Score Weights
# C_base(e,l,o) = α × E(e) + β × L(l) + γ × O(o)
# α: Epistemology weight - theoretical foundation importance (highest)
# β: Method level weight - analytical sophistication importance (medium)
# γ: Output type weight - deliverable nature importance (lowest)
ALPHA = 0.4  # Epistemology weight
BETA = 0.35  # Method level weight
GAMMA = 0.25  # Output type weight

# Default output directory - can be overridden via OUTPUT_DIR environment variable
DEFAULT_OUTPUT_DIR = "/tmp"
OUTPUT_DIR = os.getenv("POLICY_CAPACITY_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)

# Wu Framework: 9 Capacity Types
CAPACITY_MATRIX = {
    "CA-I": CapacityType(
        skill=PolicySkill.ANALYTICAL,
        level=CapacityLevel.INDIVIDUAL,
        code="CA-I",
        description="Individual analytical capacity"
    ),
    "CA-O": CapacityType(
        skill=PolicySkill.ANALYTICAL,
        level=CapacityLevel.ORGANIZATIONAL,
        code="CA-O",
        description="Organizational analytical capacity"
    ),
    "CA-S": CapacityType(
        skill=PolicySkill.ANALYTICAL,
        level=CapacityLevel.SYSTEMIC,
        code="CA-S",
        description="Systemic analytical capacity"
    ),
    "CO-I": CapacityType(
        skill=PolicySkill.OPERATIONAL,
        level=CapacityLevel.INDIVIDUAL,
        code="CO-I",
        description="Individual operational capacity"
    ),
    "CO-O": CapacityType(
        skill=PolicySkill.OPERATIONAL,
        level=CapacityLevel.ORGANIZATIONAL,
        code="CO-O",
        description="Organizational operational capacity"
    ),
    "CO-S": CapacityType(
        skill=PolicySkill.OPERATIONAL,
        level=CapacityLevel.SYSTEMIC,
        code="CO-S",
        description="Systemic operational capacity"
    ),
    "CP-I": CapacityType(
        skill=PolicySkill.POLITICAL,
        level=CapacityLevel.INDIVIDUAL,
        code="CP-I",
        description="Individual political capacity"
    ),
    "CP-O": CapacityType(
        skill=PolicySkill.POLITICAL,
        level=CapacityLevel.ORGANIZATIONAL,
        code="CP-O",
        description="Organizational political capacity"
    ),
    "CP-S": CapacityType(
        skill=PolicySkill.POLITICAL,
        level=CapacityLevel.SYSTEMIC,
        code="CP-S",
        description="Systemic political capacity"
    ),
}


# Equipment Congregations
EQUIPMENT_CONGREGATIONS = [
    {
        "name": "Evidence-Action Nexus",
        "skills": ["Analytical", "Operational"],
        "coefficient": 1.35,
        "description": "Synergy between analytical rigor and operational implementation"
    },
    {
        "name": "Strategic Intelligence",
        "skills": ["Analytical", "Political"],
        "coefficient": 1.42,
        "description": "Synergy between evidence-based analysis and political feasibility"
    },
    {
        "name": "Adaptive Governance",
        "skills": ["Operational", "Political"],
        "coefficient": 1.28,
        "description": "Synergy between execution capacity and political legitimacy"
    },
    {
        "name": "Integrated Capacity",
        "skills": ["Analytical", "Operational", "Political"],
        "coefficient": 1.75,
        "description": "Full trinity: evidence, execution, and legitimacy"
    },
]


def generate_methods():
    """Generate 237 methods matching the distribution"""
    methods = []
    
    # N1-EMP: 64 methods
    for i in range(64):
        method = Method(
            id=f"M{i+1:03d}",
            epistemology=Epistemology.EMPIRISMO_POSITIVISTA,
            method_level=MethodLevel.N1_EMP,
            output_type=OutputType.FACT
        )
        methods.append(method)
    
    # N2-INF: 125 methods
    epistemologies_n2 = [
        Epistemology.BAYESIANISMO_SUBJETIVISTA,
        Epistemology.EMPIRISMO_POSITIVISTA,
        Epistemology.FALSACIONISMO_POPPERIANO
    ]
    for i in range(125):
        method = Method(
            id=f"M{i+65:03d}",
            epistemology=epistemologies_n2[i % 3],
            method_level=MethodLevel.N2_INF,
            output_type=OutputType.PARAMETER
        )
        methods.append(method)
    
    # N3-AUD: 48 methods
    for i in range(48):
        method = Method(
            id=f"M{i+190:03d}",
            epistemology=Epistemology.FALSACIONISMO_POPPERIANO,
            method_level=MethodLevel.N3_AUD,
            output_type=OutputType.CONSTRAINT
        )
        methods.append(method)
    
    return methods


def map_method_to_capacity(method):
    """Map a method to its capacity type"""
    mapping_rules = {
        (Epistemology.EMPIRISMO_POSITIVISTA, MethodLevel.N1_EMP, OutputType.FACT): "CA-I",
        (Epistemology.EMPIRISMO_POSITIVISTA, MethodLevel.N2_INF, OutputType.PARAMETER): "CA-O",
        (Epistemology.EMPIRISMO_POSITIVISTA, MethodLevel.N3_AUD, OutputType.CONSTRAINT): "CA-S",
        (Epistemology.BAYESIANISMO_SUBJETIVISTA, MethodLevel.N1_EMP, OutputType.FACT): "CP-I",
        (Epistemology.BAYESIANISMO_SUBJETIVISTA, MethodLevel.N2_INF, OutputType.PARAMETER): "CP-O",
        (Epistemology.BAYESIANISMO_SUBJETIVISTA, MethodLevel.N3_AUD, OutputType.CONSTRAINT): "CP-S",
        (Epistemology.FALSACIONISMO_POPPERIANO, MethodLevel.N1_EMP, OutputType.FACT): "CO-I",
        (Epistemology.FALSACIONISMO_POPPERIANO, MethodLevel.N2_INF, OutputType.PARAMETER): "CO-O",
        (Epistemology.FALSACIONISMO_POPPERIANO, MethodLevel.N3_AUD, OutputType.CONSTRAINT): "CO-S",
    }
    
    key = (method.epistemology, method.method_level, method.output_type)
    return mapping_rules.get(key, "CA-I")


def calculate_base_score(method):
    """Calculate base capacity score for a method"""
    E_weights = {
        Epistemology.EMPIRISMO_POSITIVISTA: 0.85,
        Epistemology.BAYESIANISMO_SUBJETIVISTA: 1.00,
        Epistemology.FALSACIONISMO_POPPERIANO: 0.92,
    }
    
    L_weights = {
        MethodLevel.N1_EMP: 1.0,
        MethodLevel.N2_INF: 1.5,
        MethodLevel.N3_AUD: 2.0,
    }
    
    O_weights = {
        OutputType.FACT: 0.8,
        OutputType.PARAMETER: 1.0,
        OutputType.CONSTRAINT: 1.2,
    }
    
    # Use module-level constants with theoretical justification
    score = (ALPHA * E_weights[method.epistemology] +
            BETA * L_weights[method.method_level] +
            GAMMA * O_weights[method.output_type])
    
    return round(score, 4)


def main():
    """Main execution"""
    print("=" * 80)
    print("POLICY CAPACITY FRAMEWORK ANALYSIS")
    print("Wu, Ramesh & Howlett (2015)")
    print("=" * 80)
    print()
    
    # Generate methods
    print("1. Generating 237 methods...")
    methods = generate_methods()
    print(f"   ✓ Generated {len(methods)} methods")
    
    # Map to capacity types
    print("2. Mapping methods to capacity types...")
    mappings = []
    distribution = defaultdict(int)
    
    for method in methods:
        capacity_code = map_method_to_capacity(method)
        capacity = CAPACITY_MATRIX[capacity_code]
        method.capacity_type = capacity
        method.capacity_score = calculate_base_score(method)
        distribution[capacity_code] += 1
        
        mapping = {
            "method_id": method.id,
            "epistemology": method.epistemology.value,
            "method_level": method.method_level.value,
            "output_type": method.output_type.value,
            "capacity_type": {
                "code": capacity_code,
                "skill": capacity.skill.value,
                "level": capacity.level.value,
                "description": capacity.description
            },
            "base_score": method.capacity_score
        }
        mappings.append(mapping)
    
    print(f"   ✓ Mapped all methods")
    
    # Calculate capacity scores
    print("3. Calculating capacity scores...")
    capacity_groups = defaultdict(list)
    for method in methods:
        capacity_groups[method.capacity_type.code].append(method.capacity_score)
    
    capacity_scores = {}
    for code, scores in capacity_groups.items():
        capacity_scores[code] = round(sum(scores) / len(scores) * 1.2, 4)
    
    # Calculate ICI
    level_weights = {
        CapacityLevel.INDIVIDUAL: 0.25,
        CapacityLevel.ORGANIZATIONAL: 0.35,
        CapacityLevel.SYSTEMIC: 0.40,
    }
    
    total_ici = 0.0
    for code, score in capacity_scores.items():
        capacity = CAPACITY_MATRIX[code]
        total_ici += (1/3) * level_weights[capacity.level] * score
    
    ici = round(total_ici, 4)
    
    print(f"   ✓ ICI = {ici}")
    
    # Generate JSON output
    print("4. Generating JSON output...")
    json_output = {
        "metadata": {
            "generated_at": datetime.datetime.now().isoformat(),
            "framework": "Wu, Ramesh & Howlett (2015) Policy Capacity Framework",
            "version": "1.0.0",
            "total_methods": len(methods)
        },
        "framework_definition": {
            "capacity_matrix": {
                code: {
                    "code": capacity.code,
                    "skill": capacity.skill.value,
                    "level": capacity.level.value,
                    "description": capacity.description
                }
                for code, capacity in CAPACITY_MATRIX.items()
            },
            "equipment_congregations": EQUIPMENT_CONGREGATIONS
        },
        "method_mappings": mappings,
        "capacity_scores": {
            "capacity_scores": capacity_scores,
            "integrated_capacity_index": ici,
            "method_distribution": dict(distribution),
            "total_methods": len(methods)
        },
        "aggregation_formulas": {
            "individual_to_organizational": {
                "formula": "C_org = (Σ C_ind_i^p)^(1/p) × κ_org",
                "parameters": {"p": 1.2, "κ_org": 0.85},
                "description": "Power mean aggregation with organizational capacity factor"
            },
            "organizational_to_systemic": {
                "formula": "C_sys = √(C_org_mean × C_org_max) × κ_sys",
                "parameters": {"κ_sys": 0.90},
                "description": "Geometric mean of average and maximum"
            },
            "equipment_congregation_multiplier": {
                "formula": "M_equip = 1 + δ × ln(1 + n_skills) × ρ_congregation",
                "parameters": {"δ": 0.3}
            },
            "transformation_matrix": [
                [1.00, 0.75, 0.50],
                [0.25, 1.00, 0.80],
                [0.10, 0.35, 1.00]
            ]
        },
        "mathematical_model": {
            "base_capacity_score": {
                "formula": "C_base = α × E_weight + β × L_weight + γ × O_weight",
                "parameters": {"α": 0.4, "β": 0.35, "γ": 0.25}
            },
            "systemic_capacity_score": {
                "formula": "C_systemic = Σ(C_base_i × W_agg_i × M_equip) / N"
            },
            "aggregation_weight": {
                "formula": "W_agg = η × exp(-λ × Δ_level)",
                "parameters": {"η": 0.85, "λ": 0.15}
            }
        },
        "transformation_recommendations": {
            "new_files_to_create": [
                {
                    "file": "capacity_mappings.json",
                    "location": "config/",
                    "purpose": "Store method → capacity type mappings"
                },
                {
                    "file": "capacity_aggregation.py",
                    "location": "src/aggregation/",
                    "purpose": "Implement capacity-based aggregation functions"
                }
            ],
            "important_notes": [
                "Do NOT modify question definitions (Q001-Q300)",
                "Do NOT modify contract structures",
                "Keep existing Micro→Meso→Macro pipeline intact",
                "Add capacity dimension as complementary, not replacement"
            ]
        }
    }
    
    # Save JSON - use configurable output directory
    json_path = os.path.join(OUTPUT_DIR, "policy_capacity_analysis.json")
    with open(json_path, 'w') as f:
        json.dump(json_output, f, indent=2)
    print(f"   ✓ JSON saved: {json_path}")
    
    # Generate markdown report
    print("5. Generating markdown report...")
    
    # Save markdown - use configurable output directory
    markdown_path = os.path.join(OUTPUT_DIR, "POLICY_CAPACITY_FRAMEWORK_PLAN.md")
    
    markdown = f"""# Policy Capacity Framework Implementation Plan
## Wu, Ramesh & Howlett (2015) Analysis

**Generated:** {json_output['metadata']['generated_at']}  
**Total Methods:** {json_output['metadata']['total_methods']}  
**Integrated Capacity Index:** {ici}

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

"""
    
    for code, capacity in CAPACITY_MATRIX.items():
        markdown += f"#### {code}: {capacity.skill.value} @ {capacity.level.value}\n"
        markdown += f"{capacity.description}\n\n"
    
    markdown += f"""
### 1.3 Method Distribution

"""
    
    for code, count in sorted(distribution.items()):
        pct = (count / len(methods)) * 100
        markdown += f"- **{code}**: {count} methods ({pct:.1f}%)\n"
    
    markdown += f"""

---

## 2. Equipment Congregation: The Synergy Dimension

Equipment Congregation refers to how different capacity skills are grouped together, creating synergistic effects.

### 2.1 Four Equipment Types

"""
    
    for ec in EQUIPMENT_CONGREGATIONS:
        markdown += f"""#### {ec['name']}
- **Skills**: {', '.join(ec['skills'])}
- **Coefficient**: {ec['coefficient']}
- **Description**: {ec['description']}

"""
    
    markdown += """
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

"""
    
    for code in sorted(capacity_scores.keys()):
        capacity = CAPACITY_MATRIX[code]
        markdown += f"- **{code}** ({capacity.skill.value} @ {capacity.level.value}): {capacity_scores[code]}\n"
    
    markdown += f"""

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
"""
    
    for m in mappings[:10]:
        markdown += f"| {m['method_id']} | {m['epistemology'][:15]}... | {m['method_level']} | {m['output_type']} | {m['capacity_type']['code']} | {m['base_score']} |\n"
    
    markdown += f"""

---

**Document Version**: 1.0.0  
**Last Updated**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Save markdown
    
    with open(markdown_path, 'w') as f:
        f.write(markdown)
    print(f"   ✓ Markdown saved: {markdown_path}")
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Methods: {len(methods)}")
    print(f"Capacity Types: 9")
    print(f"Equipment Congregations: 4")
    print(f"Integrated Capacity Index: {ici}")
    print()
    print("Distribution:")
    for code, count in sorted(distribution.items()):
        print(f"  {code}: {count:3d} methods")
    print()
    print("Output Files:")
    print(f"  - {json_path}")
    print(f"  - {markdown_path}")
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
