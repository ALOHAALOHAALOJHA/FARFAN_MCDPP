---
description: Audit and correct batch D5 (Q1-Q5) contracts against episte_refact.md
---

# PROTOCOLO LOTE D5 (Dimensión 5)

## LOTE D5: Definición de Contratos y Tipos
```
| Contrato   | Question ID | Tipo Canónico | Estrategia Principal |
|------------|-------------|---------------|----------------------|
| D5-Q1-v4   | Q021        | TYPE_D        | financial_coherence_audit |
| D5-Q2-v4   | Q022        | TYPE_D        | financial_coherence_audit |
| D5-Q3-v4   | Q023        | TYPE_B        | bayesian_update |
| D5-Q4-v4   | Q024        | TYPE_B        | bayesian_update |
| D5-Q5-v4   | Q025        | TYPE_B        | bayesian_update |
```

## FASE D0: INICIALIZACIÓN (BLOQUEANTE)

### D0.1: Carga de Guía Canónica
```bash
view_file(/Users/recovered/PycharmProjects/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/episte_refact.md)
# SIN StartLine, SIN EndLine
```

**✅ CHECKPOINT D0.1:** Reporta primera línea, última línea (L3003), línea taxonomías (~L2915).

### D0.2: Extracción de Templates por Tipo
```
TYPE_B: bayesian_update pattern
TYPE_D: Líneas 447-490 (financial_coherence_audit)
```

### D0.3: Taxonomías Universales (L2915-3003)
- N1: "Base Empírica" / "Empirismo positivista"
- N2: "Procesamiento Inferencial" / "Bayesianismo subjetivista"
- N3: "Auditoría y Robustez" / "Falsacionismo popperiano"

---

## FASE D1: AUDITORÍA POR LOTE

### Para cada contrato [D5-Q1, D5-Q2, D5-Q3, D5-Q4, D5-Q5]:

#### D1.1: Carga de Contrato
```bash
view_file(/Users/recovered/PycharmProjects/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/contracts_v4/{contrato}-v4.json)
# SIN StartLine, SIN EndLine
```

#### D1.2: Validación de Tipo (BLOCKER)
```
Verificar contract_type en 3 ubicaciones:
1. identity.contract_type
2. fusion_specification.contract_type  
3. human_answer_structure.contract_type

DEBE coincidir con tabla de LOTE D5 arriba.
```

#### D1.3: Auditoría de 6 Partes
Para cada Parte [I, II, III, IV, V, VI]:
- Extraer reglas del template canónico (según TYPE)
- Comparar con valores en contrato
- Documentar: Campo | Guía L# | Contrato L# | Status

#### D1.4: Scoring
```
Score = (Campos Compliant / Campos Totales) × 100
STATUS: ✅ >= 95% | ⚠️ >= 80% | ❌ < 80%
```

---

## FASE C0: PLANIFICACIÓN DE CORRECCIONES

Priorizar por:
1. Desviaciones P0 (blockers)
2. Score (menor primero)

---

## FASE C1: EJECUCIÓN DE CORRECCIONES

Para cada contrato con Score < 95%:
1. Aplicar correcciones P0
2. Aplicar correcciones P1
3. Re-auditar
4. Confirmar Score >= 95%

---

## CRITERIO DE ÉXITO LOTE D5
```
✅ APROBADO ⟺ 
  - Promedio >= 95%
  - Min individual >= 90%
  - P0 desviaciones = 0
```
