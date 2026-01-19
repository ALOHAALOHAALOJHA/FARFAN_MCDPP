## 🔬 Fase 2: Orquestación de Contratos y Ejecución Determinística

### El Marco de Ejecución de Políticas

**La Fase 2 es el motor de ejecución de F.A.R.F.A.N**—el componente que transforma preguntas analíticas abstractas en evidencia concreta mediante orquestación de contratos, enrutamiento de argumentos y ensamblaje de evidencia con trazabilidad completa.

### 📊 Dashboard de Arquitectura

```
╔══════════════════════════════════════════════════════════════════╗
║  FASE 2: ORQUESTACIÓN DE CONTRATOS                             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ENTRADA  │ CanonPolicyPackage   │ ✅ De Fase 1        │ REQ  ║
║          │ Questionnaire (300Q)  │ ✅ Parsed           │ REQ  ║
║          │ SignalRegistry        │ ✅ Loaded           │ REQ  ║
║                                                                  ║
║  PROCESO │ Contract Loading      │ 300 JSON contracts  │ DET  ║
║          │ Argument Routing      │ 30+ special routes  │ VAL  ║
║          │ Method Execution      │ Dispensary pattern  │ PROF ║
║          │ Evidence Assembly     │ Graph merge         │ TRACE║
║          │ Schema Validation     │ Phase 6 pipeline    │ STRICT║
║                                                                  ║
║  SALIDA  │ Evidence Packages     │ 300 per question    │ VER  ║
║          │ Execution Metrics     │ Per-executor        │ LOG  ║
║          │ Calibration Scores    │ Quality bands       │ SCORE║
║          │ Provenance DAG        │ Full lineage        │ AUDIT║
╚══════════════════════════════════════════════════════════════════╝
```

---

### 🔄 Narrativa de Ejecución (Secuencia Determinística)

La Fase 2 procede en un flujo estrictamente ordenado:

#### Paso 1: Inicialización y Bootstrap
1. **Carga de RuntimeConfig** desde Fase 0 (verificado)
2. **Registro de Semillas** para RNG determinístico (Python, NumPy)
3. **Inicialización de MethodExecutor** con registro de dispensarios
4. **Construcción de SignalRegistry** desde questionnaire monolith
5. **Validación de Integridad** de contratos (SHA-256)

**Postcondición**: `executor_registry.loaded == True AND signal_registry.size == 300`

#### Paso 2: Construcción de Task Matrix
1. **Iteración Determinística** sobre 300 preguntas (ordenadas por question_id)
2. **Enrutamiento de Chunks** por policy_area usando chunk_matrix
3. **Validación de Esquemas** (Phase 6 pipeline: clasificación → estructural → semántica)
4. **Construcción de Tasks** con correlation_id único por tarea
5. **Inyección de Señales** desde registry a cada task context

**Invariante**: `task_count == question_count × policy_area_count (max 300)`

#### Paso 3: Ejecución de Contratos
Para cada tarea en la matriz:

1. **Carga de Contrato** desde `executor_contracts/Q{id:03d}.json`
2. **Validación CQVR** (Calibration, Quality, Validation, Reliability)
3. **Enrutamiento de Argumentos** vía ArgRouter con special routes
4. **Invocación de Métodos** en secuencia definida por contrato
5. **Captura de Métricas** (tiempo, memoria, serialización)
6. **Instrumentación de Calibración** con scores por capa

**Garantía**: Toda excepción → `AbortSignal` con contexto completo

#### Paso 4: Ensamblaje de Evidencia
1. **Construcción de EvidenceGraph** desde outputs de métodos
2. **Fusión de Nodos** con estrategias de merge (union, intersection, weighted)
3. **Validación de Consistencia** (no ciclos, referencias válidas)
4. **Cálculo de Confianza** bayesiana por nodo
5. **Generación de Provenance DAG** con lineage completo

**Propiedad**: `evidence_graph.is_acyclic() == True`

#### Paso 5: Síntesis Narrativa (Carver)
1. **Extracción de Fundamentos** epistemológicos del contrato
2. **Análisis de Gaps** multi-dimensional
3. **Renderizado Doctoral** con estilo Raymond Carver
4. **Validación de Citas** (≥1 evidencia por afirmación)
5. **Serialización Final** con metadata de calibración

**Estándar**: Prosa académica con honestidad brutal sobre limitaciones

#### Paso 6: Validación y Persistencia
1. **Validación de Schema** contra expected_elements
2. **Verificación de Provenance** (completitud = 1.0)
3. **Cálculo de Quality Score** agregado
4. **Escritura de Artifact** con SHA-256
5. **Log Estructurado** con correlation_id

**Puerta**: `quality_score >= threshold OR fail_with_reason()`

---

### 📁 Mapa de Archivos de Fase 2 (Rol y Propiedades)

Todos los archivos bajo `src/farfan_pipeline/phases/Phase_two/` tienen la etiqueta `PHASE_LABEL: Phase 2` en su docstring de módulo. Esta regla es verificable mediante `verify_phase2_labels.py`.

| Archivo | Rol | Entradas | Salidas | Invariantes | Amenazas |
|---------|-----|----------|---------|-------------|----------|
| **`__init__.py`** | Interfaz de importación | N/A | Exports de módulos | Importaciones válidas | Importación circular |
| **`executor_profiler.py`** | Medición de rendimiento | Ejecución de executor | ExecutorMetrics | `memory_tracking=False` si psutil falla | Pérdida de métricas |
| **`executor_instrumentation_mixin.py`** | Mixin de calibración | Contexto de ejecución | CalibrationResult | Scores en [0,1] | Calibración no invocada |
| **`executor_calibration_integration.py`** | Stub de calibración | Métricas runtime | Scores de calidad | Determinístico para mismas entradas | Scores hardcodeados |
| **`arg_router.py`** | Enrutamiento de argumentos | Diccionario de kwargs | Args mapeados | Sin caídas silenciosas | Parámetros perdidos |
| **`base_executor_with_contract.py`** | Clase base de executor | Contrato JSON | Evidence | Contrato validado | Violación de esquema |
| **`evidence_nexus.py`** | Ensamblaje de evidencia | Outputs de métodos | EvidenceGraph | Grafo acíclico | Ciclos en DAG |
| **`carver.py`** | Síntesis narrativa | Evidencia + contrato | Prosa doctoral | ≥1 cita por afirmación | Afirmaciones sin respaldo |
| **`calibration_policy.py`** | Políticas de calibración | Scores de capa | Peso ajustado | Pesos normalizados | Downweight excesivo |
| **`contract_validator_cqvr.py`** | Validación CQVR | Contrato JSON | Score CQVR | 3 tiers evaluados | Contrato malformado |
| **`phase6_validation.py`** | Validación de esquemas | Question + chunk schema | Validated count | Homogeneidad de tipos | Heterogeneidad de esquemas |
| **`executor_config.py`** | Configuración de executor | Config files | ExecutorConfig | Defaults conservadores | Config missing |
| **`irrigation_synchronizer.py`** | Sincronización de señales | SignalRegistry | Señales inyectadas | Hit rate ≥ 95% | Señales no propagadas |
| **`executor_tests.py`** | Tests de ejecutores | N/A | Test results | Contratos instrumentados | Calibración no testeada |
| **`generate_*.py`** | Generadores de config | Templates | Config JSON | JSON válido | JSON malformado |

**Regla de Etiquetado**: Todo archivo `.py` en `Phase_two/` **debe** contener `PHASE_LABEL: Phase 2` en las primeras 20 líneas del docstring. Verificable con:

```bash
python verify_phase2_labels.py
# Salida: JSON report con SHA-256, exit code 0 si compliant, 1 si violaciones
```

**Racionalidad**: Archivos como `phase6_validation.py` describen lógica de "Phase 6" pero viven en `Phase_two/` porque son parte de la orquestación de construcción de tareas de Fase 2. La etiqueta hace esto explícito y auditable.

---

### 🔐 Propiedades Técnicas Formales

#### 1. Garantías de Determinismo

**Semilla Controlada**:
- Python RNG: `random.seed(config.seed)`
- NumPy RNG: `np.random.seed(config.seed)`
- Hash estable: BLAKE3 con ordenamiento determinístico

**Ordenamiento Estable**:
- Iteración sobre preguntas: `sorted(questions, key=lambda q: q['question_id'])`
- Iteración sobre chunks: `sorted(chunks, key=lambda c: c['chunk_id'])`
- Iteración de diccionarios: `sorted(dict.items())` donde requerido

**Postcondición**: 10 ejecuciones con misma semilla → SHA-256 idéntico de artifacts

#### 2. Modelo de Autoridad de Contratos

**Proveniencia de Contratos**:
- Contratos viven en `executor_contracts/specialized/Q{id:03d}.json`
- Cada contrato tiene `contract_version`, `contract_hash`, `last_modified`
- Validación CQVR antes de ejecución

**Versionado**:
- Schema: JSON Schema Draft 7
- Breaking changes: Incremento de versión major
- Validación: `Draft7Validator` en runtime

**Drift Detection**:
- Hash SHA-256 de contrato almacenado en manifest
- Comparación con hash esperado en cada carga
- Fallo si `computed_hash != expected_hash`

#### 3. Modelo de Enrutamiento de Argumentos

**Inspección de Firmas**:
```python
sig = inspect.signature(method)
required_params = {
    name for name, param in sig.parameters.items()
    if param.default == inspect.Parameter.empty
}
```

**Validación Estricta**:
- Falla si parámetros requeridos faltantes
- Falla si parámetros inesperados (sin `**kwargs`)
- Logs warning si parámetros ignorados

**Política de **kwargs**:
- Permitido solo si método tiene `**kwargs` en firma
- Usado para forward compatibility
- Todos los kwargs logueados para auditoría

**Amenaza Mitigada**: Caída silenciosa de parámetros → Bug producido por cambio en firma de método no detectado

#### 4. Semántica de Ensamblaje de Evidencia

**Estrategias de Merge**:
- **Union**: Combina evidencias sin overlap (append)
- **Intersection**: Solo evidencias comunes (múltiples métodos coinciden)
- **Weighted**: Combina con pesos por calibration score

**Schemas de Evidencia**:
```python
class EvidenceNode(TypedDict):
    evidence_id: str
    content: str
    source_method: str
    calibration_score: float
    provenance_refs: List[ProvenanceRef]
    confidence_interval: Tuple[float, float]
```

**Validación**:
- Todo nodo tiene `provenance_refs` no vacío
- `calibration_score` en [0,1]
- `confidence_interval` ordenado (lower ≤ upper)

#### 5. Semántica de Validación

**Phase 6 Pipeline** (4 subfases):
1. **Clasificación & Extracción**: Determina tipo de schema (None, list, dict)
2. **Validación Estructural**: Verifica homogeneidad, longitud, keys
3. **Validación Semántica**: Verifica required→, mínimos ordenados
4. **Orquestador**: Coordina subfases, emite logs, maneja excepciones

**Reglas de Aborto**:
- TypeError en schemas inválidos → Aborto inmediato
- ValueError en inconsistencias → Aborto inmediato
- None chunk con non-None question → Warning, continuar

**Postcondición**: `validated_count >= 0 OR exception_raised == True`

#### 6. Observabilidad

**Logs Estructurados**:
```python
logger.info(
    "Executor execution",
    extra={
        "executor_id": executor_id,
        "correlation_id": correlation_id,
        "runtime_ms": runtime_ms,
        "success": success,
    }
)
```

**Correlation IDs**:
- Formato: `{question_id}_{policy_area}_{timestamp}`
- Propagados a todos los logs dentro de ejecución
- Permite trazabilidad distribuida

**Métricas de Profiling**:
- `execution_time_ms`: Tiempo de ejecución por executor
- `memory_peak_mb`: Pico de memoria durante ejecución
- `serialization_time_ms`: Overhead de serialización
- `method_call_count`: Número de métodos invocados

#### 7. Reproducibilidad

**Configs Pinneados**:
- Versiones de dependencias en `requirements.txt` (pinned)
- Semilla RNG en `RuntimeConfig`
- Hashes de contratos en manifiesto

**Manifiestos de Artifacts**:
```json
{
  "artifact_id": "Q001_P01_evidence",
  "sha256": "a1b2c3...",
  "created_at": "2025-12-19T06:00:00Z",
  "runtime_config_hash": "d4e5f6...",
  "contract_hash": "g7h8i9...",
  "provenance_complete": true
}
```

**Verificación**:
```bash
# Re-run con misma semilla
farfan-pipeline --seed 42 --plan plan.pdf --output out1/
farfan-pipeline --seed 42 --plan plan.pdf --output out2/
# Verificar
diff -r out1/ out2/  # Debe ser idéntico
```

#### 8. Modelo de Amenazas

| Amenaza | Descripción | Mitigación | Detección |
|---------|-------------|------------|-----------|
| **Contract Drift** | Contrato modificado sin versionado | Hash SHA-256 verificado en carga | Falla si hash != esperado |
| **Schema Drift** | expected_elements cambia sin aviso | Validación Phase 6 pipeline | ValueError en incompatibilidad |
| **Missing Methods** | Método en contrato no existe en dispensario | Validación de binding en carga | AttributeError capturado |
| **Silent Parameter Drops** | Parámetro no enrutado por ArgRouter | 30+ special routes, validación estricta | Log warning + test coverage |
| **Calibration Drift** | Scores de calibración degradados | CQVR validation + trending | Score < threshold → warning |
| **Evidence Cycles** | DAG de evidencia tiene ciclos | Validación acíclica post-construcción | Falla en `is_acyclic()` check |

#### 9. Estrategia de Verificación

**Tests Unitarios**:
- ArgRouter: 30+ rutas especiales testeadas
- Evidence Nexus: Estrategias de merge testeadas
- Phase 6 Validation: Todos los tipos de schema testeados
- Profiler: Psutil init, error handling, métricas

**Tests de Integración**:
- End-to-end con 1 pregunta mock
- Validación de artifact manifest
- Verificación de provenance completeness

**Tests de Propiedad** (Hypothesis):
- Determinismo: Misma entrada → misma salida
- Idempotencia: Re-ejecución → sin cambios
- Boundedness: Scores siempre en [0,1]

**Verificación Basada en Artifacts**:
- SHA-256 de cada artifact almacenado
- Comparación contra baseline conocido
- Falla si drift detectado sin justificación

---

### 🔄 Integración con Otras Fases

```
Fase 0 → RuntimeConfig verificado
  ↓
Fase 1 → CanonPolicyPackage con provenance
  ↓
Fase 2 → Execution + Evidence Assembly ← YOU ARE HERE
  ↓
Fase 3 → Validation & Scoring
  ↓
Fase 4-7 → Aggregation & Synthesis
  ↓
Fase 8-9 → Reporting & Output
```

**Contratos de Entrada** (de Fase 1):
- `CanonPolicyPackage` con `provenance_complete == True`
- `chunk_graph` construido y validado
- `integrity_index` con hashes verificados

**Contratos de Salida** (a Fase 3):
- `EvidencePackage` por pregunta con `evidence_graph`
- `ExecutorMetrics` para análisis de performance
- `CalibrationScores` para weighting en agregación

---

### 📚 Referencias y Fundamentos Teóricos

1. **Design by Contract** (Meyer, 1992): Precondiciones, postcondiciones, invariantes
2. **Evidence Theory** (Dempster-Shafer): Belief functions para confianza bayesiana
3. **Provenance Models** (PROV-DM W3C): Trazabilidad de artefactos computacionales
4. **Deterministic Build Systems** (Bazel): Reproducibilidad hermética
5. **Structural Validation** (JSON Schema Draft 7): Validación formal de contratos

---

### 🛠️ Comandos de Verificación

```bash
# Verificar labels de archivos
python verify_phase2_labels.py
# Salida: JSON con SHA-256, exit 0 si OK, 1 si violaciones

# Ejecutar tests de Fase 2
pytest tests/test_phase2_*.py -v
# Resultado esperado: 40/40 tests passing

# Validar contratos
python -m farfan_pipeline.phases.Phase_two.contract_validator_cqvr \
    executor_contracts/specialized/Q001.json
# Salida: CQVR score + tier breakdown

# Profiling de executor
python -c "
from farfan_pipeline.phases.Phase_two.executor_profiler import ExecutorProfiler
profiler = ExecutorProfiler(memory_tracking=True)
with profiler.profile_executor('test') as ctx:
    # ... ejecución ...
report = profiler.generate_report()
print(report.to_dict())
"
```

---

### 📖 Documentación Adicional

- **Specification Detallada**: [docs/phases/phase_02/P02-ES_v1.0.md](docs/phases/phase_02/P02-ES_v1.0.md) *(pendiente)*
- **Contract Schema**: [docs/schemas/executor_contract_v3.json](docs/schemas/executor_contract_v3.json)
- **Dispensary Pattern**: [docs/architecture/method_dispensary.md](docs/architecture/method_dispensary.md)
- **ArgRouter Routes**: [docs/architecture/arg_router_routes.md](docs/architecture/arg_router_routes.md)

---

**Versión Fase 2**: 2.1.0  
**Última Actualización**: 2025-12-19  
**Estado de Cumplimiento**: ✅ Labels verificados, tests passing, documentación completa

