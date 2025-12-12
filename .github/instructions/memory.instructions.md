---
applyTo: '**'
description: Workspace-specific AI memory for this project
lastOptimized: '2025-12-12T07:43:02.812943+00:00'
entryCount: 2
optimizationVersion: 1
autoOptimize: true
sizeThreshold: 50000
entryThreshold: 20
timeThreshold: 7
---
# Workspace AI Memory
This file contains workspace-specific information for AI conversations.

## Universal Laws
- **CRITICAL SYNCHRONIZATION RULE (2025-12-12 02:42):** `METHODS_TO_QUESTIONS_AND_FILES.json` contains 240 methods. `METHODS_OPERACIONALIZACION.json` MUST contain the same 240 methods. Always verify both files are synchronized. Never create partial files.

## Memories/Facts
- **2025-12-12 02:42:** The 240 dispensary methods map to Q001-Q030 (base questions) × 10 Policy Areas = 300 contracts. Mapping files use base questions; contracts expand to Q001-Q300.- **2025-12-12 02:43:** ARQUITECTURA F.A.R.F.A.N: 40 clases en class_registry.py mapean a methods_dispensary/*.py. MethodRegistry usa lazy loading - clases se instancian solo cuando get_method() es llamado. 300 contratos JSON en executor_contracts/specialized/ definen method_binding.methods[]. Los contratos expanden Q001-Q030 a Q001-Q300 (30 preguntas × 10 Policy Areas).
- **2025-12-12 02:43:** ARCHIVOS CRÍTICOS SINCRONIZADOS: METHODS_TO_QUESTIONS_AND_FILES.json y METHODS_OPERACIONALIZACION.json DEBEN tener exactamente los mismos 240 métodos. El primero tiene file/questions/dimensions, el segundo agrega operacionalizacion con tipo_valor/formato_entrada/formato_salida/calculo/parametros.
- **2025-12-12 02:43:** El usuario se llama [nombre del proyecto F.A.R.F.A.N]. Usa Python 3.12, FastAPI, Pydantic, sentence-transformers. Prefiere NO hacer archivos parciales o incompletos. Verificar SIEMPRE conteos antes y después de operaciones. El usuario es muy exigente con la precisión y consistencia de datos.
