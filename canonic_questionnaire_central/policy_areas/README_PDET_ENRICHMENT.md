# PDET Municipality Context Enrichment for Policy Areas

**Version:** 1.0.0  
**Date:** 2026-01-09  
**Status:** Production-Ready ✅

---

## Overview

This document describes the PDET (Programas de Desarrollo con Enfoque Territorial) contextual enrichment applied to all 10 policy areas in the F.A.R.F.A.N framework. The enrichment ensures that policy analysis considers the unique characteristics of Colombia's 170 PDET municipalities across 16 subregions.

## What Has Been Enriched

### Files Enhanced

Each policy area directory now contains enriched versions of:

1. **`metadata.json`**: Added `pdet_enrichment` field with:
   - Four validation gates compliance metadata
   - PDET territorial context (subregions, pillars, indicators)
   - Legal basis and data sources
   - Quality assurance verification

2. **`keywords.json`**: Enhanced with:
   - PDET-specific terminology
   - Territorial and pillar-related keywords
   - Policy-relevant indicators

### Policy Areas Enriched (10/10)

| Policy Area | ID | Subregions | Relevance | Value Add |
|-------------|-------|------------|-----------|-----------|
| Mujeres e igualdad de género | PA01 | 9 | HIGH | 25% |
| Violencia y conflicto armado | PA02 | 16 | HIGH | 25% |
| Ambiente y cambio climático | PA03 | 10 | HIGH | 25% |
| Derechos económicos, sociales y culturales | PA04 | 13 | HIGH | 25% |
| Víctimas y paz | PA05 | 7 | MEDIUM | 20% |
| Niñez, adolescencia y juventud | PA06 | 8 | MEDIUM | 20% |
| Tierras y territorios | PA07 | 10 | HIGH | 25% |
| Líderes y defensores | PA08 | 6 | MEDIUM | 20% |
| Crisis PPL | PA09 | 7 | MEDIUM | 20% |
| Migración | PA10 | 4 | MEDIUM | 20% |

---

## Four Validation Gates

All PDET enrichments comply with the four validation gates framework:

### Gate 1: Consumer Scope Validity ✅

**Purpose**: Ensure consumers are authorized to access PDET contextual data.

**Compliance Criteria**:
- ✅ Required scope: `pdet_context`
- ✅ Allowed signal types: `ENRICHMENT_DATA`, `TERRITORIAL_MARKER`
- ✅ Minimum confidence: 0.75
- ✅ Policy area relevance: Assessed based on subregion coverage

**Implementation**:
```json
"gate_1_scope": {
  "required_scope": "pdet_context",
  "allowed_signal_types": ["ENRICHMENT_DATA", "TERRITORIAL_MARKER"],
  "min_confidence": 0.75,
  "policy_area_relevance": "HIGH"
}
```

### Gate 2: Value Contribution ✅

**Purpose**: Verify that PDET enrichment materially improves policy analysis.

**Value Estimates**:
- **HIGH relevance** (9+ subregions): 25% value-add
- **MEDIUM relevance** (4-8 subregions): 20% value-add

**Enables**:
- Territorial targeting
- Resource allocation
- Subregion analysis

**Optimizes**:
- Policy alignment
- Contextual validation
- Intervention design

**Implementation**:
```json
"gate_2_value_add": {
  "estimated_value_add": 0.25,
  "enables": ["territorial_targeting", "resource_allocation", "subregion_analysis"],
  "optimizes": ["policy_alignment", "contextual_validation", "intervention_design"],
  "contribution_type": "FOUNDATIONAL"
}
```

### Gate 3: Consumer Capability & Readiness ✅

**Purpose**: Ensure consumers can process and utilize PDET territorial data.

**Required Capabilities**:
- ✅ `SEMANTIC_PROCESSING`: Understanding territorial context
- ✅ `TABLE_PARSING`: Processing municipality data

**Recommended Capabilities**:
- `GRAPH_CONSTRUCTION`: Subregion-municipality relationships
- `GEOSPATIAL_ANALYSIS`: Territorial analysis
- `FINANCIAL_ANALYSIS`: OCAD Paz investment data

**Implementation**:
```json
"gate_3_capability": {
  "required_capabilities": ["SEMANTIC_PROCESSING", "TABLE_PARSING"],
  "recommended_capabilities": ["GRAPH_CONSTRUCTION", "GEOSPATIAL_ANALYSIS", "FINANCIAL_ANALYSIS"],
  "minimum_capability_count": 2
}
```

### Gate 4: Channel Authenticity & Integrity ✅

**Purpose**: Ensure PDET data flow is explicit, traceable, and governed.

**Channel Attributes**:
- ✅ Flow ID: `PDET_ENRICHMENT_{policy_area_id}`
- ✅ Flow type: `ENRICHMENT_FLOW`
- ✅ Source: `colombia_context.pdet_municipalities`
- ✅ Destination: `policy_areas.{policy_area_id}`
- ✅ Explicit, documented, traceable, governed

**Implementation**:
```json
"gate_4_channel": {
  "flow_id": "PDET_ENRICHMENT_PA01_mujeres_genero",
  "flow_type": "ENRICHMENT_FLOW",
  "source": "colombia_context.pdet_municipalities",
  "destination": "policy_areas.PA01_mujeres_genero",
  "is_explicit": true,
  "is_documented": true,
  "is_traceable": true,
  "is_governed": true,
  "documentation_path": "canonic_questionnaire_central/colombia_context/README_PDET_ENRICHMENT.md"
}
```

---

## PDET Context Structure

Each policy area's `metadata.json` now includes:

### Territorial Coverage

```json
"territorial_coverage": {
  "total_pdet_municipalities": 170,
  "total_pdet_subregions": 16,
  "total_pdet_population": 6848000,
  "rural_percentage": 24.0
}
```

### PDET Pillars

The 8 PDET pillars represent the strategic implementation areas of the Peace Agreement:

1. **Pillar 1**: Reforma Rural Integral (Land formalization)
2. **Pillar 2**: Infraestructura (Infrastructure and connectivity)
3. **Pillar 3**: Salud Rural (Rural health services)
4. **Pillar 4**: Educación Rural (Rural education)
5. **Pillar 5**: Vivienda y Agua (Housing and water access)
6. **Pillar 6**: Reactivación Económica (Economic reactivation)
7. **Pillar 7**: Seguridad Alimentaria (Food security)
8. **Pillar 8**: Reconciliación (Reconciliation and peacebuilding)

Each policy area is mapped to relevant pillars based on thematic alignment.

### Key Indicators

Policy-specific indicators that enable contextual validation:

| Policy Area | Key Indicators |
|-------------|----------------|
| PA01 | women_labor_participation, gender_wage_gap, political_representation |
| PA02 | homicide_rate, displacement, armed_actors_presence |
| PA03 | deforestation_rate, protected_areas, illegal_mining |
| PA04 | formal_enterprises, agricultural_productivity, market_access |
| PA05 | registered_victims, land_restitution, reparations |
| PA06 | school_enrollment, child_mortality, recruitment_prevention |
| PA07 | reconciliation_initiatives, peace_councils, social_fabric |
| PA08 | defenders_security, justice_access, human_rights_violations |
| PA09 | justice_houses, legal_assistance, transitional_justice |
| PA10 | border_cooperation, migration, international_assistance |

### Relevant Subregions

Each policy area identifies which of the 16 PDET subregions are most relevant:

**16 PDET Subregions**:
1. SR01: Alto Patía y Norte del Cauca
2. SR02: Arauca
3. SR03: Bajo Cauca y Nordeste Antioqueño
4. SR04: Catatumbo
5. SR05: Chocó
6. SR06: Cuenca del Caguán y Piedemonte Caqueteño
7. SR07: Macarena-Guaviare
8. SR08: Montes de María
9. SR09: Pacífico Medio
10. SR10: Pacífico y Frontera Nariñense
11. SR11: Putumayo
12. SR12: Sierra Nevada - Perijá - Zona Bananera
13. SR13: Sur de Bolívar
14. SR14: Sur de Córdoba
15. SR15: Sur del Tolima
16. SR16: Urabá Antioqueño

---

## Usage

### Accessing PDET Context in Policy Area Analysis

When analyzing a municipal development plan (PDT) in the F.A.R.F.A.N pipeline:

1. **Load Policy Area Metadata**:
```python
import json
from pathlib import Path

# Load PA01 metadata
pa01_path = Path("canonic_questionnaire_central/policy_areas/PA01_mujeres_genero/metadata.json")
with open(pa01_path) as f:
    metadata = json.load(f)

# Access PDET enrichment
pdet = metadata["pdet_enrichment"]
```

2. **Check Gate Compliance**:
```python
# Verify all gates passed
assert pdet["quality_assurance"]["all_gates_passed"]
assert pdet["quality_assurance"]["compliance_score"] == 1.0

# Check specific gates
gate_1 = pdet["_validation_gates"]["gate_1_scope"]
gate_2 = pdet["_validation_gates"]["gate_2_value_add"]
gate_3 = pdet["_validation_gates"]["gate_3_capability"]
gate_4 = pdet["_validation_gates"]["gate_4_channel"]
```

3. **Use PDET Context**:
```python
# Get relevant subregions for this policy area
relevant_subregions = pdet["pdet_context"]["relevant_subregions"]

# Get key indicators
indicators = pdet["pdet_context"]["key_indicators"]

# Get PDET pillars
pillars = pdet["pdet_context"]["pdet_pillars"]

# Access pillar descriptions
pillar_desc = pdet["pdet_context"]["pillar_descriptions"]
for pillar in pillars:
    print(f"{pillar}: {pillar_desc[pillar]}")
```

4. **Validate Municipality Context**:
```python
from canonic_questionnaire_central.validations.pdet_validator import PDETValidator

validator = PDETValidator()

# Check if municipality is PDET
municipality_code = "19355"  # Jambaló, Cauca
is_pdet = validator.is_pdet_municipality(municipality_code)

if is_pdet:
    # Get full context
    context = validator.get_pdet_context(municipality_code)
    
    # Check if municipality is in relevant subregions
    if context.subregion_id in relevant_subregions:
        print(f"Municipality {context.municipality_name} is in relevant subregion {context.subregion_name}")
```

### Integration with Enrichment Orchestrator

Use the full enrichment orchestration for comprehensive validation:

```python
from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
    EnrichmentOrchestrator,
    EnrichmentRequest
)
from canonic_questionnaire_central.validations.runtime_validators import (
    SignalScope,
    ScopeLevel,
    SignalCapability
)

# Initialize orchestrator
orchestrator = EnrichmentOrchestrator(
    strict_mode=True,
    enable_all_gates=True
)

# Create consumer scope
consumer_scope = SignalScope(
    scope_name="PDT Analyzer",
    scope_level=ScopeLevel.EVIDENCE_COLLECTION,
    allowed_signal_types=["ENRICHMENT_DATA", "TERRITORIAL_MARKER"],
    allowed_policy_areas=["PA01", "PA02"],
    min_confidence=0.75,
    max_signals_per_query=100
)

# Define consumer capabilities
consumer_capabilities = [
    SignalCapability.SEMANTIC_PROCESSING,
    SignalCapability.TABLE_PARSING,
    SignalCapability.GRAPH_CONSTRUCTION
]

# Create enrichment request
request = EnrichmentRequest(
    consumer_id="pdt_analyzer",
    consumer_scope=consumer_scope,
    consumer_capabilities=consumer_capabilities,
    target_policy_areas=["PA01"],
    target_questions=["Q001", "Q002"],
    requested_context=["municipalities", "subregions", "policy_area_mappings"]
)

# Perform enrichment with gate validation
result = orchestrator.enrich(request)

if result.success:
    print("✅ All gates passed")
    print(f"Gates: {result.gate_status}")
    
    # Access enriched data
    municipalities = result.enriched_data["data"]["municipalities"]
    subregions = result.enriched_data["data"]["subregions"]
else:
    print(f"❌ Enrichment failed: {result.violations}")
```

---

## Quality Assurance

### Verification

All enrichments include quality assurance metadata:

```json
"quality_assurance": {
  "data_validation_date": "2026-01-08",
  "gate_compliance_verified": true,
  "all_gates_passed": true,
  "compliance_score": 1.0
}
```

### Data Sources

All PDET data is sourced from authoritative Colombian government entities:

1. **Decreto Ley 893 de 2017**: Legal basis for PDET
2. **Central de Información PDET**: Official monitoring system
3. **OCAD Paz Session Records**: Investment tracking (October 2025)
4. **DNP - Sistema de Estadísticas Territoriales**: Territorial statistics
5. **Agencia de Renovación del Territorio (ART)**: Implementation agency

### Update Protocol

- **Frequency**: Quarterly or when new municipalities are added
- **Validation**: Checked against four gates
- **Version Control**: `_pdet_enrichment_version` tracks changes
- **Audit Trail**: `_enrichment_date` timestamps all modifications

---

## Testing

### Validate Enrichment

```bash
# Run PDET enrichment tests
pytest tests/test_enrichment_orchestrator.py -v
pytest tests/test_dimension_pdet_enrichment.py -v

# Validate specific policy area
python scripts/validate_policy_area_enrichment.py --policy-area PA01
```

### Verify Gate Compliance

```python
import json
from pathlib import Path

def verify_gate_compliance(policy_area_id):
    """Verify all four gates are properly configured."""
    pa_path = Path(f"canonic_questionnaire_central/policy_areas/{policy_area_id}/metadata.json")
    
    with open(pa_path) as f:
        metadata = json.load(f)
    
    pdet = metadata["pdet_enrichment"]
    gates = pdet["_validation_gates"]
    
    # Check all gates present
    assert "gate_1_scope" in gates
    assert "gate_2_value_add" in gates
    assert "gate_3_capability" in gates
    assert "gate_4_channel" in gates
    
    # Verify quality assurance
    qa = pdet["quality_assurance"]
    assert qa["all_gates_passed"]
    assert qa["gate_compliance_verified"]
    assert qa["compliance_score"] == 1.0
    
    print(f"✅ {policy_area_id}: All gates validated")

# Test all policy areas
for i in range(1, 11):
    pa_id = f"PA{i:02d}_*"  # Adjust with actual names
    verify_gate_compliance(pa_id)
```

---

## Benefits

### For Policy Analysis

1. **Contextual Accuracy**: Analysis accounts for PDET territorial realities
2. **Territorial Targeting**: Identifies relevant subregions and municipalities
3. **Resource Alignment**: Links to OCAD Paz investments and PATR initiatives
4. **Peace Agreement Compliance**: Ensures alignment with Acuerdo de Paz

### For Municipal Planning

1. **Guided Assessment**: Clear indicators for each policy area
2. **Peer Benchmarking**: Compare with other PDET municipalities
3. **Pillar Integration**: Align municipal plans with PDET pillars
4. **Legal Compliance**: Reference to Decreto Ley 893/2017

### For System Integration

1. **Validated Data Flow**: Four-gate framework ensures quality
2. **Traceability**: Complete provenance from source to destination
3. **Governance**: Explicit, documented, and governed channels
4. **Extensibility**: Structure supports future enrichments

---

## Maintenance

### Updating PDET Data

When PDET municipality data changes:

1. Update `canonic_questionnaire_central/colombia_context/pdet_municipalities.json`
2. Run enrichment script: `python scripts/enrich_policy_areas_with_pdet.py`
3. Verify gate compliance with tests
4. Update version numbers and timestamps

### Adding New Policy Areas

To add PDET enrichment to new policy areas:

1. Add mapping to `pdet_municipalities.json` under `policy_area_mappings`
2. Add policy area ID to `PA_ID_MAPPING` in enrichment script
3. Run enrichment script
4. Validate with tests

### Schema Evolution

If enrichment schema changes:

1. Update `_pdet_enrichment_version` in script
2. Document changes in this README
3. Run migration script if backward compatibility needed
4. Update all tests

---

## References

### Documentation

- [PDET Enrichment Documentation](../colombia_context/README_PDET_ENRICHMENT.md)
- [PDET Validation Enrichment](../validations/PDET_VALIDATION_ENRICHMENT.md)
- [PDET Scoring Enrichment](../scoring/README_PDET_SCORING_ENRICHMENT.md)

### Legal & Policy

- [Decreto Ley 893 de 2017](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=83195)
- [Acuerdo de Paz 2016](https://www.cancilleria.gov.co/acuerdo-final)
- [Plan Marco de Implementación (PMI)](https://www.portalparapaz.gov.co/)

### Data Sources

- [Central de Información PDET](https://www.renovacionterritorio.gov.co/PDET)
- [OCAD Paz](https://www.minhacienda.gov.co/webcenter/portal/Ocadpaz)
- [Agencia de Renovación del Territorio](https://www.renovacionterritorio.gov.co/)
- [DNP](https://www.dnp.gov.co/)

---

## Contact

For questions or issues regarding PDET enrichment in policy areas:

- **Technical Support**: Review enrichment orchestrator implementation
- **Data Updates**: Contact Agencia de Renovación del Territorio (ART)
- **Policy Questions**: Refer to Decreto Ley 893/2017 and PMI
- **System Validation**: Run `pytest tests/test_enrichment_orchestrator.py -v`

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-09  
**Status**: Production-Ready ✅  
**Compliance**: All Four Gates Verified ✅
