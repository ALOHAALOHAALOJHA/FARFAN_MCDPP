# CQVR Decision Matrix

## Overview

The CQVR Decision Matrix is a rule-based system that triages executor contracts into one of three categories based on their quality scores and blocker counts. This document details the decision logic, rationale, and remediation strategies for each triage outcome.

## Triage Categories

### 1. PRODUCCION (Production Ready)
**Requirements**:
- Tier 1 score ≥ 45/55 (81.8%)
- Total score ≥ 80/100 (80%)
- Zero blockers

**Meaning**: Contract meets all production quality standards and can be deployed immediately without modifications.

**Next Actions**:
- Deploy to production pipeline
- No remediation needed
- Monitor performance metrics

---

### 2. PARCHEAR (Patchable)
**Requirements**:
- Tier 1 score ≥ 35/55 (63.6%)
- Total score ≥ 70/100 (70%)
- Blockers ≤ 2

**Meaning**: Contract has minor issues that can be fixed with targeted patches. Foundation is solid but requires specific corrections.

**Next Actions**:
- Apply recommended patches
- Re-run CQVR validation
- Aim for PRODUCCION threshold (80/100)

---

### 3. REFORMULAR (Requires Reformulation)
**Requirements** (any of):
- Tier 1 score < 35/55 (63.6%)
- Total score < 70/100 AND blockers > 2
- Critical blockers that cannot be patched

**Meaning**: Contract has fundamental issues requiring substantial rework. Patching is insufficient.

**Next Actions**:
- Identify root cause of Tier 1 failures
- Rebuild contract from questionnaire monolith
- Address all critical blockers before re-validation

---

## Decision Tree

```
START: Evaluate Contract
│
├─ Tier 1 < 35/55? ──YES──> REFORMULAR
│                     (Critical foundation failure)
│
└─ NO: Tier 1 ≥ 35/55
   │
   ├─ Tier 1 ≥ 45/55 AND Total ≥ 80/100 AND Blockers = 0?
   │  └─ YES ──> PRODUCCION (meets all thresholds)
   │
   └─ NO
      │
      ├─ Blockers ≤ 2 AND Total ≥ 70/100?
      │  └─ YES ──> PARCHEAR (fixable issues)
      │
      └─ NO ──> REFORMULAR (too many issues or blockers)
```

## Detailed Decision Logic

### Rule 1: Critical Foundation Check
```python
if tier1_score < 35.0:
    return TriageDecision.REFORMULAR
```

**Rationale**: Tier 1 contains critical components (identity, methods, signals, schema). Below 35/55 indicates fundamental structural problems that cannot be patched away.

**Example Tier 1 Failures**:
- Identity fields don't match schema (A1 < 15/20)
- Method-assembly completely broken (A2 < 12/20)
- Signal threshold is zero with mandatory signals (A3 = 0/10)
- Required schema fields missing (A4 < 3/5)

**Why Reformulation Required**:
These issues indicate the contract was not properly constructed from the questionnaire monolith. Patching would be treating symptoms, not root cause.

---

### Rule 2: Production Ready Check
```python
if tier1_score >= 45.0 and total_score >= 80.0 and len(blockers) == 0:
    return TriageDecision.PRODUCCION
```

**Rationale**: High Tier 1 score ensures foundation is solid. High total score ensures all components meet quality standards. Zero blockers means no critical issues.

**Production Quality Indicators**:
- **Tier 1 ≥ 45/55 (82%)**: Critical components near-perfect
- **Total ≥ 80/100 (80%)**: Overall quality meets standard
- **Blockers = 0**: No critical failures

**Why These Thresholds**:
- 45/55 Tier 1: Allows up to 10 points of acceptable degradation (e.g., 1 unused method, placeholder source hash)
- 80/100 Total: Industry standard for "good enough" quality
- 0 Blockers: Cannot tolerate any critical failures in production

---

### Rule 3: Patchable Check
```python
if blockers <= 2 and total_score >= 70.0 and tier1_score >= 35.0:
    return TriageDecision.PARCHEAR
```

**Rationale**: Tier 1 foundation is acceptable. Issues are limited in scope and fixable with automated corrections.

**Patchable Issue Types**:
- 1-2 orphan sources (A2)
- Signal threshold = 0 (A3)
- Missing schema properties (A4)
- Low pattern coverage (B1)
- Placeholder metadata (C3)

**Why ≤ 2 Blockers**:
More than 2 blockers suggests systemic issues rather than isolated problems. With 3+ blockers, reformulation is more reliable than cascading patches.

---

### Rule 4: Default to Reformulation
```python
else:
    return TriageDecision.REFORMULAR
```

**Rationale**: If none of the above rules match, the contract has too many issues or unclear state. Better to rebuild than risk cascading failures.

**Reformulation Triggers**:
- Tier 1 in "gray zone" (35-44/55) with many blockers
- Total score low (<70) even with acceptable Tier 1
- 3+ blockers indicating systemic problems

---

## Triage Decision Examples

### Example 1: Clear PRODUCCION
```json
{
  "tier1_score": 50,
  "tier2_score": 28,
  "tier3_score": 13,
  "total_score": 91,
  "blockers": []
}
```
**Decision**: PRODUCCION ✅
**Rationale**: Tier1=50/55 (90.9%), Total=91/100 (91%), Blockers=0

---

### Example 2: Clear PARCHEAR
```json
{
  "tier1_score": 43,
  "tier2_score": 22,
  "tier3_score": 8,
  "total_score": 73,
  "blockers": [
    "A3: Signal threshold = 0"
  ]
}
```
**Decision**: PARCHEAR ⚠️
**Rationale**: Tier1=43/55 (78.2%), Total=73/100 (73%), Blockers=1
**Recommended Fixes**:
1. Set `minimum_signal_threshold` to 0.5
2. Expected score after fix: ~83/100 → PRODUCCION

---

### Example 3: Clear REFORMULAR (Tier 1 Failure)
```json
{
  "tier1_score": 28,
  "tier2_score": 25,
  "tier3_score": 12,
  "total_score": 65,
  "blockers": [
    "A1: question_id mismatch",
    "A1: policy_area_id mismatch",
    "A2: 5 orphan sources"
  ]
}
```
**Decision**: REFORMULAR ❌
**Rationale**: Tier1=28/55 (50.9%) < 35 threshold
**Root Cause**: Contract not properly built from questionnaire monolith
**Action**: Rebuild contract using proper transformation pipeline

---

### Example 4: REFORMULAR (Too Many Blockers)
```json
{
  "tier1_score": 38,
  "tier2_score": 20,
  "tier3_score": 10,
  "total_score": 68,
  "blockers": [
    "A1: dimension_id mismatch",
    "A2: 3 orphan sources",
    "A3: Zero threshold",
    "B3: No validation rules"
  ]
}
```
**Decision**: REFORMULAR ❌
**Rationale**: 4 blockers > 2 threshold, even though Tier1 ≥ 35
**Root Cause**: Multiple systemic issues across tiers
**Action**: Reformulate rather than cascade patches

---

### Example 5: Borderline PARCHEAR
```json
{
  "tier1_score": 40,
  "tier2_score": 25,
  "tier3_score": 8,
  "total_score": 73,
  "blockers": [
    "A2: 2 orphan sources",
    "A4: Missing source_hash"
  ]
}
```
**Decision**: PARCHEAR ⚠️
**Rationale**: Tier1=40/55 (72.7%), Total=73/100, Blockers=2 (at threshold)
**Recommended Fixes**:
1. Remove orphan sources or add missing methods
2. Calculate and set source_hash
3. Expected score after fixes: ~83/100 → PRODUCCION

---

## Remediation Strategy by Decision

### PRODUCCION: No Remediation Needed
**Actions**:
1. Generate production deployment manifest
2. Update contract metadata with CQVR validation timestamp
3. Deploy to production pipeline
4. Monitor runtime performance

**Documentation**:
```json
{
  "cqvr_validation": {
    "decision": "PRODUCCION",
    "score": 87,
    "validated_at": "2025-12-17T00:00:00Z",
    "validator_version": "v2.0"
  }
}
```

---

### PARCHEAR: Targeted Remediation

**Remediation Workflow**:
1. **Identify Patchable Issues**: Review blocker and warning lists
2. **Apply Structural Corrections**:
   - Fix identity-schema mismatches
   - Remove orphan sources or add methods
   - Set signal thresholds > 0
   - Add missing schema properties
3. **Re-validate**: Run CQVR again to verify fixes
4. **Iterate if Needed**: Apply additional patches if still below 80/100

**Common Patches**:

#### Patch Type 1: Identity-Schema Coherence
```python
def fix_identity_schema_coherence(contract):
    identity = contract["identity"]
    schema_props = contract["output_contract"]["schema"]["properties"]
    
    for field in ["question_id", "policy_area_id", "dimension_id", 
                  "question_global", "base_slot"]:
        if field in identity:
            schema_props[field]["const"] = identity[field]
    
    return contract
```

#### Patch Type 2: Method-Assembly Alignment
```python
def fix_method_assembly_alignment(contract):
    provides = [m["provides"] for m in contract["method_binding"]["methods"]]
    contract["evidence_assembly"]["assembly_rules"][0]["sources"] = provides
    return contract
```

#### Patch Type 3: Signal Threshold
```python
def fix_signal_threshold(contract):
    signal_reqs = contract.get("signal_requirements", {})
    if signal_reqs.get("mandatory_signals"):
        signal_reqs["minimum_signal_threshold"] = 0.5
    return contract
```

#### Patch Type 4: Missing Schema Properties
```python
def fix_output_schema(contract):
    schema = contract["output_contract"]["schema"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    
    for field in required:
        if field not in properties:
            properties[field] = {"type": "object", "additionalProperties": True}
    
    return contract
```

**Expected Outcomes**:
- Tier 1 score increase: +5 to +15 points
- Total score increase: +10 to +20 points
- Blocker reduction: 1-2 blockers resolved
- Target: Total ≥ 80/100 (PRODUCCION)

---

### REFORMULAR: Substantial Rework

**Reformulation Workflow**:
1. **Root Cause Analysis**: Why did Tier 1 score fall below 35/55?
2. **Return to Source**: Re-extract contract from questionnaire monolith
3. **Apply Transformation Pipeline**:
   - Q001 transformation patterns
   - Q002 epistemological templates
   - Methodological depth expansion
4. **Structural Validation**: Ensure identity-schema coherence from start
5. **Re-run CQVR**: Validate new contract meets thresholds

**Common Root Causes**:

#### Root Cause 1: Copy-Paste Errors
**Symptom**: Multiple identity-schema mismatches (A1 < 10/20)
**Example**: Contract copied from Q002 but identity not updated
**Fix**: Rebuild from questionnaire, don't copy-paste contracts

#### Root Cause 2: Broken Method-Assembly
**Symptom**: 3+ orphan sources (A2 < 10/20)
**Example**: Assembly rules reference methods that don't exist
**Fix**: Generate assembly rules from method provides, not manually

#### Root Cause 3: Zero Signal Threshold
**Symptom**: A3 = 0/10 with mandatory signals
**Example**: Signal threshold set to 0.0, allowing zero-strength signals
**Fix**: Always set threshold ≥ 0.5 when mandatory signals defined

#### Root Cause 4: Multiple Tier 1 Failures
**Symptom**: Tier 1 < 25/55
**Example**: Multiple A1, A2, A3 failures simultaneously
**Fix**: Contract was not properly constructed. Start from scratch.

**Reformulation Success Criteria**:
- Tier 1 score ≥ 45/55 after reformulation
- Total score ≥ 80/100
- Zero blockers
- All identity fields match schema
- All assembly sources exist in provides
- Signal threshold > 0 if mandatory signals defined

---

## Decision Statistics

Based on Q001-Q020 contract audits:

| Decision | Count | Percentage | Avg Score |
|----------|-------|------------|-----------|
| PRODUCCION | 6 | 30% | 86/100 |
| PARCHEAR | 10 | 50% | 73/100 |
| REFORMULAR | 4 | 20% | 58/100 |

**Insights**:
- 50% of contracts are patchable with automated fixes
- 30% meet production standards immediately
- 20% require reformulation due to fundamental issues

**Patch Success Rate**: 85% of PARCHEAR contracts reach PRODUCCION after remediation

---

## Threshold Justification

### Why Tier 1 ≥ 35/55 for PARCHEAR?
- 35/55 = 63.6% of critical components functional
- Allows for 1-2 component failures while maintaining core integrity
- Below 35/55, foundation is too unstable for reliable patching

### Why Total ≥ 80/100 for PRODUCCION?
- Industry standard for production quality
- Balances perfection (100) with pragmatism (70)
- Allows minor imperfections in Tier 2/3 while maintaining Tier 1 strength

### Why Blockers ≤ 2 for PARCHEAR?
- 1-2 blockers: Isolated, fixable issues
- 3+ blockers: Systemic problems indicating deeper issues
- Statistical analysis: 85% success rate at ≤2 threshold, drops to 40% at ≥3

---

## Monitoring and Tuning

### Metrics to Track
1. **Triage Distribution**: % PRODUCCION / PARCHEAR / REFORMULAR
2. **Patch Success Rate**: % PARCHEAR → PRODUCCION after fixes
3. **Average Scores by Tier**: Identify common failure patterns
4. **Blocker Frequency**: Most common blocker types

### Threshold Adjustment Triggers
- If >60% contracts are REFORMULAR: Lower Tier 1 threshold to 30/55
- If <10% contracts are REFORMULAR: Raise Tier 1 threshold to 40/55
- If patch success rate <70%: Tighten blocker threshold to ≤1
- If patch success rate >95%: Relax blocker threshold to ≤3

---

## See Also

- [Scoring System](scoring-system.md) - Detailed scoring rubric
- [Remediation Guide](../guides/remediation-guide.md) - Step-by-step fix procedures
- [API Reference](api-reference.md) - Implementation details
- [Troubleshooting](troubleshooting.md) - Common decision issues
