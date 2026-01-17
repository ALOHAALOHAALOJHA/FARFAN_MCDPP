# Modular Questionnaire Architecture - Migration Guide

## Overview

The F.A.R.F.A.N pipeline was refactored to use a **modular questionnaire architecture** instead of a monolithic `questionnaire_monolith.json` file. This change enables:

1. **Granular data access** - Consumers import only what they need
2. **SISAS event-driven irrigation** - Signal Distribution Orchestrator routes data efficiently  
3. **Scope-aligned imports** - Each component gets data matching its operational scope
4. **Value-focused loading** - No unnecessary data loaded into memory

## Architecture

### Modular Structure

```
canonic_questionnaire_central/
├── dimensions/              # DIM01-DIM06, each with questions/
│   ├── DIM01_INSUMOS/
│   │   ├── metadata.json
│   │   └── questions/
│   │       ├── Q001.json
│   │       ├── Q031.json
│   │       └── ... (50 questions per dimension)
│   └── ...
├── policy_areas/            # PA01-PA10, each with metadata
│   ├── PA01_mujeres_genero/
│   │   ├── keywords.json
│   │   └── metadata.json
│   └── ...
├── cross_cutting/           # Cross-cutting themes
│   ├── cross_cutting_themes.json
│   └── themes/
├── scoring/                 # Scoring system definitions
│   └── scoring_system.json
├── validations/             # Interdependency rules
│   └── interdependency_mapping.json
├── config/                  # Canonical notation
│   └── canonical_notation.json
└── resolver.py              # CanonicalQuestionnaireResolver
```

### Resolver Pattern

The `CanonicalQuestionnaireResolver` (canonic_questionnaire_central/resolver.py) assembles the questionnaire from modular sources:

```python
from canonic_questionnaire_central.resolver import CanonicalQuestionnaireResolver

resolver = CanonicalQuestionnaireResolver()
questionnaire = resolver.resolve()

# Questionnaire now has:
# - 300 micro_questions assembled from dimensions/ × policy_areas/
# - canonical_notation from config/
# - cross_cutting themes
# - scoring system definitions
# - interdependency rules
# - Signal Distribution Orchestrator (SDO) for SISAS integration
```

## Consumer Guidelines

### 1. Scope Alignment

Each consumer should import only the data matching its operational scope:

| Consumer | Scope | Import From |
|----------|-------|-------------|
| Phase 1 Chunking | Global | resolver.resolve() |
| Phase 2 Micro Answering | Per-question | dimensions/DIM*/questions/Q*.json |
| Phase 2 Contract Validator | Policy area specific | policy_areas/PA*/ |
| Scoring System | Global scoring rules | scoring/scoring_system.json |
| Cross-cutting Validator | Theme-specific | cross_cutting/themes/ |

### 2. Value Addition

Only load data that adds value to operations:

**Bad (old monolithic approach)**:
```python
# Loads entire 1.3MB monolith for one question
with open("questionnaire_monolith.json") as f:
    data = json.load(f)
    question = next(q for q in data["blocks"]["micro_questions"] if q["question_id"] == "Q001")
```

**Good (modular approach)**:
```python
# Loads only Q001.json (~10KB)
from canonic_questionnaire_central import CQCLoader
cqc = CQCLoader()
question = cqc.get_question("Q001")  # Lazy-loaded, cached
```

### 3. SISAS Signal Tools

Consumers must be equipped with SISAS signal tools:

```python
# Use resolver with SDO enabled
resolver = CanonicalQuestionnaireResolver(sdo_enabled=True)
questionnaire = resolver.resolve()

# Access SDO for signal dispatch
from canonic_questionnaire_central.core import Signal, SignalType, SignalScope

signal = Signal(
    signal_type=SignalType.MICRO_ANSWERING,
    scope=SignalScope.QUESTION,
    question_id="Q001",
    data={"text": "policy document excerpt"}
)

# Dispatch through SDO
resolver.dispatch_signal(signal)
```

### 4. Event-Driven Irrigation

Data transmission must work as event-driven irrigation via SISAS:

```python
# Register as signal consumer
def handle_micro_signal(signal):
    # Process signal with granular context
    question_data = cqc.get_question(signal.question_id)
    patterns = cqc.resolve_patterns(signal.question_id)
    # ... scoring logic

# SDO routes signals to registered consumers
resolver.sdo.register_consumer(
    signal_type=SignalType.MICRO_ANSWERING,
    consumer=handle_micro_signal
)
```

## Migration Status

### Completed ✅
- [x] Modular structure created (dimensions/, policy_areas/, etc.)
- [x] CanonicalQuestionnaireResolver implemented
- [x] CQCLoader with lazy loading
- [x] Signal Distribution Orchestrator (SDO) integration
- [x] Removed questionnaire_monolith.json

### In Progress 🔄
- [ ] Factory refactored to use resolver (phase2_10_00_factory.py)
- [ ] Fix resolver assembly bugs (_assemble_micro_questions)
- [ ] SISAS signal registry integration with modular data
- [ ] Cross-cutting themes validation pipeline
- [ ] Interdependency rules enforcement

### Pending ⏳
- [ ] Contract generator refactored (input_registry.py)
- [ ] Scoring context enriched with granular metadata
- [ ] All consumers audited for scope alignment
- [ ] Performance benchmarks (modular vs monolithic)
- [ ] Documentation updated across codebase

## Refactoring Checklist

When refactoring a consumer from monolithic to modular:

1. **Identify scope**: What data does this consumer actually need?
2. **Check alignment**: Does the import match the consumer's operational scope?
3. **Add value**: Does this data enable or enhance the consumer's operations?
4. **Equip with SISAS**: Does the consumer have signal tools for event-driven processing?
5. **Enable irrigation**: Can data flow through SDO as signals?

If ANY of these criteria is not met, refactor is incomplete.

## References

- SISAS Architecture: `docs/design/SISAS_ARCHITECTURE.md`
- Signal Irrigation Audit: `docs/SIGNAL_IRRIGATION_AUDIT_2026_01_04.md`
- Resolver Implementation: `canonic_questionnaire_central/resolver.py`
- CQC Loader: `canonic_questionnaire_central/__init__.py`

## Known Issues

1. **Resolver Bug**: `_assemble_micro_questions()` has AttributeError when loading policy_areas
   - Symptom: `'str' object has no attribute 'get'`
   - Location: resolver.py line 946
   - Status: Under investigation

2. **Factory Migration**: phase2_10_00_factory.py partially migrated
   - load_questionnaire() updated to use resolver
   - Needs testing and validation
   - May require backward compatibility layer

3. **Test Coverage**: Original test_critical_json_files.py removed
   - Need new tests for modular architecture
   - Should test resolver assembly
   - Should test CQC loader performance

---

**Last Updated**: 2026-01-17  
**Migration Lead**: Refactoring per SISAS 2.0 requirements  
**Status**: ACTIVE MIGRATION - DO NOT USE MONOLITH
