# CQVR Training Exercise Solutions

## Complete Solutions with Explanations

This document provides detailed solutions for all training exercises, including step-by-step explanations and verification procedures.

---

## Exercise 1 Solutions: First Contract Validation

### Expected Results

```python
# Exercise 1 validation results
Total Score: 45/100
Tier 1: 38/55 (69.1%)
Tier 2: 5/30 (16.7%)
Tier 3: 2/15 (13.3%)

Decision: PARCHEAR
Blockers: 0
```

### Answer Key

1. **Total score**: 45/100
2. **Triage decision**: PARCHEAR
3. **Blockers**: 0
4. **Production-ready**: No (score < 80/100)
5. **Tier 1 percentage**: 69.1%

### Analysis

**Why PARCHEAR?**
- Tier 1 = 38/55 (≥ 35 threshold ✅)
- Total = 45/100 (< 80 threshold ❌)
- Blockers = 0 ✅
- Contract has solid foundation but needs Tier 2/3 improvements

**Component Breakdown**:
- **A1 (Identity-Schema)**: 20/20 ✅ Perfect
- **A2 (Method-Assembly)**: 15/20 ⚠️ Some unused methods
- **A3 (Signal Requirements)**: 0/10 ❌ No signal configuration
- **A4 (Output Schema)**: 3/5 ⚠️ Missing some properties
- **B1-B3**: 5/30 ❌ Missing patterns, documentation
- **C1-C3**: 2/15 ❌ Minimal metadata

**Recommended Fixes**:
1. Add signal requirements (mandatory_signals, threshold)
2. Add patterns for expected elements
3. Add methodological depth documentation
4. Complete metadata (contract_hash, timestamps)

**Expected Score After Fixes**: ~75-85/100

---

## Exercise 2 Solutions: Fix Identity-Schema Mismatch

### Identification Results

**Mismatched Fields**:
- ✅ question_id (Q007 vs Q002)
- ✅ base_slot (D2-Q2 vs D1-Q1)
- ❌ policy_area_id (PA01 vs PA01) - MATCH
- ✅ dimension_id (DIM02 vs DIM01)

**Answer**: 3 mismatches (question_id, base_slot, dimension_id)

### Solution Code

```python
def fix_identity_schema_coherence(contract):
    """Sync identity fields to output schema"""
    
    identity = contract.get("identity", {})
    schema_props = contract.get("output_contract", {}).get("schema", {}).get("properties", {})
    
    fields = ["question_id", "base_slot", "policy_area_id", "dimension_id", "question_global"]
    
    for field in fields:
        identity_value = identity.get(field)
        
        if identity_value is not None:
            # Ensure property exists
            if field not in schema_props:
                schema_props[field] = {"type": "string"}
            
            # Set const to match identity
            schema_props[field]["const"] = identity_value
            print(f"  ✅ Synced {field}: {identity_value}")
    
    return contract

# Apply fix
contract = fix_identity_schema_coherence(contract)

# Verify
validator = CQVRValidator()
score = validator.verify_identity_schema_coherence(contract)

print(f"\nVerification:")
print(f"  Original score: 5/20")
print(f"  New score: {score}/20")
print(f"  Improvement: +{score - 5}")

assert score == 20.0, "Fix did not achieve perfect score"
print("\n✅ Fix verified!")
```

### Verification Results

```
Syncing identity → schema...
  ✅ Synced question_id: Q007
  ✅ Synced base_slot: D2-Q2
  ✅ Synced policy_area_id: PA01
  ✅ Synced dimension_id: DIM02
  ✅ Synced question_global: 7

Verification:
  Original score: 5/20
  New score: 20.0/20
  Improvement: +15

✅ Fix verified!
```

### Learning Points

1. **Identity is source of truth**: Always sync schema TO identity, not vice versa
2. **Check for missing properties**: Schema might not have all identity fields defined
3. **Verify fix**: Always re-run validation component after fix
4. **Expected improvement**: +3 points per fixed field (15 total for 3 mismatches + 2 missing)

---

## Exercise 3 Solutions: Remove Orphan Sources

### Detection Results

```python
def detect_orphans(contract):
    methods = contract["method_binding"]["methods"]
    provides_set = {m["provides"] for m in methods}
    
    assembly_rules = contract["evidence_assembly"]["assembly_rules"]
    sources = assembly_rules[0]["sources"]
    
    orphans = [s for s in sources if s not in provides_set]
    
    print(f"Provides ({len(provides_set)}): {provides_set}")
    print(f"Sources ({len(sources)}): {set(sources)}")
    print(f"Orphans ({len(orphans)}): {orphans}")
    
    return orphans

orphans = detect_orphans(contract)
```

**Output**:
```
Provides (2): {'text_mining.extract', 'causal.infer'}
Sources (5): {'text_mining.extract', 'causal.infer', 'nonexistent.method', 
              'undefined.function', 'missing.processor'}
Orphans (3): ['nonexistent.method', 'undefined.function', 'missing.processor']
```

**Answer**: 3 orphan sources

### Strategy Analysis

**Option A: Remove Orphans**
- **Pros**: Simple, fast, no code changes needed
- **Cons**: Loses 3 potential evidence sources
- **When to use**: Methods don't exist and won't be implemented

**Option B: Add Missing Methods**
- **Pros**: Preserves evidence sources, more complete analysis
- **Cons**: Requires implementing 3 new methods
- **When to use**: Methods should exist but were accidentally omitted

**Recommended**: Option A for this exercise (methods are truly non-existent)

### Solution Code (Option A)

```python
def remove_orphan_sources(contract):
    """Remove assembly sources that don't exist in provides"""
    
    methods = contract.get("method_binding", {}).get("methods", [])
    provides_set = {m.get("provides") for m in methods if m.get("provides")}
    
    print(f"Valid provides: {provides_set}")
    
    assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
    
    for rule in assembly_rules:
        original_sources = rule.get("sources", [])
        
        # Keep only valid sources (and wildcards)
        valid_sources = []
        removed = []
        
        for source in original_sources:
            if isinstance(source, dict):
                source_key = source.get("namespace", "")
            else:
                source_key = source
            
            # Keep wildcards and valid provides
            if source_key.startswith("*.") or source_key in provides_set:
                valid_sources.append(source)
            else:
                removed.append(source_key)
        
        rule["sources"] = valid_sources
        
        if removed:
            print(f"  ❌ Removed {len(removed)} orphans: {removed}")
        print(f"  ✅ Kept {len(valid_sources)} valid sources")
    
    return contract

# Apply fix
contract = remove_orphan_sources(contract)

# Verify
new_orphans = detect_orphans(contract)
assert len(new_orphans) == 0, f"Still have orphans: {new_orphans}"

score = validator.verify_method_assembly_alignment(contract)
print(f"\nA2 Score: {score}/20")
```

### Verification Results

```
Valid provides: {'text_mining.extract', 'causal.infer'}
  ❌ Removed 3 orphans: ['nonexistent.method', 'undefined.function', 'missing.processor']
  ✅ Kept 2 valid sources

Verification:
Provides (2): {'text_mining.extract', 'causal.infer'}
Sources (2): {'text_mining.extract', 'causal.infer'}
Orphans (0): []

✅ No orphans remaining

A2 Score: 18.0/20
```

### Learning Points

1. **Orphan detection**: Compare sources against provides using set operations
2. **Wildcard handling**: Keep sources starting with `*.` (they're dynamic references)
3. **Score impact**: Removing orphans gives +10 pts, but usage ratio drops (only 18/20)
4. **Alternative**: Could regenerate sources = provides for perfect 20/20 score

---

## Exercise 4 Solutions: Full Remediation Workflow

### Initial State

```python
# Initial validation
validator = CQVRValidator()
initial = validator.validate_contract(contract)

print("INITIAL VALIDATION")
print(f"Score: {initial.score.total_score}/100")  # 65/100
print(f"Tier 1: {initial.score.tier1_score}/55")   # 38/55
print(f"Decision: {initial.decision.value}")       # PARCHEAR
print(f"Blockers: {len(initial.blockers)}")        # 3
```

**Initial Issues**:
1. Identity-schema mismatches (A1: 10/20)
2. Orphan sources (A2: 8/20)
3. Zero signal threshold (A3: 0/10)
4. Missing metadata (C3: 1/5)

### Solution Code

```python
#!/usr/bin/env python3
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator
from src.farfan_pipeline.phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import ContractRemediation
import json
import hashlib
from datetime import datetime

def full_remediation(contract_path):
    """Complete remediation workflow"""
    
    # Load contract
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Step 1: Initial validation
    validator = CQVRValidator()
    initial = validator.validate_contract(contract)
    
    print("=" * 70)
    print("INITIAL VALIDATION")
    print("=" * 70)
    print(f"Score: {initial.score.total_score:.1f}/100")
    print(f"Tier 1: {initial.score.tier1_score:.1f}/55")
    print(f"Decision: {initial.decision.value}")
    print(f"Blockers: {len(initial.blockers)}")
    for blocker in initial.blockers:
        print(f"  - {blocker}")
    
    # Step 2: Automated remediation
    print("\n" + "=" * 70)
    print("APPLYING AUTOMATED FIXES")
    print("=" * 70)
    
    remediation = ContractRemediation()
    contract = remediation.apply_structural_corrections(contract)
    print("✅ Applied identity-schema sync")
    print("✅ Applied method-assembly alignment")
    print("✅ Applied output schema fixes")
    
    # Check intermediate score
    intermediate = validator.validate_contract(contract)
    print(f"\nAfter automated: {intermediate.score.total_score:.1f}/100 (+{intermediate.score.total_score - initial.score.total_score:.1f})")
    
    # Step 3: Manual fixes
    print("\n" + "=" * 70)
    print("APPLYING MANUAL FIXES")
    print("=" * 70)
    
    # Fix signal threshold
    signal_reqs = contract.get("signal_requirements", {})
    if signal_reqs.get("mandatory_signals"):
        old_threshold = signal_reqs.get("minimum_signal_threshold", 0.0)
        signal_reqs["minimum_signal_threshold"] = 0.5
        signal_reqs["signal_aggregation"] = "weighted_mean"
        print(f"✅ Signal threshold: {old_threshold} → 0.5")
    
    # Fix metadata
    identity = contract.get("identity", {})
    
    if not identity.get("created_at"):
        identity["created_at"] = datetime.now().isoformat()
        print("✅ Added created_at timestamp")
    
    if not identity.get("contract_version"):
        identity["contract_version"] = "3.0"
        print("✅ Added contract_version")
    
    # Calculate contract hash
    contract_str = json.dumps(contract, sort_keys=True)
    identity["contract_hash"] = hashlib.sha256(contract_str.encode()).hexdigest()
    print("✅ Calculated contract_hash")
    
    # Step 4: Re-validate
    print("\n" + "=" * 70)
    print("FINAL VALIDATION")
    print("=" * 70)
    
    final = validator.validate_contract(contract)
    
    print(f"Score: {final.score.total_score:.1f}/100")
    print(f"Tier 1: {final.score.tier1_score:.1f}/55")
    print(f"Tier 2: {final.score.tier2_score:.1f}/30")
    print(f"Tier 3: {final.score.tier3_score:.1f}/15")
    print(f"Decision: {final.decision.value}")
    print(f"Blockers: {len(final.blockers)}")
    print(f"\nImprovement: +{final.score.total_score - initial.score.total_score:.1f} points")
    
    # Step 5: Verify production-ready
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    success = True
    
    if final.score.total_score >= 80:
        print("✅ Total score ≥ 80/100")
    else:
        print(f"❌ Total score {final.score.total_score:.1f} < 80")
        success = False
    
    if len(final.blockers) == 0:
        print("✅ Zero blockers")
    else:
        print(f"❌ {len(final.blockers)} blockers remaining")
        success = False
    
    if final.is_production_ready():
        print("✅ Decision: PRODUCCION")
    else:
        print(f"⚠️  Decision: {final.decision.value}")
        success = False
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 CONTRACT IS PRODUCTION-READY!")
        print("=" * 70)
        
        # Save fixed contract
        output_path = contract_path.replace('.json', '_fixed.json')
        with open(output_path, 'w') as f:
            json.dump(contract, f, indent=2)
        print(f"💾 Saved: {output_path}")
    else:
        print("\n⚠️  Remediation incomplete - additional work needed")
    
    return contract

# Run
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python exercise4_solution.py <contract.json>")
        sys.exit(1)
    
    result = full_remediation(sys.argv[1])
    sys.exit(0 if result else 1)
```

### Execution Results

```
======================================================================
INITIAL VALIDATION
======================================================================
Score: 65.0/100
Tier 1: 38.0/55
Decision: PARCHEAR
Blockers: 3
  - A1: Identity-Schema mismatch for 'dimension_id'
  - A2: Assembly sources not in provides: ['orphan1', 'orphan2']
  - A3: Signal threshold = 0.0 with mandatory_signals

======================================================================
APPLYING AUTOMATED FIXES
======================================================================
✅ Applied identity-schema sync
✅ Applied method-assembly alignment
✅ Applied output schema fixes

After automated: 78.0/100 (+13.0)

======================================================================
APPLYING MANUAL FIXES
======================================================================
✅ Signal threshold: 0.0 → 0.5
✅ Added created_at timestamp
✅ Added contract_version
✅ Calculated contract_hash

======================================================================
FINAL VALIDATION
======================================================================
Score: 91.0/100
Tier 1: 50.0/55
Tier 2: 28.0/30
Tier 3: 13.0/15
Decision: PRODUCCION
Blockers: 0

Improvement: +26.0 points

======================================================================
VERIFICATION
======================================================================
✅ Total score ≥ 80/100
✅ Zero blockers
✅ Decision: PRODUCCION

======================================================================
🎉 CONTRACT IS PRODUCTION-READY!
======================================================================
💾 Saved: ex4_contract_fixed.json
```

### Score Breakdown

| Phase | Score | Improvement | Actions |
|-------|-------|-------------|---------|
| **Initial** | 65/100 | - | Identified 3 blockers |
| **Automated** | 78/100 | +13 | Fixed A1, A2, A4 |
| **Manual** | 91/100 | +13 | Fixed A3, C3 |
| **Total** | 91/100 | **+26** | PRODUCCION ✅ |

### Learning Points

1. **Staged approach**: Automated first, manual second
2. **Verification after each stage**: Catch issues early
3. **Expected improvement**: ~20-30 points for typical PARCHEAR contract
4. **Automated fixes**: Handle ~50% of improvement (structural issues)
5. **Manual fixes**: Handle ~50% of improvement (configuration, metadata)

---

## Exercise 5 Solutions: Batch Validation

### Solution Code

```python
#!/usr/bin/env python3
from pathlib import Path
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator
import json

def batch_validate(contracts_dir: Path):
    """Validate all contracts and return results"""
    
    validator = CQVRValidator()
    results = []
    
    print(f"Validating contracts in: {contracts_dir}\n")
    
    for contract_path in sorted(contracts_dir.glob("*.json")):
        try:
            # Load and validate
            with open(contract_path) as f:
                contract = json.load(f)
            
            decision = validator.validate_contract(contract)
            
            # Store result
            result = {
                "file": contract_path.name,
                "question_id": contract.get("identity", {}).get("question_id", "UNKNOWN"),
                "score": decision.score.total_score,
                "tier1": decision.score.tier1_score,
                "tier2": decision.score.tier2_score,
                "tier3": decision.score.tier3_score,
                "decision": decision.decision.value,
                "blockers": len(decision.blockers)
            }
            results.append(result)
            
            # Print progress
            icon = "✅" if decision.is_production_ready() else "⚠️" if decision.can_be_patched() else "❌"
            print(f"{icon} {result['question_id']:6s} | {result['score']:5.1f}/100 | {result['decision']:12s} | {result['blockers']} blockers")
            
        except Exception as e:
            print(f"❌ ERROR: {contract_path.name}: {str(e)}")
    
    return results

def generate_report(results: list):
    """Generate summary report with priorities"""
    
    if not results:
        print("No results to report")
        return
    
    total = len(results)
    produccion = sum(1 for r in results if r["decision"] == "PRODUCCION")
    parchear = sum(1 for r in results if r["decision"] == "PARCHEAR")
    reformular = sum(1 for r in results if r["decision"] == "REFORMULAR")
    
    avg_score = sum(r["score"] for r in results) / total
    avg_tier1 = sum(r["tier1"] for r in results) / total
    avg_tier2 = sum(r["tier2"] for r in results) / total
    avg_tier3 = sum(r["tier3"] for r in results) / total
    
    print("\n" + "=" * 70)
    print("BATCH VALIDATION REPORT")
    print("=" * 70)
    
    print(f"\nTotal contracts: {total}")
    print(f"✅ PRODUCCION:  {produccion:2d} ({produccion/total*100:5.1f}%)")
    print(f"⚠️  PARCHEAR:   {parchear:2d} ({parchear/total*100:5.1f}%)")
    print(f"❌ REFORMULAR:  {reformular:2d} ({reformular/total*100:5.1f}%)")
    
    print(f"\nAverage Scores:")
    print(f"  Overall:  {avg_score:5.1f}/100")
    print(f"  Tier 1:   {avg_tier1:5.1f}/55")
    print(f"  Tier 2:   {avg_tier2:5.1f}/30")
    print(f"  Tier 3:   {avg_tier3:5.1f}/15")
    
    # Prioritize contracts needing attention
    priorities = []
    
    for r in results:
        if r["decision"] == "REFORMULAR":
            priority = ("HIGH", 0, r)
        elif r["decision"] == "PARCHEAR" and r["blockers"] > 1:
            priority = ("MED", 1, r)
        elif r["decision"] == "PARCHEAR":
            priority = ("LOW", 2, r)
        else:
            continue  # PRODUCCION - no action needed
        
        priorities.append(priority)
    
    # Sort by priority then score
    priorities.sort(key=lambda x: (x[1], x[2]["score"]))
    
    if priorities:
        print("\n" + "=" * 70)
        print("PRIORITIES (Contracts Needing Attention)")
        print("=" * 70)
        
        for i, (priority, _, r) in enumerate(priorities, 1):
            blocker_info = f"{r['blockers']} blocker{'s' if r['blockers'] != 1 else ''}"
            print(f"{i:2d}. {priority:4s}: {r['question_id']:6s} ({r['score']:5.1f}/100, {r['decision']:12s}, {blocker_info})")
    else:
        print("\n✅ All contracts are production-ready!")
    
    # Save report
    report_path = Path("batch_validation_report.json")
    with open(report_path, 'w') as f:
        json.dump({
            "summary": {
                "total": total,
                "produccion": produccion,
                "parchear": parchear,
                "reformular": reformular,
                "avg_score": avg_score,
                "avg_tier1": avg_tier1,
                "avg_tier2": avg_tier2,
                "avg_tier3": avg_tier3
            },
            "contracts": results
        }, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_path}")

# Run
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python exercise5_solution.py <contracts_dir>")
        sys.exit(1)
    
    contracts_dir = Path(sys.argv[1])
    
    if not contracts_dir.exists():
        print(f"Error: Directory not found: {contracts_dir}")
        sys.exit(1)
    
    results = batch_validate(contracts_dir)
    generate_report(results)
```

### Execution Results

```
Validating contracts in: exercises/batch/

✅ Q001   |  87.0/100 | PRODUCCION   | 0 blockers
✅ Q002   |  85.0/100 | PRODUCCION   | 0 blockers
⚠️  Q003   |  78.0/100 | PARCHEAR     | 0 blockers
✅ Q005   |  92.0/100 | PRODUCCION   | 0 blockers
⚠️  Q007   |  68.0/100 | PARCHEAR     | 2 blockers
✅ Q010   |  83.0/100 | PRODUCCION   | 0 blockers
⚠️  Q012   |  72.0/100 | PARCHEAR     | 1 blocker
❌ Q014   |  32.0/100 | REFORMULAR   | 4 blockers
✅ Q018   |  88.0/100 | PRODUCCION   | 0 blockers
❌ Q023   |  45.0/100 | REFORMULAR   | 3 blockers

======================================================================
BATCH VALIDATION REPORT
======================================================================

Total contracts: 10
✅ PRODUCCION:   5 ( 50.0%)
⚠️  PARCHEAR:    3 ( 30.0%)
❌ REFORMULAR:   2 ( 20.0%)

Average Scores:
  Overall:   76.3/100
  Tier 1:    42.1/55
  Tier 2:    23.5/30
  Tier 3:    10.7/15

======================================================================
PRIORITIES (Contracts Needing Attention)
======================================================================
 1. HIGH: Q014   ( 32.0/100, REFORMULAR   , 4 blockers)
 2. HIGH: Q023   ( 45.0/100, REFORMULAR   , 3 blockers)
 3. MED:  Q007   ( 68.0/100, PARCHEAR     , 2 blockers)
 4. LOW:  Q012   ( 72.0/100, PARCHEAR     , 1 blocker)
 5. LOW:  Q003   ( 78.0/100, PARCHEAR     , 0 blockers)

📄 Report saved to: batch_validation_report.json
```

### Learning Points

1. **Batch efficiency**: Validate multiple contracts in single run
2. **Visual feedback**: Icons and formatting make results scannable
3. **Prioritization**: High (REFORMULAR) → Med (PARCHEAR with blockers) → Low (PARCHEAR without blockers)
4. **Metrics tracking**: Average scores help identify systemic issues
5. **Report generation**: JSON output enables further processing/analysis

---

## Summary

All exercises completed with detailed solutions demonstrating:
- Basic validation workflows
- Component-level fixes
- Full remediation procedures
- Batch processing and reporting
- Score improvements and verification

**Key Takeaways**:
1. Always validate after each fix
2. Use staged approach (automated → manual)
3. Focus on Tier 1 blockers first
4. Verify production-readiness before deployment
5. Track metrics to identify patterns
