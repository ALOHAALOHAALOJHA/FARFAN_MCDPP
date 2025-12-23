# Contract Classification Analysis - V4 Generation

## Source: OPERACIONALIZACIÓN_CONTRATOS_VERSION_4, PARTE I, Sección 1.1

### Classification Table from Guide

| Tipo | Código | Contratos | Foco | Estrategia Principal |
|------|--------|-----------|------|---------------------|
| Semántico | TYPE_A | Q001, Q013 | Coherencia narrativa, NLP | semantic_triangulation |
| Bayesiano | TYPE_B | Q002, Q005, Q007, Q011, Q017, Q018, Q020, Q023, Q024, Q025, Q027, Q029 | Significancia estadística, priors | bayesian_update |
| Causal | TYPE_C | Q008, Q016, Q026, Q030 | Topología de grafos, DAGs | topological_overlay |
| Financiero | TYPE_D | Q003, Q004, Q006, Q009, Q012, Q015, Q021, Q022 | Suficiencia presupuestal | financial_coherence_audit |
| Lógico | TYPE_E | Q010, Q014, Q019, Q028 | Detección de contradicciones | logical_consistency_validation |

## Contracts to Generate (27 total)

### Batch 1: D1-Q4, D1-Q5, D2-Q1, D2-Q2, D2-Q3

#### D1-Q4 (Q004)
- **Classification**: TYPE_D (Financiero)
- **Representative Question**: Q004
- **Contracts Served**: Q004, Q034, Q064, Q094, Q124, Q154, Q184, Q214, Q244, Q274
- **Method Count**: 11
- **Dominant Classes**: PDETMunicipalPlanAnalyzer, MechanismPartExtractor, OperationalizationAuditor
- **Focus**: Responsible entities identification (often tied to financial responsibility)
- **Primary Strategy**: financial_coherence_audit (for TYPE_D)
- **N2 Strategy**: weighted_mean

#### D1-Q5 (Q005)
- **Classification**: TYPE_B (Bayesiano)
- **Representative Question**: Q005
- **Contracts Served**: Q005, Q035, Q065, Q095, Q125, Q155, Q185, Q215, Q245, Q275
- **Method Count**: 7
- **Dominant Classes**: TemporalLogicVerifier, CausalInferenceSetup, CausalExtractor
- **Focus**: Temporal consistency and failure point identification (probabilistic analysis)
- **Primary Strategy**: bayesian_update (for TYPE_B)
- **N2 Strategy**: bayesian_update

#### D2-Q1 (Q031)
- **Classification**: To be determined from Q001 base (TYPE_A expected)
- **Representative Question**: Q031
- **Contracts Served**: Q001, Q031, Q061, Q091, Q121, Q151, Q181, Q211, Q241, Q271
- **Method Count**: 7
- **Note**: This is policy area PA02's version of D1-Q1

#### D2-Q2 (Q032)
- **Classification**: To be determined from Q002 base (TYPE_B expected)
- **Representative Question**: Q032
- **Contracts Served**: Q002, Q032, Q062, Q092, Q122, Q152, Q182, Q212, Q242, Q272
- **Method Count**: 11

#### D2-Q3 (Q033)
- **Classification**: To be determined from Q003 base (TYPE_D expected)
- **Representative Question**: Q033
- **Contracts Served**: Q003, Q033, Q063, Q093, Q123, Q153, Q183, Q213, Q243, Q273
- **Method Count**: 9

## Classification Rules

### By Dominant Class (PARTE I, Sec 1.1)

**TYPE_A (Semántico):**
- SemanticAnalyzer
- TextMiningEngine
- SemanticProcessor

**TYPE_B (Bayesiano):**
- BayesianMechanismInference
- AdaptivePriorCalculator
- HierarchicalGenerativeModel
- BayesianNumericalAnalyzer

**TYPE_C (Causal):**
- CausalExtractor
- TeoriaCambio
- AdvancedDAGValidator

**TYPE_D (Financiero):**
- FinancialAuditor
- PDETMunicipalPlanAnalyzer (financial methods)

**TYPE_E (Lógico):**
- PolicyContradictionDetector
- OperationalizationAuditor
- IndustrialGradeValidator

## Strategy Assignment by Type

| Type | N1 Strategy | N2 Strategy | N3 Strategy |
|------|-------------|-------------|-------------|
| TYPE_A | semantic_corroboration | dempster_shafer | veto_gate |
| TYPE_B | concat | bayesian_update | veto_gate |
| TYPE_C | graph_construction | topological_overlay | veto_gate |
| TYPE_D | concat | weighted_mean | financial_coherence_audit + veto_gate |
| TYPE_E | concat | weighted_mean | logical_consistency_validation + veto_gate |

## Verification Checklist Before Generation

- [ ] Contract type verified against guide table
- [ ] Dominant classes analyzed and match type
- [ ] Method count verified from method_classification_all_30.json
- [ ] Strategies assigned per type (N1, N2, N3)
- [ ] All methods classified to N1/N2/N3 levels
- [ ] N3 methods have veto_conditions defined
- [ ] No spaces in provides/sources strings
