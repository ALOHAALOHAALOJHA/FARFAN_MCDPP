# 🏛️ PHASE 0: BOOTSTRAP & VALIDATION (Garantía Constitucional)

**Estado**: ✅ **VALIDADO CON CÓDIGO FUENTE**  
**Fecha de Auditoría**: 2025-12-07  
**Versión del Schema**: `1.0.0` (phase0_input_validation.py L69)

---

## 📋 PURPOSE

**Garantía Constitucional** - Establecer condiciones inmutables de ejecución antes de iniciar el análisis, asegurando la trazabilidad, el determinismo y la integridad de la configuración base.

Esta fase opera como el **control de calidad constitucional** del pipeline: si falla, **NADA** puede ejecutarse. No hay análisis parcial, no hay fallbacks. Es todo o nada.

---

## 📂 FILES (Anclados en Código Real)

### Core Implementation Files

| Archivo | Ubicación | Responsabilidad |
|---------|-----------|-----------------|
| **Phase 0 Contract** | `/src/farfan_pipeline/core/phases/phase0_input_validation.py` | Define el contrato de fase (`Phase0ValidationContract`), valida PDF y cuestionario, calcula SHA256, produce `CanonicalInput`. |
| **Boot Checks** | `/src/farfan_pipeline/core/boot_checks.py` | Validación crítica en tiempo de arranque: módulos core, calibración, spaCy model, NetworkX. |
| **Runtime Config** | `/src/farfan_pipeline/core/runtime_config.py` | Gestiona modo de ejecución (`PROD`/`DEV`/`EXPLORATORY`) y políticas de fallback estrictas. |
| **Seed Registry** | `/src/farfan_pipeline/core/orchestrator/seed_registry.py` | Inicializa determinismo mediante seeds SHA-256 derivadas de `policy_unit_id` + `correlation_id`. |
| **Phase Protocol** | `/src/farfan_pipeline/core/phases/phase_protocol.py` | Sistema de contratos abstractos (`PhaseContract`) y `PhaseManifestBuilder` para trazabilidad. |

---

## 🔄 SUB-FASES (4 Pasos Constitucionales)

### P0.0: Bootstrap & Initialization
**Tipo**: `sync`  
**Objetivo**: Inicializar sistemas base y configurar ambiente de ejecución  

| Sistema | Acción | Código Fuente |
|---------|--------|---------------|
| `RuntimeConfig` | Carga variables de entorno (`SAAAAAA_RUNTIME_MODE`, `STRICT_CALIBRATION`, etc.) para determinar modo de ejecución y políticas de fallback. | `runtime_config.py` L242-344 |
| `SeedRegistry` | Inicializa determinismo mediante derivación de seeds SHA-512 basadas en `policy_unit_id`, `correlation_id` y `component`. | `seed_registry.py` L38-100 |
| `PhaseManifestBuilder` | Prepara el rastreador de procedencia para documentar todos los pasos, contratos y hashes. | `phase_protocol.py` L294-363 |

**Evidencia de Código**:
```python
# runtime_config.py L242-256
@classmethod
def from_env(cls) -> "RuntimeConfig":
    """Parse runtime configuration from environment variables."""
    mode_str = os.getenv("SAAAAAA_RUNTIME_MODE", "prod").lower()
    try:
        mode = RuntimeMode(mode_str)
    except ValueError as e:
        raise ConfigurationError(...)
```

---

### P0.1: Input Artifact Verification
**Tipo**: `sync`  
**Objetivo**: Garantizar la inmutabilidad de los datos de entrada  

| Artefacto | Validación | Código Fuente |
|-----------|-----------|---------------|
| **PDF Input** | Verificar existencia (`pdf_path.exists()`), legibilidad, y que sea archivo regular. | `phase0_input_validation.py` L391-394 |
| **Questionnaire** | Resolver ruta del cuestionario (default: `QUESTIONNAIRE_FILE` si no se proporciona), verificar existencia. | `phase0_input_validation.py` L381-400 |
| **SHA256 Hashing** | Computar SHA256 del PDF y cuestionario usando chunks de 4096 bytes para garantizar integridad. | `phase0_input_validation.py` L436-451 |
| **PDF Metadata** | Extraer `page_count` usando PyMuPDF (fitz), validar `size_bytes > 0`. | `phase0_input_validation.py` L453-481 |

**Evidencia de Código**:
```python
# phase0_input_validation.py L406-412
pdf_sha256 = self._compute_sha256(input_data.pdf_path)
pdf_size_bytes = input_data.pdf_path.stat().st_size
pdf_page_count = self._get_pdf_page_count(input_data.pdf_path)
questionnaire_sha256 = self._compute_sha256(questionnaire_path)
```

**Invariantes Validados** (phase0_input_validation.py L223-261):
- ✅ `pdf_page_count > 0`
- ✅ `pdf_size_bytes > 0`
- ✅ `pdf_sha256` es hexadecimal de 64 caracteres
- ✅ `questionnaire_sha256` es hexadecimal de 64 caracteres
- ✅ `validation_errors` lista vacía

---

### P0.2: Runtime Dependency Checks (Boot Checks)
**Tipo**: `sync`  
**Objetivo**: Verificar dependencias críticas y calidad operativa  

| Componente | Check | Fallback Policy | Código Fuente |
|------------|-------|-----------------|---------------|
| **Contradiction Module** | Verificar disponibilidad de `PolicyContradictionDetector`. | **PROD**: Abort si falla y `ALLOW_CONTRADICTION_FALLBACK=false` (default). | `boot_checks.py` L34-58 |
| **Wiring Validator** | Verificar disponibilidad de `WiringValidator`. | **PROD**: Abort si falla y `ALLOW_VALIDATOR_DISABLE=false` (default). | `boot_checks.py` L61-84 |
| **spaCy Model** | Verificar que `preferred_spacy_model` (default: `es_core_news_lg`) esté instalado. | **PROD**: Abort si falla (no fallback). | `boot_checks.py` L87-112 |
| **Calibration Files** | Verificar existencia de `intrinsic_calibration.json`, `fusion_specification.json`, y presencia de `_base_weights`. | **PROD**: Abort si falla y `STRICT_CALIBRATION=true` (default). | `boot_checks.py` L115-183 |
| **Orchestration Metrics** | Verificar disponibilidad del contrato de métricas de orquestación. | **PROD**: Abort si falla. | `boot_checks.py` L186-216 |
| **NetworkX** | Verificar disponibilidad (soft check para graph metrics). | **Category B**: Quality degradation, no abort. | `boot_checks.py` L219-233 |

**Evidencia de Código**:
```python
# boot_checks.py L236-266
def run_boot_checks(config: RuntimeConfig) -> dict[str, bool]:
    """Run all boot checks and return results."""
    results = {}
    
    # Critical checks (Category A)
    results['contradiction_module'] = check_contradiction_module_available(config)
    results['wiring_validator'] = check_wiring_validator_available(config)
    results['spacy_model'] = check_spacy_model_available(config.preferred_spacy_model, config)
    results['calibration_files'] = check_calibration_files(config)
    results['orchestration_metrics'] = check_orchestration_metrics_contract(config)
    
    # Quality checks (Category B)
    results['networkx'] = check_networkx_available()
    
    return results
```

**Categorías de Fallback** (runtime_config.py L8-27):

| Categoría | Variables | Política PROD |
|-----------|-----------|---------------|
| **A - CRITICAL** | `ALLOW_CONTRADICTION_FALLBACK`, `ALLOW_VALIDATOR_DISABLE`, `ALLOW_EXECUTION_ESTIMATES` | ❌ **MUST FAIL FAST** - Sin fallback. |
| **B - QUALITY** | `ALLOW_NETWORKX_FALLBACK`, `ALLOW_SPACY_FALLBACK` | ⚠️ Permitido con warning explícito. |
| **C - DEVELOPMENT** | `ALLOW_DEV_INGESTION_FALLBACKS`, `ALLOW_AGGREGATION_DEFAULTS`, `ALLOW_MISSING_BASE_WEIGHTS` | 🚫 **STRICTLY FORBIDDEN** en PROD. |
| **D - OPERATIONAL** | `ALLOW_HASH_FALLBACK`, `ALLOW_PDFPLUMBER_FALLBACK` | ✅ Safe fallbacks permitidos. |

---

### P0.3: Exit Gate & Finalization
**Tipo**: `sync`  
**Objetivo**: Consolidar la Garantía Constitucional  

| Acción | Resultado | Código Fuente |
|--------|-----------|---------------|
| **Acumulación de Errores** | Si `errors` no está vacío después de P0.1 o P0.2, la ejecución **DEBE ABORTAR**. | `phase0_input_validation.py` L402-404 |
| **Construcción de `CanonicalInput`** | Empaqueta artefactos validados en objeto inmutable con `validation_passed=True`. | `phase0_input_validation.py` L418-433 |
| **Validación de Invariantes** | `Phase0ValidationContract` verifica todos los invariantes registrados. | `phase0_input_validation.py` L207-261 |
| **Registro en Manifest** | `PhaseManifestBuilder` registra contratos, timing y artefactos. | `phase_protocol.py` L309-363 |

**Evidencia de Código**:
```python
# phase0_input_validation.py L418-433
canonical_input = CanonicalInput(
    document_id=document_id,
    run_id=input_data.run_id,
    pdf_path=input_data.pdf_path,
    pdf_sha256=pdf_sha256,
    pdf_size_bytes=pdf_size_bytes,
    pdf_page_count=pdf_page_count,
    questionnaire_path=questionnaire_path,
    questionnaire_sha256=questionnaire_sha256,
    created_at=datetime.now(timezone.utc),
    phase0_version=PHASE0_VERSION,
    validation_passed=len(errors) == 0,
    validation_errors=errors,
    validation_warnings=warnings,
)
```

---

## ✅ VALIDATION (Exit Conditions)

Al final de la Fase 0, **TODAS** estas condiciones deben cumplirse:

| Condición | Verificación | Código Fuente |
|-----------|-------------|---------------|
| ✅ `bootstrap_failed = False` | Ningún error fatal en inicialización. | Implícito en `RuntimeConfig.from_env()` |
| ✅ `All env vars loaded` | `RuntimeConfig` completada sin `ConfigurationError`. | `runtime_config.py` L242-344 |
| ✅ `Seed set correctly` | Seeds determinísticas aplicadas a Python, NumPy (si disponible). | `seed_registry.py` L62-100 |
| ✅ `PDF SHA256 Computed` | Hash SHA256 del PDF calculado y validado (64 chars hex). | `phase0_input_validation.py` L407 |
| ✅ `Questionnaire SHA256 Computed` | Hash SHA256 del cuestionario calculado y validado. | `phase0_input_validation.py` L412 |
| ✅ `Boot Checks Passed` | Todas las verificaciones críticas (Category A) pasaron. | `boot_checks.py` L236-266 |
| ✅ `validation_passed == True` | `CanonicalInput` confirma éxito de validación. | `phase0_input_validation.py` L429 |

**Pydantic Validation** (phase0_input_validation.py L159-200):
- `document_id`: min_length=1
- `run_id`: min_length=1, filesystem-safe
- `pdf_sha256`: exactly 64 hexadecimal chars
- `questionnaire_sha256`: exactly 64 hexadecimal chars
- `pdf_size_bytes`: > 0
- `pdf_page_count`: > 0
- `validation_passed`: must be `True`
- `validation_errors`: must be empty list

---

## 📊 INPUT/OUTPUT CONTRACTS

### Input Contract: `Phase0Input`

```python
@dataclass
class Phase0Input:
    """Raw, unvalidated input to the pipeline."""
    pdf_path: Path
    run_id: str
    questionnaire_path: Path | None = None
```

**Validación Pydantic** (phase0_input_validation.py L90-119):
- `pdf_path`: no vacío
- `run_id`: no vacío, filesystem-safe (sin `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`)
- `questionnaire_path`: opcional

---

### Output Contract: `CanonicalInput`

```python
@dataclass
class CanonicalInput:
    """Validated, canonical input ready for Phase 1."""
    # Identity
    document_id: str
    run_id: str
    
    # Input artifacts (immutable, validated)
    pdf_path: Path
    pdf_sha256: str
    pdf_size_bytes: int
    pdf_page_count: int
    
    # Questionnaire (required for SIN_CARRETA compliance)
    questionnaire_path: Path
    questionnaire_sha256: str
    
    # Metadata
    created_at: datetime
    phase0_version: str
    
    # Validation results
    validation_passed: bool
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
```

**Invariantes Garantizados**:
1. `validation_passed == True` (L176-189)
2. `pdf_page_count > 0` (L165-168)
3. `pdf_size_bytes > 0` (L165-168)
4. `pdf_sha256` es hexadecimal de 64 caracteres (L191-199)
5. `questionnaire_sha256` es hexadecimal de 64 caracteres (L191-199)
6. `validation_errors` lista vacía (L173-188)

---

## 🚨 ERROR HANDLING

### Boot Check Errors

```python
class BootCheckError(Exception):
    """Raised when a boot check fails in strict mode."""
    
    def __init__(self, component: str, reason: str, code: str):
        self.component = component
        self.reason = reason
        self.code = code
```

**Error Codes** (boot_checks.py):
- `CONTRADICTION_MODULE_MISSING`
- `WIRING_VALIDATOR_MISSING`
- `SPACY_MODEL_MISSING`
- `CALIBRATION_DIR_MISSING`
- `CALIBRATION_FILES_MISSING`
- `CALIBRATION_BASE_WEIGHTS_MISSING`
- `CALIBRATION_PARSE_ERROR`
- `ORCHESTRATOR_MISSING`

---

### Configuration Errors

```python
class ConfigurationError(Exception):
    """Raised when runtime configuration is invalid."""
```

**Illegal Combinations in PROD** (runtime_config.py L222-239):
- `PROD + ALLOW_DEV_INGESTION_FALLBACKS=true` → **ConfigurationError**
- `PROD + ALLOW_EXECUTION_ESTIMATES=true` → **ConfigurationError**
- `PROD + ALLOW_AGGREGATION_DEFAULTS=true` → **ConfigurationError**
- `PROD + ALLOW_MISSING_BASE_WEIGHTS=true` → **ConfigurationError**

---

## 🔬 ANALOGÍA: Pre-Chequeo de Nave Espacial

La Fase 0 opera como el **pre-chequeo de una nave espacial antes del lanzamiento**:

### P0.0 (Bootstrap): Encendiendo los Sistemas de Control
- **RuntimeConfig**: Enciende los sistemas de control y fija el "modo de vuelo" (PROD/DEV/EXPLORATORY).
- **SeedRegistry**: Sincroniza los relojes internos para asegurar reproducibilidad de pruebas futuras (como GPS espacial).
- **PhaseManifestBuilder**: Inicia la caja negra (flight recorder) para documentar toda la misión.

### P0.1 (Input Verification): Revisando el Combustible y la Carga Útil
- Inspecciona el **PDF** (combustible) y el **cuestionario** (carga útil).
- Calcula **fingerprints criptográficos** (SHA256) para garantizar que no han sido alterados.
- Verifica que el PDF tiene contenido (`page_count > 0`, `size_bytes > 0`).

### P0.2 (Boot Checks): Revisando los Sistemas de Navegación Vitales
- Verifica **módulos críticos** (contradiction detector, wiring validator) - sin ellos, la nave no puede navegar.
- Verifica **calibración** (pesos base, archivos de fusión) - sin calibración, los instrumentos dan lecturas incorrectas.
- Verifica **modelos NLP** (spaCy) - sin ellos, la nave no puede "leer" las señales.

### P0.3 (Exit Gate): Autorización Final del Control de Misión
- Si **todos los checks pasaron** y **no hay advertencias críticas pendientes**, el control de misión autoriza el despegue.
- Si **hay un solo error crítico**, la misión se **ABORTA** inmediatamente (fail-fast).

**Sin esta Fase 0, el pipeline es un cohete sin pre-chequeo - puede explotar en el lanzamiento.**

---

## 🔗 EVIDENCIA DE TRIANGULACIÓN

**Archivos Auditados**:
1. ✅ `/src/farfan_pipeline/core/phases/phase0_input_validation.py` (489 líneas)
2. ✅ `/src/farfan_pipeline/core/boot_checks.py` (290 líneas)
3. ✅ `/src/farfan_pipeline/core/runtime_config.py` (539 líneas)
4. ✅ `/src/farfan_pipeline/core/orchestrator/seed_registry.py` (parcial)
5. ✅ `/src/farfan_pipeline/core/phases/phase_protocol.py` (parcial)

**READMEs Consultados**:
- [ ] `/docs/PHASE_0_README.md` (pendiente de validar)
- [ ] `CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md` (mencionado en solicitud)

**Documentación de Arquitectura**:
- [ ] `ARCHITECTURE_DIAGRAM.md`
- [ ] Documentos de contratos por fase

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### Dependencias PyMuPDF

```python
# phase0_input_validation.py L468-481
try:
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    doc.close()
    return page_count
except ImportError:
    raise ImportError(
        "PyMuPDF (fitz) required for PDF page count extraction. "
        "Install with: pip install PyMuPDF"
    )
```

**Instalación**: `pip install PyMuPDF`

---

### Variables de Ambiente Críticas

```bash
# Modo de ejecución
export SAAAAAA_RUNTIME_MODE=prod

# Categoría A - Critical
export ALLOW_CONTRADICTION_FALLBACK=false
export ALLOW_VALIDATOR_DISABLE=false
export ALLOW_EXECUTION_ESTIMATES=false

# Calibration
export STRICT_CALIBRATION=true

# Model Configuration
export PREFERRED_SPACY_MODEL=es_core_news_lg

# Processing Configuration
export EXPECTED_QUESTION_COUNT=305
export EXPECTED_METHOD_COUNT=416
export PHASE_TIMEOUT_SECONDS=300
```

---

## 🎯 PRÓXIMOS PASOS

1. ✅ **Fase 0 Validada** - Documentación alineada con código fuente.
2. ⏳ **Fase 1: SPC Ingestion** - Requiere triangulación con:
   - `phase1_spc_ingestion.py`
   - `phase1_spc_ingestion_full.py`
   - `phase1_models.py`
   - `phase1_to_phase2_adapter/`
3. ⏳ **Fases 2-10** - Pendientes de auditoría similar.

---

**🔒 ESTADO FINAL**: Fase 0 **CONSTITUCIONALEMENTE VÁLIDA** - Lista para producción.
