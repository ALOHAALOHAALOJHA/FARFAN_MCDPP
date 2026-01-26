# Dimensional Recommendations Catalog

## Overview

This catalog implements a **dimensional-first architecture** for policy recommendations, eliminating redundancy by storing core intervention logic once per `DIM×Band` combination instead of duplicating it across 10 Policy Areas (PAs).

## Architecture

### Problem Solved

**Before (PA-anchored structure):**
- 300 MICRO rules: PA01-DIM01-CRISIS, PA01-DIM01-CRÍTICO, ..., PA10-DIM06-EXCELENTE
- Same intervention logic repeated 10 times (once per PA)
- Only differences: legal framework, responsible entity, reporting system
- **Result:** 90% redundancy, maintenance nightmare

**After (Dimensional-first structure):**
- 30 dimensional recommendations: DIM01-CRISIS, DIM01-CRÍTICO, ..., DIM06-EXCELENTE
- Core intervention logic stored once per dimension-band combination
- PA-specific variations handled through `instantiation_mappings`
- **Result:** 270 fewer rules, single source of truth, easy maintenance

### Key Principle

```
Universal Logic + Specific Context = Instantiated Recommendation
```

**Universal Logic:** Dimensional template (e.g., DIM01-CRISIS)
**Specific Context:** PA instantiation variables (e.g., PA01 legal framework, entity)
**Result:** Fully contextualized recommendation (e.g., PA01-DIM01-CRISIS)

---

## File Structure

```json
{
  "metadata": {
    "version": "1.0.0",
    "dimensions_covered": 6,
    "score_bands": 5,
    "total_pas": 10,
    "architecture": "Dimensional-first design...",
    "usage_notes": [...]
  },
  "dimensions": {
    "DIM01": {
      "name": "Insumos (Diagnóstico y Líneas Base)",
      "causal_position": 1,
      "questions": ["Q001", "Q002", "Q003", "Q004", "Q005"],
      "recommendations_by_band": {
        "CRISIS": {
          "intervention_logic": "Realizar barrido de urgencia...",
          "core_activities": [...],
          "expected_products": [...],
          "outcome_indicators": [...],
          "method_bindings": {...},
          "duration_months": 3,
          "pa_instantiation_variables": {
            "legal_framework_key": "dim01_crisis_legal_framework",
            "responsible_entity_key": "pa_lead_dim01",
            "reporting_system_key": "pa_monitoring_dim01"
          }
        },
        "CRÍTICO": {...},
        ...
      }
    },
    "DIM02": {...},
    ...
  },
  "instantiation_mappings": {
    "PA01": {
      "canonical_name": "Derechos de las mujeres e igualdad de género",
      "responsible_entity": "Secretaría de la Mujer Municipal...",
      "base_legal_framework": "Ley 1257 de 2008 y CONPES 4080",
      "pa_lead_dim01": "Secretaría de la Mujer",
      "dim01_crisis_legal_framework": "Ley 1257 de 2008...",
      "pa_monitoring_dim01": "Trazador Presupuestal de Equidad...",
      ...
    },
    "PA02": {...},
    ...
  }
}
```

---

## Dimensions (DIM01-DIM06)

### DIM01: Insumos (Diagnóstico y Líneas Base)
- **Causal Position:** 1 (Foundation)
- **Questions:** Q001-Q005
- **Purpose:** Diagnostic data, baselines, institutional capacities
- **Method:** SemanticProcessor.chunk_text
- **Key Platforms:** TerriData, DANE, Sinergia

### DIM02: Productos (Metas e Indicadores)
- **Causal Position:** 2 (Definition)
- **Questions:** Q006-Q010
- **Purpose:** Expected products, measurable goals, indicators
- **Method:** PDETMunicipalPlanAnalyzer._extract_financial_amounts
- **Key Platforms:** POAI, Plan Indicativo, SECOP II

### DIM03: Procesos (Gestión y Ejecución)
- **Causal Position:** 3 (Implementation)
- **Questions:** Q011-Q015
- **Purpose:** Administrative capacity, budget execution, technical compliance
- **Method:** BayesianEvidenceExtractor.extract_prior_beliefs
- **Key Platforms:** MGA Web, SUIFP-Territorial, Banco de Proyectos

### DIM04: Resultados (Medición de Impacto)
- **Causal Position:** 4 (Outcomes)
- **Questions:** Q016-Q020
- **Purpose:** Impact measurement, target achievement, ODS alignment
- **Method:** CausalExtractor.extract_causal_hierarchy
- **Key Platforms:** Sinergia, SPI, TerriData

### DIM05: Riesgos (Transparencia y Control)
- **Causal Position:** 5 (Safeguards)
- **Questions:** Q021-Q025
- **Purpose:** Corruption risk management, transparency, accountability
- **Method:** PDETMunicipalPlanAnalyzer._extract_financial_amounts
- **Key Platforms:** DAFP, Contraloría, Procuraduría

### DIM06: Causalidad (Coherencia Sistémica)
- **Causal Position:** 6 (Systemic Coherence)
- **Questions:** Q026-Q030
- **Purpose:** Causal chain validation, logical framework, theory of change
- **Method:** CausalExtractor.extract_causal_hierarchy
- **Key Platforms:** Marco Lógico MGA, DNP KPT

---

## Score Bands

| Band | Score Range | Duration | Purpose | Blocking? |
|------|-------------|----------|---------|-----------|
| **CRISIS** | 0.00 - 0.81 | 3 months | Emergency intervention | ✅ Yes |
| **CRÍTICO** | 0.81 - 1.66 | 6 months | Major restructuring | ❌ No |
| **ACEPTABLE** | 1.66 - 2.31 | 9 months | Minor adjustments | ❌ No |
| **BUENO** | 2.31 - 2.71 | 12 months | Optimization | ❌ No |
| **EXCELENTE** | 2.71 - 3.01 | 18 months | Leadership/best practices | ❌ No |

---

## Policy Areas (PA01-PA10)

| PA | Canonical Name | Responsible Entity | Legal Framework |
|----|----------------|-------------------|-----------------|
| **PA01** | Derechos de las mujeres e igualdad de género | Secretaría de la Mujer | Ley 1257, CONPES 4080 |
| **PA02** | Prevención de la violencia y seguridad ciudadana | Secretaría de Gobierno y Seguridad | Ley 1801, Política de Seguridad |
| **PA03** | Gestión ambiental y cambio climático | Secretaría de Medio Ambiente | Ley 99 de 1993, Determinantes |
| **PA04** | Desarrollo social integral | Secretaría de Desarrollo Social | Ley 100, 115, 715 (SGP) |
| **PA05** | Atención a víctimas del conflicto | Oficina de Derechos Humanos | Ley 1448 (Ley de Víctimas) |
| **PA06** | Protección de niñez y adolescencia | Secretaría de Educación y Juventud | Ley 1098 (Código Infancia) |
| **PA07** | Desarrollo rural, agricultura y tierras | Secretaría de Tierras | Ley 160, Acuerdo de Paz |
| **PA08** | Derechos humanos y memoria histórica | Secretaría de Gobierno | Decreto 1066, Directiva 002 |
| **PA09** | Reinserción social y sistema penitenciario | Secretaría de Inclusión Social | Ley 65 (Código Penitenciario) |
| **PA10** | Migración y fronteras | Gerencia de Atención a Migrantes | Ley 2136, CONPES 3950 |

---

## Usage Examples

### Example 1: Get recommendation for PA01-DIM01-CRISIS

```python
import json

# Load catalog
with open('dimensional_recommendations_catalog.json', 'r') as f:
    catalog = json.load(f)

# 1. Get dimensional template
dim_template = catalog['dimensions']['DIM01']['recommendations_by_band']['CRISIS']

# 2. Get PA-specific context
pa_context = catalog['instantiation_mappings']['PA01']

# 3. Instantiate recommendation
intervention = dim_template['intervention_logic']
legal_framework_key = dim_template['pa_instantiation_variables']['legal_framework_key']
legal_framework = pa_context[legal_framework_key]

entity_key = dim_template['pa_instantiation_variables']['responsible_entity_key']
responsible_entity = pa_context[entity_key]

monitoring_key = dim_template['pa_instantiation_variables']['reporting_system_key']
monitoring_system = pa_context[monitoring_key]

# 4. Compose full recommendation
full_recommendation = f"""
RECOMMENDATION: PA01-DIM01-CRISIS

Intervention: {intervention}

Legal Framework: {legal_framework}
Responsible Entity: {responsible_entity}
Monitoring System: {monitoring_system}

Activities:
{chr(10).join(f'  - {a}' for a in dim_template['core_activities'])}

Expected Products:
{chr(10).join(f'  - {p}' for p in dim_template['expected_products'])}

Outcome Indicators:
{chr(10).join(f'  - {i}' for i in dim_template['outcome_indicators'])}

Duration: {dim_template['duration_months']} months
Questions Covered: {', '.join(dim_template['method_bindings']['questions_covered'])}
"""

print(full_recommendation)
```

### Example 2: Generate recommendations for all PAs in DIM01-CRISIS

```python
import json

with open('dimensional_recommendations_catalog.json', 'r') as f:
    catalog = json.load(f)

dim_template = catalog['dimensions']['DIM01']['recommendations_by_band']['CRISIS']

for pa_id, pa_context in catalog['instantiation_mappings'].items():
    print(f"\n{'='*80}")
    print(f"{pa_id}: {pa_context['canonical_name']}")
    print(f"{'='*80}")
    
    # Get PA-specific variables
    legal_framework_key = dim_template['pa_instantiation_variables']['legal_framework_key']
    legal_framework = pa_context.get(legal_framework_key, 'N/A')
    
    entity_key = dim_template['pa_instantiation_variables']['responsible_entity_key']
    responsible_entity = pa_context.get(entity_key, 'N/A')
    
    print(f"Legal Framework: {legal_framework}")
    print(f"Responsible: {responsible_entity}")
    print(f"Core Intervention: {dim_template['intervention_logic'][:100]}...")
```

### Example 3: Trace recommendation to questions

```python
import json

with open('dimensional_recommendations_catalog.json', 'r') as f:
    catalog = json.load(f)

# For PA03-DIM02-CRÍTICO
dim_id = 'DIM02'
band = 'CRITICO'
pa_id = 'PA03'

dim_data = catalog['dimensions'][dim_id]
band_data = dim_data['recommendations_by_band'][band]
pa_data = catalog['instantiation_mappings'][pa_id]

print(f"Recommendation: {pa_id}-{dim_id}-{band}")
print(f"Policy Area: {pa_data['canonical_name']}")
print(f"Dimension: {dim_data['name']}")
print(f"Score Range: {band_data['score_range']}")
print(f"\nQuestions Covered:")
for q in band_data['method_bindings']['questions_covered']:
    print(f"  - {q}")
print(f"\nMethod: {band_data['method_bindings']['primary_method']}")
print(f"Data Sources: {', '.join(band_data['method_bindings']['data_sources'])}")
```

---

## Integration with Existing Systems

### Phase 8 Pipeline Integration

```python
# In recommendation engine
def generate_micro_recommendation(pa_id: str, dim_id: str, score: float):
    """Generate PA-specific recommendation from dimensional catalog"""
    
    # 1. Load catalog
    catalog = load_dimensional_catalog()
    
    # 2. Determine band
    band = determine_band(score)
    
    # 3. Get dimensional template
    dim_template = catalog['dimensions'][dim_id]['recommendations_by_band'][band]
    
    # 4. Get PA context
    pa_context = catalog['instantiation_mappings'][pa_id]
    
    # 5. Instantiate
    recommendation = instantiate_recommendation(dim_template, pa_context)
    
    # 6. Return structured recommendation
    return {
        'rule_id': f'REC-MICRO-{pa_id}-{dim_id}-{band}',
        'pa_id': pa_id,
        'dim_id': dim_id,
        'band': band,
        'score_range': dim_template['score_range'],
        'intervention': recommendation['intervention'],
        'legal_framework': recommendation['legal_framework'],
        'responsible_entity': recommendation['responsible_entity'],
        'activities': dim_template['core_activities'],
        'products': dim_template['expected_products'],
        'indicators': dim_template['outcome_indicators'],
        'duration_months': dim_template['duration_months'],
        'questions': dim_template['method_bindings']['questions_covered'],
        'method': dim_template['method_bindings']['primary_method']
    }
```

### Backward Compatibility

The dimensional catalog can generate the same 300 MICRO rules as the original system:

```python
def generate_all_micro_rules():
    """Generate all 300 MICRO rules from dimensional catalog"""
    catalog = load_dimensional_catalog()
    rules = []
    
    for pa_id in catalog['instantiation_mappings'].keys():
        for dim_id in catalog['dimensions'].keys():
            for band in ['CRISIS', 'CRITICO', 'ACEPTABLE', 'BUENO', 'EXCELENTE']:
                rule = generate_micro_recommendation(pa_id, dim_id, band)
                rules.append(rule)
    
    return rules  # 10 PAs × 6 DIMs × 5 bands = 300 rules
```

---

## Benefits

### 1. Redundancy Elimination
- **Before:** 300 rules with 90% duplication
- **After:** 30 dimensional templates + 10 PA mappings
- **Reduction:** 270 fewer rules to maintain

### 2. Maintainability
- Update intervention logic once per DIM×Band
- Changes propagate automatically to all PAs
- Single source of truth

### 3. Extensibility
- Add new PA: Only update `instantiation_mappings`
- Add new dimension: One template serves all PAs
- No logic duplication

### 4. Consistency
- Core intervention logic consistent across all PAs
- Only PA-specific details vary (legal, entities, systems)
- Reduces human error in rule creation

### 5. Auditability
- Clear separation: universal logic vs. specific parameters
- Full traceability to questions (Q001-Q300)
- Transparent variable substitution

### 6. Compliance
- Aligned with Colombian DNP territorial planning guidelines
- Follows Ley 152/1994 framework
- Compatible with SGR, MGA, SISAS methodologies

---

## Maintenance Guidelines

### Adding a New Policy Area (PA11)

1. **Add to `instantiation_mappings`:**
```json
"PA11": {
  "canonical_name": "New Policy Area",
  "responsible_entity": "Secretaría Responsable",
  "base_legal_framework": "Ley XXX de YYYY",
  "pa_lead_dim01": "Entity for DIM01",
  "dim01_crisis_legal_framework": "Specific legal framework",
  "pa_monitoring_dim01": "Monitoring system",
  ...
}
```

2. **No changes needed in `dimensions` section** - logic is universal

3. **Result:** 30 new recommendations automatically generated (6 DIMs × 5 bands)

### Updating Intervention Logic

1. **Locate dimension and band:**
```json
"dimensions" → "DIM01" → "recommendations_by_band" → "CRISIS"
```

2. **Update fields:**
- `intervention_logic`: Core intervention text
- `core_activities`: Activity list
- `expected_products`: Product list
- `outcome_indicators`: Indicator list

3. **Result:** Change applies to ALL 10 PAs automatically

### Adding a New Dimension (DIM07)

1. **Add to `dimensions`:**
```json
"DIM07": {
  "id": "DIM07",
  "name": "New Dimension Name",
  "description": "...",
  "causal_position": 7,
  "questions": ["Q031", "Q032", "Q033", "Q034", "Q035"],
  "recommendations_by_band": {
    "CRISIS": {...},
    "CRITICO": {...},
    ...
  }
}
```

2. **Update all PA mappings:**
```json
"PA01": {
  ...
  "pa_lead_dim07": "Entity",
  "dim07_crisis_legal_framework": "Legal",
  ...
}
```

3. **Result:** 50 new recommendations (10 PAs × 5 bands)

---

## Validation

The catalog includes built-in validation:

```bash
python validate_dimensional_catalog.py
```

Checks:
- ✅ All 6 dimensions present
- ✅ All 5 bands per dimension
- ✅ All 10 PAs in instantiation mappings
- ✅ Questions Q001-Q030 covered
- ✅ Method bindings complete
- ✅ PA instantiation variables present
- ✅ Data sources specified
- ✅ Duration and score ranges valid

---

## References

### Colombian Legal Framework
- **Ley 152 de 1994:** Organic Law of Development Plans
- **Ley 715 de 2001:** General System of Participations (SGP)
- **Ley 1712 de 2014:** Transparency and Access to Public Information
- **Metodología General Ajustada (MGA):** DNP project structuring framework
- **Sistema de Seguimiento de Planes (SSP):** Official monitoring platform

### Technical Standards
- **DNP Kit de Planeación Territorial (KPT)**
- **DAFP Mapa de Riesgos** (Anti-corruption risk mapping)
- **SECOP II** (Electronic public procurement system)
- **Sinergia/TerriData** (National monitoring platforms)

---

## Contact & Support

For questions about this catalog:
- **Technical:** Phase 8 pipeline development team
- **Policy:** Colombian DNP territorial planning guidance
- **Legal:** Consult specific sectoral legal frameworks per PA

---

## Version History

- **v1.0.0** (2026-01-26): Initial dimensional-first catalog
  - 6 dimensions (DIM01-DIM06)
  - 5 score bands per dimension
  - 10 policy areas (PA01-PA10)
  - 30 dimensional recommendations
  - Complete instantiation mappings
  - Full traceability to Q001-Q300

---

## License

This catalog is part of the FARFAN_MCDPP public policy evaluation system.
