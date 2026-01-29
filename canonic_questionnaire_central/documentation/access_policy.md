DOCUMENTO MAESTRO: POLÍTICA DE ACCESO AL CUESTIONARIO
=======================================================
**Estado**: FROZEN ❄️ | **Fecha**: 2026-01-26 | **Ver**: `CANONIC_FREEZE_MANIFEST.md`

PARTE I: DECLARACIÓN DE POLÍTICA

1.1 PROPÓSITO

Esta política establece el régimen de acceso al archivo canonic_questionnaire_central/questionnaire_monolith. json (67K+ líneas, 300 micro preguntas, 4 meso, 1 macro) para garantizar:

Acceso ordenado: Eliminación de acceso caótico y no trazable
Aprovechamiento de riqueza: Uso medible de patrones, validaciones, elementos esperados
Determinismo: Cada acceso es auditable y reproducible
Arquitectura de 3 niveles: Separación estricta entre I/O, distribución y consumo
1.2 ARQUITECTURA DE 3 NIVELES

Code
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NIVEL 1: FACTORY                                   │
│                        (Acceso Total - I/O Único)                           │
│                                                                              │
│  Archivo: src/orchestration/factory.py                                       │
│  Clases:   CanonicalQuestionnaire, load_questionnaire()                      │
│  Scope:   Lectura completa del monolito + verificación SHA256               │
│  Regla:   ÚNICO punto de I/O autorizado en todo el sistema                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ Inyecta CanonicalQuestionnaire
┌─────────────────────────────────────────────────────────────────────────────┐
│                      NIVEL 2: ORQUESTADOR / SISAS                           │
│                    (Acceso Parcial Recurrente)                              │
│                                                                              │
│  Archivos:                                                                    │
│    - src/orchestration/factory. py (QuestionnaireSignalRegistry)             │
│    - src/cross_cutting_infrastrucuture/. ../SISAS/signal_registry.py         │
│    - src/cross_cutting_infrastrucuture/.../SISAS/signal_loader.py           │
│    - src/canonic_phases/Phase_zero/bootstrap.py (QuestionnaireResourceProvider)│
│                                                                              │
│  Scope:   Extrae subconjuntos por tipo (chunking, micro, validation, etc.)  │
│  Regla:   Recibe CanonicalQuestionnaire, NO hace I/O                        │
│  Output:  SignalPack, EnrichedSignalPack filtrados por policy_area          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ Inyecta SignalPack/EnrichedSignalPack
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NIVEL 3: CONSUMIDORES                                 │
│                      (Acceso Granular por Scope)                            │
│                                                                              │
│  Archivos:                                                                    │
│    - src/cross_cutting_infrastrucuture/.../SISAS/signal_intelligence_layer.py│
│    - src/cross_cutting_infrastrucuture/.../SISAS/signal_context_scoper.py   │
│    - src/cross_cutting_infrastrucuture/.../SISAS/signal_evidence_extractor.py│
│    - src/cross_cutting_infrastrucuture/.../SISAS/signal_contract_validator.py│
│    - src/canonic_phases/Phase_two/evidence_*. py                             │
│    - 30 ejecutores (D1Q1 - D6Q5)                                            │
│                                                                              │
│  Scope:   Solo patrones/elementos relevantes al contexto actual             │
│  Regla:   Recibe SignalPack inyectado, NUNCA accede a CanonicalQuestionnaire│
│  Métodos: get_patterns_for_context(), extract_structured_evidence()         │
└─────────────────────────────────────────────────────────────────────────────┘
1.3 INVARIANTES DE LA POLÍTICA

YAML
invariantes:
  nivel_1:
    - "Solo src/orchestration/factory.py hace I/O del monolito"
    - "load_questionnaire() es la ÚNICA función que lee el archivo"
    - "CanonicalQuestionnaire es frozen (inmutable)"
    - "Hash SHA256 se computa y almacena en cada carga"
    
  nivel_2:
    - "Recibe CanonicalQuestionnaire por inyección, NO por I/O"
    - "Produce SignalPack filtrados por policy_area (PA01-PA10)"
    - "QuestionnaireSignalRegistry cachea señales con LRU"
    - "Cada SignalPack tiene source_hash para trazabilidad"
    
  nivel_3:
    - "NUNCA importa CanonicalQuestionnaire"
    - "NUNCA importa load_questionnaire"
    - "Recibe SignalPack/EnrichedSignalPack como parámetro"
    - "Usa get_patterns_for_context() para filtrado adicional"
    - "Registra consumo en QuestionnaireAccessAudit"
    
  medición:
    - "Todo acceso se registra con:  nivel, accessor, block, keys"
    - "Se mide porcentaje de utilización por bloque"
    - "Violaciones de nivel se registran como violations"
1.4 GRANULARIDAD DE ACCESO POR BLOQUE

Bloque del Monolito	Nivel 1	Nivel 2	Nivel 3
canonical_notation. dimensions	✅ Total	✅ get_dimensions()	❌ Prohibido
canonical_notation.policy_areas	✅ Total	✅ get_policy_areas()	❌ Prohibido
blocks.micro_questions (300)	✅ Total	✅ Por PA/DIM	✅ Por question_id
blocks.micro_questions[]. patterns	✅ Total	✅ Expandidos 5x	✅ Filtrados por contexto
blocks.micro_questions[].expected_elements	✅ Total	✅ Por question	✅ Para validación
blocks.micro_questions[].failure_contract	✅ Total	✅ Por question	✅ Para abort
blocks.micro_questions[].validations	✅ Total	✅ Por question	✅ Para scoring
blocks.meso_questions (4)	✅ Total	✅ Por cluster	❌ Prohibido
blocks.macro_question (1)	✅ Total	✅ Completo	❌ Prohibido
PARTE II: ESTRATEGIA DE PROMPTING AVANZADO

2.1 TÉCNICA: ADVERSARIAL CONTRACT PROMPTING (ACP)

Esta técnica está diseñada para contrarrestar agentes con algoritmos corrompidos que buscan ambigüedades para inyectar mediocridad.

PRINCIPIOS ACP

YAML
principio_1_especificidad_extrema:
  descripción: "Cada instrucción debe ser tan específica que NO admita interpretación"
  ejemplo_malo: "Corrige los imports"
  ejemplo_bueno: "En línea 112 de src/orchestration/factory.py, ELIMINA 'from farfan_pipeline. core.orchestrator.questionnaire import' y NO agregues ningún import alternativo hasta completar JOBFRONT 0"

principio_2_prohibiciones_explícitas:
  descripción:  "Listar TODO lo que está prohibido, no solo lo permitido"
  formato: "PROHIBIDO-XXX:  [acción prohibida] porque [razón verificable]"
  
principio_3_artefactos_verificables:
  descripción: "Cada jobfront produce un artefacto que se puede verificar con comando"
  formato: "ARTEFACTO:  [descripción] | VERIFICACIÓN: [comando bash que retorna OK/FAIL]"
  
principio_4_orden_no_negociable:
  descripción:  "Los jobfronts tienen dependencias explícitas y orden obligatorio"
  formato: "JOBFRONT N requiere: [lista de jobfronts previos completados]"
  
principio_5_anti_escape:
  descripción: "Cerrar todas las rutas de escape que un agente mediocre usaría"
  rutas_cerradas: 
    - "Crear archivo helper/adapter/bridge/compat"
    - "Usar try/except para 'manejar' imports faltantes"
    - "Proponer 'solución temporal mientras se resuelve X'"
    - "Sugerir 'refactorización más amplia en el futuro'"
    - "Dejar código comentado 'para referencia'"
    