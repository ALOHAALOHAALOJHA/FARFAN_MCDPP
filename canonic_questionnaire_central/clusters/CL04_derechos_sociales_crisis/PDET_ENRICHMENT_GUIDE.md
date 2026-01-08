# CL04 PDET Enrichment Integration

## Overview

The CL04 cluster (Derechos Sociales & Crisis) has been enriched with PDET (Programas de Desarrollo con Enfoque Territorial) contextual information to enable territorial targeting and resource allocation for crisis management and migration policies.

## Policy Area Mappings

### PA09 - Crisis PPL (Prisons/Justice)

**PDET Subregion**: SR01 (Alto Patía y Norte del Cauca)

**Focus Municipalities**:
1. **Jambaló** (19355) - High indigenous population, justice access challenges
2. **López de Micay** (19397) - Afrodescendant community, prison oversight needs  
3. **Piamonte** (19450) - Rural isolation, limited justice infrastructure

**PDET Pillars**:
- Pillar 3: Rural health and justice
- Pillar 8: Reconciliation and human rights

**Key Indicators**:
- Justice houses coverage
- Legal assistance availability
- Detention conditions
- Indigenous justice systems integration

**Contextual Factors**:
- Ethnic diversity requires differentiated justice approaches
- Limited state presence challenges prison oversight
- Community justice mechanisms complement formal systems

### PA10 - Migración (International Migration)

**PDET Subregions**: SR02 (Arauca), SR04 (Catatumbo)

**Focus Municipalities**:

*Arauca Subregion (SR02):*
1. **Arauca** (81001) - International border, Venezuelan migration hub
2. **Fortul** (81220) - Border transit point, humanitarian needs
3. **Tame** (81794) - Reception center for displaced populations

*Catatumbo Subregion (SR04):*
4. **Convención** (54099) - Border municipality, migration corridor
5. **Teorama** (54810) - Migration route, integration challenges
6. **San Calixto** (54660) - Venezuela border, cross-border flows

**PDET Pillars**:
- Pillar 2: Infrastructure (border crossings, transit facilities)
- Pillar 3: Health (humanitarian assistance)
- Pillar 4: Education (integration of migrant children)
- Pillar 8: Social cohesion (host community-migrant relations)

**Key Indicators**:
- Migrant population count
- Border cooperation agreements
- Humanitarian assistance coverage
- Integration programs
- Xenophobia incidents
- Mixed nationality households

**Contextual Factors**:
- Venezuela border creates continuous migration pressure
- Humanitarian emergency requires coordinated response
- Host community tensions need reconciliation interventions
- Integration depends on service capacity (health, education)

## Territorial Patterns Added

### PA09 Patterns

**Municipality Patterns** (`PAT-Q271-013-PDET`):
- Alto Patía, Norte del Cauca
- Jambaló, López de Micay, Piamonte
- With semantic expansions and PDET context metadata

**Indigenous Justice Patterns** (`PAT-Q271-014-PDET`):
- comunidades indígenas
- justicia ancestral
- sistema de justicia propia
- guardia indígena

**Afrodescendant Justice Patterns** (`PAT-Q271-015-PDET`):
- comunidades afrodescendientes
- consejos comunitarios
- justicia comunitaria

### PA10 Patterns

**Border Municipality Patterns** (`PAT-Q031-013-PDET`):
- Arauca, Fortul, Tame (Arauca subregion)
- Catatumbo, Convención, Teorama, San Calixto (Catatumbo subregion)
- With semantic expansions and PDET context metadata

**Border/Migration Patterns** (`PAT-Q031-014-PDET`):
- frontera con Venezuela
- paso fronterizo
- zona de frontera
- corredor migratorio

**Transit Population Patterns** (`PAT-Q031-015-PDET`):
- caminantes
- población en tránsito
- flujo irregular
- ruta migratoria

**Social Cohesion Patterns** (`PAT-Q031-016-PDET`):
- xenofobia
- discriminación
- conflictos de convivencia
- tensiones sociales

## Four Validation Gates

The PDET enrichment implements a four-gate validation framework:

### Gate 1: Consumer Scope Validity
- Consumer must have `pdet_context` or `ENRICHMENT_DATA` in allowed signal types
- Consumer must be authorized for requested policy areas (PA09 and/or PA10)
- Unauthorized access attempts result in hard failures

### Gate 2: Value Contribution
- Estimated value-add: 35% for CL04 enrichment
- Validates that enriched data materially improves analysis capabilities
- Rejects redundant or ornamental data

### Gate 3: Consumer Capability and Readiness
- **Required capabilities**:
  - `SEMANTIC_PROCESSING`: Understanding territorial context
  - `TABLE_PARSING`: Processing municipality tables
- **Recommended capabilities**:
  - `GRAPH_CONSTRUCTION`: Subregion-municipality relationships
  - `FINANCIAL_ANALYSIS`: OCAD Paz investment data

### Gate 4: Channel Authenticity and Integrity
- Flow ID: `PDET_MUNICIPALITY_ENRICHMENT`
- Validates explicit registration, documentation, traceability
- Governance policy: four_gate_validation
- Documentation path: `canonic_questionnaire_central/colombia_context/README_PDET_ENRICHMENT.md`

## Usage Example

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

# Create consumer scope for PA09 (justice/prisons)
consumer_scope = SignalScope(
    scope_name="PA09 Crisis Analyzer",
    scope_level=ScopeLevel.EVIDENCE_COLLECTION,
    allowed_signal_types=["ENRICHMENT_DATA", "*"],
    allowed_policy_areas=["PA09"],
    min_confidence=0.50,
    max_signals_per_query=100
)

# Define capabilities
consumer_capabilities = [
    SignalCapability.SEMANTIC_PROCESSING,
    SignalCapability.TABLE_PARSING,
    SignalCapability.GRAPH_CONSTRUCTION
]

# Create enrichment request
request = EnrichmentRequest(
    consumer_id="prison_policy_analyzer",
    consumer_scope=consumer_scope,
    consumer_capabilities=consumer_capabilities,
    target_policy_areas=["PA09"],
    target_questions=["Q241", "Q242"],
    requested_context=["municipalities", "subregions", "policy_area_mappings"]
)

# Perform enrichment
result = orchestrator.enrich(request)

if result.success:
    # Access enriched data
    municipalities = result.enriched_data["data"]["municipalities"]
    # -> [Jambaló, López de Micay, Piamonte]
    
    subregions = result.enriched_data["data"]["subregions"]
    # -> [SR01: Alto Patía y Norte del Cauca]
    
    pa_mappings = result.enriched_data["data"]["policy_area_mappings"]["PA09"]
    # -> PDET pillars, indicators, contextual factors
else:
    print(f"Enrichment failed: {result.violations}")
```

## Use Cases

### PA09 (Justice/Prisons)
1. Identify municipalities with prison oversight challenges based on ethnic composition
2. Map indigenous justice systems that complement formal detention facilities
3. Target legal assistance and justice access improvements in isolated areas
4. Analyze transitional justice implementation in conflict-affected zones

### PA10 (Migration)
1. Prioritize border municipalities for migration service deployment
2. Assess humanitarian response capacity and identify gaps
3. Design culturally-appropriate integration programs based on municipal characteristics
4. Monitor xenophobia indicators and social cohesion in host communities
5. Coordinate cross-border cooperation with Venezuela in specific municipalities

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_cl04_pdet_enrichment.py -v
```

**Test Coverage**:
- Metadata structure validation (PDET config present and properly formatted)
- Gate configuration checks (all four gates enabled)
- PA09 mapping verification (SR01, 3 municipalities, correct pillars)
- PA10 mapping verification (SR02+SR04, 6 municipalities, correct pillars)
- Successful enrichment requests for both PA09 and PA10
- Gate failure scenarios (invalid scope, insufficient capabilities)
- Report generation and logging

## Data Sources

- **Primary**: Agencia de Renovación del Territorio (ART)
- **Secondary**: DNP, DANE, OCAD Paz
- **Update Frequency**: Quarterly
- **Last Validation**: 2025-10-15
- **Change Control**: CCP-PDET-2024

## References

- [PDET Enrichment System Documentation](canonic_questionnaire_central/colombia_context/README_PDET_ENRICHMENT.md)
- [Decreto Ley 893 de 2017](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=83195)
- [Central de Información PDET](https://www.renovacionterritorio.gov.co/PDET)
- [OCAD Paz](https://www.minhacienda.gov.co/webcenter/portal/Ocadpaz)
