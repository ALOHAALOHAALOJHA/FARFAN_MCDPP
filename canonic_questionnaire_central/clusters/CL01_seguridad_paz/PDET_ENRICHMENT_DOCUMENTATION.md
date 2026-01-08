# CL01 Seguridad y Paz - PDET Enrichment Documentation

## Overview

The CL01_seguridad_paz cluster has been enriched with comprehensive PDET (Programas de Desarrollo con Enfoque Territorial) contextual information to support evidence-based policy analysis in territories historically affected by armed conflict.

## Enrichment Date

**Date**: 2026-01-08  
**Version**: 1.0.0  
**Status**: ✓ VALIDATED

## What Was Added

The cluster's `metadata.json` file now includes a comprehensive `pdet_context` object with the following structure:

### 1. Core Context
- **Relevance**: CRITICAL
- **Description**: Rationale for why PDET context is essential for security and peace analysis
- **Territorial Scope**: 170 municipalities, 16 subregions, 83% of conflict victims

### 2. Security & Peace Challenges (5 categories)
1. **Violence Prevention**
   - Homicides, displacement, threats, sexual violence, landmines, recruitment
   - Key indicators: Homicide rates, RUV cases, early warnings
   
2. **Institutional Presence**
   - Gaps: Police coverage, justice system, early warning systems
   - Required capacities: Municipal victim liaison, victim attention points, transitional justice committees
   
3. **Victims Attention**
   - Challenges: Territorial extension, underreporting, return guarantees
   - Mandatory actions: Collective reparation, victim participation, coordination with UARIV
   
4. **Peace Building**
   - Initiatives: Peace councils, reconciliation processes, ex-combatant reintegration
   - Challenges: Armed groups persistence, stigmatization, social conflicts
   
5. **Transitional Justice**
   - Components: JEP, Truth Commission, Search for Disappeared
   - Municipal role: Facilitate hearings, support victims, implement non-repetition guarantees

### 3. Institutional Actors (6 entities)
- **ART** (Territorial Renewal Agency): Coordinates PDET/PATR implementation
- **UARIV** (Victims Unit): Attention and reparation coordination
- **Defensoría del Pueblo**: Early Warning System (SAT)
- **JEP**: Special Jurisdiction for Peace
- **Police/Military**: Security and public order
- **Personería Municipal**: Human rights oversight

### 4. Financing Context (5 mechanisms)
- **SGR Paz**: Peace allocation from royalties
- **OCAD Paz**: Decision-making body for peace projects
- **UARIV Co-financing**: Joint funding for reparation projects
- **International Cooperation**: UN, USAID, EU funding
- **Budget Constraints**: Fiscal autonomy challenges in category 6 municipalities

### 5. Territorial Disaggregation (4 levels)
- Municipal head vs rural dispersed
- PDET villages (11,000 total)
- Indigenous reserves and Afro-Colombian community councils
- Peasant reserve zones (ZRC)

### 6. Coherence Requirements
- **PATR Alignment**: Must incorporate PATR initiatives (Pillar 8)
- **PMI Standards**: Minimum standards from Peace Implementation Framework
- **Continuity**: 15-year PDET horizon vs 4-year PDM
- **Ethnic Consultation**: Prior consultation requirements (ILO 169)
- **Gender Approach**: Transversal gender perspective

### 7. Monitoring & Evaluation
- PDET indicators (homicide rates, early warnings attended, victim reparations)
- Biannual reporting to ART
- Participatory monitoring with citizen oversight
- Adaptive management based on security context evolution

### 8. Legal Frameworks (6 key documents)
- Decree Law 893/2017 (PDET creation)
- Law 1448/2011 (Victims Law)
- Legislative Act 01/2017 & Law 1957/2019 (JEP)
- Final Peace Agreement (2016) - Point 5 Victims
- Decree 660/2018 (Implementation Framework)
- Law 418/1997 (Public Order)

### 9. Cross-Cutting Themes
- Differential approach
- Gender perspective
- Territorial environment
- Citizen participation

## Validation Status

The enrichment has been validated against the four PDET enrichment gates:

### ✓ Gate 1: Scope Validity
- Consumer scope authorized for ENRICHMENT_DATA
- Policy areas PA02, PA03, PA07 properly covered
- CRITICAL relevance level appropriate

### ✓ Gate 2: Value Contribution
- 25 value items (exceeds 10% threshold)
- Materially improves policy analysis capabilities
- Enables territorial targeting and resource allocation

### ✓ Gate 3: Capability & Readiness
- Requires SEMANTIC_PROCESSING (✓)
- Requires TABLE_PARSING (✓)
- Structured for graph construction and financial analysis

### ✓ Gate 4: Channel Authenticity & Integrity
- Explicit data flow: PDET municipalities → CL01 metadata
- Traceable: 6 legal frameworks referenced
- Governed: Coherence requirements defined
- Documented: This file + README_PDET_ENRICHMENT.md

## Usage Example

```python
import json

# Load cluster metadata
with open('canonic_questionnaire_central/clusters/CL01_seguridad_paz/metadata.json') as f:
    cl01 = json.load(f)

# Access PDET context
pdet = cl01['pdet_context']

# Check relevance
print(f"Relevance: {pdet['relevance']}")  # CRITICAL

# Get security challenges
security_challenges = pdet['security_peace_challenges_pdet']
print(f"Number of challenge categories: {len(security_challenges)}")

# Get institutional actors
actors = pdet['institutional_actors']
for actor_id, actor_info in actors.items():
    print(f"{actor_info['name']}: {actor_info['role']}")

# Get financing mechanisms
financing = pdet['financing_context']
for mechanism_id, mechanism_info in financing.items():
    print(f"{mechanism_info['name']}: {mechanism_info['description']}")
```

## Validation Script

A validation script is provided at:
```bash
python3 scripts/validate_cl01_pdet_enrichment.py
```

This script:
- Validates JSON structure
- Checks all required fields are present
- Verifies alignment with validation gates
- Produces detailed validation report

## Impact

This enrichment enables:

1. **Better Contextualization**: Questions in CL01 can now be interpreted with full awareness of PDET territorial realities
2. **Targeted Analysis**: Consumers can filter and focus on PDET-specific security and peace challenges
3. **Institutional Coordination**: Clear mapping of which actors are responsible for what
4. **Financing Transparency**: Understanding of available funding mechanisms for security/peace initiatives
5. **Compliance Verification**: Ability to check alignment with PATR, PMI, and legal frameworks
6. **Territorial Precision**: Support for proper disaggregation at village, reserve, and community council levels

## Related Files

- **Source Data**: `canonic_questionnaire_central/colombia_context/pdet_municipalities.json`
- **Enrichment Guide**: `canonic_questionnaire_central/colombia_context/README_PDET_ENRICHMENT.md`
- **Comparison Cluster**: `canonic_questionnaire_central/clusters/CL02_grupos_poblacionales/metadata.json`
- **Validation Script**: `scripts/validate_cl01_pdet_enrichment.py`

## Maintenance

- **Update Frequency**: Quarterly (aligned with ART PATR updates)
- **Next Review**: 2026-04-08
- **Responsible**: F.A.R.F.A.N Pipeline Team
- **Change Protocol**: CCP-PDET-2024

## References

- [Decreto Ley 893 de 2017](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=83195)
- [Central de Información PDET](https://www.renovacionterritorio.gov.co/PDET)
- [OCAD Paz](https://www.minhacienda.gov.co/webcenter/portal/Ocadpaz)
- [Agencia de Renovación del Territorio](https://www.renovacionterritorio.gov.co/)

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-08  
**Author**: F.A.R.F.A.N MPP Copilot Agent
