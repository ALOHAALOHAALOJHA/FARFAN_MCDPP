# PDT Parsing Specification Implementation

## Overview

This document describes the implementation of three formal specification files for parsing and validating Plan de Desarrollo Territorial (PDT) documents in the Farfan calibration pipeline.

## Implemented Files

### 1. pdt_parsing_spec.json
**Location**: `src/farfan_pipeline/core/calibration/pdt_parsing_spec.json`

**Purpose**: Defines the hierarchical structure requirements and parsing rules for PDT documents.

**Key Components**:
- **Hierarchical Structure**: 4-level hierarchy (H1: CAPÍTULO/Título, H2: Línea estratégica, H3: Programa, H4: Sector)
- **Expected Block Sequence**: Diagnóstico → Estratégica → PPI → Seguimiento
- **Section Detection Rules**: Transition markers and semantic boundaries
- **Validation Rules**: Numbering schemes, parent-child relationships, block ordering

**Features**:
- Format patterns for each header level with examples
- Block aliases for flexible detection
- Sequence validation with inversion penalties
- Optional blocks (Marco Normativo, Paz/PDET)

### 2. section_requirements.json
**Location**: `src/farfan_pipeline/core/calibration/section_requirements.json`

**Purpose**: Defines validation thresholds for mandatory PDT sections.

**Key Components**:

#### Section Thresholds
| Section | Min Tokens | Min Keywords | Min Numbers | Min Sources | Weight | Critical |
|---------|-----------|--------------|-------------|-------------|--------|----------|
| Diagnóstico | 500 | 3 | 5 | 2 | 2.0 | Yes |
| Parte Estratégica | 400 | 3 | 3 | - | 2.0 | Yes |
| PPI | 300 | 2 | 10 | - | 2.0 | Yes |
| Seguimiento | 200 | 2 | 2 | - | 1.0 | No |
| Marco Normativo | 150 | 1 | - | - | 1.0 | No |

**Features**:
- **Required Keywords**: Specific keywords per section (e.g., "brecha", "DANE", "caracterización" for Diagnóstico)
- **Required Sources**: Data sources that must be cited (e.g., DANE, Medicina Legal)
- **Quality Indicators**: Three-tier scoring (high/medium/low quality) per section
- **Validation Rules**: Token counting, keyword matching, number detection, source detection

### 3. matrix_schemas.json
**Location**: `src/farfan_pipeline/core/calibration/matrix_schemas.json`

**Purpose**: Defines schemas for indicator matrices and PPI matrices with field requirements and validation rules.

**Key Components**:

#### Indicator Matrix Schema
**Critical Fields** (required, no placeholders):
- `Tipo`: Type of indicator (PRODUCTO/RESULTADO)
- `Línea Estratégica`: Strategic line
- `Programa`: Budget program
- `Línea Base`: Baseline value
- `Meta Cuatrienio`: 4-year target
- `Fuente`: Data source
- `Unidad Medida`: Unit of measurement

**Optional Fields**:
- `Año LB`: Baseline year (valid range: 2019-2024)
- `Código MGA`: MGA product code (7 digits)

**Temporal Validity**:
- Baseline years: 2019-2024
- Target years: 2024-2027

**Placeholder Penalty**: 3.0× multiplier for S/D, N/A, TBD values

#### PPI Matrix Schema
**Mandatory Columns**:
- `Línea Estratégica`: Strategic line
- `Programa`: Program name
- `Costo Total`: Total cost for 2024-2027

**Temporal Distribution** (vigencias):
- `2024`, `2025`, `2026`, `2027`: Annual budgets

**Funding Sources**:
- `SGP`: Sistema General de Participaciones
- `SGR`: Sistema General de Regalías
- `Propios`: Municipal own-source revenues
- `Otras`: Other sources

**Accounting Closure Requirements**:
- Temporal closure: sum(vigencias) = Costo Total ± 1%
- Source closure: sum(sources) = Costo Total ± 1%
- Minimum 80% non-zero rows

**Quality Scoring**:

**Indicator Matrix (I)**:
- `I_struct` (0.4): Field completeness
- `I_link` (0.3): Traceability to strategic lines
- `I_logic` (0.3): Temporal coherence
- Hard gate: I_struct < 0.7 → I = 0.0

**PPI Matrix (P)**:
- `P_presence` (0.2): Matrix exists
- `P_struct` (0.4): Non-zero row ratio
- `P_consistency` (0.4): Accounting closure compliance

## Anti-Gaming Detection

All three specifications include anti-gaming rules to prevent superficial compliance:

1. **Placeholder Ratio Check**: Max 10% placeholders allowed
2. **Unique Values Check**: Min 50% unique cost values in PPI
3. **Number Density Check**: Min 2% numeric tokens in critical sections
4. **Gaming Penalty Cap**: 0.3 maximum total penalty

## Integration with Existing Code

These specifications formalize the requirements already implemented in:
- `src/farfan_pipeline/core/calibration/pdt_structure.py`: PDTStructure data model
- `src/farfan_pipeline/core/calibration/unit_layer.py`: UnitLayerEvaluator implementation
- `src/farfan_pipeline/core/calibration/config 2.py`: UnitLayerConfig parameters

## Based On

All specifications are derived from:
- `canonic_description_unit_analysis.json`: Canonical description of PDT structure and patterns
- Existing implementation in unit_layer.py and pdt_structure.py
- Colombian legal framework (Ley 152 de 1994, Ley 388 de 1997)

## Validation

All JSON files have been validated for:
- ✅ Well-formed JSON syntax
- ✅ Comprehensive coverage of parsing requirements
- ✅ Alignment with existing codebase
- ✅ Mathematical consistency (weights, thresholds, formulas)

## File Sizes

- `pdt_parsing_spec.json`: 7.5 KB
- `section_requirements.json`: 13 KB
- `matrix_schemas.json`: 18 KB
- **Total**: 38.5 KB of formal specifications

## Usage

These specification files serve as:
1. **Documentation**: Formal specification of PDT parsing rules
2. **Validation Reference**: Ground truth for parser implementations
3. **Testing Baseline**: Expected structure for test case generation
4. **Configuration Source**: Can be loaded programmatically for dynamic validation

## Future Work

These specifications can be extended to:
- Generate JSON Schema for automated validation
- Create test fixtures for parser development
- Build configuration loaders for runtime validation
- Support multiple PDT formats/versions
