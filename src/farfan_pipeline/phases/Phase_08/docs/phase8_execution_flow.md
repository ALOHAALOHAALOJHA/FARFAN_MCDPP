# Phase 8 Execution Flow

## Overview

Phase 8 (Recommendation Engine - RECOMMENDER) transforms analysis results from Phase 7 into actionable policy recommendations at three hierarchical levels: MICRO, MESO, and MACRO.

**Version**: 2.0.0  
**Status**: ACTIVE  
**Last Updated**: 2026-01-13

---

## Stage-Based Architecture

Phase 8 follows a clear stage-based execution architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     PHASE 8 PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STAGE 00: FOUNDATION                                       │
│  └─ phase8_00_00_data_models.py                            │
│     • Recommendation, RecommendationSet                     │
│     • RuleCondition, TemplateContext                        │
│     • Core data structures for all modules                  │
│                                                             │
│  ↓                                                          │
│                                                             │
│  STAGE 10: VALIDATION                                       │
│  └─ phase8_10_00_schema_validation.py                      │
│     • Schema-driven rule validation                         │
│     • Ensures rule integrity before execution               │
│                                                             │
│  ↓                                                          │
│                                                             │
│  STAGE 20: CORE RECOMMENDATION GENERATION                   │
│  ├─ phase8_20_02_generic_rule_engine.py                    │
│  │  • Generic rule matching with strategy pattern           │
│  │  • O(1) rule lookup via indexing                         │
│  ├─ phase8_20_03_template_compiler.py                      │
│  │  • Template compilation for fast rendering               │
│  ├─ phase8_20_00_recommendation_engine.py                  │
│  │  • Main recommendation generation logic                  │
│  │  • MICRO, MESO, MACRO recommendation creation            │
│  ├─ phase8_20_04_recommendation_engine_orchestrator.py     │
│  │  • Orchestrates multi-engine execution                   │
│  └─ phase8_20_01_recommendation_engine_adapter.py          │
│     • Adapter for pipeline integration                      │
│                                                             │
│  ↓                                                          │
│                                                             │
│  STAGE 30: ENRICHMENT                                       │
│  └─ phase8_30_00_signal_enriched_recommendations.py        │
│     • Enrich recommendations with SISAS signals             │
│     • Priority adjustment based on signal data              │
│                                                             │
│  ↓                                                          │
│                                                             │
│  STAGE 35: TARGETING (Optional)                             │
│  └─ phase8_35_00_entity_targeted_recommendations.py        │
│     • Target recommendations to specific entities           │
│     • Entity-level customization                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Execution Sequence

### 1. **Input Reception** (From Phase 7)

Phase 8 receives analysis results from Phase 7:

```python
{
    "micro_scores": {
        "PA01-DIM01": 0.5,
        "PA01-DIM02": 1.2,
        # ... 60 total (10 PA × 6 DIM)
    },
    "cluster_data": {
        "CL01": {"score": 45, "variance": 0.12},
        # ... cluster analysis results
    },
    "macro_data": {
        "macro_band": "SATISFACTORIO"
    }
}
```

**Validation**: Input contract verifies all prerequisites (PRE-P8-001 to PRE-P8-005)

---

### 2. **Stage 00: Foundation** (Weight: 10000 - CRITICAL)

**Module**: `phase8_00_00_data_models.py`

Provides core data structures used throughout Phase 8:

- **Recommendation**: Individual recommendation with text, confidence, level
- **RecommendationSet**: Collection of recommendations with metadata
- **RuleCondition**: Conditions for rule matching
- **TemplateContext**: Context for template rendering

**Dependencies**: None (foundation layer)

---

### 3. **Stage 10: Validation** (Weight: 9000 - CRITICAL)

**Module**: `phase8_10_00_schema_validation.py`

Validates recommendation rules before execution:

```python
validator = UniversalRuleValidator()
result = validator.validate_rule(rule_dict)

if result.is_valid:
    # Proceed with rule execution
else:
    # Log validation errors
    logger.error(f"Rule validation failed: {result.errors}")
```

**Key Functions**:
- Schema-driven validation
- Ensures rule consistency
- Prevents invalid rule execution

**Dependencies**: `phase8_00_00_data_models`

---

### 4. **Stage 20: Core Generation** (Weights: 10000, 9000, 7000 - CRITICAL/HIGH)

#### 4a. Generic Rule Engine (Weight: 9000 - CRITICAL)

**Module**: `phase8_20_02_generic_rule_engine.py`

Provides generic rule matching with O(1) lookup:

```python
# Strategy-based rule matching
strategy = MicroMatchingStrategy()
engine = GenericRuleEngine(rules, strategy)

# Fast O(1) lookup
matched_rules = engine.match("PA01-DIM01", score_data)
```

**Key Features**:
- Strategy pattern for different rule levels
- Index-based O(1) rule lookup
- Reusable across MICRO, MESO, MACRO

#### 4b. Template Compiler (Weight: 7000 - HIGH)

**Module**: `phase8_20_03_template_compiler.py`

Compiles templates for efficient rendering:

```python
compiler = TemplateCompiler()
compiled = compiler.compile("Score in {{PAxx}}-{{DIMxx}} is {{score}}")

# Fast rendering (50x faster than regex)
text = compiled.render(PAxx="PA01", DIMxx="DIM01", score="0.5")
```

**Key Features**:
- Bytecode compilation
- 50x faster rendering
- Memoization for repeated compilations

#### 4c. Main Recommendation Engine (Weight: 10000 - CRITICAL)

**Module**: `phase8_20_00_recommendation_engine.py`

Main engine for generating recommendations:

```python
engine = RecommendationEngine()

# Generate at all three levels
micro_recs = engine.generate_micro_recommendations(micro_scores)
meso_recs = engine.generate_meso_recommendations(cluster_data)
macro_recs = engine.generate_macro_recommendations(macro_data)
```

**Three-Level Generation**:

1. **MICRO Level**: Policy Area × Dimension specific
   - 60 possible combinations (10 PA × 6 DIM)
   - Scores: [0, 3]
   - Granular, actionable recommendations

2. **MESO Level**: Cluster-based
   - Policy area groups
   - Scores: [0, 100]
   - Medium-term strategic recommendations

3. **MACRO Level**: Overall policy direction
   - Entire policy framework
   - Scores: [0, 100]
   - High-level strategic guidance

#### 4d. Engine Orchestrator (Weight: 8000 - HIGH)

**Module**: `phase8_20_04_recommendation_engine_orchestrator.py`

Coordinates multiple engines:

```python
orchestrator = RecommendationEngine(
    rules_path="rules.json",
    enable_validation_cache=True
)

# Orchestrates all three levels
all_recs = orchestrator.generate_all_recommendations(
    micro_scores=micro_scores,
    cluster_data=cluster_data,
    macro_data=macro_data
)
```

#### 4e. Pipeline Adapter (Weight: 5000 - HIGH)

**Module**: `phase8_20_01_recommendation_engine_adapter.py`

Adapts engine for pipeline integration:

```python
adapter = RecommendationEngineAdapter()

# Convert Phase 7 output → Phase 8 format → Phase 9 input
phase9_input = adapter.transform(phase7_output)
```

**Dependencies**: All Stage 00, 10, and earlier Stage 20 modules

---

### 5. **Stage 30: Signal Enrichment** (Weight: 6000 - HIGH)

**Module**: `phase8_30_00_signal_enriched_recommendations.py`

Enriches recommendations with SISAS signal data:

```python
enricher = SignalEnrichedRecommender()

# Add signal-based prioritization
enriched_recs = enricher.enrich_with_signals(
    recommendations=base_recs,
    signal_data=sisas_signals
)
```

**Enrichment Features**:
- SISAS signal integration
- Dynamic priority adjustment
- Contextual recommendation enhancement
- Optional (degrades gracefully if signals unavailable)

**Dependencies**: Stage 20 outputs

---

### 6. **Stage 35: Entity Targeting** (Weight: 4000 - STANDARD, Optional)

**Module**: `phase8_35_00_entity_targeted_recommendations.py`

Targets recommendations to specific entities:

```python
targeter = EntityTargetedRecommender()

# Customize for specific entities
entity_recs = targeter.target_recommendations(
    recommendations=enriched_recs,
    entity_id="ENTITY_001",
    entity_profile=entity_profile
)
```

**Targeting Features**:
- Entity-specific customization
- Profile-based recommendation filtering
- Jurisdiction-aware recommendations
- Optional enhancement module

**Dependencies**: Stage 30 outputs

---

## Data Flow

```
Phase 7 Output
      ↓
[INPUT CONTRACT VALIDATION]
      ↓
┌─────────────────────┐
│  Stage 00           │
│  Data Models        │ → Core structures loaded
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  Stage 10           │
│  Schema Validation  │ → Rules validated
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  Stage 20           │
│  Core Generation    │ → MICRO, MESO, MACRO recommendations
│                     │   • Generic engine (O(1) matching)
│                     │   • Template compiler (fast rendering)
│                     │   • Main engine (rule application)
│                     │   • Orchestrator (coordination)
│                     │   • Adapter (format conversion)
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  Stage 30           │
│  Signal Enrichment  │ → SISAS signals integrated
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  Stage 35           │
│  Entity Targeting   │ → Entity-specific customization
└──────┬──────────────┘
       ↓
[OUTPUT CONTRACT VALIDATION]
       ↓
Phase 9 Input
```

---

## Output Format

Phase 8 produces a structured output with three-level recommendations:

```json
{
  "MICRO": {
    "level": "MICRO",
    "recommendations": [
      {
        "id": "REC-MICRO-001",
        "policy_area": "PA01",
        "dimension": "DIM01",
        "text": "Mejorar la transparencia...",
        "confidence": 0.85,
        "score": 1.2,
        "priority": "HIGH"
      }
      // ... more MICRO recommendations
    ],
    "metadata": {
      "total_count": 45,
      "avg_confidence": 0.78
    }
  },
  "MESO": {
    "level": "MESO",
    "recommendations": [
      {
        "id": "REC-MESO-001",
        "cluster_id": "CL01",
        "text": "Fortalecer el marco regulatorio...",
        "confidence": 0.82,
        "score": 67,
        "priority": "HIGH"
      }
      // ... more MESO recommendations
    ],
    "metadata": {
      "total_count": 12,
      "avg_confidence": 0.80
    }
  },
  "MACRO": {
    "level": "MACRO",
    "recommendations": [
      {
        "id": "REC-MACRO-001",
        "text": "Implementar reforma integral...",
        "confidence": 0.88,
        "score": 75,
        "priority": "CRITICAL"
      }
      // ... more MACRO recommendations
    ],
    "metadata": {
      "total_count": 5,
      "avg_confidence": 0.85
    }
  },
  "metadata": {
    "phase_id": 8,
    "timestamp": "2026-01-13T22:00:00Z",
    "total_recommendations": 62,
    "confidence_stats": {
      "min": 0.60,
      "max": 0.95,
      "avg": 0.79
    }
  }
}
```

---

## Quality Assurance

### Contract Validation Points

1. **Input Validation** (Entry Point)
   - Phase 7 completion verified
   - All 60 micro scores present
   - Cluster and macro data available
   - Rule files accessible

2. **Runtime Validation** (During Execution)
   - Rule schema validation
   - Template compilation checks
   - Data structure consistency

3. **Output Validation** (Exit Point)
   - All three levels generated
   - All 10 Policy Areas covered (MICRO)
   - Confidence thresholds met (≥ 0.6)
   - Score bounds respected
   - JSON serializability

### Error Handling

- **Graceful Degradation**: Optional modules (signal enrichment, entity targeting) fail gracefully
- **Validation Errors**: Logged with detailed context
- **Rule Failures**: Individual rule failures don't block other recommendations
- **Signal Unavailability**: System continues without enrichment

---

## Performance Characteristics

| Operation | Performance | Notes |
|-----------|-------------|-------|
| Rule Matching | O(1) lookup | Via indexed engine |
| Template Rendering | 50x faster | Compiled templates |
| Validation | Memoized | Content-addressed cache |
| Full Pipeline | ~2-5 seconds | For typical input |

---

## Integration Points

### Upstream (Phase 7)
- Receives: Analysis results with micro/meso/macro scores
- Format: JSON with standardized schema
- Contract: Input contract (5 preconditions)

### Downstream (Phase 9)
- Delivers: Three-level recommendations
- Format: JSON with hierarchical structure
- Contract: Output contract (7 postconditions)

### External (Optional)
- SISAS Signal Registry: Real-time signals for enrichment
- Entity Database: Entity profiles for targeting

---

## Configuration

### Rule Files
- Location: `json_phase_eight/recommendation_rules_enhanced.json`
- Format: JSON with rule definitions
- Validation: Schema-driven validation at startup

### Constants
- Location: `primitives/PHASE_8_CONSTANTS.py`
- Includes: Thresholds, bounds, default values

### Types
- Location: `primitives/PHASE_8_TYPES.py`
- Defines: Type aliases and protocols

---

## Monitoring & Observability

### Metrics
- Total recommendations generated (by level)
- Average confidence scores
- Rule matching success rate
- Template rendering performance
- Signal enrichment coverage

### Logs
- Rule validation failures
- Recommendation generation events
- Signal integration status
- Performance warnings

---

## Dependencies

### Internal (Phase 8)
```
phase8_00_00_data_models (foundation)
  ↓
phase8_10_00_schema_validation
  ↓
phase8_20_02_generic_rule_engine ←─┐
phase8_20_03_template_compiler ←─┐ │
  ↓                              │ │
phase8_20_00_recommendation_engine │
  ↓                                │
phase8_20_04_orchestrator ─────────┘
  ↓
phase8_20_01_adapter
  ↓
phase8_30_00_signal_enriched
  ↓
phase8_35_00_entity_targeted
```

### External
- Phase 7: Analysis results
- SISAS Signal Registry: (optional) Real-time signals
- Entity Database: (optional) Entity profiles

---

## Version History

### v2.0.0 (Current)
- Modular stage-based architecture
- Generic rule engine with O(1) lookup
- Template compilation for performance
- Schema-driven validation
- Signal enrichment support
- Entity targeting (optional)

### v1.0.0 (Legacy)
- Monolithic recommendation engine
- Basic rule matching
- Simple template rendering

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-13  
**Maintained By**: F.A.R.F.A.N Phase 8 Team
