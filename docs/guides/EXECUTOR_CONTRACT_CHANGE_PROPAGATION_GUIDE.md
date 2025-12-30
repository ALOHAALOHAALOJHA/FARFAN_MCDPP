# Executor Contract v3 Structure Analysis & Change Propagation Guide

## Executive Summary

This document provides a comprehensive analysis of executor contract v3 structure and detailed procedures for propagating method changes across the 300 contract files (30 executors × 10 questions each).

## Contract Structure Analysis

### Core Components

#### 1. Identity Block
```json
{
  "identity": {
    "base_slot": "D1-Q1",           // Dimension-Question identifier
    "question_id": "Q001",           // Global question ID (Q001-Q300)
    "dimension_id": "DIM01",         // Dimension (DIM01-DIM06)
    "policy_area_id": "PA01",        // Policy area (PA01-PA10)
    "contract_version": "3.0.0",     // Contract version
    "contract_hash": "...",          // SHA-256 hash for integrity
    "created_at": "...",             // ISO timestamp
    "validated_against_schema": "executor_contract.v3.schema.json",
    "cluster_id": "CL02",            // Cluster assignment (CL01-CL04)
    "question_global": 1             // Sequential question number
  }
}
```

**Key Fields**:
- `base_slot`: Primary executor identifier (D{1-6}-Q{1-10})
- `question_id`: Maps to questionnaire_monolith.json
- `contract_hash`: Must be regenerated when contract changes

#### 2. Executor Binding
```json
{
  "executor_binding": {
    "executor_class": "D1_Q1_Executor",
    "executor_module": "farfan_core.core.orchestrator.executors"
  }
}
```

**Purpose**: Links contract to Python executor class implementation

#### 3. Method Binding (Most Critical for Changes)
```json
{
  "method_binding": {
    "orchestration_mode": "multi_method_pipeline",
    "method_count": 17,
    "methods": [
      {
        "class_name": "TextMiningEngine",
        "method_name": "diagnose_critical_links",
        "priority": 1,
        "provides": "text_mining.diagnose_critical_links",
        "role": "diagnose_critical_links_diagnosis",
        "description": "TextMiningEngine.diagnose_critical_links"
      },
      ...
    ]
  }
}
```

**Critical Fields**:
- `class_name`: Dispensary class (must exist in methods_dispensary/)
- `method_name`: Exact method name (case-sensitive)
- `priority`: Execution order (1 = first)
- `provides`: Unique capability identifier
- `role`: Semantic role in pipeline
- `description`: Human-readable description

#### 4. Question Context
```json
{
  "question_context": {
    "question_text": "¿El PDM presenta línea base...",
    "question_type": "quantitative_baseline",
    "expected_output_type": "structured_answer",
    "dimension_focus": "diagnosis",
    "complexity_level": "high"
  }
}
```

#### 5. Evidence Assembly & Validation Rules
```json
{
  "evidence_assembly": {
    "assembly_rules": [...],
    "signal_requirements": {
      "mandatory_signals": [...],
      "optional_signals": [...],
      "minimum_signal_threshold": 3
    }
  },
  "validation_rules": {
    "completeness_checks": [...],
    "quality_thresholds": {...}
  }
}
```

## Method Change Propagation Strategy

### Scenario 1: Single Method Replacement

**Problem**: `FinancialAuditor._calculate_sufficiency` is missing
**Affects**: 3 executors (D1-Q3, D3-Q2, D5-Q2)
**Replacement**: `PDETMunicipalPlanAnalyzer._assess_financial_sustainability`

#### Step-by-Step Procedure

1. **Identify Affected Contracts**
```bash
# Find all contracts using the missing method
grep -r "_calculate_sufficiency" src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/
```

2. **For Each Affected Contract**:
   
   **a. Update method_binding.methods array**:
   ```json
   // OLD
   {
     "class_name": "FinancialAuditor",
     "method_name": "_calculate_sufficiency",
     "priority": 8,
     "provides": "financial_audit.calculate_sufficiency",
     "role": "_calculate_sufficiency_calculation"
   }
   
   // NEW
   {
     "class_name": "PDETMunicipalPlanAnalyzer",
     "method_name": "_assess_financial_sustainability",
     "priority": 8,
     "provides": "financial_audit.calculate_sufficiency",  // Keep same "provides"
     "role": "_assess_financial_sustainability_assessment",
     "description": "PDETMunicipalPlanAnalyzer._assess_financial_sustainability"
   }
   ```

   **b. Update method_count**:
   ```json
   "method_count": 17  // Keep same if 1:1 replacement
   ```

   **c. Regenerate contract_hash**:
   ```python
   import hashlib
   import json
   
   with open(contract_file) as f:
       contract = json.load(f)
   
   # Remove old hash
   del contract['identity']['contract_hash']
   
   # Generate new hash
   contract_str = json.dumps(contract, sort_keys=True)
   new_hash = hashlib.sha256(contract_str.encode()).hexdigest()
   contract['identity']['contract_hash'] = new_hash
   
   # Save
   with open(contract_file, 'w') as f:
       json.dump(contract, f, indent=4)
   ```

   **d. Update timestamp**:
   ```json
   "created_at": "2025-12-11T13:35:00.000000+00:00"  // Current UTC time
   ```

3. **Validate Changes**:
```python
# Run executor factory validation
python3 src/orchestration/factory.py validate_executors
```

### Scenario 2: Method Affects Multiple Executors Per Dimension

**Problem**: `SemanticProcessor.chunk_text` missing
**Affects**: D1-Q1, D6-Q5 (2 executors, but potentially 20 contracts if all questions use it)

**Bulk Update Strategy**:

1. **Create Change Manifest**:
```json
{
  "change_type": "method_replacement",
  "source_method": {
    "class": "SemanticProcessor",
    "method": "chunk_text"
  },
  "target_method": {
    "class": "EmbeddingPolicyProducer",
    "method": "get_chunk_text"
  },
  "affected_contracts": [
    "Q001.v3.json",
    "Q002.v3.json",
    // ... 20 contracts total
  ]
}
```

2. **Automated Bulk Update Script**:
```python
#!/usr/bin/env python3
"""Bulk contract updater for method replacements"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

def update_contract_method(contract_path, old_class, old_method, new_class, new_method):
    """Update a single contract's method binding"""
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Find and update method in methods array
    updated = False
    for method_def in contract['method_binding']['methods']:
        if (method_def['class_name'] == old_class and 
            method_def['method_name'] == old_method):
            method_def['class_name'] = new_class
            method_def['method_name'] = new_method
            # Update description
            method_def['description'] = f"{new_class}.{new_method}"
            updated = True
    
    if not updated:
        print(f"  ⚠️  Method not found in {contract_path.name}")
        return False
    
    # Update timestamp
    contract['identity']['created_at'] = datetime.utcnow().isoformat() + '+00:00'
    
    # Regenerate hash
    temp_contract = contract.copy()
    del temp_contract['identity']['contract_hash']
    contract_str = json.dumps(temp_contract, sort_keys=True)
    new_hash = hashlib.sha256(contract_str.encode()).hexdigest()
    contract['identity']['contract_hash'] = new_hash
    
    # Save
    with open(contract_path, 'w') as f:
        json.dump(contract, f, indent=4)
    
    print(f"  ✅ Updated {contract_path.name}")
    return True

def bulk_update(contracts_dir, manifest):
    """Bulk update multiple contracts"""
    contracts_dir = Path(contracts_dir)
    
    old_class = manifest['source_method']['class']
    old_method = manifest['source_method']['method']
    new_class = manifest['target_method']['class']
    new_method = manifest['target_method']['method']
    
    updated_count = 0
    for contract_file in manifest['affected_contracts']:
        contract_path = contracts_dir / contract_file
        if update_contract_method(contract_path, old_class, old_method, new_class, new_method):
            updated_count += 1
    
    print(f"\n✅ Updated {updated_count}/{len(manifest['affected_contracts'])} contracts")

# Usage:
# bulk_update('src/.../specialized', change_manifest)
```

### Scenario 3: Adding New Method to Existing Executor

**Use Case**: Enhance D1-Q2 with additional financial analysis method

1. **Update Method Array**:
```json
{
  "methods": [
    // ... existing methods with priorities 1-17
    {
      "class_name": "PDETMunicipalPlanAnalyzer",
      "method_name": "analyze_financial_feasibility",
      "priority": 18,  // New priority
      "provides": "pdet_analysis.financial_feasibility",
      "role": "analyze_financial_feasibility_analysis",
      "description": "PDETMunicipalPlanAnalyzer.analyze_financial_feasibility"
    }
  ]
}
```

2. **Update method_count**:
```json
"method_count": 18  // Increment by 1
```

3. **Regenerate hash and update timestamp** (as above)

## Improved Method Suggestions with PDETMunicipalPlanAnalyzer

Based on analysis of `financiero_viabilidad_tablas.py`, here are superior replacements:

### High-Priority Replacements

#### 1. FinancialAuditor._calculate_sufficiency
**Current Suggestion**: `_validate_budget_coherence` (score: 3)
**BETTER Alternative**: `PDETMunicipalPlanAnalyzer._assess_financial_sustainability`

**Why Better**:
- Comprehensive Bayesian risk inference
- Integrates funding sources analysis
- Provides sustainability scoring (not just sufficiency check)
- Returns structured risk assessment with confidence intervals

**Implementation**:
```json
{
  "class_name": "PDETMunicipalPlanAnalyzer",
  "method_name": "_assess_financial_sustainability",
  "priority": 8,
  "provides": "pdet_analysis.financial_sustainability",
  "role": "_assess_financial_sustainability_assessment",
  "description": "Bayesian assessment of financial sustainability with risk inference"
}
```

#### 2. FinancialAuditor._detect_allocation_gaps
**Current Suggestion**: `_trace_budget_allocations` (score: 3)
**BETTER Alternative**: `PDETMunicipalPlanAnalyzer._analyze_funding_sources`

**Why Better**:
- Explicitly identifies funding source gaps
- Maps to official Colombian systems (SGP, SGR, etc.)
- Provides gap analysis with territorial context
- Returns structured gap reports

**Implementation**:
```json
{
  "class_name": "PDETMunicipalPlanAnalyzer",
  "method_name": "_analyze_funding_sources",
  "priority": 9,
  "provides": "pdet_analysis.funding_sources_gap_analysis",
  "role": "_analyze_funding_sources_analysis",
  "description": "Comprehensive funding source gap analysis with territorial context"
}
```

#### 3. FinancialAuditor._match_goal_to_budget
**Current Suggestion**: `_trace_budget_allocations` (score: 3)
**BETTER Alternative**: `PDETMunicipalPlanAnalyzer._extract_budget_for_pillar`

**Why Better**:
- Designed for PDET pillar-budget matching
- Extracts budget amounts linked to strategic goals
- Semantic matching between goals and budget tables
- Returns confidence scores for matches

**Implementation**:
```json
{
  "class_name": "PDETMunicipalPlanAnalyzer",
  "method_name": "_extract_budget_for_pillar",
  "priority": 7,
  "provides": "pdet_analysis.goal_budget_matching",
  "role": "_extract_budget_for_pillar_extraction",
  "description": "Semantic matching of goals to budget allocations with confidence scoring"
}
```

#### 4. PDETMunicipalPlanAnalyzer._generate_optimal_remediations
**Current Status**: Missing
**FOUND**: Method EXISTS in financiero_viabilidad_tablas.py line 3!

**Action**: NO REPLACEMENT NEEDED - Update catalog to include this method

**Method Signature**:
```python
def _generate_optimal_remediations(self, gaps: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Generate optimal remediation strategies for identified gaps"""
```

## Quality Assurance Checklist

### Pre-Update Validation
- [ ] Verify source method exists in dispensary
- [ ] Check method signature compatibility
- [ ] Review method docstring for expected inputs/outputs
- [ ] Confirm method is not deprecated

### Post-Update Validation
- [ ] All contract JSON files are valid JSON
- [ ] All contract_hash values regenerated
- [ ] method_count matches actual method array length
- [ ] No duplicate priority values in methods array
- [ ] All class_name values exist in methods_dispensary/
- [ ] All method_name values exist in their respective classes
- [ ] Executor factory validation passes
- [ ] Contract schema validation passes

### Testing Strategy
1. **Unit Test**: Verify each updated contract loads correctly
2. **Integration Test**: Execute affected executors with test documents
3. **Output Validation**: Compare answers before/after method change
4. **Performance Test**: Ensure no regression in execution time

## Automated Tools

### Contract Validation Tool
```python
def validate_contract(contract_path):
    """Validate a single contract for integrity"""
    with open(contract_path) as f:
        contract = json.load(f)
    
    errors = []
    
    # Check method_count matches
    declared_count = contract['method_binding']['method_count']
    actual_count = len(contract['method_binding']['methods'])
    if declared_count != actual_count:
        errors.append(f"method_count mismatch: {declared_count} != {actual_count}")
    
    # Check for duplicate priorities
    priorities = [m['priority'] for m in contract['method_binding']['methods']]
    if len(priorities) != len(set(priorities)):
        errors.append("Duplicate priority values found")
    
    # Verify hash
    temp_contract = contract.copy()
    declared_hash = temp_contract['identity']['contract_hash']
    del temp_contract['identity']['contract_hash']
    calculated_hash = hashlib.sha256(
        json.dumps(temp_contract, sort_keys=True).encode()
    ).hexdigest()
    if declared_hash != calculated_hash:
        errors.append(f"Hash mismatch: {declared_hash[:16]}... != {calculated_hash[:16]}...")
    
    return errors
```

### Mass Contract Updater
See bulk_update script in Scenario 2 above.

## Change Impact Matrix

| Missing Method | Executors Affected | Contracts to Update | Priority | Best Replacement |
|----------------|-------------------|---------------------|----------|------------------|
| FinancialAuditor._calculate_sufficiency | D1-Q3, D3-Q2, D5-Q2 | 30 (3×10) | HIGH | PDETMunicipalPlanAnalyzer._assess_financial_sustainability |
| FinancialAuditor._detect_allocation_gaps | D1-Q2, D4-Q4 | 20 (2×10) | HIGH | PDETMunicipalPlanAnalyzer._analyze_funding_sources |
| SemanticProcessor.chunk_text | D1-Q1, D6-Q5 | 20 (2×10) | HIGH | EmbeddingPolicyProducer.get_chunk_text |
| FinancialAuditor._match_goal_to_budget | D1-Q3, D3-Q3 | 20 (2×10) | MEDIUM | PDETMunicipalPlanAnalyzer._extract_budget_for_pillar |
| BayesianMechanismInference._aggregate_bayesian_confidence | D4-Q3, D5-Q2 | 20 (2×10) | MEDIUM | BayesianMechanismInference.aggregate_evidences |
| MechanismPartExtractor methods | D1-Q4 | 10 (1×10) | MEDIUM | Use existing alternatives |
| SemanticProcessor.embed_single | D1-Q1 | 10 (1×10) | LOW | SemanticProcessor._embed_batch |
| Others | Various | Various | LOW | See audit report |

**Total Contracts Requiring Updates**: ~150 of 300 (50%)

## Recommendations

1. **Immediate Action**: Update audit_executor_methods.py to use PDETMunicipalPlanAnalyzer methods as primary suggestions
2. **Batch Process**: Use bulk updater script for high-priority methods affecting 20+ contracts
3. **Validation**: Re-run executor factory validation after all updates
4. **Documentation**: Update AUDIT_EXECUTOR_METHODS.md with new suggestions
5. **Testing**: Execute full test suite on updated executors before production deployment

## Conclusion

Method changes require careful propagation across multiple contracts. The key is:
- **Systematic approach**: Use manifests and automation
- **Quality validation**: Hash verification and schema compliance
- **Better replacements**: Use comprehensive methods from PDETMunicipalPlanAnalyzer
- **Testing**: Validate outputs before production

The 30-executor × 10-question structure means method changes can cascade to 300 contracts, requiring robust automation and validation procedures.
