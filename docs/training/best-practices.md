# CQVR Best Practices Guide

## Overview

This guide presents proven best practices for working with the CQVR system, covering contract authoring, validation workflows, remediation strategies, and team collaboration.

## Contract Authoring Best Practices

### 1. Start with Templates

**Why**: Templates ensure consistent structure and reduce errors.

**How**:
```python
def create_contract_from_template(question_id: str, template_path: Path):
    """Create new contract from validated template"""
    
    # Load template
    with open(template_path) as f:
        contract = json.load(f)
    
    # Update identity fields
    contract["identity"]["question_id"] = question_id
    contract["identity"]["created_at"] = datetime.now().isoformat()
    
    # Generate unique hash
    contract_str = json.dumps(contract, sort_keys=True)
    contract["identity"]["contract_hash"] = hashlib.sha256(contract_str.encode()).hexdigest()
    
    return contract
```

**Template Sources**:
- High-scoring contracts (≥85/100)
- Production-validated contracts
- Question-type specific templates (e.g., causal analysis, pattern matching)

---

### 2. Build from Questionnaire Monolith

**Why**: Ensures identity fields are accurate and consistent with source.

**Process**:
1. Extract question data from questionnaire monolith
2. Generate contract structure from extracted data
3. Never manually type identity fields
4. Calculate source_hash for traceability

```python
def build_from_monolith(question_id: str):
    """Build contract from questionnaire monolith"""
    
    # Load monolith
    with open("canonic_questionnaire_central/questionnaire_monolith.json") as f:
        monolith = json.load(f)
    
    # Calculate source hash
    monolith_str = json.dumps(monolith, sort_keys=True)
    source_hash = hashlib.sha256(monolith_str.encode()).hexdigest()
    
    # Find question
    question = next(
        (q for q in monolith["blocks"]["micro_questions"] if q["question_id"] == question_id),
        None
    )
    
    if not question:
        raise ValueError(f"Question {question_id} not found in monolith")
    
    # Build contract with exact identity from monolith
    contract = {
        "identity": {
            "question_id": question["question_id"],
            "base_slot": question["base_slot"],
            "question_global": question["question_global"],
            "policy_area_id": question["policy_area_id"],
            "dimension_id": question["dimension_id"],
            "cluster_id": question.get("cluster_id"),
            # ... copy other identity fields
        },
        "traceability": {
            "source_hash": source_hash,
            "extracted_from": "questionnaire_monolith.json",
            "extraction_date": datetime.now().isoformat()
        }
    }
    
    return contract
```

---

### 3. Validate Early and Often

**Why**: Catch issues during development, not at deployment.

**Workflow**:
1. Validate after creating contract skeleton
2. Validate after adding each major component
3. Validate before committing to repository
4. Validate in CI/CD pipeline

```bash
# Development validation cycle
while editing contract.json; do
    python validate_contract.py contract.json
    # Fix issues
    # Repeat
done
```

**Target Milestones**:
- Skeleton: Tier 1 ≥ 35/55
- Components added: Tier 1 ≥ 45/55
- Ready to commit: Total ≥ 80/100

---

### 4. Use Specific (Not Boilerplate) Descriptions

**Why**: Specificity improves B2 score and actual usefulness.

**Bad (Boilerplate)**:
```json
{
  "steps": [
    {"description": "Execute method"},
    {"description": "Process results"},
    {"description": "Return output"}
  ],
  "complexity": "O(n)"
}
```

**Good (Specific)**:
```json
{
  "steps": [
    {"description": "Parse policy text using spaCy dependency parser to extract causal relationships"},
    {"description": "Construct directed acyclic graph (DAG) from extracted dependencies"},
    {"description": "Apply Tarjan's algorithm to detect cycles, calculate acyclicity p-value via permutation test"}
  ],
  "complexity": "O(V + E) for parsing, O(V + E) for Tarjan's, O(n! × (V + E)) for permutation test (capped at 1000 iterations)"
}
```

**Quality Checklist**:
- [ ] Names specific algorithm/library
- [ ] Describes actual data structures
- [ ] Provides realistic complexity analysis
- [ ] Documents assumptions
- [ ] References theoretical framework

---

## Validation Best Practices

### 5. Focus on Tier 1 First

**Why**: Tier 1 failures block production deployment.

**Priority Order**:
1. **Tier 1** (Critical): Fix all blockers before addressing Tier 2/3
2. **Tier 2** (Functional): Fix to reach ≥70/100 total
3. **Tier 3** (Quality): Improve to reach ≥80/100 total

**Triage by Tier 1 Score**:
- **< 35/55**: Reformulate (don't patch)
- **35-44/55**: Patch systematically
- **≥ 45/55**: Minor improvements needed

---

### 6. Fix Root Causes, Not Symptoms

**Why**: Symptom fixes don't prevent recurrence.

**Example: Identity Mismatches**

**Symptom Fix** (Don't do this):
```python
# Manually update each mismatched field
schema["properties"]["question_id"]["const"] = "Q001"
schema["properties"]["policy_area_id"]["const"] = "PA01"
# ... repeat for each field
```

**Root Cause Fix** (Do this):
```python
# Rebuild contract from questionnaire monolith
# This ensures all identity fields are correct from source
contract = build_from_monolith(question_id)
```

**Common Root Causes**:
- Copy-paste from other contracts → Use templates
- Manual typing → Generate from monolith
- Stale data → Update from monolith
- Missing validation → Add to workflow

---

### 7. Automate Repetitive Fixes

**Why**: Consistency and efficiency.

**When to Automate**:
- Same issue appears in 3+ contracts
- Fix is purely structural (no domain knowledge needed)
- Fix can be verified programmatically

**Example: Batch Signal Threshold Fix**
```python
def fix_all_signal_thresholds(contracts_dir: Path):
    """Fix zero thresholds in all contracts"""
    
    fixed_count = 0
    
    for contract_path in contracts_dir.glob("*.json"):
        with open(contract_path) as f:
            contract = json.load(f)
        
        signal_reqs = contract.get("signal_requirements", {})
        if signal_reqs.get("mandatory_signals") and signal_reqs.get("minimum_signal_threshold", 0) <= 0:
            signal_reqs["minimum_signal_threshold"] = 0.5
            
            with open(contract_path, 'w') as f:
                json.dump(contract, f, indent=2)
            
            fixed_count += 1
            print(f"✅ Fixed: {contract_path.name}")
    
    print(f"\n📊 Fixed {fixed_count} contracts")
```

---

### 8. Maintain Validation History

**Why**: Track quality trends, identify regressions.

**Implementation**:
```python
def track_validation_history(contract_path: Path):
    """Append validation results to history"""
    
    history_path = contract_path.parent / "validation_history.json"
    
    # Load contract
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Validate
    validator = CQVRValidator()
    decision = validator.validate_contract(contract)
    
    # Load history
    if history_path.exists():
        with open(history_path) as f:
            history = json.load(f)
    else:
        history = []
    
    # Append result
    history.append({
        "timestamp": datetime.now().isoformat(),
        "contract": contract_path.name,
        "question_id": contract.get("identity", {}).get("question_id"),
        "score": decision.score.total_score,
        "tier1": decision.score.tier1_score,
        "tier2": decision.score.tier2_score,
        "tier3": decision.score.tier3_score,
        "decision": decision.decision.value,
        "blockers": len(decision.blockers),
        "git_commit": get_git_commit()  # Optional
    })
    
    # Save history
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
```

**Analyze Trends**:
```python
def analyze_quality_trend(history: list):
    """Analyze quality trend over time"""
    
    scores = [h["score"] for h in history]
    
    print(f"First score:  {scores[0]:.1f}")
    print(f"Latest score: {scores[-1]:.1f}")
    print(f"Improvement:  +{scores[-1] - scores[0]:.1f}")
    print(f"Average:      {sum(scores) / len(scores):.1f}")
    
    # Detect regressions
    for i in range(1, len(scores)):
        if scores[i] < scores[i-1] - 5:  # 5+ point drop
            print(f"⚠️  REGRESSION at {history[i]['timestamp']}: {scores[i-1]:.1f} → {scores[i]:.1f}")
```

---

## Remediation Best Practices

### 9. Apply Fixes in Stages

**Why**: Easier to verify, easier to debug if something goes wrong.

**Stage 1: Automated Structural Fixes**
```python
remediation = ContractRemediation()
contract = remediation.apply_structural_corrections(contract)
validator.validate_contract(contract)  # Check improvement
```

**Stage 2: Signal Configuration**
```python
contract = fix_signal_threshold(contract)
validator.validate_contract(contract)  # Check improvement
```

**Stage 3: Metadata and Documentation**
```python
contract = fix_metadata(contract)
contract = improve_method_specificity(contract)
validator.validate_contract(contract)  # Check improvement
```

**Stage 4: Final Validation**
```python
final_decision = validator.validate_contract(contract)
assert final_decision.is_production_ready()
```

---

### 10. Verify After Each Fix

**Why**: Ensure fix worked, didn't break anything else.

**Verification Pattern**:
```python
def verify_fix(contract, component_name, verify_fn, expected_min_score):
    """Verify component fix"""
    
    score = verify_fn(contract)
    
    if score >= expected_min_score:
        print(f"✅ {component_name}: {score} (≥ {expected_min_score})")
        return True
    else:
        print(f"❌ {component_name}: {score} (< {expected_min_score})")
        return False

# Usage
validator = CQVRValidator()

# Fix A1
contract = fix_identity_schema_coherence(contract)
assert verify_fix(contract, "A1", validator.verify_identity_schema_coherence, 18.0)

# Fix A2
contract = remove_orphan_sources(contract)
assert verify_fix(contract, "A2", validator.verify_method_assembly_alignment, 18.0)

# ... continue for each fix
```

---

### 11. Don't Over-Remediate

**Why**: Diminishing returns, time better spent elsewhere.

**Production Threshold: 80/100**
- Getting from 75 → 80: High priority
- Getting from 80 → 85: Medium priority
- Getting from 85 → 95: Low priority
- Getting from 95 → 100: Very low priority

**When to Stop**:
- Score ≥ 80/100
- Zero blockers
- All Tier 1 critical components ≥ threshold

**Time Allocation**:
- 60% of time: Get below-threshold contracts to 80/100
- 30% of time: Build new high-quality contracts
- 10% of time: Polish 80+ contracts toward perfection

---

## Team Collaboration Best Practices

### 12. Establish Quality Gates

**Why**: Prevent low-quality contracts from reaching production.

**Pre-Commit Gate** (Local):
```bash
# .git/hooks/pre-commit
#!/bin/bash
for file in $(git diff --cached --name-only | grep contracts/.*\.json$); do
    python validate_contract.py "$file"
    if [ $? -eq 2 ]; then  # Exit code 2 = REFORMULAR
        echo "❌ Contract validation failed: $file"
        exit 1
    fi
done
```

**Pull Request Gate** (CI):
```yaml
- name: Validate Contracts
  run: |
    python validate_all.py contracts/ --min-score 70 --max-blockers 2
```

**Deployment Gate** (Production):
```yaml
- name: Production Validation
  run: |
    python validate_all.py contracts/production/ --min-score 80 --max-blockers 0
```

---

### 13. Share Validation Reports

**Why**: Team visibility, learning from patterns.

**Report Format**:
```markdown
# Contract Quality Report - 2025-12-17

## Summary
- Total contracts: 30
- ✅ Production ready: 18 (60%)
- ⚠️  Need patches: 10 (33%)
- ❌ Need reformulation: 2 (7%)

## Average Scores
- Overall: 82.3/100
- Tier 1: 47.1/55
- Tier 2: 25.8/30
- Tier 3: 9.4/15

## Common Issues
1. Zero signal threshold: 12 contracts (fixed)
2. Orphan sources: 8 contracts (fixed)
3. Boilerplate descriptions: 15 contracts (improving)

## Action Items
- [ ] Reformulate Q014, Q023
- [ ] Apply signal threshold fixes (batch script)
- [ ] Review method specificity guidelines
```

---

### 14. Document Custom Patterns

**Why**: Institutional knowledge, consistency.

**Pattern Documentation**:
```markdown
# Custom Pattern: Causal Chain Detection

**Question Types**: Causal analysis (DIM02)

**Pattern Example**:
```json
{
  "id": "PAT-CAUSAL-001",
  "target_element_type": "causal_chain",
  "pattern": "(?i)(causa|produce|genera|resulta en)\\s+(?:que|el|la|los|las)",
  "confidence_weight": 0.85,
  "category": "CAUSAL_RELATIONSHIP",
  "rationale": "Detects Spanish causal verbs followed by relative pronouns or articles"
}
```

**Usage**: Apply to all causal analysis contracts
**Success Rate**: 87% (validated on 20 contracts)
**Maintained By**: Team Lead
```

---

### 15. Conduct Quality Reviews

**Why**: Catch issues automated validation misses.

**Review Checklist**:
- [ ] Identity fields match source document
- [ ] Method names are accurate (not copy-paste errors)
- [ ] Patterns make semantic sense for question type
- [ ] Technical approaches are question-specific
- [ ] Template placeholders will work with runtime data

**Review Schedule**:
- New contracts: 100% review before first production use
- Existing contracts: Sample 10% quarterly
- High-stakes contracts: 100% review on each change

---

## Performance Best Practices

### 16. Batch Operations

**Why**: Faster than one-at-a-time for large contract sets.

```python
from concurrent.futures import ProcessPoolExecutor

def validate_batch_parallel(contract_files: list, max_workers: int = 4):
    """Validate contracts in parallel"""
    
    def validate_one(contract_path):
        validator = CQVRValidator()
        with open(contract_path) as f:
            contract = json.load(f)
        return validator.validate_contract(contract)
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(validate_one, contract_files))
    
    return results
```

---

### 17. Cache Validation Results

**Why**: Avoid re-validating unchanged contracts.

```python
def validate_with_cache(contract_path: Path, cache_dir: Path):
    """Validate only if contract changed"""
    
    # Calculate contract hash
    with open(contract_path, 'rb') as f:
        contract_hash = hashlib.sha256(f.read()).hexdigest()
    
    cache_file = cache_dir / f"{contract_path.stem}_{contract_hash}.json"
    
    # Check cache
    if cache_file.exists():
        with open(cache_file) as f:
            cached_result = json.load(f)
        print(f"✅ Using cached result for {contract_path.name}")
        return cached_result
    
    # Validate
    with open(contract_path) as f:
        contract = json.load(f)
    
    validator = CQVRValidator()
    decision = validator.validate_contract(contract)
    
    # Cache result
    result = {
        "score": decision.score.total_score,
        "decision": decision.decision.value,
        "blockers": decision.blockers,
        "warnings": decision.warnings
    }
    
    with open(cache_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    return result
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Don't Copy-Paste Contracts

**Why**: Identity mismatches, wrong question_id in schema.

**Instead**: Use templates or generate from monolith.

---

### ❌ Don't Ignore Warnings

**Why**: Warnings indicate quality issues that hurt score.

**Instead**: Fix warnings progressively to reach 80/100.

---

### ❌ Don't Skip Validation

**Why**: Catches issues early when they're easier to fix.

**Instead**: Validate at every stage of development.

---

### ❌ Don't Manually Type Identity Fields

**Why**: Typos, mismatches, broken traceability.

**Instead**: Generate from questionnaire monolith.

---

### ❌ Don't Fix Scores, Fix Issues

**Why**: Gaming the scoring system produces fragile contracts.

**Instead**: Understand what score means, fix underlying issues.

---

### ❌ Don't Remediate REFORMULAR Contracts

**Why**: Patching fundamental issues is unreliable.

**Instead**: Rebuild from questionnaire monolith.

---

## Success Metrics

Track these metrics to measure CQVR adoption success:

1. **Production Rate**: % contracts with score ≥ 80/100
   - Target: ≥ 70%

2. **Average Score**: Mean score across all contracts
   - Target: ≥ 78/100

3. **Blocker Rate**: % contracts with blockers
   - Target: ≤ 20%

4. **Time to Production**: Days from contract creation to production-ready
   - Target: ≤ 3 days

5. **Remediation Success**: % PARCHEAR contracts that reach PRODUCCION
   - Target: ≥ 85%

6. **Quality Trend**: Score change over time
   - Target: Improving or stable

---

## Summary

**Key Takeaways**:
1. Build from templates and questionnaire monolith
2. Validate early and often
3. Focus on Tier 1 first
4. Fix root causes, not symptoms
5. Automate repetitive tasks
6. Share knowledge and reports
7. Establish quality gates
8. Track metrics

**Quality Formula**:
```
Quality = (Automation × Consistency) + (Validation Frequency × Team Knowledge)
```

---

## See Also

- [Evaluation Guide](evaluation-guide.md) - Running validations
- [Remediation Guide](remediation-guide.md) - Fixing issues
- [Scoring System](../cqvr/scoring-system.md) - Understanding scores
- [Decision Matrix](../cqvr/decision-matrix.md) - Triage logic
