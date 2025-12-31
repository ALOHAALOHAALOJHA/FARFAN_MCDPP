# Questionnaire Monolith: Gap Analysis & Sub-Issue Breakdown
## Actionable Roadmap for Equitable Enrichment

**Date:** 2025-12-31  
**Based on:** Comprehensive Audit Report v1.0.0  
**Status:** READY FOR IMPLEMENTATION

---

## Overview

This document breaks down the audit findings into **8 discrete, actionable sub-issues** that can be addressed independently and tracked for progress. Each sub-issue includes:
- **Scope**: What needs to be done
- **Impact**: Why it matters
- **Acceptance Criteria**: How to measure completion
- **Estimated Effort**: Time/complexity estimate
- **Dependencies**: What must be done first

---

## Sub-Issue 1: Audit & Normalize Signal & Expected Elements Richness

### Status: 🔴 CRITICAL
**Priority:** P0 (Immediate)

### Gap Identified
- **Expected Elements**: ✅ 100% coverage, well-implemented
- **Signals**: ❌ 0% coverage (300/300 questions missing signals)

### Scope
1. Define signal taxonomy (keyword_presence, semantic_pattern, intensity_measure, quality_indicator, etc.)
2. Populate 3-5 signals per question across all 300 micro questions
3. Ensure signals are dimension-appropriate and policy-area-sensitive
4. Validate signal coverage is equitable across all dimensions and clusters

### Acceptance Criteria
- [ ] Signal taxonomy documented with 10-15 signal types
- [ ] 100% of questions have ≥3 signals defined
- [ ] Signal distribution is balanced (±20%) across dimensions
- [ ] All signals have clear validation logic
- [ ] Automated test suite validates signal structure

### Impact
**High Impact on:**
- Document analysis quality
- Evidence detection accuracy
- Weak-signal identification
- Semantic similarity matching

### Estimated Effort
- **Time**: 3-4 weeks
- **Complexity**: Medium-High
- **Resources**: 1 data scientist + 1 domain expert

### Dependencies
- None (can start immediately)

### Implementation Notes
```json
// Example signal structure to implement
"signals": [
  {
    "signal_id": "SIG001",
    "type": "keyword_presence",
    "keywords": ["diagnóstico", "situación actual", "problema"],
    "weight": 1.0,
    "required": true,
    "dimension_relevance": ["DIM01"]
  },
  {
    "signal_id": "SIG002",
    "type": "semantic_intensity",
    "pattern": "evidencia_cuantitativa",
    "threshold": 0.7,
    "scoring_impact": 0.3
  }
]
```

---

## Sub-Issue 2: Standardize Validation Contracts

### Status: 🟡 NEEDS ENHANCEMENT
**Priority:** P1 (High)

### Gap Identified
- **Validation Coverage**: ✅ 100% have failure_contract
- **Validation Diversity**: ⚠️ Only 3 abort conditions used (uniform across questions)

### Scope
1. Expand abort conditions from 3 to 15-20 distinct types
2. Create dimension-specific validation rules
3. Add severity levels (warning, error, critical)
4. Implement positive validation_contract (not just failure)
5. Add policy-area-sensitive validation checks

### Acceptance Criteria
- [ ] Minimum 15 distinct abort conditions defined
- [ ] Each dimension has 3-5 specialized validation rules
- [ ] All questions have both failure_contract and validation_contract
- [ ] Validation severity levels implemented (warning/error/critical)
- [ ] Validation equity audit shows no bias by policy area

### Impact
**Medium-High Impact on:**
- Question quality enforcement
- Early problem detection
- Dimension-specific rigor
- Evaluation consistency

### Estimated Effort
- **Time**: 2-3 weeks
- **Complexity**: Medium
- **Resources**: 1 software engineer + domain expert review

### Dependencies
- Sub-Issue 1 (signals) should be completed first for richer validation

### Implementation Notes
```json
// Enhanced validation structure
"failure_contract": {
  "abort_if": [
    "missing_required_element",
    "incomplete_text",
    "signal_threshold_not_met",
    "dimension_specific_check_failed"
  ],
  "severity": "critical",
  "emit_code": "ABORT-Q001-REQ-CRITICAL"
},
"validation_contract": {
  "require_all": [
    "minimum_word_count_200",
    "contains_quantitative_data",
    "sources_cited"
  ],
  "require_any": [
    "temporal_series_present",
    "comparative_analysis_present"
  ],
  "dimension_specific": {
    "DIM01": ["diagnostic_completeness_check"],
    "DIM06": ["causal_chain_verification"]
  }
}
```

---

## Sub-Issue 3: Balance Scoring Modalities & Definitions

### Status: 🔴 CRITICAL
**Priority:** P0 (Immediate)

### Gap Identified
- **Current State**: 100% of questions have `modality: "UNSPECIFIED"`
- **Expected**: Balanced distribution across TYPE_A through TYPE_F

### Scope
1. Define clear criteria for each modality (TYPE_A through TYPE_F)
2. Assign appropriate modality to all 300 questions
3. Ensure balanced distribution across dimensions (avoid 90% one type)
4. Document scoring algorithms for each modality
5. Create modality-specific aggregation rules

### Acceptance Criteria
- [ ] All 6 modality types clearly defined with examples
- [ ] 0% of questions have "UNSPECIFIED" modality
- [ ] No single modality represents >40% of any dimension
- [ ] Scoring algorithms documented and tested
- [ ] Aggregation rules validated for equity

### Impact
**Critical Impact on:**
- Score comparability
- Transparent evaluation
- Risk-based prioritization
- Cross-dimension analysis

### Estimated Effort
- **Time**: 2 weeks
- **Complexity**: Medium
- **Resources**: 1 methodologist + 1 developer

### Dependencies
- None (can proceed in parallel with other sub-issues)

### Implementation Notes
```json
// Modality definitions
{
  "TYPE_A": {
    "name": "Binary Presence/Absence",
    "use_case": "Simple existence checks",
    "score_range": [0, 1],
    "example": "¿Existe un diagnóstico?"
  },
  "TYPE_B": {
    "name": "Ordinal Scale",
    "use_case": "Quality/completeness levels",
    "score_range": [1, 5],
    "example": "Calidad del diagnóstico: 1=deficiente, 5=excelente"
  },
  "TYPE_C": {
    "name": "Quantitative Threshold",
    "use_case": "Numeric indicators with targets",
    "score_range": [0, 100],
    "example": "% de población cubierta en diagnóstico"
  },
  // ... TYPE_D, TYPE_E, TYPE_F
}

// Question assignment
"scoring": {
  "modality": "TYPE_C",
  "threshold": 80,
  "weight": 1.5,
  "dimension_adjustment": 1.0
}
```

---

## Sub-Issue 4: Strengthen Documentation & Criteria

### Status: 🔴 CRITICAL
**Priority:** P0 (Immediate)

### Gap Identified
- **Current State**: 0% of questions fully documented
- Only `question_id` field is populated (100%)
- Missing: question_text, rationale, context, guidance

### Scope
1. Populate `question_text` for all 300 questions
2. Add `rationale` explaining purpose and importance
3. Provide `context` (when/where to apply)
4. Add `guidance` (how to evaluate)
5. Include `documentation` (references to methodology guides)

### Acceptance Criteria
- [ ] 100% of questions have question_text
- [ ] 100% of questions have rationale
- [ ] ≥80% of questions have context
- [ ] ≥80% of questions have guidance
- [ ] ≥50% of questions have documentation references
- [ ] All text in Spanish (primary) with English available

### Impact
**Critical Impact on:**
- Evaluator clarity
- Consistent interpretation
- Training efficiency
- Audit transparency

### Estimated Effort
- **Time**: 4-6 weeks
- **Complexity**: Low-Medium (labor-intensive but straightforward)
- **Resources**: 2-3 domain experts + 1 editor

### Dependencies
- Should be done early to inform other sub-issues

### Implementation Notes
```json
// Documentation template
{
  "question_id": "Q001",
  "question_text": "¿El diagnóstico identifica y cuantifica el problema central con datos actualizados de fuentes oficiales?",
  "rationale": "Un diagnóstico cuantificado con datos recientes es esencial para establecer línea base, dimensionar el problema, y proyectar impacto",
  "context": "Aplicable a: Proyectos de inversión pública (MGA-BPIN), Planes de Desarrollo Municipal/Departamental, Documentos CONPES",
  "guidance": "Verificar presencia de: (1) Fuentes oficiales citadas (DANE, DNP, Ministerios), (2) Series temporales mínimo 3 años, (3) Cobertura territorial explícita, (4) Indicadores cuantitativos",
  "documentation": "Ver: Guía DNP Metodología General Ajustada (MGA), Sección 2.1 'Identificación y descripción del problema'"
}
```

---

## Sub-Issue 5: Deepen Cluster & Policy Area Interlinkage

### Status: 🔴 CRITICAL (Equity Impact)
**Priority:** P0 (Immediate)

### Gap Identified
- **Intersectionality**: 0% of questions address cross-cutting issues
- Gender, vulnerability, rights, equity mentions: all at 0%
- Policy areas exist but don't incorporate transversal themes

### Scope
1. Add explicit `policy_area_id` field to all questions (currently implicit in base_slot)
2. Validate 30 questions per policy area × 10 areas = 300 total
3. Create cross-cutting question variants for gender, vulnerability, rights, equity
4. Add `cross_cutting_considerations` structure to all questions
5. Ensure Policy Areas PA02-PA10 include gender/vulnerability lens

### Acceptance Criteria
- [ ] 100% of questions have explicit policy_area_id
- [ ] Distribution verified: 30 questions × 10 policy areas
- [ ] ≥40% of questions have cross_cutting_considerations
- [ ] PA01 (Gender) keywords appear in ≥20% of questions across PA02-PA10
- [ ] Vulnerability keywords in ≥30% of questions
- [ ] Rights/equity keywords in ≥25% of questions

### Impact
**Critical Equity Impact on:**
- Intersectional analysis capability
- Gender mainstreaming
- Vulnerable population visibility
- Human rights integration

### Estimated Effort
- **Time**: 3-4 weeks
- **Complexity**: High (requires domain expertise)
- **Resources**: 2 gender/equity specialists + 1 methodologist

### Dependencies
- Sub-Issue 4 (documentation) helps inform cross-cutting themes

### Implementation Notes
```json
// Add to each question
{
  "policy_area_id": "PA03", // Explicit assignment
  "cross_cutting_considerations": {
    "gender_sensitive": true,
    "gender_keywords": ["mujeres", "enfoque de género", "desagregación por sexo"],
    "vulnerability_aware": true,
    "vulnerable_groups": ["víctimas conflicto", "población rural dispersa"],
    "rights_based": true,
    "rights_focus": ["derecho a la educación", "no discriminación"],
    "equity_focused": true,
    "equity_indicators": ["brecha urbano-rural", "acceso diferenciado"]
  }
}
```

---

## Sub-Issue 6: Enrich Method Sets, Patterns, & Semantic Coverage

### Status: 🟢 GOOD (Enhancement Only)
**Priority:** P2 (Medium)

### Gap Identified
- **Current State**: ✅ Excellent (100% coverage, 11.6 methods/question, 30 classes, 239 functions)
- **Enhancement Opportunity**: Verify all methods exist and are tested

### Scope
1. Audit all 30 classes to verify they exist in codebase
2. Ensure all 239 functions are implemented and tested
3. Add missing methods for under-served dimensions/policy areas
4. Document method capabilities and use cases
5. Create method-to-question traceability matrix

### Acceptance Criteria
- [ ] 100% of referenced classes exist and are importable
- [ ] 100% of referenced functions exist with tests
- [ ] Method documentation covers all 30 classes
- [ ] Traceability matrix shows method-question coverage
- [ ] No dimension has <8 unique methods

### Impact
**Medium Impact on:**
- Analysis reliability
- Method maintainability
- Future extensibility

### Estimated Effort
- **Time**: 2-3 weeks
- **Complexity**: Medium
- **Resources**: 1-2 developers

### Dependencies
- None (enhancement of already-strong area)

---

## Sub-Issue 7: Normalize Granularity of Expected Elements

### Status: 🟢 GOOD (Enhancement Only)
**Priority:** P3 (Low)

### Gap Identified
- **Current State**: ✅ Excellent (100% coverage, 3.31 elements/question, 104 types, 0 vague)
- **Enhancement Opportunity**: Slight standardization of element counts

### Scope
1. Establish minimum expected_elements per question (e.g., ≥3)
2. Audit questions with <3 elements and enrich
3. Ensure element types are domain-appropriate
4. Add required flag to critical elements
5. Document element type taxonomy

### Acceptance Criteria
- [ ] All questions have ≥3 expected_elements
- [ ] Element type taxonomy documented with examples
- [ ] Each dimension has dimension-specific element types
- [ ] Required elements clearly flagged

### Impact
**Low-Medium Impact on:**
- Question specificity
- Evaluation precision
- Element type consistency

### Estimated Effort
- **Time**: 1-2 weeks
- **Complexity**: Low
- **Resources**: 1 developer + domain review

### Dependencies
- None

---

## Sub-Issue 8: Equity Audit & Risk Flagging

### Status: 🟡 NEW CAPABILITY NEEDED
**Priority:** P1 (High)

### Gap Identified
- **Current State**: No systematic equity auditing mechanism
- Manual review required to detect imbalances

### Scope
1. Create automated equity audit script (like the current audit but ongoing)
2. Define equity metrics and thresholds
3. Implement risk flagging system (low/medium/high/critical)
4. Schedule quarterly equity audits
5. Create equity dashboard for monitoring

### Acceptance Criteria
- [ ] Automated equity audit script operational
- [ ] 10+ equity metrics defined and tracked
- [ ] Risk flagging with severity levels implemented
- [ ] Quarterly audit schedule established
- [ ] Equity dashboard accessible to stakeholders

### Impact
**High Impact on:**
- Long-term equity maintenance
- Early bias detection
- Continuous improvement
- Stakeholder transparency

### Estimated Effort
- **Time**: 2-3 weeks
- **Complexity**: Medium
- **Resources**: 1 developer + 1 data analyst

### Dependencies
- Sub-Issues 1, 3, 4, 5 should be completed first to have meaningful metrics

### Implementation Notes
```python
# Equity metrics to track
equity_metrics = {
    'dimension_balance': 'Questions per dimension within ±10% of average',
    'policy_area_balance': 'Questions per policy area = 30 ± 2',
    'validation_equity': 'Validation coverage ≥90% across all dimensions',
    'modality_diversity': 'No modality >40% in any dimension',
    'cross_cutting_presence': 'Gender/vulnerability keywords in ≥30% of questions',
    'documentation_equity': 'Full documentation ≥80% across all policy areas',
    'signal_equity': 'Signal count variance <20% across dimensions',
    'method_equity': 'Method diversity ≥8 classes per dimension'
}
```

---

## Implementation Roadmap

### Week 1-2: Critical Foundations (P0)
- **Start Sub-Issue 3**: Assign scoring modalities to all questions
- **Start Sub-Issue 4**: Populate question_text for all 300 questions

### Week 3-4: Semantic Enrichment (P0)
- **Complete Sub-Issue 3**: Finalize scoring modalities
- **Complete Sub-Issue 4**: Add rationale and context
- **Start Sub-Issue 1**: Define signal taxonomy and begin population
- **Start Sub-Issue 5**: Add policy_area_id and cross-cutting structure

### Week 5-6: Depth & Equity (P0-P1)
- **Complete Sub-Issue 1**: Finish signal population
- **Complete Sub-Issue 5**: Finalize cross-cutting enrichment
- **Start Sub-Issue 2**: Expand validation diversity

### Week 7-8: Enhancement & Monitoring (P1-P2)
- **Complete Sub-Issue 2**: Finalize validation contracts
- **Start Sub-Issue 8**: Build equity audit system
- **Start Sub-Issue 6**: Audit method availability

### Week 9-10: Finalization (P2-P3)
- **Complete Sub-Issue 6**: Document methods
- **Complete Sub-Issue 8**: Launch equity dashboard
- **Start Sub-Issue 7**: Normalize expected elements granularity

---

## Success Metrics

At completion, the questionnaire should achieve:

| Metric | Current | Target |
|--------|---------|--------|
| Signal Coverage | 0% | 100% |
| Documentation Completeness | 0% | 100% |
| Scoring Modality Specification | 0% | 100% |
| Intersectionality Presence | 0% | ≥40% |
| Validation Diversity | 3 types | ≥15 types |
| Cross-Cutting Keywords | 0% | ≥30% |
| Equity Risk Flags | N/A | <5 high-severity |

---

## Governance

- **Bi-weekly review**: Progress on all active sub-issues
- **Monthly equity audit**: Run automated equity checks
- **Quarterly deep dive**: Comprehensive audit like initial assessment
- **Continuous integration**: All changes must pass equity tests

---

*Document prepared for phased implementation. Each sub-issue can be tracked as separate GitHub issue/task.*
