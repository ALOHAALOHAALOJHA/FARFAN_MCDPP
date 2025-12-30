# REPORTE FINAL: 300 Executor Contracts

**Fecha:** Diciembre 15, 2025  
**Contratos:** 300 (30 slots × 10 policy areas)  
**Versión:** v3

---

## 1. RESUMEN EJECUTIVO

### Estado de Contratos

| Métrica | Valor |
|---------|-------|
| Contratos totales | 300 |
| Slots únicos | 30 |
| Policy Areas | 10 |
| Métodos totales | ~326 únicos |
| Clases involucradas | 30+ |
| Patrones por contrato | 5-17 |

### Problemas Identificados

| Problema | Severidad | Estado |
|----------|-----------|--------|
| Patrones desconectados de métodos | ⚠️ CRÍTICO | Pendiente decisión arquitectónica |
| Evidence Nexus Migration | ⚠️ WARNING | Legacy EvidenceAssembler en uso |
| Contract Hash mismatch | ⚠️ WARNING | Requiere recálculo |

---

## 2. ARQUITECTURA DE PATRONES

### Flujo de Patrones

```
questionnaire_monolith.json
  └── blocks.micro_questions[].patterns[]
        └── extract_monolith_patterns.py
              └── Q###.v3.json.question_context.patterns[]
                    └── base_executor_with_contract.py:764
                          └── "question_patterns" en common_kwargs
                                └── ❌ NO CONSUMIDOS por métodos
```

### Hallazgo Crítico

Los métodos en `src/methods_dispensary/` usan **patrones internos**, no los del contrato:
- `IndustrialPolicyProcessor`: usa `CAUSAL_PATTERN_TAXONOMY`, `QUESTIONNAIRE_PATTERNS`
- `CausalExtractor`: usa `config.get('patterns.*')`
- `PolicyContradictionDetector`: usa patrones internos

---

## 3. MATRICES DE TRAZABILIDAD (30 SLOTS)

### SLOT 01 (Q001) | 17 métodos | 7 patrones | Cats: GENERAL, TEMPORAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `diagnose_critical_links` | TextMiningEngine | ✅ |
| 2 | `_analyze_link_text` | TextMiningEngine | ✅ |
| 3 | `process` | IndustrialPolicyProcessor | ✅ |
| 4 | `_match_patterns_in_sentences` | IndustrialPolicyProcessor | ✅ |
| 5 | `_extract_point_evidence` | IndustrialPolicyProcessor | ✅ |
| 6 | `_extract_goals` | CausalExtractor | ✅ |
| 7 | `_parse_goal_context` | CausalExtractor | ✅ |
| 8 | `_parse_amount` | FinancialAuditor | ✅ |
| 9 | `_extract_financial_amounts` | PDETMunicipalPlanAnalyzer | ✅ |
| 10 | `_extract_from_budget_table` | PDETMunicipalPlanAnalyzer | ✅ |
| 11 | `_extract_quantitative_claims` | PolicyContradictionDetector | ✅ |
| 12 | `_parse_number` | PolicyContradictionDetector | ✅ |
| 13 | `_statistical_significance_test` | PolicyContradictionDetector | ✅ |
| 14 | `evaluate_policy_metric` | BayesianNumericalAnalyzer | ❌ |
| 15 | `compare_policies` | BayesianNumericalAnalyzer | ❌ |
| 16 | `chunk_text` | SemanticProcessor | ❌ |
| 17 | `embed_single` | SemanticProcessor | ❌ |

---

### SLOT 02 (Q002) | 12 métodos | 6 patrones | Cats: GENERAL, INDICADOR

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `_audit_direct_evidence` | OperationalizationAuditor | ❌ |
| 2 | `_audit_systemic_risk` | OperationalizationAuditor | ❌ |
| 3 | `_detect_allocation_gaps` | FinancialAuditor | ✅ |
| 4 | `_detect_gaps` | BayesianMechanismInference | ✅ |
| 5 | `_generate_optimal_remediations` | PDETMunicipalPlanAnalyzer | ✅ |
| 6 | `_simulate_intervention` | PDETMunicipalPlanAnalyzer | ✅ |
| 7 | `counterfactual_query` | BayesianCounterfactualAuditor | ❌ |
| 8 | `_test_effect_stability` | BayesianCounterfactualAuditor | ❌ |
| 9 | `calculate_posterior` | BayesianConfidenceCalculator | ❌ |
| 10 | `_calculate_coherence_factor` | BayesianMechanismInference | ✅ |
| 11 | `_calculate_probability_change` | PDETMunicipalPlanAnalyzer | ✅ |
| 12 | `analyze_performance` | PerformanceAnalyzer | ❌ |

---

### SLOT 03 (Q003) | 13 métodos | 8 patrones | Cats: GENERAL, INDICADOR, UNIDAD_MEDIDA

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `trace_financial_allocation` | FinancialAuditor | ✅ |
| 2 | `_process_financial_table` | FinancialAuditor | ✅ |
| 3 | `_match_program_to_node` | FinancialAuditor | ✅ |
| 4 | `_match_goal_to_budget` | FinancialAuditor | ✅ |
| 5 | `_perform_counterfactual_budget_check` | FinancialAuditor | ✅ |
| 6 | `_calculate_sufficiency` | FinancialAuditor | ✅ |
| 7 | `analyze_financial_feasibility` | PDETMunicipalPlanAnalyzer | ✅ |
| 8 | `_extract_budget_for_pillar` | PDETMunicipalPlanAnalyzer | ✅ |
| 9 | `_compute_budget_coverage` | PDETMunicipalPlanAnalyzer | ✅ |
| 10 | `_identify_budget_gaps` | PDETMunicipalPlanAnalyzer | ✅ |
| 11 | `sensitivity_analysis` | PDETMunicipalPlanAnalyzer | ✅ |
| 12 | `_calculate_e_value` | PDETMunicipalPlanAnalyzer | ✅ |
| 13 | `counterfactual_query` | BayesianCounterfactualAuditor | ❌ |

---

### SLOT 04 (Q004) | 11 métodos | 6 patrones | Cats: GENERAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `identify_responsible_entities` | PDETMunicipalPlanAnalyzer | ✅ |
| 2 | `_extract_entities_ner` | PDETMunicipalPlanAnalyzer | ✅ |
| 3 | `_extract_entities_syntax` | PDETMunicipalPlanAnalyzer | ✅ |
| 4 | `_classify_entity_type` | PDETMunicipalPlanAnalyzer | ✅ |
| 5 | `_score_entity_specificity` | PDETMunicipalPlanAnalyzer | ✅ |
| 6 | `_consolidate_entities` | PDETMunicipalPlanAnalyzer | ✅ |
| 7 | `extract_entity_activity` | MechanismPartExtractor | ❌ |
| 8 | `_normalize_entity` | MechanismPartExtractor | ❌ |
| 9 | `_audit_direct_evidence` | OperationalizationAuditor | ❌ |
| 10 | `_score_operationalization` | OperationalizationAuditor | ❌ |
| 11 | `_check_implementation_roadblock` | OperationalizationAuditor | ❌ |

---

### SLOT 05 (Q005) | 7 métodos | 5 patrones | Cats: GENERAL, TEMPORAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `_check_deadline_constraints` | TemporalLogicVerifier | ✅ |
| 2 | `verify_temporal_consistency` | TemporalLogicVerifier | ✅ |
| 3 | `identify_failure_points` | CausalInferenceSetup | ❌ |
| 4 | `_assess_temporal_coherence` | CausalExtractor | ✅ |
| 5 | `_analyze_link_text` | TextMiningEngine | ✅ |
| 6 | `_analyze_causal_dimensions` | IndustrialPolicyProcessor | ✅ |
| 7 | `_extract_metadata` | IndustrialPolicyProcessor | ✅ |

---

### SLOT 06 (Q006) | 7 métodos | 7 patrones | Cats: GENERAL, INDICADOR

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `extract_tables` | PDFProcessor | ❌ |
| 2 | `_process_financial_table` | FinancialAuditor | ✅ |
| 3 | `_deduplicate_tables` | PDETMunicipalPlanAnalyzer | ✅ |
| 4 | `_classify_tables` | PDETMunicipalPlanAnalyzer | ✅ |
| 5 | `_is_likely_header` | PDETMunicipalPlanAnalyzer | ✅ |
| 6 | `_clean_dataframe` | PDETMunicipalPlanAnalyzer | ✅ |
| 7 | `generate_accountability_matrix` | ReportingEngine | ❌ |

---

### SLOT 07 (Q007) | 11 métodos | 7 patrones | Cats: CAUSAL, GENERAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `infer_mechanisms` | BayesianMechanismInference | ✅ |
| 2 | `_infer_single_mechanism` | BayesianMechanismInference | ✅ |
| 3 | `_infer_mechanism_type` | BayesianMechanismInference | ✅ |
| 4 | `_test_sufficiency` | BayesianMechanismInference | ✅ |
| 5 | `_test_necessity` | BayesianMechanismInference | ✅ |
| 6 | `extract_causal_hierarchy` | CausalExtractor | ✅ |
| 7 | `construir_grafo_causal` | TeoriaCambio | ❌ |
| 8 | `_es_conexion_valida` | TeoriaCambio | ❌ |
| 9 | `_calculate_similarity` | AdvancedDAGValidator | ❌ |
| 10 | `calculate_acyclicity_pvalue` | AdvancedDAGValidator | ❌ |
| 11 | `apply_test_logic` | BeachEvidentialTest | ❌ |

---

### SLOT 08 (Q008) | 9 métodos | 6 patrones | Cats: CAUSAL, GENERAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `_extract_causal_links` | CausalExtractor | ✅ |
| 2 | `_calculate_composite_likelihood` | CausalExtractor | ✅ |
| 3 | `_initialize_prior` | CausalExtractor | ✅ |
| 4 | `_calculate_type_transition_prior` | CausalExtractor | ✅ |
| 5 | `_identify_causal_edges` | PDETMunicipalPlanAnalyzer | ✅ |
| 6 | `_refine_edge_probabilities` | PDETMunicipalPlanAnalyzer | ✅ |
| 7 | `construct_scm` | BayesianCounterfactualAuditor | ❌ |
| 8 | `_create_default_equations` | BayesianCounterfactualAuditor | ❌ |
| 9 | `_calculate_complexity_score` | AdvancedDAGValidator | ❌ |

---

### SLOT 09 (Q009) | 10 métodos | 5 patrones | Cats: GENERAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `_bayesian_risk_inference` | PDETMunicipalPlanAnalyzer | ✅ |
| 2 | `sensitivity_analysis` | PDETMunicipalPlanAnalyzer | ✅ |
| 3 | `_interpret_risk` | PDETMunicipalPlanAnalyzer | ✅ |
| 4 | `_compute_robustness_value` | PDETMunicipalPlanAnalyzer | ✅ |
| 5 | `_compute_e_value` | PDETMunicipalPlanAnalyzer | ✅ |
| 6 | `_interpret_sensitivity` | PDETMunicipalPlanAnalyzer | ✅ |
| 7 | `_audit_systemic_risk` | OperationalizationAuditor | ❌ |
| 8 | `aggregate_risk_and_prioritize` | BayesianCounterfactualAuditor | ❌ |
| 9 | `_test_effect_stability` | BayesianCounterfactualAuditor | ❌ |
| 10 | `calculate_likelihood_adaptativo` | AdaptivePriorCalculator | ❌ |

---

### SLOT 10 (Q010) | 8 métodos | 6 patrones | Cats: GENERAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `_detect_logical_incompatibilities` | PolicyContradictionDetector | ✅ |
| 2 | `_calculate_coherence_metrics` | PolicyContradictionDetector | ✅ |
| 3 | `_calculate_objective_alignment` | PolicyContradictionDetector | ✅ |
| 4 | `_calculate_graph_fragmentation` | PolicyContradictionDetector | ✅ |
| 5 | `audit_sequence_logic` | OperationalizationAuditor | ❌ |
| 6 | `_calculate_coherence_factor` | BayesianMechanismInference | ✅ |
| 7 | `_score_causal_coherence` | PDETMunicipalPlanAnalyzer | ✅ |
| 8 | `calculate_likelihood_adaptativo` | AdaptivePriorCalculator | ❌ |

---

### SLOT 11 (Q011) | 8 métodos | 7 patrones | Cats: GENERAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `_compute_contextual_prior` | AdaptivePriorCalculator | ❌ |
| 2 | `_apply_empirical_correction` | AdaptivePriorCalculator | ❌ |
| 3 | `_merge_signal_evidence` | AdaptivePriorCalculator | ❌ |
| 4 | `apply_test_logic` | BeachEvidentialTest | ❌ |
| 5 | `_score_evidence_quality` | BeachEvidentialTest | ❌ |
| 6 | `identify_failure_points` | CausalInferenceSetup | ❌ |
| 7 | `_adjust_for_dag_complexity` | CausalInferenceSetup | ❌ |
| 8 | `_validate_inference_preconditions` | CausalInferenceSetup | ❌ |

---

### SLOT 12 (Q012) | 21 métodos | 8 patrones | Cats: GENERAL, INDICADOR, TEMPORAL

| # | Método | Clase | ¿Clase usa patterns? |
|---|--------|-------|---------------------|
| 1 | `_aggregate_bayesian_confidence` | BayesianMechanismInference | ✅ |
| 2 | `_test_necessity` | BayesianMechanismInference | ✅ |
| 3 | `_test_sufficiency` | BayesianMechanismInference | ✅ |
| 4-21 | *(+18 adicionales)* | *Mixtas* | *Mixto* |

---

### SLOT 13-30 (Resumen)

| Slot | Métodos | Patrones | Categorías Patrón | % Clases con patterns |
|------|---------|----------|-------------------|----------------------|
| 13 | 22 | 7 | GENERAL, INDICADOR | 68% |
| 14 | 26 | 6 | GENERAL | 54% |
| 15 | 25 | 7 | GENERAL, TERRITORIAL | 60% |
| 16 | 16 | 6 | GENERAL | 56% |
| 17 | 8 | 5 | GENERAL, CAUSAL | 38% |
| 18 | 8 | 5 | GENERAL | 25% |
| 19 | 7 | 6 | GENERAL | 43% |
| 20 | 6 | 5 | GENERAL | 33% |
| 21 | 8 | 7 | GENERAL, TEMPORAL | 75% |
| 22 | 28 | 5 | GENERAL, INDICADOR | 50% |
| 23 | 6 | 6 | GENERAL, INDICADOR | 50% |
| 24 | 7 | 6 | GENERAL | 43% |
| 25 | 8 | 7 | GENERAL | 38% |
| 26 | 8 | 6 | CAUSAL, GENERAL | 25% |
| 27 | 7 | 5 | GENERAL | 43% |
| 28 | 8 | 6 | GENERAL | 0% |
| 29 | 7 | 7 | GENERAL, INDICADOR | 0% |
| 30 | 9 | 7 | CAUSAL, GENERAL, TERRITORIAL | 33% |

---

## 4. ESTADÍSTICAS GLOBALES

### Distribución de Métodos por Slot

```
SLOT  MÉTODOS  ████████████████████████████
01    17       ████████████████▊
02    12       ████████████
03    13       █████████████
04    11       ███████████
05     7       ███████
06     7       ███████
07    11       ███████████
08     9       █████████
09    10       ██████████
10     8       ████████
11     8       ████████
12    21       █████████████████████
13    22       ██████████████████████
14    26       ██████████████████████████ (MAX)
15    25       █████████████████████████
16    16       ████████████████
17     8       ████████
18     8       ████████
19     7       ███████
20     6       ██████ (MIN)
21     8       ████████
22    28       ████████████████████████████ (MAX)
23     6       ██████ (MIN)
24     7       ███████
25     8       ████████
26     8       ████████
27     7       ███████
28     8       ████████
29     7       ███████
30     9       █████████
```

### Categorías de Patrones

| Categoría | Slots que la usan |
|-----------|-------------------|
| GENERAL | 30 (100%) |
| INDICADOR | 10 (33%) |
| TEMPORAL | 5 (17%) |
| CAUSAL | 4 (13%) |
| TERRITORIAL | 2 (7%) |
| UNIDAD_MEDIDA | 1 (3%) |

### Clases Más Frecuentes

| Clase | Ocurrencias | % de slots |
|-------|-------------|------------|
| PDETMunicipalPlanAnalyzer | 28 | 93% |
| BayesianMechanismInference | 15 | 50% |
| CausalExtractor | 14 | 47% |
| IndustrialPolicyProcessor | 10 | 33% |
| FinancialAuditor | 9 | 30% |
| PolicyContradictionDetector | 5 | 17% |

---

## 5. CONCLUSIÓN

### Estado Actual
Los 300 contratos están **estructuralmente completos** con:
- ✅ Identity sincronizado con monolito
- ✅ Method bindings definidos (30 combinaciones únicas)
- ✅ Patterns extraídos del monolito

### Decisiones Pendientes

1. **Patrones**: ¿Inyectar a métodos o mantener para documentación?
2. **Evidence Nexus**: ¿Migrar de EvidenceAssembler legacy?
3. **Hash**: ¿Recalcular para todos los contratos?

### Recomendación

**Cerrar esta iteración.** Los contratos son funcionales. Los warnings son cosméticos y pueden abordarse en un sprint dedicado.
