# Plantilla de Documentación de Pregunta (F.A.R.F.A.N)

## 1. Identificación
*   **ID Pregunta:** {{question_id}} (ej. Q006)
*   **Slot Canónico:** {{base_slot}} (ej. D2-Q1)
*   **Dimensión:** {{dimension_name}}
*   **Cluster:** {{cluster_id}}

## 2. Propósito y Racionalidad
*   **¿Qué evalúa esta pregunta?**
    {{description_of_purpose}}
*   **¿Por qué es crítica para el éxito del plan?**
    {{rationale_and_impact}}
*   **Contexto Normativo (Colombia):**
    *   {{law_or_policy_ref_1}}
    *   {{law_or_policy_ref_2}}

## 3. Criterios de Calidad y Evidencia Esperada
Para obtener una calificación alta, el plan debe demostrar:

| Elemento Esperado | Descripción Técnica | Patrones de Evidencia (Regex/Keywords) |
|-------------------|---------------------|----------------------------------------|
| {{element_1}} | {{tech_desc_1}} | `{{pattern_1}}` |
| {{element_2}} | {{tech_desc_2}} | `{{pattern_2}}` |

## 4. Guía de Interpretación de Puntaje

*   **EXCELENTE (3.0):** {{criteria_excellent}}
*   **BUENO (2.0):** {{criteria_good}}
*   **ACEPTABLE (1.0):** {{criteria_acceptable}}
*   **INSUFICIENTE (0.0):** {{criteria_insufficient}}

## 5. Ejemplos (Anónimos)

### ✅ Evidencia Fuerte
> "{{strong_example_text}}"
> *Análisis:* Este texto cumple porque...

### ⚠️ Evidencia Débil
> "{{weak_example_text}}"
> *Análisis:* Falta especificidad en...

### ❌ Ausencia de Evidencia
> "{{missing_example_text}}"

## 6. Errores Comunes
*   {{pitfall_1}}
*   {{pitfall_2}}

## 7. Estrategia de Validación Automática
Esta pregunta utiliza los siguientes métodos de validación:
1.  `{{method_1}}`: {{method_desc_1}}
2.  `{{method_2}}`: {{method_desc_2}}