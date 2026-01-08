# CL03 Territorio-Ambiente: PDET Contextual Enrichment

## Overview

This directory contains contextual enrichment data for the **CL03 Territorio-Ambiente** cluster, which integrates relevant PDET (Programas de Desarrollo con Enfoque Territorial) municipality information to provide territorial context for policy analysis.

## Cluster Scope

**Cluster ID**: CL03  
**Cluster Name**: Territorio-Ambiente  
**Policy Areas**:
- **PA04**: Derechos Económicos, Sociales y Culturales (Economic, Social, and Cultural Rights)
- **PA08**: Líderes Sociales y Defensores DDHH (Social Leaders and Human Rights Defenders)

**Rationale**: Sustainable territorial development and environmental management

## Enrichment File

### contextual_enrichment.json

This file provides PDET contextual information that enriches the questionnaire analysis for CL03 with territorial specificity.

**Key Contents**:
- PDET municipality mappings for PA04 and PA08
- Subregional context and indicators
- PDET pillar alignments
- Usage guidance for different analysis phases
- Data governance and compliance metadata

## Four Validation Gates Compliance

The CL03 enrichment is fully compliant with all four validation gates:

### ✅ Gate 1: Consumer Scope Validity

- **Required Scope**: `pdet_context`
- **Allowed Signal Types**: `ENRICHMENT_DATA`
- **Authorized Policy Areas**: PA04, PA08

Consumers must have appropriate scope authorization to access PDET contextual data.

### ✅ Gate 2: Value Contribution

- **Estimated Value-Add**: 35%
- **Value Sources**:
  1. Territorial targeting for PA04 (Economic/Social Rights)
  2. Human rights defender protection context for PA08
  3. Municipality-level indicators for territorial planning
  4. OCAD Paz investment data for resource allocation

The enrichment materially improves analysis quality by providing territorial specificity and enabling evidence-based targeting.

### ✅ Gate 3: Consumer Capability and Readiness

- **Required Capabilities**:
  - `SEMANTIC_PROCESSING`: Understanding territorial context
  - `TABLE_PARSING`: Processing municipality data tables
  
- **Recommended Capabilities**:
  - `GRAPH_CONSTRUCTION`: Subregion-municipality relationships
  - `FINANCIAL_ANALYSIS`: OCAD Paz investment analysis

### ✅ Gate 4: Channel Authenticity and Integrity

- **Flow ID**: `CL03_PDET_ENRICHMENT`
- **Source**: `colombia_context.pdet_municipalities`
- **Destination**: `clusters.CL03_territorio_ambiente`
- **Governance Policy**: `PDET_ENRICHMENT_POLICY_2024`
- **Documentation**: Available in `colombia_context/README_PDET_ENRICHMENT.md`

All data flows are explicitly documented, traceable, and governed.

## Policy Area Details

### PA04: Economic, Social, and Cultural Rights

**PDET Relevance**: HIGH

**Relevant Subregions** (6):
- SR02: Arauca
- SR03: Bajo Cauca y Nordeste Antioqueño
- SR04: Cuenca del Caguán y Piedemonte Caqueteño
- SR06: Chocó
- SR07: Macarena-Guaviare
- SR08: Montes de María

**Key Indicators**:
- Formal enterprises
- Agricultural productivity
- Market access

**PDET Pillars**:
- Pillar 6: Economic reactivation
- Pillar 7: Food security

**Contextual Notes**:
- PDET municipalities in this policy area focus on territorial economic development
- Key indicators include formal enterprises, agricultural productivity, and market access
- Relevant PDET pillars: Land formalization (1), Economic reactivation (6), Food security (7)

### PA08: Social Leaders and Human Rights Defenders

**PDET Relevance**: CRITICAL

**Relevant Subregions** (1):
- SR08: Montes de María

**Key Indicators**:
- Defenders security
- Justice access
- Human rights violations tracking

**PDET Pillars**:
- Pillar 8: Reconciliation and peacebuilding

**Contextual Notes**:
- PDET municipalities face significant challenges protecting social leaders
- Special attention to ethnic territories and rural areas with armed conflict presence
- Key focus on security mechanisms, justice access, and human rights monitoring

## Usage Guidance

### For Diagnosis (Dimension 1)

Use PDET municipality data to contextualize baseline indicators:

- Reference multidimensional poverty rates and fiscal autonomy levels
- Consider ethnic composition when analyzing territorial challenges
- Compare plan baselines against PDET municipal averages

**Example**: Question Q091 asks about diagnostic data for DESC rights. Use PDET municipality poverty rates as benchmarks.

### For Targeting (Dimensions 2-3)

Filter questions by relevant PDET subregions for territorial specificity:

- Prioritize municipalities with high poverty rates or low fiscal autonomy
- Consider PATR initiatives and active route initiatives as capacity indicators
- Focus on subregions with high relevance to policy areas

**Example**: When analyzing PA04 programs, prioritize municipalities in subregions SR02-SR08 with low fiscal autonomy.

### For Resource Allocation (Dimension 4)

Reference OCAD Paz investment data for co-financing opportunities:

- Consider existing PDET pillar investments when planning new initiatives
- Analyze gaps between PATR initiatives and active implementation
- Identify complementary funding sources

**Example**: Question Q093 asks about financial allocations. Cross-reference with OCAD Paz investment data to identify co-financing opportunities.

### For Protection Strategies (PA08)

Identify high-risk territories for social leader protection:

- Cross-reference with ethnic territories requiring differentiated approaches
- Consider armed conflict dynamics in protection planning
- Align with PDET Pillar 8 (Reconciliation) initiatives

**Example**: Question Q236 asks about theory of change for leader protection. Use PA08 subregion context to validate protection strategies against territorial armed conflict dynamics.

## Territorial Context

- **Total PDET Municipalities**: 170
- **Total Subregions**: 16
- **Rural Percentage**: 24.0%
- **Planning Horizon**: 15 years
- **Legal Basis**: Acuerdo de Paz Punto 1 + Decreto Ley 893/2017

## Integration Examples

### Example 1: Baseline Diagnostics (Q091)

**Question**: ¿El diagnóstico presenta datos numéricos para el área de DESC?

**Integration Point**: Baseline diagnostics  
**PDET Context**: Use municipality multidimensional poverty rates as benchmark for DESC indicators  
**Expected Enrichment**: Compare plan baselines against PDET municipal averages

### Example 2: Financial Allocations (Q093)

**Question**: ¿Se identifican en el PPI recursos monetarios asignados a programas sociales?

**Integration Point**: Financial allocations  
**PDET Context**: Cross-reference plan budgets with OCAD Paz investment data  
**Expected Enrichment**: Identify co-financing opportunities and resource gaps

### Example 3: Theory of Change for Protection (Q236)

**Question**: ¿Existe una teoría de cambio explícita para la protección de líderes?

**Integration Point**: Theory of change for leader protection  
**PDET Context**: Use PA08 subregion context to validate protection strategies  
**Expected Enrichment**: Ensure protection strategies account for territorial armed conflict dynamics

## Data Governance

### Authoritative Sources
- Decreto Ley 893 de 2017
- Central de Información PDET
- OCAD Paz Session Records (October 2025)
- DNP - Sistema de Estadísticas Territoriales
- Agencia de Renovación del Territorio (ART)

### Update Schedule
- **Frequency**: Quarterly
- **Last Update**: 2026-01-08T00:00:00Z
- **Change Control**: CCP-PDET-2024

### Data Owner
- **Owner**: Agencia de Renovación del Territorio (ART)
- **Compliance Framework**: Decreto Ley 893 de 2017

### Access Control
- **Public Indicators**: Population, category, subregion
- **Restricted Indicators**: Security metrics, detailed fiscal data
- **Required Scope**: `pdet_context` for full access

## Validation

The enrichment has been validated against all four gates:

```bash
# Run validation tests
cd /home/runner/work/FARFAN_MPP/FARFAN_MPP
python3 tests/test_cl03_enrichment.py
```

### Validation Results

All tests pass successfully:
- ✅ File Structure
- ✅ Policy Areas Coverage
- ✅ Gate 1 (Scope Validation)
- ✅ Gate 2 (Value-Add)
- ✅ Gate 3 (Capabilities)
- ✅ Gate 4 (Channel Authenticity)
- ✅ Orchestrator Integration
- ✅ Subregion References

## Files in This Directory

```
CL03_territorio_ambiente/
├── metadata.json                    # Cluster metadata
├── questions.json                   # 60 questions for PA04 and PA08
├── aggregation_rules.json           # Cluster scoring rules
├── contextual_enrichment.json       # PDET contextual enrichment (NEW)
└── README_ENRICHMENT.md            # This file (NEW)
```

## Related Documentation

- [PDET Enrichment System Overview](../../colombia_context/README_PDET_ENRICHMENT.md)
- [Data Governance Compliance Report](../../colombia_context/DATA_GOVERNANCE_COMPLIANCE_REPORT.md)
- [PDET Municipalities Data](../../colombia_context/pdet_municipalities.json)

## Technical Implementation

### Loading Enrichment Data

```python
import json
from pathlib import Path

# Load CL03 enrichment
enrichment_path = Path("canonic_questionnaire_central/clusters/CL03_territorio_ambiente/contextual_enrichment.json")
with open(enrichment_path, 'r', encoding='utf-8') as f:
    cl03_enrichment = json.load(f)

# Access PA04 context
pa04_context = cl03_enrichment["policy_areas"]["PA04"]
pa04_subregions = pa04_context["relevant_subregions"]
pa04_indicators = pa04_context["key_indicators"]

# Access usage guidance
guidance = cl03_enrichment["usage_guidance"]
diagnosis_guidance = guidance["for_diagnosis"]
```

### Using with Enrichment Orchestrator

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

# Create orchestrator
orchestrator = EnrichmentOrchestrator(strict_mode=True, enable_all_gates=True)

# Define scope
scope = SignalScope(
    scope_name="CL03 Analyzer",
    scope_level=ScopeLevel.EVIDENCE_COLLECTION,
    allowed_signal_types=["ENRICHMENT_DATA"],
    allowed_policy_areas=["PA04", "PA08"],
    min_confidence=0.50,
    max_signals_per_query=100
)

# Define capabilities
capabilities = [
    SignalCapability.SEMANTIC_PROCESSING,
    SignalCapability.TABLE_PARSING,
    SignalCapability.GRAPH_CONSTRUCTION
]

# Create request
request = EnrichmentRequest(
    consumer_id="cl03_analyzer",
    consumer_scope=scope,
    consumer_capabilities=capabilities,
    target_policy_areas=["PA04", "PA08"],
    target_questions=["Q091", "Q093", "Q236"],
    requested_context=["municipalities", "subregions", "policy_area_mappings"]
)

# Enrich
result = orchestrator.enrich(request)

if result.success:
    # Use enriched data
    municipalities = result.enriched_data["data"]["municipalities"]
    subregions = result.enriched_data["data"]["subregions"]
```

## Maintenance

### Updating Enrichment Data

When PDET municipality data is updated:

1. Update `pdet_municipalities.json` with new data
2. Regenerate `contextual_enrichment.json` using the creation script
3. Update `_generated_at` timestamp
4. Run validation tests to ensure compliance
5. Update this README if structure changes

### Change Log

- **2026-01-08**: Initial creation with PA04 and PA08 context
  - 6 subregions for PA04
  - 1 subregion for PA08
  - Integration examples for 3 key questions
  - All 4 gates validated and compliant

## Contact

For questions about this enrichment:
- **Data Owner**: Agencia de Renovación del Territorio (ART)
- **Technical Support**: F.A.R.F.A.N Pipeline Team
- **Governance**: See Data Governance Compliance Report

---

**Status**: ✅ VALIDATED AND OPERATIONAL

Last validated: 2026-01-08  
Validation status: All 4 gates passed  
Next review: 2026-04-08 (Quarterly)
