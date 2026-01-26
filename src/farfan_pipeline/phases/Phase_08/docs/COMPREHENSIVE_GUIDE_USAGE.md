# Phase 8 Comprehensive Guide Integration - Usage Examples

This document provides comprehensive examples of using the new Phase 8 Comprehensive Guide integration.

## Overview

Phase 8 now integrates the complete Comprehensive Guide methodology for transforming FARFAN diagnostics into PDM-ready recommendations. The new capabilities include:

1. **9-dimensional Policy Capacity Framework** (Wu-Ramesh-Howlett)
2. **Howlett's Policy Instruments** (NATO taxonomy)
3. **Colombian Value Chain Methodology** (Cadena de Valor)
4. **Colombian Legal Framework** (PDM, SGP, Municipal Categories)
5. **Lenguaje Claro Narrative Generation** (Carver Principles)
6. **8-Step Transformation Pipeline**

## Quick Start

### Basic Transformation (FARFAN → PDM)

```python
from src.farfan_pipeline.phases.Phase_08 import (
    transform_farfan_to_pdm,
    MunicipalCategory,
    CapacityDimension
)

# Prepare FARFAN diagnostic data
farfan_diagnostic = {
    "central_problem": "Women in municipality lack access to violence prevention services",
    "causes": [
        "Insufficient awareness of rights and reporting mechanisms",
        "Absence of specialized services",
        "No institutional structure for gender policy",
        "Zero budget allocation"
    ],
    "effects": [
        "Normalized gender violence",
        "Survivors lack access to justice",
        "Perpetuation of discriminatory practices"
    ],
    "evidence": [
        "78% of respondents indicate lack of knowledge about reporting mechanisms",
        "65% report no specialized services within municipality",
        "Municipal budget allocates 0% to gender equality programs"
    ],
    "questions": ["Q001", "Q002", "Q003", "Q004", "Q005"]
}

# Prepare capacity evidence (9 dimensions)
capacity_evidence = {
    CapacityDimension.INDIVIDUAL_ANALYTICAL: [
        "Planning staff <3 or no advanced training",
        "No specialized knowledge in gender policy"
    ],
    CapacityDimension.INDIVIDUAL_OPERATIONAL: [
        "Staff understand basic procurement",
        "Budget execution at 75%"
    ],
    CapacityDimension.INDIVIDUAL_POLITICAL: [
        "No prior gender policy experience",
        "Weak stakeholder management skills"
    ],
    CapacityDimension.ORGANIZATIONAL_ANALYTICAL: [
        "No gender-disaggregated data collection systems",
        "No M&E unit"
    ],
    CapacityDimension.ORGANIZATIONAL_OPERATIONAL: [
        "High staff turnover (>50% per term)",
        "No standard operating procedures",
        "Weak inter-secretariat coordination"
    ],
    CapacityDimension.ORGANIZATIONAL_POLITICAL: [
        "No participation mechanisms beyond legal minimum",
        "Low community trust"
    ],
    CapacityDimension.SYSTEMIC_ANALYTICAL: [
        "Regional university 40km away",
        "Departmental women's office exists"
    ],
    CapacityDimension.SYSTEMIC_OPERATIONAL: [
        "Functional relationship with departmental government",
        "ICBF present in municipality"
    ],
    CapacityDimension.SYSTEMIC_POLITICAL: [
        "Moderate social capital",
        "Functional JACs"
    ]
}

# Execute transformation
result = transform_farfan_to_pdm(
    municipality_id="MUN_05001",
    municipality_category=MunicipalCategory.CATEGORY_5,
    policy_area="PA01",  # Gender Equality
    dimension="DIM01",   # Insumos (Diagnóstico)
    farfan_diagnostic=farfan_diagnostic,
    capacity_evidence=capacity_evidence
)

# Access results
if result.success:
    print(f"✓ Transformation successful (Quality: {result.quality_score:.1f}/100)")
    print(f"\n--- PROSE RECOMMENDATION ---")
    print(result.prose_recommendation.full_text)
    print(f"\n--- CAPACITY PROFILE ---")
    print(f"Overall Capacity: {result.capacity_profile.overall_capacity_level.value}")
    print(f"Binding Constraints: {len(result.capacity_profile.binding_constraints)}")
    print(f"\n--- VALUE CHAIN ---")
    print(f"Objetivo General: {result.value_chain.objetivo_general.text}")
    print(f"Objetivos Específicos: {len(result.value_chain.objetivos_especificos)}")
    print(f"Productos: {len(result.value_chain.productos)}")
    print(f"Actividades: {len(result.value_chain.actividades)}")
else:
    print("✗ Transformation failed")
    for step in result.steps:
        if not step.success:
            print(f"Failed at Step {step.step_number}: {step.step_name}")
            print(f"Errors: {step.errors}")
```

## Advanced Usage

### Step-by-Step Transformation

```python
from src.farfan_pipeline.phases.Phase_08 import get_transformation_pipeline
from src.farfan_pipeline.phases.Phase_08.phase8_27_00_policy_capacity_framework import (
    PolicyCapacityFramework,
    CapacityDimension
)
from src.farfan_pipeline.phases.Phase_08.phase8_28_00_howlett_instruments import (
    InstrumentSelectionEngine
)
from src.farfan_pipeline.phases.Phase_08.phase8_29_00_value_chain_integration import (
    build_value_chain_from_farfan,
    ValueChainValidator
)
from src.farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
    ColombianLegalFrameworkEngine,
    MunicipalCategory
)
from src.farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
    NarrativeGenerator
)

# 1. Assess Capacity
capacity_framework = PolicyCapacityFramework()
capacity_profile = capacity_framework.create_comprehensive_profile(
    municipality_id="MUN_05001",
    municipality_category=5,
    assessments=capacity_evidence
)

print(f"Capacity Assessment:")
print(f"  Overall: {capacity_profile.overall_capacity_level.value}")
print(f"  Binding Constraints: {len(capacity_profile.binding_constraints)}")
for i, constraint in enumerate(capacity_profile.binding_constraints, 1):
    print(f"    {i}. {constraint.dimension.value} ({constraint.level.value})")
    print(f"       Rationale: {constraint.rationale}")

# 2. Select Instruments
instrument_engine = InstrumentSelectionEngine()
instrument_mix = instrument_engine.select_instrument_mix(
    objective="Aumentar el conocimiento sobre derechos y mecanismos de denuncia",
    problem="Insufficient awareness of rights",
    capacity_profile=capacity_profile,
    municipality_category=5,
    policy_area="PA01",
    dimension="DIM01"
)

print(f"\nInstrument Selection:")
print(f"  Primary: {instrument_mix.primary_instrument.instrument_type.value}")
print(f"  Supporting: {[s.instrument_type.value for s in instrument_mix.supporting_instruments]}")
print(f"  Sequencing: {instrument_mix.sequencing_phase.value}")
print(f"  Budget Range: {instrument_mix.estimated_budget_range}")

# 3. Build Value Chain
value_chain = build_value_chain_from_farfan(
    municipality_id="MUN_05001",
    policy_area="PA01",
    dimension="DIM01",
    farfan_diagnostic=farfan_diagnostic,
    instrument_mixes={"obj1": instrument_mix}
)

print(f"\nValue Chain:")
print(f"  Objetivo General: {value_chain.objetivo_general.text}")
print(f"  Valid: {value_chain.is_valid}")
if not value_chain.is_valid:
    print(f"  Validation Report: {value_chain.validation_report}")

# 4. Check Legal Compliance
legal_engine = ColombianLegalFrameworkEngine()
legal_obligations = legal_engine.get_legal_obligations("PA01")

print(f"\nLegal Obligations for Gender Equality:")
for obligation in legal_obligations:
    print(f"  - {obligation.law_number}/{obligation.law_year}: {obligation.description}")
    print(f"    Mandatory PDM Section: {obligation.mandatory_pdm_section}")

# 5. Generate Narrative
narrative_generator = NarrativeGenerator()
prose = narrative_generator.generate_prose_recommendation(
    value_chain=value_chain,
    instrument_mixes={"obj1": instrument_mix},
    capacity_profile=capacity_profile,
    municipality_category=MunicipalCategory.CATEGORY_5
)

print(f"\nNarrative Quality:")
print(f"  Word Count: {prose.word_count}")
print(f"  Avg Sentence Length: {prose.average_sentence_length:.1f} words")
print(f"  Carver Compliance: {prose.carver_compliance_score:.1f}/100")
print(f"\nProse Recommendation:")
print(prose.full_text[:500] + "..." if len(prose.full_text) > 500 else prose.full_text)
```

### Capacity-Specific Instrument Selection

```python
from src.farfan_pipeline.phases.Phase_08.phase8_28_00_howlett_instruments import (
    InstrumentSelectionEngine,
    InstrumentType,
    InstrumentCategory
)

engine = InstrumentSelectionEngine()

# Get all feasible instruments for low-capacity municipality
capacity_profile  # from previous example

feasible_instruments = engine._filter_feasible_instruments(
    capacity_profile=capacity_profile,
    municipality_category=5
)

print(f"Feasible Instruments for Category 5, Low Capacity:")
print(f"  Total: {len(feasible_instruments)}")
for instrument in feasible_instruments[:5]:  # Show first 5
    print(f"  - {instrument.instrument_type.value}")
    print(f"    Category: {instrument.category.value}")
    print(f"    Complexity: {instrument.implementation_complexity}")
    print(f"    Required Capacity: Analytical={instrument.required_analytical.value}, "
          f"Operational={instrument.required_operational.value}, "
          f"Political={instrument.required_political.value}")
```

### SGP Allocation Calculator

```python
from src.farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
    ColombianLegalFrameworkEngine,
    MunicipalCategory,
    SGPComponent
)

legal_engine = ColombianLegalFrameworkEngine()

# Calculate SGP allocations
municipality_category = MunicipalCategory.CATEGORY_5
total_sgp = 100_000_000  # COP 100 million

print(f"SGP Allocation for {municipality_category.value}:")
for component in SGPComponent:
    allocation = legal_engine.calculate_sgp_allocation(
        total_sgp=total_sgp,
        sgp_component=component,
        municipality_category=municipality_category
    )
    print(f"  {component.value}: COP {allocation:,.0f} ({allocation/total_sgp*100:.1f}%)")

# Get discretionary amount
discretionary = legal_engine.get_discretionary_sgp(
    total_sgp=total_sgp,
    municipality_category=municipality_category
)
print(f"\nDiscretionary (42% of General Purpose): COP {discretionary:,.0f}")
```

### Carver Principles Validation

```python
from src.farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
    CarverPrinciples
)

validator = CarverPrinciples()

# Test text samples
good_text = "La Secretaría de Desarrollo Social construirá tres aulas escolares en el mes de marzo."
bad_text = "Será construido mediante el fortalecimiento de la infraestructura educativa para garantizar el acceso."

print("Good Text:")
print(f"  Active Voice: {validator.check_active_voice(good_text)}")
print(f"  Concrete Nouns: {validator.check_concrete_nouns(good_text)}")
print(f"  Specific Verbs: {validator.check_specific_verbs(good_text)}")
print(f"  Sentence Length: {validator.check_sentence_length(good_text)}")

print("\nBad Text:")
print(f"  Active Voice: {validator.check_active_voice(bad_text)}")
print(f"  Concrete Nouns: {validator.check_concrete_nouns(bad_text)}")
print(f"  Specific Verbs: {validator.check_specific_verbs(bad_text)}")
```

## Output Structure

### PipelineResult

```python
result = transform_farfan_to_pdm(...)  # as above

# PipelineResult attributes:
result.municipality_id          # str
result.policy_area              # str
result.dimension                # str
result.steps                    # list[StepResult] - 8 steps
result.capacity_profile         # ComprehensiveCapacityProfile
result.value_chain              # ValueChainStructure
result.prose_recommendation     # ProseRecommendation
result.pdm_compliance           # PDMCompliance
result.success                  # bool
result.quality_score            # float (0-100)
result.total_duration_seconds   # float
result.farfan_questions         # list[str]
result.evidence_used            # list[str]
result.legal_frameworks         # list[str]
```

### ComprehensiveCapacityProfile

```python
capacity_profile = result.capacity_profile

# 9 capacity dimensions
capacity_profile.individual_analytical      # CapacityAssessment
capacity_profile.individual_operational     # CapacityAssessment
capacity_profile.individual_political       # CapacityAssessment
capacity_profile.organizational_analytical  # CapacityAssessment
capacity_profile.organizational_operational # CapacityAssessment
capacity_profile.organizational_political   # CapacityAssessment
capacity_profile.systemic_analytical        # CapacityAssessment
capacity_profile.systemic_operational       # CapacityAssessment
capacity_profile.systemic_political         # CapacityAssessment

# Overall assessment
capacity_profile.binding_constraints        # list[BindingConstraint]
capacity_profile.overall_capacity_level     # CapacityLevel (LOW/MEDIUM/HIGH)
capacity_profile.implementation_readiness   # str
capacity_profile.recommended_sequencing     # list[str]
```

### ValueChainStructure

```python
value_chain = result.value_chain

# Problem identification
value_chain.problem_tree          # ProblemTree

# Objectives
value_chain.objetivo_general      # ObjetivoGeneral
value_chain.objetivos_especificos # list[ObjetivoEspecifico]

# Products and activities
value_chain.productos             # list[Producto]
value_chain.actividades           # list[Actividad]

# Validation
value_chain.is_valid              # bool
value_chain.validation_report     # str
```

### ProseRecommendation

```python
prose = result.prose_recommendation

# Full text and metrics
prose.full_text                   # str (complete prose recommendation)
prose.word_count                  # int
prose.average_sentence_length     # float
prose.carver_compliance_score     # float (0-100)

# Sections
prose.sections                    # dict[str, str]
# Keys: diagnosis_context, intervention_description, timeline_specification,
#       budget_details, verification_mechanisms, sustainability_approach

# Quality details
prose.violations                  # list[str] (Carver principle violations)
```

## Best Practices

### 1. Always Provide Complete Capacity Evidence

```python
# ✓ GOOD: Complete evidence for all 9 dimensions
capacity_evidence = {
    CapacityDimension.INDIVIDUAL_ANALYTICAL: [...],
    CapacityDimension.INDIVIDUAL_OPERATIONAL: [...],
    # ... all 9 dimensions
}

# ✗ BAD: Incomplete evidence
capacity_evidence = {
    CapacityDimension.ORGANIZATIONAL_OPERATIONAL: [...]
    # Missing 8 dimensions - will default to LOW
}
```

### 2. Use Appropriate Municipal Category

```python
# Categories 1-3: Higher capacity, more own-source revenue
municipality_category = MunicipalCategory.CATEGORY_2

# Categories 4-6: Lower capacity, SGP-dependent
municipality_category = MunicipalCategory.CATEGORY_5
```

### 3. Validate Value Chain Before Narrative

```python
value_chain = build_value_chain_from_farfan(...)

if not value_chain.is_valid:
    print(f"Value Chain Issues: {value_chain.validation_report}")
    # Fix issues before generating narrative
```

### 4. Check Quality Score

```python
result = transform_farfan_to_pdm(...)

if result.quality_score < 70:
    print("Low quality score - review:")
    for step in result.steps:
        if step.warnings:
            print(f"Step {step.step_number} warnings: {step.warnings}")
```

## Integration with Existing Phase 8

The Comprehensive Guide integration coexists with the existing Phase 8 architecture:

```python
# Traditional approach (Dimensional Engine)
from src.farfan_pipeline.phases.Phase_08 import get_unified_bifurcator

engine = get_unified_bifurcator()
result = engine.generate_micro_recommendations(micro_scores)

# New approach (Comprehensive Guide)
from src.farfan_pipeline.phases.Phase_08 import transform_farfan_to_pdm

result = transform_farfan_to_pdm(...)
```

Both approaches can be used depending on requirements:
- **Dimensional Engine**: Fast, rule-based recommendations
- **Comprehensive Guide**: Full PDM methodology with capacity calibration

## Next Steps

1. **Integrate with Dimensional Engine**: Merge Comprehensive Guide outputs with dimensional recommendations
2. **Add AI Quality Evaluation**: Implement 7-criteria scoring from guide
3. **Create Quality Bands**: Implement Excelente → Crisis banding
4. **Full Traceability**: Link recommendations to specific FARFAN questions

## Support

For issues or questions:
- Review module docstrings
- Check Phase 8 README
- Examine test files in `tests/test_phase8_30_31_integration.py`
