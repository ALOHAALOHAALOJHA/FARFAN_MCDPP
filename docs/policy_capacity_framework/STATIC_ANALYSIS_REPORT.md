# Static Analysis Report
## Policy Capacity Mapping from Source Code

**Generated:** static_analysis_capacity_mapper.py  
**Trusted Source:** episteme_rules.md  
**Total Methods:** 652

---

## Methodology

This analysis performs **static code analysis** of Python source files in
`src/farfan_pipeline/methods/` to classify methods according to episteme_rules.md.

### Untrusted Sources (Ignored)

All existing JSON classification files are considered UNTRUSTED and ignored:
- `classified_methods.json`
- `method_sets_by_question.json`
- `METHODS_OPERACIONALIZACION.json`
- `METHODS_TO_QUESTIONS_AND_FILES.json`

### Classification Rules

Classification is based on:

1. **Class name matching** (confidence: 0.9)
2. **Method name prefix matching** (confidence: 0.8)
3. **Method name keyword matching** (confidence: 0.6)

---

## Results

### Epistemological Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| N1-EMP | 165 | 25.3% |
| N2-INF | 379 | 58.1% |
| N3-AUD | 108 | 16.6% |

### Policy Capacity Distribution

| Capacity Type | Count | Percentage |
|---------------|-------|------------|
| CA-I | 165 | 25.3% |
| CA-O | 338 | 51.8% |
| CO-O | 41 | 6.3% |
| CO-S | 94 | 14.4% |
| CP-O | 14 | 2.1% |

### Classification Confidence

| Level | Count |
|-------|-------|
| High (≥0.8) | 403 |
| Medium (≥0.5) | 27 |
| Low (<0.5) | 222 |

---

## Sample Methods

First 20 methods with high confidence classification:

| Class | Method | File | Level | Capacity | Confidence |
|-------|--------|------|-------|----------|------------|
| AdvancedSemanticChunker | chunk_document | embedding_policy.py | N1-EMP | CA-I | 0.80 |
| AdvancedSemanticChunker | _extract_sections | embedding_policy.py | N1-EMP | CA-I | 0.80 |
| AdvancedSemanticChunker | _extract_tables | embedding_policy.py | N1-EMP | CA-I | 0.80 |
| AdvancedSemanticChunker | _extract_lists | embedding_policy.py | N1-EMP | CA-I | 0.80 |
| AdvancedSemanticChunker | _infer_pdq_context | embedding_policy.py | N2-INF | CA-O | 0.80 |
| BayesianNumericalAnalyzer | evaluate_policy_metric | embedding_policy.py | N2-INF | CA-O | 0.90 |
| BayesianNumericalAnalyzer | _beta_binomial_posterior | embedding_policy.py | N2-INF | CA-O | 0.90 |
| BayesianNumericalAnalyzer | _normal_normal_posterior | embedding_policy.py | N2-INF | CA-O | 0.90 |
| BayesianNumericalAnalyzer | _classify_evidence_strength | embedding_policy.py | N2-INF | CA-O | 0.90 |
| BayesianNumericalAnalyzer | _compute_coherence | embedding_policy.py | N2-INF | CA-O | 0.90 |
| BayesianNumericalAnalyzer | _null_evaluation | embedding_policy.py | N2-INF | CA-O | 0.90 |
| BayesianNumericalAnalyzer | serialize_posterior_samples | embedding_policy.py | N2-INF | CA-O | 0.90 |
| BayesianNumericalAnalyzer | compare_policies | embedding_policy.py | N2-INF | CA-O | 0.90 |
| PolicyAnalysisEmbedder | process_document | embedding_policy.py | N2-INF | CA-O | 0.80 |
| PolicyAnalysisEmbedder | evaluate_policy_numerical_consistency | embedding_policy.py | N2-INF | CA-O | 0.80 |
| PolicyAnalysisEmbedder | compare_policy_interventions | embedding_policy.py | N2-INF | CA-O | 0.80 |
| PolicyAnalysisEmbedder | _embed_texts | embedding_policy.py | N2-INF | CA-O | 0.80 |
| PolicyAnalysisEmbedder | _extract_numerical_values | embedding_policy.py | N1-EMP | CA-I | 0.80 |
| PolicyAnalysisEmbedder | _compute_overall_confidence | embedding_policy.py | N2-INF | CA-O | 0.80 |
| EmbeddingPolicyProducer | process_document | embedding_policy.py | N2-INF | CA-O | 0.80 |

---

## Complete Method List

See `static_analysis_results.json` for complete details.
