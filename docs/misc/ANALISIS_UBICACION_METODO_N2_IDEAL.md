# ANÁLISIS: UBICACIÓN DEL MÉTODO N2 IDEAL FALTANTE

## MÉTODO IDEAL FALTANTE

**Nombre propuesto:** `validate_semantic_completeness_coherence`

**Funcionalidad:**
- Validar coherencia meta-actividad (si las metas son coherentes con las actividades propuestas)
- Validar compatibilidad recursos-plazos (si los recursos son compatibles con los plazos temporales)
- Validar completitud mínima (si hay datos mínimos requeridos para constituir línea base válida)

**Nivel:** N2 (Validación semántica)
**Tipo:** TYPE_A compatible (determinista, no bayesiano)
**Requires:** `raw_facts` (de N1)

---

## OPCIONES DE UBICACIÓN

### OPCIÓN 1: `TemporalLogicVerifier` en `contradiction_deteccion.py`

**Ubicación:** `src/farfan_pipeline/methods/contradiction_deteccion.py`

**Ventajas:**
- ✅ Ya tiene métodos temporales (`_parse_temporal_marker`, `_build_timeline`)
- ✅ Ya tiene validación de compatibilidad (`_are_mutually_exclusive`, `_check_deadline_constraints`)
- ✅ Cohesión epistemológica: validación lógica temporal
- ✅ Bajo costo de refactorización: solo agregar método

**Desventajas:**
- ⚠️ Nombre sugiere solo temporal, pero el método necesita validar más
- ⚠️ No cubre "coherencia meta-actividad" (fuera del dominio temporal)

**Costo refactorización:** 🟢 BAJO (1-2 horas)
**Unidad epistemológica:** 🟡 MEDIA (solo cubre parte del dominio)

**Veredicto:** ⚠️ **PARCIAL** - Solo para validación recursos-plazos, no para meta-actividad

---

### OPCIÓN 2: `PolicyContradictionDetector` en `contradiction_deteccion.py`

**Ubicación:** `src/farfan_pipeline/methods/contradiction_deteccion.py`

**Ventajas:**
- ✅ Ya tiene métodos de coherencia (`_calculate_coherence_metrics`, `_calculate_objective_alignment`)
- ✅ Ya trabaja con `PolicyStatement` y estructuras complejas
- ✅ Tiene infraestructura para análisis semántico

**Desventajas:**
- ❌ Orientado a **detección de contradicciones** (más N3 que N2)
- ❌ Usa modelos bayesianos/transformers (contaminación epistemológica para TYPE_A)
- ❌ Métodos existentes son más complejos (detección vs validación simple)

**Costo refactorización:** 🔴 ALTO (requiere extraer lógica de validación de detección)
**Unidad epistemológica:** 🔴 BAJA (contaminación bayesiana, orientación N3)

**Veredicto:** ❌ **NO RECOMENDADO** - Contaminación epistemológica y orientación incorrecta

---

### OPCIÓN 3: `IndustrialPolicyProcessor` en `policy_processor.py`

**Ubicación:** `src/farfan_pipeline/methods/policy_processor.py`

**Ventajas:**
- ✅ Ya tiene `_apply_validation_rules` (validación canónica)
- ✅ Ya tiene `_match_patterns_in_sentences` (validación de patrones)
- ✅ Epistemología TYPE_A pura (sin bayesiano)
- ✅ Acceso a `VALIDATION_RULES` canónicas

**Desventajas:**
- ⚠️ Orientado a procesamiento general, no validación semántica específica
- ⚠️ Métodos existentes son más para matching de patrones que coherencia lógica
- ⚠️ No tiene infraestructura para análisis meta-actividad

**Costo refactorización:** 🟡 MEDIO (requiere agregar lógica de coherencia semántica)
**Unidad epistemológica:** 🟡 MEDIA (cohesión con validación, pero falta lógica semántica)

**Veredicto:** ⚠️ **VIABLE PERO SUBÓPTIMO** - Requiere agregar lógica que no está en el dominio del procesador

---

### OPCIÓN 4: Nueva clase `SemanticValidator` en `contradiction_deteccion.py`

**Ubicación:** `src/farfan_pipeline/methods/contradiction_deteccion.py` (nueva clase)

**Ventajas:**
- ✅ **Máxima unidad epistemológica:** Clase dedicada a validación semántica N2
- ✅ **Sin contaminación:** Separada de detección de contradicciones (N3) y extracción (N1)
- ✅ **Cohesión clara:** Todos los métodos N2 de validación semántica en un lugar
- ✅ **Escalable:** Fácil agregar más validaciones N2 en el futuro
- ✅ **Nombre explícito:** `SemanticValidator` deja claro su propósito

**Desventajas:**
- ⚠️ Requiere crear nueva clase (más código)
- ⚠️ Puede reutilizar métodos de `TemporalLogicVerifier` (composición)

**Costo refactorización:** 🟢 BAJO-MEDIO (crear clase nueva, reutilizar lógica existente)
**Unidad epistemológica:** 🟢 ALTA (máxima cohesión, propósito único)

**Veredicto:** ✅ **RECOMENDADO** - Máxima unidad epistemológica y claridad

---

### OPCIÓN 5: Nueva clase `SemanticValidator` en archivo separado

**Ubicación:** `src/farfan_pipeline/methods/semantic_validator.py` (nuevo archivo)

**Ventajas:**
- ✅ **Separación completa:** Archivo dedicado solo a validación semántica
- ✅ **Sin dependencias:** No contamina otros módulos
- ✅ **Máxima claridad:** Propósito único y explícito

**Desventajas:**
- ⚠️ Más archivos = más complejidad de estructura
- ⚠️ Puede requerir imports adicionales

**Costo refactorización:** 🟡 MEDIO (crear archivo nuevo, actualizar imports)
**Unidad epistemológica:** 🟢 ALTA (máxima separación)

**Veredicto:** ✅ **VIABLE** - Si se espera crecimiento futuro de validaciones N2

---

## COMPARACIÓN FINAL

| Opción | Ubicación | Costo Refactorización | Unidad Epistemológica | Escalabilidad | Veredicto |
|--------|-----------|----------------------|----------------------|---------------|-----------|
| **1. TemporalLogicVerifier** | `contradiction_deteccion.py` | 🟢 BAJO | 🟡 MEDIA | 🟡 MEDIA | ⚠️ PARCIAL |
| **2. PolicyContradictionDetector** | `contradiction_deteccion.py` | 🔴 ALTO | 🔴 BAJA | 🟡 MEDIA | ❌ NO |
| **3. IndustrialPolicyProcessor** | `policy_processor.py` | 🟡 MEDIO | 🟡 MEDIA | 🟡 MEDIA | ⚠️ SUBÓPTIMO |
| **4. SemanticValidator (mismo archivo)** | `contradiction_deteccion.py` | 🟢 BAJO-MEDIO | 🟢 ALTA | 🟢 ALTA | ✅ **RECOMENDADO** |
| **5. SemanticValidator (archivo nuevo)** | `semantic_validator.py` | 🟡 MEDIO | 🟢 ALTA | 🟢 ALTA | ✅ VIABLE |

---

## RECOMENDACIÓN FINAL

### 🎯 OPCIÓN RECOMENDADA: Opción 4

**Crear clase `SemanticValidator` en `contradiction_deteccion.py`**

**Justificación:**

1. **Unidad epistemológica máxima:**
   - Clase dedicada exclusivamente a validación semántica N2
   - Separada de detección de contradicciones (N3) y extracción (N1)
   - Propósito único y claro

2. **Costo de refactorización bajo-medio:**
   - Crear nueva clase en archivo existente (no requiere nuevo archivo)
   - Puede reutilizar métodos de `TemporalLogicVerifier` mediante composición
   - No requiere modificar código existente

3. **Escalabilidad:**
   - Fácil agregar más validaciones N2 en el futuro
   - Estructura clara para crecimiento
   - No contamina otros módulos

4. **Cohesión con código existente:**
   - `contradiction_deteccion.py` ya tiene `TemporalLogicVerifier` (validación temporal)
   - Puede reutilizar lógica temporal existente
   - Mantiene validaciones relacionadas en el mismo módulo

**Estructura propuesta:**

```python
class SemanticValidator:
    """
    Validación semántica N2 para TYPE_A contracts.
    
    Valida coherencia y completitud de datos extraídos sin inferencia bayesiana.
    Solo validación lógica determinista.
    """
    
    def __init__(self, temporal_verifier: TemporalLogicVerifier | None = None):
        self.temporal_verifier = temporal_verifier or TemporalLogicVerifier()
    
    def validate_semantic_completeness_coherence(
        self,
        raw_facts: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Valida coherencia meta-actividad, compatibilidad recursos-plazos,
        y completitud mínima de datos.
        
        Args:
            raw_facts: Datos extraídos por métodos N1
            
        Returns:
            dict con validaciones y resultados binarios (pass/fail)
        """
        # Implementación...
```

---

## COSTO DE REFACTORIZACIÓN DETALLADO

### Opción 4 (Recomendada):

**Tareas:**
1. Crear clase `SemanticValidator` en `contradiction_deteccion.py` (30 min)
2. Implementar `validate_semantic_completeness_coherence` (2-3 horas)
3. Reutilizar `TemporalLogicVerifier` mediante composición (30 min)
4. Agregar tests unitarios (1 hora)
5. Actualizar imports en contratos que lo usen (30 min)

**Total estimado:** 4-5 horas

**Riesgos:**
- 🟢 Bajo: No modifica código existente
- 🟢 Bajo: Solo agrega nueva funcionalidad
- 🟢 Bajo: Reutiliza código existente

---

## ALTERNATIVA: Opción 5 (Archivo separado)

Si se espera crecimiento significativo de validaciones N2, la Opción 5 es viable:

**Tareas adicionales:**
- Crear nuevo archivo `semantic_validator.py` (15 min)
- Actualizar `__init__.py` del módulo (5 min)
- Actualizar imports en múltiples lugares (30 min)

**Total estimado:** 5-6 horas

**Veredicto:** Opción 5 es mejor si se planea crear múltiples clases de validación N2 en el futuro.

---

## CONCLUSIÓN

**Recomendación:** **Opción 4** (clase `SemanticValidator` en `contradiction_deteccion.py`)

**Razones:**
- ✅ Máxima unidad epistemológica
- ✅ Bajo-medio costo de refactorización
- ✅ Escalable y claro
- ✅ Cohesión con código existente
- ✅ Sin contaminación epistemológica

**Próximos pasos:**
1. Crear clase `SemanticValidator` en `contradiction_deteccion.py`
2. Implementar método `validate_semantic_completeness_coherence`
3. Reutilizar `TemporalLogicVerifier` mediante composición
4. Agregar tests y documentación


