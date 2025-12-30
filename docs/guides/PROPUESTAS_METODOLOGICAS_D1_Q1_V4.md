# PROPUESTAS METODOLÓGICAS PARA D1-Q1-V4

## CONTEXTO

**Pregunta Q001 (Representativa de D1-Q1):**
> ¿El diagnóstico presenta datos numéricos (tasas de VBG, porcentajes de participación, cifras de brechas salariales) para el área de Derechos de las mujeres e igualdad de género que sirvan como línea base? Se debe verificar la presencia de un año de referencia y la mención de fuentes (ej. DANE, Medicina Legal, Observatorio de Género).

**Dimensión:** DIM01 (INSUMOS) - Diagnóstico y Recursos

**Requisitos de la pregunta:**
1. **Datos numéricos:** Tasas de VBG, porcentajes de participación, cifras de brechas salariales
2. **Línea base:** Verificar que los datos sirvan como línea base
3. **Año de referencia:** Presencia explícita de año de referencia
4. **Fuentes:** Mención de fuentes oficiales (DANE, Medicina Legal, Observatorio de Género, etc.)

**Naturaleza epistemológica:** 
- **Tipo de contrato:** TYPE_A (Semántico)
- **Epistemología:** Empirismo semántico - Extracción directa de evidencia factual sin inferencia causal o bayesiana
- **Nivel de análisis:** N1 (Empírico) → N2 (Validación semántica) → N3 (Auditoría de completitud)

---

## PROPUESTA 1: JUEGO SEMÁNTICO-EXTRACTIVO PURO

### Filosofía metodológica
Enfoque **minimalista y directo**: extracción empírica pura sin procesamiento inferencial complejo. Maximiza la trazabilidad y minimiza la interpretación.

### Estructura epistemológica

**PHASE A (N1-EMP): Extracción empírica directa**
- **Epistemología:** Empirismo positivista
- **Objetivo:** Producir `raw_facts` estructurados sin interpretación

**PHASE B (N2-INF): Validación semántica**
- **Epistemología:** Verificación semántica (no inferencial fuerte)
- **Objetivo:** Validar coherencia y completitud de los datos extraídos

**PHASE C (N3-AUD): Auditoría de completitud**
- **Epistemología:** Auditoría de cumplimiento
- **Objetivo:** Verificar que se cumplan todos los requisitos de la pregunta

### Métodos propuestos

#### PHASE A - N1 (Extracción empírica)

1. **`PolicyContradictionDetector._extract_quantitative_claims`**
   - **Clase:** `PolicyContradictionDetector`
   - **Archivo:** `contradiction_deteccion.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae afirmaciones cuantitativas estructuradas (porcentajes, tasas, cifras) con contexto
   - **Cobertura:** Datos numéricos (tasas, porcentajes, cifras)
   - **Rationale:** Método especializado en extracción de datos cuantitativos con contexto, ideal para identificar tasas de VBG y porcentajes

2. **`PolicyContradictionDetector._extract_temporal_markers`**
   - **Clase:** `PolicyContradictionDetector`
   - **Archivo:** `contradiction_deteccion.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae marcadores temporales (años, períodos, fechas) del texto
   - **Cobertura:** Año de referencia
   - **Rationale:** Identifica años explícitos en el texto, necesario para verificar año de referencia

3. **`IndustrialPolicyProcessor._extract_point_evidence`**
   - **Clase:** `IndustrialPolicyProcessor`
   - **Archivo:** `policy_processor.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae evidencia puntual por área de política usando patrones canónicos
   - **Cobertura:** Fuentes y contexto de área de política (Derechos de las mujeres)
   - **Rationale:** Permite identificar menciones de fuentes oficiales y contexto específico del área de política

#### PHASE B - N2 (Validación semántica)

4. **`PolicyContradictionDetector._parse_number`**
   - **Clase:** `PolicyContradictionDetector`
   - **Archivo:** `contradiction_deteccion.py`
   - **Nivel:** N2-INF
   - **Output:** `PARAMETER`
   - **Descripción:** Parsea números desde texto y valida formato numérico
   - **Requires:** `raw_facts`
   - **Cobertura:** Validación de formato numérico
   - **Rationale:** Valida que los datos numéricos extraídos sean parseables y coherentes

5. **`IndustrialPolicyProcessor._match_patterns_in_sentences`**
   - **Clase:** `IndustrialPolicyProcessor`
   - **Archivo:** `policy_processor.py`
   - **Nivel:** N2-INF
   - **Output:** `PARAMETER`
   - **Descripción:** Ejecuta matching de patrones de validación (fuentes, años, unidades de medición)
   - **Requires:** `raw_facts`
   - **Cobertura:** Validación de fuentes y años mediante patrones
   - **Rationale:** Valida presencia de fuentes oficiales y años de referencia usando patrones canónicos

#### PHASE C - N3 (Auditoría)

6. **`OperationalizationAuditor._audit_direct_evidence`**
   - **Clase:** `OperationalizationAuditor`
   - **Archivo:** `derek_beach.py`
   - **Nivel:** N3-AUD
   - **Output:** `AUDIT`
   - **Descripción:** Audita trazabilidad de evidencia directa (verifica línea base, fuentes, años)
   - **Requires:** `raw_facts`, `inferred_parameters`
   - **Cobertura:** Auditoría completa de requisitos (datos numéricos, línea base, año, fuentes)
   - **Rationale:** Método especializado en auditoría de evidencia, verifica cumplimiento de todos los requisitos

### Ventajas
- ✅ Máxima trazabilidad: cada dato tiene origen claro
- ✅ Sin sesgo inferencial: no introduce interpretaciones
- ✅ Rápido y eficiente: procesamiento directo
- ✅ Defendible epistemológicamente: empirismo puro

### Desventajas
- ⚠️ Limitado a datos explícitos: no infiere datos implícitos
- ⚠️ Dependiente de calidad del texto: requiere texto bien estructurado

---

## PROPUESTA 2: JUEGO HÍBRIDO SEMÁNTICO-BAYESIANO

### Filosofía metodológica
Enfoque **robusto con validación probabilística**: combina extracción semántica con validación bayesiana para manejar incertidumbre y datos incompletos.

### Estructura epistemológica

**PHASE A (N1-EMP): Extracción empírica**
- **Epistemología:** Empirismo semántico
- **Objetivo:** Producir `raw_facts` con embeddings semánticos

**PHASE B (N2-INF): Inferencia bayesiana de completitud**
- **Epistemología:** Inferencia bayesiana (validación probabilística)
- **Objetivo:** Calcular probabilidad de completitud y calidad de datos

**PHASE C (N3-AUD): Auditoría con confianza bayesiana**
- **Epistemología:** Auditoría bayesiana
- **Objetivo:** Evaluar cumplimiento con intervalos de confianza

### Métodos propuestos

#### PHASE A - N1 (Extracción empírica)

1. **`PolicyContradictionDetector._extract_quantitative_claims`**
   - **Clase:** `PolicyContradictionDetector`
   - **Archivo:** `contradiction_deteccion.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae afirmaciones cuantitativas estructuradas
   - **Cobertura:** Datos numéricos

2. **`PolicyAnalysisEmbedder._extract_numerical_values`**
   - **Clase:** `PolicyAnalysisEmbedder`
   - **Archivo:** `embedding_policy.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae valores numéricos usando patrones JSON y embeddings semánticos
   - **Cobertura:** Datos numéricos con contexto semántico
   - **Rationale:** Usa embeddings para identificar valores numéricos en contexto semántico rico

3. **`SemanticProcessor.chunk_text`**
   - **Clase:** `SemanticProcessor`
   - **Archivo:** `semantic_chunking_policy.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Chunking semántico que preserva estructura del documento (respeta secciones, tablas)
   - **Cobertura:** Estructura del documento (permite identificar secciones de diagnóstico)
   - **Rationale:** Identifica secciones relevantes donde buscar datos de línea base

#### PHASE B - N2 (Inferencia bayesiana)

4. **`BayesianConfidenceCalculator.calculate_posterior`**
   - **Clase:** `BayesianConfidenceCalculator`
   - **Archivo:** `contradiction_deteccion.py`
   - **Nivel:** N2-INF
   - **Output:** `PARAMETER`
   - **Descripción:** Calcula probabilidad posterior de completitud de datos (datos numéricos, año, fuentes)
   - **Requires:** `raw_facts`
   - **Cobertura:** Probabilidad de completitud de requisitos
   - **Rationale:** Calcula confianza probabilística de que se cumplan todos los requisitos

5. **`BayesianNumericalAnalyzer.evaluate_policy_metric`**
   - **Clase:** `BayesianNumericalAnalyzer`
   - **Archivo:** `policy_processor.py` (referenciado en METHOD_CLASSES)
   - **Nivel:** N2-INF
   - **Output:** `PARAMETER`
   - **Descripción:** Evalúa métricas de política con incertidumbre bayesiana
   - **Requires:** `raw_facts`
   - **Cobertura:** Validación probabilística de datos numéricos
   - **Rationale:** Valida calidad y coherencia de datos numéricos con incertidumbre

6. **`PolicyContradictionDetector._statistical_significance_test`**
   - **Clase:** `PolicyContradictionDetector`
   - **Archivo:** `contradiction_deteccion.py`
   - **Nivel:** N2-INF
   - **Output:** `PARAMETER`
   - **Descripción:** Prueba significancia estadística de datos extraídos
   - **Requires:** `raw_facts`
   - **Cobertura:** Validación estadística de suficiencia de datos
   - **Rationale:** Verifica que haya suficientes datos para constituir línea base válida

#### PHASE C - N3 (Auditoría bayesiana)

7. **`OperationalizationAuditor._audit_direct_evidence`**
   - **Clase:** `OperationalizationAuditor`
   - **Archivo:** `derek_beach.py`
   - **Nivel:** N3-AUD
   - **Output:** `AUDIT`
   - **Descripción:** Audita evidencia directa con evaluación bayesiana de confianza
   - **Requires:** `raw_facts`, `inferred_parameters`
   - **Cobertura:** Auditoría completa con intervalos de confianza

### Ventajas
- ✅ Maneja incertidumbre: proporciona intervalos de confianza
- ✅ Robusto ante datos incompletos: inferencia probabilística
- ✅ Validación estadística: prueba significancia de datos
- ✅ Riqueza semántica: embeddings capturan contexto

### Desventajas
- ⚠️ Mayor complejidad: requiere procesamiento bayesiano
- ⚠️ Menos trazable: inferencia introduce interpretación
- ⚠️ Más lento: procesamiento de embeddings y bayesiano

---

## PROPUESTA 3: JUEGO SEMÁNTICO-ESTRUCTURAL CON TABLAS

### Filosofía metodológica
Enfoque **orientado a estructura documental**: aprovecha la estructura de documentos de política (tablas, secciones) para extracción precisa de datos de línea base.

### Estructura epistemológica

**PHASE A (N1-EMP): Extracción estructural**
- **Epistemología:** Empirismo estructural
- **Objetivo:** Extraer datos de estructuras documentales (tablas, secciones)

**PHASE B (N2-INF): Validación estructural y semántica**
- **Epistemología:** Verificación estructural-semántica
- **Objetivo:** Validar coherencia entre estructura y contenido

**PHASE C (N3-AUD): Auditoría estructural**
- **Epistemología:** Auditoría de estructura documental
- **Objetivo:** Verificar completitud estructural de requisitos

### Métodos propuestos

#### PHASE A - N1 (Extracción estructural)

1. **`PDETMunicipalPlanAnalyzer._extract_financial_amounts`**
   - **Clase:** `PDETMunicipalPlanAnalyzer`
   - **Archivo:** `financiero_viabilidad_tablas.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae montos financieros y datos numéricos de tablas y texto
   - **Cobertura:** Datos numéricos de tablas (indicadores, líneas base)
   - **Rationale:** Especializado en extracción de datos numéricos de tablas estructuradas

2. **`PDETMunicipalPlanAnalyzer._extract_from_budget_table`**
   - **Clase:** `PDETMunicipalPlanAnalyzer`
   - **Archivo:** `financiero_viabilidad_tablas.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae datos de tablas de presupuesto e indicadores (incluye línea base, fuentes, años)
   - **Cobertura:** Datos estructurados de tablas (línea base, año, fuentes)
   - **Rationale:** Extrae datos completos de tablas de indicadores que típicamente incluyen línea base, año y fuentes

3. **`PolicyContradictionDetector._extract_temporal_markers`**
   - **Clase:** `PolicyContradictionDetector`
   - **Archivo:** `contradiction_deteccion.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae marcadores temporales del texto
   - **Cobertura:** Año de referencia

4. **`IndustrialPolicyProcessor._extract_metadata`**
   - **Clase:** `IndustrialPolicyProcessor`
   - **Archivo:** `policy_processor.py`
   - **Nivel:** N1-EMP
   - **Output:** `FACT`
   - **Descripción:** Extrae metadatos del documento (período, entidad, título)
   - **Cobertura:** Contexto temporal y estructural del documento
   - **Rationale:** Identifica período del plan que puede servir como año de referencia implícito

#### PHASE B - N2 (Validación estructural)

5. **`PDETMunicipalPlanAnalyzer._score_indicators`**
   - **Clase:** `PDETMunicipalPlanAnalyzer`
   - **Archivo:** `financiero_viabilidad_tablas.py`
   - **Nivel:** N2-INF
   - **Output:** `PARAMETER`
   - **Descripción:** Evalúa calidad de indicadores (completitud de columnas: indicador, línea base, meta, fuente)
   - **Requires:** `raw_facts`
   - **Cobertura:** Validación de completitud estructural de tablas de indicadores
   - **Rationale:** Valida que las tablas de indicadores tengan estructura completa (línea base, fuente, año)

6. **`IndustrialPolicyProcessor._apply_validation_rules`**
   - **Clase:** `IndustrialPolicyProcessor`
   - **Archivo:** `policy_processor.py`
   - **Nivel:** N2-INF
   - **Output:** `PARAMETER`
   - **Descripción:** Aplica reglas de validación canónicas (buscar_indicadores_cuantitativos, verificar_fuentes, series_temporales)
   - **Requires:** `raw_facts`
   - **Cobertura:** Validación de requisitos mediante reglas canónicas
   - **Rationale:** Valida cumplimiento de requisitos usando reglas específicas del cuestionario

#### PHASE C - N3 (Auditoría estructural)

7. **`OperationalizationAuditor._audit_direct_evidence`**
   - **Clase:** `OperationalizationAuditor`
   - **Archivo:** `derek_beach.py`
   - **Nivel:** N3-AUD
   - **Output:** `AUDIT`
   - **Descripción:** Audita trazabilidad de evidencia directa con énfasis en estructura documental
   - **Requires:** `raw_facts`, `inferred_parameters`
   - **Cobertura:** Auditoría completa de requisitos

### Ventajas
- ✅ Aprovecha estructura documental: tablas y secciones bien definidas
- ✅ Alta precisión: extracción de datos estructurados es más confiable
- ✅ Completo: tablas de indicadores típicamente incluyen todos los requisitos
- ✅ Eficiente: procesamiento estructurado es rápido

### Desventajas
- ⚠️ Dependiente de estructura: requiere documentos bien estructurados
- ⚠️ Puede perder datos en texto libre: si datos no están en tablas
- ⚠️ Menos flexible: asume estructura estándar de documentos

---

## COMPARACIÓN DE PROPUESTAS

| Criterio | Propuesta 1: Semántico-Extractivo | Propuesta 2: Híbrido Bayesiano | Propuesta 3: Estructural |
|----------|-----------------------------------|-------------------------------|-------------------------|
| **Complejidad** | Baja | Alta | Media |
| **Trazabilidad** | Máxima | Media | Alta |
| **Robustez ante incertidumbre** | Baja | Alta | Media |
| **Dependencia de estructura** | Baja | Baja | Alta |
| **Velocidad** | Alta | Baja | Media |
| **Cobertura de requisitos** | Alta | Alta | Muy Alta |
| **Defendibilidad epistemológica** | Muy Alta | Alta | Alta |
| **Manejo de datos incompletos** | Bajo | Alto | Medio |

## RECOMENDACIÓN

**Propuesta recomendada: Propuesta 1 (Semántico-Extractivo Puro)**

**Justificación:**
1. **Alineación epistemológica:** TYPE_A requiere empirismo semántico puro, sin inferencia bayesiana fuerte
2. **Trazabilidad:** Máxima trazabilidad de evidencia, crítico para auditoría
3. **Simplicidad:** Menor complejidad reduce puntos de falla
4. **Defendibilidad:** Enfoque empirista puro es más defendible ante auditoría externa
5. **Cobertura suficiente:** Los métodos propuestos cubren todos los requisitos de la pregunta

**Alternativa:** Si los documentos tienen estructura muy consistente con tablas de indicadores, la **Propuesta 3** puede ser más eficiente y precisa.

---

## NOTAS TÉCNICAS

### Validación de métodos
Todos los métodos propuestos deben ser validados contra:
- Contratos existentes similares (D1-Q2, D1-Q3)
- Patrones canónicos del cuestionario (`VALIDATION_RULES`)
- Estructura epistemológica v4.0

### Consideraciones de implementación
- Los métodos deben respetar la estructura de fases N1 → N2 → N3
- La fusión de evidencia debe seguir `fusion_specification` para TYPE_A
- Los `requires` y `modifies` deben ser correctamente especificados
- La `traceability` debe incluir todos los métodos utilizados


