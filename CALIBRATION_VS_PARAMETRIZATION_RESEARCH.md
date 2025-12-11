# 🔬 RESEARCH REPORT: Calibration vs Parametrization

**Date**: 2024-12-10  
**Purpose**: Understand distinction for filtering script  
**Status**: COMPLETE

---

## 📊 EXECUTIVE SUMMARY

After comprehensive research across codebase and documentation, here's the crystal-clear distinction:

### **CALIBRATION (WHAT Quality We Measure)**
- **Purpose**: Define INTRINSIC QUALITY of methods
- **Example**: "This executor has 0.85 theoretical soundness"
- **Frequency**: Quarterly changes, peer-reviewed
- **Location**: `system/config/calibration/*.json`
- **Governance**: Domain experts, methodological review

### **PARAMETRIZATION (HOW We Execute)**
- **Purpose**: Define RUNTIME EXECUTION parameters
- **Example**: "Run this with 60s timeout, 3 retries"
- **Frequency**: Daily changes, no review needed
- **Location**: `ExecutorConfig`, CLI args, ENV vars
- **Governance**: Operations team

---

## 🎯 KEY FINDING: TWO TYPES OF PARAMETERS

### Type 1: CENTRALIZED Parameters (In Config Files)

**What**: Runtime execution settings that are STABLE across runs

**Examples**:
```json
{
  "timeout_s": 120.0,
  "retry": 3,
  "max_tokens": 2048,
  "temperature": 0.7,
  "seed": 42
}
```

**Where**:
- `system/config/environments/{env}.json` (if it existed)
- `ExecutorConfig` dataclass defaults
- Currently: Individual executor files (DECENTRALIZED - PROBLEM!)

**Characteristics**:
- Same across most executions
- Environment-specific (dev/staging/prod)
- Loaded once per session
- ✅ SHOULD BE CENTRALIZED

---

### Type 2: DYNAMIC Parameters (NOT Centralized)

**What**: Method-specific, instance-specific, or user-provided parameters

**Examples**:
```python
# Method-specific
question_id = "Q1D2"  # Which question to score
dimension_id = "DIM01"  # Which dimension to analyze

# Instance-specific  
pdt_document = load_pdt("path/to/file.pdf")  # Input document
current_context = {"project": "ABC123"}  # Execution context

# User-provided
custom_threshold = 0.8  # User override for this run
```

**Where**:
- Function arguments
- Method inputs
- User interface
- Runtime state

**Characteristics**:
- Different every call
- Business logic dependent
- Cannot be pre-configured
- ❌ SHOULD NOT BE CENTRALIZED

---

## 📋 COMPLETE PARAMETER CLASSIFICATION

### CALIBRATION Parameters (Methods Needing Calibration)

**File**: `COHORT_2024_methods_requiring_calibration.json`

**Criteria** (ANY of these):
1. ✅ Has `role` in: `['executor', 'score', 'analyzer']`
2. ✅ Produces quality scores/ratings
3. ✅ Makes analytical decisions
4. ✅ Affects policy interpretation

**Examples**:
```python
# executor - NEEDS CALIBRATION
def execute_D1Q1(pdt: PDT) -> float:
    """Scores dimension 1, question 1"""
    return compute_score(pdt)

# score - NEEDS CALIBRATION
def score_policy_coherence(policy: Policy) -> float:
    """Rates policy coherence"""
    return analyze_coherence(policy)

# analyzer - NEEDS CALIBRATION
def analyze_evidence_strength(evidence: Evidence) -> float:
    """Analyzes evidence quality"""
    return assess_evidence(evidence)
```

**What They Get**:
- `base_score`: Intrinsic quality (0.5-0.9)
- `layer`: Which layers they need (@b, @chain, @q, etc.)
- `min_confidence`: Minimum acceptable score

**Count**: ~514 methods (executors: 207, analyzers: 117, scorers: 100, etc.)

---

### PARAMETRIZATION Parameters (Methods Needing Parametrization)

**File**: `COHORT_2024_methods_requiring_parametrization.json`

**Criteria** (ANY of these):
1. ✅ Has CENTRALIZED runtime parameters (timeout, retry, etc.)
2. ✅ Calls external services (LLM, API)
3. ✅ Has configurable execution behavior
4. ✅ Needs environment-specific settings

**Examples**:
```python
# Calls LLM - NEEDS PARAMETRIZATION
def extract_with_llm(text: str) -> dict:
    """Uses GPT to extract entities"""
    # Needs: max_tokens, temperature, timeout_s
    return call_llm(text)

# External API - NEEDS PARAMETRIZATION
def fetch_policy_data(url: str) -> dict:
    """Fetches from external API"""
    # Needs: timeout_s, retry, backoff
    return requests.get(url)

# Configurable behavior - NEEDS PARAMETRIZATION
def process_batch(items: list) -> list:
    """Processes items in batches"""
    # Needs: batch_size, max_workers, memory_limit
    return [process(item) for item in items]
```

**What They Get**:
- `timeout_s`: Max execution time
- `retry`: Retry attempts
- `max_tokens`: LLM token limit (if applicable)
- `temperature`: LLM temperature (if applicable)
- Other runtime configs

**Count**: TBD (need to scan for LLM calls, external APIs, configurable behavior)

---

## 🔍 CRITICAL DISTINCTION

### Methods Needing BOTH

Some methods need BOTH calibration AND parametrization:

```python
def execute_D1Q1_with_llm(pdt: PDT) -> float:
    """
    NEEDS CALIBRATION:
      - Produces quality score
      - Analytical method
      - base_score = 0.75
    
    NEEDS PARAMETRIZATION:
      - Calls LLM
      - timeout_s = 120.0
      - max_tokens = 2048
    """
    result = call_llm(extract_text(pdt))
    return compute_score(result)
```

**Solution**: Method appears in BOTH filtered JSONs!

---

## 📁 CURRENT STATE ANALYSIS

### What's Centralized NOW

1. ✅ **Layer Requirements**: `src/core/calibration/layer_requirements.py`
   - Maps roles → required layers
   - Single source of truth
   - Well-defined

2. ✅ **Fusion Weights**: `COHORT_2024_fusion_weights.json`
   - Choquet integral weights
   - Linear + interaction terms
   - Calibration parameter

3. ⚠️ **Partially Centralized**: Intrinsic calibration
   - Currently: ALL methods (wrong!)
   - Should be: Only methods requiring calibration

### What's NOT Centralized (PROBLEM!)

1. ❌ **Executor Configs**: Individual executor files
   - Each executor has own config
   - Duplicated timeout/retry values
   - Should be: Single `ExecutorConfig` per environment

2. ❌ **LLM Parameters**: Scattered across code
   - Hard-coded in various places
   - Should be: Centralized config

3. ❌ **Retry/Timeout**: Inconsistent
   - Different values everywhere
   - Should be: Environment-specific config

---

## 🎯 FILTERING LOGIC

### For CALIBRATION (Quality Assessment)

```python
def requires_calibration(method_info: dict) -> bool:
    """Determine if method needs calibration."""
    
    # Check 1: Role-based
    calibration_roles = {'executor', 'score', 'analyzer', 'extractor'}
    if method_info.get('role') in calibration_roles:
        return True
    
    # Check 2: Name patterns
    name = method_info.get('canonical_name', '').lower()
    if any(pattern in name for pattern in ['score', 'rate', 'evaluate', 'assess', 'execute', 'analyze']):
        return True
    
    # Check 3: Returns float (likely a score)
    # Would need AST analysis to detect return type
    
    return False
```

**Result**: ~500-600 methods (out of 1,990)

---

### For PARAMETRIZATION (Runtime Execution)

```python
def requires_parametrization(method_info: dict) -> bool:
    """Determine if method needs runtime parametrization."""
    
    # Check 1: Calls LLM
    file_path = method_info.get('file_path', '')
    with open(file_path) as f:
        content = f.read()
        if 'openai' in content or 'call_llm' in content or 'gpt' in content.lower():
            return True
    
    # Check 2: External API calls
    if 'requests.' in content or 'httpx' in content or 'urllib' in content:
        return True
    
    # Check 3: Batch processing
    if 'batch' in method_info.get('method_name', '').lower():
        return True
    
    # Check 4: Has timeout/retry in current code
    if 'timeout' in content or 'retry' in content:
        return True
    
    return False
```

**Result**: TBD (need to scan code content)

---

## ✅ RECOMMENDATIONS

### Immediate Actions

1. **Create Filtered JSONs**:
   ```
   COHORT_2024_methods_requiring_calibration.json
   COHORT_2024_methods_requiring_parametrization.json
   ```

2. **Use Role-Based Filtering First**:
   - Calibration: roles in {executor, score, analyzer, extractor}
   - Parametrization: scan for LLM/API calls

3. **Allow Overlap**:
   - Methods can be in BOTH lists
   - Calibration doesn't preclude parametrization

### Next Phase Actions

1. **Centralize ExecutorConfig**:
   - Create `system/config/environments/` directory
   - Define `development.json`, `staging.json`, `production.json`
   - Load via hierarchy: CLI → ENV → file → defaults

2. **Audit Hardcoded Parameters**:
   - Run `scripts/detect_hardcoded_calibrations.py`
   - Identify timeout/retry scattered in code
   - Move to centralized configs

3. **Create Parameter Registry**:
   - List of all methods needing parametrization
   - Their required parameters
   - Default values per environment

---

## 📊 EXPECTED RESULTS

After filtering:

```
Total methods: 1,990

Requiring CALIBRATION: ~514
  - executors: 207
  - analyzers: 117
  - scorers: 100
  - extractors: 36
  - others: ~54

Requiring PARAMETRIZATION: ~200-300 (estimate)
  - LLM calls: ~50-100
  - External APIs: ~30-50
  - Batch processors: ~20-30
  - Configurable behavior: ~100-150

In BOTH lists: ~100-150
  (e.g., executors that call LLMs)

Needing NEITHER: ~1,200-1,400
  (utility functions, helpers, data structures)
```

---

## 🎓 GOLDEN RULES

1. **Calibration = WHAT quality**: "This method has 0.85 soundness"
2. **Parametrization = HOW to run**: "Run with 60s timeout, 3 retries"
3. **Centralized params = STABLE**: Same across most runs
4. **Dynamic params = VARIABLE**: Different every call
5. **Methods can need BOTH**: Executor calling LLM = calibration + parametrization

---

## ✅ READY TO PROCEED

With this research, I can now create:

1. ✅ Filtering script with correct logic
2. ✅ `methods_requiring_calibration.json` (role-based)
3. ✅ `methods_requiring_parametrization.json` (code-scan based)
4. ✅ Documentation of distinction
5. ✅ Recommendations for centralization

**Shall I proceed with creating the filtering scripts?**

