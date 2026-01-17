# ⚠️ DEPRECATED MODULES

## Archivos en este directorio son LEGACY y NO deben usarse

**Fecha de depuración:** 2026-01-14

---

## 📁 Archivos Deprecados

### 1. `signal_consumption.py`
**Razón:** Reemplazado por el sistema modular de consumers/
**Usar en su lugar:**
```python
from SISAS.consumers.base_consumer import BaseConsumer
from SISAS.consumers.phase1.phase1_11_00_signal_enrichment import SignalEnrichmentConsumer
```

### 2. `signal_types.py`
**Razón:** Reemplazado por signals/types/ con 6 categorías estructuradas
**Usar en su lugar:**
```python
from SISAS.signals.types.structural import StructuralAlignmentSignal
from SISAS.signals.types.integrity import EventPresenceSignal
from SISAS.signals.types.epistemic import AnswerDeterminacySignal
# etc.
```

### 3. `signal_wiring_fixes.py`
**Razón:** Fixes ya aplicados en la versión productiva
**Nota:** Los fixes de wiring están integrados en core/bus.py y core/contracts.py

---

## ⚠️ NO MODIFICAR ESTOS ARCHIVOS

Estos archivos se mantienen solo para:
- Referencia histórica
- Compatibilidad temporal con código legacy
- Análisis de evolución del sistema

---

## ✅ SISTEMA PRODUCTIVO

**Usar:** `SISAS/` - Sistema certificado 100% para producción

**Estructura:**
- `core/` - Signal, Event, Contracts, Bus
- `signals/types/` - 6 categorías de señales
- `vehicles/` - 10 vehículos de transporte
- `consumers/` - 18 consumidores por fase
- `irrigation/` - Sistema de irrigación
- `vocabulary/` - Vocabularios y alignment
- `config/` - Configuración de buses
- `schemas/` - Schemas JSON

---

**Ver:** `SISAS_CERTIFICATION_PACK.md` para audit completo
