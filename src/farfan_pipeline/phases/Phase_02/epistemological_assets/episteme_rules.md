## GUÍA DE OPERACIONALIZACIÓN EPISTEMOLÓGICA PARA LA ELABORACIÓN DE 300 CONTRATOS  EJECUTORES 


Entiendase ejecutor como una unidad de orquestación de métodos: 

Un Executor es un functor que preserva la estructura de dependencias entre métodos y las mapea a la categoría de outputs.  

Es una tupla ordenada con estructura de lattice**:  

```
Executor ≜ ⟨ M, (L, ≤), π, ρ, ⊗ ⟩

donde:
  M = {m₁, .. ., mₙ}           -- conjunto de métodos
  L = {N1, N2, N3, N4}        -- lattice de niveles epistemológicos  
  ≤ = N1 ≤ N2 ≤ N3 ≤ N4       -- orden de dependencia
  π : M → L                   -- asignación de nivel a método
  ρ : M → {FACT, PARAMETER, CONSTRAINT, NARRATIVE}  -- tipo de output
  ⊗ : Output × Output → Output -- operador de fusión (no conmutativo para N3)
```

**La no-conmutatividad de ⊗ para N3 captura la asimetría popperiana**:  

```
∀o₁ ∈ Output(N1 ∪ N2), ∀o₃ ∈ Output(N3):
  o₁ ⊗ o₃ ≠ o₃ ⊗ o₁
  
  específicamente:
  o₃ ⊗ o₁ puede = ∅  (N3 anula N1)
  o₁ ⊗ o₃ = o₃       (N1 no puede anular N3)
```

---

### Documento de Referencia Canónico

| Campo | Valor |
|-------|-------|
| Versión | 1.0.0 |
| Fecha | 2025-12-22 |
| Fuentes | episte_refact. md, taxonomías epistemológicas, feedback crítico |
| Aplica a | 30 contratos base (D1-Q1 a D6-Q5) |

---

## PARTE I: CLASIFICACIÓN PREVIA OBLIGATORIA

Antes de diligenciar cualquier sección, DEBE determinarse: 

### 1.1 Tipo de Contrato (Cluster Funcional)

| Tipo | Código | Contratos | Foco | Estrategia de Fusión Principal |
|------|--------|-----------|------|-------------------------------|
| Semántico | TYPE_A | Q001, Q013 | Coherencia narrativa, NLP | `semantic_triangulation` |
| Bayesiano | TYPE_B | Q002, Q005, Q007, Q011, Q017, Q018, Q020, Q023, Q024, Q025, Q027, Q029 | Significancia estadística, priors | `bayesian_update` |
| Causal | TYPE_C | Q008, Q016, Q026, Q030 | Topología de grafos, DAGs | `topological_overlay` |
| Financiero | TYPE_D | Q003, Q004, Q006, Q009, Q012, Q015, Q021, Q022 | Suficiencia presupuestal | `financial_coherence_audit` |
| Lógico | TYPE_E | Q010, Q014, Q019, Q028 | Detección de contradicciones | `logical_consistency_validation` |

### 1.2 Nivel Epistemológico de Cada Método

| Nivel | Código | Función Cognitiva | Epistemología | Tipo de Output |
|-------|--------|-------------------|---------------|----------------|
| 0 | N0-INFRA | Soporte técnico sin juicio | Instrumentalismo | `INFRASTRUCTURE` |
| 1 | N1-EMP | Extraer hechos brutos | Empirismo positivista | `FACT` |
| 2 | N2-INF | Transformar datos en conocimiento probabilístico | Bayesianismo subjetivista | `PARAMETER` |
| 3 | N3-AUD | Cuestionar, validar o refutar | Falsacionismo popperiano | `CONSTRAINT` |
| 4 | N4-META | Analizar el propio proceso analítico | Reflexividad crítica | `META_ANALYSIS` |

### 1.3 Tipo de Output por Método

| Tipo Output | Nivel Origen | Comportamiento en Fusión | Símbolo |
|-------------|--------------|--------------------------|---------|
| `FACT` | N1 | Se SUMA al grafo como nodo | ⊕ |
| `PARAMETER` | N2 | MODIFICA pesos de aristas | ⊗ |
| `CONSTRAINT` | N3 | FILTRA/BLOQUEA ramas si falla | ⊘ |
| `NARRATIVE` | N4 | CONSUME grafo para texto final | ⊙ |

---

## PARTE II: METHOD_BINDING

### 2.1 Estructura Requerida

```json
"method_binding": {
  "orchestration_mode": "epistemological_pipeline",
  "contract_type": "<TYPE_A|TYPE_B|TYPE_C|TYPE_D|TYPE_E>",
  "method_count": <N>,
  "execution_phases": {
    "phase_A_construction": { /* N1 methods */ },
    "phase_B_computation": { /* N2 methods */ },
    "phase_C_litigation": { /* N3 methods */ }
  }
}
```

### 2.2 Reglas de Diligenciamiento por Fase

#### PHASE_A:  Construction (Nivel 1 - Empírico)

**Propósito**:  Ejecutar todos los métodos que extraen hechos brutos. 

**Criterios de inclusión**:
- Método lee directamente `PreprocesadoMetadata` o documento raw
- Output son literales:  strings, números, listas de entidades observadas
- NO realiza transformación interpretativa
- Patrones de nombre: `extract_*`, `parse_*`, `mine_*`, `chunk_*`

**Campos requeridos por método**: 

```json
{
  "class_name": "string",
  "method_name": "string",
  "mother_file": "string",
  "provides":  "string (formato:  classname_lower. method_name_sin_underscore)",
  "level": "N1-EMP",
  "output_type": "FACT",
  "fusion_behavior": "additive",
  "description": "string",
  "requires": []
}
```

**Clases típicas de N1**:
- TextMiningEngine:  `diagnose_critical_links`, `_analyze_link_text`
- IndustrialPolicyProcessor: `_extract_point_evidence`, `_extract_metadata`
- CausalExtractor: `_extract_goals`, `_parse_goal_context`
- PDETMunicipalPlanAnalyzer: `_extract_financial_amounts`, `_extract_from_budget_table`, `_extract_entities_syntax`
- SemanticProcessor: `chunk_text`
- PolicyContradictionDetector: `_extract_quantitative_claims`, `_parse_number`

---

#### PHASE_B: Computation (Nivel 2 - Inferencial)

**Propósito**:  Transformar hechos N1 en conocimiento probabilístico.

**Criterios de inclusión**:
- Consume outputs de N1
- Produce cantidades derivadas:  scores, probabilidades, relaciones inferidas
- Realiza análisis estadístico, scoring, generación de embeddings
- Patrones de nombre: `analyze_*`, `score_*`, `calculate_*`, `infer_*`, `evaluate_*`, `compare_*`

**Campos requeridos por método**: 

```json
{
  "class_name": "string",
  "method_name": "string",
  "mother_file": "string",
  "provides":  "string",
  "level":  "N2-INF",
  "output_type": "PARAMETER",
  "fusion_behavior":  "multiplicative",
  "description": "string",
  "requires": ["raw_facts"],
  "modifies": ["edge_weights", "confidence_scores"]
}
```

**Clases típicas de N2**: 
- BayesianNumericalAnalyzer:  `evaluate_policy_metric`, `compare_policies`
- AdaptivePriorCalculator: `calculate_likelihood_adaptativo`, `_adjust_domain_weights`, `sensitivity_analysis`
- HierarchicalGenerativeModel: `verify_conditional_independence`, `_calculate_r_hat`, `_calculate_ess`
- BayesianMechanismInference: `_test_sufficiency`, `_test_necessity`, `_calculate_coherence_factor`
- TeoriaCambio: `_encontrar_caminos_completos`, `validacion_completa`
- SemanticProcessor: `embed_single`
- IndustrialPolicyProcessor: `process`, `_match_patterns_in_sentences`, `_analyze_causal_dimensions`

---

#### PHASE_C:  Litigation (Nivel 3 - Auditoría)

**Propósito**:  Intentar "romper" los resultados de Phase_B.  Actúan como **VETO GATES**. 

**Criterios de inclusión**: 
- Consume outputs de N1 Y N2
- Produce flags de validación, reportes de contradicción, moduladores de confianza
- Puede INVALIDAR o SUPRIMIR hallazgos de capas anteriores
- Patrones de nombre: `validate_*`, `detect_*`, `audit_*`, `check_*`, `test_*`, `verify_*`

**PROPIEDAD CRÍTICA**:  Influencia ASIMÉTRICA — puede invalidar N1/N2, pero N1/N2 NO pueden invalidar N3.

**Campos requeridos por método**:

```json
{
  "class_name": "string",
  "method_name": "string",
  "mother_file": "string",
  "provides": "string",
  "level":  "N3-AUD",
  "output_type": "CONSTRAINT",
  "fusion_behavior":  "gate",
  "description":  "string",
  "requires": ["raw_facts", "inferences"],
  "modulates": ["raw_facts. confidence", "inferences. confidence"],
  "veto_conditions": {
    "<condition_name>": {
      "trigger": "<condition>",
      "action": "block_branch | reduce_confidence | flag_caution",
      "scope": "affected_subgraph | source_facts | contradicting_nodes",
      "confidence_multiplier": <0.0 | 0.5 | 0.7>
    }
  }
}
```

**Clases típicas de N3**:
- PolicyContradictionDetector: `_detect_logical_incompatibilities`, `_calculate_coherence_metrics`, `_statistical_significance_test`
- FinancialAuditor: `_detect_allocation_gaps`, `_calculate_sufficiency`
- IndustrialGradeValidator: `execute_suite`, `validate_connection_matrix`, `validate_engine_readiness`
- AdvancedDAGValidator: `_is_acyclic`, `calculate_acyclicity_pvalue`, `_calculate_statistical_power`
- BayesianCounterfactualAuditor: `construct_scm`, `counterfactual_query`
- OperationalizationAuditor:  `audit_sequence_logic`, `_audit_systemic_risk`
- TemporalLogicVerifier: `verify_temporal_consistency`

---

### 2.3 Árbol de Decisión para Clasificación

```
Método M: 
│
├─ ¿M lee PreprocesadoMetadata directamente?
│  ├─ SÍ → ¿M transforma/interpreta?
│  │  ├─ NO → N1-EMP (FACT)
│  │  └─ SÍ → ¿Output es literal o derivado?
│  │     ├─ Literal → N1-EMP (FACT)
│  │     └─ Derivado → N2-INF (PARAMETER)
│  │
│  └─ NO → ¿Qué consume M?
│     ├─ Solo N1 → ¿M valida o infiere?
│     │  ├─ Valida → N3-AUD (CONSTRAINT)
│     │  └─ Infiere → N2-INF (PARAMETER)
│     │
│     ├─ N1 + N2 → ¿M valida o sintetiza?
│     │  ├─ Valida → N3-AUD (CONSTRAINT)
│     │  └─ Sintetiza → N4-SYN (NARRATIVE)
│     │
│     └─ N1 + N2 + N3 → N4-SYN (NARRATIVE)
```

---

## PARTE III:  EVIDENCE_ASSEMBLY

### 3.1 Estructura Requerida

```json
"evidence_assembly": {
  "engine":  "EVIDENCE_NEXUS",
  "module": "farfan_pipeline. phases.Phase_two. evidence_nexus",
  "class_name": "EvidenceNexus",
  "method_name": "assemble",
  "type_system": { /* Tipología de outputs */ },
  "assembly_rules": [ /* 4 reglas obligatorias */ ]
}
```

### 3.2 Sistema de Tipos (type_system)

```json
"type_system": {
  "FACT": {
    "origin_level": "N1",
    "fusion_operation": "graph_node_addition",
    "merge_behavior": "additive",
    "symbol":  "⊕",
    "description":  "Se SUMA al grafo como nodo"
  },
  "PARAMETER": {
    "origin_level": "N2",
    "fusion_operation": "edge_weight_modification",
    "merge_behavior": "multiplicative",
    "symbol": "⊗",
    "description": "MODIFICA pesos de aristas del grafo"
  },
  "CONSTRAINT": {
    "origin_level": "N3",
    "fusion_operation":  "branch_filtering",
    "merge_behavior": "gate",
    "symbol": "⊘",
    "description": "FILTRA/BLOQUEA ramas si validación falla"
  },
  "NARRATIVE": {
    "origin_level": "N4",
    "fusion_operation":  "synthesis",
    "merge_behavior": "terminal",
    "symbol": "⊙",
    "description": "CONSUME grafo para texto final"
  }
}
```

### 3.3 Reglas de Ensamblaje (assembly_rules)

#### PLANTILLA POR TIPO DE CONTRATO

##### TYPE_A: Semántico

```json
"assembly_rules": [
  {
    "rule_id": "R1_empirical_extraction",
    "rule_type": "empirical_basis",
    "target":  "raw_facts",
    "sources": ["<todos los provides de N1>"],
    "merge_strategy": "concat_with_deduplication",
    "deduplication_key": "element_id",
    "output_type": "FACT",
    "confidence_propagation": "preserve_individual"
  },
  {
    "rule_id": "R2_semantic_triangulation",
    "rule_type": "corroboration",
    "target": "triangulated_facts",
    "sources": ["<todos los provides de N2>"],
    "input_dependencies": ["raw_facts"],
    "merge_strategy": "semantic_triangulation",
    "operation": "if TextMining AND IndustrialPolicy extract same datum → merge nodes, increase confidence",
    "output_type": "PARAMETER",
    "confidence_propagation":  "corroborative_boost"
  },
  {
    "rule_id": "R3_audit_gate",
    "rule_type": "robustness_gate",
    "target": "validated_facts",
    "sources": ["<todos los provides de N3>"],
    "input_dependencies":  ["raw_facts", "triangulated_facts"],
    "merge_strategy": "veto_gate",
    "output_type": "CONSTRAINT",
    "gate_logic": {
      "contradiction_detected": {"action": "suppress_fact", "multiplier": 0.0},
      "low_coherence":  {"action": "reduce_confidence", "multiplier": 0.5}
    }
  },
  {
    "rule_id": "R4_narrative_synthesis",
    "rule_type": "synthesis",
    "target":  "human_answer",
    "sources": [],
    "input_dependencies": ["validated_facts", "triangulated_facts", "audit_results"],
    "merge_strategy":  "carver_doctoral_synthesis",
    "output_type":  "NARRATIVE",
    "external_handler": "DoctoralCarverSynthesizer"
  }
]
```

##### TYPE_B:  Bayesiano

```json
"assembly_rules": [
  {
    "rule_id": "R1_empirical_basis",
    "rule_type": "empirical_basis",
    "target": "prior_distribution",
    "sources": ["pdetmunicipalplananalyzer.*", "<N1 methods>"],
    "merge_strategy": "concat",
    "output_type": "FACT"
  },
  {
    "rule_id": "R2_probabilistic_update",
    "rule_type": "probabilistic_update",
    "target": "posterior_belief",
    "sources": ["adaptivepriorcalculator.*", "hierarchicalgenerativemodel.*", "bayesiannumericalanalyzer.*"],
    "input_dependencies": ["prior_distribution"],
    "merge_strategy": "bayesian_update",
    "operation": "posterior = update_belief(prior, likelihood_from_evidence)",
    "output_type": "PARAMETER"
  },
  {
    "rule_id":  "R3_robustness_gate",
    "rule_type": "robustness_gate",
    "target": "validated_posterior",
    "sources": ["advanceddagvalidator. calculate_statistical_power", "<N3 methods>"],
    "input_dependencies": ["posterior_belief"],
    "merge_strategy":  "veto_gate",
    "gate_logic": {
      "statistical_power_below_threshold": {
        "condition": "result < 0.8",
        "action": "downgrade_confidence_to_zero"
      }
    },
    "output_type": "CONSTRAINT"
  },
  {
    "rule_id": "R4_synthesis",
    "rule_type": "synthesis",
    "target":  "human_answer",
    "input_dependencies": ["validated_posterior"],
    "merge_strategy": "carver_doctoral_synthesis",
    "output_type": "NARRATIVE"
  }
]
```

##### TYPE_C: Causal

```json
"assembly_rules":  [
  {
    "rule_id": "R1_structure_definition",
    "rule_type": "structure_definition",
    "target": "causal_graph",
    "sources": ["teoriacambio. encontrar_caminos", "causalextractor.*"],
    "merge_strategy": "graph_construction",
    "output_type":  "FACT"
  },
  {
    "rule_id": "R2_edge_inference",
    "rule_type": "edge_inference",
    "target": "weighted_causal_graph",
    "sources": ["bayesianmechanisminference.*", "<N2 methods>"],
    "input_dependencies": ["causal_graph"],
    "merge_strategy": "topological_overlay",
    "operation": "if TeoriaCambio path AND CausalExtractor path → check for cycles",
    "output_type": "PARAMETER"
  },
  {
    "rule_id":  "R3_validity_check",
    "rule_type":  "validity_check",
    "target":  "validated_graph",
    "sources": ["advanceddagvalidator.is_acyclic", "bayesiancounterfactualauditor.*"],
    "input_dependencies":  ["weighted_causal_graph"],
    "merge_strategy": "veto_gate",
    "gate_logic": {
      "cycle_detected": {"action": "invalidate_graph", "multiplier": 0.0},
      "scm_construction_failed": {"action":  "block_branch", "scope": "affected_subgraph"}
    },
    "output_type":  "CONSTRAINT"
  },
  {
    "rule_id": "R4_synthesis",
    "rule_type": "synthesis",
    "target": "human_answer",
    "input_dependencies": ["validated_graph"],
    "merge_strategy":  "carver_doctoral_synthesis",
    "output_type":  "NARRATIVE"
  }
]
```

##### TYPE_D: Financiero

```json
"assembly_rules":  [
  {
    "rule_id": "R1_financial_extraction",
    "rule_type": "empirical_basis",
    "target": "financial_facts",
    "sources": ["pdetmunicipalplananalyzer._extract_financial_amounts", "financialauditor._parse_amount", "<N1 methods>"],
    "merge_strategy": "concat",
    "output_type": "FACT"
  },
  {
    "rule_id": "R2_sufficiency_analysis",
    "rule_type": "computation",
    "target":  "sufficiency_scores",
    "sources": ["financialauditor._calculate_sufficiency", "<N2 methods>"],
    "input_dependencies": ["financial_facts"],
    "merge_strategy":  "weighted_mean",
    "output_type": "PARAMETER"
  },
  {
    "rule_id":  "R3_coherence_audit",
    "rule_type": "financial_coherence_audit",
    "target": "validated_financials",
    "sources": ["financialauditor._detect_allocation_gaps", "<N3 methods>"],
    "input_dependencies": ["financial_facts", "sufficiency_scores"],
    "merge_strategy": "veto_gate",
    "gate_logic": {
      "budget_gap_detected": {"action": "flag_insufficiency", "multiplier": 0.3},
      "allocation_mismatch": {"action": "reduce_confidence", "multiplier":  0.5}
    },
    "output_type":  "CONSTRAINT"
  },
  {
    "rule_id": "R4_synthesis",
    "rule_type":  "synthesis",
    "target": "human_answer",
    "input_dependencies":  ["validated_financials"],
    "merge_strategy": "carver_doctoral_synthesis",
    "output_type": "NARRATIVE"
  }
]
```

##### TYPE_E:  Lógico

```json
"assembly_rules": [
  {
    "rule_id": "R1_statement_extraction",
    "rule_type": "empirical_basis",
    "target": "policy_statements",
    "sources": ["<N1 methods>"],
    "merge_strategy": "concat",
    "output_type": "FACT"
  },
  {
    "rule_id": "R2_coherence_computation",
    "rule_type": "computation",
    "target": "coherence_metrics",
    "sources": ["policycontradictiondetector._calculate_coherence_metrics", "<N2 methods>"],
    "input_dependencies":  ["policy_statements"],
    "merge_strategy": "weighted_mean",
    "output_type": "PARAMETER"
  },
  {
    "rule_id": "R3_contradiction_detection",
    "rule_type":  "logical_consistency_validation",
    "target": "validated_statements",
    "sources": ["policycontradictiondetector._detect_logical_incompatibilities", "operationalizationauditor. audit_sequence_logic", "<N3 methods>"],
    "input_dependencies": ["policy_statements", "coherence_metrics"],
    "merge_strategy": "veto_gate",
    "gate_logic": {
      "logical_contradiction":  {"action": "suppress_contradicting_nodes", "multiplier":  0.0},
      "sequence_violation": {"action": "flag_invalid_sequence", "multiplier": 0.2}
    },
    "output_type": "CONSTRAINT"
  },
  {
    "rule_id": "R4_synthesis",
    "rule_type": "synthesis",
    "target": "human_answer",
    "input_dependencies": ["validated_statements"],
    "merge_strategy": "carver_doctoral_synthesis",
    "output_type": "NARRATIVE"
  }
]
```

---

## PARTE IV:  FUSION_SPECIFICATION

### 4.1 Estructura Requerida

```json
"fusion_specification": {
  "contract_type": "<TYPE_A|TYPE_B|TYPE_C|TYPE_D|TYPE_E>",
  "primary_strategy": "<strategy_name>",
  "level_strategies": { /* Estrategia por nivel */ },
  "cross_layer_effects": { /* Efectos entre capas */ },
  "fusion_pipeline": { /* Secuencia de fusión */ }
}
```

### 4.2 Estrategias por Nivel

```json
"level_strategies": {
  "N1_fact_fusion": {
    "strategy":  "<concat | semantic_corroboration | graph_construction>",
    "behavior": "additive",
    "conflict_resolution": "corroborative_stacking",
    "formula": "if same_fact detected by multiple methods → confidence = 1 - ∏(1 - conf_i)"
  },
  "N2_parameter_fusion":  {
    "strategy": "<weighted_mean | bayesian_update | topological_overlay | dempster_shafer>",
    "behavior": "multiplicative",
    "conflict_resolution": "weighted_voting",
    "affects":  ["N1_facts. confidence", "N1_facts.edge_weights"]
  },
  "N3_constraint_fusion": {
    "strategy": "veto_gate",
    "behavior":  "gate",
    "asymmetry_principle": "audit_dominates",
    "propagation": {
      "upstream":  "confidence_backpropagation",
      "downstream":  "branch_blocking"
    }
  }
}
```

### 4.3 Estrategias según Tipo de Contrato

| Tipo | N1 Strategy | N2 Strategy | N3 Strategy |
|------|-------------|-------------|-------------|
| TYPE_A (Semántico) | `semantic_corroboration` | `dempster_shafer` | `veto_gate` |
| TYPE_B (Bayesiano) | `concat` | `bayesian_update` | `veto_gate` |
| TYPE_C (Causal) | `graph_construction` | `topological_overlay` | `veto_gate` |
| TYPE_D (Financiero) | `concat` | `weighted_mean` | `financial_coherence_audit` + `veto_gate` |
| TYPE_E (Lógico) | `concat` | `weighted_mean` | `logical_consistency_validation` + `veto_gate` |

### 4.4 Tabla de Estrategias de Fusión

| Estrategia | Nivel | Función | Uso |
|------------|-------|---------|-----|
| `concat` | N1 | Concatenar evidencia de múltiples fuentes | 74. 8% |
| `weighted_mean` | N2 | Promediar confianza con pesos | 24.9% |
| `semantic_corroboration` | N1 | Fusionar nodos si dicen lo mismo → mayor peso | TYPE_A |
| `bayesian_update` | N2 | Prior + Likelihood → Posterior | TYPE_B |
| `topological_overlay` | N1+N3 | Fusionar grafos detectando ciclos | TYPE_C |
| `financial_coherence_audit` | N3 | Validar coherencia presupuestal | TYPE_D |
| `logical_consistency_validation` | N3 | Validar consistencia lógica | TYPE_E |
| `veto_gate` | N3 | Si auditoría falla → bloquear rama | TODOS |
| `confidence_modulation` | N3 | Penalizar score si auditoría débil (×0.5) | TODOS |
| `graph_construction` | N1 | Construir grafo de evidencia | TYPE_C |
| `edge_inference` | N2 | Inferir relaciones entre nodos | TYPE_C |
| `dempster_shafer` | N2 | Propagación de creencia combinatoria | TYPE_A |
| `carver_doctoral_synthesis` | N4 | Síntesis narrativa PhD-style | TODOS |

---

## PARTE V:  CROSS_LAYER_FUSION

### 5.1 Estructura Requerida

```json
"cross_layer_fusion":  {
  "N1_to_N2":  {
    "relationship": "N2 reads N1 facts",
    "effect": "N2 computes parameters FROM N1 observations",
    "data_flow": "forward_propagation"
  },
  "N2_to_N1": {
    "relationship": "N2 modifies N1 confidence",
    "effect": "Edge weights adjust fact confidence scores",
    "data_flow": "confidence_backpropagation"
  },
  "N3_to_N1": {
    "relationship": "N3 can BLOCK N1 facts",
    "effect": "Failed constraints remove facts from graph",
    "data_flow": "veto_propagation",
    "asymmetry": "N1 CANNOT invalidate N3"
  },
  "N3_to_N2": {
    "relationship": "N3 can INVALIDATE N2 parameters",
    "effect": "Failed constraints nullify parameter modifications",
    "data_flow": "inference_modulation",
    "asymmetry": "N2 CANNOT invalidate N3"
  },
  "all_to_N4": {
    "relationship": "N4 consumes validated outputs from all layers",
    "effect": "Synthesis constructs narrative from filtered graph",
    "data_flow": "terminal_aggregation"
  }
}
```

### 5.2 Reglas de Propagación de Bloqueo (N3)

```json
"blocking_propagation_rules": {
  "matrix_not_positive_definite": {
    "triggered_by": "IndustrialGradeValidator",
    "action": "block_branch",
    "scope": "affected_subgraph",
    "propagation":  "upstream_and_downstream"
  },
  "statistical_significance_failed": {
    "triggered_by": "PolicyContradictionDetector._statistical_significance_test",
    "action":  "block_branch",
    "scope": "source_facts",
    "propagation": "downstream_only"
  },
  "logical_contradiction":  {
    "triggered_by": "PolicyContradictionDetector._detect_logical_incompatibilities",
    "action": "block_branch",
    "scope": "contradicting_nodes",
    "propagation":  "both"
  },
  "cycle_detected": {
    "triggered_by": "AdvancedDAGValidator._is_acyclic",
    "action":  "invalidate_graph",
    "scope": "entire_causal_graph",
    "propagation":  "total"
  },
  "budget_insufficiency": {
    "triggered_by":  "FinancialAuditor._detect_allocation_gaps",
    "action":  "flag_and_reduce",
    "scope":  "affected_goals",
    "propagation": "downstream_only",
    "confidence_multiplier": 0.3
  }
}
```

---

## PARTE VI: HUMAN_ANSWER_STRUCTURE

### 6.1 Estructura Requerida

```json
"human_answer_structure": {
  "format": "markdown",
  "template_mode": "epistemological_narrative",
  "contract_type": "<TYPE_A|TYPE_B|TYPE_C|TYPE_D|TYPE_E>",
  "sections": [
    { /* S1: Veredicto */ },
    { /* S2: Evidencia Dura (N1) */ },
    { /* S3: Análisis de Robustez (N3) */ },
    { /* S4: Puntos Ciegos */ }
  ],
  "argumentative_roles": { /* Roles por nivel */ },
  "confidence_interpretation": { /* Interpretación de scores */ }
}
```

### 6.2 Secciones Obligatorias

#### S1: VEREDICTO (Synthesis)

```json
{
  "section_id": "S1_verdict",
  "title": "### Veredicto",
  "layer": "N4",
  "data_source": "synthesis_output",
  "narrative_style": "declarative",
  "template": "**Conclusión**:  {verdict_statement}\n\n**Confianza Global**: {final_confidence_pct}% ({confidence_interpretation})\n\n**Base Metodológica**: {method_count} métodos ejecutados, {audit_count} validaciones, {blocked_count} ramas bloqueadas.",
  "argumentative_role": "SYNTHESIS"
}
```

#### S2: EVIDENCIA DURA (Empirical - N1)

```json
{
  "section_id":  "S2_empirical_base",
  "title": "### Base Empírica:  Hechos Observados",
  "layer": "N1",
  "data_source": "validated_facts",
  "narrative_style":  "descriptive",
  "template": "**Elementos Detectados**: {fact_count} hechos extraídos de {document_coverage_pct}% del texto.\n\n**Fuentes Oficiales**: {official_sources_list}\n\n**Indicadores Cuantitativos**: {quantitative_indicators}\n\n**Cobertura Temporal**:  {temporal_series}",
  "argumentative_role": "EMPIRICAL_BASIS",
  "epistemological_note": "Observaciones directas sin transformación interpretativa."
}
```

#### S3: ANÁLISIS DE ROBUSTEZ (Audit - N3)

```json
{
  "section_id": "S3_robustness_audit",
  "title":  "### Análisis de Robustez:  Validación y Limitaciones",
  "layer": "N3",
  "data_source": "audit_results",
  "narrative_style":  "critical",
  "template": "**Validaciones Ejecutadas**: {validation_count}\n\n**Contradicciones Detectadas**: {contradiction_count}\n{contradiction_details}\n\n**Ramas Bloqueadas**: {blocked_branches_count}\n{blocking_reasons}\n\n**Modulaciones de Confianza**: {confidence_adjustments}\n\n**Limitaciones Metodológicas**: {limitations_list}",
  "argumentative_role": "ROBUSTNESS_QUALIFIER",
  "epistemological_note":  "Meta-juicios sobre confiabilidad.  N3 puede VETAR hallazgos de N1/N2.",
  "veto_display": {
    "if_veto_triggered": "⚠️ ALERTA:  {veto_reason}.  El modelo lógico es INVÁLIDO técnicamente.",
    "if_no_veto":  "✓ Todas las validaciones pasaron."
  }
}
```

#### S4: PUNTOS CIEGOS (Gaps)

```json
{
  "section_id": "S4_gaps",
  "title": "### Puntos Ciegos:  Evidencia Faltante",
  "layer": "N4-META",
  "data_source": "gap_analysis",
  "narrative_style":  "diagnostic",
  "template": "**Métodos sin Resultados**: {empty_methods_count} de {total_methods}\n{empty_methods_list}\n\n**Elementos Esperados no Encontrados**: {missing_elements}\n\n**Cobertura de Patterns**: {pattern_coverage_pct}%\n\n**Impacto en Confianza**:  {gap_impact_assessment}",
  "argumentative_role": "META_TRACEABILITY"
}
```

### 6.3 Roles Argumentativos por Nivel

```json
"argumentative_roles":  {
  "N1_roles": [
    {
      "role":  "EMPIRICAL_BASIS",
      "description": "Hecho observable innegable",
      "example": "Se encontraron 15 menciones a VBG",
      "narrative_weight": "high"
    }
  ],
  "N2_roles": [
    {
      "role":  "INFERENTIAL_BRIDGE",
      "description": "Conexión lógica derivada",
      "example": "Con 95% confianza, el prior se actualiza",
      "narrative_weight": "medium"
    },
    {
      "role": "CONTEXTUAL_QUALIFIER",
      "description": "Condiciona validez a contexto",
      "example": "Válido solo en zona rural",
      "narrative_weight": "medium"
    }
  ],
  "N3_roles":  [
    {
      "role": "ROBUSTNESS_QUALIFIER",
      "description": "Advertencia de calidad/limitación",
      "example": "La muestra es pequeña (n=5)",
      "narrative_weight": "high"
    },
    {
      "role": "REFUTATIONAL_SIGNAL",
      "description": "Evidencia negativa que contradice",
      "example": "Meta A incompatible con Meta B",
      "narrative_weight": "critical"
    },
    {
      "role": "FINANCIAL_CONSTRAINT",
      "description": "Límites presupuestales a viabilidad",
      "example": "Presupuesto insuficiente para meta",
      "narrative_weight": "critical"
    },
    {
      "role": "LOGICAL_INCONSISTENCY",
      "description": "Contradicción lógica interna",
      "example": "Secuencia de actividades inválida",
      "narrative_weight":  "critical"
    }
  ],
  "N4_roles":  [
    {
      "role": "META_TRACEABILITY",
      "description": "Calidad del proceso analítico",
      "example": "95% cobertura de patterns",
      "narrative_weight": "medium"
    }
  ]
}
```

### 6.4 Interpretación de Confianza

```json
"confidence_interpretation": {
  "critical":  {
    "range": "0-19%",
    "label": "INVÁLIDO",
    "description": "Veto activado por N3, modelo lógico inválido técnicamente",
    "display":  "🔴"
  },
  "low": {
    "range": "20-49%",
    "label": "DÉBIL",
    "description": "Evidencia insuficiente, contradicciones detectadas, o validación fallida",
    "display": "🟠"
  },
  "medium": {
    "range":  "50-79%",
    "label": "MODERADO",
    "description": "Evidencia presente con limitaciones o inconsistencias menores",
    "display": "🟡"
  },
  "high":  {
    "range": "80-100%",
    "label": "ROBUSTO",
    "description": "Múltiples observaciones corroborantes, sin contradicciones, auditorías pasadas",
    "display": "🟢"
  }
}
```

---

## PARTE VII: CHECKLIST DE VALIDACIÓN

### 7.1 Validación Estructural

Para cada contrato generado, verificar:

- [ ] `method_binding. contract_type` coincide con clasificación del contrato
- [ ] Todos los métodos del inventario están en exactamente UNA fase (A, B, o C)
- [ ] Cada método tiene `level`, `output_type`, `fusion_behavior` asignados
- [ ] Métodos N3 tienen `veto_conditions` definidas
- [ ] Dependencias respetan jerarquía:  N1→N2→N3→N4

### 7.2 Validación de Ensamblaje

- [ ] `assembly_rules` contiene exactamente 4 reglas (R1, R2, R3, R4)
- [ ] `sources` de cada regla cubren todos los `provides` del nivel correspondiente
- [ ] `merge_strategy` coincide con tipo de contrato
- [ ] R3 tiene `gate_logic` con condiciones de veto

### 7.3 Validación de Fusión

- [ ] `fusion_specification. contract_type` coincide con clasificación
- [ ] `level_strategies` define estrategia para N1, N2, N3
- [ ] `cross_layer_fusion` define todas las relaciones
- [ ] Asimetría N3 está explícitamente declarada

### 7.4 Validación de Respuesta Humana

- [ ] `human_answer_structure` tiene 4 secciones (S1-S4)
- [ ] S3 tiene `veto_display` para casos de bloqueo
- [ ] `argumentative_roles` cubren todos los niveles
- [ ] `confidence_interpretation` tiene 4 rangos

---

// ═══════════════════════════════════════════════════════════════════════════════
// EJEMPLO COMENTADO PARA CONTRATO EPISTEMOLÓGICO V4 PARA D1-Q1
// ═══════════════════════════════════════════════════════════════════════════════
// 
// PASO PREVIO OBLIGATORIO (PARTE I, Sección 1.1):
// Antes de diligenciar, debemos clasificar el contrato. 
// 
// Q001 pertenece a base_question "01" que cubre:
// - Diagnóstico con datos numéricos (tasas VBG, porcentajes, cifras)
// - Verificación de fuentes oficiales (DANE, Medicina Legal)
// - Línea base temporal
//
// Según la tabla de PARTE I, Sección 1.1:
// Q001 es TYPE_A (Semántico) porque su foco es: 
// - Coherencia narrativa
// - Alineación temática  
// - NLP (procesamiento de lenguaje natural)
//
// Esto determina TODO lo que sigue.
// ═══════════════════════════════════════════════════════════════════════════════

{
  // ─────────────────────────────────────────────────────────────────────────────
  // SECCIÓN:  identity
  // ─────────────────────────────────────────────────────────────────────────────
  // Esta sección NO se modifica según la guía (PARTE IV, Sección 4.1 de episte_refact. md)
  // Solo agregamos contract_type para facilitar validación downstream. 
  
  "identity": {
    "base_slot": "D1-Q1",
    "representative_question_id": "Q001",
    "dimension_id": "DIM01",
    "policy_area_ids_served": ["PA01", "PA02", "PA03", "PA04", "PA05", "PA06", "PA07", "PA08", "PA09", "PA10"],
    "contracts_served": ["Q001", "Q031", "Q061", "Q091", "Q121", "Q151", "Q181", "Q211", "Q241", "Q271"],
    
    // ⬇️ NUEVO: Clasificación según PARTE I, Sección 1.1
    "contract_type": "TYPE_A",
    "contract_type_name": "Semántico",
    "contract_type_focus": "Coherencia narrativa, alineación temática, NLP",
    
    "contract_version": "4.0.0-epistemological",
    "created_at": "2025-12-22T00:00:00Z",
    "specification_source": "guia_diligenciamiento_v1.0.0"
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // SECCIÓN: executor_binding
  // ─────────────────────────────────────────────────────────────────────────────
  // No modificada por la guía epistemológica. 
  
  "executor_binding": {
    "executor_class": "D1_Q1_Executor",
    "executor_module": "farfan_pipeline. phases.Phase_two. executors"
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: method_binding
  // ═══════════════════════════════════════════════════════════════════════════════
  // 
  // GUÍA APLICADA:  PARTE II (Method Binding)
  // 
  // Según PARTE II, Sección 2.1, la estructura debe ser:
  // - orchestration_mode: "epistemological_pipeline" (NO "multi_method_pipeline")
  // - contract_type: el tipo clasificado en PARTE I
  // - execution_phases: 3 fases obligatorias (A, B, C)
  //
  // Las fases corresponden a (PARTE II, Sección 2.2):
  // - phase_A_construction: Métodos N1 (empíricos)
  // - phase_B_computation: Métodos N2 (inferenciales)
  // - phase_C_litigation: Métodos N3 (auditoría)
  // ═══════════════════════════════════════════════════════════════════════════════

  "method_binding": {
    // ⬇️ Cambiado de "multi_method_pipeline" según PARTE II, Sección 2.1
    "orchestration_mode": "epistemological_pipeline",
    
    // ⬇️ Tipo de contrato determina estrategias de fusión
    "contract_type": "TYPE_A",
    
    "method_count": 17,

    // ─────────────────────────────────────────────────────────────────────────
    // EXECUTION_PHASES:  Reemplaza el array plano "methods" 
    // ─────────────────────────────────────────────────────────────────────────
    // 
    // Según PARTE II, Sección 2.2:
    // "Debes implementar Fases de Ejecución en el orquestador"
    // - Fase A (Construction): Ejecuta todos los métodos de Nivel 1
    // - Fase B (Computation): Ejecuta Nivel 2 usando outputs de A
    // - Fase C (Litigation): Ejecuta Nivel 3 para intentar "romper" resultados de B
    // ─────────────────────────────────────────────────────────────────────────

    "execution_phases": {
      
      // ═════════════════════════════════════════════════════════════════════════
      // PHASE_A:  CONSTRUCTION (Nivel 1 - Empírico)
      // ═════════════════════════════════════════════════════════════════════════
      // 
      // GUÍA:  PARTE II, Sección 2.2 - PHASE_A
      // 
      // Criterios de inclusión (cito textualmente):
      // - "Método lee directamente PreprocesadoMetadata o documento raw"
      // - "Output son literales:  strings, números, listas de entidades"
      // - "NO realiza transformación interpretativa"
      // - "Patrones de nombre: extract_*, parse_*, mine_*, chunk_*"
      //
      // Campos requeridos según PARTE II, Sección 2.2:
      // - class_name, method_name, mother_file, provides
      // - level:  "N1-EMP"
      // - output_type: "FACT"
      // - fusion_behavior: "additive"
      // - requires:  [] (vacío para N1)
      // ═════════════════════════════════════════════════════════════════════════

      "phase_A_construction": {
        "description": "Empirical observation layer - direct document extraction without interpretation",
        "level": "N1",
        "level_name": "Base Empírica",
        "epistemology": "Empirismo positivista - los datos existen independientemente del observador",
        
        "methods": [
          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 1: _extract_point_evidence
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1? 
          // - Nombre contiene "extract_" → cumple patrón de PARTE II, Sección 2.2
          // - Extrae evidencia puntual como texto literal
          // - No computa scores ni probabilidades
          {
            "class_name": "IndustrialPolicyProcessor",
            "method_name": "_extract_point_evidence",
            "mother_file": "policy_processor. py",
            "provides": "industrialpolicyprocessor.extract_point_evidence",
            "level":  "N1-EMP",
            "output_type":  "FACT",
            "fusion_behavior": "additive",
            "description": "Extrae evidencia puntual del texto como observación literal",
            "requires":  [],
            "classification_rationale": "Patrón 'extract_' + output literal → N1-EMP (PARTE II, Sec 2.2)"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 2: _extract_goals
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1?
          // - Nombre contiene "extract_" → patrón N1
          // - Extrae metas/objetivos como texto
          // - Listado en "Clases típicas de N1" (PARTE II, Sección 2.2)
          {
            "class_name": "CausalExtractor",
            "method_name": "_extract_goals",
            "mother_file":  "derek_beach.py",
            "provides": "causalextractor.extract_goals",
            "level": "N1-EMP",
            "output_type": "FACT",
            "fusion_behavior": "additive",
            "description": "Extrae metas y objetivos como segmentos de texto literal",
            "requires": [],
            "classification_rationale":  "Patrón 'extract_' + clase CausalExtractor listada en N1 típicas"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 3: _parse_goal_context
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1?
          // - Nombre contiene "parse_" → patrón N1 (PARTE II, Sec 2.2)
          // - Parsea contexto extrayendo texto literal
          // - Explícitamente listado:  "CausalExtractor._parse_goal_context (when extracting literal text)"
          {
            "class_name": "CausalExtractor",
            "method_name":  "_parse_goal_context",
            "mother_file": "derek_beach.py",
            "provides": "causalextractor.parse_goal_context",
            "level": "N1-EMP",
            "output_type": "FACT",
            "fusion_behavior": "additive",
            "description": "Parsea contexto de metas extrayendo texto literal",
            "requires":  [],
            "classification_rationale": "Patrón 'parse_' + extrae texto literal → N1-EMP"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 4: _parse_amount
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1?
          // - Nombre contiene "parse_" → patrón N1
          // - Extrae montos como números literales del documento
          // - No calcula, solo parsea
          {
            "class_name": "FinancialAuditor",
            "method_name": "_parse_amount",
            "mother_file": "derek_beach.py",
            "provides":  "financialauditor.parse_amount",
            "level":  "N1-EMP",
            "output_type": "FACT",
            "fusion_behavior":  "additive",
            "description": "Parsea montos financieros como números literales",
            "requires": [],
            "classification_rationale": "Patrón 'parse_' + output numérico literal → N1-EMP"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 5: _extract_financial_amounts
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1?
          // - Nombre contiene "extract_" → patrón N1
          // - Listado explícitamente en "Clases típicas de N1":  
          //   "PDETMunicipalPlanAnalyzer:  _extract_financial_amounts"
          {
            "class_name": "PDETMunicipalPlanAnalyzer",
            "method_name": "_extract_financial_amounts",
            "mother_file":  "financiero_viabilidad_tablas.py",
            "provides": "pdetmunicipalplananalyzer. extract_financial_amounts",
            "level": "N1-EMP",
            "output_type":  "FACT",
            "fusion_behavior": "additive",
            "description":  "Extrae montos financieros de tablas del documento",
            "requires": [],
            "classification_rationale": "Patrón 'extract_' + clase listada en N1 típicas (PARTE II, Sec 2.2)"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 6: _extract_from_budget_table
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1? 
          // - Nombre contiene "extract_" → patrón N1
          // - Listado en "Clases típicas de N1": 
          //   "PDETMunicipalPlanAnalyzer: _extract_from_budget_table"
          {
            "class_name":  "PDETMunicipalPlanAnalyzer",
            "method_name":  "_extract_from_budget_table",
            "mother_file": "financiero_viabilidad_tablas.py",
            "provides": "pdetmunicipalplananalyzer.extract_from_budget_table",
            "level": "N1-EMP",
            "output_type": "FACT",
            "fusion_behavior": "additive",
            "description": "Extrae datos crudos de tablas presupuestales",
            "requires": [],
            "classification_rationale":  "Patrón 'extract_' + clase listada en N1 típicas"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 7: _extract_quantitative_claims
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1?
          // - Nombre contiene "extract_" → patrón N1
          // - Extrae afirmaciones cuantitativas como observaciones
          // - No las valida (eso sería N3), solo las extrae
          {
            "class_name": "PolicyContradictionDetector",
            "method_name": "_extract_quantitative_claims",
            "mother_file": "contradiction_deteccion.py",
            "provides": "policycontradictiondetector.extract_quantitative_claims",
            "level": "N1-EMP",
            "output_type": "FACT",
            "fusion_behavior": "additive",
            "description": "Extrae afirmaciones cuantitativas del texto",
            "requires": [],
            "classification_rationale":  "Patrón 'extract_' + output son claims literales"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 8: _parse_number
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1?
          // - Nombre contiene "parse_" → patrón N1
          // - Convierte strings a números (extracción, no inferencia)
          {
            "class_name": "PolicyContradictionDetector",
            "method_name": "_parse_number",
            "mother_file": "contradiction_deteccion.py",
            "provides": "policycontradictiondetector.parse_number",
            "level": "N1-EMP",
            "output_type":  "FACT",
            "fusion_behavior": "additive",
            "description":  "Parsea números del texto como valores literales",
            "requires": [],
            "classification_rationale": "Patrón 'parse_' + output literal"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 9: chunk_text
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N1?
          // - Nombre contiene "chunk_" → patrón N1 (PARTE II, Sec 2.2)
          // - Listado explícitamente:  "SemanticProcessor: chunk_text"
          // - Segmenta texto sin interpretación
          {
            "class_name": "SemanticProcessor",
            "method_name": "chunk_text",
            "mother_file": "semantic_chunking_policy.py",
            "provides": "semanticprocessor.chunk_text",
            "level": "N1-EMP",
            "output_type": "FACT",
            "fusion_behavior": "additive",
            "description": "Segmenta texto en chunks sin transformación semántica",
            "requires": [],
            "classification_rationale": "Patrón 'chunk_' + listado en N1 típicas"
          }
        ],

        "dependencies": [],
        "output_target": "raw_facts"
      },

      // ═════════════════════════════════════════════════════════════════════════
      // PHASE_B:  COMPUTATION (Nivel 2 - Inferencial)
      // ═════════════════════════════════════════════════════════════════════════
      // 
      // GUÍA:  PARTE II, Sección 2.2 - PHASE_B
      // 
      // Criterios de inclusión (cito textualmente):
      // - "Consume outputs de N1"
      // - "Produce cantidades derivadas:  scores, probabilidades, relaciones inferidas"
      // - "Realiza análisis estadístico, scoring, generación de embeddings"
      // - "Patrones de nombre: analyze_*, score_*, calculate_*, infer_*, evaluate_*, compare_*"
      //
      // Campos requeridos: 
      // - level: "N2-INF"
      // - output_type:  "PARAMETER"
      // - fusion_behavior: "multiplicative"
      // - requires: ["raw_facts"]
      // - modifies: ["edge_weights", "confidence_scores"]
      // ═════════════════════════════════════════════════════════════════════════

      "phase_B_computation": {
        "description": "Inferential analysis layer - transformation of observations into analytical constructs",
        "level": "N2",
        "level_name": "Procesamiento Inferencial",
        "epistemology": "Bayesianismo subjetivista - creencias actualizables por evidencia",

        "methods": [
          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 10: diagnose_critical_links
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N2?
          // - "diagnose" implica análisis/inferencia (no extracción)
          // - Listado en taxonomía N1 PERO con función inferencial
          // - Produce diagnóstico (juicio derivado), no dato crudo
          // 
          // NOTA: La taxonomía lo lista en N1 pero su función es inferencial. 
          // Aplicamos el árbol de decisión (PARTE II, Sec 2.3):
          // "¿M transforma/interpreta?  → SÍ → ¿Output derivado?  → SÍ → N2-INF"
          {
            "class_name": "TextMiningEngine",
            "method_name": "diagnose_critical_links",
            "mother_file": "analyzer_one. py",
            "provides": "textminingengine.diagnose_critical_links",
            "level": "N2-INF",
            "output_type":  "PARAMETER",
            "fusion_behavior": "multiplicative",
            "description": "Diagnostica vínculos críticos infiriendo relaciones entre elementos",
            "requires": ["raw_facts"],
            "modifies": ["edge_weights"],
            "classification_rationale": "Verbo 'diagnose' implica inferencia; output es juicio derivado → N2-INF (árbol PARTE II, Sec 2.3)"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 11: _analyze_link_text
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N2?
          // - Nombre contiene "analyze_" → patrón N2 explícito
          // - Produce análisis (derivado), no texto crudo
          {
            "class_name": "TextMiningEngine",
            "method_name":  "_analyze_link_text",
            "mother_file": "analyzer_one.py",
            "provides": "textminingengine.analyze_link_text",
            "level": "N2-INF",
            "output_type": "PARAMETER",
            "fusion_behavior": "multiplicative",
            "description": "Analiza texto de vínculos computando métricas derivadas",
            "requires": ["raw_facts"],
            "modifies": ["edge_weights", "confidence_scores"],
            "classification_rationale": "Patrón 'analyze_' → N2-INF (PARTE II, Sec 2.2)"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 12: process
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N2?
          // - Listado en "Clases típicas de N2": 
          //   "IndustrialPolicyProcessor: process"
          // - Procesa y transforma datos en constructos analíticos
          {
            "class_name": "IndustrialPolicyProcessor",
            "method_name": "process",
            "mother_file": "policy_processor.py",
            "provides":  "industrialpolicyprocessor.process",
            "level": "N2-INF",
            "output_type": "PARAMETER",
            "fusion_behavior": "multiplicative",
            "description": "Pipeline principal de procesamiento que transforma observaciones en constructos",
            "requires":  ["raw_facts"],
            "modifies": ["edge_weights", "confidence_scores"],
            "classification_rationale": "Listado en N2 típicas + transforma datos → N2-INF"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 13: _match_patterns_in_sentences
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N2?
          // - Pattern matching produce scores de coincidencia (derivados)
          // - Retorna tuple[list, list[int]] → resultados analíticos
          // - Listado en taxonomía original como N2
          {
            "class_name": "IndustrialPolicyProcessor",
            "method_name": "_match_patterns_in_sentences",
            "mother_file":  "policy_processor. py",
            "provides": "industrialpolicyprocessor. match_patterns_in_sentences",
            "level": "N2-INF",
            "output_type": "PARAMETER",
            "fusion_behavior": "multiplicative",
            "description": "Matchea patrones retornando scores de coincidencia",
            "requires":  ["raw_facts"],
            "modifies": ["confidence_scores"],
            "classification_rationale": "Produce scores analíticos (no literales) → N2-INF"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 14: evaluate_policy_metric
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N2?
          // - Nombre contiene "evaluate_" → patrón N2 explícito
          // - Listado en "Clases típicas de N2":
          //   "BayesianNumericalAnalyzer:  evaluate_policy_metric"
          // - Retorna BayesianEvaluation → cantidad derivada probabilística
          {
            "class_name": "BayesianNumericalAnalyzer",
            "method_name":  "evaluate_policy_metric",
            "mother_file": "embedding_policy. py",
            "provides": "bayesiannumericalanalyzer.evaluate_policy_metric",
            "level": "N2-INF",
            "output_type": "PARAMETER",
            "fusion_behavior": "multiplicative",
            "description": "Evaluación bayesiana que produce distribución posterior",
            "requires":  ["raw_facts"],
            "modifies": ["confidence_scores", "posterior_distribution"],
            "classification_rationale": "Patrón 'evaluate_' + clase listada en N2 típicas + output probabilístico"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 15: compare_policies
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N2? 
          // - Nombre contiene "compare_" → patrón N2 explícito
          // - Listado en "Clases típicas de N2": 
          //   "BayesianNumericalAnalyzer:  compare_policies"
          // - Produce comparación (inferencia relacional)
          {
            "class_name":  "BayesianNumericalAnalyzer",
            "method_name": "compare_policies",
            "mother_file": "embedding_policy.py",
            "provides": "bayesiannumericalanalyzer.compare_policies",
            "level": "N2-INF",
            "output_type": "PARAMETER",
            "fusion_behavior": "multiplicative",
            "description": "Compara políticas produciendo métricas de diferencia",
            "requires": ["raw_facts"],
            "modifies": ["edge_weights"],
            "classification_rationale": "Patrón 'compare_' + clase listada en N2 típicas"
          },

          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 16: embed_single
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N2?
          // - Genera embeddings (representaciones numéricas derivadas)
          // - Output:  NDArray[np.floating] → cantidad derivada
          // - Transforma texto en vector (transformación interpretativa)
          {
            "class_name": "SemanticProcessor",
            "method_name": "embed_single",
            "mother_file": "semantic_chunking_policy.py",
            "provides": "semanticprocessor.embed_single",
            "level": "N2-INF",
            "output_type": "PARAMETER",
            "fusion_behavior": "multiplicative",
            "description": "Genera embedding vectorial del texto (representación derivada)",
            "requires": ["raw_facts"],
            "modifies": ["semantic_vectors"],
            "classification_rationale": "Output es representación derivada (vector), no literal → N2-INF"
          }
        ],

        "dependencies": ["phase_A_construction"],
        "output_target": "inferences"
      },

      // ═════════════════════════════════════════════════════════════════════════
      // PHASE_C:  LITIGATION (Nivel 3 - Auditoría)
      // ═════════════════════════════════════════════════════════════════════════
      // 
      // GUÍA:  PARTE II, Sección 2.2 - PHASE_C
      // 
      // Criterios de inclusión (cito textualmente):
      // - "Consume outputs de N1 Y N2"
      // - "Produce flags de validación, reportes de contradicción, moduladores de confianza"
      // - "Puede INVALIDAR o SUPRIMIR hallazgos de capas anteriores"
      // - "Patrones de nombre: validate_*, detect_*, audit_*, check_*, test_*, verify_*"
      //
      // PROPIEDAD CRÍTICA (cito textualmente):
      // "Influencia ASIMÉTRICA — puede invalidar N1/N2, pero N1/N2 NO pueden invalidar N3"
      //
      // Campos requeridos:
      // - level: "N3-AUD"
      // - output_type:  "CONSTRAINT"
      // - fusion_behavior: "gate"
      // - requires: ["raw_facts", "inferences"]
      // - modulates: campos que puede afectar
      // - veto_conditions: condiciones de bloqueo
      // ═════════════════════════════════════════════════════════════════════════

      "phase_C_litigation": {
        "description": "Audit layer - attempt to 'break' results from Phase B.  Acts as VETO GATE.",
        "level":  "N3",
        "level_name": "Auditoría y Robustez",
        "epistemology":  "Falsacionismo popperiano - el conocimiento se fortalece por intentos de refutación",
        
        // ⬇️ CRÍTICO: Propiedad de asimetría declarada explícitamente
        "asymmetry_principle": "N3 can invalidate N1/N2 findings, but N1/N2 CANNOT invalidate N3",

        "methods": [
          // ─────────────────────────────────────────────────────────────────
          // MÉTODO 17: _statistical_significance_test
          // ─────────────────────────────────────────────────────────────────
          // ¿Por qué N3? 
          // - Nombre contiene "test_" → patrón N3 explícito (PARTE II, Sec 2.2)
          // - Es un TEST de significancia estadística
          // - Puede INVALIDAR hallazgos si p-value no es significativo
          // - Listado en "Clases típicas de N3":
          //   "PolicyContradictionDetector: _statistical_significance_test"
          //
          // NOTA CRÍTICA (de la taxonomía):
          // "Un p-value no es una evidencia igual que un párrafo de texto"
          // Por eso es CONSTRAINT, no FACT ni PARAMETER. 
          {
            "class_name":  "PolicyContradictionDetector",
            "method_name":  "_statistical_significance_test",
            "mother_file": "contradiction_deteccion.py",
            "provides": "policycontradictiondetector.statistical_significance_test",
            "level": "N3-AUD",
            "output_type": "CONSTRAINT",
            "fusion_behavior": "gate",
            "description": "Test de significancia estadística que puede VETAR hallazgos",
            "requires": ["raw_facts", "inferences"],
            
            // ⬇️ Campos que este método puede MODULAR (reducir confianza o bloquear)
            "modulates": [
              "raw_facts. confidence",
              "inferences.confidence"
            ],
            
            // ⬇️ VETO_CONDITIONS:  Condiciones bajo las cuales este método BLOQUEA
            // Según PARTE II, Sección 2.2:
            // "Métodos N3 tienen veto_conditions definidas"
            "veto_conditions": {
              "significance_below_threshold": {
                "trigger": "p_value > 0.05",
                "action": "reduce_confidence",
                "scope": "affected_claims",
                "confidence_multiplier": 0.5,
                "rationale": "Hallazgo no estadísticamente significativo"
              },
              "high_variance_detected": {
                "trigger": "coefficient_of_variation > 0.8",
                "action": "flag_caution",
                "scope": "source_facts",
                "confidence_multiplier": 0.7,
                "rationale": "Alta variabilidad reduce confiabilidad"
              }
            },

            "classification_rationale":  "Patrón 'test_' + puede invalidar hallazgos + listado en N3 típicas (PARTE II, Sec 2.2)"
          }
        ],

        "dependencies": ["phase_A_construction", "phase_B_computation"],
        "output_target": "audit_results",
        
        // ⬇️ Según PARTE II, Sec 2.2: "fusion_mode" para N3
        "fusion_mode": "modulation"
      }
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN:  question_context
  // ═══════════════════════════════════════════════════════════════════════════════
  // No modificada por la guía (se preserva de v3).
  
  "question_context": {
    "monolith_ref": "Q001",
    "overrides": null,
    "failure_contract": {
      "abort_if":  ["missing_required_element", "incomplete_text", "no_quantitative_data"],
      "emit_code": "ABORT-D1-Q1-REQ"
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN:  signal_requirements
  // ═══════════════════════════════════════════════════════════════════════════════
  // No modificada por la guía (se preserva de v3).
  
  "signal_requirements": {
    "derivation_source": "expected_elements",
    "derivation_rules": {
      "mandatory":  "expected_elements[required=true]. type → detection_{type}",
      "optional": "expected_elements[required=false].type → detection_{type}"
    },
    "signal_aggregation": "weighted_mean",
    "minimum_signal_threshold": 0.5
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: evidence_assembly
  // ═══════════════════════════════════════════════════════════════════════════════
  // 
  // GUÍA APLICADA: PARTE III (Evidence Assembly)
  // 
  // Según PARTE III, Sección 3.1, la estructura debe incluir:
  // - type_system:  Tipología de outputs (PARTE III, Sec 3.2)
  // - assembly_rules: 4 reglas obligatorias (PARTE III, Sec 3.3)
  //
  // Según PARTE III, Sección 3.3: 
  // Para TYPE_A (Semántico), usamos la PLANTILLA TYPE_A con:
  // - R1: empirical_extraction
  // - R2: semantic_triangulation (estrategia específica de TYPE_A)
  // - R3: audit_gate (veto_gate)
  // - R4: narrative_synthesis
  // ═══════════════════════════════════════════════════════════════════════════════

  "evidence_assembly": {
    "engine": "EVIDENCE_NEXUS",
    "module": "farfan_pipeline. phases.Phase_two.evidence_nexus",
    "class_name": "EvidenceNexus",
    "method_name": "assemble",

    // ─────────────────────────────────────────────────────────────────────────
    // TYPE_SYSTEM: Define tipos de output y su comportamiento en fusión
    // ─────────────────────────────────────────────────────────────────────────
    // GUÍA: PARTE III, Sección 3.2
    // 
    // Cada tipo tiene: 
    // - origin_level: De qué nivel proviene
    // - fusion_operation: Qué hace en el grafo
    // - merge_behavior: Cómo se comporta al fusionar
    // - symbol:  Representación visual
    // ─────────────────────────────────────────────────────────────────────────

    "type_system": {
      "FACT": {
        "origin_level": "N1",
        "fusion_operation":  "graph_node_addition",
        "merge_behavior": "additive",
        "symbol": "⊕",
        "description":  "Se SUMA al grafo como nodo - observación literal"
      },
      "PARAMETER":  {
        "origin_level": "N2",
        "fusion_operation": "edge_weight_modification",
        "merge_behavior": "multiplicative",
        "symbol": "⊗",
        "description": "MODIFICA pesos de aristas del grafo - inferencia derivada"
      },
      "CONSTRAINT": {
        "origin_level": "N3",
        "fusion_operation":  "branch_filtering",
        "merge_behavior": "gate",
        "symbol": "⊘",
        "description": "FILTRA/BLOQUEA ramas si validación falla - veto epistemológico"
      },
      "NARRATIVE": {
        "origin_level": "N4",
        "fusion_operation":  "synthesis",
        "merge_behavior": "terminal",
        "symbol": "⊙",
        "description": "CONSUME grafo para texto final - síntesis narrativa"
      }
    },

    // ─────────────────────────────────────────────────────────────────────────
    // ASSEMBLY_RULES: 4 reglas obligatorias
    // ─────────────────────────────────────────────────────────────────────────
    // GUÍA: PARTE III, Sección 3.3 - PLANTILLA TYPE_A (Semántico)
    // 
    // Usamos la plantilla TYPE_A porque Q001 es contrato semántico. 
    // La estrategia clave es semantic_triangulation: 
    // "Si TextMining y IndustrialPolicy extraen el mismo dato → merge nodes, increase confidence"
    // ─────────────────────────────────────────────────────────────────────────

    "assembly_rules": [
      // ═════════════════════════════════════════════════════════════════════
      // REGLA R1: EMPIRICAL_EXTRACTION
      // ═════════════════════════════════════════════════════════════════════
      // 
      // GUÍA: PARTE III, Sección 3.3 - R1 de plantilla TYPE_A
      // 
      // Esta regla: 
      // - Consolida TODOS los outputs de N1 (los 9 métodos de phase_A)
      // - Usa concat_with_deduplication para evitar duplicados
      // - Preserva confianza individual de cada observación
      // ═════════════════════════════════════════════════════════════════════
      {
        "rule_id": "R1_empirical_extraction",
        "rule_type": "empirical_basis",
        "target":  "raw_facts",
        
        // ⬇️ TODOS los provides de N1 (9 métodos)
        "sources": [
          "industrialpolicyprocessor. extract_point_evidence",
          "causalextractor.extract_goals",
          "causalextractor.parse_goal_context",
          "financialauditor.parse_amount",
          "pdetmunicipalplananalyzer.extract_financial_amounts",
          "pdetmunicipalplananalyzer. extract_from_budget_table",
          "policycontradictiondetector.extract_quantitative_claims",
          "policycontradictiondetector.parse_number",
          "semanticprocessor.chunk_text"
        ],
        
        "merge_strategy": "concat_with_deduplication",
        "deduplication_key": "element_id",
        "output_type": "FACT",
        "confidence_propagation": "preserve_individual",
        
        "rationale": "Según PARTE III, Sec 3.3: R1 consolida outputs empíricos de N1"
      },

      // ═════════════════════════════════════════════════════════════════════
      // REGLA R2: SEMANTIC_TRIANGULATION
      // ═════════════════════════════════════════════════════════════════════
      // 
      // GUÍA: PARTE III, Sección 3.3 - R2 de plantilla TYPE_A
      // 
      // ESTRATEGIA ESPECÍFICA DE TYPE_A (Semántico):
      // "semantic_triangulation" - Si múltiples métodos detectan el mismo
      // hecho, fusionar nodos y AUMENTAR confianza (corroboración).
      //
      // Cita de taxonomía de fusión (PARTE IV, Sec 4.4):
      // "semantic_corroboration:  Fusionar nodos si dicen lo mismo → mayor peso"
      // ═════════════════════════════════════════════════════════════════════
      {
        "rule_id": "R2_semantic_triangulation",
        "rule_type": "corroboration",
        "target":  "triangulated_facts",
        
        // ⬇️ TODOS los provides de N2 (7 métodos)
        "sources": [
          "textminingengine.diagnose_critical_links",
          "textminingengine.analyze_link_text",
          "industrialpolicyprocessor.process",
          "industrialpolicyprocessor. match_patterns_in_sentences",
          "bayesiannumericalanalyzer.evaluate_policy_metric",
          "bayesiannumericalanalyzer.compare_policies",
          "semanticprocessor.embed_single"
        ],
        
        "input_dependencies": ["raw_facts"],
        
        // ⬇️ ESTRATEGIA CLAVE DE TYPE_A
        "merge_strategy": "semantic_triangulation",
        
        // ⬇️ Operación específica de triangulación semántica
        "operation": {
          "description": "Si TextMining AND IndustrialPolicy extraen mismo dato → merge nodes, increase confidence",
          "corroboration_formula": "confidence_new = 1 - ∏(1 - conf_i)",
          "semantic_similarity_threshold": 0.85
        },
        
        "output_type": "PARAMETER",
        "confidence_propagation": "corroborative_boost",
        
        "rationale": "Según PARTE III, Sec 3.3: TYPE_A usa semantic_triangulation para corroboración"
      },

      // ═════════════════════════════════════════════════════════════════════
      // REGLA R3: AUDIT_GATE
      // ═════════════════════════════════════════════════════════════════════
      // 
      // GUÍA: PARTE III, Sección 3.3 - R3 de plantilla TYPE_A
      // 
      // Esta regla implementa el VETO GATE de N3.
      // 
      // CRÍTICO (de la taxonomía):
      // "Si IndustrialGradeValidator falla, la respuesta no debe ser 
      //  'tenemos evidencia mixta', debe ser 'el modelo lógico es inválido técnicamente'"
      //
      // gate_logic define las condiciones de veto y sus efectos. 
      // ═════════════════════════════════════════════════════════════════════
      {
        "rule_id": "R3_audit_gate",
        "rule_type": "robustness_gate",
        "target": "validated_facts",
        
        // ⬇️ TODOS los provides de N3 (1 método en este contrato)
        "sources": [
          "policycontradictiondetector.statistical_significance_test"
        ],
        
        "input_dependencies": ["raw_facts", "triangulated_facts"],
        
        // ⬇️ ESTRATEGIA DE VETO (universal para todos los tipos)
        "merge_strategy": "veto_gate",
        
        "output_type": "CONSTRAINT",
        
        // ⬇️ GATE_LOGIC:  Define cuándo y cómo se bloquea
        // Según PARTE III, Sec 3.3: "R3 tiene gate_logic con condiciones de veto"
        "gate_logic": {
          "contradiction_detected": {
            "action": "suppress_fact",
            "confidence_multiplier": 0.0,
            "scope": "contradicting_nodes",
            "display_message": "⚠️ Contradicción detectada:  hallazgo suprimido"
          },
          "low_coherence":  {
            "action": "reduce_confidence",
            "confidence_multiplier": 0.5,
            "scope": "affected_subgraph",
            "display_message": "⚠️ Baja coherencia: confianza reducida 50%"
          },
          "significance_failed": {
            "action": "flag_caution",
            "confidence_multiplier": 0.7,
            "scope": "source_facts",
            "display_message": "⚠️ Significancia estadística no alcanzada"
          }
        },
        
        "rationale": "Según PARTE III, Sec 3.3: R3 implementa veto_gate para N3"
      },

      // ═════════════════════════════════════════════════════════════════════
      // REGLA R4: NARRATIVE_SYNTHESIS
      // ═════════════════════════════════════════════════════════════════════
      // 
      // GUÍA:  PARTE III, Sección 3.3 - R4 de todas las plantillas
      // 
      // Esta regla:
      // - Consume el grafo validado (después del veto gate)
      // - Genera la respuesta humana usando DoctoralCarverSynthesizer
      // - Es terminal (no alimenta otras reglas)
      // ═════════════════════════════════════════════════════════════════════
      {
        "rule_id":  "R4_narrative_synthesis",
        "rule_type":  "synthesis",
        "target": "human_answer",
        
        // ⬇️ Sin sources directos - consume el grafo procesado
        "sources": [],
        
        "input_dependencies": ["validated_facts", "triangulated_facts", "audit_results"],
        
        "merge_strategy": "carver_doctoral_synthesis",
        "output_type": "NARRATIVE",
        
        "external_handler": {
          "class":  "DoctoralCarverSynthesizer",
          "module": "farfan_pipeline. phases.Phase_two.carver"
        },
        
        "rationale": "Según PARTE III, Sec 3.3: R4 genera narrativa PhD-style"
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: fusion_specification
  // ═══════════════════════════════════════════════════════════════════════════════
  // 
  // GUÍA APLICADA:  PARTE IV (Fusion Specification)
  // 
  // Según PARTE IV, Sección 4.1, la estructura debe incluir: 
  // - contract_type
  // - primary_strategy
  // - level_strategies
  // - cross_layer_effects
  // - fusion_pipeline
  //
  // Según PARTE IV, Sección 4.3 (tabla de estrategias por tipo):
  // TYPE_A (Semántico):
  // - N1 Strategy:  semantic_corroboration
  // - N2 Strategy: dempster_shafer
  // - N3 Strategy: veto_gate
  // ═══════════════════════════════════════════════════════════════════════════════

  "fusion_specification": {
    "contract_type": "TYPE_A",
    
    // ⬇️ Estrategia principal para TYPE_A (de taxonomía de fusión)
    "primary_strategy":  "semantic_triangulation",

    // ─────────────────────────────────────────────────────────────────────────
    // LEVEL_STRATEGIES:  Estrategia por nivel
    // ─────────────────────────────────────────────────────────────────────────
    // GUÍA: PARTE IV, Sección 4.2 y 4.3
    // 
    // Para TYPE_A según tabla 4.3:
    // - N1: semantic_corroboration
    // - N2: dempster_shafer
    // - N3: veto_gate
    // ─────────────────────────────────────────────────────────────────────────

    "level_strategies": {
      // ═══════════════════════════════════════════════════════════════════
      // N1: SEMANTIC_CORROBORATION
      // ═══════════════════════════════════════════════════════════════════
      // 
      // ¿Por qué semantic_corroboration para N1 en TYPE_A? 
      // 
      // Cita de PARTE IV, Sec 4.4:
      // "semantic_corroboration: Fusionar nodos si dicen lo mismo → mayor peso"
      // 
      // En contratos semánticos, múltiples métodos pueden detectar el mismo
      // hecho (ej.  TextMining y IndustrialPolicy encuentran la misma fuente).
      // En lugar de crear nodos duplicados, los fusionamos y aumentamos
      // la confianza por corroboración. 
      // ═══════════════════════════════════════════════════════════════════
      "N1_fact_fusion": {
        "strategy": "semantic_corroboration",
        "behavior": "additive",
        "conflict_resolution": "corroborative_stacking",
        "formula": {
          "description": "Si mismo hecho detectado por múltiples métodos → confidence aumenta",
          "expression": "confidence_combined = 1 - ∏(1 - conf_i)",
          "example": "3 métodos con conf 0.7 cada uno → combined = 1 - (0.3)³ = 0.973"
        },
        "rationale": "PARTE IV, Sec 4.3: TYPE_A usa semantic_corroboration para N1"
      },

      // ═══════════════════════════════════════════════════════════════════
      // N2: DEMPSTER_SHAFER
      // ═══════════════════════════════════════════════════════════════════
      // 
      // ¿Por qué dempster_shafer para N2 en TYPE_A?
      // 
      // Cita de PARTE IV, Sec 4.4:
      // "dempster_shafer: Propagación de creencia combinatoria"
      // 
      // En contratos semánticos, las inferencias de N2 (diagnósticos,
      // análisis, scores) pueden tener diferentes grados de certeza.
      // Dempster-Shafer permite combinar evidencia de múltiples fuentes
      // manejando incertidumbre explícitamente.
      // ═══════════════════════════════════════════════════════════════════
      "N2_parameter_fusion": {
        "strategy": "dempster_shafer",
        "behavior": "multiplicative",
        "conflict_resolution": "belief_combination",
        "affects":  ["N1_facts. confidence", "N1_facts.edge_weights"],
        "formula": {
          "description": "Combina masa de probabilidad de múltiples fuentes",
          "normalization": "Descarta conflictos irreconciliables"
        },
        "rationale": "PARTE IV, Sec 4.3: TYPE_A usa dempster_shafer para N2"
      },

      // ═══════════════════════════════════════════════════════════════════
      // N3: VETO_GATE
      // ═══════════════════════════════════════════════════════════════════
      // 
      // ¿Por qué veto_gate para N3 en TODOS los tipos?
      // 
      // Cita de PARTE IV, Sec 4.4:
      // "veto_gate: Si auditoría falla → bloquear rama de evidencia"
      // 
      // CRÍTICO (de taxonomía original):
      // "Si IndustrialGradeValidator falla, la respuesta NO debe ser
      //  'tenemos evidencia mixta', debe ser 'el modelo es INVÁLIDO técnicamente'"
      // 
      // N3 tiene influencia ASIMÉTRICA:  puede invalidar N1/N2, pero
      // N1/N2 NO pueden invalidar N3.
      // ═══════════════════════════════════════════════════════════════════
      "N3_constraint_fusion": {
        "strategy": "veto_gate",
        "behavior":  "gate",
        "asymmetry_principle": "audit_dominates",
        "propagation": {
          "upstream": "confidence_backpropagation",
          "downstream":  "branch_blocking"
        },
        "rationale":  "PARTE IV, Sec 4.3: TODOS los tipos usan veto_gate para N3"
      }
    },

    // ─────────────────────────────────────────────────────────────────────────
    // FUSION_PIPELINE:  Secuencia de fusión
    // ─────────────────────────────────────────────────────────────────────────
    // GUÍA: No explícita, pero derivada de la lógica de fases
    // 
    // El pipeline refleja la secuencia: 
    // Stage 1: BUILD grafo de N1
    // Stage 2: MODIFY pesos con N2
    // Stage 3: FILTER/BLOCK con N3
    // Stage 4: GENERATE narrativa
    // ─────────────────────────────────────────────────────────────────────────

    "fusion_pipeline": {
      "stage_1_fact_accumulation": {
        "input": "phase_A_construction. outputs",
        "operation": "BUILD evidence graph from extracted facts",
        "output": "evidence_graph_v1",
        "type_consumed": "FACT",
        "behavior": "additive"
      },
      "stage_2_parameter_application": {
        "input": ["evidence_graph_v1", "phase_B_computation.outputs"],
        "operation": "MODIFY edge weights based on inferred parameters",
        "output": "evidence_graph_v2_weighted",
        "type_consumed": "PARAMETER",
        "behavior": "multiplicative"
      },
      "stage_3_constraint_filtering": {
        "input": ["evidence_graph_v2_weighted", "phase_C_litigation.outputs"],
        "operation": "FILTER/BLOCK branches that fail validation",
        "output": "evidence_graph_v3_validated",
        "type_consumed": "CONSTRAINT",
        "behavior": "gate",
        "blocking_log": "audit_results.blocked_branches"
      },
      "stage_4_synthesis": {
        "input": "evidence_graph_v3_validated",
        "operation": "GENERATE narrative from validated graph",
        "output": "human_answer",
        "type_produced": "NARRATIVE"
      }
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: cross_layer_fusion
  // ═══════════════════════════════════════════════════════════════════════════════
  // 
  // GUÍA APLICADA:  PARTE V (Cross Layer Fusion)
  // 
  // Según PARTE V, Sección 5.1, define relaciones entre capas. 
  // 
  // CRÍTICO: La asimetría de N3 debe estar explícita: 
  // "N3 can BLOCK N1 facts...  asymmetry:  N1 CANNOT invalidate N3"
  // ═══════════════════════════════════════════════════════════════════════════════

  "cross_layer_fusion": {
    // ─────────────────────────────────────────────────────────────────────────
    // N1 → N2: Forward Propagation
    // ─────────────────────────────────────────────────────────────────────────
    // Los hechos de N1 fluyen hacia N2 para ser analizados. 
    // N2 LEE N1, no lo modifica directamente en este flujo.
    
    "N1_to_N2":  {
      "relationship": "N2 reads N1 facts",
      "effect": "N2 computes parameters FROM N1 observations",
      "data_flow": "forward_propagation",
      "rationale": "PARTE V, Sec 5.1: N2 consume outputs de N1 para inferir"
    },

    // ─────────────────────────────────────────────────────────────────────────
    // N2 → N1: Confidence Backpropagation
    // ─────────────────────────────────────────────────────────────────────────
    // Los parámetros de N2 pueden MODIFICAR la confianza de hechos N1.
    // Ej: Si análisis semántico encuentra alta coherencia, aumenta confianza
    // de los hechos que contribuyeron a ese análisis.
    
    "N2_to_N1":  {
      "relationship": "N2 modifies N1 confidence",
      "effect": "Edge weights adjust fact confidence scores",
      "data_flow": "confidence_backpropagation",
      "rationale": "PARTE V, Sec 5.1: N2 (PARAMETER) modifica pesos de N1 (FACT)"
    },

    // ─────────────────────────────────────────────────────────────────────────
    // N3 → N1: Veto Propagation (ASIMÉTRICO)
    // ─────────────────────────────────────────────────────────────────────────
    // N3 puede BLOQUEAR hechos de N1 si fallan validación.
    // 
    // ⚠️ ASIMETRÍA: N1 NO puede invalidar N3.
    // Si N3 dice "esto es contradictorio", el hecho de N1 SE SUPRIME.
    
    "N3_to_N1":  {
      "relationship": "N3 can BLOCK N1 facts",
      "effect": "Failed constraints remove facts from graph",
      "data_flow": "veto_propagation",
      "asymmetry": "N1 CANNOT invalidate N3",
      "rationale":  "PARTE V, Sec 5.1: Influencia asimétrica de N3 sobre N1"
    },

    // ─────────────────────────────────────────────────────────────────────────
    // N3 → N2: Inference Modulation (ASIMÉTRICO)
    // ─────────────────────────────────────────────────────────────────────────
    // N3 puede INVALIDAR inferencias de N2.
    // 
    // ⚠️ ASIMETRÍA: N2 NO puede invalidar N3.
    // Si N3 dice "la inferencia no es significativa", la inferencia SE ANULA.
    
    "N3_to_N2":  {
      "relationship": "N3 can INVALIDATE N2 parameters",
      "effect": "Failed constraints nullify parameter modifications",
      "data_flow": "inference_modulation",
      "asymmetry": "N2 CANNOT invalidate N3",
      "rationale": "PARTE V, Sec 5.1: Influencia asimétrica de N3 sobre N2"
    },

    // ─────────────────────────────────────────────────────────────────────────
    // ALL → N4: Terminal Aggregation
    // ─────────────────────────────────────────────────────────────────────────
    // N4 consume el grafo ya filtrado por N3.
    // Solo ve los hechos e inferencias que SOBREVIVIERON el veto gate.
    
    "all_to_N4": {
      "relationship": "N4 consumes validated outputs from all layers",
      "effect": "Synthesis constructs narrative from filtered graph",
      "data_flow": "terminal_aggregation",
      "rationale": "PARTE V, Sec 5.1: N4 es terminal, consume grafo validado"
    },

    // ─────────────────────────────────────────────────────────────────────────
    // BLOCKING_PROPAGATION_RULES
    // ─────────────────────────────────────────────────────────────────────────
    // GUÍA:  PARTE V, Sección 5.2
    // 
    // Define cómo se propaga un bloqueo cuando N3 detecta un problema.
    // ─────────────────────────────────────────────────────────────────────────

    "blocking_propagation_rules": {
      "statistical_significance_failed": {
        "triggered_by": "PolicyContradictionDetector._statistical_significance_test",
        "action": "block_branch",
        "scope": "source_facts",
        "propagation":  "downstream_only",
        "rationale": "PARTE V, Sec 5.2: Significancia fallida bloquea hechos fuente"
      },
      "logical_contradiction":  {
        "triggered_by": "PolicyContradictionDetector._detect_logical_incompatibilities",
        "action": "block_branch",
        "scope":  "contradicting_nodes",
        "propagation":  "both",
        "rationale": "PARTE V, Sec 5.2: Contradicción bloquea ambos lados"
      }
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: human_answer_structure
  // ═══════════════════════════════
Continúo el contrato D1-Q1 donde lo dejamos.

---

```jsonc
  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN:  human_answer_structure
  // ═══════════════════════════════════════════════════════════════════════════════
  // 
  // GUÍA APLICADA:  PARTE VI (Human Answer Structure)
  // 
  // Según PARTE VI, Sección 6. 1, la estructura debe incluir: 
  // - format:  "markdown"
  // - template_mode: "epistemological_narrative"
  // - contract_type: el tipo clasificado
  // - sections: 4 secciones obligatorias (S1-S4)
  // - argumentative_roles: roles por nivel
  // - confidence_interpretation: interpretación de scores
  //
  // PRINCIPIO CLAVE (de la taxonomía original):
  // "Para que la respuesta humana refleje esta profundidad sin abrumar"
  // 
  // La estructura NO es un dump de datos.  Es una NARRATIVA que articula
  // la procedencia epistemológica de cada afirmación.
  // ═══════════════════════════════════════════════════════════════════════════════

  "human_answer_structure":  {
    "format": "markdown",
    
    // ⬇️ Modo de template según PARTE VI, Sec 6.1
    "template_mode": "epistemological_narrative",
    
    "contract_type": "TYPE_A",

    // ─────────────────────────────────────────────────────────────────────────────
    // SECTIONS:  4 secciones obligatorias
    // ─────────────────────────────────────────────────────────────────────────────
    // 
    // GUÍA:  PARTE VI, Sección 6.2
    // 
    // La estructura dinámica propuesta en la taxonomía es:
    // 1. El Veredicto (Synthesis) - Conclusión directa
    // 2. La Evidencia Dura (Empirical - N1) - Hechos observables
    // 3. El Análisis de Robustez (Audit - N3) - Donde brilla el sistema
    // 4. Los Puntos Ciegos (Gaps) - Qué métodos devolvieron vacío
    //
    // NOTA CRÍTICA (cita textual de taxonomía):
    // "Aquí es donde brilla tu sistema: 'Sin embargo, el validador DAG detectó
    // inconsistencias cíclicas en la teoría de cambio, y el análisis de 
    // sensibilidad sugiere que el resultado es frágil ante cambios pequeños'"
    //
    // Es decir: S3 no es un adorno.  Es donde el falsacionismo popperiano
    // se manifiesta en la narrativa. 
    // ─────────────────────────────────────────────────────────────────────────────

    "sections": [
      // ═════════════════════════════════════════════════════════════════════════
      // S1: VEREDICTO (Synthesis)
      // ═════════════════════════════════════════════════════════════════════════
      // 
      // GUÍA: PARTE VI, Sección 6.2 - S1
      // 
      // Esta sección va PRIMERO porque el lector (funcionario público, 
      // evaluador de política) necesita la conclusión inmediatamente.
      // 
      // El veredicto es el OUTPUT de N4:  síntesis que integra todo. 
      // Pero incluye metadata de confianza y base metodológica para
      // que el lector sepa qué tan sólida es la conclusión. 
      // 
      // PRINCIPIO:  "La meta es viable/inviable con una confianza del X%"
      // No hay ambigüedad.  Hay declaración + incertidumbre cuantificada.
      // ═════════════════════════════════════════════════════════════════════════
      {
        "section_id": "S1_verdict",
        "title": "### Veredicto",
        "layer": "N4",
        "layer_name": "Síntesis",
        "data_source": "synthesis_output",
        "narrative_style": "declarative",
        
        // ⬇️ Template con placeholders que Carver poblará
        "template":  {
          "structure": [
            "**Conclusión**:  {verdict_statement}",
            "",
            "**Confianza Global**: {final_confidence_pct}% ({confidence_label})",
            "",
            "**Base Metodológica**:  {method_count} métodos ejecutados en 3 fases epistemológicas, {audit_count} validaciones de robustez, {blocked_count} ramas bloqueadas por inconsistencia."
          ],
          "placeholders": {
            "verdict_statement": {
              "type": "string",
              "source": "synthesis. verdict",
              "example": "El diagnóstico presenta datos numéricos suficientes para establecer línea base en el área de Derechos de las mujeres e igualdad de género"
            },
            "final_confidence_pct": {
              "type": "number",
              "source": "synthesis. confidence",
              "range": [0, 100]
            },
            "confidence_label":  {
              "type": "enum",
              "source": "confidence_interpretation",
              "values": ["INVÁLIDO", "DÉBIL", "MODERADO", "ROBUSTO"]
            },
            "method_count": {
              "type": "number",
              "source": "method_binding. method_count"
            },
            "audit_count":  {
              "type": "number",
              "source":  "phase_C_litigation.methods.length"
            },
            "blocked_count": {
              "type": "number",
              "source":  "audit_results.blocked_branches.length"
            }
          }
        },
        
        "argumentative_role": "SYNTHESIS",
        
        "rationale": "PARTE VI, Sec 6.2: S1 entrega conclusión directa con incertidumbre cuantificada"
      },

      // ═════════════════════════════════════════════════════════════════════════
      // S2: EVIDENCIA DURA (Empirical - N1)
      // ═════════════════════════════════════════════════════════════════════════
      // 
      // GUÍA: PARTE VI, Sección 6.2 - S2
      // 
      // Esta sección presenta los HECHOS OBSERVABLES de N1.
      // Son observaciones directas, no interpretaciones.
      // 
      // PRINCIPIO EPISTEMOLÓGICO (cita de taxonomía):
      // "Empirismo positivista - los datos existen independientemente del observador"
      // 
      // El lector debe poder verificar estas afirmaciones volviendo al
      // documento fuente.  Son LITERALES, no inferencias.
      // 
      // Para Q001 específicamente, los hechos relevantes son:
      // - Fuentes oficiales mencionadas (DANE, Medicina Legal, etc.)
      // - Indicadores cuantitativos encontrados (tasas, porcentajes)
      // - Cobertura temporal (años de referencia)
      // - Cobertura territorial (departamental, municipal, etc.)
      // ═════════════════════════════════════════════════════════════════════════
      {
        "section_id": "S2_empirical_base",
        "title": "### Base Empírica:  Hechos Observados",
        "layer": "N1",
        "layer_name": "Base Empírica",
        "data_source": "validated_facts",
        "narrative_style":  "descriptive",
        
        "template": {
          "structure": [
            "**Elementos Detectados**:  {fact_count} hechos extraídos de {document_coverage_pct}% del texto analizado.",
            "",
            "**Fuentes Oficiales Identificadas**:",
            "{official_sources_list}",
            "",
            "**Indicadores Cuantitativos**:",
            "{quantitative_indicators_list}",
            "",
            "**Cobertura Temporal**:  {temporal_coverage}",
            "",
            "**Cobertura Territorial**:  {territorial_coverage}"
          ],
          "placeholders": {
            "fact_count": {
              "type": "number",
              "source": "raw_facts.count",
              "description": "Total de hechos extraídos por métodos N1"
            },
            "document_coverage_pct":  {
              "type": "number",
              "source": "analysis_metadata.coverage_percentage",
              "description": "Porcentaje del documento procesado"
            },
            "official_sources_list": {
              "type":  "markdown_list",
              "source": "raw_facts.filter(type='official_source')",
              "format": "- {source_name} (mencionada {mention_count} veces)",
              "example": "- DANE (mencionada 3 veces)\n- Medicina Legal (mencionada 2 veces)"
            },
            "quantitative_indicators_list": {
              "type": "markdown_list",
              "source": "raw_facts.filter(type='quantitative_indicator')",
              "format": "- {indicator_value}:  {indicator_context}",
              "example": "- 45.3%: tasa de participación laboral femenina\n- 12 por 100.000: tasa de violencia intrafamiliar"
            },
            "temporal_coverage": {
              "type":  "string",
              "source": "raw_facts.temporal_range",
              "example": "Datos de 2019-2023 (5 años de serie temporal)"
            },
            "territorial_coverage": {
              "type": "string",
              "source": "raw_facts.territorial_scope",
              "example": "Cobertura departamental con desagregación urbano/rural"
            }
          }
        },
        
        "argumentative_role": "EMPIRICAL_BASIS",
        
        // ⬇️ Nota epistemológica que puede incluirse en la narrativa
        "epistemological_note":  {
          "include_in_output": true,
          "text": "📋 *Nota metodológica:  Estas son observaciones directas del documento fuente, sin transformación interpretativa.  El lector puede verificarlas en el texto original.*"
        },
        
        "rationale": "PARTE VI, Sec 6.2: S2 presenta hechos literales de N1 verificables en documento fuente"
      },

      // ═════════════════════════════════════════════════════════════════════════
      // S3: ANÁLISIS DE ROBUSTEZ (Audit - N3)
      // ═════════════════════════════════════════════════════════════════════════
      // 
      // GUÍA:  PARTE VI, Sección 6.2 - S3
      // 
      // ⚠️ ESTA ES LA SECCIÓN MÁS IMPORTANTE DEL FRAMEWORK ⚠️
      // 
      // Cita textual de la taxonomía:
      // "Aquí es donde brilla tu sistema.  'Sin embargo, el validador DAG
      // detectó inconsistencias cíclicas en la teoría de cambio, y el
      // análisis de sensibilidad sugiere que el resultado es frágil
      // ante cambios presupuestales pequeños. '"
      // 
      // Esta sección implementa FALSACIONISMO POPPERIANO en la narrativa: 
      // - ¿Qué intentamos refutar? 
      // - ¿Lo logramos?  (contradicciones detectadas)
      // - ¿Qué evidencia fue SUPRIMIDA por fallar validación?
      // - ¿Qué limitaciones metodológicas existen?
      // 
      // Si N3 detectó problemas, la respuesta NO es "evidencia mixta". 
      // La respuesta es declaración explícita de invalidez parcial o total.
      // 
      // PROPIEDAD CRÍTICA: veto_display
      // Si hay veto activo, se muestra alerta prominente.
      // ═════════════════════════════════════════════════════════════════════════
      {
        "section_id": "S3_robustness_audit",
        "title": "### Análisis de Robustez:  Validación y Limitaciones",
        "layer": "N3",
        "layer_name": "Auditoría y Robustez",
        "data_source":  "audit_results",
        "narrative_style": "critical",
        
        "template": {
          "structure": [
            "{veto_alert}",
            "",
            "**Validaciones Ejecutadas**:  {validation_count} pruebas de robustez",
            "",
            "**Contradicciones Detectadas**:  {contradiction_count}",
            "{contradiction_details}",
            "",
            "**Hechos Suprimidos**: {suppressed_count} observaciones eliminadas por inconsistencia",
            "{suppression_details}",
            "",
            "**Modulaciones de Confianza**:",
            "{confidence_adjustments}",
            "",
            "**Limitaciones Metodológicas**:",
            "{limitations_list}"
          ],
          "placeholders": {
            "veto_alert": {
              "type": "conditional",
              "condition": "audit_results.has_critical_veto",
              "if_true": "⛔ **ALERTA CRÍTICA**: {veto_reason}.  Los hallazgos de esta sección han sido INVALIDADOS por fallar validación de robustez.",
              "if_false":  "✅ Todas las validaciones críticas pasaron.",
              "source":  "audit_results. critical_veto"
            },
            "validation_count":  {
              "type": "number",
              "source": "audit_results.validations_executed"
            },
            "contradiction_count":  {
              "type": "number",
              "source": "audit_results.contradictions. length"
            },
            "contradiction_details": {
              "type": "markdown_list",
              "source": "audit_results.contradictions",
              "format":  "- ⚠️ {contradiction_type}: {description}\n  - Afecta:  {affected_facts}\n  - Acción: {action_taken}",
              "example": "- ⚠️ Inconsistencia numérica: El documento reporta 45% en página 3 y 12% en página 7 para el mismo indicador\n  - Afecta: indicador_participacion_laboral\n  - Acción:  Ambos valores suprimidos, confianza → 0%",
              "if_empty": "No se detectaron contradicciones."
            },
            "suppressed_count": {
              "type": "number",
              "source":  "audit_results. suppressed_facts.length"
            },
            "suppression_details": {
              "type":  "markdown_list",
              "source":  "audit_results. suppressed_facts",
              "format":  "- {fact_id}: {suppression_reason}",
              "if_empty": "Ningún hecho fue suprimido."
            },
            "confidence_adjustments": {
              "type": "markdown_list",
              "source": "audit_results.confidence_modulations",
              "format": "- {target}:  {original_confidence}% → {adjusted_confidence}% ({adjustment_reason})",
              "example": "- Indicadores cuantitativos:  85% → 60% (muestra pequeña, n=3)",
              "if_empty": "No hubo ajustes de confianza."
            },
            "limitations_list": {
              "type":  "markdown_list",
              "source":  "audit_results. methodological_limitations",
              "format": "- {limitation_type}: {description}",
              "example": "- Cobertura temporal limitada: Solo 2 años de datos disponibles (mínimo recomendado:  3)\n- Fuentes no diversificadas: 80% de indicadores provienen de una sola fuente"
            }
          }
        },
        
        "argumentative_role": "ROBUSTNESS_QUALIFIER",
        
        // ⬇️ Roles argumentativos específicos de N3
        // Según PARTE VI, Sec 6.3: N3 tiene múltiples roles
        "sub_roles": [
          {
            "role": "REFUTATIONAL_SIGNAL",
            "description": "Evidencia negativa que contradice",
            "narrative_weight": "critical",
            "example": "Meta A incompatible con Meta B"
          },
          {
            "role": "FINANCIAL_CONSTRAINT",
            "description": "Límites presupuestales a viabilidad",
            "narrative_weight":  "critical",
            "example": "Presupuesto insuficiente para meta"
          },
          {
            "role": "LOGICAL_INCONSISTENCY",
            "description": "Contradicción lógica interna",
            "narrative_weight": "critical",
            "example": "Secuencia de actividades inválida"
          }
        ],
        
        // ⬇️ VETO_DISPLAY:  Cómo mostrar cuando hay bloqueo
        // Esto es lo que diferencia este sistema de otros
        "veto_display":  {
          "prominence": "high",
          "styling": "alert_box",
          "if_veto_triggered": {
            "template": "⛔ **MODELO INVÁLIDO**: {veto_reason}.  Este hallazgo NO debe usarse para toma de decisiones.",
            "confidence_override": 0,
            "recommendation": "Revisar documento fuente y corregir inconsistencias antes de re-evaluar."
          },
          "if_partial_veto": {
            "template":  "⚠️ **ROBUSTEZ PARCIAL**: {partial_veto_count} de {total_findings} hallazgos fueron invalidados.  Usar con precaución.",
            "confidence_reduction": 0.5
          },
          "if_no_veto": {
            "template":  "✅ **VALIDACIÓN COMPLETA**:  Todos los hallazgos sobrevivieron las pruebas de refutación.",
            "confidence_boost": 1.1
          }
        },
        
        "epistemological_note":  {
          "include_in_output":  true,
          "text": "🔬 *Nota metodológica: Esta sección aplica falsacionismo popperiano.  Los métodos de auditoría intentaron activamente REFUTAR los hallazgos.  Lo que sobrevive este escrutinio es epistemológicamente más robusto.*"
        },
        
        "rationale": "PARTE VI, Sec 6.2: S3 es donde el falsacionismo se manifiesta.  N3 puede VETAR, no solo 'agregar evidencia'."
      },

      // ═════════════════════════════════════════════════════════════════════════
      // S4: PUNTOS CIEGOS (Gaps)
      // ═════════════════════════════════════════════════════════════════════════
      // 
      // GUÍA:  PARTE VI, Sección 6.2 - S4
      // 
      // Esta sección es METACOGNITIVA: analiza qué NO pudimos detectar.
      // 
      // PRINCIPIO EPISTEMOLÓGICO (cita de taxonomía):
      // "Reflexividad crítica - el sistema observa sus propias limitaciones"
      // 
      // Preguntas que responde:
      // - ¿Qué métodos de N1 devolvieron vacío?
      // - ¿Qué elementos esperados no se encontraron?
      // - ¿Qué porcentaje de cobertura logramos?
      // - ¿Cómo impactan estos gaps en la confianza final?
      // 
      // Esta sección es crucial para HONESTIDAD EPISTEMOLÓGICA.
      // Un sistema que solo reporta lo que encontró, sin reportar
      // lo que NO encontró, es epistemológicamente incompleto.
      // ═════════════════════════════════════════════════════════════════════════
      {
        "section_id": "S4_gaps",
        "title":  "### Puntos Ciegos:  Evidencia Faltante",
        "layer": "N4-META",
        "layer_name": "Meta-Análisis",
        "data_source": "gap_analysis",
        "narrative_style": "diagnostic",
        
        "template": {
          "structure": [
            "**Métodos sin Resultados**: {empty_methods_count} de {total_methods} métodos no produjeron hallazgos",
            "{empty_methods_details}",
            "",
            "**Elementos Esperados no Encontrados**:",
            "{missing_elements_list}",
            "",
            "**Cobertura de Validaciones**:",
            "- Patterns ejecutados: {patterns_executed}/{patterns_total} ({pattern_coverage_pct}%)",
            "- Fuentes esperadas vs encontradas: {sources_found}/{sources_expected}",
            "",
            "**Impacto en Confianza**:",
            "{gap_impact_assessment}"
          ],
          "placeholders": {
            "empty_methods_count": {
              "type":  "number",
              "source": "gap_analysis.empty_methods. length"
            },
            "total_methods": {
              "type": "number",
              "source": "method_binding.method_count"
            },
            "empty_methods_details": {
              "type": "markdown_list",
              "source": "gap_analysis.empty_methods",
              "format": "- `{method_name}`: {expected_output} → No encontrado",
              "example": "- `_extract_temporal_series`: Series temporales → No encontrado\n- `_parse_territorial_coverage`: Cobertura territorial → No encontrado",
              "if_empty":  "Todos los métodos produjeron resultados."
            },
            "missing_elements_list": {
              "type": "markdown_list",
              "source": "gap_analysis.missing_expected_elements",
              "format": "- {element_type}: {requirement} (requerido:  {is_mandatory})",
              "example": "- Series temporales: Mínimo 3 años (requerido: SÍ)\n- Desagregación por género: Datos separados M/F (requerido: NO)"
            },
            "patterns_executed":  {
              "type": "number",
              "source": "gap_analysis.patterns_matched"
            },
            "patterns_total":  {
              "type": "number",
              "source": "question_context.patterns. length"
            },
            "pattern_coverage_pct":  {
              "type": "number",
              "source": "gap_analysis.pattern_coverage_percentage"
            },
            "sources_found": {
              "type": "number",
              "source":  "gap_analysis. official_sources_found"
            },
            "sources_expected": {
              "type": "number",
              "source":  "question_context.expected_elements. filter(type='fuentes_oficiales').minimum"
            },
            "gap_impact_assessment": {
              "type": "string",
              "source": "gap_analysis.confidence_impact",
              "example": "Los gaps identificados reducen la confianza global en 15%.  El elemento crítico faltante es la serie temporal, lo cual limita la capacidad de establecer tendencias."
            }
          }
        },
        
        "argumentative_role": "META_TRACEABILITY",
        
        "epistemological_note":  {
          "include_in_output":  true,
          "text": "🔍 *Nota metodológica: Esta sección practica reflexividad crítica.  Reportamos no solo lo que encontramos, sino lo que NO encontramos y cómo eso afecta nuestras conclusiones.*"
        },
        
        "rationale": "PARTE VI, Sec 6.2: S4 implementa honestidad epistemológica reportando gaps"
      }
    ],

    // ─────────────────────────────────────────────────────────────────────────────
    // ARGUMENTATIVE_ROLES:  Roles por nivel
    // ─────────────────────────────────────────────────────────────────────────────
    // 
    // GUÍA: PARTE VI, Sección 6.3
    // 
    // Cada nivel epistemológico tiene roles argumentativos específicos. 
    // Estos roles determinan: 
    // - Cómo se presenta la información en la narrativa
    // - Qué peso tiene en la conclusión final
    // - Cómo se interpreta por el lector
    // 
    // TAXONOMÍA DE ROLES (de la guía original):
    // - EMPIRICAL_BASIS (N1): Hecho observable innegable
    // - INFERENTIAL_BRIDGE (N2): Conexión lógica derivada
    // - ROBUSTNESS_QUALIFIER (N3): Advertencia de calidad/limitación
    // - REFUTATIONAL_SIGNAL (N3): Evidencia negativa que contradice
    // - CONTEXTUAL_QUALIFIER (N2+N3): Condiciona validez a contexto
    // - FINANCIAL_CONSTRAINT (N3): Límites presupuestales
    // - LOGICAL_INCONSISTENCY (N3): Contradicción lógica
    // - META_TRACEABILITY (N4): Calidad del proceso analítico
    // ─────────────────────────────────────────────────────────────────────────────

    "argumentative_roles":  {
      "N1_roles": [
        {
          "role":  "EMPIRICAL_BASIS",
          "description": "Hecho observable innegable extraído del documento",
          "narrative_weight": "high",
          "verifiability": "El lector puede verificar en documento fuente",
          "example": "Se encontraron 15 menciones a VBG en el diagnóstico",
          "linguistic_markers": ["Se detectó", "El documento contiene", "Se identificaron"]
        }
      ],
      
      "N2_roles": [
        {
          "role": "INFERENTIAL_BRIDGE",
          "description":  "Conexión lógica derivada de observaciones",
          "narrative_weight": "medium",
          "verifiability": "Derivado de N1, requiere aceptar metodología",
          "example": "Con 95% de confianza, el prior se actualiza a favor de cumplimiento",
          "linguistic_markers":  ["El análisis sugiere", "Con X% de confianza", "Se infiere que"]
        },
        {
          "role": "CONTEXTUAL_QUALIFIER",
          "description":  "Condiciona validez de hallazgo a contexto específico",
          "narrative_weight": "medium",
          "verifiability": "Depende de supuestos contextuales",
          "example":  "Válido solo para zona rural del departamento",
          "linguistic_markers": ["En el contexto de", "Aplicable cuando", "Condicionado a"]
        }
      ],
      
      "N3_roles": [
        {
          "role": "ROBUSTNESS_QUALIFIER",
          "description": "Advertencia sobre calidad o limitación del hallazgo",
          "narrative_weight": "high",
          "verifiability": "Resultado de prueba de validación",
          "example": "La muestra es pequeña (n=5), lo cual limita generalización",
          "linguistic_markers": ["Sin embargo", "Limitación:", "Precaución: "]
        },
        {
          "role": "REFUTATIONAL_SIGNAL",
          "description": "Evidencia que contradice o invalida hallazgo previo",
          "narrative_weight": "critical",
          "verifiability": "Detectado por método de auditoría",
          "example": "Meta A es incompatible con Meta B según análisis de coherencia",
          "linguistic_markers": ["CONTRADICCIÓN:", "Invalidado por", "Incompatible con"],
          "triggers_veto": true
        },
        {
          "role": "FINANCIAL_CONSTRAINT",
          "description": "Límite presupuestal que afecta viabilidad",
          "narrative_weight": "critical",
          "verifiability": "Calculado por FinancialAuditor",
          "example": "Presupuesto asignado cubre solo 40% del requerido para la meta",
          "linguistic_markers": ["Insuficiencia:", "Gap presupuestal:", "Déficit de"]
        },
        {
          "role": "LOGICAL_INCONSISTENCY",
          "description": "Contradicción en secuencia lógica o estructura",
          "narrative_weight": "critical",
          "verifiability": "Detectado por validador lógico",
          "example": "Actividad B depende de Actividad C, pero C está programada después de B",
          "linguistic_markers":  ["Inconsistencia lógica:", "Secuencia inválida:", "Ciclo detectado: "],
          "triggers_veto": true
        }
      ],
      
      "N4_roles": [
        {
          "role": "META_TRACEABILITY",
          "description":  "Información sobre calidad del proceso analítico mismo",
          "narrative_weight": "medium",
          "verifiability": "Metadata del sistema",
          "example":  "95% de cobertura de patterns, 17 métodos ejecutados",
          "linguistic_markers": ["Metodológicamente", "El análisis cubrió", "Se ejecutaron"]
        }
      ]
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // CONFIDENCE_INTERPRETATION: Interpretación de scores
    // ─────────────────────────────────────────────────────────────────────────────
    // 
    // GUÍA:  PARTE VI, Sección 6.4
    // 
    // Define 4 rangos de confianza con: 
    // - Etiqueta verbal
    // - Descripción de qué significa
    // - Indicador visual
    // 
    // PRINCIPIO:  El lector no técnico debe entender inmediatamente
    // qué tan confiable es la conclusión.
    // ─────────────────────────────────────────────────────────────────────────────

    "confidence_interpretation": {
      "critical": {
        "range": [0, 19],
        "label": "INVÁLIDO",
        "description": "Veto activado por N3. El modelo lógico o evidencial es técnicamente inválido.  NO usar para toma de decisiones.",
        "display":  "🔴",
        "color_code": "#DC3545",
        "action_required": "Revisar documento fuente y corregir inconsistencias críticas antes de re-evaluar.",
        "triggers":  ["critical_veto", "cycle_detected", "fundamental_contradiction"]
      },
      
      "low": {
        "range": [20, 49],
        "label": "DÉBIL",
        "description": "Evidencia insuficiente, contradicciones menores detectadas, o validación parcialmente fallida.  Usar con extrema precaución.",
        "display":  "🟠",
        "color_code": "#FD7E14",
        "action_required": "Complementar con fuentes adicionales antes de tomar decisiones.",
        "triggers": ["insufficient_sources", "partial_validation_failure", "high_gap_count"]
      },
      
      "medium": {
        "range": [50, 79],
        "label": "MODERADO",
        "description": "Evidencia presente con limitaciones o inconsistencias menores. Apropiado para decisiones preliminares, no definitivas.",
        "display": "🟡",
        "color_code": "#FFC107",
        "action_required": "Considerar limitaciones documentadas en S3 y S4 al interpretar.",
        "triggers":  ["minor_inconsistencies", "partial_coverage", "some_methods_empty"]
      },
      
      "high": {
        "range": [80, 100],
        "label": "ROBUSTO",
        "description": "Múltiples observaciones corroborantes, sin contradicciones, todas las auditorías pasadas. Apropiado para toma de decisiones.",
        "display":  "🟢",
        "color_code": "#28A745",
        "action_required": "Ninguna.  Hallazgos listos para uso en política pública.",
        "triggers": ["full_corroboration", "all_validations_passed", "high_coverage"]
      }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // NARRATIVE_GENERATION_RULES: Reglas para Carver
    // ─────────────────────────────────────────────────────────────────────────────
    // 
    // Estas reglas guían a DoctoralCarverSynthesizer en cómo construir
    // la narrativa final.
    // ─────────────────────────────────────────────────────────────────────────────

    "narrative_generation_rules": {
      "ordering": {
        "description": "Orden de secciones en output final",
        "sequence": ["S1_verdict", "S2_empirical_base", "S3_robustness_audit", "S4_gaps"],
        "rationale": "Veredicto primero (el lector quiere conclusión), luego evidencia, luego robustez, luego gaps"
      },
      
      "length_constraints": {
        "S1_verdict": {"max_words": 150, "style":  "concise"},
        "S2_empirical_base": {"max_words": 400, "style": "comprehensive"},
        "S3_robustness_audit": {"max_words": 500, "style": "detailed_critical"},
        "S4_gaps": {"max_words": 300, "style": "diagnostic"}
      },
      
      "conditional_inclusion": {
        "if_veto_triggered": {
          "emphasize":  ["S3_robustness_audit"],
          "de_emphasize": ["S2_empirical_base"],
          "rationale": "Si hay veto, la robustez es más importante que la evidencia (que fue invalidada)"
        },
        "if_high_confidence": {
          "emphasize": ["S2_empirical_base", "S1_verdict"],
          "de_emphasize": ["S4_gaps"],
          "rationale": "Si confianza alta, enfocarse en evidencia sólida"
        },
        "if_many_gaps": {
          "emphasize": ["S4_gaps"],
          "add_warning": "⚠️ Cobertura analítica limitada.  Interpretar con cautela.",
          "rationale": "Muchos gaps requieren transparencia adicional"
        }
      },
      
      "linguistic_consistency": {
        "avoid":  ["probablemente", "quizás", "tal vez", "parece que"],
        "prefer": ["con X% de confianza", "la evidencia indica", "el análisis muestra"],
        "rationale": "Evitar hedging. Cuantificar incertidumbre en vez de usar lenguaje vago."
      }
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN:  output_contract
  // ═══════════════════════════════════════════════════════════════════════════════
  // No modificada extensivamente por la guía.  Se preserva schema de v3
  // con adición de campos epistemológicos. 
  
  "output_contract": {
    "result_type": "Phase2QuestionResult",
    "schema":  {
      "type": "object",
      "required": ["base_slot", "question_id", "evidence", "score", "human_answer"],
      "properties": {
        "base_slot": {"type": "string", "const": "D1-Q1"},
        "question_id": {"type":  "string"},
        "dimension_id": {"type": "string"},
        "policy_area_id": {"type":  "string"},
        "score": {"type": "number", "minimum":  0, "maximum": 1},
        "confidence_label": {"type": "string", "enum":  ["INVÁLIDO", "DÉBIL", "MODERADO", "ROBUSTO"]},
        "evidence":  {"type": "object"},
        "human_answer": {"type":  "string"},
        "epistemological_trace": {
          "type":  "object",
          "properties": {
            "n1_facts_count": {"type": "number"},
            "n2_inferences_count": {"type": "number"},
            "n3_validations_count": {"type": "number"},
            "veto_triggered": {"type": "boolean"},
            "blocked_branches": {"type": "array"}
          }
        },
        "validation":  {"type": "object"},
        "metadata": {"type": "object"}
      }
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN:  validation_rules
  // ═══════════════════════════════════════════════════════════════════════════════
  // No modificada por la guía. 
  
  "validation_rules": {
    "na_policy":  "abort_on_critical",
    "derivation_source": "expected_elements",
    "engine":  "VALIDATION_ENGINE",
    "module": "farfan_pipeline. phases.Phase_two. evidence_nexus",
    "class_name": "ValidationEngine",
    "method_name": "validate"
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: error_handling
  // ═══════════════════════════════════════════════════════════════════════════════
  // No modificada por la guía.
  
  "error_handling": {
    "on_method_not_found": "raise",
    "on_method_failure": "propagate_with_trace",
    "on_assembly_failure": "propagate_with_trace",
    "failure_contract": {
      "abort_if":  ["missing_required_element", "incomplete_text"],
      "emit_code": "ABORT-D1-Q1-REQ"
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: traceability
  // ═══════════════════════════════════════════════════════════════════════════════
  // Actualizada con historial de refactoring epistemológico. 
  
  "traceability": {
    "canonical_sources": {
      "questionnaire":  "canonic_questionnaire_central/questionnaire_monolith.json",
      "method_inventory": "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/canonical_methods_triangulated.json",
      "method_classification": "method_classification_all_30. json",
      "epistemological_guide": "guia_diligenciamiento_contratos_v4.md",
      "taxonomies": "taxonomias_epistemologicas_farfan.md"
    },
    "generation":  {
      "method":  "v4_epistemological_generation",
      "timestamp": "2025-12-22T00:00:00Z",
      "generator_version": "1.0.0"
    },
    "refactoring_history": [
      {
        "from_version": "3.0.0",
        "to_version": "4.0.0-epistemological",
        "date": "2025-12-22T00:00:00Z",
        "rationale": "Implementación de arquitectura epistemológica estratificada con falsacionismo popperiano",
        "changes":  [
          "Reemplazo de 'methods' plano por 'execution_phases' (A/B/C)",
          "Clasificación de métodos por nivel epistemológico (N1/N2/N3/N4)",
          "Tipificación de outputs (FACT/PARAMETER/CONSTRAINT/NARRATIVE)",
          "Implementación de veto_gate asimétrico para N3",
          "Reestructuración de assembly_rules en 4 reglas tipadas",
          "Adición de fusion_specification con estrategias por nivel",
          "Implementación de cross_layer_fusion con asimetría explícita",
          "Reestructuración de human_answer_structure en 4 secciones epistemológicas",
          "Adición de argumentative_roles por nivel",
          "Implementación de veto_display para comunicar invalidaciones"
        ],
        "epistemological_framework": {
          "N1":  "Empirismo positivista",
          "N2": "Bayesianismo subjetivista",
          "N3": "Falsacionismo popperiano",
          "N4": "Reflexividad crítica"
        }
      }
    ],
    "prohibitions": {
      "v3_recovery": "FORBIDDEN",
      "v3_migration": "FORBIDDEN",
      "v3_reference": "FORBIDDEN"
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: compatibility
  // ═══════════════════════════════════════════════════════════════════════════════
  
  "compatibility": {
    "questionnaire_monolith_version": "3.0.0",
    "version_detection": "runtime",
    "minimum_requirements": {
      "signal_registry": "MicroAnsweringSignalPack support",
      "hydrator":  "ContractHydrator v1.0.0",
      "carver": "DoctoralCarverSynthesizer v3.0.0",
      "evidence_nexus": "EvidenceNexus v2.0.0 (with typed fusion support)"
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // SECCIÓN: calibration
  // ═══════════════════════════════════════════════════════════════════════════════
  
  "calibration": {
    "status": "runtime",
    "sources": {
      "intrinsic_calibration": "config/intrinsic_calibration.json",
      "fusion_specification": "config/fusion_specification.json"
    }
  }
}
```

---

## RESUMEN DEL CONTRATO D1-Q1 v4

| Aspecto | Valor |
|---------|-------|
| **Tipo de Contrato** | TYPE_A (Semántico) |
| **Métodos Totales** | 17 |
| **Métodos N1 (Empíricos)** | 9 |
| **Métodos N2 (Inferenciales)** | 7 |
| **Métodos N3 (Auditoría)** | 1 |
| **Estrategia N1** | semantic_corroboration |
| **Estrategia N2** | dempster_shafer |
| **Estrategia N3** | veto_gate (asimétrico) |
| **Secciones de Respuesta** | 4 (Veredicto, Evidencia, Robustez, Gaps) |
| **Framework Epistemológico** | Falsacionismo popperiano implementado en N3 |

---

## CHECKLIST DE VALIDACIÓN (PARTE VII de la guía)

| Item | Status |
|------|--------|
| `method_binding.contract_type` coincide con clasificación | ✅ TYPE_A |
| Todos los métodos en exactamente UNA fase | ✅ 9+7+1=17 |
| Cada método tiene level, output_type, fusion_behavior | ✅ |
| Métodos N3 tienen veto_conditions | ✅ |
| Dependencias respetan jerarquía N1→N2→N3→N4 | ✅ |
| assembly_rules contiene 4 reglas (R1-R4) | ✅ |
| sources cubren todos los provides | ✅ |
| merge_strategy coincide con tipo (semantic_triangulation) | ✅ |
| R3 tiene gate_logic con condiciones de veto | ✅ |
| fusion_specification define estrategia por nivel | ✅ |
| cross_layer_fusion define todas las relaciones | ✅ |
| Asimetría N3 explícitamente declarada | ✅ |
| human_answer_structure tiene 4 secciones (S1-S4) | ✅ |
| S3 tiene veto_display | ✅ |
| argumentative_roles cubren todos los niveles | ✅ |
| confidence_interpretation tiene 4 rangos | ✅ |

---

ANEXO DE TAXONOMÍAS


TAXONOMÍAS EPISTEMOLÓGICAS COMPLETAS - F.A.R.F.A.N

1. TAXONOMÍA EPISTEMOLÓGICA DE MÉTODOS (Función Cognitiva)
NIVEL 0: Infraestructura Metodológica
Función: Soporte técnico sin juicio analítico. Epistemología: Instrumentalismo puro - herramientas sin carga teórica.
Clase	Métodos	Rol
ConfigLoader	load, validate	Carga configuración
PDETMunicipalPlanAnalyzer	_get_spanish_stopwords, _deduplicate_tables, _indicator_to_dict	Normalización
AdaptivePriorCalculator	generate_traceability_record	Logging
NIVEL 1: Base Empírica (Detection & Extraction)
Función: Extraer hechos brutos sin emitir juicios de valor. Epistemología: Empirismo positivista - los datos existen independientemente del observador.
Clase	Métodos Clave	Paradigma
TextMiningEngine	diagnose_critical_links, _analyze_link_text	Minería textual crítica
IndustrialPolicyProcessor	process, _extract_point_evidence, _match_patterns	Pattern matching industrial
CausalExtractor	_extract_goals, _parse_goal_context, _calculate_language_specificity	Análisis del discurso causal
PDETMunicipalPlanAnalyzer	_extract_financial_amounts, _extract_from_budget_table	Extracción estructurada
SemanticProcessor	chunk_text, embed_single, _detect_pdm_structure	Preprocesamiento semántico
SemanticAnalyzer	analyze_coherence, extract_themes	Análisis temático
NIVEL 2: Procesamiento Inferencial (Computation & Synthesis)
Función: Transformar datos en conocimiento probabilístico. Epistemología: Bayesianismo subjetivista - creencias actualizables por evidencia.
Clase	Métodos Clave	Paradigma
BayesianNumericalAnalyzer	evaluate_policy_metric, compare_policies	Comparación bayesiana de políticas
AdaptivePriorCalculator	calculate_likelihood_adaptativo, _adjust_domain_weights, sensitivity_analysis	Priors adaptativos contextuales
HierarchicalGenerativeModel	verify_conditional_independence, _generate_independence_tests, calculate_r_hat	Modelos jerárquicos generativos
BayesFactorTable	get_bayes_factor	Cuantificación de evidencia relativa
BayesianMechanismInference	aggregate_confidence, _test_sufficiency, _test_necessity, _calculate_coherence_factor	Inferencia mecanística
TeoriaCambio	_encontrar_caminos_completos, validacion_completa, _extraer_categorias, _generar_sugerencias	Reconstrucción de teorías de cambio
NIVEL 3: Auditoría y Robustez (Refutation & Control)
Función: Cuestionar, validar o refutar hallazgos. Actúan como "Veto Gates". Epistemología: Falsacionismo popperiano - el conocimiento se fortalece por intentos de refutación.
Clase	Métodos Clave	Paradigma
PolicyContradictionDetector	_detect_logical_incompatibilities, _calculate_coherence_metrics, _statistical_significance_test	Detección de inconsistencias lógicas
FinancialAuditor	_parse_amount, _calculate_sufficiency	Validación de viabilidad financiera
IndustrialGradeValidator	execute_suite, validate_connection_matrix	Validación industrial rigurosa
AdvancedDAGValidator	_calculate_bayesian_posterior, _calculate_confidence_interval, is_acyclic, _perform_sensitivity_analysis	Validación de grafos causales
BayesianCounterfactualAuditor	construct_scm	Auditoría contrafactual
OperationalizationAuditor	audit_sequence_logic	Validación de secuencias lógicas
TemporalLogicVerifier	verify_temporal_consistency	Verificación de coherencia temporal
NIVEL 4: Meta-Análisis (Identificación de Fallas)
Función: Analizar el propio proceso analítico y detectar puntos de quiebre. Epistemología: Reflexividad crítica - el sistema observa sus propias limitaciones.
Clase	Métodos Clave	Paradigma
CausalInferenceSetup	identify_failure_points, _get_dynamics_pattern	Detección de vulnerabilidades causales
PerformanceAnalyzer	analyze_performance, loss_functions	Evaluación del rendimiento analítico
2. TIPOLOGÍA DE CONTRATOS (Clusters Funcionales)
TIPO A: Semánticos (Text-Heavy) - 6.7%
Contratos: Q001, Q013 Foco: Coherencia narrativa, alineación temática, NLP. Clases Dominantes: SemanticAnalyzer, TextMiningEngine, SemanticProcessor Estrategia de Fusión: Triangulación semántica

TIPO B: Bayesianos (Probabilistic) - 40.0%
Contratos: Q002, Q005, Q007, Q011, Q017, Q018, Q020, Q023, Q024, Q025, Q027, Q029 Foco: Significancia estadística, intervalos de confianza, priors. Clases Dominantes: BayesianMechanismInference, HierarchicalGenerativeModel, AdaptivePriorCalculator Estrategia de Fusión: Actualización bayesiana de creencias

TIPO C: Causales (Graph-Native) - 13.3%
Contratos: Q008, Q016, Q026, Q030 Foco: Topología de grafos, cadenas causales, DAGs. Clases Dominantes: CausalExtractor, TeoriaCambio, AdvancedDAGValidator Estrategia de Fusión: Superposición topológica

TIPO D: Financieros (Finance-Heavy) - 26.7%
Contratos: Q003, Q004, Q006, Q009, Q012, Q015, Q021, Q022 Foco: Suficiencia presupuestal, coherencia costo-meta. Clases Dominantes: FinancialAuditor, PDETMunicipalPlanAnalyzer Estrategia de Fusión: Consistencia contable

TIPO E: Lógicos (Logic-Heavy) - 13.3%
Contratos: Q010, Q014, Q019, Q028 Foco: Complementariedad, secuencia lógica, detección de contradicciones. Clases Dominantes: PolicyContradictionDetector, IndustrialGradeValidator, OperationalizationAuditor Estrategia de Fusión: Validación de consistencia lógica

SUBTIPO F: Detección de Fallas - 6.7%
Contratos: Q005, Q030 Foco: Puntos de falla, restricciones, riesgos estructurales. Clases: CausalInferenceSetup Estrategia de Fusión: Mapeo de vulnerabilidades

3. TAXONOMÍA DE ESTRATEGIAS DE FUSIÓN
Estrategia	Nivel	Función	Uso
concat	1	Concatenar evidencia de múltiples fuentes	74.8%
weighted_mean	2	Promediar confianza con pesos	24.9%
semantic_corroboration	1	Fusionar nodos si dicen lo mismo → mayor peso	Tipo A
bayesian_update	2	Prior + Likelihood → Posterior	Tipo B
topological_overlay	1+3	Fusionar grafos detectando ciclos	Tipo C
financial_coherence_audit	3	Validar coherencia presupuestal	Tipo D
veto_gate	3	Si auditoría falla → bloquear rama de evidencia	Todos
confidence_modulation	3	Penalizar score si auditoría débil (×0.5)	Todos
graph_construction	1	Construir grafo de evidencia	Q001
edge_inference	2	Inferir relaciones entre nodos	Q001
dempster_shafer	2	Propagación de creencia combinatoria	Q001
carver_doctoral_synthesis	4	Síntesis narrativa PhD-style	Q001
4. TAXONOMÍA DE ROLES ARGUMENTATIVOS
Rol	Nivel Origen	Función en Narrativa	Ejemplo
EMPIRICAL_BASIS	1	Hecho observable innegable	"Se encontraron 15 menciones a VBG"
INFERENTIAL_BRIDGE	2	Conexión lógica derivada	"Con 95% confianza, el prior se actualiza"
ROBUSTNESS_QUALIFIER	3	Advertencia de calidad/limitación	"La muestra es pequeña (n=5)"
REFUTATIONAL_SIGNAL	3	Evidencia negativa que contradice	"Meta A incompatible con Meta B"
CONTEXTUAL_QUALIFIER	2+3	Condiciona validez a contexto	"Válido solo en zona rural"
FINANCIAL_CONSTRAINT	3	Límites presupuestales a viabilidad	"Presupuesto insuficiente para meta"
LOGICAL_INCONSISTENCY	3	Contradicción lógica interna	"Secuencia de actividades inválida"
META_TRACEABILITY	4	Calidad del proceso analítico	"95% cobertura de patterns"
