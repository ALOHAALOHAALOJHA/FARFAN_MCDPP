3
I. ANÁLISIS DEL ESTADO ACTUAL DEL CANONIC CENTRAL

1.1 Extracción del Núcleo Canónico desde sabana_final_decisiones.csv

Analizando los datos, identifico los componentes que constituyen el Canonic Central basándome en:

irrigability_bucket: irrigable_now o not_irrigable_yet (excluyo definitely_not)
added_value: YES (excluyo MARGINAL)
stage: Fases operativas (no External)
II. INVENTARIO EXHAUSTIVO DEL CANONIC CENTRAL

2.1 REGISTROS CANÓNICOS (37 items)

YAML
# _registry/ - Núcleo de definiciones canónicas

TIER_1_CRITICAL:  # Sin estos, el sistema no puede operar
  - path: "_registry/EMPIRICAL_CORPUS_INDEX.json"
    stage: phase_1
    irrigability:  not_irrigable_yet
    gap:  NECESITA_VEHICULO
    consumers: [phase1_11_00_signal_enrichment. py, phase1_13_00_cpp_ingestion.py]
    bytes:  10773
    
  - path: "_registry/patterns/MASTER_INDEX.json"
    stage: Cross-Phase
    irrigability: irrigable_now
    gap:  NECESITA_CONSUMIDOR
    vehiculos: [signal_context_scoper, signal_evidence_extractor, signal_intelligence_layer, signal_loader, signal_quality_metrics, signal_registry, signals]
    bytes: 2150659  # ARCHIVO MÁS GRANDE - Índice maestro de patrones

TIER_2_CAPABILITIES: # Definiciones de capacidades del sistema
  - path: "_registry/capabilities/capability_definitions.json"
    stage: Cross-Phase
    irrigability: irrigable_now
    gap: [NECESITA_VEHICULO, NECESITA_CONSUMIDOR]
    bytes: 5424
    
  - path: "_registry/capabilities/consumer_capability_declarations.json"
    stage: Cross-Phase
    irrigability: irrigable_now
    gap: [NECESITA_VEHICULO, NECESITA_CONSUMIDOR]
    bytes: 7284
    
  - path: "_registry/capabilities/signal_capability_map.json"
    stage: Cross-Phase
    irrigability: irrigable_now
    gap: [NECESITA_VEHICULO, NECESITA_CONSUMIDOR]
    bytes: 4719

TIER_3_ENTITIES: # Corpus empírico y entidades canónicas (12 items)
  - path: "_registry/entities/corpus_empirico_calibracion_extractores.json"
    stage: phase_3
    irrigability: irrigable_now
    gap: [NECESITA_VEHICULO, VOCAB_SEÑALES_NO_ALINEADO, VOCAB_CAPACIDADES_NO_ALINEADO]
    consumers: [phase3_10_00_phase3_signal_enriched_scoring.py]
    bytes: 25394
    
  - path: "_registry/entities/corpus_empirico_integrado. json"
    stage: phase_3
    irrigability: irrigable_now
    gap: [NECESITA_VEHICULO, VOCAB_SEÑALES_NO_ALINEADO, VOCAB_CAPACIDADES_NO_ALINEADO]
    consumers: [phase3_10_00_phase3_signal_enriched_scoring.py]
    bytes: 47605
    
  - path: "_registry/entities/corpus_empirico_normatividad.json"
    stage: phase_3
    bytes: 8702
    
  - path: "_registry/entities/index. json"
    bytes: 3620
    
  - path: "_registry/entities/institutions.json"
    bytes: 34126
    
  - path: "_registry/entities/institutions_expanded.json"
    bytes: 21645
    
  - path: "_registry/entities/international. json"
    bytes: 1178
    
  - path: "_registry/entities/normative. json"
    bytes: 5298
    
  - path: "_registry/entities/normative_compliance.json"
    bytes: 8765
    
  - path: "_registry/entities/policy_areas_canonical.json"
    bytes: 3172
    
  - path: "_registry/entities/populations.json"
    bytes: 2252
    
  - path: "_registry/entities/territorial.json"
    bytes: 17200

TIER_4_MEMBERSHIP_CRITERIA: # Criterios de membresía (13 items)
  - path: "_registry/membership_criteria/MC01_structural_markers.json"
    stage: phase_1
    irrigability: not_irrigable_yet
    gap: NECESITA_VEHICULO
    consumers: [phase1_11_00_signal_enrichment.py, phase1_13_00_cpp_ingestion.py]
    bytes: 5206
    
  - path: "_registry/membership_criteria/MC02_quantitative_triplets.json"
    bytes: 8327
    
  - path: "_registry/membership_criteria/MC03_normative_references.json"
    bytes: 7443
    
  - path: "_registry/membership_criteria/MC04_programmatic_hierarchy.json"
    bytes: 5453
    
  - path: "_registry/membership_criteria/MC05_financial_chains.json"
    bytes: 9438
    
  - path: "_registry/membership_criteria/MC06_population_disaggregation.json"
    bytes: 7393
    
  - path: "_registry/membership_criteria/MC07_temporal_markers.json"
    bytes: 4325
    
  - path: "_registry/membership_criteria/MC08_causal_verbs.json"
    bytes: 7841
    
  - path: "_registry/membership_criteria/MC09_institutional_network.json"
    bytes: 6044
    
  - path: "_registry/membership_criteria/MC10_semantic_relationships.json"
    bytes: 3740
    
  # Bindings
  - path: "_registry/membership_criteria/_bindings/mc_to_dimensions.json"
    bytes: 2924
    
  - path: "_registry/membership_criteria/_bindings/mc_to_questions.json"
    bytes: 4386
    
  - path: "_registry/membership_criteria/_bindings/mc_to_scoring.json"
    bytes: 4307
    
  # Calibration
  - path: "_registry/membership_criteria/_calibration/extractor_calibration.json"
    bytes: 33335

TIER_5_QUESTIONS: # Preguntas canónicas (3 items)
  - path: "_registry/questions/integration_map.json"
    stage: Cross-Phase
    irrigability: irrigable_now
    gap:  NECESITA_CONSUMIDOR
    vehiculos: [signal_context_scoper, signal_irrigator, signal_registry]
    bytes: 47605
    
  - path:  "_registry/questions/macro_question. json"
    stage: phase_8
    irrigability: not_irrigable_yet
    gap: NINGUNO  # ¡LISTO PARA IRRIGAR!
    vehiculos: [signal_context_scoper, signal_registry]
    consumers: [phase8_30_00_signal_enriched_recommendations.py]
    bytes: 920
    
  - path: "_registry/questions/meso_questions.json"
    stage: phase_7
    irrigability: irrigable_now
    gap:  NECESITA_CONSUMIDOR
    vehiculos: [signal_context_scoper, signal_registry]
    bytes: 2582
2.2 PATRONES CANÓNICOS (22 items irrigables)

YAML
PATTERNS_BY_CATEGORY:  # Todos irrigable_now con gap:  VOCAB_SEÑALES_NO_ALINEADO
  vehiculos_comunes: [signal_context_scoper, signal_evidence_extractor, signal_intelligence_layer, signal_loader, signal_quality_metrics, signal_registry, signals]
  consumers_comunes: [phase2_10_00_factory. py, phase2_30_03_resource_aware_executor.py, phase2_40_03_irrigation_synchronizer.py, phase2_60_00_base_executor_with_contract.py, phase2_80_00_evidence_nexus.py, phase2_95_00_contract_hydrator.py, phase2_95_02_precision_tracking.py]
  
  items: 
    - CAUSAL_CONNECTOR. json:  1309 bytes
    - CAUSAL_OUTCOME.json: 3916 bytes
    - DESCRIPCION. json: 3672 bytes
    - FUENTE_OFICIAL.json: 23677 bytes
    - GENERAL. json: 1847511 bytes  # CRÍTICO - Patrones generales
    - INDICADOR. json: 133398 bytes
    - INSTITUCIONAL.json: 10429 bytes
    - INSTRUMENTO.json: 13171 bytes
    - MECANISMO_COMPLETO.json: 1348 bytes
    - MEDICION.json: 3691 bytes
    - POBLACION.json: 3846 bytes
    - PRODUCTO_TIPO.json: 3699 bytes
    - TEMPORAL.json: 17560 bytes
    - TERRITORIAL.json: 80766 bytes
    - UNIDAD_MEDIDA.json: 2542 bytes

PATTERNS_BY_CONTEXT: 
  - PDET. json: 1712 bytes

PATTERNS_BY_DIMENSION:
  - DIM01. json: 549182 bytes
  - DIM02.json: 332860 bytes
  - DIM03.json: 302275 bytes
  - DIM04.json: 242877 bytes
  - DIM05.json: 293268 bytes
  - DIM06.json: 271228 bytes

PATTERNS_BY_POLICY_AREA:
  - PA01.json: 34376 bytes
  - PA02.json: 1819 bytes
2.3 CLUSTERS CANÓNICOS (12 items - TODOS irrigable_now, gap: NINGUNO)

YAML
CLUSTERS:  # ¡LISTOS PARA IRRIGAR AHORA!
  vehiculo:  signal_registry
  consumers: [phase0_90_02_bootstrap.py, providers.py, wiring_types. py]
  
  CL01_seguridad_paz: 
    - aggregation_rules.json: 3273 bytes
    - metadata.json: 14046 bytes
    - questions.json: 813146 bytes
    
  CL02_grupos_poblacionales:
    - aggregation_rules.json: 5595 bytes
    - metadata.json: 4519 bytes
    - questions.json: 872173 bytes
    
  CL03_territorio_ambiente:
    - aggregation_rules.json: 1277 bytes
    - contextual_enrichment.json: 6286 bytes
    - metadata.json: 337 bytes
    - questions.json: 545945 bytes
    
  CL04_derechos_sociales_crisis:
    - aggregation_rules.json: 1233 bytes
    - metadata.json: 5688 bytes
    - questions.json: 554006 bytes
2.4 DIMENSIONES CANÓNICAS (18 items core - irrigable_now, gap: NINGUNO)

YAML
DIMENSIONS: # ¡LISTOS PARA IRRIGAR!
  vehiculo: signal_registry
  consumers: [phase0_90_02_bootstrap.py, providers. py, wiring_types.py]
  
  DIM01_INSUMOS:
    - metadata.json: 376 bytes
    - pdet_context.json: 16366 bytes
    - questions.json: 499545 bytes
    
  DIM02_ACTIVIDADES:
    - metadata.json: 367 bytes
    - pdet_context.json: 11718 bytes
    - questions.json: 484774 bytes
    
  DIM03_PRODUCTOS:
    - metadata.json: 358 bytes
    - pdet_context.json: 7013 bytes
    - questions.json: 841168 bytes
    
  DIM04_RESULTADOS:
    - metadata.json: 337 bytes
    - pdet_context.json: 7036 bytes
    - questions.json: 443258 bytes
    
  DIM05_IMPACTOS:
    - metadata.json: 370 bytes
    - pdet_context.json: 9494 bytes
    - questions.json: 479197 bytes
    
  DIM06_CAUSALIDAD:
    - metadata. json: 385 bytes
    - pdet_context.json: 9806 bytes
    - questions.json: 423220 bytes
2.5 POLICY AREAS (30 items - irrigable_now, gap: NINGUNO)

YAML
POLICY_AREAS: # ¡TODOS LISTOS! 
  vehiculos: [signal_quality_metrics, signal_registry, signals]
  consumers: [phase0_90_02_bootstrap. py, providers.py, wiring_types.py]
  
  PA01_mujeres_genero:
    - keywords.json: 3646 bytes (duplicate warning)
    - metadata.json: 5438 bytes
    - questions.json: 916726 bytes
    
  PA02_violencia_conflicto:
    - keywords.json: 3460 bytes
    - metadata.json: 5941 bytes
    - questions.json: 874279 bytes
    
  PA03_ambiente_cambio_climatico:
    - keywords.json: 4781 bytes
    - metadata.json: 5515 bytes
    - questions.json: 877190 bytes
    
  PA04_derechos_economicos_sociales_culturales:
    - keywords. json: 6459 bytes
    - metadata.json: 5709 bytes
    - questions.json: 884050 bytes
    
  PA05_victimas_paz:
    - keywords.json: 5230 bytes
    - metadata.json: 5389 bytes
    - questions.json: 876921 bytes
    
  PA06_ninez_adolescencia_juventud:
    - keywords. json: 5388 bytes
    - metadata.json: 5572 bytes
    - questions.json: 883327 bytes
    
  PA07_tierras_territorios: 
    - keywords.json: 5632 bytes
    - metadata.json: 5398 bytes
    - questions.json: 880600 bytes
    
  PA08_lideres_defensores: 
    - keywords.json: 5484 bytes
    - metadata.json: 5646 bytes
    - questions.json: 876660 bytes
    
  PA09_crisis_PPL:
    - keywords.json: 6088 bytes
    - metadata.json: 5365 bytes
    - questions.json: 890720 bytes
    
  PA10_migracion: 
    - keywords.json: 7059 bytes
    - metadata.json: 5307 bytes
    - questions.json: 891566 bytes
2.6 CROSS-CUTTING THEMES (11 items - irrigable_now, gap: NINGUNO)

YAML
CROSS_CUTTING: 
  vehiculos: [signal_enhancement_integrator, signal_registry]
  consumers: [phase0_90_02_bootstrap.py, providers.py, wiring_types.py]
  
  core: 
    - cross_cutting_themes.json: 9993 bytes
    - theme_integration_framework.json: 12175 bytes
    
  themes:
    CC_COHERENCIA_NORMATIVA:
      - detection_rules.json: 3746 bytes
    CC_CONTEXTO_PDET:
      - detection_rules.json: 12890 bytes
    CC_ENFOQUE_DIFERENCIAL:
      - detection_rules.json: 4017 bytes
    CC_ENTORNO_TERRITORIAL:
      - detection_rules. json: 7972 bytes
    CC_INTEROPERABILIDAD:
      - detection_rules.json: 8085 bytes
    CC_MECANISMOS_SEGUIMIENTO:
      - detection_rules. json: 7960 bytes
    CC_PARTICIPACION_CIUDADANA:
      - detection_rules.json: 7681 bytes
    CC_PERSPECTIVA_GENERO:
      - detection_rules.json: 6875 bytes
    CC_SOSTENIBILIDAD_PRESUPUESTAL:
      - detection_rules. json: 3211 bytes
2.7 CONFIGURACIÓN Y SCORING (7 items - irrigable_now, gap: NINGUNO)

YAML
CONFIG_AND_SCORING:
  - path: "config/canonical_notation.json"
    stage: phase_0
    consumers: [phase0_90_02_bootstrap.py, providers.py, wiring_types.py]
    gap: NECESITA_VEHICULO
    bytes: 67014
    
  - path: "_registry/questionnaire_index.json"
    stage: phase_0
    consumers: [phase0_90_02_bootstrap. py, providers.py, wiring_types.py]
    gap: NECESITA_VEHICULO
    bytes: 30652

SCORING: 
  vehiculos: [signal_enhancement_integrator, signal_intelligence_layer, signal_registry]
  consumers: [phase0_90_02_bootstrap.py, providers.py, wiring_types. py]
  
  - scoring/calibration/empirical_weights. json: 10365 bytes
  - scoring/scoring_system.json: 10673 bytes

SEMANTIC: 
  vehiculos: [signal_enhancement_integrator, signal_intelligence_layer, signal_registry]
  consumers: [phase0_90_02_bootstrap.py, providers. py, wiring_types.py]
  
  - semantic/pdet_semantic_enrichment. json: 15752 bytes
  - semantic/semantic_config.json: 8089 bytes

GOVERNANCE:
  - governance/governance. json: 14210 bytes
2.8 COLOMBIA CONTEXT (3 items - irrigable_now, gap: NECESITA_VEHICULO)

YAML
COLOMBIA_CONTEXT:
  stage: phase_3
  consumers: [phase3_10_00_phase3_signal_enriched_scoring.py]
  gap: [NECESITA_VEHICULO, VOCAB_SEÑALES_NO_ALINEADO, VOCAB_CAPACIDADES_NO_ALINEADO]
  
  - colombia_context. json: 73110 bytes
  - municipal_governance.json: 20773 bytes
  - pdet_municipalities.json: 1088931 bytes  # ARCHIVO MUY GRANDE
2.9 VALIDATIONS (5 items - irrigable_now, gap: NECESITA_CONSUMIDOR)

YAML
VALIDATIONS:
  stage: Cross-Phase
  vehiculos: [signal_enhancement_integrator, signal_intelligence_layer, signal_registry]
  gap: NECESITA_CONSUMIDOR
  
  - interdependency_mapping.json: 11887 bytes
  - normalization_report.json: 6230 bytes
  - quality_assurance_test_suite.json: 12423 bytes
  - referential_integrity.json: 9744 bytes
  - validation_templates.json: 29384 bytes
III. DIAGNÓSTICO DE GAPS POR CATEGORÍA

3.1 Matriz de Estado Actual

Code
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MATRIZ DE GAPS DEL CANONIC CENTRAL                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ CATEGORÍA              │ TOTAL │ IRRIGABLE │ NECESITA  │ NECESITA   │ VOCAB    │
│                        │       │ AHORA     │ VEHÍCULO  │ CONSUMIDOR │ NO ALIN.  │
├────────────────────────┼───────┼───────────┼───────────┼────────────┼──────────┤
│ Registry/Entities      │   12  │     12    │     12    │     0      │    12    │
│ Registry/Membership    │   13  │      0    │     13    │     0      │     0    │
│ Registry/Capabilities  │    3  │      3    │      3    │     3      │     0    │
│ Registry/Questions     │    3  │      2    │      0    │     2      │     0    │
│ Registry/Patterns      │   23  │     23    │      0    │     1      │    22    │
│ Clusters               │   12  │     12    │      0    │     0      │     0    │
│ Dimensions (core)      │   18  │     18    │      0    │     0      │     0    │
│ Policy Areas           │   30  │     30    │      0    │     0      │     0    │
│ Cross-Cutting          │   11  │     11    │      0    │     0      │     0    │
│ Scoring/Semantic       │    4  │      4    │      0    │     0      │     0    │
│ Colombia Context       │    3  │      3    │      3    │     0      │     3    │
│ Validations            │    5  │      5    │      0    │     5      │     0    │
│ Config                 │    2  │      2    │      2    │     0      │     0    │
│ Governance             │    1  │      1    │      0    │     0      │     0    │
├────────────────────────┼───────┼───────────┼───────────┼────────────┼──────────┤
│ TOTAL                  │  140  │    126    │     33    │    11      │    37    │
└─────────────────────────────────────────────────────────────────────────────────┘
3.2 Priorización de Resolución de Gaps

YAML
PRIORITY_1_CRITICAL:  # Resolver primero - Bloquean todo
  description: "Items que bloquean la irrigación de múltiples consumidores"
  
  items:
    - _registry/EMPIRICAL_CORPUS_INDEX.json
      problema:  NECESITA_VEHICULO
      impacto:  Bloquea phase1_11_00 y phase1_13_00
      
    - _registry/patterns/MASTER_INDEX.json
      problema: NECESITA_CONSUMIDOR
      impacto: 7 vehículos sin destino

PRIORITY_2_VOCAB_ALIGNMENT: # Resolver segundo
  description: "Vocabularios no alineados entre señales y capacidades"
  count: 37 items
  
  afectados:
    - Todas las entidades en _registry/entities/
    - Todos los patterns en _registry/patterns/by_category/
    - Colombia context completo

PRIORITY_3_CONSUMER_DECLARATION: # Resolver tercero
  description: "Necesitan declarar consumidor en fase"
  count: 11 items
  
  afectados:
    - _registry/patterns/MASTER_INDEX.json
    - _registry/questions/integration_map.json
    - _registry/questions/meso_questions.json
    - Todos los validations/
IV. ARQUITECTURA DEL NUEVO SISTEMA SISAS

4.1 Estructura de Directorios Final

Code
src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/
├── core/
│   ├── __init__.py
│   ├── signal. py                    # Definición base de Signal
│   ├── event. py                     # Definición de Event
│   ├── contracts. py                 # Contratos de publicación/consumo
│   └── bus.py                       # Bus de señales
│
├── vehicles/
│   ├── __init__.py
│   ├── base_vehicle.py              # Clase base para vehículos
│   ├── signal_registry.py           # Vehículo:  signal_registry
│   ├── signal_context_scoper.py     # Vehículo: signal_context_scoper
│   ├── signal_evidence_extractor.py # Vehículo: signal_evidence_extractor
│   ├── signal_intelligence_layer.py # Vehículo: signal_intelligence_layer
│   ├── signal_loader.py             # Vehículo: signal_loader
│   ├── signal_quality_metrics.py    # Vehículo: signal_quality_metrics
│   ├── signal_irrigator.py          # Vehículo: signal_irrigator
│   ├── signal_enhancement_integrator.py  # Vehículo: signal_enhancement_integrator
│   └── signals.py                   # Vehículo: signals (agregador)
│
├── consumers/
│   ├── __init__.py
│   ├── base_consumer.py             # Clase base para consumidores
│   ├── phase0/
│   │   ├── __init__.py
│   │   ├── phase0_90_02_bootstrap.py
│   │   ├── providers.py
│   │   └── wiring_types.py
│   ├── phase1/
│   │   ├── __init__. py
│   │   ├── phase1_11_00_signal_enrichment.py
│   │   └── phase1_13_00_cpp_ingestion.py
│   ├── phase2/
│   │   ├── __init__.py
│   │   ├── phase2_10_00_factory.py
│   │   ├── phase2_30_03_resource_aware_executor.py
│   │   ├── phase2_40_03_irrigation_synchronizer.py
│   │   ├── phase2_60_00_base_executor_with_contract.py
│   │   ├── phase2_80_00_evidence_nexus.py
│   │   ├── phase2_95_00_contract_hydrator.py
│   │   └── phase2_95_02_precision_tracking.py
│   ├── phase3/
│   │   ├── __init__. py
│   │   └── phase3_10_00_phase3_signal_enriched_scoring.py
│   ├── phase7/
│   │   └── __init__.py              # Pendiente declarar consumidor
│   └── phase8/
│       ├── __init__.py
│       └── phase8_30_00_signal_enriched_recommendations.py
│
├── signals/
│   ├── __init__.py
│   ├── types/
│   │   ├── __init__.py
│   │   ├── structural. py            # StructuralAlignmentSignal, SchemaConflictSignal
│   │   ├── integrity.py             # EventPresenceSignal, EventCompletenessSignal
│   │   ├── epistemic.py             # DeterminacySignal, SpecificitySignal, EmpiricalSupportSignal
│   │   ├── contrast.py              # DecisionDivergenceSignal, ConfidenceDropSignal
│   │   ├── operational.py           # ExecutionAttemptSignal, FailureModeSignal
│   │   └── consumption.py           # FrequencySignal, TemporalCouplingSignal
│   └── registry.py                  # Registro central de tipos de señales
│
├── irrigation/
│   ├── __init__.py
│   ├── irrigation_map.py            # Mapa de irrigación:  quién recibe qué
│   ├── irrigation_executor.py       # Ejecutor de irrigación
│   └── irrigation_validator.py      # Validador de contratos
│
├── vocabulary/
│   ├── __init__.py
│   ├── signal_vocabulary.py         # Vocabulario canónico de señales
│   ├── capability_vocabulary.py     # Vocabulario canónico de capacidades
│   └── alignment_checker.py         # Verificador de alineación
│
├── audit/
│   ├── __init__.py
│   ├── signal_auditor.py            # Auditor de señales
│   ├── consumer_auditor.py          # Auditor de consumidores
│   └── decision_auditor.py          # Auditor de decisiones
│
├── schemas/
│   ├── signal_schema.json           # JSON Schema para señales
│   ├── event_schema.json            # JSON Schema para eventos
│   ├── contract_schema.json         # JSON Schema para contratos
│   └── irrigation_spec_schema.json  # JSON Schema para specs de irrigación
│
└── config/
    ├── __init__.py
    ├── bus_config.yaml              # Configuración de buses
    ├── irrigation_config.yaml       # Configuración de irrigación
    └── vocabulary_config.yaml       # Configuración de vocabularios
V. ESPECIFICACIONES TÉCNICAS DETALLADAS

5.1 CORE: Signal Base

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/signal.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic
from uuid import uuid4
import hashlib
import json


class SignalCategory(Enum):
    """Categorías de señales según taxonomía SISAS"""
    STRUCTURAL = "structural"
    INTEGRITY = "integrity"
    EPISTEMIC = "epistemic"
    CONTRAST = "contrast"
    OPERATIONAL = "operational"
    CONSUMPTION = "consumption"


class SignalConfidence(Enum):
    """Niveles de confianza de una señal"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True)
class SignalContext:
    """
    Contexto de anclaje de una señal. 
    Una señal SIEMPRE está anclada a un contexto específico.
    """
    node_type: str          # tipo de nodo:  "policy_area", "dimension", "question", "cluster"
    node_id: str            # identificador del nodo:  "PA03", "DIM02", "Q147"
    phase: str              # fase del pipeline: "phase_0", "phase_1", etc.
    consumer_scope: str     # alcance del consumidor: "Phase_0", "Phase_2", "Cross-Phase"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "node_type":  self.node_type,
            "node_id": self.node_id,
            "phase":  self.phase,
            "consumer_scope": self.consumer_scope
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> SignalContext:
        return cls(
            node_type=data["node_type"],
            node_id=data["node_id"],
            phase=data["phase"],
            consumer_scope=data["consumer_scope"]
        )


@dataclass(frozen=True)
class SignalSource:
    """
    Origen de una señal - trazabilidad completa
    """
    event_id: str                    # ID del evento que generó la señal
    source_file: str                 # Archivo JSON canónico de origen
    source_path: str                 # Path completo en el repositorio
    generation_timestamp: datetime   # Cuándo se generó
    generator_vehicle: str           # Qué vehículo la generó
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source_file": self.source_file,
            "source_path": self.source_path,
            "generation_timestamp": self. generation_timestamp.isoformat(),
            "generator_vehicle": self.generator_vehicle
        }


@dataclass
class Signal(ABC):
    """
    Clase base abstracta para todas las señales SISAS. 
    
    AXIOMAS DE SEÑAL (inmutables):
    1. derived:  Nunca primaria, siempre derivada de eventos
    2. deterministic: Mismo input → misma señal
    3. versioned: Nunca se sobrescribe, solo se acumula
    4. contextual: Anclada a nodo, fase, consumidor
    5. auditable: Explica por qué existe
    6. non_imperative: No ordena, no decide
    """
    
    # Identificación
    signal_id: str = field(default_factory=lambda:  str(uuid4()))
    signal_type: str = field(init=False)  # Se define en subclases
    version: str = "1.0.0"
    
    # Contexto (SIEMPRE requerido)
    context: SignalContext = field(default=None)
    
    # Origen (trazabilidad)
    source: SignalSource = field(default=None)
    
    # Payload de la señal
    value: Any = field(default=None)
    confidence: SignalConfidence = field(default=SignalConfidence.INDETERMINATE)
    rationale: str = field(default="")
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = field(default=None)
    tags: List[str] = field(default_factory=list)
    
    # Auditoría
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validación post-inicialización"""
        if self. context is None:
            raise ValueError("Signal MUST have a context (axiom:  contextual)")
        if self.source is None:
            raise ValueError("Signal MUST have a source (axiom: derived)")
        
        # Registrar creación en audit trail
        self.audit_trail.append({
            "action": "CREATED",
            "timestamp": self.created_at.isoformat(),
            "signal_id": self.signal_id,
            "signal_type":  self.signal_type
        })
    
    @property
    @abstractmethod
    def category(self) -> SignalCategory:
        """Cada señal debe declarar su categoría"""
        pass
    
    def compute_hash(self) -> str:
        """
        Computa hash determinístico de la señal.
        Garantiza axioma: deterministic
        """
        hashable_content = {
            "signal_type": self.signal_type,
            "context": self.context.to_dict(),
            "value": self.value,
            "version": self.version
        }
        content_str = json.dumps(hashable_content, sort_keys=True)
        return hashlib. sha256(content_str.encode()).hexdigest()
    
    def is_valid(self) -> bool:
        """Verifica si la señal es válida"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]: 
        """Serializa la señal a diccionario"""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "category": self.category.value,
            "version": self.version,
            "context": self.context.to_dict(),
            "source": self.source.to_dict() if self.source else None,
            "value": self.value,
            "confidence": self.confidence.value,
            "rationale": self.rationale,
            "created_at": self.created_at.isoformat(),
            "expires_at": self. expires_at.isoformat() if self.expires_at else None,
            "tags": self. tags,
            "hash": self.compute_hash()
        }
    
    def add_audit_entry(self, action: str, details: Dict[str, Any] = None):
        """Añade entrada al audit trail"""
        entry = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "signal_id": self.signal_id
        }
        if details: 
            entry["details"] = details
        self.audit_trail.append(entry)
5.2 CORE: Event

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/event.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json


class EventType(Enum):
    """Tipos de eventos en el sistema"""
    # Eventos de datos canónicos
    CANONICAL_DATA_LOADED = "canonical_data_loaded"
    CANONICAL_DATA_VALIDATED = "canonical_data_validated"
    CANONICAL_DATA_TRANSFORMED = "canonical_data_transformed"
    
    # Eventos de irrigación
    IRRIGATION_REQUESTED = "irrigation_requested"
    IRRIGATION_STARTED = "irrigation_started"
    IRRIGATION_COMPLETED = "irrigation_completed"
    IRRIGATION_FAILED = "irrigation_failed"
    
    # Eventos de consumo
    CONSUMER_REGISTERED = "consumer_registered"
    CONSUMER_RECEIVED_DATA = "consumer_received_data"
    CONSUMER_PROCESSED_DATA = "consumer_processed_data"
    
    # Eventos de señales
    SIGNAL_GENERATED = "signal_generated"
    SIGNAL_PUBLISHED = "signal_published"
    SIGNAL_CONSUMED = "signal_consumed"
    
    # Eventos de contraste (legacy vs nuevo)
    CONTRAST_STARTED = "contrast_started"
    CONTRAST_DIVERGENCE_DETECTED = "contrast_divergence_detected"
    CONTRAST_COMPLETED = "contrast_completed"


@dataclass(frozen=True)
class EventPayload:
    """Payload inmutable de un evento"""
    data: Dict[str, Any]
    schema_version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]: 
        return {
            "data":  self.data,
            "schema_version": self.schema_version
        }


@dataclass
class Event:
    """
    Evento empírico en el sistema SISAS.
    
    Un evento es un HECHO que ocurrió. 
    NO interpreta, NO juzga, solo registra.
    
    Los eventos son la FUENTE de las señales.
    """
    
    # Identificación
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = field(default=EventType.CANONICAL_DATA_LOADED)
    
    # Temporal
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Ubicación en el sistema
    source_component: str = ""          # Componente que generó el evento
    source_file: str = ""               # Archivo canónico relacionado
    source_path: str = ""               # Path completo
    
    # Payload (lo que pasó)
    payload: EventPayload = field(default=None)
    
    # Contexto de procesamiento
    phase: str = ""                     # Fase del pipeline
    consumer_scope: str = ""            # Alcance del consumidor
    
    # Metadatos
    correlation_id: Optional[str] = None  # Para trazar eventos relacionados
    causation_id: Optional[str] = None    # Evento que causó este
    
    # Estado
    processed: bool = False
    processing_errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el evento"""
        return {
            "event_id": self.event_id,
            "event_type":  self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source_component": self.source_component,
            "source_file": self.source_file,
            "source_path": self. source_path,
            "payload": self.payload.to_dict() if self.payload else None,
            "phase": self.phase,
            "consumer_scope": self.consumer_scope,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "processed": self. processed
        }
    
    @classmethod
    def from_canonical_file(
        cls,
        file_path: str,
        file_content: Dict[str, Any],
        phase: str,
        consumer_scope: str
    ) -> Event:
        """
        Factory para crear evento desde archivo canónico.
        """
        import os
        
        return cls(
            event_type=EventType.CANONICAL_DATA_LOADED,
            source_file=os.path.basename(file_path),
            source_path=file_path,
            payload=EventPayload(data=file_content),
            phase=phase,
            consumer_scope=consumer_scope,
            source_component="canonical_loader"
        )
    
    def mark_processed(self):
        """Marca el evento como procesado"""
        self.processed = True
    
    def add_error(self, error: str):
        """Añade error de procesamiento"""
        self.processing_errors.append(error)


@dataclass
class EventStore:
    """
    Almacén de eventos - NUNCA se borran. 
    Implementa el axioma:  Ningún evento se pierde.
    """
    
    events: List[Event] = field(default_factory=list)
    _index_by_type: Dict[str, List[str]] = field(default_factory=dict)
    _index_by_file: Dict[str, List[str]] = field(default_factory=dict)
    _index_by_phase: Dict[str, List[str]] = field(default_factory=dict)
    
    def append(self, event: Event) -> str:
        """
        Añade evento al store.
        Retorna el event_id. 
        """
        self.events.append(event)
        
        # Indexar por tipo
        if event.event_type. value not in self._index_by_type:
            self._index_by_type[event.event_type.value] = []
        self._index_by_type[event.event_type.value]. append(event.event_id)
        
        # Indexar por archivo
        if event.source_file:
            if event.source_file not in self._index_by_file:
                self._index_by_file[event.source_file] = []
            self._index_by_file[event. source_file].append(event. event_id)
        
        # Indexar por fase
        if event.phase:
            if event.phase not in self._index_by_phase:
                self._index_by_phase[event.phase] = []
            self._index_by_phase[event.phase].append(event.event_id)
        
        return event.event_id
    
    def get_by_id(self, event_id: str) -> Optional[Event]:
        """Obtiene evento por ID"""
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None
    
    def get_by_type(self, event_type: EventType) -> List[Event]:
        """Obtiene eventos por tipo"""
        ids = self._index_by_type.get(event_type.value, [])
        return [e for e in self.events if e.event_id in ids]
    
    def get_by_file(self, source_file: str) -> List[Event]:
        """Obtiene eventos por archivo fuente"""
        ids = self._index_by_file.get(source_file, [])
        return [e for e in self. events if e.event_id in ids]
    
    def get_by_phase(self, phase: str) -> List[Event]:
        """Obtiene eventos por fase"""
        ids = self._index_by_phase.get(phase, [])
        return [e for e in self.events if e.event_id in ids]
    
    def get_unprocessed(self) -> List[Event]:
        """Obtiene eventos no procesados"""
        return [e for e in self.events if not e.processed]
    
    def count(self) -> int:
        """Total de eventos"""
        return len(self.events)
    
    def to_jsonl(self) -> str:
        """Exporta a formato JSONL para persistencia"""
        lines = []
        for event in self.events:
            lines.append(json.dumps(event.to_dict()))
        return "\n".join(lines)
5.3 CORE: Contracts

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/contracts.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from abc import ABC, abstractmethod


class ContractType(Enum):
    """Tipos de contrato"""
    PUBLICATION = "publication"    # Contrato de quién puede publicar
    CONSUMPTION = "consumption"    # Contrato de quién puede consumir
    IRRIGATION = "irrigation"      # Contrato de irrigación


class ContractStatus(Enum):
    """Estado del contrato"""
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


@dataclass
class SignalTypeSpec:
    """Especificación de un tipo de señal permitido en el contrato"""
    signal_type: str
    required_confidence: str = "LOW"  # Mínimo:  HIGH, MEDIUM, LOW
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    validators: List[Callable] = field(default_factory=list)


@dataclass
class PublicationContract:
    """
    Contrato de Publicación. 
    Define QUÉ puede publicar un vehículo y CÓMO. 
    """
    
    contract_id: str
    contract_type: ContractType = ContractType.PUBLICATION
    status: ContractStatus = ContractStatus.DRAFT
    
    # Quién publica
    publisher_vehicle: str = ""
    
    # Qué puede publicar
    allowed_signal_types: List[SignalTypeSpec] = field(default_factory=list)
    
    # A qué buses puede publicar
    allowed_buses:  List[str] = field(default_factory=list)
    
    # Restricciones
    max_signals_per_second: int = 1000
    require_context:  bool = True
    require_source: bool = True
    
    # Validaciones
    pre_publish_validators: List[Callable] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    
    def validate_signal(self, signal: Any) -> tuple[bool, List[str]]:
        """
        Valida que una señal cumpla el contrato.
        Retorna (es_válido, lista_de_errores)
        """
        errors = []
        
        # Verificar tipo permitido
        signal_type = getattr(signal, 'signal_type', None)
        allowed_types = [spec.signal_type for spec in self.allowed_signal_types]
        
        if signal_type not in allowed_types:
            errors.append(f"Signal type '{signal_type}' not allowed.  Allowed:  {allowed_types}")
        
        # Verificar contexto
        if self.require_context and not hasattr(signal, 'context'):
            errors.append("Signal must have context")
        elif self.require_context and signal.context is None:
            errors.append("Signal context cannot be None")
        
        # Verificar source
        if self.require_source and not hasattr(signal, 'source'):
            errors.append("Signal must have source")
        elif self.require_source and signal.source is None:
            errors.append("Signal source cannot be None")
        
        # Ejecutar validadores custom
        for validator in self.pre_publish_validators:
            try:
                is_valid, msg = validator(signal)
                if not is_valid:
                    errors.append(msg)
            except Exception as e:
                errors.append(f"Validator error: {str(e)}")
        
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id":  self.contract_id,
            "contract_type": self.contract_type.value,
            "status": self.status.value,
            "publisher_vehicle": self.publisher_vehicle,
            "allowed_signal_types": [s.signal_type for s in self.allowed_signal_types],
            "allowed_buses": self. allowed_buses,
            "version": self.version
        }


@dataclass
class ConsumptionContract:
    """
    Contrato de Consumo. 
    Define QUÉ puede consumir un consumidor y CÓMO debe procesarlo.
    """
    
    contract_id: str
    contract_type: ContractType = ContractType.CONSUMPTION
    status: ContractStatus = ContractStatus.DRAFT
    
    # Quién consume
    consumer_id: str = ""
    consumer_phase: str = ""
    
    # Qué puede consumir
    subscribed_signal_types: List[str] = field(default_factory=list)
    subscribed_buses: List[str] = field(default_factory=list)
    
    # Filtros
    context_filters: Dict[str, List[str]] = field(default_factory=dict)
    # Ejemplo: {"node_type": ["policy_area", "dimension"], "phase": ["phase_0"]}
    
    # Restricciones de procesamiento
    max_processing_time_ms: int = 5000
    require_acknowledgement: bool = True
    retry_on_failure: bool = True
    max_retries: int = 3
    
    # Capacidades requeridas (del vocabulario)
    required_capabilities: List[str] = field(default_factory=list)
    
    # Callbacks
    on_receive:  Optional[Callable] = None
    on_process_complete: Optional[Callable] = None
    on_process_error:  Optional[Callable] = None
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    
    def matches_signal(self, signal: Any) -> bool:
        """
        Verifica si una señal cumple los filtros del contrato.
        """
        # Verificar tipo
        if signal.signal_type not in self. subscribed_signal_types: 
            return False
        
        # Verificar filtros de contexto
        if self.context_filters:
            signal_context = signal.context. to_dict() if signal.context else {}
            
            for filter_key, allowed_values in self.context_filters.items():
                if filter_key in signal_context:
                    if signal_context[filter_key] not in allowed_values:
                        return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self. contract_id,
            "contract_type": self.contract_type.value,
            "status":  self.status.value,
            "consumer_id": self.consumer_id,
            "consumer_phase": self.consumer_phase,
            "subscribed_signal_types": self.subscribed_signal_types,
            "subscribed_buses":  self.subscribed_buses,
            "context_filters": self. context_filters,
            "required_capabilities": self.required_capabilities,
            "version": self.version
        }


@dataclass
class IrrigationContract:
    """
    Contrato de Irrigación. 
    Define la relación completa entre un archivo canónico,
    sus vehículos de transporte, y sus consumidores.
    """
    
    contract_id: str
    contract_type: ContractType = ContractType.IRRIGATION
    status: ContractStatus = ContractStatus.DRAFT
    
    # Archivo canónico fuente
    source_file: str = ""
    source_path: str = ""
    source_phase: str = ""
    
    # Vehículos que transportan
    vehicles: List[str] = field(default_factory=list)
    
    # Consumidores destino
    consumers: List[str] = field(default_factory=list)
    
    # Señales que se generan
    generated_signals: List[str] = field(default_factory=list)
    
    # Requisitos de vocabulario
    required_signal_vocabulary: List[str] = field(default_factory=list)
    required_capability_vocabulary: List[str] = field(default_factory=list)
    
    # Estado de alineación
    vocabulary_aligned: bool = False
    gaps:  List[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    
    def is_irrigable(self) -> bool:
        """
        Verifica si el contrato permite irrigación.
        """
        return (
            len(self.vehicles) > 0 and
            len(self. consumers) > 0 and
            self.vocabulary_aligned and
            len(self.gaps) == 0 and
            self.status == ContractStatus.ACTIVE
        )
    
    def get_blocking_gaps(self) -> List[str]:
        """Retorna gaps que bloquean la irrigación"""
        blocking = []
        
        if len(self.vehicles) == 0:
            blocking.append("NECESITA_VEHICULO")
        
        if len(self.consumers) == 0:
            blocking. append("NECESITA_CONSUMIDOR")
        
        if not self.vocabulary_aligned:
            if "VOCAB_SEÑALES_NO_ALINEADO" in self.gaps:
                blocking.append("VOCAB_SEÑALES_NO_ALINEADO")
            if "VOCAB_CAPACIDADES_NO_ALINEADO" in self.gaps:
                blocking.append("VOCAB_CAPACIDADES_NO_ALINEADO")
        
        return blocking
    
    def to_dict(self) -> Dict[str, Any]: 
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type.value,
            "status": self.status. value,
            "source_file": self.source_file,
            "source_path": self. source_path,
            "source_phase": self.source_phase,
            "vehicles": self. vehicles,
            "consumers": self.consumers,
            "generated_signals": self.generated_signals,
            "vocabulary_aligned": self.vocabulary_aligned,
            "gaps": self. gaps,
            "is_irrigable": self.is_irrigable(),
            "version":  self.version
        }


@dataclass
class ContractRegistry:
    """
    Registro central de todos los contratos.
    """
    
    publication_contracts: Dict[str, PublicationContract] = field(default_factory=dict)
    consumption_contracts: Dict[str, ConsumptionContract] = field(default_factory=dict)
    irrigation_contracts: Dict[str, IrrigationContract] = field(default_factory=dict)
    
    def register_publication(self, contract: PublicationContract) -> str:
        """Registra contrato de publicación"""
        self.publication_contracts[contract.contract_id] = contract
        return contract.contract_id
    
    def register_consumption(self, contract: ConsumptionContract) -> str:
        """Registra contrato de consumo"""
        self.consumption_contracts[contract.contract_id] = contract
        return contract.contract_id
    
    def register_irrigation(self, contract: IrrigationContract) -> str:
        """Registra contrato de irrigación"""
        self.irrigation_contracts[contract.contract_id] = contract
        return contract.contract_id
    
    def get_contracts_for_vehicle(self, vehicle: str) -> List[PublicationContract]:
        """Obtiene contratos de publicación para un vehículo"""
        return [c for c in self. publication_contracts.values() 
                if c.publisher_vehicle == vehicle]
    
    def get_contracts_for_consumer(self, consumer: str) -> List[ConsumptionContract]:
        """Obtiene contratos de consumo para un consumidor"""
        return [c for c in self.consumption_contracts.values() 
                if c.consumer_id == consumer]
    
    def get_irrigation_for_file(self, source_path: str) -> Optional[IrrigationContract]: 
        """Obtiene contrato de irrigación para un archivo"""
        for contract in self.irrigation_contracts. values():
            if contract.source_path == source_path:
                return contract
        return None
    
    def get_irrigable_contracts(self) -> List[IrrigationContract]: 
        """Obtiene todos los contratos que pueden irrigar ahora"""
        return [c for c in self.irrigation_contracts.values() if c.is_irrigable()]
    
    def get_blocked_contracts(self) -> List[tuple[IrrigationContract, List[str]]]:
        """Obtiene contratos bloqueados con sus gaps"""
        result = []
        for contract in self.irrigation_contracts.values():
            if not contract.is_irrigable():
                result.append((contract, contract.get_blocking_gaps()))
        return result
5.4 CORE: Signal Bus

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/bus.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict
from queue import Queue, Empty
from threading import Lock
import logging

from . signal import Signal, SignalCategory
from .contracts import PublicationContract, ConsumptionContract, ContractRegistry


class BusType(Enum):
    """Tipos de bus según categoría de señales"""
    STRUCTURAL = "structural_bus"
    INTEGRITY = "integrity_bus"
    EPISTEMIC = "epistemic_bus"
    CONTRAST = "contrast_bus"
    OPERATIONAL = "operational_bus"
    CONSUMPTION = "consumption_bus"
    UNIVERSAL = "universal_bus"  # Recibe todo


@dataclass
class BusMessage:
    """Mensaje que circula por el bus"""
    signal: Signal
    publisher_vehicle: str
    published_at: datetime = field(default_factory=datetime. utcnow)
    message_id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    acknowledged_by: Set[str] = field(default_factory=set)
    
    def acknowledge(self, consumer_id: str):
        """Marca el mensaje como recibido por un consumidor"""
        self.acknowledged_by.add(consumer_id)


@dataclass
class SignalBus:
    """
    Bus de señales.
    
    Principios:
    1. Nada circula sin contrato
    2. Todo se registra
    3. Los consumidores analizan, no ejecutan
    """
    
    bus_type: BusType
    name: str = ""
    
    # Cola de mensajes
    _queue: Queue = field(default_factory=Queue)
    _lock: Lock = field(default_factory=Lock)
    
    # Suscriptores
    _subscribers:  Dict[str, ConsumptionContract] = field(default_factory=dict)
    
    # Historial (NUNCA se borra)
    _message_history: List[BusMessage] = field(default_factory=list)
    _max_history_size: int = 100000
    
    # Estadísticas
    _stats: Dict[str, int] = field(default_factory=lambda: {
        "total_published": 0,
        "total_delivered": 0,
        "total_rejected": 0,
        "total_errors": 0
    })
    
    # Logger
    _logger: logging.Logger = field(default=None)
    
    def __post_init__(self):
        if not self.name:
            self. name = self. bus_type.value
        if self._logger is None:
            self._logger = logging.getLogger(f"SISAS.Bus.{self.name}")
    
    def publish(
        self,
        signal: Signal,
        publisher_vehicle: str,
        publication_contract: PublicationContract
    ) -> tuple[bool, str]:
        """
        Publica una señal en el bus.
        
        Retorna (éxito, mensaje/error)
        """
        # Validar contrato
        is_valid, errors = publication_contract.validate_signal(signal)
        
        if not is_valid: 
            self._stats["total_rejected"] += 1
            error_msg = f"Contract validation failed: {errors}"
            self._logger.warning(error_msg)
            return (False, error_msg)
        
        # Verificar que el bus está permitido
        if self.name not in publication_contract.allowed_buses:
            self._stats["total_rejected"] += 1
            error_msg = f"Bus '{self. name}' not in allowed buses"
            self._logger.warning(error_msg)
            return (False, error_msg)
        
        # Crear mensaje
        message = BusMessage(
            signal=signal,
            publisher_vehicle=publisher_vehicle
        )
        
        #
You said: CONTINUA
CONTINUA

Copilot said: ### 5. 4 CORE: Signal Bus
5. 4 CORE: Signal Bus (Continuación)

Python
        # Encolar mensaje
        with self._lock:
            self._queue.put(message)
            self._message_history.append(message)
            
            # Limitar historial si excede máximo
            if len(self._message_history) > self._max_history_size:
                # No borramos, movemos a almacenamiento persistente
                self._persist_overflow()
            
            self._stats["total_published"] += 1
        
        self._logger.info(
            f"Signal published: {signal.signal_type} from {publisher_vehicle}"
        )
        
        # Notificar a suscriptores
        self._notify_subscribers(message)
        
        return (True, message.message_id)
    
    def subscribe(self, contract: ConsumptionContract) -> bool:
        """
        Suscribe un consumidor al bus.
        """
        if self.name not in contract.subscribed_buses:
            self._logger.warning(
                f"Consumer {contract.consumer_id} tried to subscribe to "
                f"non-allowed bus {self.name}"
            )
            return False
        
        with self._lock:
            self._subscribers[contract.consumer_id] = contract
        
        self._logger.info(f"Consumer {contract.consumer_id} subscribed to {self.name}")
        return True
    
    def unsubscribe(self, consumer_id: str) -> bool:
        """Desuscribe un consumidor"""
        with self._lock:
            if consumer_id in self._subscribers:
                del self._subscribers[consumer_id]
                self._logger.info(f"Consumer {consumer_id} unsubscribed from {self.name}")
                return True
        return False
    
    def _notify_subscribers(self, message: BusMessage):
        """Notifica a todos los suscriptores que coincidan"""
        for consumer_id, contract in self._subscribers.items():
            if contract.matches_signal(message.signal):
                try:
                    if contract.on_receive: 
                        contract.on_receive(message. signal, consumer_id)
                    message.acknowledge(consumer_id)
                    self._stats["total_delivered"] += 1
                except Exception as e: 
                    self._stats["total_errors"] += 1
                    self._logger.error(
                        f"Error notifying {consumer_id}: {str(e)}"
                    )
                    if contract.on_process_error:
                        contract. on_process_error(message. signal, consumer_id, e)
    
    def get_pending_messages(self) -> List[BusMessage]:
        """Obtiene mensajes pendientes sin vaciar la cola"""
        with self._lock:
            return list(self._queue.queue)
    
    def consume_next(self, timeout: float = 1.0) -> Optional[BusMessage]:
        """Consume el siguiente mensaje de la cola"""
        try:
            return self._queue.get(timeout=timeout)
        except Empty: 
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas del bus"""
        return self._stats. copy()
    
    def get_subscriber_count(self) -> int:
        """Número de suscriptores"""
        return len(self._subscribers)
    
    def _persist_overflow(self):
        """Persiste mensajes cuando excede el límite"""
        # Implementar persistencia a disco/DB
        overflow_count = len(self._message_history) - self._max_history_size
        if overflow_count > 0:
            # Los primeros N mensajes van a persistencia
            to_persist = self._message_history[:overflow_count]
            self._message_history = self._message_history[overflow_count:]
            # TODO: Escribir to_persist a almacenamiento persistente
            self._logger.info(f"Persisted {overflow_count} messages from {self.name}")


@dataclass
class BusRegistry:
    """
    Registro central de todos los buses.
    """
    
    buses: Dict[str, SignalBus] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)
    
    def __post_init__(self):
        # Crear buses por defecto para cada categoría
        for bus_type in BusType:
            self.create_bus(bus_type)
    
    def create_bus(self, bus_type: BusType, name: str = None) -> SignalBus:
        """Crea un nuevo bus"""
        bus_name = name or bus_type.value
        with self._lock:
            if bus_name not in self.buses:
                self.buses[bus_name] = SignalBus(
                    bus_type=bus_type,
                    name=bus_name
                )
        return self.buses[bus_name]
    
    def get_bus(self, name: str) -> Optional[SignalBus]:
        """Obtiene un bus por nombre"""
        return self.buses.get(name)
    
    def get_bus_for_signal(self, signal: Signal) -> SignalBus:
        """Obtiene el bus apropiado para una señal según su categoría"""
        category_to_bus = {
            SignalCategory.STRUCTURAL: BusType.STRUCTURAL,
            SignalCategory.INTEGRITY: BusType.INTEGRITY,
            SignalCategory.EPISTEMIC: BusType.EPISTEMIC,
            SignalCategory.CONTRAST:  BusType.CONTRAST,
            SignalCategory.OPERATIONAL:  BusType.OPERATIONAL,
            SignalCategory.CONSUMPTION:  BusType.CONSUMPTION,
        }
        bus_type = category_to_bus.get(signal.category, BusType.UNIVERSAL)
        return self.buses[bus_type. value]
    
    def publish_to_appropriate_bus(
        self,
        signal: Signal,
        publisher_vehicle: str,
        publication_contract: PublicationContract
    ) -> tuple[bool, str]:
        """Publica una señal en el bus apropiado según su categoría"""
        bus = self.get_bus_for_signal(signal)
        return bus.publish(signal, publisher_vehicle, publication_contract)
    
    def get_all_stats(self) -> Dict[str, Dict[str, int]]:
        """Estadísticas de todos los buses"""
        return {name: bus.get_stats() for name, bus in self.buses. items()}
5.5 SIGNALS: Tipos de Señales

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/structural. py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ... core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class AlignmentStatus(Enum):
    """Estados de alineación estructural"""
    ALIGNED = "ALIGNED"
    PARTIAL = "PARTIAL"
    MISALIGNED = "MISALIGNED"
    UNKNOWN = "UNKNOWN"


@dataclass
class StructuralAlignmentSignal(Signal):
    """
    Señal que indica si un dato/evento mapea correctamente
    a la estructura canónica.
    
    Uso:  Verificar que Q147 existe, está ligada a PA03, tiene métodos definidos. 
    """
    
    signal_type: str = field(default="StructuralAlignmentSignal", init=False)
    
    # Payload específico
    alignment_status: AlignmentStatus = AlignmentStatus.UNKNOWN
    canonical_path: str = ""  # Path canónico esperado
    actual_path: str = ""     # Path real encontrado
    missing_elements: List[str] = field(default_factory=list)
    extra_elements: List[str] = field(default_factory=list)
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL
    
    def compute_alignment_score(self) -> float:
        """Calcula score de alineación 0.0 a 1.0"""
        if self.alignment_status == AlignmentStatus.ALIGNED: 
            return 1.0
        elif self.alignment_status == AlignmentStatus.PARTIAL: 
            total_issues = len(self.missing_elements) + len(self.extra_elements)
            if total_issues == 0:
                return 0.5
            return max(0.1, 0.5 - (total_issues * 0.1))
        elif self.alignment_status == AlignmentStatus.MISALIGNED: 
            return 0.0
        return 0.0


@dataclass
class SchemaConflictSignal(Signal):
    """
    Señal que indica conflicto de esquemas entre datos.
    
    Uso: Detectar cuando un archivo tiene estructura diferente a la esperada. 
    """
    
    signal_type: str = field(default="SchemaConflictSignal", init=False)
    
    # Payload específico
    expected_schema_version: str = ""
    actual_schema_version: str = ""
    conflict_type: str = ""  # "missing_field", "type_mismatch", "extra_field"
    conflicting_fields: List[Dict[str, Any]] = field(default_factory=list)
    # Cada conflicto:  {"field": "name", "expected": "string", "actual": "int"}
    
    is_breaking: bool = False  # ¿El conflicto rompe la compatibilidad?
    suggested_resolution: str = ""
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. STRUCTURAL


@dataclass  
class CanonicalMappingSignal(Signal):
    """
    Señal que indica el resultado de mapear un ítem a entidades canónicas.
    
    Uso: Verificar que una respuesta se mapea a policy_area, dimension, etc.
    """
    
    signal_type: str = field(default="CanonicalMappingSignal", init=False)
    
    # Payload específico
    source_item_id: str = ""
    mapped_entities: Dict[str, str] = field(default_factory=dict)
    # Ejemplo: {"policy_area": "PA03", "dimension": "DIM02", "cluster": "CL01"}
    
    unmapped_aspects: List[str] = field(default_factory=list)
    mapping_completeness: float = 0.0  # 0.0 a 1.0
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/integrity.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class PresenceStatus(Enum):
    """Estados de presencia de evento"""
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    PARTIAL = "PARTIAL"


class CompletenessLevel(Enum):
    """Niveles de completitud"""
    COMPLETE = "COMPLETE"
    MOSTLY_COMPLETE = "MOSTLY_COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    EMPTY = "EMPTY"


@dataclass
class EventPresenceSignal(Signal):
    """
    Señal que indica si un evento esperado existe. 
    
    Uso:  Verificar que AnswerSubmitted para Q147 existe.
    """
    
    signal_type: str = field(default="EventPresenceSignal", init=False)
    
    # Payload específico
    expected_event_type: str = ""
    presence_status: PresenceStatus = PresenceStatus.ABSENT
    event_count: int = 0
    first_occurrence:  Optional[str] = None  # timestamp ISO
    last_occurrence: Optional[str] = None
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. INTEGRITY


@dataclass
class EventCompletenessSignal(Signal):
    """
    Señal que indica qué tan completo es un evento. 
    
    Uso:  Verificar que el evento tiene todos los campos requeridos.
    """
    
    signal_type: str = field(default="EventCompletenessSignal", init=False)
    
    # Payload específico
    completeness_level: CompletenessLevel = CompletenessLevel. EMPTY
    required_fields: List[str] = field(default_factory=list)
    present_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    
    completeness_score: float = 0.0  # 0.0 a 1.0
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.INTEGRITY
    
    def __post_init__(self):
        super().__post_init__()
        # Calcular campos faltantes
        self.missing_fields = [
            f for f in self.required_fields if f not in self.present_fields
        ]
        # Calcular score
        if self.required_fields:
            self.completeness_score = len(self.present_fields) / len(self.required_fields)


@dataclass
class DataIntegritySignal(Signal):
    """
    Señal que indica la integridad referencial de los datos.
    
    Uso: Verificar que las referencias entre archivos son válidas.
    """
    
    signal_type: str = field(default="DataIntegritySignal", init=False)
    
    # Payload específico
    source_file: str = ""
    referenced_files: List[str] = field(default_factory=list)
    valid_references: List[str] = field(default_factory=list)
    broken_references: List[str] = field(default_factory=list)
    
    integrity_score: float = 0.0
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. INTEGRITY
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/epistemic.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class DeterminacyLevel(Enum):
    """Niveles de determinismo de una respuesta"""
    HIGH = "HIGH"           # Afirmación clara y sin ambigüedad
    MEDIUM = "MEDIUM"       # Afirmación con alguna vaguedad
    LOW = "LOW"             # Afirmación muy vaga o condicional
    INDETERMINATE = "INDETERMINATE"  # No se puede determinar


class SpecificityLevel(Enum):
    """Niveles de especificidad"""
    HIGH = "HIGH"           # Menciona instrumento, alcance, responsable
    MEDIUM = "MEDIUM"       # Menciona algunos elementos
    LOW = "LOW"             # Muy genérico
    NONE = "NONE"           # Sin especificidad


class EmpiricalSupportLevel(Enum):
    """Niveles de soporte empírico"""
    STRONG = "STRONG"       # Referencia documental clara
    MODERATE = "MODERATE"   # Referencia parcial
    WEAK = "WEAK"           # Sin referencia pero plausible
    NONE = "NONE"           # Sin evidencia


@dataclass
class AnswerDeterminacySignal(Signal):
    """
    Señal que evalúa qué tan determinante es una respuesta.
    
    Uso: Evaluar "Sí, se realiza evaluación previa en algunos casos"
    → MEDIUM (afirmación con scope ambiguity)
    """
    
    signal_type:  str = field(default="AnswerDeterminacySignal", init=False)
    
    # Payload específico
    question_id: str = ""
    determinacy_level: DeterminacyLevel = DeterminacyLevel.INDETERMINATE
    
    # Indicadores detectados
    affirmative_markers: List[str] = field(default_factory=list)
    # ["sí", "existe", "se realiza"]
    
    ambiguity_markers: List[str] = field(default_factory=list)
    # ["algunos casos", "a veces", "parcialmente"]
    
    negation_markers: List[str] = field(default_factory=list)
    # ["no", "nunca", "ninguno"]
    
    conditional_markers: List[str] = field(default_factory=list)
    # ["si", "cuando", "dependiendo"]
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC


@dataclass
class AnswerSpecificitySignal(Signal):
    """
    Señal que evalúa qué tan específica es una respuesta. 
    
    Uso:  Detectar si menciona instrumento formal, alcance obligatorio, 
    responsable institucional. 
    """
    
    signal_type: str = field(default="AnswerSpecificitySignal", init=False)
    
    # Payload específico
    question_id: str = ""
    specificity_level: SpecificityLevel = SpecificityLevel.NONE
    
    # Elementos esperados vs encontrados
    expected_elements: List[str] = field(default_factory=list)
    # ["formal_instrument", "mandatory_scope", "institutional_owner"]
    
    found_elements: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)
    
    specificity_score: float = 0.0
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. EPISTEMIC


@dataclass
class EmpiricalSupportSignal(Signal):
    """
    Señal que evalúa el soporte empírico/documental de una respuesta.
    
    Uso: Detectar si hay referencia a ley, decreto, resolución, documento.
    """
    
    signal_type: str = field(default="EmpiricalSupportSignal", init=False)
    
    # Payload específico
    question_id: str = ""
    support_level: EmpiricalSupportLevel = EmpiricalSupportLevel. NONE
    
    # Referencias encontradas
    normative_references: List[str] = field(default_factory=list)
    # ["Ley 1448 de 2011", "Decreto 4800"]
    
    document_references: List[str] = field(default_factory=list)
    # ["Plan Nacional de Desarrollo", "CONPES 3932"]
    
    institutional_references: List[str] = field(default_factory=list)
    # ["Ministerio del Interior", "Unidad de Víctimas"]
    
    temporal_references: List[str] = field(default_factory=list)
    # ["2022", "desde 2018", "vigencia 2023"]
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC


@dataclass
class MethodApplicationSignal(Signal):
    """
    Señal que indica el resultado de aplicar un método de evaluación.
    
    Uso: Registrar qué método se aplicó y su resultado.
    """
    
    signal_type: str = field(default="MethodApplicationSignal", init=False)
    
    # Payload específico
    question_id: str = ""
    method_id: str = ""  # "MC01", "MC05_financial_chains"
    method_version: str = ""
    
    # Resultado
    method_result: Dict[str, Any] = field(default_factory=dict)
    extraction_successful: bool = False
    extracted_values: List[Any] = field(default_factory=list)
    
    processing_time_ms: float = 0.0
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/contrast.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class DivergenceType(Enum):
    """Tipos de divergencia"""
    VALUE_MISMATCH = "VALUE_MISMATCH"
    CLASSIFICATION_MISMATCH = "CLASSIFICATION_MISMATCH"
    CONFIDENCE_MISMATCH = "CONFIDENCE_MISMATCH"
    STRUCTURE_MISMATCH = "STRUCTURE_MISMATCH"


class DivergenceSeverity(Enum):
    """Severidad de la divergencia"""
    CRITICAL = "CRITICAL"   # Afecta decisiones
    HIGH = "HIGH"           # Diferencia significativa
    MEDIUM = "MEDIUM"       # Diferencia notable
    LOW = "LOW"             # Diferencia menor


@dataclass
class DecisionDivergenceSignal(Signal):
    """
    Señal que indica divergencia entre sistema legacy y nuevo.
    
    Uso: Comparar output legacy "COMPLIANT" vs señales "INDETERMINATE"
    """
    
    signal_type: str = field(default="DecisionDivergenceSignal", init=False)
    
    # Payload específico
    item_id: str = ""  # Q147, PA03, etc.
    
    # Valores comparados
    legacy_value: Any = None
    legacy_source: str = ""
    
    signal_based_value: Any = None
    supporting_signals: List[str] = field(default_factory=list)
    
    # Análisis de divergencia
    divergence_type: DivergenceType = DivergenceType.VALUE_MISMATCH
    divergence_severity: DivergenceSeverity = DivergenceSeverity.MEDIUM
    divergence_explanation: str = ""
    
    # Recomendación (NO imperativa)
    suggested_investigation: str = ""
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONTRAST


@dataclass
class ConfidenceDropSignal(Signal):
    """
    Señal que indica caída de confianza en una evaluación.
    
    Uso: Detectar cuando las señales sugieren menor confianza que antes.
    """
    
    signal_type: str = field(default="ConfidenceDropSignal", init=False)
    
    # Payload específico
    item_id: str = ""
    
    previous_confidence: float = 0.0
    current_confidence: float = 0.0
    drop_percentage: float = 0.0
    
    contributing_factors: List[str] = field(default_factory=list)
    # ["new_ambiguity_detected", "reference_invalidated", "scope_change"]
    
    trend:  str = ""  # "declining", "stable", "improving"
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. CONTRAST


@dataclass
class TemporalContrastSignal(Signal):
    """
    Señal que indica cambios entre evaluaciones en diferentes momentos.
    
    Uso: Tracking de evolución de respuestas/evaluaciones.
    """
    
    signal_type: str = field(default="TemporalContrastSignal", init=False)
    
    # Payload específico
    item_id: str = ""
    
    baseline_timestamp: str = ""
    current_timestamp: str = ""
    
    baseline_state: Dict[str, Any] = field(default_factory=dict)
    current_state: Dict[str, Any] = field(default_factory=dict)
    
    changes_detected: List[Dict[str, Any]] = field(default_factory=list)
    # [{"field": "score", "old": 0.7, "new": 0.5, "delta": -0.2}]
    
    stability_score: float = 0.0  # 1.0 = sin cambios, 0.0 = cambio total
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONTRAST
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/operational.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class ExecutionStatus(Enum):
    """Estados de ejecución"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class FailureMode(Enum):
    """Modos de falla"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TRANSFORMATION_ERROR = "TRANSFORMATION_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    UNKNOWN = "UNKNOWN"


@dataclass
class ExecutionAttemptSignal(Signal):
    """
    Señal que registra un intento de ejecución. 
    
    Uso: Registrar que se intentó procesar Q147, incluso si falló.
    """
    
    signal_type: str = field(default="ExecutionAttemptSignal", init=False)
    
    # Payload específico
    execution_id: str = ""
    component:  str = ""  # Qué componente ejecutó
    operation: str = ""  # Qué operación
    
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    
    input_summary: Dict[str, Any] = field(default_factory=dict)
    output_summary: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class FailureModeSignal(Signal):
    """
    Señal que describe cómo falló una operación.
    
    Uso: Diagnóstico detallado de fallas.
    """
    
    signal_type: str = field(default="FailureModeSignal", init=False)
    
    # Payload específico
    execution_id: str = ""
    failure_mode: FailureMode = FailureMode.UNKNOWN
    
    error_message: str = ""
    error_code: str = ""
    stack_trace: str = ""
    
    recoverable: bool = False
    retry_count: int = 0
    max_retries: int = 3
    
    suggested_action: str = ""
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class LegacyActivitySignal(Signal):
    """
    Señal que registra actividad del sistema legacy.
    
    Uso: Observación pasiva del legacy sin intervenir (JF-0, JF-1).
    """
    
    signal_type:  str = field(default="LegacyActivitySignal", init=False)
    
    # Payload específico
    legacy_component: str = ""
    activity_type: str = ""  # "read", "write", "transform", "decision"
    
    input_captured: Dict[str, Any] = field(default_factory=dict)
    output_captured: Dict[str, Any] = field(default_factory=dict)
    
    # NO interpretamos, solo registramos
    raw_payload: str = ""
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL


@dataclass
class LegacyDependencySignal(Signal):
    """
    Señal que mapea dependencias del sistema legacy.
    
    Uso: Entender de qué depende el legacy antes de reemplazarlo.
    """
    
    signal_type: str = field(default="LegacyDependencySignal", init=False)
    
    # Payload específico
    legacy_component: str = ""
    
    upstream_dependencies: List[str] = field(default_factory=list)
    downstream_dependents: List[str] = field(default_factory=list)
    
    data_dependencies: List[str] = field(default_factory=list)
    service_dependencies: List[str] = field(default_factory=list)
    
    criticality:  str = ""  # "critical", "important", "optional"
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.OPERATIONAL
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/consumption.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


@dataclass
class FrequencySignal(Signal):
    """
    Señal que indica frecuencia de uso/acceso.
    
    Uso: Tracking de qué datos se usan más. 
    """
    
    signal_type: str = field(default="FrequencySignal", init=False)
    
    # Payload específico
    resource_id: str = ""  # Archivo, endpoint, señal
    resource_type: str = ""  # "canonical_file", "signal", "endpoint"
    
    access_count: int = 0
    period_start: str = ""
    period_end:  str = ""
    
    access_pattern: str = ""  # "bursty", "steady", "declining", "growing"
    peak_hour: int = 0  # 0-23
    
    consumers_accessing: List[str] = field(default_factory=list)
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. CONSUMPTION


@dataclass
class TemporalCouplingSignal(Signal):
    """
    Señal que indica acoplamiento temporal entre componentes.
    
    Uso: Detectar si dos componentes siempre se activan juntos.
    """
    
    signal_type: str = field(default="TemporalCouplingSignal", init=False)
    
    # Payload específico
    component_a: str = ""
    component_b: str = ""
    
    correlation_coefficient: float = 0.0  # -1 a 1
    coupling_strength: str = ""  # "strong", "moderate", "weak", "none"
    
    co_occurrence_count: int = 0
    observation_period_days: int = 0
    
    typical_lag_ms: float = 0.0  # Tiempo entre activación de A y B
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONSUMPTION


@dataclass
class ConsumerHealthSignal(Signal):
    """
    Señal que indica salud de un consumidor.
    
    Uso: Monitoreo de consumidores para detectar degradación.
    """
    
    signal_type: str = field(default="ConsumerHealthSignal", init=False)
    
    # Payload específico
    consumer_id: str = ""
    consumer_phase: str = ""
    
    signals_received: int = 0
    signals_processed: int = 0
    signals_failed: int = 0
    
    avg_processing_time_ms: float = 0.0
    error_rate: float = 0.0
    
    health_status: str = ""  # "healthy", "degraded", "unhealthy", "unknown"
    last_activity:  str = ""
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.CONSUMPTION
5. 6 VEHICLES: Base Vehicle y Implementaciones

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/base_vehicle.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from datetime import datetime

from .. core.signal import Signal, SignalContext, SignalSource
from ..core.event import Event, EventStore
from ..core.contracts import PublicationContract, ContractRegistry
from ..core.bus import BusRegistry, SignalBus


@dataclass
class VehicleCapabilities: 
    """Declaración de capacidades de un vehículo"""
    can_load:  bool = False          # Puede cargar datos canónicos
    can_scope: bool = False         # Puede aplicar scope/contexto
    can_extract: bool = False       # Puede extraer evidencia
    can_transform: bool = False     # Puede transformar datos
    can_enrich: bool = False        # Puede enriquecer con señales
    can_validate: bool = False      # Puede validar contratos
    can_irrigate: bool = False      # Puede ejecutar irrigación
    
    signal_types_produced: List[str] = field(default_factory=list)
    signal_types_consumed: List[str] = field(default_factory=list)


@dataclass
class BaseVehicle(ABC):
    """
    Clase base abstracta para todos los vehículos SISAS.
    
    Un vehículo es un componente que: 
    1. Carga datos canónicos
    2. Los transforma en eventos
    3. Genera señales a partir de eventos
    4. Publica señales en buses
    """
    
    vehicle_id: str
    vehicle_name: str
    
    # Capacidades
    capabilities: VehicleCapabilities = field(default_factory=VehicleCapabilities)
    
    # Contrato de publicación
    publication_contract: Optional[PublicationContract] = None
    
    # Registros
    event_store: EventStore = field(default_factory=EventStore)
    bus_registry: Optional[BusRegistry] = None
    contract_registry: Optional[ContractRegistry] = None
    
    # Estado
    is_active: bool = False
    last_activity: Optional[datetime] = None
    
    # Estadísticas
    stats: Dict[str, int] = field(default_factory=lambda: {
        "events_created": 0,
        "signals_generated": 0,
        "signals_published": 0,
        "errors":  0
    })
    
    @abstractmethod
    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa datos y genera señales.
        Cada vehículo implementa su lógica específica.
        """
        pass
    
    def create_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source_file: str,
        source_path: str,
        phase: str,
        consumer_scope: str
    ) -> Event:
        """Crea un evento y lo registra"""
        from ..core.event import Event, EventType, EventPayload
        
        event = Event(
            event_type=EventType(event_type) if event_type in [e.value for e in EventType] else EventType.CANONICAL_DATA_LOADED,
            source_file=source_file,
            source_path=source_path,
            payload=EventPayload(data=payload),
            phase=phase,
            consumer_scope=consumer_scope,
            source_component=self.vehicle_id
        )
        
        self.event_store.append(event)
        self.stats["events_created"] += 1
        self.last_activity = datetime.utcnow()
        
        return event
    
    def create_signal_source(self, event: Event) -> SignalSource:
        """Crea SignalSource a partir de un evento"""
        return SignalSource(
            event_id=event.event_id,
            source_file=event.source_file,
            source_path=event.source_path,
            generation_timestamp=datetime.utcnow(),
            generator_vehicle=self.vehicle_id
        )
    
    def publish_signal(self, signal: Signal) -> tuple[bool, str]:
        """Publica una señal en el bus apropiado"""
        if not self.bus_registry:
            return (False, "No bus registry configured")
        
        if not self.publication_contract:
            return (False, "No publication contract configured")
        
        success, result = self.bus_registry.publish_to_appropriate_bus(
            signal=signal,
            publisher_vehicle=self.vehicle_id,
            publication_contract=self. publication_contract
        )
        
        if success:
            self.stats["signals_published"] += 1
        else:
            self.stats["errors"] += 1
        
        return (success, result)
    
    def activate(self):
        """Activa el vehículo"""
        self. is_active = True
        self.last_activity = datetime.utcnow()
    
    def deactivate(self):
        """Desactiva el vehículo"""
        self. is_active = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del vehículo"""
        return {
            "vehicle_id": self.vehicle_id,
            "vehicle_name":  self.vehicle_name,
            "is_active": self.is_active,
            "last_activity":  self.last_activity. isoformat() if self.last_activity else None,
            "capabilities": {
                "can_load": self. capabilities.can_load,
                "can_scope": self.capabilities.can_scope,
                "can_extract": self.capabilities. can_extract,
                "signal_types_produced": self.capabilities.signal_types_produced
            },
            "stats": self.stats
        }
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_registry.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import os

from .base_vehicle import BaseVehicle, VehicleCapabilities
from .. core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..signals.types.structural import (
    StructuralAlignmentSignal, 
    AlignmentStatus,
    CanonicalMappingSignal
)
from ..signals.types.integrity import (
    EventPresenceSignal,
    PresenceStatus,
    EventCompletenessSignal,
    CompletenessLevel
)


@dataclass
class SignalRegistryVehicle(BaseVehicle):
    """
    Vehículo:  signal_registry
    
    Responsabilidad: Cargar archivos canónicos y generar señales
    de alineación estructural e integridad. 
    
    Archivos que procesa (del canonic central):
    - clusters/*/metadata.json, questions. json, aggregation_rules.json
    - dimensions/*/metadata.json, questions.json, pdet_context.json
    - policy_areas/*/metadata.json, questions. json, keywords.json
    - cross_cutting/*. json
    - scoring/*. json
    - governance/*.json
    """
    
    vehicle_id: str = field(default="signal_registry")
    vehicle_name: str = field(default="Signal Registry Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=True,
        can_scope=False,
        can_extract=False,
        can_transform=True,
        can_enrich=False,
        can_validate=True,
        can_irrigate=False,
        signal_types_produced=[
            "StructuralAlignmentSignal",
            "CanonicalMappingSignal",
            "EventPresenceSignal",
            "EventCompletenessSignal"
        ]
    ))
    
    # Esquemas esperados por tipo de archivo
    expected_schemas: Dict[str, List[str]] = field(default_factory=lambda: {
        "metadata.json": ["id", "name", "description", "version"],
        "questions.json": ["questions"],
        "aggregation_rules. json": ["rules", "weights"],
        "keywords.json": ["keywords"],
        "pdet_context.json": ["context", "municipalities"],
        "detection_rules.json": ["rules", "patterns"],
        "scoring_system.json": ["dimensions", "weights", "thresholds"],
        "governance. json": ["policies", "actors", "mechanisms"]
    })
    
    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa un archivo canónico y genera señales.
        """
        signals = []
        
        # Crear evento de carga
        event = self.create_event(
            event_type="canonical_data_loaded",
            payload={"keys": list(data.keys()), "size": len(json.dumps(data))},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # 1. Señal de alineación estructural
        alignment_signal = self._generate_alignment_signal(data, context, source)
        signals.append(alignment_signal)
        
        # 2. Señal de presencia de evento
        presence_signal = self._generate_presence_signal(data, context, source)
        signals.append(presence_signal)
        
        # 3. Señal de completitud
        completeness_signal = self._generate_completeness_signal(data, context, source)
        signals.append(completeness_signal)
        
        # 4. Señal de mapeo canónico (si aplica)
        if self._should_generate_mapping_signal(context):
            mapping_signal = self._generate_mapping_signal(data, context, source)
            signals.append(mapping_signal)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _generate_alignment_signal(
        self, 
        data: Dict[str, Any], 
        context: SignalContext,
        source: SignalSource
    ) -> StructuralAlignmentSignal:
        """Genera señal de alineación estructural"""
        
        # Determinar esquema esperado
        file_type = context.node_id.split("/")[-1] if "/" in context.node_id else context.node_id
        expected_fields = self.expected_schemas.get(file_type, [])
        
        actual_fields = list(data.keys())
        missing = [f for f in expected_fields if f not in actual_fields]
        extra = [f for f in actual_fields if f not in expected_fields and expected_fields]
        
        # Determinar estado
        if not missing and not extra:
            status = AlignmentStatus.ALIGNED
            confidence = SignalConfidence.HIGH
        elif not missing: 
            status = AlignmentStatus.ALIGNED
            confidence = SignalConfidence.MEDIUM
        elif len(missing) < len(expected_fields) / 2:
            status = AlignmentStatus.PARTIAL
            confidence = SignalConfidence. MEDIUM
        else:
            status = AlignmentStatus.MISALIGNED
            confidence = SignalConfidence.HIGH
        
        return StructuralAlignmentSignal(
            context=context,
            source=source,
            alignment_status=status,
            canonical_path=f"{context.node_type}/{context.node_id}",
            actual_path=source.source_path,
            missing_elements=missing,
            extra_elements=extra,
            confidence=confidence,
            rationale=f"Alignment check:  {len(missing)} missing, {len(extra)} extra fields"
        )
    
    def _generate_presence_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EventPresenceSignal:
        """Genera señal de presencia"""
        
        has_content = bool(data) and any(
            v is not None and v != [] and v != {} 
            for v in data.values()
        )
        
        return EventPresenceSignal(
            context=context,
            source=source,
            expected_event_type="canonical_data_loaded",
            presence_status=PresenceStatus. PRESENT if has_content else PresenceStatus.PARTIAL,
            event_count=1,
            confidence=SignalConfidence.HIGH,
            rationale=f"Data {'present' if has_content else 'empty or partial'}"
        )
    
    def _generate_completeness_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EventCompletenessSignal:
        """Genera señal de completitud"""
        
        file_type = context.node_id.split("/")[-1] if "/" in context.node_id else context.node_id
        required = self.expected_schemas.get(file_type, [])
        present = [f for f in required if f in data and data[f]]
        
        if not required: 
            level = CompletenessLevel. COMPLETE
            score = 1.0
        elif len(present) == len(required):
            level = CompletenessLevel.COMPLETE
            score = 1.0
        elif len(present) >= len(required) * 0.75:
            level = CompletenessLevel.MOSTLY_COMPLETE
            score = len(present) / len(required)
        elif len(present) > 0:
            level = CompletenessLevel.INCOMPLETE
            score = len(present) / len(required)
        else:
            level = CompletenessLevel.EMPTY
            score = 0.0
        
        return EventCompletenessSignal(
            context=context,
            source=source,
            completeness_level=level,
            required_fields=required,
            present_fields=present,
            completeness_score=score,
            confidence=SignalConfidence.HIGH,
            rationale=f"Completeness:  {len(present)}/{len(required)} required fields present"
        )
    
    def _should_generate_mapping_signal(self, context: SignalContext) -> bool:
        """Determina si debe generar señal de mapeo"""
        return context.node_type in ["question", "policy_area", "dimension", "cluster"]
    
    def _generate_mapping_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> CanonicalMappingSignal: 
        """Genera señal de mapeo canónico"""
        
        mapped = {}
        unmapped = []
        
        # Intentar extraer mapeos del contenido
        if "policy_area" in data:
            mapped["policy_area"] = data["policy_area"]
        elif "PA" in context.node_id:
            mapped["policy_area"] = context.node_id
        else:
            unmapped.append("policy_area")
        
        if "dimension" in data: 
            mapped["dimension"] = data["dimension"]
        elif "DIM" in context.node_id:
            mapped["dimension"] = context.node_id
        else:
            unmapped.append("dimension")
        
        if "cluster" in data:
            mapped["cluster"] = data["cluster"]
        elif "CL" in context.node_id:
            mapped["cluster"] = context.node_id
        
        completeness = len(mapped) / (len(mapped) + len(unmapped)) if (mapped or unmapped) else 1.0
        
        return CanonicalMappingSignal(
            context=context,
            source=source,
            source_item_id=context.node_id,
            mapped_entities=mapped,
            unmapped_aspects=unmapped,
            mapping_completeness=completeness,
            confidence=SignalConfidence. MEDIUM if unmapped else SignalConfidence.HIGH,
            rationale=f"Mapped {len(mapped)} entities, {len(unmapped)} unmapped"
        )
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_context_scoper.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from .. signals.types.structural import CanonicalMappingSignal
from ..signals.types.epistemic import (
    AnswerDeterminacySignal,
    DeterminacyLevel,
    AnswerSpecificitySignal,
    SpecificityLevel
)


@dataclass
class SignalContextScoperVehicle(BaseVehicle):
    """
    Vehículo: signal_context_scoper
    
    Responsabilidad: Aplicar contexto y scope a los datos,
    determinando a qué nodos pertenecen y qué señales deben generarse.
    
    Archivos que procesa: 
    - dimensions/*/questions/*. json (preguntas individuales)
    - _registry/questions/*. json
    - _registry/patterns/*.json
    """
    
    vehicle_id:  str = field(default="signal_context_scoper")
    vehicle_name: str = field(default="Signal Context Scoper Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=True,
        can_extract=True,
        can_transform=True,
        can_enrich=False,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=[
            "CanonicalMappingSignal",
            "AnswerDeterminacySignal",
            "AnswerSpecificitySignal"
        ]
    ))
    
    # Marcadores para análisis epistémico
    affirmative_markers: List[str] = field(default_factory=lambda:  [
        "sí", "si", "existe", "cuenta con", "dispone de", "tiene",
        "se realiza", "se implementa", "está vigente", "opera"
    ])
    
    ambiguity_markers: List[str] = field(default_factory=lambda: [
        "algunos", "ciertos", "parcialmente", "a veces", "en ocasiones",
        "dependiendo", "cuando sea posible", "según el caso"
    ])
    
    negation_markers: List[str] = field(default_factory=lambda: [
        "no", "nunca", "ninguno", "ninguna", "sin", "carece",
        "no existe", "no cuenta", "no dispone", "no tiene"
    ])
    
    specificity_elements: List[str] = field(default_factory=lambda: [
        "ley", "decreto", "resolución", "acuerdo", "ordenanza",
        "ministerio", "secretaría", "dirección", "unidad",
        "presupuesto", "recursos", "asignación"
    ])
    
    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """Procesa datos aplicando scope y contexto"""
        signals = []
        
        event = self.create_event(
            event_type="canonical_data_validated",
            payload=data,
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context. phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self. create_signal_source(event)
        
        # Si es una pregunta, aplicar análisis epistémico
        if context.node_type == "question" or "question" in str(data. get("type", "")):
            answer_text = data.get("answer", data.get("response", ""))
            
            if answer_text:
                # Señal de determinismo
                determinacy = self._analyze_determinacy(answer_text, context, source)
                signals. append(determinacy)
                
                # Señal de especificidad
                specificity = self._analyze_specificity(answer_text, data, context, source)
                signals.append(specificity)
        
        # Generar mapeo canónico basado en contexto
        mapping = self._generate_context_mapping(data, context, source)
        signals.append(mapping)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _analyze_determinacy(
        self,
        text: str,
        context: SignalContext,
        source: SignalSource
    ) -> AnswerDeterminacySignal:
        """Analiza determinismo de una respuesta"""
        
        text_lower = text.lower()
        
        found_affirmative = [m for m in self.affirmative_markers if m in text_lower]
        found_ambiguity = [m for m in self.ambiguity_markers if m in text_lower]
        found_negation = [m for m in self.negation_markers if m in text_lower]
        
        # Determinar nivel
        if found_negation and not found_affirmative: 
            level = DeterminacyLevel.HIGH  # Negación clara
            rationale = "Clear negative statement"
        elif found_affirmative and not found_ambiguity and not found_negation:
            level = DeterminacyLevel.HIGH  # Afirmación clara
            rationale = "Clear affirmative statement"
        elif found_affirmative and found_ambiguity: 
            level = DeterminacyLevel.MEDIUM  # Afirmación con ambigüedad
            rationale = "Affirmative with scope ambiguity"
        elif found_ambiguity: 
            level = DeterminacyLevel.LOW
            rationale = "High ambiguity detected"
        else:
            level = DeterminacyLevel.INDETERMINATE
            rationale = "Cannot determine stance"
        
        return AnswerDeterminacySignal(
            context=context,
            source=source,
            question_id=context.node_id,
            determinacy_level=level,
            affirmative_markers=found_affirmative,
            ambiguity_markers=found_ambiguity,
            negation_markers=found_negation,
            confidence=SignalConfidence. MEDIUM,
            rationale=rationale
        )
    
    def _analyze_specificity(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> AnswerSpecificitySignal: 
        """Analiza especificidad de una respuesta"""
        
        text_lower = text.lower()
        
        expected = ["formal_instrument", "institutional_owner", "mandatory_scope", "budget_allocation"]
        found = []
        
        # Buscar elementos de especificidad
        if any(m in text_lower for m in ["ley", "decreto", "resolución", "acuerdo"]):
            found.append("formal_instrument")
        
        if any(m in text_lower for m in ["ministerio", "secretaría", "dirección", "unidad", "entidad"]):
            found.append("institutional_owner")
        
        if any(m in text_lower for m in ["obligatorio", "debe", "deberá", "exige"]):
            found.append("mandatory_scope")
        
        if any(m in text_lower for m in ["presupuesto", "recursos", "millones", "asignación"]):
            found. append("budget_allocation")
        
        missing = [e for e in expected if e not in found]
        
        if len(found) >= 3:
            level = SpecificityLevel.HIGH
        elif len(found) >= 2:
            level = SpecificityLevel.MEDIUM
        elif len(found) >= 1:
            level = SpecificityLevel.LOW
        else:
            level = SpecificityLevel.NONE
        
        score = len(found) / len(expected) if expected else 0.0
        
        return AnswerSpecificitySignal(
            context=context,
            source=source,
            question_id=context.node_id,
            specificity_level=level,
            expected_elements=expected,
            found_elements=found,
            missing_elements=missing,
            specificity_score=score,
            confidence=SignalConfidence. MEDIUM,
            rationale=f"Found {len(found)}/{len(expected)} specificity elements"
        )
    
    def _generate_context_mapping(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> CanonicalMappingSignal:
        """Genera mapeo basado en contexto inferido"""
        
        mapped = {}
        
        # Inferir de context
        if "PA" in context.node_id:
            pa_match = [p for p in ["PA01", "PA02", "PA03", "PA04", "PA05", 
                                     "PA06", "PA07", "PA08", "PA09", "PA10"]
                       if p in context.node_id]
            if pa_match: 
                mapped["policy_area"] = pa_match[0]
        
        if "DIM" in context.node_id:
            dim_match = [d for d in ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]
                        if d in context. node_id]
            if dim_match:
                mapped["dimension"] = dim_match[0]
        
        if "CL" in context.node_id:
            cl_match = [c for c in ["CL01", "CL02", "CL03", "CL04"]
                       if c in context.node_id]
            if cl_match: 
                mapped["cluster"] = cl_match[0]
        
        # Inferir de data
        if "policy_area" in data:
            mapped["policy_area"] = data["policy_area"]
        if "dimension" in data:
            mapped["dimension"] = data["dimension"]
        
        return CanonicalMappingSignal(
            context=context,
            source=source,
            source_item_id=context. node_id,
            mapped_entities=mapped,
            unmapped_aspects=[],
            mapping_completeness=1.0 if mapped else 0.0,
            confidence=SignalConfidence.HIGH if mapped else SignalConfidence.LOW,
            rationale=f"Context-based mapping: {list(mapped.keys())}"
        )
5.7 IRRIGATION: Mapa y Ejecutor

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_map.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class IrrigabilityStatus(Enum):
    """Estados de irrigabilidad"""
    IRRIGABLE_NOW = "irrigable_now"
    NOT_IRRIGABLE_YET = "not_irrigable_yet"
    DEFINITELY_NOT = "definitely_not"


@dataclass
class IrrigationTarget:
    """Destino de irrigación"""
    consumer_id: str
    consumer_phase: str
    required_signals: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)


@dataclass
class IrrigationSource:
    """Fuente de irrigación"""
    file_path: str
    stage: str
    phase: str
    vehicles: List[str] = field(default_factory=list)
    consumers: List[str] = field(default_factory=list)
    irrigability:  IrrigabilityStatus = IrrigabilityStatus.DEFINITELY_NOT
    gaps: List[str] = field(default_factory=list)
    added_value: str = "MARGINAL"
    file_bytes: int = 0


@dataclass
class IrrigationRoute:
    """Ruta completa de irrigación:  archivo → vehículos → señales → consumidores"""
    source: IrrigationSource
    vehicles: List[str] = field(default_factory=list)
    signals_generated: List[str] = field(default_factory=list)
    targets: List[IrrigationTarget] = field(default_factory=list)
    is_active: bool = False


@dataclass
class IrrigationMap:
    """
    Mapa completo de irrigación del sistema. 
    Define quién produce qué, para quién, a través de qué vehículos. 
    """
    
    routes: Dict[str, IrrigationRoute] = field(default_factory=dict)
    
    # Índices para búsqueda rápida
    _by_phase: Dict[str, List[str]] = field(default_factory=dict)
    _by_vehicle: Dict[str, List[str]] = field(default_factory=dict)
    _by_consumer: Dict[str, List[str]] = field(default_factory=dict)
    _by_irrigability: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_route(self, route:  IrrigationRoute):
        """Añade una ruta al mapa"""
        route_id = route.source.file_path
        self.routes[route_id] = route
        
        # Indexar por fase
        phase = route.source.phase
        if phase not in self._by_phase:
            self._by_phase[phase] = []
        self._by_phase[phase].append(route_id)
        
        # Indexar por vehículo
        
You said: CONTINUA
CONTINUA

Copilot said: ### 5.7 IRRIGATION: Mapa y Ejecutor
5.7 IRRIGATION: Mapa y Ejecutor (Continuación)

Python
        # Indexar por vehículo
        for vehicle in route.vehicles:
            if vehicle not in self._by_vehicle:
                self._by_vehicle[vehicle] = []
            self._by_vehicle[vehicle].append(route_id)
        
        # Indexar por consumidor
        for target in route.targets:
            if target.consumer_id not in self._by_consumer:
                self._by_consumer[target.consumer_id] = []
            self._by_consumer[target.consumer_id].append(route_id)
        
        # Indexar por irrigabilidad
        status = route.source.irrigability. value
        if status not in self._by_irrigability:
            self._by_irrigability[status] = []
        self._by_irrigability[status].append(route_id)
    
    def get_routes_for_phase(self, phase: str) -> List[IrrigationRoute]:
        """Obtiene rutas por fase"""
        route_ids = self._by_phase.get(phase, [])
        return [self.routes[rid] for rid in route_ids]
    
    def get_routes_for_vehicle(self, vehicle: str) -> List[IrrigationRoute]:
        """Obtiene rutas que usan un vehículo específico"""
        route_ids = self._by_vehicle.get(vehicle, [])
        return [self.routes[rid] for rid in route_ids]
    
    def get_routes_for_consumer(self, consumer:  str) -> List[IrrigationRoute]:
        """Obtiene rutas que alimentan a un consumidor"""
        route_ids = self._by_consumer.get(consumer, [])
        return [self. routes[rid] for rid in route_ids]
    
    def get_irrigable_now(self) -> List[IrrigationRoute]:
        """Obtiene rutas que pueden irrigar ahora"""
        route_ids = self._by_irrigability.get("irrigable_now", [])
        return [self.routes[rid] for rid in route_ids]
    
    def get_blocked_routes(self) -> List[tuple[IrrigationRoute, List[str]]]:
        """Obtiene rutas bloqueadas con sus gaps"""
        blocked = []
        for status in ["not_irrigable_yet", "definitely_not"]:
            route_ids = self._by_irrigability.get(status, [])
            for rid in route_ids:
                route = self.routes[rid]
                blocked.append((route, route.source.gaps))
        return blocked
    
    def get_statistics(self) -> Dict[str, Any]:
        """Estadísticas del mapa de irrigación"""
        total = len(self.routes)
        irrigable = len(self._by_irrigability. get("irrigable_now", []))
        not_yet = len(self._by_irrigability.get("not_irrigable_yet", []))
        definitely_not = len(self._by_irrigability.get("definitely_not", []))
        
        # Contar gaps
        all_gaps = []
        for route in self.routes.values():
            all_gaps.extend(route. source.gaps)
        
        gap_counts = {}
        for gap in all_gaps:
            gap_counts[gap] = gap_counts.get(gap, 0) + 1
        
        return {
            "total_routes": total,
            "irrigable_now": irrigable,
            "not_irrigable_yet":  not_yet,
            "definitely_not": definitely_not,
            "irrigable_percentage": (irrigable / total * 100) if total > 0 else 0,
            "phases":  list(self._by_phase. keys()),
            "vehicles_in_use": list(self._by_vehicle.keys()),
            "consumers_registered": list(self._by_consumer.keys()),
            "gap_summary": gap_counts
        }
    
    @classmethod
    def from_sabana_csv(cls, csv_data: List[Dict[str, Any]]) -> 'IrrigationMap': 
        """
        Construye el mapa desde el CSV de decisiones (sabana_final_decisiones.csv)
        """
        irrigation_map = cls()
        
        for row in csv_data:
            # Filtrar solo items del canonic central (no MARGINAL, no External)
            if row.get("added_value") == "MARGINAL": 
                continue
            if row.get("stage") == "External":
                continue
            
            # Crear source
            source = IrrigationSource(
                file_path=row. get("json_file_path", ""),
                stage=row. get("stage", ""),
                phase=row.get("phase", ""),
                vehicles=cls._parse_list(row.get("vehiculos_str", "NINGUNO")),
                consumers=cls._parse_list(row.get("consumidores_str", "NINGUNO")),
                irrigability=cls._parse_irrigability(row.get("irrigability_bucket", "")),
                gaps=cls._parse_list(row.get("gaps_str", "NINGUNO")),
                added_value=row.get("added_value", ""),
                file_bytes=int(row.get("file_bytes", 0))
            )
            
            # Crear targets
            targets = []
            for consumer in source.consumers:
                if consumer != "NINGUNO":
                    targets.append(IrrigationTarget(
                        consumer_id=consumer,
                        consumer_phase=source.phase
                    ))
            
            # Crear ruta
            route = IrrigationRoute(
                source=source,
                vehicles=[v for v in source.vehicles if v != "NINGUNO"],
                signals_generated=[],  # Se llenará al procesar
                targets=targets,
                is_active=source.irrigability == IrrigabilityStatus.IRRIGABLE_NOW
            )
            
            irrigation_map.add_route(route)
        
        return irrigation_map
    
    @staticmethod
    def _parse_list(value: str) -> List[str]:
        """Parsea lista separada por comas"""
        if not value or value == "NINGUNO": 
            return []
        return [v.strip() for v in value.split(",") if v.strip()]
    
    @staticmethod
    def _parse_irrigability(value: str) -> IrrigabilityStatus:
        """Parsea estado de irrigabilidad"""
        mapping = {
            "irrigable_now": IrrigabilityStatus.IRRIGABLE_NOW,
            "not_irrigable_yet": IrrigabilityStatus. NOT_IRRIGABLE_YET,
            "definitely_not":  IrrigabilityStatus. DEFINITELY_NOT
        }
        return mapping.get(value, IrrigabilityStatus.DEFINITELY_NOT)
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_executor.py

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json
import logging

from . irrigation_map import IrrigationMap, IrrigationRoute, IrrigabilityStatus
from .. core.signal import Signal, SignalContext
from ..core.event import Event, EventStore, EventType
from ..core.contracts import IrrigationContract, ContractRegistry, ContractStatus
from ..core.bus import BusRegistry
from ..vehicles.base_vehicle import BaseVehicle
from ..signals.types. operational import ExecutionAttemptSignal, ExecutionStatus, FailureModeSignal, FailureMode


class IrrigationPhase(Enum):
    """Fases de la irrigación según JF (Job Fronts)"""
    JF0_CONTAINMENT = "JF0"      # Contención del legacy
    JF1_OBSERVATION = "JF1"      # Observación pasiva
    JF2_EXTRACTION = "JF2"       # Extracción empírica
    JF3_CANONIZATION = "JF3"     # Canonización estructural
    JF4_INSTRUMENTATION = "JF4"  # Instrumentación de eventos
    JF5_SIGNAL_GEN = "JF5"       # Generación de señales (NÚCLEO SISAS)
    JF6_BUS_CONTRACTS = "JF6"    # Buses y contratos
    JF7_CONSUMERS = "JF7"        # Consumidores analíticos
    JF8_CONTRAST = "JF8"         # Contraste legacy vs nuevo
    JF9_SUBSTITUTION = "JF9"     # Sustitución controlada
    JF10_AUDIT = "JF10"          # Auditoría continua


@dataclass
class IrrigationResult:
    """Resultado de una irrigación"""
    route_id: str
    success: bool
    signals_generated: List[Signal] = field(default_factory=list)
    signals_published: int = 0
    consumers_notified: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IrrigationExecutor:
    """
    Ejecutor de irrigación. 
    
    Responsabilidades:
    1. Cargar datos canónicos
    2. Pasarlos por vehículos apropiados
    3. Generar señales
    4. Publicar en buses
    5. Notificar a consumidores
    6. Registrar todo para auditoría
    """
    
    irrigation_map: IrrigationMap = field(default_factory=IrrigationMap)
    bus_registry: BusRegistry = field(default_factory=BusRegistry)
    contract_registry: ContractRegistry = field(default_factory=ContractRegistry)
    event_store: EventStore = field(default_factory=EventStore)
    
    # Vehículos registrados
    vehicles: Dict[str, BaseVehicle] = field(default_factory=dict)
    
    # Loaders de archivos
    file_loaders:  Dict[str, Callable] = field(default_factory=dict)
    
    # Estado
    current_phase: IrrigationPhase = IrrigationPhase.JF0_CONTAINMENT
    is_running: bool = False
    
    # Resultados
    execution_history: List[IrrigationResult] = field(default_factory=list)
    
    # Logger
    _logger: logging.Logger = field(default=None)
    
    def __post_init__(self):
        if self._logger is None:
            self._logger = logging.getLogger("SISAS.IrrigationExecutor")
        
        # Registrar loader por defecto para JSON
        self.file_loaders["json"] = self._load_json_file
    
    def register_vehicle(self, vehicle: BaseVehicle):
        """Registra un vehículo"""
        self.vehicles[vehicle. vehicle_id] = vehicle
        vehicle.bus_registry = self.bus_registry
        vehicle.contract_registry = self.contract_registry
        self._logger.info(f"Vehicle registered: {vehicle.vehicle_id}")
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Carga un archivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def execute_route(self, route: IrrigationRoute, base_path: str = "") -> IrrigationResult: 
        """
        Ejecuta una ruta de irrigación completa. 
        """
        start_time = datetime.utcnow()
        result = IrrigationResult(route_id=route.source.file_path, success=False)
        
        try: 
            # 1. Verificar que la ruta es irrigable
            if route.source.irrigability != IrrigabilityStatus. IRRIGABLE_NOW:
                result.errors.append(f"Route not irrigable: {route.source. gaps}")
                return result
            
            # 2. Verificar vehículos disponibles
            missing_vehicles = [v for v in route.vehicles if v not in self.vehicles]
            if missing_vehicles: 
                result.errors.append(f"Missing vehicles: {missing_vehicles}")
                return result
            
            # 3. Cargar archivo canónico
            file_path = f"{base_path}/{route.source.file_path}" if base_path else route.source.file_path
            
            try:
                data = self._load_json_file(file_path)
            except Exception as e:
                result.errors.append(f"Failed to load file: {str(e)}")
                return result
            
            # 4. Crear contexto
            context = SignalContext(
                node_type=self._infer_node_type(route.source.file_path),
                node_id=route.source.file_path,
                phase=route.source.phase,
                consumer_scope=route.source.stage
            )
            
            # 5. Registrar evento de carga
            load_event = Event(
                event_type=EventType.CANONICAL_DATA_LOADED,
                source_file=route.source.file_path,
                source_path=file_path,
                phase=route.source.phase,
                consumer_scope=route.source.stage,
                source_component="irrigation_executor"
            )
            self.event_store.append(load_event)
            
            # 6. Procesar con cada vehículo
            all_signals = []
            
            for vehicle_id in route.vehicles:
                vehicle = self.vehicles[vehicle_id]
                
                try:
                    signals = vehicle.process(data, context)
                    all_signals.extend(signals)
                    self._logger.debug(
                        f"Vehicle {vehicle_id} generated {len(signals)} signals"
                    )
                except Exception as e:
                    result.errors.append(f"Vehicle {vehicle_id} error: {str(e)}")
                    # Generar señal de falla
                    failure_signal = self._create_failure_signal(
                        vehicle_id, str(e), context
                    )
                    all_signals.append(failure_signal)
            
            result.signals_generated = all_signals
            
            # 7. Publicar señales en buses
            for signal in all_signals:
                for vehicle_id in route.vehicles:
                    vehicle = self.vehicles[vehicle_id]
                    if vehicle.publication_contract:
                        success, msg = vehicle.publish_signal(signal)
                        if success:
                            result.signals_published += 1
                        else:
                            self._logger.warning(f"Failed to publish:  {msg}")
            
            # 8. Notificar consumidores
            for target in route.targets:
                result.consumers_notified.append(target.consumer_id)
                self._logger.info(f"Consumer notified: {target.consumer_id}")
            
            # 9. Registrar evento de irrigación completada
            complete_event = Event(
                event_type=EventType.IRRIGATION_COMPLETED,
                source_file=route.source.file_path,
                phase=route.source.phase,
                source_component="irrigation_executor"
            )
            self.event_store.append(complete_event)
            
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Execution error: {str(e)}")
            self._logger.error(f"Irrigation failed for {route.source.file_path}:  {e}")
        
        finally:
            end_time = datetime.utcnow()
            result.duration_ms = (end_time - start_time).total_seconds() * 1000
            result.timestamp = end_time
            self.execution_history.append(result)
        
        return result
    
    def execute_phase(self, phase: str, base_path: str = "") -> List[IrrigationResult]: 
        """
        Ejecuta todas las rutas de una fase. 
        """
        results = []
        routes = self.irrigation_map.get_routes_for_phase(phase)
        
        self._logger.info(f"Executing phase {phase}:  {len(routes)} routes")
        
        for route in routes: 
            if route.source.irrigability == IrrigabilityStatus. IRRIGABLE_NOW:
                result = self.execute_route(route, base_path)
                results.append(result)
        
        return results
    
    def execute_all_irrigable(self, base_path: str = "") -> List[IrrigationResult]: 
        """
        Ejecuta todas las rutas irrigables ahora.
        """
        results = []
        routes = self.irrigation_map.get_irrigable_now()
        
        self._logger.info(f"Executing all irrigable routes: {len(routes)}")
        
        for route in routes:
            result = self. execute_route(route, base_path)
            results.append(result)
        
        return results
    
    def _infer_node_type(self, file_path: str) -> str:
        """Infiere el tipo de nodo desde el path"""
        path_lower = file_path.lower()
        
        if "question" in path_lower:
            return "question"
        elif "policy_area" in path_lower or "/pa" in path_lower:
            return "policy_area"
        elif "dimension" in path_lower or "/dim" in path_lower: 
            return "dimension"
        elif "cluster" in path_lower or "/cl" in path_lower:
            return "cluster"
        elif "pattern" in path_lower: 
            return "pattern"
        elif "cross_cutting" in path_lower:
            return "cross_cutting"
        elif "_registry" in path_lower:
            return "registry"
        else: 
            return "canonical_file"
    
    def _create_failure_signal(
        self, 
        vehicle_id: str, 
        error:  str, 
        context: SignalContext
    ) -> FailureModeSignal: 
        """Crea señal de falla"""
        from ..core.signal import SignalSource
        
        source = SignalSource(
            event_id="",
            source_file=context.node_id,
            source_path=context.node_id,
            generation_timestamp=datetime.utcnow(),
            generator_vehicle="irrigation_executor"
        )
        
        return FailureModeSignal(
            context=context,
            source=source,
            execution_id=f"{vehicle_id}_{context.node_id}",
            failure_mode=FailureMode. TRANSFORMATION_ERROR,
            error_message=error,
            recoverable=True
        )
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Resumen de ejecuciones"""
        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r. success)
        failed = total - successful
        
        total_signals = sum(len(r.signals_generated) for r in self.execution_history)
        total_published = sum(r.signals_published for r in self.execution_history)
        
        avg_duration = (
            sum(r.duration_ms for r in self.execution_history) / total
            if total > 0 else 0
        )
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "total_signals_generated": total_signals,
            "total_signals_published": total_published,
            "avg_duration_ms": avg_duration,
            "current_phase": self.current_phase.value
        }
5.8 VOCABULARY: Alineación de Vocabularios

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vocabulary/signal_vocabulary.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum


@dataclass
class SignalTypeDefinition:
    """Definición canónica de un tipo de señal"""
    signal_type: str
    category: str
    description: str
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    value_type: str = "any"  # "enum", "float", "string", "dict"
    value_constraints: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"


@dataclass
class SignalVocabulary:
    """
    Vocabulario canónico de señales.
    Define todos los tipos de señales válidos en el sistema.
    """
    
    definitions: Dict[str, SignalTypeDefinition] = field(default_factory=dict)
    
    def __post_init__(self):
        # Registrar tipos de señales del sistema
        self._register_structural_signals()
        self._register_integrity_signals()
        self._register_epistemic_signals()
        self._register_contrast_signals()
        self._register_operational_signals()
        self._register_consumption_signals()
    
    def _register_structural_signals(self):
        """Registra señales estructurales"""
        self.register(SignalTypeDefinition(
            signal_type="StructuralAlignmentSignal",
            category="structural",
            description="Indica si un dato mapea correctamente a la estructura canónica",
            required_fields=["alignment_status", "canonical_path"],
            optional_fields=["missing_elements", "extra_elements"],
            value_type="enum",
            value_constraints={"values": ["ALIGNED", "PARTIAL", "MISALIGNED", "UNKNOWN"]}
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="SchemaConflictSignal",
            category="structural",
            description="Indica conflicto de esquemas entre datos",
            required_fields=["expected_schema_version", "actual_schema_version", "conflict_type"],
            optional_fields=["conflicting_fields", "is_breaking"]
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="CanonicalMappingSignal",
            category="structural",
            description="Resultado de mapear un ítem a entidades canónicas",
            required_fields=["source_item_id", "mapped_entities"],
            optional_fields=["unmapped_aspects", "mapping_completeness"]
        ))
    
    def _register_integrity_signals(self):
        """Registra señales de integridad"""
        self.register(SignalTypeDefinition(
            signal_type="EventPresenceSignal",
            category="integrity",
            description="Indica si un evento esperado existe",
            required_fields=["expected_event_type", "presence_status"],
            optional_fields=["event_count", "first_occurrence", "last_occurrence"],
            value_type="enum",
            value_constraints={"values": ["PRESENT", "ABSENT", "PARTIAL"]}
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="EventCompletenessSignal",
            category="integrity",
            description="Indica qué tan completo es un evento",
            required_fields=["completeness_level", "required_fields", "present_fields"],
            optional_fields=["missing_fields", "completeness_score"],
            value_type="enum",
            value_constraints={"values": ["COMPLETE", "MOSTLY_COMPLETE", "INCOMPLETE", "EMPTY"]}
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="DataIntegritySignal",
            category="integrity",
            description="Indica la integridad referencial de los datos",
            required_fields=["source_file", "referenced_files"],
            optional_fields=["valid_references", "broken_references", "integrity_score"]
        ))
    
    def _register_epistemic_signals(self):
        """Registra señales epistémicas"""
        self.register(SignalTypeDefinition(
            signal_type="AnswerDeterminacySignal",
            category="epistemic",
            description="Evalúa qué tan determinante es una respuesta",
            required_fields=["question_id", "determinacy_level"],
            optional_fields=["affirmative_markers", "ambiguity_markers", "negation_markers"],
            value_type="enum",
            value_constraints={"values": ["HIGH", "MEDIUM", "LOW", "INDETERMINATE"]}
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="AnswerSpecificitySignal",
            category="epistemic",
            description="Evalúa qué tan específica es una respuesta",
            required_fields=["question_id", "specificity_level"],
            optional_fields=["expected_elements", "found_elements", "missing_elements"],
            value_type="enum",
            value_constraints={"values": ["HIGH", "MEDIUM", "LOW", "NONE"]}
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="EmpiricalSupportSignal",
            category="epistemic",
            description="Evalúa el soporte empírico/documental de una respuesta",
            required_fields=["question_id", "support_level"],
            optional_fields=["normative_references", "document_references", "institutional_references"],
            value_type="enum",
            value_constraints={"values": ["STRONG", "MODERATE", "WEAK", "NONE"]}
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="MethodApplicationSignal",
            category="epistemic",
            description="Resultado de aplicar un método de evaluación",
            required_fields=["question_id", "method_id", "method_result"],
            optional_fields=["extraction_successful", "extracted_values", "processing_time_ms"]
        ))
    
    def _register_contrast_signals(self):
        """Registra señales de contraste"""
        self.register(SignalTypeDefinition(
            signal_type="DecisionDivergenceSignal",
            category="contrast",
            description="Indica divergencia entre sistema legacy y nuevo",
            required_fields=["item_id", "legacy_value", "signal_based_value"],
            optional_fields=["divergence_type", "divergence_severity", "divergence_explanation"]
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="ConfidenceDropSignal",
            category="contrast",
            description="Indica caída de confianza en una evaluación",
            required_fields=["item_id", "previous_confidence", "current_confidence"],
            optional_fields=["drop_percentage", "contributing_factors", "trend"]
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="TemporalContrastSignal",
            category="contrast",
            description="Indica cambios entre evaluaciones en diferentes momentos",
            required_fields=["item_id", "baseline_timestamp", "current_timestamp"],
            optional_fields=["baseline_state", "current_state", "changes_detected"]
        ))
    
    def _register_operational_signals(self):
        """Registra señales operacionales"""
        self.register(SignalTypeDefinition(
            signal_type="ExecutionAttemptSignal",
            category="operational",
            description="Registra un intento de ejecución",
            required_fields=["execution_id", "component", "operation", "status"],
            optional_fields=["started_at", "completed_at", "duration_ms"]
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="FailureModeSignal",
            category="operational",
            description="Describe cómo falló una operación",
            required_fields=["execution_id", "failure_mode", "error_message"],
            optional_fields=["error_code", "stack_trace", "recoverable"]
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="LegacyActivitySignal",
            category="operational",
            description="Registra actividad del sistema legacy",
            required_fields=["legacy_component", "activity_type"],
            optional_fields=["input_captured", "output_captured", "raw_payload"]
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="LegacyDependencySignal",
            category="operational",
            description="Mapea dependencias del sistema legacy",
            required_fields=["legacy_component"],
            optional_fields=["upstream_dependencies", "downstream_dependents", "criticality"]
        ))
    
    def _register_consumption_signals(self):
        """Registra señales de consumo"""
        self.register(SignalTypeDefinition(
            signal_type="FrequencySignal",
            category="consumption",
            description="Indica frecuencia de uso/acceso",
            required_fields=["resource_id", "resource_type", "access_count"],
            optional_fields=["period_start", "period_end", "access_pattern"]
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="TemporalCouplingSignal",
            category="consumption",
            description="Indica acoplamiento temporal entre componentes",
            required_fields=["component_a", "component_b", "correlation_coefficient"],
            optional_fields=["coupling_strength", "co_occurrence_count"]
        ))
        
        self.register(SignalTypeDefinition(
            signal_type="ConsumerHealthSignal",
            category="consumption",
            description="Indica salud de un consumidor",
            required_fields=["consumer_id", "health_status"],
            optional_fields=["signals_received", "signals_processed", "error_rate"]
        ))
    
    def register(self, definition: SignalTypeDefinition):
        """Registra una definición de tipo de señal"""
        self. definitions[definition.signal_type] = definition
    
    def get(self, signal_type: str) -> Optional[SignalTypeDefinition]:
        """Obtiene definición de un tipo de señal"""
        return self.definitions.get(signal_type)
    
    def is_valid_type(self, signal_type: str) -> bool:
        """Verifica si un tipo de señal es válido"""
        return signal_type in self.definitions
    
    def get_by_category(self, category: str) -> List[SignalTypeDefinition]:
        """Obtiene tipos de señal por categoría"""
        return [d for d in self.definitions. values() if d.category == category]
    
    def validate_signal(self, signal:  Any) -> tuple[bool, List[str]]:
        """
        Valida una señal contra el vocabulario. 
        Retorna (es_válido, lista_de_errores)
        """
        errors = []
        
        signal_type = getattr(signal, 'signal_type', None)
        if not signal_type:
            errors. append("Signal has no signal_type")
            return (False, errors)
        
        definition = self.get(signal_type)
        if not definition: 
            errors.append(f"Unknown signal type: {signal_type}")
            return (False, errors)
        
        # Verificar campos requeridos
        for field_name in definition.required_fields:
            if not hasattr(signal, field_name):
                errors.append(f"Missing required field: {field_name}")
            elif getattr(signal, field_name) is None:
                errors. append(f"Required field is None: {field_name}")
        
        # Verificar constraints de valor si aplica
        if definition.value_type == "enum" and "values" in definition.value_constraints:
            value = getattr(signal, 'value', None)
            if value is not None: 
                allowed = definition.value_constraints["values"]
                # El valor podría ser un Enum, extraer su valor
                value_str = value.value if hasattr(value, 'value') else str(value)
                if value_str not in allowed:
                    errors. append(f"Invalid value '{value_str}'.  Allowed:  {allowed}")
        
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporta vocabulario a diccionario"""
        return {
            signal_type: {
                "category": d.category,
                "description":  d.description,
                "required_fields": d.required_fields,
                "optional_fields":  d.optional_fields,
                "value_type": d.value_type,
                "value_constraints": d.value_constraints,
                "version": d.version
            }
            for signal_type, d in self.definitions.items()
        }
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vocabulary/capability_vocabulary.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CapabilityDefinition:
    """Definición de una capacidad"""
    capability_id: str
    name: str
    description: str
    category: str  # "loading", "scoping", "extraction", "transformation", "enrichment", "validation", "irrigation"
    required_signals: List[str] = field(default_factory=list)
    produced_signals: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    version: str = "1.0.0"


@dataclass
class CapabilityVocabulary:
    """
    Vocabulario canónico de capacidades.
    Define todas las capacidades válidas del sistema.
    """
    
    definitions: Dict[str, CapabilityDefinition] = field(default_factory=dict)
    
    def __post_init__(self):
        self._register_core_capabilities()
    
    def _register_core_capabilities(self):
        """Registra capacidades core del sistema"""
        
        # Capacidades de carga
        self.register(CapabilityDefinition(
            capability_id="can_load_canonical",
            name="Load Canonical Data",
            description="Capacidad de cargar archivos canónicos JSON",
            category="loading",
            produced_signals=["EventPresenceSignal", "StructuralAlignmentSignal"]
        ))
        
        # Capacidades de scoping
        self.register(CapabilityDefinition(
            capability_id="can_scope_context",
            name="Apply Context Scope",
            description="Capacidad de aplicar contexto y scope a datos",
            category="scoping",
            required_signals=["StructuralAlignmentSignal"],
            produced_signals=["CanonicalMappingSignal"]
        ))
        
        # Capacidades de extracción
        self.register(CapabilityDefinition(
            capability_id="can_extract_evidence",
            name="Extract Evidence",
            description="Capacidad de extraer evidencia empírica de respuestas",
            category="extraction",
            required_signals=["CanonicalMappingSignal"],
            produced_signals=["EmpiricalSupportSignal", "MethodApplicationSignal"]
        ))
        
        self.register(CapabilityDefinition(
            capability_id="can_extract_determinacy",
            name="Extract Determinacy",
            description="Capacidad de evaluar determinismo de respuestas",
            category="extraction",
            produced_signals=["AnswerDeterminacySignal"]
        ))
        
        self.register(CapabilityDefinition(
            capability_id="can_extract_specificity",
            name="Extract Specificity",
            description="Capacidad de evaluar especificidad de respuestas",
            category="extraction",
            produced_signals=["AnswerSpecificitySignal"]
        ))
        
        # Capacidades de transformación
        self.register(CapabilityDefinition(
            capability_id="can_transform_to_signals",
            name="Transform to Signals",
            description="Capacidad de transformar eventos en señales tipadas",
            category="transformation",
            required_signals=["EventPresenceSignal"],
            produced_signals=["*"]  # Puede producir cualquier señal
        ))
        
        # Capacidades de enriquecimiento
        self.register(CapabilityDefinition(
            capability_id="can_enrich_with_context",
            name="Enrich with Context",
            description="Capacidad de enriquecer datos con contexto PDET, territorial, etc.",
            category="enrichment",
            dependencies=["can_scope_context"]
        ))
        
        self.register(CapabilityDefinition(
            capability_id="can_enrich_with_signals",
            name="Enrich with Signals",
            description="Capacidad de enriquecer datos con señales previas",
            category="enrichment",
            required_signals=["*"]  # Requiere señales existentes
        ))
        
        # Capacidades de validación
        self.register(CapabilityDefinition(
            capability_id="can_validate_contracts",
            name="Validate Contracts",
            description="Capacidad de validar contratos de irrigación",
            category="validation",
            produced_signals=["DataIntegritySignal"]
        ))
        
        self.register(CapabilityDefinition(
            capability_id="can_validate_schema",
            name="Validate Schema",
            description="Capacidad de validar esquemas de datos",
            category="validation",
            produced_signals=["SchemaConflictSignal"]
        ))
        
        # Capacidades de irrigación
        self.register(CapabilityDefinition(
            capability_id="can_irrigate",
            name="Execute Irrigation",
            description="Capacidad de ejecutar irrigación completa",
            category="irrigation",
            dependencies=["can_load_canonical", "can_transform_to_signals"],
            produced_signals=["ExecutionAttemptSignal"]
        ))
        
        # Capacidades de contraste
        self.register(CapabilityDefinition(
            capability_id="can_contrast_legacy",
            name="Contrast with Legacy",
            description="Capacidad de contrastar resultados con sistema legacy",
            category="contrast",
            produced_signals=["DecisionDivergenceSignal", "ConfidenceDropSignal"]
        ))
        
        # Capacidades de auditoría
        self.register(CapabilityDefinition(
            capability_id="can_audit_signals",
            name="Audit Signals",
            description="Capacidad de auditar señales generadas",
            category="audit",
            required_signals=["*"]
        ))
        
        self.register(CapabilityDefinition(
            capability_id="can_audit_consumers",
            name="Audit Consumers",
            description="Capacidad de auditar consumidores",
            category="audit",
            produced_signals=["ConsumerHealthSignal"]
        ))
    
    def register(self, definition: CapabilityDefinition):
        """Registra una definición de capacidad"""
        self.definitions[definition.capability_id] = definition
    
    def get(self, capability_id:  str) -> Optional[CapabilityDefinition]:
        """Obtiene definición de una capacidad"""
        return self.definitions. get(capability_id)
    
    def is_valid(self, capability_id: str) -> bool:
        """Verifica si una capacidad es válida"""
        return capability_id in self.definitions
    
    def get_by_category(self, category: str) -> List[CapabilityDefinition]:
        """Obtiene capacidades por categoría"""
        return [d for d in self.definitions.values() if d.category == category]
    
    def get_producers_of(self, signal_type: str) -> List[CapabilityDefinition]:
        """Obtiene capacidades que producen un tipo de señal"""
        result = []
        for d in self.definitions.values():
            if signal_type in d.produced_signals or "*" in d.produced_signals:
                result.append(d)
        return result
    
    def get_consumers_of(self, signal_type: str) -> List[CapabilityDefinition]:
        """Obtiene capacidades que requieren un tipo de señal"""
        result = []
        for d in self.definitions.values():
            if signal_type in d.required_signals or "*" in d.required_signals:
                result.append(d)
        return result
Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vocabulary/alignment_checker. py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from . signal_vocabulary import SignalVocabulary
from .capability_vocabulary import CapabilityVocabulary


@dataclass
class AlignmentIssue:
    """Problema de alineación detectado"""
    issue_type: str  # "missing_signal", "missing_capability", "incompatible_version", "orphan_signal"
    severity: str    # "critical", "warning", "info"
    component: str   # Componente afectado
    details: str     # Descripción del problema
    suggested_fix: str = ""


@dataclass
class AlignmentReport:
    """Reporte de alineación de vocabularios"""
    is_aligned: bool
    issues: List[AlignmentIssue] = field(default_factory=list)
    signals_checked: int = 0
    capabilities_checked: int = 0
    coverage_percentage: float = 0.0
    
    def add_issue(self, issue: AlignmentIssue):
        self.issues.append(issue)
        if issue.severity == "critical": 
            self.is_aligned = False


@dataclass
class VocabularyAlignmentChecker:
    """
    Verificador de alineación entre vocabularios de señales y capacidades.
    
    Detecta: 
    1. Señales sin productor
    2. Señales sin consumidor
    3. Capacidades que requieren señales inexistentes
    4. Capacidades que producen señales no definidas
    """
    
    signal_vocabulary: SignalVocabulary = field(default_factory=SignalVocabulary)
    capability_vocabulary: CapabilityVocabulary = field(default_factory=CapabilityVocabulary)
    
    def check_alignment(self) -> AlignmentReport:
        """
        Verifica alineación completa entre vocabularios.
        """
        report = AlignmentReport(is_aligned=True)
        
        # 1. Verificar que cada señal tiene al menos un productor
        self._check_signal_producers(report)
        
        # 2. Verificar que cada señal tiene al menos un consumidor potencial
        self._check_signal_consumers(report)
        
        # 3. Verificar que las capacidades referencian señales válidas
        self._check_capability_signals(report)
        
        # 4. Verificar dependencias de capacidades
        self._check_capability_dependencies(report)
        
        # Calcular cobertura
        total_signals = len(self.signal_vocabulary.definitions)
        total_capabilities = len(self.capability_vocabulary.definitions)
        critical_issues = sum(1 for i in report.issues if i.severity == "critical")
        
        report.signals_checked = total_signals
        report.capabilities_checked = total_capabilities
        
        if total_signals + total_capabilities > 0:
            report.coverage_percentage = (
                1 - (critical_issues / (total_signals + total_capabilities))
            ) * 100
        
        return report
    
    def _check_signal_producers(self, report: AlignmentReport):
        """Verifica que cada señal tiene productor"""
        for signal_type in self.signal_vocabulary.definitions:
            producers = self.capability_vocabulary.get_producers_of(signal_type)
            
            if not producers:
                report.add_issue(AlignmentIssue(
                    issue_type="orphan_signal",
                    severity="warning",
                    component=signal_type,
                    details=f"Signal type '{signal_type}' has no defined producer capability",
                    suggested_fix=f"Add a capability that produces '{signal_type}'"
                ))
    
    def _check_signal_consumers(self, report: AlignmentReport):
        """Verifica que cada señal tiene consumidor potencial"""
        for signal_type in self.signal_vocabulary.definitions:
            consumers = self.capability_vocabulary.get_consumers_of(signal_type)
            
            # No es crítico si no tiene consumidor, pero es una advertencia
            if not consumers: 
                report.add_issue(AlignmentIssue(
                    issue_type="unused_signal",
                    severity="info",
                    component=signal_type,
                    details=f"Signal type '{signal_type}' has no defined consumer capability",
                    suggested_fix=f"Consider if '{signal_type}' is needed or add a consumer"
                ))
    
    def _check_capability_signals(self, report: AlignmentReport):
        """Verifica que las capacidades referencian señales válidas"""
        for cap_id, cap_def in self.capability_vocabulary.definitions.items():
            # Verificar señales requeridas
            for signal_type in cap_def. required_signals:
                if signal_type != "*" and not self.signal_vocabulary.is_valid_type(signal_type):
                    report.add_issue(AlignmentIssue(
                        issue_type="missing_signal",
                        severity="critical",
                        component=cap_id,
                        details=f"Capability '{cap_id}' requires undefined signal '{signal_type}'",
                        suggested_fix=f"Define signal type '{signal_type}' in SignalVocabulary"
                    ))
            
            # Verificar señales producidas
            for signal_type in cap_def.produced_signals:
                if signal_type != "*" and not self.signal_vocabulary.is_valid_type(signal_type):
                    report.add_issue(AlignmentIssue(
                        issue_type="missing_signal",
                        severity="critical",
                        component=cap_id,
                        details=f"Capability '{cap_id}' produces undefined signal '{signal_type}'",
                        suggested_fix=f"Define signal type '{signal_type}' in SignalVocabulary"
                    ))
    
    def _check_capability_dependencies(self, report: AlignmentReport):
        """Verifica dependencias entre capacidades"""
        for cap_id, cap_def in self.capability_vocabulary.definitions. items():
            for dep_id in cap_def. dependencies:
                if not self.capability_vocabulary.is_valid(dep_id):
                    report.add_issue(AlignmentIssue(
                        issue_type="missing_capability",
                        severity="critical",
                        component=cap_id,
                        details=f"Capability '{cap_id}' depends on undefined capability '{dep_id}'",
                        suggested_fix=f"Define capability '{dep_id}' in CapabilityVocabulary"
                    ))
    
    def check_vehicle_alignment(
        self, 
        vehicle_id: str, 
        declared_signals: List[str],
        declared_capabilities: List[str]
    ) -> AlignmentReport:
        """
        Verifica alineación de un vehículo específico.
        """
        report = AlignmentReport(is_aligned=True)
        
        # Verificar señales declaradas
        for signal_type in declared_signals:
            if not self.signal_vocabulary.is_valid_type(signal_type):
                report.add_issue(AlignmentIssue(
                    issue_type="missing_signal",
                    severity="critical",
                    component=vehicle_id,
                    details=f"Vehicle declares undefined signal type '{signal_type}'",
                    suggested_fix=f"Add '{signal_type}' to SignalVocabulary or remove from vehicle"
                ))
        
        # Verificar capacidades declaradas
        for cap_id in declared_capabilities: 
            if not self.capability_vocabulary.is_valid(cap_id):
                report.add_issue(AlignmentIssue(
                    issue_type="missing_capability",
                    severity="critical",
                    component=vehicle_id,
                    details=f"Vehicle declares undefined capability '{cap_id}'",
                    suggested_fix=f"Add '{cap_id}' to CapabilityVocabulary or remove from vehicle"
                ))
        
        report.signals_checked = len(declared_signals)
        report.capabilities_checked = len(declared_capabilities)
        
        return report
    
    def check_irrigation_route_alignment(
        self,
        route_id: str,
        vehicles: List[str],
        required_signals: List[str],
        target_consumers: List[str]
    ) -> AlignmentReport:
        """
        Verifica alineación de una ruta de irrigación.
        """
        report = AlignmentReport(is_aligned=True)
        
        # Verificar que los vehículos pueden producir las señales requeridas
        for signal_type in required_signals: 
            if not self.signal_vocabulary.is_valid_type(signal_type):
                report.add_issue(AlignmentIssue(
                    issue_type="missing_signal",
                    severity="critical",
                    component=route_id,
                    details=f"Route requires undefined signal type '{signal_type}'",
                    suggested_fix=f"Define '{signal_type}' or update route requirements"
                ))
        
        return report
    
    def generate_gap_resolution_plan(self, report: AlignmentReport) -> List[Dict[str, Any]]:
        """
        Genera plan de resolución de gaps basado en el reporte.
        """
        plan = []
        
        # Agrupar issues por tipo
        by_type:  Dict[str, List[AlignmentIssue]] = {}
        for issue in report.issues:
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type]. append(issue)
        
        # Generar pasos del plan
        priority = 1
        
        # Primero resolver señales faltantes (críticas)
        if "missing_signal" in by_type:
            plan.append({
                "priority": priority,
                "action": "DEFINE_MISSING_SIGNALS",
                "description": "Definir tipos de señales faltantes en SignalVocabulary",
                "items": [i.component for i in by_type["missing_signal"]],
                "severity": "critical"
            })
            priority += 1
        
        # Luego resolver capacidades faltantes
        if "missing_capability" in by_type:
            plan. append({
                "priority": priority,
                "action": "DEFINE_MISSING_CAPABILITIES",
                "description": "Definir capacidades faltantes en CapabilityVocabulary",
                "items": [i.component for i in by_type["missing_capability"]],
                "severity":  "critical"
            })
            priority += 1
        
        # Luego resolver señales huérfanas
        if "orphan_signal" in by_type:
            plan.append({
                "priority":  priority,
                "action": "ASSIGN_PRODUCERS",
                "description": "Asignar productores a señales huérfanas",
                "items": [i.component for i in by_type["orphan_signal"]],
                "severity":  "warning"
            })
            priority += 1
        
        # Finalmente revisar señales no usadas
        if "unused_signal" in by_type:
            plan.append({
                "priority": priority,
                "action":  "REVIEW_UNUSED_SIGNALS",
                "description": "Revisar si las señales no usadas son necesarias",
                "items": [i.component for i in by_type["unused_signal"]],
                "severity": "info"
            })
        
        return plan
VI. CONFIGURACIÓN Y SCHEMAS

6.1 Bus Configuration

YAML
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config/bus_config.yaml

buses:
  structural_bus:
    type: structural
    max_queue_size: 10000
    persistence:
      enabled: true
      path: "_data/buses/structural/"
    subscribers:
      max_per_bus: 50
    
  integrity_bus:
    type: integrity
    max_queue_size:  10000
    persistence: 
      enabled: true
      path:  "_data/buses/integrity/"
      
  epistemic_bus:
    type:  epistemic
    max_queue_size: 50000  # Mayor capacidad para señales epistémicas
    persistence: 
      enabled: true
      path: "_data/buses/epistemic/"
      
  contrast_bus:
    type: contrast
    max_queue_size:  5000
    persistence:
      enabled: true
      path: "_data/buses/contrast/"
      
  operational_bus:
    type: operational
    max_queue_size:  20000
    persistence:
      enabled: true
      path: "_data/buses/operational/"
      
  consumption_bus:
    type: consumption
    max_queue_size:  10000
    persistence: 
      enabled: true
      path:  "_data/buses/consumption/"

  universal_bus:
    type: universal
    max_queue_size:  100000
    persistence: 
      enabled: true
      path:  "_data/buses/universal/"

defaults:
  message_ttl_seconds: 86400  # 24 horas
  max_retries: 3
  retry_delay_ms: 1000
  acknowledgement_timeout_ms: 5000
6.2 Irrigation Configuration

YAML
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config/irrigation_config. yaml

irrigation: 
  base_path: "src/farfan_pipeline/data"
  
  phases:
    phase_0:
      description: "Bootstrap y carga inicial"
      priority: 1
      parallel_routes:  10
      
    phase_1:
      description: "Signal enrichment e ingestion"
      priority: 2
      parallel_routes: 5
      depends_on: [phase_0]
      
    phase_2:
      description:  "Factory, execution, synchronization"
      priority: 3
      parallel_routes: 7
      depends_on: [phase_1]
      
    phase_3:
      description: "Signal enriched scoring"
      priority: 4
      parallel_routes: 3
      depends_on: [phase_2]
      
    phase_7:
      description: "Meso questions processing"
      priority: 5
      parallel_routes: 2
      depends_on: [phase_3]
      
    phase_8:
      description: "Signal enriched recommendations"
      priority: 6
      parallel_routes: 1
      depends_on: [phase_7]

  vehicles:
    signal_registry:
      enabled: true
      priority: 1
      
    signal_context_scoper:
      enabled: true
      priority: 2
      
    signal_evidence_extractor:
      enabled:  true
      priority: 3
      
    signal_intelligence_layer:
      enabled: true
      priority: 4
      
    signal_loader:
      enabled: true
      priority: 1
      
    signal_quality_metrics:
      enabled: true
      priority: 5
      
    signal_irrigator:
      enabled: true
      priority: 6
      
    signal_enhancement_integrator:
      enabled: true
      priority: 7
      
    signals: 
      enabled: true
      priority: 8

  execution: 
    max_concurrent_routes: 20
    route_timeout_seconds: 300
    retry_failed_routes: true
    max_route_retries: 3
    
  logging:
    level: INFO
    file: "_logs/irrigation. log"
    rotation:  daily
    
  audit:
    enabled: true
    store_all_signals: true
    store_path: "_audit/irrigation/"
6.3 JSON Schemas

JSON
// src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/schemas/signal_schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://sisas.farfan/schemas/signal. json",
  "title": "SISAS Signal Schema",
  "description": "Schema for all SISAS signals",
  "type": "object",
  "required": ["signal_id", "signal_type", "category", "version", "context", "source", "created_at"],
  "properties": {
    "signal_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the signal"
    },
    "signal_type": {
      "type": "string",
      "description": "Type of signal from SignalVocabulary"
    },
    "category": {
      "type": "string",
      "enum": ["structural", "integrity", "epistemic", "contrast", "operational", "consumption"],
      "description": "Signal category"
    },
    "version": {
      "type":  "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Signal version (semver)"
    },
    "context":  {
      "type": "object",
      "required": ["node_type", "node_id", "phase", "consumer_scope"],
      "properties": {
        "node_type": {
          "type": "string",
          "description": "Type of canonical node"
        },
        "node_id": {
          "type": "string",
          "description": "Identifier of the node"
        },
        "phase": {
          "type": "string",
          "description": "Pipeline phase"
        },
        "consumer_scope": {
          "type":  "string",
          "description":  "Consumer scope"
        }
      }
    },
    "source": {
      "type": "object",
      "required": ["event_id", "source_file", "generation_timestamp", "generator_vehicle"],
      "properties": {
        "event_id": {
          "type": "string",
          "description": "ID of the source event"
        },
        "source_file": {
          "type": "string",
          "description": "Source canonical file"
        },
        "source_path": {
          "type": "string",
          "description": "Full path to source"
        },
        "generation_timestamp": {
          "type":  "string",
          "format": "date-time",
          "description":  "When the signal was generated"
        },
        "generator_vehicle": {
          "type": "string",
          "description": "Vehicle that generated the signal"
        }
      }
    },
    "value": {
      "description": "Signal value (type depends on signal_type)"
    },
    "confidence": {
      "type": "string",
      "enum": ["HIGH", "MEDIUM", "LOW", "INDETERMINATE"],
      "description":  "Confidence level"
    },
    "rationale": {
      "type":  "string",
      "description":  "Explanation of why the signal exists"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Creation timestamp"
    },
    "expires_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "Expiration timestamp (optional)"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Tags for categorization"
    },
    "hash": {
      "type": "string",
      "description": "Deterministic hash of signal content"
    }
  }
}
VII. PLAN DE IMPLEMENTACIÓN DETALLADO

7.1 Fase 1: Infraestructura Core (Semana 1-2)

YAML
FASE_1:
  nombre: "Infraestructura Core"
  duración: "2 semanas"
  
  entregables:
    - core/signal. py:  "Implementación completa de Signal base"
    - core/event.py: "Implementación completa de Event y EventStore"
    - core/contracts.py: "Contratos de publicación, consumo e irrigación"
    - core/bus.py: "SignalBus y BusRegistry"
    
  pruebas: 
    - test_signal_creation.py: "Pruebas de creación de señales"
    - test_event_store.py: "Pruebas de almacenamiento de eventos"
    - test_bus_publish.py: "Pruebas de publicación en buses"
    - test_contracts.py: "Pruebas de validación de contratos"
    
  criterios_de_éxito: 
    - "100% de cobertura en tests de core"
    - "Todas las señales son inmutables después de creación"
    - "EventStore nunca pierde eventos"
    - "Buses validan contratos antes de publicar"
7.2 Fase 2: Tipos de Señales (Semana 3)

YAML
FASE_2:
  nombre: "Tipos de Señales"
  duración: "1 semana"
  
  entregables:
    - signals/types/structural.py: "StructuralAlignmentSignal, SchemaConflictSignal, CanonicalMappingSignal"
    - signals/types/integrity.py: "EventPresenceSignal, EventCompletenessSignal, DataIntegritySignal"
    - signals/types/epistemic. py: "AnswerDeterminacySignal, AnswerSpecificitySignal, EmpiricalSupportSignal, MethodApplicationSignal"
    - signals/types/contrast.py: "DecisionDivergenceSignal, ConfidenceDropSignal, TemporalContrastSignal"
    - signals/types/operational.py: "ExecutionAttemptSignal, Fail
You said: CONTINUA
CONTINUA

Copilot said: ### 7.2 Fase 2: Tipos de Señales
7.2 Fase 2: Tipos de Señales (Semana 3) - Continuación

YAML
FASE_2:
  nombre: "Tipos de Señales"
  duración: "1 semana"
  
  entregables:
    - signals/types/structural.py: "StructuralAlignmentSignal, SchemaConflictSignal, CanonicalMappingSignal"
    - signals/types/integrity.py: "EventPresenceSignal, EventCompletenessSignal, DataIntegritySignal"
    - signals/types/epistemic. py: "AnswerDeterminacySignal, AnswerSpecificitySignal, EmpiricalSupportSignal, MethodApplicationSignal"
    - signals/types/contrast.py: "DecisionDivergenceSignal, ConfidenceDropSignal, TemporalContrastSignal"
    - signals/types/operational.py: "ExecutionAttemptSignal, FailureModeSignal, LegacyActivitySignal, LegacyDependencySignal"
    - signals/types/consumption.py: "FrequencySignal, TemporalCouplingSignal, ConsumerHealthSignal"
    - signals/registry.py: "Registro central de tipos"
    
  pruebas: 
    - test_structural_signals.py
    - test_integrity_signals. py
    - test_epistemic_signals.py
    - test_contrast_signals.py
    - test_operational_signals.py
    - test_consumption_signals.py
    
  criterios_de_éxito: 
    - "Cada tipo de señal tiene tests de serialización/deserialización"
    - "Todos los enums están definidos y documentados"
    - "Hash determinístico funciona correctamente"
7.3 Fase 3: Vehículos (Semana 4-5)

YAML
FASE_3:
  nombre: "Implementación de Vehículos"
  duración: "2 semanas"
  
  entregables:
    semana_4:
      - vehicles/base_vehicle.py: "Clase base con capacidades"
      - vehicles/signal_registry.py: "Vehículo principal para carga canónica"
      - vehicles/signal_context_scoper.py: "Vehículo para scoping y contexto"
      - vehicles/signal_loader.py: "Vehículo para carga de archivos"
      
    semana_5:
      - vehicles/signal_evidence_extractor.py: "Extracción de evidencia"
      - vehicles/signal_intelligence_layer.py: "Capa de inteligencia"
      - vehicles/signal_quality_metrics.py: "Métricas de calidad"
      - vehicles/signal_irrigator.py: "Ejecución de irrigación"
      - vehicles/signal_enhancement_integrator.py: "Integración de enriquecimiento"
      - vehicles/signals. py: "Vehículo agregador"
      
  mapeo_vehiculo_a_archivos:
    signal_registry: 
      archivos_canónicos:
        - "clusters/*/metadata.json"
        - "clusters/*/questions.json"
        - "clusters/*/aggregation_rules.json"
        - "dimensions/*/metadata.json"
        - "dimensions/*/questions.json"
        - "dimensions/*/pdet_context.json"
        - "policy_areas/*/metadata.json"
        - "policy_areas/*/questions.json"
        - "policy_areas/*/keywords.json"
        - "cross_cutting/*. json"
        - "scoring/*. json"
        - "governance/*.json"
      señales_producidas:
        - StructuralAlignmentSignal
        - EventPresenceSignal
        - EventCompletenessSignal
        - CanonicalMappingSignal
        
    signal_context_scoper: 
      archivos_canónicos:
        - "dimensions/*/questions/*. json"
        - "_registry/questions/*. json"
        - "_registry/patterns/*.json"
      señales_producidas:
        - CanonicalMappingSignal
        - AnswerDeterminacySignal
        - AnswerSpecificitySignal
        
    signal_evidence_extractor:
      archivos_canónicos:
        - "_registry/patterns/by_category/*.json"
        - "_registry/patterns/by_dimension/*.json"
        - "_registry/patterns/by_policy_area/*.json"
      señales_producidas:
        - EmpiricalSupportSignal
        - MethodApplicationSignal
        
    signal_intelligence_layer: 
      archivos_canónicos: 
        - "_registry/membership_criteria/*.json"
        - "_registry/entities/*.json"
        - "scoring/calibration/*. json"
      señales_producidas:
        - MethodApplicationSignal
        - AnswerDeterminacySignal
        - AnswerSpecificitySignal
        
    signal_quality_metrics: 
      archivos_canónicos:
        - "policy_areas/*/keywords.json"
        - "policy_areas/*/questions.json"
      señales_producidas:
        - DataIntegritySignal
        - EventCompletenessSignal
        
    signal_enhancement_integrator:
      archivos_canónicos:
        - "cross_cutting/*. json"
        - "scoring/*. json"
        - "semantic/*. json"
        - "validations/*.json"
      señales_producidas:
        - StructuralAlignmentSignal
        - CanonicalMappingSignal
        
  pruebas:
    - test_vehicle_registration.py
    - test_vehicle_processing.py
    - test_vehicle_signal_generation.py
    - test_vehicle_publication.py
    
  criterios_de_éxito:
    - "Cada vehículo procesa sus archivos asignados"
    - "Cada vehículo genera las señales declaradas"
    - "Los vehículos publican en los buses correctos"
7.4 Fase 4: Vocabularios y Alineación (Semana 6)

YAML
FASE_4:
  nombre: "Vocabularios y Alineación"
  duración: "1 semana"
  
  entregables:
    - vocabulary/signal_vocabulary.py: "Vocabulario completo de señales"
    - vocabulary/capability_vocabulary.py: "Vocabulario completo de capacidades"
    - vocabulary/alignment_checker.py: "Verificador de alineación"
    
  tareas: 
    - "Registrar los 18 tipos de señales en SignalVocabulary"
    - "Registrar las 12 capacidades en CapabilityVocabulary"
    - "Implementar verificación cruzada"
    - "Generar reporte de gaps"
    - "Crear plan de resolución automático"
    
  resolución_de_gaps_identificados:
    VOCAB_SEÑALES_NO_ALINEADO:
      archivos_afectados:  37
      acción:  "Mapear cada archivo a tipos de señales específicos"
      
    VOCAB_CAPACIDADES_NO_ALINEADO: 
      archivos_afectados: 15
      acción: "Declarar capacidades requeridas por cada consumidor"
      
  pruebas:
    - test_vocabulary_completeness.py
    - test_alignment_checker.py
    - test_gap_resolution. py
    
  criterios_de_éxito:
    - "0 gaps críticos en AlignmentReport"
    - "100% de señales tienen productor"
    - "100% de capacidades referencian señales válidas"
7.5 Fase 5: Sistema de Irrigación (Semana 7-8)

YAML
FASE_5:
  nombre: "Sistema de Irrigación"
  duración: "2 semanas"
  
  entregables:
    semana_7:
      - irrigation/irrigation_map.py: "Mapa completo de irrigación"
      - irrigation/irrigation_executor.py: "Ejecutor de rutas"
      - irrigation/irrigation_validator.py: "Validador de contratos"
      
    semana_8:
      - "Integración con archivos canónicos reales"
      - "Ejecución de irrigación fase por fase"
      - "Generación de reportes de irrigación"
      
  construcción_del_mapa: 
    desde_csv:  "sabana_final_decisiones.csv"
    total_rutas: 140
    irrigable_now: 126
    con_gaps: 14
    
  ejecución_por_fases:
    phase_0:
      archivos:  89
      consumidores: ["phase0_90_02_bootstrap.py", "providers. py", "wiring_types.py"]
      
    phase_1:
      archivos:  14
      consumidores: ["phase1_11_00_signal_enrichment.py", "phase1_13_00_cpp_ingestion.py"]
      
    phase_2:
      archivos: 43
      consumidores: 
        - "phase2_10_00_factory. py"
        - "phase2_30_03_resource_aware_executor.py"
        - "phase2_40_03_irrigation_synchronizer.py"
        - "phase2_60_00_base_executor_with_contract. py"
        - "phase2_80_00_evidence_nexus.py"
        - "phase2_95_00_contract_hydrator.py"
        - "phase2_95_02_precision_tracking.py"
        
    phase_3:
      archivos: 15
      consumidores: ["phase3_10_00_phase3_signal_enriched_scoring.py"]
      
    phase_7:
      archivos: 1
      consumidores: ["PENDIENTE_DECLARAR"]
      
    phase_8:
      archivos: 1
      consumidores: ["phase8_30_00_signal_enriched_recommendations.py"]
      
  pruebas:
    - test_irrigation_map_construction.py
    - test_route_execution.py
    - test_phase_execution.py
    - test_full_irrigation. py
    
  criterios_de_éxito:
    - "Todas las rutas irrigable_now se ejecutan sin errores"
    - "Cada consumidor recibe las señales esperadas"
    - "Audit trail completo de toda irrigación"
7.6 Fase 6: Consumidores (Semana 9-10)

YAML
FASE_6:
  nombre: "Implementación de Consumidores"
  duración: "2 semanas"
  
  entregables:
    - consumers/base_consumer.py: "Clase base para consumidores"
    - consumers/phase0/*. py: "Consumidores de phase_0"
    - consumers/phase1/*.py: "Consumidores de phase_1"
    - consumers/phase2/*.py: "Consumidores de phase_2"
    - consumers/phase3/*.py: "Consumidores de phase_3"
    - consumers/phase7/*.py: "Consumidores de phase_7 (NUEVO)"
    - consumers/phase8/*.py: "Consumidores de phase_8"
    
  implementación_base_consumer:
    capacidades: 
      - "Suscripción a buses"
      - "Filtrado de señales por contexto"
      - "Procesamiento analítico (NO ejecutivo)"
      - "Acknowledgement de señales"
      - "Reporte de salud"
      
  consumidores_por_fase:
    phase_0:
      phase0_90_02_bootstrap. py: 
        señales_consumidas: 
          - StructuralAlignmentSignal
          - EventPresenceSignal
          - CanonicalMappingSignal
        capacidades_requeridas:
          - can_load_canonical
          - can_validate_schema
          
      providers.py:
        señales_consumidas:
          - StructuralAlignmentSignal
          - EventCompletenessSignal
        capacidades_requeridas: 
          - can_scope_context
          
      wiring_types.py:
        señales_consumidas: 
          - CanonicalMappingSignal
        capacidades_requeridas: 
          - can_validate_contracts
          
    phase_1:
      phase1_11_00_signal_enrichment.py:
        señales_consumidas:
          - StructuralAlignmentSignal
          - EventPresenceSignal
          - MethodApplicationSignal
        capacidades_requeridas:
          - can_enrich_with_signals
          
      phase1_13_00_cpp_ingestion.py:
        señales_consumidas: 
          - EventPresenceSignal
          - EventCompletenessSignal
        capacidades_requeridas: 
          - can_load_canonical
          
    phase_2:
      phase2_10_00_factory.py:
        señales_consumidas:
          - StructuralAlignmentSignal
          - CanonicalMappingSignal
        capacidades_requeridas:
          - can_transform_to_signals
          
      phase2_30_03_resource_aware_executor.py:
        señales_consumidas:
          - ExecutionAttemptSignal
          - FailureModeSignal
        capacidades_requeridas: 
          - can_irrigate
          
      phase2_40_03_irrigation_synchronizer.py:
        señales_consumidas:
          - ExecutionAttemptSignal
          - TemporalCouplingSignal
        capacidades_requeridas:
          - can_irrigate
          
      phase2_60_00_base_executor_with_contract.py:
        señales_consumidas:
          - StructuralAlignmentSignal
          - DataIntegritySignal
        capacidades_requeridas: 
          - can_validate_contracts
          
      phase2_80_00_evidence_nexus.py:
        señales_consumidas:
          - EmpiricalSupportSignal
          - MethodApplicationSignal
        capacidades_requeridas: 
          - can_extract_evidence
          
      phase2_95_00_contract_hydrator.py:
        señales_consumidas:
          - StructuralAlignmentSignal
          - SchemaConflictSignal
        capacidades_requeridas: 
          - can_validate_contracts
          
      phase2_95_02_precision_tracking.py:
        señales_consumidas: 
          - AnswerDeterminacySignal
          - AnswerSpecificitySignal
        capacidades_requeridas:
          - can_extract_determinacy
          - can_extract_specificity
          
    phase_3:
      phase3_10_00_phase3_signal_enriched_scoring.py:
        señales_consumidas:
          - AnswerDeterminacySignal
          - AnswerSpecificitySignal
          - EmpiricalSupportSignal
          - MethodApplicationSignal
          - CanonicalMappingSignal
        capacidades_requeridas: 
          - can_enrich_with_signals
          - can_extract_evidence
          
    phase_7:
      NUEVO_CONSUMIDOR_REQUERIDO:
        descripción: "Consumidor para meso_questions.json"
        señales_consumidas:
          - CanonicalMappingSignal
          - StructuralAlignmentSignal
        capacidades_requeridas: 
          - can_scope_context
          
    phase_8:
      phase8_30_00_signal_enriched_recommendations.py:
        señales_consumidas:
          - AnswerDeterminacySignal
          - AnswerSpecificitySignal
          - EmpiricalSupportSignal
          - DecisionDivergenceSignal
        capacidades_requeridas: 
          - can_enrich_with_signals
          - can_contrast_legacy
          
  pruebas: 
    - test_consumer_subscription.py
    - test_consumer_filtering.py
    - test_consumer_processing.py
    - test_consumer_health.py
    
  criterios_de_éxito:
    - "Cada consumidor procesa solo señales que coinciden con su contrato"
    - "Ningún consumidor ejecuta decisiones directamente"
    - "Todos los consumidores reportan salud"
7.7 Fase 7: Auditoría y Contraste (Semana 11)

YAML
FASE_7:
  nombre: "Auditoría y Contraste Legacy"
  duración: "1 semana"
  
  entregables:
    - audit/signal_auditor.py: "Auditor de señales"
    - audit/consumer_auditor.py: "Auditor de consumidores"
    - audit/decision_auditor.py: "Auditor de decisiones"
    
  implementación_JF8_contraste:
    descripción: "Ejecutar legacy y nuevo en paralelo, comparar outputs"
    
    pasos:
      1_capturar_legacy:
        acción: "Capturar outputs del sistema legacy"
        señales_generadas:
          - LegacyActivitySignal
          - LegacyDependencySignal
          
      2_ejecutar_nuevo:
        acción: "Ejecutar sistema de señales"
        señales_generadas: 
          - AnswerDeterminacySignal
          - AnswerSpecificitySignal
          - EmpiricalSupportSignal
          
      3_comparar: 
        acción: "Comparar resultados"
        señales_generadas:
          - DecisionDivergenceSignal
          - ConfidenceDropSignal
          
      4_publicar_divergencias:
        acción: "Publicar diferencias como señales"
        bus:  contrast_bus
        
  implementación_JF10_auditoría:
    descripción:  "Auditoría continua que nunca se apaga"
    
    auditorías: 
      signal_audit:
        frecuencia: "continua"
        verifica: 
          - "Ninguna señal es huérfana"
          - "Todas las señales tienen source válido"
          - "Hash de señales es consistente"
          
      consumer_audit:
        frecuencia: "cada 5 minutos"
        verifica:
          - "Todos los consumidores están respondiendo"
          - "Error rate < 5%"
          - "Processing time < SLA"
          
      decision_audit:
        frecuencia:  "bajo demanda"
        verifica: 
          - "Decisiones justificables solo con señales"
          - "Trazabilidad completa desde dato hasta decisión"
          
  pruebas:
    - test_signal_audit.py
    - test_consumer_audit.py
    - test_decision_audit.py
    - test_legacy_contrast.py
    
  criterios_de_éxito:
    - "100% de señales auditables"
    - "0 señales huérfanas"
    - "Divergencias legacy detectadas y registradas"
7.8 Fase 8: Integración Final y Migración (Semana 12)

YAML
FASE_8:
  nombre: "Integración Final y Migración"
  duración: "1 semana"
  
  entregables:
    - "Sistema SISAS completamente funcional"
    - "Migración de sistema legacy"
    - "Documentación completa"
    - "Runbooks de operación"
    
  pasos_de_migración:
    1_verificación_pre_migración:
      - "Ejecutar AlignmentChecker:  0 gaps críticos"
      - "Ejecutar irrigación completa en modo dry-run"
      - "Verificar todos los consumidores responden"
      - "Verificar audit trail funciona"
      
    2_migración_gradual:
      orden: 
        - phase_0: "Primero - Bootstrap"
        - phase_1: "Segundo - Enrichment"
        - phase_2: "Tercero - Execution"
        - phase_3: "Cuarto - Scoring"
        - phase_7: "Quinto - Meso"
        - phase_8: "Sexto - Recommendations"
        
    3_contraste_paralelo:
      duración: "48 horas mínimo"
      acciones:
        - "Ejecutar legacy y nuevo en paralelo"
        - "Capturar todas las divergencias"
        - "Generar reporte de comparación"
        
    4_corte_controlado:
      condiciones:
        - "Divergencias < 5%"
        - "Error rate < 1%"
        - "Todos los consumidores healthy"
        - "Audit completo disponible"
        
    5_apagado_legacy:
      condiciones:
        - "Sistema nuevo estable por 24 horas"
        - "Rollback plan verificado"
        - "Stakeholders notificados"
        
  verificación_estado_final:
    checklist:
      - "El legacy puede apagarse y nada deja de ser observable"
      - "Las decisiones pueden justificarse solo con señales"
      - "Cualquier consumidor puede ser auditado"
      - "Ningún evento se pierde"
      - "Ninguna señal es huérfana"
      
  documentación: 
    - "README. md:  Overview del sistema"
    - "ARCHITECTURE.md: Arquitectura detallada"
    - "SIGNALS.md: Catálogo de señales"
    - "VEHICLES.md: Documentación de vehículos"
    - "CONSUMERS.md: Documentación de consumidores"
    - "OPERATIONS.md: Runbook de operaciones"
    - "TROUBLESHOOTING.md: Guía de resolución de problemas"
VIII. CONTRATOS DE IRRIGACIÓN POR ARCHIVO

8.1 Contratos para Archivos IRRIGABLE_NOW

Python
# Generación automática de contratos desde sabana_final_decisiones.csv

IRRIGATION_CONTRACTS = {
    # === CLUSTERS (12 archivos) - LISTOS ===
    "clusters/CL01_seguridad_paz/aggregation_rules.json":  {
        "contract_id": "IC_CL01_AGG",
        "source_phase": "phase_0",
        "vehicles": ["signal_registry"],
        "consumers": ["phase0_90_02_bootstrap.py", "providers.py", "wiring_types.py"],
        "signals": ["StructuralAlignmentSignal", "EventPresenceSignal", "CanonicalMappingSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    "clusters/CL01_seguridad_paz/metadata.json": {
        "contract_id": "IC_CL01_META",
        "source_phase":  "phase_0",
        "vehicles": ["signal_registry"],
        "consumers": ["phase0_90_02_bootstrap.py", "providers.py", "wiring_types.py"],
        "signals": ["StructuralAlignmentSignal", "EventPresenceSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    "clusters/CL01_seguridad_paz/questions.json": {
        "contract_id": "IC_CL01_Q",
        "source_phase":  "phase_0",
        "vehicles": ["signal_registry"],
        "consumers": ["phase0_90_02_bootstrap.py", "providers.py", "wiring_types.py"],
        "signals": ["StructuralAlignmentSignal", "EventPresenceSignal", "EventCompletenessSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    # ...  (repetir para CL02, CL03, CL04)
    
    # === DIMENSIONS (18 archivos core) - LISTOS ===
    "dimensions/DIM01_INSUMOS/metadata.json": {
        "contract_id": "IC_DIM01_META",
        "source_phase": "phase_0",
        "vehicles": ["signal_registry"],
        "consumers": ["phase0_90_02_bootstrap.py", "providers.py", "wiring_types.py"],
        "signals": ["StructuralAlignmentSignal", "EventPresenceSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    "dimensions/DIM01_INSUMOS/pdet_context.json": {
        "contract_id": "IC_DIM01_PDET",
        "source_phase": "phase_0",
        "vehicles": ["signal_registry"],
        "consumers": ["phase0_90_02_bootstrap.py", "providers.py", "wiring_types.py"],
        "signals": ["StructuralAlignmentSignal", "CanonicalMappingSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    "dimensions/DIM01_INSUMOS/questions.json": {
        "contract_id": "IC_DIM01_Q",
        "source_phase": "phase_0",
        "vehicles": ["signal_registry"],
        "consumers": ["phase0_90_02_bootstrap.py", "providers. py", "wiring_types. py"],
        "signals": ["StructuralAlignmentSignal", "EventPresenceSignal", "EventCompletenessSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    # ... (repetir para DIM02-DIM06)
    
    # === POLICY AREAS (30 archivos) - LISTOS ===
    "policy_areas/PA01_mujeres_genero/metadata.json": {
        "contract_id": "IC_PA01_META",
        "source_phase": "phase_0",
        "vehicles": ["signal_quality_metrics", "signal_registry", "signals"],
        "consumers": ["phase0_90_02_bootstrap. py", "providers.py", "wiring_types.py"],
        "signals": ["StructuralAlignmentSignal", "EventPresenceSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    "policy_areas/PA01_mujeres_genero/keywords.json": {
        "contract_id": "IC_PA01_KW",
        "source_phase": "phase_0",
        "vehicles": ["signal_quality_metrics", "signal_registry", "signals"],
        "consumers": ["phase0_90_02_bootstrap.py", "providers. py", "wiring_types. py"],
        "signals": ["StructuralAlignmentSignal", "DataIntegritySignal"],
        "status": "ACTIVE",
        "gaps": [],
        "notes": "Potential duplicate warning"
    },
    "policy_areas/PA01_mujeres_genero/questions.json": {
        "contract_id": "IC_PA01_Q",
        "source_phase":  "phase_0",
        "vehicles": ["signal_quality_metrics", "signal_registry", "signals"],
        "consumers": ["phase0_90_02_bootstrap. py", "providers.py", "wiring_types.py"],
        "signals": ["StructuralAlignmentSignal", "EventPresenceSignal", "EventCompletenessSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    # ... (repetir para PA02-PA10)
    
    # === PATTERNS (22 archivos) - NECESITAN ALINEACIÓN VOCAB ===
    "_registry/patterns/by_category/GENERAL.json": {
        "contract_id": "IC_PAT_GENERAL",
        "source_phase": "phase_2",
        "vehicles": ["signal_context_scoper", "signal_evidence_extractor", "signal_intelligence_layer", 
                     "signal_loader", "signal_quality_metrics", "signal_registry", "signals"],
        "consumers":  ["phase2_10_00_factory.py", "phase2_30_03_resource_aware_executor.py",
                     "phase2_40_03_irrigation_synchronizer.py", "phase2_60_00_base_executor_with_contract.py",
                     "phase2_80_00_evidence_nexus. py", "phase2_95_00_contract_hydrator.py",
                     "phase2_95_02_precision_tracking. py"],
        "signals": ["StructuralAlignmentSignal", "MethodApplicationSignal", "EmpiricalSupportSignal"],
        "status": "PENDING",
        "gaps": ["VOCAB_SEÑALES_NO_ALINEADO"],
        "resolution": "Mapear patrones a señales específicas"
    },
    # ... (repetir para otros patterns)
    
    # === REGISTRY/ENTITIES (12 archivos) - NECESITAN VEHÍCULO Y ALINEACIÓN ===
    "_registry/entities/corpus_empirico_integrado.json": {
        "contract_id": "IC_ENT_CORPUS",
        "source_phase": "phase_3",
        "vehicles": [],  # NECESITA VEHÍCULO
        "consumers": ["phase3_10_00_phase3_signal_enriched_scoring.py"],
        "signals": ["MethodApplicationSignal", "EmpiricalSupportSignal"],
        "status": "PENDING",
        "gaps": ["NECESITA_VEHICULO", "VOCAB_SEÑALES_NO_ALINEADO", "VOCAB_CAPACIDADES_NO_ALINEADO"],
        "resolution": "Asignar signal_intelligence_layer como vehículo"
    },
    
    # === REGISTRY/QUESTIONS (3 archivos) ===
    "_registry/questions/macro_question.json": {
        "contract_id": "IC_Q_MACRO",
        "source_phase": "phase_8",
        "vehicles": ["signal_context_scoper", "signal_registry"],
        "consumers": ["phase8_30_00_signal_enriched_recommendations.py"],
        "signals": ["CanonicalMappingSignal", "AnswerDeterminacySignal"],
        "status": "ACTIVE",  # ¡LISTO!
        "gaps": []
    },
    "_registry/questions/meso_questions.json": {
        "contract_id": "IC_Q_MESO",
        "source_phase": "phase_7",
        "vehicles": ["signal_context_scoper", "signal_registry"],
        "consumers":  [],  # NECESITA CONSUMIDOR
        "signals": ["CanonicalMappingSignal", "StructuralAlignmentSignal"],
        "status": "PENDING",
        "gaps": ["NECESITA_CONSUMIDOR"],
        "resolution": "Crear phase7_consumer. py"
    },
    
    # === CROSS-CUTTING (11 archivos) - LISTOS ===
    "cross_cutting/cross_cutting_themes.json": {
        "contract_id": "IC_CC_THEMES",
        "source_phase": "phase_0",
        "vehicles": ["signal_enhancement_integrator", "signal_registry"],
        "consumers": ["phase0_90_02_bootstrap.py", "providers.py", "wiring_types.py"],
        "signals": ["StructuralAlignmentSignal", "CanonicalMappingSignal"],
        "status": "ACTIVE",
        "gaps": []
    },
    
    # === VALIDATIONS (5 archivos) - NECESITAN CONSUMIDOR ===
    "validations/referential_integrity.json": {
        "contract_id": "IC_VAL_REF",
        "source_phase": "Cross-Phase",
        "vehicles": ["signal_enhancement_integrator", "signal_intelligence_layer", "signal_registry"],
        "consumers": [],  # NECESITA CONSUMIDOR
        "signals": ["DataIntegritySignal", "SchemaConflictSignal"],
        "status": "PENDING",
        "gaps": ["NECESITA_CONSUMIDOR"],
        "resolution":  "Crear validation_consumer.py o asignar a consumidor existente"
    }
}
8.2 Script de Generación de Contratos

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/scripts/generate_contracts.py

import csv
import json
from typing import Dict, List, Any
from dataclasses import asdict

from .. core.contracts import IrrigationContract, ContractStatus, ContractRegistry
from ..irrigation. irrigation_map import IrrigationSource, IrrigabilityStatus


def generate_contracts_from_csv(csv_path: str) -> ContractRegistry:
    """
    Genera contratos de irrigación desde sabana_final_decisiones.csv
    """
    registry = ContractRegistry()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Filtrar items no canónicos
            if row. get("added_value") == "MARGINAL":
                continue
            if row.get("stage") == "External":
                continue
            
            # Parsear datos
            file_path = row. get("json_file_path", "")
            stage = row.get("stage", "")
            phase = row.get("phase", "")
            vehicles = parse_list(row.get("vehiculos_str", ""))
            consumers = parse_list(row.get("consumidores_str", ""))
            gaps = parse_list(row.get("gaps_str", ""))
            irrigability = row.get("irrigability_bucket", "")
            
            # Determinar estado del contrato
            if irrigability == "irrigable_now" and not gaps:
                status = ContractStatus.ACTIVE
            elif irrigability == "not_irrigable_yet": 
                status = ContractStatus. DRAFT
            else:
                status = ContractStatus.SUSPENDED
            
            # Crear contrato
            contract = IrrigationContract(
                contract_id=f"IC_{file_path. replace('/', '_').replace('.json', '')}",
                source_file=file_path. split('/')[-1],
                source_path=file_path,
                source_phase=phase,
                vehicles=vehicles,
                consumers=consumers,
                vocabulary_aligned=("VOCAB_SEÑALES_NO_ALINEADO" not in gaps and 
                                   "VOCAB_CAPACIDADES_NO_ALINEADO" not in gaps),
                gaps=gaps,
                status=status
            )
            
            registry.register_irrigation(contract)
    
    return registry


def parse_list(value: str) -> List[str]:
    """Parsea lista separada por comas"""
    if not value or value == "NINGUNO":
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def export_contracts_to_json(registry: ContractRegistry, output_path: str):
    """Exporta contratos a JSON"""
    contracts = {
        cid: contract.to_dict() 
        for cid, contract in registry.irrigation_contracts.items()
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(contracts, f, indent=2, ensure_ascii=False)


def generate_gap_resolution_tasks(registry: ContractRegistry) -> List[Dict[str, Any]]:
    """
    Genera tareas de resolución de gaps
    """
    tasks = []
    
    blocked = registry.get_blocked_contracts()
    
    # Agrupar por tipo de gap
    by_gap:  Dict[str, List[str]] = {}
    for contract, gaps in blocked: 
        for gap in gaps:
            if gap not in by_gap:
                by_gap[gap] = []
            by_gap[gap]. append(contract. source_path)
    
    # Generar tareas
    priority = 1
    
    if "NECESITA_VEHICULO" in by_gap: 
        tasks.append({
            "priority": priority,
            "gap_type": "NECESITA_VEHICULO",
            "action": "AGREGAR_CARGA_EN_VEHICULO",
            "description": "Asignar vehículos a archivos que no tienen",
            "files_affected": len(by_gap["NECESITA_VEHICULO"]),
            "files":  by_gap["NECESITA_VEHICULO"],
            "suggested_vehicles": {
                "_registry/entities/":  "signal_intelligence_layer",
                "_registry/membership_criteria/": "signal_intelligence_layer",
                "colombia_context/": "signal_enhancement_integrator",
                "config/": "signal_loader"
            }
        })
        priority += 1
    
    if "NECESITA_CONSUMIDOR" in by_gap: 
        tasks.append({
            "priority": priority,
            "gap_type": "NECESITA_CONSUMIDOR",
            "action": "DECLARAR_CONSUMIDOR_EN_FASE",
            "description": "Declarar consumidores para archivos sin destino",
            "files_affected": len(by_gap["NECESITA_CONSUMIDOR"]),
            "files": by_gap["NECESITA_CONSUMIDOR"],
            "suggested_consumers":  {
                "_registry/patterns/MASTER_INDEX.json": "phase2_pattern_consumer. py",
                "_registry/questions/integration_map.json": "phase_integration_consumer.py",
                "_registry/questions/meso_questions.json": "phase7_meso_consumer.py",
                "validations/": "validation_consumer. py"
            }
        })
        priority += 1
    
    if "VOCAB_SEÑALES_NO_ALINEADO" in by_gap:
        tasks.append({
            "priority": priority,
            "gap_type": "VOCAB_SEÑALES_NO_ALINEADO",
            "action": "ALINEAR_VOCABULARIOS",
            "description": "Mapear archivos a tipos de señales específicos",
            "files_affected":  len(by_gap["VOCAB_SEÑALES_NO_ALINEADO"]),
            "files": by_gap["VOCAB_SEÑALES_NO_ALINEADO"],
            "mapping_required": True
        })
        priority += 1
    
    if "VOCAB_CAPACIDADES_NO_ALINEADO" in by_gap:
        tasks. append({
            "priority": priority,
            "gap_type":  "VOCAB_CAPACIDADES_NO_ALINEADO",
            "action": "ALINEAR_CAPACIDADES",
            "description": "Declarar capacidades requeridas por consumidores",
            "files_affected": len(by_gap["VOCAB_CAPACIDADES_NO_ALINEADO"]),
            "files":  by_gap["VOCAB_CAPACIDADES_NO_ALINEADO"]
        })
    
    return tasks


if __name__ == "__main__": 
    # Generar contratos
    registry = generate_contracts_from_csv("sabana_final_decisiones.csv")
    
    # Exportar a JSON
    export_contracts_to_json(registry, "_registry/irrigation_contracts.json")
    
    # Generar tareas de resolución
    tasks = generate_gap_resolution_tasks(registry)
    
    with open("_registry/gap_resolution_tasks.json", 'w', encoding='utf-8') as f:
        json. dump(tasks, f, indent=2, ensure_ascii=False)
    
    # Estadísticas
    stats = {
        "total_contracts": len(registry.irrigation_contracts),
        "active":  len([c for c in registry.irrigation_contracts.values() 
                      if c.status == ContractStatus.ACTIVE]),
        "pending": len([c for c in registry.irrigation_contracts.values() 
                       if c.status == ContractStatus.DRAFT]),
        "suspended": len([c for c in registry.irrigation_contracts.values() 
                         if c.status == ContractStatus.SUSPENDED]),
        "resolution_tasks": len(tasks)
    }
    
    print(json.dumps(stats, indent=2))
IX. RESOLUCIÓN DE GAPS ESPECÍFICOS

9.1 Gap: NECESITA_VEHICULO (33 archivos)

Python
# Resolución de gap NECESITA_VEHICULO

VEHICLE_ASSIGNMENTS = {
    # _registry/entities/ (12 archivos) → signal_intelligence_layer
    "_registry/entities/corpus_empirico_calibracion_extractores.json": "signal_intelligence_layer",
    "_registry/entities/corpus_empirico_integrado.json": "signal_intelligence_layer",
    "_registry/entities/corpus_empirico_normatividad. json": "signal_intelligence_layer",
    "_registry/entities/index.json": "signal_intelligence_layer",
    "_registry/entities/institutions.json": "signal_intelligence_layer",
    "_registry/entities/institutions_expanded.json": "signal_intelligence_layer",
    "_registry/entities/international. json": "signal_intelligence_layer",
    "_registry/entities/normative. json": "signal_intelligence_layer",
    "_registry/entities/normative_compliance.json": "signal_intelligence_layer",
    "_registry/entities/policy_areas_canonical.json": "signal_intelligence_layer",
    "_registry/entities/populations.json": "signal_intelligence_layer",
    "_registry/entities/territorial.json": "signal_intelligence_layer",
    
    # _registry/membership_criteria/ (13 archivos) → signal_intelligence_layer
    "_registry/membership_criteria/MC01_structural_markers.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC02_quantitative_triplets.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC03_normative_references.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC04_programmatic_hierarchy.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC05_financial_chains.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC06_population_disaggregation.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC07_temporal_markers.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC08_causal_verbs.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC09_institutional_network.json": "signal_intelligence_layer",
    "_registry/membership_criteria/MC10_semantic_relationships.json": "signal_intelligence_layer",
    "_registry/membership_criteria/_bindings/mc_to_dimensions.json": "signal_intelligence_layer",
    "_registry/membership_criteria/_bindings/mc_to_questions.json": "signal_intelligence_layer",
    "_registry/membership_criteria/_bindings/mc_to_scoring.json": "signal_intelligence_layer",
    "_registry/membership_criteria/_calibration/extractor_calibration.json": "signal_intelligence_layer",
    
    # _registry/EMPIRICAL_CORPUS_INDEX. json → signal_loader
    "_registry/EMPIRICAL_CORPUS_INDEX. json": "signal_loader",
    
    # _registry/capabilities/ (3 archivos) → signal_registry
    "_registry/capabilities/capability_definitions.json": "signal_registry",
    "_registry/capabilities/consumer_capability_declarations.json": "signal_registry",
    "_registry/capabilities/signal_capability_map.json": "signal_registry",
    
    # colombia_context/ (3 archivos) → signal_enhancement_integrator
    "colombia_context/colombia_context. json": "signal_enhancement_integrator",
    "colombia_context/municipal_governance.json": "signal_enhancement_integrator",
    "colombia_context/pdet_municipalities.json": "signal_enhancement_integrator",
    
    # config/ (2 archivos) → signal_loader
    "config/canonical_notation.json": "signal_loader",
    "_registry/questionnaire_index.json": "signal_loader"
}


def apply_vehicle_assignments():
    """
    Aplica asignaciones de vehículos a contratos existentes
    """
    # Cargar contratos
    with open("_registry/irrigation_contracts.json", 'r') as f:
        contracts = json.load(f)
    
    # Aplicar asignaciones
    for file_path, vehicle in VEHICLE_ASSIGNMENTS.items():
        contract_id = f"IC_{file_path.replace('/', '_').replace('.json', '')}"
        
        if contract_id in contracts:
            if vehicle not in contracts[contract_id]["vehicles"]:
                contracts[contract_id]["vehicles"].append(vehicle)
            
            # Remover gap
            if "NECESITA_VEHICULO" in contracts[contract_id]["gaps"]:
                contracts[contract_id]["gaps"].remove("NECESITA_VEHICULO")
            
            # Actualizar estado si ya no hay gaps críticos
            if not contracts[contract_id]["gaps"]:
                contracts[contract_id]["status"] = "ACTIVE"
    
    # Guardar
    with open("_registry/irrigation_contracts.json", 'w') as f:
        json. dump(contracts, f, indent=2)
9.2 Gap: NECESITA_CONSUMIDOR (11 archivos)

Python
# Resolución de gap NECESITA_CONSUMIDOR

CONSUMER_DECLARATIONS = {
    # _registry/patterns/MASTER_INDEX.json → phase2_pattern_consumer.py
    "_registry/patterns/MASTER_INDEX.json": {
        "consumer_id": "phase2_pattern_consumer.py",
        "consumer_phase": "phase_2",
        "signals_consumed": ["StructuralAlignmentSignal", "CanonicalMappingSignal"],
        "capabilities_required": ["can_load_canonical", "can_scope_context"]
    },
    
    # _registry/questions/integration_map.json → cross_phase_integration_consumer.py
    "_registry/questions/integration_map.json": {
        "consumer_id": "cross_phase_integration_consumer.py",
        "consumer_phase":  "Cross-Phase",
        "signals_consumed": ["CanonicalMappingSignal", "StructuralAlignmentSignal"],
        "capabilities_required": ["can_scope_context"]
    },
    
    # _registry/questions/meso_questions.json → phase7_meso_consumer.py (NUEVO)
    "_registry/questions/meso_questions.json": {
        "consumer_id": "phase7_meso_consumer. py",
        "consumer_phase": "phase_7",
        "signals_consumed": ["CanonicalMappingSignal", "StructuralAlignmentSignal"],
        "capabilities_required": ["can_scope_context"]
    },
    
    # validations/ (5 archivos) → validation_consumer.py
    "validations/interdependency_mapping.json": {
        "consumer_id": "validation_consumer. py",
        "consumer_phase": "Cross-Phase",
        "signals_consumed": ["DataIntegritySignal", "SchemaConflictSignal"],
        "capabilities_required": ["can_validate_schema", "can_validate_contracts"]
    },
    "validations/normalization_report.json": {
        "consumer_id": "validation_consumer. py",
        "consumer_phase": "Cross-Phase",
        "signals_consumed": ["DataIntegritySignal"],
        "capabilities_required": ["can_validate_schema"]
    },
    "validations/quality_assurance_test_suite.json": {
        "consumer_id": "validation_consumer. py",
        "consumer_phase": "Cross-Phase",
        "signals_consumed": ["DataIntegritySignal", "EventCompletenessSignal"],
        "capabilities_required": ["can_validate_schema"]
    },
    "validations/referential_integrity.json": {
        "consumer_id": "validation_consumer.py",
        "consumer_phase": "Cross-Phase",
        "signals_consumed":  ["DataIntegritySignal"],
        "capabilities_required": ["can_validate_contracts"]
    },
    "validations/validation_templates.json": {
        "consumer_id": "validation_consumer. py",
        "consumer_phase": "Cross-Phase",
        "signals_consumed": ["StructuralAlignmentSignal"],
        "capabilities_required": ["can_validate_schema"]
    }
}


# Implementación del nuevo consumidor phase7_meso_consumer.py
PHASE7_MESO_CONSUMER_CODE = '''
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase7/phase7_meso_consumer. py

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ... core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase7MesoConsumer(BaseConsumer):
    """
    Consumidor para meso_questions.json en Phase 7.
    
    Procesa preguntas de nivel meso y genera análisis agregado.
    """
    
    consumer_id: str = "phase7_meso_consumer.py"
    consumer_phase: str = "phase_7"
    
    def __post_init__(self):
        super().__post_init__()
        
        # Configurar contrato de consumo
        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE7_MESO",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "CanonicalMappingSignal",
                "StructuralAlignmentSignal"
            ],
            subscribed_buses=["structural_bus"],
            context_filters={
                "phase":  ["phase_7"],
                "node_type": ["question"]
            },
            required_capabilities=["can_scope_context"]
        )
    
    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa una señal recibida. 
        
        NO ejecuta decisiones, solo analiza. 
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal. signal_type,
            "processed":  True,
            "analysis": {}
        }
        
        if signal.signal_type == "CanonicalMappingSignal":
            result["analysis"] = self._analyze_mapping(signal)
        elif signal.signal_type == "StructuralAlignmentSignal":
            result["analysis"] = self._analyze_alignment(signal)
        
        return result
    
    def _analyze_mapping(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de mapeo"""
        return {
            "mapped_entities": getattr(signal, 'mapped_entities', {}),
            "mapping_completeness": getattr(signal, 'mapping_completeness', 0. 0),
            "unmapped":  getattr(signal, 'unmapped_aspects', [])
        }
    
    def _analyze_alignment(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de alineación"""
        return {
            "alignment_status": getattr(signal, 'alignment_status', None),
            "missing_elements": getattr(signal, 'missing_elements', [])
        }
'''
9.3 Gap: VOCAB_SEÑALES_NO_ALINEADO (37 archivos)

Python
# Mapeo de archivos a tipos de señales específicos

SIGNAL_TYPE_MAPPING = {
    # _registry/entities/ → Señales de inteligencia y extracción
    "_registry/entities/*": {
        "signals_produced": [
            "MethodApplicationSignal",
            "EmpiricalSupportSignal",
            "CanonicalMappingSignal"
        ],
        "signals_consumed": [
            "StructuralAlignmentSignal"
        ]
    },
    
    # _registry/patterns/by_category/ → Señales de extracción
    "_registry/patterns/by_category/*": {
        "signals_produced": [
            "MethodApplicationSignal",
            "EmpiricalSupportSignal",
            "AnswerSpecificitySignal"
        ],
        "signals_consumed": [
            "CanonicalMappingSignal",
            "EventPresenceSignal"
        ]
    },
    
    # _registry/patterns/by_dimension/ → Señales epistémicas
    "_registry/patterns/by_dimension/*": {
        "signals_produced": [
            "AnswerDeterminacySignal",
            "AnswerSpecificitySignal",
            "MethodApplicationSignal"
        ],
        "signals_consumed": [
            "StructuralAlignmentSignal",
            "CanonicalMappingSignal"
        ]
    },
    
    # _registry/patterns/by_policy_area/ → Señales de contexto
    "_registry/patterns/by_policy_area/*": {
        "signals_produced": [
            "CanonicalMappingSignal",
            "MethodApplicationSignal"
        ],
        "signals_consumed": [
            "StructuralAlignmentSignal"
        ]
    },
    
    # colombia_context/ → Señales de enriquecimiento
    "colombia_context/*": {
        "signals_produced": [
            "CanonicalMappingSignal",
            "StructuralAlignmentSignal"
        ],
        "signals_consumed": [
            "EventPresenceSignal"
        ]
    },
    
    # _registry/keywords/ → Señales de validación
    "_registry/keywords/*": {
        "signals_produced": [
            "DataIntegritySignal",
            "EventCompletenessSignal"
        ],
        "signals_consumed": [
            "StructuralAlignmentSignal"
        ]
    }
}


def resolve_vocab_alignment():
    """
    Resuelve el gap de vocabulario de señales
    """
    # Cargar vocabulario de señales
    from .. vocabulary.signal_vocabulary import SignalVocabulary
    vocab = SignalVocabulary()
    
    # Cargar contratos
    with open("_registry/irrigation_contracts.json", 'r') as f:
        contracts = json.load(f)
    
    # Aplicar mapeos
    for pattern, mapping in SIGNAL_TYPE_MAPPING.items():
        for contract_id, contract in contracts.items():
            file_path = contract["source_path"]
            
            # Verificar si el archivo coincide con el patrón
            if matches_pattern(file_path, pattern):
                # Agregar señales
                contract["generated_signals"] = mapping["signals_produced"]
                
                # Verificar que las señales existen en vocabulario
                for signal_type in mapping["signals_produced"]:
                    if vocab.is_valid_type(signal_type):
                        # Remover gap
                        if "VOCAB_SEÑALES_NO_ALINEADO" in contract["gaps"]:
                            contract["gaps"].remove("VOCAB_SEÑALES_NO_ALINEADO")
                        contract["vocabulary_aligned"] = True
    
    # Guardar
    with open("_registry/irrigation_contracts.json", 'w') as f:
        json.dump(contracts, f, indent=2)


def matches_pattern(file_path: str, pattern: str) -> bool:
    """Verifica si un path coincide con un patrón"""
    import fnmatch
    return fnmatch.fnmatch(file_path, pattern)
X. COMANDOS DE EJECUCIÓN

10.1 Script Principal de Inicialización

Python
# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/main.py

#!/usr/bin/env python3
"""
SISAS - Signal-Irrigated System for Analytical Support
Main entry point for irrigation execution
"""

import argparse
import logging
import sys
from pathlib import Path

from . core.bus import BusRegistry
from .core.contracts import ContractRegistry
from .core.event import EventStore
from .vocabulary.signal_vocabulary import SignalVocabulary
from .vocabulary.capability_vocabulary import CapabilityVocabulary
from .vocabulary. alignment_checker import VocabularyAlignmentChecker
from .irrigation. irrigation_map import IrrigationMap
from .irrigation.irrigation_executor import IrrigationExecutor
from .vehicles.signal_registry import SignalRegistryVehicle
from .vehicles.signal_context_scoper import SignalContextScoperVehicle


def setup_logging(level:  str = "INFO"):
    """Configura logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('_logs/sisas.log')
        ]
    )


def initialize_system():
    """Inicializa el sistema SISAS completo"""
    logger = logging.getLogger("SISAS. Init")
    logger.info("Initializing SISAS...")
    
    # 1. Crear registros
    bus_registry = BusRegistry()
    contract_registry = ContractRegistry()
    event_store = EventStore()
    
    # 2. Crear vocabularios
    signal_vocab = SignalVocabulary()
    capability_vocab = CapabilityVocabulary()
    
    # 3. Verificar alineación
    alignment_checker = VocabularyAlignmentChecker(
        signal_vocabulary=signal_vocab,
        capability_vocabulary=capability_vocab
    )
    alignment_report = alignment_checker.check_alignment()
    
    if not alignment_report.is_aligned:
        logger.warning(f"Vocabulary alignment issues:  {len(alignment_report.issues)}")
        for issue in alignment_report.issues:
            if issue.severity == "critical":
                logger.error(f"  CRITICAL: {issue.details}")
    
    # 4. Crear vehículos
    vehicles = {
        "signal_registry": SignalRegistryVehicle(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store
        ),
        "signal_context_scoper": SignalContextScoperVehicle(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store
        )
    }
    
    # 5. Crear ejecutor de irrigación
    executor = IrrigationExecutor(
        bus_registry=bus_registry,
        contract_registry=contract_registry,
        event_store=event_store
    )
    
    # Registrar vehículos
    for vehicle in vehicles.values():
        executor.register_vehicle(vehicle)
    
    logger.info("SISAS initialized successfully")
    
    return {
        "executor": executor,
        "bus_registry": bus_registry,
        "contract_registry": contract_registry,
        "event_store":  event_store,
        "signal_vocab": signal_vocab,
        "capability_vocab": capability_vocab,
        "alignment_checker": alignment_checker
    }


def load_irrigation_map(csv_path: str) -> IrrigationMap:
    """Carga mapa de irrigación desde CSV"""
    import csv
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    return IrrigationMap. from_sabana_csv(data)


def run_irrigation(args):
    """Ejecuta irrigación"""
    logger = logging.getLogger("SISAS.Run")
    
    # Inicializar
    system = initialize_system()
    executor = system["executor"]
    
    # Cargar mapa
    irrigation_map = load_irrigation_map(args.csv_path)
    executor.irrigation_map = irrigation_map
    
    # Estadísticas
    stats = irrigation_map.get_statistics()
    logger.info(f"Loaded irrigation map:  {stats['total_routes']} routes")
    logger.info(f"  Irrigable now: {stats['irrigable_now']}")
    logger.info(f"  Not irrigable yet: {stats['not_irrigable_yet']}")
    
    # Ejecutar según modo
    if args.phase: 
        logger.info(f"Executing phase:  {args.phase}")
        results = executor.execute_phase(args.phase, args.base_path)
    elif args.all:
        logger.info("Executing all irrigable routes")
        results = executor.execute_all_irrigable(args.base_path)
    else:
        logger.error("Specify --phase or --all")
        return
    
    # Reportar resultados
    summary = executor.get_execution_summary()
    logger.info(f"Execution complete:")
    logger.info(f"  Total:  {summary['total_executions']}")
    logger.info(f"  Successful: {summary['successful']}")
    logger.info(f"  Failed: {summary['failed']}")
    logger.info(f"  Signals generated: {summary['total_signals_generated']}")


def check_alignment(args):
    """Verifica alineación de vocabularios"""
    logger = logging.getLogger("SISAS.Check")
    
    system = initialize_system()
    checker = system["alignment_checker"]
    
    report = checker.check_alignment()
    
    print(f"\n{'='*60}")
    print("SISAS Vocabulary Alignment Report")
    print(f"{'='*60}")
    print(f"Aligned: {report.is_aligned}")
    print(f"Signals checked: {report.signals_checked}")
    print(f"Capabilities checked: {report.capabilities_checked}")
    print(f"Coverage: {report.coverage_percentage:.1f}%")
    print(f"Issues: {len(report.issues)}")
    
    if report.issues:
        print(f"\n{'Issues by severity:'}")
        for severity in ["critical", "warning", "info"]:
            issues = [i for i in report.issues if i.severity == severity]
            if issues:
                print(f"\n  {severity.upper()} ({len(issues)}):")
                for issue in issues[: 5]:  # Most
You said: CONTINUA
CONTINUA 

Copilot said: ### 10.1 Script Principal de Inicialización (Continuación) ```python
10.1 Script Principal de Inicialización (Continuación)

Python
                for issue in issues[: 5]:  # Mostrar máximo 5 por categoría
                    print(f"    - {issue.component}: {issue.details}")
                if len(issues) > 5:
                    print(f"    ... and {len(issues) - 5} more")
    
    # Generar plan de resolución si hay issues
    if report.issues:
        plan = checker.generate_gap_resolution_plan(report)
        print(f"\n{'='*60}")
        print("Gap Resolution Plan")
        print(f"{'='*60}")
        for step in plan:
            print(f"\nPriority {step['priority']}: {step['action']}")
            print(f"  Description: {step['description']}")
            print(f"  Severity: {step['severity']}")
            print(f"  Items affected: {len(step['items'])}")


def generate_contracts(args):
    """Genera contratos desde CSV"""
    logger = logging.getLogger("SISAS. Contracts")
    
    from . scripts.generate_contracts import (
        generate_contracts_from_csv,
        export_contracts_to_json,
        generate_gap_resolution_tasks
    )
    
    logger.info(f"Generating contracts from {args.csv_path}")
    
    registry = generate_contracts_from_csv(args.csv_path)
    
    # Exportar
    output_path = args.output or "_registry/irrigation_contracts.json"
    export_contracts_to_json(registry, output_path)
    logger.info(f"Contracts exported to {output_path}")
    
    # Generar tareas
    tasks = generate_gap_resolution_tasks(registry)
    tasks_path = output_path.replace(".json", "_tasks.json")
    
    import json
    with open(tasks_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    logger.info(f"Resolution tasks exported to {tasks_path}")
    
    # Estadísticas
    from .core.contracts import ContractStatus
    stats = {
        "total":  len(registry. irrigation_contracts),
        "active": len([c for c in registry.irrigation_contracts. values() 
                      if c.status == ContractStatus.ACTIVE]),
        "pending": len([c for c in registry.irrigation_contracts.values() 
                       if c.status == ContractStatus.DRAFT]),
        "tasks":  len(tasks)
    }
    
    print(f"\nContract Generation Summary:")
    print(f"  Total contracts: {stats['total']}")
    print(f"  Active (ready to irrigate): {stats['active']}")
    print(f"  Pending (have gaps): {stats['pending']}")
    print(f"  Resolution tasks: {stats['tasks']}")


def show_stats(args):
    """Muestra estadísticas del sistema"""
    logger = logging.getLogger("SISAS.Stats")
    
    # Cargar mapa de irrigación
    irrigation_map = load_irrigation_map(args. csv_path)
    stats = irrigation_map.get_statistics()
    
    print(f"\n{'='*60}")
    print("SISAS Irrigation Statistics")
    print(f"{'='*60}")
    print(f"\nRoutes:")
    print(f"  Total: {stats['total_routes']}")
    print(f"  Irrigable now: {stats['irrigable_now']} ({stats['irrigable_percentage']:.1f}%)")
    print(f"  Not irrigable yet: {stats['not_irrigable_yet']}")
    print(f"  Definitely not:  {stats['definitely_not']}")
    
    print(f"\nPhases:  {', '.join(stats['phases'])}")
    print(f"Vehicles in use: {len(stats['vehicles_in_use'])}")
    for v in stats['vehicles_in_use']:
        print(f"  - {v}")
    
    print(f"\nConsumers registered: {len(stats['consumers_registered'])}")
    
    print(f"\nGap Summary:")
    for gap, count in sorted(stats['gap_summary'].items(), key=lambda x: -x[1]):
        print(f"  {gap}: {count} files")


def main():
    """Entry point principal"""
    parser = argparse.ArgumentParser(
        description="SISAS - Signal-Irrigated System for Analytical Support"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    subparsers = parser. add_subparsers(dest="command", help="Commands")
    
    # Comando:  run
    run_parser = subparsers.add_parser("run", help="Run irrigation")
    run_parser.add_argument("--csv-path", required=True, help="Path to sabana CSV")
    run_parser.add_argument("--base-path", default="", help="Base path for canonical files")
    run_parser.add_argument("--phase", help="Execute specific phase")
    run_parser.add_argument("--all", action="store_true", help="Execute all irrigable routes")
    run_parser.set_defaults(func=run_irrigation)
    
    # Comando: check
    check_parser = subparsers.add_parser("check", help="Check vocabulary alignment")
    check_parser.set_defaults(func=check_alignment)
    
    # Comando: contracts
    contracts_parser = subparsers.add_parser("contracts", help="Generate irrigation contracts")
    contracts_parser.add_argument("--csv-path", required=True, help="Path to sabana CSV")
    contracts_parser. add_argument("--output", help="Output path for contracts JSON")
    contracts_parser.set_defaults(func=generate_contracts)
    
    # Comando: stats
    stats_parser = subparsers.add_parser("stats", help="Show irrigation statistics")
    stats_parser.add_argument("--csv-path", required=True, help="Path to sabana CSV")
    stats_parser.set_defaults(func=show_stats)
    
    args = parser.parse_args()
    
    if not args.command:
        parser. print_help()
        return
    
    setup_logging(args.log_level)
    args.func(args)


if __name__ == "__main__": 
    main()
10.2 Comandos de Uso

bash
# =============================================================================
# COMANDOS DE EJECUCIÓN SISAS
# =============================================================================

# 1. Ver estadísticas del sistema
python -m src.farfan_pipeline.infrastructure.irrigation_using_signals. SISAS.main \
    stats --csv-path sabana_final_decisiones.csv

# 2. Verificar alineación de vocabularios
python -m src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    check

# 3. Generar contratos de irrigación
python -m src. farfan_pipeline.infrastructure. irrigation_using_signals.SISAS.main \
    contracts --csv-path sabana_final_decisiones.csv \
    --output _registry/irrigation_contracts.json

# 4. Ejecutar irrigación de una fase específica
python -m src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    run --csv-path sabana_final_decisiones.csv \
    --base-path src/farfan_pipeline/data \
    --phase phase_0

# 5. Ejecutar todas las rutas irrigables
python -m src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main \
    run --csv-path sabana_final_decisiones.csv \
    --base-path src/farfan_pipeline/data \
    --all

# 6. Ejecutar con logging detallado
python -m src.farfan_pipeline. infrastructure.irrigation_using_signals. SISAS.main \
    --log-level DEBUG \
    run --csv-path sabana_final_decisiones.csv \
    --all
XI. TESTS COMPLETOS

11.1 Test Suite Principal

Python
# tests/test_sisas/test_core. py

import pytest
from datetime import datetime
from uuid import uuid4

from src.farfan_pipeline.infrastructure.irrigation_using_signals. SISAS.core.signal import (
    Signal, SignalContext, SignalSource, SignalCategory, SignalConfidence
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import (
    Event, EventStore, EventType, EventPayload
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import (
    PublicationContract, ConsumptionContract, IrrigationContract,
    ContractRegistry, ContractStatus, SignalTypeSpec
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS. core.bus import (
    SignalBus, BusRegistry, BusType, BusMessage
)


class TestSignalContext:
    """Tests para SignalContext"""
    
    def test_create_context(self):
        context = SignalContext(
            node_type="question",
            node_id="Q147",
            phase="phase_0",
            consumer_scope="Phase_0"
        )
        assert context.node_type == "question"
        assert context.node_id == "Q147"
    
    def test_context_to_dict(self):
        context = SignalContext(
            node_type="policy_area",
            node_id="PA03",
            phase="phase_2",
            consumer_scope="Phase_2"
        )
        d = context.to_dict()
        assert d["node_type"] == "policy_area"
        assert d["node_id"] == "PA03"
    
    def test_context_from_dict(self):
        data = {
            "node_type": "dimension",
            "node_id":  "DIM01",
            "phase": "phase_0",
            "consumer_scope": "Phase_0"
        }
        context = SignalContext.from_dict(data)
        assert context.node_type == "dimension"


class TestSignalSource:
    """Tests para SignalSource"""
    
    def test_create_source(self):
        source = SignalSource(
            event_id=str(uuid4()),
            source_file="questions.json",
            source_path="dimensions/DIM01/questions.json",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle="signal_registry"
        )
        assert source.generator_vehicle == "signal_registry"
    
    def test_source_to_dict(self):
        source = SignalSource(
            event_id="evt-123",
            source_file="metadata.json",
            source_path="clusters/CL01/metadata.json",
            generation_timestamp=datetime(2026, 1, 14, 10, 0, 0),
            generator_vehicle="signal_loader"
        )
        d = source.to_dict()
        assert d["event_id"] == "evt-123"
        assert "2026-01-14" in d["generation_timestamp"]


class TestEventStore:
    """Tests para EventStore"""
    
    def test_append_event(self):
        store = EventStore()
        event = Event(
            event_type=EventType.CANONICAL_DATA_LOADED,
            source_file="test.json",
            phase="phase_0"
        )
        event_id = store.append(event)
        assert event_id == event.event_id
        assert store.count() == 1
    
    def test_get_by_type(self):
        store = EventStore()
        
        e1 = Event(event_type=EventType.CANONICAL_DATA_LOADED, source_file="a.json")
        e2 = Event(event_type=EventType.CANONICAL_DATA_VALIDATED, source_file="b.json")
        e3 = Event(event_type=EventType.CANONICAL_DATA_LOADED, source_file="c.json")
        
        store.append(e1)
        store.append(e2)
        store.append(e3)
        
        loaded = store.get_by_type(EventType.CANONICAL_DATA_LOADED)
        assert len(loaded) == 2
    
    def test_get_by_phase(self):
        store = EventStore()
        
        e1 = Event(event_type=EventType.CANONICAL_DATA_LOADED, phase="phase_0")
        e2 = Event(event_type=EventType.CANONICAL_DATA_LOADED, phase="phase_1")
        e3 = Event(event_type=EventType.CANONICAL_DATA_LOADED, phase="phase_0")
        
        store.append(e1)
        store.append(e2)
        store.append(e3)
        
        phase0 = store.get_by_phase("phase_0")
        assert len(phase0) == 2
    
    def test_events_never_lost(self):
        """Axioma:  Ningún evento se pierde"""
        store = EventStore()
        
        for i in range(1000):
            event = Event(
                event_type=EventType. CANONICAL_DATA_LOADED,
                source_file=f"file_{i}.json"
            )
            store.append(event)
        
        assert store.count() == 1000


class TestContracts:
    """Tests para contratos"""
    
    def test_publication_contract_validation(self):
        contract = PublicationContract(
            contract_id="PC_TEST",
            publisher_vehicle="signal_registry",
            allowed_signal_types=[
                SignalTypeSpec(signal_type="StructuralAlignmentSignal"),
                SignalTypeSpec(signal_type="EventPresenceSignal")
            ],
            allowed_buses=["structural_bus", "integrity_bus"],
            require_context=True,
            require_source=True
        )
        
        # Crear señal mock para validación
        from src.farfan_pipeline.infrastructure.irrigation_using_signals. SISAS.signals. types. structural import (
            StructuralAlignmentSignal, AlignmentStatus
        )
        
        context = SignalContext(
            node_type="test",
            node_id="test-1",
            phase="phase_0",
            consumer_scope="Test"
        )
        source = SignalSource(
            event_id="evt-1",
            source_file="test.json",
            source_path="test/test.json",
            generation_timestamp=datetime. utcnow(),
            generator_vehicle="test"
        )
        
        signal = StructuralAlignmentSignal(
            context=context,
            source=source,
            alignment_status=AlignmentStatus. ALIGNED
        )
        
        is_valid, errors = contract.validate_signal(signal)
        assert is_valid
        assert len(errors) == 0
    
    def test_consumption_contract_filtering(self):
        contract = ConsumptionContract(
            contract_id="CC_TEST",
            consumer_id="test_consumer",
            consumer_phase="phase_0",
            subscribed_signal_types=["StructuralAlignmentSignal"],
            context_filters={
                "phase": ["phase_0", "phase_1"],
                "node_type": ["question", "dimension"]
            }
        )
        
        # Mock signal que coincide
        class MockSignal:
            signal_type = "StructuralAlignmentSignal"
            context = SignalContext(
                node_type="question",
                node_id="Q001",
                phase="phase_0",
                consumer_scope="Phase_0"
            )
        
        assert contract.matches_signal(MockSignal())
        
        # Mock signal que NO coincide (tipo incorrecto)
        class MockSignal2:
            signal_type = "OtherSignal"
            context = SignalContext(
                node_type="question",
                node_id="Q001",
                phase="phase_0",
                consumer_scope="Phase_0"
            )
        
        assert not contract.matches_signal(MockSignal2())
    
    def test_irrigation_contract_irrigability(self):
        # Contrato completo - puede irrigar
        contract1 = IrrigationContract(
            contract_id="IC_COMPLETE",
            source_file="test.json",
            source_path="test/test.json",
            source_phase="phase_0",
            vehicles=["signal_registry"],
            consumers=["consumer_1"],
            vocabulary_aligned=True,
            gaps=[],
            status=ContractStatus.ACTIVE
        )
        assert contract1.is_irrigable()
        
        # Contrato sin vehículos - NO puede irrigar
        contract2 = IrrigationContract(
            contract_id="IC_NO_VEHICLE",
            source_file="test2.json",
            source_path="test/test2.json",
            source_phase="phase_0",
            vehicles=[],
            consumers=["consumer_1"],
            vocabulary_aligned=True,
            gaps=["NECESITA_VEHICULO"],
            status=ContractStatus.DRAFT
        )
        assert not contract2.is_irrigable()
        assert "NECESITA_VEHICULO" in contract2.get_blocking_gaps()


class TestBus:
    """Tests para buses de señales"""
    
    def test_bus_creation(self):
        bus = SignalBus(
            bus_type=BusType.STRUCTURAL,
            name="test_structural_bus"
        )
        assert bus. name == "test_structural_bus"
        assert bus.get_subscriber_count() == 0
    
    def test_bus_registry_creation(self):
        registry = BusRegistry()
        
        # Debe crear buses por defecto
        assert registry. get_bus("structural_bus") is not None
        assert registry.get_bus("epistemic_bus") is not None
        assert registry.get_bus("universal_bus") is not None
    
    def test_bus_subscription(self):
        registry = BusRegistry()
        bus = registry.get_bus("structural_bus")
        
        contract = ConsumptionContract(
            contract_id="CC_SUB_TEST",
            consumer_id="test_consumer",
            consumer_phase="phase_0",
            subscribed_signal_types=["StructuralAlignmentSignal"],
            subscribed_buses=["structural_bus"]
        )
        
        success = bus.subscribe(contract)
        assert success
        assert bus. get_subscriber_count() == 1
    
    def test_bus_stats(self):
        bus = SignalBus(bus_type=BusType. STRUCTURAL)
        stats = bus.get_stats()
        
        assert "total_published" in stats
        assert "total_delivered" in stats
        assert "total_rejected" in stats
        assert "total_errors" in stats
11.2 Tests de Señales

Python
# tests/test_sisas/test_signals.py

import pytest
from datetime import datetime

from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
    SignalContext, SignalSource, SignalCategory, SignalConfidence
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals.types.structural import (
    StructuralAlignmentSignal, AlignmentStatus,
    SchemaConflictSignal, CanonicalMappingSignal
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals. SISAS.signals.types.epistemic import (
    AnswerDeterminacySignal, DeterminacyLevel,
    AnswerSpecificitySignal, SpecificityLevel,
    EmpiricalSupportSignal, EmpiricalSupportLevel
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals. types.contrast import (
    DecisionDivergenceSignal, DivergenceType, DivergenceSeverity
)


@pytest.fixture
def sample_context():
    return SignalContext(
        node_type="question",
        node_id="Q147",
        phase="phase_0",
        consumer_scope="Phase_0"
    )


@pytest.fixture
def sample_source():
    return SignalSource(
        event_id="evt-test-123",
        source_file="Q147.json",
        source_path="dimensions/DIM06/questions/Q147.json",
        generation_timestamp=datetime. utcnow(),
        generator_vehicle="signal_context_scoper"
    )


class TestStructuralSignals:
    """Tests para señales estructurales"""
    
    def test_structural_alignment_signal(self, sample_context, sample_source):
        signal = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.ALIGNED,
            canonical_path="dimensions/DIM06/questions/Q147",
            actual_path="dimensions/DIM06/questions/Q147.json",
            missing_elements=[],
            extra_elements=[]
        )
        
        assert signal.signal_type == "StructuralAlignmentSignal"
        assert signal.category == SignalCategory.STRUCTURAL
        assert signal.alignment_status == AlignmentStatus. ALIGNED
        assert signal.compute_alignment_score() == 1.0
    
    def test_alignment_score_partial(self, sample_context, sample_source):
        signal = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.PARTIAL,
            canonical_path="test",
            actual_path="test",
            missing_elements=["field1"],
            extra_elements=["field2"]
        )
        
        score = signal.compute_alignment_score()
        assert 0 < score < 1.0
    
    def test_canonical_mapping_signal(self, sample_context, sample_source):
        signal = CanonicalMappingSignal(
            context=sample_context,
            source=sample_source,
            source_item_id="Q147",
            mapped_entities={
                "policy_area": "PA03",
                "dimension": "DIM06",
                "cluster": "CL01"
            },
            unmapped_aspects=[],
            mapping_completeness=1.0
        )
        
        assert signal.signal_type == "CanonicalMappingSignal"
        assert signal.mapped_entities["policy_area"] == "PA03"


class TestEpistemicSignals:
    """Tests para señales epistémicas"""
    
    def test_determinacy_signal_high(self, sample_context, sample_source):
        signal = AnswerDeterminacySignal(
            context=sample_context,
            source=sample_source,
            question_id="Q147",
            determinacy_level=DeterminacyLevel.HIGH,
            affirmative_markers=["sí", "existe", "cuenta con"],
            ambiguity_markers=[],
            negation_markers=[]
        )
        
        assert signal.signal_type == "AnswerDeterminacySignal"
        assert signal.category == SignalCategory.EPISTEMIC
        assert signal.determinacy_level == DeterminacyLevel.HIGH
    
    def test_determinacy_signal_medium(self, sample_context, sample_source):
        signal = AnswerDeterminacySignal(
            context=sample_context,
            source=sample_source,
            question_id="Q147",
            determinacy_level=DeterminacyLevel.MEDIUM,
            affirmative_markers=["sí"],
            ambiguity_markers=["en algunos casos"],
            negation_markers=[]
        )
        
        assert signal.determinacy_level == DeterminacyLevel.MEDIUM
        assert "en algunos casos" in signal.ambiguity_markers
    
    def test_specificity_signal(self, sample_context, sample_source):
        signal = AnswerSpecificitySignal(
            context=sample_context,
            source=sample_source,
            question_id="Q147",
            specificity_level=SpecificityLevel.LOW,
            expected_elements=["formal_instrument", "institutional_owner", "mandatory_scope"],
            found_elements=["institutional_owner"],
            missing_elements=["formal_instrument", "mandatory_scope"],
            specificity_score=0.33
        )
        
        assert signal.signal_type == "AnswerSpecificitySignal"
        assert signal.specificity_level == SpecificityLevel.LOW
        assert len(signal.missing_elements) == 2
    
    def test_empirical_support_signal(self, sample_context, sample_source):
        signal = EmpiricalSupportSignal(
            context=sample_context,
            source=sample_source,
            question_id="Q147",
            support_level=EmpiricalSupportLevel. MODERATE,
            normative_references=["Ley 1448 de 2011"],
            document_references=[],
            institutional_references=["Unidad de Víctimas"]
        )
        
        assert signal.signal_type == "EmpiricalSupportSignal"
        assert signal.support_level == EmpiricalSupportLevel.MODERATE
        assert "Ley 1448 de 2011" in signal.normative_references


class TestContrastSignals: 
    """Tests para señales de contraste"""
    
    def test_decision_divergence_signal(self, sample_context, sample_source):
        signal = DecisionDivergenceSignal(
            context=sample_context,
            source=sample_source,
            item_id="Q147",
            legacy_value="COMPLIANT",
            legacy_source="legacy_system_v1",
            signal_based_value="INDETERMINATE",
            supporting_signals=["AnswerDeterminacySignal", "EmpiricalSupportSignal"],
            divergence_type=DivergenceType.CLASSIFICATION_MISMATCH,
            divergence_severity=DivergenceSeverity.HIGH
        )
        
        assert signal.signal_type == "DecisionDivergenceSignal"
        assert signal.category == SignalCategory.CONTRAST
        assert signal.legacy_value != signal.signal_based_value
        assert signal.divergence_severity == DivergenceSeverity.HIGH


class TestSignalDeterminism:
    """Tests para el axioma:  deterministic (mismo input → misma señal)"""
    
    def test_same_input_same_hash(self, sample_context, sample_source):
        """El mismo input debe producir el mismo hash"""
        signal1 = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.ALIGNED,
            canonical_path="test/path",
            actual_path="test/path"
        )
        
        signal2 = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus. ALIGNED,
            canonical_path="test/path",
            actual_path="test/path"
        )
        
        # Los hashes deben ser idénticos
        assert signal1.compute_hash() == signal2.compute_hash()
    
    def test_different_input_different_hash(self, sample_context, sample_source):
        """Diferente input debe producir diferente hash"""
        signal1 = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.ALIGNED,
            canonical_path="test/path1",
            actual_path="test/path1"
        )
        
        signal2 = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.MISALIGNED,  # Diferente
            canonical_path="test/path2",
            actual_path="test/path2"
        )
        
        assert signal1.compute_hash() != signal2.compute_hash()
11.3 Tests de Irrigación

Python
# tests/test_sisas/test_irrigation.py

import pytest
import json
import tempfile
from pathlib import Path

from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation. irrigation_map import (
    IrrigationMap, IrrigationRoute, IrrigationSource, IrrigationTarget,
    IrrigabilityStatus
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_executor import (
    IrrigationExecutor, IrrigationResult
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS. vehicles.signal_registry import (
    SignalRegistryVehicle
)
from src.farfan_pipeline.infrastructure. irrigation_using_signals.SISAS.core.bus import BusRegistry
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS. core.contracts import ContractRegistry
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core. event import EventStore


class TestIrrigationMap: 
    """Tests para el mapa de irrigación"""
    
    def test_create_route(self):
        source = IrrigationSource(
            file_path="clusters/CL01/metadata.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=["signal_registry"],
            consumers=["phase0_bootstrap. py"],
            irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
            gaps=[],
            added_value="YES",
            file_bytes=5000
        )
        
        route = IrrigationRoute(
            source=source,
            vehicles=["signal_registry"],
            targets=[IrrigationTarget(
                consumer_id="phase0_bootstrap. py",
                consumer_phase="phase_0"
            )],
            is_active=True
        )
        
        assert route.source. irrigability == IrrigabilityStatus.IRRIGABLE_NOW
        assert route.is_active
    
    def test_add_route_to_map(self):
        irrigation_map = IrrigationMap()
        
        source = IrrigationSource(
            file_path="test/test.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=["signal_registry"],
            consumers=["consumer1"],
            irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
            gaps=[]
        )
        
        route = IrrigationRoute(
            source=source,
            vehicles=["signal_registry"],
            targets=[IrrigationTarget(consumer_id="consumer1", consumer_phase="phase_0")],
            is_active=True
        )
        
        irrigation_map.add_route(route)
        
        assert len(irrigation_map.routes) == 1
        assert irrigation_map.get_irrigable_now()[0] == route
    
    def test_get_routes_by_phase(self):
        irrigation_map = IrrigationMap()
        
        # Agregar rutas de diferentes fases
        for phase in ["Phase_0", "Phase_1", "Phase_0"]:
            source = IrrigationSource(
                file_path=f"test/{phase}/file.json",
                stage=phase. lower(),
                phase=phase,
                vehicles=["signal_registry"],
                consumers=[],
                irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
                gaps=[]
            )
            route = IrrigationRoute(source=source, vehicles=["signal_registry"])
            irrigation_map.add_route(route)
        
        phase0_routes = irrigation_map.get_routes_for_phase("Phase_0")
        assert len(phase0_routes) == 2
    
    def test_get_blocked_routes(self):
        irrigation_map = IrrigationMap()
        
        # Ruta bloqueada
        source1 = IrrigationSource(
            file_path="blocked/file. json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=[],  # Sin vehículo
            consumers=[],
            irrigability=IrrigabilityStatus.NOT_IRRIGABLE_YET,
            gaps=["NECESITA_VEHICULO", "NECESITA_CONSUMIDOR"]
        )
        route1 = IrrigationRoute(source=source1)
        irrigation_map.add_route(route1)
        
        # Ruta no bloqueada
        source2 = IrrigationSource(
            file_path="ok/file.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=["signal_registry"],
            consumers=["consumer1"],
            irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
            gaps=[]
        )
        route2 = IrrigationRoute(source=source2, vehicles=["signal_registry"])
        irrigation_map.add_route(route2)
        
        blocked = irrigation_map.get_blocked_routes()
        assert len(blocked) == 1
        assert "NECESITA_VEHICULO" in blocked[0][1]
    
    def test_statistics(self):
        irrigation_map = IrrigationMap()
        
        # Agregar varias rutas
        statuses = [
            IrrigabilityStatus.IRRIGABLE_NOW,
            IrrigabilityStatus.IRRIGABLE_NOW,
            IrrigabilityStatus.NOT_IRRIGABLE_YET,
            IrrigabilityStatus. DEFINITELY_NOT
        ]
        
        for i, status in enumerate(statuses):
            source = IrrigationSource(
                file_path=f"test/file_{i}.json",
                stage="phase_0",
                phase="Phase_0",
                vehicles=["v1"] if status == IrrigabilityStatus. IRRIGABLE_NOW else [],
                consumers=[],
                irrigability=status,
                gaps=[] if status == IrrigabilityStatus.IRRIGABLE_NOW else ["GAP"]
            )
            route = IrrigationRoute(source=source)
            irrigation_map.add_route(route)
        
        stats = irrigation_map.get_statistics()
        assert stats["total_routes"] == 4
        assert stats["irrigable_now"] == 2
        assert stats["not_irrigable_yet"] == 1
        assert stats["definitely_not"] == 1


class TestIrrigationExecutor:
    """Tests para el ejecutor de irrigación"""
    
    @pytest.fixture
    def executor(self):
        bus_registry = BusRegistry()
        contract_registry = ContractRegistry()
        event_store = EventStore()
        
        executor = IrrigationExecutor(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store
        )
        
        # Registrar vehículo
        vehicle = SignalRegistryVehicle(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store
        )
        executor.register_vehicle(vehicle)
        
        return executor
    
    @pytest.fixture
    def temp_canonical_file(self):
        """Crea archivo canónico temporal para tests"""
        with tempfile. NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        ) as f:
            json. dump({
                "id": "TEST_001",
                "name": "Test File",
                "description": "Test canonical file",
                "version": "1.0.0",
                "questions": []
            }, f)
            return f.name
    
    def test_register_vehicle(self, executor):
        assert "signal_registry" in executor.vehicles
    
    def test_execute_route_success(self, executor, temp_canonical_file):
        source = IrrigationSource(
            file_path=temp_canonical_file,
            stage="phase_0",
            phase="Phase_0",
            vehicles=["signal_registry"],
            consumers=["test_consumer"],
            irrigability=IrrigabilityStatus. IRRIGABLE_NOW,
            gaps=[]
        )
        
        route = IrrigationRoute(
            source=source,
            vehicles=["signal_registry"],
            targets=[IrrigationTarget(
                consumer_id="test_consumer",
                consumer_phase="phase_0"
            )],
            is_active=True
        )
        
        result = executor.execute_route(route)
        
        assert result. success
        assert len(result. signals_generated) > 0
        assert "test_consumer" in result.consumers_notified
    
    def test_execute_route_blocked(self, executor):
        source = IrrigationSource(
            file_path="nonexistent/file.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=[],  # Sin vehículo
            consumers=[],
            irrigability=IrrigabilityStatus.NOT_IRRIGABLE_YET,
            gaps=["NECESITA_VEHICULO"]
        )
        
        route = IrrigationRoute(source=source)
        
        result = executor.execute_route(route)
        
        assert not result.success
        assert len(result.errors) > 0
    
    def test_execution_summary(self, executor, temp_canonical_file):
        # Ejecutar algunas rutas
        for i in range(3):
            source = IrrigationSource(
                file_path=temp_canonical_file,
                stage="phase_0",
                phase="Phase_0",
                vehicles=["signal_registry"],
                consumers=["consumer"],
                irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
                gaps=[]
            )
            route = IrrigationRoute(
                source=source,
                vehicles=["signal_registry"],
                targets=[IrrigationTarget(consumer_id="consumer", consumer_phase="phase_0")]
            )
            executor.execute_route(route)
        
        summary = executor.get_execution_summary()
        
        assert summary["total_executions"] == 3
        assert summary["successful"] == 3
        assert summary["failed"] == 0
        assert summary["total_signals_generated"] > 0
XII. RESUMEN EJECUTIVO FINAL

12.1 Estado Actual del Canonic Central

Code
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ESTADO DEL CANONIC CENTRAL - SISAS                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  TOTAL ARCHIVOS CANÓNICOS: 140                                               ║
║  ─────────────────────────────────────────────────────────────────────────   ║
║                                                                              ║
║  ✅ IRRIGABLE_NOW:            126 archivos (90%)                              ║
║     └─ Listos para irrigar sin modificaciones                                ║
║                                                                              ║
║  ⏳ NOT_IRRIGABLE_YET:        14 archivos (10%)                               ║
║     └─ Requieren resolución de gaps específicos                              ║
║                                                                              ║
║  ❌ DEFINITELY_NOT:          0 archivos en canonic central                   ║
║     └─ (Los MARGINAL fueron excluidos del análisis)                          ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                         GAPS IDENTIFICADOS                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🔧 NECESITA_VEHICULO:              33 archivos                              ║
║     └─ Resolución:  Asignar signal_intelligence_layer, signal_loader          ║
║                                                                              ║
║  👤 NECESITA_CONSUMIDOR:            11 archivos                              ║
║     └─ Resolución: Crear phase7_meso_consumer. py, validation_consumer.py     ║
║                                                                              ║
║  📚 VOCAB_SEÑALES_NO_ALINEADO:      37 archivos                              ║
║     └─ Resolución: Mapear a tipos de señales en SignalVocabulary             ║
║                                                                              ║
║  🔗 VOCAB_CAPACIDADES_NO_ALINEADO:  15 archivos                              ║
║     └─ Resolución: Declarar capacidades en CapabilityVocabulary              ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                         ARQUITECTURA SISAS                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  SEÑALES DEFINIDAS:         18 tipos                                         ║
║     ├─ Structural:    3 (Alignment, Schema, Mapping)                          ║
║     ├─ Integrity:    3 (Presence, Completeness, DataIntegrity)               ║
║     ├─ Epistemic:    4 (Determinacy, Specificity, Support, Method)           ║
║     ├─ Contrast:     3 (Divergence, ConfidenceDrop, Temporal)                ║
║     ├─ Operational:  4 (Execution, Failure, LegacyActivity, Dependency)      ║
║     └─ Consumption:  3 (Frequency, TemporalCoupling, ConsumerHealth)         ║
║                                                                              ║
║  VEHÍCULOS IMPLEMENTADOS:   9                                                ║
║     ├─ signal_registry (core)                                                ║
║     ├─ signal_context_scoper                                                 ║
║     ├─ signal_evidence_extractor                                             ║
║     ├─ signal_intelligence_layer                                             ║
║     ├─ signal_loader                                                         ║
║     ├─ signal_quality_metrics                                                ║
║     ├─ signal_irrigator                                                      ║
║     ├─ signal_enhancement_integrator                                         ║
║     └─ signals (agregador)                                                   ║
║                                                                              ║
║  BUSES CONFIGURADOS:        7                                                ║
║     ├─ structural_bus                                                        ║
║     ├─ integrity_bus                                                         ║
║     ├─ epistemic_bus                                                         ║
║     ├─ contrast_bus                                                          ║
║     ├─ operational_bus                                                       ║
║     ├─ consumption_bus                                                       ║
║     └─ universal_bus                                                         ║
║                                                                              ║
║  CONSUMIDORES:               12                                               ║
║     ├─ Phase 0: 3 (bootstrap, providers, wiring_types)                       ║
║     ├─ Phase 1: 2 (signal_enrichment, cpp_ingestion)                         ║
║     ├─ Phase 2: 7 (factory, executor, synchronizer, etc.)                    ║
║     ├─ Phase 3: 1 (signal_enriched_scoring)                                  ║
║     ├─ Phase 7: 1 (NUEVO - meso_consumer) ← A CREAR                          ║
║     └─ Phase 8: 1 (signal_enriched_recommendations)                          ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                         PLAN DE IMPLEMENTACIÓN                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Semana 1-2:   Infraestructura Core (Signal, Event, Bus, Contracts)          ║
║  Semana 3:     Tipos de Señales (18 tipos)                                   ║
║  Semana 4-5:   Vehículos (9 implementaciones)                                ║
║  Semana 6:     Vocabularios y Alineación                                     ║
║  Semana 7-8:   Sistema de Irrigación                                         ║
║  Semana 9-10:  Consumidores (12 implementaciones)                            ║
║  Semana 11:    Auditoría y Contraste Legacy                                  ║
║  Semana 12:    Integración Final y Migración                                 ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                         CRITERIOS DE ÉXITO                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ✓ El legacy puede apagarse y nada deja de ser observable                    ║
║  ✓ Las decisiones pueden justificarse solo con señales                       ║
║  ✓ Cualquier consumidor puede ser auditado                                   ║
║  ✓ Ningún evento se pierde                                                   ║
║  ✓ Ninguna señal es huérfana                                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
12.2 Archivos a Crear

Code
src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/
├── __init__.py
├── main.py                              # Entry point CLI
│
├── core/
│   ├── __init__.py
│   ├── signal. py                        # ~200 líneas
│   ├── event.py                         # ~250 líneas
│   ├── contracts.py                     # ~400 líneas
│   └── bus.py                           # ~300 líneas
│
├── signals/
│   ├── __init__.py
│   ├── registry.py                      # ~100 líneas
│   └── types/
│       ├── __init__.py
│       ├── structural.py                # ~150 líneas
│       ├── integrity.py                 # ~120 líneas
│       ├── epistemic.py                 # ~200 líneas
│       ├── contrast.py                  # ~150 líneas
│       ├── operational.py               # ~180 líneas
│       └── consumption.py               # ~100 líneas
│
├── vehicles/
│   ├── __init__.py
│   ├── base_vehicle.py                  # ~200 líneas
│   ├── signal_registry. py               # ~250 líneas
│   ├── signal_context_scoper. py         # ~200 líneas
│   ├── signal_evidence_extractor.py     # ~180 líneas
│   ├── signal_intelligence_layer.py     # ~200 líneas
│   ├── signal_loader.py                 # ~150 líneas
│   ├── signal_quality_metrics.py        # ~150 líneas
│   ├── signal_irrigator.py              # ~180 líneas
│   ├── signal_enhancement_integrator. py # ~180 líneas
│   └── signals.py                       # ~100 líneas
│
├── consumers/
│   ├── __init__.py
│   ├── base_consumer.py                 # ~150 líneas
│   ├── phase0/
│   │   └── *. py                         # 3 archivos
│   ├── phase1/
│   │   └── *.py                         # 2 archivos
│   ├── phase2/
│   │   └── *.py                         # 7 archivos
│   ├── phase3/
│   │   └── *.py                         # 1 archivo
│   ├── phase7/
│   │   └── phase7_meso_consumer.py      # NUEVO
│   └── phase8/
│       └── *. py                         # 1 archivo
│
├── irrigation/
│   ├── __init__.py
│   ├── irrigation_map.py                # ~300 líneas
│   ├── irrigation_executor.py           # ~400 líneas
│   └── irrigation_validator.py          # ~150 líneas
│
├── vocabulary/
│   ├── __init__.py
│   ├── signal_vocabulary.py             # ~400 líneas
│   ├── capability_vocabulary.py         # ~250 líneas
│   └── alignment_checker.py             # ~300 líneas
│
├── audit/
│   ├── __init__.py
│   ├── signal_auditor.py                # ~200 líneas
│   ├── consumer_auditor.py              # ~150 líneas
│   └── decision_auditor.py              # ~200 líneas
│
├── schemas/
│   ├── signal_schema.json
│   ├── event_schema.json
│   ├── contract_schema.json
│   └── irrigation_spec_schema.json
│
├── config/
│   ├── __init__.py
│   ├── bus_config.yaml
│   ├── irrigation_config.yaml
│   └── vocabulary_config.yaml
│
└── scripts/
    ├── __init__.py
    └── generate_contracts.py            # ~200 líneas

TOTAL ESTIMADO: ~6,000 líneas de código Python + configs
12.3 Próximos Pasos Inmediatos

YAML
SEMANA_1_TAREAS:
  día_1_2:
    - "Crear estructura de directorios"
    - "Implementar core/signal.py"
    - "Implementar core/event.py"
    - "Tests unitarios para Signal y Event"
    
  día_3_4:
    - "Implementar core/contracts.py"
    - "Implementar core/bus.py"
    - "Tests unitarios para Contracts y Bus"
    
  día_5:
    - "Integración core completo"
    - "Tests de integración"
    - "Documentación de core"

COMANDOS_INICIALES:
  # Crear estructura
  mkdir -p src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/{core,signals/types,vehicles,consumers,irrigation,vocabulary,audit,schemas,config,scripts}
  
  # Crear __init__.py en todos los directorios
  find src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS -type d -exec touch {}/__init__.py \;
  
  # Copiar código de esta especificación a archivos
  # (manual o script de extracción)
