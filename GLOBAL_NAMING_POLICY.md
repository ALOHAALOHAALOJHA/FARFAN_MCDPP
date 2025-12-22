# POLÍTICA GLOBAL DE NOMENCLATURA JERÁRQUICA F.A.R.F.A.N

**Documento:** FPN-GLOBAL-001  
**Versión:** 1.0.0  
**Fecha:** 2025-12-21  
**Estado:** AUTORITATIVO  
**Alcance:** Todos los artefactos del F.A.R.F.A.N Pipeline

---

## TABLA DE CONTENIDOS

1. [Propósito y Alcance](#1-propósito-y-alcance)
2. [Principios Universales](#2-principios-universales)
3. [Arquitectura de Nomenclatura](#3-arquitectura-de-nomenclatura)
4. [Políticas por Categoría de Artefacto](#4-políticas-por-categoría-de-artefacto)
5. [Jerarquía de Directorios](#5-jerarquía-de-directorios)
6. [Políticas de Almacenamiento](#6-políticas-de-almacenamiento)
7. [Sistema de Etiquetado](#7-sistema-de-etiquetado)
8. [Artefactos Fuera de Fases Canónicas](#8-artefactos-fuera-de-fases-canónicas)
9. [Validación y Compliance](#9-validación-y-compliance)
10. [Mantenimiento y Gobernanza](#10-mantenimiento-y-gobernanza)

---

## 1. PROPÓSITO Y ALCANCE

### 1.1 Objetivos Estratégicos

Esta política establece el **sistema universal de nomenclatura, organización y almacenamiento** para todos los artefactos del ecosistema F.A.R.F.A.N, garantizando:

- **Trazabilidad Total:** Cada artefacto debe autodescribir su propósito, origen, fase y criticidad
- **Higiene Extrema:** Zero tolerancia a archivos huérfanos, duplicados o mal clasificados
- **Escalabilidad Determinística:** Sistema preparado para 10x crecimiento sin refactorización
- **Auditoría Continua:** Compliance automático verificable en CI/CD
- **Onboarding Instantáneo:** Cualquier ingeniero debe entender la estructura en <10 minutos

### 1.2 Alcance Total

**INCLUYE:**
- ✅ Código fuente Python (fases 0-9, infraestructura, utilidades)
- ✅ Contratos JSON (executor_contracts, templates, schemas)
- ✅ Documentación (técnica, auditorial, executiva)
- ✅ Scripts auxiliares (validación, transformación, deployment)
- ✅ Artefactos de ejecución (logs, traces, reports, metrics)
- ✅ Configuración (YAML, TOML, INI, ENV)
- ✅ Tests (unitarios, integración, end-to-end)
- ✅ Assets multimedia (diagramas, visualizaciones, dashboards)

**EXCLUYE:**
- ❌ Entornos virtuales (`*-env/`, `venv/`)
- ❌ Cachés de build (`.pytest_cache/`, `__pycache__/`)
- ❌ Datos sensibles o credenciales
- ❌ Dependencias externas (`node_modules/`, `.venv/`)

### 1.3 Autoridad y Precedencia

Este documento es **LA ÚNICA FUENTE AUTORITATIVA** para nomenclatura global. En caso de conflicto:

1. **FPN-GLOBAL-001** (este documento) tiene precedencia absoluta
2. Políticas específicas de fase (ej. FPN-P2-001) extienden pero NO contradicen esta política
3. Cualquier desviación requiere:
   - Aprobación del comité técnico
   - Justificación documentada en ADR (Architecture Decision Record)
   - Actualización formal con versión semántica incrementada

---

## 2. PRINCIPIOS UNIVERSALES

### 2.1 Axioma de Autodescripción

```
AXIOMA: El nombre de cualquier artefacto debe comunicar CLARAMENTE:
  - Qué es (tipo)
  - Para qué sirve (propósito)
  - Dónde vive (jerarquía)
  - Cuándo se usa (fase/ciclo de vida)
```

**Ejemplos de cumplimiento:**
- ✅ `phase2_60_02_arg_router.py` → Fase 2, etapa 60, orden 02, enruta argumentos
- ✅ `Q005_contract_validation_report.json` → Reporte de validación del contrato Q005
- ✅ `AUDIT_EXECUTOR_CONTRACTS_V3_Q001_Q020_EXECUTIVE_SUMMARY.md` → Resumen ejecutivo de auditoría de contratos Q001-Q020 versión 3

**Ejemplos de violación:**
- ❌ `temp.py` → Sin contexto
- ❌ `utils.json` → Demasiado genérico
- ❌ `fix_v2_final_FINAL.py` → Caótico, no versionado

### 2.2 Principio de Inmutabilidad de Identidad

Una vez asignado un **identificador canónico** (número de fase, etapa, orden, código de contrato, etc.), **NUNCA SE REASIGNA**:

- Los números son permanentes en logs, trazas, métricas
- La deprecación NO libera el número para reutilización
- Se mantiene mapping histórico en `MIGRATION_MAP.json`

### 2.3 Principio de Minimalismo Radical

```
REGLA: Ningún artefacto debe existir sin propósito activo documentado.
```

**Acciones obligatorias:**
- Archivos experimentales → `experimental/` con fecha de expiración
- Código legacy → `archive/` con timestamp
- Duplicados → Eliminar sin excepción
- Archivos sin uso en 90 días → Auditoría de relevancia

### 2.4 Principio de Jerarquía Determinística

La estructura de directorios refleja la **arquitectura del sistema**, no preferencias personales:

```
BUENA JERARQUÍA: src/ → farfan_pipeline/ → phases/ → Phase_two/ → phase2_*.py
MALA JERARQUÍA: my_code/ → stuff/ → phase2_v3/ → file.py
```

### 2.5 Principio de Compliance por Defecto

Todos los artefactos nuevos deben:
- Pasar validación automática antes de commit (pre-commit hooks)
- Incluir metadatos mínimos (autor, fecha, versión, propósito)
- Seguir convenciones de estilo (ruff, black, mypy)
- Documentar desviaciones explícitamente

---

## 3. ARQUITECTURA DE NOMENCLATURA

### 3.1 Sistema de Prefijos Globales

| Prefijo | Alcance | Formato | Ejemplo |
|---------|---------|---------|---------|
| `phase[0-9]_` | Código de fases | `phase{N}_*` | `phase2_60_02_arg_router.py` |
| `Q[0-9]{3}_` | Contratos/preguntas | `Q{NNN}_*` | `Q005_executor_contract.json` |
| `FPN-` | Documentos de política | `FPN-{SCOPE}-{NNN}` | `FPN-GLOBAL-001.md` |
| `AUDIT_` | Reportes de auditoría | `AUDIT_{TOPIC}_*` | `AUDIT_EXECUTOR_METHODS.md` |
| `BATCH[0-9]+_` | Evaluaciones por lote | `BATCH{N}_*` | `BATCH_8_FINAL_SUMMARY.md` |
| `CQVR_` | Evaluaciones CQVR | `CQVR_*` | `CQVR_EVALUATION_RESULTS.json` |
| `PHASE_[0-9]_` | Docs de fase | `PHASE_{N}_*` | `PHASE_0_AUDIT_REPORT.md` |

### 3.2 Convenciones de Sufijos

| Sufijo | Propósito | Extensiones | Ejemplos |
|--------|-----------|-------------|----------|
| `_SUMMARY` | Resúmenes ejecutivos | `.md`, `.txt` | `IMPLEMENTATION_SUMMARY.md` |
| `_REPORT` | Reportes detallados | `.md`, `.json` | `audit_contracts_report.json` |
| `_SPEC` | Especificaciones técnicas | `.md` | `Technical_Specification_Contract_Loader.md` |
| `_PLAN` | Planes de acción | `.md` | `ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md` |
| `_GUIDE` | Guías de usuario | `.md` | `TEST_EXECUTION_GUIDE.md` |
| `_INDEX` | Índices/catálogos | `.md`, `.json` | `CONTRACT_AUDIT_INDEX.md` |
| `_TRACKING` | Seguimiento de métricas | `.md`, `.json` | `CQVR_IMPROVEMENT_TRACKING.md` |
| `_MAP` | Mapeos/correspondencias | `.json`, `.txt` | `import_map.txt` |

### 3.3 Reglas de Case Convention

| Contexto | Convención | Regex | Ejemplo |
|----------|------------|-------|---------|
| Código Python (módulos) | `snake_case` | `^[a-z][a-z0-9_]+\.py$` | `arg_router.py` |
| Código Python (clases) | `PascalCase` | `^[A-Z][a-zA-Z0-9]+$` | `ArgRouter` |
| Código Python (funciones) | `snake_case` | `^[a-z][a-z0-9_]+$` | `route_arguments()` |
| Contratos JSON | `snake_case` | `^Q[0-9]{3}_[a-z][a-z0-9_]+\.json$` | `Q005_executor_contract.json` |
| Documentación | `UPPER_SNAKE_CASE` | `^[A-Z][A-Z0-9_]+\.md$` | `AUDIT_REPORT.md` |
| Scripts auxiliares | `snake_case` | `^[a-z][a-z0-9_]+\.(py\|sh)$` | `validate_contracts.py` |
| Configuración | `lowercase` o `kebab-case` | Varía por tool | `pyproject.toml`, `.pre-commit-config.yaml` |

---

## 4. POLÍTICAS POR CATEGORÍA DE ARTEFACTO

### 4.1 Código Fuente Python - Módulos de Fases Canónicas

#### 4.1.1 Arquitectura de Fases y Etapas

Cada fase tiene su propia **taxonomía de etapas temporales** que reflejan su flujo de procesamiento específico. El sistema de numeración de etapas es **específico por fase**, no global.

**Formato Canónico Universal:**
```
phase{N}_{ETAPA}_{ORDEN}_{nombre_descriptivo}.py
```

**Componentes:**
- `{N}`: Número de fase [0-9]
- `{ETAPA}`: Identificador de etapa temporal [00-99], **específico de cada fase**
- `{ORDEN}`: Posición dentro de etapa [00-99], refleja dependencias/ejecución
- `{nombre_descriptivo}`: snake_case, max 32 chars, autoexplicativo

**Restricciones Técnicas (Universal):**
- RT-001: El prefijo `phase{N}_` es OBLIGATORIO e INMUTABLE
- RT-002: ETAPA y ORDEN deben ser integers de EXACTAMENTE 2 DÍGITOS (con leading zero)
- RT-003: El separador entre ETAPA y ORDEN es UNDERSCORE (_), no punto ni guión
- RT-004: El nombre_descriptivo debe usar snake_case estricto (minúsculas, underscores, sin números al inicio)
- RT-005: La longitud total del nombre de archivo no debe exceder 64 caracteres (excluyendo extensión)
- RT-006: Caracteres permitidos en nombre_descriptivo: [a-z0-9_], sin caracteres especiales, espacios ni Unicode

**Regex de Validación:**
```python
PHASE_MODULE_PATTERN = re.compile(
    r'^phase(?P<fase>[0-9])_'
    r'(?P<etapa>\d{2})_(?P<orden>\d{2})_'
    r'(?P<nombre>[a-z][a-z0-9_]+)\.py$'
)
```

#### 4.1.2 Taxonomía de Etapas por Fase

Cada fase define su propio mapa de etapas temporales. A continuación, las taxonomías canónicas:

##### **PHASE 0: Validación y Hardening**

| Código | Nombre | Descripción | Cardinalidad | Tiempo |
|--------|--------|-------------|--------------|--------|
| 00 | Base Utilities | `__init__`, constantes | 1-3 | t=init |
| 10 | Schema Validation | Validadores de schemas JSON | 2-5 | t=0 |
| 20 | Contract Inspection | Inspección de contratos | 2-4 | t=1 |
| 30 | Wiring Validation | Validación de conexiones | 3-6 | t=2 |
| 40 | Invariant Checks | Verificación de invariantes | 2-5 | t=3 |
| 50 | Report Generation | Generación de reportes | 1-3 | t=4 |
| 90 | Integration | Integración con pipeline | 1-2 | t=5 |

**Etapas Reservadas Phase 0:** 60-89 (futuras validaciones especializadas)

**Ejemplo Phase 0:**
```python
# phase0_10_00_contract_schema_validator.py
# phase0_10_01_method_signature_validator.py
# phase0_30_00_orchestrator_wiring_checker.py
```

##### **PHASE 1: Ingestion y Parsing**

| Código | Nombre | Descripción | Cardinalidad | Tiempo |
|--------|--------|-------------|--------------|--------|
| 00 | Base Utilities | `__init__`, helpers | 1-3 | t=init |
| 10 | File Ingestion | Lectura de archivos fuente | 2-4 | t=0 |
| 20 | Format Detection | Detección de formatos | 1-3 | t=1 |
| 30 | Parser Selection | Selección de parser | 2-4 | t=2 |
| 40 | Content Extraction | Extracción de contenido | 3-6 | t=3 |
| 50 | Normalization | Normalización de datos | 2-5 | t=4 |
| 60 | Validation | Validación de integridad | 2-4 | t=5 |
| 90 | Bundle Creation | Creación de ProcessorBundle | 1-2 | t=6 |

**Etapas Reservadas Phase 1:** 70-89

##### **PHASE 2: Orchestration y Execution** ⭐

| Código | Nombre | Descripción | Cardinalidad | Tiempo |
|--------|--------|-------------|--------------|--------|
| 00 | Utilidades Base | `__init__`, helpers básicos | 1-5 | t=init |
| 09 | Utilidades Testing | Test suites, fixtures | 1-5 | t=test |
| 10 | Inicialización | Factory, registros, configuración | 4-8 | t=0 |
| 20 | Validación Estática | Validadores pre-ejecución | 2-6 | t=1 |
| 30 | Gestión de Recursos | Managers, alertas, wrappers | 3-8 | t=2 |
| 40 | Sincronización | ChunkMatrix, JOIN, ExecutionPlan | 4-8 | t=3 |
| 50 | Orquestación | TaskExecutor, planificadores | 2-4 | t=4 |
| 60 | Ejecución Loop | Ejecutores, validadores runtime | 6-12 | t=5-305 |
| 70 | **(RESERVADO)** | Futura capa de transformación | 0 | - |
| 80 | Análisis | EvidenceNexus, razonamiento causal | 1-3 | t=306 |
| 90 | Síntesis | Carver, renderizado narrativo | 1-3 | t=307 |
| 95 | Telemetría | Profiling, métricas, persistencia | 4-8 | t=1-307 |

**Principios específicos Phase 2:**
- **Gap Estratégico:** ETAPA 70 reservada para optimización futura
- **Parallelismo:** Solo ETAPA 95 (Telemetría) ejecuta en paralelo
- **Hotpath:** ETAPA 60 es CRÍTICA (300 iteraciones)
- **Singleton:** ETAPA 10 ejecuta UNA sola vez

**Ejemplo Phase 2:**
```python
# phase2_10_00_factory.py
# phase2_40_03_irrigation_synchronizer.py
# phase2_60_02_arg_router.py
# phase2_80_00_evidence_nexus.py
```

##### **PHASE 3: Semantic Analysis**

| Código | Nombre | Descripción | Cardinalidad | Tiempo |
|--------|--------|-------------|--------------|--------|
| 00 | Base Utilities | `__init__` | 1-2 | t=init |
| 10 | Tokenization | Tokenización de texto | 2-4 | t=0 |
| 20 | Embedding Generation | Generación de embeddings | 3-6 | t=1 |
| 30 | Semantic Clustering | Clustering semántico | 2-5 | t=2 |
| 40 | Entity Recognition | NER y entity linking | 3-7 | t=3 |
| 50 | Relationship Extraction | Extracción de relaciones | 2-5 | t=4 |
| 60 | Semantic Graph | Construcción de grafo | 2-4 | t=5 |
| 90 | Integration | Integración con pipeline | 1-2 | t=6 |

**Etapas Reservadas Phase 3:** 70-89

##### **PHASE 4-9: Taxonomías por Definir**

Para fases sin taxonomía establecida, usar estructura genérica:

| Código | Nombre | Propósito |
|--------|--------|-----------|
| 00 | Base | Inicialización mínima |
| 10 | Input Processing | Procesamiento de entrada |
| 20 | Validation | Validación |
| 30 | Transformation | Transformación principal |
| 40 | Analysis | Análisis |
| 50 | Output Generation | Generación de salida |
| 90 | Integration | Integración |

**IMPORTANTE:** Cada fase DEBE documentar su taxonomía de etapas en su `README.md` específico.

#### 4.1.3 Reglas de Asignación de Etapas (Universal)

**R-ETAPA-001:** Las etapas se asignan en **múltiplos de 10** para maximizar gaps estratégicos.

**R-ETAPA-002:** Etapas 01-08 están **RESERVADAS** para micro-etapas futuras (excepto 09 para testing).

**R-ETAPA-003:** Cada fase puede definir **hasta 10 etapas principales** (00, 10, 20, ..., 90).

**R-ETAPA-004:** La etapa 70 es tradicionalmente **RESERVADA** para optimización/transformación intermedia.

**R-ETAPA-005:** Telemetría/observabilidad típicamente usa **ETAPA 95** (ejecución paralela).

#### 4.1.4 Reglas de Asignación de Orden (Universal)

**R-ORDEN-001:** Dentro de una etapa, ORDEN comienza en **00** (no 01).

**R-ORDEN-002:** Se incrementa de uno en uno: 00, 01, 02, ..., 99.

**R-ORDEN-003:** Los gaps dentro de una etapa deben **justificarse en documentación** (README de fase).

**R-ORDEN-004:** ORDEN refleja la **secuencia de ejecución o dependencias**, NO orden alfabético.

**R-ORDEN-005:** El módulo con ORDEN=00 en una etapa es típicamente el **componente base** de esa etapa.

**Ejemplo de orden correcto (Phase 2, Etapa 60):**
```
60.00 - base_executor           [componente base, debe existir primero]
60.01 - contract_validator      [valida antes de ejecutar]
60.02 - arg_router              [rutea argumentos a métodos]
60.03 - signature_runtime_validator [valida durante ejecución]
60.04 - resource_aware_executor [wrapper adaptativo de recursos]
60.05 - calibration_policy      [calibra resultados post-ejecución]
60.06 - instrumentation_mixin   [hooks de observabilidad]
```

#### 4.1.5 Nombres Descriptivos (Universal)

**R-NOMBRE-001:** Usar **VERBOS** (para acciones) o **SUSTANTIVOS TÉCNICOS** (para entidades), no palabras genéricas.

**R-NOMBRE-002:** Evitar redundancia con el número de etapa en el nombre.

**R-NOMBRE-003:** Patrones preferidos:
- `<entidad>` (ej. `factory`, `registry`)
- `<entidad>_<tipo>` (ej. `contract_validator`, `resource_manager`)
- `<componente>_<acción>` (ej. `irrigation_synchronizer`, `arg_router`)

**R-NOMBRE-004:** Prohibido usar abreviaturas no estándar o acrónimos oscuros.

**R-NOMBRE-005:** Máximo 32 caracteres para el componente de nombre (sin contar prefijos numéricos).

**Ejemplos buenos:**
- ✅ `factory` (entidad clara)
- ✅ `contract_validator_cqvr` (componente + tipo + acrónimo estándar)
- ✅ `irrigation_synchronizer` (acción + rol)
- ✅ `evidence_nexus` (componente + metáfora técnica establecida)

**Ejemplos malos:**
- ❌ `helper` (demasiado genérico)
- ❌ `utils` (sin información contextual)
- ❌ `thing_doer` (poco profesional)
- ❌ `mgr` (abreviatura no estándar)

#### 4.1.6 File Header Template (Mandatory)

**TODAS** las nuevas fases canónicas `.py` DEBEN comenzar con:

```python
"""
Module: src.canonic_phases.phase_{N}.<module_name>
Purpose: <ONE SENTENCE - what this module does>
Owner: phase{N}_<subsystem>
Lifecycle: ACTIVE|DEPRECATED|EXPERIMENTAL
Version: <SEMVER>
Effective-Date: <YYYY-MM-DD>

Contracts-Enforced:
    - <ContractName1>: <one-line description>
    - <ContractName2>: <one-line description>

Determinism:
    Seed-Strategy: FIXED|PARAMETERIZED|NOT_APPLICABLE
    State-Management: <description of state handling>

Inputs:
    - <InputName>: <Type> — <description>

Outputs:
    - <OutputName>: <Type> — <description>

Failure-Modes:
    - <FailureMode1>: <ErrorType> — <when this occurs>
    - <FailureMode2>: <ErrorType> — <when this occurs>
"""
from __future__ import annotations

# METADATA
__version__ = "<SEMVER>"
__phase__ = <N>
__stage__ = <ETAPA>
__order__ = <ORDEN>
__author__ = "<nombre>"
__created__ = "<YYYY-MM-DD>"
__modified__ = "<YYYY-MM-DD>"
__criticality__ = "CRITICAL|HIGH|MEDIUM|LOW"
__execution_pattern__ = "Singleton|Per-Task|Continuous|On-Demand|Parallel"
__module_type__ = "AUTH|REG|CFG|VAL|MGR|EXEC|ORCH|ANAL|SYNT|PROF|UTIL"

# PHASE_LABEL (legacy compatibility)
PHASE_LABEL = "Phase {N}"

# [Código del módulo]
```

**Campos Obligatorios:**
- `Module:` Ruta canónica del módulo
- `Purpose:` Una oración describiendo responsabilidad única
- `Owner:` Subsistema responsable (ej. `phase2_orchestration`)
- `Lifecycle:` Estado actual del módulo
- `Determinism.Seed-Strategy:` Estrategia de reproducibilidad
- `Inputs/Outputs:` Contratos de entrada/salida
- `Failure-Modes:` Modos de falla documentados

**Validación:**
Este header es verificado por `scripts/validation/validate_file_headers.py` en pre-commit.

#### 4.1.7 Infraestructura y Utilidades

**Formato:**
```
{categoria}/{nombre_descriptivo}.py
```

**Categorías permitidas:**
- `src/farfan_core/` → Core del sistema
- `src/farfan_pipeline/` → Pipeline principal
- `scripts/` → Scripts auxiliares
- `tests/` → Test suites
- `tools/` → Herramientas de desarrollo

**Restricciones:**
- NO usar `utils/`, `helpers/`, `misc/` (demasiado genéricos)
- Nombres deben reflejar responsabilidad específica
- Máximo 3 niveles de anidación

**Ejemplos:**
- ✅ `src/farfan_core/orchestration/task_scheduler.py`
- ✅ `scripts/validation/audit_contracts.py`
- ✅ `tests/integration/test_phase2_pipeline.py`
- ❌ `src/utils/helper.py`
- ❌ `scripts/misc/thing.py`

#### 4.1.3 Metadatos Obligatorios en Módulos

Todo módulo Python debe incluir en sus primeras 20 líneas:

```python
"""
Descripción concisa del módulo (1-3 líneas).

PHASE_LABEL: Phase {N}  # Para módulos de fase
MODULE_TYPE: {TIPO}     # AUTH|REG|CFG|VAL|MGR|EXEC|ORCH|ANAL|SYNT|PROF|UTIL
CRITICALITY: {NIVEL}    # CRITICAL|HIGH|MEDIUM|LOW
EXECUTION_PATTERN: {PATRON}  # Singleton|Per-Task|Continuous|On-Demand|Parallel

Autor: {nombre}
Fecha creación: {YYYY-MM-DD}
Última modificación: {YYYY-MM-DD}
"""
```

### 4.2 Contratos JSON

#### 4.2.1 Contratos de Ejecución

**Formato:**
```
Q{NNN}_executor_contract.json
```

**Donde:**
- `{NNN}`: Número de pregunta [001-300], con leading zeros

**Ubicación:**
```
executor_contracts/specialized/Q{NNN}_executor_contract.json
```

**Validación:**
- Debe pasar schema validation contra `contract_schema.json`
- Debe incluir `method_binding.methods[]` no vacío
- `metadata.contract_id` debe coincidir con `Q{NNN}`

#### 4.2.2 Templates y Schemas

**Formato:**
```
{tipo}_{nombre}_template.json
{nombre}_schema.json
```

**Ubicación:**
```
contract_templates/{categoria}/{nombre}.(json|yaml)
```

**Ejemplos:**
- ✅ `contract_templates/executor/base_contract_template.json`
- ✅ `contract_templates/schemas/cqvr_schema.json`
- ❌ `templates/my_template.json` (fuera de jerarquía)

### 4.3 Documentación

#### 4.3.1 Documentación Técnica

**Formato:**
```
{CATEGORIA}_{TEMA}_{TIPO}.md
```

**Categorías:**
- `AUDIT` → Auditorías de código/sistema
- `PHASE_{N}` → Documentación de fase específica
- `IMPLEMENTATION` → Guías de implementación
- `ARCHITECTURE` → Decisiones arquitectónicas
- `SPECIFICATION` → Especificaciones técnicas

**Tipos:**
- `REPORT` → Reportes detallados
- `SUMMARY` → Resúmenes ejecutivos
- `GUIDE` → Guías paso a paso
- `SPEC` → Especificaciones formales
- `INDEX` → Catálogos/índices
- `PLAN` → Planes de acción
- `QUICK_REF` → Referencias rápidas

**Ejemplos:**
- ✅ `AUDIT_EXECUTOR_METHODS_REPORT.md`
- ✅ `PHASE_2_IMPLEMENTATION_SUMMARY.md`
- ✅ `ARCHITECTURE_TRANSFORMATION_PLAN.md`
- ❌ `my_notes.md`
- ❌ `doc_v3_final.md`

#### 4.3.2 Metadatos Obligatorios en Documentación

Todo documento `.md` debe comenzar con frontmatter:

```markdown
# {TÍTULO DEL DOCUMENTO}

**Documento:** {CÓDIGO ÚNICO}  
**Versión:** {SEMVER}  
**Fecha:** {YYYY-MM-DD}  
**Estado:** {DRAFT|REVIEW|APPROVED|AUTORITATIVO|DEPRECATED}  
**Autor:** {nombre}  
**Alcance:** {descripción breve}  

---

[contenido]
```

### 4.4 Scripts Auxiliares

#### 4.4.1 Scripts de Validación

**Formato:**
```
validate_{tema}.py
audit_{sistema}.py
```

**Ubicación:**
```
scripts/validation/{nombre}.py
scripts/audit/{nombre}.py
```

**Estándares:**
- Deben ser ejecutables: `chmod +x`
- Incluir shebang: `#!/usr/bin/env python3`
- Docstring con uso: `--help` flag obligatorio
- Exit codes: 0=success, 1=validation failed, 2=error

#### 4.4.2 Scripts de Transformación

**Formato:**
```
transform_{entidad}.py
generate_{artefacto}.py
```

**Ubicación:**
```
scripts/transformation/{nombre}.py
scripts/generation/{nombre}.py
```

#### 4.4.3 Scripts de Deployment

**Formato:**
```
deploy_{target}.sh
rollback_{componente}.sh
```

**Ubicación:**
```
scripts/deployment/{nombre}.sh
```

### 4.5 Artefactos de Ejecución

#### 4.5.1 Logs y Trazas

**Formato:**
```
{timestamp}_{fase}_{componente}.log
```

**Ubicación:**
```
artifacts/logs/{YYYY-MM-DD}/{nombre}.log
```

**Ejemplo:**
```
artifacts/logs/2025-12-21/143052_phase2_executor.log
```

#### 4.5.2 Reportes de Ejecución

**Formato:**
```
{timestamp}_{tipo}_report.{json|md}
```

**Ubicación:**
```
artifacts/reports/{categoria}/{timestamp}_{nombre}.{ext}
```

**Ejemplo:**
```
artifacts/reports/cqvr/20251221_Q005_evaluation_report.json
```

#### 4.5.3 Métricas y Telemetría

**Formato:**
```
{timestamp}_metrics_{componente}.json
```

**Ubicación:**
```
artifacts/metrics/{YYYY-MM}/{timestamp}_{nombre}.json
```

### 4.6 Tests

#### 4.6.1 Tests Unitarios

**Formato:**
```
test_{modulo_a_testear}.py
```

**Ubicación:**
```
tests/unit/phase_{N}/test_{nombre}.py
```

**Ejemplo:**
```
tests/unit/phase_2/test_arg_router.py
```

#### 4.6.2 Tests de Integración

**Formato:**
```
test_{flujo}_integration.py
```

**Ubicación:**
```
tests/integration/test_{nombre}_integration.py
```

#### 4.6.3 Tests End-to-End

**Formato:**
```
test_{escenario}_e2e.py
```

**Ubicación:**
```
tests/e2e/test_{nombre}_e2e.py
```

---

## 5. JERARQUÍA DE DIRECTORIOS

### 5.1 Estructura Canónica de Fases

Cada fase canónica (Phase_zero - Phase_nine) DEBE seguir esta estructura estricta:

```
src/farfan_pipeline/phases/Phase_{name}/
│
├── README.md                         # 📘 README OBLIGATORIO (formato peer-review journal)
├── PHASE_{N}_CONSTANTS.py           # 🔒 Constantes de fase (OBLIGATORIO)
├── __init__.py                       # Inicialización del paquete
│
├── phase{N}_*.py                     # Módulos con nomenclatura posicional
│   ├── phase{N}_00.00___init__.py   # (si aplica)
│   ├── phase{N}_10.00_<nombre>.py   # Etapa 10
│   ├── phase{N}_10.01_<nombre>.py
│   ├── phase{N}_20.00_<nombre>.py   # Etapa 20
│   └── ...
│
├── json_files_phase_{name}/          # 📂 JSON auxiliares (si aplica)
│   ├── schemas/                      # Schemas de validación
│   ├── configs/                      # Configuraciones
│   └── mappings/                     # Mapeos de datos
│
├── contracts/                        # 📜 Contratos específicos de fase (si aplica)
│   ├── input_contracts/
│   └── output_contracts/
│
├── tests/                            # 🧪 Tests específicos de fase
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── docs/                             # 📚 Documentación técnica de fase
    ├── architecture.md               # Arquitectura de la fase
    ├── irrigation_flow.md            # 💧 Diagrama de irrigación (OBLIGATORIO)
    ├── transformation_narrative.md   # 📖 Narrativa de transformación (OBLIGATORIO)
    └── module_dependencies.dot       # Grafo de dependencias
```

### 5.2 Archivo README.md de Fase (OBLIGATORIO)

**TODAS** las fases canónicas DEBEN incluir un `README.md` con estructura de **artículo peer-review**:

```markdown
# Phase {N}: {Nombre de la Fase}

**Document ID:** PHASE-{N}-README  
**Version:** {SEMVER}  
**Date:** {YYYY-MM-DD}  
**Status:** ACTIVE  
**Authors:** {lista de autores}

---

## Abstract

{Resumen ejecutivo de 150-250 palabras describiendo propósito, metodología y resultados de la fase}

---

## 1. Introduction

### 1.1 Phase Overview
{Descripción general de la fase, su rol en el pipeline}

### 1.2 Motivation
{Por qué existe esta fase, qué problema resuelve}

### 1.3 Scope and Boundaries
{Qué incluye y qué NO incluye la fase}

---

## 2. Architecture

### 2.1 Stage Taxonomy

**Tabla de Etapas Canónicas:**

| Código | Nombre | Descripción | Cardinalidad | Tiempo |
|--------|--------|-------------|--------------|--------|
| 00 | ... | ... | ... | ... |
| 10 | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |

### 2.2 Stage Dependency Graph

```
[ASCII diagram o referencia a docs/module_dependencies.dot]
```

### 2.3 Module Classification

**Por Tipo:**
- AUTH: {lista de módulos}
- EXEC: {lista de módulos}
- VAL: {lista de módulos}
- ...

**Por Criticidad:**
- CRITICAL: {módulos}
- HIGH: {módulos}
- MEDIUM: {módulos}
- LOW: {módulos}

---

## 3. Transformation Narrative (Narrativa de Forzamiento)

### 3.1 Input Specification

**Formato de Entrada:**
```python
{Estructura de datos de entrada con tipos}
```

**Precondiciones:**
- {Lista de precondiciones que debe cumplir el input}

### 3.2 Processing Pipeline

**Flujo de Transformación:**

```
INPUT → [ETAPA 10] → [ETAPA 20] → ... → OUTPUT
```

**Detalle por Etapa:**

#### 3.2.1 ETAPA 10: {Nombre}
- **Input:** {tipo}
- **Processing:** {descripción detallada del procesamiento}
- **Output:** {tipo}
- **Invariants:** {invariantes que se mantienen}
- **Side Effects:** {efectos secundarios, si aplica}

#### 3.2.2 ETAPA 20: {Nombre}
[repetir estructura]

### 3.3 Output Specification

**Formato de Salida:**
```python
{Estructura de datos de salida con tipos}
```

**Postcondiciones:**
- {Lista de postcondiciones garantizadas}

---

## 4. Irrigation Flow (Flujo de Irrigación) 💧

### 4.1 Signal Propagation

**Diagrama de Irrigación:**
```
[Referencia a docs/irrigation_flow.md o diagrama inline]
```

### 4.2 Data Dependencies

**Matriz de Dependencias:**

| Módulo | Consume | Produce | Observa |
|--------|---------|---------|---------|
| phase{N}_10.00 | {datos} | {datos} | {señales} |
| phase{N}_20.00 | {datos} | {datos} | {señales} |
| ... | ... | ... | ... |

### 4.3 Synchronization Points

- **Punto 1:** {descripción de sincronización crítica}
- **Punto 2:** ...

---

## 5. Module Inventory

### 5.1 Complete File List

**Módulos activos:**

| Archivo | Etapa | Orden | Tipo | Criticidad | Propósito |
|---------|-------|-------|------|------------|-----------|
| phase{N}_10.00_xxx.py | 10 | 00 | AUTH | CRITICAL | {propósito} |
| phase{N}_10.01_yyy.py | 10 | 01 | REG | HIGH | {propósito} |
| ... | ... | ... | ... | ... | ... |

**Total:** {N} módulos activos

### 5.2 Deprecated Modules

{Lista de módulos deprecados con fecha y razón}

---

## 6. Determinism and Reproducibility

### 6.1 Seed Management
{Estrategia de seeds para reproducibilidad}

### 6.2 State Management
{Manejo de estado mutable, si aplica}

### 6.3 Idempotency Guarantees
{Garantías de idempotencia}

---

## 7. Performance Characteristics

### 7.1 Computational Complexity
- **Time Complexity:** O(...)
- **Space Complexity:** O(...)

### 7.2 Resource Requirements
- **RAM:** {estimación}
- **CPU:** {estimación}
- **Disk I/O:** {estimación}

### 7.3 Bottlenecks
{Identificación de cuellos de botella conocidos}

---

## 8. Testing Strategy

### 8.1 Test Coverage
- **Unit Tests:** {N} tests, {X}% coverage
- **Integration Tests:** {N} tests
- **E2E Tests:** {N} tests

### 8.2 Critical Test Scenarios
{Lista de escenarios críticos testeados}

---

## 9. Error Handling and Recovery

### 9.1 Failure Modes
{Tabla de modos de falla por módulo}

### 9.2 Recovery Strategies
{Estrategias de recuperación ante fallos}

### 9.3 Circuit Breakers
{Circuit breakers implementados, si aplica}

---

## 10. Maintenance and Evolution

### 10.1 Known Issues
{Issues conocidos sin resolver}

### 10.2 Future Enhancements
{Mejoras planificadas}

### 10.3 Migration Notes
{Notas de migración para cambios breaking}

---

## 11. References

### 11.1 Related Documentation
- {Enlaces a documentación relacionada}

### 11.2 External Dependencies
- {Lista de dependencias externas con versiones}

### 11.3 Academic References
{Referencias académicas si aplica}

---

## Appendices

### A. Glossary
{Glosario de términos específicos de la fase}

### B. Configuration Examples
{Ejemplos de configuración}

### C. Troubleshooting Guide
{Guía de troubleshooting común}

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | {autor} | Initial version |

```

**Validación:**
El README es verificado por `scripts/validation/validate_phase_readme.py` que verifica:
- Presencia de todas las secciones obligatorias
- Tabla de etapas completa
- Inventario de módulos actualizado
- Narrativa de irrigación presente

### 5.3 Archivo PHASE_{N}_CONSTANTS.py (OBLIGATORIO)

Cada fase DEBE tener un archivo de constantes:

```python
"""
Module: src.canonic_phases.phase_{N}.PHASE_{N}_CONSTANTS
Purpose: Constantes globales de Phase {N}
Owner: phase{N}_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: YYYY-MM-DD
"""
from __future__ import annotations

from typing import Final

# METADATA
__version__ = "1.0.0"
__phase__ = {N}

# ============================================================================
# PHASE IDENTIFICATION
# ============================================================================

PHASE_NUMBER: Final[int] = {N}
PHASE_NAME: Final[str] = "Phase {N}: {Nombre}"
PHASE_LABEL: Final[str] = f"Phase {PHASE_NUMBER}"

# ============================================================================
# STAGE DEFINITIONS
# ============================================================================

STAGE_BASE: Final[int] = 0
STAGE_TESTING: Final[int] = 9
STAGE_INIT: Final[int] = 10
STAGE_VALIDATION: Final[int] = 20
STAGE_RESOURCES: Final[int] = 30
# ... [definir todas las etapas de la fase]

VALID_STAGES: Final[set[int]] = {
    STAGE_BASE,
    STAGE_TESTING,
    STAGE_INIT,
    # ... [todas las etapas válidas]
}

# ============================================================================
# MODULE TYPES
# ============================================================================

TYPE_AUTHORITY: Final[str] = "AUTH"
TYPE_REGISTRY: Final[str] = "REG"
TYPE_CONFIG: Final[str] = "CFG"
TYPE_VALIDATOR: Final[str] = "VAL"
TYPE_MANAGER: Final[str] = "MGR"
TYPE_EXECUTOR: Final[str] = "EXEC"
TYPE_ORCHESTRATOR: Final[str] = "ORCH"
TYPE_ANALYZER: Final[str] = "ANAL"
TYPE_SYNTHESIZER: Final[str] = "SYNT"
TYPE_PROFILER: Final[str] = "PROF"
TYPE_UTILITY: Final[str] = "UTIL"

VALID_MODULE_TYPES: Final[set[str]] = {
    TYPE_AUTHORITY,
    TYPE_REGISTRY,
    TYPE_CONFIG,
    TYPE_VALIDATOR,
    TYPE_MANAGER,
    TYPE_EXECUTOR,
    TYPE_ORCHESTRATOR,
    TYPE_ANALYZER,
    TYPE_SYNTHESIZER,
    TYPE_PROFILER,
    TYPE_UTILITY,
}

# ============================================================================
# CRITICALITY LEVELS
# ============================================================================

CRITICALITY_CRITICAL: Final[str] = "CRITICAL"
CRITICALITY_HIGH: Final[str] = "HIGH"
CRITICALITY_MEDIUM: Final[str] = "MEDIUM"
CRITICALITY_LOW: Final[str] = "LOW"

VALID_CRITICALITY_LEVELS: Final[set[str]] = {
    CRITICALITY_CRITICAL,
    CRITICALITY_HIGH,
    CRITICALITY_MEDIUM,
    CRITICALITY_LOW,
}

# ============================================================================
# EXECUTION PATTERNS
# ============================================================================

PATTERN_SINGLETON: Final[str] = "Singleton"
PATTERN_PER_TASK: Final[str] = "Per-Task"
PATTERN_CONTINUOUS: Final[str] = "Continuous"
PATTERN_ON_DEMAND: Final[str] = "On-Demand"
PATTERN_PARALLEL: Final[str] = "Parallel"

VALID_EXECUTION_PATTERNS: Final[set[str]] = {
    PATTERN_SINGLETON,
    PATTERN_PER_TASK,
    PATTERN_CONTINUOUS,
    PATTERN_ON_DEMAND,
    PATTERN_PARALLEL,
}

# ============================================================================
# RESOURCE LIMITS (if applicable to phase)
# ============================================================================

MAX_MEMORY_MB: Final[int] = 4096
MAX_CPU_PERCENT: Final[float] = 80.0
TIMEOUT_SECONDS: Final[int] = 300

# ============================================================================
# DETERMINISM
# ============================================================================

DEFAULT_SEED: Final[int] = 42
SEED_STRATEGY: Final[str] = "FIXED"  # or "PARAMETERIZED" or "NOT_APPLICABLE"

# ============================================================================
# PHASE-SPECIFIC CONSTANTS
# ============================================================================

# [Añadir constantes específicas de la fase aquí]
# Ejemplos:
# - Phase 2: CHUNK_SIZE, TASK_COUNT, etc.
# - Phase 3: EMBEDDING_DIMENSION, MAX_TOKENS, etc.
```

### 5.4 Archivo docs/irrigation_flow.md (OBLIGATORIO)

Cada fase DEBE documentar su flujo de irrigación:

```markdown
# Phase {N}: Irrigation Flow Diagram

**Document ID:** PHASE-{N}-IRRIGATION  
**Version:** 1.0.0  
**Date:** YYYY-MM-DD

---

## 1. Irrigation Overview

{Descripción general del flujo de señales/datos en la fase}

## 2. Signal Taxonomy

### 2.1 Input Signals

| Signal | Type | Source | Description |
|--------|------|--------|-------------|
| {nombre} | {tipo} | {módulo/fase} | {descripción} |

### 2.2 Internal Signals

| Signal | Type | Producer | Consumer(s) | Lifecycle |
|--------|------|----------|-------------|-----------|
| {nombre} | {tipo} | {módulo} | {módulos} | {cuándo existe} |

### 2.3 Output Signals

| Signal | Type | Destination | Description |
|--------|------|-------------|-------------|
| {nombre} | {tipo} | {módulo/fase} | {descripción} |

## 3. Irrigation Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE {N} IRRIGATION                      │
└─────────────────────────────────────────────────────────────┘

INPUT SIGNALS
    ↓
┌───────────────┐
│  ETAPA 10     │ → [signal_a] ─────────┐
│  {nombre}     │                        │
└───────────────┘                        ↓
                                    ┌───────────────┐
                                    │  ETAPA 20     │
INPUT SIGNALS ──→ [signal_b] ───→   │  {nombre}     │
                                    └───────────────┘
                                         ↓
                                    [signal_c]
                                         ↓
                                    ┌───────────────┐
                                    │  ETAPA 30     │
                                    │  {nombre}     │
                                    └───────────────┘
                                         ↓
                                    OUTPUT SIGNALS
```

## 4. Synchronization Points

### 4.1 Critical Joins

{Descripción de puntos donde múltiples señales se sincronizan}

### 4.2 Barriers

{Descripción de barreras de sincronización}

### 4.3 Deadlock Prevention

{Estrategias para prevenir deadlocks}

## 5. Data Dependencies

{Matriz o grafo de dependencias de datos entre módulos}

## 6. Performance Implications

{Impacto de la irrigación en performance}
```

### 5.5 Estructura Global Completa

```
F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/
│
├── src/                              # Código fuente
│   ├── farfan_core/                  # Core del sistema
│   │   ├── core/                     # Lógica central
│   │   ├── orchestration/            # Orquestación
│   │   ├── analysis/                 # Métodos de análisis
│   │   └── api/                      # API REST
│   │
│   └── farfan_pipeline/              # Pipeline principal
│       ├── phases/                   # 🔹 FASES CANÓNICAS (estructura estricta)
│       │   ├── Phase_zero/
│       │   │   ├── README.md          # ✅ OBLIGATORIO
│       │   │   ├── PHASE_0_CONSTANTS.py  # ✅ OBLIGATORIO
│       │   │   ├── docs/
│       │   │   │   ├── irrigation_flow.md  # ✅ OBLIGATORIO
│       │   │   │   └── transformation_narrative.md  # ✅ OBLIGATORIO
│       │   │   ├── phase0_*.py
│       │   │   └── tests/
│       │   ├── Phase_one/
│       │   │   ├── README.md
│       │   │   ├── PHASE_1_CONSTANTS.py
│       │   │   ├── docs/
│       │   │   ├── phase1_*.py
│       │   │   └── tests/
│       │   ├── Phase_two/           # ⭐ Referencia canónica
│       │   │   ├── README.md
│       │   │   ├── PHASE_2_CONSTANTS.py
│       │   │   ├── docs/
│       │   │   │   ├── irrigation_flow.md
│       │   │   │   ├── transformation_narrative.md
│       │   │   │   └── module_dependencies.dot
│       │   │   ├── phase2_*.py       # Módulos con nomenclatura posicional
│       │   │   ├── json_files_phase_two/
│       │   │   │   ├── schemas/
│       │   │   │   ├── configs/
│       │   │   │   └── mappings/
│       │   │   ├── contracts/
│       │   │   └── tests/
│       │   ├── Phase_three/
│       │   │   └── [estructura idéntica]
│       │   ├── ...
│       │   └── Phase_nine/
│       │       └── [estructura idéntica]
│       │
│       ├── methods_dispensary/       # Métodos del dispensario
│       │   ├── __init__.py
│       │   ├── class_registry.py
│       │   └── {metodo}.py
│       │
│       └── infrastructure/           # SISAS, recursos
│
├── executor_contracts/               # Contratos de ejecución
│   ├── specialized/                  # Q001-Q300
│   │   └── Q{NNN}_executor_contract.json
│   └── templates/                    # Templates base
│
├── contract_templates/               # Templates y schemas
│   ├── executor/
│   ├── schemas/
│   └── validation/
│
├── scripts/                          # Scripts auxiliares
│   ├── validation/
│   ├── transformation/
│   ├── deployment/
│   └── migration/
│
├── tests/                            # Test suites
│   ├── unit/
│   │   ├── phase_0/
│   │   ├── phase_2/
│   │   └── ...
│   ├── integration/
│   └── e2e/
│
├── artifacts/                        # Artefactos de ejecución
│   ├── logs/
│   │   └── {YYYY-MM-DD}/
│   ├── reports/
│   │   ├── cqvr/
│   │   ├── audit/
│   │   └── execution/
│   ├── metrics/
│   │   └── {YYYY-MM}/
│   └── traces/
│
├── docs/                             # Documentación versionada
│   ├── architecture/
│   ├── api/
│   ├── guides/
│   └── policies/
│
├── archive/                          # Código legacy
│   └── {YYYY-MM-DD}_{descripcion}/
│
├── experimental/                     # Experimentos temporales
│   └── {fecha_expiracion}_{nombre}/
│
├── data/                             # Datos de entrada
│   ├── input/
│   ├── reference/
│   └── test_fixtures/
│
├── dashboard/                        # Dashboards y visualización
│   ├── html/
│   ├── static/
│   └── templates/
│
├── reports/                          # Reportes estáticos (root)
│   ├── AUDIT_*.md
│   ├── PHASE_*.md
│   ├── BATCH_*.md
│   └── CQVR_*.md
│
├── .github/                          # CI/CD
│   └── workflows/
│
├── .git/
├── .gitignore
├── README.md
├── pyproject.toml
├── requirements.txt
└── setup.py
```

### 5.2 Reglas de Jerarquía

**R-HIERARCHY-001:** Máximo 5 niveles de anidación desde root.

**R-HIERARCHY-002:** Nombres de directorios:
- Código: `snake_case` o `PascalCase` (consistente dentro de nivel)
- Documentación: `lowercase` o `kebab-case`

**R-HIERARCHY-003:** Directorios prohibidos:
- ❌ `temp/`, `tmp/`
- ❌ `backup/`, `old/`
- ❌ `misc/`, `other/`
- ❌ `stuff/`, `things/`

**R-HIERARCHY-004:** Directorios con fecha de expiración:
- `experimental/{YYYY-MM-DD}_{nombre}/` → Auto-eliminar después de 90 días
- `archive/{YYYY-MM-DD}_{nombre}/` → Mantener 2 años, luego comprimir

---

## 6. POLÍTICAS DE ALMACENAMIENTO

### 6.1 Higiene de Artefactos

#### 6.1.1 Regla de Zero Duplicados

```
REGLA ESTRICTA: Ningún contenido idéntico puede existir en dos ubicaciones.
```

**Enforcement:**
- Pre-commit hook detecta archivos con hash idéntico
- CI/CD falla si encuentra duplicados
- Excepción: Symlinks documentados explícitamente

**Script de detección:**
```bash
#!/bin/bash
# scripts/validation/detect_duplicates.sh

find src/ artifacts/ docs/ -type f -exec md5sum {} + | \
  sort | \
  uniq -w32 -d --all-repeated=separate
```

#### 6.1.2 Regla de Archivos Huérfanos

```
REGLA: Todo artefacto debe tener al menos 1 referencia activa o fecha de expiración.
```

**Definiciones:**
- **Archivo huérfano:** No importado, no ejecutado, no referenciado en docs
- **Tiempo de gracia:** 30 días desde creación
- **Acción:** Mover a `archive/` con timestamp

**Script de auditoría:**
```python
# scripts/audit/find_orphan_files.py
import os
import time
from datetime import datetime, timedelta

GRACE_PERIOD_DAYS = 30
SEARCH_PATHS = ['src/', 'scripts/', 'docs/']

def find_orphans():
    orphans = []
    cutoff = time.time() - (GRACE_PERIOD_DAYS * 86400)
    
    for path in SEARCH_PATHS:
        for root, dirs, files in os.walk(path):
            for file in files:
                filepath = os.path.join(root, file)
                stat = os.stat(filepath)
                
                # Check last access time
                if stat.st_atime < cutoff:
                    orphans.append({
                        'path': filepath,
                        'last_access': datetime.fromtimestamp(stat.st_atime),
                        'size': stat.st_size
                    })
    
    return orphans
```

#### 6.1.3 Regla de Tamaño de Archivos

| Categoría | Límite | Acción si excede |
|-----------|--------|------------------|
| Código Python | 1000 líneas | Refactorizar en módulos |
| JSON | 500 KB | Comprimir o dividir |
| Documentación MD | 10,000 líneas | Dividir en subsecciones |
| Logs | 100 MB | Rotar y comprimir |
| Artefactos binarios | 50 MB | Mover a storage externo |

**Enforcement:**
```python
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-file-size
        name: Check file sizes
        entry: python scripts/validation/check_file_sizes.py
        language: python
        pass_filenames: true
```

### 6.2 Rotación y Compresión

#### 6.2.1 Logs

**Política:**
```
artifacts/logs/{YYYY-MM-DD}/{timestamp}_{componente}.log
```

- Rotación diaria automática
- Compresión después de 7 días → `.log.gz`
- Retención: 90 días comprimido, luego eliminar

**Implementación:**
```bash
# scripts/maintenance/rotate_logs.sh
#!/bin/bash

LOG_DIR="artifacts/logs"
COMPRESS_AFTER=7    # días
RETENTION=90        # días

# Comprimir logs > 7 días
find "$LOG_DIR" -name "*.log" -mtime +$COMPRESS_AFTER -exec gzip {} \;

# Eliminar logs > 90 días
find "$LOG_DIR" -name "*.log.gz" -mtime +$RETENTION -delete
```

#### 6.2.2 Métricas

**Política:**
```
artifacts/metrics/{YYYY-MM}/{timestamp}_metrics_{componente}.json
```

- Agregación mensual en archivo consolidado
- Retención: 12 meses detallado, 5 años agregado

#### 6.2.3 Reportes

**Política:**
```
artifacts/reports/{categoria}/{timestamp}_{nombre}.{json|md}
```

- Sin rotación automática
- Auditoría manual trimestral
- Mover reportes obsoletos a `archive/`

### 6.3 Backup y Recuperación

**Estrategia 3-2-1:**
- 3 copias de datos críticos
- 2 medios diferentes (local + cloud)
- 1 copia offsite

**Artefactos críticos:**
- `src/` → Git + backup diario
- `executor_contracts/` → Git + backup diario
- `artifacts/metrics/` → Backup semanal
- `docs/policies/` → Git + backup mensual

---

## 7. SISTEMA DE ETIQUETADO

### 7.1 Labels en Git

#### 7.1.1 Tags de Versión

**Formato:** `v{MAJOR}.{MINOR}.{PATCH}`

**Ejemplos:**
- `v1.0.0` → Release inicial
- `v1.2.3` → Versión estable
- `v2.0.0-alpha.1` → Pre-release

#### 7.1.2 Labels de Pull Requests

| Label | Significado | Acción |
|-------|-------------|--------|
| `breaking-change` | Cambio no compatible | Requiere aprobación lead |
| `hotfix` | Fix urgente | Fast-track review |
| `refactor` | Refactorización | Extensa revisión de tests |
| `documentation` | Solo docs | No requiere tests |
| `phase-{N}` | Afecta fase N | Review por experto de fase |
| `needs-migration` | Requiere migración | Generar migration script |
| `policy-update` | Actualiza política | Requiere ADR |

### 7.2 Metadatos en Archivos

#### 7.2.1 Código Python

```python
# METADATA
__version__ = "1.2.3"
__author__ = "F.A.R.F.A.N Team"
__created__ = "2025-01-15"
__modified__ = "2025-12-21"
__phase__ = 2
__stage__ = 60
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"
```

#### 7.2.2 JSON

```json
{
  "$schema": "contract_schema.json",
  "metadata": {
    "contract_id": "Q005",
    "version": "3.0.0",
    "created": "2025-01-15",
    "last_modified": "2025-12-21",
    "author": "system",
    "status": "active"
  },
  ...
}
```

#### 7.2.3 Markdown

```markdown
---
document_id: FPN-GLOBAL-001
version: 1.0.0
status: AUTORITATIVO
created: 2025-12-21
author: Tech Committee
tags: [policy, naming, global]
---
```

---

## 8. ARTEFACTOS FUERA DE FASES CANÓNICAS

### 8.1 Documentación Root-Level

**Política:**
```
Archivos en root (/) deben ser documentación ejecutiva o índices generales.
```

**Formato:**
```
{CATEGORIA}_{TEMA}_{TIPO}.md
```

**Categorías permitidas:**
- `AUDIT_` → Auditorías multi-fase
- `IMPLEMENTATION_` → Resúmenes de implementación global
- `ARCHITECTURE_` → Decisiones arquitectónicas
- `DEPLOYMENT_` → Guías de deployment
- `CHANGELOG` → Historial de cambios (único sin prefijo)
- `README` → Documentación principal (único sin prefijo)

**Restricciones:**
- **Máximo 50 archivos** en root
- Archivos >100 KB deben moverse a `docs/`
- Nombres deben ser AUTOEXPLICATIVOS
- Prohibido: `doc.md`, `notes.md`, `temp.md`

**Ejemplos válidos:**
```
✅ /README.md
✅ /CHANGELOG.md
✅ /AUDIT_EXECUTOR_CONTRACTS_V3_Q001_Q020_EXECUTIVE_SUMMARY.md
✅ /IMPLEMENTATION_SUMMARY_REPORT_GENERATION.md
✅ /ARCHITECTURE_TRANSFORMATION_MASTER_PLAN.md
✅ /DEPLOYMENT_CHECKLIST.md
```

**Ejemplos inválidos:**
```
❌ /document.md
❌ /my_notes.md
❌ /temp_analysis.md
❌ /fix_v2_FINAL.md
```

### 8.2 Scripts Root-Level

**Política:**
```
Solo scripts de ENTRADA PRINCIPAL permitidos en root.
```

**Scripts permitidos:**
- `RUN_PIPELINE.py` → Entry point principal
- `install.sh` → Setup inicial
- `run_pipeline.sh` → Wrapper de ejecución

**Cualquier otro script → `scripts/{categoria}/`**

### 8.3 Configuración Root-Level

**Archivos de configuración permitidos en root:**
```
✅ pyproject.toml          # Build system
✅ setup.py                # Package setup
✅ requirements.txt        # Dependencies
✅ .gitignore              # Git config
✅ .pre-commit-config.yaml # Pre-commit hooks
✅ .ruff.toml              # Linter config
✅ mypy.ini                # Type checker config
✅ pytest.ini              # Test config
```

**Prohibidos:**
```
❌ config.json
❌ settings.yaml
❌ my_config.ini
```

### 8.4 Artefactos Temporales

**Política de experimentación:**
```
experimental/{YYYY-MM-DD}_expiry_{nombre}/
```

**Reglas:**
- Fecha de expiración OBLIGATORIA en nombre de carpeta
- Auto-eliminación después de fecha (CI/CD cronjob)
- Máximo 90 días de vida
- Prohibido en producción

**Ejemplo:**
```
experimental/2025-03-21_expiry_llm_optimization/
  ├── README.md          # Justificación del experimento
  ├── experiment.py
  └── results.json
```

### 8.5 Archive y Legacy

**Política de archivado:**
```
archive/{YYYY-MM-DD}_{descripcion}/
```

**Reglas:**
- Timestamp OBLIGATORIO
- Incluir `ARCHIVE_README.md` explicando razón
- Compresión opcional para >100 MB
- Retención: 2 años, luego evaluación de eliminación

**Ejemplo:**
```
archive/2024-06-15_old_phase2_nomenclature/
  ├── ARCHIVE_README.md  # Por qué se archivó
  ├── phase2_a_*.py
  └── MIGRATION_MAP.json
```

---

## 9. VALIDACIÓN Y COMPLIANCE

### 9.1 Validador Global

**Script maestro:**
```bash
#!/usr/bin/env python3
"""
Validador global de nomenclatura F.A.R.F.A.N.
Archivo: scripts/validation/validate_global_naming_policy.py
"""

import sys
from pathlib import Path
from typing import List, Dict
import re
import json

class PolicyValidator:
    def __init__(self, root: Path):
        self.root = root
        self.errors = []
        self.warnings = []
    
    def validate_all(self):
        """Ejecuta todas las validaciones."""
        self.validate_phase_modules()
        self.validate_contracts()
        self.validate_documentation()
        self.validate_scripts()
        self.validate_hierarchy()
        self.validate_orphans()
        self.validate_duplicates()
        
        self.report_results()
    
    def validate_phase_modules(self):
        """Valida módulos de fase."""
        pattern = re.compile(
            r'^phase(?P<fase>[0-9])_'
            r'(?P<etapa>\d{2})\.(?P<orden>\d{2})_'
            r'(?P<nombre>[a-z][a-z0-9_]+)\.py$'
        )
        
        for phase_dir in self.root.glob('src/farfan_pipeline/phases/Phase_*/'):
            for py_file in phase_dir.glob('phase*.py'):
                if not pattern.match(py_file.name):
                    self.errors.append({
                        'file': str(py_file),
                        'code': 'PHASE-001',
                        'message': 'Formato de nombre inválido'
                    })
    
    def validate_contracts(self):
        """Valida contratos JSON."""
        pattern = re.compile(r'^Q(?P<num>\d{3})_executor_contract\.json$')
        
        contract_dir = self.root / 'executor_contracts/specialized'
        if contract_dir.exists():
            for json_file in contract_dir.glob('*.json'):
                if not pattern.match(json_file.name):
                    self.errors.append({
                        'file': str(json_file),
                        'code': 'CONTRACT-001',
                        'message': 'Formato de contrato inválido'
                    })
    
    def validate_documentation(self):
        """Valida documentación root."""
        root_docs = list(self.root.glob('*.md'))
        
        # Excluir permitidos
        allowed = {'README.md', 'CHANGELOG.md'}
        root_docs = [f for f in root_docs if f.name not in allowed]
        
        # Validar formato
        pattern = re.compile(r'^[A-Z][A-Z0-9_]+\.md$')
        for doc in root_docs:
            if not pattern.match(doc.name):
                self.errors.append({
                    'file': str(doc),
                    'code': 'DOC-001',
                    'message': 'Documentación root debe usar UPPER_SNAKE_CASE'
                })
        
        # Límite de 50 archivos
        if len(root_docs) > 50:
            self.warnings.append({
                'code': 'DOC-002',
                'message': f'Demasiados archivos en root: {len(root_docs)} (máx 50)'
            })
    
    def validate_scripts(self):
        """Valida que solo scripts permitidos estén en root."""
        allowed_root_scripts = {
            'RUN_PIPELINE.py',
            'install.sh',
            'run_pipeline.sh',
            'setup.py'
        }
        
        for script in self.root.glob('*.{py,sh}'):
            if script.name not in allowed_root_scripts:
                self.warnings.append({
                    'file': str(script),
                    'code': 'SCRIPT-001',
                    'message': f'Script debería estar en scripts/: {script.name}'
                })
    
    def validate_hierarchy(self):
        """Valida profundidad de jerarquía."""
        max_depth = 5
        
        for path in self.root.rglob('*'):
            if path.is_file():
                depth = len(path.relative_to(self.root).parts)
                if depth > max_depth:
                    self.warnings.append({
                        'file': str(path),
                        'code': 'HIERARCHY-001',
                        'message': f'Profundidad {depth} excede máximo {max_depth}'
                    })
    
    def validate_orphans(self):
        """Detecta archivos huérfanos."""
        import time
        cutoff = time.time() - (30 * 86400)  # 30 días
        
        for py_file in self.root.rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            stat = py_file.stat()
            if stat.st_atime < cutoff:
                self.warnings.append({
                    'file': str(py_file),
                    'code': 'ORPHAN-001',
                    'message': f'Sin acceso por >30 días'
                })
    
    def validate_duplicates(self):
        """Detecta archivos duplicados por hash."""
        import hashlib
        
        hashes = {}
        for file in self.root.rglob('*'):
            if file.is_file() and file.suffix in {'.py', '.json', '.md'}:
                try:
                    content = file.read_bytes()
                    hash_val = hashlib.md5(content).hexdigest()
                    
                    if hash_val in hashes:
                        self.errors.append({
                            'file': str(file),
                            'code': 'DUPLICATE-001',
                            'message': f'Duplicado de: {hashes[hash_val]}'
                        })
                    else:
                        hashes[hash_val] = str(file)
                except:
                    pass
    
    def report_results(self):
        """Genera reporte de resultados."""
        print("=" * 70)
        print("VALIDADOR GLOBAL DE NOMENCLATURA F.A.R.F.A.N")
        print("=" * 70)
        
        if self.errors:
            print(f"\n❌ {len(self.errors)} ERRORES CRÍTICOS:")
            for error in self.errors:
                print(f"  [{error['code']}] {error.get('file', 'N/A')}")
                print(f"      {error['message']}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"  [{warning['code']}] {warning.get('file', 'N/A')}")
                print(f"      {warning['message']}")
        
        if not self.errors and not self.warnings:
            print("\n✅ TODOS LOS ARTEFACTOS CUMPLEN LA POLÍTICA")
        
        print("=" * 70)
        
        sys.exit(1 if self.errors else 0)

if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parents[2]
    validator = PolicyValidator(root_dir)
    validator.validate_all()
```

### 9.2 Integración CI/CD

**GitHub Actions workflow:**
```yaml
# .github/workflows/validate-naming-policy.yml
name: Global Naming Policy Compliance

on:
  pull_request:
  push:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Run global naming validator
        run: |
          python scripts/validation/validate_global_naming_policy.py
      
      - name: Check for orphan files
        run: |
          python scripts/audit/find_orphan_files.py
      
      - name: Detect duplicates
        run: |
          bash scripts/validation/detect_duplicates.sh
      
      - name: Fail if policy violated
        if: failure()
        run: |
          echo "❌ Violación de FPN-GLOBAL-001"
          echo "Ver: docs/policies/GLOBAL_NAMING_POLICY.md"
          exit 1
```

### 9.3 Pre-commit Hooks

**Configuración:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-naming-policy
        name: Validate Naming Policy
        entry: python scripts/validation/validate_global_naming_policy.py
        language: python
        pass_filenames: false
        always_run: true
      
      - id: check-file-sizes
        name: Check File Sizes
        entry: python scripts/validation/check_file_sizes.py
        language: python
        pass_filenames: true
      
      - id: prevent-root-scripts
        name: Prevent Root Scripts
        entry: bash -c 'if [[ "$1" =~ ^[^/]+\.(py|sh)$ ]]; then echo "Scripts must be in scripts/"; exit 1; fi'
        language: system
        pass_filenames: true
        files: '^[^/]+\.(py|sh)$'
        exclude: '^(RUN_PIPELINE\.py|install\.sh|run_pipeline\.sh|setup\.py)$'
```

---

## 10. MANTENIMIENTO Y GOBERNANZA

### 10.1 Comité de Nomenclatura

**Responsabilidades:**
- Aprobar desviaciones de política
- Revisar propuestas de nuevas categorías
- Actualizar políticas trimestralmente
- Resolver conflictos de nomenclatura

**Composición:**
- Lead Architect
- DevOps Lead
- 2x Senior Engineers
- Technical Writer

### 10.2 Proceso de Cambio

**Para modificar esta política:**

1. **Propuesta (ADR):**
   ```markdown
   # ADR-XXX: Cambio en Política de Nomenclatura
   
   ## Contexto
   [Describir problema actual]
   
   ## Decisión
   [Cambio propuesto]
   
   ## Consecuencias
   [Impacto en código existente]
   
   ## Alternativas Consideradas
   [Otras opciones evaluadas]
   ```

2. **Revisión:**
   - Comité de Nomenclatura revisa
   - Se requiere consenso (4/5 votos)

3. **Implementación:**
   - Actualizar este documento (incrementar versión)
   - Generar migration script si aplica
   - Actualizar validadores
   - Comunicar a todo el equipo

4. **Deployment:**
   - Merge a `main`
   - Crear tag de versión de política
   - Actualizar docs

### 10.3 Ciclo de Auditoría

**Auditorías automáticas:**
- **Diaria:** Detección de duplicados
- **Semanal:** Archivos huérfanos
- **Mensual:** Validación completa de compliance

**Auditorías manuales:**
- **Trimestral:** Revisión de estructura de directorios
- **Semestral:** Evaluación de archivos en `archive/`
- **Anual:** Refactorización mayor si es necesario

### 10.4 Métricas de Salud

**KPIs de compliance:**
- **Compliance Score:** % archivos que pasan validación (objetivo: >98%)
- **Orphan Rate:** % archivos sin uso (objetivo: <2%)
- **Duplicate Rate:** % archivos duplicados (objetivo: 0%)
- **Avg File Age:** Edad promedio de archivos (objetivo: <6 meses)
- **Root Clutter:** # archivos en root (objetivo: <50)

**Dashboard:**
```python
# scripts/metrics/generate_compliance_dashboard.py
import json
from pathlib import Path
from datetime import datetime

def generate_dashboard():
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'compliance_score': 0.0,
        'orphan_rate': 0.0,
        'duplicate_rate': 0.0,
        'avg_file_age_days': 0.0,
        'root_file_count': 0
    }
    
    # [Calcular métricas]
    
    # Generar HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Naming Policy Compliance Dashboard</title></head>
    <body>
        <h1>F.A.R.F.A.N Naming Policy Compliance</h1>
        <p>Last updated: {metrics['timestamp']}</p>
        
        <div class="metric">
            <h2>Compliance Score</h2>
            <p class="value">{metrics['compliance_score']:.1f}%</p>
        </div>
        
        <!-- Más métricas -->
    </body>
    </html>
    """
    
    Path('dashboard/compliance.html').write_text(html)

if __name__ == "__main__":
    generate_dashboard()
```

---

## 11. ANEXOS

### 11.1 Glosario

| Término | Definición |
|---------|------------|
| **Artefacto** | Cualquier archivo generado o mantenido en el repositorio |
| **Compliance** | Conformidad con las reglas de esta política |
| **Huérfano** | Archivo sin referencias activas ni uso documentado |
| **Fase Canónica** | Fases 0-9 del pipeline principal |
| **Criticidad** | Nivel de impacto de un módulo (CRITICAL, HIGH, MEDIUM, LOW) |
| **Etapa** | Subdivisión temporal dentro de una fase |
| **CQVR** | Contract, Question, Validation, Response (framework de evaluación) |

### 11.2 Expresiones Regulares de Referencia

```python
# Módulos de fase
PHASE_MODULE = r'^phase[0-9]_\d{2}\.\d{2}_[a-z][a-z0-9_]+\.py$'

# Contratos
CONTRACT = r'^Q\d{3}_executor_contract\.json$'

# Documentación root
ROOT_DOC = r'^[A-Z][A-Z0-9_]+\.(md|txt)$'

# Scripts
SCRIPT = r'^[a-z][a-z0-9_]+\.(py|sh)$'

# Timestamps
TIMESTAMP = r'^\d{8}_\d{6}$'  # YYYYMMDD_HHMMSS
DATE = r'^\d{4}-\d{2}-\d{2}$'  # YYYY-MM-DD
```

### 11.3 Ejemplos Completos

#### Ejemplo 1: Nuevo Módulo de Fase

```python
# Crear: src/farfan_pipeline/phases/Phase_two/phase2_65.00_cache_layer.py

"""
Capa de caché para optimización de ejecución repetida.

PHASE_LABEL: Phase 2
MODULE_TYPE: EXEC
CRITICALITY: MEDIUM
EXECUTION_PATTERN: On-Demand

Autor: John Doe
Fecha creación: 2025-12-21
Última modificación: 2025-12-21
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 2
__stage__ = 65
__order__ = 0

class CacheLayer:
    ...
```

#### Ejemplo 2: Nuevo Contrato

```json
// Crear: executor_contracts/specialized/Q301_executor_contract.json

{
  "$schema": "../../contract_templates/schemas/contract_schema.json",
  "metadata": {
    "contract_id": "Q301",
    "version": "1.0.0",
    "created": "2025-12-21",
    "author": "system",
    "status": "draft"
  },
  "method_binding": {
    "methods": ["analyze_new_dimension"]
  },
  ...
}
```

#### Ejemplo 3: Nuevo Documento de Auditoría

```markdown
<!-- Crear: reports/AUDIT_CACHE_LAYER_IMPLEMENTATION_REPORT.md -->

# AUDITORÍA DE IMPLEMENTACIÓN DE CAPA DE CACHÉ

**Documento:** AUDIT-CACHE-001  
**Versión:** 1.0.0  
**Fecha:** 2025-12-21  
**Estado:** DRAFT  
**Autor:** John Doe  
**Alcance:** Módulo phase2_65.00_cache_layer.py

---

## Resumen Ejecutivo
[...]
```

### 11.4 Checklist de Compliance

**Para cada nuevo artefacto:**

- [ ] Nombre sigue formato de categoría correspondiente
- [ ] Ubicación en jerarquía correcta
- [ ] Metadatos obligatorios presentes
- [ ] Pasa validación de pre-commit
- [ ] Documentación inline suficiente
- [ ] Referenciado en al menos 1 lugar (imports, docs, tests)
- [ ] Tests correspondientes creados (si código)
- [ ] Sin duplicados de contenido
- [ ] Tamaño dentro de límites
- [ ] Revisado por par

---

## 12. CONTROL DE VERSIONES DE POLÍTICA

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0.0 | 2025-12-21 | Versión inicial extrapolada de FPN-P2-001 | Tech Committee |

---

**FIN DEL DOCUMENTO**

Para consultas o propuestas de cambio, contactar al Comité de Nomenclatura o abrir ADR.
