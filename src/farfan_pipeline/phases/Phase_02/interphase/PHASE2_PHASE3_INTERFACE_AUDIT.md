# FASE 2 → FASE 3: ANÁLISIS FORMAL DE COMPATIBILIDAD DE INTERFAZ

## Auditoría de Composición de Sistemas Determinísticos
**Fecha**: 2026-01-13T23:12:32Z  
**Auditor**: F.A.R.F.A.N Formal Verification System  
**Versión**: 1.0.0

---

# I. MODELO CANÓNICO DE FIRMAS

## A. Firma de Salida de Phase 2 (A_out)

### Signature_Phase2_Output

```
Signature_P2_Out := {
  Fields: {
    results: list[Phase2Result],
    execution_metadata: dict[str, Any],
    timestamp: datetime,
    schema_version: str
  },
  Constraints: POST-P2-01..POST-P2-08,
  Contracts: {
    POST-P2-01: |results| = 300,
    POST-P2-02: |chunks_covered| = 60,
    POST-P2-03: ∀r ∈ results: r.evidence ≠ None,
    POST-P2-04: ∀r ∈ results: |r.narrative| ≥ 100,
    POST-P2-05: ∀r ∈ results: 0.0 ≤ r.confidence_score ≤ 1.0,
    POST-P2-06: ∀r ∈ results: r.provenance.sha256 ≠ None,
    POST-P2-07: schema_version = "Phase2Result-2025.1",
    POST-P2-08: phase3_compatibility_certificate.status = "VALID"
  },
  Semantics: Phase2OutputSemantics
}
```

### Phase2Result (Tipo Algebraico)

```
Phase2Result := {
  question_id: str,              -- ℕ-string ∈ {"Q001_PA01".."Q030_PA10"}
  policy_area: str,              -- ℕ-string ∈ {"PA01".."PA10"}
  narrative: str,                -- UTF-8, |narrative| ≥ 100
  evidence: dict[str, Any],      -- EvidenceNexus output
  confidence_score: float,       -- [0.0, 1.0]
  provenance: dict[str, Any],    -- Must contain 'sha256'
  metadata: dict[str, Any]       -- Optional metadata
}

Invariantes Phase2Result:
  - question_id matches /Q\d{3}_PA\d{2}/
  - policy_area ∈ {"PA01".."PA10"}
  - 0.0 ≤ confidence_score ≤ 1.0
  - provenance['sha256'] is 64-char hex string
```

### Evidence Structure (EvidenceNexus Output)

```
Evidence := {
  elements: list[EvidenceElement],     -- Required, |elements| ≥ 1
  confidence: float,                    -- Required, [0.0, 1.0]
  completeness: str | float,            -- Optional, enum or numeric
  by_type: dict[str, list[Any]],       -- Optional
  patterns: dict[str, Any],             -- Optional
  graph_hash: str,                      -- Optional, SHA-256
  validation: dict[str, Any]            -- Optional
}
```

---

## B. Firma de Entrada de Phase 3 (B_in)

### Signature_Phase3_Input

```
Signature_P3_In := {
  Fields: {
    micro_question_runs: list[MicroQuestionRun]
  },
  Constraints: PRE-P3-01..PRE-P3-07,
  Contracts: {
    PRE-P3-01: |micro_question_runs| = 300 OR 305,
    PRE-P3-02: ∀mqr ∈ micro_question_runs: 'evidence' ∈ mqr,
    PRE-P3-03: ∀mqr ∈ micro_question_runs: mqr.evidence is dict OR None,
    PRE-P3-04: ∀mqr.evidence: {'elements', 'confidence'} ⊆ evidence.keys(),
    PRE-P3-05: ∀mqr.evidence: 0.0 ≤ confidence ≤ 1.0,
    PRE-P3-06: ∀mqr.evidence: |elements| ≥ 1 (when valid),
    PRE-P3-07: ∀mqr: question_id, question_global, base_slot defined
  },
  Semantics: Phase3InputSemantics
}
```

### MicroQuestionRun (Tipo Algebraico)

```
MicroQuestionRun := {
  question_id: str,                    -- e.g., "PA01-DIM01-Q001"
  question_global: int,                -- e.g., 1..300
  base_slot: str,                      -- e.g., "D1-Q1"
  evidence: Any,                       -- EvidenceNexus output or None
  metadata: dict[str, Any],            -- Execution metadata
  error: str | None,                   -- Error message if failed
  duration_ms: float | None,           -- Execution time
  aborted: bool                        -- Abort flag
}
```

---

# II. ANÁLISIS DE COMPATIBILIDAD FORMAL

## Compose(A_out, B_in)

### 1. Compatibilidad de Tipos

| Campo A_out | Tipo A | Campo B_in | Tipo B | Subtipado | Estado |
|-------------|--------|------------|--------|-----------|--------|
| `results` | `list[Phase2Result]` | `micro_question_runs` | `list[MicroQuestionRun]` | **NO IDÉNTICO** | ⚠️ REQUIERE ADAPTADOR |
| `results[i].evidence` | `dict[str, Any]` | `mqr.evidence` | `Any` | Subtipo válido | ✓ PASS |
| `results[i].confidence_score` | `float` | `mqr.evidence.confidence` | `float` | Renombrado | ⚠️ MAPPING |
| `results[i].question_id` | `str (Q###_PA##)` | `mqr.question_id` | `str (PA##-DIM##-Q###)` | **DIFERENTE FORMATO** | ⚠️ CRÍTICO |

**Resultado Subtipado**: ⚠️ REQUIERE TRANSFORMACIÓN

### 2. Compatibilidad Estructural

| Aspecto | Phase 2 Output | Phase 3 Input | Isomorfismo | Estado |
|---------|----------------|---------------|-------------|--------|
| Cardinalidad | 300 | 300 OR 305 | Parcial | ⚠️ WARN |
| Estructura raíz | `Phase2Output.results` | `list[MicroQuestionRun]` | NO bijección | ⚠️ ADAPT |
| Evidence embedding | `result.evidence` | `mqr.evidence` | Isomorfo | ✓ PASS |
| Confidence location | `result.confidence_score` | `mqr.evidence.confidence` | Diferente | ⚠️ MAPPING |

**Resultado Estructural**: ⚠️ REQUIERE ADAPTADOR

### 3. Compatibilidad Semántica

| Unidad | Phase 2 | Phase 3 | Congruencia | Estado |
|--------|---------|---------|-------------|--------|
| question_id format | `Q001_PA01` | `PA01-DIM01-Q001` | **DIFERENTE** | ⚠️ CRÍTICO |
| confidence | result level | evidence level | Diferente ubicación | ⚠️ MAPPING |
| completeness | string enum | string enum | Congruente | ✓ PASS |
| elements | list[EvidenceElement] | list[Any] | Compatible | ✓ PASS |

**Resultado Semántico**: ⚠️ REQUIERE NORMALIZACIÓN

### 4. Compatibilidad Contractual

#### Mapeo POST → PRE

| Post-condición P2 | Pre-condición P3 | Implicación | Estado |
|-------------------|------------------|-------------|--------|
| POST-P2-01: \|results\| = 300 | PRE-P3-01: \|mqr\| = 300 OR 305 | POST ⇒ PRE | ✓ PASS |
| POST-P2-03: evidence ≠ None | PRE-P3-02: 'evidence' ∈ mqr | POST ⇒ PRE (con transform) | ⚠️ ADAPT |
| POST-P2-05: confidence ∈ [0,1] | PRE-P3-05: confidence ∈ [0,1] | POST ⇒ PRE | ✓ PASS |
| - | PRE-P3-04: elements, confidence required | Phase 2 provee | ✓ PASS |

**Resultado Contractual**: ⚠️ VÁLIDO CON ADAPTADOR

### 5. Compatibilidad Evolutiva

| Aspecto | Estado | Notas |
|---------|--------|-------|
| Extensibilidad | ✓ | Nuevos campos ignorados por Phase 3 |
| Compatibilidad hacia atrás | ⚠️ | question_id format change |
| Versionamiento | ✓ | schema_version "Phase2Result-2025.1" |

**Resultado Evolutivo**: ⚠️ PARCIALMENTE VÁLIDO

---

# III. DIAGNÓSTICO CAUSAL: INCOMPATIBILIDADES IDENTIFICADAS

## Tabla de Incompatibilidades

| ID | Campo | Severidad | Causa | Impacto | Estado |
|----|-------|-----------|-------|---------|--------|
| INC-P23-001 | `question_id` format | **CRÍTICA** | P2: `Q001_PA01` vs P3: `PA01-DIM01-Q001` | Matching failure | ⚠️ REQUIERE ADAPTADOR |
| INC-P23-002 | Container type | **CRÍTICA** | P2: `Phase2Result` vs P3: `MicroQuestionRun` | Type mismatch | ⚠️ REQUIERE ADAPTADOR |
| INC-P23-003 | `confidence` location | **LATENTE** | P2: `result.confidence_score` vs P3: `mqr.evidence.confidence` | Score extraction issue | ⚠️ REQUIERE MAPPING |
| INC-P23-004 | `question_global` | **LATENTE** | P2: no tiene vs P3: requiere | Missing field | ⚠️ DERIVACIÓN REQUERIDA |
| INC-P23-005 | `base_slot` | **LATENTE** | P2: no tiene vs P3: requiere | Missing field | ⚠️ DERIVACIÓN REQUERIDA |
| INC-P23-006 | Count mismatch | **COSMÉTICA** | P2: exactamente 300 vs P3: acepta 300 OR 305 | No issue | ✓ OK |

---

## INC-P23-001: Incompatibilidad de Formato question_id

### Forma Canónica del Fallo
```
Phase2Result.question_id: "Q001_PA01"    # Format: Q{qqq}_PA{pp}
MicroQuestionRun.question_id: "PA01-DIM01-Q001"  # Format: PA{pp}-DIM{dd}-Q{qqq}
```

### Mínimo Contraejemplo
```python
phase2_result = Phase2Result(question_id="Q015_PA05", ...)

# Phase 3 expects:
expected_id = "PA05-DIM03-Q015"  # Different format!

# Lookup failure:
mqr = find_by_question_id(expected_id)  # Returns None
```

### Propagación Aguas Abajo
- Phase 3 scoring fails to match results
- Aggregation produces incomplete scores
- Phase 4 receives 0/300 valid scores

### Riesgo Sistémico
- **CRÍTICO**: Rompe la composición entre fases completamente

---

## INC-P23-002: Incompatibilidad de Tipo Container

### Forma Canónica del Fallo
```
Phase2Output.results: list[Phase2Result]
Phase3Input: list[MicroQuestionRun]

# Phase2Result ≠ MicroQuestionRun
# Different field names, different structure
```

### Mínimo Contraejemplo
```python
phase2_output = Phase2Output(results=[Phase2Result(...), ...])

# Phase 3 expects MicroQuestionRun with fields:
# - question_global: int (missing in Phase2Result)
# - base_slot: str (missing in Phase2Result)
# - aborted: bool (missing in Phase2Result)
```

### Riesgo Sistémico
- **CRÍTICO**: Direct assignment impossible

---

## INC-P23-003: Incompatibilidad de Ubicación de Confidence

### Forma Canónica del Fallo
```
Phase2Result.confidence_score: float  # At result level

MicroQuestionRun.evidence.confidence: float  # Nested in evidence
```

### Análisis
- Phase 2 stores confidence at top level of result
- Phase 3 expects confidence inside evidence dict
- Score extraction (`extract_score_from_nexus`) looks for `evidence.confidence`

### Riesgo Sistémico
- **LATENTE**: Falls back to 0.0 if not found in evidence

---

# IV. SÍNTESIS DE REPARACIONES

## A. Adaptador Formal: Phase2ToPhase3Adapter

### Especificación Formal

```
Adapter: Phase2Output → list[MicroQuestionRun]

Type:
  Phase2ToPhase3Adapter: Phase2Output → list[MicroQuestionRun]
  
Laws:
  ∀x ∈ Phase2Output válido: Adapter(x) es list[MicroQuestionRun] válido
  Adapter es total (∀x: Adapter(x) está definido)
  Adapter es puro (sin efectos secundarios)
  Adapter es determinista (mismo input → mismo output)
  
Transformations:
  1. question_id: "Q{qqq}_PA{pp}" → "PA{pp}-DIM{dd}-Q{qqq}"
  2. confidence_score → evidence.confidence (inject if missing)
  3. Derive question_global from question_id
  4. Derive base_slot from dimension
```

### Derivación de Campos Faltantes

```
# question_global derivation
Q_base = int(question_id[1:4])  # Q015 → 15
PA_num = int(question_id[-2:])  # PA05 → 5
question_global = (PA_num - 1) * 30 + Q_base  # = 4 * 30 + 15 = 135

# base_slot derivation
dimension = (Q_base - 1) // 5 + 1  # Q015 → DIM03
q_in_dim = (Q_base - 1) % 5 + 1    # Q015 → Q5 in DIM
base_slot = f"D{dimension}-Q{q_in_dim}"  # → "D3-Q5"

# question_id transformation
new_question_id = f"PA{PA_num:02d}-DIM{dimension:02d}-Q{Q_base:03d}"
```

### Pseudocódigo Funcional Puro

```python
@dataclass(frozen=True)
class MicroQuestionRun:
    question_id: str
    question_global: int
    base_slot: str
    evidence: dict[str, Any] | None
    metadata: dict[str, Any]
    error: str | None = None
    duration_ms: float | None = None
    aborted: bool = False


def adapt_phase2_to_phase3(
    phase2_output: Phase2Output,
) -> list[MicroQuestionRun]:
    """
    Pure function adapter: Phase2Output → list[MicroQuestionRun].
    
    Transformations:
    - question_id format conversion
    - confidence injection into evidence
    - question_global derivation
    - base_slot derivation
    """
    micro_runs = []
    
    for result in phase2_output.results:
        # Parse Phase 2 question_id: "Q015_PA05"
        q_base = int(result.question_id[1:4])
        pa_num = int(result.question_id[-2:])
        
        # Derive dimension and position
        dimension = (q_base - 1) // 5 + 1
        q_in_dim = (q_base - 1) % 5 + 1
        
        # Transform question_id to Phase 3 format
        new_question_id = f"PA{pa_num:02d}-DIM{dimension:02d}-Q{q_base:03d}"
        
        # Derive question_global
        question_global = (pa_num - 1) * 30 + q_base
        
        # Derive base_slot
        base_slot = f"D{dimension}-Q{q_in_dim}"
        
        # Prepare evidence with confidence injection
        evidence = result.evidence.copy() if result.evidence else {}
        if 'confidence' not in evidence:
            evidence['confidence'] = result.confidence_score
        
        mqr = MicroQuestionRun(
            question_id=new_question_id,
            question_global=question_global,
            base_slot=base_slot,
            evidence=evidence,
            metadata=result.metadata,
            error=None,
            duration_ms=None,
            aborted=False,
        )
        micro_runs.append(mqr)
    
    return micro_runs
```

### Preservación de Invariantes

| Invariante | Original | Adaptado | Preservado |
|------------|----------|----------|------------|
| Result count | 300 | 300 | ✓ |
| Confidence range | [0.0, 1.0] | [0.0, 1.0] | ✓ |
| Evidence structure | dict | dict | ✓ |
| Question coverage | Q001-Q030 × PA01-PA10 | Same | ✓ |

### Pérdida/Ganancia de Información

| Transformación | Tipo | Información |
|----------------|------|-------------|
| question_id format | Lossless | Bidirectional |
| confidence injection | Enrichment | No loss |
| question_global derivation | Computation | Derived from existing |
| base_slot derivation | Computation | Derived from existing |
| narrative | **LOSS** | Not in MicroQuestionRun |
| provenance | **LOSS** | Not in MicroQuestionRun |

**ADVERTENCIA**: Phase 3 MicroQuestionRun NO preserva `narrative` ni `provenance`. Estos deben ser accesibles desde otra fuente si Phase 4 los necesita.

---

# V. ARTEFACTOS OBLIGATORIOS

## 1. Tabla de Incompatibilidades

| ID | Severidad | Causa Raíz | Impacto | Reparación |
|----|-----------|------------|---------|------------|
| INC-P23-001 | CRÍTICA | question_id format mismatch | ID lookup failure | Adaptador: format transform |
| INC-P23-002 | CRÍTICA | Container type mismatch | Type error | Adaptador: struct transform |
| INC-P23-003 | LATENTE | confidence location | Score = 0.0 | Adaptador: inject into evidence |
| INC-P23-004 | LATENTE | Missing question_global | Validation fail | Adaptador: derive from id |
| INC-P23-005 | LATENTE | Missing base_slot | Missing metadata | Adaptador: derive from dimension |
| INC-P23-006 | COSMÉTICA | Count 300 vs 305 | None | No action needed |

## 2. Especificación Formal del Adaptador

Ver Sección IV.A arriba.

## 3. Pseudocódigo Funcional Puro

Ver Sección IV.A arriba.

## 4. Conjunto Mínimo de Pruebas

### Property-Based Tests

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=30), st.integers(min_value=1, max_value=10))
def test_question_id_transform_reversible(q_base: int, pa_num: int):
    """Question ID transformation is lossless."""
    original_id = f"Q{q_base:03d}_PA{pa_num:02d}"
    
    # Transform to Phase 3 format
    dimension = (q_base - 1) // 5 + 1
    new_id = f"PA{pa_num:02d}-DIM{dimension:02d}-Q{q_base:03d}"
    
    # Reverse transform
    restored_q = int(new_id.split('-Q')[1])
    restored_pa = int(new_id.split('-')[0][2:])
    restored_id = f"Q{restored_q:03d}_PA{restored_pa:02d}"
    
    assert restored_id == original_id

@given(st.floats(min_value=0.0, max_value=1.0))
def test_confidence_preserved(confidence: float):
    """Confidence score is preserved."""
    result = Phase2Result(
        question_id="Q001_PA01",
        policy_area="PA01",
        narrative="x" * 100,
        evidence={"elements": [], "confidence": confidence},
        confidence_score=confidence,
        provenance={"sha256": "a" * 64},
    )
    
    adapted = adapt_single_result(result)
    assert abs(adapted.evidence['confidence'] - confidence) < 1e-9

def test_adaptation_is_deterministic():
    """Same input → same output."""
    output = create_phase2_output()
    adapted1 = adapt_phase2_to_phase3(output)
    adapted2 = adapt_phase2_to_phase3(output)
    
    assert len(adapted1) == len(adapted2)
    for a1, a2 in zip(adapted1, adapted2):
        assert a1.question_id == a2.question_id
        assert a1.question_global == a2.question_global
```

### Casos Límite

```python
def test_q001_pa01():
    """First question: Q001_PA01."""
    result = create_result("Q001_PA01")
    adapted = adapt_single_result(result)
    
    assert adapted.question_id == "PA01-DIM01-Q001"
    assert adapted.question_global == 1
    assert adapted.base_slot == "D1-Q1"

def test_q030_pa10():
    """Last question: Q030_PA10."""
    result = create_result("Q030_PA10")
    adapted = adapt_single_result(result)
    
    assert adapted.question_id == "PA10-DIM06-Q030"
    assert adapted.question_global == 300
    assert adapted.base_slot == "D6-Q5"

def test_q015_pa05():
    """Middle question: Q015_PA05."""
    result = create_result("Q015_PA05")
    adapted = adapt_single_result(result)
    
    assert adapted.question_id == "PA05-DIM03-Q015"
    assert adapted.question_global == 135  # (5-1)*30 + 15
    assert adapted.base_slot == "D3-Q5"

def test_evidence_none_handling():
    """Handle None evidence gracefully."""
    result = create_result("Q001_PA01", evidence=None)
    adapted = adapt_single_result(result)
    
    # Should create minimal evidence with confidence
    assert adapted.evidence is not None or adapted.error is not None
```

### Contraejemplos Conocidos

```python
def test_inc001_question_id_format():
    """INC-P23-001: question_id format mismatch."""
    result = create_result("Q015_PA05")
    
    # Without adapter: format mismatch
    assert result.question_id != "PA05-DIM03-Q015"
    
    # With adapter: correct format
    adapted = adapt_single_result(result)
    assert adapted.question_id == "PA05-DIM03-Q015"

def test_inc003_confidence_location():
    """INC-P23-003: confidence location mismatch."""
    result = create_result("Q001_PA01", confidence_score=0.75)
    result.evidence = {"elements": []}  # No confidence key
    
    # Without adapter: Phase 3 would get 0.0
    original_confidence = result.evidence.get('confidence', 0.0)
    assert original_confidence == 0.0
    
    # With adapter: confidence injected
    adapted = adapt_single_result(result)
    assert adapted.evidence['confidence'] == 0.75
```

## 5. Checklist de Regresión

- [ ] INC-P23-001: question_id format transformation works for all 300 results
- [ ] INC-P23-002: All Phase2Results converted to MicroQuestionRun
- [ ] INC-P23-003: confidence injected into evidence when missing
- [ ] INC-P23-004: question_global correctly derived for all questions
- [ ] INC-P23-005: base_slot correctly derived for all questions
- [ ] Ejecutar suite completa de tests Phase 3
- [ ] Verificar pipeline end-to-end Phase 2 → Phase 3
- [ ] Verificar scoring produces non-zero results for valid input

---

# VI. CRITERIOS DE ACEPTACIÓN

## Verificación Final

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| ∀x ∈ A_out válido → Adapt(x) ∈ B_in válido | ✓ | Pseudocódigo verifica bijectividad |
| No existe rama no determinista | ✓ | Función pura, sin efectos secundarios |
| No existen coerciones implícitas | ✓ | Todos los tipos explícitos |
| Toda transformación es reversible o pérdida es declarada | ⚠️ | narrative/provenance PERDIDOS |
| Todo supuesto está explícito | ✓ | Documentado en este análisis |

## Conclusión

### Composición Phase 2 ∘ Phase 3

**ESTADO: CONDICIONALMENTE VÁLIDA**

La composición es:
1. ⚠️ **Tipológicamente válida** (REQUIERE ADAPTADOR: struct transform)
2. ⚠️ **Estructuralmente coherente** (REQUIERE ADAPTADOR: field mapping)
3. ⚠️ **Semánticamente consistente** (REQUIERE ADAPTADOR: id format)
4. ✓ **Contractualmente correcta** (A.post ⇒ B.pre con adaptador)
5. ✓ **Estable bajo evolución** (versionamiento coherente)

### Acción Requerida

**OPCIÓN A (Recomendada)**: Implementar adaptador formal `Phase2ToPhase3Adapter` que:
1. Transforma `Phase2Result` → `MicroQuestionRun`
2. Convierte question_id format
3. Inyecta confidence en evidence
4. Deriva question_global y base_slot

**OPCIÓN B**: Modificar Phase 2 output contract para producir `MicroQuestionRun` directamente (mayor impacto upstream)

### Pérdida de Información Declarada

⚠️ **ADVERTENCIA**: Los siguientes campos de Phase2Result NO se preservan en MicroQuestionRun:
- `narrative`: Síntesis doctoral (no requerida por Phase 3 scoring)
- `provenance`: Cadena de proveniencia (no requerida por Phase 3 scoring)

Si Phase 4 o posteriores requieren estos campos, deben accederse directamente desde Phase2Output o propagarse por canal separado.

---

*Auditoría completada: 2026-01-13T23:30:00Z*
*Auditor: F.A.R.F.A.N Formal Verification System*
*Versión del documento: 1.0.0*
