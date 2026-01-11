# Phase 5 Empirical Validation Protocol

## Scoring Validation with Real Colombian Development Plans (PDT)

**Protocol Version:** 1.0.1  
**Date:** 2026-01-11  
**Status:** APPROVED — Implementation In Progress

---

## 1. Executive Summary

This protocol establishes the methodology for empirically validating the F.A.R.F.A.N Phase 5 (Policy Area Aggregation) scoring system using three real Colombian Territorial Development Plans (Planes de Desarrollo Territorial - PDT) available in the repository.

### 1.1 Available Test Corpus

| Plan ID | Municipality | Department | Period | Pages | Text Size |
|---------|--------------|------------|--------|-------|-----------|
| **Plan_1** | Timbiquí | Cauca | 2012-2015 | 78 | 150 KB |
| **Plan_2** | Florencia | Cauca | 2024-2027 | 327 | 775 KB |
| **Plan_3** | Caloto | Cauca | 2024-2027 | 170 | 423 KB |

### 1.2 Policy Areas Under Evaluation

| ID | Canonical Name (Spanish) | English Translation |
|----|--------------------------|---------------------|
| **PA01** | Derechos de las mujeres e igualdad de género | Women's rights and gender equality |
| **PA02** | Prevención de la violencia y protección frente al conflicto | Violence prevention and conflict protection |
| **PA03** | Ambiente sano, cambio climático, prevención y atención a desastres | Healthy environment, climate change, disaster prevention |
| **PA04** | Derechos económicos, sociales y culturales | Economic, social and cultural rights |
| **PA05** | Derechos de las víctimas y construcción de paz | Victims' rights and peacebuilding |
| **PA06** | Derecho al buen futuro de la niñez, adolescencia, juventud | Rights to a good future for children, adolescents, youth |
| **PA07** | Tierras y territorios | Land and territories |
| **PA08** | Líderes y defensores de derechos humanos | Human rights leaders and defenders |
| **PA09** | Crisis de derechos de personas privadas de la libertad | Rights crisis of persons deprived of liberty |
| **PA10** | Migración transfronteriza | Cross-border migration |

### 1.3 Validation Objectives

1. **Functional Validation**: Verify Phase 5 produces exactly 10 AreaScores per document
2. **Invariant Verification**: Confirm hermeticity (6 dimensions per area), bounds [0, 3], convexity
3. **Sensitivity Analysis**: Assess score stability across documents of varying size/quality
4. **Expert Correlation**: Compare automated scores against human expert baseline
5. **Cross-Document Consistency**: Verify comparable documents produce comparable scores

---

## 2. Hypotheses

| ID | Hypothesis | Test Method | Acceptance Criterion |
|----|------------|-------------|----------------------|
| **H1** | Phase 5 produces exactly 10 AreaScores | Assertion | Pass/Fail |
| **H2** | All scores ∈ [0.0, 3.0] | Bounds check | 100% compliance |
| **H3** | All areas have 6 dimensions | Hermeticity check | 100% compliance |
| **H4** | Convexity holds: min(dims) ≤ area ≤ max(dims) | Property test | 100% compliance |
| **H5** | Larger documents (Plan_2) have higher coverage scores | Correlation | Spearman ρ > 0.5 |
| **H6** | Newer plans (2024) score higher on alignment | t-test | p < 0.05 |
| **H7** | Automated scores correlate with expert scores | Pearson r | r > 0.7 |
| **H8** | Inter-rater reliability is acceptable | Cohen's κ | κ > 0.6 |

---

## 3. Success Criteria

| Criterion | Threshold | Weight |
|-----------|-----------|--------|
| All invariants pass (H1-H4) | 100% | **Required** |
| Size correlation (H5) | ρ > 0.5 | Informational |
| Year effect (H6) | p < 0.05 | Informational |
| Expert correlation (H7) | r > 0.7 | **Required** |
| Inter-rater reliability (H8) | κ > 0.6 | **Required** |
| Threshold sensitivity | Change rate < 20% | Desirable |
| Weight sensitivity | Rank ρ > 0.9 | Desirable |

**Overall Validation**: PASS if all **Required** criteria met.

---

## 4. Timeline

| Day | Phase | Activities | Deliverables |
|-----|-------|------------|--------------|
| 1 | A | Environment setup, expert recruitment | `corpus_checksums.txt`, config files |
| 2-3 | B | Automated pipeline execution | `validation_results.json` |
| 4-6 | C | Expert scoring, IRR computation | Expert sheets, `irr_results.json` |
| 7 | D | Sensitivity analysis | `sensitivity_results.json` |
| 8 | E | Report compilation | `VALIDATION_REPORT.md` |

---

## 5. Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Protocol Author | AI Assistant | ✓ | 2026-01-11 |
| Technical Lead | User | ✓ APPROVED | 2026-01-11 |

---

**Implementation Status**: IN PROGRESS
