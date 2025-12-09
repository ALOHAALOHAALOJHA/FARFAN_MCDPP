# SECCIÓN 1: PORTADA Y METADATOS

**Título:** Compendio Técnico F.A.R.F.A.N.: Implementación Canónica
**Subtítulo:** Un Modelo Mecanicista para el Análisis de Políticas Públicas
**Versión:** 1.0.0-CANONIC
**Fecha:** 2025-11-29
**Autores:** Jules, Compilador Mecanicista IA
**Estado:** Referencia Canónica

---

## 1.1. Abstract (Resumen Ejecutivo)

Este documento constituye la especificación técnica canónica y el manual de implementación del sistema F.A.R.F.A.N. (Framework for Advanced Research and Forecasting in Algorithmic Networks). F.A.R.F.A.N. es un modelo computacional mecanicista diseñado para simular, analizar y predecir los efectos de intervenciones de políticas públicas en sistemas sociotécnicos complejos. A diferencia de los modelos puramente estadísticos, F.A.R.F.A.N. se fundamenta en la representación explícita de los mecanismos causales que gobiernan la dinámica del sistema, permitiendo una exploración contrafactual robusta y una comprensión profunda de las interdependencias entre agentes, redes y resultados.

El presente compendio ofrece una descripción exhaustiva y autocontenida de la arquitectura, el modelo matemático subyacente, los protocolos de implementación y los procedimientos operativos del sistema. Su propósito es servir como la única fuente de verdad (`single source of truth`) para desarrolladores, analistas y mantenedores, garantizando la reproducibilidad determinista de los análisis y la coherencia conceptual del framework. El documento detalla cada componente, desde la ingesta de datos y la arquitectura de capas hasta el pipeline de ejecución por fases, los métodos de calibración y parametrización, y el sistema de artefactos de datos. Se incluye el código fuente completo y comentado de los scripts críticos, así como las especificaciones para la generación de los gráficos y visualizaciones requeridos, todo ello en estricta adherencia a la estética del ecosistema AtroZ.

## 1.2. Palabras Clave

-   Política Pública
-   Modelo Mecanicista
-   Calibración de Modelos
-   Parametrización
-   F.A.R.F.A.N.
-   Ciencia Social Computacional
-   Arquitectura de Sistemas
-   Reproducibilidad Determinista
-   Análisis Contrafactual
-   Sistemas Sociotécnicos

## 1.3. Tabla de Contenidos

*Se generará dinámicamente al finalizar la redacción de todas las secciones.*

## 1.4. Cómo usar este compendio con el código real del repositorio

Este documento ahora está alineado con la topología real del código en `src/farfan_pipeline/`. Las rutas
referenciadas a continuación existen en el repositorio y son el camino canónico de ejecución:

-   **Entrypoint verificado**: `src/farfan_pipeline/entrypoint/main.py` (usa el orquestador central y valida
    Phase 2 con `validate_phase2_result`).
-   **Orquestación de fases**: `src/farfan_pipeline/core/phases/phase_orchestrator.py` (Fase 0 → Fase 1 →
    Adapter → Fase 2, con contratos en `phase0_input_validation.py`, `phase1_spc_ingestion.py`,
    `phase1_to_phase2_adapter/`).
-   **Orquestador core (11 fases)**: `src/farfan_pipeline/core/orchestrator/core.py` (integra ejecutores,
    agregadores y verificación de contratos).
-   **Ejecución batch**: `src/farfan_pipeline/core/orchestrator/batch_executor.py` (clases `BatchExecutor`,
    `BatchExecutorConfig` y tests en `tests/test_batch_executor.py`).
-   **Calibración**: `src/farfan_pipeline/core/calibration/orchestrator.py` (carga `config/intrinsic_calibration.json`
    y runtime layers de `system/config/calibration/runtime_layers.json`).
-   **Ingesta SPC**: `src/farfan_pipeline/processing/spc_ingestion.py` y adaptador
    `src/farfan_pipeline/utils/spc_adapter.py`.
-   **Agregación**: `src/farfan_pipeline/processing/aggregation.py` (Dimension, Area, Cluster, Macro).
-   **Configuración y CLI**: `system/config/config_manager.py`, `system/config/config_cli.py` y ejemplos en
    `system/config/example_usage.py`.

---

# SECCIÓN 2: VISIÓN GENERAL DEL SISTEMA F.A.R.F.A.N.

## 2.1. Propósito y Filosofía de Diseño

El sistema F.A.R.F.A.N. fue concebido para abordar una limitación fundamental en el análisis de políticas públicas tradicional: la dificultad de modelar y predecir los efectos de segundo y tercer orden que emergen de la compleja red de interacciones entre individuos, instituciones y el entorno. La filosofía de diseño se basa en dos pilares:

1.  **Mecanicismo Explícito:** En lugar de depender de correlaciones estadísticas, el modelo representa explícitamente las "tuercas y tornillos" del sistema. Cada componente, desde un agente individual hasta una estructura de red, posee un conjunto definido de estados y reglas de transición. Este enfoque permite no solo predecir *qué* sucederá, sino comprender *por qué* sucede, abriendo la puerta a un análisis causal riguroso.
2.  **Reproducibilidad Determinista:** En un entorno de alto riesgo como el de las políticas públicas, la confianza en los resultados es primordial. F.A.R.F.A.N. está diseñado para ser completamente determinista. Dada una misma semilla (`seed`), configuración y conjunto de datos de entrada, el sistema producirá bit a bit los mismos resultados. Este compendio es la clave para alcanzar dicha reproducibilidad, al documentar de forma exhaustiva cada paso y cada artefacto.

El propósito de este documento es, por tanto, servir como el "código fuente" conceptual y operativo del sistema, permitiendo a cualquier agente (humano o artificial) compilar y ejecutar el modelo de forma idéntica al diseño canónico.

## 2.2. Componentes Principales del Ecosistema

El ecosistema F.A.R.F.A.N. es un conjunto de componentes con responsabilidades explícitas y rutas reales en este
repositorio:

-   **Código fuente (`src/farfan_pipeline/`):** Implementa la lógica del pipeline (orquestación, ejecutores,
    análisis, SPC, agregación) y el runner verificado en `entrypoint/main.py`.
-   **Calibración y configuración:** JSON en `config/` y `system/config/` (runtime layers, transforms) gestionados
    por `system/config/config_manager.py` y CLI en `system/config/config_cli.py`.
-   **Especificación canónica (este compendio):** Fuente de verdad sobre arquitectura y contratos, enlazado a rutas
    reales del código.
-   **Datos y schemas (`data/`, `config/canonical_ontologies/`, `rules/`):** Esquemas y monolitos validados por
    los cargadores de `core/orchestrator/questionnaire.py` y los contratos de fases.
-   **Pipeline de ejecución:** `python -m farfan_pipeline.entrypoint.main` (o scripts en `scripts/`) que invocan
    al `PhaseOrchestrator` y al `Orchestrator` core; no existe `Makefile` en este repo.

Las interacciones siguen contratos estrictos (TypedDict y validaciones Pydantic) en límites de fase y orquestación.

## 2.3. Flujo de Procesamiento a Alto Nivel

El flujo de trabajo canónico dentro de F.A.R.F.A.N. sigue una secuencia lógica y ordenada, que se puede resumir en los siguientes macro-pasos:

1.  **Fase de Ingesta y Estructuración:** Los datos brutos son procesados y transformados en "Smart Policy Chunks" (SPCs), las unidades de análisis fundamentales del sistema.
2.  **Fase de Orquestación y Scoring:** El orquestador central (`core.py`) ejecuta una secuencia de 11 fases de análisis sobre los SPCs. Cada fase invoca "Executors" específicos que aplican la lógica de negocio y los modelos parciales definidos en el `questionnaire_monolith.json`.
3.  **Fase de Agregación:** Los resultados a nivel micro (scores de preguntas individuales) se agregan jerárquicamente para obtener métricas a nivel de dimensión, área de política y clúster.
4.  **Fase de Análisis Secundario:** Sobre los datos agregados se ejecutan análisis adicionales, como la detección de dispersión o la calibración entre pares.
5.  **Fase de Salida y Visualización:** Los resultados finales se guardan en artefactos de datos estructurados (JSON) y se generan las visualizaciones canónicas (gráficos `.png`) para el AtroZ Dashboard.

Este compendio detallará cada uno de estos pasos con una granularidad extrema en las secciones subsiguientes. La Sección 3 describirá la arquitectura de software, la Sección 4 el pipeline de fases, y las secciones posteriores se adentrarán en el modelo matemático, la implementación y los artefactos específicos.

---

# SECCIÓN 3: ARQUITECTURA DE CAPAS (LAYERED ARCHITECTURE)

## 3.1. Principios Arquitectónicos

La arquitectura de F.A.R.F.A.N. se rige por el principio de **separación de conceptos (Separation of Concerns)**. El sistema está organizado en un conjunto de capas horizontales estrictas, donde cada capa tiene una responsabilidad bien definida y solo puede interactuar con las capas directamente adyacentes a ella (preferiblemente solo con la capa inferior). Este diseño persigue los siguientes objetivos:

-   **Modularidad y Cohesión:** Agrupar la lógica relacionada en módulos cohesivos, facilitando su comprensión y mantenimiento.
-   **Bajo Acoplamiento:** Minimizar las dependencias entre componentes, permitiendo que una capa sea modificada o reemplazada con un impacto mínimo en el resto del sistema.
-   **Testabilidad:** Aislar la lógica de negocio de la infraestructura y el acceso a datos, lo que permite realizar pruebas unitarias de forma más sencilla y robusta.
-   **Claridad del Flujo de Datos:** Establecer un flujo de control y de datos unidireccional y predecible, evitando la complejidad de las dependencias circulares.

A continuación, se describe cada una de las capas, desde la más externa (interfaz de usuario/scripts) hasta la más interna (datos y utilidades).

## 3.2. Visualización de la Arquitectura

*Nota: La siguiente es una descripción textual del gráfico canónico de la arquitectura. El script para generar la imagen `.png` correspondiente se encuentra en la Sección 9. El gráfico debe mostrar cinco cajas horizontales apiladas, etiquetadas de "Capa 0" a "Capa 4", con flechas que indican las dependencias permitidas, apuntando siempre hacia abajo.*

![Arquitectura de capas](../phases/phase_1/images/canonical_architecture.png)

## 3.3. Detalle de las Capas

### 3.3.1. Capa 0: Orquestación y Punto de Entrada (Orchestration & Entrypoint Layer)

-   **Propósito:** Es la capa más externa del sistema. Su única responsabilidad es iniciar, configurar y monitorizar la ejecución del pipeline completo. No contiene ninguna lógica de negocio.
-   **Componentes Clave:**
    -   `src/farfan_pipeline/entrypoint/main.py`: Runner verificado con `VerificationManifest` y validación de Phase 2.
    -   `src/farfan_pipeline/scripts/`: Scripts auxiliares (p.ej. `run_complete_analysis_plan1.py`) que invocan al runner.
    -   `src/farfan_pipeline/core/phases/phase_orchestrator.py`: Secuencia constitucional de fases (0 → 1 → Adapter → 2).
-   **Dependencias:** Invoca directamente la **Capa 1 (Orquestador core)** y consume configuraciones desde **Capa 5**.

### 3.3.2. Capa 1: Lógica de Negocio y Análisis (Business Logic & Analysis Layer)

-   **Propósito:** Contiene la implementación de todos los algoritmos, reglas y modelos que constituyen el "cerebro" de F.A.R.F.A.N. Esta capa es la que ejecuta los análisis específicos definidos en el monolito.
-   **Componentes Clave:**
    -   `src/farfan_pipeline/core/orchestrator/core.py`: Orquestador de 11 fases con rutas de argumentos y validación.
    -   `src/farfan_pipeline/core/orchestrator/executors.py`: Ejecutores de micro-pregunta y configuración (`METHOD_SEQUENCE`).
    -   `src/farfan_pipeline/analysis/scoring.py` y `analysis/meso_cluster_analysis.py`: Lógica de scoring y análisis secundarios.
    -   `src/farfan_pipeline/core/orchestrator/batch_executor.py`: Infraestructura de ejecución batch y streaming.
-   **Dependencias:** Consume datos procesados (SPC + agregación) de la **Capa 2** y utilidades/configuración de **Capa 5**.

### 3.3.3. Capa 2: Procesamiento y Agregación de Datos (Data Processing & Aggregation Layer)

-   **Propósito:** Su responsabilidad es la manipulación, transformación y agregación de los datos. Convierte los resultados micro en macro-indicadores.
-   **Componentes Clave:**
    -   `src/farfan_pipeline/processing/spc_ingestion.py`: Pipeline SPC canónico (fase 1) que produce `CanonPolicyPackage`.
    -   `src/farfan_pipeline/utils/spc_adapter.py`: Adaptador SPC → `PreprocessedDocument` usado por el orquestador.
    -   `src/farfan_pipeline/processing/aggregation.py`: `DimensionAggregator`, `AreaPolicyAggregator`, `ClusterAggregator`, `MacroAggregator`.
-   **Dependencias:** Usa modelos/contratos de **Capa 5** (`core/types.py`, validaciones en `core/phases/phase2_types.py`).

### 3.3.4. Capa 3: Abstracción de Datos y Servicios (Data Abstraction & Services Layer)

-   **Propósito:** Actúa como un intermediario entre la lógica de negocio y las fuentes de datos físicas. Proporciona una API limpia y estable para acceder a recursos clave, ocultando los detalles de implementación (ej. si un archivo se lee del disco o de una base de datos).
-   **Componentes Clave:**
    -   `src/farfan_pipeline/core/orchestrator/questionnaire.py`: Carga y valida el monolito (SHA-256).
    -   `src/farfan_pipeline/core/orchestrator/factory.py`: Construye el `processor` con orquestador y ejecutores.
    -   `src/farfan_pipeline/core/calibration/orchestrator.py`: Evalúa calibración usando configuraciones en `config/` y `system/config/`.
-   **Dependencias:** Depende de la **Capa 5 (Datos y Configuración)** para rutas y parámetros.

### 3.3.5. Capa 4: Utilidades y Soporte (Utilities & Support Layer)

-   **Propósito:** Es la capa más fundamental. Proporciona herramientas, funciones y definiciones transversales que son utilizadas por todas las demás capas del sistema. No contiene ninguna lógica de negocio.
-   **Componentes Clave:**
    -   `src/farfan_pipeline/utils/`: Utilidades generales, adaptadores y funciones de determinismo.
    -   `src/farfan_pipeline/utils/validation/`: Modelos Pydantic y contratos.
    -   `src/farfan_pipeline/core/types.py`: Tipos compartidos (`PreprocessedDocument`, `ChunkData`).
-   **Dependencias:** Solo depende de librerías externas; provee soporte transversal a capas superiores.

### 3.3.6. Capa 5: Datos y Configuración (Data & Configuration Layer)

-   **Propósito:** No es una capa de código, sino la representación de los datos en reposo. Contiene todos los archivos de configuración, datos de entrada y especificaciones que el sistema necesita para funcionar.
-   **Componentes Clave:**
    -   `data/questionnaire_monolith.json`: Especifica preguntas, ejecutores y scoring.
    -   `config/`: Monolitos y parámetros (intrinsic calibration, catálogos canónicos, rutas).
    -   `system/config/`: Configs gestionables en runtime (p.ej. `calibration/runtime_layers.json`, `unit_transforms.json`).
-   **Dependencias:** Es la base sobre la que operan todas las demás capas. No depende de ninguna otra capa.

---

# SECCIÓN 4: PIPELINE DE FASES DE EJECUCIÓN

## 4.1. Visión General del Pipeline

El corazón operativo de F.A.R.F.A.N. es un pipeline secuencial y determinista compuesto por 11 fases. Cada fase es una etapa de procesamiento discreta que toma los artefactos de la fase anterior, realiza una transformación o análisis específico, y entrega sus resultados a la fase siguiente. Esta estructura garantiza un flujo de datos unidireccional, trazable y robusto.

La ejecución del pipeline es gestionada por la clase `Orchestrator` (ubicada en `src/farfan_pipeline/core/orchestrator/core.py`), que actúa como el director de orquesta, asegurando que cada fase se ejecute en el orden correcto, con los `inputs` requeridos y bajo las restricciones de recursos definidas.

## 4.2. Visualización del Pipeline

*Nota: El gráfico canónico del pipeline ya está generado en `docs/phases/phase_1/images/canonical_pipeline.png`.*

![Pipeline de 11 fases](../phases/phase_1/images/canonical_pipeline.png)

## 4.3. Detalle de las Fases

A continuación se detalla el propósito, las pre-condiciones (inputs) y las post-condiciones (outputs) de cada una de las 11 fases canónicas.

### FASE 0: Validación de Configuración
-   **Propósito:** Cargar y validar la configuración central del sistema, principalmente el `questionnaire_monolith.json`. Esta fase actúa como una compuerta de calidad: si la configuración es inválida, el pipeline no puede continuar.
-   **Pre-condiciones:** Acceso al `questionnaire_monolith.json` canónico.
-   **Post-condiciones:** Un objeto de configuración (`config`) validado en memoria, que contiene el monolito, su hash SHA-256, las listas de preguntas y un informe de la integridad estructural.

### FASE 1: Ingestión de Documento
-   **Propósito:** Procesar un documento de política pública de entrada (ej. un PDF) y transformarlo en la estructura de datos interna del orquestador, el `PreprocessedDocument`. Esta fase utiliza el pipeline canónico de "Smart Policy Chunks" (SPCs).
-   **Pre-condiciones:** Un objeto `config` de la FASE 0 y la ruta a un documento de entrada.
-   **Post-condiciones:** Una instancia de `PreprocessedDocument` que contiene el texto, los metadatos y, crucialmente, una lista de 60 "Smart Policy Chunks" estructurados y anotados con `policy_area_id` y `dimension_id`.

### FASE 2: Ejecución de Micro-Preguntas
-   **Propósito:** Ejecutar la lógica de análisis para cada una de las ~300 micro-preguntas definidas en el monolito. Cada pregunta es procesada por un `Executor` específico (ej. `D1Q1_Executor`) que aplica una secuencia de métodos de análisis sobre los `chunks` relevantes del documento.
-   **Pre-condiciones:** Una instancia de `PreprocessedDocument` (FASE 1) y el objeto `config` (FASE 0).
-   **Post-condiciones:** Una lista de objetos `MicroQuestionRun`, donde cada uno contiene la "evidencia" extraída para una pregunta específica o un mensaje de error si el análisis falló.

### FASE 3: Scoring de Resultados Micro
-   **Propósito:** Tomar la "evidencia" cruda de la fase anterior y aplicarle las reglas de puntuación (scoring) definidas en el monolito. Cada pregunta tiene una modalidad de scoring (ej. `TYPE_A`, `TYPE_B`) que se traduce en un score numérico.
-   **Pre-condiciones:** La lista de `MicroQuestionRun` (FASE 2) y el objeto `config` (FASE 0).
-   **Post-condiciones:** Una lista de objetos `ScoredMicroQuestion`, que enriquecen los resultados anteriores con un `score` numérico, un `normalized_score` (0-1) y un nivel de calidad (`quality_level`).

### FASE 4: Agregación de Dimensiones
-   **Propósito:** Primer nivel de agregación jerárquica. Agrupa los scores de las micro-preguntas por dimensión y área de política para calcular un `DimensionScore` para cada una de las 60 combinaciones (10 áreas x 6 dimensiones).
-   **Pre-condiciones:** La lista de `ScoredMicroQuestion` (FASE 3) y el objeto `config` (FASE 0).
-   **Post-condiciones:** Una lista de 60 objetos `DimensionScore`.

### FASE 5: Agregación de Áreas de Política
-   **Propósito:** Segundo nivel de agregación. Consolida los 6 `DimensionScore` de cada área de política para producir un único `AreaScore` por cada una de las 10 áreas.
-   **Pre-condiciones:** La lista de `DimensionScore` (FASE 4) y el objeto `config` (FASE 0).
-   **Post-condiciones:** Una lista de 10 objetos `AreaScore`.

### FASE 6: Agregación de Clústeres
-   **Propósito:** Tercer nivel de agregación. Agrupa los `AreaScore` según la definición de clústeres del monolito para producir un `ClusterScore` para cada clúster.
-   **Pre-condiciones:** La lista de `AreaScore` (FASE 5) y el objeto `config` (FASE 0).
-   **Post-condiciones:** Una lista de objetos `ClusterScore` (típicamente 4).

### FASE 7: Evaluación Macro
-   **Propósito:** Nivel final de agregación. Sintetiza todos los `ClusterScore` en un único `MacroScore` que representa la evaluación global del documento. También calcula métricas de coherencia y alineamiento estratégico.
-   **Pre-condiciones:** La lista de `ClusterScore` (FASE 6) y el objeto `config` (FASE 0).
-   **Post-condiciones:** Un objeto `MacroScoreDict` que contiene el score final, el nivel de calidad global y métricas analíticas avanzadas.

### FASE 8: Generación de Recomendaciones
-   **Propósito:** Utilizar los resultados de todos los niveles de agregación (micro, meso y macro) para generar recomendaciones estratégicas accionables a través de un motor de reglas (`RecommendationEngine`).
-   **Pre-condiciones:** El `MacroScoreDict` (FASE 7) y acceso a los resultados de fases anteriores a través del contexto del orquestador.
-   **Post-condiciones:** Un diccionario estructurado que contiene listas de recomendaciones a nivel MICRO, MESO y MACRO.

### FASE 9: Ensamblado de Reporte
-   **Propósito:** Consolidar todos los resultados, métricas y recomendaciones en una única estructura de datos coherente, lista para ser exportada.
-   **Pre-condiciones:** Las recomendaciones (FASE 8) y el objeto `config` (FASE 0).
-   **Post-condiciones:** Un objeto de reporte (`report`) en formato diccionario.

### FASE 10: Formateo y Exportación
-   **Propósito:** Tomar el reporte final y formatearlo en el payload de salida definitivo (ej. JSON), incluyendo metadatos de la ejecución del pipeline.
-   **Pre-condiciones:** El objeto `report` (FASE 9) y el objeto `config` (FASE 0).
-   **Post-condiciones:** Un `export_payload` final en formato diccionario, que es el artefacto terminal del pipeline.

## 4.4. Implementación Canónica: El Código del Orquestador

La siguiente sección presenta el código fuente completo y comentado de la clase `Orchestrator`. Este código **es la implementación canónica** del pipeline de 11 fases descrito anteriormente. Su inclusión en este compendio no es meramente ilustrativa; es la especificación técnica definitiva de cómo se ejecuta el pipeline, garantizando la reproducibilidad.

```python
# Contenido del archivo: src/saaaaaa/core/orchestrator/core.py
# NOTA: Este código ha sido extraído directamente del repositorio en la versión canónica.
# Se han añadido comentarios adicionales para clarificar su rol dentro de este compendio.
"""Core orchestrator classes, data models, and execution engine.

This module contains the fundamental building blocks for orchestration:
- Data models (PreprocessedDocument, Evidence, PhaseResult, etc.)
- Abort signaling (AbortSignal, AbortRequested)
- Resource management (ResourceLimits, PhaseInstrumentation)
- Method execution (MethodExecutor)
- Orchestrator (the main 11-phase orchestration engine)

The Orchestrator is the sole owner of the provider; processors and executors
receive pre-prepared data.
"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
import os
import statistics
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import asdict, dataclass, field, is_dataclass, replace
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, ParamSpec, TypedDict, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from .factory import CanonicalQuestionnaire

from ...analysis.recommendation_engine import RecommendationEngine
from ...config.paths import PROJECT_ROOT, RULES_DIR, CONFIG_DIR
from ...processing.aggregation import (
    AggregationSettings,
    AreaPolicyAggregator,
    AreaScore,
    ClusterAggregator,
    ClusterScore,
    DimensionAggregator,
    DimensionScore,
    MacroAggregator,
    MacroScore,
    ValidationError,
    group_by,
    validate_scored_results,
)
from ..dependency_lockdown import get_dependency_lockdown
from . import executors_contract as executors
from .arg_router import ArgRouterError, ArgumentValidationError, ExtendedArgRouter
from .class_registry import ClassRegistryError, build_class_registry
from .executor_config import ExecutorConfig
from .versions import CALIBRATION_VERSION
from ...utils.paths import safe_join

logger = logging.getLogger(__name__)
_CORE_MODULE_DIR = Path(__file__).resolve().parent


def resolve_workspace_path(
    path: str | Path,
    *,
    project_root: Path = PROJECT_ROOT,
    rules_dir: Path = RULES_DIR,
    module_dir: Path = _CORE_MODULE_DIR,
) -> Path:
    """Resolve repository-relative paths deterministically."""
    path_obj = Path(path)

    if path_obj.is_absolute():
        return path_obj

    sanitized = safe_join(project_root, *path_obj.parts)
    candidates = [
        sanitized,
        safe_join(module_dir, *path_obj.parts),
        safe_join(rules_dir, *path_obj.parts),
    ]

    if not path_obj.parts or path_obj.parts[0] != "rules":
        candidates.append(safe_join(rules_dir, "METODOS", *path_obj.parts))

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return sanitized

# Environment-configurable expectations for validation
EXPECTED_QUESTION_COUNT = int(os.getenv("EXPECTED_QUESTION_COUNT", "305"))
EXPECTED_METHOD_COUNT = int(os.getenv("EXPECTED_METHOD_COUNT", "416"))
PHASE_TIMEOUT_DEFAULT = int(os.getenv("PHASE_TIMEOUT_SECONDS", "300"))
P01_EXPECTED_CHUNK_COUNT = 60


class PhaseTimeoutError(RuntimeError):
    """Raised when a phase exceeds its timeout."""

    def __init__(self, phase_id: int | str, phase_name: str, timeout_s: float) -> None:
        self.phase_id = phase_id
        self.phase_name = phase_name
        self.timeout_s = timeout_s
        super().__init__(
            f"Phase {phase_id} ({phase_name}) timed out after {timeout_s}s"
        )


# ParamSpec and TypeVar for execute_phase_with_timeout
P = ParamSpec("P")
T = TypeVar("T")


async def execute_phase_with_timeout(
    phase_id: int,
    phase_name: str,
    coro: Callable[P, T] | None = None,
    *varargs: P.args,
    handler: Callable[P, T] | None = None,  # Legacy parameter for backward compatibility
    args: tuple | None = None,  # Legacy parameter for backward compatibility
    timeout_s: float = 300.0,
    **kwargs: P.kwargs,
) -> T:
    """Execute an async phase with timeout and comprehensive logging.

    Args:
        phase_id: Numeric phase identifier
        phase_name: Human-readable phase name
        coro: Coroutine/callable to execute (preferred)
        *varargs: Positional arguments for coro (when using positional style)
        handler: Legacy alias for coro (for backward compatibility)
        args: Legacy parameter for positional arguments (for backward compatibility)
        timeout_s: Timeout in seconds (default: 300.0)
        **kwargs: Keyword arguments for coro

    Returns:
        Result from coro

    Raises:
        PhaseTimeoutError: If execution exceeds timeout_s
        Exception: Any exception raised by coro
        ValueError: If neither coro nor handler is provided
    """
    # Support both coro and handler (legacy) parameter names
    target = coro or handler
    if target is None:
        raise ValueError("Either 'coro' or 'handler' must be provided")

    # Support both varargs (*args in signature) and args kwarg (legacy)
    call_args = varargs if varargs else (args or ())

    start = time.perf_counter()
    logger.info(
        "phase_execution_started",
        extra={"phase_id": phase_id, "phase_name": phase_name, "timeout_s": timeout_s},
    )
    try:
        result = await asyncio.wait_for(target(*call_args, **kwargs), timeout=timeout_s)
        elapsed = time.perf_counter() - start
        logger.info(
            "phase_execution_completed",
            extra={
                "phase_id": phase_id,
                "phase_name": phase_name,
                "elapsed_s": elapsed,
                "timeout_s": timeout_s,
                "time_remaining_s": timeout_s - elapsed,
            },
        )
        return result
    except asyncio.TimeoutError as exc:
        elapsed = time.perf_counter() - start
        logger.error(
            "phase_execution_timeout",
            extra={
                "phase_id": phase_id,
                "phase_name": phase_name,
                "elapsed_s": elapsed,
                "timeout_s": timeout_s,
                "exceeded_by_s": elapsed - timeout_s,
            },
        )
        raise PhaseTimeoutError(phase_id, phase_name, timeout_s) from exc
    except asyncio.CancelledError:
        elapsed = time.perf_counter() - start
        logger.warning(
            "phase_execution_cancelled",
            extra={
                "phase_id": phase_id,
                "phase_name": phase_name,
                "elapsed_s": elapsed,
            },
        )
        raise  # Re-raise to propagate cancellation
    except Exception as exc:
        elapsed = time.perf_counter() - start
        logger.error(
            "phase_execution_error",
            extra={
                "phase_id": phase_id,
                "phase_name": phase_name,
                "elapsed_s": elapsed,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )
        raise


def _normalize_monolith_for_hash(monolith: dict | MappingProxyType) -> dict:
    """Normalize monolith for hash computation and JSON serialization.

    Converts MappingProxyType to dict recursively to ensure:
    1. JSON serialization doesn't fail
    2. Hash computation is consistent

    Args:
        monolith: Monolith data (may be MappingProxyType or dict)

    Returns:
        Normalized dict suitable for hashing and JSON serialization

    Raises:
        RuntimeError: If normalization fails or produces inconsistent results
    """
    if isinstance(monolith, MappingProxyType):
        monolith = dict(monolith)

    # Deep-convert nested mapping proxies if they exist
    def _convert(obj: Any) -> Any:
        if isinstance(obj, MappingProxyType):
            obj = dict(obj)
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        return obj

    normalized = _convert(monolith)

    # Verify normalization is idempotent
    try:
        # Test that we can serialize it
        json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Monolith normalization failed: {exc}") from exc

    return normalized


class MacroScoreDict(TypedDict):
    """Typed container for macro score evaluation results."""
    macro_score: MacroScore
    macro_score_normalized: float
    cluster_scores: list[ClusterScore]
    cross_cutting_coherence: float
    systemic_gaps: list[str]
    strategic_alignment: float
    quality_band: str


@dataclass
class ClusterScoreData:
    """Type-safe cluster score data for macro evaluation."""
    id: str
    score: float
    normalized_score: float


@dataclass
class MacroEvaluation:
    """Type-safe macro evaluation result.

    This replaces polymorphic dict/object handling with a strict contract.
    All downstream consumers must treat macro scores as this type.
    """
    macro_score: float
    macro_score_normalized: float
    clusters: list[ClusterScoreData]


@dataclass(frozen=True)
class Provenance:
    """Provenance metadata for a chunk."""
    page_number: int
    section_header: str | None = None
    bbox: tuple[float, float, float, float] | None = None
    span_in_page: tuple[int, int] | None = None
    source_file: str | None = None

@dataclass(frozen=True)
class ChunkData:
    """Single semantic chunk from SPC (Smart Policy Chunks).

    Preserves chunk structure and metadata from the ingestion pipeline,
    enabling chunk-aware executor routing and scoped processing.
    """
    id: int
    text: str
    chunk_type: Literal["diagnostic", "activity", "indicator", "resource", "temporal", "entity"]
    sentences: list[int]  # Global sentence IDs in this chunk
    tables: list[int]     # Global table IDs in this chunk
    start_pos: int
    end_pos: int
    confidence: float
    edges_out: list[int] = field(default_factory=list)  # Chunk IDs this connects to
    edges_in: list[int] = field(default_factory=list)   # Chunk IDs connecting to this
    policy_area_id: str | None = None
    dimension_id: str | None = None
    provenance: Provenance | None = None


@dataclass
class PreprocessedDocument:
    """Orchestrator representation of a processed document.

    This is the normalized document format used internally by the orchestrator.
    It can be constructed from ingestion payloads or created directly.

    New in SPC exploitation: Preserves chunk structure when processing_mode='chunked',
    enabling chunk-aware executor routing and reducing redundant processing.
    """
    document_id: str
    raw_text: str
    sentences: list[Any]
    tables: list[Any]
    metadata: dict[str, Any]
    sentence_metadata: list[Any] = field(default_factory=list)
    indexes: dict[str, Any] | None = None
    structured_text: dict[str, Any] | None = None
    language: str | None = None
    ingested_at: datetime | None = None
    full_text: str | None = None

    # NEW CHUNK FIELDS for SPC exploitation
    chunks: list[ChunkData] = field(default_factory=list)
    chunk_index: dict[str, int] = field(default_factory=dict)  # Fast lookup: entity_id → chunk_id
    chunk_graph: dict[str, Any] = field(default_factory=dict)  # Exposed graph structure
    processing_mode: Literal["flat", "chunked"] = "flat"  # Mode flag for backward compatibility

    def __post_init__(self) -> None:
        """Validate document fields after initialization.

        Raises:
            ValueError: If raw_text is empty or whitespace-only
        """
        if (not self.raw_text or not self.raw_text.strip()) and self.full_text:
            # Backward-compatible fallback when only full_text is provided
            self.raw_text = self.full_text
        if not self.raw_text or not self.raw_text.strip():
            raise ValueError(
                "PreprocessedDocument cannot have empty raw_text. "
                "Use PreprocessedDocument.ensure() to create from SPC pipeline."
            )

    @staticmethod
    def _dataclass_to_dict(value: Any) -> Any:
        """Convert a dataclass to a dictionary if applicable."""
        if is_dataclass(value):
            return asdict(value)
        return value

    @classmethod
    def ensure(
        cls, document: Any, *, document_id: str | None = None, use_spc_ingestion: bool = True
    ) -> PreprocessedDocument:
        """Normalize arbitrary ingestion payloads into orchestrator documents.

        Args:
            document: Document to normalize (PreprocessedDocument or CanonPolicyPackage)
            document_id: Optional document ID override
            use_spc_ingestion: Must be True (SPC is now the only supported ingestion method)

        Returns:
            PreprocessedDocument instance

        Raises:
            ValueError: If use_spc_ingestion is False
            TypeError: If document type is not supported
        """
        # Enforce SPC-only ingestion
        if not use_spc_ingestion:
            raise ValueError(
                "SPC ingestion is now required. Set use_spc_ingestion=True or remove the parameter. "
                "Legacy ingestion methods (document_ingestion module) are no longer supported."
            )

        # Reject class types - only accept instances
        if isinstance(document, type):
            class_name = getattr(document, '__name__', str(document))
            raise TypeError(
                f"Expected document instance, got class type '{class_name}'. "
                "Pass an instance of the document, not the class itself."
            )

        if isinstance(document, cls):
            return document

        # Check for SPC (Smart Policy Chunks) ingestion - canonical phase-one
        # Documents must have chunk_graph attribute (from CanonPolicyPackage)
        if hasattr(document, "chunk_graph"):
            # Validate chunk_graph exists and is not empty
            chunk_graph = getattr(document, "chunk_graph", None)
            if chunk_graph is None:
                raise ValueError(
                    "Document has chunk_graph attribute but it is None. "
                    "Ensure SPC ingestion pipeline completed successfully."
                )

            # Validate chunk_graph has chunks
            if not hasattr(chunk_graph, 'chunks') or not chunk_graph.chunks:
                raise ValueError(
                    "Document chunk_graph is empty. "
                    "Ensure SPC ingestion pipeline completed successfully and extracted chunks."
                )

            try:
                from saaaaaa.utils.spc_adapter import SPCAdapter
                adapter = SPCAdapter()
                preprocessed = adapter.to_preprocessed_document(document, document_id=document_id)

                # Comprehensive SPC ingestion validation
                validation_results = []

                # Validate raw_text
                if not preprocessed.raw_text or not preprocessed.raw_text.strip():
                    raise ValueError(
                        "SPC ingestion produced empty document. "
                        "Check that the source document contains extractable text."
                    )
                text_length = len(preprocessed.raw_text)
                validation_results.append(f"raw_text: {text_length} chars")

                # Validate sentences extracted
                sentence_count = len(preprocessed.sentences) if preprocessed.sentences else 0
                if sentence_count == 0:
                    logger.warning("SPC ingestion produced zero sentences - document may be malformed")
                validation_results.append(f"sentences: {sentence_count}")

                # Validate chunk_graph exists
                chunk_count = preprocessed.metadata.get("chunk_count", 0)
                validation_results.append(f"chunks: {chunk_count}")

                # Log successful validation
                logger.info(f"SPC ingestion validation passed: {', '.join(validation_results)}")

                return preprocessed
            except ImportError as e:
                raise ImportError(
                    "SPC ingestion requires spc_adapter module. "
                    "Ensure saaaaaa.utils.spc_adapter is available."
                ) from e
            except ValueError:
                # Re-raise ValueError directly (e.g., empty document validation)
                raise
            except Exception as e:
                raise TypeError(
                    f"Failed to adapt SPC document: {e}. "
                    "Ensure document is a valid CanonPolicyPackage instance from SPC pipeline."
                ) from e

        raise TypeError(
            "Unsupported preprocessed document payload. "
            f"Expected PreprocessedDocument or CanonPolicyPackage with chunk_graph, got {type(document)!r}. "
            "Documents must be processed through the SPC ingestion pipeline first."
        )

@dataclass
class Evidence:
    """Evidence container for orchestrator results."""
    modality: str
    elements: list[Any] = field(default_factory=list)
    raw_results: dict[str, Any] = field(default_factory=dict)

class AbortRequested(RuntimeError):
    """Raised when an abort signal is triggered during orchestration."""

class AbortSignal:
    """Thread-safe abort signal shared across orchestration phases."""

    def __init__(self) -> None:
        self._event = threading.Event()
        self._lock = threading.Lock()
        self._reason: str | None = None
        self._timestamp: datetime | None = None

    def abort(self, reason: str) -> None:
        """Trigger an abort with a reason and timestamp."""
        if not reason:
            reason = "Abort requested"
        with self._lock:
            if not self._event.is_set():
                self._event.set()
                self._reason = reason
                self._timestamp = datetime.utcnow()

    def is_aborted(self) -> bool:
        """Check whether abort has been triggered."""
        return self._event.is_set()

    def get_reason(self) -> str | None:
        """Return the abort reason if set."""
        with self._lock:
            return self._reason

    def get_timestamp(self) -> datetime | None:
        """Return the abort timestamp if set."""
        with self._lock:
            return self._timestamp

    def reset(self) -> None:
        """Clear the abort signal."""
        with self._lock:
            self._event.clear()
            self._reason = None
            self._timestamp = None

class ResourceLimits:
    """Runtime resource guard with adaptive worker prediction."""

    def __init__(
        self,
        max_memory_mb: float | None = 4096.0,
        max_cpu_percent: float = 85.0,
        max_workers: int = 32,
        min_workers: int = 4,
        hard_max_workers: int = 64,
        history: int = 120,
    ) -> None:
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self.min_workers = max(1, min_workers)
        self.hard_max_workers = max(self.min_workers, hard_max_workers)
        self._max_workers = max(self.min_workers, min(max_workers, self.hard_max_workers))
        self._usage_history: deque[dict[str, float]] = deque(maxlen=history)
        self._semaphore: asyncio.Semaphore | None = None
        self._semaphore_limit = self._max_workers
        self._async_lock: asyncio.Lock | None = None
        self._psutil = None
        self._psutil_process = None
        try:  # pragma: no cover - optional dependency
            import psutil  # type: ignore[import-untyped]

            self._psutil = psutil
            self._psutil_process = psutil.Process(os.getpid())
        except Exception:  # pragma: no cover - psutil missing
            self._psutil = None
            self._psutil_process = None

    @property
    def max_workers(self) -> int:
        """Return the current worker budget."""
        return self._max_workers

    def attach_semaphore(self, semaphore: asyncio.Semaphore) -> None:
        """Attach an asyncio semaphore for budget control."""
        self._semaphore = semaphore
        self._semaphore_limit = self._max_workers

    async def apply_worker_budget(self) -> int:
        """Apply the current worker budget to the semaphore."""
        if self._semaphore is None:
            return self._max_workers

        if self._async_lock is None:
            self._async_lock = asyncio.Lock()

        async with self._async_lock:
            desired = self._max_workers
            current = self._semaphore_limit
            if desired > current:
                for _ in range(desired - current):
                    self._semaphore.release()
            elif desired < current:
                reduction = current - desired
                for _ in range(reduction):
                    await self._semaphore.acquire()
            self._semaphore_limit = desired
            return self._max_workers

    def _record_usage(self, usage: dict[str, float]) -> None:
        """Record resource usage and predict worker budget."""
        self._usage_history.append(usage)
        self._predict_worker_budget()

    def _predict_worker_budget(self) -> None:
        """Adjust worker budget based on recent resource usage."""
        if len(self._usage_history) < 5:
            return

        cpu_vals = [entry["cpu_percent"] for entry in self._usage_history]
        mem_vals = [entry["memory_percent"] for entry in self._usage_history]
        recent_cpu = cpu_vals[-5:]
        recent_mem = mem_vals[-5:]
        avg_cpu = statistics.mean(recent_cpu)
        avg_mem = statistics.mean(recent_mem)

        new_budget = self._max_workers
        if self.max_cpu_percent and avg_cpu > self.max_cpu_percent * 0.95 or self.max_memory_mb and avg_mem > 90.0:
            new_budget = max(self.min_workers, self._max_workers - 1)
        elif avg_cpu < self.max_cpu_percent * 0.6 and avg_mem < 70.0:
            new_budget = min(self.hard_max_workers, self._max_workers + 1)

        self._max_workers = max(self.min_workers, min(new_budget, self.hard_max_workers))

    def check_memory_exceeded(
        self, usage: dict[str, float] | None = None
    ) -> tuple[bool, dict[str, float]]:
        """Check if memory limit has been exceeded."""
        usage = usage or self.get_resource_usage()
        exceeded = False
        if self.max_memory_mb is not None:
            exceeded = usage.get("rss_mb", 0.0) > self.max_memory_mb
        return exceeded, usage

    def check_cpu_exceeded(
        self, usage: dict[str, float] | None = None
    ) -> tuple[bool, dict[str, float]]:
        """Check if CPU limit has been exceeded."""
        usage = usage or self.get_resource_usage()
        exceeded = False
        if self.max_cpu_percent:
            exceeded = usage.get("cpu_percent", 0.0) > self.max_cpu_percent
        return exceeded, usage

    def get_resource_usage(self) -> dict[str, float]:
        """Capture current resource usage metrics."""
        timestamp = datetime.utcnow().isoformat()
        cpu_percent = 0.0
        memory_percent = 0.0
        rss_mb = 0.0

        if self._psutil:
            try:  # pragma: no cover - psutil branch
                cpu_percent = float(self._psutil.cpu_percent(interval=None))
                virtual_memory = self._psutil.virtual_memory()
                memory_percent = float(virtual_memory.percent)
                if self._psutil_process is not None:
                    rss_mb = float(self._psutil_process.memory_info().rss / (1024 * 1024))
            except Exception:
                cpu_percent = 0.0
        else:
            try:
                load1, _, _ = os.getloadavg()
                cpu_percent = float(min(100.0, load1 * 100))
            except OSError:
                cpu_percent = 0.0
            try:
                import resource

                usage_info = resource.getrusage(resource.RUSAGE_SELF)
                rss_mb = float(usage_info.ru_maxrss / 1024)
            except Exception:
                rss_mb = 0.0

        usage = {
            "timestamp": timestamp,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "rss_mb": rss_mb,
            "worker_budget": float(self._max_workers),
        }
        self._record_usage(usage)
        return usage

    def get_usage_history(self) -> list[dict[str, float]]:
        """Return the recorded usage history."""
        return list(self._usage_history)

class PhaseInstrumentation:
    """Collects granular telemetry for each orchestration phase."""

    def __init__(
        self,
        phase_id: int,
        name: str,
        items_total: int | None = None,
        snapshot_interval: int = 10,
        resource_limits: ResourceLimits | None = None,
    ) -> None:
        self.phase_id = phase_id
        self.name = name
        self.items_total = items_total or 0
        self.snapshot_interval = max(1, snapshot_interval)
        self.resource_limits = resource_limits
        self.items_processed = 0
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.warnings: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []
        self.resource_snapshots: list[dict[str, Any]] = []
        self.latencies: list[float] = []
        self.anomalies: list[dict[str, Any]] = []

    def start(self, items_total: int | None = None) -> None:
        """Mark the start of phase execution."""
        if items_total is not None:
            self.items_total = items_total
        self.start_time = time.perf_counter()

    def increment(self, count: int = 1, latency: float | None = None) -> None:
        """Increment processed item count and optionally record latency."""
        self.items_processed += count
        if latency is not None:
            self.latencies.append(latency)
            self._detect_latency_anomaly(latency)
        if self.resource_limits and self.should_snapshot():
            self.capture_resource_snapshot()

    def should_snapshot(self) -> bool:
        """Determine if a resource snapshot should be captured."""
        if self.items_total == 0:
            return False
        if self.items_processed == 0:
            return False
        return self.items_processed % self.snapshot_interval == 0

    def capture_resource_snapshot(self) -> None:
        """Capture a resource usage snapshot."""
        if not self.resource_limits:
            return
        snapshot = self.resource_limits.get_resource_usage()
        snapshot["items_processed"] = self.items_processed
        self.resource_snapshots.append(snapshot)

    def record_warning(self, category: str, message: str, **extra: Any) -> None:
        """Record a warning during phase execution."""
        entry = {
            "category": category,
            "message": message,
            **extra,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.warnings.append(entry)

    def record_error(self, category: str, message: str, **extra: Any) -> None:
        """Record an error during phase execution."""
        entry = {
            "category": category,
            "message": message,
            **extra,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.errors.append(entry)

    def _detect_latency_anomaly(self, latency: float) -> None:
        """Detect latency anomalies using statistical thresholds."""
        if len(self.latencies) < 5:
            return
        mean_latency = statistics.mean(self.latencies)
        std_latency = statistics.pstdev(self.latencies) or 0.0
        threshold = mean_latency + (3 * std_latency)
        if std_latency and latency > threshold:
            self.anomalies.append(
                {
                    "type": "latency_spike",
                    "latency": latency,
                    "mean": mean_latency,
                    "std": std_latency,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    def complete(self) -> None:
        """Mark the end of phase execution."""
        self.end_time = time.perf_counter()

    def duration_ms(self) -> float | None:
        """Return the phase duration in milliseconds."""
        if self.start_time is None or self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000.0

    def progress(self) -> float | None:
        """Return the progress fraction (0.0 to 1.0)."""
        if not self.items_total:
            return None
        return min(1.0, self.items_processed / float(self.items_total))

    def throughput(self) -> float | None:
        """Return items processed per second."""
        if self.start_time is None:
            return None
        elapsed = (
            (time.perf_counter() - self.start_time)
            if self.end_time is None
            else (self.end_time - self.start_time)
        )
        if not elapsed:
            return None
        return self.items_processed / elapsed

    def latency_histogram(self) -> dict[str, float | None]:
        """Return latency percentiles."""
        if not self.latencies:
            return {"p50": None, "p95": None, "p99": None}
        sorted_latencies = sorted(self.latencies)

        def percentile(p: float) -> float:
            if not sorted_latencies:
                return 0.0
            k = (len(sorted_latencies) - 1) * (p / 100.0)
            f = int(k)
            c = min(f + 1, len(sorted_latencies) - 1)
            if f == c:
                return sorted_latencies[int(k)]
            d0 = sorted_latencies[f] * (c - k)
            d1 = sorted_latencies[c] * (k - f)
            return d0 + d1

        return {
            "p50": percentile(50.0),
            "p95": percentile(95.0),
            "p99": percentile(99.0),
        }

    def build_metrics(self) -> dict[str, Any]:
        """Build a metrics summary dictionary."""
        return {
            "phase_id": self.phase_id,
            "name": self.name,
            "duration_ms": self.duration_ms(),
            "items_processed": self.items_processed,
            "items_total": self.items_total,
            "progress": self.progress(),
            "throughput": self.throughput(),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "resource_snapshots": list(self.resource_snapshots),
            "latency_histogram": self.latency_histogram(),
            "anomalies": list(self.anomalies),
        }

@dataclass
class PhaseResult:
    """Result of a single orchestration phase."""
    success: bool
    phase_id: str
    data: Any
    error: Exception | None
    duration_ms: float
    mode: str
    aborted: bool = False

@dataclass
class MicroQuestionRun:
    """Result of executing a single micro-question."""
    question_id: str
    question_global: int
    base_slot: str
    metadata: dict[str, Any]
    evidence: Evidence | None
    error: str | None = None
    duration_ms: float | None = None
    aborted: bool = False

@dataclass
class ScoredMicroQuestion:
    """Scored micro-question result."""
    question_id: str
    question_global: int
    base_slot: str
    score: float | None
    normalized_score: float | None
    quality_level: str | None
    evidence: Evidence | None
    scoring_details: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class _LazyInstanceDict:
    """Lazy instance dictionary for backward compatibility.

    Provides dict-like interface but delegates to MethodRegistry
    for lazy instantiation. This maintains compatibility with code
    that accesses MethodExecutor.instances directly.
    """

    def __init__(self, method_registry: Any) -> None:
        self._registry = method_registry

    def get(self, class_name: str, default: Any = None) -> Any:
        """Get instance lazily."""
        try:
            return self._registry._get_instance(class_name)
        except Exception:
            return default

    def __getitem__(self, class_name: str) -> Any:
        """Get instance lazily (dict access)."""
        return self._registry._get_instance(class_name)

    def __contains__(self, class_name: str) -> bool:
        """Check if class is available."""
        return class_name in self._registry._class_paths

    def keys(self) -> list[str]:
        """Get available class names."""
        return list(self._registry._class_paths.keys())

    def values(self) -> list[Any]:
        """Get instantiated instances (triggers lazy loading)."""
        return [self.get(name) for name in self.keys()]

    def items(self) -> list[tuple[str, Any]]:
        """Get (name, instance) pairs (triggers lazy loading)."""
        return [(name, self.get(name)) for name in self.keys()]

    def __len__(self) -> int:
        """Get number of available classes."""
        return len(self._registry._class_paths)


class MethodExecutor:
    """Execute catalog methods using lazy method injection.

    This executor uses MethodRegistry for lazy instantiation:
    - Classes are loaded only when their methods are first called
    - Failed classes don't block other methods from working
    - Methods can be directly injected without classes
    - Instance caching for efficiency

    No upfront class instantiation - lightweight and decoupled.
    """

    def __init__(
        self,
        dispatcher: Any | None = None, # dispatcher is deprecated
        signal_registry: Any | None = None,
        method_registry: Any | None = None, # MethodRegistry instance
    ) -> None:
        from .method_registry import MethodRegistry, setup_default_instantiation_rules

        self.degraded_mode = False
        self.degraded_reasons: list[str] = []
        self.signal_registry = signal_registry

        # Initialize method registry with lazy loading
        if method_registry is not None:
            self._method_registry = method_registry
        else:
            try:
                self._method_registry = MethodRegistry()
                setup_default_instantiation_rules(self._method_registry)
                logger.info("method_registry_initialized_lazy_mode")
            except Exception as exc:
                self.degraded_mode = True
                reason = f"Method registry initialization failed: {exc}"
                self.degraded_reasons.append(reason)
                logger.error("DEGRADED MODE: %s", reason)
                # Create empty registry for graceful degradation
                self._method_registry = MethodRegistry(class_paths={})

        # Build minimal class type registry for ArgRouter compatibility
        # Note: This doesn't instantiate classes, just loads types
        try:
            from .class_registry import build_class_registry
            registry = build_class_registry()
        except (ClassRegistryError, ModuleNotFoundError, ImportError) as exc:
            self.degraded_mode = True
            reason = f"Could not build class registry: {exc}"
            self.degraded_reasons.append(reason)
            logger.warning("DEGRADED MODE: %s", reason)
            registry = {}

        # Create ExtendedArgRouter with the registry for enhanced validation and metrics
        self._router = ExtendedArgRouter(registry)
        self.instances = _LazyInstanceDict(self._method_registry)

    @staticmethod
    def _supports_parameter(callable_obj: Any, parameter_name: str) -> bool:
        try:
            signature = inspect.signature(callable_obj)
        except (TypeError, ValueError):  # pragma: no cover - builtins / C extensions
            return False
        return parameter_name in signature.parameters

    def execute(self, class_name: str, method_name: str, **kwargs: Any) -> Any:
        """Execute a method using lazy instantiation.

        Args:
            class_name: Name of the class.
            method_name: Name of the method to execute.
            **kwargs: Keyword arguments to pass to the method call.

        Returns:
            The method's return value.

        Raises:
            ArgRouterError: If routing fails
            AttributeError: If method doesn't exist
            MethodRegistryError: If method cannot be retrieved
        """
        from .method_registry import MethodRegistryError

        # Get method from registry (lazy instantiation)
        try:
            method = self._method_registry.get_method(class_name, method_name)
        except MethodRegistryError as exc:
            logger.error(
                "method_retrieval_failed",
                class_name=class_name,
                method_name=method_name,
                error=str(exc),
            )
            # Graceful degradation - return None for missing methods
            if self.degraded_mode:
                logger.warning("Returning None due to degraded mode")
                return None
            raise AttributeError(
                f"Cannot retrieve {class_name}.{method_name}: {exc}"
            ) from exc

        # Route arguments and execute
        try:
            args, routed_kwargs = self._router.route(class_name, method_name, dict(kwargs))
            return method(*args, **routed_kwargs)
        except (ArgRouterError, ArgumentValidationError):
            logger.exception("Argument routing failed for %s.%s", class_name, method_name)
            raise
        except Exception:
            logger.exception("Method execution failed for %s.%s", class_name, method_name)
            raise

    def inject_method(
        self,
        class_name: str,
        method_name: str,
        method: Callable[..., Any],
    ) -> None:
        """Inject a method directly without requiring a class.

        This allows you to provide custom implementations that bypass
        class instantiation entirely. Useful for:
        - Custom implementations
        - Mocking/testing
        - Hotfixes without modifying classes

        Example:
            def custom_analyzer(text: str, **kwargs) -> dict:
                return {"result": "custom analysis"}

            executor.inject_method("CustomClass", "analyze", custom_analyzer)

        Args:
            class_name: Virtual class name for routing
            method_name: Method name
            method: Callable to inject
        """
        self._method_registry.inject_method(class_name, method_name, method)
        logger.info(
            "method_injected_into_executor",
            class_name=class_name,
            method_name=method_name,
        )

    def has_method(self, class_name: str, method_name: str) -> bool:
        """Check if a method is available.

        Args:
            class_name: Class name
            method_name: Method name

        Returns:
            True if method exists or is injected
        """
        return self._method_registry.has_method(class_name, method_name)

    def get_registry_stats(self) -> dict[str, Any]:
        """Get statistics from the method registry.

        Returns:
            Dict with registry statistics including:
            - total_classes_registered: Total classes in registry
            - instantiated_classes: Classes that have been instantiated
            - failed_classes: Classes that failed instantiation
            - direct_methods_injected: Methods injected directly
        """
        return self._method_registry.get_stats()

    def get_routing_metrics(self) -> dict[str, Any]:
        """Get routing metrics from ExtendedArgRouter.

        Returns:
            Dict with routing statistics including:
            - total_routes: Total number of routes processed
            - special_routes_hit: Count of special route invocations
            - validation_errors: Count of validation failures
            - silent_drops_prevented: Count of silent parameter drops prevented
        """
        if hasattr(self._router, 'get_metrics'):
            return self._router.get_metrics()
        return {}

def validate_phase_definitions(phase_list: list[tuple[int, str, str, str]], orchestrator_class: type) -> None:
    """Validate phase definitions for structural coherence.

    This is a hard gate: if phase definitions are broken, the orchestrator cannot start.
    No "limited mode" is allowed when the base schema is corrupted.

    Args:
        phase_list: List of phase tuples (id, mode, handler, label)
        orchestrator_class: Orchestrator class to check for handler methods

    Raises:
        RuntimeError: If phase definitions are invalid
    """
    if not phase_list:
        raise RuntimeError("FASES cannot be empty - no phases defined for orchestration")

    # Extract phase IDs
    phase_ids = [phase[0] for phase in phase_list]

    # Check for duplicate phase IDs
    seen_ids = set()
    for phase_id in phase_ids:
        if phase_id in seen_ids:
            raise RuntimeError(
                f"Duplicate phase ID {phase_id} in FASES definition. "
                "Phase IDs must be unique."
            )
        seen_ids.add(phase_id)

    # Check that IDs are contiguous starting from 0
    # For performance: check sorted and validate range
    if phase_ids != sorted(phase_ids):
        raise RuntimeError(
            f"Phase IDs must be sorted in ascending order. Got {phase_ids}"
        )
    if phase_ids[0] != 0:
        raise RuntimeError(
            f"Phase IDs must start from 0. Got first ID: {phase_ids[0]}"
        )
    if phase_ids[-1] != len(phase_list) - 1:
        raise RuntimeError(
            f"Phase IDs must be contiguous from 0 to {len(phase_list) - 1}. "
            f"Got highest ID: {phase_ids[-1]}"
        )

    # Validate each phase
    valid_modes = {"sync", "async"}
    for phase_id, mode, handler_name, label in phase_list:
        # Validate mode
        if mode not in valid_modes:
            raise RuntimeError(
                f"Phase {phase_id} ({label}): invalid mode '{mode}'. "
                f"Mode must be one of {valid_modes}"
            )

        # Validate handler exists as method in orchestrator
        if not hasattr(orchestrator_class, handler_name):
            raise RuntimeError(
                f"Phase {phase_id} ({label}): handler method '{handler_name}' "
                f"does not exist in {orchestrator_class.__name__}"
            )

        # Validate handler is callable
        handler = getattr(orchestrator_class, handler_name, None)
        if not callable(handler):
            raise RuntimeError(
                f"Phase {phase_id} ({label}): handler '{handler_name}' "
                f"is not callable"
            )


class Orchestrator:
    """Robust 11-phase orchestrator with abort support and resource control.

    The Orchestrator owns the provider and prepares all data for processors
    and executors. It executes 11 phases synchronously or asynchronously,
    with full instrumentation and abort capability.
    """

    FASES: list[tuple[int, str, str, str]] = [
        (0, "sync", "_load_configuration", "FASE 0 - Validación de Configuración"),
        (1, "sync", "_ingest_document", "FASE 1 - Ingestión de Documento"),
        (2, "async", "_execute_micro_questions_async", "FASE 2 - Micro Preguntas"),
        (3, "async", "_score_micro_results_async", "FASE 3 - Scoring Micro"),
        (4, "async", "_aggregate_dimensions_async", "FASE 4 - Agregación Dimensiones"),
        (5, "async", "_aggregate_policy_areas_async", "FASE 5 - Agregación Áreas"),
        (6, "sync", "_aggregate_clusters", "FASE 6 - Agregación Clústeres"),
        (7, "sync", "_evaluate_macro", "FASE 7 - Evaluación Macro"),
        (8, "async", "_generate_recommendations", "FASE 8 - Recomendaciones"),
        (9, "sync", "_assemble_report", "FASE 9 - Ensamblado de Reporte"),
        (10, "async", "_format_and_export", "FASE 10 - Formateo y Exportación"),
    ]

    PHASE_ITEM_TARGETS: dict[int, int] = {
        0: 1,
        1: 1,
        2: 300,
        3: 300,
        4: 60,
        5: 10,
        6: 4,
        7: 1,
        8: 1,
        9: 1,
        10: 1,
    }

    PHASE_OUTPUT_KEYS: dict[int, str] = {
        0: "config",
        1: "document",
        2: "micro_results",
        3: "scored_results",
        4: "dimension_scores",
        5: "policy_area_scores",
        6: "cluster_scores",
        7: "macro_result",
        8: "recommendations",
        9: "report",
        10: "export_payload",
    }

    PHASE_ARGUMENT_KEYS: dict[int, list[str]] = {
        1: ["pdf_path", "config"],
        2: ["document", "config"],
        3: ["micro_results", "config"],
        4: ["scored_results", "config"],
        5: ["dimension_scores", "config"],
        6: ["policy_area_scores", "config"],
        7: ["cluster_scores", "config"],
        8: ["macro_result", "config"],
        9: ["recommendations", "config"],
        10: ["report", "config"],
    }

    # Phase timeout configuration (in seconds)
    PHASE_TIMEOUTS: dict[int, float] = {
        0: 60,     # Configuration validation
        1: 120,    # Document ingestion
        2: 600,    # Micro questions (300 items)
        3: 300,    # Scoring micro
        4: 180,    # Dimension aggregation
        5: 120,    # Policy area aggregation
        6: 60,     # Cluster aggregation
        7: 60,     # Macro evaluation
        8: 120,    # Recommendations
        9: 60,     # Report assembly
        10: 120,   # Format and export
    }

    # Score normalization constant
    PERCENTAGE_SCALE: int = 100

    def __init__(
        self,
        method_executor: MethodExecutor,
        questionnaire: CanonicalQuestionnaire,
        executor_config: "ExecutorConfig",
        calibration_orchestrator: Optional["CalibrationOrchestrator"] = None,
        resource_limits: ResourceLimits | None = None,
        resource_snapshot_interval: int = 10,
    ) -> None:
        """Initialize the orchestrator with all dependencies injected.

        Args:
            method_executor: A configured MethodExecutor instance.
            questionnaire: A loaded and validated CanonicalQuestionnaire instance.
            executor_config: The executor configuration object.
            calibration_orchestrator: The calibration orchestrator instance.
            resource_limits: Resource limit configuration.
            resource_snapshot_interval: Interval for resource snapshots.
        """
        from .factory import _validate_questionnaire_structure

        validate_phase_definitions(self.FASES, self.__class__)

        self.executor = method_executor
        self._canonical_questionnaire = questionnaire
        self._monolith_data = dict(questionnaire.data)
        self.executor_config = executor_config
        self.calibration_orchestrator = calibration_orchestrator
        self.resource_limits = resource_limits or ResourceLimits()
        self.resource_snapshot_interval = max(1, resource_snapshot_interval)
        from .factory import get_questionnaire_provider
        self.questionnaire_provider = get_questionnaire_provider()

        # Validate questionnaire structure
        try:
            _validate_questionnaire_structure(self._monolith_data)
        except (ValueError, TypeError) as e:
            raise RuntimeError(
                f"Questionnaire structure validation failed: {e}. "
                "Cannot start orchestrator with corrupt questionnaire."
            ) from e

        if not self.executor.instances:
            raise RuntimeError(
                "MethodExecutor.instances is empty - no executable methods registered."
            )

        self.executors = {
            "D1-Q1": executors.D1Q1_Executor, "D1-Q2": executors.D1Q2_Executor,
            "D1-Q3": executors.D1Q3_Executor, "D1-Q4": executors.D1Q4_Executor,
            "D1-Q5": executors.D1Q5_Executor, "D2-Q1": executors.D2Q1_Executor,
            "D2-Q2": executors.D2Q2_Executor, "D2-Q3": executors.D2Q3_Executor,
            "D2-Q4": executors.D2Q4_Executor, "D2-Q5": executors.D2Q5_Executor,
            "D3-Q1": executors.D3Q1_Executor, "D3-Q2": executors.D3Q2_Executor,
            "D3-Q3": executors.D3Q3_Executor, "D3-Q4": executors.D3Q4_Executor,
            "D3-Q5": executors.D3Q5_Executor, "D4-Q1": executors.D4Q1_Executor,
            "D4-Q2": executors.D4Q2_Executor, "D4-Q3": executors.D4Q3_Executor,
            "D4-Q4": executors.D4Q4_Executor, "D4-Q5": executors.D4Q5_Executor,
            "D5-Q1": executors.D5Q1_Executor, "D5-Q2": executors.D5Q2_Executor,
            "D5-Q3": executors.D5Q3_Executor, "D5-Q4": executors.D5Q4_Executor,
            "D5-Q5": executors.D5Q5_Executor, "D6-Q1": executors.D6Q1_Executor,
            "D6-Q2": executors.D6Q2_Executor, "D6-Q3": executors.D6Q3_Executor,
            "D6-Q4": executors.D6Q4_Executor, "D6-Q5": executors.D6Q5_Executor,
        }

        self.abort_signal = AbortSignal()
        self.phase_results: list[PhaseResult] = []
        self._phase_instrumentation: dict[int, PhaseInstrumentation] = {}
        self._phase_status: dict[int, str] = {
            phase_id: "not_started" for phase_id, *_ in self.FASES
        }
        self._phase_outputs: dict[int, Any] = {}
        self._context: dict[str, Any] = {}
        self._start_time: float | None = None

        self.dependency_lockdown = get_dependency_lockdown()
        logger.info(
            f"Orchestrator dependency mode: {self.dependency_lockdown.get_mode_description()}"
        )

        try:
            self.recommendation_engine = RecommendationEngine(
                rules_path=RULES_DIR / "recommendation_rules_enhanced.json",
                schema_path=RULES_DIR / "recommendation_rules_enhanced.schema.json",
                questionnaire_provider=self.questionnaire_provider,
                orchestrator=self
            )
            logger.info("RecommendationEngine initialized with enhanced v2.0 rules")
        except Exception as e:
            logger.warning(f"Failed to initialize RecommendationEngine: {e}")
            self.recommendation_engine = None

    async def run(
        self,
        preprocessed_doc: Any,
        output_path: str | None = None,
        phase_timeout: float = 300,
        enable_cache: bool = True,
        progress_callback: Callable[[int, str, float], None] | None = None,
    ) -> dict[str, Any]:
        """Execute complete 11-phase orchestration pipeline with observability.

        This is the main entry point for orchestration, implementing:
        1. Real phase-by-phase execution (not simulated)
        2. OpenTelemetry spans for each phase
        3. Progress callbacks for UI/dashboard updates
        4. WiringValidator contract checks at boundaries
        5. Manifest generation for audit trail

        Args:
            preprocessed_doc: PreprocessedDocument from SPCAdapter
            output_path: Optional path to write final report
            phase_timeout: Timeout per phase in seconds
            enable_cache: Enable caching for expensive operations
            progress_callback: Optional callback(phase_num, phase_name, progress) for real-time updates

        Returns:
            Dict with complete orchestration results:
                - macro_analysis: Macro-level scores
                - meso_analysis: Cluster-level scores
                - micro_analysis: Question-level scores
                - recommendations: Generated recommendations
                - report: Final assembled report
                - metadata: Pipeline metadata

        Raises:
            ValueError: If preprocessed_doc is invalid
            RuntimeError: If orchestration fails
        """
        from saaaaaa.observability import get_tracer, SpanKind

        tracer = get_tracer(__name__)

        # Start root span for entire orchestration
        with tracer.start_span("orchestration.run", kind=SpanKind.SERVER) as root_span:
            root_span.set_attribute("document_id", str(preprocessed_doc.document_id))
            root_span.set_attribute("phase_count", 11)
            root_span.set_attribute("cache_enabled", enable_cache)

            logger.info(
                "orchestration_started",
                document_id=preprocessed_doc.document_id,
                phase_count=11,
            )

            # Initialize result accumulator
            results = {
                "document_id": preprocessed_doc.document_id,
                "phases_completed": 0,
                "macro_analysis": None,
                "meso_analysis": None,
                "micro_analysis": None,
                "recommendations": None,
                "report": None,
                "metadata": {
                    "orchestrator_version": "2.0",
                    "start_time": datetime.now().isoformat(),
                },
            }

            try:
                # Phase 0: Configuration validation (already done in __init__)
                if progress_callback:
                    progress_callback(0, "Configuration Validation", 0.0)

                with tracer.start_span("phase.0.configuration", kind=SpanKind.INTERNAL) as span:
                    span.set_attribute("phase_id", 0)
                    span.set_attribute("phase_name", "Configuration Validation")
                    logger.info("phase_start", phase=0, name="Configuration Validation")

                    # Validate catalog is loaded
                    if self.catalog is None:
                        raise RuntimeError(
                            "Catalog not loaded. Cannot execute orchestration without method catalog."
                        )

                    logger.info("phase_complete", phase=0)
                    results["phases_completed"] = 1

                # Phase 1: Document ingestion (already complete - validate adapter contract)
                if progress_callback:
                    progress_callback(1, "Document Ingestion Validation", 9.1)

                with tracer.start_span("phase.1.ingestion_validation", kind=SpanKind.INTERNAL) as span:
                    span.set_attribute("phase_id", 1)
                    span.set_attribute("phase_name", "Document Ingestion Validation")
                    span.set_attribute("sentence_count", len(preprocessed_doc.sentences))

                    logger.info("phase_start", phase=1, name="Document Ingestion Validation")

                    # Runtime validation: Adapter → Orchestrator contract
                    try:
                        from saaaaaa.core.wiring.validation import WiringValidator
                        validator = WiringValidator()

                        preprocessed_dict = {
                            "document_id": preprocessed_doc.document_id,
                            "full_text": preprocessed_doc.full_text,
                            "sentences": list(preprocessed_doc.sentences),
                            "language": preprocessed_doc.language,
                            "sentence_count": len(preprocessed_doc.sentences),
                            "has_structured_text": preprocessed_doc.structured_text is not None,
                            "has_indexes": preprocessed_doc.indexes is not None,
                        }

                        validator.validate_adapter_to_orchestrator(preprocessed_dict)
                        logger.info("✓ Adapter → Orchestrator contract validated")
                    except ImportError:
                        logger.warning("WiringValidator not available, skipping contract validation")
                    except Exception as e:
                        logger.error(f"Contract validation failed: {e}")
                        raise RuntimeError(f"Adapter → Orchestrator contract violation: {e}") from e

                    logger.info("phase_complete", phase=1)
                    results["phases_completed"] = 2

                # Phase 2-10: Execute remaining phases
                # NOTE: Full phase implementation would call handler methods from FASES
                # For now, we'll create placeholder structure that real methods can populate

                phase_definitions = [
                    (2, "Micro Questions", "micro_analysis", 18.2),
                    (3, "Scoring Micro", "scored_micro", 27.3),
                    (4, "Dimension Aggregation", "dimension_scores", 36.4),
                    (5, "Policy Area Aggregation", "policy_area_scores", 45.5),
                    (6, "Cluster Aggregation", "cluster_scores", 54.5),
                    (7, "Macro Evaluation", "macro_analysis", 63.6),
                    (8, "Recommendations", "recommendations", 72.7),
                    (9, "Report Assembly", "report", 81.8),
                    (10, "Export", "export_payload", 90.9),
                ]

                for phase_id, phase_name, output_key, progress in phase_definitions:
                    if progress_callback:
                        progress_callback(phase_id, phase_name, progress)

                    with tracer.start_span(f"phase.{phase_id}.{output_key}", kind=SpanKind.INTERNAL) as span:
                        span.set_attribute("phase_id", phase_id)
                        span.set_attribute("phase_name", phase_name)

                        logger.info("phase_start", phase=phase_id, name=phase_name)

                        # Execute phase handler if it exists
                        phase_tuple = next((p for p in self.FASES if p[0] == phase_id), None)
                        if phase_tuple:
                            _, mode, handler_name, _ = phase_tuple

                            # Check if handler exists
                            if hasattr(self, handler_name):
                                handler = getattr(self, handler_name)

                                # Execute handler based on mode
                                try:
                                    if mode == "async":
                                        # Async handler - await it
                                        phase_output = await handler(preprocessed_doc=preprocessed_doc)
                                    else:
                                        # Sync handler
                                        phase_output = handler(preprocessed_doc=preprocessed_doc)

                                    # Store output
                                    self._phase_outputs[phase_id] = phase_output
                                    results[output_key] = phase_output

                                    span.set_attribute("phase_success", True)
                                    logger.info("phase_complete", phase=phase_id, output_size=len(str(phase_output)))
                                except Exception as e:
                                    logger.error(f"Phase {phase_id} handler failed: {e}")
                                    span.set_attribute("phase_success", False)
                                    span.set_attribute("phase_error", str(e))
                                    # Continue with empty output for now
                                    results[output_key] = {"error": str(e), "phase": phase_id}
                            else:
                                logger.warning(f"Phase {phase_id} handler '{handler_name}' not found")
                                results[output_key] = {"placeholder": True, "phase": phase_id}
                        else:
                            logger.warning(f"Phase {phase_id} not defined in FASES")
                            results[output_key] = {"placeholder": True, "phase": phase_id}

                        results["phases_completed"] = phase_id + 1

                # Final callback
                if progress_callback:
                    progress_callback(11, "Complete", 100.0)

                # Write output if path provided
                if output_path:
                    from pathlib import Path
                    import json

                    output_file = Path(output_path)
                    output_file.parent.mkdir(parents=True, exist_ok=True)

                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

                    logger.info(f"Results written to: {output_path}")
                    results["metadata"]["output_path"] = str(output_path)

                results["metadata"]["end_time"] = datetime.now().isoformat()
                results["metadata"]["success"] = True

                root_span.set_attribute("orchestration_success", True)
                logger.info("orchestration_complete", phases_completed=results["phases_completed"])

                return results

            except Exception as e:
                logger.error(f"Orchestration failed: {e}", exc_info=True)
                root_span.set_attribute("orchestration_success", False)
                root_span.set_attribute("error", str(e))

                results["metadata"]["end_time"] = datetime.now().isoformat()
                results["metadata"]["success"] = False
                results["metadata"]["error"] = str(e)

                raise RuntimeError(f"Orchestration pipeline failed: {e}") from e

    def execute_sophisticated_engineering_operation(self, policy_area_id: str) -> dict[str, Any]:
        """
        Orchestrates a sophisticated engineering operation:
        1. Generates 10 smart policy chunks using the canonical SPC ingestion pipeline.
        2. Loads the corresponding signals (patterns and regex) for the policy area.
        3. Instantiates an executor.
        4. Distributes a "work package" (chunks and signals) to the executor.
        5. Returns the generated artifacts as evidence.
        """
        logger.info(f"--- Starting Sophisticated Engineering Operation for: {policy_area_id} ---")

        # 1. Generate 10 smart policy chunks
        from pathlib import Path

        from saaaaaa.processing.spc_ingestion import CPPIngestionPipeline

        document_path = Path(f"data/policy_areas/{policy_area_id}.txt")
        logger.info(f"Processing document: {document_path}")

        ingestion_pipeline = CPPIngestionPipeline()
        canon_package = asyncio.run(ingestion_pipeline.process(document_path, max_chunks=10))

        logger.info(f"Generated {len(canon_package.chunk_graph.chunks)} chunks for {policy_area_id}.")

        # 2. Load signals
        from .questionnaire import load_questionnaire
        from .signal_loader import build_signal_pack_from_monolith

        questionnaire = load_questionnaire()
        signal_pack = build_signal_pack_from_monolith(policy_area_id, questionnaire=questionnaire)
        logger.info(f"Loaded signal pack for {policy_area_id} with {len(signal_pack.patterns)} patterns.")

        # 3. Instantiate an executor
        from . import executors

        # Simple mock for the signal registry, as the executor expects an object with a 'get' method.
        class MockSignalRegistry:
            def __init__(self, pack) -> None:
                self._pack = pack
            def get(self, _policy_area):
                return self._pack

        executor_instance = executors.D1Q1_Executor(
            method_executor=self.executor,
            signal_registry=MockSignalRegistry(signal_pack)
        )
        logger.info(f"Instantiated executor: {executor_instance.__class__.__name__}")

        # 4. Prepare and "distribute" the work package
        work_package = {
            "canon_policy_package": canon_package.to_dict(),
            "signal_pack": signal_pack.to_dict(),
        }

        logger.info(f"Distributing work package to executor for {policy_area_id}.")
        # This simulates the distribution. The executor method will provide the evidence of receipt.
        if hasattr(executor_instance, 'receive_and_process_work_package'):
            executor_instance.receive_and_process_work_package(work_package)
        else:
            logger.error("Executor does not have the 'receive_and_process_work_package' method.")

        logger.info(f"--- Completed Sophisticated Engineering Operation for: {policy_area_id} ---")

        # 5. Return evidence
        return {
            "canon_package": canon_package.to_dict(),
            "signal_pack": signal_pack.to_dict(),
        }

    def _resolve_path(self, path: str | None) -> str | None:
        """Resolve a relative or absolute path, searching multiple candidate locations."""
        if path is None:
            return None
        resolved = resolve_workspace_path(path)
        return str(resolved)

    def _get_phase_timeout(self, phase_id: int) -> float:
        """Get timeout for a specific phase."""
        return self.PHASE_TIMEOUTS.get(phase_id, 300.0)  # Default 5 minutes

    def process_development_plan(
            self, pdf_path: str, preprocessed_document: Any | None = None
    ) -> list[PhaseResult]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError("process_development_plan() debe ejecutarse fuera de un loop asyncio activo")
        return asyncio.run(
            self.process_development_plan_async(
                pdf_path, preprocessed_document=preprocessed_document
            )
        )

    async def process(self, preprocessed_document: Any) -> list[PhaseResult]:
        """
        DEPRECATED ALIAS for process_development_plan_async().

        This method exists ONLY for backward compatibility with code
        that incorrectly assumed Orchestrator had a .process() method.

        Use process_development_plan_async() instead.

        Args:
            preprocessed_document: PreprocessedDocument to process

        Returns:
            List of phase results

        Raises:
            DeprecationWarning: This method is deprecated
        """
        import warnings
        warnings.warn(
            "Orchestrator.process() is deprecated. "
            "Use process_development_plan_async(pdf_path, preprocessed_document=...) instead.",
            DeprecationWarning,
            stacklevel=2
        )

        # Extract pdf_path from preprocessed_document if available
        pdf_path = getattr(preprocessed_document, 'source_path', None)
        if pdf_path is None:
            # Try to get from metadata
            metadata = getattr(preprocessed_document, 'metadata', {})
            pdf_path = metadata.get('source_path', 'unknown.pdf')

        return await self.process_development_plan_async(
            pdf_path=str(pdf_path),
            preprocessed_document=preprocessed_document
        )

    async def process_development_plan_async(
            self, pdf_path: str, preprocessed_document: Any | None = None
    ) -> list[PhaseResult]:
        self.reset_abort()
        self.phase_results = []
        self._phase_instrumentation = {}
        self._phase_outputs = {}
        self._context = {"pdf_path": pdf_path}
        if preprocessed_document is not None:
            self._context["preprocessed_override"] = preprocessed_document
        self._phase_status = {phase_id: "not_started" for phase_id, *_ in self.FASES}
        self._start_time = time.perf_counter()

        for phase_id, mode, handler_name, phase_label in self.FASES:
            self._ensure_not_aborted()
            handler = getattr(self, handler_name)
            instrumentation = PhaseInstrumentation(
                phase_id=phase_id,
                name=phase_label,
                items_total=self.PHASE_ITEM_TARGETS.get(phase_id),
                snapshot_interval=self.resource_snapshot_interval,
                resource_limits=self.resource_limits,
            )
            instrumentation.start(items_total=self.PHASE_ITEM_TARGETS.get(phase_id))
            self._phase_instrumentation[phase_id] = instrumentation
            self._phase_status[phase_id] = "running"

            args = [self._context[key] for key in self.PHASE_ARGUMENT_KEYS.get(phase_id, [])]

            success = False
            data: Any = None
            error: Exception | None = None
            try:
                if mode == "sync":
                    data = handler(*args)
                else:
                    # Use centralized execute_phase_with_timeout
                    data = await execute_phase_with_timeout(
                        phase_id,
                        phase_label,
                        handler,
                        *args,
                        timeout_s=self._get_phase_timeout(phase_id),
                    )
                success = True
            except PhaseTimeoutError as exc:
                error = exc
                success = False
                instrumentation.record_error("timeout", str(exc))
                self.request_abort(f"Fase {phase_id} timed out: {exc}")
            except AbortRequested as exc:
                error = exc
                success = False
                instrumentation.record_warning("abort", str(exc))
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Fase %s falló", phase_label)
                error = exc
                success = False
                instrumentation.record_error("exception", str(exc))
                self.request_abort(f"Fase {phase_id} falló: {exc}")
            finally:
                instrumentation.complete()

            aborted = self.abort_signal.is_aborted()
            duration_ms = instrumentation.duration_ms() or 0.0
            phase_result = PhaseResult(
                success=success and not aborted,
                phase_id=str(phase_id),
                data=data,
                error=error,
                duration_ms=duration_ms,
                mode=mode,
                aborted=aborted,
            )
            self.phase_results.append(phase_result)

            if success and not aborted:
                self._phase_outputs[phase_id] = data
                out_key = self.PHASE_OUTPUT_KEYS.get(phase_id)
                if out_key:
                    self._context[out_key] = data
                self._phase_status[phase_id] = "completed"
            elif aborted:
                self._phase_status[phase_id] = "aborted"
                break
            else:
                self._phase_status[phase_id] = "failed"
                break

        return self.phase_results

    def get_processing_status(self) -> dict[str, Any]:
        if self._start_time is None:
            status = "not_started"
            elapsed = 0.0
            completed_flag = False
        else:
            aborted = self.abort_signal.is_aborted()
            status = "aborted" if aborted else "running"
            elapsed = time.perf_counter() - self._start_time
            completed_flag = all(state == "completed" for state in self._phase_status.values()) and not aborted

        completed = sum(1 for state in self._phase_status.values() if state == "completed")
        total = len(self.FASES)
        overall_progress = completed / total if total else 0.0

        phase_progress = {
            str(phase_id): instr.progress()
            for phase_id, instr in self._phase_instrumentation.items()
        }

        resource_usage = self.resource_limits.get_resource_usage() if self._start_time else {}

        return {
            "status": status,
            "overall_progress": overall_progress,
            "phase_progress": phase_progress,
            "elapsed_time_s": elapsed,
            "resource_usage": resource_usage,
            "abort_status": self.abort_signal.is_aborted(),
            "abort_reason": self.abort_signal.get_reason(),
            "completed": completed_flag,
        }

    def get_phase_metrics(self) -> dict[str, Any]:
        return {
            str(phase_id): instr.build_metrics()
            for phase_id, instr in self._phase_instrumentation.items()
        }

    async def monitor_progress_async(self, poll_interval: float = 2.0):
        while True:
            status = self.get_processing_status()
            yield status
            if status["status"] != "running":
                break
            await asyncio.sleep(poll_interval)

    def abort_handler(self, reason: str) -> None:
        self.request_abort(reason)

    def request_abort(self, reason: str) -> None:
        """Request orchestration to abort with a specific reason."""
        self.abort_signal.abort(reason)
        logger.warning(f"Abort requested: {reason}")

    def reset_abort(self) -> None:
        """Reset the abort signal to allow new orchestration runs."""
        self.abort_signal.reset()
        logger.debug("Abort signal reset")

    def _ensure_not_aborted(self) -> None:
        """Check if orchestration has been aborted and raise exception if so."""
        if self.abort_signal.is_aborted():
            reason = self.abort_signal.get_reason() or "Unknown reason"
            raise AbortRequested(f"Orchestration aborted: {reason}")

    def health_check(self) -> dict[str, Any]:
        usage = self.resource_limits.get_resource_usage()
        cpu_headroom = max(0.0, self.resource_limits.max_cpu_percent - usage.get("cpu_percent", 0.0))
        mem_headroom = max(0.0, (self.resource_limits.max_memory_mb or 0.0) - usage.get("rss_mb", 0.0))
        score = max(0.0, min(100.0, (cpu_headroom / max(1.0, self.resource_limits.max_cpu_percent)) * 50.0))
        if self.resource_limits.max_memory_mb:
            score += max(0.0, min(50.0, (mem_headroom / max(1.0, self.resource_limits.max_memory_mb)) * 50.0))
        score = min(100.0, score)
        if self.abort_signal.is_aborted():
            score = min(score, 20.0)
        return {"score": score, "resource_usage": usage, "abort": self.abort_signal.is_aborted()}

    def get_system_health(self) -> dict[str, Any]:
        """
        Comprehensive system health check.

        Returns health status with component checks for:
        - Method executor
        - Questionnaire provider (if available)
        - Resource limits and usage

        Returns:
            Dict with overall status ('healthy', 'degraded', 'unhealthy')
            and component-specific health information
        """
        health = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {}
        }

        # Check method executor
        try:
            executor_health = {
                'instances_loaded': len(self.executor.instances),
                'calibrations_loaded': len(self.executor.calibrations),
                'status': 'healthy'
            }
            health['components']['method_executor'] = executor_health
        except Exception as e:
            health['status'] = 'unhealthy'
            health['components']['method_executor'] = {
                'status': 'unhealthy',
                'error': str(e)
            }

        # Check questionnaire provider (if available)
        try:
            from . import get_questionnaire_provider
            provider = get_questionnaire_provider()
            questionnaire_health = {
                'has_data': provider.has_data(),
                'status': 'healthy' if provider.has_data() else 'unhealthy'
            }
            health['components']['questionnaire_provider'] = questionnaire_health

            if not provider.has_data():
                health['status'] = 'degraded'
        except Exception as e:
            health['status'] = 'unhealthy'
            health['components']['questionnaire_provider'] = {
                'status': 'unhealthy',
                'error': str(e)
            }

        # Check resource limits
        try:
            usage = self.resource_limits.get_resource_usage()
            resource_health = {
                'cpu_percent': usage.get('cpu_percent', 0),
                'memory_mb': usage.get('rss_mb', 0),
                'worker_budget': usage.get('worker_budget', 0),
                'status': 'healthy'
            }

            # Warning thresholds
            if usage.get('cpu_percent', 0) > 80:
                resource_health['status'] = 'degraded'
                resource_health['warning'] = 'High CPU usage'
                health['status'] = 'degraded'

            if usage.get('rss_mb', 0) > 3500:  # Near 4GB limit
                resource_health['status'] = 'degraded'
                resource_health['warning'] = 'High memory usage'
                health['status'] = 'degraded'

            health['components']['resources'] = resource_health
        except Exception as e:
            health['status'] = 'unhealthy'
            health['components']['resources'] = {
                'status': 'unhealthy',
                'error': str(e)
            }

        # Check abort status
        if self.abort_signal.is_aborted():
            health['status'] = 'unhealthy'
            health['abort_reason'] = self.abort_signal.get_reason()

        return health

    def export_metrics(self) -> dict[str, Any]:
        """
        Export all metrics for monitoring.

        Returns:
            Dict containing:
            - timestamp: Current UTC timestamp
            - phase_metrics: Metrics for all phases
            - resource_usage: Resource usage history
            - abort_status: Current abort status
            - phase_status: Status of all phases
        """
        abort_timestamp = self.abort_signal.get_timestamp()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'phase_metrics': self.get_phase_metrics(),
            'resource_usage': self.resource_limits.get_usage_history(),
            'abort_status': {
                'is_aborted': self.abort_signal.is_aborted(),
                'reason': self.abort_signal.get_reason(),
                'timestamp': abort_timestamp.isoformat() if abort_timestamp else None,
            },
            'phase_status': dict(self._phase_status),
        }

    def _load_configuration(self) -> dict[str, Any]:
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[0]
        start = time.perf_counter()

        # Use pre-loaded monolith data (I/O-free path)
        if self._monolith_data is not None:
            # Normalize monolith for hash and serialization (handles MappingProxyType)
            monolith = _normalize_monolith_for_hash(self._monolith_data)

            # Stable, content-based hash for reproducibility
            monolith_hash = hashlib.sha256(
                json.dumps(monolith, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
        else:
            raise ValueError(
                "No monolith data available. Use saaaaaa.core.orchestrator.factory to load "
                "data and pass via monolith parameter for I/O-free initialization."
            )

        micro_questions: list[dict[str, Any]] = monolith["blocks"].get("micro_questions", [])
        meso_questions: list[dict[str, Any]] = monolith["blocks"].get("meso_questions", [])
        macro_question: dict[str, Any] = monolith["blocks"].get("macro_question", {})

        question_total = len(micro_questions) + len(meso_questions) + (1 if macro_question else 0)
        if question_total != EXPECTED_QUESTION_COUNT:
            logger.warning("Question count mismatch: expected %s, got %s", EXPECTED_QUESTION_COUNT, question_total)
            instrumentation.record_error("integrity", f"Conteo de preguntas inesperado: {question_total}", expected=EXPECTED_QUESTION_COUNT, found=question_total)

        structure_report = self._validate_contract_structure(monolith, instrumentation)

        method_summary: dict[str, Any] = {}
        # Use pre-loaded method_map data (I/O-free path)
        if self._method_map_data is not None:
            method_map = self._method_map_data

            # ========================================================================
            # PROMPT_NONEMPTY_EXECUTION_GRAPH_ENFORCER: Validate method_map is non-empty
            # Cannot route methods with empty map
            # ========================================================================
            if not method_map:
                raise RuntimeError(
                    "Method map is empty - cannot route methods. "
                    "A non-empty method map is required for orchestration."
                )

            summary = method_map.get("summary", {})
            total_methods = summary.get("total_methods")
            if total_methods != EXPECTED_METHOD_COUNT:
                logger.warning("Method count mismatch: expected %s, got %s", EXPECTED_METHOD_COUNT, total_methods)
                instrumentation.record_error(
                    "catalog",
                    "Total de métodos inesperado",
                    expected=EXPECTED_METHOD_COUNT,
                    found=total_methods,
                )
            method_summary = {
                "total_methods": total_methods,
                "metadata": summary,
            }

        schema_report: dict[str, Any] = {"errors": []}
        # Use pre-loaded schema data (I/O-free path)
        if self._schema_data is not None:
            try:  # pragma: no cover - optional dependency
                import jsonschema

                schema = self._schema_data

                validator = jsonschema.Draft202012Validator(schema)
                schema_errors = [
                    {
                        "path": list(error.path),
                        "message": error.message,
                    }
                    for error in validator.iter_errors(monolith)
                ]
                schema_report["errors"] = schema_errors
                if schema_errors:
                    instrumentation.record_error(
                        "schema",
                        f"Validation errors: {len(schema_errors)}",
                        count=len(schema_errors),
                    )
            except ImportError:
                logger.warning("jsonschema not installed, skipping schema validation")

        duration = time.perf_counter() - start
        instrumentation.increment(latency=duration)

        aggregation_settings = AggregationSettings.from_monolith(monolith)
        config = {
            "catalog": self.catalog,
            "monolith": monolith,
            "monolith_sha256": monolith_hash,
            "micro_questions": micro_questions,
            "meso_questions": meso_questions,
            "macro_question": macro_question,
            "structure_report": structure_report,
            "method_summary": method_summary,
            "schema_report": schema_report,
            # Internal aggregation settings (underscore denotes private use).
            # Created during Phase 0 as required by the C0-CONFIG-V1.0 contract.
            # Consumed by downstream aggregation logic in later phases.
            "_aggregation_settings": aggregation_settings,
        }

        return config

    def _validate_contract_structure(self, monolith: dict[str, Any], instrumentation: PhaseInstrumentation) -> dict[
        str, Any]:
        micro_questions = monolith["blocks"].get("micro_questions", [])
        base_slots = {question.get("base_slot") for question in micro_questions}
        modalities = {question.get("scoring_modality") for question in micro_questions}
        expected_modalities = {"TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E", "TYPE_F"}

        if len(base_slots) != 30:
            instrumentation.record_error(
                "structure",
                "Cantidad de slots base inválida",
                expected=30,
                found=len(base_slots),
            )

        missing_modalities = expected_modalities - modalities
        if missing_modalities:
            instrumentation.record_error(
                "structure",
                "Modalidades faltantes",
                missing=sorted(missing_modalities),
            )

        slot_area_map: dict[str, str] = {}
        area_cluster_map: dict[str, str] = {}
        for question in micro_questions:
            slot = question.get("base_slot")
            area = question.get("policy_area_id")
            cluster = question.get("cluster_id")
            if slot and area:
                previous = slot_area_map.setdefault(slot, area)
                if previous != area:
                    instrumentation.record_error(
                        "structure",
                        "Asignación de área inconsistente",
                        base_slot=slot,
                        previous=previous,
                        current=area,
                    )
            if area and cluster:
                previous_cluster = area_cluster_map.setdefault(area, cluster)
                if previous_cluster != cluster:
                    instrumentation.record_error(
                        "structure",
                        "Área asignada a múltiples clústeres",
                        area=area,
                        previous=previous_cluster,
                        current=cluster,
                    )

        return {
            "base_slots": sorted(base_slots),
            "modalities": sorted(modalities),
            "slot_area_map": slot_area_map,
            "area_cluster_map": area_cluster_map,
        }

    def _ingest_document(self, pdf_path: str, config: dict[str, Any]) -> PreprocessedDocument:
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[1]
        start = time.perf_counter()

        document_id = os.path.splitext(os.path.basename(pdf_path))[0] or "doc_1"

        # Initialize and run the canonical SPC ingestion pipeline
        try:
            from saaaaaa.processing.spc_ingestion import CPPIngestionPipeline
            from pathlib import Path

            pipeline = CPPIngestionPipeline()
            # Note: The process method in the pipeline is async
            canon_package = asyncio.run(pipeline.process(
                document_path=Path(pdf_path),
                document_id=document_id
            ))
        except ImportError as e:
            error_msg = f"Failed to import CPPIngestionPipeline: {e}"
            instrumentation.record_error("ingestion", "Import Error", reason=error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"SPC Ingestion pipeline failed: {e}"
            instrumentation.record_error("ingestion", "Pipeline Failure", reason=error_msg)
            raise RuntimeError(error_msg) from e

        # Adapt the output CanonPolicyPackage to the PreprocessedDocument format
        try:
            preprocessed = PreprocessedDocument.ensure(
                canon_package, document_id=document_id, use_spc_ingestion=True
            )
        except (TypeError, ValueError) as exc:
            error_msg = f"Failed to adapt CanonPolicyPackage to PreprocessedDocument: {exc}"
            instrumentation.record_error(
                "ingestion", "Adapter Error", reason=error_msg
            )
            raise TypeError(error_msg) from exc

        # Validate that the document is not empty
        if not preprocessed.raw_text or not preprocessed.raw_text.strip():
            error_msg = "Empty document after ingestion - raw_text is empty or whitespace-only"
            instrumentation.record_error(
                "ingestion", "Empty document", reason=error_msg
            )
            raise ValueError(error_msg)

        # === P01-ES v1.0 VALIDATION GATES ===
        # 1. Enforce strict chunk count of 60
        actual_chunk_count = preprocessed.metadata.get("chunk_count", 0)
        if actual_chunk_count != P01_EXPECTED_CHUNK_COUNT:
            error_msg = (
                f"P01 Validation Failed: Expected exactly {P01_EXPECTED_CHUNK_COUNT} chunks, "
                f"but found {actual_chunk_count}."
            )
            instrumentation.record_error("ingestion", "Chunk Count Mismatch", reason=error_msg)
            raise ValueError(error_msg)

        # 2. Enforce presence of policy_area_id and dimension_id in all chunks
        if not preprocessed.chunks:
            error_msg = "P01 Validation Failed: No chunks found in PreprocessedDocument."
            instrumentation.record_error("ingestion", "Empty Chunk List", reason=error_msg)
            raise ValueError(error_msg)

        for i, chunk in enumerate(preprocessed.chunks):
            # The chunk object from the adapter is a dataclass, so we use getattr
            if not getattr(chunk, 'policy_area_id', None):
                error_msg = f"P01 Validation Failed: Chunk {i} is missing 'policy_area_id'."
                instrumentation.record_error("ingestion", "Missing Metadata", reason=error_msg)
                raise ValueError(error_msg)
            if not getattr(chunk, 'dimension_id', None):
                error_msg = f"P01 Validation Failed: Chunk {i} is missing 'dimension_id'."
                instrumentation.record_error("ingestion", "Missing Metadata", reason=error_msg)
                raise ValueError(error_msg)

        logger.info(f"✅ P01-ES v1.0 validation gates passed for {actual_chunk_count} chunks.")

        text_length = len(preprocessed.raw_text)
        sentence_count = len(preprocessed.sentences) if preprocessed.sentences else 0
        adapter_source = preprocessed.metadata.get("adapter_source", "unknown")

        # Store ingestion information for verification manifest
        ingestion_info = {
            "method": "SPC",  # Only SPC is supported
            "chunk_count": chunk_count,
            "text_length": text_length,
            "sentence_count": sentence_count,
            "adapter_source": adapter_source,
            "chunk_strategy": preprocessed.metadata.get("chunk_strategy", "semantic"),
        }
        if "chunk_overlap" in preprocessed.metadata:
            ingestion_info["chunk_overlap"] = preprocessed.metadata["chunk_overlap"]

        # Store in context for manifest generation
        if hasattr(self, "_context"):
            self._context["ingestion_info"] = ingestion_info

        logger.info(
            f"Document ingested successfully: document_id={document_id}, "
            f"method=SPC, text_length={text_length}, chunk_count={chunk_count}, "
            f"sentence_count={sentence_count}"
        )

        duration = time.perf_counter() - start
        instrumentation.increment(latency=duration)
        return preprocessed

    async def _execute_micro_questions_async(
            self,
            document: PreprocessedDocument,
            config: dict[str, Any],
    ) -> list[MicroQuestionRun]:
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[2]
        micro_questions = config.get("micro_questions", [])
        instrumentation.items_total = len(micro_questions)
        ordered_questions: list[dict[str, Any]] = []

        # NEW: Initialize chunk router for chunk-aware execution
        chunk_routes: dict[int, Any] = {}
        if document.processing_mode == "chunked" and document.chunks:
            try:
                from saaaaaa.core.orchestrator.chunk_router import ChunkRouter
                router = ChunkRouter()

                # Route chunks to executors
                for chunk in document.chunks:
                    route = router.route_chunk(chunk)
                    if not route.skip_reason:
                        chunk_routes[chunk.id] = route

                logger.info(
                    f"Chunk-aware execution enabled: routed {len(chunk_routes)} chunks "
                    f"from {len(document.chunks)} total chunks"
                )
            except ImportError:
                logger.warning("ChunkRouter not available, falling back to flat mode")
                chunk_routes = {}

        # STRICT ORDERING: Dimension -> Policy Area -> Question ID
        # This enforces the requirement: "FIRST ALL THE QUESTIONS OF DIMENSION 1... THEN SECOND DIMENSION..."
        ordered_questions = sorted(
            micro_questions,
            key=lambda q: (
                q.get("dimension_id", "DIM99"),
                q.get("policy_area_id", "PA99"),
                q.get("question_id", "Q999")
            )
        )

        semaphore = asyncio.Semaphore(self.resource_limits.max_workers)
        self.resource_limits.attach_semaphore(semaphore)

        circuit_breakers: dict[str, dict[str, Any]] = {
            slot: {"failures": 0, "open": False}
            for slot in self.executors
        }

        results: list[MicroQuestionRun] = []

        # NEW: Track chunk execution metrics
        execution_metrics = {
            "chunk_executions": 0,  # Actual chunk-level executions
            "full_doc_executions": 0,  # Fallback full document executions
            "total_chunks_processed": 0,  # Total chunks that could have been processed
        }

        async def process_question(question: dict[str, Any]) -> MicroQuestionRun:
            await self.resource_limits.apply_worker_budget()
            async with semaphore:
                self._ensure_not_aborted()
                question_id = question.get("question_id", "")
                question_global = int(question.get("question_global", 0))
                base_slot = question.get("base_slot", "")
                metadata = {
                    key: question.get(key)
                    for key in (
                        "question_id",
                        "question_global",
                        "base_slot",
                        "dimension_id",
                        "policy_area_id",
                        "cluster_id",
                        "scoring_modality",
                        "expected_elements",
                    )
                }

                circuit = circuit_breakers.setdefault(base_slot, {"failures": 0, "open": False})
                if circuit.get("open"):
                    instrumentation.record_warning(
                        "circuit_breaker",
                        "Circuit breaker abierto, pregunta omitida",
                        base_slot=base_slot,
                        question_id=question_id,
                    )
                    instrumentation.increment()
                    return MicroQuestionRun(
                        question_id=question_id,
                        question_global=question_global,
                        base_slot=base_slot,
                        metadata=metadata,
                        evidence=None,
                        error="circuit_breaker_open",
                        aborted=False,
                    )

                usage = self.resource_limits.get_resource_usage()
                mem_exceeded, usage = self.resource_limits.check_memory_exceeded(usage)
                cpu_exceeded, usage = self.resource_limits.check_cpu_exceeded(usage)
                if mem_exceeded:
                    instrumentation.record_warning("resource", "Límite de memoria excedido", usage=usage)
                if cpu_exceeded:
                    instrumentation.record_warning("resource", "Límite de CPU excedido", usage=usage)

                start_time = time.perf_counter()
                executor_class = self.executors.get(base_slot)
                evidence: Evidence | None = None
                error_message: str | None = None

                if not executor_class:
                    error_message = f"Ejecutor no definido para {base_slot}"
                    instrumentation.record_error("executor", error_message, base_slot=base_slot)
                else:
                    try:
                        executor_instance = executor_class(
                            self.executor,
                            signal_registry=self.executor.signal_registry,
                            config=self.executor_config,
                            questionnaire_provider=self.questionnaire_provider,
                            calibration_orchestrator=self.calibration_orchestrator
                        )

                        # STRICT FILTERING: Pass ONLY chunks matching the question's PA and DIM
                        target_pa = question.get("policy_area_id")
                        target_dim = question.get("dimension_id")

                        filtered_chunks = [
                            c for c in document.chunks
                            if c.policy_area_id == target_pa and c.dimension_id == target_dim
                        ]

                        # Create scoped document with ONLY relevant chunks
                        scoped_document = replace(document, chunks=filtered_chunks)

                        # Execute question with SCOPED document
                        evidence = await asyncio.to_thread(
                            executor_instance.execute,
                            scoped_document,
                            self.executor,
                            question_context=question
                        )
                        circuit["failures"] = 0
                    except Exception as exc:
                        circuit["failures"] += 1
                        error_message = str(exc)
                        instrumentation.record_error(
                            "micro_question",
                            error_message,
                            base_slot=base_slot,
                            question_id=question_id,
                        )
                        if circuit["failures"] >= 3:
                            circuit["open"] = True
                            instrumentation.record_warning(
                                "circuit_breaker",
                                "Circuit breaker activado",
                                base_slot=base_slot,
                            )

                duration = time.perf_counter() - start_time
                instrumentation.increment(latency=duration)
                if instrumentation.items_processed % 10 == 0:
                    instrumentation.record_warning(
                        "progress",
                        "Progreso de micro preguntas",
                        processed=instrumentation.items_processed,
                        total=instrumentation.items_total,
                    )

                return MicroQuestionRun(
                    question_id=question_id,
                    question_global=question_global,
                    base_slot=base_slot,
                    metadata=metadata,
                    evidence=evidence,
                    error=error_message,
                    duration_ms=duration * 1000.0,
                    aborted=self.abort_signal.is_aborted(),
                )

        tasks = [asyncio.create_task(process_question(question)) for question in ordered_questions]

        try:
            for task in asyncio.as_completed(tasks):
                result = await task
                results.append(result)
                if self.abort_signal.is_aborted():
                    raise AbortRequested(self.abort_signal.get_reason() or "Abort requested")
        except AbortRequested:
            for task in tasks:
                task.cancel()
            raise

        # Log chunk execution metrics
        if chunk_routes and document.processing_mode == "chunked":
            total_possible = len(micro_questions) * len(document.chunks)
            actual_executed = execution_metrics["chunk_executions"] + execution_metrics["full_doc_executions"]
            savings_pct = ((total_possible - actual_executed) / max(total_possible, 1)) * 100 if total_possible > 0 else 0

            logger.info(
                f"Chunk execution metrics: {execution_metrics['chunk_executions']} chunk-scoped, "
                f"{execution_metrics['full_doc_executions']} full-doc, "
                f"{total_possible} total possible, "
                f"savings: {savings_pct:.1f}%"
            )

            # Store metrics for verification manifest
            if not hasattr(self, '_execution_metrics'):
                self._execution_metrics = {}
            self._execution_metrics['phase_2'] = {
                'chunk_executions': execution_metrics['chunk_executions'],
                'full_doc_executions': execution_metrics['full_doc_executions'],
                'total_possible_executions': total_possible,
                'actual_executions': actual_executed,
                'savings_percent': savings_pct,
            }

        return results

    async def _score_micro_results_async(
            self,
            micro_results: list[MicroQuestionRun],
            config: dict[str, Any],
    ) -> list[ScoredMicroQuestion]:
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[3]
        instrumentation.items_total = len(micro_results)

        # Import from the flat scoring.py module file
        import importlib.util
        from pathlib import Path
        scoring_file_path = Path(__file__).parent.parent.parent / "analysis" / "scoring.py"
        spec = importlib.util.spec_from_file_location("scoring_flat", scoring_file_path)
        scoring_flat = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scoring_flat)
        ScoringEvidence = scoring_flat.Evidence
        MicroQuestionScorer = scoring_flat.MicroQuestionScorer
        ScoringModality = scoring_flat.ScoringModality

        scorer = MicroQuestionScorer()
        results: list[ScoredMicroQuestion] = []
        semaphore = asyncio.Semaphore(self.resource_limits.max_workers)
        self.resource_limits.attach_semaphore(semaphore)

        async def score_item(item: MicroQuestionRun) -> ScoredMicroQuestion:
            async with semaphore:
                await self.resource_limits.apply_worker_budget()
                self._ensure_not_aborted()
                start = time.perf_counter()

                modality_value = item.metadata.get("scoring_modality", "TYPE_A")
                try:
                    modality = ScoringModality(modality_value)
                except Exception:
                    modality = ScoringModality.TYPE_A

                if item.error or not item.evidence:
                    instrumentation.record_warning(
                        "scoring",
                        "Evidencia ausente para scoring",
                        question_id=item.question_id,
                        error=item.error,
                    )
                    instrumentation.increment(latency=time.perf_counter() - start)
                    return ScoredMicroQuestion(
                        question_id=item.question_id,
                        question_global=item.question_global,
                        base_slot=item.base_slot,
                        score=None,
                        normalized_score=None,
                        quality_level=None,
                        evidence=item.evidence,
                        metadata=item.metadata,
                        error=item.error or "missing_evidence",
                    )

                # Handle evidence as either dict or dataclass
                if isinstance(item.evidence, dict):
                    elements_found = item.evidence.get("elements", [])
                    raw_results = item.evidence.get("raw_results", {})
                else:
                    elements_found = getattr(item.evidence, "elements", [])
                    raw_results = getattr(item.evidence, "raw_results", {})

                scoring_evidence = ScoringEvidence(
                    elements_found=elements_found,
                    confidence_scores=raw_results.get("confidence_scores", []),
                    semantic_similarity=raw_results.get("semantic_similarity"),
                    pattern_matches=raw_results.get("pattern_matches", {}),
                    metadata=raw_results,
                )

                try:
                    scored = await asyncio.to_thread(
                        scorer.apply_scoring_modality,
                        item.question_id,
                        item.question_global,
                        modality,
                        scoring_evidence,
                    )
                    duration = time.perf_counter() - start
                    instrumentation.increment(latency=duration)
                    return ScoredMicroQuestion(
                        question_id=scored.question_id,
                        question_global=scored.question_global,
                        base_slot=item.base_slot,
                        score=scored.raw_score,
                        normalized_score=scored.normalized_score,
                        quality_level=scored.quality_level.value,
                        evidence=item.evidence,
                        scoring_details=scored.scoring_details,
                        metadata=item.metadata,
                    )
                except Exception as exc:  # pragma: no cover - dependencia externa
                    instrumentation.record_error(
                        "scoring",
                        str(exc),
                        question_id=item.question_id,
                    )
                    duration = time.perf_counter() - start
                    instrumentation.increment(latency=duration)
                    return ScoredMicroQuestion(
                        question_id=item.question_id,
                        question_global=item.question_global,
                        base_slot=item.base_slot,
                        score=None,
                        normalized_score=None,
                        quality_level=None,
                        evidence=item.evidence,
                        metadata=item.metadata,
                        error=str(exc),
                    )

        tasks = [asyncio.create_task(score_item(item)) for item in micro_results]
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
            if self.abort_signal.is_aborted():
                raise AbortRequested(self.abort_signal.get_reason() or "Abort requested")

        return results

    async def _aggregate_dimensions_async(
            self,
            scored_results: list[ScoredMicroQuestion],
            config: dict[str, Any],
    ) -> list[DimensionScore]:
        """Aggregate micro question scores into dimension scores using DimensionAggregator.

        Args:
            scored_results: List of scored micro questions
            config: Configuration dict containing monolith

        Returns:
            List of DimensionScore objects with full validation and diagnostics
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[4]

        # Get monolith from config
        monolith = config.get("monolith")
        if not monolith:
            logger.error("No monolith in config for dimension aggregation")
            return []

        aggregation_settings = config.setdefault(
            "_aggregation_settings",
            AggregationSettings.from_monolith(monolith),
        )

        # Initialize dimension aggregator
        aggregator = DimensionAggregator(
            monolith,
            abort_on_insufficient=False,
            aggregation_settings=aggregation_settings,
        )

        scored_payloads: list[dict[str, Any]] = []
        for item in scored_results:
            metadata = item.metadata or {}
            if item.score is None:
                continue
            policy_area = metadata.get("policy_area_id") or metadata.get("policy_area") or ""
            dimension = metadata.get("dimension_id") or metadata.get("dimension") or ""
            evidence_payload: dict[str, Any]
            if item.evidence and is_dataclass(item.evidence):
                evidence_payload = asdict(item.evidence)
            elif isinstance(item.evidence, dict):
                evidence_payload = item.evidence
            else:
                evidence_payload = {}
            raw_results = item.scoring_details if isinstance(item.scoring_details, dict) else {}
            scored_payloads.append(
                {
                    "question_global": item.question_global,
                    "base_slot": item.base_slot,
                    "policy_area": str(policy_area),
                    "dimension": str(dimension),
                    "score": float(item.score),
                    "quality_level": str(item.quality_level or "INSUFICIENTE"),
                    "evidence": evidence_payload,
                    "raw_results": raw_results,
                }
            )

        if not scored_payloads:
            instrumentation.items_total = 0
            return []

        try:
            validated_results = validate_scored_results(scored_payloads)
        except ValidationError as exc:
            logger.error("Invalid scored results for dimension aggregation: %s", exc)
            raise

        group_by_keys = aggregator.dimension_group_by_keys
        key_func = lambda result: tuple(getattr(result, key, None) for key in group_by_keys)
        grouped_results = group_by(validated_results, key_func)

        instrumentation.items_total = len(grouped_results)
        dimension_scores: list[DimensionScore] = []

        for group_key, items in grouped_results.items():
            self._ensure_not_aborted()
            await asyncio.sleep(0)
            start = time.perf_counter()
            group_by_values = dict(zip(group_by_keys, group_key, strict=False))
            try:
                dim_score = aggregator.aggregate_dimension(
                    scored_results=items,
                    group_by_values=group_by_values,
                )
                dimension_scores.append(dim_score)
            except Exception as exc:
                logger.error(
                    "Failed to aggregate dimension %s/%s: %s",
                    group_by_values.get("dimension"),
                    group_by_values.get("policy_area"),
                    exc,
                )
            instrumentation.increment(latency=time.perf_counter() - start)

        return dimension_scores

    async def _aggregate_policy_areas_async(
            self,
            dimension_scores: list[DimensionScore],
            config: dict[str, Any],
    ) -> list[AreaScore]:
        """Aggregate dimension scores into policy area scores using AreaPolicyAggregator.

        Args:
            dimension_scores: List of DimensionScore objects
            config: Configuration dict containing monolith

        Returns:
            List of AreaScore objects with full validation and diagnostics
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[5]

        # Get monolith from config
        monolith = config.get("monolith")
        if not monolith:
            logger.error("No monolith in config for area aggregation")
            return []

        aggregation_settings = config.setdefault(
            "_aggregation_settings",
            AggregationSettings.from_monolith(monolith),
        )

        # Initialize area aggregator
        aggregator = AreaPolicyAggregator(
            monolith,
            abort_on_insufficient=False,
            aggregation_settings=aggregation_settings,
        )

        group_by_keys = aggregator.area_group_by_keys
        key_func = lambda score: tuple(getattr(score, key, None) for key in group_by_keys)
        grouped_scores = group_by(dimension_scores, key_func)

        instrumentation.items_total = len(grouped_scores)
        area_scores: list[AreaScore] = []

        for group_key, scores in grouped_scores.items():
            self._ensure_not_aborted()
            await asyncio.sleep(0)
            start = time.perf_counter()
            group_by_values = dict(zip(group_by_keys, group_key, strict=False))
            try:
                area_score = aggregator.aggregate_area(
                    dimension_scores=scores,
                    group_by_values=group_by_values,
                )
                area_scores.append(area_score)
            except Exception as exc:
                logger.error(
                    "Failed to aggregate policy area %s: %s",
                    group_by_values.get("area_id"),
                    exc,
                )
            instrumentation.increment(latency=time.perf_counter() - start)

        return area_scores

    def _aggregate_clusters(
            self,
            policy_area_scores: list[AreaScore],
            config: dict[str, Any],
    ) -> list[ClusterScore]:
        """Aggregate policy area scores into cluster scores using ClusterAggregator.

        Args:
            policy_area_scores: List of AreaScore objects
            config: Configuration dict containing monolith

        Returns:
            List of ClusterScore objects with full validation and diagnostics
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[6]

        # Get monolith from config
        monolith = config.get("monolith")
        if not monolith:
            logger.error("No monolith in config for cluster aggregation")
            return []

        aggregation_settings = config.setdefault(
            "_aggregation_settings",
            AggregationSettings.from_monolith(monolith),
        )

        # Initialize cluster aggregator
        aggregator = ClusterAggregator(
            monolith,
            abort_on_insufficient=False,
            aggregation_settings=aggregation_settings,
        )

        clusters = monolith["blocks"]["niveles_abstraccion"]["clusters"]

        area_to_cluster: dict[str, str] = {}
        for cluster in clusters:
            cluster_id = cluster.get("cluster_id")
            for area_id in cluster.get("policy_area_ids", []):
                if cluster_id and area_id:
                    area_to_cluster[area_id] = cluster_id

        enriched_scores: list[AreaScore] = []
        for score in policy_area_scores:
            cluster_id = area_to_cluster.get(score.area_id)
            if not cluster_id:
                logger.warning(
                    "Area %s not mapped to any cluster definition",
                    score.area_id,
                )
                continue
            score.cluster_id = cluster_id
            enriched_scores.append(score)

        group_by_keys = aggregator.cluster_group_by_keys
        key_func = lambda area_score: tuple(getattr(area_score, key, None) for key in group_by_keys)
        grouped_scores = group_by(enriched_scores, key_func)

        instrumentation.items_total = len(grouped_scores)
        cluster_scores: list[ClusterScore] = []

        for group_key, scores in grouped_scores.items():
            self._ensure_not_aborted()
            start = time.perf_counter()
            group_by_values = dict(zip(group_by_keys, group_key, strict=False))
            try:
                cluster_score = aggregator.aggregate_cluster(
                    area_scores=scores,
                    group_by_values=group_by_values,
                )
                cluster_scores.append(cluster_score)
            except Exception as exc:
                logger.error(
                    "Failed to aggregate cluster %s: %s",
                    group_by_values.get("cluster_id"),
                    exc,
                )
            instrumentation.increment(latency=time.perf_counter() - start)

        return cluster_scores

    def _evaluate_macro(self, cluster_scores: list[ClusterScore], config: dict[str, Any]) -> MacroScoreDict:
        """Evaluate macro level using MacroAggregator.

        Args:
            cluster_scores: List of ClusterScore objects from FASE 6
            config: Configuration dict containing monolith

        Returns:
            MacroScoreDict with macro_score, macro_score_normalized, and cluster_scores
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[7]
        start = time.perf_counter()

        # Get monolith from config
        monolith = config.get("monolith")
        if not monolith:
            logger.error("No monolith in config for macro evaluation")
            macro_score = MacroScore(
                score=0.0,
                quality_level="INSUFICIENTE",
                cross_cutting_coherence=0.0,
                systemic_gaps=[],
                strategic_alignment=0.0,
                cluster_scores=[],
                validation_passed=False,
                validation_details={"error": "No monolith", "type": "config"}
            )
            result: MacroScoreDict = {
                "macro_score": macro_score,
                "macro_score_normalized": 0.0,
                "cluster_scores": cluster_scores,
                "cross_cutting_coherence": macro_score.cross_cutting_coherence,
                "systemic_gaps": macro_score.systemic_gaps,
                "strategic_alignment": macro_score.strategic_alignment,
                "quality_band": macro_score.quality_level,
            }
            return result

        aggregation_settings = config.setdefault(
            "_aggregation_settings",
            AggregationSettings.from_monolith(monolith),
        )

        # Initialize macro aggregator
        aggregator = MacroAggregator(
            monolith,
            abort_on_insufficient=False,
            aggregation_settings=aggregation_settings,
        )

        # Extract area_scores and dimension_scores from cluster_scores
        area_scores: list[AreaScore] = []
        dimension_scores: list[DimensionScore] = []

        for cluster in cluster_scores:
            area_scores.extend(cluster.area_scores)
            for area in cluster.area_scores:
                dimension_scores.extend(area.dimension_scores)

        # Remove duplicates (in case areas appear in multiple clusters)
        seen_areas = set()
        unique_areas = []
        for area in area_scores:
            if area.area_id not in seen_areas:
                seen_areas.add(area.area_id)
                unique_areas.append(area)

        seen_dims = set()
        unique_dims = []
        for dim in dimension_scores:
            key = (dim.dimension_id, dim.area_id)
            if key not in seen_dims:
                seen_dims.add(key)
                unique_dims.append(dim)

        # Evaluate macro
        try:
            macro_score = aggregator.evaluate_macro(
                cluster_scores=cluster_scores,
                area_scores=unique_areas,
                dimension_scores=unique_dims
            )
        except Exception as e:
            logger.error(f"Failed to evaluate macro: {e}")
            macro_score = MacroScore(
                score=0.0,
                quality_level="INSUFICIENTE",
                cross_cutting_coherence=0.0,
                systemic_gaps=[],
                strategic_alignment=0.0,
                cluster_scores=cluster_scores,
                validation_passed=False,
                validation_details={"error": str(e), "type": "exception"}
            )

        instrumentation.increment(latency=time.perf_counter() - start)
        # macro_score is already normalized to 0-1 range from averaging cluster scores
        # Extract the score field from the MacroScore object with explicit float conversion
        macro_score_normalized = float(macro_score.score) if isinstance(macro_score, MacroScore) else float(macro_score)

        result: MacroScoreDict = {
            "macro_score": macro_score,
            "macro_score_normalized": macro_score_normalized,
            "cluster_scores": cluster_scores,
            "cross_cutting_coherence": macro_score.cross_cutting_coherence,
            "systemic_gaps": macro_score.systemic_gaps,
            "strategic_alignment": macro_score.strategic_alignment,
            "quality_band": macro_score.quality_level,
        }
        return result

    async def _generate_recommendations(
            self,
            macro_result: dict[str, Any],
            config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate recommendations at MICRO, MESO, and MACRO levels using RecommendationEngine.

        This phase connects to the orchestrator's 3-level flux:
        - MICRO: Uses scored question results from phase 3
        - MESO: Uses cluster aggregations from phase 6
        - MACRO: Uses macro evaluation from phase 7

        Args:
            macro_result: Macro evaluation results from phase 7
            config: Configuration dictionary

        Returns:
            Dictionary with MICRO, MESO, and MACRO recommendations
        """
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[8]
        start = time.perf_counter()

        await asyncio.sleep(0)

        # If RecommendationEngine is not available, return empty recommendations
        if self.recommendation_engine is None:
            logger.warning("RecommendationEngine not available, returning empty recommendations")
            recommendations = {
                "MICRO": {"level": "MICRO", "recommendations": [], "generated_at": datetime.utcnow().isoformat()},
                "MESO": {"level": "MESO", "recommendations": [], "generated_at": datetime.utcnow().isoformat()},
                "MACRO": {"level": "MACRO", "recommendations": [], "generated_at": datetime.utcnow().isoformat()},
                "macro_score": macro_result.get("macro_score"),
            }
            instrumentation.increment(latency=time.perf_counter() - start)
            return recommendations

        try:
            # ========================================================================
            # MICRO LEVEL: Transform scored results to PA-DIM scores
            # ========================================================================
            micro_scores: dict[str, float] = {}
            scored_results = self._context.get('scored_results', [])

            # Group by policy area and dimension to calculate average scores
            pa_dim_groups: dict[str, list[float]] = {}
            for result in scored_results:
                if hasattr(result, 'metadata') and result.metadata:
                    pa_id = result.metadata.get('policy_area_id')
                    dim_id = result.metadata.get('dimension_id')
                    score = result.normalized_score

                    if pa_id and dim_id and score is not None:
                        key = f"{pa_id}-{dim_id}"
                        if key not in pa_dim_groups:
                            pa_dim_groups[key] = []
                        pa_dim_groups[key].append(score)

            # Calculate average for each PA-DIM combination
            for key, scores in pa_dim_groups.items():
                if scores:
                    micro_scores[key] = sum(scores) / len(scores)

            logger.info(f"Extracted {len(micro_scores)} MICRO PA-DIM scores for recommendations")

            # ========================================================================
            # MESO LEVEL: Transform cluster scores
            # ========================================================================
            cluster_data: dict[str, Any] = {}
            cluster_scores = self._context.get('cluster_scores', [])

            for cluster in cluster_scores:
                cluster_id = cluster.get('cluster_id')
                cluster_score = cluster.get('score')
                areas = cluster.get('areas', [])

                if cluster_id and cluster_score is not None:
                    # cluster_score is already normalized to 0-1 range from aggregation
                    normalized_cluster_score = cluster_score

                    # Calculate variance across areas in this cluster using normalized scores
                    # area scores are already normalized to 0-1 range from aggregation
                    valid_area_scores = [
                        (area, area.get('score'))
                        for area in areas
                        if area.get('score') is not None
                    ]
                    normalized_area_values = [score for _, score in valid_area_scores]
                    variance = (
                        statistics.variance(normalized_area_values)
                        if len(normalized_area_values) > 1
                        else 0.0
                    )

                    # Find weakest policy area in cluster
                    weakest_area = (
                        min(valid_area_scores, key=lambda item: item[1])
                        if valid_area_scores
                        else None
                    )
                    weak_pa = weakest_area[0].get('area_id') if weakest_area else None

                    cluster_data[cluster_id] = {
                        'score': normalized_cluster_score * self.PERCENTAGE_SCALE,  # 0-100 scale
                        'variance': variance,
                        'weak_pa': weak_pa
                    }

            logger.info(f"Extracted {len(cluster_data)} MESO cluster metrics for recommendations")

            # ========================================================================
            # MACRO LEVEL: Transform macro evaluation
            # ========================================================================
            macro_score = macro_result.get('macro_score')
            macro_score_normalized = macro_result.get('macro_score_normalized')

            # macro_score is already normalized to 0-1 range
            # Extract the score value if macro_score is a MacroScore object
            if macro_score is not None and macro_score_normalized is None:
                macro_score_normalized = macro_score.score if isinstance(macro_score, MacroScore) else macro_score

            # Extract numeric value from macro_score_normalized (may be dict/object)
            macro_score_numeric = None
            if macro_score_normalized is not None:
                if isinstance(macro_score_normalized, dict):
                    macro_score_numeric = macro_score_normalized.get('score')
                elif hasattr(macro_score_normalized, 'score'):
                    try:
                        macro_score_numeric = macro_score_normalized.score
                    except (AttributeError, TypeError) as e:
                        logger.warning(f"Failed to extract score attribute: {e}")
                        macro_score_numeric = None
                else:
                    # Already a numeric value
                    macro_score_numeric = macro_score_normalized

                # Validate that extracted value is numeric
                if macro_score_numeric is not None and not isinstance(macro_score_numeric, (int, float)):
                    logger.warning(
                        f"Expected numeric macro_score, got {type(macro_score_numeric).__name__}: {macro_score_numeric!r}"
                    )
                    macro_score_numeric = None

            # Determine macro band based on score
            macro_band = 'INSUFICIENTE'
            if macro_score_numeric is not None:
                scaled_score = float(macro_score_numeric) * self.PERCENTAGE_SCALE
                if scaled_score >= 75:
                    macro_band = 'SATISFACTORIO'
                elif scaled_score >= 55:
                    macro_band = 'ACEPTABLE'
                elif scaled_score >= 35:
                    macro_band = 'DEFICIENTE'

            # Find clusters below target (< 55%)
            # cluster scores are already normalized to 0-1 range
            clusters_below_target = []
            for cluster in cluster_scores:
                cluster_id = cluster.get('cluster_id')
                cluster_score = cluster.get('score', 0)
                if cluster_score is not None and cluster_score * self.PERCENTAGE_SCALE < 55:
                    clusters_below_target.append(cluster_id)

            # Calculate overall variance
            # cluster scores are already normalized to 0-1 range
            normalized_cluster_scores = [
                c.get('score')
                for c in cluster_scores
                if c.get('score') is not None
            ]
            overall_variance = (
                statistics.variance(normalized_cluster_scores)
                if len(normalized_cluster_scores) > 1
                else 0.0
            )

            variance_alert = 'BAJA'
            if overall_variance >= 0.18:
                variance_alert = 'ALTA'
            elif overall_variance >= 0.08:
                variance_alert = 'MODERADA'

            # Find priority micro gaps (lowest scoring PA-DIM combinations)
            sorted_micro = sorted(micro_scores.items(), key=lambda x: x[1])
            priority_micro_gaps = [k for k, v in sorted_micro[:5] if v < 0.55]

            macro_data = {
                'macro_band': macro_band,
                'clusters_below_target': clusters_below_target,
                'variance_alert': variance_alert,
                'priority_micro_gaps': priority_micro_gaps,
                'macro_score_percentage': (
                    float(macro_score_numeric) * self.PERCENTAGE_SCALE if macro_score_numeric is not None else None
                )
            }

            logger.info(f"Macro band: {macro_band}, Clusters below target: {len(clusters_below_target)}")

            # ========================================================================
            # GENERATE RECOMMENDATIONS AT ALL 3 LEVELS
            # ========================================================================
            context = {
                'generated_at': datetime.utcnow().isoformat(),
                'macro_score': macro_score
            }

            recommendation_sets = self.recommendation_engine.generate_all_recommendations(
                micro_scores=micro_scores,
                cluster_data=cluster_data,
                macro_data=macro_data,
                context=context
            )

            # Convert RecommendationSet objects to dictionaries
            recommendations = {
                level: rec_set.to_dict() for level, rec_set in recommendation_sets.items()
            }
            recommendations['macro_score'] = macro_score
            recommendations['macro_score_normalized'] = macro_score_normalized

            logger.info(
                f"Generated recommendations: "
                f"MICRO={len(recommendation_sets['MICRO'].recommendations)}, "
                f"MESO={len(recommendation_sets['MESO'].recommendations)}, "
                f"MACRO={len(recommendation_sets['MACRO'].recommendations)}"
            )

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}", exc_info=True)
            recommendations = {
                "MICRO": {"level": "MICRO", "recommendations": [], "generated_at": datetime.utcnow().isoformat()},
                "MESO": {"level": "MESO", "recommendations": [], "generated_at": datetime.utcnow().isoformat()},
                "MACRO": {"level": "MACRO", "recommendations": [], "generated_at": datetime.utcnow().isoformat()},
                "macro_score": macro_result.get("macro_score"),
                "error": str(e)
            }

        instrumentation.increment(latency=time.perf_counter() - start)
        return recommendations

    def _assemble_report(self, recommendations: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[9]
        start = time.perf_counter()

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "recommendations": recommendations,
            "metadata": {
                "monolith_sha256": config.get("monolith_sha256"),
                "method_summary": config.get("method_summary"),
            },
        }

        instrumentation.increment(latency=time.perf_counter() - start)
        return report

    async def _format_and_export(self, report: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        self._ensure_not_aborted()
        instrumentation = self._phase_instrumentation[10]
        start = time.perf_counter()

        await asyncio.sleep(0)
        export_payload = {
            "report": report,
            "phase_metrics": self.get_phase_metrics(),
            "completed_at": datetime.utcnow().isoformat(),
        }

        instrumentation.increment(latency=time.perf_counter() - start)
        return export_payload


def describe_pipeline_shape(
    monolith: dict[str, Any] | None = None,
    executor_instances: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe the actual pipeline shape from live data.

    Computes phase count, question count, and executor count from real data
    instead of using hard-coded constants.

    Args:
        monolith: Questionnaire monolith (if available)
        executor_instances: MethodExecutor.instances dict (if available)

    Returns:
        Dict with actual pipeline metrics
    """
    shape: dict[str, Any] = {
        "phases": len(Orchestrator.FASES),
    }

    if monolith:
        micro_questions = monolith.get("blocks", {}).get("micro_questions", [])
        meso_questions = monolith.get("blocks", {}).get("meso_questions", [])
        macro_question = monolith.get("blocks", {}).get("macro_question", {})
        question_total = len(micro_questions) + len(meso_questions) + (1 if macro_question else 0)
        shape["expected_micro_questions"] = question_total

    if executor_instances:
        shape["registered_executors"] = len(executor_instances)

    return shape

```

---

# SECCIÓN 5: MODELO MATEMÁTICO AMPLIFICADO

## 5.1. Fundamento: La Función de Calibración `Cal(I)`

El pilar del sistema de calidad y confianza de F.A.R.F.A.N. es la función de calibración, denotada como `Cal(I)`. El propósito de esta función es asignar una puntuación cuantitativa, normalizada en el intervalo `[0, 1]`, a cualquier instancia de método analítico (`I`) que se ejecuta dentro del pipeline. Un valor de `1` representa una confianza máxima en el resultado del método, mientras que un valor de `0` indica una falla crítica o una falta total de confianza.

Es fundamental entender que `Cal(I)` no es una simple métrica de "precisión". Es una función de agregación multidimensional que evalúa una instancia de método a través de un conjunto de "capas" (`Layers`) de calidad. Estas capas miden desde la calidad intrínseca del código hasta su compatibilidad con el contexto de análisis específico (la pregunta, la dimensión, el área de política) y la calidad del documento de entrada.

El modelo está diseñado para ser:
-   **Comprensivo:** Cubre todo el ciclo de vida de un método, desde su diseño teórico hasta su ejecución operativa.
-   **Sensible al Contexto:** El mismo método puede (y debe) recibir puntuaciones diferentes si se aplica a diferentes preguntas o a documentos de calidades distintas.
-   **Transparente y Auditable:** Cada componente de la puntuación final puede ser desglosado y rastreado hasta su evidencia de origen, como se especifica en la Sección 7 del `canonic_calibration_methods.md`.

## 5.2. El Operador de Fusión: Agregación de Choquet 2-Aditiva

La fórmula central que combina las puntuaciones de las diferentes capas en el `Cal(I)` final es un **Operador de Agregación de Choquet 2-Aditivo**. Esta elección no es arbitraria; se selecciona por su capacidad para modelar no solo la importancia individual de cada capa, sino también las **interacciones y sinergias** entre pares de capas.

### 5.2.1. Definición Formal

Dada una instancia de método `I` con un conjunto de capas activas `L(M)` y un conjunto de interacciones definidas `S_int ⊆ L(M) × L(M)`, la función de calibración se define como:

```
Cal(I) = Σ_{ℓ ∈ L(M)} a_ℓ · x_ℓ(I) + Σ_{(ℓ,k) ∈ S_int} a_ℓk · min(x_ℓ(I), x_k(I))
```

Donde:
-   `x_ℓ(I)`: Es la puntuación normalizada `[0, 1]` de la capa `ℓ`.
-   `a_ℓ`: Es el peso base (importancia intrínseca) de la capa `ℓ`.
-   `a_ℓk`: Es el peso de la interacción entre las capas `ℓ` y `k`.
-   `min(x_ℓ(I), x_k(I))`: Es el operador que captura el efecto "eslabón más débil".

### 5.2.2. Amplificación e Interpretación de la Fórmula

La fórmula se descompone en dos partes clave:

1.  **Suma Lineal Ponderada (`Σ a_ℓ · x_ℓ(I)`):**
    -   **Qué es:** Esta es la parte "clásica" de la puntuación. Es una media ponderada de las puntuaciones de cada capa de calidad consideradas de forma independiente.
    -   **Interpretación:** Representa la contribución de cada faceta de calidad por sí misma. Por ejemplo, la calidad del código (`x_@b`) contribuye a la puntuación final independientemente de la calidad del documento de entrada (`x_@u`).

2.  **Término de Interacción (`Σ a_ℓk · min(x_ℓ(I), x_k(I))`):**
    -   **Qué es:** Esta es la innovación clave del modelo. Captura la idea de que algunas capas de calidad están interconectadas. El operador `min` es crucial aquí.
    -   **Interpretación:** Modela el principio del "eslabón más débil". La contribución de una interacción está limitada por la capa con el rendimiento más bajo. Por ejemplo, consideremos la interacción entre la calidad del documento (`@u`) y la compatibilidad de la cadena de datos (`@chain`). Se puede tener una cadena de datos perfectamente cableada (`x_@chain = 1.0`), pero si la calidad del documento es pobre (`x_@u = 0.4`), la sinergia entre ambas será limitada por el `0.4`. El `min(0.4, 1.0)` resulta en `0.4`. Esto formaliza la intuición de que "un cableado perfecto no puede salvar un análisis basado en datos de mala calidad".

## 5.3. Desglose de las Capas de Calidad (`x_ℓ(I)`)

Cada `x_ℓ(I)` es una función que mide un aspecto específico de la calidad. A continuación, se detallan las capas canónicas, su propósito y cómo se conectan con los artefactos del sistema.

### 5.3.1. Capa Base `@b`: Calidad Intrínseca del Método
-   **Propósito:** Evaluar la calidad del código del método (`M`) de forma aislada, sin considerar el contexto de ejecución.
-   **Fórmula:** `x_@b(I) = w_th · b_theory(M) + w_imp · b_impl(M) + w_dep · b_deploy(M)`
-   **Conexión a la Implementación:**
    -   `b_theory`: Se evalúa mediante una rúbrica sobre la solidez teórica del método.
    -   `b_impl`: Se mide con herramientas de análisis estático de código (ej. `pytest --cov` para `test_coverage`), linters y rúbricas de calidad de software.
    -   `b_deploy`: Se calcula a partir de datos históricos de ejecución (ej. logs de CI/CD, métricas de estabilidad en producción).

### 5.3.2. Capa de Cadena `@chain`: Compatibilidad de Datos
-   **Propósito:** Verificar que los inputs y outputs del método `v` se ajustan a los contratos de datos (`schemas`) definidos en el grafo computacional `Γ`.
-   **Fórmula:** Es un conjunto de reglas que asignan un valor discreto (0, 0.3, 0.6, 0.8, 1.0).
-   **Conexión a la Implementación:** Esta capa se alimenta de la validación contra los `JSON Schemas` ubicados en `data/schemas/`. Un `hard_mismatch` (ej. esperar un `string` y recibir un `integer`) resulta en `x_@chain = 0`, lo que anula efectivamente la ejecución.

### 5.3.3. Capa de Unidad de Análisis `@u`: Calidad del Documento
-   **Propósito:** Medir cómo la calidad del documento de entrada (`U`) afecta el rendimiento del método.
-   **Fórmula:** `x_@u(I) = g_M(U)` donde `g_M` es una función que modela la sensibilidad del método `M` a la calidad del input `U`.
-   **Conexión a la Implementación:** El valor de `U` se calcula analizando el documento de entrada (ej. completitud de secciones, calidad de indicadores). La función `g_M` se define en la configuración del modelo y es específica para cada tipo de método. Por ejemplo, un método de extracción (`g_STRUCT`) puede fallar catastróficamente (`g_M(U) = 0`) si la calidad del documento es inferior a un umbral (ej. `U < 0.3`).

### 5.3.4. Capas de Contexto `@q, @d, @p`: Adecuación al Problema
-   **Propósito:** Evaluar si el método `M` es el adecuado para la Pregunta (`@q`), Dimensión (`@d`) y Área de Política (`@p`) específicas.
-   **Fórmula:** Una función de mapeo `Q_f(M | Q)` que asigna un score basado en si el método es `primary`, `secondary`, `compatible`, etc.
-   **Conexión a la Implementación:** Esta es una de las conexiones más directas. Estos valores se leen del `questionnaire_monolith.json`, específicamente de la sección `method_sets` de cada pregunta. Esto asegura que la calibración está alineada con la especificación central del negocio.

### 5.3.5. Capa de Interplay `@C`: Congruencia de Ensambles
-   **Propósito:** Cuando múltiples métodos colaboran para responder una pregunta (un "interplay" `G`), esta capa evalúa qué tan bien "encajan" entre sí.
-   **Fórmula:** `C_play(G | ctx) = c_scale · c_sem · c_fusion`
-   **Conexión a la Implementación:**
    -   `c_scale`: Verifica si los rangos de salida son compatibles (ej. ambos devuelven un score de 0 a 1).
    -   `c_sem`: Comprueba la superposición de conceptos semánticos (tags en la configuración).
    -   `c_fusion`: Valida que la regla para combinar los resultados (`fusion_rule`) esté declarada en el `questionnaire_monolith.json` (ej. `scoring_modality: "TYPE_A"`).

### 5.3.6. Capa Meta `@m`: Gobernanza y Observabilidad
-   **Propósito:** Evaluar la madurez operativa del método.
-   **Fórmula:** `h_M(m_transp, m_gov, m_cost)`
-   **Conexión a la Implementación:**
    -   `m_transp`: ¿El método produce logs estructurados y trazas de ejecución auditables?
    -   `m_gov`: ¿Está el método versionado (`git tag`), y su ejecución ligada a un hash de configuración específico?
    -   `m_cost`: ¿Cuál es su huella de recursos (CPU, memoria) durante la ejecución?

## 5.4. Ejemplo Numérico Amplificado

Revisitemos el `Worked Example 5.1` de la especificación, añadiendo una capa narrativa para clarificar el impacto de cada término.

**Contexto:** Calculamos `Cal(I)` para un método de tipo `SCORE_Q`.

**Paso 1: Puntuaciones de Capas (Inputs)**
Supongamos que el método es excelente en casi todos los aspectos, pero se aplica a un documento de calidad mediocre.
-   `x_@b` (Calidad Código) = **0.9** (Muy bueno)
-   `x_@chain` (Cableado) = **1.0** (Perfecto)
-   `x_@q`, `x_@d`, `x_@C` = **1.0** (Perfectamente adecuado y compatible)
-   `x_@p` (Área Política) = **0.8** (Buena adecuación)
-   `x_@m` (Gobernanza) = **0.95** (Muy maduro)
-   `x_@u` (Calidad Documento) = **0.6** (Mediocre, el punto débil)

**Paso 2: Parámetros del Modelo (Pesos)**
Estos pesos (simplificados para claridad) definen la importancia de cada capa y de sus interacciones.
-   **Pesos Lineales (`a_ℓ`):** `a_@b=0.17`, `a_@chain=0.13`, `a_@q=0.08`, `a_@d=0.07`, `a_@p=0.06`, `a_@C=0.08`, `a_@u=0.04`, `a_@m=0.04` (Suma = 0.67)
-   **Pesos de Interacción (`a_ℓk`):** `a_(@u,@chain)=0.13`, `a_(@chain,@C)=0.10`, `a_(@q,@d)=0.10` (Suma = 0.33)
-   **Verificación:** Suma total de pesos = 0.67 + 0.33 = 1.0. El modelo está normalizado.

**Paso 3: Cálculo de la Parte Lineal**
Multiplicamos cada score por su peso.
-   `Suma_Lineal = (0.17 * 0.9) + (0.13 * 1.0) + ... + (0.04 * 0.6) + (0.04 * 0.95)`
-   `Suma_Lineal = 0.153 + 0.13 + 0.08 + 0.07 + 0.048 + 0.08 + 0.024 + 0.038 = 0.623`
-   **Interpretación:** Basado solo en sus méritos independientes, el método obtendría un **0.623**.

**Paso 4: Cálculo de la Parte de Interacción (El "Eslabón Débil")**
Aquí es donde la baja calidad del documento (`x_@u = 0.6`) penaliza el resultado.
-   **Término 1 (`@u`, `@chain`):** `0.13 * min(x_@u, x_@chain) = 0.13 * min(0.6, 1.0) = 0.13 * 0.6 = 0.078`
    -   *Análisis:* La interacción se ve **limitada por el 0.6 de la calidad del documento**. El cableado perfecto de 1.0 no puede superar esta limitación.
-   **Término 2 (`@chain`, `@C`):** `0.10 * min(x_@chain, x_@C) = 0.10 * min(1.0, 1.0) = 0.10 * 1.0 = 0.10`
    -   *Análisis:* Interacción perfecta, sin penalización.
-   **Término 3 (`@q`, `@d`):** `0.10 * min(x_@q, x_@d) = 0.10 * min(1.0, 1.0) = 0.10 * 1.0 = 0.10`
    -   *Análisis:* Interacción perfecta, sin penalización.
-   `Suma_Interacción = 0.078 + 0.10 + 0.10 = 0.278`

**Paso 5: Puntuación Final de Calibración**
-   `Cal(I) = Suma_Lineal + Suma_Interacción = 0.623 + 0.278 = 0.901`
-   **Interpretación Final:** La puntuación final es un robusto **0.90**. Sin embargo, es visible cómo la puntuación de la interacción `(@u, @chain)` fue de `0.078` en lugar del máximo posible de `0.13`. Esta diferencia de `~0.05` es la penalización cuantitativa impuesta por el modelo debido a la pobre calidad del documento que actúa como un cuello de botella para un método por lo demás excelente. El modelo ha capturado exitosamente la dependencia no lineal.

---

# SECCIÓN 6: IMPLEMENTACIÓN DE CALIBRACIÓN

## 6.1. Paradigma de Calibración: Un Servicio, no un Script

A diferencia de un proceso de "entrenamiento" o "ajuste de modelos" que se ejecuta como una tarea por lotes, la calibración en F.A.R.F.A.N. se implementa como un **servicio en tiempo de ejecución**. Durante la FASE 2 del pipeline principal, cada vez que un `Executor` invoca un método de análisis, el `Orchestrator` consulta al `CalibrationOrchestrator` para obtener una puntuación de confianza (`Cal(I)`) para esa invocación específica.

Este diseño tiene implicaciones importantes:
-   **No existe un comando `make calibrate` monolítico.** La calibración es una parte integral y dinámica del pipeline.
-   **La reproducibilidad determinista** no depende de un script de ejecución, sino de un **artefacto de configuración versionado**: el archivo que contiene las puntuaciones de la capa base.

## 6.2. El Artefacto Canónico: `intrinsic_calibration.json`

La única fuente de verdad para la calibración del sistema es el archivo `config/intrinsic_calibration.json`.

-   **Propósito:** Este archivo JSON contiene un diccionario donde las claves son los identificadores de los métodos (ej. `"Analyzer.extract_patterns_v2"`) y los valores son objetos que contienen, como mínimo, la puntuación de la capa base (`intrinsic_score`), que corresponde al `x_@b` del modelo matemático.
-   **Estructura de Ejemplo:**
    ```json
    {
      "Analyzer.extract_patterns_v2": {
        "intrinsic_score": 0.92,
        "metadata": {
          "b_theory_score": 0.95,
          "b_impl_score": 0.90,
          "b_deploy_score": 0.91,
          "last_calibrated": "2025-10-01"
        }
      },
      "Validator.check_coherence": {
        "intrinsic_score": 0.88,
        "metadata": { ... }
      },
      "...": "..."
    }
    ```
-   **Gobernanza:** Para garantizar la reproducibilidad, cualquier ejecución canónica del pipeline F.A.R.F.A.N. debe estar asociada a un hash SHA-256 específico de la versión de `intrinsic_calibration.json` utilizada.

## 6.3. Arquitectura del Servicio de Calibración

El servicio se implementa a través de dos clases singleton que aseguran que los datos de calibración se carguen una sola vez y se compartan de manera eficiente en todo el sistema.

### 6.3.1. El Cargador de Datos: `IntrinsicCalibrationLoader`

-   **Propósito:** Su única responsabilidad es localizar, cargar y parsear el archivo `intrinsic_calibration.json`, proporcionando una interfaz simple para que el resto del sistema consulte las puntuaciones base.
-   **Implementación Canónica:**

    ```python
    # Contenido del archivo: src/saaaaaa/core/calibration/intrinsic_loader.py
    import json
    import logging
    from pathlib import Path
    from typing import Any, Dict, Optional

    logger = logging.getLogger(__name__)

    class IntrinsicCalibrationLoader:
        _instance = None
        _data: Dict[str, Any] = {}
        _loaded = False

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(IntrinsicCalibrationLoader, cls).__new__(cls)
            return cls._instance

        def load(self, config_path: str = "config/intrinsic_calibration.json") -> None:
            """Load intrinsic calibration data from JSON."""
            if self._loaded:
                return

            path = Path(config_path)
            if not path.exists():
                repo_root = Path(__file__).parent.parent.parent.parent.parent
                path = repo_root / config_path

            if not path.exists():
                 logger.warning(f"Intrinsic calibration file not found at {path}. Using empty config.")
                 self._data = {}
                 self._loaded = True
                 return

            try:
                with open(path, "r") as f:
                    self._data = json.load(f)
                self._loaded = True
                logger.info(f"Loaded intrinsic calibration from {path}")
            except Exception as e:
                logger.error(f"Failed to load intrinsic calibration: {e}")
                self._data = {}

        def get_intrinsic_score(self, method_id: str) -> float:
            """Get intrinsic score (@b) for a method."""
            if not self._loaded:
                self.load()

            method_data = self._data.get(method_id)
            if method_data:
                return method_data.get("intrinsic_score", 0.5)
            return 0.5

        def get_metadata(self, method_id: str) -> Optional[Dict[str, Any]]:
            """Get full metadata for a method."""
            if not self._loaded:
                self.load()
            return self._data.get(method_id)
    ```

### 6.3.2. El Orquestador de Calibración: `CalibrationOrchestrator`

-   **Propósito:** Es el punto de entrada principal para el servicio. Utiliza el `IntrinsicCalibrationLoader` para obtener el score `@b` y luego ejecuta el resto del proceso de calibración.
-   **NOTA IMPORTANTE SOBRE LA IMPLEMENTACIÓN ACTUAL:** La versión canónica actual del `CalibrationOrchestrator` implementa una **versión simplificada** del modelo matemático completo. Específicamente, en lugar de calcular cada capa de forma independiente y usar el agregador de Choquet, estima las capas `>@b` basándose en la puntuación `@b` y utiliza un promedio simple. Esto se hace por razones de rendimiento y se anota en el código como un punto para una futura implementación completa del modelo de Choquet.
-   **Implementación Canónica:**

    ```python
    # Contenido del archivo: src/saaaaaa/core/calibration/orchestrator.py
    import logging
    from typing import Any, Dict, List
    from dataclasses import dataclass, field

    from .intrinsic_loader import IntrinsicCalibrationLoader
    from .layer_requirements import get_required_layers_for_method

    logger = logging.getLogger(__name__)

    @dataclass
    class CalibrationResult:
        final_score: float
        layer_scores: Dict[str, float]
        metadata: Dict[str, Any]

        def get_failure_reason(self) -> str:
            if self.final_score < 0.5: # Simple threshold for reason
                return "Low confidence score"
            return ""

    class CalibrationOrchestrator:
        _instance = None
        _initialized = False

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(CalibrationOrchestrator, cls).__new__(cls)
            return cls._instance

        def initialize(self) -> None:
            """Initialize the orchestrator and dependencies."""
            if self._initialized:
                return

            self.intrinsic_loader = IntrinsicCalibrationLoader()
            self.intrinsic_loader.load()
            self._initialized = True
            logger.info("CalibrationOrchestrator initialized")

        def calibrate(self, method_id: str, context: Dict[str, Any]) -> CalibrationResult:
            """
            Calibrate a method execution.

            1. Load @b from IntrinsicCalibrationLoader
            2. Determine layers from LAYER_REQUIREMENTS
            3. Evaluate each layer (SIMPLIFIED)
            4. Aggregate (SIMPLIFIED - Average)
            5. Return CalibrationResult
            """
            if not self._initialized:
                self.initialize()

            # 1. Get Intrinsic Score (@b)
            intrinsic_score = self.intrinsic_loader.get_intrinsic_score(method_id)

            # 2. Determine Required Layers
            required_layers = get_required_layers_for_method(method_id)

            # 3. Evaluate Layers (SIMPLIFIED IMPLEMENTATION)
            # Placeholder: In the future, instantiate specific layer evaluators here.
            layer_scores = {}
            for layer in required_layers:
                if layer == "@b":
                    layer_scores[layer] = intrinsic_score
                else:
                    # Placeholder logic: Estimate other layers based on the intrinsic score.
                    layer_scores[layer] = min(1.0, intrinsic_score * 1.1)

            # 4. Aggregate (SIMPLIFIED - Simple average, not Choquet)
            if layer_scores:
                final_score = sum(layer_scores.values()) / len(layer_scores)
            else:
                final_score = intrinsic_score

            return CalibrationResult(
                final_score=final_score,
                layer_scores=layer_scores,
                metadata={"method_id": method_id, "layers_evaluated": required_layers}
            )
    ```

## 6.4. Proceso de Recalibración (Manual Operativo)

Para actualizar o recalibrar el sistema, un operador debe seguir los siguientes pasos:

1.  **Análisis y Rúbrica:** Evaluar los métodos del sistema (nuevos o modificados) de acuerdo a las rúbricas definidas en el `canonic_calibration_methods.md` para la capa base (`b_theory`, `b_impl`, `b_deploy`).
2.  **Actualización del JSON:** Modificar o añadir las entradas correspondientes en el archivo `config/intrinsic_calibration.json`, actualizando el `intrinsic_score` y los metadatos asociados.
3.  **Versionado y Hash:** Versionar el archivo `intrinsic_calibration.json` utilizando `git` y calcular su nuevo hash SHA-256.
4.  **Ejecución de Verificación:** Ejecutar el pipeline de F.A.R.F.A.N. sobre un conjunto de documentos de validación ("golden set") y comparar los resultados con la ejecución anterior para evaluar el impacto de la recalibración.
5.  **Despliegue:** Una vez validado, el nuevo archivo `intrinsic_calibration.json` se convierte en la versión canónica para futuras ejecuciones.

---

# SECCIÓN 7: IMPLEMENTACIÓN DE PARAMETRIZACIÓN

## 7.1. Distinción Fundamental: Calibración vs. Parametrización

En el ecosistema F.A.R.F.A.N., es crucial entender la distinción entre calibración y parametrización, ya que son sistemas ortogonales con propósitos diferentes:

-   **Calibración (Sección 6):** Responde a la pregunta "**¿Cuánta confianza tenemos en el resultado de este método en este contexto?**". Es una evaluación de la *calidad y fiabilidad* de la ejecución de un método.
-   **Parametrización (Esta Sección):** Responde a la pregunta "**¿Cómo debe comportarse este método?**". Es la *configuración* de los parámetros internos que gobiernan la lógica de un método.

Un método bien calibrado (alta confianza) puede comportarse de maneras muy diferentes según sus parámetros. Por ejemplo, un método de extracción de patrones puede tener una alta calibración, pero sus parámetros determinarán qué patrones específicos busca. La arquitectura del sistema impone una separación estricta entre estos dos conceptos.

## 7.2. El Artefacto Canónico: `CANONICAL_METHOD_PARAMETERIZATION_SPEC.json`

De forma análoga a la calibración, la parametrización se basa en un único artefacto canónico que sirve como fuente de verdad. Aunque los tests se refieren a `method_parameters.json` por simplicidad, la especificación completa y autorizada es `MIGRATION_ARTIFACTS_FAKE_TO_REAL/03_METHOD_INVENTORIES/CANONICAL_METHOD_PARAMETERIZATION_SPEC.json`.

-   **Propósito:** Este archivo JSON define cada parámetro para cada método del sistema. No solo especifica valores por defecto, sino también los rangos permitidos, el tipo de dato, y, fundamentalmente, una **justificación epistémica** que documenta el porqué de la elección de ese parámetro desde una perspectiva metodológica y de software.
-   **Estructura de Ejemplo:**
    ```json
    {
      "method_id": "Analyzer.detect_bottlenecks_v1",
      "parameters": [
        {
          "name": "density_threshold",
          "type": "float",
          "range": [0.0, 1.0],
          "default": 0.7,
          "source": "code (hardcoded)",
          "epistemic_justification": "DECISION THRESHOLD with substantive policy implications. This is NOT a tuning parameter—it's a diagnostic cutpoint... Default 0.7 means 70% of expected density is required...",
          "notes": "CRITICAL: This is a consequential diagnostic threshold, not a technical tuning parameter"
        }
      ]
    }
    ```
-   **Gobernanza:** Al igual que con la calibración, la reproducibilidad determinista exige que cada ejecución del pipeline esté vinculada a un hash SHA-256 específico de la especificación de parametrización utilizada.

## 7.3. Arquitectura del Servicio de Parametrización

El sistema de parametrización se implementa como un servicio de carga de configuración, utilizando un singleton para garantizar un acceso eficiente y consistente a los parámetros en todo el sistema.

### 7.3.1. El Cargador de Parámetros: `ParameterLoader`

-   **Propósito:** La única responsabilidad de esta clase es localizar, cargar y parsear el archivo de parámetros (`method_parameters.json` o la especificación canónica), proporcionando una interfaz simple para que los métodos consulten su configuración en tiempo de ejecución.
-   **Implementación Canónica:**

    ```python
    # Contenido del archivo: src/saaaaaa/core/calibration/parameter_loader.py
    import json
    import logging
    from pathlib import Path
    from typing import Any, Dict

    logger = logging.getLogger(__name__)

    class ParameterLoader:
        _instance = None
        _data: Dict[str, Any] = {}
        _loaded = False

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(ParameterLoader, cls).__new__(cls)
            return cls._instance

        def load(self, config_path: str = "config/method_parameters.json") -> None:
            """Load method parameters from JSON."""
            if self._loaded:
                return

            path = Path(config_path)
            if not path.exists():
                repo_root = Path(__file__).parent.parent.parent.parent.parent
                path = repo_root / config_path

            if not path.exists():
                 logger.warning(f"Method parameters file not found at {path}. Using empty config.")
                 self._data = {}
                 self._loaded = True
                 return

            try:
                with open(path, "r") as f:
                    self._data = json.load(f)
                self._loaded = True
                logger.info(f"Loaded method parameters from {path}")
            except Exception as e:
                logger.error(f"Failed to load method parameters: {e}")
                self._data = {}

        def get(self, method_id: str) -> Dict[str, Any]:
            """Get parameters for a method."""
            if not self._loaded:
                self.load()
            return self._data.get(method_id, {})
    ```

## 7.4. Proceso de Uso y Actualización

### 7.4.1. Uso en Tiempo de Ejecución

Durante la FASE 2 del pipeline, cuando un `Executor` necesita ejecutar un método, su `MethodExecutor` interno es responsable de:
1.  Invocar al `ParameterLoader` para obtener el diccionario de parámetros para el `method_id` que se va a ejecutar.
2.  Pasar estos parámetros como argumentos (`**kwargs`) a la llamada del método.
3.  Esto asegura que los métodos no contengan valores "mágicos" o hardcodeados, sino que se configuren externamente a través de la especificación canónica.

### 7.4.2. Manual de Actualización de Parámetros

Para modificar el comportamiento de un método a través de sus parámetros, el proceso es el siguiente:
1.  **Análisis Metodológico:** Determinar el nuevo valor del parámetro y redactar una `epistemic_justification` clara que explique el impacto del cambio.
2.  **Actualización de la Especificación:** Modificar la entrada correspondiente en el archivo `CANONICAL_METHOD_PARAMETERIZATION_SPEC.json`.
3.  **Versionado y Hash:** Versionar el archivo (`git commit`) y calcular su nuevo hash SHA-256 para mantener la trazabilidad.
4.  **Ejecución de Verificación:** Al igual que con la calibración, ejecutar el pipeline sobre un "golden set" de documentos para validar que el cambio de parámetro tiene el efecto deseado y no introduce regresiones inesperadas.
5.  **Despliegue:** Una vez validado, el nuevo archivo de especificación se convierte en el canónico.

---

# SECCIÓN 8: SISTEMA DE ARTEFACTOS Y SCHEMAS

## 8.1. Principio de "Contratos Estrictos"

La robustez del sistema F.A.R.F.A.N. se fundamenta en un principio de **"Contratos Estrictos"**: cada componente que produce o consume datos debe adherirse a un `schema` formalmente definido. Este enfoque, validado en tiempo de ejecución, previene errores de integración, garantiza la coherencia de los datos a través del pipeline y hace explícita la estructura de cada artefacto.

Todos los `schemas` canónicos se encuentran en el directorio `config/schemas/` y están escritos en el estándar JSON Schema.

## 8.2. El Artefacto Central: `questionnaire_monolith.json`

Este es el artefacto más importante del sistema. No es simplemente un archivo de datos, sino la **especificación ejecutable** de la lógica de negocio completa del análisis de políticas públicas.

-   **Ubicación:** `data/questionnaire_monolith.json`
-   **Schema de Validación:** `config/schemas/questionnaire_monolith.schema.json`
-   **Propósito:** Define de forma jerárquica toda la estructura del análisis, incluyendo:
    -   Los clústeres, áreas de política y dimensiones.
    -   El catálogo completo de micro-preguntas.
    -   Para cada pregunta, especifica el `Executor` responsable (`base_slot`), los métodos de análisis a invocar (`method_sets`), y la modalidad de puntuación (`scoring_modality`).
-   **Estructura Principal (Campos Clave):**
    -   `version`: Versión semántica del monolito.
    -   `schema_version`: Versión del `schema` al que se adhiere.
    -   `blocks`: El objeto principal que contiene la lógica.
        -   `niveles_abstraccion`: Define la jerarquía de `clusters`, `policy_areas` y `dimensions`.
        -   `micro_questions`: Una lista de ~300 objetos, cada uno representando una pregunta.
            -   `question_id`: Identificador único (ej. "D1-Q1-1").
            -   `base_slot`: El `Executor` que la procesará (ej. "D1-Q1").
            -   `policy_area_id`, `dimension_id`, `cluster_id`: La posición de la pregunta en la jerarquía.
            -   `scoring_modality`: El tipo de lógica de puntuación a aplicar (ej. "TYPE_A").
            -   `method_sets`: Objeto que define los métodos primarios y secundarios para el análisis.
        -   `meso_questions`, `macro_question`: (Estructuras análogas para futuras expansiones).

## 8.3. Artefactos de Configuración de Métodos

Como se detalló en las Secciones 6 y 7, la calibración y parametrización de los métodos se gestionan a través de artefactos JSON dedicados.

### 8.3.1. Calibración Intrínseca
-   **Artefacto:** `config/intrinsic_calibration.json`
-   **Propósito:** Almacenar la puntuación de la capa base (`@b`) para cada método.
-   **Estructura Clave:** Un diccionario donde cada clave es un `method_id` y el valor es un objeto con la clave `intrinsic_score`.

### 8.3.2. Parametrización de Métodos
-   **Artefacto:** `MIGRATION_ARTIFACTS_FAKE_TO_REAL/03_METHOD_INVENTORIES/CANONICAL_METHOD_PARAMETERIZATION_SPEC.json`
-   **Propósito:** Definir todos los parámetros, sus rangos, valores por defecto y justificación epistémica.
-   **Estructura Clave:** Una lista de objetos, donde cada objeto representa un `method_id` y contiene una lista de `parameters`. Cada parámetro es un objeto detallado con `name`, `type`, `range`, `default`, y `epistemic_justification`.

## 8.4. Schemas de Contratos Clave

Además del `schema` del monolito, existen otros `schemas` que definen contratos importantes dentro del pipeline.

### 8.4.1. Contrato del Executor: `executor_contract.v3.schema.json`
-   **Ubicación:** `config/schemas/executor_contract.v3.schema.json`
-   **Propósito:** Define la estructura de la **"Evidencia"** (`Evidence`), que es el objeto que cada `Executor` debe devolver tras analizar una pregunta. Este contrato es fundamental para la interoperabilidad entre la FASE 2 (Ejecución) y la FASE 3 (Scoring).
-   **Estructura Clave del Objeto `Evidence`:**
    -   `modality`: Una cadena que describe la modalidad de la evidencia (ej. "text_extraction", "pattern_match").
    -   `elements`: Una lista de los elementos extraídos (ej. frases, números).
    -   `raw_results`: Un diccionario que contiene datos adicionales del análisis, como `confidence_scores` o `semantic_similarity`.

### 8.4.2. Contrato de Recomendaciones: `recommendation_rules_enhanced.schema.json`
-   **Ubicación:** `config/schemas/recommendation_rules_enhanced.schema.json`
-   **Propósito:** Valida la estructura del archivo de reglas que utiliza el `RecommendationEngine` en la FASE 8.
-   **Estructura Clave:**
    -   Define una lista de `rules`, donde cada regla tiene:
        -   `level`: El nivel donde aplica la regla (MICRO, MESO, MACRO).
        -   `conditions`: Un conjunto de condiciones lógicas que se evalúan contra los resultados del pipeline (ej. `macro_band == 'DEFICIENTE'`).
        -   `recommendation`: El texto de la recomendación a generar si las condiciones se cumplen, a menudo con plantillas para insertar valores (`{priority_micro_gaps}`).

### 8.4.3. Manifiesto de Verificación: `verification_manifest.schema.json`
-   **Ubicación:** `config/schemas/verification_manifest.schema.json`
-   **Propósito:** Define la estructura del artefacto final de una ejecución, que sirve como un registro auditable y autocontenido de todo el proceso. Contiene hashes de todos los artefactos de entrada, métricas de rendimiento de cada fase y un resumen de los resultados.
-   **Estructura Clave:**
    -   `run_id`: Identificador único de la ejecución.
    -   `timestamp`: Fecha y hora de la ejecución.
    -   `input_hashes`: Hashes SHA-256 del documento de entrada, `questionnaire_monolith`, `intrinsic_calibration`, etc.
    -   `phase_metrics`: Un objeto que detalla el rendimiento (duración, errores, etc.) de cada una de las 11 fases.
    -   `final_scores`: El `MacroScore` y los `ClusterScores` finales.

## 8.5. Flujo de Artefactos en el Pipeline

El siguiente diagrama textual ilustra cómo estos artefactos se consumen y producen a lo largo del pipeline de 11 fases:

```
[FASE 0] --(Consume)--> questionnaire_monolith.json
           --(Produce)--> config_object

[FASE 1] --(Consume)--> documento_entrada.pdf, config_object
           --(Produce)--> PreprocessedDocument (con 60 SPCs)

[FASE 2] --(Consume)--> PreprocessedDocument, config_object
           --(Consume)--> intrinsic_calibration.json (vía servicio)
           --(Consume)--> method_parameters.json (vía servicio)
           --(Produce)--> List[MicroQuestionRun] (con "Evidence" validada por executor_contract.schema.json)

[FASE 3] --(Consume)--> List[MicroQuestionRun]
           --(Produce)--> List[ScoredMicroQuestion]

[FASE 4-7] --(Agregación)--> ...

[FASE 8] --(Consume)--> recommendation_rules_enhanced.json
           --(Produce)--> recommendations_object

...

[FASE 10] --(Produce)--> export_payload (validado por verification_manifest.schema.json)
```

---

# SECCIÓN 9: ESPECIFICACIONES DE GRÁFICOS

## 9.1. Principios de Visualización

Todos los gráficos generados por el sistema F.A.R.F.A.N. deben adherirse a la **estética "AtroZ Dashboard"**. Los principios son:
-   **Fondo:** Oscuro (`#000000` o similar).
-   **Paleta de Colores:** Colores neón y brillantes (cian, magenta, verde, amarillo) para los elementos de datos, y blanco o gris claro para el texto.
-   **Tipografía:** Fuentes monoespaciadas (preferiblemente 'JetBrains Mono' o, en su defecto, 'monospace').
-   **Diseño:** Limpio, minimalista y sin desorden. Evitar rejillas, bordes innecesarios y elementos decorativos que no aporten información.

A continuación se proporcionan los scripts de Python (`matplotlib`) que constituyen la especificación canónica para generar los gráficos requeridos en este compendio. Las imágenes `.png` generadas se encuentran en el directorio `CANONIC_COMPENDIUM/images/`.

## 9.2. Gráfico 1: Arquitectura de Capas

-   **Referencia:** Sección 3.2
-   **Archivo de Salida:** `CANONIC_COMPENDIUM/images/architecture_layers.png`
-   **Descripción:** Un diagrama de cajas apiladas que representa las 6 capas de la arquitectura del sistema, desde la Capa 0 (Orquestación) hasta la Capa 5 (Datos), con flechas que indican el flujo de dependencias estrictamente hacia abajo.
-   **Código de Generación Canónico:**

    ```python
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Estética AtroZ
    plt.style.use('dark_background')
    plt.rcParams['font.family'] = 'monospace'
    plt.rcParams['text.color'] = '#E0E0E0'
    plt.rcParams['axes.labelcolor'] = '#E0E0E0'
    plt.rcParams['xtick.color'] = '#CCCCCC'
    plt.rcParams['ytick.color'] = '#CCCCCC'

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    # Título del Gráfico
    ax.text(0.5, 0.95, 'Arquitectura de Capas de F.A.R.F.A.N.',
            ha='center', va='center', fontsize=20, weight='bold', color='#FFFFFF')

    # Definición de Capas
    layers = [
        {"name": "Capa 0: Orquestación y Punto de Entrada", "color": "#FF00FF"}, # Magenta
        {"name": "Capa 1: Lógica de Negocio y Análisis", "color": "#00FFFF"},   # Cian
        {"name": "Capa 2: Procesamiento y Agregación", "color": "#00FF00"},   # Verde
        {"name": "Capa 3: Abstracción de Datos", "color": "#FFFF00"},         # Amarillo
        {"name": "Capa 4: Utilidades y Soporte", "color": "#FFA500"},         # Naranja
        {"name": "Capa 5: Datos y Configuración", "color": "#FF4500"}          # Rojo-Naranja
    ]
    num_layers = len(layers)
    box_width = 0.8
    box_height = 0.1
    gap = 0.05
    y_start = 0.8

    # Dibujar cajas y texto
    for i, layer in enumerate(layers):
        y_pos = y_start - i * (box_height + gap)
        rect = patches.Rectangle(
            (0.5 - box_width / 2, y_pos - box_height / 2),
            box_width, box_height,
            linewidth=2, edgecolor=layer['color'], facecolor='#1A1A1A'
        )
        ax.add_patch(rect)
        ax.text(0.5, y_pos, layer['name'], ha='center', va='center', fontsize=12, color=layer['color'])

    # Dibujar flechas de dependencia (siempre hacia abajo)
    for i in range(num_layers - 1):
        y_top = y_start - i * (box_height + gap) - box_height / 2
        y_bottom = y_start - (i + 1) * (box_height + gap) + box_height / 2
        ax.arrow(0.5, y_top, 0, y_bottom - y_top,
                 head_width=0.02, head_length=0.015, fc='white', ec='white', length_includes_head=True)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # La línea de guardado se omite en el compendio, pero se usaría así:
    # plt.savefig('CANONIC_COMPENDIUM/images/architecture_layers.png', bbox_inches='tight', pad_inches=0.1)
    ```

## 9.3. Gráfico 2: Pipeline de Fases

-   **Referencia:** Sección 4.2
-   **Archivo de Salida:** `CANONIC_COMPENDIUM/images/pipeline_flow.png`
-   **Descripción:** Un diagrama de flujo que muestra las 11 fases del pipeline, desde la F0 (Validación de Configuración) hasta la F10 (Exportación), organizadas en una cuadrícula para mayor claridad y conectadas por flechas que indican la secuencia de ejecución.
-   **Código de Generación Canónico:**

    ```python
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Estética AtroZ
    plt.style.use('dark_background')
    plt.rcParams['font.family'] = 'monospace'
    plt.rcParams['text.color'] = '#E0E0E0'

    fig, ax = plt.subplots(figsize=(14, 12))
    ax.axis('off')

    # Título
    ax.text(0.5, 0.98, 'Pipeline de 11 Fases de F.A.R.F.A.N.',
            ha='center', va='center', fontsize=22, weight='bold', color='#FFFFFF')

    # Definición de Fases
    phases = [
        "F0: Val. Config", "F1: Ingestión", "F2: Micro-Preguntas",
        "F3: Scoring Micro", "F4: Agreg. Dimensiones", "F5: Agreg. Áreas",
        "F6: Agreg. Clústeres", "F7: Eval. Macro", "F8: Recomendaciones",
        "F9: Ensamblado Reporte", "F10: Exportación"
    ]
    num_phases = len(phases)
    box_width = 0.15
    box_height = 0.08
    x_start, y_start = 0.1, 0.9
    x_gap, y_gap = 0.2, 0.15
    cols = 3

    # Dibujar cajas y flechas
    for i, phase in enumerate(phases):
        row = i // cols
        col = i % cols

        x_pos = x_start + col * x_gap
        y_pos = y_start - row * y_gap

        # Caja
        rect = patches.FancyBboxPatch(
            (x_pos - box_width / 2, y_pos - box_height / 2),
            box_width, box_height,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            linewidth=2, edgecolor='#00FFFF', facecolor='#1A1A1A' # Cian
        )
        ax.add_patch(rect)
        ax.text(x_pos, y_pos, phase.replace(": ", ":\\n"), ha='center', va='center', fontsize=9, color='#FFFFFF', wrap=True)

        # Flecha a la siguiente fase
        if i < num_phases - 1:
            next_row = (i + 1) // cols
            next_col = (i + 1) % cols

            next_x = x_start + next_col * x_gap
            next_y = y_start - next_row * y_gap

            if next_col > col: # Flecha a la derecha
                start_x, start_y = x_pos + box_width / 2, y_pos
                end_x, end_y = next_x - box_width / 2, next_y
                ax.arrow(start_x, start_y, end_x - start_x, 0,
                         head_width=0.01, head_length=0.015, fc='white', ec='white', length_includes_head=True)
            elif next_row > row: # Flecha hacia abajo
                start_x, start_y = x_pos, y_pos - box_height / 2
                # Conexión indirecta para bajar
                mid_y = y_pos - y_gap / 2
                plt.plot([x_pos, x_pos], [start_y, mid_y], color='white', lw=1) # Linea hacia abajo
                plt.plot([x_pos, next_x], [mid_y, mid_y], color='white', lw=1)   # Linea horizontal
                ax.arrow(next_x, mid_y, 0, next_y + box_height / 2 - mid_y,
                         head_width=0.01, head_length=0.015, fc='white', ec='white', length_includes_head=True)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # La línea de guardado se omite en el compendio, pero se usaría así:
    # plt.savefig('CANONIC_COMPENDIUM/images/pipeline_flow.png', bbox_inches='tight', pad_inches=0.1)
    ```

---

# SECCIÓN 10: MANUAL DE REPRODUCCIÓN DETERMINISTA (RUNBOOK)

## 10.1. Objetivo y Pre-requisitos

Este manual proporciona la secuencia exacta de comandos y verificaciones necesarias para ejecutar el pipeline F.A.R.F.A.N. de forma **determinista**. El objetivo es que, partiendo de un estado limpio del repositorio y utilizando los artefactos canónicos versionados, cualquier agente pueda producir resultados idénticos bit a bit a una ejecución de referencia.

**Pre-requisitos:**
1.  Un entorno Linux con `git`, `python` (>=3.12), `make` y `pip` instalados.
2.  Acceso de solo lectura al repositorio `saaaaaa`.
3.  Una copia local del documento de política pública a analizar (ej. `documento_entrada.pdf`).

## 10.2. FASE I: Configuración del Entorno

Esta fase prepara el entorno de ejecución, instala dependencias y descarga los modelos necesarios.

### Paso 1.1: Clonar el Repositorio y Verificar Versión
Asegúrese de estar en la versión (commit hash) exacta del código que corresponde a los artefactos canónicos.
```bash
# git clone <repository_url>
# cd saaaaaa
# git checkout <commit_hash_canónico>
```

### Paso 1.2: Instalación de Dependencias Canónicas
El comando `make setup` instala todas las dependencias de Python requeridas, tal como están fijadas (`pinned`) en los archivos `requirements.txt`. Esto es crucial para la reproducibilidad.
```bash
make setup
```

### Paso 1.3: Descarga de Activos Externos
El sistema depende de modelos de lenguaje pre-entrenados. El comando `make equip` descarga y los instala.
```bash
make equip
# Este comando ejecuta internamente:
# python -m spacy download es_core_news_lg
# python -m nltk.downloader punkt
```
**Verificación:** Al finalizar esta fase, el entorno virtual debe contener todas las librerías y los modelos de Spacy y NLTK deben estar disponibles.

## 10.3. FASE II: Verificación Pre-Vuelo (Pre-flight Check)

Antes de ejecutar el pipeline, se debe verificar la integridad del entorno y la configuración.

### Paso 2.1: Ejecutar las Verificaciones del Sistema
El comando `make verify` ejecuta un conjunto de pruebas y linters para asegurar que el código está en un estado coherente y correcto.
```bash
make verify
```
**Verificación:** El comando `make verify` debe finalizar sin errores. Cualquier fallo indica un problema en la configuración del entorno o una inconsistencia en el código que debe resolverse antes de continuar.

### Paso 2.2: Verificar Hashes de Artefactos Canónicos
Este es el paso más crítico para la reproducibilidad. Verifique que los hashes SHA-256 de los artefactos de entrada coinciden con los de la ejecución de referencia.

```bash
# Ejemplo de verificación
sha256sum data/questionnaire_monolith.json
sha256sum config/intrinsic_calibration.json
sha256sum MIGRATION_ARTIFACTS_FAKE_TO_REAL/03_METHOD_INVENTORIES/CANONICAL_METHOD_PARAMETERIZATION_SPEC.json

# Salida esperada (ejemplo):
# a1b2c3d4...  data/questionnaire_monolith.json
# e5f6g7h8...  config/intrinsic_calibration.json
# i9j0k1l2...  .../CANONICAL_METHOD_PARAMETERIZATION_SPEC.json
```
**Verificación:** Los hashes deben coincidir exactamente con los hashes de referencia documentados para la versión canónica que se desea replicar.

## 10.4. FASE III: Ejecución del Pipeline Canónico

Esta fase ejecuta el pipeline de 11 fases sobre el documento de entrada.

### Paso 3.1: Preparar el Documento de Entrada
Coloque el documento a analizar en una ubicación conocida, por ejemplo, en el directorio raíz del repositorio.
```bash
# cp /ruta/al/documento_entrada.pdf .
```

### Paso 3.2: Ejecutar el Pipeline
El `Orchestrator` se invoca a través de un script de ejecución. Asumiendo un script canónico `scripts/run_canonical_pipeline.py`, la ejecución sería:

```python
# Contenido de ejemplo para run_canonical_pipeline.py
import asyncio
from saaaaaa.core.wiring.bootstrap import bootstrap_system
from saaaaaa.processing.spc_ingestion import CPPIngestionPipeline

async def main():
    # 1. Bootstrap del sistema para obtener el orquestador
    components = bootstrap_system()
    orchestrator = components.orchestrator

    # 2. Ingestión del documento (Fase 1 externa para obtener PreprocessedDocument)
    # NOTA: En la implementación real, el orquestador mismo llama a la ingestión
    # en su FASE 1. Aquí se muestra cómo se haría si se invoca externamente.
    pdf_path = "documento_entrada.pdf"

    # 3. Ejecución del pipeline completo (de la FASE 0 a la 10)
    print("Iniciando ejecución del pipeline canónico...")
    phase_results = await orchestrator.process_development_plan_async(pdf_path=pdf_path)

    # 4. Procesar y guardar el resultado final
    final_payload = phase_results[-1].data
    # ... (guardar en un archivo de salida)
    print("Ejecución completada.")

if __name__ == "__main__":
    asyncio.run(main())
```

**Comando de ejecución:**
```bash
python scripts/run_canonical_pipeline.py
```

## 10.5. FASE IV: Verificación de Resultados

Tras la ejecución, el paso final es verificar que el artefacto de salida es idéntico al de referencia.

### Paso 4.1: Calcular Hash del Artefacto de Salida
El pipeline producirá un archivo de salida (ej. `output_report.json`). Calcule su hash SHA-256.
```bash
sha256sum output_report.json
```
**Verificación Final:** El hash del archivo de salida debe ser **idéntico bit a bit** al hash del artefacto de salida de la ejecución de referencia. Una coincidencia exacta confirma que la reproducción ha sido exitosa y determinista.

---

# SECCIÓN 11: ANEXOS

## Anexo A: Glosario de Términos Canónicos

-   **Artefacto Canónico (Canonical Artifact):** Un archivo (generalmente JSON) que sirve como la única fuente de verdad (`single source of truth`) para una pieza de configuración o especificación del sistema. Ejemplos: `questionnaire_monolith.json`, `intrinsic_calibration.json`. Su integridad se verifica mediante hashes SHA-256.

-   **Calibración (Calibration):** El proceso de asignar una puntuación de confianza (`Cal(I)`) a la ejecución de un método en un contexto específico. Mide la *fiabilidad* del resultado, no su valor. Ver Sección 6.

-   **Compendio Técnico (Technical Compendium):** Este mismo documento. La especificación canónica y el manual de implementación del sistema F.A.R.F.A.N.

-   **Executor:** Una clase de Python cuya responsabilidad es orquestar la secuencia de métodos de análisis necesarios para responder a una micro-pregunta específica. No contiene la lógica de análisis en sí, sino la secuencia de llamadas a los métodos. Ejemplo: `D1Q1_Executor`.

-   **F.A.R.F.A.N.:** Acrónimo de "Framework for Advanced Research and Forecasting in Algorithmic Networks". El nombre en clave del sistema completo.

-   **Función de Calibración (`Cal(I)`):** El modelo matemático (basado en Agregación de Choquet) que fusiona las puntuaciones de múltiples capas de calidad para producir un único score de confianza para una instancia de método. Ver Sección 5.

-   **Capa de Calidad (Layer):** Una de las dimensiones utilizadas para evaluar una instancia de método. Cada capa (`@b`, `@chain`, `@u`, etc.) mide un aspecto específico de la calidad, como la robustez del código o la adecuación al contexto.

-   **Modelo Mecanicista (Mechanistic Model):** Un tipo de modelo que representa explícitamente los mecanismos causales y las interacciones de un sistema, en lugar de depender únicamente de correlaciones estadísticas. Es la filosofía de diseño fundamental de F.A.R.F.A.N.

-   **Monolito del Cuestionario (Questionnaire Monolith):** El archivo `questionnaire_monolith.json`. Es el artefacto central que define la lógica de negocio del sistema, incluyendo todas las preguntas, su jerarquía, y qué `Executors` y métodos las procesan. Ver Sección 8.2.

-   **Parametrización (Parameterization):** El proceso de configurar el comportamiento interno de un método a través de parámetros definidos externamente. Controla *cómo* funciona un método. Ver Sección 7.

-   **Reproducibilidad Determinista (Deterministic Reproducibility):** Un objetivo de diseño clave que garantiza que, dado el mismo conjunto de entradas (código, artefactos canónicos, documento), el sistema producirá resultados idénticos bit a bit en cada ejecución.

-   **Smart Policy Chunk (SPC):** La unidad de análisis fundamental del sistema, generada en la FASE 1. Es un segmento semántico de un documento de política pública, anotado con metadatos como `policy_area_id` y `dimension_id`. El pipeline opera sobre una estructura de 60 SPCs canónicos.

## Anexo B: Tabla de Mapeo Conceptual

| Concepto Abstracto | Implementación Concreta en F.A.R.F.A.N. | Referencia en Compendio |
| :----------------- | :-------------------------------------- | :---------------------- |
| Lógica de Negocio | `questionnaire_monolith.json` | Sección 8.2 |
| Ejecución del Pipeline | Clase `Orchestrator` en `core.py` | Sección 4.4 |
| Confianza en el Método | Sistema de **Calibración** (`Cal(I)`) | Sección 5 y 6 |
| Configuración del Método | Sistema de **Parametrización** | Sección 7 |
| Calidad del Código | Capa de Calidad Base (`@b`) | Sección 5.3.1, 6.2 |
| Calidad del Documento | Capa de Unidad de Análisis (`@u`) | Sección 5.3.3 |
| Contratos de Datos | `JSON Schemas` en `config/schemas/` | Sección 8 |
| Reproducibilidad | Verificación de Hashes SHA-256 | Sección 10.2 |
| Motor de Análisis | Clases `Method` (ej. `Analyzer`) | Sección 3.3.2 |
| Orquestador de Análisis | Clases `Executor` (ej. `D1Q1_Executor`) | Sección 3.3.2 |
