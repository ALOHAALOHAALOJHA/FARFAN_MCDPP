# 📊 EPISTEMIC ASSIGNMENT AUDIT REPORT
**Fecha**: 2025-12-31
**Archivo**: EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030.json

## 📈 Resumen Ejecutivo

- **Preguntas auditadas**: 30/30
- **Checks totales**: 475
- **Checks pasados**: 369 ✅
- **Checks fallados**: 106 ❌
- **Cumplimiento**: 77.7%

## 🚨 Issues por Severidad

- 🔴 **Críticos**: 7
- 🟠 **Altos**: 72
- 🟡 **Medios**: 27
- 🟢 **Bajos**: 0

## ❌ ESTADO: REQUIERE CORRECCIONES

Se encontraron issues críticos que deben ser resueltos.

## 🐛 Issues Detectados

### 🔴 CRÍTICO

**Q004** - N2_MANDATORY_METHOD
- Falta método mandatorio N2 para TYPE_D: FinancialAggregator.normalize
  - Esperado: `FinancialAggregator.normalize`
  - Actual: `FinancialCoherenceAnalyzer.calculate_weighted_mean`

**Q006** - N2_MANDATORY_METHOD
- Falta método mandatorio N2 para TYPE_D: FinancialAggregator.normalize
  - Esperado: `FinancialAggregator.normalize`
  - Actual: `FinancialCoherenceAnalyzer.calculate_weighted_mean`

**Q009** - N2_MANDATORY_METHOD
- Falta método mandatorio N2 para TYPE_D: FinancialAggregator.normalize
  - Esperado: `FinancialAggregator.normalize`
  - Actual: `FinancialCoherenceAnalyzer.calculate_weighted_mean`

**Q012** - N2_MANDATORY_METHOD
- Falta método mandatorio N2 para TYPE_D: FinancialAggregator.normalize
  - Esperado: `FinancialAggregator.normalize`
  - Actual: `FinancialCoherenceAnalyzer.calculate_weighted_mean`

**Q015** - N2_MANDATORY_METHOD
- Falta método mandatorio N2 para TYPE_D: FinancialAggregator.normalize
  - Esperado: `FinancialAggregator.normalize`
  - Actual: `FinancialCoherenceAnalyzer.calculate_weighted_mean`

**Q021** - N2_MANDATORY_METHOD
- Falta método mandatorio N2 para TYPE_D: FinancialAggregator.normalize
  - Esperado: `FinancialAggregator.normalize`
  - Actual: `FinancialCoherenceAnalyzer.calculate_weighted_mean`

**Q022** - N2_MANDATORY_METHOD
- Falta método mandatorio N2 para TYPE_D: FinancialAggregator.normalize
  - Esperado: `FinancialAggregator.normalize`
  - Actual: `FinancialCoherenceAnalyzer.calculate_weighted_mean`

### 🟠 ALTO

**Q002** - N2_EPISTEMIC_NECESSITY
- Método N2[1] 'BayesianNumericalAnalyzer.evaluate_policy_metric' tiene forced_inclusion pero no es mandatorio para TYPE_B

**Q003** - FUSION_STRATEGY
- Estrategia R1 incorrecta para TYPE_D
  - Esperado: `financial_aggregation`
  - Actual: `concat`

**Q005** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q005** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q005** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q006** - N1_FUSION_BEHAVIOR
- Método N1[0] 'FinancialAggregator.aggregate_financial_data' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q006** - N1_FUSION_BEHAVIOR
- Método N1[1] 'TextMiningEngine.extract_product_entities' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q006** - N3_FUSION_BEHAVIOR
- Método N3[0] 'FiscalSustainabilityValidator.check_sufficiency_gate' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q007** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q007** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q007** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q008** - N1_FUSION_BEHAVIOR
- Método N1[0] 'CausalLinkExtractor.extract_causal_links' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q008** - N1_FUSION_BEHAVIOR
- Método N1[1] 'TeoriaCambio.construir_grafo_causal' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q008** - N3_FUSION_BEHAVIOR
- Método N3[0] 'DAGCycleDetector.veto_on_cycle' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q009** - N1_FUSION_BEHAVIOR
- Método N1[0] 'FinancialAggregator.aggregate_financial_data' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q009** - N3_FUSION_BEHAVIOR
- Método N3[0] 'FiscalSustainabilityValidator.check_sufficiency_gate' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q010** - N1_FUSION_BEHAVIOR
- Método N1[0] 'LogicalConsistencyChecker.fact_collation' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q010** - N3_FUSION_BEHAVIOR
- Método N3[0] 'ContradictionDominator.apply_dominance_veto' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q011** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q011** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q011** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q012** - N1_FUSION_BEHAVIOR
- Método N1[0] 'FinancialAggregator.aggregate_financial_data' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q012** - N3_FUSION_BEHAVIOR
- Método N3[0] 'FiscalSustainabilityValidator.check_sufficiency_gate' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q013** - N1_FUSION_BEHAVIOR
- Método N1[0] 'AdvancedSemanticChunker.chunk_text' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q013** - N1_FUSION_BEHAVIOR
- Método N1[1] 'TextMiningEngine.extract_security_keywords' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q013** - N3_FUSION_BEHAVIOR
- Método N3[0] 'ContradictionDominator.apply_dominance_veto' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q014** - N1_FUSION_BEHAVIOR
- Método N1[0] 'LogicalConsistencyChecker.fact_collation' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q014** - N3_FUSION_BEHAVIOR
- Método N3[0] 'ContradictionDominator.apply_dominance_veto' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q015** - N1_FUSION_BEHAVIOR
- Método N1[0] 'FinancialAggregator.aggregate_financial_data' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q015** - N3_FUSION_BEHAVIOR
- Método N3[0] 'FiscalSustainabilityValidator.check_sufficiency_gate' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q016** - N1_FUSION_BEHAVIOR
- Método N1[0] 'CausalLinkExtractor.extract_causal_links' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q016** - N1_FUSION_BEHAVIOR
- Método N1[1] 'TeoriaCambio.construir_grafo_causal' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q016** - N3_FUSION_BEHAVIOR
- Método N3[0] 'DAGCycleDetector.veto_on_cycle' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q017** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q017** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q017** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q018** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q018** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q018** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q019** - N1_FUSION_BEHAVIOR
- Método N1[0] 'LogicalConsistencyChecker.fact_collation' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q019** - N3_FUSION_BEHAVIOR
- Método N3[0] 'ContradictionDominator.apply_dominance_veto' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q020** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q020** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q020** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q021** - N1_FUSION_BEHAVIOR
- Método N1[0] 'FinancialAggregator.aggregate_financial_data' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q021** - N3_FUSION_BEHAVIOR
- Método N3[0] 'FiscalSustainabilityValidator.check_sufficiency_gate' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q022** - N1_FUSION_BEHAVIOR
- Método N1[0] 'FinancialAggregator.aggregate_financial_data' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q022** - N3_FUSION_BEHAVIOR
- Método N3[0] 'FiscalSustainabilityValidator.check_sufficiency_gate' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q022** - FUSION_STRATEGY
- Estrategia R1 incorrecta para TYPE_D
  - Esperado: `financial_aggregation`
  - Actual: `concat`

**Q023** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q023** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q023** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q024** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q024** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q024** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q025** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q025** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q025** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q026** - N1_FUSION_BEHAVIOR
- Método N1[0] 'CausalLinkExtractor.extract_causal_links' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q026** - N1_FUSION_BEHAVIOR
- Método N1[1] 'TeoriaCambio.construir_grafo_causal' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q026** - N3_FUSION_BEHAVIOR
- Método N3[0] 'DAGCycleDetector.veto_on_cycle' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q027** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q027** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q027** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q028** - N1_FUSION_BEHAVIOR
- Método N1[0] 'LogicalConsistencyChecker.fact_collation' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q028** - N3_FUSION_BEHAVIOR
- Método N3[0] 'ContradictionDominator.apply_dominance_veto' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q029** - N1_FUSION_BEHAVIOR
- Método N1[0] 'BayesianEvidenceExtractor.extract_prior_beliefs' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q029** - N1_FUSION_BEHAVIOR
- Método N1[1] 'BayesianEvidenceExtractor.extract_likelihood_evidence' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q029** - N3_FUSION_BEHAVIOR
- Método N3[0] 'StatisticalGateAuditor.test_significance' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

**Q030** - N1_FUSION_BEHAVIOR
- Método N1[0] 'CausalLinkExtractor.extract_causal_links' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q030** - N1_FUSION_BEHAVIOR
- Método N1[1] 'TeoriaCambio.construir_grafo_causal' debe tener fusion_behavior='concat'
  - Esperado: `concat`

**Q030** - N3_FUSION_BEHAVIOR
- Método N3[0] 'DAGCycleDetector.veto_on_cycle' debe tener fusion_behavior con 'veto_gate'
  - Esperado: `veto_gate`

### 🟡 MEDIO

**Q004** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q005** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q006** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q007** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q008** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q009** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q010** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q011** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q012** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q013** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q014** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q015** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q016** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q017** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q018** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q019** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q020** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q021** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q022** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q023** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q024** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q025** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q026** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q027** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q028** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q029** - OVERALL_JUSTIFICATION
- Falta overall_justification

**Q030** - OVERALL_JUSTIFICATION
- Falta overall_justification

## 💡 Recomendaciones

1. **Prioridad Alta**: Resolver todos los issues críticos (🔴)
2. Verificar que los métodos mandatorios están presentes según episte_refact.md Section 2.2
3. Asegurar que output_types son correctos: N1=FACT, N2=PARAMETER, N3=CONSTRAINT
4. Validar estrategias de fusión según TYPE
