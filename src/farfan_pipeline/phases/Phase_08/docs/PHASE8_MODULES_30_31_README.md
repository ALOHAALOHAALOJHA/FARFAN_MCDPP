# Phase 8 Modules 30-31: Legal Framework & Narrative Generation

## Overview

Two essential modules for Phase 8 recommendations enhancement, implementing Colombian legal compliance validation and clear narrative generation following Carver principles.

## Module 30: Colombian Legal Framework (`phase8_30_00_colombian_legal_framework.py`)

### Purpose
Comprehensive Colombian legal framework engine for PDM (Plan de Desarrollo Municipal) formulation and compliance validation.

### Key Features

#### 1. Municipal Categorization
- 7 categories (Special, 1-6) based on Law 617/2000 and Law 1551/2012
- Population and income thresholds (SMMLV)
- Determines planning requirements and competencies

```python
from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
    ColombianLegalFrameworkEngine,
    MunicipalCategory
)

engine = ColombianLegalFrameworkEngine()
category = engine.get_municipality_category(population=45_000, income_smmlv=35_000)
# Returns: MunicipalCategory.CATEGORY_3
```

#### 2. SGP Allocation Calculator
- Sistema General de Participaciones (Law 715/2001)
- 4 components: Education (58.5%), Health (24.5%), General Purpose (11.6%), Water (5.4%)
- Discretionary percentages for categories 4-6

```python
sgp = engine.get_sgp_allocation(MunicipalCategory.CATEGORY_4, SGPComponent.GENERAL_PURPOSE)
# Returns: {
#     'total_percentage': 0.116,
#     'discretionary_percentage': 0.04872,  # 42% of 11.6%
#     'earmarked_percentage': 0.06728,
#     'receives_sector': True
# }
```

#### 3. Legal Framework Mapping
Maps all 10 FARFAN policy areas to Colombian laws:
- **PA01 (Gender Equality)** → Ley 1257/2008
- **PA02 (Victims' Rights)** → Ley 1448/2011
- **PA03 (Environment)** → Ley 99/1993, Ley 388/1997 (POT)
- **PA04 (Children/Youth)** → Ley 1098/2006 Art. 204
- **PA05 (Human Rights Defenders)** → Decree 1066/2015
- **PA06 (Economic Development)** → Ley 1551/2012 (municipal competence)
- **PA07 (Infrastructure/Mobility)** → Ley 1551/2012 + POT
- **PA08 (Education)** → Ley 715/2001
- **PA09 (Health)** → Ley 715/2001
- **PA10 (Institutional Capacity)** → Ley 1474/2011, Ley 1712/2014

```python
frameworks = engine.get_legal_obligations("PA01")
# Returns list of LegalFramework objects with:
# - law_number, law_year, description
# - applicable_municipalities
# - mandatory_pdm_section
# - verification_entity
```

#### 4. PDM Compliance Validation
Validates recommendations against legal, financing, and timeline requirements:

```python
compliance = engine.validate_pdm_compliance(
    recommendation_id="PA01-DIM01-CRISIS",
    policy_area="PA01",
    municipality_category=MunicipalCategory.CATEGORY_3,
    required_financing_sources=[FinancingSource.RECURSOS_PROPIOS],
    formulation_phase=PDMFormulationPhase.INVESTMENT_PLAN,
)

print(compliance.compliance_level)  # "FULL", "PARTIAL", or "NON_COMPLIANT"
print(compliance.overall_compliance_score)  # 0-1
print(compliance.recommendations_for_compliance)  # List of action items
```

#### 5. Financing Source Identification
Identifies available financing sources by instrument type, municipality category, and policy area:

```python
sources = engine.get_financing_sources(
    instrument_type="INFRASTRUCTURE",
    municipality_category=MunicipalCategory.CATEGORY_4,
    policy_area="PA07",
)
# Returns: [SGP_GENERAL_PURPOSE, RECURSOS_PROPIOS, CREDITO, REGALIAS, ...]
```

#### 6. PDM Formulation Timeline
Month-by-month requirements (January-May):
- **January-February**: Diagnostic (DIAGNOSTIC)
- **March**: Strategic Part (STRATEGIC_PART)
- **April**: Investment Plan (INVESTMENT_PLAN)
- **April-May**: CTP Approval (CTP_APPROVAL)
- **May**: Council Approval (COUNCIL_APPROVAL)

### Data Structures

#### `MunicipalCategory` (Enum)
```python
SPECIAL, CATEGORY_1, CATEGORY_2, CATEGORY_3, CATEGORY_4, CATEGORY_5, CATEGORY_6
```

#### `SGPComponent` (Enum)
```python
EDUCATION, HEALTH, GENERAL_PURPOSE, WATER_SANITATION
```

#### `FinancingSource` (Enum)
```python
SGP_EDUCATION, SGP_HEALTH, SGP_GENERAL_PURPOSE, SGP_WATER,
RECURSOS_PROPIOS, REGALIAS, CREDITO,
COFINANCIACION_NACIONAL, COFINANCIACION_DEPARTAMENTAL,
COOPERACION_INTERNACIONAL
```

#### `LegalFramework` (Dataclass)
- law_number, law_year, description
- applicable_municipalities
- mandatory_pdm_section
- verification_entity
- budget_earmark (optional)
- coordination_required

#### `ComplianceReport` (Dataclass)
- legal compliance (is_legally_compliant, legal_gaps)
- financing viability (financing_viability, financing_gaps)
- timeline feasibility (is_timeline_feasible, timeline_risks)
- overall_compliance_score (0-1)
- recommendations_for_compliance

---

## Module 31: Narrative Generation (`phase8_31_00_narrative_generation.py`)

### Purpose
Generate clear, actionable prose recommendations using Carver principles for lenguaje claro (plain language).

### Key Features

#### 1. Carver Principles Validator
Five core principles for clear writing:

1. **Active Voice** - "La alcaldía construirá" NOT "Será construido por"
2. **Short Sentences** - Maximum 25 words per sentence
3. **Concrete Nouns** - "10 aulas" NOT "infraestructura educativa"
4. **Specific Verbs** - "construir", "capacitar" NOT "fortalecer", "garantizar"
5. **Familiar Vocabulary** - Avoid unnecessary jargon

```python
from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import CarverPrinciples

bad_text = (
    "Se fortalecerá la gobernanza mediante la implementación de una estrategia "
    "holística que será ejecutada por la alcaldía."
)

score, violations = CarverPrinciples.validate_all(bad_text)
print(f"Score: {score}/100")  # Lower score due to violations
print(f"Violations: {len(violations)}")

for v in violations:
    print(f"  - {v.principle}: {v.explanation}")
    print(f"    Fix: {v.suggested_fix}")
```

#### 2. Narrative Template
Six mandatory sections for PDM recommendations:

1. **Diagnosis Context** - FARFAN findings justifying intervention
2. **Intervention Description** - Instruments, activities, products
3. **Timeline Specification** - Month-by-month implementation
4. **Budget Details** - Sources, amounts, responsible entities
5. **Verification Mechanisms** - Indicators, frequency, reporting
6. **Sustainability Approach** - Long-term maintenance, institutionalization

#### 3. Prose Recommendation Generation

```python
from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import NarrativeGenerator
from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import ColombianLegalFrameworkEngine

legal_engine = ColombianLegalFrameworkEngine()
generator = NarrativeGenerator(legal_engine=legal_engine)

# Generate prose recommendation from structured inputs
prose_rec = generator.generate_prose_recommendation(
    value_chain=value_chain_structure,
    instruments=instrument_mix,
    capacity_profile=capacity_profile,
)

print(prose_rec.full_text)  # Complete narrative
print(f"Word count: {prose_rec.word_count}")
print(f"Carver score: {prose_rec.carver_compliance_score}/100")
```

#### 4. Bullet-to-Prose Conversion

```python
from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import convert_bullets_to_prose

bullets = [
    "Falta de infraestructura educativa en zona rural",
    "Docentes sin capacitación en pedagogía actualizada",
    "Ausencia de material didáctico",
]

prose = convert_bullets_to_prose(bullets)
print(prose)
# "Se identificó falta de infraestructura educativa en zona rural, 
#  docentes sin capacitación en pedagogía actualizada, y ausencia de material didáctico."
```

#### 5. Responsible Entity Specification

```python
# Specify responsible entities by activity and municipality size
responsible = generator.specify_responsible_entities(
    activity="budget",
    municipality_category=MunicipalCategory.SPECIAL
)
print(responsible)  # "la Secretaría de Hacienda Municipal"

responsible = generator.specify_responsible_entities(
    activity="budget",
    municipality_category=MunicipalCategory.CATEGORY_6
)
print(responsible)  # "la Tesorería Municipal"
```

### Data Structures

#### `CarverViolation` (Dataclass)
- principle (e.g., "ACTIVE_VOICE", "SENTENCE_LENGTH")
- line_number
- sentence
- explanation
- suggested_fix
- severity ("HIGH", "MEDIUM", "LOW")

#### `NarrativeTemplate` (Dataclass)
- diagnosis_context
- intervention_description
- timeline_specification
- budget_details
- verification_mechanisms
- sustainability_approach

#### `ProseRecommendation` (Dataclass)
- recommendation_id
- policy_area, dimension
- municipality_category
- full_text (complete prose)
- sections (dict of section texts)
- word_count, sentence_count, average_sentence_length
- carver_compliance_score (0-100)
- carver_violations (list of issues)
- value_chain_id
- legal_frameworks_cited

---

## Integration with Phase 8 Pipeline

### Phase 8 Module Dependencies

```
phase8_27 (Policy Capacity Framework)
    ↓
phase8_28 (Howlett Instruments)
    ↓
phase8_29 (Value Chain Integration)
    ↓
phase8_30 (Colombian Legal Framework) ← NEW
    ↓
phase8_31 (Narrative Generation) ← NEW
```

### Complete Workflow Example

```python
from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
    ColombianLegalFrameworkEngine,
    MunicipalCategory,
    FinancingSource,
    PDMFormulationPhase
)
from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
    NarrativeGenerator,
    CarverPrinciples
)

# Step 1: Determine municipality category
legal_engine = ColombianLegalFrameworkEngine()
category = legal_engine.get_municipality_category(
    population=35_000,
    income_smmlv=28_000
)

# Step 2: Get legal obligations for policy area
frameworks = legal_engine.get_legal_obligations("PA01")
print(f"Must comply with: {frameworks[0].law_number}/{frameworks[0].law_year}")

# Step 3: Identify financing sources
sources = legal_engine.get_financing_sources(
    instrument_type="SERVICE_DELIVERY",
    municipality_category=category,
    policy_area="PA01"
)

# Step 4: Validate compliance
compliance = legal_engine.validate_pdm_compliance(
    recommendation_id="PA01-DIM01-CRISIS",
    policy_area="PA01",
    municipality_category=category,
    required_financing_sources=sources,
    formulation_phase=PDMFormulationPhase.INVESTMENT_PLAN
)

if compliance.compliance_level != "FULL":
    print(f"Compliance gaps: {compliance.legal_gaps}")
    print(f"Actions needed: {compliance.recommendations_for_compliance}")

# Step 5: Generate narrative
narrative_gen = NarrativeGenerator(legal_engine=legal_engine)

# Would use actual value chain, instruments, capacity profile in production
# prose_rec = narrative_gen.generate_prose_recommendation(
#     value_chain=value_chain,
#     instruments=instruments,
#     capacity_profile=capacity_profile
# )

# Step 6: Validate Carver principles
# score, violations = CarverPrinciples.validate_all(prose_rec.full_text)
# if score < 80:
#     print("Needs revision - Carver violations found")
```

---

## Production Usage

### Best Practices

1. **Legal Compliance First**
   - Always validate legal compliance before generating narrative
   - Ensure municipality category is correctly determined
   - Check financing source availability

2. **Narrative Quality Control**
   - Aim for Carver score >80 for production recommendations
   - Review HIGH severity violations manually
   - Test narrative flow with actual PDM reviewers

3. **Responsible Entity Specification**
   - Use category-specific entity names
   - Verify against municipal organizational structure
   - Consider capacity constraints

4. **Integration Points**
   - Legal framework informs value chain construction
   - Compliance gaps feed back to instrument selection
   - Narrative quality affects PDM approval probability

### Testing

Both modules include comprehensive unit tests:

```bash
cd /home/runner/work/FARFAN_MCDPP/FARFAN_MCDPP/src/farfan_pipeline/phases/Phase_08
python3 tests/test_phase8_30_31_integration.py
```

### Performance

- **Legal Framework Engine**: O(1) lookup for most operations
- **Narrative Generator**: O(n) where n = sentence count
- **Carver Validation**: O(n*m) where n = sentences, m = principles

---

## Maintenance

### Updating Legal Frameworks

When Colombian laws change:

1. Update `POLICY_AREA_LEGAL_FRAMEWORKS` dict in phase8_30
2. Add new `LegalFramework` entries
3. Update verification entities if changed
4. Run integration tests

### Updating Carver Principles

To refine validation rules:

1. Modify pattern lists in `CarverPrinciples` class
2. Adjust scoring weights in `validate_all()` method
3. Test with representative sample texts
4. Document changes in severity classifications

---

## Version History

- **v1.0.0** (2026-01-26): Initial release
  - Colombian legal framework engine
  - Carver principles validator
  - Narrative generation system
  - Full Phase 8 integration

---

## Authors

F.A.R.F.A.N Architecture Team

---

## License

Part of the FARFAN_MCDPP public policy evaluation pipeline.
