# Phase 8 Primitives

**Document ID:** PHASE-8-PRIMITIVES  
**Version:** 1.0.0  
**Date:** 2026-01-05  
**Status:** ACTIVE  
**Classification:** CANONICAL

---

## Overview

This directory contains all primitive types, constants, and foundational definitions for Phase 8 - Recommendation Engine. Following GNEA standards, all primitives are centralized here to prevent duplication and ensure consistency.

## Contents

| File | Purpose | Description |
|------|---------|-------------|
| `PHASE_8_CONSTANTS.py` | Global Constants | All immutable constants for Phase 8 |
| `PHASE_8_TYPES.py` | Type Definitions | TypedDicts, NewTypes, and type aliases |
| `PHASE_8_ENUMS.py` | Enumerations | Enum types for type-safe values |
| `__init__.py` | Package Init | Exports all primitives |

## Usage

### Importing Constants

```python
from farfan_pipeline.phases.Phase_eight.primitives import (
    PHASE_NUMBER,
    PHASE_NAME,
    MIN_CONFIDENCE_THRESHOLD,
    MICRO_SCORE_THRESHOLD_DEFAULT,
    VALID_LEVELS,
)

# Use constants
if score < MICRO_SCORE_THRESHOLD_DEFAULT:
    generate_recommendation()
```

### Importing Types

```python
from farfan_pipeline.phases.Phase_eight.primitives import (
    AnalysisResultsInput,
    PolicyContextInput,
    RecommendationOutput,
    MicroScoreKey,
)

def process_analysis(
    results: AnalysisResultsInput,
    context: PolicyContextInput,
) -> list[RecommendationOutput]:
    ...
```

### Importing Enums

```python
from farfan_pipeline.phases.Phase_eight.primitives import (
    Level,
    ScoreBand,
    VarianceLevel,
)

# Use enums
level = Level.MICRO
band = ScoreBand.from_score(score=45.0)
variance = VarianceLevel.from_variance(0.15)
```

## Constant Categories

### Phase Identification
- `PHASE_NUMBER`: 8
- `PHASE_NAME`: "Phase 8: Recommendation Engine"
- `PHASE_CODENAME`: "RECOMMENDER"

### Stage Definitions
- `STAGE_BASE`: 0 - Package init
- `STAGE_INIT`: 10 - Initialization
- `STAGE_ENGINE`: 20 - Core engine
- `STAGE_ENRICHMENT`: 30 - Signal enrichment

### Score Thresholds
- `MICRO_SCORE_THRESHOLD_DEFAULT`: 1.65
- `MESO_SCORE_BAND_LOW`: 55.0
- `MESO_SCORE_BAND_HIGH`: 75.0
- `VARIANCE_LOW_THRESHOLD`: 0.08
- `VARIANCE_HIGH_THRESHOLD`: 0.18

### Recommendation Settings
- `MAX_RECOMMENDATIONS_PER_AREA`: 10
- `MIN_CONFIDENCE_THRESHOLD`: 0.6
- `SIGNAL_WEIGHT_DEFAULT`: 1.0

## Type Definitions

### Input Types
- `AnalysisResultsInput`: P8-IN-001 contract
- `PolicyContextInput`: P8-IN-002 contract
- `SignalDataInput`: P8-IN-003 contract (optional)

### Score Key Types
- `MicroScoreKey`: "PA##-DIM##" format
- `ClusterKey`: "CL##" format
- `QuestionId`: "Q###" format

### Output Types
- `RecommendationOutput`: Single recommendation
- `RecommendationSetOutput`: Set with metadata
- `RecommendationMetadata`: P8-OUT-002 contract

## Enum Types

### Level
```python
Level.MICRO  # Question-level
Level.MESO   # Cluster-level  
Level.MACRO  # Plan-level
```

### ScoreBand
```python
ScoreBand.BAJO          # < 55
ScoreBand.MEDIO         # 55-75
ScoreBand.ALTO          # >= 75
ScoreBand.SATISFACTORIO # >= 65
ScoreBand.INSUFICIENTE  # < 50
```

### VarianceLevel
```python
VarianceLevel.BAJA   # < 0.08
VarianceLevel.MEDIA  # 0.08-0.18
VarianceLevel.ALTA   # >= 0.18
```

## Best Practices

1. **Always import from `primitives`** - Don't define local constants
2. **Use typed dicts** - For all structured data
3. **Use enums** - For fixed value sets
4. **Use NewType** - For semantic type aliases

## See Also

- [PHASE_8_MANIFEST.json](../PHASE_8_MANIFEST.json) - Phase manifest
- [interfaces/](../interfaces/) - Interface contracts
- [GLOBAL_NAMING_POLICY.md](/GLOBAL_NAMING_POLICY.md) - GNEA standards
