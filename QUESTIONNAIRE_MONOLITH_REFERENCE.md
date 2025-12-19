# 📋 GUÍA DEFINITIVA: `questionnaire_monolith.json`

> **Documento de referencia técnica para desarrolladores del pipeline F.A.R.F.A.N**  
> Generado: 11 de diciembre de 2025

---

## 📊 RESUMEN EJECUTIVO

El archivo `questionnaire_monolith.json` es el **artefacto canónico central** del sistema F.A.R.F.A.N. Contiene:

| Componente | Cantidad | Descripción |
|------------|----------|-------------|
| `macro_question` | 1 | Evaluación holística del plan completo |
| `meso_questions` | 4 | Una por cluster (agregación intermedia) |
| `micro_questions` | 300 | Preguntas individuales de evaluación |
| **Total** | **305** | Preguntas en el sistema |

**Estructura jerárquica:**
```
MACRO (1)
  └── MESO (4 clusters)
        └── MICRO (300 preguntas)
              └── patterns[] + method_sets[] + validations{}
```

---

## 1️⃣ `canonical_notation` — DICCIONARIO DE REFERENCIA

### ¿Qué es?
Mapeos canónicos de códigos a nombres. Es el "diccionario" que traduce IDs cortos a nombres completos.

### 1.1 Dimensions (6 dimensiones de la cadena de valor)

```json
"dimensions": {
  "D1": { "code": "DIM01", "name": "INSUMOS", "label": "Diagnóstico y Recursos" },
  "D2": { "code": "DIM02", "name": "ACTIVIDADES", "label": "Diseño de Intervención" },
  "D3": { "code": "DIM03", "name": "PRODUCTOS", "label": "Productos y Outputs" },
  "D4": { "code": "DIM04", "name": "RESULTADOS", "label": "Resultados y Outcomes" },
  "D5": { "code": "DIM05", "name": "IMPACTOS", "label": "Impactos de Largo Plazo" },
  "D6": { "code": "DIM06", "name": "CAUSALIDAD", "label": "Teoría de Cambio" }
}
```

| Código | Nombre | Descripción |
|--------|--------|-------------|
| DIM01 | INSUMOS | Evalúa diagnóstico territorial, líneas base, brechas |
| DIM02 | ACTIVIDADES | Evalúa formalización con responsables, cronogramas, costos |
| DIM03 | PRODUCTOS | Evalúa especificación de bienes/servicios verificables |
| DIM04 | RESULTADOS | Evalúa cambios en población con métricas y metas |
| DIM05 | IMPACTOS | Evalúa transformaciones estructurales de largo plazo |
| DIM06 | CAUSALIDAD | Evalúa teorías de cambio, causas raíz, supuestos |

### 1.2 Policy Areas (10 áreas de política pública)

```json
"policy_areas": {
  "PA01": { "name": "Derechos de las mujeres e igualdad de género", "legacy_id": "P1" },
  "PA02": { "name": "Prevención de la violencia y protección frente al conflicto", "legacy_id": "P2" },
  "PA03": { "name": "Ambiente sano, cambio climático, prevención y atención a desastres", "legacy_id": "P3" },
  "PA04": { "name": "Derechos económicos, sociales y culturales", "legacy_id": "P4" },
  "PA05": { "name": "Derechos de las víctimas y construcción de paz", "legacy_id": "P5" },
  "PA06": { "name": "Derecho al buen futuro de la niñez, adolescencia, juventud", "legacy_id": "P6" },
  "PA07": { "name": "Tierras y territorios", "legacy_id": "P7" },
  "PA08": { "name": "Líderes y defensores de derechos humanos", "legacy_id": "P8" },
  "PA09": { "name": "Crisis de derechos de personas privadas de la libertad", "legacy_id": "P9" },
  "PA10": { "name": "Migración transfronteriza", "legacy_id": "P10" }
}
```

**USO:** Cuando ves `"dimension_id": "DIM01"` en una pregunta, consultas aquí para saber que significa "INSUMOS".

---

## 2️⃣ `macro_question` — LA PREGUNTA GLOBAL

### ¿Qué es?
Evaluación holística del plan completo. Se calcula **DESPUÉS** de todas las micro y meso.

### Ejemplo completo:

```json
"macro_question": {
  "question_id": "MACRO_1",
  "question_global": 305,
  "text": "¿El Plan de Desarrollo presenta una visión integral y coherente que articula todos los clusters y dimensiones?",
  "type": "MACRO",
  "scoring_modality": "MACRO_HOLISTIC",
  "aggregation_method": "holistic_assessment",
  "clusters": ["CL01", "CL02", "CL03", "CL04"],
  
  "patterns": [
    { "type": "narrative_coherence", "description": "Evaluar coherencia narrativa global del plan", "priority": 1 },
    { "type": "cross_cluster_integration", "description": "Verificar integración entre todos los clusters", "priority": 1 },
    { "type": "long_term_vision", "description": "Evaluar visión de largo plazo y transformación estructural", "priority": 2 }
  ],
  
  "fallback": {
    "condition": "always_true",
    "pattern": "MACRO_AMBIGUO",
    "priority": 999
  }
}
```

### ¿Qué es `fallback`?
Es un **"catch-all"**. Si NINGÚN pattern hace match, se emite este código por defecto para no dejar evaluaciones sin respuesta.

---

## 3️⃣ `meso_questions` — PREGUNTAS INTERMEDIAS (4 total)

### ¿Qué es?
Evalúan cómo se integran las policy_areas **DENTRO** de cada cluster.

### Los 4 clusters:

| Cluster | ID | Policy Areas | Descripción |
|---------|-----|--------------|-------------|
| Seguridad y Paz | CL01 | PA02, PA03, PA07 | Seguridad humana, protección de la vida |
| Grupos Poblacionales | CL02 | PA01, PA05, PA06 | Enfoque diferencial y derechos específicos |
| Territorio-Ambiente | CL03 | PA04, PA08 | Sostenibilidad territorial |
| Derechos Sociales & Crisis | CL04 | PA09, PA10 | DESC y gestión de crisis migratoria |

### Ejemplo MESO_1:

```json
{
  "question_id": "MESO_1",
  "question_global": 301,
  "text": "¿Cómo se integran las políticas en el cluster Seguridad y Paz?",
  "cluster_id": "CL01",
  "policy_areas": ["P2", "P3", "P7"],
  "scoring_modality": "MESO_INTEGRATION",
  "aggregation_method": "weighted_average",
  "patterns": [
    { "type": "cross_reference", "description": "Verificar referencias cruzadas entre áreas ['P2', 'P3', 'P7']" },
    { "type": "coherence", "description": "Evaluar coherencia narrativa entre políticas del cluster" }
  ]
}
```

---

## 4️⃣ `micro_questions` — EL NÚCLEO (300 preguntas)

### ¿Qué es?
Las preguntas individuales que evalúan aspectos específicos. Cada una tiene su propio arsenal de patterns y métodos.

### Estructura de una micro_question:

```json
{
  // === IDENTIFICACIÓN ===
  "question_id": "Q001",
  "question_global": 1,
  "base_slot": "D1-Q1",              // Dimensión 1, Pregunta 1 de esa dimensión
  "dimension_id": "DIM01",           // INSUMOS
  "policy_area_id": "PA01",          // Género
  "cluster_id": "CL02",              // Grupos Poblacionales
  
  "text": "¿El diagnóstico presenta datos numéricos (tasas de VBG, porcentajes...) que sirvan como línea base?",
  
  // === SCORING ===
  "scoring_modality": "TYPE_A",
  "scoring_definition_ref": "scoring_modalities.TYPE_A",
  
  // === SUB-ESTRUCTURAS ===
  "expected_elements": [...],
  "failure_contract": {...},
  "method_sets": [...],
  "patterns": [...],
  "validations": {...}
}
```

---

## 5️⃣ `expected_elements` — QUÉ DEBE TENER LA RESPUESTA

### ¿Qué es?
Lista de elementos que el evaluador debe encontrar en el texto para dar puntaje.

### Ejemplo 1: Q001 (Diagnóstico de género)

```json
"expected_elements": [
  { "type": "cobertura_territorial_especificada", "required": true },
  { "type": "fuentes_oficiales", "minimum": 2 },
  { "type": "indicadores_cuantitativos", "minimum": 3 },
  { "type": "series_temporales_años", "minimum": 3 }
]
```

### Ejemplo 2: Q006 (Formato tabular)

```json
"expected_elements": [
  { "type": "formato_tabular", "required": true },
  { "type": "columna_responsable", "required": true },
  { "type": "columna_producto", "required": true },
  { "type": "columna_cronograma", "required": true },
  { "type": "columna_costo", "required": true }
]
```

### Ejemplo 3: Q021 (Impactos de largo plazo)

```json
"expected_elements": [
  { "type": "impacto_definido", "required": true },
  { "type": "ruta_transmision", "required": true },
  { "type": "rezago_temporal", "required": true }
]
```

### Significado de campos:

| Campo | Significado |
|-------|-------------|
| `required: true` | DEBE existir, si no hay → score 0 |
| `minimum: N` | Debe haber al menos N instancias |

---

## 6️⃣ `failure_contract` — QUÉ PASA SI FALLA

### ¿Qué es?
Define cuándo ABORTAR el análisis y qué código de error emitir.

### Ejemplo:

```json
"failure_contract": {
  "abort_if": ["missing_required_element", "incomplete_text"],
  "emit_code": "ABORT-Q001-REQ"
}
```

### Condiciones de aborto posibles:

| Condición | Significado |
|-----------|-------------|
| `missing_required_element` | Falta un `expected_element` con `required: true` |
| `incomplete_text` | El texto está truncado o incompleto |

**Uso:** Si se cumple alguna condición, se emite el código y se marca como fallo determinístico.

---

## 7️⃣ `method_sets` — MÉTODOS PYTHON A EJECUTAR

### ¿Qué es?
Lista **ordenada** de métodos que el pipeline debe invocar para evaluar esta pregunta.

### Ejemplo Q001 (Pregunta de diagnóstico):

```json
"method_sets": [
  {
    "class": "TextMiningEngine",
    "function": "diagnose_critical_links",
    "method_type": "analysis",
    "priority": 1,
    "description": "TextMiningEngine.diagnose_critical_links"
  },
  {
    "class": "IndustrialPolicyProcessor",
    "function": "_extract_point_evidence",
    "method_type": "extraction",
    "priority": 5
  },
  {
    "class": "BayesianNumericalAnalyzer",
    "function": "evaluate_policy_metric",
    "method_type": "analysis",
    "priority": 14,
    "produces_elements": ["posterior_confidence_metric"]
  },
  {
    "class": "PolicyContradictionDetector",
    "function": "_extract_quantitative_claims",
    "method_type": "extraction",
    "priority": 11,
    "depends_on_patterns": ["PAT-Q001-011", "PAT-Q001-006"]
  }
]
```

### Ejemplo Q006 (Pregunta de tablas):

```json
"method_sets": [
  { "class": "PDFProcessor", "function": "extract_tables", "method_type": "extraction", "priority": 1 },
  { "class": "FinancialAuditor", "function": "_process_financial_table", "method_type": "analysis", "priority": 2 },
  { "class": "PDETMunicipalPlanAnalyzer", "function": "_classify_tables", "method_type": "analysis", "priority": 4 }
]
```

### Campos importantes:

| Campo | Descripción |
|-------|-------------|
| `priority` | Orden de ejecución (1 primero, 17 último) |
| `method_type` | `"extraction"` \| `"analysis"` \| `"validation"` \| `"scoring"` |
| `depends_on_patterns` | Solo ejecutar si estos patterns dieron match |
| `produces_elements` | Este método genera nuevos elementos para el scoring |

---

## 8️⃣ `patterns` — PATRONES DE EXTRACCIÓN (REGEX/NER)

### ¿Qué es?
Expresiones regulares para detectar evidencia en el texto.

### Ejemplo 1: Patrón TEMPORAL

```json
{
  "id": "PAT-Q001-000",
  "category": "TEMPORAL",
  "pattern": "línea base|año base|situación inicial|diagnóstico de género",
  "match_type": "REGEX",
  "confidence_weight": 0.85,
  "specificity": "MEDIUM",
  "flags": "i",
  "context_scope": "PARAGRAPH"
}
```

### Ejemplo 2: Patrón FUENTE_OFICIAL (con semantic_expansion)

```json
{
  "id": "PAT-Q001-002",
  "category": "FUENTE_OFICIAL",
  "pattern": "DANE|Medicina Legal|Fiscalía|Policía Nacional|SIVIGILA|SISPRO",
  "match_type": "NER_OR_REGEX",
  "confidence_weight": 0.95,
  "specificity": "HIGH",
  "validation_rule": "must_be_capitalized",
  "context_requirement": "within_diagnostic_section",
  "entity_type": "ORG",
  "semantic_expansion": {
    "DANE": ["Departamento Administrativo Nacional de Estadística", "estadísticas oficiales"],
    "SIVIGILA": ["Sistema de Vigilancia en Salud Pública", "vigilancia epidemiológica"],
    "SISPRO": ["Sistema Integral de Información de la Protección Social"]
  }
}
```

### Ejemplo 3: Patrón INDICADOR (números/porcentajes)

```json
{
  "id": "PAT-Q001-011",
  "category": "INDICADOR",
  "pattern": "\\d+(\\.\\d+)?\\s*%",
  "match_type": "REGEX",
  "confidence_weight": 0.85
}
```

### Ejemplo 4: Patrón TERRITORIAL

```json
{
  "id": "PAT-Q005-004",
  "category": "TERRITORIAL",
  "pattern": "Acuerdo Municipal|Decreto Municipal",
  "match_type": "REGEX"
}
```

### Ejemplo 5: Patrón con dynamic_update

```json
{
  "id": "PAT-Q001-013",
  "category": "TEMPORAL",
  "pattern": "serie histórica|evolución 20\\d{2}-20\\d{2}|tendencia de los últimos",
  "dynamic_update": "CURRENT_YEAR_WINDOW"
}
```

### Ejemplo 6: Patrón de TABLA

```json
{
  "id": "PAT-Q006-003",
  "category": "TEMPORAL",
  "table_structure_parsing": {
    "detect_boundaries": true,
    "cell_relationship_mapping": true
  }
}
```

### Ejemplo 7: Patrón con pattern_ref (referencia compartida)

```json
{
  "id": "PAT-Q006-000",
  "pattern_ref": "PAT-0105",
  "evidence_modality": "TABLE"
}
```

### Categorías de patterns:

| Categoría | Qué detecta | Ejemplos |
|-----------|-------------|----------|
| `TEMPORAL` | Años, periodos, series | "2019-2023", "cuatrienio anterior" |
| `FUENTE_OFICIAL` | Instituciones oficiales | DANE, DNP, SIVIGILA |
| `INDICADOR` | Números, porcentajes, tasas | "45.3%", "tasa de 12.5" |
| `UNIDAD_MEDIDA` | Unidades de medición | "por 100.000 hab", "%" |
| `TERRITORIAL` | Ámbito geográfico | "municipal", "departamental" |
| `GENERAL` | Todo lo demás | Conceptos específicos del tema |

### Match types:

| Tipo | Descripción |
|------|-------------|
| `REGEX` | Expresión regular pura |
| `LITERAL` | Texto exacto (más rápido) |
| `NER_OR_REGEX` | Primero intenta Named Entity Recognition, si falla usa regex |

---

## 9️⃣ `validations` — REGLAS DE VALIDACIÓN

### ¿Qué es?
Validaciones adicionales que deben cumplirse para dar puntaje.

### Ejemplo completo de Q001:

```json
"validations": {
  "buscar_indicadores_cuantitativos": {
    "minimum_required": 3,
    "patterns": [
      "\\d{1,3}(\\.\\d{3})*(,\\d{1,2})?\\s*%",
      "\\d+\\s*(por|cada)\\s*(100|mil|100\\.000)",
      "tasa\\s+de\\s+\\w+",
      "índice\\s+de\\s+\\w+"
    ],
    "specificity": "HIGH",
    "proximity_validation": {
      "require_near": ["año", "periodo", "vigencia"],
      "max_distance": 30
    }
  },
  
  "cobertura": {
    "minimum_required": 1,
    "patterns": ["departamental", "municipal", "urbano", "rural", "territorial", "poblacional"],
    "specificity": "HIGH"
  },
  
  "series_temporales": {
    "minimum_years": 3,
    "patterns": ["20\\d{2}", "año", "periodo", "histórico", "serie"],
    "specificity": "MEDIUM"
  },
  
  "unidades_medicion": {
    "minimum_required": 2,
    "patterns": ["por 100.000", "por 1.000", "%", "porcentaje", "tasa", "razón"],
    "specificity": "MEDIUM"
  },
  
  "verificar_fuentes": {
    "minimum_required": 2,
    "patterns": ["fuente:", "según", "datos de", "DANE", "DNP", "SISPRO", "SIVIGILA", "Ministerio"],
    "specificity": "MEDIUM"
  },
  
  "completeness_check": {
    "type": "completeness",
    "threshold": 0.8
  }
}
```

### Campos importantes:

| Campo | Descripción |
|-------|-------------|
| `minimum_required` | Cantidad mínima de matches necesarios |
| `minimum_years` | Años mínimos para series temporales |
| `patterns[]` | Regex a buscar para esta validación |
| `specificity` | `HIGH` \| `MEDIUM` \| `LOW` |
| `proximity_validation` | Debe aparecer cerca de ciertos términos |
| `threshold` | Porcentaje mínimo de completitud (0.0-1.0) |

---

## 🔟 `scoring` — DEFINICIONES DE PUNTAJE

### Niveles de calificación:

```json
"micro_levels": [
  { "level": "EXCELENTE", "min_score": 0.85, "color": "green" },
  { "level": "BUENO", "min_score": 0.70, "color": "blue" },
  { "level": "ACEPTABLE", "min_score": 0.55, "color": "yellow" },
  { "level": "INSUFICIENTE", "min_score": 0.0, "color": "red" }
]
```

### Modalidades de scoring:

| Tipo | Descripción | Agregación |
|------|-------------|------------|
| `TYPE_A` | Cuenta 4 elementos, escala 0-3 | `presence_threshold` (umbral 0.7) |
| `TYPE_B` | Cuenta hasta 3 elementos, 1 punto c/u | `binary_sum` (max 3) |
| `TYPE_C` | Cuenta 2 elementos, escala 0-3 | `presence_threshold` (umbral 0.5) |
| `TYPE_D` | Cuenta 3 elementos ponderados | `weighted_sum` (pesos [0.4, 0.3, 0.3]) |
| `TYPE_E` | Verificación booleana | `binary_presence` |
| `TYPE_F` | Similitud semántica continua | `normalized_continuous` (minmax) |

### Ejemplo de definición:

```json
"modality_definitions": {
  "TYPE_A": {
    "description": "Count 4 elements and scale to 0-3",
    "aggregation": "presence_threshold",
    "threshold": 0.7,
    "failure_code": "F-A-MIN"
  },
  "TYPE_D": {
    "description": "Count 3 elements, weighted",
    "aggregation": "weighted_sum",
    "weights": [0.4, 0.3, 0.3],
    "failure_code": "F-D-MIN"
  }
}
```

---

## 1️⃣1️⃣ `semantic_layers` — CONFIGURACIÓN NLP

```json
"semantic_layers": {
  "disambiguation": {
    "entity_linker": "spaCy_es_core_news_lg",
    "confidence_threshold": 0.72
  },
  "embedding_strategy": {
    "model": "multilingual-e5-base",
    "dimension": 768,
    "hybrid": {
      "bm25": true,
      "fusion": "RRF"
    }
  }
}
```

| Campo | Valor | Descripción |
|-------|-------|-------------|
| `entity_linker` | spaCy_es_core_news_lg | Modelo para desambiguación de entidades |
| `confidence_threshold` | 0.72 | Umbral mínimo de confianza para NER |
| `model` | multilingual-e5-base | Modelo de embeddings |
| `dimension` | 768 | Dimensión del vector de embedding |
| `bm25` | true | Usar BM25 para búsqueda híbrida |
| `fusion` | RRF | Reciprocal Rank Fusion para combinar resultados |

---

## 1️⃣2️⃣ `niveles_abstraccion` — METADATA DE JERARQUÍA

### Clusters:

```json
"clusters": [
  {
    "cluster_id": "CL01",
    "policy_area_ids": ["PA02", "PA03", "PA07"],
    "legacy_policy_area_ids": ["P2", "P3", "P7"],
    "rationale": "Seguridad humana, protección de la vida y paz territorial",
    "i18n": {
      "default": "es",
      "keys": { "label_es": "Seguridad y Paz", "label_en": "Security and Peace" }
    }
  }
]
```

### Dimensions metadata:

```json
"dimensions": [
  {
    "dimension_id": "DIM01",
    "legacy_id": "D1",
    "description": "Evalúa la calidad del diagnóstico territorial, líneas base cuantitativas, identificación de brechas y suficiencia de recursos.",
    "i18n": {
      "keys": { "label_es": "Insumos (Diagnóstico y Líneas Base)" }
    }
  }
]
```

### Policy areas metadata:

```json
"policy_areas": [
  {
    "policy_area_id": "PA01",
    "cluster_id": "CL02",
    "dimension_ids": ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"],
    "legacy_ids": ["P1"],
    "required_evidence_keys": ["official_stats", "official_documents", "third_party_research"]
  }
]
```

---

## 1️⃣3️⃣ `integrity` & `observability`

### Checksums e integridad:

```json
"integrity": {
  "monolith_hash": "de52721917492cac3e6c548dc7457d9de68b66183bebdaf825e090e3bbdba6d0",
  "ruleset_hash": "9daaaf91c4c9bc90c3212c196c719f7120fca4c3b2b7875851c3e18e428e600a",
  "question_count": {
    "macro": 1,
    "meso": 4,
    "micro": 300,
    "total": 305
  }
}
```

### Telemetría:

```json
"observability": {
  "telemetry_schema": {
    "logs": {
      "format": "jsonl",
      "fields": ["timestamp", "question_id", "pattern_id", "matched_text", "confidence", "trace_id", "ruleset_hash"]
    },
    "metrics": [
      { "name": "pattern_match_count", "level": "MICRO", "aggregation": "sum" }
    ],
    "tracing": {
      "propagation": "...",
      "span_structure": [...]
    }
  }
}
```

---

## 🎯 FLUJO DE EVALUACIÓN COMPLETO

```
┌─────────────────────────────────────────────────────────────┐
│  1. CARGAR micro_question Q001                              │
├─────────────────────────────────────────────────────────────┤
│  2. BUSCAR patterns[] en el texto                           │
│     → Compilar regex de cada pattern                        │
│     → Ejecutar matching por categoría                       │
│     → Registrar matches con confidence_weight               │
├─────────────────────────────────────────────────────────────┤
│  3. EJECUTAR method_sets[] en orden de priority             │
│     → Verificar depends_on_patterns (si aplica)             │
│     → Ejecutar método Python                                │
│     → Recoger produces_elements (si aplica)                 │
├─────────────────────────────────────────────────────────────┤
│  4. VALIDAR con validations{}                               │
│     → Verificar minimum_required                            │
│     → Aplicar proximity_validation                          │
│     → Calcular completeness_check                           │
├─────────────────────────────────────────────────────────────┤
│  5. VERIFICAR expected_elements[]                           │
│     → ¿Todos los required: true presentes?                  │
│     → ¿Se cumplen los minimum: N?                           │
├─────────────────────────────────────────────────────────────┤
│  6. SI FALLA → failure_contract.emit_code                   │
│     → Abortar si abort_if[] se cumple                       │
│     → Emitir código determinístico                          │
├─────────────────────────────────────────────────────────────┤
│  7. CALCULAR score según scoring_modality                   │
│     → TYPE_A, TYPE_B, TYPE_C, TYPE_D, TYPE_E, TYPE_F        │
│     → Aplicar aggregation y threshold                       │
├─────────────────────────────────────────────────────────────┤
│  8. AGREGAR meso_questions por cluster                      │
│     → weighted_average de micro scores del cluster          │
├─────────────────────────────────────────────────────────────┤
│  9. CALCULAR macro_question holísticamente                  │
│     → Integración de todos los clusters                     │
│     → Si no match → fallback.pattern                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 UBICACIÓN DEL ARCHIVO

```
/canonic_questionnaire_central/questionnaire_monolith.json
```

**Líneas totales:** 67,355  
**Versión:** Generado 2025-10-29T02:21:25.777170+00:00

---

## 🔗 REFERENCIAS CRUZADAS

| Archivo | Relación |
|---------|----------|
| `analyzer_one.py` | Debe cargar `dimensions` y `policy_areas` desde este JSON |
| `rubric_scoring_FIXED.json` | Definiciones de scoring complementarias |
| `method_config_loader.py` | Lee `method_sets` para routing de métodos |

---

---

## 📚 CATÁLOGO EXHAUSTIVO DE TIPOS Y CRITERIOS DE MEMBRESÍA

### A. TIPOS DE `expected_elements`

Todos los valores posibles para `expected_elements[].type`:

| Tipo | Descripción | Usado en |
|------|-------------|----------|
| `cobertura_territorial_especificada` | Ámbito geográfico definido | DIM01 |
| `fuentes_oficiales` | Referencias a entidades como DANE, DNP | DIM01 |
| `indicadores_cuantitativos` | Números, tasas, porcentajes | DIM01 |
| `series_temporales_años` | Datos históricos multi-año | DIM01 |
| `cuantificacion_brecha` | Diferencia cuantificada entre situación actual y deseada | DIM01 |
| `sesgos_reconocidos` | Limitaciones metodológicas explícitas | DIM01 |
| `vacios_explicitos` | Gaps de información declarados | DIM01 |
| `formato_tabular` | Presentación en tabla estructurada | DIM02 |
| `columna_responsable` | Columna con entidad/persona responsable | DIM02 |
| `columna_producto` | Columna con entregables/outputs | DIM02 |
| `columna_cronograma` | Columna con fechas/plazos | DIM02 |
| `columna_costo` | Columna con presupuesto/recursos | DIM02 |
| `instrumento_especificado` | Herramienta/mecanismo definido | DIM02 |
| `logica_causal_explicita` | Teoría de cambio articulada | DIM02, DIM06 |
| `poblacion_objetivo_definida` | Beneficiarios específicos | DIM02 |
| `impacto_definido` | Transformación de largo plazo | DIM05 |
| `ruta_transmision` | Cadena causal desde output a impacto | DIM05 |
| `rezago_temporal` | Tiempo esperado para observar cambios | DIM05 |
| `usa_proxies` | Indicadores indirectos cuando no hay directos | DIM05 |
| `usa_indices_compuestos` | Índices agregados (ej. IDH) | DIM05 |
| `justifica_validez` | Argumenta por qué el indicador es válido | DIM05 |
| `trazabilidad_ppi_bpin` | Códigos de proyectos de inversión | DIM03 |

---

### B. CATEGORÍAS DE `patterns`

Valores posibles para `patterns[].category`:

| Categoría | Descripción | Ejemplos de patterns |
|-----------|-------------|---------------------|
| `TEMPORAL` | Referencias temporales | años, periodos, series históricas |
| `FUENTE_OFICIAL` | Instituciones estatales | DANE, DNP, SIVIGILA, Ministerios |
| `INDICADOR` | Métricas cuantitativas | porcentajes, tasas, índices |
| `UNIDAD_MEDIDA` | Denominadores y escalas | "por 100.000", "por 1.000" |
| `TERRITORIAL` | Ámbitos geográficos | municipal, departamental, rural |
| `GENERAL` | Conceptos temáticos específicos | VBG, feminicidio, víctimas |

---

### C. TIPOS DE `match_type`

Valores posibles para `patterns[].match_type`:

| Tipo | Descripción | Cuándo usar |
|------|-------------|-------------|
| `REGEX` | Expresión regular pura | Patrones complejos con alternativas |
| `LITERAL` | Coincidencia exacta | Términos fijos, más rápido |
| `NER_OR_REGEX` | Primero NER, fallback a regex | Entidades nombradas (ORG, LOC, PER) |

---

### D. NIVELES DE `specificity`

Valores posibles para `patterns[].specificity` y `validations[].specificity`:

| Nivel | Significado | Uso |
|-------|-------------|-----|
| `HIGH` | Alta precisión, pocos falsos positivos | Términos técnicos únicos |
| `MEDIUM` | Balance precisión/recall | Conceptos generales |
| `LOW` | Alta cobertura, más falsos positivos | Términos ambiguos |

---

### E. TIPOS DE `method_type`

Valores posibles para `method_sets[].method_type`:

| Tipo | Descripción | Ejemplos de métodos |
|------|-------------|---------------------|
| `extraction` | Extrae información del texto | `extract_tables`, `_parse_amount` |
| `analysis` | Analiza/procesa información extraída | `diagnose_critical_links`, `infer_mechanisms` |
| `validation` | Verifica consistencia/calidad | `_audit_direct_evidence`, `validate_quality_criteria` |
| `scoring` | Calcula puntajes | `calculate_posterior`, `calculate_quality_score` |

---

### F. MODALIDADES DE `scoring_modality`

#### Para micro_questions:

| Modalidad | Descripción | Agregación | Parámetros |
|-----------|-------------|------------|------------|
| `TYPE_A` | Cuenta 4 elementos → escala 0-3 | `presence_threshold` | `threshold: 0.7` |
| `TYPE_B` | Cuenta hasta 3 elementos, 1 pt c/u | `binary_sum` | `max_score: 3` |
| `TYPE_C` | Cuenta 2 elementos → escala 0-3 | `presence_threshold` | `threshold: 0.5` |
| `TYPE_D` | 3 elementos ponderados | `weighted_sum` | `weights: [0.4, 0.3, 0.3]` |
| `TYPE_E` | Verificación booleana | `binary_presence` | — |
| `TYPE_F` | Similitud semántica continua | `normalized_continuous` | `normalization: minmax` |

#### Para meso_questions:

| Modalidad | Descripción |
|-----------|-------------|
| `MESO_INTEGRATION` | Agregación de micro por cluster |

#### Para macro_question:

| Modalidad | Descripción |
|-----------|-------------|
| `MACRO_HOLISTIC` | Evaluación integral del plan |

---

### G. TIPOS DE `aggregation_method`

| Método | Nivel | Descripción |
|--------|-------|-------------|
| `weighted_average` | MESO | Promedio ponderado de micro scores |
| `holistic_assessment` | MACRO | Evaluación cualitativa integral |

---

### H. CONDICIONES DE `failure_contract.abort_if`

| Condición | Significado |
|-----------|-------------|
| `missing_required_element` | Falta un `expected_element` con `required: true` |
| `incomplete_text` | Texto truncado o incompleto |

---

### I. TIPOS DE `validations`

Nombres de validaciones y sus campos:

| Validación | Campos | Descripción |
|------------|--------|-------------|
| `buscar_indicadores_cuantitativos` | `minimum_required`, `patterns[]`, `specificity`, `proximity_validation` | Busca números/tasas |
| `cobertura` | `minimum_required`, `patterns[]`, `specificity` | Verifica ámbito territorial |
| `series_temporales` | `minimum_years`, `patterns[]`, `specificity` | Verifica datos históricos |
| `unidades_medicion` | `minimum_required`, `patterns[]`, `specificity` | Verifica denominadores |
| `verificar_fuentes` | `minimum_required`, `patterns[]`, `specificity` | Verifica citas de fuentes |
| `completeness_check` | `type`, `threshold` | Verifica completitud general |
| `monitoring_keywords` | `minimum_required`, `patterns[]`, `specificity` | Palabras clave de monitoreo |

---

### J. CAMPOS DE `proximity_validation`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `require_near` | `string[]` | Términos que deben estar cerca |
| `max_distance` | `int` | Distancia máxima en caracteres |

---

### K. CAMPOS DE `semantic_expansion`

Estructura para expandir términos con sinónimos/variantes:

```json
{
  "DANE": ["Departamento Administrativo Nacional de Estadística", "estadísticas oficiales"],
  "SIVIGILA": ["Sistema de Vigilancia en Salud Pública", "vigilancia epidemiológica"]
}
```

---

### L. TIPOS DE `entity_type` (NER)

| Tipo | Descripción | Ejemplos |
|------|-------------|----------|
| `ORG` | Organizaciones | DANE, Ministerio, Fiscalía |
| `LOC` | Lugares | Municipio, Departamento |
| `PER` | Personas | — |
| `DATE` | Fechas | 2024, enero |
| `MONEY` | Cantidades monetarias | $1.000.000 |

---

### M. CAMPOS DE `table_structure_parsing`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `detect_boundaries` | `bool` | Detectar límites de tabla |
| `cell_relationship_mapping` | `bool` | Mapear relaciones entre celdas |

---

### N. CAMPOS DE `numeric_parsing`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `currency_format` | `string` | Formato de moneda (ej. COP) |
| `written_numbers` | `bool` | Parsear números escritos |

---

### O. CAMPOS DE `semantic_analysis`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `detect_hedging` | `bool` | Detectar lenguaje evasivo |
| `uncertainty_markers` | `string[]` | Marcadores de incertidumbre |

---

### P. TIPOS DE `dynamic_update`

| Valor | Descripción |
|-------|-------------|
| `CURRENT_YEAR_WINDOW` | Actualiza patrones de año con ventana actual |

---

### Q. CAMPOS DE `negative_filter`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `required_co_occurrence.terms` | `string[]` | Términos que deben co-ocurrir |
| `required_co_occurrence.proximity` | `int` | Distancia máxima |

---

### R. TIPOS DE `context_scope`

| Valor | Descripción |
|-------|-------------|
| `PARAGRAPH` | Buscar en párrafo completo |
| `SENTENCE` | Buscar solo en oración |
| `DOCUMENT` | Buscar en todo el documento |

---

### S. TIPOS DE `evidence_modality`

| Valor | Descripción |
|-------|-------------|
| `TABLE` | Evidencia en formato tabla |
| `TEXT` | Evidencia en texto narrativo |
| `FIGURE` | Evidencia en figura/gráfico |

---

### T. NIVELES DE CALIFICACIÓN (`micro_levels`)

| Nivel | min_score | Color |
|-------|-----------|-------|
| `EXCELENTE` | 0.85 | green |
| `BUENO` | 0.70 | blue |
| `ACEPTABLE` | 0.55 | yellow |
| `INSUFICIENTE` | 0.00 | red |

---

### U. IDENTIFICADORES CANÓNICOS

| ID | Formato | Ejemplo | Descripción |
|----|---------|---------|-------------|
| `dimension_id` | `DIMxx` | `DIM01` | 6 dimensiones (01-06) |
| `policy_area_id` | `PAxx` | `PA01` | 10 áreas (01-10) |
| `cluster_id` | `CLxx` | `CL01` | 4 clusters (01-04) |
| `question_id` | `Qxxx` | `Q001` | 300 micro preguntas |
| `pattern_id` | `PAT-Qxxx-xxx` | `PAT-Q001-002` | Patrón específico de pregunta |
| `pattern_ref` | `PAT-xxxx` | `PAT-0105` | Patrón compartido global |

---

### V. CAMPOS BOOLEANOS

| Campo | Ubicación | Descripción |
|-------|-----------|-------------|
| `required` | `expected_elements[]` | Elemento obligatorio |
| `bm25` | `semantic_layers.embedding_strategy.hybrid` | Usar BM25 |
| `detect_boundaries` | `table_structure_parsing` | Detectar límites |
| `cell_relationship_mapping` | `table_structure_parsing` | Mapear celdas |
| `detect_hedging` | `semantic_analysis` | Detectar evasión |

---

### W. CAMPOS NUMÉRICOS

| Campo | Ubicación | Tipo | Rango |
|-------|-----------|------|-------|
| `confidence_weight` | `patterns[]` | `float` | 0.0 - 1.0 |
| `confidence_threshold` | `semantic_layers.disambiguation` | `float` | 0.0 - 1.0 |
| `threshold` | `validations.completeness_check` | `float` | 0.0 - 1.0 |
| `minimum_required` | `validations.*` | `int` | ≥ 1 |
| `minimum` | `expected_elements[]` | `int` | ≥ 1 |
| `minimum_years` | `validations.series_temporales` | `int` | ≥ 1 |
| `max_distance` | `proximity_validation` | `int` | caracteres |
| `priority` | `method_sets[]`, `patterns[]` | `int` | 1-999 |
| `dimension` | `embedding_strategy` | `int` | 768 |

---

### X. RELACIONES JERÁRQUICAS

```
questionnaire_monolith.json
│
├── canonical_notation
│   ├── dimensions{} ────────────────→ 6 items (D1-D6)
│   │   └── {code, name, label}
│   └── policy_areas{} ──────────────→ 10 items (PA01-PA10)
│       └── {name, legacy_id}
│
├── blocks
│   ├── macro_question ──────────────→ 1 item
│   │   └── clusters[] → references CL01-CL04
│   │
│   ├── meso_questions[] ────────────→ 4 items
│   │   └── cluster_id → references CLxx
│   │   └── policy_areas[] → references Pxx
│   │
│   ├── micro_questions[] ───────────→ 300 items
│   │   ├── dimension_id → references DIMxx
│   │   ├── policy_area_id → references PAxx
│   │   ├── cluster_id → references CLxx
│   │   ├── method_sets[] → references Python classes/functions
│   │   ├── patterns[] → defines PAT-Qxxx-xxx
│   │   │   └── pattern_ref → references PAT-xxxx (global)
│   │   └── validations{} → local rules
│   │
│   ├── niveles_abstraccion
│   │   ├── clusters[] → defines CL01-CL04
│   │   ├── dimensions[] → defines DIM01-DIM06
│   │   └── policy_areas[] → defines PA01-PA10
│   │
│   ├── scoring
│   │   ├── micro_levels[] → 4 levels
│   │   ├── modalities{} → TYPE_A-F
│   │   └── modality_definitions{} → TYPE_A-F details
│   │
│   └── semantic_layers
│       ├── disambiguation{}
│       └── embedding_strategy{}
│
├── integrity
│   ├── monolith_hash
│   ├── ruleset_hash
│   └── question_count{}
│
└── observability
    └── telemetry_schema{}
```

---

> **NOTA:** Este documento es generado automáticamente. Para actualizaciones, regenerar desde `questionnaire_monolith.json`.

-----------------------------------------------
DETALLE GRANULAR: 
1. RESUMEN EJECUTIVO

1.1 Propósito del Sistema

Este JSON implementa un sistema integral de análisis y validación de políticas públicas colombianas, específicamente diseñado para evaluar planes de desarrollo territorial (PDET), políticas municipales y documentos gubernamentales mediante técnicas de inferencia causal bayesiana, minería de textos y validación de coherencia lógica.

1.2 Métricas Clave

Tamaño estructural: 58,408 paths únicos
Densidad de datos: 83.8% (48,961 valores / 58,408 paths)
Profundidad máxima: 9 niveles
Componentes principales: 7,970 objetos, 1,478 arrays
Volumen textual: 35,145 strings (longitud promedio: 19 chars)
2. ARQUITECTURA TÉCNICA

2.1 Topología Estructural

Nivel    Nodos      %        Función
─────────────────────────────────────────────
  1         7      0.01%    Raíz principal
  2        12      0.02%    Categorías mayores
  3       344      0.59%    Subcategorías
  4      4,334     7.42%    Grupos de validación
  5      7,699    13.18%    Definiciones de reglas
  6     45,110    77.23%    ⚠️ CAPA CRÍTICA: Patrones y metadatos
  7       670      1.15%    Expansiones semánticas
  8       228      0.39%    Metadatos auxiliares
  9         4      0.01%    Hojas profundas
Observación: El 77% de la estructura se concentra en el nivel 6, indicando un diseño de "expansión masiva" donde cada regla de validación tiene múltiples atributos asociados.

2.2 Distribución de Tipos de Datos

Tipo	Cantidad	Porcentaje	Uso Principal
string	35,145	60.2%	Patrones regex, descripciones, nombres de funciones
object	7,970	13.6%	Estructuras de configuración
null	6,588	11.3%	Campos opcionales no poblados
number	6,402	11.0%	Prioridades, pesos, especificidad
array	1,478	2.5%	Colecciones de patrones
boolean	826	1.4%	Flags de validación
Insight: La alta proporción de strings (60%) y nulls (11%) sugiere un sistema extensible con muchos campos opcionales para futuras expansiones.

3. TAXONOMÍA DE CAMPOS

3.1 Top 20 Campos por Frecuencia

Rank	Campo	Ocurrencias	Naturaleza	Cardinalidad
1	description	3,514	Metadata	Variable
2	priority	3,485	Ordenamiento	1-999
3	method_type	3,481	Clasificación	4 valores
4	function	3,481	Referencia Python	~120 únicas
5	class	3,481	Referencia Python	30 clases
6	specificity	2,263	Calificación	4 niveles
7	validation_rule	2,208	Regla de validación	Variable
8	semantic_expansion	2,208	Expansión semántica	Variable
9	match_type	2,208	Tipo de matching	3 valores
10	id	2,208	Identificador	Único
11	flags	2,208	Opciones regex	Homogéneo
12	context_scope	2,208	Alcance contextual	2 valores
13	context_requirement	2,208	Requisito contextual	Variable
14	confidence_weight	2,208	Peso probabilístico	0.85-0.95
15	category	2,208	Categoría temática	12 valores
16	pattern	1,610	Expresión regex	Único
17	type	1,147	Tipo de objeto	Variable
18	required	812	Obligatoriedad	Boolean
19	pattern_ref	599	Referencia cruzada	Único
20	patterns	360	Colección patrones	Array
3.2 Análisis de Cardinalidad

Campos Homogéneos (baja varianza):

flags: "i" (100% de casos) - case-insensitive universal
context_scope: PARAGRAPH (99.5%) vs SENTENCE (0.5%)
match_type: REGEX (91.5%), LITERAL (7.6%), NER_OR_REGEX (0.9%)
Campos Heterogéneos (alta varianza):

function: 120+ funciones únicas, distribución Zipf (top función: 40 ocurrencias)
description: Altamente variable, longitud 1-500 chars
pattern: 1,610 patrones únicos (regex mayormente)
5. SISTEMA DE PATRONES

5.1 Categorías de Patrones (12 tipos)

Categoría	Count	% Total	Propósito
GENERAL	1,902	86.1%	Patrones genéricos de validación
INDICADOR	157	7.1%	Identificación de indicadores/métricas
TERRITORIAL	70	3.2%	Referencias geográficas
TEMPORAL	34	1.5%	Referencias temporales
FUENTE_OFICIAL	19	0.9%	Entidades oficiales (DANE, etc.)
CAUSAL	14	0.6%	Conectores causales
CAUSAL_OUTCOME	3	0.1%	Resultados causales
POBLACION	3	0.1%	Referencias poblacionales
INSTRUMENTO	2	0.1%	Instrumentos de política
UNIDAD_MEDIDA	2	0.1%	Unidades de medición
CAUSAL_CONNECTOR	1	<0.1%	Conectores causales específicos
MECANISMO_COMPLETO	1	<0.1%	Mecanismos causales completos
Insight: La categoría GENERAL domina abrumadoramente (86%), sugiriendo un sistema con muchas reglas de propósito general y pocas especializadas.

5.2 Tipos de Matching

Match Type	Count	% Total	Descripción
REGEX	2,020	91.5%	Expresiones regulares
LITERAL	169	7.6%	Coincidencias literales
NER_OR_REGEX	19	0.9%	Named Entity Recognition + regex
5.3 Niveles de Especificidad

Distribución ajustada por contexto:

VERY_HIGH: Patrones altamente específicos (ej: nombres propios)
HIGH:      Patrones con contexto claro
MEDIUM:    Patrones balanceados (DOMINANTE)
LOW:       Patrones amplios/ambiguos
5.4 Context Scopes

PARAGRAPH (99.5%): Evaluación a nivel de párrafo completo
SENTENCE (0.5%): Evaluación a nivel de oración (casos especiales)
6. SISTEMA DE CONTEXTOS

6.1 Context Requirements (Top 20)

Representan condiciones que deben cumplirse para aplicar una validación:

Contexto	Count	Tema
completeness	289	Completitud de información
coherencia_demostrada	10	Coherencia lógica
analisis_contextual	10	Análisis de contexto
analisis_realismo	10	Realismo de propuestas
asignacion_explicita	10	Asignación de recursos
cadena_causal_explicita	10	Cadenas causales explícitas
ciclos_aprendizaje	10	Ciclos de retroalimentación
coherencia_recursos	9	Coherencia en recursos
enfoque_diferencial	10	Enfoque diferenciado
evidencia_comparada	10	Evidencia comparativa
gobernanza	10	Estructura de gobernanza
horizonte_temporal	10	Plazos y temporalidad
mecanismo_causal_explicito	10	Mecanismos causales claros
poblacion_objetivo_definida	10	Población objetivo clara
restricciones_presupuestales	10	Límites presupuestarios
riesgos_identificados	10	Identificación de riesgos
supuestos_identificados	10	Supuestos explicitados
teoria_cambio_explicita	10	Teoría del cambio explícita
trazabilidad_presupuestal	10	Trazabilidad de recursos
vinculo_diagnostico_actividad	10	Vínculo diagnóstico-acción
Clusters temáticos identificados:

Cluster Causal (30 referencias): cadena_causal, mecanismo_causal, ruta_transmision
Cluster Financiero (29 referencias): restricciones_presupuestales, trazabilidad, coherencia_recursos
Cluster Temporal (20 referencias): horizonte_temporal, rezago_temporal, secuenciacion_logica
Cluster de Rigor (30 referencias): evidencia_comparada, justifica_validez, documenta_validez
7. SISTEMA DE CONFIANZA

7.1 Confidence Weights

Rango: 0.85 - 0.95

Estadísticas:
- Mínimo:   0.85
- Máximo:   0.95
- Promedio: 0.850 (altamente sesgado hacia el mínimo)
Interpretación:

Sistema conservador: la mayoría de validaciones tienen peso 0.85
Pesos altos (0.95) reservados para patrones de alta certeza (ej: FUENTE_OFICIAL con NER)
8. ANÁLISIS DE STRINGS

8.1 Estadísticas Generales

Total de strings: 35,145
Longitud mínima: 1 char
Longitud máxima: 500 chars
Longitud promedio: 19.02 chars
Mediana estimada: ~15 chars
8.2 Distribución de Longitudes

Rango      Estimado     Tipo de contenido
──────────────────────────────────────────────
1-10       ~15,000      IDs, keywords, flags
11-30      ~12,000      Nombres de funciones, descripciones cortas
31-100     ~6,000       Descripciones medianas, patrones regex
101-200    ~1,500       Descripciones largas
201-500    ~645         Descripciones muy detalladas, documentación
9. HETEROGENEIDAD Y VARIANZA

9.1 Coeficiente de Heterogeneidad por Campo

Campo	Valores únicos	Total	Heterogeneidad
id	2,208	2,208	100.0% (único)
pattern	1,610	1,610	100.0% (único)
function	~120	3,481	3.4% (alta reutilización)
description	~2,000	3,514	56.9% (media-alta)
class	30	3,481	0.9% (muy baja)
category	12	2,208	0.5% (muy baja)
match_type	3	2,208	0.1% (extremadamente baja)
context_scope	2	2,208	<0.1% (binario)
flags	1	2,208	0% (constante)
9.2 Índice de Reutilización

Funciones más reutilizadas:

Función	Usos	Clase
PDETMunicipalPlanAnalyzer._compute_robustness_value	40	PDETMunicipalPlanAnalyzer
BayesianMechanismInference._test_necessity	40	BayesianMechanismInference
PerformanceAnalyzer.analyze_performance	40	PerformanceAnalyzer
Observación: Alta reutilización sugiere métodos polimórficos que se aplican a múltiples contextos de validación.

10. RELACIONES Y DEPENDENCIAS

11. PATRONES DE DISEÑO IDENTIFICADOS

11.1 Strategy Pattern

Cada clase implementa diferentes estrategias de análisis (analysis, extraction, validation, scoring).

11.2 Chain of Responsibility

El sistema de prioridades (1-999) sugiere procesamiento en cadena donde validaciones de mayor prioridad se ejecutan primero.

11.3 Template Method

Los campos method_type, class, function indican métodos template que se personalizan según contexto.

11.4 Repository Pattern

El uso de pattern_ref y id únicos sugiere un repositorio central de patrones reutilizables.

12. ANÁLISIS DE CALIDAD

12.1 Indicadores Positivos

✅ Alta densidad (83.8%): Sistema bien poblado, poco desperdicio estructural
✅ IDs únicos: Sistema trazable y auditable
✅ Modularidad: 599 referencias cruzadas indican reutilización
✅ Extensibilidad: 11.3% de nulls permiten expansión futura
✅ Documentación: 3,514 descripciones (cobertura ~100%)

Documento generado: Diciembre 15, 2025
Versión: 1.0
Analista: Claude (Anthropic)