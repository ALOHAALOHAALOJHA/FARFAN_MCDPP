# SISAS 5.0 - Agenda de Irrigación por Fase

**Documento**: SISAS_5.0_IRRIGATION_AGENDA.md
**Versión**: 1.0.0
**Fecha**: 2026-01-18
**Status**: ACTIVO

---

## Resumen Ejecutivo

Este documento define la **agenda de irrigación por fase** que especifica cómo los 4 pilares de SISAS 5.0 se integran con el pipeline principal F.A.R.F.A.N (Phase 0-9).

### Problema

Los 4 pilares SISAS están implementados pero **desconectados** del pipeline:
- PILAR 1 DEPURACIÓN → No se ejecuta antes de irrigation
- PILAR 2 ORQUESTACIÓN → No se integra con MainOrchestrator
- PILAR 3 WIRING → No se usa para configurar vehicles
- PILAR 4 ARMONIZACIÓN → No se valida después de cambios

### Solución

Definir **puntos de integración** específicos para cada pilar en cada fase del pipeline.

---

## Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 SISAS 5.0 INTEGRATION ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐                                                       │
│   │ MainOrchestrator│  ← Orquesta Phase 0-9 (nivel de FASES)               │
│   └────────┬────────┘                                                       │
│            │                                                                │
│            ▼                                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    PHASE EXECUTION LIFECYCLE                         │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │                                                                     │   │
│   │  1. BEFORE PHASE:                                                    │   │
│   │     ┌──────────────────────┐                                         │   │
│   │     │ PILAR 1: DEPURACIÓN   │ ← DepurationValidator.depurate(files)   │   │
│   │     │   (Validar archivos)  │                                         │   │
│   │     └──────────┬───────────┘                                         │   │
│   │                │                                                     │   │
│   │                ▼                                                     │   │
│   │  2. PHASE START:                                                     │   │
│   │     ┌──────────────────────┐                                         │   │
│   │     │ PILAR 3: WIRING      │ ← WiringConfiguration.validate_wiring() │   │
│   │     │   (Configurar vehicles│                                         │   │
│   │     │    → consumers)      │                                         │   │
│   │     └──────────┬───────────┘                                         │   │
│   │                │                                                     │   │
│   │                ▼                                                     │   │
│   │  3. DURING PHASE:                                                    │   │
│   │     ┌──────────────────────┐                                         │   │
│   │     │ PILAR 2: ORQUESTACIÓN │ ← SISASOrchestrator.orchestrate()     │   │
│   │     │   (Orquestar irrigation│                                       │   │
│   │     │    archivo → señal)    │                                         │   │
│   │     └──────────┬───────────┘                                         │   │
│   │                │                                                     │   │
│   │                ▼                                                     │   │
│   │  4. AFTER PHASE:                                                     │   │
│   │     ┌──────────────────────┐                                         │   │
│   │     │ PILAR 4: ARMONIZACIÓN │ ← HarmonizationValidator.validate()   │   │
│   │     │   (Validar coherencia │                                         │   │
│   │     │    post-cambios)      │                                         │   │
│   │     └──────────┬───────────┘                                         │   │
│   │                │                                                     │   │
│   │                ▼                                                     │   │
│   │           [NEXT PHASE]                                               │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Punto de Integración 1: PILAR 1 DEPURACIÓN

### Ubicación en el Lifecycle
**ANTES** de que cada fase procese sus archivos de entrada.

### Responsabilidades
```python
# Antes de ejecutar Phase N:
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.validators.depuration import (
    DepurationValidator,
    FileRole
)

def depurate_phase_input(phase_id: str, file_paths: List[str]) -> DepurationResult:
    """
    Ejecuta PILAR 1 DEPURACIÓN sobre archivos de entrada de una fase.

    Checks ejecutados:
    1. EXISTENCIA - El archivo existe
    2. FORMATO JSON - JSON válido
    3. SCHEMA COMPLIANCE - Cumple schema según rol
    4. INTEGRIDAD REFERENCIAL - Referencias existen
    5. REQUISITOS DE IRRIGACIÓN - Tiene vehicle y consumers
    6. COHERENCIA DE DATOS - Datos lógicamente consistentes
    """
    validator = DepurationValidator(
        questionnaire_path="path/to/questionnaire_monolith.json",
        vehicle_registry_path="path/to/vehicle_registry.json",
        consumer_registry_path="path/to/consumer_registry.json"
    )

    results = []
    for file_path in file_paths:
        result = validator.depurate(file_path)
        if not result.is_valid:
            raise DepurationError(
                f"Archivo {file_path} falló depuración: {result.errors}"
            )
        results.append(result)

    return results
```

### Integración por Fase

| Fase | Archivos a Depurar | FileRole | Ubicación de Llamada |
|------|-------------------|----------|---------------------|
| **Phase 0** | Config files | `config_file` | `execute_phase_00()` antes de cargar config |
| **Phase 1** | PDF input | `source_document` | `Phase1Executor.execute()` antes de chunking |
| **Phase 2** | CPP (60 chunks) | `canon_policy_package` | `execute_phase_02()` antes de crear ExecutionPlan |
| **Phase 3** | ExecutorResults (300) | `phase2_result` | `execute_phase_03()` antes de scoring |
| **Phase 4** | ScoredMicroQuestions (300) | `phase3_output` | `execute_phase_04()` antes de aggregation |
| **Phase 5** | DimensionScores (60) | `dimension_score` | `execute_phase_05()` antes de area integration |
| **Phase 6** | AreaScores (10) | `area_score` | `execute_phase_06()` antes de weighting |
| **Phase 7** | PolicyIndex | `policy_index` | `execute_phase_07()` antes de synthesis |
| **Phase 8** | Recommendations | `recommendation` | `execute_phase_08()` antes de report gen |
| **Phase 9** | Report artifacts | `report_artifact` | `execute_phase_09()` antes de final output |

### Código de Integración (MainOrchestrator)

```python
# En src/farfan_pipeline/orchestration/sisas_aware/main_orchestrator.py

async def _start_phase(self, phase_id: str):
    """Start a phase by publishing PhaseStartSignal."""

    # 🆕 PILAR 1: DEPURACIÓN (ANTES de procesar)
    if self.config.enable_depuration:
        input_files = self._get_phase_input_files(phase_id)
        depuration_results = await self._depurate_phase_inputs(
            phase_id, input_files
        )
        # Validar que todos los archivos pasaron depuración
        for result in depuration_results:
            if not result.is_valid:
                raise OrchestrationError(
                    f"Depuration failed for {result.file_path}: "
                    f"{result.errors}"
                )

    # ... resto del código original de Phase start
```

---

## Punto de Integración 2: PILAR 2 ORQUESTACIÓN

### Ubicación en el Lifecycle
**DURANTE** la ejecución de una fase, para orquestar la irrigación de archivos.

### Responsabilidades
```python
# Durante la ejecución de Phase N:
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.orchestration.sisas_orchestrator import (
    SISASOrchestrator,
    DependencyGraph,
    OrchestrationResult
)

def orchestrate_phase_irrigation(
    phase_id: str,
    files_to_irrigate: List[str],
    vehicles: List[str],
    consumers: List[str]
) -> OrchestrationResult:
    """
    Ejecuta PILAR 2 ORQUESTACIÓN para irrigar archivos de una fase.

    Flujo:
    1. Construir grafo de dependencias
    2. Ordenamiento topológico
    3. Ejecutar cada subfase en orden
    4. Validar estado final
    """
    orchestrator = SISASOrchestrator(
        dependency_graph=DependencyGraph(),
        bus_registry=bus_registry,
        wiring_config=wiring_config
    )

    result = orchestrator.orchestrate_full_irrigation(
        file_paths=files_to_irrigate,
        vehicles=vehicles,
        consumers=consumers,
        fail_fast=True
    )

    return result
```

### Integración por Fase

| Fase | Archivos a Irrigar | Vehicles | Consumers | Ubicación |
|------|-------------------|----------|-----------|-----------|
| **Phase 1** | 300 chunks | ChunkVehicle | QualityConsumer, SP12IrrigationConsumer | SP4-SP12 |
| **Phase 2** | 300 questions | QuestionVehicle | EvidenceConsumer, SynthesisConsumer | Task execution |
| **Phase 3** | 300 answers | AnswerVehicle | ScoringConsumer | Score calculation |
| **Phase 4** | 300 micro-questions | MicroQuestionVehicle | AggregationConsumer | Dimension aggregation |
| **Phase 5** | 60 dimension scores | DimensionScoreVehicle | AreaIntegrationConsumer | Area integration |
| **Phase 6** | 10 area scores | AreaScoreVehicle | WeightingConsumer | Policy weighting |
| **Phase 7** | Policy index | IndexVehicle | SynthesisConsumer | Index synthesis |
| **Phase 8** | Recommendations | RecommendationVehicle | ReportConsumer | Report generation |
| **Phase 9** | Report artifacts | ReportVehicle | OutputConsumer | Final output |

### Código de Integración (por fase)

```python
# Ejemplo: Phase 2 (Task Execution)

from farfan_pipeline.phases.Phase_02.phase2_50_00_task_executor import (
    TaskExecutor,
    DynamicContractExecutor
)

async def execute_phase_2_with_sisas(
    cpp: CanonPolicyPackage,
    signal_registry: SignalRegistry
) -> ExecutorResults:
    """
    Ejecuta Phase 2 con PILAR 2 ORQUESTACIÓN integrado.
    """

    # 🆕 PILAR 2: ORQUESTACIÓN DE IRRIGACIÓN
    orchestrator = SISASOrchestrator(
        dependency_graph=build_phase2_dependency_graph(),
        bus_registry=get_bus_registry(),
        wiring_config=get_wiring_config()
    )

    # Definir vehicles y consumers para Phase 2
    vehicles = [
        "QuestionVehicle",      # Genera QuestionSignal
        "EvidenceVehicle",      # Genera EvidenceSignal
        "MethodVehicle",        # Genera MethodSignal
        "SynthesisVehicle"      # Genera SynthesisSignal
    ]

    consumers = [
        "EvidenceConsumer",     # Consume QuestionSignal + EvidenceSignal
        "MethodConsumer",       # Consume QuestionSignal + MethodSignal
        "SynthesisConsumer",    # Consume todos los signals
        "CarverConsumer"        # Genera narrativas estilo Carver
    ]

    # Orquestar irrigación de 300 preguntas
    irrigation_result = orchestrator.orchestrate_full_irrigation(
        file_paths=[q.question_id for q in cpp.questions],  # 300 preguntas
        vehicles=vehicles,
        consumers=consumers,
        fail_fast=True
    )

    # Ejecutar con señales irrigadas
    executor = TaskExecutor(
        signal_registry=signal_registry,
        irrigation_context=irrigation_result.context
    )

    results = await executor.execute_all_tasks(
        irrigation_result.execution_plan
    )

    return results
```

---

## Punto de Integración 3: PILAR 3 WIRING

### Ubicación en el Lifecycle
**AL INICIO** de cada fase, antes de procesar archivos.

### Responsabilidades
```python
# Al iniciar Phase N:
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.wiring.wiring_config import (
    WiringConfiguration,
    WIRING_DEFAULTS
)

def configure_phase_wiring(phase_id: str) -> WiringValidationReport:
    """
    Ejecuta PILAR 3 WIRING para configurar conexiones vehículo→consumer.

    Mapeos validados:
    1. signal_to_bus - signal_type → bus_name
    2. vehicle_contracts - vehicle → {signal_types, buses}
    3. consumer_contracts - consumer → {subscribed_signals, bus_name}
    4. file_to_vehicle - patrón archivo → vehicle
    5. vehicle_to_consumers - vehicle → [consumers]
    """
    config = WiringConfiguration(
        signal_to_bus=WIRING_DEFAULTS["signal_to_bus"],
        vehicle_contracts=WIRING_DEFAULTS["vehicle_contracts"],
        consumer_contracts=WIRING_DEFAULTS["consumer_contracts"],
        file_to_vehicle=WIRING_DEFAULTS["file_to_vehicle"],
        vehicle_to_consumers=WIRING_DEFAULTS["vehicle_to_consumers"]
    )

    # Validar configuración
    report = config.validate_wiring()

    if not report.is_valid:
        raise WiringConfigurationError(
            f"Wiring configuration invalid for Phase {phase_id}: "
            f"{report.issues}"
        )

    return report
```

### Integración por Fase

| Fase | Vehicles Requeridos | Consumers Requeridos | Signal Types |
|------|-------------------|---------------------|--------------|
| **Phase 1** | ChunkVehicle, PDMVehicle | QualityConsumer, SP12IrrigationConsumer | ChunkSignal, PDMSignal, QualitySignal |
| **Phase 2** | QuestionVehicle, EvidenceVehicle | EvidenceConsumer, MethodConsumer, SynthesisConsumer | QuestionSignal, EvidenceSignal, MethodSignal |
| **Phase 3** | AnswerVehicle | ScoringConsumer | AnswerSignal, ScoreSignal |
| **Phase 4** | MicroQuestionVehicle | AggregationConsumer | MicroQuestionSignal, AggregationSignal |
| **Phase 5** | DimensionScoreVehicle | AreaIntegrationConsumer | DimensionSignal, AreaSignal |
| **Phase 6** | AreaScoreVehicle | WeightingConsumer | AreaSignal, WeightSignal |
| **Phase 7** | IndexVehicle | SynthesisConsumer | IndexSignal, SynthesisSignal |
| **Phase 8** | RecommendationVehicle | ReportConsumer | RecommendationSignal, ReportSignal |
| **Phase 9** | ReportVehicle | OutputConsumer | ReportSignal, OutputSignal |

### Código de Integración (WiringLoader)

```python
# En src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/wiring/wiring_loader.py

class PhaseWiringLoader:
    """
    Carga configuración de wiring específica por fase.
    """

    PHASE_WIRING_CONFIGS = {
        "phase_01": {
            "vehicles": ["ChunkVehicle", "PDMVehicle"],
            "consumers": ["QualityConsumer", "SP12IrrigationConsumer"],
            "signal_types": ["ChunkSignal", "PDMSignal", "QualitySignal"],
            "file_patterns": {
                "chunk_*.json": "ChunkVehicle",
                "pdm_*.json": "PDMVehicle"
            }
        },
        "phase_02": {
            "vehicles": ["QuestionVehicle", "EvidenceVehicle", "MethodVehicle"],
            "consumers": ["EvidenceConsumer", "MethodConsumer", "SynthesisConsumer"],
            "signal_types": ["QuestionSignal", "EvidenceSignal", "MethodSignal"],
            "file_patterns": {
                "Q*.json": "QuestionVehicle",
                "evidence_*.json": "EvidenceVehicle",
                "method_*.json": "MethodVehicle"
            }
        },
        # ... configuraciones para phases 3-9
    }

    @classmethod
    def load_wiring_for_phase(cls, phase_id: str) -> WiringConfiguration:
        """Carga configuración de wiring para una fase específica."""
        config = cls.PHASE_WIRING_CONFIGS.get(phase_id)
        if not config:
            raise ValueError(f"No wiring configuration for phase: {phase_id}")

        return WiringConfiguration(
            file_to_vehicle=config["file_patterns"],
            vehicle_to_consumers=cls._build_vehicle_consumer_map(config),
            # ... otros mapeos
        )
```

---

## Punto de Integración 4: PILAR 4 ARMONIZACIÓN

### Ubicación en el Lifecycle
**DESPUÉS** de que una fase completa su procesamiento.

### Responsabilidades
```python
# Después de ejecutar Phase N:
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.harmonization.harmonization_validator import (
    HarmonizationValidator,
    HarmonizationReport
)

def validate_phase_harmonization(
    phase_id: str,
    phase_output: Any,
    phase_metadata: Dict[str, Any]
) -> HarmonizationReport:
    """
    Ejecuta PILAR 4 ARMONIZACIÓN para validar coherencia post-cambios.

    Dimensiones validadas:
    1. VOCABULARIO ↔ CÓDIGO - signal_types en código vs definición
    2. CÓDIGO ↔ METADATOS - implementación vs descripción
    3. METADATOS ↔ DATOS - esquemas vs datos reales
    4. WIRING ↔ CÓDIGO - configuración vs implementación
    5. SCHEMAS ↔ DATOS - validación de estructura
    6. DEPENDENCIES ↔ ORQUESTACIÓN - dependencias vs flujo real
    """
    validator = HarmonizationValidator(
        vocabulary_path="path/to/signal_vocabulary.json",
        codebase_root="src/farfan_pipeline",
        wiring_config=wiring_config
    )

    report = validator.validate_full_harmonization()

    if not report.is_harmonized:
        # Emitir advertencia pero no fallar la fase
        logger.warning(
            f"Harmonization issues detected in Phase {phase_id}: "
            f"{report.issues}"
        )

    return report
```

### Integración por Fase

| Fase | Dimensiones Críticas | Validaciones Específicas |
|------|---------------------|--------------------------|
| **Phase 1** | SCHEMAS↔DATOS, METADATOS↔DATOS | 300 chunks válidos, PDM metadata completo |
| **Phase 2** | DEPENDENCIES↔ORQUESTACIÓN, WIRING↔CÓDIGO | 300 tasks ejecutados, vehicles conectados |
| **Phase 3** | VOCABULARIO↔CÓDIGO, CÓDIGO↔METADATOS | Scores válidos, signals correctamente tipados |
| **Phase 4** | SCHEMAS↔DATOS | Aggregation válida, 60 dimension scores |
| **Phase 5** | DEPENDENCIES↔ORQUESTACIÓN | Area integración consistente |
| **Phase 6** | WIRING↔CÓDIGO | Weighting configuration coherente |
| **Phase 7** | METADATOS↔DATOS | Index metadata completo |
| **Phase 8** | VOCABULARIO↔CÓDIGO | Recommendations bien formadas |
| **Phase 9** | SCHEMAS↔DATOS, CÓDIGO↔METADATOS | Report válido, output consistente |

### Código de Integración (MainOrchestrator)

```python
# En src/farfan_pipeline/orchestration/sisas_aware/main_orchestrator.py

def _handle_phase_complete_signal(self, signal: PhaseCompleteSignal):
    """Handle PhaseCompleteSignal from a phase."""

    # ... código existente ...

    # 🆕 PILAR 4: ARMONIZACIÓN (DESPUÉS de completar)
    if self.config.enable_harmonization:
        harmonization_report = self._validate_phase_harmonization(
            phase_id=phase_id,
            phase_output=signal.completion_metadata
        )

        # Registrar issues de harmonización
        if not harmonization_report.is_harmonized:
            self._harmonization_issues[phase_id] = harmonization_report.issues

    # ... resto del código ...
```

---

## Orden de Ejecución de Pilares

### Por Fase (Secuencia Completa)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE EXECUTION WITH 4 PILLARS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase N                                                                    │
│    │                                                                       │
│    ├──► [ANTES] PILAR 1: DEPURACIÓN                                        │
│    │         └─ DepurationValidator.depurate(input_files)                  │
│    │                                                                       │
│    ├──► [INICIO] PILAR 3: WIRING                                           │
│    │         └─ WiringConfiguration.validate_wiring()                      │
│    │                                                                       │
│    ├──► [DURANTE] PILAR 2: ORQUESTACIÓN                                    │
│    │         └─ SISASOrchestrator.orchestrate_full_irrigation()            │
│    │              ├─ Cargar archivos                                       │
│    │              ├─ Ejecutar vehicles                                     │
│    │              ├─ Publicar signals                                     │
│    │              └─ Consumir signals                                     │
│    │                                                                       │
│    └──► [DESPUÉS] PILAR 4: ARMONIZACIÓN                                    │
│              └─ HarmonizationValidator.validate_full_harmonization()      │
│                                                                             │
│  [NEXT PHASE]                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Timeline de Ejecución (Ejemplo Phase 2)

```
T0: Phase 2 Start
│
├─ T0+0ms:   PILAR 1 DEPURACIÓN
│            └─ Validar CPP (60 chunks)
│            └─ Validar questionnaire (300 questions)
│            └─ Validar contracts (300 JSONs)
│
├─ T0+50ms:  PILAR 3 WIRING
│            └─ Configurar QuestionVehicle → EvidenceConsumer
│            └─ Configurar EvidenceVehicle → MethodConsumer
│            └─ Validar signal contracts
│
├─ T0+100ms: PILAR 2 ORQUESTACIÓN
│            │
│            ├─ Load 300 questions
│            ├─ Route to chunks (ChunkMatrix lookup)
│            ├─ Resolve signals (SISAS integration)
│            ├─ Execute 300 tasks
│            │   ├─ N1-EMP (Empirical extraction)
│            │   ├─ N2-INF (Inference)
│            │   └─ N3-AUD (Auditing)
│            └─ Collect 300 results
│
├─ T0+5000ms: PILAR 4 ARMONIZACIÓN
│             └─ Validar VOCABULARIO↔CÓDIGO
│             └─ Validar SCHEMAS↔DATOS
│             └─ Validar DEPENDENCIES↔ORQUESTACIÓN
│
T0+5100ms: Phase 2 Complete → Phase 3 Start
```

---

## Configuración de Pilares

### Habilitar/Deshabilitar Pilares

```python
# En src/farfan_pipeline/orchestration/sisas_aware/main_orchestrator.py

@dataclass
class OrchestratorConfiguration:
    """Configuration for the orchestrator."""

    # Configuración existente
    mode: OrchestratorMode = OrchestratorMode.HYBRID
    max_parallel_phases: int = 4
    # ...

    # 🆕 Configuración de 4 pilares SISAS
    enable_pillar_1_depuration: bool = True
    enable_pillar_2_orchestration: bool = True
    enable_pillar_3_wiring: bool = True
    enable_pillar_4_harmonization: bool = True

    # Modos de fallo
    depuration_fail_fast: bool = True        # Fallar si depuration falla
    harmonization_warn_only: bool = True     # Solo advertir si harmonization falla
```

### Paths de Configuración

```python
# Paths a configuraciones de pilares
SISAS_5_0_CONFIG = {
    "pillar_1": {
        "questionnaire_path": "canonic_questionnaire_central/questionnaire_monolith.json",
        "vehicle_registry": "artifacts/registries/vehicle_registry.json",
        "consumer_registry": "artifacts/registries/consumer_registry.json",
        "schema_dir": "artifacts/schemas/"
    },
    "pillar_2": {
        "dependency_graph_path": "artifacts/dependency_graphs/",
        "orchestration_plan_path": "artifacts/orchestration_plans/"
    },
    "pillar_3": {
        "wiring_config_path": "artifacts/wiring/wiring_config.json",
        "signal_vocabulary_path": "artifacts/signals/signal_vocabulary.json"
    },
    "pillar_4": {
        "codebase_root": "src/farfan_pipeline",
        "harmonization_rules_path": "artifacts/harmonization/rules.json"
    }
}
```

---

## Plan de Implementación

### Fase 1: Infraestructura (1-2 semanas)
- [ ] Crear `PhaseWiringLoader` para cargar configs por fase
- [ ] Integrar PILAR 1 en `MainOrchestrator._start_phase()`
- [ ] Integrar PILAR 4 en `MainOrchestrator._handle_phase_complete_signal()`

### Fase 2: Integración por Fase (2-3 semanas)
- [ ] Integrar PILAR 2 en Phase 1 (ChunkVehicle + PDMVehicle)
- [ ] Integrar PILAR 2 en Phase 2 (QuestionVehicle + EvidenceVehicle)
- [ ] Integrar PILAR 2 en Phase 3-9 (vehicles y consumers específicos)

### Fase 3: Validación (1 semana)
- [ ] Crear tests de integración end-to-end
- [ ] Validar que los 4 pilares se ejecutan en orden correcto
- [ ] Validar que las fases completan exitosamente

### Fase 4: Optimización (1 semana)
- [ ] Paralelizar PILAR 1 (depuración de múltiples archivos)
- [ ] Optimizar PILAR 2 (caching de dependency graphs)
- [ ] Optimizar PILAR 4 (validación incremental)

---

## Métricas de Éxito

### Cobertura de Pilares
- **PILAR 1**: 100% de archivos de entrada depurados
- **PILAR 2**: 100% de fases usan SISASOrchestrator
- **PILAR 3**: 100% de fases tienen wiring configurado
- **PILAR 4**: 100% de fases validan harmonización

### Métricas de Calidad
- **Tasa de fallo en PILAR 1**: < 0.1% (archivos inválidos rechazados)
- **Tiempo de PILAR 2**: < 5% overhead en tiempo de ejecución
- **Tiempo de PILAR 3**: < 100ms (validación de wiring)
- **Tiempo de PILAR 4**: < 200ms (validación de harmonización)

### Métricas de Integración
- **Número de fases integradas**: 10 (Phase 0-9)
- **Número de vehicles configurados**: ~30
- **Número de consumers configurados**: ~25
- **Número de signal types validados**: ~50

---

## Ejemplo Completo: Phase 2

```python
# Ejemplo completo de Phase 2 con los 4 pilares integrados

async def execute_phase_2_complete(
    cpp: CanonPolicyPackage,
    orchestrator_config: OrchestratorConfiguration
) -> ExecutorResults:
    """
    Ejecuta Phase 2 con los 4 pilares SISAS completamente integrados.
    """

    # =========================================================================
    # ANTES DE PHASE 2: PILAR 1 - DEPURACIÓN
    # =========================================================================
    if orchestrator_config.enable_pillar_1_depuration:
        logger.info("Phase 2: Ejecutando PILAR 1 DEPURACIÓN")

        depuration_validator = DepurationValidator(
            questionnaire_path="canonic_questionnaire_central/questionnaire_monolith.json",
            vehicle_registry_path="artifacts/registries/vehicle_registry.json",
            consumer_registry_path="artifacts/registries/consumer_registry.json"
        )

        # Depurar CPP
        cpp_result = depuration_validator.depurate(
            cpp.metadata["source_path"],
            role=FileRole.CANON_POLICY_PACKAGE
        )
        if not cpp_result.is_valid:
            raise DepurationError(f"CPP depuration failed: {cpp_result.errors}")

        # Depurar questionnaire
        q_result = depuration_validator.depurate(
            "canonic_questionnaire_central/questionnaire_monolith.json",
            role=FileRole.QUESTIONNAIRE_MONOLITH
        )
        if not q_result.is_valid:
            raise DepurationError(f"Questionnaire depuration failed: {q_result.errors}")

    # =========================================================================
    # INICIO DE PHASE 2: PILAR 3 - WIRING
    # =========================================================================
    if orchestrator_config.enable_pillar_3_wiring:
        logger.info("Phase 2: Ejecutando PILAR 3 WIRING")

        wiring_config = PhaseWiringLoader.load_wiring_for_phase("phase_02")
        wiring_report = wiring_config.validate_wiring()

        if not wiring_report.is_valid:
            raise WiringConfigurationError(
                f"Wiring validation failed: {wiring_report.issues}"
            )

    # =========================================================================
    # DURANTE PHASE 2: PILAR 2 - ORQUESTACIÓN
    # =========================================================================
    if orchestrator_config.enable_pillar_2_orchestration:
        logger.info("Phase 2: Ejecutando PILAR 2 ORQUESTACIÓN")

        # Crear SISASOrchestrator
        sisas_orchestrator = SISASOrchestrator(
            dependency_graph=build_phase2_dependency_graph(),
            bus_registry=get_bus_registry(),
            wiring_config=wiring_config
        )

        # Ejecutar irrigación completa
        irrigation_result = sisas_orchestrator.orchestrate_full_irrigation(
            file_paths=[q.question_id for q in cpp.questions],  # 300 preguntas
            vehicles=["QuestionVehicle", "EvidenceVehicle", "MethodVehicle"],
            consumers=["EvidenceConsumer", "MethodConsumer", "SynthesisConsumer"],
            fail_fast=True
        )

        # Validar resultado
        if not irrigation_result.is_success:
            raise OrchestrationError(
                f"Irrigation failed: {irrigation_result.errors}"
            )

    # =========================================================================
    # EJECUTAR TAREAS (con signals irrigados)
    # =========================================================================
    logger.info("Phase 2: Ejecutando 300 tareas con señales irrigadas")

    task_executor = TaskExecutor(
        signal_registry=build_signal_registry(),
        irrigation_context=irrigation_result.context if irrigation_result else None
    )

    results = await task_executor.execute_all_tasks(
        irrigation_result.execution_plan if irrigation_result else None
    )

    # =========================================================================
    # DESPUÉS DE PHASE 2: PILAR 4 - ARMONIZACIÓN
    # =========================================================================
    if orchestrator_config.enable_pillar_4_harmonization:
        logger.info("Phase 2: Ejecutando PILAR 4 ARMONIZACIÓN")

        harmonization_validator = HarmonizationValidator(
            vocabulary_path="artifacts/signals/signal_vocabulary.json",
            codebase_root="src/farfan_pipeline",
            wiring_config=wiring_config
        )

        harmonization_report = harmonization_validator.validate_full_harmonization()

        if not harmonization_report.is_harmonized:
            logger.warning(
                f"Harmonization issues detected: {harmonization_report.issues}"
            )

    # =========================================================================
    # RETORNAR RESULTADOS
    # =========================================================================
    logger.info("Phase 2: Completado con éxito")

    return results
```

---

## Referencias

- **SISAS 5.0 Specification**: `/docs/SISAS_5.0_SPECIFICATION.md`
- **MainOrchestrator**: `src/farfan_pipeline/orchestration/sisas_aware/main_orchestrator.py`
- **SISASOrchestrator**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/orchestration/sisas_orchestrator.py`
- **DepurationValidator**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/validators/depuration.py`
- **WiringConfiguration**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/wiring/wiring_config.py`
- **HarmonizationValidator**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/harmonization/harmonization_validator.py`

---

**Status del Documento**: ACTIVO
**Última Actualización**: 2026-01-18
**Maintainer**: SISAS Core Team
