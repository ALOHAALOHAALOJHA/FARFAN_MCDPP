# ESPECIFICACIÓN CANÓNICA DE NOTACIÓN F.A.R.F.A.N 3.0
## Sistema de Evaluación Causal para Planes de Desarrollo Territorial

**Versión**: 4.0.0  
**Fecha**: 2026-01-26 (Updated)  
**Estado**: FROZEN ❄️ - FUENTE ÚNICA DE VERDAD  
**Autor**: Sistema F.A.R.F.A.N  
**Freeze Manifest**: Ver `CANONIC_FREEZE_MANIFEST.md`

---

## ÍNDICE

1. [Arquitectura y Jerarquía de Evaluación](#1-arquitectura-y-jerarquía-de-evaluación)
2. [Sistema de Códigos y Notación](#2-sistema-de-códigos-y-notación)
3. [Nivel MICRO: 300 Preguntas Específicas](#3-nivel-micro-300-preguntas-específicas)
4. [Nivel MESO: 4 Preguntas de Integración por Cluster](#4-nivel-meso-4-preguntas-de-integración-por-cluster)
5. [Nivel MACRO: Pregunta de Coherencia Global](#5-nivel-macro-pregunta-de-coherencia-global)
6. [ANEXO A: Slots y Equivalencia Posicional Relativa](#anexo-a-slots-y-equivalencia-posicional-relativa)
7. [ANEXO B: Catálogo de Códigos Adicionales](#anexo-b-catálogo-de-códigos-adicionales)

---

## 1. ARQUITECTURA Y JERARQUÍA DE EVALUACIÓN

### 1.1 Estructura Piramidal

```
                    ┌─────────────────────────────────┐
                    │        NIVEL MACRO (1)          │
                    │      Pregunta Q305 / MACRO_1    │
                    │     Coherencia Global del PDM   │
                    └─────────────────────────────────┘
                                    ▲
                    ┌───────────────┴───────────────┐
                    │       NIVEL MESO (4)          │
                    │   Q301-Q304 / MESO_1-MESO_4   │
                    │  Integración por Cluster      │
                    └───────────────────────────────┘
                                    ▲
        ┌───────────────────────────┴───────────────────────────┐
        │                   NIVEL MICRO (300)                    │
        │          Q001-Q300 por 10 Áreas de Política           │
        │        6 Dimensiones × 5 Preguntas × 10 PAs           │
        └────────────────────────────────────────────────────────┘
```

### 1.2 Métricas del Sistema

| Nivel | Cantidad | Rango de IDs | Función |
|-------|----------|--------------|---------|
| MICRO | 300 | Q001-Q300 | Evaluación granular por PA y DIM |
| MESO | 4 | Q301-Q304 (MESO_1-4) | Integración intra-cluster |
| MACRO | 1 | Q305 (MACRO_1) | Coherencia global del plan |
| **TOTAL** | **305** | Q001-Q305 | - |

---

## 2. SISTEMA DE CÓDIGOS Y NOTACIÓN

### 2.1 Áreas de Política (PA01-PA10) — DECÁLOGO

| Código | Abreviatura | Nombre Oficial Completo |
|--------|-------------|-------------------------|
| **PA01** | `MUJ` | Derechos de las mujeres e igualdad de género |
| **PA02** | `VIO` | Prevención de la violencia y protección de la población frente al conflicto armado y la violencia generada por grupos delincuenciales organizados, asociada a economías ilegales |
| **PA03** | `AMB` | Ambiente sano, cambio climático, prevención y atención a desastres |
| **PA04** | `DESC` | Derechos económicos, sociales y culturales |
| **PA05** | `VIC` | Derechos de las víctimas y construcción de paz |
| **PA06** | `NIÑ` | Derecho al buen futuro de la niñez, adolescencia, juventud y entornos protectores |
| **PA07** | `TIE` | Tierras y territorios |
| **PA08** | `LID` | Líderes y lideresas, defensores y defensoras de derechos humanos, comunitarios, sociales, ambientales, de la tierra, el territorio y de la naturaleza |
| **PA09** | `PPL` | Crisis de derechos de personas privadas de la libertad |
| **PA10** | `MIG` | Migración transfronteriza |

### 2.2 Dimensiones de Análisis (DIM01-DIM06)

| Código | Abreviatura | Nombre | Posición en Cadena Causal |
|--------|-------------|--------|---------------------------|
| **DIM01** | `INS` | Insumos (Diagnóstico y Líneas Base) | 1 - Foundation |
| **DIM02** | `ACT` | Actividades (Diseño de Intervención) | 2 - Mechanisms |
| **DIM03** | `PRO` | Productos (Verificables) | 3 - Outputs |
| **DIM04** | `RES` | Resultados (Medibles) | 4 - Outcomes |
| **DIM05** | `IMP` | Impactos (Largo Plazo) | 5 - Impacts |
| **DIM06** | `COH` | Coherencia Causal (Teoría de Cambio) | 6 - System |

### 2.3 Clusters Temáticos (CL01-CL04)

| Código | Abreviatura | Nombre | Áreas de Política | Peso |
|--------|-------------|--------|-------------------|------|
| **CL01** | `SEC-PAZ` | Seguridad y Paz | PA02, PA05, PA07 | 25% |
| **CL02** | `GP` | Grupos Poblacionales | PA01, PA06, PA08 | 30% |
| **CL03** | `TERR-AMB` | Territorio-Ambiente | PA03, PA04 | 22% |
| **CL04** | `DESC-CRISIS` | Derechos Sociales & Crisis | PA09, PA10 | 23% |

---

## 3. NIVEL MICRO: 300 PREGUNTAS ESPECÍFICAS

### 3.1 Preguntas Genéricas (30 Base Questions)

Las 30 preguntas genéricas se aplican a cada una de las 10 áreas de política, generando 300 preguntas específicas.

#### DIMENSIÓN 1: INSUMOS (DIM01/INS) — 5 Preguntas

| Slot | Código | Abreviatura | Título | Pregunta Genérica |
|------|--------|-------------|--------|-------------------|
| D1-Q1 | `D1.Q1` | `LB-FUENTE` | Líneas base con fuente y desagregación | ¿El diagnóstico del sector presenta datos cuantitativos (tasas, porcentajes, cifras absolutas) con año de referencia y fuente identificada, desagregados por territorio o población? |
| D1-Q2 | `D1.Q2` | `BRECHA-VACIO` | Cuantificación de brechas y vacíos | ¿El diagnóstico dimensiona numéricamente la magnitud del problema o déficit del sector y reconoce explícitamente limitaciones en los datos? |
| D1-Q3 | `D1.Q3` | `RECUR-ASIG` | Recursos presupuestales asignados | ¿El Plan Plurianual de Inversiones (PPI) o tablas presupuestales asignan recursos monetarios explícitos a programas del sector? |
| D1-Q4 | `D1.Q4` | `CAP-INST` | Capacidades institucionales | ¿El plan identifica las entidades responsables del sector, describe sus capacidades y señala limitaciones institucionales? |
| D1-Q5 | `D1.Q5` | `ALCANCE-COMP` | Justificación de alcance y competencias | ¿El plan justifica el alcance de sus intervenciones mencionando el marco normativo aplicable y competencias? |

#### DIMENSIÓN 2: ACTIVIDADES (DIM02/ACT) — 5 Preguntas

| Slot | Código | Abreviatura | Título | Pregunta Genérica |
|------|--------|-------------|--------|-------------------|
| D2-Q1 | `D2.Q1` | `ACT-OPER` | Actividades operacionalizadas | ¿Las actividades aparecen en formato estructurado con atributos verificables (responsable, producto, cronograma, costo)? |
| D2-Q2 | `D2.Q2` | `DET-INSTR` | Detalle de instrumentos | ¿La descripción especifica el instrumento, población objetivo y contribución al resultado? |
| D2-Q3 | `D2.Q3` | `VINC-CAUSA` | Vínculo con causas | ¿Las actividades se vinculan explícitamente con problemas identificados en el diagnóstico? |
| D2-Q4 | `D2.Q4` | `RIESG-MITIG` | Riesgos y mitigación | ¿El plan identifica obstáculos y propone medidas de mitigación? |
| D2-Q5 | `D2.Q5` | `COH-ESTRAT` | Coherencia estratégica | ¿El plan describe cómo las actividades se complementan o siguen secuencia lógica? |

#### DIMENSIÓN 3: PRODUCTOS (DIM03/PRO) — 5 Preguntas

| Slot | Código | Abreviatura | Título | Pregunta Genérica |
|------|--------|-------------|--------|-------------------|
| D3-Q1 | `D3.Q1` | `IND-PROD` | Indicadores de producto | ¿Los indicadores de producto incluyen línea base, meta cuantitativa y fuente de verificación? |
| D3-Q2 | `D3.Q2` | `PROP-META` | Proporcionalidad meta | ¿Las metas guardan relación con la magnitud del problema identificado? |
| D3-Q3 | `D3.Q3` | `TRAZ-PRES` | Trazabilidad presupuestal | ¿Los productos están vinculados a códigos presupuestales (BPIN, PPI, SGP)? |
| D3-Q4 | `D3.Q4` | `FACT-ACT` | Factibilidad actividad-meta | ¿Existe correspondencia factible entre tipo de actividad y magnitud de meta? |
| D3-Q5 | `D3.Q5` | `MEC-PROD-RES` | Mecanismo producto→resultado | ¿El plan describe cómo los productos contribuyen a los resultados? |

#### DIMENSIÓN 4: RESULTADOS (DIM04/RES) — 5 Preguntas

| Slot | Código | Abreviatura | Título | Pregunta Genérica |
|------|--------|-------------|--------|-------------------|
| D4-Q1 | `D4.Q1` | `IND-RES` | Indicadores de resultado | ¿Los indicadores de resultado están definidos con línea base, meta y horizonte temporal? |
| D4-Q2 | `D4.Q2` | `RUTA-CAUS` | Ruta causal con supuestos | ¿El plan describe la ruta que lleva a los resultados con condiciones necesarias? |
| D4-Q3 | `D4.Q3` | `JUST-AMB` | Justificación de ambición | ¿La ambición de las metas se justifica en función de recursos y capacidad? |
| D4-Q4 | `D4.Q4` | `ATEN-PRIOR` | Atención a problemas priorizados | ¿Los resultados atienden los problemas priorizados en el diagnóstico? |
| D4-Q5 | `D4.Q5` | `ALIN-MARC` | Alineación con marcos superiores | ¿El plan declara alineación con PND, ODS, marcos normativos? |

#### DIMENSIÓN 5: IMPACTOS (DIM05/IMP) — 5 Preguntas

| Slot | Código | Abreviatura | Título | Pregunta Genérica |
|------|--------|-------------|--------|-------------------|
| D5-Q1 | `D5.Q1` | `IMP-LP` | Impactos de largo plazo | ¿El plan define transformaciones que trascienden el cuatrienio? |
| D5-Q2 | `D5.Q2` | `IND-PROXY` | Uso de índices o proxies | ¿Se utilizan índices reconocidos para medir impactos? |
| D5-Q3 | `D5.Q3` | `RIESG-SIST` | Riesgos sistémicos | ¿Los impactos consideran riesgos externos que podrían revertir logros? |
| D5-Q4 | `D5.Q4` | `REAL-EFECT` | Realismo y efectos no deseados | ¿El plan evalúa si la ambición es realista y considera efectos no deseados? |
| D5-Q5 | `D5.Q5` | `SOST-IMP` | Sostenibilidad de impactos | ¿El plan describe cómo se sostendrán los impactos más allá del periodo de gobierno? |

#### DIMENSIÓN 6: COHERENCIA CAUSAL (DIM06/COH) — 5 Preguntas

| Slot | Código | Abreviatura | Título | Pregunta Genérica |
|------|--------|-------------|--------|-------------------|
| D6-Q1 | `D6.Q1` | `TdC-EXPL` | Teoría de cambio explícita | ¿El plan presenta descripción explícita de cómo se generan los cambios? |
| D6-Q2 | `D6.Q2` | `PROP-REAL` | Proporcionalidad y realismo | ¿El plan evita saltos desproporcionados en su lógica causal? |
| D6-Q3 | `D6.Q3` | `COMPLEJ-APREND` | Complejidad y aprendizaje | ¿El plan reconoce complejidad y propone mecanismos para ajustar? |
| D6-Q4 | `D6.Q4` | `MONIT-RETRO` | Sistema de monitoreo | ¿Se describe un sistema de monitoreo con retroalimentación? |
| D6-Q5 | `D6.Q5` | `CONTEXT-TERR` | Contextualización territorial | ¿El plan considera el contexto municipal específico y grupos diferenciados? |

---

### 3.2 Mapeo Completo de 300 Preguntas MICRO

#### Fórmula de Derivación

```
question_id = Q + [((PA_index - 1) × 30) + ((DIM_index - 1) × 5) + Q_index]

Donde:
- PA_index = 1..10 (PA01 = 1, PA10 = 10)
- DIM_index = 1..6 (DIM01 = 1, DIM06 = 6)
- Q_index = 1..5 (Q1..Q5 dentro de cada dimensión)
```

#### Tabla de Preguntas por Área de Política

##### PA01 — Derechos de las mujeres e igualdad de género (Q001-Q030)

| Slot | question_id | question_global | Abrev | Tema |
|------|-------------|-----------------|-------|------|
| D1-Q1 | Q001 | 1 | PA01-LB-FUENTE | Líneas base género |
| D1-Q2 | Q002 | 2 | PA01-BRECHA-VACIO | Brechas género |
| D1-Q3 | Q003 | 3 | PA01-RECUR-ASIG | Recursos género |
| D1-Q4 | Q004 | 4 | PA01-CAP-INST | Capacidades género |
| D1-Q5 | Q005 | 5 | PA01-ALCANCE-COMP | Alcance género |
| D2-Q1 | Q006 | 6 | PA01-ACT-OPER | Actividades género |
| D2-Q2 | Q007 | 7 | PA01-DET-INSTR | Instrumentos género |
| D2-Q3 | Q008 | 8 | PA01-VINC-CAUSA | Vínculos causas género |
| D2-Q4 | Q009 | 9 | PA01-RIESG-MITIG | Riesgos género |
| D2-Q5 | Q010 | 10 | PA01-COH-ESTRAT | Coherencia género |
| D3-Q1 | Q011 | 11 | PA01-IND-PROD | Indicadores prod género |
| D3-Q2 | Q012 | 12 | PA01-PROP-META | Proporcionalidad género |
| D3-Q3 | Q013 | 13 | PA01-TRAZ-PRES | Trazabilidad género |
| D3-Q4 | Q014 | 14 | PA01-FACT-ACT | Factibilidad género |
| D3-Q5 | Q015 | 15 | PA01-MEC-PROD-RES | Mecanismo género |
| D4-Q1 | Q016 | 16 | PA01-IND-RES | Indicadores result género |
| D4-Q2 | Q017 | 17 | PA01-RUTA-CAUS | Ruta causal género |
| D4-Q3 | Q018 | 18 | PA01-JUST-AMB | Justificación género |
| D4-Q4 | Q019 | 19 | PA01-ATEN-PRIOR | Atención prior género |
| D4-Q5 | Q020 | 20 | PA01-ALIN-MARC | Alineación género |
| D5-Q1 | Q021 | 21 | PA01-IMP-LP | Impactos LP género |
| D5-Q2 | Q022 | 22 | PA01-IND-PROXY | Proxies género |
| D5-Q3 | Q023 | 23 | PA01-RIESG-SIST | Riesgos sist género |
| D5-Q4 | Q024 | 24 | PA01-REAL-EFECT | Realismo género |
| D5-Q5 | Q025 | 25 | PA01-SOST-IMP | Sostenibilidad género |
| D6-Q1 | Q026 | 26 | PA01-TdC-EXPL | TdC género |
| D6-Q2 | Q027 | 27 | PA01-PROP-REAL | Proporcionalidad género |
| D6-Q3 | Q028 | 28 | PA01-COMPLEJ-APREND | Complejidad género |
| D6-Q4 | Q029 | 29 | PA01-MONIT-RETRO | Monitoreo género |
| D6-Q5 | Q030 | 30 | PA01-CONTEXT-TERR | Contexto género |

##### PA02 — Prevención de la violencia... (Q031-Q060)

| Slot | question_id | question_global | Abrev | Tema |
|------|-------------|-----------------|-------|------|
| D1-Q1 | Q031 | 31 | PA02-LB-FUENTE | Líneas base violencia |
| D1-Q2 | Q032 | 32 | PA02-BRECHA-VACIO | Brechas violencia |
| D1-Q3 | Q033 | 33 | PA02-RECUR-ASIG | Recursos violencia |
| D1-Q4 | Q034 | 34 | PA02-CAP-INST | Capacidades violencia |
| D1-Q5 | Q035 | 35 | PA02-ALCANCE-COMP | Alcance violencia |
| D2-Q1 | Q036 | 36 | PA02-ACT-OPER | Actividades violencia |
| D2-Q2 | Q037 | 37 | PA02-DET-INSTR | Instrumentos violencia |
| D2-Q3 | Q038 | 38 | PA02-VINC-CAUSA | Vínculos violencia |
| D2-Q4 | Q039 | 39 | PA02-RIESG-MITIG | Riesgos violencia |
| D2-Q5 | Q040 | 40 | PA02-COH-ESTRAT | Coherencia violencia |
| D3-Q1 | Q041 | 41 | PA02-IND-PROD | Indicadores prod violencia |
| D3-Q2 | Q042 | 42 | PA02-PROP-META | Proporcionalidad violencia |
| D3-Q3 | Q043 | 43 | PA02-TRAZ-PRES | Trazabilidad violencia |
| D3-Q4 | Q044 | 44 | PA02-FACT-ACT | Factibilidad violencia |
| D3-Q5 | Q045 | 45 | PA02-MEC-PROD-RES | Mecanismo violencia |
| D4-Q1 | Q046 | 46 | PA02-IND-RES | Indicadores result violencia |
| D4-Q2 | Q047 | 47 | PA02-RUTA-CAUS | Ruta causal violencia |
| D4-Q3 | Q048 | 48 | PA02-JUST-AMB | Justificación violencia |
| D4-Q4 | Q049 | 49 | PA02-ATEN-PRIOR | Atención prior violencia |
| D4-Q5 | Q050 | 50 | PA02-ALIN-MARC | Alineación violencia |
| D5-Q1 | Q051 | 51 | PA02-IMP-LP | Impactos LP violencia |
| D5-Q2 | Q052 | 52 | PA02-IND-PROXY | Proxies violencia |
| D5-Q3 | Q053 | 53 | PA02-RIESG-SIST | Riesgos sist violencia |
| D5-Q4 | Q054 | 54 | PA02-REAL-EFECT | Realismo violencia |
| D5-Q5 | Q055 | 55 | PA02-SOST-IMP | Sostenibilidad violencia |
| D6-Q1 | Q056 | 56 | PA02-TdC-EXPL | TdC violencia |
| D6-Q2 | Q057 | 57 | PA02-PROP-REAL | Proporcionalidad violencia |
| D6-Q3 | Q058 | 58 | PA02-COMPLEJ-APREND | Complejidad violencia |
| D6-Q4 | Q059 | 59 | PA02-MONIT-RETRO | Monitoreo violencia |
| D6-Q5 | Q060 | 60 | PA02-CONTEXT-TERR | Contexto violencia |

##### PA03 — Ambiente sano... (Q061-Q090)

| Rango | Patrón | Tema |
|-------|--------|------|
| Q061-Q065 | DIM01 | Insumos ambiente |
| Q066-Q070 | DIM02 | Actividades ambiente |
| Q071-Q075 | DIM03 | Productos ambiente |
| Q076-Q080 | DIM04 | Resultados ambiente |
| Q081-Q085 | DIM05 | Impactos ambiente |
| Q086-Q090 | DIM06 | Coherencia ambiente |

##### PA04 — Derechos económicos, sociales y culturales (Q091-Q120)

| Rango | Patrón | Tema |
|-------|--------|------|
| Q091-Q095 | DIM01 | Insumos DESC |
| Q096-Q100 | DIM02 | Actividades DESC |
| Q101-Q105 | DIM03 | Productos DESC |
| Q106-Q110 | DIM04 | Resultados DESC |
| Q111-Q115 | DIM05 | Impactos DESC |
| Q116-Q120 | DIM06 | Coherencia DESC |

##### PA05 — Derechos de las víctimas... (Q121-Q150)

| Rango | Patrón | Tema |
|-------|--------|------|
| Q121-Q125 | DIM01 | Insumos víctimas |
| Q126-Q130 | DIM02 | Actividades víctimas |
| Q131-Q135 | DIM03 | Productos víctimas |
| Q136-Q140 | DIM04 | Resultados víctimas |
| Q141-Q145 | DIM05 | Impactos víctimas |
| Q146-Q150 | DIM06 | Coherencia víctimas |

##### PA06 — Niñez, adolescencia, juventud... (Q151-Q180)

| Rango | Patrón | Tema |
|-------|--------|------|
| Q151-Q155 | DIM01 | Insumos niñez |
| Q156-Q160 | DIM02 | Actividades niñez |
| Q161-Q165 | DIM03 | Productos niñez |
| Q166-Q170 | DIM04 | Resultados niñez |
| Q171-Q175 | DIM05 | Impactos niñez |
| Q176-Q180 | DIM06 | Coherencia niñez |

##### PA07 — Tierras y territorios (Q181-Q210)

| Rango | Patrón | Tema |
|-------|--------|------|
| Q181-Q185 | DIM01 | Insumos tierras |
| Q186-Q190 | DIM02 | Actividades tierras |
| Q191-Q195 | DIM03 | Productos tierras |
| Q196-Q200 | DIM04 | Resultados tierras |
| Q201-Q205 | DIM05 | Impactos tierras |
| Q206-Q210 | DIM06 | Coherencia tierras |

##### PA08 — Líderes y lideresas... (Q211-Q240)

| Rango | Patrón | Tema |
|-------|--------|------|
| Q211-Q215 | DIM01 | Insumos líderes |
| Q216-Q220 | DIM02 | Actividades líderes |
| Q221-Q225 | DIM03 | Productos líderes |
| Q226-Q230 | DIM04 | Resultados líderes |
| Q231-Q235 | DIM05 | Impactos líderes |
| Q236-Q240 | DIM06 | Coherencia líderes |

##### PA09 — Crisis de derechos PPL (Q241-Q270)

| Rango | Patrón | Tema |
|-------|--------|------|
| Q241-Q245 | DIM01 | Insumos PPL |
| Q246-Q250 | DIM02 | Actividades PPL |
| Q251-Q255 | DIM03 | Productos PPL |
| Q256-Q260 | DIM04 | Resultados PPL |
| Q261-Q265 | DIM05 | Impactos PPL |
| Q266-Q270 | DIM06 | Coherencia PPL |

##### PA10 — Migración transfronteriza (Q271-Q300)

| Rango | Patrón | Tema |
|-------|--------|------|
| Q271-Q275 | DIM01 | Insumos migración |
| Q276-Q280 | DIM02 | Actividades migración |
| Q281-Q285 | DIM03 | Productos migración |
| Q286-Q290 | DIM04 | Resultados migración |
| Q291-Q295 | DIM05 | Impactos migración |
| Q296-Q300 | DIM06 | Coherencia migración |

---

## 4. NIVEL MESO: 4 PREGUNTAS DE INTEGRACIÓN POR CLUSTER

### 4.1 Especificación de Preguntas MESO

| ID | question_global | Cluster | Código | Áreas Integradas | Pregunta |
|----|-----------------|---------|--------|------------------|----------|
| **MESO_1** | 301 | CL01 | `MESO-SEC-PAZ` | PA02, PA05, PA07 | ¿Cómo se integran las políticas en el cluster Seguridad y Paz? |
| **MESO_2** | 302 | CL02 | `MESO-GP` | PA01, PA06, PA08 | ¿Cómo se integran las políticas en el cluster Grupos Poblacionales? |
| **MESO_3** | 303 | CL03 | `MESO-TERR-AMB` | PA03, PA04 | ¿Cómo se integran las políticas en el cluster Territorio-Ambiente? |
| **MESO_4** | 304 | CL04 | `MESO-DESC-CRI` | PA09, PA10 | ¿Cómo se integran las políticas en el cluster Derechos Sociales & Crisis? |

### 4.2 Lógica de Agregación MESO

```
MESO_score = weighted_average(PA_scores) × integration_factor

Donde:
- PA_scores = puntajes de las PA del cluster
- integration_factor = coherence_score × cross_reference_score
```

### 4.3 Patrones de Evaluación MESO

Cada pregunta MESO evalúa:

1. **cross_reference**: Referencias cruzadas entre áreas del cluster
2. **coherence**: Coherencia narrativa entre políticas

---

## 5. NIVEL MACRO: PREGUNTA DE COHERENCIA GLOBAL

### 5.1 Especificación de Pregunta MACRO

| ID | question_global | Código | Abreviatura | Pregunta Completa |
|----|-----------------|--------|-------------|-------------------|
| **MACRO_1** | 305 | `MACRO-1` | `PDM-GLOBAL` | ¿El Plan de Desarrollo presenta una visión integral y coherente que articula todos los clusters y dimensiones? |

### 5.2 Componentes de Evaluación MACRO

| Patrón | Prioridad | Descripción |
|--------|-----------|-------------|
| `narrative_coherence` | 1 | Evaluar coherencia narrativa global del plan |
| `cross_cluster_integration` | 1 | Verificar integración entre todos los clusters |
| `long_term_vision` | 2 | Evaluar visión de largo plazo y transformación estructural |

### 5.3 Lógica de Agregación MACRO

```
MACRO_score = holistic_assessment(
    all_cluster_scores,
    narrative_coherence,
    cross_cluster_integration,
    long_term_vision
)

Scoring Modality: MACRO_HOLISTIC
Fallback: MACRO_AMBIGUO (priority 999)
```

---

## ANEXO A: SLOTS Y EQUIVALENCIA POSICIONAL RELATIVA

### A.1 Definición de Slots

Un **Slot** es la posición genérica de una pregunta dentro de la matriz 6×5 (Dimensión × Pregunta).

| Slot | Notación | Significado |
|------|----------|-------------|
| D1-Q1 | Dimensión 1, Pregunta 1 | Primera pregunta de Insumos |
| D1-Q2 | Dimensión 1, Pregunta 2 | Segunda pregunta de Insumos |
| ... | ... | ... |
| D6-Q5 | Dimensión 6, Pregunta 5 | Quinta pregunta de Coherencia |

### A.2 Equivalencia Posicional Relativa

Las preguntas con el **mismo slot** son **equivalentes posicionales** entre áreas de política.

```
Ejemplo: D1-Q1 (Líneas base con fuente)

PA01: Q001 → Líneas base de género
PA02: Q031 → Líneas base de prevención de violencia
PA03: Q061 → Líneas base de ambiente
PA04: Q091 → Líneas base de DESC
PA05: Q121 → Líneas base de víctimas
PA06: Q151 → Líneas base de niñez
PA07: Q181 → Líneas base de tierras
PA08: Q211 → Líneas base de líderes
PA09: Q241 → Líneas base de PPL
PA10: Q271 → Líneas base de migración
```

### A.3 Tabla de Equivalencia Posicional Completa

| Slot | Código | PA01 | PA02 | PA03 | PA04 | PA05 | PA06 | PA07 | PA08 | PA09 | PA10 |
|------|--------|------|------|------|------|------|------|------|------|------|------|
| D1-Q1 | LB-FUENTE | Q001 | Q031 | Q061 | Q091 | Q121 | Q151 | Q181 | Q211 | Q241 | Q271 |
| D1-Q2 | BRECHA-VACIO | Q002 | Q032 | Q062 | Q092 | Q122 | Q152 | Q182 | Q212 | Q242 | Q272 |
| D1-Q3 | RECUR-ASIG | Q003 | Q033 | Q063 | Q093 | Q123 | Q153 | Q183 | Q213 | Q243 | Q273 |
| D1-Q4 | CAP-INST | Q004 | Q034 | Q064 | Q094 | Q124 | Q154 | Q184 | Q214 | Q244 | Q274 |
| D1-Q5 | ALCANCE-COMP | Q005 | Q035 | Q065 | Q095 | Q125 | Q155 | Q185 | Q215 | Q245 | Q275 |
| D2-Q1 | ACT-OPER | Q006 | Q036 | Q066 | Q096 | Q126 | Q156 | Q186 | Q216 | Q246 | Q276 |
| D2-Q2 | DET-INSTR | Q007 | Q037 | Q067 | Q097 | Q127 | Q157 | Q187 | Q217 | Q247 | Q277 |
| D2-Q3 | VINC-CAUSA | Q008 | Q038 | Q068 | Q098 | Q128 | Q158 | Q188 | Q218 | Q248 | Q278 |
| D2-Q4 | RIESG-MITIG | Q009 | Q039 | Q069 | Q099 | Q129 | Q159 | Q189 | Q219 | Q249 | Q279 |
| D2-Q5 | COH-ESTRAT | Q010 | Q040 | Q070 | Q100 | Q130 | Q160 | Q190 | Q220 | Q250 | Q280 |
| D3-Q1 | IND-PROD | Q011 | Q041 | Q071 | Q101 | Q131 | Q161 | Q191 | Q221 | Q251 | Q281 |
| D3-Q2 | PROP-META | Q012 | Q042 | Q072 | Q102 | Q132 | Q162 | Q192 | Q222 | Q252 | Q282 |
| D3-Q3 | TRAZ-PRES | Q013 | Q043 | Q073 | Q103 | Q133 | Q163 | Q193 | Q223 | Q253 | Q283 |
| D3-Q4 | FACT-ACT | Q014 | Q044 | Q074 | Q104 | Q134 | Q164 | Q194 | Q224 | Q254 | Q284 |
| D3-Q5 | MEC-PROD-RES | Q015 | Q045 | Q075 | Q105 | Q135 | Q165 | Q195 | Q225 | Q255 | Q285 |
| D4-Q1 | IND-RES | Q016 | Q046 | Q076 | Q106 | Q136 | Q166 | Q196 | Q226 | Q256 | Q286 |
| D4-Q2 | RUTA-CAUS | Q017 | Q047 | Q077 | Q107 | Q137 | Q167 | Q197 | Q227 | Q257 | Q287 |
| D4-Q3 | JUST-AMB | Q018 | Q048 | Q078 | Q108 | Q138 | Q168 | Q198 | Q228 | Q258 | Q288 |
| D4-Q4 | ATEN-PRIOR | Q019 | Q049 | Q079 | Q109 | Q139 | Q169 | Q199 | Q229 | Q259 | Q289 |
| D4-Q5 | ALIN-MARC | Q020 | Q050 | Q080 | Q110 | Q140 | Q170 | Q200 | Q230 | Q260 | Q290 |
| D5-Q1 | IMP-LP | Q021 | Q051 | Q081 | Q111 | Q141 | Q171 | Q201 | Q231 | Q261 | Q291 |
| D5-Q2 | IND-PROXY | Q022 | Q052 | Q082 | Q112 | Q142 | Q172 | Q202 | Q232 | Q262 | Q292 |
| D5-Q3 | RIESG-SIST | Q023 | Q053 | Q083 | Q113 | Q143 | Q173 | Q203 | Q233 | Q263 | Q293 |
| D5-Q4 | REAL-EFECT | Q024 | Q054 | Q084 | Q114 | Q144 | Q174 | Q204 | Q234 | Q264 | Q294 |
| D5-Q5 | SOST-IMP | Q025 | Q055 | Q085 | Q115 | Q145 | Q175 | Q205 | Q235 | Q265 | Q295 |
| D6-Q1 | TdC-EXPL | Q026 | Q056 | Q086 | Q116 | Q146 | Q176 | Q206 | Q236 | Q266 | Q296 |
| D6-Q2 | PROP-REAL | Q027 | Q057 | Q087 | Q117 | Q147 | Q177 | Q207 | Q237 | Q267 | Q297 |
| D6-Q3 | COMPLEJ-APREND | Q028 | Q058 | Q088 | Q118 | Q148 | Q178 | Q208 | Q238 | Q268 | Q298 |
| D6-Q4 | MONIT-RETRO | Q029 | Q059 | Q089 | Q119 | Q149 | Q179 | Q209 | Q239 | Q269 | Q299 |
| D6-Q5 | CONTEXT-TERR | Q030 | Q060 | Q090 | Q120 | Q150 | Q180 | Q210 | Q240 | Q270 | Q300 |

### A.4 Fórmula de children_questions

Cada pregunta genérica tiene 10 "hijos" (una por PA):

```python
def get_children_for_slot(dim_index, q_index):
    """
    dim_index: 1-6 (DIM01-DIM06)
    q_index: 1-5 (Q1-Q5 dentro de la dimensión)
    """
    base_offset = (dim_index - 1) * 5 + q_index
    children = []
    for pa in range(10):  # PA01-PA10
        q_id = f"Q{(pa * 30) + base_offset:03d}"
        children.append(q_id)
    return children

# Ejemplo: D1-Q1 → [Q001, Q031, Q061, Q091, Q121, Q151, Q181, Q211, Q241, Q271]
```

---

## ANEXO B: CATÁLOGO DE CÓDIGOS ADICIONALES

### B.1 Modalidades de Scoring

| Código | Nivel | Descripción |
|--------|-------|-------------|
| `TYPE_A` | MICRO | Scoring estándar para preguntas específicas |
| `TYPE_B` | MICRO | Scoring con pesos diferenciados |
| `TYPE_C` | MICRO | Scoring binario (cumple/no cumple) |
| `TYPE_D` | MICRO | Scoring financiero |
| `MESO_INTEGRATION` | MESO | Agregación por cluster |
| `MACRO_HOLISTIC` | MACRO | Evaluación holística global |

### B.2 Códigos de Patrones

| Prefijo | Ejemplo | Uso |
|---------|---------|-----|
| `PAT-QXXX-YYY` | PAT-Q001-002 | Patrón YYY de pregunta QXXX |
| `PAT-GLOBAL-XXX` | PAT-GLOBAL-001 | Patrón aplicable globalmente |

### B.3 Códigos de Fallo (Failure Contracts)

| Código | Significado |
|--------|-------------|
| `ABORT-QXXX-REQ` | Abortar por requisito faltante en QXXX |
| `ABORT-DX-QY-PAZ-REQ` | Abortar DIM X, Q Y, PA Z por requisito |
| `MACRO_AMBIGUO` | Fallback cuando evaluación macro es indeterminada |

### B.4 Tipos de Match de Patrones

| Tipo | Descripción |
|------|-------------|
| `REGEX` | Expresión regular |
| `LITERAL` | Coincidencia literal |
| `SEMANTIC` | Búsqueda semántica (embeddings) |
| `NER_OR_REGEX` | Named Entity Recognition + Regex |
| `HYBRID` | Combinación de métodos |

### B.5 Categorías de Patrones

| Categoría | Descripción |
|-----------|-------------|
| `TEMPORAL` | Fechas, períodos, años |
| `GENERAL` | Patrones de propósito general |
| `FUENTE_OFICIAL` | Referencias a fuentes oficiales |
| `INDICADOR` | Indicadores cuantitativos |
| `UNIDAD_MEDIDA` | Unidades de medición |

### B.6 Glosario de Abreviaturas

| Abreviatura | Significado Completo |
|-------------|----------------------|
| PA | Policy Area (Área de Política) |
| DIM | Dimension (Dimensión de Análisis) |
| CL | Cluster (Agrupación Temática) |
| Q | Question (Pregunta) |
| LB | Línea Base |
| TdC | Teoría de Cambio |
| DESC | Derechos Económicos, Sociales y Culturales |
| PPL | Personas Privadas de la Libertad |
| VBG | Violencia Basada en Género |
| PPI | Plan Plurianual de Inversiones |
| BPIN | Banco de Proyectos de Inversión Nacional |
| SGP | Sistema General de Participaciones |
| PND | Plan Nacional de Desarrollo |
| ODS | Objetivos de Desarrollo Sostenible |
| RUV | Registro Único de Víctimas |
| PAPSIVI | Programa de Atención Psicosocial y Salud Integral a Víctimas |

---

**FIN DEL DOCUMENTO**

*Documento generado automáticamente por el sistema F.A.R.F.A.N 3.0*  
*Este documento es la FUENTE ÚNICA DE VERDAD para la notación canónica*
