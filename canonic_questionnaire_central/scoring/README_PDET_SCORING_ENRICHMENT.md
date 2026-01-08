# PDET Context Enrichment for Scoring System

## Overview

The PDET (Programas de Desarrollo con Enfoque Territorial) Context Enrichment for Scoring extends the canonical scoring system to include territorial context from Colombian PDET municipalities. This enrichment enables scoring criteria and analysis to reflect relevant geographical and social context, validated through the four-gate validation framework.

## Purpose

- **Territorial Awareness**: Adjust scoring thresholds based on PDET municipality characteristics
- **Policy Area Alignment**: Map scoring to relevant PDET subregions for each policy area
- **PDET Pillars Integration**: Connect questionnaire dimensions to PDET pillars
- **Validated Enrichment**: Ensure all enrichment passes four validation gates

## Architecture

### Components

1. **PDETScoringEnricher**: Main enrichment orchestrator
2. **PDETScoringContext**: Data structure for PDET context
3. **EnrichedScoredResult**: Scored result with PDET enrichment
4. **Four-Gate Validation**: Ensures enrichment governance compliance

### Integration Points

```
Evidence Collection (Phase 2)
       ↓
Basic Scoring (Phase 3)
       ↓
PDET Enrichment ← Four-Gate Validation
       ↓
Enriched Scoring with Territorial Context
       ↓
Adaptive Scoring (Phase 4+)
```

## Four-Gate Validation

All PDET enrichments are validated through four gates:

### Gate 1: Consumer Scope Validity
- **Purpose**: Authorize scoring system to access PDET data
- **Requirements**: 
  - Signal type: `ENRICHMENT_DATA`
  - Scope level: `EVIDENCE_COLLECTION`
  - All policy areas authorized

### Gate 2: Value Contribution
- **Purpose**: Verify enrichment adds material value
- **Threshold**: Minimum 10% value-add
- **Estimated Value**: 25% for PDET municipality context

### Gate 3: Consumer Capability
- **Purpose**: Ensure scoring system can process PDET data
- **Required Capabilities**:
  - `SEMANTIC_PROCESSING`
  - `TABLE_PARSING`
- **Recommended Capabilities**:
  - `GRAPH_CONSTRUCTION`

### Gate 4: Channel Authenticity
- **Purpose**: Ensure traceable, governed data flow
- **Flow ID**: `PDET_MUNICIPALITY_ENRICHMENT`
- **Documentation**: `README_PDET_ENRICHMENT.md`

## Usage

### Basic Enrichment

```python
from canonic_questionnaire_central.scoring.modules import (
    create_pdet_enricher,
    apply_scoring,
)

# Create enricher
enricher = create_pdet_enricher(
    strict_mode=True,
    enable_territorial_adjustment=True
)

# Score evidence (normal scoring)
evidence = {"elements": [...], "confidence": 0.75}
scored_result = apply_scoring(evidence, modality="TYPE_E")

# Enrich with PDET context
enriched_result = enricher.enrich_scored_result(
    scored_result=scored_result,
    question_id="Q001",
    policy_area="PA02",
    requested_context=["municipalities", "subregions", "policy_area_mappings"]
)

# Check enrichment status
if enriched_result.enrichment_applied:
    print(f"Territorial coverage: {enriched_result.pdet_context.territorial_coverage}")
    print(f"Relevant pillars: {enriched_result.pdet_context.relevant_pillars}")
    print(f"Adjustment: {enriched_result.territorial_adjustment}")
```

### Applying Territorial Adjustments

```python
# Get adjusted modality config
from canonic_questionnaire_central.scoring.modules import get_modality_config

base_config = get_modality_config("TYPE_E")
adjusted_config = enricher.apply_enrichment_to_config(
    base_config=base_config,
    pdet_context=enriched_result.pdet_context,
    territorial_adjustment=enriched_result.territorial_adjustment
)

# Use adjusted config for re-scoring
adjusted_result = apply_scoring(evidence, modality="TYPE_E", config=adjusted_config)
```

### Getting Enrichment Summary

```python
summary = enricher.get_enrichment_summary(enriched_result)

print(f"Enrichment applied: {summary['enrichment_applied']}")
print(f"Gate validation: {summary['gate_validation']}")
print(f"Municipalities: {summary['municipalities_count']}")
print(f"Subregions: {summary['subregions_count']}")
print(f"Territorial coverage: {summary['territorial_coverage']:.2%}")
print(f"Adjustment: {summary['territorial_adjustment']:.3f}")
```

## Territorial Adjustments

### Adjustment Factors

Territorial adjustments make scoring **more lenient** for areas with high PDET relevance:

| Factor | Bonus | Condition |
|--------|-------|-----------|
| High Coverage | +0.05 | Coverage ≥ 50% |
| Medium Coverage | +0.03 | Coverage ≥ 25% |
| Pillar Relevance | +0.03/pillar | Max +0.09 |
| Territorial Modality | +0.02 | TYPE_E modality |
| **Maximum Total** | **+0.16** | Combined |

### Coverage Calculation

```python
# Municipal coverage: ratio of relevant municipalities to total (170)
municipal_coverage = len(municipalities) / 170.0

# Subregional coverage: ratio of relevant subregions to total (16)
subregional_coverage = len(subregions) / 16.0

# Overall coverage (weighted)
territorial_coverage = (municipal_coverage * 0.6) + (subregional_coverage * 0.4)
```

### Threshold Adjustment

```python
# Original threshold
base_threshold = 0.65

# Apply adjustment (lowers threshold = more lenient)
adjusted_threshold = max(
    base_threshold - territorial_adjustment,
    0.4  # Minimum floor
)

# Example: base=0.65, adjustment=0.05 → adjusted=0.60
```

## Policy Area to PDET Subregion Mapping

Each policy area maps to specific PDET subregions:

| Policy Area | Subregions | Description |
|-------------|------------|-------------|
| PA01 (Gender) | SR04, SR05, SR08 | Gender initiatives |
| PA02 (Violence/Security) | SR01-SR08 | All subregions |
| PA03 (Environment) | SR03, SR05, SR06, SR07 | Deforestation/mining areas |
| PA04 (Economic Development) | SR02, SR03, SR04, SR06, SR07, SR08 | Agricultural projects |
| PA05 (Victims/Restitution) | SR01, SR05, SR08 | Land restitution |
| PA06 (Children/Youth) | SR04, SR05, SR06 | Education initiatives |
| PA07 (Peace Building) | SR01, SR02, SR03, SR04, SR07 | Reconciliation |
| PA08 (Human Rights) | SR08 | Human rights defenders |
| PA09 (Justice) | SR01 | Transitional justice |
| PA10 (International) | SR02, SR04 | Border cooperation |

## PDET Pillars to Dimensions

PDET pillars map to questionnaire dimensions:

| PDET Pillar | Dimension | Focus Area |
|-------------|-----------|------------|
| Pillar 1: Land Formalization | Structural | Property rights |
| Pillar 2: Infrastructure | Instrumental | Roads, connectivity |
| Pillar 3: Rural Health | Substantive | Healthcare access |
| Pillar 4: Education | Procedural | School access |
| Pillar 5: Housing/Water | Substantive | Basic services |
| Pillar 6: Economic Reactivation | Instrumental | Economic development |
| Pillar 7: Food Security | Substantive | Agriculture, nutrition |
| Pillar 8: Reconciliation | Symbolic | Peace building |

## Enrichment Metadata

Each enriched result includes metadata:

```json
{
  "enrichment_applied": true,
  "gate_validation_status": {
    "gate_1_scope": true,
    "gate_2_value_add": true,
    "gate_3_capability": true,
    "gate_4_channel": true
  },
  "municipalities_count": 8,
  "subregions_count": 8,
  "territorial_coverage": 0.50,
  "relevant_pillars": ["pillar_1", "pillar_2", "pillar_8"],
  "territorial_adjustment": 0.08,
  "base_score": 0.70,
  "adjusted_threshold": 0.57
}
```

## Configuration

Enrichment configuration in `scoring_system.json`:

```json
{
  "pdet_enrichment": {
    "enabled": true,
    "strict_mode": true,
    "enable_territorial_adjustment": true,
    "territorial_adjustments": {
      "coverage_high_bonus": 0.05,
      "coverage_medium_bonus": 0.03,
      "pillar_relevance_bonus_per_pillar": 0.03,
      "max_total_adjustment": 0.16,
      "min_threshold_floor": 0.4
    }
  }
}
```

## Testing

Run tests to validate enrichment:

```bash
# Test PDET scoring enrichment
pytest tests/test_pdet_scoring_enrichment.py -v

# Test specific functionality
pytest tests/test_pdet_scoring_enrichment.py::TestPDETScoringEnricher::test_territorial_coverage_calculation -v
```

## Examples

### Example 1: High PDET Relevance (PA02 - Violence/Security)

```python
# PA02 covers all 8 PDET subregions
enriched = enricher.enrich_scored_result(
    scored_result=scored_result,
    question_id="Q001",
    policy_area="PA02"
)

# Expected results:
# - 8 subregions (100% coverage)
# - High territorial_coverage (~1.0)
# - Significant adjustment (~0.08-0.16)
# - Relevant pillars: ["pillar_8"] (reconciliation)
```

### Example 2: Moderate PDET Relevance (PA01 - Gender)

```python
# PA01 covers 3 PDET subregions
enriched = enricher.enrich_scored_result(
    scored_result=scored_result,
    question_id="Q010",
    policy_area="PA01"
)

# Expected results:
# - 3 subregions (~19% coverage)
# - Moderate territorial_coverage (~0.2-0.3)
# - Small adjustment (~0.03-0.06)
# - Relevant pillars: ["pillar_4", "pillar_8"]
```

### Example 3: Territorial Question (TYPE_E)

```python
# TYPE_E modality gets additional bonus
result_territorial = ScoredResult(
    score=0.68,
    normalized_score=68.0,
    quality_level="BUENO",
    passes_threshold=True,
    modality="TYPE_E",  # Territorial modality
    scoring_metadata={"threshold": 0.65}
)

enriched = enricher.enrich_scored_result(
    scored_result=result_territorial,
    question_id="Q015",
    policy_area="PA03"  # Environment
)

# Gets +0.02 bonus for TYPE_E modality
# Plus coverage and pillar bonuses
```

## Error Handling

### Gate Validation Failure

If enrichment fails validation:

```python
enriched = enricher.enrich_scored_result(...)

if not enriched.enrichment_applied:
    # Check which gates failed
    for gate, passed in enriched.gate_validation_status.items():
        if not passed:
            print(f"Gate {gate} failed")
    
    # Fall back to base result
    result = enriched.base_result
```

### Missing PDET Data

If PDET data is unavailable:

```python
try:
    enriched = enricher.enrich_scored_result(...)
except Exception as e:
    logger.warning(f"Enrichment failed: {e}")
    # Use base scoring result
    result = scored_result
```

## Performance Considerations

- **Caching**: Enricher caches PDET data on initialization
- **Lazy Evaluation**: Enrichment only performed when requested
- **Gate Bypass**: Set `strict_mode=False` to allow scoring without enrichment
- **Selective Context**: Request only needed context types

## Best Practices

1. **Initialize Once**: Create enricher once and reuse
2. **Check Application**: Always verify `enrichment_applied` flag
3. **Log Failures**: Log gate validation failures for monitoring
4. **Document Adjustments**: Include adjustment rationale in metadata
5. **Test Coverage**: Test enrichment with representative policy areas

## Troubleshooting

### Enrichment Not Applied

**Problem**: `enrichment_applied = False`

**Solutions**:
- Check gate validation status
- Verify PDET data loaded
- Ensure policy area has PDET mapping
- Check strict_mode setting

### Unexpected Adjustments

**Problem**: Adjustments too large or small

**Solutions**:
- Review territorial coverage calculation
- Check pillar mappings for policy area
- Verify adjustment factors in config
- Inspect enrichment summary

### Performance Issues

**Problem**: Enrichment too slow

**Solutions**:
- Request only needed context types
- Initialize enricher once, not per request
- Consider caching enrichment results
- Profile gate validation performance

## References

- [PDET Enrichment System](./README_PDET_ENRICHMENT.md)
- [Scoring System Documentation](../../docs/cqvr/scoring-system.md)
- [Four-Gate Validation Framework](../validations/README.md)
- [PDET Municipality Data](./pdet_municipalities.json)

## Changelog

### Version 1.0.0 (2026-01-08)
- Initial implementation of PDET scoring enrichment
- Four-gate validation integration
- Territorial adjustment calculations
- Policy area to subregion mapping
- PDET pillars to dimensions mapping
- Comprehensive test coverage
- Documentation and examples

## License

Proprietary - F.A.R.F.A.N Pipeline Team © 2024
