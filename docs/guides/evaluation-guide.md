# CQVR Evaluation Guide

## Overview

This guide provides step-by-step instructions for running CQVR evaluations on executor contracts, interpreting results, and taking appropriate actions based on triage decisions.

## Prerequisites

- Python 3.12+
- F.A.R.F.A.N pipeline installed
- Access to executor contracts directory
- Basic understanding of JSON format

## Quick Start

### 1. Run Basic Evaluation

```bash
# Navigate to project root
cd /path/to/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL

# Activate virtual environment (if using one)
source venv/bin/activate

# Run evaluation on single contract
python -c "
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator
import json

with open('path/to/contract.json') as f:
    contract = json.load(f)

validator = CQVRValidator()
decision = validator.validate_contract(contract)

print(f'Score: {decision.score.total_score}/100')
print(f'Decision: {decision.decision.value}')
print(f'Blockers: {len(decision.blockers)}')
"
```

### 2. Interpret Results

CQVR returns three possible decisions:

| Decision | Meaning | Action |
|----------|---------|--------|
| **PRODUCCION** | Ready for production | Deploy immediately |
| **PARCHEAR** | Can be patched | Apply fixes, re-validate |
| **REFORMULAR** | Requires reformulation | Rebuild contract |

---

## Detailed Workflow

### Step 1: Prepare Contract for Evaluation

**1.1 Verify Contract Format**

Ensure contract is valid JSON:
```bash
python -m json.tool contract.json > /dev/null
```

If errors occur, fix JSON syntax before proceeding.

**1.2 Check Required Fields**

Verify contract has all required top-level fields:
```python
required_fields = [
    "identity",
    "method_binding",
    "evidence_assembly",
    "signal_requirements",
    "output_contract",
    "validation_rules",
    "error_handling"
]

import json
with open('contract.json') as f:
    contract = json.load(f)

missing = [field for field in required_fields if field not in contract]
if missing:
    print(f"Missing fields: {missing}")
else:
    print("✅ All required fields present")
```

---

### Step 2: Run CQVR Validation

**2.1 Single Contract Validation**

Create validation script `validate_contract.py`:

```python
#!/usr/bin/env python3
"""Validate single contract with CQVR"""
import sys
import json
from pathlib import Path
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator

def validate_contract(contract_path: Path):
    """Run CQVR validation and print detailed report"""
    
    # Load contract
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Validate
    validator = CQVRValidator()
    decision = validator.validate_contract(contract)
    
    # Print report
    print("=" * 70)
    print(f"CQVR EVALUATION REPORT: {contract_path.name}")
    print("=" * 70)
    
    # Scores
    print(f"\n📊 SCORES:")
    print(f"  Tier 1 (Critical):    {decision.score.tier1_score:5.1f}/55  ({decision.score.tier1_percentage:5.1f}%)")
    print(f"  Tier 2 (Functional):  {decision.score.tier2_score:5.1f}/30  ({decision.score.tier2_percentage:5.1f}%)")
    print(f"  Tier 3 (Quality):     {decision.score.tier3_score:5.1f}/15  ({decision.score.tier3_percentage:5.1f}%)")
    print(f"  ─────────────────────────────────────")
    print(f"  TOTAL:                {decision.score.total_score:5.1f}/100 ({decision.score.total_percentage:5.1f}%)")
    
    # Decision
    decision_icon = {
        "PRODUCCION": "✅",
        "PARCHEAR": "⚠️",
        "REFORMULAR": "❌"
    }
    icon = decision_icon.get(decision.decision.value, "❓")
    print(f"\n🎯 DECISION: {icon} {decision.decision.value}")
    
    # Rationale
    print(f"\n💡 RATIONALE:")
    print(f"  {decision.rationale}")
    
    # Blockers
    if decision.blockers:
        print(f"\n🚫 BLOCKERS ({len(decision.blockers)}):")
        for blocker in decision.blockers:
            print(f"  • {blocker}")
    else:
        print(f"\n✅ NO BLOCKERS")
    
    # Warnings
    if decision.warnings:
        print(f"\n⚠️  WARNINGS ({len(decision.warnings)}):")
        for warning in decision.warnings[:5]:  # Show first 5
            print(f"  • {warning}")
        if len(decision.warnings) > 5:
            print(f"  ... and {len(decision.warnings) - 5} more")
    
    # Recommendations
    if decision.recommendations:
        print(f"\n💡 RECOMMENDATIONS ({len(decision.recommendations)}):")
        for rec in decision.recommendations[:3]:  # Show top 3
            print(f"  • {rec['issue']}: {rec['fix']}")
            print(f"    Priority: {rec['priority']}, Impact: {rec.get('impact', 'N/A')}")
    
    print("\n" + "=" * 70)
    
    return decision

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_contract.py <contract.json>")
        sys.exit(1)
    
    contract_path = Path(sys.argv[1])
    if not contract_path.exists():
        print(f"Error: Contract not found: {contract_path}")
        sys.exit(1)
    
    decision = validate_contract(contract_path)
    
    # Exit with appropriate code
    if decision.is_production_ready():
        sys.exit(0)
    elif decision.can_be_patched():
        sys.exit(1)
    else:
        sys.exit(2)
```

Run validation:
```bash
python validate_contract.py contracts/Q001.v3.json
```

**2.2 Batch Validation**

Create batch validation script `validate_all.py`:

```python
#!/usr/bin/env python3
"""Validate all contracts in directory"""
import json
from pathlib import Path
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator

def validate_all_contracts(contracts_dir: Path, output_file: Path = None):
    """Validate all contracts and generate summary"""
    
    validator = CQVRValidator()
    results = []
    
    # Find all contract files
    contract_files = list(contracts_dir.glob("*.json"))
    print(f"Found {len(contract_files)} contracts to validate\n")
    
    # Validate each contract
    for contract_path in sorted(contract_files):
        try:
            with open(contract_path) as f:
                contract = json.load(f)
            
            decision = validator.validate_contract(contract)
            
            result = {
                "file": contract_path.name,
                "question_id": contract.get("identity", {}).get("question_id", "UNKNOWN"),
                "score": decision.score.total_score,
                "tier1": decision.score.tier1_score,
                "tier2": decision.score.tier2_score,
                "tier3": decision.score.tier3_score,
                "decision": decision.decision.value,
                "blockers": len(decision.blockers),
                "warnings": len(decision.warnings)
            }
            results.append(result)
            
            # Print progress
            icon = "✅" if decision.is_production_ready() else "⚠️" if decision.can_be_patched() else "❌"
            print(f"{icon} {result['question_id']:6s} | {result['score']:5.1f}/100 | {result['decision']:12s} | {result['blockers']} blockers")
            
        except Exception as e:
            print(f"❌ {contract_path.name}: ERROR - {str(e)}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total = len(results)
    produccion = sum(1 for r in results if r["decision"] == "PRODUCCION")
    parchear = sum(1 for r in results if r["decision"] == "PARCHEAR")
    reformular = sum(1 for r in results if r["decision"] == "REFORMULAR")
    
    avg_score = sum(r["score"] for r in results) / total if total > 0 else 0
    avg_tier1 = sum(r["tier1"] for r in results) / total if total > 0 else 0
    
    print(f"\nTotal contracts:      {total}")
    print(f"  ✅ PRODUCCION:      {produccion:3d} ({produccion/total*100:5.1f}%)")
    print(f"  ⚠️  PARCHEAR:        {parchear:3d} ({parchear/total*100:5.1f}%)")
    print(f"  ❌ REFORMULAR:      {reformular:3d} ({reformular/total*100:5.1f}%)")
    print(f"\nAverage score:        {avg_score:5.1f}/100")
    print(f"Average Tier 1:       {avg_tier1:5.1f}/55")
    
    # Save results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": total,
                    "produccion": produccion,
                    "parchear": parchear,
                    "reformular": reformular,
                    "avg_score": avg_score,
                    "avg_tier1": avg_tier1
                },
                "contracts": results
            }, f, indent=2)
        print(f"\n📄 Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validate_all.py <contracts_dir> [output.json]")
        sys.exit(1)
    
    contracts_dir = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    results = validate_all_contracts(contracts_dir, output_file)
```

Run batch validation:
```bash
python validate_all.py contracts/specialized/ results.json
```

---

### Step 3: Interpret Results

**3.1 Understanding Scores**

Each score component indicates contract quality:

**Tier 1: Critical Components (55 pts)**
- **≥ 45/55**: Excellent foundation, production-ready
- **35-44/55**: Acceptable foundation, patchable
- **< 35/55**: Poor foundation, requires reformulation

**Tier 2: Functional Components (30 pts)**
- **≥ 25/30**: Good functional quality
- **20-24/30**: Acceptable functionality
- **< 20/30**: Poor functional quality

**Tier 3: Quality Components (15 pts)**
- **≥ 12/15**: Excellent documentation
- **8-11/15**: Good documentation
- **< 8/15**: Poor documentation

**Total Score (100 pts)**
- **≥ 80/100**: Production quality
- **70-79/100**: Needs improvement
- **< 70/100**: Significant issues

**3.2 Understanding Decisions**

**PRODUCCION** ✅
```
Tier 1: 48/55 (87.3%)
Total:  87/100 (87%)
Blockers: 0
```
**Meaning**: Contract meets all production standards
**Action**: Deploy immediately

---

**PARCHEAR** ⚠️
```
Tier 1: 40/55 (72.7%)
Total:  73/100 (73%)
Blockers: 2
```
**Meaning**: Minor issues, fixable with patches
**Action**: Review blockers, apply fixes, re-validate

---

**REFORMULAR** ❌
```
Tier 1: 28/55 (50.9%)
Total:  65/100 (65%)
Blockers: 4
```
**Meaning**: Fundamental issues, patching insufficient
**Action**: Rebuild contract from questionnaire monolith

---

### Step 4: Take Action Based on Decision

**4.1 PRODUCCION - Deploy to Production**

Contract is ready for deployment:

```bash
# 1. Tag contract as validated
python -c "
import json
from datetime import datetime

with open('contract.json') as f:
    contract = json.load(f)

contract['cqvr_validation'] = {
    'decision': 'PRODUCCION',
    'score': 87,
    'validated_at': datetime.now().isoformat(),
    'validator_version': 'v2.0'
}

with open('contract.json', 'w') as f:
    json.dump(contract, f, indent=2)
"

# 2. Move to production directory
mv contract.json contracts/production/

# 3. Deploy to pipeline
python deploy_contract.py contract.json
```

**4.2 PARCHEAR - Apply Fixes**

Contract has fixable issues. See [Remediation Guide](remediation-guide.md) for detailed fix procedures.

Quick fix workflow:
```bash
# 1. Review blockers
python validate_contract.py contract.json | grep "BLOCKERS"

# 2. Apply automated fixes
python -c "
from src.farfan_pipeline.phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import ContractRemediation
import json

with open('contract.json') as f:
    contract = json.load(f)

remediation = ContractRemediation()
patched = remediation.apply_structural_corrections(contract)

with open('contract_patched.json', 'w') as f:
    json.dump(patched, f, indent=2)
"

# 3. Re-validate
python validate_contract.py contract_patched.json

# 4. If score ≥ 80/100, deploy
```

**4.3 REFORMULAR - Rebuild Contract**

Contract has fundamental issues. Rebuild from source:

```bash
# 1. Identify contract question
question_id=$(jq -r '.identity.question_id' contract.json)

# 2. Rebuild from questionnaire monolith
python transform_contract.py $question_id --output contract_rebuilt.json

# 3. Validate rebuilt contract
python validate_contract.py contract_rebuilt.json

# 4. Replace old contract if validation passes
mv contract_rebuilt.json contract.json
```

---

## Common Evaluation Scenarios

### Scenario 1: New Contract Authoring

**Goal**: Validate contract during development

**Workflow**:
1. Author contract JSON
2. Run CQVR validation
3. Fix issues iteratively
4. Validate until score ≥ 80/100

```bash
# Iterative validation loop
while true; do
    python validate_contract.py my_contract.json
    read -p "Continue editing? (y/n) " yn
    case $yn in
        [Yy]* ) continue;;
        [Nn]* ) break;;
    esac
done
```

---

### Scenario 2: Contract Migration

**Goal**: Validate existing contracts for quality

**Workflow**:
1. Run batch validation on all contracts
2. Identify contracts needing remediation
3. Apply fixes to PARCHEAR contracts
4. Rebuild REFORMULAR contracts
5. Re-validate all

```bash
# 1. Initial validation
python validate_all.py contracts/ initial_results.json

# 2. Filter contracts by decision
jq '.contracts[] | select(.decision == "PARCHEAR") | .file' initial_results.json

# 3. Apply fixes (see remediation guide)
for file in $(jq -r '.contracts[] | select(.decision == "PARCHEAR") | .file' initial_results.json); do
    python apply_fixes.py "contracts/$file"
done

# 4. Re-validate
python validate_all.py contracts/ final_results.json
```

---

### Scenario 3: CI/CD Integration

**Goal**: Validate contracts in continuous integration pipeline

**Workflow**:
1. Run validation on changed contracts
2. Fail build if score < 80/100 or blockers > 0
3. Generate validation report

**GitHub Actions Example**:
```yaml
name: Validate Contracts

on:
  pull_request:
    paths:
      - 'contracts/**/*.json'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Validate changed contracts
        run: |
          for file in $(git diff --name-only origin/main | grep '\.json$'); do
            python validate_contract.py "$file" || exit 1
          done
      
      - name: Generate report
        if: always()
        run: python validate_all.py contracts/ validation_report.json
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation_report.json
```

---

## Tips and Best Practices

### Tip 1: Validate Early and Often
Run CQVR during contract authoring, not just before deployment.

### Tip 2: Focus on Tier 1 First
Tier 1 components are critical. Ensure Tier 1 ≥ 35/55 before worrying about Tier 2/3.

### Tip 3: Fix Blockers Before Warnings
Blockers prevent production deployment. Fix all blockers first, then address warnings.

### Tip 4: Use Automated Fixes
For PARCHEAR contracts, use automated remediation tools before manual editing.

### Tip 5: Track Quality Over Time
Save validation results to track contract quality trends.

```bash
# Append results to history
python validate_all.py contracts/ results_$(date +%Y%m%d).json
```

### Tip 6: Batch Process Similar Issues
If multiple contracts have same blocker, fix all at once with script.

### Tip 7: Document Custom Fixes
If you apply manual fixes not covered by automated remediation, document them.

---

## Troubleshooting

### Issue: Validation takes too long

**Solution**: Use batch validation with parallelization
```python
from concurrent.futures import ProcessPoolExecutor

def validate_parallel(contract_files):
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(validate_single, contract_files)
    return list(results)
```

### Issue: Contract scores inconsistently

**Solution**: Ensure deterministic validation
```python
# Sort sets before iteration
provides_set = sorted(provides_set)
```

### Issue: Can't find validator module

**Solution**: Add project root to Python path
```bash
export PYTHONPATH=/path/to/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL:$PYTHONPATH
```

---

## See Also

- [Scoring System](../cqvr/scoring-system.md) - Detailed scoring rubric
- [Decision Matrix](../cqvr/decision-matrix.md) - Triage logic
- [Remediation Guide](remediation-guide.md) - Fix procedures
- [Troubleshooting](../cqvr/troubleshooting.md) - Common issues
- [API Reference](../cqvr/api-reference.md) - Code examples
