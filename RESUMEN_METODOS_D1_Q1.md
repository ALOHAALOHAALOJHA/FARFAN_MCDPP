# RESUMEN: MÉTODOS RELEVANTES PARA D1-Q1

## CONTEXTO

**Pregunta Q001 (D1-Q1):**
> ¿El diagnóstico presenta datos numéricos (tasas de VBG, porcentajes de participación, cifras de brechas salariales) para el área de Derechos de las mujeres e igualdad de género que sirvan como línea base? Se debe verificar la presencia de un año de referencia y la mención de fuentes (ej. DANE, Medicina Legal, Observatorio de Género).

**Requisitos:**
1. Datos numéricos (tasas, porcentajes, cifras)
2. Línea base
3. Año de referencia
4. Fuentes oficiales

---

## MÉTODOS IDENTIFICADOS POR NIVEL

### N1 (EXTRACCIÓN EMPÍRICA) - 11 métodos

#### Top métodos N1 para D1-Q1:

1. **`PDETMunicipalPlanAnalyzer._extract_financial_amounts`**
   - **Score D1-Q1:** 0.350
   - **Score N1:** 0.433
   - **Archivo:** `financiero_viabilidad_tablas.py:650-695`
   - **Relevancia:** Extrae montos financieros y datos numéricos de tablas y texto
   - **Cobertura:** ✅ Datos numéricos

2. **`PolicyContradictionDetector._extract_quantitative_claims`**
   - **Score D1-Q1:** 0.262
   - **Score N1:** 0.417
   - **Archivo:** `contradiction_deteccion.py:1187-1215`
   - **Relevancia:** Extrae afirmaciones cuantitativas estructuradas (porcentajes, tasas, cifras) con contexto
   - **Cobertura:** ✅ Datos numéricos

3. **`PolicyAnalysisEmbedder._extract_numerical_values`**
   - **Score D1-Q1:** 0.262
   - **Score N1:** 0.383
   - **Archivo:** `embedding_policy.py:1466-1518`
   - **Relevancia:** Extrae valores numéricos usando patrones JSON y embeddings semánticos
   - **Cobertura:** ✅ Datos numéricos

4. **`PolicyContradictionDetector._extract_temporal_markers`**
   - **Score D1-Q1:** 0.200
   - **Score N1:** 0.400
   - **Archivo:** `contradiction_deteccion.py:1165-1184`
   - **Relevancia:** Extrae marcadores temporales del texto (años, períodos, fechas)
   - **Cobertura:** ✅ Año de referencia

5. **`TemporalLogicVerifier._parse_temporal_marker`**
   - **Score D1-Q1:** 0.200
   - **Score N1:** 0.300
   - **Archivo:** `contradiction_deteccion.py:229-254`
   - **Relevancia:** Parsea marcador temporal a timestamp numérico (formato colombiano)
   - **Cobertura:** ✅ Año de referencia

6. **`FinancialAuditor._parse_amount`**
   - **Score D1-Q1:** 0.175
   - **Score N1:** 0.100
   - **Archivo:** `derek_beach.py:3415-3428`
   - **Relevancia:** Parsea montos monetarios de varios formatos
   - **Cobertura:** ✅ Datos numéricos

#### Otros métodos N1 relevantes:
- `PDETMunicipalPlanAnalyzer._extract_from_budget_table` (Score D1-Q1: 0.175)
- `IndustrialPolicyProcessor._extract_point_evidence` (Score D1-Q1: 0.150)
- `PolicyContradictionDetector._parse_number` (Score D1-Q1: 0.150)
- `CausalExtractor._extract_goals` (Score D1-Q1: 0.125)
- `CDAFFramework._generate_extraction_report` (Score D1-Q1: 0.175)

---

### N2 (VALIDACIÓN SEMÁNTICA) - 1 método

1. **`CanonicalQuestionSegmenter._build_manifest`**
   - **Score D1-Q1:** 0.150
   - **Score N2:** 0.300
   - **Archivo:** `analyzer_one.py:2357`
   - **Relevancia:** Construye manifiesto de segmentación canónica
   - **Nota:** Método genérico, no específico para D1-Q1

**⚠️ OBSERVACIÓN:** Hay pocos métodos N2 específicos para D1-Q1. Se recomienda usar métodos N1 con validación semántica integrada o crear métodos N2 específicos.

---

### N3 (AUDITORÍA) - 4 métodos

1. **`OperationalizationAuditor.audit_evidence_traceability`**
   - **Score D1-Q1:** 0.387
   - **Score N3:** 0.320
   - **Archivo:** `derek_beach.py:3687-3815`
   - **Relevancia:** Audita trazabilidad de evidencia para todos los nodos. Incluye validación de línea base, fuentes, años
   - **Cobertura:** ✅ Línea base ✅ Fuentes ✅ Año de referencia

2. **`PolicyAnalysisEmbedder.evaluate_policy_numerical_consistency`**
   - **Score D1-Q1:** 0.275
   - **Score N3:** 0.120
   - **Archivo:** `embedding_policy.py:1136-1186`
   - **Relevancia:** Evaluación bayesiana de consistencia numérica para métricas de política
   - **Cobertura:** ✅ Datos numéricos
   - **⚠️ Nota:** Usa Bayes, puede no ser apropiado para TYPE_A

3. **`OperationalizationAuditor._audit_direct_evidence`**
   - **Score D1-Q1:** 0.150
   - **Score N3:** 0.360
   - **Archivo:** `derek_beach.py:4100`
   - **Relevancia:** Audita evidencia directa con evaluación de confianza
   - **Cobertura:** ✅ Auditoría completa

4. **`OperationalizationAuditor._audit_systemic_risk`**
   - **Score D1-Q1:** 0.150
   - **Score N3:** 0.360
   - **Archivo:** `derek_beach.py:4257`
   - **Relevancia:** Audita riesgo sistémico
   - **Cobertura:** ⚠️ No específico para D1-Q1

---

## RECOMENDACIONES PARA D1-Q1

### Propuesta de métodos N1 (Extracción empírica):

**Mínimo (3 métodos):**
1. `PolicyContradictionDetector._extract_quantitative_claims` - Datos numéricos
2. `PolicyContradictionDetector._extract_temporal_markers` - Año de referencia
3. `IndustrialPolicyProcessor._extract_point_evidence` - Fuentes y contexto

**Recomendado (4-5 métodos):**
1. `PolicyContradictionDetector._extract_quantitative_claims` - Datos numéricos estructurados
2. `PolicyContradictionDetector._extract_temporal_markers` - Año de referencia
3. `PDETMunicipalPlanAnalyzer._extract_financial_amounts` - Datos numéricos de tablas
4. `PolicyAnalysisEmbedder._extract_numerical_values` - Valores numéricos con embeddings
5. `IndustrialPolicyProcessor._extract_point_evidence` - Fuentes y contexto

### Propuesta de métodos N2 (Validación semántica):

**Recomendado (2-3 métodos):**
1. `PolicyContradictionDetector._parse_number` - Validación de formato numérico
2. `IndustrialPolicyProcessor._match_patterns_in_sentences` - Validación de patrones (fuentes, años)
3. `TemporalLogicVerifier._parse_temporal_marker` - Validación de formato temporal

**⚠️ Nota:** Los métodos N2 existentes son limitados. Se recomienda crear métodos N2 específicos o usar validación integrada en métodos N1.

### Propuesta de métodos N3 (Auditoría):

**Recomendado (1 método):**
1. `OperationalizationAuditor.audit_evidence_traceability` - Auditoría completa de requisitos

---

## ANÁLISIS DE COBERTURA

### Cobertura de requisitos por método:

| Requisito | Métodos N1 | Métodos N2 | Métodos N3 |
|-----------|------------|------------|------------|
| **Datos numéricos** | ✅ 6 métodos | ⚠️ 0 métodos | ⚠️ 1 método (Bayes) |
| **Línea base** | ⚠️ 0 métodos directos | ⚠️ 0 métodos | ✅ 1 método |
| **Año de referencia** | ✅ 2 métodos | ⚠️ 0 métodos | ✅ 1 método |
| **Fuentes** | ⚠️ 0 métodos directos | ⚠️ 0 métodos | ✅ 1 método |

### Gaps identificados:

1. **Extracción de fuentes (N1):** No hay métodos específicos para extraer menciones de fuentes oficiales (DANE, Medicina Legal, etc.)
2. **Extracción de línea base (N1):** No hay métodos específicos para identificar datos que sirvan como línea base
3. **Validación N2:** Pocos métodos N2 específicos para validar requisitos de D1-Q1

---

## CONCLUSIÓN

Los métodos identificados cubren parcialmente los requisitos de D1-Q1:

✅ **Bien cubierto:**
- Extracción de datos numéricos (múltiples métodos)
- Extracción de años de referencia (2 métodos)

⚠️ **Parcialmente cubierto:**
- Línea base (solo en auditoría N3)
- Fuentes (solo en auditoría N3)

❌ **No cubierto:**
- Extracción específica de fuentes (N1)
- Extracción específica de línea base (N1)
- Validación semántica específica (N2)

**Recomendación:** Usar los métodos identificados como base, pero considerar crear métodos adicionales específicos para:
- Extracción de fuentes oficiales (N1)
- Identificación de datos de línea base (N1)
- Validación semántica de requisitos (N2)


