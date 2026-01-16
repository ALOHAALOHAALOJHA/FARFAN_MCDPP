# Plan de Reorganización y Etiquetamiento FARFAN 2025.1

**Objetivo**: Unificar la folderización, documentación y etiquetamiento para reflejar la arquitectura de calibración epistémica y PDM implementada.

**Fecha**: 2026-01-15
**Versión**: 1.0.0
**Autor**: FARFAN Engineering Team

---

## 📊 DIAGNÓSTICO ACTUAL

### Problemas Identificados

| # | Problema | Impacto | Ubicación |
|---|----------|---------|-----------|
| 1 | **Naming inconsistente**: `Phase_X` vs `phaseX` | Alto | `/phases/` vs `/irrigation_using_signals/SISAS/consumers/` |
| 2 | **Documentación dispersa**: 9+ locaciones docs | Alto | Root + cada Phase + subdirectorios |
| 3 | **Calibración fragmentada**: 3 sistemas diferentes | Medio | `/infrastructure/calibration/`, `/config/`, `_registry/` |
| 4 | **Tests desalineados**: No mirror completo con src | Medio | `/tests/` vs `/src/` |
| 5 | **SISAS naming**: `phaseX` inconsistente con `Phase_X` | Medio | `/irrigation_using_signals/SISAS/consumers/` |
| 6 | **Dashboard naming**: `dashboard_atroz_` con underscore | Bajo | `/dashboard_atroz_/` |
| 7 | **PDM documentation**: Solo en `/docs/PDM_STRUCTURAL_RECOGNITION.md` | Bajo | Root level |

---

## 🎯 VISIÓN UNIFICADA

### Principios Rectores

1. **EPISTEMIC-FIRST**: La estructura debe reflejar las 5 capas epistémicas (N0-N4)
2. **CALIBRATION-CENTRIC**: La calibración es el núcleo organizativo
3. **DOCUMENTATION-AS-CODE**: La documentación vive junto al código
4. **TEST-MIRROR**: Los tests espejan perfectamente la estructura src/
5. **CONSISTENT-NAMING**: Un solo naming convention en todo el proyecto

---

## 📁 NUEVA ESTRUCTURA PROPUESTA

```
FARFAN_MPP/
│
├── README.md                           # Root README (actualizado)
├── CHANGELOG.md                        # Registro de cambios
├── pyproject.toml                      # Configuración proyecto
│
├── docs/                               # DOCUMENTACIÓN CENTRALIZADA
│   ├── INDEX.md                         # Índice principal
│   ├── EPISTEMIC_ARCHITECTURE.md       # Arquitectura epistémica
│   ├── CALIBRATION_SYSTEM.md           # Sistema de calibración
│   ├── PDM_RECOGNITION.md              # Reconocimiento PDM
│   ├── PHASE_OVERVIEW.md                # Visión general fases
│   │
│   ├── architecture/                    # Documentación arquitectónica
│   │   ├── LAYER_0_INFRASTRUCTURE.md
│   │   ├── LAYER_1_EPISTEMIC_LEVELS.md
│   │   ├── LAYER_2_CONTRACT_TYPES.md
│   │   ├── LAYER_3_PDM_SENSITIVITY.md
│   │   └── LAYER_4_CALIBRATION_REGISTRY.md
│   │
│   ├── guides/                          # Guías de uso
│   │   ├── QUICKSTART.md
│   │   ├── CALIBRATION_GUIDE.md
│   │   ├── PDM_INTEGRATION_GUIDE.md
│   │   └── TESTING_GUIDE.md
│   │
│   ├── api/                             # Documentación API
│   │   ├── phase0_api.md
│   │   ├── phase1_api.md
│   │   ├── phase2_api.md
│   │   └── ...
│   │
│   └── legacy/                          # Documentación histórica
│       ├── PHASE1_OLD.md
│       └── ...
│
├── src/
│   └── farfan_pipeline/
│       │
│       ├── __init__.py
│       │
│       ├── # =========================================
│       ├── # SISTEMA DE CALIBRACIÓN EPISTÉMICA
│       ├── # =========================================
│       ├── calibration/                   # 🎯 NÚCLEO: Sistema de calibración
│       │   ├── __init__.py
│       │   ├── README.md                   # Documentación calibración
│       │   │
│       │   ├── core/                      # Niveles epistémicos (N0-N4)
│       │   │   ├── __init__.py
│       │   │   ├── n0_infrastructure.py
│       │   │   ├── n1_empirical.py
│       │   │   ├── n2_inferential.py
│       │   │   ├── n3_audit.py
│       │   │   ├── n4_meta.py
│       │   │   └── base_calibration.py     # Clase base
│       │   │
│       │   ├── registry/                  # 8-layer resolution
│       │   │   ├── __init__.py
│       │   │   ├── calibration_registry.py
│       │   │   └── pdm_profile.py         # PDM structural profile
│       │   │
│       │   ├── config/                    # Configuraciones JSON
│       │   │   ├── method_registry.json    # Mapping método→nivel
│       │   │   ├── level_defaults/         # Defaults por nivel
│       │   │   │   ├── n0_infrastructure.json
│       │   │   │   ├── n1_empirical.json
│       │   │   │   ├── n2_inferential.json
│       │   │   │   ├── n3_audit.json
│       │   │   │   └── n4_meta.json
│       │   │   ├── type_overrides/          # Overrides por tipo
│       │   │   │   ├── type_a.json          # Semantic Triangulation
│       │   │   │   ├── type_b.json          # Bayesian Inference
│       │   │   │   ├── type_c.json          # Causal Inference
│       │   │   │   ├── type_d.json          # Financial Aggregation
│       │   │   │   ├── type_e.json          # Logical Consistency
│       │   │   │   └── subtype_f.json       # Hybrid/Fallback
│       │   │   └── pdm_rules/              # Reglas PDM-driven
│       │   │       ├── pdm_master_config.json
│       │   │       ├── n1_pdm_rules.json
│       │   │       ├── n2_pdm_rules.json
│       │   │       └── n3_pdm_rules.json
│       │   │
│       │   └── contracts/                 # Contratos calibración
│       │       ├── __init__.py
│       │       ├── calibration_contract.py
│       │       └── validation.py
│       │
│       ├── # =========================================
│       ├── # RECONOCIMIENTO ESTRUCTURAL PDM
│       ├── # =========================================
│       ├── pdm/                             # PDM structural recognition
│       │   ├── __init__.py
│       │   ├── README.md                   # Documentación PDM
│       │   │
│       │   ├── profile/                   # PDM profile (Ley 152/94)
│       │   │   ├── __init__.py
│       │   │   ├── structural_profile.py   # PDMStructuralProfile
│       │   │   ├── hierarchy_levels.py     # H1-H5 enums
│       │   │   ├── canonical_sections.py    # Secciones canónicas
│       │   │   ├── semantic_rules.py        # Reglas semánticas
│       │   │   └── table_schemas.py         # Schemas tablas PDM
│       │   │
│       │   ├── contracts/                 # Contratos PDM
│       │   │   ├── __init__.py
│       │   │   ├── pdm_contracts.py
│       │   │   └── sp2_sp4_obligations.py
│       │   │
│       │   ├── integration/               # Integración Phase 1
│       │   │   ├── __init__.py
│       │   │   ├── sp2_integration.py      # Integración SP2
│       │   │   └── sp4_integration.py      # Integración SP4
│       │   │
│       │   └── calibrator/                # Ex-post calibrator
│       │       ├── __init__.py
│       │       ├── pdm_calibrator.py
│       │       └── optimization.py
│       │
│       ├── # =========================================
│       ├── # INFRAESTRUCTURA COMPARTIDA
│       ├── # =========================================
│       ├── infrastructure/                 # Infraestructura compartida
│       │   ├── __init__.py
│       │   ├── extractors/
│       │   ├── validators/
│       │   ├── scoring/
│       │   └── utils/
│       │
│       ├── questionnaire/                  # Cuestionario centralizado
│       │   ├── __init__.py
│       │   ├── registry.py                # Registro preguntas
│       │   ├── mapper.py                  # Mapeo preguntas
│       │   └── config/
│       │       ├── questionnaire.json
│       │       └── signal_registry.json
│       │
│       ├── signals/                        # Procesamiento de señales
│       │   ├── __init__.py
│       │   ├── sisas/                     # SISAS v2.0
│       │   │   ├── consumers/             # phase0-phase8
│       │   │   ├── core/
│       │   │   └── signals/
│       │   └── enrichment/
│       │
│       ├── methods/                        # Métodos de análisis
│       │   ├── __init__.py
│       │   ├── text_mining/
│       │   ├── causal/
│       │   ├── financial/
│       │   └── governance/
│       │
│       ├── orchestration/                  # Orquestación
│       │   ├── __init__.py
│       │   ├── factory/
│       │   ├── executor/
│       │   └── policies/
│       │
│       ├── models/                         # Modelos de datos
│       │   ├── __init__.py
│       │   ├── phase1_models.py
│       │   ├── phase2_models.py
│       │   └── contracts/
│       │
│       ├── # =========================================
│       ├── # FASES DEL PIPELINE
│       ├── # =========================================
│       ├── phases/                          # Fases 0-9
│       │   ├── __init__.py
│       │   ├── README.md                   # Overview fases
│       │   │
│       │   ├── Phase_00/                   # Fase 0: Ingestión
│       │   │   ├── __init__.py
│       │   │   ├── README.md
│       │   │   ├── phase0_executor.py
│       │   │   └── docs/
│       │   │       ├── phase0_spec.md
│       │   │       └── phase0_api.md
│       │   │
│       │   ├── Phase_01/                   # Fase 1: Preprocesamiento
│       │   │   ├── __init__.py
│       │   │   ├── README.md
│       │   │   ├── sp0_language.py
│       │   │   ├── sp1_preprocessing.py
│       │   │   ├── sp2_structural.py       # Usa pdm/integration
│       │   │   ├── sp3_kg.py
│       │   │   ├── sp4_segmentation.py     # Usa pdm/integration
│       │   │   ├── sp5_causal.py
│       │   │   ├── sp6_integrated_causal.py
│       │   │   ├── sp7_arguments.py
│       │   │   ├── sp8_temporal.py
│       │   │   ├── sp9_causal_integration.py
│       │   │   ├── sp10_strategic.py
│       │   │   ├── sp11_smart_chunks.py
│       │   │   ├── sp12_sisas_irrigation.py
│       │   │   ├── sp13_cpp_packaging.py
│       │   │   ├── sp14_quality.py
│       │   │   ├── sp15_strategic_ranking.py
│       │   │   ├── phase1_executor.py
│       │   │   └── docs/
│       │   │       ├── phase1_spec.md
│       │   │       ├── phase1_api.md
│       │   │       └── phase1_pdm_integration.md
│       │   │
│       │   ├── Phase_02/                   # Fase 2: Ejecución
│       │   │   ├── __init__.py
│       │   │   ├── README.md
│       │   │   ├── factory.py               # Usa calibration/registry
│       │   │   ├── task_executor.py         # Usa calibration N1
│       │   │   ├── evidence_nexus.py        # Usa calibration N2
│       │   │   ├── base_executor.py         # Usa calibration N3
│       │   │   ├── contracts/
│       │   │   └── docs/
│       │   │       ├── phase2_spec.md
│       │   │       ├── phase2_api.md
│       │   │       └── phase2_calibration_integration.md
│       │   │
│       │   └── Phase_03_through_09/        # Fases 3-9
│       │       └── ...
│       │
│       └── utils/                          # Utilidades compartidas
│           ├── __init__.py
│           ├── logging.py
│           ├── validation.py
│           └── ...
│
├── tests/                              # TESTS (mirror src/)
│   ├── __init__.py
│   ├── conftest.py                     # Config pytest compartida
│   │
│   ├── calibration/                    # Tests de calibración
│   │   ├── __init__.py
│   │   ├── test_epistemic_integrity.py
│   │   ├── test_calibration_registry.py
│   │   ├── test_pdm_rules.py
│   │   └── test_type_configs.py
│   │
│   ├── pdm/                            # Tests de PDM
│   │   ├── __init__.py
│   │   ├── test_structural_profile.py
│   │   ├── test_pdm_contracts.py
│   │   ├── test_pdm_integration.py
│   │   └── test_pdm_calibrator.py
│   │
│   ├── infrastructure/                 # Tests de infra
│   │   └── ...
│   │
│   ├── phases/                         # Tests por fase
│   │   ├── __init__.py
│   │   ├── test_phase_01/
│   │   │   ├── __init__.py
│   │   │   ├── test_sp0.py
│   │   │   ├── test_sp2.py
│   │   │   ├── test_sp4.py
│   │   │   └── ...
│   │   ├── test_phase_02/
│   │   │   ├── __init__.py
│   │   │   ├── test_factory.py
│   │   │   ├── test_task_executor.py
│   │   │   └── ...
│   │   └── test_phase_03_through_09/
│   │       └── ...
│   │
│   └── integration/                   # Tests integración
│       ├── __init__.py
│       ├── test_calibration_pdm_integration.py
│       └── test_end_to_end.py
│
├── artifacts/                          # ARTIFACTOS GENERADOS
│   ├── logs/
│   ├── checkpoints/
│   └── reports/
│
└── scripts/                            # SCRIPTS DE UTILIDAD
    ├── migrate_to_new_structure.py   # Script migración
    ├── validate_structure.py          # Validar estructura
    └── generate_docs.py               # Generar documentación
```

---

## 🔄 PLAN DE MIGRACIÓN

### Fase 1: Preparación (1-2 días)
1. Crear estructura de directorios nueva
2. Crear script de migración automatizada
3. Backup completo del repositorio

### Fase 2: Migración Sistema Calibración (2-3 días)
1. Mover `/infrastructure/calibration/` → `/calibration/`
2. Consolidar configs desde `/config/` → `/calibration/config/`
3. Actualizar imports en todos los archivos
4. Ejecutar tests de calibración

### Fase 3: Migración PDM (2-3 días)
1. Mover `/infrastructure/parametrization/` → `/pdm/`
2. Mover `/infrastructure/contractual/pdm_contracts.py` → `/pdm/contracts/`
3. Actualizar integraciones Phase 1
4. Ejecutar tests PDM

### Fase 4: Reorganización Fases (3-4 días)
1. Renombrar `Phase_X` → `Phase_XX` (dos dígitos)
2. Crear estructura docs/ en cada fase
3. Mover archivos a ubicaciones correctas
4. Actualizar todos los imports

### Fase 5: Reorganización Tests (2 días)
1. Crear estructura mirror de src/
2. Mover tests a ubicaciones correctas
3. Actualizar imports en tests
4. Ejecutar suite completa

### Fase 6: Documentación Centralizada (3-4 días)
1. Crear `/docs/` centralizado
2. Mover documentación desde fases
3. Crear índice principal
4. Generar API docs automáticamente

### Fase 7: Validación Final (2 días)
1. Ejecutar suite completa de tests
2. Validar que todos los imports funcionan
3. Verificar documentación completa
4. Limpiar archivos obsoletos

**TOTAL ESTIMADO**: 15-20 días

---

## 📋 CONVENCIONES DE NOMBRES UNIFICADAS

### Directorios
- **Fases**: `Phase_XX` (dos dígitos, cero-padding)
- **Paquetes**: `snake_case` (todo minúsculas con guiones bajos)
- **Tests**: `test_*.py` prefijo

### Archivos Python
- **Módulos**: `snake_case.py`
- **Clases**: `PascalCase`
- **Funciones**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`

### Archivos de Configuración JSON
- **Niveles**: `n{n}_{role}.json` (ej: `n1_empirical.json`)
- **Tipos**: `{type}.json` (ej: `type_a.json`)
- **Reglas**: `{context}_{rules}.json` (ej: `pdm_master_config.json`)

### Documentación
- **Principal**: `TITLE.md` (UPPER_SNAKE_CASE)
- **Secciones**: `## Title` (Markdown)
- **Código**: ````python``` bloques

---

## 🏷️ ETIQUETADO DE ARCHIVOS

### Metadata en Archivos Python
```python
"""
[Módulo/Componente]

Breve descripción del componente.

EPISTEMIC LEVEL: N0-N4
OUTPUT TYPE: PARAMETER/CONSTRAINT/FACT
FUSION BEHAVIOR: multiplicative/additive/gate

Architecture Layers:
    Layer 0: Global Defaults
    Layer 1: Level Determination
    Layer 2: Level Defaults
    Layer 3: Type Overrides
    Layer 4: PDM Adjustments

Constitutional Constraints:
    - CI-01: 300 contracts
    - CI-02: Zero legacy classes
    - CI-03: Level immutability
    - CI-04: N3 asymmetry
    - CI-05: PDM preserves level

Author: FARFAN Engineering Team
Version: X.Y.Z
Created: YYYY-MM-DD
Modified: YYYY-MM-DD
"""
```

### Etiquetas en Documentos Markdown
```markdown
# [Título]

**Nivel Epistémico**: N1-EMP
**Última Actualización**: 2026-01-15
**Versión**: 1.0.0
**Estado**: Production Ready

## Índice
1. [Descripción](#descripción)
2. [Arquitectura](#arquitectura)
3. [Uso](#uso)
```

---

## 📊 MÉTRICAS DE ÉXITO

### Antes (Estado Actual)
- ✅ Archivos fuente: Organizados funcionalmente
- ⚠️ Calibración: Fragmentada en 3 locaciones
- ⚠️ PDM: Disperso entre infrastructure/
- ⚠️ Documentación: 9+ locaciones diferentes
- ⚠️ Tests: No mirror completo con src/
- ⚠️ Naming: Inconsistente (Phase_X vs phaseX)

### Después (Objetivo)
- ✅ Archivos fuente: Organizados por capas epistémicas
- ✅ Calibración: Consolidada en `/calibration/`
- ✅ PDM: Consolidado en `/pdm/`
- ✅ Documentación: Centralizada en `/docs/`
- ✅ Tests: Mirror perfecto con src/
- ✅ Naming: 100% consistente

---

## 🎯 PRÓXIMOS PASOS

1. **Revisar este plan** con el equipo
2. **Aprobar estructura final**
3. **Crear script de migración**
4. **Ejecutar migración por fases**
5. **Validar exhaustivamente**
6. **Documentar cambios**
7. **Limpiar estructura vieja**

---

**APROBADO POR**: [Pendiente]
**FECHA DE REVISIÓN**: [Pendiente]
**FECHA DE EJECUCIÓN ESTIMADA**: [Pendiente]
