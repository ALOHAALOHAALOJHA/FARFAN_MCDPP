# Transformation Requirements Guide: Q005-Q020 Contract Audit

## Quick Reference

This guide provides actionable steps for addressing issues identified in the CQVR v2.0 audit of contracts Q005-Q020.

## Priority Matrix

```
🔴 CRITICAL → BLOCK DEPLOYMENT → Fix immediately
🟠 HIGH     → DEGRADED QUALITY → Fix before next release
🟡 MEDIUM   → UX IMPACT       → Fix in maintenance cycle
```

## CRITICAL Issues (BLOCKING)

### 1. Schema Mismatch (category: schema_mismatch)

**Problem**: Identity fields don't match output_contract.schema.properties constants

**Impact**: Contract validation fails, executor cannot process results

**Fix**:
```python
# In Q0XX.v3.json, ensure exact match:
identity = {
    "question_id": "Q0XX",
    "policy_area_id": "PA01",
    "dimension_id": "DIM0X",
    "question_global": XX,
    "base_slot": "DX-QY"
}

# Must match:
output_contract.schema.properties = {
    "question_id": {"const": "Q0XX"},      # EXACT match
    "policy_area_id": {"const": "PA01"},   # EXACT match
    "dimension_id": {"const": "DIM0X"},    # EXACT match
    "question_global": {"const": XX},      # EXACT match
    "base_slot": {"const": "DX-QY"}        # EXACT match
}
```

**Verification**:
```bash
# Check specific contract
python -c "
import json
c = json.load(open('src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q0XX.v3.json'))
identity = c['identity']
schema = c['output_contract']['schema']['properties']
for field in ['question_id', 'policy_area_id', 'dimension_id', 'question_global', 'base_slot']:
    match = identity[field] == schema[field]['const']
    print(f'{field}: {\"✓\" if match else \"✗\"} {identity[field]} vs {schema[field][\"const\"]}')
"
```

### 2. Assembly Orphans (category: assembly_orphans)

**Problem**: evidence_assembly rules reference provides that don't exist in method_binding

**Impact**: Assembly fails at runtime, evidence cannot be collected

**Fix**:
```python
# Step 1: Collect all actual provides
provides = [m['provides'] for m in contract['method_binding']['methods']]
# Example: ['temporallogicverifier.check_deadline_constraints', 'causalinferencesetup.identify_failure_points', ...]

# Step 2: Update assembly_rules to ONLY use these provides
contract['evidence_assembly']['assembly_rules'] = [
    {
        "target": "elements_found",
        "sources": provides,  # Use ALL actual provides
        "merge_strategy": "concat"
    },
    {
        "target": "confidence_scores",
        "sources": [p for p in provides if 'bayesian' in p or 'confidence' in p],
        "merge_strategy": "weighted_mean"
    }
]

# Step 3: Remove ANY source that doesn't exist in provides
# ❌ BAD: "sources": ["text_mining.critical_links", "non_existent_method"]
# ✓ GOOD: "sources": [p for p in provides if 'text_mining' in p]
```

**Automated Fix Script**:
```python
# fix_assembly_orphans.py
import json
from pathlib import Path

def fix_assembly(contract_path):
    with open(contract_path) as f:
        contract = json.load(f)
    
    provides = {m['provides'] for m in contract['method_binding']['methods']}
    
    for rule in contract['evidence_assembly']['assembly_rules']:
        sources = rule.get('sources', [])
        valid_sources = [s for s in sources if s in provides]
        rule['sources'] = valid_sources
    
    with open(contract_path, 'w') as f:
        json.dump(contract, f, indent=2, ensure_ascii=False)
    
    print(f"Fixed {contract_path}")

# Usage:
# fix_assembly('src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q007.v3.json')
```

### 3. Signal Threshold Zero (category: signal_threshold_zero)

**Problem**: minimum_signal_threshold = 0.0 with mandatory_signals defined

**Impact**: Signal validation never triggers, executor accepts invalid data

**Fix**:
```python
# Change threshold to non-zero value
contract['signal_requirements']['minimum_signal_threshold'] = 0.5  # or 0.3 minimum

# Rule: If mandatory_signals exist, threshold MUST be > 0
```

**Quick Fix**:
```bash
# Batch fix all contracts with threshold 0
for f in src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q{005..020}.v3.json; do
    python -c "
import json
c = json.load(open('$f'))
if c.get('signal_requirements', {}).get('minimum_signal_threshold', 1) == 0:
    c['signal_requirements']['minimum_signal_threshold'] = 0.5
    json.dump(c, open('$f', 'w'), indent=2, ensure_ascii=False)
    print('Fixed: $f')
"
done
```

## HIGH Issues

### 4. Weak Methodological Depth (category: weak_methodological_depth)

**Problem**: Method descriptions are generic boilerplate

**Impact**: Poor debugging, unclear analysis steps, reduced interpretability

**Examples of Generic Descriptions** (to avoid):
- "Execute analysis"
- "Process results"
- "Return structured output"
- "Run calculation"

**Good Descriptions** (specific):
- "Extract causal links using spaCy dependency parsing with custom verb patterns"
- "Calculate Bayesian posterior using Beta(α=2, β=5) prior based on historical data"
- "Detect contradictions by comparing numerical claims within 2 standard deviations"

**Fix**:
```python
# Update methodological_depth section
contract['output_contract']['human_readable_output']['methodological_depth'] = {
    "methods": [
        {
            "method_id": "temporallogicverifier.check_deadline_constraints",
            "paradigm": "Temporal Logic Verification",
            "technical_approach": {
                "steps": [
                    {
                        "order": 1,
                        "description": "Parse deadline expressions using regex pattern: (\\d{1,2})\\s+(días|meses|años)",
                        "complexity": "O(n) where n = document length"
                    },
                    {
                        "order": 2,
                        "description": "Validate temporal consistency against PDET guidelines (max 180 days)",
                        "complexity": "O(1)"
                    },
                    {
                        "order": 3,
                        "description": "Calculate confidence score using weighted average of pattern matches",
                        "complexity": "O(m) where m = number of matches"
                    }
                ]
            }
        }
    ]
}
```

### 5. Insufficient Patterns (category: insufficient_patterns)

**Problem**: Too few regex patterns for effective document matching

**Impact**: Low evidence extraction rate, missed relevant content

**Minimum Requirements**:
- At least 5 patterns per contract
- Coverage of all expected_elements types
- Confidence weights between 0.7-0.95

**Fix**:
```python
# Expand pattern set
contract['question_context']['patterns'] = [
    {
        "id": "PAT-Q0XX-000",
        "pattern": r"primary pattern|main regex",
        "category": "GENERAL",
        "confidence_weight": 0.85,
        "match_type": "REGEX",
        "flags": "i"
    },
    {
        "id": "PAT-Q0XX-001",
        "pattern": r"variant pattern|alternative form",
        "category": "VARIANT",
        "confidence_weight": 0.75,
        "match_type": "REGEX",
        "flags": "i"
    },
    # Add at least 5 patterns total
]

# Ensure unique IDs
assert len({p['id'] for p in patterns}) == len(patterns)

# Ensure all expected elements have pattern coverage
expected_types = {e['type'] for e in contract['question_context']['expected_elements']}
pattern_coverage = {e for e in expected_types if any(e.lower() in p['pattern'].lower() for p in patterns)}
assert pattern_coverage == expected_types, f"Missing patterns for: {expected_types - pattern_coverage}"
```

## MEDIUM Issues

### 6. Documentation Gaps (category: documentation_gaps)

**Problem**: Human-readable template lacks proper references or placeholders

**Impact**: Poor user experience, unclear reporting

**Fix**:
```python
contract['output_contract']['human_readable_output']['template'] = {
    "title": "Q{question_number}: {question_text}",  # Include question reference
    "summary": "{score_interpretation} based on {evidence_count} evidence elements",
    "evidence_detail": "{evidence_list}",
    "confidence": "Confidence: {confidence_score}",
    "required_placeholders": [
        "{score}",
        "{evidence_count}",
        "{confidence_score}",
        "{question_number}",
        "{question_text}"
    ]
}
```

## Batch Remediation Scripts

### Fix All Critical Issues
```bash
#!/bin/bash
# fix_critical_issues.sh

CONTRACTS_DIR="src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized"

for contract in $CONTRACTS_DIR/Q{005..020}.v3.json; do
    echo "Processing $contract..."
    
    python -c "
import json
from pathlib import Path

contract_path = Path('$contract')
with open(contract_path) as f:
    c = json.load(f)

# Fix 1: Signal threshold
if c.get('signal_requirements', {}).get('minimum_signal_threshold', 1) == 0:
    c['signal_requirements']['minimum_signal_threshold'] = 0.5
    print('  ✓ Fixed signal threshold')

# Fix 2: Assembly orphans
provides = {m['provides'] for m in c['method_binding']['methods']}
for rule in c.get('evidence_assembly', {}).get('assembly_rules', []):
    sources = rule.get('sources', [])
    valid = [s for s in sources if s in provides]
    if len(valid) != len(sources):
        rule['sources'] = valid
        print(f'  ✓ Fixed assembly orphans: removed {len(sources) - len(valid)} invalid sources')

# Save
with open(contract_path, 'w') as f:
    json.dump(c, f, indent=2, ensure_ascii=False)
"
done

echo "✅ All critical issues fixed. Re-run audit to verify."
```

## Validation After Fixes

```bash
# Re-run audit
./audit_contracts_Q005_Q020.py

# Check improvement
python -c "
import json
audit = json.load(open('contract_audit_Q005_Q020.json'))
stats = audit['summary_statistics']
print(f'Production Ready: {stats[\"production_ready\"]}/16')
print(f'Average Score: {stats[\"average_total_score\"]}/100')
print(f'Reformulation Needed: {stats[\"requires_reformulation\"]}')
"
```

## Decision Tree

```
START
  |
  ├─ Score < 35/55 (Tier 1) → REFORMULAR_COMPLETO
  |  └─ Regenerate from canonical questionnaire
  |
  ├─ Score 35-44/55 (Tier 1) → Check blockers
  |  ├─ Schema mismatch → REFORMULAR_SCHEMA
  |  ├─ Assembly orphans → REFORMULAR_ASSEMBLY  
  |  └─ Single blocker → PARCHEAR_CRITICO
  |
  ├─ Score 45-49/55 (Tier 1) + Total 60-79 → PARCHEAR_MAJOR
  |  └─ Fix assembly, patterns, validation
  |
  ├─ Score 45-49/55 (Tier 1) + Total ≥70 → PARCHEAR_MINOR
  |  └─ Minor adjustments only
  |
  └─ Score ≥50/55 (Tier 1) + Total ≥80 → PRODUCTION
     └─ Deploy after optional minor patches
```

## Contact and Support

For questions about transformation requirements:
1. Check the audit report: `contract_audit_Q005_Q020.json`
2. Review manifest: `transformation_requirements_manifest.json`
3. Reference CQVR spec: `src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/# Rúbrica CQVR v2.py`

## Maintenance Schedule

- **Daily**: Monitor CRITICAL issues
- **Weekly**: Address HIGH issues
- **Monthly**: Improve MEDIUM issues
- **Quarterly**: Review CQVR thresholds and adjust standards
