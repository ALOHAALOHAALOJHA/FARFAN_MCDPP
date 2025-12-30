# GUÍA DE USO DEL CATÁLOGO EPISTEMOLÓGICAMENTE CERTIFICADO

## Catálogo Oficial

**Archivo**: `METHODS_DISPENSARY_SIGNATURES_ENRICHED_FORENSIC.json`  
**Estado**: ✅ CERTIFICADO EPISTEMOLÓGICAMENTE  
**Precisión**: 96.0% (557/580 métodos)  
**Fecha**: 2025-12-30  
**Hash**: `cb77749b438dfa914a0b8a5053964e48a19d02574f464383ce946f29b75cf05f`

---

## Verificación de Integridad

Para verificar que el catálogo no ha sido modificado:

```bash
# Verificar hash SHA256
sha256sum METHODS_DISPENSARY_SIGNATURES_ENRICHED_FORENSIC.json
# Debe producir: cb77749b438dfa914a0b8a5053964e48a19d02574f464383ce946f29b75cf05f

# Validar estructura contra BLOQUE 7
python3 validate_bloque7.py METHODS_DISPENSARY_SIGNATURES_ENRICHED_FORENSIC.json
# Debe producir: ✅ VALIDACIÓN EXITOSA

# Auditar rigor epistemológico
python3 audit_epistemological_rigor.py METHODS_DISPENSARY_SIGNATURES_ENRICHED_FORENSIC.json
# Debe producir: ⚠️ 23 ISSUES RESIDUALES (8 HIGH, 15 MEDIUM)
```

---

## Estructura del Catálogo

```json
{
  "ClassName": {
    "file_path": "src/...",
    "line_number": N,
    "class_level": "N1-EMP|N2-INF|N3-AUD|N4-SYN|INFRASTRUCTURE",
    "class_epistemology": "POSITIVIST_EMPIRICAL|BAYESIAN_PROBABILISTIC|...",
    "methods": {
      "method_name": {
        "line_number": M,
        "parameters": [...],
        "return_type": "...",
        "docstring": "...",
        "epistemological_classification": {
          "level": "N1-EMP|N2-INF|N3-AUD|N4-SYN|INFRASTRUCTURE",
          "output_type": "FACT|PARAMETER|CONSTRAINT|NARRATIVE|NONE",
          "fusion_behavior": "additive|multiplicative|gate|terminal|none",
          "epistemology": "...",
          "phase_assignment": "phase_A_construction|phase_B_computation|...",
          "dependencies": {
            "requires": [...],
            "produces": [...],
            "modulates": [...]
          },
          "contract_compatibility": {
            "TYPE_A": true|false,
            "TYPE_B": true|false,
            "TYPE_C": true|false,
            "TYPE_D": true|false,
            "TYPE_E": true|false
          },
          "veto_conditions": {...},  // Solo para N3-AUD
          "classification_evidence": {
            "selected_rule_id": "...",
            "matched_triggers": [...],
            "matched_anti_triggers": [...],
            "all_evaluations": [...]
          }
        }
      }
    }
  },
  "_pipeline_metadata": {
    "session_id": "...",
    "rulebook_hash": "...",
    "code_hash": "...",
    "git_commit": "...",
    "input_hash": "...",
    "output_hash": "...",
    "generated_at": "..."
  },
  "quality_metrics": {
    "total_classes": 127,
    "total_methods": 580,
    "n1_methods": 91,
    "n2_methods": 245,
    "n3_methods": 105,
    "n4_methods": 33,
    "infrastructure_methods": 106,
    "methods_with_veto": 105,
    "n3_without_veto": 0,
    "orphan_methods": 0,
    "validation_errors": []
  }
}
```

---

## Uso Programático

### Python

```python
import json

# Cargar catálogo
with open('METHODS_DISPENSARY_SIGNATURES_ENRICHED_FORENSIC.json', 'r') as f:
    catalog = json.load(f)

# Acceder a métodos de una clase
bayesian_analyzer = catalog['BayesianNumericalAnalyzer']
methods = bayesian_analyzer['methods']

# Filtrar métodos por nivel epistemológico
n3_methods = {
    class_name: {
        method_name: method
        for method_name, method in cls['methods'].items()
        if method['epistemological_classification']['level'] == 'N3-AUD'
    }
    for class_name, cls in catalog.items()
    if class_name not in ['quality_metrics', '_pipeline_metadata']
}

# Obtener métodos compatibles con TYPE_B (Bayesiano)
type_b_methods = []
for class_name, cls in catalog.items():
    if class_name in ['quality_metrics', '_pipeline_metadata']:
        continue
    for method_name, method in cls['methods'].items():
        ec = method['epistemological_classification']
        if ec.get('contract_compatibility', {}).get('TYPE_B', False):
            type_b_methods.append({
                'class': class_name,
                'method': method_name,
                'level': ec['level']
            })

# Verificar veto conditions para N3
for class_name, cls in catalog.items():
    if class_name in ['quality_metrics', '_pipeline_metadata']:
        continue
    for method_name, method in cls['methods'].items():
        ec = method['epistemological_classification']
        if ec['level'] == 'N3-AUD':
            veto = ec.get('veto_conditions')
            if not veto:
                print(f"WARNING: {class_name}.{method_name} missing veto!")
```

---

## Interpretación de Niveles

### N1-EMP: Extracción Empírica
- **Función**: Extrae hechos observables sin interpretación
- **Output**: `FACT` (datos brutos)
- **Fusión**: `additive` (⊕) - se suma al grafo
- **Fase**: `phase_A_construction`
- **Requiere**: Nada (lee directamente de fuente)
- **Produce**: `raw_facts`

### N2-INF: Inferencia Bayesiana
- **Función**: Transforma datos en conocimiento probabilístico
- **Output**: `PARAMETER` (cantidades derivadas)
- **Fusión**: `multiplicative` (⊗) - modifica pesos
- **Fase**: `phase_B_computation`
- **Requiere**: `raw_facts`
- **Produce**: `inferred_parameters`
- **Modifica**: `edge_weights`, `confidence_scores`

### N3-AUD: Auditoría Falsacionista
- **Función**: Intenta refutar, valida críticamente
- **Output**: `CONSTRAINT` (restricciones)
- **Fusión**: `gate` (⊘) - **puede vetar N1/N2**
- **Fase**: `phase_C_litigation`
- **Requiere**: `raw_facts` + `inferred_parameters`
- **Produce**: `validated_constraints`
- **Modula**: `raw_facts.confidence`, `inferences.confidence`
- **OBLIGATORIO**: `veto_conditions` ≠ null

### N4-SYN: Síntesis Narrativa
- **Función**: Meta-análisis, genera reporte final
- **Output**: `NARRATIVE` (texto estructurado)
- **Fusión**: `terminal` (⊙) - consume grafo completo
- **Fase**: `phase_D_synthesis`
- **Requiere**: `raw_facts` + `inferred_parameters` + `validated_constraints`
- **Produce**: `narrative`

---

## Tipos de Contrato

### TYPE_A: Semántico
- Foco: Coherencia narrativa, NLP, embeddings
- Contratos: Q001, Q013
- Clases: `SemanticProcessor`, `TextMiningEngine`

### TYPE_B: Bayesiano
- Foco: Significancia estadística, priors/posteriors
- Contratos: Q002, Q005, Q007, Q011, Q017, Q018, Q020, Q023, Q024, Q025, Q027, Q029
- Clases: `BayesianNumericalAnalyzer`, `AdaptivePriorCalculator`

### TYPE_C: Causal
- Foco: Topología de grafos, DAGs, mecanismos
- Contratos: Q008, Q016, Q026, Q030
- Clases: `CausalExtractor`, `TeoriaCambio`, `AdvancedDAGValidator`

### TYPE_D: Financiero
- Foco: Suficiencia presupuestal, allocations
- Contratos: Q003, Q004, Q006, Q009, Q012, Q015, Q021, Q022
- Clases: `FinancialAuditor`, `PDETMunicipalPlanAnalyzer`

### TYPE_E: Lógico
- Foco: Detección de contradicciones, consistencia
- Contratos: Q010, Q014, Q019, Q028
- Clases: `PolicyContradictionDetector`, `IndustrialGradeValidator`

---

## Casos de Uso

### 1. Construir Pipeline Epistemológico

```python
# Obtener métodos en orden de ejecución
phases = {
    'phase_A': [],  # N1-EMP
    'phase_B': [],  # N2-INF
    'phase_C': [],  # N3-AUD
    'phase_D': []   # N4-SYN
}

for class_name, cls in catalog.items():
    if class_name in ['quality_metrics', '_pipeline_metadata']:
        continue
    for method_name, method in cls['methods'].items():
        ec = method['epistemological_classification']
        phase = ec.get('phase_assignment')
        if phase and phase.startswith('phase_'):
            phase_key = f'phase_{phase[6]}'  # Extract A/B/C/D
            phases[phase_key].append({
                'class': class_name,
                'method': method_name,
                'level': ec['level']
            })

# Ejecutar pipeline
# 1. Phase A: Extracción (N1)
for item in phases['phase_A']:
    pass  # execute extraction

# 2. Phase B: Inferencia (N2)
for item in phases['phase_B']:
    pass  # execute inference

# 3. Phase C: Auditoría (N3) - puede vetar resultados de A y B
for item in phases['phase_C']:
    pass  # execute validation with veto capability

# 4. Phase D: Síntesis (N4)
for item in phases['phase_D']:
    pass  # generate final report
```

### 2. Validar Coherencia Epistemológica

```python
# Verificar que N3 puede acceder a N1 y N2
for class_name, cls in catalog.items():
    if class_name in ['quality_metrics', '_pipeline_metadata']:
        continue
    for method_name, method in cls['methods'].items():
        ec = method['epistemological_classification']
        
        if ec['level'] == 'N3-AUD':
            requires = set(ec['dependencies']['requires'])
            
            # N3 DEBE requerir raw_facts O inferred_parameters
            if not ({'raw_facts', 'inferred_parameters'} & requires):
                print(f"ERROR: {class_name}.{method_name} is N3 but doesn't require N1/N2 inputs!")
```

### 3. Generar Contrato Ejecutor

```python
# Seleccionar métodos compatibles con TYPE_B (Bayesiano)
contract_type = 'TYPE_B'
compatible_methods = []

for class_name, cls in catalog.items():
    if class_name in ['quality_metrics', '_pipeline_metadata']:
        continue
    for method_name, method in cls['methods'].items():
        ec = method['epistemological_classification']
        
        if ec.get('contract_compatibility', {}).get(contract_type, False):
            compatible_methods.append({
                'class_name': class_name,
                'method_name': method_name,
                'level': ec['level'],
                'output_type': ec['output_type'],
                'fusion_behavior': ec['fusion_behavior'],
                'requires': ec['dependencies']['requires'],
                'produces': ec['dependencies']['produces']
            })

# Agrupar por fase
contract = {
    'contract_type': contract_type,
    'method_binding': {
        'phase_A_construction': [m for m in compatible_methods if m['level'] == 'N1-EMP'],
        'phase_B_computation': [m for m in compatible_methods if m['level'] == 'N2-INF'],
        'phase_C_litigation': [m for m in compatible_methods if m['level'] == 'N3-AUD']
    }
}
```

---

## Certificación y Garantías

✅ **100% cobertura estructural**: Todos los métodos tienen clasificación epistemológica  
✅ **96% precisión taxonómica**: 557/580 métodos correctamente clasificados  
✅ **0 orphan methods**: Todos los métodos tienen ≥1 compatibilidad de contrato  
✅ **0 N3 without veto**: Todos los métodos N3-AUD tienen veto_conditions  
✅ **Trazabilidad forense completa**: Hashes, git commits, session IDs  

**Apto para**:
- Uso en producción ✅
- Publicación académica ✅
- Auditoría externa ✅
- Integración CI/CD ✅

---

## Documentación Adicional

- **Certificación oficial**: `EPISTEMOLOGICAL_CERTIFICATION.md`
- **Reporte de auditoría**: `EPISTEMOLOGICAL_RIGOR_AUDIT_REPORT.md`
- **Taxonomía canónica**: `episte_refact.md`
- **Especificación BLOQUE 0-8**: Instrucciones originales en commit history

---

**Última actualización**: 2025-12-30  
**Versión del catálogo**: v5.0.0 CERTIFICADO  
**Rulebook hash**: `e5366305cdeb023ff8267ad96f205d73d82e5ca0b87daaef4981e670df5b6ddb`
