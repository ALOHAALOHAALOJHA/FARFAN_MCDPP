# CQVR Troubleshooting Guide

## Overview

This guide provides solutions to common issues encountered when using the CQVR (Contract Quality Verification and Remediation) system. Issues are organized by component and severity.

## Table of Contents

1. [Tier 1 Issues (Critical)](#tier-1-issues-critical)
2. [Tier 2 Issues (Functional)](#tier-2-issues-functional)
3. [Tier 3 Issues (Quality)](#tier-3-issues-quality)
4. [Validation Errors](#validation-errors)
5. [Performance Issues](#performance-issues)
6. [Integration Problems](#integration-problems)

---

## Tier 1 Issues (Critical)

### Issue: A1 - Identity-Schema Mismatch

**Symptoms**:
```
Blocker: A1: Identity-Schema mismatch for 'question_id': identity=Q001, schema=Q002
Score: A1 = 15/20 (5 points lost)
```

**Root Cause**: Identity fields don't match output schema const values, usually from copy-paste errors.

**Solution**:
```python
# Manual fix
def fix_identity_schema_mismatch(contract):
    identity = contract["identity"]
    schema_props = contract["output_contract"]["schema"]["properties"]
    
    # Sync identity → schema
    for field in ["question_id", "policy_area_id", "dimension_id", 
                  "question_global", "base_slot"]:
        if field in identity:
            if field not in schema_props:
                schema_props[field] = {}
            schema_props[field]["const"] = identity[field]
    
    return contract
```

**Prevention**:
- Never copy-paste contracts between questions
- Always generate contracts from questionnaire monolith
- Use automated transformation pipelines

**Impact if Ignored**: Contract outputs will have incorrect identity metadata, breaking downstream aggregation.

---

### Issue: A2 - Orphan Sources in Assembly Rules

**Symptoms**:
```
Blocker: A2: Assembly sources not in provides: ['nonexistent.method', 'undefined.function']
Score: A2 = 5/20 (15 points lost)
```

**Root Cause**: Assembly rules reference methods that don't exist in method_binding.methods.

**Solution**:
```python
# Option 1: Remove orphan sources
def remove_orphan_sources(contract):
    provides_set = {
        m["provides"] 
        for m in contract["method_binding"]["methods"]
    }
    
    for rule in contract["evidence_assembly"]["assembly_rules"]:
        rule["sources"] = [
            src for src in rule["sources"]
            if src in provides_set or src.startswith("*.")
        ]
    
    return contract

# Option 2: Generate sources from provides
def regenerate_sources(contract):
    provides = [
        m["provides"] 
        for m in contract["method_binding"]["methods"]
    ]
    
    contract["evidence_assembly"]["assembly_rules"][0]["sources"] = provides
    return contract
```

**Prevention**:
- Generate assembly_rules.sources from method_binding.methods.provides
- Don't manually edit sources
- Validate provides before creating assembly rules

**Impact if Ignored**: Evidence assembly will fail at runtime, unable to find referenced methods.

---

### Issue: A3 - Zero Signal Threshold with Mandatory Signals

**Symptoms**:
```
Blocker: A3: CRITICAL - minimum_signal_threshold=0.0 but mandatory_signals defined. 
         Zero-strength signals will pass validation.
Score: A3 = 0/10 (CRITICAL FAILURE)
```

**Root Cause**: Signal threshold set to 0, allowing zero-strength signals to pass validation.

**Why This Is Critical**: With threshold=0, a signal with strength=0.0 is considered valid, meaning:
- Evidence with no support passes validation
- Contradictory evidence with negative weight passes
- Statistical tests with p-value=1.0 (no significance) pass

**Solution**:
```python
def fix_signal_threshold(contract):
    signal_reqs = contract.get("signal_requirements", {})
    
    if signal_reqs.get("mandatory_signals"):
        # Set threshold to 0.5 (50% confidence minimum)
        signal_reqs["minimum_signal_threshold"] = 0.5
        
        # Optionally set signal weights
        if not signal_reqs.get("signal_weights"):
            signals = signal_reqs["mandatory_signals"]
            signal_reqs["signal_weights"] = {
                sig: 1.0 / len(signals) for sig in signals
            }
    
    return contract
```

**Recommended Thresholds**:
- **0.5**: Default (50% confidence)
- **0.7**: High confidence required
- **0.3**: Exploratory analysis (low bar)

**Prevention**:
- Always set threshold ≥ 0.3 when mandatory_signals defined
- Review questionnaire monolith signal configuration
- Use template contracts with correct defaults

**Impact if Ignored**: Invalid evidence will pass validation, corrupting downstream analysis.

---

### Issue: A4 - Required Fields Not in Properties

**Symptoms**:
```
Blocker: A4: Required fields not in properties: ['analysis', 'confidence']
Score: A4 = 0/5
```

**Root Cause**: Output schema lists fields as required but doesn't define them in properties.

**Solution**:
```python
def fix_missing_schema_properties(contract):
    schema = contract["output_contract"]["schema"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    
    for field in required:
        if field not in properties:
            # Add property with permissive type
            properties[field] = {
                "type": "object",
                "additionalProperties": True,
                "description": f"Auto-generated property for {field}"
            }
    
    return contract
```

**Better Solution** (if you know the types):
```python
def fix_missing_schema_properties_typed(contract):
    schema = contract["output_contract"]["schema"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    
    # Define proper types for common fields
    type_map = {
        "evidence": {"type": "array", "items": {"type": "object"}},
        "validation": {"type": "object"},
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    }
    
    for field in required:
        if field not in properties:
            properties[field] = type_map.get(field, {"type": "object"})
    
    return contract
```

**Prevention**:
- Define properties before marking fields as required
- Use schema validation during contract creation
- Copy property definitions from similar contracts

---

## Tier 2 Issues (Functional)

### Issue: B1 - Low Pattern Coverage

**Symptoms**:
```
Warning: B1: Pattern count (2) < required elements (5)
Score: B1 = 4/10
```

**Root Cause**: Not enough patterns defined to cover expected elements.

**Solution**:
```python
def generate_patterns_for_elements(contract):
    """Generate basic patterns for uncovered expected elements"""
    patterns = contract["question_context"]["patterns"]
    expected = contract["question_context"]["expected_elements"]
    
    # Extract covered element types
    covered_types = {
        p.get("target_element_type") 
        for p in patterns 
        if p.get("target_element_type")
    }
    
    # Generate patterns for uncovered elements
    pattern_id_counter = len(patterns) + 1
    
    for element in expected:
        elem_type = element.get("type")
        if elem_type not in covered_types:
            patterns.append({
                "id": f"PAT-{pattern_id_counter:03d}",
                "target_element_type": elem_type,
                "pattern": f"(?i){elem_type.replace('_', ' ')}",
                "confidence_weight": 0.8,
                "category": "GENERATED"
            })
            pattern_id_counter += 1
    
    return contract
```

**Manual Alternative**: Add patterns based on question content:
```json
{
  "patterns": [
    {
      "id": "PAT-001",
      "target_element_type": "instrumento_especificado",
      "pattern": "(?i)(programa|proyecto|política)\\s+(?:de\\s+)?(?:género|igualdad)",
      "confidence_weight": 0.9,
      "category": "POLICY_INSTRUMENT"
    }
  ]
}
```

**Prevention**:
- Start with template patterns for common element types
- Copy patterns from similar questions
- Use pattern generation tools

---

### Issue: B2 - Boilerplate Method Descriptions

**Symptoms**:
```
Warning: B2: High boilerplate ratio: 8/10 methods
Score: B2 = 2/10
```

**Root Cause**: Method technical_approach contains generic descriptions like "Execute method", "Process results".

**Generic Patterns Detected**:
- "Execute"
- "Process results"
- "Return structured output"
- "O(n) where n=input size"
- "Input data is preprocessed"

**Solution**: Replace with specific descriptions:

**Before** (Boilerplate):
```json
{
  "technical_approach": {
    "steps": [
      {"step": 1, "description": "Execute method"},
      {"step": 2, "description": "Process results"},
      {"step": 3, "description": "Return structured output"}
    ],
    "complexity": "O(n) where n=input size"
  }
}
```

**After** (Specific):
```json
{
  "technical_approach": {
    "steps": [
      {
        "step": 1, 
        "description": "Parse policy text into dependency graph using spaCy NLP pipeline"
      },
      {
        "step": 2, 
        "description": "Apply DAG validation: check for cycles using Tarjan's algorithm"
      },
      {
        "step": 3, 
        "description": "Calculate acyclicity p-value via permutation test (1000 iterations)"
      }
    ],
    "complexity": "O(V + E) for graph construction, O(n!) worst-case for permutation test",
    "assumptions": [
      "Text dependencies imply causal structure",
      "Cycles indicate logical inconsistencies",
      "P-value < 0.05 rejects null hypothesis of random graph"
    ]
  }
}
```

**Template for Quality Descriptions**:
1. **Specific inputs**: What data structures/formats?
2. **Specific algorithms**: Which algorithm/library?
3. **Specific outputs**: What structure/meaning?
4. **Complexity**: Actual algorithmic complexity
5. **Assumptions**: What must be true for this to work?

---

### Issue: B3 - No Failure Contract

**Symptoms**:
```
Warning: B3: No emit_code in failure_contract
Score: B3 = 8/10 (-2 pts)
```

**Root Cause**: Error handling doesn't specify emit_code for failure scenarios.

**Solution**:
```python
def add_failure_contract(contract):
    """Add failure contract with emit_code"""
    error_handling = contract.get("error_handling", {})
    
    if "failure_contract" not in error_handling:
        error_handling["failure_contract"] = {}
    
    failure = error_handling["failure_contract"]
    
    # Add emit_code if missing
    if not failure.get("emit_code"):
        question_id = contract["identity"]["question_id"]
        failure["emit_code"] = f"FAIL_{question_id}_VALIDATION"
    
    # Add abort conditions if missing
    if not failure.get("abort_if"):
        failure["abort_if"] = [
            "validation.completeness < 0.5",
            "validation.coherence < 0.3",
            "len(evidence) == 0"
        ]
    
    contract["error_handling"] = error_handling
    return contract
```

**Prevention**:
- Always define failure_contract during contract creation
- Use template failure contracts
- Copy from similar contracts

---

## Tier 3 Issues (Quality)

### Issue: C1 - Boilerplate Documentation

**Symptoms**:
```
Warning: C1: Boilerplate paradigms detected: 6/10 methods
Score: C1 = 1/5
```

**Root Cause**: Epistemological foundations use generic phrases.

**Boilerplate Patterns**:
- "analytical paradigm"
- "This method contributes"
- "method implements structured analysis"

**Solution**: Replace with specific paradigms:

**Before** (Boilerplate):
```json
{
  "epistemological_foundation": {
    "paradigm": "analytical paradigm",
    "justification": "This method contributes to systematic analysis"
  }
}
```

**After** (Specific):
```json
{
  "epistemological_foundation": {
    "paradigm": "Bayesian Causal Inference with Counterfactual Testing",
    "justification": "Uses Bayesian updating to quantify causal necessity vs sufficiency, following Pearl's ladder of causation. Counterfactual testing via intervention simulations enables distinguishing correlation from causation.",
    "theoretical_framework": [
      "Pearl, J. (2009). Causality: Models, Reasoning, and Inference",
      "Spirtes, P. et al. (2000). Causation, Prediction, and Search"
    ]
  }
}
```

**Quality Checklist for Paradigms**:
- [ ] Names specific methodology (Bayesian, Frequentist, Causal, etc.)
- [ ] Explains *why* this approach vs alternatives
- [ ] References theoretical framework
- [ ] Describes assumptions and limitations

---

### Issue: C2 - Missing Template Placeholders

**Symptoms**:
```
Warning: C2: Template summary has no dynamic placeholders
Score: C2 = 3/5
```

**Root Cause**: Human-readable template has static text, won't adapt to runtime data.

**Solution**: Add dynamic placeholders:

**Before** (Static):
```json
{
  "template": {
    "title": "Gender Policy Analysis",
    "summary": "Analysis of gender policy instruments and causal logic."
  }
}
```

**After** (Dynamic):
```json
{
  "template": {
    "title": "Q007: Gender Activity Description Analysis (D2-Q2)",
    "summary": "Identified {instrument_count} policy instruments with {causal_logic_score:.1%} causal logic coherence. {validation_status}: {completeness_score:.1%} evidence completeness across {element_count} required elements."
  }
}
```

**Common Placeholders**:
- `{score}`: Overall score
- `{confidence}`: Confidence level
- `{evidence_count}`: Number of evidence items
- `{validation_status}`: Pass/Fail status
- `{completeness_score}`: Completeness percentage

---

### Issue: C3 - Missing Metadata

**Symptoms**:
```
Warning: C3: source_hash is placeholder - breaks provenance chain
Score: C3 = 2/5
```

**Root Cause**: Contract metadata incomplete (contract_hash, source_hash, timestamps).

**Solution**:
```python
import hashlib
import json
from datetime import datetime

def fix_metadata(contract):
    """Fix missing metadata fields"""
    identity = contract["identity"]
    traceability = contract.get("traceability", {})
    
    # Calculate contract hash
    contract_str = json.dumps(contract, sort_keys=True)
    identity["contract_hash"] = hashlib.sha256(contract_str.encode()).hexdigest()
    
    # Set created_at if missing
    if not identity.get("created_at"):
        identity["created_at"] = datetime.now().isoformat()
    
    # Set contract version
    if not identity.get("contract_version"):
        identity["contract_version"] = "3.0"
    
    # Set validated_against_schema
    if not identity.get("validated_against_schema"):
        identity["validated_against_schema"] = "executor_contract_v3_schema.json"
    
    # Calculate source_hash from questionnaire monolith
    if not traceability.get("source_hash") or traceability["source_hash"].startswith("TODO"):
        # Load questionnaire monolith and calculate hash
        with open("canonic_questionnaire_central/questionnaire_monolith.json") as f:
            monolith = f.read()
        traceability["source_hash"] = hashlib.sha256(monolith.encode()).hexdigest()
    
    contract["traceability"] = traceability
    return contract
```

**Prevention**:
- Generate metadata during contract creation
- Use contract creation templates with metadata
- Validate metadata before saving

---

## Validation Errors

### Error: "Contract validation failed: invalid JSON"

**Cause**: Contract file has syntax errors.

**Solution**:
```bash
# Validate JSON syntax
python -m json.tool contract.json > /dev/null

# Or use jq
jq empty contract.json
```

**Common JSON Errors**:
- Missing commas between fields
- Trailing commas in arrays/objects
- Unescaped quotes in strings
- Invalid unicode characters

---

### Error: "KeyError: 'identity'"

**Cause**: Contract missing required top-level fields.

**Solution**: Ensure contract has all required fields:
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

for field in required_fields:
    if field not in contract:
        print(f"Missing required field: {field}")
```

---

### Error: "TypeError: 'NoneType' object is not iterable"

**Cause**: Expected array/list is None or missing.

**Solution**: Add defensive checks:
```python
# Before
for method in contract["method_binding"]["methods"]:
    ...

# After
methods = contract.get("method_binding", {}).get("methods", [])
for method in methods:
    ...
```

---

## Performance Issues

### Issue: Validation is Slow (>5 seconds per contract)

**Symptoms**: CQVR validation taking excessively long.

**Causes**:
1. Large contracts (>10MB)
2. Too many patterns (>100)
3. Deep nesting in JSON

**Solutions**:

**1. Profile validation**:
```python
import cProfile

def profile_validation():
    validator = CQVRValidator()
    pr = cProfile.Profile()
    pr.enable()
    
    decision = validator.validate_contract(contract)
    
    pr.disable()
    pr.print_stats(sort='cumtime')

profile_validation()
```

**2. Optimize pattern checking**:
```python
# Cache compiled regexes
import re

class OptimizedCQVRValidator(CQVRValidator):
    def __init__(self):
        super().__init__()
        self._pattern_cache = {}
    
    def verify_pattern_coverage(self, contract):
        patterns = contract.get("question_context", {}).get("patterns", [])
        
        # Compile patterns once
        for pattern in patterns:
            if pattern.get("id") not in self._pattern_cache:
                self._pattern_cache[pattern["id"]] = re.compile(
                    pattern.get("pattern", "")
                )
        
        # Rest of validation...
```

**3. Batch validation**:
```python
# Instead of validating one at a time
for contract_path in contracts:
    validator = CQVRValidator()  # DON'T: Creates validator each time
    validator.validate_contract(contract)

# Do this:
validator = CQVRValidator()  # DO: Reuse validator
for contract_path in contracts:
    validator.validate_contract(contract)
```

---

## Integration Problems

### Issue: CI/CD Pipeline Fails with CQVR

**Symptoms**: Pipeline passes locally but fails in CI.

**Common Causes**:

**1. File path differences**:
```python
# Wrong: Absolute path
contract_path = "/home/user/contracts/Q001.json"

# Right: Relative path
contract_path = Path("contracts/Q001.json")
```

**2. Missing dependencies**:
```yaml
# Add to CI config
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    # Ensure CQVR dependencies installed
```

**3. Different Python versions**:
```yaml
# Pin Python version in CI
- uses: actions/setup-python@v4
  with:
    python-version: '3.12'
```

---

### Issue: CQVR Results Different Between Runs

**Symptoms**: Same contract gets different scores on different runs.

**Cause**: Non-deterministic validation (random sampling, unordered sets).

**Solution**: Ensure deterministic validation:
```python
# Fix: Sort sets before iteration
provides_set = sorted(provides_set)  # Not: provides_set = set(...)

# Fix: Sort dict keys
for key in sorted(properties.keys()):
    ...

# Fix: Set random seed if using sampling
import random
random.seed(42)
```

---

## Getting Help

If your issue isn't covered here:

1. **Check Logs**: Enable debug logging
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Minimal Reproduction**: Create minimal contract that reproduces issue

3. **Review Examples**: Check working contracts (Q001, Q002, Q007)

4. **Consult Documentation**:
   - [Scoring System](scoring-system.md) - Rubric details
   - [Decision Matrix](decision-matrix.md) - Triage logic
   - [API Reference](api-reference.md) - Implementation details

5. **Report Bug**: Include:
   - CQVR version
   - Contract JSON (sanitized)
   - Full error message
   - Expected vs actual behavior

---

## See Also

- [Scoring System](scoring-system.md) - Component details
- [Decision Matrix](decision-matrix.md) - Triage rules
- [API Reference](api-reference.md) - Code examples
- [Evaluation Guide](../guides/evaluation-guide.md) - Usage instructions
