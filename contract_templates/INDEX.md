# Contract Templates Quick Reference

## Templates Overview

| Template | Purpose | Primary Source | Size | Complexity |
|----------|---------|---------------|------|------------|
| `epistemological_foundation_template.json` | Document method paradigms, ontology, epistemology | Q002 (12 methods) | 28KB | Medium |
| `methodological_depth_template.json` | Complete technical specifications + integration docs | Q001 (17 methods) | 22KB | High |
| `assembly_rules_alignment.json` | Ensure complete method→assembly mapping | Q001 (perfect alignment) | 18KB | Low-Medium |

## Quick Selection Guide

### "I need to document..."

#### ...why a method uses Bayesian inference
→ Use `epistemological_foundation_template.json`
- Section: `epistemological_foundation_schema`
- Pattern: `best_practice_patterns.bayesian_methods`
- Reference: `reference_examples.q002_method_1_audit_direct_evidence`

#### ...how a method works algorithmically
→ Use `methodological_depth_template.json`
- Section: `method_documentation_schema.technical_approach`
- Include: algorithm, input, output, steps (5+), complexity, assumptions, limitations
- Reference: `reference_examples.q001_17_method_pipeline`

#### ...causal inference with Pearl's framework
→ Use `epistemological_foundation_template.json`
- Section: `best_practice_patterns.causal_inference_methods`
- Pattern: SCM/do-calculus/counterfactuals
- Reference: `reference_examples.q002_method_7_counterfactual_query`

#### ...how multiple methods integrate
→ Use `methodological_depth_template.json`
- Section: `method_combination_logic_schema`
- Include: combination_strategy, rationale, evidence_fusion, confidence_aggregation, execution_order, trade_offs, dependency_graph
- Reference: `reference_examples.q002_12_method_hierarchical_pipeline`

#### ...assembly rules for evidence fusion
→ Use `assembly_rules_alignment.json`
- Section: `alignment_patterns`
- Pattern: Choose from pattern_1 (all to graph), pattern_2 (typed concat), pattern_3 (wildcards), pattern_4 (hierarchical)
- Reference: `reference_examples.q001_perfect_alignment`

#### ...NLP entity extraction
→ Use `epistemological_foundation_template.json`
- Section: `best_practice_patterns.nlp_methods`
- Pattern: Neural/Rule-based with linguistic theory
- Reference: `reference_examples.q004_method_1_identify_responsible_entities`

#### ...statistical hypothesis testing
→ Use `epistemological_foundation_template.json`
- Section: `best_practice_patterns.statistical_testing_methods`
- Pattern: Frequentist with effect sizes
- Theory: Neyman-Pearson, Cohen (1988)

#### ...domain-specific hybrid methods
→ Use `epistemological_foundation_template.json`
- Section: `best_practice_patterns.domain_specific_methods`
- Pattern: Domain theory + computational method
- Reference: `reference_examples.q004_method_1_identify_responsible_entities` (Institutional Theory + NER)

## Template Components Map

### Epistemological Foundation Template

```
epistemological_foundation_schema/
├── paradigm (e.g., "Bayesian Evidential Reasoning")
├── ontological_basis (what exists/is real)
├── epistemological_stance (how knowledge is acquired)
├── theoretical_framework (4-6 academic references)
└── justification (why appropriate for question)

best_practice_patterns/
├── bayesian_methods
├── causal_inference_methods
├── statistical_testing_methods
├── nlp_methods
└── domain_specific_methods

reference_examples/
├── q002_method_1_audit_direct_evidence (Bayesian + SCM)
├── q002_method_7_counterfactual_query (Pearl's Ladder Level 3)
└── q004_method_1_identify_responsible_entities (Institutional + NER)
```

### Methodological Depth Template

```
method_documentation_schema/
├── method_name, class_name, priority, role
├── epistemological_foundation (see above)
├── technical_approach/
│   ├── algorithm
│   ├── input, output
│   ├── steps (5+ detailed)
│   ├── complexity (Big-O with variables)
│   ├── assumptions
│   └── limitations
└── output_interpretation/
    ├── output_structure (example)
    ├── interpretation_guide (thresholds)
    └── actionable_insights

method_combination_logic_schema/
├── combination_strategy
├── rationale
├── evidence_fusion
├── confidence_aggregation
├── execution_order
├── trade_offs
└── dependency_graph/
    ├── independent
    ├── dependent_chains
    ├── parallel_branches
    └── aggregation_sinks
```

### Assembly Rules Alignment Template

```
assembly_rules_schema/
└── [
    {
      target: "evidence_graph",
      sources: ["method1.provides", ...],
      merge_strategy: "graph_construction",
      description: "..."
    }
  ]

alignment_validation_rules/
├── rule_1_complete_coverage (CRITICAL)
├── rule_2_no_orphan_sources (WARNING)
├── rule_3_unique_provides (CRITICAL)
└── rule_4_evidence_graph_all_methods (HIGH)

alignment_patterns/
├── pattern_1_all_methods_to_graph (Q001)
├── pattern_2_typed_concatenation (Q002)
├── pattern_3_wildcard_aggregation
└── pattern_4_hierarchical_assembly

anti_patterns/
├── antipattern_1_incomplete_sources
├── antipattern_2_orphan_sources
├── antipattern_3_duplicate_provides
├── antipattern_4_missing_confidence_aggregation
└── antipattern_5_wrong_merge_strategy
```

## Common Use Cases

### Case 1: New Bayesian Method
1. Use `epistemological_foundation_template.json` → `best_practice_patterns.bayesian_methods`
2. Document paradigm: "Bayesian [Specific Application]"
3. Include 4+ references: Bayes' theorem, specific framework, domain application
4. Use `methodological_depth_template.json` → `technical_approach` with MCMC/conjugate update steps
5. Add to `assembly_rules_alignment.json` sources list

### Case 2: Causal Inference Pipeline
1. Use `epistemological_foundation_template.json` → `best_practice_patterns.causal_inference_methods`
2. Specify Pearl framework (do-calculus/counterfactuals/SCM)
3. Document intervention/counterfactual steps in `methodological_depth_template.json`
4. Use hierarchical assembly pattern (`alignment_patterns.pattern_4_hierarchical_assembly`)

### Case 3: Multi-Method Pipeline (10+ methods)
1. Document each method with `methodological_depth_template.json` structure
2. Create `method_combination_logic` section with:
   - Dependency graph showing execution order
   - Trade-offs analysis
   - Evidence fusion approach
3. Validate assembly with `assembly_rules_alignment.json` → `alignment_validation_rules`
4. Run validation pseudocode to ensure 100% coverage

### Case 4: NLP + Domain Theory Hybrid
1. Use `epistemological_foundation_template.json` → `best_practice_patterns.domain_specific_methods`
2. Document both computational (NER/parsing) and domain (institutional theory) foundations
3. Specify hybrid epistemology: "knowledge via computational extraction validated by domain theory"
4. Include references from both NLP literature and domain theory

## Quality Gates

Before finalizing contract, verify:

| Gate | Check | Template Section | Severity |
|------|-------|------------------|----------|
| Epistemological rigor | 4+ references, clear paradigm | `epistemological_foundation_template` | HIGH |
| Technical completeness | 5+ steps, complexity analysis | `methodological_depth_template` | HIGH |
| Assembly coverage | All method.provides in sources | `assembly_rules_alignment` rule_1 | CRITICAL |
| No orphan sources | All sources have methods | `assembly_rules_alignment` rule_2 | WARNING |
| Unique provides | No duplicate provides keys | `assembly_rules_alignment` rule_3 | CRITICAL |
| Integration docs | Dependency graph, trade-offs | `methodological_depth_template` | MEDIUM |
| Actionable insights | Output interpretation guide | `methodological_depth_template` | MEDIUM |

## File Sizes & Load Times

| File | Lines | Size | Typical Load Time |
|------|-------|------|-------------------|
| `epistemological_foundation_template.json` | 450+ | 28KB | <10ms |
| `methodological_depth_template.json` | 380+ | 22KB | <10ms |
| `assembly_rules_alignment.json` | 320+ | 18KB | <10ms |
| `README.md` | 400+ | 24KB | N/A (docs) |
| `INDEX.md` | 200+ | 12KB | N/A (this file) |

## Template Version Compatibility

| Template Version | Contract Version | Source Contracts | Date |
|-----------------|------------------|------------------|------|
| 1.0.0 | v3.0+ | Q001-Q004 v3 | 2025-11-28 |

## Next Steps

1. **Read** `README.md` for comprehensive documentation
2. **Browse** individual template files for detailed schemas
3. **Reference** Q001-Q004 contracts for real-world examples
4. **Validate** new contracts using alignment rules
5. **Contribute** new patterns as contracts evolve

---

*Last Updated: 2025-11-28*  
*Template Version: 1.0.0*  
*Source Contracts: Q001.v3, Q002.v3, Q003.v3, Q004.v3*
