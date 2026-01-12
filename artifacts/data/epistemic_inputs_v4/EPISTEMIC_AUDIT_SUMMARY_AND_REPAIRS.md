# 📊 EPISTEMIC METHOD ASSIGNMENTS AUDIT - SUMMARY & REPAIR PLAN

**Date**: 2025-12-31  
**Auditor**: AI Agent (PythonGod Trinity)  
**File Audited**: `artifacts/data/reports/EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030.json`  
**Specification**: `docs/misc/episte_refact.md`  

---

## 🎯 EXECUTIVE SUMMARY

**Overall Compliance**: 77.7%  
**Status**: ❌ **REQUIRES CORRECTIONS**

- ✅ **Passed Checks**: 369/475
- ❌ **Failed Checks**: 106/475
- 🔴 **Critical Issues**: 7
- 🟠 **High Issues**: 72
- 🟡 **Medium Issues**: 27

### Key Findings

1. **TYPE Classification**: ✅ **PERFECT** - All 30 questions correctly classified
2. **Output Types**: ✅ **PERFECT** - All N1=FACT, N2=PARAMETER, N3=CONSTRAINT correct
3. **Mandatory Methods**: ❌ **7 CRITICAL** - Missing `FinancialAggregator.normalize` in TYPE_D questions
4. **Fusion Behaviors**: ❌ **72 HIGH** - Missing or incorrect `fusion_behavior` specifications
5. **Overall Justifications**: ⚠️ **27 MEDIUM** - Missing from Q004-Q030 (only Q001-Q003 have them)

---

## 🔴 CRITICAL ISSUES (7)

### Issue: Missing Mandatory Method for TYPE_D Questions

**Affected Questions**: Q004, Q006, Q009, Q012, Q015, Q021, Q022

**Problem**: Per `episte_refact.md` Section 2.2, TYPE_D requires **mandatory** N2 method:
- `FinancialAggregator.normalize`

**Current State**: These questions use `FinancialCoherenceAnalyzer.calculate_weighted_mean` instead.

**Root Cause**: The assignments file uses a **different but semantically equivalent** method. However, the specification explicitly requires `FinancialAggregator.normalize` with `forced_inclusion`.

**Impact**: Non-compliance with mandatory method requirements from episte_refact.md.

**Repair Strategy** (2 options):

#### Option A: Update Assignments File (Recommended)
Add the mandatory method while keeping existing method:

```json
{
  "method_id": "FinancialAggregator.normalize_to_budget_base",
  "file": "financiero_viabilidad_tablas.py",
  "justification": "N2: MANDATORY for TYPE_D. Expresses allocations as % of total budget for comparability. Formula: (amount / total_budget) * 100.",
  "output_type": "PARAMETER",
  "fusion_behavior": "weighted_mean",
  "epistemic_necessity": "forced_inclusion"
}
```

#### Option B: Update Specification
If `FinancialCoherenceAnalyzer.calculate_weighted_mean` is the correct modern implementation, update episte_refact.md Section 2.2 to reflect this.

**Recommendation**: **Option A** - Add the mandatory method as specified.

---

## 🟠 HIGH ISSUES (72)

### Issue 1: Missing `fusion_behavior` in Most Methods

**Pattern**: All non-Q001/Q002/Q003 methods are missing the `fusion_behavior` field.

**Examples**:
- Q005 N1[0]: `BayesianEvidenceExtractor.extract_prior_beliefs` - missing `fusion_behavior: "concat"`
- Q008 N3[0]: `DAGCycleDetector.veto_on_cycle` - missing `fusion_behavior: "veto_gate"`

**Expected Values by Level**:
- **N1-EMP**: `fusion_behavior: "concat"` (unless TYPE_A semantic methods)
- **N2-INF**: Varies by TYPE:
  - TYPE_A: `"dempster_shafer"` or `"semantic_triangulation"`
  - TYPE_B: `"bayesian_update"`
  - TYPE_C: `"topological_overlay"`
  - TYPE_D/E: `"weighted_mean"`
- **N3-AUD**: `fusion_behavior: "veto_gate"` or `"statistical_threshold_gate"` or `"cycle_detection_veto"`

**Repair**: Add `fusion_behavior` field to all methods following the pattern established in Q001-Q003.

### Issue 2: Incorrect Fusion Strategy R1 for TYPE_D

**Affected**: Q003, Q022

**Problem**: TYPE_D R1 strategy is `"concat"` but should be `"financial_aggregation"` per episte_refact.md Section 4.3.

**Fix**:
```json
"fusion_strategy": {
  "R1": "financial_aggregation",  // Changed from "concat"
  "R2": "weighted_mean",
  "R3": "sufficiency_gate"
}
```

### Issue 3: `epistemic_necessity` Misuse

**Example**: Q002 N2[1] - `BayesianNumericalAnalyzer.evaluate_policy_metric` has `forced_inclusion` but is NOT mandatory for TYPE_B.

**Mandatory Methods by TYPE** (from episte_refact.md):
- TYPE_A N2: `DempsterShaferCombinator` ✓
- TYPE_B N2: `BayesianUpdater` ONLY ✗ (not BayesianNumericalAnalyzer)
- TYPE_C N2: `DAGCycleDetector` ✓
- TYPE_D N2: `FinancialAggregator.normalize` ✗ (missing)
- TYPE_E N2: `LogicalConsistencyChecker` ✓

**Fix**: Remove `forced_inclusion` from non-mandatory methods, or change to `"mandatory"` or `"preferred"`.

---

## 🟡 MEDIUM ISSUES (27)

### Issue: Missing `overall_justification` in Q004-Q030

**Problem**: Only Q001, Q002, Q003 have `overall_justification`. Q004-Q030 are missing this field.

**Impact**: Reduces traceability and epistemic transparency.

**Example Fix** (Q005):
```json
"overall_justification": "Q005 asks about quantified service coverage targets for VBG victims - inherently Bayesian (prior beliefs about capacity + likelihood from statistics). TYPE_B strategy: N1 extracts priors/likelihoods, N2 computes posterior via Bayes update, N3 validates statistical significance with gate. This ensures coverage goals are statistically sound and not aspirational guesses."
```

**Pattern**: Each justification should:
1. Restate the question's essence
2. Explain WHY it's classified as that TYPE
3. Describe the epistemic flow: N1→N2→N3
4. Emphasize the veto gate role of N3

---

## ✅ STRENGTHS

1. **Perfect TYPE Classification**: All 30 questions correctly mapped to TYPE_A/B/C/D/E
2. **Correct Output Types**: 100% compliance - All N1=FACT, N2=PARAMETER, N3=CONSTRAINT
3. **Comprehensive Coverage**: All 30 questions have methods assigned
4. **Strong Q001-Q003 Examples**: These 3 questions serve as excellent templates
5. **Correct Distribution**:
   - TYPE_A: 2 ✓
   - TYPE_B: 12 ✓
   - TYPE_C: 4 ✓
   - TYPE_D: 8 ✓
   - TYPE_E: 4 ✓

---

## 🛠️ SPECIFIC REPAIR RECOMMENDATIONS

### Priority 1: Critical Fixes (7 issues)

**Task 1.1**: Add Mandatory N2 Method to TYPE_D Questions

For Q004, Q006, Q009, Q012, Q015, Q021, Q022, add:

```json
"N2-INF": [
  {
    "method_id": "FinancialAggregator.normalize_to_budget_base",
    "file": "financiero_viabilidad_tablas.py",
    "justification": "N2: MANDATORY for TYPE_D per episte_refact.md Section 2.2. Expresses allocations as % of total budget for comparability. Formula: (amount / total_budget) * 100.",
    "output_type": "PARAMETER",
    "fusion_behavior": "weighted_mean",
    "epistemic_necessity": "forced_inclusion"
  },
  // ... existing methods
]
```

### Priority 2: High Fixes (72 issues)

**Task 2.1**: Add `fusion_behavior` to All Methods

Use Q001-Q003 as templates. For each method level:

**N1-EMP Pattern**:
```json
{
  "method_id": "...",
  "file": "...",
  "justification": "...",
  "output_type": "FACT",
  "fusion_behavior": "concat",  // ADD THIS
  "epistemic_necessity": "..."
}
```

**N2-INF Pattern** (varies by TYPE):
```json
// TYPE_B
"fusion_behavior": "bayesian_update"

// TYPE_C  
"fusion_behavior": "topological_overlay"

// TYPE_D/E
"fusion_behavior": "weighted_mean"

// TYPE_A
"fusion_behavior": "dempster_shafer" // or "semantic_triangulation"
```

**N3-AUD Pattern**:
```json
// TYPE_B
"fusion_behavior": "statistical_threshold_gate"

// TYPE_C
"fusion_behavior": "cycle_detection_veto"

// TYPE_A/E
"fusion_behavior": "veto_gate"

// TYPE_D
"fusion_behavior": "veto_gate"
```

**Task 2.2**: Fix Fusion Strategy R1 for TYPE_D

For Q003, Q022:
```json
"fusion_strategy": {
  "R1": "financial_aggregation",  // Changed from "concat"
  "R2": "weighted_mean",
  "R3": "sufficiency_gate"
}
```

**Task 2.3**: Correct `epistemic_necessity` Values

Remove `forced_inclusion` from non-mandatory methods:
- Q002 N2[1]: `BayesianNumericalAnalyzer.evaluate_policy_metric` → change to `"mandatory"`

### Priority 3: Medium Fixes (27 issues)

**Task 3.1**: Add `overall_justification` to Q004-Q030

Template:
```json
"overall_justification": "Q[NUM] [restate question essence] - [TYPE explanation]. TYPE_[X] strategy: N1 [extracts what], N2 [computes what via which method], N3 [validates via which gate]. This ensures [final epistemic guarantee]."
```

Examples:

**TYPE_B (Q005)**:
```json
"overall_justification": "Q005 requires assessment of quantified service coverage targets - inherently Bayesian (priors about capacity + likelihood from data). TYPE_B: N1 extracts priors/likelihoods, N2 updates posterior via BayesianUpdater, N3 validates significance via StatisticalGateAuditor. Ensures targets are evidence-based, not aspirational."
```

**TYPE_C (Q008)**:
```json
"overall_justification": "Q008 asks about theory of change articulation - pure causal graph validation. TYPE_C: N1 extracts causal links and builds DAG, N2 detects cycles via DAGCycleDetector, N3 vetoes if cycle found (confidence=0.0). Ensures causal logic is acyclic and valid."
```

**TYPE_D (Q009)**:
```json
"overall_justification": "Q009 requires financial resources for indicator systems - budget coherence check. TYPE_D: N1 extracts budget allocations, N2 normalizes and computes weighted mean coherence, N3 validates sufficiency via FiscalSustainabilityValidator. Ensures indicators are adequately funded."
```

**TYPE_E (Q010)**:
```json
"overall_justification": "Q010 assesses consistency between indicators and goals - logical coherence check. TYPE_E: N1 collates statements, N2 checks consistency via MIN logic (one contradiction → confidence=0), N3 applies ContradictionDominator veto. Ensures no logical contradictions exist."
```

---

## 📋 VALIDATION AGAINST audit_v4_rigorous.py

### Compatibility Check

The file would **partially pass** `audit_v4_rigorous.py` but fail on:

1. **Section 2 (Method Binding)**: Would fail checks for:
   - `2.4.X` - N1 methods missing `fusion_behavior` field
   - `2.6.X` - N2 methods missing `fusion_behavior` field
   - `2.8.X` - N3 methods missing `fusion_behavior` field
   - `2.8.15` - Missing `veto_conditions` in N3 methods (assignments file doesn't include this level of detail)

2. **Section 3 (Evidence Assembly)**: Would pass (fusion_strategy is correct in most cases)

3. **Section 4 (Fusion Specification)**: Not applicable (assignments file is different structure than full contracts)

**Note**: The assignments file is a **simplified view** of method assignments, NOT a full executor contract. It lacks:
- `veto_conditions` specifications
- Full `evidence_assembly` rules
- `cross_layer_fusion` details
- `human_answer_structure` specifications

These are expected to be in the **actual 300 executor contracts**, not in this assignments summary file.

---

## 🎯 ACCEPTANCE CRITERIA FOR FIXES

After repairs, the file should achieve:

- [ ] **100% Critical Compliance**: All 7 TYPE_D questions have `FinancialAggregator.normalize`
- [ ] **≥95% High Compliance**: All methods have correct `fusion_behavior`
- [ ] **≥90% Medium Compliance**: Most questions have `overall_justification`
- [ ] **Overall Compliance**: ≥95%

---

## 📊 PROPOSED FILE STRUCTURE (Post-Repair)

```json
{
  "metadata": { ... },
  "assignments": {
    "Q001": {
      "question": "...",
      "type": "TYPE_A",
      "dimension": "...",
      "policy_area": "...",
      "epistemic_profile": { ... },
      "selected_methods": {
        "N1-EMP": [
          {
            "method_id": "...",
            "file": "...",
            "justification": "...",
            "output_type": "FACT",
            "fusion_behavior": "concat",  // ✅ REQUIRED
            "epistemic_necessity": "..."
          }
        ],
        "N2-INF": [
          {
            "method_id": "...",
            "file": "...",
            "justification": "...",
            "output_type": "PARAMETER",
            "fusion_behavior": "bayesian_update",  // ✅ REQUIRED (varies by TYPE)
            "epistemic_necessity": "forced_inclusion"  // Only if mandatory
          }
        ],
        "N3-AUD": [
          {
            "method_id": "...",
            "file": "...",
            "justification": "...",
            "output_type": "CONSTRAINT",
            "fusion_behavior": "veto_gate",  // ✅ REQUIRED (varies by TYPE)
            "epistemic_necessity": "forced_inclusion"  // Mandatory for all N3
          }
        ]
      },
      "fusion_strategy": {
        "R1": "...",  // Must match TYPE
        "R2": "...",
        "R3": "..."
      },
      "overall_justification": "..."  // ✅ REQUIRED
    }
  }
}
```

---

## 🚀 NEXT STEPS

1. **Immediate**: Fix 7 critical issues (add mandatory N2 methods to TYPE_D)
2. **High Priority**: Add `fusion_behavior` to all 72 affected methods
3. **Medium Priority**: Add `overall_justification` to Q004-Q030
4. **Validation**: Re-run `audit_epistemic_assignments.py` to confirm ≥95% compliance
5. **Integration**: Use corrected assignments to generate/validate the 300 executor contracts

---

## 📎 APPENDIX: episte_refact.md Key Requirements

### Section 2.2: Mandatory Methods by TYPE

| TYPE | N2 Mandatory | N3 Mandatory |
|------|--------------|--------------|
| TYPE_A | DempsterShaferCombinator | ContradictionDominator |
| TYPE_B | BayesianUpdater | StatisticalGateAuditor |
| TYPE_C | DAGCycleDetector | DAGCycleDetector.veto_on_cycle |
| TYPE_D | FinancialAggregator.normalize | FiscalSustainabilityValidator |
| TYPE_E | LogicalConsistencyChecker (MIN) | ContradictionDominator |

### Section 4.3: Fusion Strategies by TYPE

| TYPE | R1 Strategy | R2 Strategy | R3 Strategy |
|------|-------------|-------------|-------------|
| TYPE_A | semantic_bundling | semantic_triangulation | contradiction_veto |
| TYPE_B | concat | bayesian_update | statistical_gate |
| TYPE_C | graph_construction | topological_overlay | cycle_detection_veto |
| TYPE_D | financial_aggregation | weighted_mean | sufficiency_gate |
| TYPE_E | fact_collation | min_consistency | contradiction_veto |

---

**End of Report**
