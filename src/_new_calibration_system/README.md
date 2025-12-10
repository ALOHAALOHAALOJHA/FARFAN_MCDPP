# _new_calibration_system (TEMPORAL)

## PROPÓSITO
Sistema de calibración completo en desarrollo aislado.
**NO USAR en producción hasta migración completa.**

## ARQUITECTURA OBJETIVO

```
intrinsic_calibration.json (campo "layer")
           ↓
    LAYER_REQUIREMENTS
           ↓
   Capas requeridas por método
```

## MIGRACIÓN
Tras validación, este sistema reemplazará:
- `src/core/calibration/`
- Archivos `COHORT_2024_*` relevantes en `cross_cutting_infrastrucuture/`

## JOBFRONTS

| # | Estado | Nombre | Artefacto |
|---|--------|--------|-----------|
| 0 | ✅ | AISLAMIENTO | Esta estructura |
| 1 | ⬜ | INVENTARIO | `canonical_method_catalog.json` |
| 2 | ⬜ | RUBRIC | `intrinsic_calibration_rubric.json` |
| 3 | ⬜ | TRIAGE ENGINE | `intrinsic_calibration.json` poblado |
| 4 | ⬜ | CORE SYSTEM | Singletons, loaders, decoradores |
| 5 | ⬜ | VALIDACIÓN | Tests passing |
| 6 | ⬜ | MIGRACIÓN | Sistema reemplazado |

## ESTRUCTURA

```
_new_calibration_system/
├── __init__.py
├── README.md
├── config/
│   ├── canonical_method_catalog.json   # ~2000 métodos
│   ├── intrinsic_calibration.json      # Scores y layer por método
│   ├── intrinsic_calibration_rubric.json
│   ├── method_parameters.json
│   ├── fusion_weights.json
│   └── layer_requirements.json
├── core/
│   ├── __init__.py                     # Singletons
│   ├── layer_requirements.py           # ÚNICO LAYER_REQUIREMENTS
│   ├── intrinsic_loader.py
│   ├── parameter_loader.py
│   ├── decorators.py
│   └── orchestrator.py
├── scripts/
│   ├── scan_methods_inventory.py
│   ├── triage_intrinsic_calibration.py
│   ├── detect_hardcoded.py
│   └── verify_anchoring.py
└── tests/
    ├── test_layer_requirements.py
    ├── test_singletons.py
    ├── test_no_hardcoded.py
    └── test_full_coverage.py
```

## REGLAS NO NEGOCIABLES

1. **CERO imports del sistema existente** - Todo autocontenido
2. **JSON es fuente de verdad** - Python lee, no define
3. **Singletons obligatorios** - `get_calibration_orchestrator()`, etc.
4. **TODOS los métodos en inventario** - ~2000, no solo executors
