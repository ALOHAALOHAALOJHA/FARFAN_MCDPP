# Colombian PDM-Specific Chunk Production Guide

**Version:** 1.0.0  
**Date:** 2026-01-18  
**Author:** F.A.R.F.A.N Core Team

## Overview

This document describes the enhancements made to Phase 1 chunk production to optimize for Colombian Municipal Development Plans (Planes de Desarrollo Municipal - PDM).

## Purpose

Colombian PDMs have a specific structure defined by:
- **Ley 152 de 1994** (Organic Planning Law)
- **DNP Guidelines** (National Planning Department)
- **CONPES Social Policies** (National Policy Council)
- **Standard PDM Structure** used across Colombian municipalities

The enhanced chunking system ensures that chunks are:
1. **SMART**: Contain relevant PDM-specific context and markers
2. **COMPREHENSIVE**: Cover all standard PDM sections systematically
3. **DETAILED**: Include fine-grained territorial and policy indicators

## Architecture

### Phase 1 SP4: Question-Aware Segmentation

Phase 1 SP4 creates **exactly 300 chunks** mapped to questionnaire questions:
- **10 Policy Areas** (PA01-PA10)
- **6 Dimensions** (DIM01-DIM06)
- **5 Questions per PA×DIM** (Q1-Q5)
- **Total: 300 chunks** (10 × 6 × 5)

### Colombian PDM Enhancement Layer

The new `phase1_07_01_colombian_pdm_enhancer.py` module adds:

```python
class ColombianPDMChunkEnhancer:
    """
    Analyzes chunks for Colombian PDM-specific patterns:
    - Regulatory framework references (Ley 152, CONPES, etc.)
    - Standard PDM section markers
    - Territorial indicators (NBI, SISBEN, DANE, etc.)
    - Financial/budget markers
    - Differential approach markers (enfoque diferencial)
    - Quantitative density analysis
    - Strategic planning elements
    """
```

## Colombian PDM Pattern Categories

### 1. Regulatory Framework Markers

Detects references to Colombian legal framework:
- `Ley 152 de 1994` - Planning law
- `Ley 1098 de 2006` - Children's code
- `Constitución Política` - Constitution
- `CONPES \d+` - Policy documents
- `DNP` - National Planning Department
- `POT/PBOT/EOT` - Territorial ordering plans
- `Acuerdo de Paz` - Peace agreement
- `Ley 1448` - Victims law

**Importance:** Legal compliance and regulatory alignment

### 2. Standard PDM Section Markers

Identifies key PDM structural sections:
- `Diagnóstico territorial` - Territorial diagnosis
- `Visión y objetivos` - Vision and objectives
- `Ejes estratégicos` - Strategic axes
- `Programas y subprogramas` - Programs and subprograms
- `Plan plurianual de inversiones` - Multi-year investment plan
- `Indicadores y metas` - Indicators and targets
- `Sistema de seguimiento` - Monitoring system
- `Marco fiscal de mediano plazo` - Medium-term fiscal framework

**Importance:** Structural completeness and organization

### 3. Territorial Indicators

Recognizes Colombian socioeconomic indicators:
- `NBI` - Unsatisfied Basic Needs (Necesidades Básicas Insatisfechas)
- `SISBEN` - Socioeconomic classification system
- `Cobertura` - Coverage indicators
- `Tasa de` - Rate indicators
- `DANE` - National statistics department
- `Código DANE` - Municipal identification codes
- `Categoría [1-6]` - Municipal category
- `IPM` - Multidimensional Poverty Index

**Importance:** Data-driven planning and baseline establishment

### 4. Financial & Budget Markers

Detects budget and financial planning elements:
- `Presupuesto de inversión` - Investment budget
- `Fuentes de financiación` - Financing sources
- `Recursos propios/transferidos` - Own/transferred resources
- `Sistema General de Participaciones (SGP)` - General participation system
- `Regalías` - Royalties
- `Cofinanciación` - Co-financing
- `Recursos del crédito` - Credit resources

**Importance:** Fiscal feasibility and resource allocation

### 5. Differential Approach Markers

Identifies inclusive planning for specific populations:
- `Enfoque diferencial` - Differential approach
- `Pueblos indígenas` - Indigenous peoples
- `Comunidades afrodescendientes` - Afro-descendant communities
- `Población LGBTI` - LGBTI population
- `Personas con discapacidad` - People with disabilities
- `Adultos mayores` - Elderly
- `Primera infancia` - Early childhood
- `Perspectiva de género` - Gender perspective
- `Víctimas del conflicto` - Conflict victims

**Importance:** Equity and inclusion in territorial planning

### 6. Quantitative Markers

Analyzes numerical density and specificity:
- Percentages: `\d+%`
- Amounts: `\d+ millones/miles/billones`
- Measurements: `\d+ hectáreas/metros/kilómetros`
- Population: `\d+ personas/habitantes/beneficiarios`
- Targets: `Meta: \d+`
- Baselines: `Línea base: \d+`

**Importance:** Quantification and measurability

### 7. Strategic Planning Elements

Recognizes planning methodology markers:
- `Objetivos estratégicos/específicos` - Strategic/specific objectives
- `Metas del cuatrienio` - Four-year targets
- `Indicadores de producto/resultado/impacto` - Output/outcome/impact indicators
- `Teoría del cambio` - Theory of change
- `Cadena de valor` - Value chain
- `Marco lógico` - Logical framework
- `Articulación con` - Articulation with

**Importance:** Planning rigor and methodology

## PDM Specificity Score

Each chunk receives a **PDM Specificity Score** (0.0 to 1.0):

```python
Score = 0.15 * (Regulatory) +
        0.20 * (Sections) +
        0.20 * (Indicators) +
        0.15 * (Financial) +
        0.15 * (Differential) +
        0.15 * (Strategic)
```

**Interpretation:**
- **0.8-1.0**: Highly PDM-specific, rich in Colombian context
- **0.6-0.8**: Good PDM content, standard planning elements
- **0.4-0.6**: Moderate PDM relevance
- **0.2-0.4**: Low PDM specificity
- **0.0-0.2**: Generic or non-PDM content

## Chunk Metadata Enhancement

Enhanced chunks include:

```json
{
  "chunk_id": "CHUNK-PA01-DIM01-Q1",
  "policy_area_id": "PA01",
  "dimension_id": "DIM01",
  "question_id": "Q001",
  "content": "...",
  "colombian_pdm_enhancement": {
    "pdm_specificity_score": 0.85,
    "has_regulatory_reference": true,
    "has_section_marker": true,
    "has_territorial_indicator": true,
    "has_financial_info": true,
    "has_differential_approach": true,
    "quantitative_density": 2.3,
    "has_strategic_elements": true,
    "context_markers": {
      "regulatory": 3,
      "sections": 2,
      "indicators": 5,
      "financial": 4,
      "differential": 2,
      "strategic": 3
    },
    "detected_sections": ["Diagnóstico territorial", "Plan de inversión"],
    "indicator_types": ["NBI", "SISBEN", "DANE"],
    "population_groups": ["Primera infancia", "Víctimas del conflicto"]
  }
}
```

## Document Processing Guards

### Problem: Re-chunking Already Chunked Documents

Some methods in the dispensary process documents directly, while others expect pre-chunked documents. Re-chunking can cause:
- Loss of provenance information
- Duplication of processing
- Inconsistent chunk boundaries
- Wasted computational resources

### Solution: Guard Clauses

The module provides guard functions:

```python
from farfan_pipeline.phases.Phase_01.phase1_07_01_colombian_pdm_enhancer import (
    check_if_already_chunked,
    assert_not_chunked,
    AlreadyChunkedError
)

def my_document_processing_method(document):
    """Process a raw document (should NOT be chunked)."""
    
    # Guard clause - raise error if already chunked
    assert_not_chunked(document, method_name="my_document_processing_method")
    
    # Safe to process...
    # This method operates on unchunked documents
```

**When to use:**
- ✅ **Use `assert_not_chunked()`** in methods that perform raw document extraction/parsing
- ✅ **Use `check_if_already_chunked()`** for conditional logic
- ❌ **Don't use** in methods that explicitly operate on chunks

## Integration with Phase 2

Phase 2 executors receive enhanced chunks with PDM-specific metadata:

```python
# In Phase 2 executor contract
def execute(self, chunks: List[Chunk]) -> ExecutionResult:
    """Execute analysis on enhanced chunks."""
    
    for chunk in chunks:
        # Access PDM enhancement
        pdm_info = chunk.metadata.get("colombian_pdm_enhancement", {})
        
        if pdm_info.get("has_territorial_indicator"):
            # Prioritize chunks with territorial data
            pass
        
        if pdm_info.get("pdm_specificity_score", 0) > 0.7:
            # High-quality PDM content
            pass
```

## Benefits for Colombian PDM Analysis

1. **Improved Question Answering**
   - Chunks contain relevant PDM-specific context
   - Better matching between questions and content

2. **Enhanced Evidence Quality**
   - Territorial indicators provide quantitative backing
   - Regulatory references establish legal basis

3. **Differential Approach Detection**
   - Automatic identification of inclusive planning
   - Population-specific content flagging

4. **Financial Traceability**
   - Budget information co-located with planning content
   - Resource allocation visibility

5. **Structural Completeness**
   - Detection of missing PDM sections
   - Systematic coverage verification

## Usage Example

```python
from farfan_pipeline.phases.Phase_01.phase1_07_01_colombian_pdm_enhancer import (
    ColombianPDMChunkEnhancer
)

# Initialize enhancer
enhancer = ColombianPDMChunkEnhancer()

# Enhance a chunk
enhancement = enhancer.enhance_chunk(
    chunk_content=chunk.content,
    chunk_metadata=chunk.metadata
)

# Add enhancement to metadata
updated_metadata = enhancer.add_enhancement_to_metadata(
    chunk_metadata=chunk.metadata,
    enhancement=enhancement
)

# Check specificity
if enhancement.pdm_specificity_score > 0.8:
    logger.info(f"High-quality PDM chunk: {chunk.chunk_id}")
```

## Future Enhancements

Potential improvements:
1. Machine learning-based section classification
2. Entity recognition for Colombian municipalities/departments
3. PDET territory detection (Peace Agreement territories)
4. Ethnic consultation markers for indigenous territories
5. Climate adaptation and disaster risk management markers
6. SDG (Sustainable Development Goals) alignment detection

## References

- **Ley 152 de 1994** - Ley Orgánica del Plan de Desarrollo
- **DNP Guidelines** - Guía Metodológica para la Formulación de Planes de Desarrollo Territorial
- **CONPES Documents** - Documentos de Política del Consejo Nacional de Política Económica y Social
- **F.A.R.F.A.N Framework** - Framework for Assessment of Results-based Financing and Articulated Networks

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-18  
**Maintainer:** F.A.R.F.A.N Core Architecture Team
