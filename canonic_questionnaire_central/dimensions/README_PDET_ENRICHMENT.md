# PDET Context Enrichment for Dimensions

## Overview

This directory contains PDET (Programas de Desarrollo con Enfoque Territorial) context enrichment files for each of the six dimensions of the F.A.R.F.A.N questionnaire. These enrichment files provide PDET-specific evaluation criteria, pillar mappings, validation gate alignments, and common gap patterns to enable rigorous evaluation of development plans from Colombia's 170 PDET municipalities.

## Purpose

PDET municipalities are conflict-affected territories with unique characteristics:
- **High poverty rates**: Average 46.8% multidimensional poverty
- **Weak fiscal capacity**: 88.8% are Category 6 municipalities
- **Ethnic diversity**: High indigenous and Afro-Colombian populations
- **Conflict legacy**: Victimization, displacement, armed actors presence
- **Rural focus**: 24% rural population with territorial disaggregation to vereda level
- **15-year horizon**: Special planning regime under Decree Law 893/2017

These context files ensure that dimension evaluations are calibrated to PDET realities and aligned with the four validation gates.

## Structure

Each dimension has a corresponding `pdet_context.json` file in its directory:

```
dimensions/
├── DIM01_INSUMOS/
│   ├── metadata.json
│   ├── questions.json
│   ├── questions/
│   └── pdet_context.json          ← PDET enrichment
├── DIM02_ACTIVIDADES/
│   ├── metadata.json
│   ├── questions.json
│   ├── questions/
│   └── pdet_context.json          ← PDET enrichment
├── DIM03_PRODUCTOS/
│   ├── metadata.json
│   ├── questions.json
│   ├── questions/
│   └── pdet_context.json          ← PDET enrichment
├── DIM04_RESULTADOS/
│   ├── metadata.json
│   ├── questions.json
│   ├── questions/
│   └── pdet_context.json          ← PDET enrichment
├── DIM05_IMPACTOS/
│   ├── metadata.json
│   ├── questions.json
│   ├── questions/
│   └── pdet_context.json          ← PDET enrichment
└── DIM06_CAUSALIDAD/
    ├── metadata.json
    ├── questions.json
    ├── questions/
    └── pdet_context.json          ← PDET enrichment
```

## PDET Context Schema

Each `pdet_context.json` file contains:

### 1. Validation Gates Alignment

Specifies how the dimension aligns with the four validation gates:

- **Gate 1 (Scope)**: Required scope levels and signal types
- **Gate 2 (Value-Add)**: Estimated value-add and components
- **Gate 3 (Capability)**: Required and recommended capabilities
- **Gate 4 (Channel)**: Data flow specifications and governance

### 2. PDET Pillar Mapping

Maps dimension evaluation criteria to PDET's 8 pillars:

1. **Pillar 1**: Land formalization and property rights
2. **Pillar 2**: Infrastructure and land adequacy
3. **Pillar 3**: Rural health
4. **Pillar 4**: Rural education
5. **Pillar 5**: Housing and water
6. **Pillar 6**: Economic reactivation
7. **Pillar 7**: Food security and nutrition
8. **Pillar 8**: Reconciliation and peacebuilding

Each dimension identifies primary and secondary pillar relevance with specific requirements.

### 3. PDET-Specific Criteria

Dimension-specific evaluation criteria tailored to PDET municipalities:

- **Territorial disaggregation**: Vereda, corregimiento, urban/rural
- **Ethnic differential approach**: Indigenous, Afro-Colombian groups
- **Conflict-affected indicators**: Victimization, displacement, security
- **Fiscal capacity constraints**: SGP dependency, OCAD Paz resources
- **PATR alignment**: Integration with regional transformation plans
- **Participation mechanisms**: Community councils, ethnic authorities

### 4. Policy Area Specificity

Dimension requirements broken down by the 10 policy areas:

- **PA01**: Gender Equality
- **PA02**: Violence & Security
- **PA03**: Environment & Climate
- **PA04**: Economic Development
- **PA05**: Victims & Restitution
- **PA06**: Children & Youth
- **PA07**: Peace Building
- **PA08**: Human Rights
- **PA09**: Justice
- **PA10**: International/Migration

Each policy area has specific diagnostic/intervention requirements and priority subregions.

### 5. Common Gaps

Documented patterns of planning failures specific to PDET municipalities:

- Gap description and prevalence
- Impact on planning quality
- Remediation strategies

## Dimension-Specific Focus

### DIM01 - INSUMOS (Diagnostic & Baseline)

**Focus**: Diagnostic quality, baseline data, resource assessment

**Key PDET Criteria**:
- Territorial disaggregation to vereda level
- Multidimensional poverty baselines (>40% threshold)
- Conflict-affected indicators
- Fiscal autonomy assessment (Category 6 dominance)
- PATR initiatives integration
- Data recency (max 3 years old)

**Primary Pillars**: Land formalization (P1), Education (P4)

**Common Gaps**: Territorial aggregation, ethnic invisibilization, outdated baselines

### DIM02 - ACTIVIDADES (Intervention Design)

**Focus**: Activity formalization, causal mechanisms, chronograms

**Key PDET Criteria**:
- PATR alignment and timeline consistency
- Community participation mechanisms
- Differential approach by population groups
- Causal mechanism specification
- Responsible entity clarity
- Budget detail with funding sources

**Primary Pillars**: Infrastructure (P2), Economic reactivation (P6), Reconciliation (P8)

**Common Gaps**: Generic activities, missing causal logic, undefined responsibilities

### DIM03 - PRODUCTOS (Outputs & Deliverables)

**Focus**: Product specification, measurement units, deliverable clarity

**Key PDET Criteria**:
- Product specification rigor (quantitative, units, quality)
- PATR output consistency
- Territorial disaggregation of products
- Measurement feasibility
- Beneficiary quantification with disaggregation

**Primary Pillars**: Infrastructure (P2), Education (P4), Health (P3)

**Common Gaps**: Vague deliverables, no baselines, aggregated targets

### DIM04 - RESULTADOS (Outcomes & Population Change)

**Focus**: Outcome definition, measurement, causal attribution

**Key PDET Criteria**:
- Outcome vs. output distinction
- Causal attribution (contribution not attribution)
- Measurement rigor (baselines, targets, methods)
- Temporal realism (appropriate lag times)
- Differential outcomes by population groups

**Primary Pillars**: Land formalization (P1), Education (P4), Reconciliation (P8)

**Common Gaps**: Output-outcome confusion, no causal theory, unmeasurable outcomes

### DIM05 - IMPACTOS (Long-term Transformations)

**Focus**: Structural change, sustainability, 15-year vision

**Key PDET Criteria**:
- Structural transformation focus (not incremental change)
- 15-year horizon (2017-2032)
- Sustainability mechanisms explicit
- Attribution complexity acknowledged
- Territorial equity in impacts
- Conflict transformation demonstrated

**Primary Pillars**: Reconciliation (P8), Land formalization (P1), Economic transformation (P6)

**Common Gaps**: Outcomes mislabeled as impacts, no sustainability mechanism, unrealistic timelines

### DIM06 - CAUSALIDAD (Theory of Change)

**Focus**: Causal logic, assumptions, evidence base

**Key PDET Criteria**:
- Explicit theory of change with all results levels
- Assumption identification and testing
- Causal mechanism specification
- Evidence base for causal claims
- Context specificity (conflict, ethnicity, capacity)
- Plausibility checks

**All Pillars**: Theory of change required for all interventions

**Common Gaps**: Missing theory, implicit assumptions, linear thinking, borrowed theories

## Usage

### For Methods (Extractors/Analyzers)

Methods can load PDET context to inform evaluation:

```python
import json
from pathlib import Path

def load_pdet_context(dimension_id: str) -> dict:
    """Load PDET context for a dimension."""
    dimension_dir = Path(f"canonic_questionnaire_central/dimensions/{dimension_id}")
    pdet_context_file = dimension_dir / "pdet_context.json"
    
    with open(pdet_context_file, "r", encoding="utf-8") as f:
        return json.load(f)

# Example: Load DIM01 context
dim01_context = load_pdet_context("DIM01_INSUMOS")

# Access criteria
ethnic_approach = dim01_context["pdet_specific_criteria"]["ethnic_differential_approach"]
required_groups = ethnic_approach["ethnic_groups"]
# ['Indígena', 'Afrodescendiente', 'Mestizo', 'ROM']

# Access pillar mapping
primary_pillars = dim01_context["pdet_pillar_mapping"]["primary_pillars"]
for pillar in primary_pillars:
    print(f"Pillar {pillar['pillar_id']}: {pillar['pillar_name']}")
    print(f"Relevance: {pillar['relevance_score']}")
```

### For Validators

Validators can check alignment with validation gates:

```python
def validate_gate_alignment(dimension_id: str, consumer_scope: dict) -> bool:
    """Validate consumer scope against dimension requirements."""
    context = load_pdet_context(dimension_id)
    gate1 = context["validation_gates_alignment"]["gate_1_scope"]
    
    required_scope = gate1["required_scope"]
    allowed_types = gate1["allowed_signal_types"]
    
    # Check scope authorization
    if required_scope not in consumer_scope["allowed_scopes"]:
        return False
    
    # Check signal types
    for signal_type in consumer_scope["requested_types"]:
        if signal_type not in allowed_types and "*" not in allowed_types:
            return False
    
    return True
```

### For Question Evaluation

Questions can be evaluated against PDET-specific criteria:

```python
def evaluate_question_pdet_alignment(question_data: dict, dimension_id: str, policy_area_id: str) -> dict:
    """Evaluate question alignment with PDET criteria."""
    context = load_pdet_context(dimension_id)
    
    # Get policy area specific requirements
    pa_specificity = context["pdet_specific_criteria"].get("policy_area_specificity", {})
    pa_requirements = pa_specificity.get(policy_area_id, {})
    
    # Get common gaps to check for
    common_gaps = context["common_diagnostic_gaps"] if dimension_id == "DIM01_INSUMOS" else \
                  context.get("common_design_gaps", context.get("common_outcome_gaps", {}))
    
    evaluation = {
        "dimension_id": dimension_id,
        "policy_area_id": policy_area_id,
        "pdet_criteria_met": [],
        "pdet_criteria_failed": [],
        "detected_gaps": [],
        "pillar_alignment": []
    }
    
    # Perform evaluation logic here
    
    return evaluation
```

## Integration with Enrichment Orchestrator

The PDET context files integrate with the enrichment orchestrator:

```python
from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
    EnrichmentOrchestrator,
    EnrichmentRequest
)

orchestrator = EnrichmentOrchestrator(strict_mode=True, enable_all_gates=True)

# Request enrichment for specific dimension
request = EnrichmentRequest(
    consumer_id="dim01_evaluator",
    consumer_scope=scope,
    consumer_capabilities=capabilities,
    target_policy_areas=["PA01", "PA02"],
    target_questions=["Q001", "Q002"],
    target_dimensions=["DIM01_INSUMOS"],  # Dimension-specific enrichment
    requested_context=["municipalities", "pdet_pillars", "policy_area_mappings"]
)

result = orchestrator.enrich(request)
```

## Validation

To validate PDET enrichment files:

```bash
# Run PDET enrichment validation
python scripts/validate_pdet_enrichment.py

# Validate specific dimension
python scripts/validate_pdet_enrichment.py --dimension DIM01_INSUMOS
```

## Maintenance

### Update Schedule

PDET context files should be updated:
- **Quarterly**: For PATR implementation status, OCAD Paz approvals
- **Annually**: For poverty rates, demographic changes, pillar progress
- **As needed**: For legal framework changes, new PDET policies

### Change Control

All changes to PDET context files must:
1. Document change in metadata `change_log`
2. Increment version number
3. Update `last_updated` timestamp
4. Validate against schema
5. Run full test suite
6. Update this README if structure changes

## References

### Legal Framework
- [Decreto Ley 893 de 2017](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=83195) - PDET legal basis
- [Acuerdo de Paz Punto 1](https://www.cancilleria.gov.co/acuerdo-final-paz) - Territorial rural reform

### Data Sources
- [Agencia de Renovación del Territorio (ART)](https://www.renovacionterritorio.gov.co/)
- [Central de Información PDET](https://www.renovacionterritorio.gov.co/PDET)
- [OCAD Paz](https://www.minhacienda.gov.co/webcenter/portal/Ocadpaz)
- [DANE - Statistics](https://www.dane.gov.co/)

### Related Documentation
- `canonic_questionnaire_central/colombia_context/README_PDET_ENRICHMENT.md` - Main PDET enrichment system
- `canonic_questionnaire_central/colombia_context/pdet_municipalities.json` - Detailed municipality data
- `canonic_questionnaire_central/patterns/pdet_empirical_patterns.json` - PDET-specific patterns

## License

Proprietary - F.A.R.F.A.N Pipeline Team © 2024

## Contact

For questions about PDET context enrichment:
- Technical issues: Use GitHub Issues
- Content updates: Contact Policy Analytics Research Unit
- PDET data inquiries: Reference ART official sources

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-08  
**Author**: PDET Enrichment System
