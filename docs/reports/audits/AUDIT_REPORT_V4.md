# REPORTE DE AUDITORÍA - F.A.R.F.A.N Contract Generator v4.0.0

## RESUMEN EJECUTIVO
- **Fecha de auditoría:** 2026-01-03
- **Auditor:** Gemini CLI Auditor
- **Veredicto:** RECHAZADO
- **Severidad máxima encontrada:** CRÍTICA (El código no es ejecutable)

## CHECKLIST DE INVARIANTES
| Invariante | Status | Evidencia |
|------------|--------|-----------|
| E-001 Coherencia Nivel-Fase | ✓ | `input_registry.py`: `_validate_phase_level_coherence` (HARD FAILURE) |
| I-8 Preservación de Orden | ✓ | `chain_composer.py`: Uso de tuplas inmutables y comprensión ordenada |
| I-9 Sin Fusión Implícita | ✓ | `method_expander.py`: Relación 1:1 en expansión |
| Asimetría N3 | ✓ | `contract_assembler.py`: "N1 CANNOT invalidate N3" presente |
| Determinismo | ✓ | `json_emitter.py`: `sort_keys=False` (preserva orden inserción), `InputLoader` usa `sort_keys=True` para hashes |
| **300 Contratos** | **✗** | **FALLO CRÍTICO**: El generador itera solo sobre 30 preguntas, ignorando los 10 sectores. |

## MÉTRICAS OBTENIDAS
| Métrica | Valor Esperado | Valor Real |
|---------|----------------|------------|
| Total contratos | 300 | 30 (en ejecución previa) / 0 (crash actual) |
| Ejecución | Exitosa | **CRASH** (`TypeError` al importar) |

## HALLAZGOS

### Críticos (bloquean producción)
1.  **Código NO Ejecutable (TypeError):**
    *   **Ubicación:** `method_expander.py`, clase `ExpandedMethodUnit`.
    *   **Descripción:** La dataclass define el campo `veto_conditions` con un valor por defecto (`default_factory=dict`) ANTES de campos obligatorios (`expansion_source`, `expansion_timestamp`). Esto es ilegal en Python y causa un `TypeError` inmediato al importar el módulo.
    *   **Evidencia:** `TypeError: non-default argument 'expansion_source' follows default argument`.

2.  **Incumplimiento de Alcance (300 Contratos):**
    *   **Ubicación:** `contract_generator.py`, método `generate()`.
    *   **Descripción:** El bucle principal itera solo sobre `question_ids` (30 iteraciones). No existe el bucle anidado sobre los 10 sectores requerido para generar los 300 contratos.
    *   **Evidencia:** `contracts_v4` contiene solo 30 archivos (`D1_Q1`...`D6_Q5`).

3.  **Firma de Método Incompatible:**
    *   **Ubicación:** `contract_generator.py` (Orquestador) vs `contract_assembler.py` (Ensamblador).
    *   **Descripción:** El orquestador llama a `assemble_contract(chain, classification)`, pero la definición del método exige 4 argumentos: `(chain, classification, sector, contract_number)`. Esto causará un `TypeError` en tiempo de ejecución (si se corrige el error anterior).

4.  **Falta de Definición de Sectores:**
    *   **Ubicación:** `input_registry.py` y sistema de archivos.
    *   **Descripción:** No se encontró la constante `SECTOR_DEFINITIONS` requerida en la auditoría, ni archivos `sectors.json` en los assets. El sistema no "conoce" los 10 sectores de política pública.

### Altos (degradan calidad)
1.  **Severidad de Validación N3:**
    *   **Ubicación:** `contract_validator.py`.
    *   **Descripción:** La validación de asimetría N3 está marcada como `ValidationSeverity.HIGH`. Según los criterios de rechazo absoluto ("Invariante VETO GATE - CRÍTICO"), debería ser `CRITICAL`. Una violación aquí degradaría la calidad pero no bloquearía la emisión del contrato bajo la lógica actual.

## TESTS EJECUTADOS
| Test | Resultado | Notas |
|------|-----------|-------|
| Ejecución de script | **FAIL** | Crash inmediato por error de sintaxis en Dataclass |
| Conteo de Salida | **FAIL** | 30 archivos encontrados vs 300 requeridos |
| Invariantes Estáticos | **PASS** | Revisión de código confirma E-001, I-8, I-9 |

## RECOMENDACIONES
1.  **Corregir Dataclass:** Mover `veto_conditions` al final de `ExpandedMethodUnit` o asignar valores por defecto a los campos siguientes.
2.  **Implementar Sectores:** Crear `sectors.json` con los 10 sectores (PA01-PA10) y cargarlos en `InputRegistry`.
3.  **Corregir Orquestador:** Modificar `ContractGenerator.generate` para iterar `for question in questions: for sector in sectors: ...`.
4.  **Corregir Llamada a Assembler:** Pasar `sector` y `contract_number` (contador global 1-300) a `assemble_contract`.
5.  **Elevar Severidad:** Cambiar validación de asimetría N3 a `ValidationSeverity.CRITICAL`.
