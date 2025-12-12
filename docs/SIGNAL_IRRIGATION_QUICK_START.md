# Signal Irrigation Enhancements - Quick Start Guide

**Quick reference for using signal-enriched modules in Phases 3-9**

---

## Import Statements

```python
# Phase 3: Scoring
from canonic_phases.Phase_three.signal_enriched_scoring import (
    SignalEnrichedScorer,
    get_signal_adjusted_threshold,
    get_signal_quality_validation,
)

# Phase 4-7: Aggregation
from canonic_phases.Phase_four_five_six_seven.signal_enriched_aggregation import (
    SignalEnrichedAggregator,
    adjust_weights,
    interpret_dispersion,
)

# Phase 8: Recommendations
from canonic_phases.Phase_eight.signal_enriched_recommendations import (
    SignalEnrichedRecommender,
    enhance_rule_matching,
    prioritize_interventions,
)

# Phase 9: Reporting
from canonic_phases.Phase_nine.signal_enriched_reporting import (
    SignalEnrichedReporter,
    enrich_narrative,
    select_report_sections,
)
```

---

## Phase 3: Quick Examples

### Adjust Threshold
```python
scorer = SignalEnrichedScorer(signal_registry=registry)
adjusted, details = scorer.adjust_threshold_for_question(
    question_id="Q001",
    base_threshold=0.65,
    score=0.5,
    metadata={"completeness": "complete"},
)
```

### Validate Quality
```python
validated, details = scorer.validate_quality_level(
    question_id="Q001",
    quality_level="INSUFICIENTE",
    score=0.85,
    completeness="complete",
)
# validated may be "ACEPTABLE" (promoted)
```

---

## Phase 4-7: Quick Examples

### Adjust Weights
```python
aggregator = SignalEnrichedAggregator(signal_registry=registry)
adjusted, details = aggregator.adjust_aggregation_weights(
    base_weights={"Q1": 0.2, "Q2": 0.2, "Q3": 0.2, "Q4": 0.2, "Q5": 0.2},
    score_data={"Q1": 0.3, "Q2": 0.25, "Q3": 0.8, "Q4": 0.7, "Q5": 0.6},
)
# Critical scores get weight boost
```

### Analyze Dispersion
```python
metrics, interpretation = aggregator.analyze_score_dispersion(
    scores=[0.75, 0.78, 0.76, 0.77, 0.79],
    context="dimension_DIM01",
)
# metrics["cv"] < 0.15 → convergence
# interpretation provides recommendations
```

---

## Phase 8: Quick Examples

### Enhance Rule
```python
recommender = SignalEnrichedRecommender(signal_registry=registry)
met, details = recommender.enhance_rule_condition(
    rule_id="RULE001",
    condition={"field": "score", "operator": "lt", "value": 0.5},
    score_data={"score": 0.3, "question_global": 1},
)
# met == True, details has enhancement info
```

### Compute Priority
```python
priority, details = recommender.compute_intervention_priority(
    recommendation={"rule_id": "RULE001"},
    score_data={"score": 0.25, "quality_level": "INSUFICIENTE"},
)
# priority > 0.7 for critical issues
```

---

## Phase 9: Quick Examples

### Enrich Narrative
```python
reporter = SignalEnrichedReporter(signal_registry=registry)
enriched, details = reporter.enrich_narrative_context(
    question_id="Q001",
    base_narrative="The baseline analysis is incomplete.",
    score_data={"score": 0.3, "quality_level": "INSUFICIENTE"},
)
# enriched has additional context from signals
```

### Determine Emphasis
```python
emphasis, details = reporter.determine_section_emphasis(
    section_id="SEC01",
    section_data={"scores": [0.2, 0.3, 0.25, 0.28]},
    policy_area="PA01",
)
# emphasis > 0.7 → high detail level
```

---

## Convenience Functions

### One-liners for Common Operations

```python
# Phase 3: Adjust threshold without class instance
from canonic_phases.Phase_three.signal_enriched_scoring import get_signal_adjusted_threshold
adjusted, details = get_signal_adjusted_threshold(registry, "Q001", 0.65, 0.5, {})

# Phase 4-7: Adjust weights without class instance
from canonic_phases.Phase_four_five_six_seven.signal_enriched_aggregation import adjust_weights
adjusted, details = adjust_weights(registry, base_weights, score_data)

# Phase 8: Prioritize recommendations
from canonic_phases.Phase_eight.signal_enriched_recommendations import prioritize_interventions
prioritized = prioritize_interventions(registry, recommendations, score_data)

# Phase 9: Enrich narrative
from canonic_phases.Phase_nine.signal_enriched_reporting import enrich_narrative
enriched, details = enrich_narrative(registry, "Q001", base_narrative, score_data)
```

---

## Feature Flags

Enable/disable specific features:

```python
# Phase 3
scorer = SignalEnrichedScorer(
    signal_registry=registry,
    enable_threshold_adjustment=True,   # Default: True
    enable_quality_validation=True,     # Default: True
)

# Phase 4-7
aggregator = SignalEnrichedAggregator(
    signal_registry=registry,
    enable_weight_adjustment=True,      # Default: True
    enable_dispersion_analysis=True,    # Default: True
)

# Phase 8
recommender = SignalEnrichedRecommender(
    signal_registry=registry,
    enable_pattern_matching=True,       # Default: True
    enable_priority_scoring=True,       # Default: True
)

# Phase 9
reporter = SignalEnrichedReporter(
    signal_registry=registry,
    enable_narrative_enrichment=True,   # Default: True
    enable_section_selection=True,      # Default: True
    enable_evidence_highlighting=True,  # Default: True
)
```

---

## Common Patterns

### Pattern 1: Graceful Degradation
```python
# Works without signal registry
scorer = SignalEnrichedScorer(signal_registry=None)
adjusted, details = scorer.adjust_threshold_for_question(...)
# Returns base_threshold unchanged with details["adjustment"] == "none"
```

### Pattern 2: Provenance Tracking
```python
# All enhancements add signal_enrichment metadata
enriched_details = {
    **base_details,
    "signal_enrichment": {
        "enabled": True,
        "registry_available": True,
        "threshold_adjustment": {...},
        "quality_validation": {...},
    }
}
```

### Pattern 3: Error Handling
```python
try:
    adjusted, details = scorer.adjust_threshold_for_question(...)
except Exception as e:
    # All methods catch exceptions and return base values
    # Check details["error"] for error message
    logger.warning(f"Signal enrichment failed: {e}")
    adjusted = base_threshold  # Fallback
```

---

## Testing

```bash
# Run all signal irrigation tests
pytest tests/test_signal_irrigation_enhancements.py -v

# Run specific phase
pytest tests/test_signal_irrigation_enhancements.py::TestPhase3SignalEnrichment -v

# Run integration tests
pytest tests/test_signal_irrigation_enhancements.py::TestSignalIrrigationIntegration -v
```

---

## Key Metrics

| Enhancement | Metric | Threshold |
|-------------|--------|-----------|
| **Threshold Adjustment** | Pattern count | >15 → -0.05 adjustment |
| **Weight Adjustment** | Score criticality | <0.4 → 1.2× boost |
| **Dispersion Analysis** | Coefficient of Variation | <0.15 → convergence |
| **Priority Scoring** | Score severity | <0.3 → +0.3 priority |
| **Section Emphasis** | Variance | >0.15 → +0.3 emphasis |

---

## Troubleshooting

### Issue: Enhancements not applied
**Check**: Signal registry availability
```python
if scorer.signal_registry is None:
    logger.warning("Signal registry not available")
```

### Issue: Unexpected results
**Check**: Feature flags
```python
if not scorer.enable_threshold_adjustment:
    logger.info("Threshold adjustment disabled")
```

### Issue: Import errors
**Check**: Python path setup
```python
import sys
sys.path.insert(0, "src")  # Add src to path
```

---

## Quick Reference: Return Values

All enhancement methods return tuples of `(result, details)`:

```python
# Phase 3
(adjusted_threshold: float, adjustment_details: dict)
(validated_quality: str, validation_details: dict)

# Phase 4-7
(adjusted_weights: dict, adjustment_details: dict)
(metrics: dict, interpretation: dict)
(method_name: str, selection_details: dict)

# Phase 8
(condition_met: bool, evaluation_details: dict)
(priority_score: float, priority_details: dict)
(template_id: str, selection_details: dict)

# Phase 9
(enriched_narrative: str, enrichment_details: dict)
(emphasis_score: float, emphasis_details: dict)
(highlighted_evidence: list, highlighting_details: dict)
```

---

## More Information

- Full Documentation: `docs/SIGNAL_IRRIGATION_ENHANCEMENTS.md`
- Test Suite: `tests/test_signal_irrigation_enhancements.py`
- SISAS Documentation: `docs/SISAS_STRATEGIC_ENHANCEMENTS.md`
- Phase 1 Signals: `docs/PHASE_1_SIGNAL_ENRICHMENT.md`

---

**Last Updated:** 2025-12-11  
**Version:** 1.0.0
