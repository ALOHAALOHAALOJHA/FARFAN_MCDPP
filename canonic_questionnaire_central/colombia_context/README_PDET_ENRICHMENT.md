# PDET Context Enrichment System

## Overview

The PDET Context Enrichment System provides a governed, validated mechanism for enriching canonical questionnaire data with contextual information about Colombian municipalities participating in the PDET (Programas de Desarrollo con Enfoque Territorial) initiative.

## Four Validation Gates

The system implements a four-gate validation framework to ensure data enrichment meets strict governance requirements:

### Gate 1: Consumer Scope Validity
**Purpose**: Ensure consumers' declared scopes authorize access to canonical data.

**Validation Criteria**:
- Consumer must have `pdet_context` or `ENRICHMENT_DATA` in allowed signal types
- Consumer must be authorized for requested policy areas
- Unauthorized access attempts result in hard failures

**Implementation**: `scope_validator.py`

**Example**:
```python
from canonic_questionnaire_central.validations.runtime_validators import ScopeValidator, SignalScope

validator = ScopeValidator()
scope = SignalScope(
    scope_name="PDET Consumer",
    allowed_signal_types=["ENRICHMENT_DATA"],
    allowed_policy_areas=["PA01", "PA02"],
    min_confidence=0.50,
    max_signals_per_query=100
)

result = validator.validate(
    consumer_id="my_consumer",
    scope=scope,
    signal_type="ENRICHMENT_DATA",
    signal_confidence=0.85
)
assert result.valid
```

### Gate 2: Value Contribution
**Purpose**: Verify that enriched data materially improves, enables, or optimizes consumer processes.

**Validation Criteria**:
- Estimated value-add must exceed 10% threshold
- Redundant or ornamental data is rejected
- Value is calculated based on context type and policy area relevance

**Value Estimates**:
- Municipality data: 25% value-add
- Subregion context: 20% value-add
- Policy area mappings: 30% value-add
- PDET pillars: 15% value-add

**Implementation**: `value_add_validator.py`

**Example**:
```python
from canonic_questionnaire_central.validations.runtime_validators import ValueAddScorer

scorer = ValueAddScorer(min_value_add_threshold=0.10)

# Estimate value for PDET enrichment
estimated_value = scorer.estimate_value_add(
    signal_type="ENRICHMENT_DATA",
    payload={"context_type": "municipalities", "policy_areas": ["PA01", "PA02"]}
)

assert estimated_value >= 0.10  # Above threshold
```

### Gate 3: Consumer Capability and Readiness
**Purpose**: Check that consumers possess necessary tools and capabilities to utilize enriched data.

**Required Capabilities**:
- `SEMANTIC_PROCESSING`: Understanding territorial context
- `TABLE_PARSING`: Processing municipality tables

**Recommended Capabilities**:
- `GRAPH_CONSTRUCTION`: Subregion-municipality relationships
- `FINANCIAL_ANALYSIS`: OCAD Paz investment data

**Implementation**: `capability_validator.py`

**Example**:
```python
from canonic_questionnaire_central.validations.runtime_validators import (
    CapabilityValidator,
    SignalCapability
)

class MyConsumer:
    consumer_id = "my_consumer"
    declared_capabilities = {
        SignalCapability.SEMANTIC_PROCESSING,
        SignalCapability.TABLE_PARSING,
        SignalCapability.GRAPH_CONSTRUCTION
    }

validator = CapabilityValidator()
result = validator.validate(MyConsumer(), "ENRICHMENT_DATA")
assert result.can_process
```

### Gate 4: Channel Authenticity and Integrity
**Purpose**: Confirm all data channels are explicit, traceable, governed, and resilient.

**Validation Criteria**:
- Flow must be explicitly registered
- Documentation path must be provided
- Traceability must be enabled
- Governance policy must be defined
- Change control and observability are recommended

**Implementation**: `channel_validator.py`

**Example**:
```python
from canonic_questionnaire_central.validations.runtime_validators import (
    ChannelValidator,
    DataFlow,
    ChannelType
)

validator = ChannelValidator()

# Register a data flow
flow = DataFlow(
    flow_id="MY_ENRICHMENT_FLOW",
    flow_type=ChannelType.ENRICHMENT_FLOW,
    source="my_source",
    destination="my_destination",
    data_schema="MySchema",
    governance_policy="my_policy",
    is_explicit=True,
    is_documented=True,
    is_traceable=True,
    is_governed=True,
    documentation_path="docs/my_flow.md"
)

validator.register_flow(flow)
result = validator.validate_flow("MY_ENRICHMENT_FLOW")
assert result.valid
assert result.compliance_score == 1.0
```

## Enrichment Orchestrator

The `EnrichmentOrchestrator` coordinates all four validation gates and manages the enrichment process.

### Usage Example

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
    allowed_signal_types=["ENRICHMENT_DATA", "*"],
    allowed_policy_areas=["PA01", "PA02", "PA03"],
    min_confidence=0.50,
    max_signals_per_query=100
)

# Define consumer capabilities
consumer_capabilities = [
    SignalCapability.SEMANTIC_PROCESSING,
    SignalCapability.TABLE_PARSING,
    SignalCapability.GRAPH_CONSTRUCTION,
    SignalCapability.FINANCIAL_ANALYSIS
]

# Create enrichment request
request = EnrichmentRequest(
    consumer_id="pdt_analyzer",
    consumer_scope=consumer_scope,
    consumer_capabilities=consumer_capabilities,
    target_policy_areas=["PA01", "PA02"],
    target_questions=["Q001", "Q002"],
    requested_context=["municipalities", "subregions", "policy_area_mappings"]
)

# Perform enrichment
result = orchestrator.enrich(request)

if result.success:
    print(f"Enrichment succeeded!")
    print(f"Gates passed: {result.gate_status}")
    
    # Access enriched data
    municipalities = result.enriched_data["data"]["municipalities"]
    subregions = result.enriched_data["data"]["subregions"]
    pa_mappings = result.enriched_data["data"]["policy_area_mappings"]
else:
    print(f"Enrichment failed: {result.violations}")
```

## PDET Municipalities Data

The system includes comprehensive data for 170 PDET municipalities across 16 subregions.

### Data Structure

```json
{
  "overview": {
    "total_municipalities": 170,
    "total_subregions": 16,
    "total_veredas": 11000,
    "total_population": 6600000,
    "rural_percentage": 24.0,
    "planning_horizon_years": 15
  },
  "subregions": [
    {
      "subregion_id": "SR01",
      "name": "Alto Patía y Norte del Cauca",
      "department": ["Cauca"],
      "municipalities": [
        {
          "municipality_code": "19355",
          "name": "Jambaló",
          "category": "Sixth",
          "population": 16800,
          "patr_initiatives": 142,
          "multidimensional_poverty_rate": 45.2,
          "key_pdet_pillars": ["pillar_1", "pillar_4", "pillar_8"]
        }
      ]
    }
  ],
  "policy_area_mappings": {
    "PA01_Gender": {
      "relevant_subregions": ["SR04", "SR05", "SR08"],
      "key_indicators": ["women_labor_participation", "gender_wage_gap"],
      "pdet_pillars": ["pillar_4", "pillar_8"]
    }
  }
}
```

### Accessing PDET Data

```python
from canonic_questionnaire_central.colombia_context import (
    get_pdet_municipalities,
    get_pdet_subregions,
    get_pdet_municipalities_for_policy_area
)

# Get all PDET data
pdet_data = get_pdet_municipalities()

# Get subregions
subregions = get_pdet_subregions()

# Get municipalities for specific policy area
pa01_municipalities = get_pdet_municipalities_for_policy_area("PA01")
```

## Compliance and Reporting

### Generate Compliance Report

```python
# After performing enrichments
report = orchestrator.get_enrichment_report()

print(f"Total requests: {report['enrichment_orchestrator_report']['total_requests']}")
print(f"Success rate: {report['enrichment_orchestrator_report']['success_rate']:.2%}")

# Gate-specific reports
gate1_report = report['gate_1_scope_validator']
gate2_report = report['gate_2_value_add_scorer']
gate3_report = report['gate_3_capability_validator']
gate4_report = report['gate_4_channel_validator']
```

### Export Enrichment Log

```python
from pathlib import Path

# Export detailed log
orchestrator.export_enrichment_log(Path("enrichment_log.json"))
```

## Integration with Canonical Questionnaire

### Policy Area Targeting

The system provides automatic filtering of PDET data based on policy areas:

- **PA01 (Gender)**: Municipalities with gender-specific initiatives
- **PA02 (Violence/Security)**: All PDET municipalities (high relevance)
- **PA03 (Environment)**: Municipalities with deforestation/mining issues
- **PA04 (Economic Development)**: Municipalities with agricultural projects
- **PA05 (Victims/Restitution)**: Municipalities with land restitution programs
- **PA06 (Children/Youth)**: Municipalities with education initiatives
- **PA07 (Peace Building)**: All municipalities with reconciliation programs
- **PA08 (Human Rights)**: Municipalities with human rights defenders
- **PA09 (Justice)**: Municipalities with transitional justice processes
- **PA10 (International)**: Border municipalities with international cooperation

### PDET Pillars Mapping

The 8 PDET pillars map to questionnaire dimensions:

1. **Pillar 1**: Land formalization → Dimension: Structural
2. **Pillar 2**: Infrastructure → Dimension: Instrumental
3. **Pillar 3**: Rural health → Dimension: Substantive
4. **Pillar 4**: Education → Dimension: Procedural
5. **Pillar 5**: Housing/Water → Dimension: Substantive
6. **Pillar 6**: Economic reactivation → Dimension: Instrumental
7. **Pillar 7**: Food security → Dimension: Substantive
8. **Pillar 8**: Reconciliation → Dimension: Symbolic

## Data Governance

### Update Frequency
- Quarterly updates from authoritative sources
- Last validation: 2025-10-15
- Change control protocol: CCP-PDET-2024

### Authoritative Sources
- Agencia de Renovación del Territorio (ART)
- Departamento Nacional de Planeación (DNP)
- DANE (statistics)
- OCAD Paz (investment data)

### Access Control
- **Public indicators**: Population, category, subregion
- **Restricted indicators**: Security metrics, detailed fiscal data
- **Required scope**: `pdet_context` for full access

## Testing

Run the test suite:

```bash
# Test channel validator
pytest tests/test_channel_validator.py -v

# Test enrichment orchestrator
pytest tests/test_enrichment_orchestrator.py -v

# Run all enrichment tests
pytest tests/ -k "channel_validator or enrichment_orchestrator" -v
```

## Troubleshooting

### Common Issues

**Issue**: Gate 1 fails with "scope not authorized"
- **Solution**: Ensure consumer scope includes `ENRICHMENT_DATA` in `allowed_signal_types`

**Issue**: Gate 3 fails with "missing capabilities"
- **Solution**: Consumer must declare `SEMANTIC_PROCESSING` and `TABLE_PARSING` capabilities

**Issue**: No municipalities returned
- **Solution**: Check that target policy areas match municipalities in PDET subregions

**Issue**: Gate 4 fails with "flow not documented"
- **Solution**: Ensure data flow has `is_documented=True` and valid `documentation_path`

## References

- [Decreto Ley 893 de 2017](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=83195)
- [Central de Información PDET](https://www.renovacionterritorio.gov.co/PDET)
- [OCAD Paz](https://www.minhacienda.gov.co/webcenter/portal/Ocadpaz)
- [Agencia de Renovación del Territorio](https://www.renovacionterritorio.gov.co/)

## License

Proprietary - F.A.R.F.A.N Pipeline Team © 2024
