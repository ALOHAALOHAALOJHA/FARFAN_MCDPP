# ARTEFACTO DE ANÁLISIS: DIAGNÓSTICO LOTE D5 Y CONTRATOS TYPE_D

**Fecha:** Martes, 23 de Diciembre de 2025
**Objetivo:** Consolidar la información derivada de los comandos de diagnóstico para el lote de contratos D5 y la definición canónica TYPE_D.

## 1. ANÁLISIS CANÓNICO (episte_refact.md)

La guía canónica define explícitamente el **TYPE_D** como **Financiero**.

*   **Definición:**
    *   **Nombre:** Financiero (Finance-Heavy)
    *   **Foco:** Suficiencia presupuestal, coherencia costo-meta.
    *   **Clases Dominantes:** `FinancialAuditor`, `PDETMunicipalPlanAnalyzer`.
    *   **Estrategia de Fusión:** Consistencia contable.

*   **Reglas de Ensamblaje (Assembly Rules) Canónicas para TYPE_D:**
    1.  **R1_financial_extraction** (Type: `empirical_basis`): Extracción de hechos financieros (`financial_facts`).
    2.  **R2_sufficiency_analysis** (Type: `computation`): Cálculo de suficiencia (`sufficiency_scores`).
    3.  **R3_coherence_audit** (Type: `financial_coherence_audit`): Auditoría de coherencia (`validated_financials`). *Critico: Usa `veto_gate`.*
    4.  **R4_synthesis** (Type: `synthesis`): Síntesis narrativa (`human_answer`).

## 2. ESTADO ACTUAL DEL LOTE D5 (contracts_v4)

Se analizaron los archivos `D5-Q1-v4.json` a `D5-Q5-v4.json`. Se observan inconsistencias críticas en la tipificación y reglas de ensamblaje.

| Contrato | Contract Type (Identity) | Assembly Rules (Detectadas) | Estado |
| :--- | :--- | :--- | :--- |
| **D5-Q1-v4.json** | **TYPE_D** | **Correctas (TYPE_D)** <br> (`R1_financial...`, `R2_sufficiency...`) | 🟢 **ALINEADO** |
| **D5-Q2-v4.json** | TYPE_A | Incorrectas (Generic/TYPE_A/B) | 🔴 **DESALINEADO** |
| **D5-Q3-v4.json** | TYPE_B | Incorrectas (TYPE_B Generic) | 🔴 **DESALINEADO** |
| **D5-Q4-v4.json** | TYPE_C | Incorrectas (TYPE_C Generic) | 🔴 **DESALINEADO** |
| **D5-Q5-v4.json** | **TYPE_D** | **Incorrectas (TYPE_B Generic)** <br> (`R2_bayesian_update`...) | 🔴 **INCONSISTENTE** |

**Hallazgos Clave:**
1.  Solo **D5-Q1** implementa correctamente la estructura `TYPE_D` definida en la guía canónica.
2.  **D5-Q5** se identifica como `TYPE_D` pero sus reglas de ensamblaje corresponden a un contrato probabilístico (`TYPE_B`), lo que generará errores de ejecución al intentar auditar aspectos financieros con lógica bayesiana.
3.  **D5-Q2, Q3, Q4** tienen tipos diversos (A, B, C) que no parecen corresponder con la intención de un lote financiero (D5), sugiriendo una generación heterogénea no controlada.

## 3. DISPONIBILIDAD DE MÉTODOS FINANCIEROS

El análisis de código confirma la existencia de métodos financieros listos para ser vinculados, ubicados principalmente en `financiero_viabilidad_tablas.py`.

*   **Métodos Detectados:**
    *   `_find_mediator_mentions` (N1-EMP)
    *   `generate_counterfactuals` (N2-INF)
    *   `_simulate_intervention` (N2-INF)
    *   `_generate_scenario_narrative` (N2-INF)

Estos métodos están alineados con la taxonomía `TYPE_D` pero actualmente **no están siendo utilizados** en los contratos desalineados (Q2-Q5), los cuales carecen de la fase `execution_phases` poblada con estos métodos específicos.

## 4. CONCLUSIÓN Y RECOMENDACIÓN

El lote D5 presenta una **fragmentación estructural**. La intención parece ser que todo el lote (o su mayoría) opere bajo la lógica financiera (`TYPE_D`), dado el análisis de dimensiones y la nomenclatura del lote.

**Acciones Inmediatas Requeridas:**
1.  **Refactorización Masiva:** Convertir D5-Q2, D5-Q3, D5-Q4 y reparar D5-Q5 para que adopten la estructura `TYPE_D` (Identity + Assembly Rules) usando D5-Q1 como plantilla maestra.
2.  **Vinculación de Métodos:** Asegurar que los métodos de `financiero_viabilidad_tablas.py` sean los inyectados en la sección `method_binding` de estos contratos.
3.  **Validación DIM05:** Confirmar si DIM05 corresponde exclusivamente al dominio financiero para estandarizar todos los contratos bajo este tipo.
