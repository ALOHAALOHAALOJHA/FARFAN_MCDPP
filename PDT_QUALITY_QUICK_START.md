# PDT Quality Integration - Quick Start

## 30-Second Overview

Boost signal pattern precision by prioritizing patterns from high-quality PDT sections using Unit Layer (@u) metrics.

## Installation

No installation needed - already integrated into `farfan_pipeline.core.orchestrator`.

## Basic Usage

```python
from farfan_pipeline.core.orchestrator import (
    create_enriched_signal_pack,
    compute_pdt_section_quality,
)

# 1. Compute section quality
metrics = compute_pdt_section_quality(
    section_name="Diagnóstico",
    unit_layer_scores={
        "score": 0.85,
        "components": {"I_struct": 0.88}
    }
)

# 2. Build quality map
pdt_quality_map = {"Diagnóstico": metrics}

# 3. Create enriched pack
enriched = create_enriched_signal_pack(
    base_signal_pack=signal_pack,
    pdt_quality_map=pdt_quality_map
)

# 4. Get boosted patterns
patterns, stats = enriched.get_patterns_for_context(
    {"pdt_section": "Diagnóstico"},
    enable_pdt_boost=True
)

# 5. Check results
print(f"Boosted: {stats['pdt_quality_boost']['boosted_count']}")
print(f"Avg boost: {stats['pdt_quality_boost']['avg_boost_factor']:.2f}x")
```

## Quality Levels & Boost Factors

| I_struct Range | Quality Level | Boost Factor |
|----------------|---------------|--------------|
| ≥ 0.8          | Excellent     | 1.5x         |
| 0.6 - 0.8      | Good          | 1.2x         |
| 0.4 - 0.6      | Acceptable    | 1.0x         |
| < 0.4          | Poor          | 0.8x         |

## Key Metrics

### Unit Layer (@u) Components
- **S**: Structural compliance
- **M**: Mandatory sections
- **I**: Indicator quality (I_struct, I_link, I_logic)
- **P**: PPI completeness

### Boost Statistics
```python
stats["pdt_quality_boost"] = {
    "total_patterns": 100,
    "boosted_count": 80,
    "excellent_quality": 25,
    "avg_boost_factor": 1.2
}
```

### Correlation Metrics
```python
stats["pdt_precision_correlation"] = {
    "high_quality_retention_rate": 0.85,
    "low_quality_retention_rate": 0.50,
    "quality_correlation": 0.35
}
```

## Common Patterns

### Pattern 1: Multiple Sections
```python
sections = ["Diagnóstico", "Parte Estratégica", "PPI"]
pdt_quality_map = {
    section: compute_pdt_section_quality(section, unit_layer_scores=scores)
    for section, scores in section_scores.items()
}
```

### Pattern 2: Dynamic Updates
```python
enriched.add_pdt_section_quality(
    "New Section",
    unit_layer_scores={"score": 0.75, "components": {"I_struct": 0.72}}
)
```

### Pattern 3: Quality Summary
```python
summary = enriched.get_pdt_quality_summary()
print(f"Sections: {summary['total_sections']}")
print(f"Avg I_struct: {summary['avg_I_struct']:.2f}")
```

## When to Use

✅ Use PDT quality boosting when:
- Analyzing patterns from PDT documents
- Quality varies significantly across sections
- Need to prioritize high-quality sources
- Want measurable quality-precision correlation

❌ Skip PDT boosting when:
- Not analyzing PDT documents
- All sections have similar quality
- Quality data unavailable

## Run Examples

```bash
python examples/pdt_quality_integration_example.py
```

## Run Tests

```bash
pytest tests/core/test_pdt_quality_integration.py -v
```

## More Information

- **Full Guide**: `PDT_QUALITY_INTEGRATION_GUIDE.md`
- **Implementation**: `PDT_QUALITY_INTEGRATION_SUMMARY.md`
- **Code**: `src/farfan_pipeline/core/orchestrator/pdt_quality_integration.py`
