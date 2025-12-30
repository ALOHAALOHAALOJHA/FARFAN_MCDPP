# TABLA DE COMPATIBILIDAD DE MÉTODOS PARA Q014

## Q014: ¿Existe una relación factible entre la actividad y la meta del producto asociado?

**Dimensiones analíticas evaluadas:**
1. **Relación actividad-meta** (factibilidad, coherencia, alineación) - Peso: 4.0
2. **Plazos** (realistas, temporal, deadline) - Peso: 3.0
3. **Recursos** (realistas, financieros, suficiencia) - Peso: 3.0

---

## 📊 N1-EMP (EXTRACCIÓN) - Top 15 Métodos

| # | Clase | Método | Dim | Score | Act-Meta | Plazos | Recursos | Archivo |
|---|-------|--------|-----|-------|----------|--------|----------|---------|
| 1 | PolicyContradictionDetector | `_extract_temporal_markers` | 3 | 16.0 | 1 | 3 | 1 | contradiction_deteccion.py |
| 2 | TemporalLogicVerifier | `_extract_resources` | 2 | 24.0 | 0 | 5 | 3 | contradiction_deteccion.py |
| 3 | CDAFFramework | `_extract_feedback_from_audit` | 2 | 19.0 | 4 | 0 | 1 | derek_beach.py |
| 4 | FinancialAuditor | `_parse_amount` | 2 | 13.0 | 1 | 0 | 3 | derek_beach.py |
| 5 | PDETMunicipalPlanAnalyzer | `_extract_budget_for_pillar` | 2 | 13.0 | 1 | 0 | 3 | financiero_viabilidad_tablas.py |
| 6 | PolicyContradictionDetector | `_extract_quantitative_claims` | 2 | 7.0 | 1 | 0 | 1 | contradiction_deteccion.py |
| 7 | PDETMunicipalPlanAnalyzer | `_identify_funding_source` | 1 | 18.0 | 0 | 0 | 6 | financiero_viabilidad_tablas.py |
| 8 | PDETMunicipalPlanAnalyzer | `_extract_from_budget_table` | 1 | 18.0 | 0 | 0 | 6 | financiero_viabilidad_tablas.py |
| 9 | PolicyContradictionDetector | `_parse_number` | 1 | 15.0 | 0 | 0 | 5 | contradiction_deteccion.py |
| 10 | PolicyContradictionDetector | `_extract_resource_mentions` | 1 | 15.0 | 0 | 0 | 5 | contradiction_deteccion.py |
| 11 | CausalExtractor | `_extract_goals` | 1 | 12.0 | 3 | 0 | 0 | derek_beach.py |
| 12 | CausalExtractor | `_parse_goal_context` | 1 | 12.0 | 3 | 0 | 0 | derek_beach.py |
| 13 | CausalExtractor | `extract_causal_hierarchy` | 1 | 8.0 | 2 | 0 | 0 | derek_beach.py |
| 14 | PDETMunicipalPlanAnalyzer | `_extract_financial_amounts` | 1 | 6.0 | 0 | 0 | 2 | financiero_viabilidad_tablas.py |
| 15 | IndustrialPolicyProcessor | `_extract_metadata` | 1 | 4.0 | 1 | 0 | 0 | policy_processor.py |

---

## 🔬 N2-INF (INFERENCIA) - Top 25 Métodos

| # | Clase | Método | Dim | Score | Act-Meta | Plazos | Recursos | Archivo |
|---|-------|--------|-----|-------|----------|--------|----------|---------|
| 1 | PDETMunicipalPlanAnalyzer | `generate_executive_report` | 3 | 37.0 | 4 | 2 | 5 | financiero_viabilidad_tablas.py |
| 2 | PDETMunicipalPlanAnalyzer | `generate_recommendations` | 3 | 32.0 | 5 | 3 | 1 | financiero_viabilidad_tablas.py |
| 3 | CausalExtractor | `_assess_temporal_coherence` | 3 | 24.0 | 3 | 1 | 3 | derek_beach.py |
| 4 | OperationalizationAuditor | `_get_remediation_text` | 3 | 24.0 | 3 | 1 | 3 | derek_beach.py |
| 5 | PDETMunicipalPlanAnalyzer | `_scenario_to_dict` | 3 | 22.0 | 4 | 1 | 1 | financiero_viabilidad_tablas.py |
| 6 | PDETMunicipalPlanAnalyzer | `_quality_to_dict` | 3 | 22.0 | 4 | 1 | 1 | financiero_viabilidad_tablas.py |
| 7 | PDETMunicipalPlanAnalyzer | `_generate_recommendations` | 3 | 17.0 | 2 | 1 | 2 | financiero_viabilidad_tablas.py |
| 8 | PDETMunicipalPlanAnalyzer | `export_causal_network` | 3 | 16.0 | 1 | 1 | 3 | financiero_viabilidad_tablas.py |
| 9 | PolicyContradictionDetector | `_determine_semantic_role` | 3 | 16.0 | 1 | 1 | 3 | contradiction_deteccion.py |
| 10 | OperationalizationAuditor | `_build_normative_dag` | 3 | 14.0 | 2 | 1 | 1 | derek_beach.py |
| 11 | PDETMunicipalPlanAnalyzer | `calculate_quality_score` | 3 | 14.0 | 2 | 1 | 1 | financiero_viabilidad_tablas.py |
| 12 | AdaptivePriorCalculator | `sensitivity_analysis` | 3 | 13.0 | 1 | 1 | 2 | derek_beach.py |
| 13 | PDETMunicipalPlanAnalyzer | `_generate_optimal_remediations` | 3 | 13.0 | 1 | 1 | 2 | financiero_viabilidad_tablas.py |
| 14 | CausalExtractor | `_get_policy_area_keywords` | 3 | 10.0 | 1 | 1 | 1 | derek_beach.py |
| 15 | CausalExtractor | `_calculate_dynamic_weights` | 3 | 10.0 | 1 | 1 | 1 | derek_beach.py |
| 16 | CausalExtractor | `_calculate_composite_likelihood` | 3 | 10.0 | 1 | 1 | 1 | derek_beach.py |
| 17 | AdaptivePriorCalculator | `calculate_likelihood_adaptativo` | 3 | 10.0 | 1 | 1 | 1 | derek_beach.py |
| 18 | FinancialAuditor | `trace_financial_allocation` | 2 | 31.0 | 4 | 0 | 5 | derek_beach.py |
| 19 | FinancialAuditor | `_calculate_sufficiency` | 2 | 24.0 | 3 | 0 | 4 | derek_beach.py |
| 20 | TemporalLogicVerifier | `verify_temporal_consistency` | 2 | 21.0 | 0 | 7 | 0 | contradiction_deteccion.py |
| 21 | TemporalLogicVerifier | `_are_mutually_exclusive` | 2 | 24.0 | 0 | 5 | 3 | contradiction_deteccion.py |
| 22 | CausalExtractor | `_assess_financial_consistency` | 2 | 21.0 | 3 | 0 | 3 | derek_beach.py |
| 23 | FinancialAuditor | `_match_goal_to_budget` | 2 | 19.0 | 3 | 0 | 3 | derek_beach.py |
| 24 | PDETMunicipalPlanAnalyzer | `_assess_financial_sustainability` | 2 | 18.0 | 0 | 0 | 6 | financiero_viabilidad_tablas.py |
| 25 | CausalExtractor | `_calculate_coherence_factor` | 2 | 17.0 | 4 | 0 | 1 | derek_beach.py |

---

## ⚖️  N3-AUD (AUDITORÍA) - Top 15 Métodos

| # | Clase | Método | Dim | Score | Act-Meta | Plazos | Recursos | Archivo |
|---|-------|--------|-----|-------|----------|--------|----------|---------|
| 1 | FinancialAuditor | `_perform_counterfactual_budget_check` | 2 | 35.0 | 5 | 0 | 5 | derek_beach.py |
| 2 | FinancialAuditor | `_detect_allocation_gaps` | 2 | 21.0 | 3 | 0 | 3 | derek_beach.py |
| 3 | OperationalizationAuditor | `_perform_counterfactual_budget_check` | 2 | 25.0 | 4 | 0 | 3 | derek_beach.py |
| 4 | OperationalizationAuditor | `_audit_causal_implications` | 2 | 20.0 | 2 | 0 | 4 | derek_beach.py |
| 5 | OperationalizationAuditor | `audit_causal_coherence_d6` | 2 | 19.0 | 4 | 0 | 1 | derek_beach.py |
| 6 | BayesianCounterfactualAuditor | `aggregate_risk_and_prioritize` | 2 | 18.0 | 3 | 0 | 2 | derek_beach.py |
| 7 | OperationalizationAuditor | `audit_sequence_logic` | 2 | 15.0 | 3 | 1 | 0 | derek_beach.py |
| 8 | BayesianCounterfactualAuditor | `_test_effect_stability` | 2 | 15.0 | 3 | 0 | 1 | derek_beach.py |
| 9 | BeachEvidentialTest | `classify_test` | 2 | 11.0 | 2 | 0 | 1 | derek_beach.py |
| 10 | OperationalizationAuditor | `_audit_systemic_risk` | 2 | 11.0 | 2 | 1 | 0 | derek_beach.py |
| 11 | TemporalLogicVerifier | `_check_deadline_constraints` | 2 | 9.0 | 0 | 3 | 0 | contradiction_deteccion.py |
| 12 | PolicyContradictionDetector | `_detect_temporal_conflicts` | 2 | 9.0 | 0 | 3 | 0 | contradiction_deteccion.py |
| 13 | PolicyContradictionDetector | `_detect_resource_conflicts` | 2 | 9.0 | 0 | 0 | 3 | contradiction_deteccion.py |
| 14 | OperationalizationAuditor | `audit_evidence_traceability` | 1 | 12.0 | 3 | 0 | 0 | derek_beach.py |
| 15 | OperationalizationAuditor | `_audit_direct_evidence` | 1 | 8.0 | 2 | 0 | 0 | derek_beach.py |

---

## 🎯 MÉTODOS QUE CUBREN LAS 3 DIMENSIONES (MÁXIMA COMPATIBILIDAD)

Estos métodos cubren **actividad-meta**, **plazos** y **recursos** simultáneamente:

| # | Nivel | Clase | Método | Score | Act-Meta | Plazos | Recursos | Archivo |
|---|-------|-------|--------|-------|----------|--------|----------|---------|
| 1 | N2 | PDETMunicipalPlanAnalyzer | `generate_executive_report` | 37.0 | 4 | 2 | 5 | financiero_viabilidad_tablas.py |
| 2 | N2 | PDETMunicipalPlanAnalyzer | `generate_recommendations` | 32.0 | 5 | 3 | 1 | financiero_viabilidad_tablas.py |
| 3 | N2 | CausalExtractor | `_assess_temporal_coherence` | 24.0 | 3 | 1 | 3 | derek_beach.py |
| 4 | N2 | OperationalizationAuditor | `_get_remediation_text` | 24.0 | 3 | 1 | 3 | derek_beach.py |
| 5 | N2 | PDETMunicipalPlanAnalyzer | `_scenario_to_dict` | 22.0 | 4 | 1 | 1 | financiero_viabilidad_tablas.py |
| 6 | N2 | PDETMunicipalPlanAnalyzer | `_quality_to_dict` | 22.0 | 4 | 1 | 1 | financiero_viabilidad_tablas.py |
| 7 | N2 | PDETMunicipalPlanAnalyzer | `_generate_recommendations` | 17.0 | 2 | 1 | 2 | financiero_viabilidad_tablas.py |
| 8 | N2 | PDETMunicipalPlanAnalyzer | `export_causal_network` | 16.0 | 1 | 1 | 3 | financiero_viabilidad_tablas.py |
| 9 | N1 | PolicyContradictionDetector | `_extract_temporal_markers` | 16.0 | 1 | 3 | 1 | contradiction_deteccion.py |
| 10 | N2 | PolicyContradictionDetector | `_determine_semantic_role` | 16.0 | 1 | 1 | 3 | contradiction_deteccion.py |
| 11 | N2 | OperationalizationAuditor | `_build_normative_dag` | 14.0 | 2 | 1 | 1 | derek_beach.py |
| 12 | N2 | PDETMunicipalPlanAnalyzer | `calculate_quality_score` | 14.0 | 2 | 1 | 1 | financiero_viabilidad_tablas.py |
| 13 | N2 | AdaptivePriorCalculator | `sensitivity_analysis` | 13.0 | 1 | 1 | 2 | derek_beach.py |
| 14 | N2 | PDETMunicipalPlanAnalyzer | `_generate_optimal_remediations` | 13.0 | 1 | 1 | 2 | financiero_viabilidad_tablas.py |
| 15 | N2 | CausalExtractor | `_get_policy_area_keywords` | 10.0 | 1 | 1 | 1 | derek_beach.py |
| 16 | N2 | CausalExtractor | `_calculate_dynamic_weights` | 10.0 | 1 | 1 | 1 | derek_beach.py |
| 17 | N2 | CausalExtractor | `_calculate_composite_likelihood` | 10.0 | 1 | 1 | 1 | derek_beach.py |
| 18 | N2 | AdaptivePriorCalculator | `calculate_likelihood_adaptativo` | 10.0 | 1 | 1 | 1 | derek_beach.py |

---

## 📈 RESUMEN ESTADÍSTICO

- **Total métodos analizados:** 307
- **Métodos que cubren 3 dimensiones:** 19
- **Métodos que cubren 2 dimensiones:** 89
- **Métodos que cubren 1 dimensión:** 199

### Métodos más compatibles por dimensión:

**Relación Actividad-Meta:**
- `PDETMunicipalPlanAnalyzer.generate_recommendations` (Score: 5)
- `PDETMunicipalPlanAnalyzer.generate_executive_report` (Score: 4)
- `CausalExtractor._calculate_coherence_factor` (Score: 4)

**Plazos:**
- `TemporalLogicVerifier.verify_temporal_consistency` (Score: 7)
- `TemporalLogicVerifier._extract_resources` (Score: 5)
- `TemporalLogicVerifier._are_mutually_exclusive` (Score: 5)

**Recursos:**
- `PDETMunicipalPlanAnalyzer._identify_funding_source` (Score: 6)
- `PDETMunicipalPlanAnalyzer._extract_from_budget_table` (Score: 6)
- `PDETMunicipalPlanAnalyzer._assess_financial_sustainability` (Score: 6)

---

## 💡 RECOMENDACIONES

Para responder Q014 con máxima cobertura de dimensiones analíticas, se recomienda:

1. **N1 (Extracción):** `CausalExtractor._extract_goals` + `PolicyContradictionDetector._extract_temporal_markers` + `PDETMunicipalPlanAnalyzer._extract_financial_amounts`

2. **N2 (Inferencia):** 
   - `PDETMunicipalPlanAnalyzer.generate_executive_report` (cubre las 3 dimensiones)
   - `CausalExtractor._assess_temporal_coherence` (cubre las 3 dimensiones)
   - `FinancialAuditor._calculate_sufficiency` (actividad-meta + recursos)

3. **N3 (Auditoría):** 
   - `FinancialAuditor._perform_counterfactual_budget_check` (actividad-meta + recursos)
   - `TemporalLogicVerifier._check_deadline_constraints` (plazos)
   - `OperationalizationAuditor.audit_sequence_logic` (actividad-meta + plazos)

---

**Archivo generado:** `tabla_compatibilidad_q014_final.json`
**Fecha:** 2025-01-XX

