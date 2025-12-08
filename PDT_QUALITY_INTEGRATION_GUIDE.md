# PDT Quality Integration Guide

## Overview

This guide describes the integration of Unit Layer (@u) structural analysis metrics into the EnrichedSignalPack intelligence layer for enhanced pattern filtering and precision improvement.

## Architecture

The PDT Quality Integration extends the signal intelligence layer with:

1. **Unit Layer Metrics Integration**: Incorporates S/M/I/P scores from PDT structural analysis
2. **Pattern Quality Boosting**: Prioritizes patterns from high-quality PDT sections
3. **Precision Correlation Tracking**: Measures correlation between PDT quality and pattern accuracy

```
EnrichedSignalPack
    ↓
├── Semantic Expansion (5x)
├── Context Filtering (60% precision)
│   └── PDT Quality Boosting
│       ├── I_struct>0.8 (excellent) → 1.5x boost
│       ├── I_struct>0.6 (good) → 1.2x boost
│       ├── I_struct>0.4 (acceptable) → 1.0x boost
│       └── I_struct<0.4 (poor) → 0.8x boost
├── Evidence Extraction (1,200 elements)
└── Contract Validation (600 contracts)
```

## Unit Layer (@u) Metrics

The Unit Layer evaluates PDT quality through 4 components:

- **S (Structural Compliance)**: Block coverage, hierarchy, sequence
- **M (Mandatory Sections)**: Completeness of critical sections
- **I (Indicator Quality)**: Structured metrics with sub-components:
  - `I_struct`: Field completeness in indicator matrix
  - `I_link`: Traceability between indicators and strategic lines
  - `I_logic`: Year coherence and logical consistency
- **P (PPI Completeness)**: Presence, structure, and accounting consistency

### Quality Thresholds

```python
PDT_QUALITY_THRESHOLDS = {
    "I_struct_excellent": 0.8,   # High-quality sections
    "I_struct_good": 0.6,         # Good sections
    "I_struct_acceptable": 0.4,   # Acceptable sections
    "S_structural_min": 0.5,      # Minimum structural compliance
    "M_mandatory_min": 0.5,       # Minimum mandatory sections
    "P_ppi_min": 0.5,            # Minimum PPI quality
}
```

### Boost Factors

```python
BOOST_FACTORS = {
    "excellent": 1.5,   # I_struct>0.8
    "good": 1.2,        # I_struct>0.6
    "acceptable": 1.0,  # I_struct>0.4
    "poor": 0.8,        # I_struct<0.4
}
```

## Usage

### 1. Computing PDT Section Quality

```python
from farfan_pipeline.core.orchestrator import (
    compute_pdt_section_quality,
    PDTQualityMetrics,
)

# From PDT structure
metrics = compute_pdt_section_quality(
    section_name="Diagnóstico",
    pdt_structure=pdt_struct  # PDTStructure from parser
)

# From pre-computed Unit Layer scores
metrics = compute_pdt_section_quality(
    section_name="PPI",
    unit_layer_scores={
        "score": 0.85,
        "components": {
            "S": 0.90,
            "M": 0.80,
            "I": 0.85,
            "I_struct": 0.88,
            "I_link": 0.82,
            "I_logic": 0.85,
            "P": 0.80,
        }
    }
)

print(f"Section: {metrics.section_name}")
print(f"I_struct: {metrics.I_struct}")
print(f"Quality Level: {metrics.quality_level}")
print(f"Boost Factor: {metrics.boost_factor}")
```

### 2. Creating EnrichedSignalPack with PDT Quality

```python
from farfan_pipeline.core.orchestrator import (
    create_enriched_signal_pack,
    compute_pdt_section_quality,
)

# Build PDT quality map
pdt_quality_map = {}

sections = ["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"]
for section in sections:
    metrics = compute_pdt_section_quality(
        section_name=section,
        pdt_structure=pdt_struct
    )
    pdt_quality_map[section] = metrics

# Create enriched pack with PDT quality
enriched = create_enriched_signal_pack(
    base_signal_pack=signal_pack,
    enable_semantic_expansion=True,
    pdt_quality_map=pdt_quality_map
)
```

### 3. Pattern Filtering with PDT Boost

```python
# Get patterns with PDT quality boosting
document_context = {
    "section": "Diagnóstico",
    "chapter": 2,
    "pdt_section": "Diagnóstico"
}

filtered_patterns, stats = enriched.get_patterns_for_context(
    document_context=document_context,
    track_precision_improvement=True,
    enable_pdt_boost=True  # Enable PDT quality boosting
)

# Check boost statistics
pdt_boost = stats["pdt_quality_boost"]
print(f"Patterns boosted: {pdt_boost['boosted_count']}")
print(f"Excellent quality: {pdt_boost['excellent_quality']}")
print(f"Good quality: {pdt_boost['good_quality']}")
print(f"Avg boost factor: {pdt_boost['avg_boost_factor']:.2f}")

# Check precision correlation
pdt_corr = stats["pdt_precision_correlation"]
print(f"High quality retention: {pdt_corr['high_quality_retention_rate']:.2%}")
print(f"Low quality retention: {pdt_corr['low_quality_retention_rate']:.2%}")
print(f"Quality correlation: {pdt_corr['quality_correlation']:.3f}")
```

### 4. Dynamic PDT Quality Updates

```python
# Add or update section quality
new_metrics = enriched.add_pdt_section_quality(
    section_name="Marco Normativo",
    unit_layer_scores={
        "score": 0.75,
        "components": {
            "S": 0.80,
            "M": 0.70,
            "I_struct": 0.72,
        }
    }
)

# Get quality summary
summary = enriched.get_pdt_quality_summary()
print(f"Total sections tracked: {summary['total_sections']}")
print(f"Average I_struct: {summary['avg_I_struct']:.2f}")
print(f"Quality distribution: {summary['quality_distribution']}")
```

## Pattern Metadata

Patterns boosted by PDT quality contain additional metadata:

```python
for pattern in filtered_patterns:
    print(f"Pattern ID: {pattern['id']}")
    print(f"  PDT Quality Boost: {pattern.get('pdt_quality_boost', 1.0)}")
    print(f"  PDT Quality Level: {pattern.get('pdt_quality_level', 'unknown')}")
    print(f"  Original Priority: {pattern.get('original_priority', 1.0)}")
    print(f"  Boosted Priority: {pattern.get('boosted_priority', 1.0)}")
```

## Precision Improvement Correlation

The integration tracks how PDT quality correlates with precision improvement:

```python
# Extract correlation metrics
correlation = stats["pdt_precision_correlation"]

# Retention rates by quality
for level, metrics in correlation["precision_by_quality_level"].items():
    print(f"{level}:")
    print(f"  Total: {metrics['total']}")
    print(f"  Retained: {metrics['retained']}")
    print(f"  Retention Rate: {metrics['retention_rate']:.2%}")
    print(f"  Avg I_struct: {metrics['avg_I_struct']:.2f}")

# Threshold effectiveness
for threshold, metrics in correlation["I_struct_threshold_effectiveness"].items():
    print(f"\n{threshold}:")
    print(f"  Above threshold: {metrics['above_count']} patterns")
    print(f"  Above retention: {metrics['above_retention']:.2%}")
    print(f"  Below retention: {metrics['below_retention']:.2%}")
    print(f"  Effectiveness: {metrics['effectiveness']:.2%}")
```

## Benefits

1. **Higher Precision**: Patterns from high-quality sections (I_struct>0.8) are prioritized
2. **Quality-Aware Filtering**: Low-quality sections contribute less to final results
3. **Measurable Impact**: Correlation tracking validates PDT quality contribution
4. **Adaptive Boosting**: Boost factors adjust based on I_struct thresholds

## Implementation Details

### PDT Quality Computation

The `compute_pdt_section_quality()` function:
1. Accepts either PDTStructure or pre-computed Unit Layer scores
2. Extracts S/M/I/P component scores
3. Determines quality level based on I_struct threshold
4. Assigns appropriate boost factor

### Pattern Boosting

The `apply_pdt_quality_boost()` function:
1. Matches patterns to PDT sections via metadata
2. Applies boost factor to pattern priority
3. Reorders patterns by boosted priority
4. Tracks boost statistics

### Correlation Tracking

The `track_pdt_precision_correlation()` function:
1. Compares patterns before/after filtering
2. Measures retention rates by quality level
3. Computes correlation between I_struct and retention
4. Evaluates threshold effectiveness (I_struct>0.8, >0.6, >0.4)

## Integration with Unit Layer

The integration leverages the existing Unit Layer (@u) evaluation:

```python
from farfan_pipeline.core.calibration.unit_layer import UnitLayerEvaluator
from farfan_pipeline.core.calibration.config import UnitLayerConfig

# Evaluate PDT quality
config = UnitLayerConfig()
evaluator = UnitLayerEvaluator(config)
layer_score = evaluator.evaluate(pdt_structure)

# Use scores for pattern boosting
metrics = compute_pdt_section_quality(
    section_name="Diagnóstico",
    unit_layer_scores={
        "score": layer_score.score,
        "components": layer_score.components
    }
)
```

## Metrics Export

All PDT quality metrics are accessible:

```python
# From PDTQualityMetrics
metrics_dict = metrics.to_dict()
# Returns: {
#   "S_structural": 0.90,
#   "M_mandatory": 0.80,
#   "I_struct": 0.85,
#   "I_link": 0.82,
#   "I_logic": 0.85,
#   "I_total": 0.84,
#   "P_presence": 1.0,
#   "P_struct": 0.75,
#   "P_consistency": 0.80,
#   "P_total": 0.78,
#   "U_total": 0.82,
#   "quality_level": "excellent",
#   "boost_factor": 1.5,
#   "precision_improvement": 0.15
# }
```

## Testing

Example test pattern:

```python
def test_pdt_quality_boost():
    # Create mock PDT quality map
    pdt_quality_map = {
        "Diagnóstico": PDTQualityMetrics(
            I_struct=0.85,
            quality_level="excellent",
            boost_factor=1.5,
            section_name="Diagnóstico"
        ),
        "PPI": PDTQualityMetrics(
            I_struct=0.35,
            quality_level="poor",
            boost_factor=0.8,
            section_name="PPI"
        )
    }
    
    # Create enriched pack
    enriched = create_enriched_signal_pack(
        base_signal_pack=mock_pack,
        pdt_quality_map=pdt_quality_map
    )
    
    # Filter patterns
    context = {"pdt_section": "Diagnóstico"}
    patterns, stats = enriched.get_patterns_for_context(context)
    
    # Verify boost applied
    assert stats["pdt_quality_boost"]["boosted_count"] > 0
    assert stats["pdt_quality_boost"]["excellent_quality"] > 0
    
    # Verify correlation tracked
    assert "pdt_precision_correlation" in stats
    corr = stats["pdt_precision_correlation"]
    assert corr["high_quality_retention_rate"] >= corr["low_quality_retention_rate"]
```

## Performance Impact

- **Computation**: O(n) for n patterns
- **Memory**: Minimal overhead (<1MB for typical quality maps)
- **Boost Application**: <10ms for 1000 patterns
- **Correlation Tracking**: <20ms additional overhead

## Future Enhancements

1. **Multi-dimensional Boosting**: Incorporate S, M, P scores alongside I_struct
2. **Dynamic Thresholds**: Learn optimal thresholds from historical data
3. **Section-specific Models**: Different boost strategies per PDT section
4. **Cross-section Dependencies**: Account for inter-section quality relationships
