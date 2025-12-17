# CQVR Remediation Guide

## Overview

This guide provides detailed, step-by-step procedures for fixing contract issues identified by CQVR validation. Each fix includes code examples, verification steps, and expected score improvements.

## Table of Contents

1. [Automated Remediation](#automated-remediation)
2. [Tier 1 Fixes (Critical)](#tier-1-fixes-critical)
3. [Tier 2 Fixes (Functional)](#tier-2-fixes-functional)
4. [Tier 3 Fixes (Quality)](#tier-3-fixes-quality)
5. [Remediation Workflow](#remediation-workflow)
6. [Verification](#verification)

---

## Automated Remediation

CQVR provides automated remediation for common structural issues.

### Apply All Structural Corrections

```python
from src.farfan_pipeline.phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import ContractRemediation
import json

def auto_remediate(contract_path):
    """Apply all automated fixes to contract"""
    
    # Load contract
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Apply remediation
    remediation = ContractRemediation()
    patched = remediation.apply_structural_corrections(contract)
    
    # Save patched contract
    output_path = contract_path.replace('.json', '_patched.json')
    with open(output_path, 'w') as f:
        json.dump(patched, f, indent=2)
    
    print(f"✅ Applied automated fixes: {output_path}")
    return patched

# Usage
auto_remediate('contract.json')
```

**Automated Fixes Include**:
- ✅ Identity-schema coherence
- ✅ Method-assembly alignment
- ✅ Missing schema properties

**Not Automated** (require manual fixes):
- ❌ Signal threshold configuration
- ❌ Pattern generation
- ❌ Method specificity improvements
- ❌ Documentation quality

---

## Tier 1 Fixes (Critical)

### Fix A1: Identity-Schema Mismatch

**Issue**: Identity fields don't match output schema const values

**Blocker Example**:
```
A1: Identity-Schema mismatch for 'question_id': identity=Q001, schema=Q002
```

**Manual Fix**:
```python
def fix_identity_schema_coherence(contract):
    """Sync identity fields to output schema"""
    
    identity = contract.get("identity", {})
    schema_props = contract.get("output_contract", {}).get("schema", {}).get("properties", {})
    
    # Fields to sync
    fields = ["question_id", "policy_area_id", "dimension_id", "question_global", "base_slot"]
    
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
with open('contract.json') as f:
    contract = json.load(f)

contract = fix_identity_schema_coherence(contract)

with open('contract_fixed.json', 'w') as f:
    json.dump(contract, f, indent=2)
```

**Expected Score Improvement**: +5 to +20 points (A1)

**Verification**:
```python
# Verify fix worked
validator = CQVRValidator()
score = validator.verify_identity_schema_coherence(contract)
assert score == 20.0, f"Identity-schema still has issues: {score}/20"
print("✅ A1 fixed: 20/20 points")
```

---

### Fix A2: Orphan Sources in Assembly Rules

**Issue**: Assembly rules reference methods that don't exist

**Blocker Example**:
```
A2: Assembly sources not in provides: ['nonexistent.method', 'undefined.function']
```

**Option 1: Remove Orphan Sources**
```python
def remove_orphan_sources(contract):
    """Remove assembly sources that don't exist in provides"""
    
    # Get valid provides
    methods = contract.get("method_binding", {}).get("methods", [])
    provides_set = {m.get("provides") for m in methods if m.get("provides")}
    
    print(f"Valid provides: {len(provides_set)}")
    
    # Filter orphan sources
    assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
    
    for rule in assembly_rules:
        original_sources = rule.get("sources", [])
        
        # Keep only valid sources (and wildcards)
        valid_sources = []
        orphans_removed = []
        
        for source in original_sources:
            if isinstance(source, dict):
                source_key = source.get("namespace", "")
            else:
                source_key = source
            
            # Keep wildcards and valid provides
            if source_key.startswith("*.") or source_key in provides_set:
                valid_sources.append(source)
            else:
                orphans_removed.append(source_key)
        
        rule["sources"] = valid_sources
        
        if orphans_removed:
            print(f"  ❌ Removed orphan sources: {orphans_removed}")
        print(f"  ✅ Valid sources: {len(valid_sources)}")
    
    return contract
```

**Option 2: Regenerate Sources from Provides** (Recommended)
```python
def regenerate_assembly_sources(contract):
    """Regenerate assembly sources from method provides"""
    
    # Get all provides
    methods = contract.get("method_binding", {}).get("methods", [])
    provides = [m.get("provides") for m in methods if m.get("provides")]
    
    print(f"Regenerating sources from {len(provides)} methods")
    
    # Replace sources with provides
    assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
    
    if assembly_rules:
        assembly_rules[0]["sources"] = provides
        print(f"  ✅ Set {len(provides)} sources")
    else:
        print("  ⚠️  No assembly rules found")
    
    return contract
```

**Expected Score Improvement**: +10 to +15 points (A2)

**Verification**:
```python
score = validator.verify_method_assembly_alignment(contract)
assert score >= 18.0, f"Assembly still has issues: {score}/20"
print(f"✅ A2 fixed: {score}/20 points")
```

---

### Fix A3: Zero Signal Threshold

**Issue**: Signal threshold is zero with mandatory signals defined

**Blocker Example**:
```
A3: CRITICAL - minimum_signal_threshold=0.0 but mandatory_signals defined.
    Zero-strength signals will pass validation.
```

**Fix**:
```python
def fix_signal_threshold(contract):
    """Set appropriate signal threshold"""
    
    signal_reqs = contract.get("signal_requirements", {})
    mandatory_signals = signal_reqs.get("mandatory_signals", [])
    
    if mandatory_signals:
        # Set threshold to 0.5 (50% confidence minimum)
        old_threshold = signal_reqs.get("minimum_signal_threshold", 0.0)
        signal_reqs["minimum_signal_threshold"] = 0.5
        
        print(f"  📊 Signal threshold: {old_threshold} → 0.5")
        
        # Set aggregation method if missing
        if not signal_reqs.get("signal_aggregation"):
            signal_reqs["signal_aggregation"] = "weighted_mean"
            print(f"  ✅ Set aggregation: weighted_mean")
        
        # Set signal weights if missing
        if not signal_reqs.get("signal_weights"):
            weight = 1.0 / len(mandatory_signals)
            signal_reqs["signal_weights"] = {
                sig: weight for sig in mandatory_signals
            }
            print(f"  ✅ Set equal weights: {weight:.3f}")
    
    contract["signal_requirements"] = signal_reqs
    return contract
```

**Alternative Thresholds**:
- **0.3**: Low confidence (exploratory)
- **0.5**: Medium confidence (standard)
- **0.7**: High confidence (strict)
- **0.9**: Very high confidence (critical decisions)

**Expected Score Improvement**: +10 points (A3)

**Verification**:
```python
score = validator.verify_signal_requirements(contract)
assert score >= 8.0, f"Signal requirements still have issues: {score}/10"
print(f"✅ A3 fixed: {score}/10 points")
```

---

### Fix A4: Missing Schema Properties

**Issue**: Required fields not defined in schema properties

**Blocker Example**:
```
A4: Required fields not in properties: ['analysis', 'confidence']
```

**Fix**:
```python
def fix_missing_schema_properties(contract):
    """Add missing schema properties for required fields"""
    
    schema = contract.get("output_contract", {}).get("schema", {})
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    
    # Type definitions for common fields
    type_map = {
        "base_slot": {"type": "string", "pattern": "^D[0-9]+-Q[0-9]+$"},
        "question_id": {"type": "string", "pattern": "^Q[0-9]{3}$"},
        "question_global": {"type": "integer", "minimum": 1, "maximum": 300},
        "policy_area_id": {"type": "string", "pattern": "^PA[0-9]{2}$"},
        "dimension_id": {"type": "string", "pattern": "^DIM[0-9]{2}$"},
        "evidence": {
            "type": "array",
            "items": {"type": "object"},
            "minItems": 1
        },
        "validation": {
            "type": "object",
            "properties": {
                "completeness": {"type": "number", "minimum": 0, "maximum": 1},
                "coherence": {"type": "number", "minimum": 0, "maximum": 1}
            }
        },
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "analysis": {"type": "object", "additionalProperties": True}
    }
    
    added = []
    for field in required:
        if field not in properties:
            # Use known type or default to object
            properties[field] = type_map.get(field, {
                "type": "object",
                "additionalProperties": True
            })
            added.append(field)
            print(f"  ✅ Added property: {field}")
    
    if not added:
        print("  ℹ️  All required fields already defined")
    
    return contract
```

**Expected Score Improvement**: +3 points (A4)

**Verification**:
```python
score = validator.verify_output_schema(contract)
assert score >= 3.0, f"Output schema still has issues: {score}/5"
print(f"✅ A4 fixed: {score}/5 points")
```

---

## Tier 2 Fixes (Functional)

### Fix B1: Low Pattern Coverage

**Issue**: Not enough patterns to cover expected elements

**Warning Example**:
```
B1: Pattern count (2) < required elements (5)
```

**Fix**:
```python
def generate_patterns_for_elements(contract):
    """Generate basic patterns for uncovered expected elements"""
    
    patterns = contract.get("question_context", {}).get("patterns", [])
    expected = contract.get("question_context", {}).get("expected_elements", [])
    
    # Find uncovered elements
    covered_types = {p.get("target_element_type") for p in patterns}
    required_elements = [e for e in expected if e.get("required")]
    
    uncovered = [e for e in required_elements if e.get("type") not in covered_types]
    
    if not uncovered:
        print("  ✅ All elements covered")
        return contract
    
    # Generate patterns
    pattern_id = len(patterns) + 1
    
    for element in uncovered:
        elem_type = element.get("type", "")
        elem_name = elem_type.replace("_", " ")
        
        pattern = {
            "id": f"PAT-{pattern_id:03d}",
            "target_element_type": elem_type,
            "pattern": f"(?i){elem_name}",
            "confidence_weight": 0.8,
            "category": "GENERATED",
            "description": f"Auto-generated pattern for {elem_type}"
        }
        
        patterns.append(pattern)
        pattern_id += 1
        
        print(f"  ✅ Generated pattern for: {elem_type}")
    
    return contract
```

**Manual Pattern Creation** (Better Quality):
```python
# Example: Create specific pattern for "instrumento_especificado"
pattern = {
    "id": "PAT-001",
    "target_element_type": "instrumento_especificado",
    "pattern": r"(?i)(programa|proyecto|política|iniciativa)\s+(?:de\s+)?(?:género|igualdad|equidad)",
    "confidence_weight": 0.9,
    "category": "POLICY_INSTRUMENT",
    "description": "Identifies policy instruments related to gender equality"
}
```

**Expected Score Improvement**: +3 to +5 points (B1)

---

### Fix B2: Boilerplate Method Descriptions

**Issue**: Method technical approaches contain generic descriptions

**Warning Example**:
```
B2: High boilerplate ratio: 8/10 methods
```

**Fix**: Replace generic descriptions with specific ones:

```python
def improve_method_specificity(contract):
    """Replace boilerplate with specific technical approaches"""
    
    methods = contract.get("methodological_depth", {}).get("methods", [])
    
    # Generic phrases to replace
    replacements = {
        "Execute": {
            "BayesianMechanismInference": "Apply Bayesian inference to estimate causal mechanisms",
            "CausalExtractor": "Extract causal relationships using dependency parsing",
            "AdvancedDAGValidator": "Validate directed acyclic graph structure"
        },
        "Process results": {
            "default": "Aggregate evidence scores using weighted mean"
        },
        "Return structured output": {
            "default": "Format output as JSON schema-compliant object"
        }
    }
    
    improved = 0
    for method_info in methods:
        method_name = method_info.get("method_name", "")
        steps = method_info.get("technical_approach", {}).get("steps", [])
        
        for step in steps:
            desc = step.get("description", "")
            
            # Replace generic phrases
            for generic, specific_map in replacements.items():
                if generic in desc:
                    # Use method-specific replacement or default
                    new_desc = specific_map.get(method_name, specific_map.get("default", desc))
                    step["description"] = new_desc
                    improved += 1
    
    print(f"  ✅ Improved {improved} method descriptions")
    return contract
```

**Manual Improvement Template**:
```json
{
  "technical_approach": {
    "steps": [
      {
        "step": 1,
        "description": "[Specific algorithm]: Parse [specific input] using [specific library/method]"
      },
      {
        "step": 2,
        "description": "[Specific computation]: Calculate [specific metric] via [specific formula/algorithm]"
      },
      {
        "step": 3,
        "description": "[Specific validation]: Verify [specific criterion] using [specific test]"
      }
    ],
    "complexity": "[Actual Big-O]: O(V + E) for graph, O(n log n) for sorting",
    "assumptions": [
      "[Specific assumption about data structure]",
      "[Specific assumption about input validity]",
      "[Specific assumption about algorithm applicability]"
    ]
  }
}
```

**Expected Score Improvement**: +4 to +6 points (B2)

---

### Fix B3: Missing Validation Rules

**Issue**: No validation rules or incomplete coverage

**Warning Example**:
```
B3: No validation_rules.rules defined
```

**Fix**:
```python
def add_validation_rules(contract):
    """Add validation rules for required elements"""
    
    expected = contract.get("question_context", {}).get("expected_elements", [])
    required_elements = [e.get("type") for e in expected if e.get("required")]
    
    validation_rules = {
        "rules": [
            {
                "rule_id": "COMPLETENESS_CHECK",
                "type": "completeness",
                "must_contain": {
                    "elements": required_elements,
                    "minimum_count": len(required_elements)
                },
                "severity": "BLOCKER"
            },
            {
                "rule_id": "COHERENCE_CHECK",
                "type": "coherence",
                "should_contain": [
                    {
                        "elements": required_elements,
                        "relationships": ["causal", "temporal"]
                    }
                ],
                "severity": "WARNING"
            }
        ]
    }
    
    contract["validation_rules"] = validation_rules
    
    # Add failure contract
    if "error_handling" not in contract:
        contract["error_handling"] = {}
    
    question_id = contract["identity"]["question_id"]
    contract["error_handling"]["failure_contract"] = {
        "emit_code": f"FAIL_{question_id}_VALIDATION",
        "abort_if": [
            f"validation.completeness < {len(required_elements) / (len(required_elements) + 2)}",
            "validation.coherence < 0.3",
            "len(evidence) == 0"
        ]
    }
    
    print(f"  ✅ Added validation rules for {len(required_elements)} elements")
    return contract
```

**Expected Score Improvement**: +5 to +8 points (B3)

---

## Tier 3 Fixes (Quality)

### Fix C1: Boilerplate Documentation

**Issue**: Epistemological foundations contain generic phrases

**Fix**: Replace with specific paradigms (see examples in [scoring-system.md](../cqvr/scoring-system.md))

**Expected Score Improvement**: +2 to +4 points (C1)

---

### Fix C2: Missing Template Placeholders

**Issue**: Human-readable template has no dynamic content

**Fix**:
```python
def add_template_placeholders(contract):
    """Add dynamic placeholders to template"""
    
    identity = contract.get("identity", {})
    question_id = identity.get("question_id", "")
    base_slot = identity.get("base_slot", "")
    
    template = {
        "title": f"{question_id}: [Question Title] ({base_slot})",
        "summary": (
            "Identified {{instrument_count}} policy instruments with "
            "{{causal_logic_score:.1%}} causal logic coherence. "
            "{{validation_status}}: {{completeness_score:.1%}} evidence completeness "
            "across {{element_count}} required elements."
        ),
        "sections": [
            {
                "heading": "Evidence Summary",
                "content": "Found {{evidence_count}} evidence items with average confidence {{avg_confidence:.2f}}"
            },
            {
                "heading": "Validation Results",
                "content": "Completeness: {{completeness:.1%}}, Coherence: {{coherence:.1%}}"
            }
        ]
    }
    
    contract["output_contract"]["human_readable_output"]["template"] = template
    print("  ✅ Added dynamic template placeholders")
    return contract
```

**Expected Score Improvement**: +2 points (C2)

---

### Fix C3: Missing Metadata

**Issue**: Contract metadata incomplete

**Fix**:
```python
import hashlib
from datetime import datetime

def fix_metadata(contract):
    """Complete contract metadata"""
    
    identity = contract.get("identity", {})
    traceability = contract.get("traceability", {})
    
    # Contract hash
    contract_str = json.dumps(contract, sort_keys=True)
    identity["contract_hash"] = hashlib.sha256(contract_str.encode()).hexdigest()[:64]
    
    # Created_at
    if not identity.get("created_at"):
        identity["created_at"] = datetime.now().isoformat()
    
    # Contract version
    if not identity.get("contract_version"):
        identity["contract_version"] = "3.0"
    
    # Schema validation
    if not identity.get("validated_against_schema"):
        identity["validated_against_schema"] = "executor_contract_v3_schema.json"
    
    # Source hash (from questionnaire monolith)
    if not traceability.get("source_hash") or traceability["source_hash"].startswith("TODO"):
        try:
            with open("canonic_questionnaire_central/questionnaire_monolith.json", "rb") as f:
                monolith_bytes = f.read()
            traceability["source_hash"] = hashlib.sha256(monolith_bytes).hexdigest()
            print("  ✅ Calculated source_hash from monolith")
        except FileNotFoundError:
            print("  ⚠️  Could not calculate source_hash: monolith not found")
    
    contract["traceability"] = traceability
    
    print(f"  ✅ Updated metadata")
    print(f"    - contract_hash: {identity['contract_hash'][:16]}...")
    print(f"    - created_at: {identity.get('created_at')}")
    print(f"    - version: {identity.get('contract_version')}")
    
    return contract
```

**Expected Score Improvement**: +2 to +5 points (C3)

---

## Remediation Workflow

### Complete Remediation Process

```python
#!/usr/bin/env python3
"""Complete contract remediation workflow"""

import json
from pathlib import Path
from src.farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator
from src.farfan_pipeline.phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import ContractRemediation

def full_remediation(contract_path: Path):
    """Apply all remediations and validate"""
    
    print(f"🔧 Remediating: {contract_path.name}")
    print("=" * 70)
    
    # Load contract
    with open(contract_path) as f:
        contract = json.load(f)
    
    # Initial validation
    validator = CQVRValidator()
    initial = validator.validate_contract(contract)
    
    print(f"\n📊 INITIAL SCORE: {initial.score.total_score:.1f}/100")
    print(f"   Decision: {initial.decision.value}")
    print(f"   Blockers: {len(initial.blockers)}")
    
    if initial.is_production_ready():
        print("\n✅ Already production ready!")
        return contract
    
    if initial.requires_reformulation():
        print("\n❌ Requires reformulation - automated fixes insufficient")
        return None
    
    # Apply automated fixes
    print("\n🔧 APPLYING AUTOMATED FIXES...")
    remediation = ContractRemediation()
    contract = remediation.apply_structural_corrections(contract)
    
    # Apply manual fixes
    print("\n🔧 APPLYING MANUAL FIXES...")
    
    # Fix signal threshold
    signal_reqs = contract.get("signal_requirements", {})
    if signal_reqs.get("mandatory_signals") and signal_reqs.get("minimum_signal_threshold", 0) <= 0:
        contract = fix_signal_threshold(contract)
    
    # Add metadata
    contract = fix_metadata(contract)
    
    # Re-validate
    final = validator.validate_contract(contract)
    
    print(f"\n📊 FINAL SCORE: {final.score.total_score:.1f}/100")
    print(f"   Improvement: +{final.score.total_score - initial.score.total_score:.1f} points")
    print(f"   Decision: {final.decision.value}")
    print(f"   Blockers: {len(final.blockers)}")
    
    if final.is_production_ready():
        print("\n✅ REMEDIATION SUCCESSFUL!")
        
        # Save fixed contract
        output_path = contract_path.parent / f"{contract_path.stem}_fixed.json"
        with open(output_path, 'w') as f:
            json.dump(contract, f, indent=2)
        
        print(f"💾 Saved: {output_path}")
        return contract
    else:
        print("\n⚠️  Remediation incomplete")
        print(f"Remaining blockers: {len(final.blockers)}")
        for blocker in final.blockers:
            print(f"  • {blocker}")
        return None

# Usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python remediate.py <contract.json>")
        sys.exit(1)
    
    result = full_remediation(Path(sys.argv[1]))
    sys.exit(0 if result else 1)
```

---

## Verification

### Verify All Fixes

```python
def verify_remediation(contract, initial_score):
    """Verify remediation improved score"""
    
    validator = CQVRValidator()
    final_decision = validator.validate_contract(contract)
    
    print("\n✅ VERIFICATION RESULTS:")
    print(f"   Initial: {initial_score:.1f}/100")
    print(f"   Final:   {final_decision.score.total_score:.1f}/100")
    print(f"   Δ:       +{final_decision.score.total_score - initial_score:.1f}")
    
    # Check improvements
    assert final_decision.score.total_score > initial_score, "Score did not improve"
    assert len(final_decision.blockers) <= 2, "Too many remaining blockers"
    
    if final_decision.is_production_ready():
        print("\n🎉 VERIFICATION PASSED: Production ready!")
        return True
    else:
        print(f"\n⚠️  VERIFICATION INCOMPLETE: {final_decision.decision.value}")
        return False
```

---

## See Also

- [Evaluation Guide](evaluation-guide.md) - Run validations
- [Scoring System](../cqvr/scoring-system.md) - Understand scores
- [Decision Matrix](../cqvr/decision-matrix.md) - Triage logic
- [Troubleshooting](../cqvr/troubleshooting.md) - Common issues
