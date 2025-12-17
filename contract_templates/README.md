# Contract Templates - Best Practices from Q001-Q004

This directory contains reusable templates extracted from the best practices observed in Q001-Q004 executor contracts. These templates capture patterns for epistemological rigor, methodological depth, and structural alignment that ensure high-quality contract documentation.

## Template Files

### 1. `epistemological_foundation_template.json`
**Purpose**: Captures Q002's detailed Bayesian/causal paradigm documentation structure

**Key Features**:
- Complete epistemological foundation schema (paradigm, ontological_basis, epistemological_stance, theoretical_framework, justification)
- Best practice patterns for different method types (Bayesian, causal inference, statistical testing, NLP, domain-specific)
- 6+ academic references with specific contributions per method
- Explicit connection between question requirements and paradigm capabilities

**Derived From**:
- Q002.v3.json: 12 methods with comprehensive epistemological foundations
- Q001.v3.json: Structural causal models and evidence graph paradigms
- Q004.v3.json: Institutional theory + NLP hybrid epistemologies

**When to Use**: Apply when documenting methods that require rigorous epistemological grounding, particularly:
- Bayesian methods requiring prior specification and belief updating
- Causal inference methods using Pearl's framework or counterfactuals
- Statistical testing with hypothesis testing or effect size estimation
- NLP methods combining linguistic theory with computational extraction
- Domain-specific methods integrating theoretical frameworks with computational analysis

**Reference Examples**:
- `q002_method_1_audit_direct_evidence`: Bayesian evidential reasoning with SCM-informed priors
- `q002_method_7_counterfactual_query`: Pearl's Ladder of Causation Level 3
- `q004_method_1_identify_responsible_entities`: Institutional Theory + NER hybrid

---

### 2. `methodological_depth_template.json`
**Purpose**: Captures Q001's 17-method documentation structure for comprehensive technical specifications

**Key Features**:
- Complete method documentation schema (method_name, class_name, priority, role, epistemological_foundation, technical_approach, output_interpretation)
- Technical approach with algorithm, input/output, 5+ steps, complexity analysis, assumptions, limitations
- Output interpretation with thresholds, interpretation guide, and actionable insights
- Method combination logic documenting strategy, rationale, evidence fusion, confidence aggregation, execution order, trade-offs
- Dependency graph visualization (independent roots, sequential chains, parallel branches, aggregation sinks)

**Derived From**:
- Q001.v3.json: 17 methods with complete technical documentation
- Q002.v3.json: 12 methods with detailed algorithmic specifications and 4-layer hierarchical pipeline
- Q003.v3.json: 13 methods with financial analysis workflows
- Q004.v3.json: 11 methods with NLP pipeline specifications

**When to Use**: Apply when documenting complex multi-method pipelines (3+ methods) requiring:
- Detailed algorithmic specifications
- Integration documentation across multiple methods
- Dependency management and execution sequencing
- Trade-off analysis between competing design goals

**Reference Examples**:
- `q001_17_method_pipeline`: Sequential pipeline with graph-based evidence fusion
- `q002_12_method_hierarchical_pipeline`: Four-layer hierarchy with Dempster-Shafer fusion and counterfactual validation

---

### 3. `assembly_rules_alignment.json`
**Purpose**: Captures Q001's perfect method→provides→sources mapping for ensuring complete evidence assembly

**Key Features**:
- Core principle: Every method.provides MUST appear in assembly_rules[].sources
- Alignment validation rules (complete coverage, no orphan sources, unique provides, evidence graph completeness)
- Assembly patterns (all methods to graph, typed concatenation, wildcard aggregation, hierarchical multi-stage)
- Implementation guidelines (enumerate methods, design strategy, write rules, validate alignment, document merge strategies)
- Anti-patterns with detection and fixes
- Validation tool pseudocode for automated checking

**Derived From**:
- Q001.v3.json: Perfect alignment of 17 methods with assembly_rules sources
- Q002.v3.json: 12 methods with complete assembly coverage
- Q003.v3.json: 13 methods mapped to evidence graph construction
- Q004.v3.json: 11 methods with consolidated entity assembly

**When to Use**: Apply when writing or validating evidence_assembly.assembly_rules to ensure:
- No method output is lost during assembly
- All assembly sources have corresponding methods
- Merge strategies are appropriate for data types
- Hierarchical assembly stages are correctly sequenced

**Validation Rules**:
1. **Complete Coverage** (CRITICAL): Every method.provides in at least one assembly_rule.sources
2. **No Orphan Sources** (WARNING): Every non-wildcard source has corresponding method.provides
3. **Unique Provides** (CRITICAL): No duplicate method.provides keys
4. **Evidence Graph All Methods** (HIGH): If using graph_construction, sources includes ALL methods

---

## Usage Guidelines

### Quick Start

1. **Choose appropriate template** based on task:
   - Documenting method epistemology → `epistemological_foundation_template.json`
   - Writing comprehensive method documentation → `methodological_depth_template.json`
   - Validating assembly rules → `assembly_rules_alignment.json`

2. **Follow template structure**:
   - Copy relevant sections from template
   - Replace placeholder values with method-specific content
   - Ensure all required fields are populated

3. **Validate against quality indicators**:
   - Epistemological: 4+ references, explicit paradigm attribution, clear justification
   - Methodological: 5+ algorithmic steps, complexity analysis, threshold-based interpretation
   - Assembly: 100% method coverage in sources, appropriate merge strategies

### Integration with Contracts

These templates are designed to be integrated into executor contracts (v3.0+) in the following sections:

```json
{
  "method_binding": {
    "methods": [
      {
        "class_name": "...",
        "method_name": "...",
        "priority": 1,
        "provides": "...",
        "role": "...",
        "description": "..."
      }
    ]
  },
  "evidence_assembly": {
    "assembly_rules": [
      /* Use assembly_rules_alignment.json patterns here */
    ]
  },
  "output_contract": {
    "human_readable_output": {
      "methodological_depth": {
        "methods": [
          /* Use methodological_depth_template.json + epistemological_foundation_template.json here */
        ],
        "method_combination_logic": {
          /* Use methodological_depth_template.json method_combination_logic_schema here */
        }
      }
    }
  }
}
```

### Quality Checklist

Before finalizing a contract using these templates, verify:

#### Epistemological Foundation
- [ ] Paradigm named and attributed to foundational work
- [ ] Ontological basis specifies what exists/is measurable
- [ ] Epistemological stance clarifies knowledge acquisition process
- [ ] 4+ theoretical framework references with specific contributions
- [ ] Justification links question requirements to paradigm strengths

#### Methodological Depth
- [ ] Algorithm description is concrete and implementable
- [ ] Input/output types are fully specified
- [ ] 5+ algorithmic steps with sufficient detail
- [ ] Complexity analysis with variable definitions
- [ ] Assumptions and limitations explicitly stated
- [ ] Output interpretation provides threshold-based decision rules
- [ ] Actionable insights connect outputs to question evaluation

#### Assembly Rules Alignment
- [ ] Every method.provides appears in assembly_rules[].sources
- [ ] No orphan sources (non-wildcard sources have corresponding methods)
- [ ] Unique method.provides keys (no duplicates)
- [ ] If graph_construction: sources includes ALL methods
- [ ] Merge strategies appropriate for data types
- [ ] Clear descriptions for each assembly rule

---

## Best Practice Patterns

### Bayesian Methods
**Epistemology**: Critical Bayesian with corpus-informed priors  
**Technical**: Hierarchical modeling with MCMC or conjugate updates  
**Assembly**: Belief propagation via Dempster-Shafer across evidence graph

### Causal Inference Methods
**Epistemology**: Interventionist causality (Pearl's framework)  
**Technical**: SCM with do-calculus, graph surgery, or twin networks  
**Assembly**: Causal edge inference (CAUSES, SUPPORTS, CONTRADICTS)

### Statistical Testing Methods
**Epistemology**: Falsificationist (Neyman-Pearson)  
**Technical**: Hypothesis testing with effect size quantification  
**Assembly**: Contradiction detection via pairwise claim comparison

### NLP Methods
**Epistemology**: Supervised learning or rule-based linguistic  
**Technical**: Neural sequence labeling or dependency parsing  
**Assembly**: Entity consolidation via fuzzy matching + coreference

### Hybrid Domain Methods
**Epistemology**: Domain theory + computational extraction  
**Technical**: Theory-guided feature engineering + ML/NLP  
**Assembly**: Domain-validated evidence nodes with theoretical constraints

---

## Template Evolution

These templates are extracted from Q001-Q004 (v3.0 contracts) and represent current best practices as of 2025-11-28. As additional high-quality contracts are developed, these templates will be updated to incorporate new patterns.

### Version History
- **v1.0.0** (2025-11-28): Initial extraction from Q001-Q004
  - Epistemological foundation template (Q002 paradigm depth)
  - Methodological depth template (Q001 17-method structure)
  - Assembly rules alignment (Q001 perfect mapping)

### Contributing
When creating new contracts with novel best practices:
1. Document the pattern in the contract's methodological_depth section
2. If the pattern is reusable, propose an update to the relevant template
3. Include reference examples from the new contract
4. Update version history

---

## References

### Source Contracts
- **Q001.v3.json**: 17 methods, perfect assembly alignment, comprehensive epistemological foundations
- **Q002.v3.json**: 12 methods, detailed Bayesian/causal paradigms, 4-layer hierarchical pipeline
- **Q003.v3.json**: 13 methods, financial analysis workflows, EvidenceNexus integration
- **Q004.v3.json**: 11 methods, institutional theory + NLP hybrid, entity consolidation pipeline

### Theoretical Foundations
- Pearl, J. (2000). *Causality: Models, Reasoning, and Inference*. Cambridge University Press.
- Pearl, J., & Mackenzie, D. (2018). *The Book of Why*. Basic Books.
- Gelman, A., et al. (2013). *Bayesian Data Analysis* (3rd ed.). CRC Press.
- Jaynes, E.T. (2003). *Probability Theory: The Logic of Science*. Cambridge University Press.

### Colombian Policy Context
- Ley 1257 de 2008: Gender violence prevention framework
- Decreto 111 de 1996: Estatuto Orgánico de Presupuesto
- Ley 489 de 1998: Administrative structure norms
- Conpes 161/2013: Gender equality policy guidelines

---

## Contact

For questions about these templates or to propose enhancements:
- Review existing contracts in `src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/`
- Consult `AGENTS.md` for F.A.R.F.A.N architecture overview
- Follow contract v3.0 schema: `executor_contract.v3.schema.json`
