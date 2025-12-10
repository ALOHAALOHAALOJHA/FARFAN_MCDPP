# Plan: Transformación Completa del Sistema de Calibración con Migración Segura

**TL;DR**: Crear carpeta temporal aislada (`_new_calibration_system/`), construir ahí el sistema completo de inventario/triage/calibración/capas, validar que funciona, y SOLO ENTONCES migrar reemplazando lo existente. Cero riesgo de romper el sistema actual durante desarrollo.

---

## JOBFRONTS OVERVIEW

| # | NOMBRE | DEPENDENCIAS | ARTEFACTO PRINCIPAL |
|---|--------|--------------|---------------------|
| 0 | AISLAMIENTO | Ninguno | `src/_new_calibration_system/` estructura |
| 1 | INVENTARIO | 0 | `canonical_method_catalog.json` (~2000 métodos) |
| 2 | RUBRIC | 0 | `intrinsic_calibration_rubric.json` |
| 3 | TRIAGE ENGINE | 1, 2 | `intrinsic_calibration.json` poblado |
| 4 | CORE SYSTEM | 3 | Singletons, loaders, decoradores |
| 5 | VALIDACIÓN | 4 | Tests passing, cero hardcoded |
| 6 | MIGRACIÓN | 5 | Sistema reemplazado, legacy archivado |

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    JOBFRONT 0: AISLAMIENTO - CARPETA TEMPORAL                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ REQUIERE: Ninguno (es el primer jobfront)                                    ║
║ ARCHIVO:  src/_new_calibration_system/ (CREAR ESTRUCTURA COMPLETA)           ║
║ LÍNEAS:   N/A - Creación de directorios y archivos vacíos                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                              CONTEXTO                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ESTADO ACTUAL:                                                               ║
║   - Sistema de calibración disperso en múltiples ubicaciones:                ║
║     • src/core/calibration/ (4 archivos)                                     ║
║     • src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/    ║
║       calibration/ (50+ archivos COHORT_2024_*)                              ║
║     • src/canonic_phases/Phase_two/executor_calibration_integration.py       ║
║   - Valores hardcoded en executor_calibration_integration.py líneas 46-64    ║
║   - JSONs incompletos (intrinsic_calibration.json sin sección "methods")     ║
║   - canonical_method_catalog.json NO EXISTE                                  ║
║   - intrinsic_calibration_rubric.json NO EXISTE                              ║
║                                                                              ║
║ PROBLEMA:                                                                    ║
║   Modificar el sistema actual directamente puede romper funcionalidad        ║
║   existente. No hay forma segura de desarrollar el nuevo sistema mientras    ║
║   el viejo sigue en uso.                                                     ║
║                                                                              ║
║ CAUSA RAÍZ:                                                                  ║
║   Desarrollo incremental sin aislamiento = acumulación de deuda técnica      ║
║   y riesgo de regresiones durante refactorización.                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                              TAREA                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ACCIÓN PRINCIPAL: CREAR estructura de directorios completa                   ║
║                                                                              ║
║ ESTRUCTURA EXACTA A CREAR:                                                   ║
║                                                                              ║
║   src/_new_calibration_system/                                               ║
║   ├── __init__.py                    # Vacío, marca como paquete             ║
║   ├── README.md                      # Propósito: "Sistema temporal..."      ║
║   ├── config/                                                                ║
║   │   ├── __init__.py                                                        ║
║   │   ├── canonical_method_catalog.json      # JOBFRONT 1 lo poblará         ║
║   │   ├── intrinsic_calibration.json         # JOBFRONT 3 lo poblará         ║
║   │   ├── intrinsic_calibration_rubric.json  # JOBFRONT 2 lo creará          ║
║   │   ├── method_parameters.json             # Parametrización               ║
║   │   ├── fusion_weights.json                # Copiar de existente           ║
║   │   └── layer_requirements.json            # Copiar de existente           ║
║   ├── core/                                                                  ║
║   │   ├── __init__.py                # Singletons get_*()                    ║
║   │   ├── layer_requirements.py      # ÚNICO LAYER_REQUIREMENTS              ║
║   │   ├── intrinsic_loader.py        # IntrinsicCalibrationLoader            ║
║   │   ├── parameter_loader.py        # ParameterLoader                       ║
║   │   ├── decorators.py              # @calibrated_method                    ║
║   │   └── orchestrator.py            # CalibrationOrchestrator               ║
║   ├── scripts/                                                               ║
║   │   ├── __init__.py                                                        ║
║   │   ├── scan_methods_inventory.py  # Genera catalog                        ║
║   │   ├── triage_intrinsic_calibration.py  # Script del usuario              ║
║   │   ├── detect_hardcoded.py        # Detector de violaciones               ║
║   │   └── verify_anchoring.py        # Verificador de anclaje                ║
║   └── tests/                                                                 ║
║       ├── __init__.py                                                        ║
║       ├── test_layer_requirements.py                                         ║
║       ├── test_singletons.py                                                 ║
║       ├── test_no_hardcoded.py                                               ║
║       └── test_full_coverage.py                                              ║
║                                                                              ║
║ CONTENIDO MÍNIMO DE __init__.py RAÍZ:                                        ║
║   ```python                                                                  ║
║   """                                                                        ║
║   _new_calibration_system - TEMPORARY ISOLATED DEVELOPMENT                   ║
║                                                                              ║
║   DO NOT IMPORT FROM HERE IN PRODUCTION CODE.                                ║
║   This package will replace src/core/calibration/ after validation.          ║
║   """                                                                        ║
║   __version__ = "0.0.1-dev"                                                  ║
║   __status__ = "DEVELOPMENT_ISOLATED"                                        ║
║   ```                                                                        ║
║                                                                              ║
║ CONTENIDO README.md:                                                         ║
║   ```markdown                                                                ║
║   # _new_calibration_system (TEMPORAL)                                       ║
║                                                                              ║
║   ## PROPÓSITO                                                               ║
║   Sistema de calibración completo en desarrollo aislado.                     ║
║   NO USAR en producción hasta migración completa.                            ║
║                                                                              ║
║   ## MIGRACIÓN                                                               ║
║   Tras validación, este sistema reemplazará:                                 ║
║   - src/core/calibration/                                                    ║
║   - Archivos COHORT_2024_* relevantes                                        ║
║                                                                              ║
║   ## JOBFRONTS                                                               ║
║   - [x] JOBFRONT 0: Estructura creada                                        ║
║   - [ ] JOBFRONT 1: Inventario de métodos                                    ║
║   - [ ] JOBFRONT 2: Rubric machine-readable                                  ║
║   - [ ] JOBFRONT 3: Triage y calibración                                     ║
║   - [ ] JOBFRONT 4: Core system                                              ║
║   - [ ] JOBFRONT 5: Validación                                               ║
║   - [ ] JOBFRONT 6: Migración                                                ║
║   ```                                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                           PROHIBICIONES                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PROHIBIDO-0-001: Modificar CUALQUIER archivo fuera de                        ║
║                  src/_new_calibration_system/                                ║
║                                                                              ║
║ PROHIBIDO-0-002: Importar desde src/core/calibration/ o                      ║
║                  cross_cutting_infrastrucuture/ en los nuevos archivos       ║
║                                                                              ║
║ PROHIBIDO-0-003: Copiar código existente sin marcar origen                   ║
║                  (si se copia, agregar # SOURCE: path/original.py:L##)       ║
║                                                                              ║
║ PROHIBIDO-0-004: Crear archivos .py con lógica funcional en JOBFRONT 0       ║
║                  (solo __init__.py vacíos o con docstrings)                  ║
║                                                                              ║
║ PROHIBIDO-0-005: Usar nombres que NO empiecen con _ para la carpeta raíz     ║
║                  (debe ser _new_calibration_system/, no new_calibration/)    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                           VERIFICACIÓN                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PRE-CONDICIÓN:                                                               ║
║   ```bash                                                                    ║
║   test ! -d "src/_new_calibration_system" && echo "OK" || echo "FAIL"        ║
║   ```                                                                        ║
║   RESULTADO ESPERADO: OK                                                     ║
║                                                                              ║
║ POST-CONDICIÓN:                                                              ║
║   ```bash                                                                    ║
║   # Verificar estructura completa                                            ║
║   DIRS="config core scripts tests"                                           ║
║   ALL_OK=true                                                                ║
║   for d in $DIRS; do                                                         ║
║     if [ ! -d "src/_new_calibration_system/$d" ]; then                       ║
║       echo "FAIL: Missing $d"                                                ║
║       ALL_OK=false                                                           ║
║     fi                                                                       ║
║   done                                                                       ║
║   # Verificar archivos críticos                                              ║
║   FILES="__init__.py README.md config/__init__.py core/__init__.py"          ║
║   for f in $FILES; do                                                        ║
║     if [ ! -f "src/_new_calibration_system/$f" ]; then                       ║
║       echo "FAIL: Missing $f"                                                ║
║       ALL_OK=false                                                           ║
║     fi                                                                       ║
║   done                                                                       ║
║   $ALL_OK && echo "JOBFRONT 0 COMPLETE" || echo "JOBFRONT 0 FAILED"          ║
║   ```                                                                        ║
║   RESULTADO ESPERADO: JOBFRONT 0 COMPLETE                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                           ARTEFACTO                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ TIPO: Estructura de directorios + archivos stub                              ║
║                                                                              ║
║ CONTENIDO MÍNIMO:                                                            ║
║   - 4 subdirectorios (config/, core/, scripts/, tests/)                      ║
║   - 1 README.md con checklist de JOBFRONTS                                   ║
║   - 8+ archivos __init__.py (1 por directorio)                               ║
║   - 6 archivos .json vacíos en config/ (estructura {})                       ║
║                                                                              ║
║ CRITERIO DE ACEPTACIÓN:                                                      ║
║   - [ ] Carpeta raíz es exactamente src/_new_calibration_system/             ║
║   - [ ] Todos los __init__.py existen y son válidos Python                   ║
║   - [ ] README.md contiene checklist de 7 JOBFRONTS                          ║
║   - [ ] Ningún archivo importa de sistema existente                          ║
║   - [ ] POST-CONDICIÓN bash retorna "JOBFRONT 0 COMPLETE"                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## JOBFRONTS PENDIENTES (A DETALLAR)

### JOBFRONT 1: INVENTARIO
- Ejecutar scan_methods_inventory.py adaptado
- Generar canonical_method_catalog.json con ~2000 métodos
- Campos por método: method_id, module, class, method_name, file_path, line_number, docstring, layer

### JOBFRONT 2: RUBRIC
- Crear intrinsic_calibration_rubric.json
- Reglas machine-readable para triage (Q1, Q2, Q3)
- Fórmulas para b_theory, b_impl, b_deploy

### JOBFRONT 3: TRIAGE ENGINE
- Adaptar triage_intrinsic_calibration.py del usuario
- Ejecutar sobre catalog → generar intrinsic_calibration.json poblado
- TODOS los métodos con entrada, NO defaults uniformes

### JOBFRONT 4: CORE SYSTEM
- layer_requirements.py (ÚNICO, lee de JSON)
- intrinsic_loader.py (get_required_layers_for_method)
- parameter_loader.py
- decorators.py (@calibrated_method, @calibration_required)
- orchestrator.py (singleton)

### JOBFRONT 5: VALIDACIÓN
- test_no_hardcoded.py (cero LAYER_WEIGHTS duplicados)
- test_singletons.py (get_calibration_orchestrator es único)
- test_full_coverage.py (todos los métodos en JSON)
- detect_hardcoded.py pasa con 0 findings

### JOBFRONT 6: MIGRACIÓN
- Backup de sistema actual en archive/
- Reemplazo de src/core/calibration/
- Actualización de imports en todo el repo
- Eliminación de _new_calibration_system/
