# Executor Method Availability Audit Report

## Executive Summary

The **Executor Method Availability Audit** ensures all 30 executors have complete method availability from the methods dispensary. This directly impacts the quality of answers that executors provide, as missing methods may lead to incomplete or degraded analysis.

## Critical Finding

**12 out of 30 executors (40%)** have missing methods that are not available in the dispensary catalog.

- **Total Missing Methods**: 14 unique method signatures
- **Overall Health**: 60.0%
- **Executors Affected**: D1-Q1, D1-Q2, D1-Q3, D1-Q4, D3-Q2, D3-Q3, D4-Q1, D4-Q3, D4-Q4, D5-Q2, D6-Q1, D6-Q5

## Audit Methodology

1. **Load Executor Configurations**: Parse `executors_methods.json` (30 executors)
2. **Load Validation Failures**: Parse `executor_factory_validation.json` (14 failures)
3. **Scan Dispensary**: AST-parse all Python files in `src/methods_dispensary/`
4. **Identify Gaps**: Cross-reference executor requirements with available methods
5. **Generate Suggestions**: Find similar methods based on:
   - Keyword matching in method names
   - Docstring content analysis
   - Same-class vs. cross-class alternatives
   - Similarity scoring algorithm

## Affected Executors

### Dimension 1: Diagnosis

#### D1-Q1: QuantitativeBaselineExtractor
**Question**: Extracts numeric data, reference years, and official sources as baseline

**Missing Methods**:
- `SemanticProcessor.chunk_text` ❌
- `SemanticProcessor.embed_single` ❌

**Suggested Alternatives**:
- `EmbeddingPolicyProducer.get_chunk_text` (score: 6) ✅
- `SemanticChunkingProducer.get_chunk_text` (score: 6) ✅
- `SemanticProcessor._embed_batch` (score: 4) for embedding

**Impact**: May affect text preprocessing and semantic analysis capabilities.

#### D1-Q2: ProblemDimensioningAnalyzer
**Question**: Quantifies problem magnitude, gaps, and identifies data limitations

**Missing Methods**:
- `FinancialAuditor._detect_allocation_gaps` ❌
- `PDETMunicipalPlanAnalyzer._generate_optimal_remediations` ❌

**Suggested Alternatives**:
- `FinancialAuditor._trace_budget_allocations` (score: 3)
- `FinancialAuditor._calculate_gap_metrics` (score: 2)

**Impact**: May affect financial gap detection and remediation generation.

#### D1-Q3: FinancialTracingAnalyzer
**Question**: Traces monetary resources assigned to programs in Investment Plan (PPI)

**Missing Methods**:
- `FinancialAuditor._calculate_sufficiency` ❌
- `FinancialAuditor._match_goal_to_budget` ❌

**Suggested Alternatives**:
- `FinancialAuditor._validate_budget_coherence` (score: 3)
- `FinancialAuditor._trace_budget_allocations` (score: 3)

**Impact**: Critical - affects budget tracing and sufficiency analysis.

#### D1-Q4: CapacityIdentificationAnalyzer
**Question**: Identifies installed capacity (entities, staff, equipment) and limitations

**Missing Methods**:
- `MechanismPartExtractor._calculate_ea_confidence` ❌
- `MechanismPartExtractor._validate_entity_activity` ❌

**Suggested Alternatives**:
- `MechanismPartExtractor._extract_entity_activity_pairs` (score: 4)
- `MechanismPartExtractor._validate_mechanisms` (score: 3)

**Impact**: May affect entity-activity confidence calculations.

### Dimension 3: Products

#### D3-Q2: TargetProportionalityAnalyzer
**Question**: Analyzes proportionality of targets to the diagnosed universe

**Missing Methods**:
- `FinancialAuditor._calculate_sufficiency` ❌

**Suggested Alternatives**:
- `FinancialAuditor._validate_budget_coherence` (score: 3)

#### D3-Q3: TraceabilityBudgetOrgAnalyzer
**Question**: Validates budgetary and organizational traceability of products

**Missing Methods**:
- `FinancialAuditor._match_goal_to_budget` ❌

**Suggested Alternatives**:
- `FinancialAuditor._trace_budget_allocations` (score: 3)

### Dimension 4: Results

#### D4-Q1: OutcomeIndicatorCompletenessAnalyzer
**Question**: Validates outcome indicators (baseline, target, horizon)

**Missing Methods**:
- `CausalExtractor._classify_goal_type` ❌

**Suggested Alternatives**:
- `CausalExtractor._extract_goals` (score: 3)
- `CausalExtractor._parse_goal_context` (score: 2)

#### D4-Q3: ResultAmbitionJustificationAnalyzer
**Question**: Analyzes justification of result ambition

**Missing Methods**:
- `BayesianMechanismInference._aggregate_bayesian_confidence` ❌

**Suggested Alternatives**:
- `BayesianMechanismInference.aggregate_evidences` (score: 4)
- `BayesianMechanismInference._calculate_confidence_intervals` (score: 3)

#### D4-Q4: ResultProblemAlignmentAnalyzer
**Question**: Evaluates whether results address/resolve prioritized problems

**Missing Methods**:
- `FinancialAuditor._detect_allocation_gaps` ❌

### Dimension 5: Impact

#### D5-Q2: CompositeProxyValidityAnalyzer
**Question**: Validates composite indices/proxies for complex impacts

**Missing Methods**:
- `BayesianMechanismInference._aggregate_bayesian_confidence` ❌
- `FinancialAuditor._calculate_sufficiency` ❌

### Dimension 6: Theory of Change & Sustainability

#### D6-Q1: TheoryOfChangeBuilderValidator
**Question**: Builds/validates explicit Theory of Change with diagram and assumptions

**Missing Methods**:
- `TeoriaCambio.export_nodes` ❌

**Suggested Alternatives**:
- `TeoriaCambio.export_graph` (score: 4)
- `TeoriaCambio.get_nodes` (score: 3)

#### D6-Q5: ContextualAdaptationEvaluator
**Question**: Evaluates contextual adaptation: differential impacts and territorial constraints

**Missing Methods** (4 total):
- `CausalInferenceSetup._get_dynamics_pattern` ❌
- `SemanticProcessor._detect_pdm_structure` ❌
- `SemanticProcessor._detect_table` ❌
- `SemanticProcessor.chunk_text` ❌

**Suggested Alternatives**:
- `EmbeddingPolicyProducer.get_chunk_text` (score: 6)
- `SemanticProcessor._detect_numerical_data` (score: 2)

## Dispensary Statistics

**Total Classes Scanned**: 66  
**Total Methods Available**: 642

**Top Dispensary Classes by Method Count**:
1. `PDETMunicipalPlanAnalyzer`: 78 methods
2. `DerekBeachProcessor`: 62 methods
3. `BayesianMultilevelSystem`: 45 methods
4. `FinancialAuditor`: 38 methods
5. `CausalExtractor`: 34 methods

## Recommendations

### Immediate Actions (Critical)

1. **Implement Missing Methods** in their respective classes:
   - `FinancialAuditor`: Add `_calculate_sufficiency`, `_match_goal_to_budget`, `_detect_allocation_gaps`
   - `SemanticProcessor`: Add `chunk_text`, `embed_single`, `_detect_pdm_structure`, `_detect_table`
   - `BayesianMechanismInference`: Add `_aggregate_bayesian_confidence`
   - `MechanismPartExtractor`: Add `_calculate_ea_confidence`, `_validate_entity_activity`
   - `CausalExtractor`: Add `_classify_goal_type`
   - `CausalInferenceSetup`: Add `_get_dynamics_pattern`
   - `TeoriaCambio`: Add `export_nodes`
   - `PDETMunicipalPlanAnalyzer`: Add `_generate_optimal_remediations`

2. **Use Suggested Alternatives** (Temporary Fix):
   - Update executor contracts to use available methods with similar functionality
   - Example: Replace `SemanticProcessor.chunk_text` with `EmbeddingPolicyProducer.get_chunk_text`

3. **Validate Executor Outputs**:
   - Test affected executors to ensure answer quality is not degraded
   - Compare outputs before and after method replacement

### Short-term Improvements

4. **Create Method Adapter Layer**:
   - Build facade pattern to map missing methods to available alternatives
   - Maintain backward compatibility while refactoring

5. **Enhance Dispensary Coverage**:
   - Review all 14 missing methods and their intended functionality
   - Add comprehensive implementations to the dispensary

6. **Update Contract Validation**:
   - Modify `executor_factory_validation.json` to mark suggested alternatives as acceptable
   - Re-run validation after implementing changes

### Long-term Strategy

7. **Automated Dependency Checking**:
   - Add this audit to CI/CD pipeline
   - Fail builds if executors reference non-existent methods

8. **Method Documentation**:
   - Ensure all dispensary methods have comprehensive docstrings
   - Document method contracts and expected inputs/outputs

9. **Executor Health Dashboard**:
   - Create visual dashboard showing executor health status
   - Track method availability over time

## Implementation Priority

### Priority 1: HIGH IMPACT (Affects multiple executors)
- `FinancialAuditor._calculate_sufficiency` (affects D1-Q3, D3-Q2, D5-Q2)
- `FinancialAuditor._detect_allocation_gaps` (affects D1-Q2, D4-Q4)
- `SemanticProcessor.chunk_text` (affects D1-Q1, D6-Q5)
- `BayesianMechanismInference._aggregate_bayesian_confidence` (affects D4-Q3, D5-Q2)

### Priority 2: MEDIUM IMPACT (Affects 1-2 executors)
- `FinancialAuditor._match_goal_to_budget` (affects D1-Q3, D3-Q3)
- `MechanismPartExtractor` methods (affects D1-Q4)
- `SemanticProcessor.embed_single` (affects D1-Q1)

### Priority 3: LOW IMPACT (Specialized functionality)
- `TeoriaCambio.export_nodes` (affects D6-Q1, has alternative)
- `CausalExtractor._classify_goal_type` (affects D4-Q1, has alternatives)
- `SemanticProcessor._detect_*` methods (affects D6-Q5, has alternatives)

## Success Metrics

- **Target**: 100% executor health (all methods available)
- **Current**: 60% executor health
- **Gap**: 40% (12 executors with issues)

**Next Milestone**: Implement Priority 1 methods to reach 80% health

## Audit Automation

This audit has been integrated into the audit suite:

```bash
# Run executor method audit only
python3 audit_executor_methods.py

# Run all audits (includes executor methods)
./run_all_audits.sh
```

**Report Files**:
- `audit_executor_methods_report.json` - Machine-readable detailed results
- `AUDIT_EXECUTOR_METHODS.md` - This human-readable report

## Conclusion

The executor method availability audit has identified **critical gaps** in method availability that may impact answer quality. With **20 concrete replacement suggestions** provided, the system can be quickly stabilized using existing methods while permanent implementations are developed.

**Immediate action is recommended** for Priority 1 methods to prevent degraded analysis quality in production.

---

**Audit Date**: 2025-12-11  
**Audit Tool**: audit_executor_methods.py  
**Executors Analyzed**: 30  
**Methods Scanned**: 642  
**Issues Found**: 14 missing methods across 12 executors
