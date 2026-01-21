# Deprecated Orchestrators

## Status: DEPRECATED as of 2026-01-19

The following orchestrator files are **DEPRECATED** and will be removed in version 3.0.0:

| File | Replacement |
|------|-------------|
| `src/farfan_pipeline/infrastructure/extractors/extractor_orchestrator.py` | `UnifiedOrchestrator` |
| `canonic_questionnaire_central/colombia_context/async_orchestrator.py` | `UnifiedOrchestrator` |
| `canonic_questionnaire_central/colombia_context/enrichment_orchestrator.py` | `UnifiedOrchestrator` |
| `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/orchestration/sisas_orchestrator.py` | `UnifiedOrchestrator` |

## Migration Guide

### Before (Deprecated)

```python
from farfan_pipeline.infrastructure.extractors.extractor_orchestrator import ExtractorOrchestrator
from canonic_questionnaire_central.colombia_context.async_orchestrator import AsyncEnrichmentOrchestrator
from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import EnrichmentOrchestrator
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.orchestration.sisas_orchestrator import SISASOrchestrator
```

### After (Current)

```python
from farfan_pipeline.orchestration import UnifiedOrchestrator, OrchestratorConfig

config = OrchestratorConfig(enable_sisas=True)
orchestrator = UnifiedOrchestrator(config=config)
```

## Functionality Mapping

| Deprecated Feature | UnifiedOrchestrator Equivalent |
|-------------------|-------------------------------|
| `ExtractorOrchestrator.process_document()` | `UnifiedOrchestrator._execute_phase_01()` |
| `AsyncEnrichmentOrchestrator.enrich_async()` | `UnifiedOrchestrator` with SISAS signal dispatch |
| `EnrichmentOrchestrator.process_with_gates()` | `UnifiedOrchestrator._execute_phase_02()` via `phase_02_enrichment_consumer` |
| `SISASOrchestrator.irrigate()` | `SignalDistributionOrchestrator.dispatch()` via `UnifiedOrchestrator.context.sisas` |

## Consumer Configuration

The 10 phase consumers are now configured in `UnifiedOrchestrator.CONSUMER_CONFIGS`:

| Consumer ID | Phase | Capabilities |
|-------------|-------|--------------|
| `phase_00_assembly_consumer` | Phase 0 | STATIC_LOAD, SIGNAL_PACK, PHASE_MONITORING |
| `phase_01_extraction_consumer` | Phase 1 | EXTRACTION, STRUCTURAL_PARSING, ... |
| `phase_02_enrichment_consumer` | Phase 2 | ENRICHMENT, PATTERN_MATCHING, ENTITY_RECOGNITION |
| `phase_03_validation_consumer` | Phase 3 | VALIDATION, NORMATIVE_CHECK, COHERENCE_CHECK |
| `phase_04_micro_consumer` | Phase 4 | SCORING, MICRO_LEVEL, CHOQUET_INTEGRAL |
| `phase_05_meso_consumer` | Phase 5 | SCORING, MESO_LEVEL, DIMENSION_AGGREGATION |
| `phase_06_macro_consumer` | Phase 6 | SCORING, MACRO_LEVEL, POLICY_AREA_AGGREGATION |
| `phase_07_aggregation_consumer` | Phase 7 | AGGREGATION, CLUSTER_LEVEL |
| `phase_08_integration_consumer` | Phase 8 | INTEGRATION, RECOMMENDATION_ENGINE |
| `phase_09_report_consumer` | Phase 9 | REPORT_GENERATION, ASSEMBLY, EXPORT |

## Validation

Run the migration check script:

```bash
python scripts/sisas_migration/migrate_orchestrators.py --check
```

To see fix suggestions:

```bash
python scripts/sisas_migration/migrate_orchestrators.py --fix
```

## Timeline

- **2026-01-19**: Deprecation warnings added
- **2026-04-01**: Removal planned for version 3.0.0

## See Also

- [SISAS Unification Documentation](docs/sisas_unification/README.md)
- [Migration Checklist](docs/sisas_unification/MIGRATION_CHECKLIST.md)
- [Architecture Documentation](docs/sisas_unification/ARCHITECTURE.md)
