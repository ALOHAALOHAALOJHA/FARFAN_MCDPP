# CQVR API Reference

## Overview

This document provides comprehensive API documentation for the CQVR (Contract Quality Verification and Remediation) system. The API consists of validator classes, data models, and utility functions for contract quality assessment.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Data Models](#data-models)
3. [Validation Methods](#validation-methods)
4. [Usage Examples](#usage-examples)
5. [Integration Patterns](#integration-patterns)

---

## Core Classes

### CQVRValidator

Main validation class that implements the CQVR v2.0 rubric.

**Location**: `src/farfan_pipeline/phases/Phase_two/contract_validator_cqvr.py`

```python
class CQVRValidator:
    """Contract Quality Validation with Rubric-based scoring (CQVR v2.0)"""
    
    # Threshold constants
    TIER1_THRESHOLD = 35.0
    TIER1_PRODUCTION_THRESHOLD = 45.0
    TOTAL_PRODUCTION_THRESHOLD = 80.0
    
    def __init__(self) -> None:
        """Initialize validator with empty blocker/warning lists"""
        
    def validate_contract(self, contract: dict[str, Any]) -> ContractTriageDecision:
        """
        Run full CQVR validation on contract.
        
        Args:
            contract: Executor contract JSON as dict
            
        Returns:
            ContractTriageDecision with score, decision, and recommendations
            
        Example:
            >>> validator = CQVRValidator()
            >>> decision = validator.validate_contract(contract)
            >>> print(f"Score: {decision.score.total_score}/100")
            >>> print(f"Decision: {decision.decision.value}")
        """
```

**Key Methods**:

#### validate_contract
```python
def validate_contract(self, contract: dict[str, Any]) -> ContractTriageDecision
```
Runs complete CQVR validation and returns triage decision.

**Process**:
1. Evaluate Tier 1 components (A1-A4)
2. Evaluate Tier 2 components (B1-B3)
3. Evaluate Tier 3 components (C1-C3)
4. Calculate total score
5. Make triage decision
6. Generate rationale

**Returns**: `ContractTriageDecision` object

---

#### Tier 1 Validation Methods

##### verify_identity_schema_coherence
```python
def verify_identity_schema_coherence(self, contract: dict[str, Any]) -> float
```
**A1: Identity-Schema Coherence (20 pts)**

Validates that identity fields match output schema const values.

**Checked Fields**:
- `question_id`: 5 pts
- `policy_area_id`: 5 pts
- `dimension_id`: 5 pts
- `question_global`: 3 pts
- `base_slot`: 2 pts

**Blockers Added**:
- Identity-Schema mismatch for each field
- Missing fields in identity or schema

**Example**:
```python
score = validator.verify_identity_schema_coherence(contract)
# Returns: 20.0 if all match, proportional penalty for mismatches
```

---

##### verify_method_assembly_alignment
```python
def verify_method_assembly_alignment(self, contract: dict[str, Any]) -> float
```
**A2: Method-Assembly Alignment (20 pts)**

Validates that assembly sources reference valid method provides.

**Scoring**:
- No orphan sources: 10 pts
- Method usage ratio ≥90%: 5 pts
- Method count matches: 3 pts
- Consistency bonus: 2 pts

**Blockers Added**:
- No methods defined
- Orphan sources (sources not in provides)

**Example**:
```python
score = validator.verify_method_assembly_alignment(contract)
# Returns: 0-20 based on alignment quality
```

---

##### verify_signal_requirements
```python
def verify_signal_requirements(self, contract: dict[str, Any]) -> float
```
**A3: Signal Requirements (10 pts)**

Validates signal threshold configuration.

**Critical Check**: If mandatory_signals defined, threshold MUST be > 0.

**Scoring**:
- Valid threshold: 5 pts
- Well-formed signals: 3 pts
- Valid aggregation: 2 pts

**Blockers Added**:
- CRITICAL: Zero threshold with mandatory signals

**Example**:
```python
score = validator.verify_signal_requirements(contract)
# Returns: 0 if critical failure, 0-10 otherwise
```

---

##### verify_output_schema
```python
def verify_output_schema(self, contract: dict[str, Any]) -> float
```
**A4: Output Schema (5 pts)**

Validates required fields are defined in schema properties.

**Scoring**:
- All required in properties: 3 pts
- Valid source hash: 2 pts

**Blockers Added**:
- Required fields not in properties

**Example**:
```python
score = validator.verify_output_schema(contract)
# Returns: 0-5 based on schema completeness
```

---

#### Tier 2 Validation Methods

##### verify_pattern_coverage
```python
def verify_pattern_coverage(self, contract: dict[str, Any]) -> float
```
**B1: Pattern Coverage (10 pts)**

Validates patterns cover expected elements.

**Scoring**:
- Pattern coverage ratio: 5 pts (proportional)
- Valid confidence weights: 3 pts
- Unique pattern IDs: 2 pts

**Example**:
```python
score = validator.verify_pattern_coverage(contract)
# Returns: 0-10 based on pattern quality
```

---

##### verify_method_specificity
```python
def verify_method_specificity(self, contract: dict[str, Any]) -> float
```
**B2: Method Specificity (10 pts)**

Validates methods are specific, not boilerplate.

**Generic Patterns Detected**:
- "Execute"
- "Process results"
- "Return structured output"
- "O(n) where n=input size"

**Scoring**:
- Specificity ratio: 6 pts (proportional)
- Complexity analysis: 2 pts
- Assumptions documented: 2 pts

**Example**:
```python
score = validator.verify_method_specificity(contract)
# Returns: 0-10 based on method quality
```

---

##### verify_validation_rules
```python
def verify_validation_rules(self, contract: dict[str, Any]) -> float
```
**B3: Validation Rules (10 pts)**

Validates that validation rules cover required elements.

**Scoring**:
- Required elements covered: 5 pts
- Rule diversity (must + should): 3 pts
- Failure contract defined: 2 pts

**Blockers Added**:
- No validation rules defined

**Example**:
```python
score = validator.verify_validation_rules(contract)
# Returns: 0-10 based on validation completeness
```

---

#### Tier 3 Validation Methods

##### verify_documentation_quality
```python
def verify_documentation_quality(self, contract: dict[str, Any]) -> float
```
**C1: Documentation Quality (5 pts)**

Validates epistemological foundations are specific.

**Boilerplate Patterns Detected**:
- "analytical paradigm"
- "This method contributes"
- "method implements structured analysis"

**Scoring**:
- Specific paradigms: 2 pts
- Reasoning in justifications: 2 pts
- Theoretical references: 1 pt

---

##### verify_human_template
```python
def verify_human_template(self, contract: dict[str, Any]) -> float
```
**C2: Human Template (5 pts)**

Validates templates reference identity and have placeholders.

**Scoring**:
- Title references identity: 3 pts
- Dynamic placeholders: 2 pts

---

##### verify_metadata_completeness
```python
def verify_metadata_completeness(self, contract: dict[str, Any]) -> float
```
**C3: Metadata Completeness (5 pts)**

Validates contract metadata is complete.

**Scoring**:
- Valid contract hash (64 chars): 2 pts
- Valid created_at timestamp: 1 pt
- Schema validation version: 1 pt
- Contract version: 1 pt

---

## Data Models

### CQVRScore

Represents CQVR scoring results.

```python
@dataclass
class CQVRScore:
    tier1_score: float
    tier2_score: float
    tier3_score: float
    total_score: float
    tier1_max: float = 55.0
    tier2_max: float = 30.0
    tier3_max: float = 15.0
    total_max: float = 100.0
    component_scores: dict[str, float] = field(default_factory=dict)
    component_details: dict[str, dict[str, Any]] = field(default_factory=dict)
    
    @property
    def tier1_percentage(self) -> float:
        """Tier 1 score as percentage"""
        return (self.tier1_score / self.tier1_max) * 100
    
    @property
    def tier2_percentage(self) -> float:
        """Tier 2 score as percentage"""
        return (self.tier2_score / self.tier2_max) * 100
    
    @property
    def tier3_percentage(self) -> float:
        """Tier 3 score as percentage"""
        return (self.tier3_score / self.tier3_max) * 100
    
    @property
    def total_percentage(self) -> float:
        """Total score as percentage"""
        return (self.total_score / self.total_max) * 100
```

**Example**:
```python
score = CQVRScore(
    tier1_score=48.0,
    tier2_score=27.0,
    tier3_score=12.0,
    total_score=87.0
)
print(f"Tier 1: {score.tier1_percentage:.1f}%")  # 87.3%
print(f"Total: {score.total_percentage:.1f}%")    # 87.0%
```

---

### TriageDecision

Enum representing triage outcomes.

```python
class TriageDecision(Enum):
    PRODUCCION = "PRODUCCION"    # Production ready
    REFORMULAR = "REFORMULAR"    # Requires reformulation
    PARCHEAR = "PARCHEAR"        # Can be patched
```

**Usage**:
```python
if decision.decision == TriageDecision.PRODUCCION:
    deploy_to_production(contract)
elif decision.decision == TriageDecision.PARCHEAR:
    apply_patches(contract)
else:
    reformulate_contract(contract)
```

---

### ContractTriageDecision

Complete triage decision with score and recommendations.

```python
@dataclass
class ContractTriageDecision:
    decision: TriageDecision
    score: CQVRScore
    blockers: list[str]
    warnings: list[str]
    recommendations: list[dict[str, Any]]
    rationale: str
    
    def is_production_ready(self) -> bool:
        """True if decision is PRODUCCION"""
        return self.decision == TriageDecision.PRODUCCION
    
    def requires_reformulation(self) -> bool:
        """True if decision is REFORMULAR"""
        return self.decision == TriageDecision.REFORMULAR
    
    def can_be_patched(self) -> bool:
        """True if decision is PARCHEAR"""
        return self.decision == TriageDecision.PARCHEAR
```

**Example**:
```python
decision = validator.validate_contract(contract)

print(f"Decision: {decision.decision.value}")
print(f"Score: {decision.score.total_score}/100")
print(f"Blockers: {len(decision.blockers)}")
print(f"Rationale: {decision.rationale}")

if decision.can_be_patched():
    for rec in decision.recommendations:
        print(f"- {rec['issue']}: {rec['fix']}")
```

---

## Usage Examples

### Example 1: Basic Validation

```python
from contract_validator_cqvr import CQVRValidator
import json

# Load contract
with open('contracts/Q001.v3.json') as f:
    contract = json.load(f)

# Validate
validator = CQVRValidator()
decision = validator.validate_contract(contract)

# Check results
if decision.is_production_ready():
    print(f"✅ Ready for production: {decision.score.total_score}/100")
else:
    print(f"❌ Not ready: {decision.decision.value}")
    print(f"Blockers: {decision.blockers}")
```

---

### Example 2: Batch Validation

```python
from pathlib import Path
from contract_validator_cqvr import CQVRValidator

def validate_all_contracts(contract_dir: Path) -> dict:
    """Validate all contracts in directory"""
    validator = CQVRValidator()
    results = {}
    
    for contract_path in contract_dir.glob("*.json"):
        with open(contract_path) as f:
            contract = json.load(f)
        
        decision = validator.validate_contract(contract)
        results[contract_path.name] = {
            "score": decision.score.total_score,
            "decision": decision.decision.value,
            "blockers": len(decision.blockers)
        }
    
    return results

# Run validation
results = validate_all_contracts(Path("contracts/specialized/"))

# Report
for name, result in results.items():
    status = "✅" if result["decision"] == "PRODUCCION" else "❌"
    print(f"{status} {name}: {result['score']}/100 ({result['decision']})")
```

---

### Example 3: CI/CD Integration

```python
#!/usr/bin/env python3
"""CI/CD contract validation script"""
import sys
import json
from pathlib import Path
from contract_validator_cqvr import CQVRValidator

def validate_for_ci(contract_path: Path, min_score: int = 80) -> bool:
    """
    Validate contract for CI/CD pipeline.
    
    Returns:
        True if contract meets threshold, False otherwise
    """
    with open(contract_path) as f:
        contract = json.load(f)
    
    validator = CQVRValidator()
    decision = validator.validate_contract(contract)
    
    print(f"Contract: {contract_path.name}")
    print(f"Score: {decision.score.total_score}/100")
    print(f"Decision: {decision.decision.value}")
    
    if decision.score.total_score < min_score:
        print(f"\n❌ FAILED: Score {decision.score.total_score} < {min_score}")
        print(f"Blockers: {decision.blockers}")
        return False
    
    if len(decision.blockers) > 0:
        print(f"\n❌ FAILED: {len(decision.blockers)} blockers")
        for blocker in decision.blockers:
            print(f"  - {blocker}")
        return False
    
    print(f"\n✅ PASSED: Contract meets quality threshold")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_ci.py <contract.json>")
        sys.exit(1)
    
    passed = validate_for_ci(Path(sys.argv[1]))
    sys.exit(0 if passed else 1)
```

**CI Configuration** (GitHub Actions):
```yaml
- name: Validate Contracts
  run: |
    for contract in contracts/*.json; do
      python validate_ci.py "$contract" || exit 1
    done
```

---

### Example 4: Remediation Workflow

```python
from contract_validator_cqvr import CQVRValidator
from contract_remediation import ContractRemediation
import json

def remediate_contract(contract_path: Path) -> bool:
    """
    Attempt to remediate contract to production quality.
    
    Returns:
        True if remediation successful, False otherwise
    """
    # Load contract
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Initial validation
    validator = CQVRValidator()
    decision = validator.validate_contract(contract)
    
    print(f"Initial score: {decision.score.total_score}/100")
    
    if decision.is_production_ready():
        print("Already production ready")
        return True
    
    if decision.requires_reformulation():
        print("Requires reformulation, cannot patch")
        return False
    
    # Apply remediation
    print("Applying patches...")
    remediation = ContractRemediation()
    patched = remediation.apply_structural_corrections(contract)
    
    # Re-validate
    final_decision = validator.validate_contract(patched)
    print(f"Final score: {final_decision.score.total_score}/100")
    
    if final_decision.is_production_ready():
        # Save patched contract
        with open(contract_path, 'w') as f:
            json.dump(patched, f, indent=2)
        print("✅ Remediation successful")
        return True
    else:
        print("❌ Remediation insufficient")
        return False
```

---

### Example 5: Metrics Collection

```python
from contract_validator_cqvr import CQVRValidator
from pathlib import Path
import json

def collect_metrics(contracts_dir: Path) -> dict:
    """Collect CQVR metrics across all contracts"""
    validator = CQVRValidator()
    metrics = {
        "total_contracts": 0,
        "produccion": 0,
        "parchear": 0,
        "reformular": 0,
        "avg_score": 0.0,
        "avg_tier1": 0.0,
        "avg_tier2": 0.0,
        "avg_tier3": 0.0,
        "common_blockers": {}
    }
    
    total_score = 0.0
    total_tier1 = 0.0
    total_tier2 = 0.0
    total_tier3 = 0.0
    
    for contract_path in contracts_dir.glob("*.json"):
        with open(contract_path) as f:
            contract = json.load(f)
        
        decision = validator.validate_contract(contract)
        metrics["total_contracts"] += 1
        
        # Count decisions
        if decision.decision.value == "PRODUCCION":
            metrics["produccion"] += 1
        elif decision.decision.value == "PARCHEAR":
            metrics["parchear"] += 1
        else:
            metrics["reformular"] += 1
        
        # Accumulate scores
        total_score += decision.score.total_score
        total_tier1 += decision.score.tier1_score
        total_tier2 += decision.score.tier2_score
        total_tier3 += decision.score.tier3_score
        
        # Count blockers
        for blocker in decision.blockers:
            blocker_type = blocker.split(":")[0]
            metrics["common_blockers"][blocker_type] = \
                metrics["common_blockers"].get(blocker_type, 0) + 1
    
    # Calculate averages
    if metrics["total_contracts"] > 0:
        metrics["avg_score"] = total_score / metrics["total_contracts"]
        metrics["avg_tier1"] = total_tier1 / metrics["total_contracts"]
        metrics["avg_tier2"] = total_tier2 / metrics["total_contracts"]
        metrics["avg_tier3"] = total_tier3 / metrics["total_contracts"]
    
    return metrics

# Collect and report
metrics = collect_metrics(Path("contracts/specialized/"))
print(json.dumps(metrics, indent=2))
```

---

## Integration Patterns

### Pattern 1: Pre-Commit Hook

Validate contracts before committing to repository.

```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.json$'); do
    if [[ $file == contracts/* ]]; then
        python validate_ci.py "$file"
        if [ $? -ne 0 ]; then
            echo "Contract validation failed: $file"
            exit 1
        fi
    fi
done
```

---

### Pattern 2: Continuous Monitoring

Monitor contract quality over time.

```python
from contract_validator_cqvr import CQVRValidator
import json
from datetime import datetime

def monitor_contract_quality(contract_path: Path, history_path: Path):
    """Track contract quality over time"""
    with open(contract_path) as f:
        contract = json.load(f)
    
    validator = CQVRValidator()
    decision = validator.validate_contract(contract)
    
    # Load history
    if history_path.exists():
        with open(history_path) as f:
            history = json.load(f)
    else:
        history = []
    
    # Append current score
    history.append({
        "timestamp": datetime.now().isoformat(),
        "score": decision.score.total_score,
        "tier1": decision.score.tier1_score,
        "tier2": decision.score.tier2_score,
        "tier3": decision.score.tier3_score,
        "decision": decision.decision.value,
        "blockers": len(decision.blockers)
    })
    
    # Save history
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
```

---

### Pattern 3: Automated Remediation Pipeline

```python
def automated_remediation_pipeline(contracts_dir: Path):
    """Automatically remediate all patchable contracts"""
    validator = CQVRValidator()
    remediation = ContractRemediation()
    
    results = {
        "attempted": 0,
        "successful": 0,
        "failed": 0,
        "already_ready": 0
    }
    
    for contract_path in contracts_dir.glob("*.json"):
        with open(contract_path) as f:
            contract = json.load(f)
        
        decision = validator.validate_contract(contract)
        
        if decision.is_production_ready():
            results["already_ready"] += 1
            continue
        
        if not decision.can_be_patched():
            continue
        
        results["attempted"] += 1
        
        # Apply patches
        patched = remediation.apply_structural_corrections(contract)
        final_decision = validator.validate_contract(patched)
        
        if final_decision.is_production_ready():
            with open(contract_path, 'w') as f:
                json.dump(patched, f, indent=2)
            results["successful"] += 1
        else:
            results["failed"] += 1
    
    return results
```

---

## See Also

- [Scoring System](scoring-system.md) - Detailed rubric
- [Decision Matrix](decision-matrix.md) - Triage logic
- [User Guide](../guides/evaluation-guide.md) - Step-by-step usage
- [Troubleshooting](troubleshooting.md) - Common issues
