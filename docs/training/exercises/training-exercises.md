# CQVR Training Exercises

## Overview

Hands-on exercises to build CQVR proficiency. Each exercise includes a scenario, tasks, and verification steps.

## Exercise 1: First Contract Validation

**Difficulty**: Beginner  
**Time**: 15 minutes  
**Skills**: Basic CQVR validation, result interpretation

### Scenario
You have a newly authored contract for Q001 that needs validation before deployment.

### Tasks

1. **Run CQVR validation on the provided contract**
2. **Interpret the results**
3. **Identify the triage decision**

### Setup

Create a test contract `exercises/ex1_contract.json`:
```json
{
  "identity": {
    "question_id": "Q001",
    "base_slot": "D1-Q1",
    "question_global": 1,
    "policy_area_id": "PA01",
    "dimension_id": "DIM01",
    "contract_version": "3.0",
    "created_at": "2025-12-17T00:00:00Z"
  },
  "method_binding": {
    "method_count": 3,
    "methods": [
      {"provides": "text_mining.extract", "method_name": "TextMiningExtractor"},
      {"provides": "causal.infer", "method_name": "CausalInference"},
      {"provides": "validation.check", "method_name": "ValidationChecker"}
    ]
  },
  "evidence_assembly": {
    "assembly_rules": [{
      "sources": ["text_mining.extract", "causal.infer", "validation.check"]
    }]
  },
  "signal_requirements": {
    "mandatory_signals": ["feasibility_score"],
    "minimum_signal_threshold": 0.5,
    "signal_aggregation": "weighted_mean"
  },
  "output_contract": {
    "schema": {
      "required": ["base_slot", "question_id", "evidence"],
      "properties": {
        "base_slot": {"const": "D1-Q1"},
        "question_id": {"const": "Q001"},
        "question_global": {"const": 1},
        "policy_area_id": {"const": "PA01"},
        "dimension_id": {"const": "DIM01"},
        "evidence": {"type": "array"}
      }
    }
  },
  "validation_rules": {
    "rules": [{
      "rule_id": "COMPLETENESS",
      "must_contain": {"elements": ["policy_goal"]}
    }]
  },
  "error_handling": {
    "failure_contract": {
      "emit_code": "FAIL_Q001_VALIDATION"
    }
  },
  "question_context": {
    "patterns": [],
    "expected_elements": []
  },
  "methodological_depth": {
    "methods": []
  },
  "traceability": {}
}
```

### Step 1: Run Validation

```python
#!/usr/bin/env python3
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator
import json

# Load contract
with open('exercises/ex1_contract.json') as f:
    contract = json.load(f)

# Validate
validator = CQVRValidator()
decision = validator.validate_contract(contract)

# Print results
print(f"Total Score: {decision.score.total_score}/100")
print(f"Tier 1: {decision.score.tier1_score}/55")
print(f"Tier 2: {decision.score.tier2_score}/30")
print(f"Tier 3: {decision.score.tier3_score}/15")
print(f"\nDecision: {decision.decision.value}")
print(f"Blockers: {len(decision.blockers)}")
for blocker in decision.blockers:
    print(f"  - {blocker}")
```

### Step 2: Answer Questions

1. **What is the total score?** ______/100
2. **What is the triage decision?** (PRODUCCION / PARCHEAR / REFORMULAR)
3. **How many blockers are there?** ______
4. **Is the contract production-ready?** (Yes / No)
5. **What percentage is the Tier 1 score?** ______%

### Step 3: Verify Your Answers

<details>
<summary>Click to see solutions</summary>

**Expected Results**:
1. Total Score: ~45/100
2. Decision: PARCHEAR (Tier 1 ≥ 35/55 but total < 70)
3. Blockers: 0-2
4. Production-ready: No
5. Tier 1 percentage: ~75-85%

**Analysis**:
- Tier 1 is acceptable (no critical failures)
- Tier 2/3 are low due to missing patterns, methods, documentation
- Contract can be patched to reach production threshold
</details>

---

## Exercise 2: Fix Identity-Schema Mismatch

**Difficulty**: Intermediate  
**Time**: 20 minutes  
**Skills**: Identifying mismatches, applying fixes, verification

### Scenario
A contract has identity-schema mismatches causing A1 component failure.

### Setup

Create `exercises/ex2_contract.json` with intentional mismatches:
```json
{
  "identity": {
    "question_id": "Q007",
    "base_slot": "D2-Q2",
    "policy_area_id": "PA01",
    "dimension_id": "DIM02"
  },
  "output_contract": {
    "schema": {
      "properties": {
        "question_id": {"const": "Q002"},  // MISMATCH
        "base_slot": {"const": "D1-Q1"},   // MISMATCH
        "policy_area_id": {"const": "PA01"},
        "dimension_id": {"const": "DIM01"} // MISMATCH
      }
    }
  }
  // ... rest of contract
}
```

### Tasks

1. **Run validation to identify mismatches**
2. **Fix all identity-schema mismatches**
3. **Re-validate to verify fix**
4. **Calculate score improvement**

### Step 1: Identify Mismatches

```python
validator = CQVRValidator()
validator.blockers = []
score = validator.verify_identity_schema_coherence(contract)

print(f"A1 Score: {score}/20")
print(f"Blockers: {validator.blockers}")
```

**Question**: Which fields have mismatches?
- [ ] question_id
- [ ] base_slot
- [ ] policy_area_id
- [ ] dimension_id

### Step 2: Apply Fix

```python
def fix_identity_schema_coherence(contract):
    identity = contract["identity"]
    schema_props = contract["output_contract"]["schema"]["properties"]
    
    # TODO: Sync identity → schema
    # Your code here
    
    return contract

contract = fix_identity_schema_coherence(contract)
```

### Step 3: Verify Fix

```python
new_score = validator.verify_identity_schema_coherence(contract)
print(f"Original score: {score}/20")
print(f"New score: {new_score}/20")
print(f"Improvement: +{new_score - score}")
```

**Expected improvement**: +10 to +15 points

<details>
<summary>Click to see solution</summary>

```python
def fix_identity_schema_coherence(contract):
    identity = contract["identity"]
    schema_props = contract["output_contract"]["schema"]["properties"]
    
    for field in ["question_id", "base_slot", "policy_area_id", "dimension_id"]:
        if field in identity:
            if field not in schema_props:
                schema_props[field] = {}
            schema_props[field]["const"] = identity[field]
    
    return contract
```

**Verification**:
- Mismatches: question_id, base_slot, dimension_id (3 fields)
- Fix: Sync all 5 identity fields to schema
- New A1 score: 20/20
- Improvement: +15 points
</details>

---

## Exercise 3: Remove Orphan Sources

**Difficulty**: Intermediate  
**Time**: 25 minutes  
**Skills**: Method-assembly alignment, orphan detection

### Scenario
Assembly rules reference methods that don't exist, causing A2 blocker.

### Setup

```json
{
  "method_binding": {
    "methods": [
      {"provides": "text_mining.extract"},
      {"provides": "causal.infer"}
    ]
  },
  "evidence_assembly": {
    "assembly_rules": [{
      "sources": [
        "text_mining.extract",
        "causal.infer",
        "nonexistent.method",      // ORPHAN
        "undefined.function",       // ORPHAN
        "missing.processor"         // ORPHAN
      ]
    }]
  }
}
```

### Tasks

1. **Identify orphan sources**
2. **Choose remediation strategy** (remove orphans OR add missing methods)
3. **Apply fix**
4. **Verify no orphans remain**

### Step 1: Detect Orphans

```python
def detect_orphans(contract):
    methods = contract["method_binding"]["methods"]
    provides_set = {m["provides"] for m in methods}
    
    assembly_rules = contract["evidence_assembly"]["assembly_rules"]
    sources = assembly_rules[0]["sources"]
    
    orphans = [s for s in sources if s not in provides_set]
    
    print(f"Provides: {provides_set}")
    print(f"Sources: {set(sources)}")
    print(f"Orphans: {orphans}")
    
    return orphans

orphans = detect_orphans(contract)
```

**Question**: How many orphan sources are there? ______

### Step 2: Choose Strategy

**Option A: Remove Orphans**
- Pros: Simple, fast
- Cons: Loses potential evidence sources

**Option B: Add Missing Methods**
- Pros: Preserves evidence sources
- Cons: Requires implementing methods

**Which strategy would you choose and why?**

### Step 3: Apply Fix (Option A)

```python
def remove_orphan_sources(contract):
    # TODO: Implement orphan removal
    # Your code here
    
    return contract

contract = remove_orphan_sources(contract)
```

### Step 4: Verify

```python
new_orphans = detect_orphans(contract)
assert len(new_orphans) == 0, f"Still have orphans: {new_orphans}"
print("✅ No orphans remaining")

score = validator.verify_method_assembly_alignment(contract)
print(f"A2 Score: {score}/20")
```

<details>
<summary>Click to see solution</summary>

**Answers**:
1. Orphan count: 3 (nonexistent.method, undefined.function, missing.processor)
2. Strategy: Option A (remove orphans) is appropriate if methods don't exist

**Solution**:
```python
def remove_orphan_sources(contract):
    methods = contract["method_binding"]["methods"]
    provides_set = {m["provides"] for m in methods}
    
    assembly_rules = contract["evidence_assembly"]["assembly_rules"]
    assembly_rules[0]["sources"] = [
        s for s in assembly_rules[0]["sources"]
        if s in provides_set
    ]
    
    return contract
```

**Verification**:
- Original sources: 5
- Orphans removed: 3
- Remaining sources: 2
- A2 score: ~18/20 (slight penalty for unused methods removed)
</details>

---

## Exercise 4: Full Remediation Workflow

**Difficulty**: Advanced  
**Time**: 45 minutes  
**Skills**: Complete remediation, validation, verification

### Scenario
You have a contract scoring 65/100 (PARCHEAR decision) with multiple issues. Apply complete remediation to reach production quality (≥80/100).

### Setup

Use provided contract `exercises/ex4_contract.json` with multiple issues:
- Identity-schema mismatches (A1)
- Orphan sources (A2)
- Zero signal threshold (A3)
- Missing metadata (C3)

### Tasks

1. **Run initial validation**
2. **Apply automated fixes**
3. **Apply manual fixes for remaining issues**
4. **Re-validate**
5. **Verify production-ready (≥80/100, 0 blockers)**

### Workflow

```python
#!/usr/bin/env python3
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator
from src.farfan_pipeline.phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import ContractRemediation
import json

# Load contract
with open('exercises/ex4_contract.json') as f:
    contract = json.load(f)

# Step 1: Initial validation
validator = CQVRValidator()
initial = validator.validate_contract(contract)

print("INITIAL VALIDATION")
print(f"Score: {initial.score.total_score}/100")
print(f"Decision: {initial.decision.value}")
print(f"Blockers: {len(initial.blockers)}")

# Step 2: Automated remediation
print("\nAPPLYING AUTOMATED FIXES...")
remediation = ContractRemediation()
contract = remediation.apply_structural_corrections(contract)

# Step 3: Manual fixes
print("\nAPPLYING MANUAL FIXES...")

# TODO: Fix signal threshold
# Your code here

# TODO: Fix metadata
# Your code here

# Step 4: Re-validate
final = validator.validate_contract(contract)

print("\nFINAL VALIDATION")
print(f"Score: {final.score.total_score}/100")
print(f"Improvement: +{final.score.total_score - initial.score.total_score}")
print(f"Decision: {final.decision.value}")
print(f"Blockers: {len(final.blockers)}")

# Step 5: Verify production-ready
assert final.score.total_score >= 80, "Score too low for production"
assert len(final.blockers) == 0, "Blockers remaining"
print("\n✅ CONTRACT IS PRODUCTION-READY")
```

### Success Criteria

- [ ] Initial score documented
- [ ] All automated fixes applied
- [ ] All manual fixes applied
- [ ] Final score ≥ 80/100
- [ ] Zero blockers
- [ ] Production-ready decision

<details>
<summary>Click to see solution approach</summary>

**Step-by-step**:

1. **Initial validation**: ~65/100, PARCHEAR, 3-4 blockers

2. **Automated fixes** (ContractRemediation):
   - Identity-schema sync: +10 pts
   - Orphan sources removed: +5 pts
   - Missing properties added: +3 pts
   - **After automated**: ~83/100

3. **Manual fixes**:
   ```python
   # Fix signal threshold
   signal_reqs = contract.get("signal_requirements", {})
   if signal_reqs.get("mandatory_signals"):
       signal_reqs["minimum_signal_threshold"] = 0.5
   
   # Fix metadata
   import hashlib
   from datetime import datetime
   
   identity = contract["identity"]
   identity["created_at"] = datetime.now().isoformat()
   identity["contract_version"] = "3.0"
   
   contract_str = json.dumps(contract, sort_keys=True)
   identity["contract_hash"] = hashlib.sha256(contract_str.encode()).hexdigest()
   ```
   - Signal threshold: +10 pts
   - Metadata: +3 pts
   - **After manual**: ~96/100

4. **Final validation**: 96/100, PRODUCCION, 0 blockers

5. **Success**: Contract production-ready ✅
</details>

---

## Exercise 5: Batch Validation

**Difficulty**: Advanced  
**Time**: 30 minutes  
**Skills**: Automation, batch processing, reporting

### Scenario
Validate 10 contracts, generate summary report, identify which need attention.

### Tasks

1. **Create 10 test contracts** (mix of quality levels)
2. **Run batch validation**
3. **Generate summary report**
4. **Prioritize contracts for remediation**

### Implementation

```python
#!/usr/bin/env python3
from pathlib import Path
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator
import json

def batch_validate(contracts_dir: Path):
    """Validate all contracts and return results"""
    
    validator = CQVRValidator()
    results = []
    
    for contract_path in sorted(contracts_dir.glob("*.json")):
        # TODO: Validate contract
        # TODO: Store result
        pass
    
    return results

def generate_report(results: list):
    """Generate summary report"""
    
    # TODO: Calculate statistics
    # TODO: Identify priorities
    # TODO: Print report
    pass

# Run
results = batch_validate(Path("exercises/batch/"))
generate_report(results)
```

### Expected Output

```
BATCH VALIDATION REPORT
=======================
Total contracts: 10
✅ PRODUCCION:  5 (50%)
⚠️  PARCHEAR:   3 (30%)
❌ REFORMULAR:  2 (20%)

Average score: 76.3/100

PRIORITIES:
1. HIGH: Q014 (32/100, REFORMULAR)
2. HIGH: Q023 (45/100, REFORMULAR)
3. MED:  Q007 (68/100, PARCHEAR, 2 blockers)
4. MED:  Q012 (72/100, PARCHEAR, 1 blocker)
5. LOW:  Q003 (78/100, PARCHEAR, 0 blockers)
```

<details>
<summary>Click to see solution</summary>

```python
def batch_validate(contracts_dir: Path):
    validator = CQVRValidator()
    results = []
    
    for contract_path in sorted(contracts_dir.glob("*.json")):
        try:
            with open(contract_path) as f:
                contract = json.load(f)
            
            decision = validator.validate_contract(contract)
            
            results.append({
                "file": contract_path.name,
                "question_id": contract.get("identity", {}).get("question_id"),
                "score": decision.score.total_score,
                "decision": decision.decision.value,
                "blockers": len(decision.blockers)
            })
        except Exception as e:
            print(f"Error validating {contract_path.name}: {e}")
    
    return results

def generate_report(results: list):
    total = len(results)
    produccion = sum(1 for r in results if r["decision"] == "PRODUCCION")
    parchear = sum(1 for r in results if r["decision"] == "PARCHEAR")
    reformular = sum(1 for r in results if r["decision"] == "REFORMULAR")
    
    avg_score = sum(r["score"] for r in results) / total
    
    print("BATCH VALIDATION REPORT")
    print("=" * 23)
    print(f"Total contracts: {total}")
    print(f"✅ PRODUCCION:  {produccion} ({produccion/total*100:.0f}%)")
    print(f"⚠️  PARCHEAR:   {parchear} ({parchear/total*100:.0f}%)")
    print(f"❌ REFORMULAR:  {reformular} ({reformular/total*100:.0f}%)")
    print(f"\nAverage score: {avg_score:.1f}/100")
    
    # Prioritize
    priorities = []
    for r in results:
        if r["decision"] == "REFORMULAR":
            priority = "HIGH"
        elif r["decision"] == "PARCHEAR" and r["blockers"] > 0:
            priority = "MED"
        elif r["score"] < 80:
            priority = "LOW"
        else:
            continue
        
        priorities.append((priority, r["question_id"], r["score"], r["decision"], r["blockers"]))
    
    priorities.sort(key=lambda x: (
        {"HIGH": 0, "MED": 1, "LOW": 2}[x[0]],
        x[2]  # Sort by score within priority
    ))
    
    print("\nPRIORITIES:")
    for i, (priority, qid, score, decision, blockers) in enumerate(priorities, 1):
        print(f"{i}. {priority:4s}: {qid} ({score:.0f}/100, {decision}, {blockers} blockers)")
```
</details>

---

## Additional Exercises

### Exercise 6: Pattern Generation
Create patterns for a new question type covering expected elements.

### Exercise 7: Method Specificity
Improve boilerplate method descriptions to specific technical approaches.

### Exercise 8: CI/CD Integration
Set up GitHub Actions workflow to validate contracts on pull requests.

### Exercise 9: Quality Monitoring
Track contract quality metrics over time, detect regressions.

### Exercise 10: Custom Remediation
Write custom remediation script for domain-specific issue.

---

## See Also

- [Solutions](../training/solutions/) - Detailed solutions for all exercises
- [Best Practices](best-practices.md) - Guidelines for CQVR usage
- [Evaluation Guide](../guides/evaluation-guide.md) - Validation procedures
- [Remediation Guide](../guides/remediation-guide.md) - Fix procedures
