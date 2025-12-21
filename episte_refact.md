# Epistemological Refactoring Guide for Executor Contracts

## Executive Summary

This guide provides a systematic methodology to refactor 30 executor contracts from a **flat epistemological architecture** to a **stratified epistemological architecture**. The refactoring addresses five specific structural deficiencies identified in the critical analysis:

1. `method_combination_logic` - Transform from flat sequential list to functional dependency graph
2. `merging_strategy` - Replace additive graph construction with functional layering
3. `evidence_fusion` - Implement asymmetric fusion respecting epistemological roles
4. `assembly_rules` - Decompose monolithic rules into discrete pipeline stages
5. `human_answer_structure` - Restructure narrative to reflect cognitive provenance

---

## Part I: Methodological Taxonomy

### 1.1 Epistemological Layer Classification System

Each method must be assigned to exactly one epistemological layer based on its **functional role**, not its implementation details.

#### **L1: EMPIRICAL** (Detection & Extraction)
**Functional Definition**: Methods that perform direct observation on source documents without interpretation or transformation.

**Classification Criteria**:
- **Input**: `PreprocesadoMetadata` or raw document structure
- **Output**: Literal extractions (strings, numbers, lists of observed entities)
- **Operation**: Pattern matching, regex, entity extraction, document traversal
- **Epistemic Status**: Produces **observations**, not **inferences**

**Method Signatures (examples)**:
```
TextMiningEngine.extract_*
IndustrialPolicyProcessor._extract_point_evidence
CausalExtractor._parse_goal_context (when extracting literal text)
PDETMunicipalPlanAnalyzer._extract_*
SemanticProcessor.chunk_text
CDAFFramework._extract_*
```

**Taxonomic Code**: `L1-EMP`

---

#### **L2: INFERENTIAL** (Analysis & Interpretation)
**Functional Definition**: Methods that transform empirical observations into analytical constructs (patterns, scores, probabilities, relationships).

**Classification Criteria**:
- **Input**: Outputs from L1 methods (observed facts)
- **Output**: Derived quantities (scores, probabilities, inferred relationships)
- **Operation**: Statistical analysis, scoring algorithms, embedding generation, pattern synthesis
- **Epistemic Status**: Produces **interpretations** and **inferences**

**Method Signatures (examples)**:
```
BayesianNumericalAnalyzer.*
SemanticProcessor.generate_embeddings
CausalExtractor.diagnose_critical_links (when inferring causality)
PDETMunicipalPlanAnalyzer._score_*
IndustrialPolicyProcessor._analyze_causal_dimensions
AdaptivePriorCalculator.calculate_*
```

**Taxonomic Code**: `L2-INF`

---

#### **L3: AUDIT** (Validation & Refutation)
**Functional Definition**: Methods that evaluate the **validity** and **coherence** of L1 and L2 outputs, with the capacity to suppress, modulate, or invalidate findings.

**Classification Criteria**:
- **Input**: Outputs from L1 and/or L2 methods
- **Output**: Validation flags, contradiction reports, confidence modulators
- **Operation**: Consistency checking, statistical testing, logical validation
- **Epistemic Status**: Produces **meta-judgments** about the reliability of other layers
- **Critical Property**: **Asymmetric influence** - can invalidate findings from L1/L2, but L1/L2 cannot invalidate L3

**Method Signatures (examples)**:
```
PolicyContradictionDetector.*
FinancialAuditor.*
CDAFFramework._validate_dnp_compliance
AdaptivePriorCalculator.validate_quality_criteria
ContradictionDetector.*
```

**Taxonomic Code**: `L3-AUD`

---

#### **L4: SYNTHESIS** (Integration & Narrative)
**Functional Definition**: Methods that construct human-readable narratives by integrating outputs from all preceding layers.

**Classification Criteria**:
- **Input**: Outputs from L1, L2, and L3
- **Output**: Structured narratives, reports, human-readable summaries
- **Operation**: Template population, narrative construction, synthesis
- **Epistemic Status**: Produces **communicative artifacts**, not new evidence

**Method Signatures (examples)**:
```
CDAFFramework._generate_dnp_report
Carver.generate_human_answer
SemanticProcessor.synthesize_*
Any method matching pattern *_generate_report, *_synthesize_*
```

**Taxonomic Code**: `L4-SYN`

---

### 1.2 Dependency Mapping Rules

**Strict Hierarchy**:
```
L1 → L2 → L3 → L4
```

**Valid Dependencies**:
- L1: `[]` (no dependencies, operates on raw documents)
- L2: `[L1]` (depends on empirical observations)
- L3: `[L1, L2]` (depends on both observations and inferences)
- L4: `[L1, L2, L3]` (depends on all prior layers)

**Invalid Dependencies**:
- L1 depending on L2, L3, or L4
- L2 depending on L3 or L4
- L3 depending on L4
- Any circular dependencies

---

## Part II: Refactoring Procedure

### 2.1 Analysis Phase: Method Classification

**For each contract, execute the following:**

#### Step 2.1.1: Extract Method Inventory
Locate `method_binding.methods` array and enumerate all methods:

```python
methods = contract["method_binding"]["methods"]
method_inventory = [
    {
        "class_name": m["class_name"],
        "method_name": m["method_name"],
        "provides": m["provides"],
        "priority": m["priority"]
    }
    for m in methods
]
```

#### Step 2.1.2: Apply Classification Algorithm

For each method in inventory:

1. **Lexical Analysis**:
   - If `method_name` matches `^(extract|parse|mine|chunk)_`: Candidate for **L1-EMP**
   - If `method_name` matches `^(analyze|score|calculate|infer)_`: Candidate for **L2-INF**
   - If `method_name` matches `^(validate|detect|audit|check)_`: Candidate for **L3-AUD**
   - If `method_name` matches `^(generate|synthesize|report)_`: Candidate for **L4-SYN**

2. **Functional Analysis**:
   - Examine the method's docstring or implementation
   - Identify actual input and output types
   - Confirm epistemic role (observation vs inference vs validation vs synthesis)

3. **Dependency Analysis**:
   - Determine what data the method requires to execute
   - If requires only `PreprocesadoMetadata`: **L1-EMP**
   - If requires L1 outputs: **L2-INF** or **L3-AUD**
   - If requires L1+L2 outputs: **L3-AUD**
   - If requires L1+L2+L3 outputs: **L4-SYN**

4. **Assignment**:
   Assign taxonomic code and document rationale.

#### Step 2.1.3: Construct Classification Table

Create a structured representation:

```json
{
  "contract_id": "Q230",
  "method_classification": [
    {
      "class_name": "PDETMunicipalPlanAnalyzer",
      "method_name": "_score_pdet_alignment",
      "layer": "L2-INF",
      "rationale": "Computes alignment score (inference) from extracted PDET elements (L1)",
      "dependencies": ["L1"],
      "provides": "pdet_analysis.score_pdet_alignment"
    },
    {
      "class_name": "CDAFFramework",
      "method_name": "_validate_dnp_compliance",
      "layer": "L3-AUD",
      "rationale": "Validates compliance (audit) against DNP standards",
      "dependencies": ["L1", "L2"],
      "provides": "cdafframework.validate_dnp_compliance"
    }
  ]
}
```

---

### 2.2 Refactoring Phase 1: `method_binding` Restructuring

**Objective**: Replace flat `methods` array with hierarchical `execution_graph`.

#### Step 2.2.1: Identify Current Structure

Locate in contract:
```json
"method_binding": {
  "orchestration_mode": "multi_method_pipeline",
  "method_count": N,
  "methods": [ ... ]
}
```

#### Step 2.2.2: Construct `execution_graph`

**Template Structure**:
```json
"method_binding": {
  "orchestration_mode": "epistemological_pipeline",
  "method_count": N,
  "execution_graph": {
    "L1_empirical": {
      "description": "Empirical observation layer - direct document extraction",
      "methods": [ /* Methods classified as L1-EMP */ ],
      "dependencies": [],
      "output_target": "raw_facts"
    },
    "L2_inferential": {
      "description": "Inferential analysis layer - transformation of observations into analytical constructs",
      "methods": [ /* Methods classified as L2-INF */ ],
      "dependencies": ["L1_empirical"],
      "output_target": "inferences"
    },
    "L3_audit": {
      "description": "Audit layer - validation and refutation of prior layers",
      "methods": [ /* Methods classified as L3-AUD */ ],
      "dependencies": ["L1_empirical", "L2_inferential"],
      "output_target": "audit_results",
      "fusion_mode": "modulation"
    },
    "L4_synthesis": {
      "description": "Synthesis layer - narrative construction for human consumption",
      "methods": [ /* Methods classified as L4-SYN */ ],
      "dependencies": ["L1_empirical", "L2_inferential", "L3_audit"],
      "output_target": "final_narrative"
    }
  }
}
```

#### Step 2.2.3: Populate Method Arrays

For each layer, populate `methods` array with methods matching that layer's taxonomic code:

**Method Entry Schema**:
```json
{
  "class_name": "string",
  "method_name": "string",
  "provides": "string (dot-notation key)",
  "role": "string (taxonomic code)",
  "description": "string",
  "requires": ["array of dependency keys"] // Only for L2, L3, L4
}
```

**Example for L3**:
```json
"L3_audit": {
  "methods": [
    {
      "class_name": "CDAFFramework",
      "method_name": "_validate_dnp_compliance",
      "provides": "cdafframework.validate_dnp_compliance",
      "role": "L3-AUD",
      "description": "Validates compliance with DNP standards",
      "requires": ["raw_facts", "inferences"],
      "modulates": ["raw_facts.confidence", "inferences.confidence"]
    }
  ]
}
```

**Critical Addition for L3 Methods**: Include `modulates` field specifying which confidence values from L1/L2 can be affected.

---

### 2.3 Refactoring Phase 2: `assembly_rules` Decomposition

**Objective**: Transform monolithic assembly rule into four discrete pipeline stages.

#### Step 2.3.1: Identify Current Structure

Locate in contract:
```json
"assembly_rules": [
  {
    "target": "evidence_graph" | "elements_found",
    "sources": [ /* flat list of all method provides keys */ ],
    "merge_strategy": "graph_construction" | "concat"
  }
]
```

#### Step 2.3.2: Define Four Discrete Rules

Replace entire `assembly_rules` array with:

```json
"assembly_rules": [
  {
    "rule_id": "R1_empirical_consolidation",
    "description": "Consolidate empirical observations from L1 methods",
    "target": "raw_facts",
    "sources": [
      /* List all "provides" keys from L1-EMP methods */
    ],
    "merge_strategy": "concat_with_deduplication",
    "deduplication_key": "element_id",
    "confidence_propagation": "preserve_individual"
  },
  
  {
    "rule_id": "R2_inferential_aggregation",
    "description": "Aggregate analytical inferences from L2 methods",
    "target": "inferences",
    "sources": [
      /* List all "provides" keys from L2-INF methods */
    ],
    "input_dependencies": ["raw_facts"],
    "merge_strategy": "weighted_aggregation",
    "confidence_propagation": "conservative_bayesian"
  },
  
  {
    "rule_id": "R3_audit_modulation",
    "description": "Apply audit results to modulate confidence of L1 and L2 outputs",
    "target": "validated_facts",
    "sources": [
      /* List all "provides" keys from L3-AUD methods */
    ],
    "input_dependencies": ["raw_facts", "inferences"],
    "merge_strategy": "confidence_modulation",
    "modulation_rules": {
      "contradiction_detected": {
        "action": "suppress_fact",
        "confidence_multiplier": 0.0,
        "flag": "CONTRADICTION"
      },
      "validation_failure": {
        "action": "reduce_confidence",
        "confidence_multiplier": 0.5,
        "flag": "VALIDATION_FAILURE"
      },
      "high_uncertainty": {
        "action": "flag_caution",
        "confidence_multiplier": 0.7,
        "flag": "HIGH_UNCERTAINTY"
      }
    }
  },
  
  {
    "rule_id": "R4_narrative_synthesis",
    "description": "Construct human-readable narrative from all layers",
    "target": "human_answer",
    "sources": [
      /* List all "provides" keys from L4-SYN methods */
    ],
    "input_dependencies": ["validated_facts", "inferences", "audit_results"],
    "merge_strategy": "narrative_construction"
  }
]
```

#### Step 2.3.3: Populate `sources` Arrays

**For R1**: Extract all `provides` keys from methods classified as L1-EMP
**For R2**: Extract all `provides` keys from methods classified as L2-INF
**For R3**: Extract all `provides` keys from methods classified as L3-AUD
**For R4**: Extract all `provides` keys from methods classified as L4-SYN

---

### 2.4 Refactoring Phase 3: `evidence_fusion` Specification

**Objective**: Define layer-specific fusion strategies that respect epistemological asymmetry.

#### Step 2.4.1: Add `fusion_specification` Section

Insert as new top-level key in contract:

```json
"fusion_specification": {
  "L1_empirical_fusion": {
    "strategy": "corroborative_aggregation",
    "description": "Multiple detections of same fact increase confidence via Bayesian updating",
    "algorithm": "independent_corroboration",
    "formula": "P(fact|A,B) ∝ P(fact|A) × P(fact|B)",
    "independence_assumption": true
  },
  
  "L2_inferential_fusion": {
    "strategy": "coherence_alignment",
    "description": "Inferences must satisfy logical consistency constraints",
    "algorithm": "constraint_satisfaction",
    "independence_assumption": false,
    "conflict_resolution": "weighted_voting",
    "coherence_threshold": 0.7
  },
  
  "L3_audit_fusion": {
    "strategy": "asymmetric_modulation",
    "description": "Audit failures can suppress or modulate L1/L2 findings",
    "algorithm": "veto_gate_with_multiplier",
    "asymmetry_principle": "audit_dominates",
    "suppression_rules": {
      "contradiction_detected": {
        "action": "suppress_fact",
        "rationale": "Logical contradiction invalidates factual claim"
      },
      "validation_failure": {
        "action": "reduce_confidence",
        "multiplier": 0.5,
        "rationale": "Failed validation reduces but does not eliminate evidence"
      }
    }
  },
  
  "cross_layer_fusion": {
    "L1_to_L2": "forward_propagation",
    "L2_to_L3": "audit_submission",
    "L3_to_L1": "confidence_backpropagation",
    "L3_to_L2": "inference_modulation"
  }
}
```

**Critical Point**: The `L3_audit_fusion` strategy is **not additive**. It can **veto** or **suppress** findings from L1 and L2, which is fundamentally different from how L1 and L2 interact.

---

### 2.5 Refactoring Phase 4: `human_answer_structure` Stratification

**Objective**: Restructure narrative template to articulate epistemological provenance.

#### Step 2.5.1: Identify Current Structure

Locate in contract:
```json
"human_answer_structure": {
  "format": "markdown",
  "template": {
    "title": "...",
    "summary": "...",
    "score_section": "...",
    "elements_section": "..."
  }
}
```

#### Step 2.5.2: Replace with Stratified Template

```json
"human_answer_structure": {
  "format": "markdown",
  "template_mode": "epistemological_narrative",
  "sections": [
    {
      "section_id": "S1_empirical_base",
      "title": "### 1. Empirical Base: Observed Facts",
      "layer": "L1",
      "data_source": "validated_facts",
      "narrative_style": "descriptive",
      "template": "**Observed Elements**: {fact_count} factual elements detected across {document_coverage_pct}% of analyzed text.\n\n**Official Sources Identified**: {official_sources_list}\n\n**Quantitative Indicators**: {quantitative_indicators_list}\n\n**Temporal Coverage**: {temporal_series}",
      "epistemological_note": "These are direct observations from source documents without interpretive transformation."
    },
    
    {
      "section_id": "S2_inferential_analysis",
      "title": "### 2. Inferential Analysis: Patterns and Relationships",
      "layer": "L2",
      "data_source": "inferences",
      "narrative_style": "analytical",
      "template": "**Probabilistic Assessment**: {bayesian_summary}\n\n**Causal Linkages**: {causal_links_summary}\n\n**Alignment Scores**: {alignment_scores}\n\n**Confidence Metrics**: Mean confidence = {mean_confidence}, σ = {std_confidence}",
      "epistemological_note": "These are analytical constructs derived from empirical observations, representing inferred patterns and relationships."
    },
    
    {
      "section_id": "S3_audit_findings",
      "title": "### 3. Audit Layer: Robustness and Limitations",
      "layer": "L3",
      "data_source": "audit_results",
      "narrative_style": "critical",
      "template": "**Validation Results**: {validation_summary}\n\n**Contradictions Detected**: {contradiction_count}\n- {contradiction_details}\n\n**Suppressed Facts**: {suppressed_facts_count} empirical observations were suppressed due to:\n- {suppression_reasons}\n\n**Confidence Modulations**: {confidence_adjustment_summary}\n\n**Methodological Limitations**: {limitations_list}",
      "epistemological_note": "This section presents meta-judgments about the reliability and coherence of prior layers, including identified weaknesses and contradictions."
    },
    
    {
      "section_id": "S4_integrated_synthesis",
      "title": "### 4. Integrated Synthesis: Policy Implications",
      "layer": "L4",
      "data_source": "final_narrative",
      "narrative_style": "argumentative",
      "template": "**Verdict**: {verdict}\n\n**Synthetic Interpretation**: {integrated_interpretation}\n\n**Policy Recommendations**: {recommendations}\n\n**Epistemological Guarantee**: This analysis integrates {method_count} methods across 4 epistemological layers. Final confidence: {final_confidence_pct}%, modulated by {audit_count} validation checks.",
      "epistemological_note": "This synthesis integrates all epistemological layers into an actionable narrative, explicitly acknowledging the provenance and reliability of constituent elements."
    }
  ],
  
  "confidence_interpretation": {
    "high": "≥80%: Multiple corroborating observations, no contradictions, passed all audits",
    "medium": "50-79%: Evidence present but with limitations or minor inconsistencies",
    "low": "<50%: Weak evidence, contradictions detected, or failed validation"
  }
}
```

---

### 2.6 Refactoring Phase 5: Metadata Updates

#### Step 2.6.1: Update Contract Version

Locate `identity.contract_version` and update:
```json
"identity": {
  "contract_version": "4.0.0-epistemological",
  "refactoring_date": "<ISO-8601 timestamp>",
  "refactoring_rationale": "Stratified epistemological architecture to address flatness critique"
}
```

#### Step 2.6.2: Add Refactoring Provenance

In `traceability` section, add:
```json
"traceability": {
  "refactoring_history": [
    {
      "from_version": "3.0.0",
      "to_version": "4.0.0-epistemological",
      "date": "<ISO-8601 timestamp>",
      "rationale": "Transformed from flat method list to hierarchical execution graph with epistemological stratification",
      "changes": [
        "Introduced execution_graph in method_binding",
        "Decomposed assembly_rules into 4-stage pipeline",
        "Added fusion_specification with asymmetric L3 modulation",
        "Restructured human_answer_structure with 4 epistemological sections"
      ]
    }
  ]
}
```

---

## Part III: Validation Procedures

### 3.1 Structural Validation Checklist

For each refactored contract, verify:

- [ ] All methods from original `methods` array are present in `execution_graph`
- [ ] Each method is assigned to exactly one layer (L1, L2, L3, or L4)
- [ ] Dependency declarations are consistent with layer hierarchy
- [ ] `assembly_rules` contains exactly 4 rules (R1, R2, R3, R4)
- [ ] `sources` arrays in assembly rules collectively cover all method `provides` keys
- [ ] `fusion_specification` section is present with all 3 layer-specific strategies
- [ ] `human_answer_structure` contains 4 sections (S1, S2, S3, S4)
- [ ] Contract version updated to `4.0.0-epistemological`

### 3.2 Logical Validation Checks

**Dependency Acyclicity**:
```python
def validate_no_cycles(execution_graph):
    for layer in ["L2_inferential", "L3_audit", "L4_synthesis"]:
        for dep in execution_graph[layer]["dependencies"]:
            assert dep in ["L1_empirical", "L2_inferential", "L3_audit"]
            # Ensure no forward references
```

**Coverage Completeness**:
```python
def validate_coverage(execution_graph, assembly_rules):
    all_provides = [m["provides"] for layer in execution_graph.values() 
                    for m in layer["methods"]]
    all_sources = [s for rule in assembly_rules for s in rule["sources"]]
    assert set(all_provides) == set(all_sources)
```

---

## Part IV: Implementation Notes

### 4.1 NO Modification to Existing Fields

**Do NOT modify**:
- `question_context`
- `signal_requirements`
- `output_contract`
- `validation_rules`
- `error_handling`
- `fallback_strategy`
- `test_configuration`
- `compatibility`
- `calibration`
- `method_outputs`

These sections remain unchanged. The refactoring is strictly limited to the five identified sections.

### 4.2 Preservation of `provides` Keys

All `provides` keys from original methods must be preserved exactly. They serve as the contract's interface specification and changing them would break downstream consumers.

### 4.3 Backward Compatibility Considerations

While the structure changes significantly, the contract must continue to specify:
- The same set of methods
- The same `provides` keys
- The same overall outputs

The refactoring changes **how** methods are organized and **how** their outputs are fused, not **what** methods are executed or **what** they produce.

---

## Part V: Taxonomy Reference

### Classification Decision Tree

```
Method M:
│
├─ Does M directly read PreprocesadoMetadata?
│  ├─ YES → Does M perform transformation/interpretation?
│  │  ├─ NO → L1-EMP
│  │  └─ YES → Examine output type
│  │     ├─ Literal extractions → L1-EMP
│  │     └─ Derived quantities → L2-INF
│  └─ NO → What does M consume?
│     ├─ L1 outputs only → Does M validate or infer?
│     │  ├─ Validate → L3-AUD
│     │  └─ Infer → L2-INF
│     ├─ L1 + L2 outputs → Does M validate or synthesize?
│     │  ├─ Validate → L3-AUD
│     │  └─ Synthesize → L4-SYN
│     └─ L1 + L2 + L3 outputs → L4-SYN
```

### Taxonomic Codes Summary

| Code | Layer | Function | Input | Output | Symmetry |
|------|-------|----------|-------|--------|----------|
| L1-EMP | Empirical | Detection | Raw doc | Observations | Additive |
| L2-INF | Inferential | Analysis | L1 | Inferences | Additive |
| L3-AUD | Audit | Validation | L1, L2 | Flags | **Asymmetric** |
| L4-SYN | Synthesis | Narrative | L1, L2, L3 | Text | N/A |

---

## Conclusion

This guide provides a deterministic procedure for refactoring all 30 contracts. The key principles are:

1. **Classification before refactoring**: Understand what each method does epistemologically
2. **Strict hierarchy enforcement**: L1 → L2 → L3 → L4, no exceptions
3. **Asymmetric fusion for L3**: Audits can veto findings, not merely "contribute evidence"
4. **Narrative stratification**: Human output must articulate cognitive provenance
5. **Preservation of interface**: All `provides` keys and method signatures remain unchanged

The refactoring addresses the epistemological flatness critique while maintaining full backward compatibility at the interface level.
