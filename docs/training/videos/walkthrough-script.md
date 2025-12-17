# CQVR Video Walkthrough Script

## Video 1: Introduction to CQVR (10 minutes)

### Scene 1: Welcome and Overview (2 min)

**[SCREEN: Title slide "CQVR: Contract Quality Verification and Remediation"]**

"Welcome to this tutorial on CQVR - the Contract Quality Verification and Remediation system. In this series, you'll learn how to validate executor contracts, interpret quality scores, and fix common issues.

CQVR is a three-tier scoring system that evaluates contracts on a 100-point scale. It helps ensure contracts meet production quality standards before deployment."

**[SCREEN: Show CQVR score breakdown visualization]**

"Let's start with the basics."

---

### Scene 2: Three-Tier System Explained (3 min)

**[SCREEN: Tier 1 components diagram]**

"CQVR uses three tiers to evaluate contract quality:

**Tier 1: Critical Components** - 55 points
These are foundation elements required for execution:
- Identity-Schema Coherence: 20 points
- Method-Assembly Alignment: 20 points
- Signal Requirements: 10 points
- Output Schema: 5 points

If Tier 1 falls below 35 points, the contract requires reformulation."

**[SCREEN: Tier 2 components diagram]**

"**Tier 2: Functional Components** - 30 points
These enable proper evidence processing:
- Pattern Coverage: 10 points
- Method Specificity: 10 points
- Validation Rules: 10 points"

**[SCREEN: Tier 3 components diagram]**

"**Tier 3: Quality Components** - 15 points
These ensure maintainability:
- Documentation Quality: 5 points
- Human Template: 5 points
- Metadata Completeness: 5 points

Your goal: reach 80/100 total score with zero blockers for production deployment."

---

### Scene 3: Decision Matrix (2 min)

**[SCREEN: Decision matrix flowchart]**

"CQVR makes one of three triage decisions:

**PRODUCCION** - Ready for deployment
- Requires: Tier 1 ≥ 45, Total ≥ 80, Zero blockers

**PARCHEAR** - Can be patched
- Requires: Tier 1 ≥ 35, Total ≥ 70, Blockers ≤ 2

**REFORMULAR** - Requires rebuild
- Triggered by: Tier 1 < 35 OR too many blockers

The decision tells you what action to take next."

---

### Scene 4: Your First Validation (3 min)

**[SCREEN: Terminal with code editor]**

"Let's run your first CQVR validation. I'll show you the basic workflow."

**[TYPE]**
```python
from contract_validator_cqvr import CQVRValidator
import json

with open('contract.json') as f:
    contract = json.load(f)

validator = CQVRValidator()
decision = validator.validate_contract(contract)

print(f"Score: {decision.score.total_score}/100")
print(f"Decision: {decision.decision.value}")
```

**[RUN CODE, SHOW OUTPUT]**
```
Score: 73/100
Decision: PARCHEAR
Blockers: 2
```

"This contract scored 73/100 with a PARCHEAR decision. That means it has fixable issues. Let's see what those blockers are."

**[TYPE]**
```python
for blocker in decision.blockers:
    print(f"- {blocker}")
```

**[SHOW OUTPUT]**
```
- A3: Signal threshold = 0.0 but mandatory_signals defined
- A4: Required field 'validation' not in properties
```

"In the next video, we'll learn how to fix these issues. Thanks for watching!"

---

## Video 2: Running Evaluations (15 minutes)

### Scene 1: Setting Up (2 min)

**[SCREEN: Project directory structure]**

"Welcome back! In this video, we'll run evaluations on real contracts and interpret the results.

First, make sure your environment is set up:
1. Python 3.12+ installed
2. F.A.R.F.A.N pipeline installed
3. Contract files ready

Let's create a validation script."

---

### Scene 2: Single Contract Validation (5 min)

**[SCREEN: Code editor with validate_contract.py]**

"Here's a complete validation script that provides detailed output."

**[SHOW CODE, EXPLAIN KEY PARTS]**
```python
#!/usr/bin/env python3
"""Validate single contract with detailed report"""
import sys
import json
from pathlib import Path
from contract_validator_cqvr import CQVRValidator

def validate_contract(contract_path: Path):
    # Load contract
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Validate
    validator = CQVRValidator()
    decision = validator.validate_contract(contract)
    
    # Print report
    print("=" * 70)
    print(f"CQVR EVALUATION: {contract_path.name}")
    print("=" * 70)
    
    # Scores
    print(f"\nSCORES:")
    print(f"  Tier 1: {decision.score.tier1_score:5.1f}/55  ({decision.score.tier1_percentage:5.1f}%)")
    print(f"  Tier 2: {decision.score.tier2_score:5.1f}/30  ({decision.score.tier2_percentage:5.1f}%)")
    print(f"  Tier 3: {decision.score.tier3_score:5.1f}/15  ({decision.score.tier3_percentage:5.1f}%)")
    print(f"  TOTAL:  {decision.score.total_score:5.1f}/100 ({decision.score.total_percentage:5.1f}%)")
    
    # Decision
    print(f"\nDECISION: {decision.decision.value}")
    
    # Blockers
    if decision.blockers:
        print(f"\nBLOCKERS ({len(decision.blockers)}):")
        for blocker in decision.blockers:
            print(f"  • {blocker}")
    
    return decision

if __name__ == "__main__":
    contract_path = Path(sys.argv[1])
    validate_contract(contract_path)
```

**[RUN SCRIPT ON SAMPLE CONTRACT]**

"Let's run this on Q001 contract."

**[SHOW TERMINAL OUTPUT]**
```
CQVR EVALUATION: Q001.v3.json
======================================================================

SCORES:
  Tier 1:  48.0/55  (87.3%)
  Tier 2:  27.0/30  (90.0%)
  Tier 3:  12.0/15  (80.0%)
  TOTAL:   87.0/100 (87.0%)

DECISION: PRODUCCION

NO BLOCKERS
```

"Excellent! This contract is production-ready with 87/100 points and zero blockers."

---

### Scene 3: Interpreting Results (3 min)

**[SCREEN: Results breakdown visualization]**

"Let's understand what these scores mean:

**Tier 1: 48/55 (87.3%)**
- This is above the 45-point production threshold
- Critical components are solid
- Minor issues don't block deployment

**Tier 2: 27/30 (90.0%)**
- Functional components working well
- Good pattern coverage and validation rules

**Tier 3: 12/15 (80.0%)**
- Documentation quality is good
- Room for improvement but not critical

**Total: 87/100**
- Exceeds 80-point production threshold
- No blockers = ready to deploy"

---

### Scene 4: Batch Validation (5 min)

**[SCREEN: Batch validation script]**

"For multiple contracts, use batch validation."

**[SHOW AND RUN CODE]**
```python
#!/usr/bin/env python3
"""Validate all contracts in directory"""
from pathlib import Path
from contract_validator_cqvr import CQVRValidator
import json

def validate_all(contracts_dir: Path):
    validator = CQVRValidator()
    results = []
    
    for contract_path in sorted(contracts_dir.glob("*.json")):
        with open(contract_path) as f:
            contract = json.load(f)
        
        decision = validator.validate_contract(contract)
        
        result = {
            "file": contract_path.name,
            "score": decision.score.total_score,
            "decision": decision.decision.value,
            "blockers": len(decision.blockers)
        }
        results.append(result)
        
        # Print progress
        icon = "✅" if decision.is_production_ready() else "⚠️" if decision.can_be_patched() else "❌"
        print(f"{icon} {result['file']:20s} | {result['score']:5.1f}/100 | {result['decision']:12s}")
    
    # Summary
    total = len(results)
    produccion = sum(1 for r in results if r["decision"] == "PRODUCCION")
    
    print(f"\nSummary: {produccion}/{total} production-ready ({produccion/total*100:.0f}%)")
    
    return results

# Run
results = validate_all(Path("contracts/specialized/"))
```

**[SHOW OUTPUT]**
```
✅ Q001.v3.json         |  87.0/100 | PRODUCCION  
⚠️  Q002.v3.json         |  73.0/100 | PARCHEAR    
✅ Q003.v3.json         |  85.0/100 | PRODUCCION  
❌ Q014.v3.json         |  32.0/100 | REFORMULAR  

Summary: 2/4 production-ready (50%)
```

"This gives you a quick overview of contract quality across your repository."

---

## Video 3: Fixing Common Issues (20 minutes)

### Scene 1: Identity-Schema Mismatch (5 min)

**[SCREEN: Contract with mismatch highlighted]**

"Let's fix the most common issue: identity-schema mismatches.

Here's a contract where identity says Q001 but schema says Q002."

**[SHOW PROBLEM]**
```json
{
  "identity": {
    "question_id": "Q001"
  },
  "output_contract": {
    "schema": {
      "properties": {
        "question_id": {"const": "Q002"}  // MISMATCH!
      }
    }
  }
}
```

"This causes runtime errors when the contract outputs Q002 but was supposed to process Q001.

Let's fix it programmatically."

**[TYPE AND EXPLAIN CODE]**
```python
def fix_identity_schema_coherence(contract):
    """Sync identity fields to output schema"""
    
    identity = contract["identity"]
    schema_props = contract["output_contract"]["schema"]["properties"]
    
    # Sync each identity field
    for field in ["question_id", "policy_area_id", "dimension_id", 
                  "question_global", "base_slot"]:
        if field in identity:
            # Ensure property exists
            if field not in schema_props:
                schema_props[field] = {}
            
            # Set const to match identity
            schema_props[field]["const"] = identity[field]
            print(f"✅ Synced {field}: {identity[field]}")
    
    return contract

# Apply fix
contract = fix_identity_schema_coherence(contract)

# Verify
validator = CQVRValidator()
score = validator.verify_identity_schema_coherence(contract)
print(f"A1 Score: {score}/20")  # Should be 20/20
```

**[RUN AND SHOW OUTPUT]**
```
✅ Synced question_id: Q001
✅ Synced policy_area_id: PA01
✅ Synced dimension_id: DIM01
✅ Synced question_global: 1
✅ Synced base_slot: D1-Q1
A1 Score: 20.0/20
```

"Perfect! All fields now match. Score improved from 8/20 to 20/20."

---

### Scene 2: Zero Signal Threshold (4 min)

**[SCREEN: Signal threshold problem]**

"Another critical issue: zero signal threshold with mandatory signals.

This is dangerous because it allows zero-confidence evidence to pass validation."

**[SHOW PROBLEM]**
```json
{
  "signal_requirements": {
    "mandatory_signals": ["feasibility_score"],
    "minimum_signal_threshold": 0.0  // CRITICAL!
  }
}
```

"Let's fix it."

**[TYPE AND EXPLAIN CODE]**
```python
def fix_signal_threshold(contract):
    """Set appropriate signal threshold"""
    
    signal_reqs = contract.get("signal_requirements", {})
    
    if signal_reqs.get("mandatory_signals"):
        # Set threshold to 0.5 (50% confidence minimum)
        old_threshold = signal_reqs.get("minimum_signal_threshold", 0.0)
        signal_reqs["minimum_signal_threshold"] = 0.5
        
        print(f"📊 Threshold: {old_threshold} → 0.5")
        
        # Set aggregation if missing
        if not signal_reqs.get("signal_aggregation"):
            signal_reqs["signal_aggregation"] = "weighted_mean"
            print("✅ Set aggregation: weighted_mean")
    
    return contract

contract = fix_signal_threshold(contract)

# Verify
score = validator.verify_signal_requirements(contract)
print(f"A3 Score: {score}/10")
```

**[RUN AND SHOW OUTPUT]**
```
📊 Threshold: 0.0 → 0.5
✅ Set aggregation: weighted_mean
A3 Score: 10.0/10
```

"Great! Now only high-confidence signals pass validation."

---

### Scene 3: Orphan Sources (5 min)

**[SCREEN: Orphan sources visualization]**

"Orphan sources are assembly rules that reference methods that don't exist.

Let's see an example."

**[SHOW PROBLEM]**
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
        "nonexistent.method",  // ORPHAN!
        "undefined.function"   // ORPHAN!
      ]
    }]
  }
}
```

"At runtime, the system will try to call 'nonexistent.method' and crash. Let's fix it."

**[TYPE CODE]**
```python
def remove_orphan_sources(contract):
    """Remove sources that don't exist in provides"""
    
    # Get valid provides
    methods = contract["method_binding"]["methods"]
    provides_set = {m["provides"] for m in methods}
    
    print(f"Valid provides: {provides_set}")
    
    # Filter orphan sources
    assembly_rules = contract["evidence_assembly"]["assembly_rules"]
    
    for rule in assembly_rules:
        original_sources = rule["sources"]
        valid_sources = [s for s in original_sources if s in provides_set]
        
        orphans = set(original_sources) - set(valid_sources)
        if orphans:
            print(f"❌ Removed orphans: {orphans}")
        
        rule["sources"] = valid_sources
        print(f"✅ Kept {len(valid_sources)} valid sources")
    
    return contract

contract = remove_orphan_sources(contract)
```

**[RUN AND SHOW OUTPUT]**
```
Valid provides: {'text_mining.extract', 'causal.infer'}
❌ Removed orphans: {'nonexistent.method', 'undefined.function'}
✅ Kept 2 valid sources
A2 Score: 18.0/20
```

---

### Scene 4: Complete Remediation (6 min)

**[SCREEN: Full remediation workflow]**

"Let's put it all together with a complete remediation workflow.

We'll start with a contract scoring 65/100 and bring it to production quality."

**[SHOW CODE]**
```python
def full_remediation(contract_path):
    """Complete remediation workflow"""
    
    # Load
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Initial validation
    validator = CQVRValidator()
    initial = validator.validate_contract(contract)
    
    print(f"INITIAL: {initial.score.total_score:.1f}/100 - {initial.decision.value}")
    
    # Apply automated fixes
    from cqvr_validator import ContractRemediation
    remediation = ContractRemediation()
    contract = remediation.apply_structural_corrections(contract)
    
    # Apply manual fixes
    contract = fix_signal_threshold(contract)
    contract = fix_metadata(contract)
    
    # Re-validate
    final = validator.validate_contract(contract)
    
    print(f"FINAL:   {final.score.total_score:.1f}/100 - {final.decision.value}")
    print(f"IMPROVEMENT: +{final.score.total_score - initial.score.total_score:.1f} points")
    
    if final.is_production_ready():
        print("✅ PRODUCTION READY!")
        # Save fixed contract
        output_path = contract_path.replace('.json', '_fixed.json')
        with open(output_path, 'w') as f:
            json.dump(contract, f, indent=2)
    
    return contract

# Run
contract = full_remediation('contract.json')
```

**[RUN AND SHOW OUTPUT WITH PROGRESS]**
```
INITIAL: 65.0/100 - PARCHEAR

Applying automated fixes...
✅ Fixed identity-schema coherence
✅ Removed orphan sources
✅ Added missing schema properties

Applying manual fixes...
📊 Signal threshold: 0.0 → 0.5
✅ Updated metadata

FINAL:   87.0/100 - PRODUCCION
IMPROVEMENT: +22.0 points

✅ PRODUCTION READY!
```

"Excellent! We've successfully remediated the contract from 65 to 87 points."

---

## Video 4: Best Practices (12 minutes)

### Scene 1: Contract Authoring (3 min)

**[SCREEN: Best practices checklist]**

"Let's talk about best practices for working with CQVR.

**Rule 1: Build from Templates**
Don't start from scratch - use validated templates."

**[SHOW CODE]**
```python
def create_from_template(question_id, template="contracts/template.json"):
    with open(template) as f:
        contract = json.load(f)
    
    # Update identity
    contract["identity"]["question_id"] = question_id
    # ... update other fields
    
    return contract
```

"**Rule 2: Never Copy-Paste Contracts**
This causes identity mismatches. Generate from questionnaire monolith instead."

"**Rule 3: Validate Early and Often**
Don't wait until deployment - validate during development."

---

### Scene 2: Validation Workflow (3 min)

**[SCREEN: Development workflow diagram]**

"Here's the recommended validation workflow:

1. **Create contract skeleton** → Validate (target: Tier 1 ≥ 35)
2. **Add methods and patterns** → Validate (target: Tier 1 ≥ 45)
3. **Add documentation** → Validate (target: Total ≥ 80)
4. **Commit to repository** → CI validates
5. **Deploy to production** → Final validation

Each stage has clear quality gates."

---

### Scene 3: Remediation Strategy (3 min)

**[SCREEN: Remediation decision tree]**

"When fixing issues, follow this strategy:

**If REFORMULAR**: Don't patch - rebuild from monolith

**If PARCHEAR**:
1. Apply automated fixes first
2. Fix Tier 1 blockers
3. Address Tier 2/3 issues
4. Re-validate after each stage

**Focus on**: Tier 1 > Tier 2 > Tier 3

**Stop when**: Score ≥ 80, Blockers = 0"

---

### Scene 4: Team Collaboration (3 min)

**[SCREEN: Team workflow]**

"For team success:

**Establish Quality Gates**:
- Pre-commit hook: Validates contracts before commit
- Pull request: CI validates changed contracts
- Deployment: Production gate requires 80/100

**Share Validation Reports**:
- Weekly quality metrics
- Common issues identified
- Remediation patterns documented

**Maintain History**:
- Track quality trends
- Identify regressions
- Celebrate improvements"

---

## Video 5: Advanced Topics (15 minutes)

### Scene 1: CI/CD Integration (4 min)
- GitHub Actions workflow
- Automated validation on PR
- Blocking deployments

### Scene 2: Quality Monitoring (4 min)
- Tracking metrics over time
- Identifying trends
- Regression detection

### Scene 3: Custom Remediation (4 min)
- Writing custom fix scripts
- Domain-specific issues
- Batch processing

### Scene 4: Performance Optimization (3 min)
- Parallel validation
- Caching results
- Profiling slow validations

---

## Series Summary

**5 Videos Total: ~72 minutes**

1. Introduction to CQVR (10 min)
2. Running Evaluations (15 min)
3. Fixing Common Issues (20 min)
4. Best Practices (12 min)
5. Advanced Topics (15 min)

Each video includes:
- Clear explanations
- Live code demonstrations
- Real examples
- Practical takeaways

**Target Audience**: 
- Contract authors
- Quality engineers
- DevOps teams
- Technical leads

**Prerequisites**:
- Basic Python knowledge
- Familiarity with JSON
- Understanding of the F.A.R.F.A.N pipeline

---

## Additional Resources

After watching, viewers should:
- Read the [Evaluation Guide](../guides/evaluation-guide.md)
- Work through [Training Exercises](exercises/training-exercises.md)
- Reference [API Documentation](../cqvr/api-reference.md)
- Consult [Troubleshooting Guide](../cqvr/troubleshooting.md)
