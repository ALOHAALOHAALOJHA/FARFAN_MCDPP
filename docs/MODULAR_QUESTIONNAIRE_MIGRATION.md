# Modular Questionnaire Migration Guide

This document describes the migration from the legacy `questionnaire_monolith.json` to the **modular questionnaire structure** under `canonic_questionnaire_central/`.

## Background

The 300-question analytical questionnaire was previously stored as a single monolithic JSON file. This caused:

- Large file sizes (~25 MB)
- Merge conflicts when multiple contributors edited different policy areas
- Difficulty maintaining provenance per policy area or dimension
- No granular loading (full file always loaded)

## New Architecture

The questionnaire is now **modularized**:

```
canonic_questionnaire_central/
├── modular_manifest.json          # Master manifest with structure and totals
├── questionnaire_index.json       # ID→file mapping for fast lookup
├── canonical_notation.json        # Shared dimensions/policy_areas metadata
├── meso_questions.json            # 4 meso-level questions
├── macro_question.json            # 1 macro-level question
├── policy_areas/
│   ├── PA01_mujeres_genero/
│   │   ├── metadata.json
│   │   ├── keywords.json
│   │   └── questions.json         # 30 questions for PA01
│   ├── PA02_violencia_conflicto/
│   │   └── ...
│   └── ... (PA03–PA10)
├── dimensions/
│   ├── DIM01_INSUMOS/
│   │   ├── metadata.json
│   │   └── questions.json         # 50 questions for DIM01
│   └── ... (DIM02–DIM06)
├── clusters/
│   ├── CL01_seguridad_paz/
│   │   └── questions.json
│   └── ... (CL02–CL04)
├── questionnaire_monolith.json    # BACKUP ONLY (legacy)
└── questionnaire_monolith.json.backup
```

## Loading Strategy

| Environment Variable | Default | Behavior |
|----------------------|---------|----------|
| `USE_MODULAR_QUESTIONNAIRE` | `true` | Load from modular structure via `QuestionnaireModularResolver` |
| | `false` | Load legacy monolith file (deprecated) |

### Programmatic Usage

```python
# Modern approach (default)
from farfan_pipeline.infrastructure.questionnaire import QuestionnaireModularResolver

resolver = QuestionnaireModularResolver()
payload = resolver.build_monolith_payload()
# payload.data contains the full 300-question structure

# Load specific slice (efficient for per-policy-area tasks)
pa_slice = resolver.load_policy_area("PA03")  # 30 questions
dim_slice = resolver.load_dimension("DIM04")  # 50 questions

# Signal registry creation from modular
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
    create_signal_registry_from_modular,
)
registry = create_signal_registry_from_modular()
```

### Factory Integration

`AnalysisPipelineFactory` automatically uses the modular path when `RuntimeConfig.use_modular_questionnaire` is `True` (default). No code changes required in most cases.

## Parity Tests

Run parity tests to verify modular and monolith equivalence:

```bash
pytest tests/test_modular_monolith_parity.py -v
```

These tests verify:

- Total question count (300)
- Per-policy-area count (30 each)
- Per-dimension count (50 each)
- ID ordering matches index
- Canonical notation alignment

## Migration Checklist

1. **No code changes** needed for standard pipeline invocations.
2. Update any hardcoded paths referencing `questionnaire_monolith.json`.
3. Use `QuestionnaireModularResolver` for new features needing per-PA/dimension access.
4. Keep the monolith backup intact for emergency fallback.
5. Run `tests/test_modular_monolith_parity.py` to confirm equivalence.

## Files Changed

| File | Change |
|------|--------|
| `phase0_10_00_paths.py` | Added modular path constants |
| `phase0_10_01_runtime_config.py` | Added `use_modular_questionnaire` flag |
| `phase2_10_00_factory.py` | Auto-selects modular vs monolith loader |
| `signal_registry.py` | Added `create_signal_registry_from_modular()` |
| `signal_loader.py` | Deprecated; reference modular resolver |
| `phase2_60_01_contract_validator_cqvr.py` | Updated hash recommendation |
| `phase2_95_00_contract_hydrator.py` | Updated docstring |
| `README.md`, `Phase_two/README.md` | Updated invocation examples |
| `modular_manifest.json` | Added loading_strategy section |

## FAQ

**Q: Is the monolith file still valid?**  
A: Yes, it's retained as a backup and for emergency fallback (`USE_MODULAR_QUESTIONNAIRE=false`).

**Q: Will my existing tests break?**  
A: No. The modular loader assembles an equivalent payload; all downstream APIs remain unchanged.

**Q: How do I contribute new questions?**  
A: Edit the appropriate `policy_areas/PAxx_*/questions.json` file and update the counts in `modular_manifest.json`.
