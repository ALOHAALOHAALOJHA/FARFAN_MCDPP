# SISAS DEPURACIÓN RADICAL - PLAN DE REORGANIZACIÓN
## Análisis de Implementaciones Duplicadas y Obsoletas
## Fecha: 2026-01-14

---

## 🔍 DIAGNÓSTICO: DUPLICACIONES DETECTADAS

### 1. **DUPLICACIONES CRÍTICAS (SISAS raíz vs vehicles/)**

Archivos duplicados entre raíz SISAS y vehicles/:

```
❌ DUPLICADOS - ELIMINAR DE RAÍZ:
./SISAS/signal_context_scoper.py        → MOVER A vehicles/signal_context_scoper.py ✅
./SISAS/signal_irrigator.py             → MOVER A vehicles/signal_irrigator.py ✅
./SISAS/signal_registry.py              → MOVER A vehicles/signal_registry.py ✅
./SISAS/signals.py                      → MOVER A vehicles/signals.py ✅
./SISAS/signal_loader.py                → MOVER A vehicles/signal_loader.py ✅
./SISAS/signal_enhancement_integrator.py → MOVER A vehicles/signal_enhancement_integrator.py ✅
./SISAS/signal_quality_metrics.py       → MOVER A vehicles/signal_quality_metrics.py ✅
./SISAS/signal_evidence_extractor.py    → MOVER A vehicles/signal_evidence_extractor.py ✅
./SISAS/signal_intelligence_layer.py    → MOVER A vehicles/signal_intelligence_layer.py ✅
```

### 2. **ARCHIVOS EN RAÍZ SISAS QUE NECESITAN ORGANIZACIÓN**

```
❌ DESORGANIZADOS - REUBICAR:
./SISAS/signal_scoring_context.py       → utils/ o helpers/
./SISAS/signal_resolution.py            → utils/
./SISAS/signal_consumption_integration.py → integration/
./SISAS/signal_consumption.py           → deprecated/ (reemplazado por consumers/)
./SISAS/signal_semantic_context.py      → utils/ o semantic/
./SISAS/signal_semantic_expander.py     → semantic/
./SISAS/signal_wiring_fixes.py          → deprecated/ (fixes ya aplicados)
./SISAS/signal_types.py                 → deprecated/ (reemplazado por signals/types/)
./SISAS/signal_validation_specs.py      → validators/
./SISAS/signal_method_metadata.py       → metadata/
```

### 3. **IMPLEMENTACIONES EN phases/ - LEGACY vs SISAS**

```
⚠️ LEGACY (No usar - mantener para compatibilidad):
./phases/Phase_01/phase1_11_00_signal_enrichment.py
./phases/Phase_03/phase3_10_00_phase3_signal_enriched_scoring.py
./phases/Phase_08/phase8_30_00_signal_enriched_recommendations.py
./phases/Phase_04/signal_enriched_aggregation.py
./phases/Phase_09/phase9_10_00_signal_enriched_reporting.py

✅ PRODUCCIÓN (usar desde SISAS):
./SISAS/consumers/phase1/phase1_11_00_signal_enrichment.py
./SISAS/consumers/phase3/phase3_10_00_signal_enriched_scoring.py
./SISAS/consumers/phase8/phase8_30_00_signal_enriched_recommendations.py
```

### 4. **OTROS ARCHIVOS SIGNAL-RELATED**

```
./infrastructure/irrigation_using_signals/comprehensive_signal_audit.py  → audits/
./infrastructure/irrigation_using_signals/audit_signal_irrigation.py     → audits/
./dashboard_atroz_/signals_service.py                                    → LEGACY
./dashboard_atroz_/signal_extraction_sota.py                             → LEGACY
```

---

## 📁 ESTRUCTURA FINAL PROPUESTA (POST-DEPURACIÓN)

```
src/farfan_pipeline/infrastructure/irrigation_using_signals/
└── SISAS/  ⭐ SISTEMA PRODUCTIVO FINAL
    ├── __init__.py
    ├── main.py
    │
    ├── core/                          ✅ CERTIFICADO (4 archivos)
    │   ├── __init__.py
    │   ├── signal.py                  ✅ INMUTABLE
    │   ├── event.py                   ✅ ARCHIVE (no delete)
    │   ├── contracts.py               ✅
    │   └── bus.py                     ✅
    │
    ├── signals/                       ✅ CERTIFICADO
    │   ├── __init__.py
    │   └── types/                     ✅ 6 categorías
    │       ├── __init__.py
    │       ├── structural.py          ✅
    │       ├── integrity.py           ✅
    │       ├── epistemic.py           ✅
    │       ├── contrast.py            ✅
    │       ├── operational.py         ✅
    │       └── consumption.py         ✅
    │
    ├── vehicles/                      ✅ CERTIFICADO (10 vehículos)
    │   ├── __init__.py
    │   ├── base_vehicle.py            ✅
    │   ├── signal_registry.py         ✅
    │   ├── signal_context_scoper.py   ✅
    │   ├── signal_evidence_extractor.py ✅
    │   ├── signal_enhancement_integrator.py ✅
    │   ├── signal_intelligence_layer.py ✅
    │   ├── signal_irrigator.py        ✅
    │   ├── signal_loader.py           ✅
    │   ├── signal_quality_metrics.py  ✅
    │   ├── signal_registry.py         ✅
    │   └── signals.py                 ✅
    │
    ├── consumers/                     ✅ CERTIFICADO (18 consumers)
    │   ├── __init__.py
    │   ├── base_consumer.py           ✅
    │   ├── phase0/                    ✅ 3 consumidores
    │   ├── phase1/                    ✅ 2 consumidores
    │   ├── phase2/                    ✅ 4 consumidores
    │   ├── phase3/                    ✅ 1 consumidor
    │   ├── phase7/                    ✅ 1 consumidor
    │   └── phase8/                    ✅ 1 consumidor
    │
    ├── irrigation/                    ✅ CERTIFICADO
    │   ├── __init__.py
    │   ├── irrigation_map.py          ✅
    │   └── irrigation_executor.py     ✅
    │
    ├── vocabulary/                    ✅ CERTIFICADO
    │   ├── __init__.py
    │   ├── signal_vocabulary.py       ✅
    │   ├── capability_vocabulary.py   ✅
    │   └── alignment_checker.py       ✅
    │
    ├── config/                        ✅ CERTIFICADO
    │   ├── __init__.py
    │   ├── bus_config.yaml            ✅ 7 buses
    │   └── irrigation_config.yaml     ✅
    │
    ├── schemas/                       ✅ CERTIFICADO
    │   ├── __init__.py
    │   ├── signal_schema.json         ✅
    │   ├── event_schema.json          ✅
    │   ├── contract_schema.json       ✅
    │   └── irrigation_spec_schema.json ✅
    │
    ├── scripts/                       ✅ CERTIFICADO
    │   ├── __init__.py
    │   └── generate_contracts.py      ✅
    │
    ├── audit/                         ✅ CERTIFICADO
    │   ├── __init__.py
    │   ├── signal_auditor.py          ✅
    │   ├── contrast_auditor.py        ✅
    │   └── alignment_auditor.py       ✅
    │
    ├── utils/                         🆕 NUEVO
    │   ├── __init__.py
    │   ├── signal_scoring_context.py  ← MOVIDO
    │   ├── signal_resolution.py       ← MOVIDO
    │   ├── signal_semantic_context.py ← MOVIDO
    │   └── signal_validation_specs.py ← MOVIDO
    │
    ├── semantic/                      🆕 NUEVO
    │   ├── __init__.py
    │   └── signal_semantic_expander.py ← MOVIDO
    │
    ├── integration/                   🆕 NUEVO
    │   ├── __init__.py
    │   └── signal_consumption_integration.py ← MOVIDO
    │
    ├── metadata/                      🆕 NUEVO
    │   ├── __init__.py
    │   └── signal_method_metadata.py  ← MOVIDO
    │
    └── _deprecated/                   🆕 NUEVO (LEGACY)
        ├── signal_consumption.py      ← LEGACY
        ├── signal_types.py            ← LEGACY (reemplazado)
        ├── signal_wiring_fixes.py     ← LEGACY (fixes aplicados)
        └── README_DEPRECATED.md       ← Explicación

phases/  ⚠️ LEGACY (mantener para compatibilidad, no modificar)
└── _LEGACY_SIGNAL_IMPLEMENTATIONS.md  ← Documento explicativo

examples/
└── sisas_signal_delivery_demo.py     ✅ ACTUALIZAR imports

tests/
├── test_sisas/                        ✅ CERTIFICADO
└── signals/                           ⚠️ LEGACY o duplicado
```

---

## 🎯 ACCIONES DE DEPURACIÓN

### FASE 1: REORGANIZACIÓN INTERNA SISAS ✅

**1.1 Crear directorios nuevos:**
```bash
mkdir -p SISAS/utils
mkdir -p SISAS/semantic
mkdir -p SISAS/integration
mkdir -p SISAS/metadata
mkdir -p SISAS/_deprecated
```

**1.2 Mover archivos de raíz a módulos:**
```bash
# Utils
mv SISAS/signal_scoring_context.py SISAS/utils/
mv SISAS/signal_resolution.py SISAS/utils/
mv SISAS/signal_semantic_context.py SISAS/utils/
mv SISAS/signal_validation_specs.py SISAS/utils/

# Semantic
mv SISAS/signal_semantic_expander.py SISAS/semantic/

# Integration
mv SISAS/signal_consumption_integration.py SISAS/integration/

# Metadata
mv SISAS/signal_method_metadata.py SISAS/metadata/

# Deprecated
mv SISAS/signal_consumption.py SISAS/_deprecated/
mv SISAS/signal_types.py SISAS/_deprecated/
mv SISAS/signal_wiring_fixes.py SISAS/_deprecated/
```

**1.3 Eliminar duplicados de raíz (ya están en vehicles/):**
```bash
rm SISAS/signal_context_scoper.py
rm SISAS/signal_irrigator.py
rm SISAS/signal_registry.py
rm SISAS/signals.py
rm SISAS/signal_loader.py
rm SISAS/signal_enhancement_integrator.py
rm SISAS/signal_quality_metrics.py
rm SISAS/signal_evidence_extractor.py
rm SISAS/signal_intelligence_layer.py
```

### FASE 2: MARCAJE LEGACY ⚠️

**2.1 Crear documento explicativo en phases/:**
```markdown
# LEGACY_SIGNAL_IMPLEMENTATIONS.md

⚠️ **ESTAS IMPLEMENTACIONES SON LEGACY**

NO USAR para nuevos desarrollos.
Mantenidas solo para compatibilidad con código existente.

**USAR EN SU LUGAR:**
- SISAS/consumers/phase1/phase1_11_00_signal_enrichment.py
- SISAS/consumers/phase3/phase3_10_00_signal_enriched_scoring.py
- SISAS/consumers/phase8/phase8_30_00_signal_enriched_recommendations.py

**SISTEMA PRODUCTIVO:** `SISAS/` (100% certificado)
```

**2.2 Agregar warnings en archivos legacy:**
```python
# Al inicio de cada archivo legacy en phases/
"""
⚠️ LEGACY IMPLEMENTATION - DO NOT USE

This is a legacy implementation maintained for backward compatibility.

PRODUCTION SYSTEM:
Use SISAS/consumers/phase{N}/ instead.

See: LEGACY_SIGNAL_IMPLEMENTATIONS.md
"""
```

### FASE 3: ACTUALIZACIÓN DE IMPORTS 🔄

**3.1 Actualizar imports en archivos que usen los módulos movidos:**
```python
# ANTES:
from SISAS.signal_scoring_context import ...

# DESPUÉS:
from SISAS.utils.signal_scoring_context import ...
```

**3.2 Actualizar examples/sisas_signal_delivery_demo.py**

### FASE 4: SELLADO DE PATHS 🔒

**4.1 Crear __init__.py en cada nuevo módulo**
**4.2 Agregar deprecation warnings donde corresponda**
**4.3 Documentar exports públicos vs internos**

### FASE 5: DOCUMENTACIÓN 📚

**5.1 Generar SYSTEM_INVENTORY.md**
**5.2 Actualizar matrix_sabana.csv**
**5.3 Crear MIGRATION_GUIDE.md**

---

## 🚨 ARCHIVOS A ELIMINAR (PURGA)

```bash
# Duplicados confirmados (ya en vehicles/)
./SISAS/signal_context_scoper.py
./SISAS/signal_irrigator.py
./SISAS/signal_registry.py
./SISAS/signals.py
./SISAS/signal_loader.py
./SISAS/signal_enhancement_integrator.py
./SISAS/signal_quality_metrics.py
./SISAS/signal_evidence_extractor.py
./SISAS/signal_intelligence_layer.py
```

---

## ✅ RESULTADO ESPERADO

**ANTES:**
- 50+ archivos signal-related distribuidos en múltiples ubicaciones
- Duplicaciones entre raíz y vehicles/
- Implementaciones legacy mezcladas con productivo
- Confusión sobre qué versión usar

**DESPUÉS:**
- Estructura clara en SISAS/ (certificada 100%)
- Sin duplicaciones
- Legacy claramente marcado y separado
- Documentación completa del sistema
- Matrix actualizada

---

## 📊 IMPACTO

| Categoría | Antes | Después | Cambio |
|-----------|-------|---------|--------|
| Archivos signal-related | ~50 | ~45 | -5 duplicados |
| Directorios SISAS | 10 | 14 | +4 organizados |
| Archivos en raíz SISAS | 15 | 1 (main.py) | -14 reorganizados |
| Archivos legacy marcados | 0 | 10+ | +10 advertencias |
| Documentación | Parcial | Completa | +3 docs |

---

## 🎯 PRIORIDAD DE EJECUCIÓN

1. **CRÍTICO:** Eliminar duplicados (Fase 1.3)
2. **ALTO:** Reorganizar archivos (Fase 1.2)
3. **MEDIO:** Marcar legacy (Fase 2)
4. **BAJO:** Actualizar imports (Fase 3)
5. **INFO:** Documentación (Fase 5)

---

**Este plan garantiza:**
- ✅ Una sola fuente de verdad (SISAS/)
- ✅ Sin duplicaciones ni confusiones
- ✅ Legacy claramente separado
- ✅ Documentación completa
- ✅ Sistema listo para producción
