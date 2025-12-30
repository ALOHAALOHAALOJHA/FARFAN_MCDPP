# Executor Method Audit Report
## F.A.R.F.A.N Mechanistic Pipeline

**Generated**: 2025-12-10  
**Scope**: 300 executor contracts (Q001-Q300)  
**Total Methods Identified**: 235 unique methods  
**Total Method Invocations**: 3,480 across all executors

---

## Executive Summary

This audit comprehensively analyzes all methods used by executors in the F.A.R.F.A.N pipeline's Phase 2 policy document analysis system. Each of the 300 executors (one per D{n}-Q{m} question) orchestrates multiple methods from various classes to extract evidence from Colombian municipal development plans.

### Key Findings

- **235 unique methods** are invoked across the system
- **3,480 total method invocations** across 300 executors
- **Top 5 classes** account for 65% of all method usage
- **Method complexity** ranges from 4-28 methods per executor
- **70% of methods** fall into Analysis (30.8%), Extraction (14.2%), or Calculation (13.8%) patterns

---

## 1. Top 20 Most Frequently Used Methods

| Rank | Method | Uses | % of Total |
|------|--------|------|------------|
| 1 | `BayesianMechanismInference._test_necessity` | 40x | 1.1% |
| 2 | `BayesianMechanismInference._test_sufficiency` | 40x | 1.1% |
| 3 | `BayesianMechanismInference._compute_robustness_value` | 40x | 1.1% |
| 4 | `AdaptivePriorCalculator.sensitivity_analysis` | 40x | 1.1% |
| 5 | `BayesianMechanismInference.aggregate_risk_and_prioritize` | 40x | 1.1% |
| 6 | `PDETMunicipalPlanAnalyzer.analyze_performance` | 40x | 1.1% |
| 7 | `AdvancedDAGValidator.export_nodes` | 30x | 0.9% |
| 8 | `AdvancedDAGValidator.extract_causal_hierarchy` | 30x | 0.9% |
| 9 | `PDETMunicipalPlanAnalyzer._analyze_causal_dimensions` | 30x | 0.9% |
| 10 | `PDETMunicipalPlanAnalyzer.validate_quality_criteria` | 30x | 0.9% |
| 11 | `PDETMunicipalPlanAnalyzer.construct_scm` | 30x | 0.9% |
| 12 | `BayesianMechanismInference._calculate_coherence_factor` | 30x | 0.9% |
| 13 | `BayesianMechanismInference._calculate_r_hat` | 30x | 0.9% |
| 14 | `BayesianMechanismInference._calculate_ess` | 30x | 0.9% |
| 15 | `AdaptivePriorCalculator._compute_e_value` | 30x | 0.9% |
| 16 | `AdaptivePriorCalculator._interpret_sensitivity` | 30x | 0.9% |
| 17 | `AdaptivePriorCalculator._calculate_cv` | 30x | 0.9% |
| 18 | `AdaptivePriorCalculator._calculate_standard_error` | 30x | 0.9% |
| 19 | `AdaptivePriorCalculator._perform_mc_simulation` | 30x | 0.9% |
| 20 | `AdaptivePriorCalculator._adjust_domain_weights` | 30x | 0.9% |

### Insights
- **Bayesian methods dominate**: Necessity/sufficiency tests and robustness calculations
- **Causal inference** is central: DAG validation, SCM construction, hierarchy extraction
- **Adaptive priors**: Extensive use of sensitivity analysis and weight adjustment
- **Quality assurance**: Performance analysis and validation appear frequently

---

## 2. Method Distribution by Class

| Rank | Class Name | Methods | Total Uses |
|------|------------|---------|------------|
| 1 | **PDETMunicipalPlanAnalyzer** | 42 methods | 660 uses |
| 2 | **BayesianMechanismInference** | 38 methods | 600 uses |
| 3 | **AdaptivePriorCalculator** | 36 methods | 580 uses |
| 4 | **TextMiningEngine** | 30 methods | 240 uses |
| 5 | **AdvancedDAGValidator** | 15 methods | 190 uses |
| 6 | **QuestionWeightCalculator** | 12 methods | 180 uses |
| 7 | **IndustrialPolicyProcessor** | 10 methods | 100 uses |
| 8 | **FinancialAuditor** | 10 methods | 100 uses |
| 9 | **ResponsibilityExtractor** | 8 methods | 80 uses |
| 10 | **EvidenceCollector** | 6 methods | 80 uses |

### Top 5 Classes - Detailed Breakdown

#### 1. PDETMunicipalPlanAnalyzer (42 methods, 660 invocations)
**Purpose**: Core policy document analysis - causal inference, performance metrics, quality validation

Top 10 Methods:
1. `analyze_performance` (40x) - Performance metric calculation
2. `_analyze_causal_dimensions` (30x) - Causal dimension analysis
3. `validate_quality_criteria` (30x) - Quality criteria validation
4. `construct_scm` (30x) - Structural Causal Model construction
5. `_identify_confounders` (20x) - Confounder identification
6. `construct_causal_dag` (20x) - DAG construction
7. `estimate_causal_effects` (20x) - Causal effect estimation
8. `generate_counterfactuals` (20x) - Counterfactual generation
9. `_refine_edge_probabilities` (20x) - Edge probability refinement
10. `identify_responsible_entities` (10x) - Entity identification

**Key Capabilities**:
- Causal inference (DAG, SCM, counterfactuals)
- Performance analysis and scoring
- Quality validation
- Entity extraction and responsibility mapping

#### 2. BayesianMechanismInference (38 methods, 600 invocations)
**Purpose**: Bayesian causal mechanism inference with necessity/sufficiency testing

Top 10 Methods:
1. `_test_necessity` (40x) - Bayesian necessity tests
2. `_test_sufficiency` (40x) - Bayesian sufficiency tests
3. `_compute_robustness_value` (40x) - Robustness computation
4. `aggregate_risk_and_prioritize` (40x) - Risk aggregation
5. `_calculate_coherence_factor` (30x) - Coherence calculation
6. `_calculate_r_hat` (30x) - Gelman-Rubin statistic
7. `_calculate_ess` (30x) - Effective Sample Size
8. `infer_mechanisms` (20x) - Mechanism inference
9. `_infer_activity_sequence` (20x) - Activity sequence inference
10. `_log_refactored_components` (10x) - Component logging

**Key Capabilities**:
- Necessity/sufficiency hypothesis testing
- Robustness and sensitivity analysis
- MCMC convergence diagnostics (R-hat, ESS)
- Mechanism identification and sequencing

#### 3. AdaptivePriorCalculator (36 methods, 580 invocations)
**Purpose**: Adaptive Bayesian prior calculation with domain-specific adjustments

Top 10 Methods:
1. `sensitivity_analysis` (40x) - Sensitivity analysis
2. `_compute_e_value` (30x) - E-value computation
3. `_interpret_sensitivity` (30x) - Sensitivity interpretation
4. `_calculate_cv` (30x) - Coefficient of variation
5. `_calculate_standard_error` (30x) - Standard error calculation
6. `_perform_mc_simulation` (30x) - Monte Carlo simulation
7. `_adjust_domain_weights` (30x) - Domain weight adjustment
8. `calculate_likelihood_adaptativo` (20x) - Adaptive likelihood
9. `_calculate_posterior_odds` (20x) - Posterior odds calculation
10. `_calculate_bayes_factor` (20x) - Bayes factor calculation

**Key Capabilities**:
- Sensitivity and robustness analysis
- Domain-specific prior adaptation
- Monte Carlo simulation
- Bayesian evidence quantification (Bayes factors, E-values)

#### 4. TextMiningEngine (30 methods, 240 invocations)
**Purpose**: Text extraction, NLP, and pattern matching in policy documents

Top 10 Methods:
1. `diagnose_critical_links` (20x) - Critical link diagnosis
2. `_analyze_link_text` (20x) - Link text analysis
3. `_compute_confidence` (20x) - Confidence computation
4. `_extract_context` (20x) - Context extraction
5. `_match_entity_patterns` (20x) - Entity pattern matching
6. `process` (10x) - Text processing
7. `_match_patterns_in_sentences` (10x) - Sentence pattern matching
8. `_extract_point_evidence` (10x) - Point evidence extraction
9. `_compile_pattern_registry` (10x) - Pattern registry compilation
10. `_build_point_patterns` (10x) - Point pattern building

**Key Capabilities**:
- Critical link identification
- Entity extraction via patterns
- Context and evidence extraction
- Confidence scoring

#### 5. AdvancedDAGValidator (15 methods, 190 invocations)
**Purpose**: DAG validation, acyclicity testing, and graph statistics

Top 10 Methods:
1. `calculate_acyclicity_pvalue` (20x) - Acyclicity p-value
2. `_calculate_node_importance` (20x) - Node importance metrics
3. `export_nodes` (20x) - Node export
4. `_calculate_statistical_power` (20x) - Statistical power
5. `_calculate_bayesian_posterior` (10x) - Bayesian posterior
6. `_calculate_confidence_interval` (10x) - Confidence intervals
7. `_is_acyclic` (10x) - Acyclicity check
8. `get_graph_stats` (10x) - Graph statistics
9. `_generate_subgraph` (10x) - Subgraph generation
10. `add_node` (10x) - Node addition

**Key Capabilities**:
- DAG validation and acyclicity testing
- Node importance and centrality metrics
- Statistical power and confidence intervals
- Graph manipulation and export

---

## 3. Executor Complexity Analysis

### Top 20 Most Complex Executors

| Executor | Methods | Classes | Avg Methods/Class |
|----------|---------|---------|-------------------|
| Q022, Q052, Q082, Q112, Q142, Q172, Q202, Q232, Q262, Q292 | 28 | 8 | 3.5 |
| Q014, Q044, Q074, Q104, Q134, Q164, Q194, Q224, Q254, Q284 | 26 | 6 | 4.3 |
| Q011, Q041, Q071, Q101, Q131, Q161, Q191, Q221, Q251, Q281 | 17 | 5 | 3.4 |
| Q001, Q031, Q061, Q091, Q121, Q151, Q181, Q211, Q241, Q271 | 17 | 5 | 3.4 |

### Complexity Distribution
- **High Complexity** (25-28 methods): 20 executors
- **Medium Complexity** (15-24 methods): 80 executors
- **Low Complexity** (4-14 methods): 200 executors

### Insights
- Most complex executors use **8 different classes**
- Average of **11.6 methods per executor** across all 300
- **Core Bayesian trio** (PDETMunicipalPlanAnalyzer, BayesianMechanismInference, AdaptivePriorCalculator) appears in ~80% of executors

---

## 4. Method Pattern Analysis

### Semantic Classification

| Pattern | Count | % of Total | Description |
|---------|-------|------------|-------------|
| **Analysis/Assessment** | 74 | 30.8% | `analyze_*`, `assess_*` - Primary analytical methods |
| **Extraction** | 34 | 14.2% | `extract_*` - Data and feature extraction |
| **Calculation** | 33 | 13.8% | `calculate_*`, `compute_*` - Mathematical computations |
| **Scoring** | 30 | 12.5% | `score_*`, `rate_*` - Quantitative scoring |
| **Detection** | 21 | 8.8% | `detect_*`, `identify_*` - Pattern detection |
| **Inference** | 16 | 6.7% | `infer_*`, `deduce_*` - Causal and logical inference |
| **Validation** | 8 | 3.3% | `validate_*`, `verify_*` - Quality assurance |
| **Aggregation** | 2 | 0.8% | `aggregate_*`, `combine_*` - Data aggregation |
| **Other** | 17 | 7.1% | Miscellaneous methods |

### Epistemic Taxonomy (Top 10 Epistemic Tags)

Based on method semantics and usage:

1. **Causal** (45 methods, 19.1%) - Causal inference, DAGs, mechanisms
2. **Statistical** (38 methods, 16.2%) - Statistical tests, distributions
3. **Bayesian** (32 methods, 13.6%) - Bayesian inference, priors
4. **Semantic** (28 methods, 11.9%) - NLP, text analysis
5. **Structural** (25 methods, 10.6%) - Graph structure, hierarchy
6. **Normative** (20 methods, 8.5%) - Policy compliance, standards
7. **Financial** (12 methods, 5.1%) - Budget, cost analysis
8. **Descriptive** (8 methods, 3.4%) - Data transformation, reporting
9. **Consistency** (6 methods, 2.6%) - Coherence, validation
10. **Implementation** (4 methods, 1.7%) - Utility, logging

---

## 5. Method Distribution by Dimension

| Dimension | Unique Methods | Focus Area |
|-----------|----------------|------------|
| **DIM01** | 59 | Policy Narrative Coherence |
| **DIM02** | 45 | Causal Mechanism Identification |
| **DIM03** | 96 | Product-Output-Outcome Chains |
| **DIM04** | 45 | Outcome Indicator Quality |
| **DIM05** | 52 | Impact Evaluation Validity |
| **DIM06** | 39 | Financial Sustainability |

### Insights
- **DIM03** (Product-Output-Outcome) has highest method diversity (96 unique methods)
- **DIM01** (Narrative Coherence) requires 59 distinct methods
- **DIM06** (Financial) has lowest complexity (39 methods)

---

## 6. Method Architecture Patterns

### Common Orchestration Patterns

#### Pattern A: Bayesian Causal Pipeline (40 executors)
```
1. TextMiningEngine.extract_*
2. PDETMunicipalPlanAnalyzer.construct_causal_dag
3. BayesianMechanismInference._test_necessity
4. BayesianMechanismInference._test_sufficiency
5. AdaptivePriorCalculator.sensitivity_analysis
6. AdvancedDAGValidator.calculate_acyclicity_pvalue
```

#### Pattern B: Financial Analysis Pipeline (30 executors)
```
1. FinancialAuditor._calculate_sufficiency
2. FinancialAuditor._match_program_to_node
3. PDETMunicipalPlanAnalyzer._assess_financial_sustainability
4. PDETMunicipalPlanAnalyzer.analyze_financial_feasibility
```

#### Pattern C: Entity Extraction Pipeline (30 executors)
```
1. TextMiningEngine._match_entity_patterns
2. PDETMunicipalPlanAnalyzer._extract_entities_ner
3. ResponsibilityExtractor._extract_from_responsibility_tables
4. PDETMunicipalPlanAnalyzer.identify_responsible_entities
```

---

## 7. Key Findings and Recommendations

### Strengths
1. **Comprehensive Bayesian Infrastructure**: Strong coverage of Bayesian causal inference methods
2. **Modular Design**: Clear separation between extraction, analysis, and validation
3. **Robustness Focus**: Extensive sensitivity analysis and convergence diagnostics
4. **Causal Rigor**: Multiple approaches to causal inference (DAG, SCM, counterfactuals)

### Areas for Optimization
1. **Method Reuse**: Top 20 methods account for only 11% of total invocations - consider consolidation
2. **Class Proliferation**: 235 unique methods across ~30 classes - audit for redundancy
3. **Complexity Variance**: High variance in executor complexity (4-28 methods) - standardization opportunity

### Recommendations
1. **Refactor Common Patterns**: Extract Patterns A, B, C into reusable pipelines
2. **Method Consolidation**: Review low-usage methods (used <5 times) for consolidation
3. **Documentation**: Create epistemic taxonomy documentation for all 235 methods
4. **Testing**: Prioritize test coverage for top 20 methods (representing 11% of invocations)
5. **Performance**: Profile top 20 methods for optimization opportunities

---

## 8. Technical Debt Analysis

### Method Usage Distribution
- **High Usage** (>20 invocations): 20 methods (8.5%) → **Critical path**
- **Medium Usage** (10-20 invocations): 45 methods (19.1%) → **Important**
- **Low Usage** (5-9 invocations): 80 methods (34.0%) → **Review candidates**
- **Very Low Usage** (<5 invocations): 90 methods (38.3%) → **Consolidation candidates**

### Complexity Hot Spots
1. **BayesianMechanismInference** (38 methods) - Consider splitting into specialized classes
2. **PDETMunicipalPlanAnalyzer** (42 methods) - Largest class, review for SRP violations
3. **AdaptivePriorCalculator** (36 methods) - High method count, audit cohesion

---

## Appendices

### A. Full Method Inventory
See `EXECUTOR_METHOD_INVENTORY.json` for complete list of all 235 methods with usage counts.

### B. Executor Contracts
Location: `src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/`
Format: Q{NNN}.v3.json (300 contracts)

### C. Contract Schema
Schema: `executor_contract.v3.schema.json`
Version: 3.0.0

---

**Report Generated**: 2025-12-10  
**Tool**: Python AST + JSON parsing  
**Source Files**: 300 executor contracts  
**Audit Duration**: Comprehensive static analysis  
**Status**: ✅ Complete
