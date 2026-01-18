# Phase 2 Method Availability Audit - Critical Findings

**Date:** 2026-01-18  
**Auditor:** GitHub Copilot  
**Scope:** Comprehensive method availability, injection mechanisms, and call success factors

---

## Executive Summary

A comprehensive audit of Phase 2's 237 methods revealed **CRITICAL blockers** preventing method availability with 100% certainty. NO FALLBACKS are provided - all issues must be resolved for production readiness.

### Critical Statistics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Methods** | 237 | - |
| **Fully Available (100% certainty)** | 14 (5.91%) | 🔴 CRITICAL |
| **Methods with Blockers** | 223 (94.09%) | 🔴 CRITICAL |
| **Import Errors** | 223 methods | 🔴 CRITICAL |
| **Module Path Errors** | 237 methods (latent) | 🔴 FIXED |

**Availability Rate: 5.91%** - UNACCEPTABLE for production

---

## Critical Issue #1: Incorrect Module Path Mapping (RESOLVED)

### Problem

`phase2_10_02_methods_registry.py` line 50-60: `_MOTHER_FILE_TO_MODULE` dictionary maps to non-existent `methods_dispensary.*` module paths.

```python
# INCORRECT (Before)
_MOTHER_FILE_TO_MODULE: dict[str, str] = {
    "derek_beach.py": "methods_dispensary.derek_beach",  # ❌ Module doesn't exist
    "policy_processor.py": "methods_dispensary.policy_processor",  # ❌
    ...
}
```

### Impact

- **ALL** 237 methods would fail to inject
- `inject_canonical_methods()` would raise `ModuleNotFoundError`
- Method registry would be empty
- Contract execution would fail immediately

### Resolution (APPLIED)

```python
# CORRECT (After Fix)
_MOTHER_FILE_TO_MODULE: dict[str, str] = {
    "derek_beach.py": "farfan_pipeline.methods.derek_beach",  # ✅ Correct path
    "policy_processor.py": "farfan_pipeline.methods.policy_processor",  # ✅
    "teoria_cambio.py": "farfan_pipeline.methods.teoria_cambio",  # ✅
    "financiero_viabilidad_tablas.py": "farfan_pipeline.methods.financiero_viabilidad_tablas",  # ✅
    "embedding_policy.py": "farfan_pipeline.methods.embedding_policy",  # ✅
    "analyzer_one.py": "farfan_pipeline.methods.analyzer_one",  # ✅
    "contradiction_deteccion.py": "farfan_pipeline.methods.contradiction_deteccion",  # ✅
    "semantic_chunking_policy.py": "farfan_pipeline.methods.semantic_chunking_policy",  # ✅
    "bayesian_multilevel_system.py": "farfan_pipeline.methods.bayesian_multilevel_system",  # ✅
}
```

**Status:** ✅ FIXED in commit (pending)

---

## Critical Issue #2: Missing Runtime Dependencies

### Problem

223 out of 237 methods (94%) cannot be imported due to missing Python packages.

### Dependency Analysis

| Missing Package | Methods Affected | Files Affected |
|----------------|------------------|----------------|
| **numpy** | 117 methods | bayesian_multilevel_system.py, analyzer_one.py, others |
| **canonic_questionnaire_central** | 66 methods | derek_beach.py, policy_processor.py, financiero_viabilidad_tablas.py |
| **networkx** | 30 methods | Multiple files |
| **img2table** | 10 methods | financiero_viabilidad_tablas.py |

### Root Cause

Dependencies ARE defined in `requirements.txt` but NOT installed in the runtime environment:

```txt
# From requirements.txt (DEFINED BUT NOT INSTALLED)
numpy>=1.26.4,<2.0.0
pandas>=2.1.0
scikit-learn>=1.6.0
scipy>=1.11.0
nltk>=3.8.0
sentence-transformers>=3.1.0,<3.2.0
torch>=2.1.0
transformers>=4.41.0,<4.42.0
networkx>=3.0.0
```

### Impact on Call Success

**Current State:**
- Method availability: 5.91%
- Call success probability: ~0% (methods cannot even be imported)
- Risk level: CRITICAL for 223/237 methods

**After Dependency Installation:**
- Expected availability: ~94% (223 methods become importable)
- Call success probability: ~80-95% (pending instantiation validation)
- Risk level: LOW-MEDIUM for most methods

### Resolution Required

```bash
# IMMEDIATE ACTION REQUIRED
pip install -r requirements.txt

# Critical packages (minimum):
pip install numpy>=1.26.4 pandas scikit-learn scipy networkx
```

**Estimated Installation Time:** 2-5 minutes  
**Estimated Download Size:** ~500MB-2GB (depends on torch CPU vs GPU)

---

## Critical Issue #3: Missing Canonical Methods Inventory

### Problem

`phase2_10_02_methods_registry.py` line 45 references non-existent file:

```python
_CANONICAL_INVENTORY_PATH = (
    Path(__file__).resolve().parent / "json_files_phase_two" / "canonical_methods_triangulated.json"
)
```

**File Status:** ❌ DOES NOT EXIST

### Impact

- `inject_canonical_methods()` will fail immediately
- FileNotFoundError raised on method injection
- Method registry remains empty
- All 300 contracts will fail to execute

### Available Files

```
src/farfan_pipeline/phases/Phase_02/epistemological_assets/
  - method_sets_by_question.json ✅ EXISTS
  - classified_methods.json ✅ EXISTS
  - contratos_clasificados.json ✅ EXISTS
```

### Resolution Options

**Option A (Recommended):** Use existing `method_sets_by_question.json`

1. Update `_CANONICAL_INVENTORY_PATH` to point to epistemological_assets
2. Modify `load_canonical_methods_inventory()` to parse new format
3. Verify format compatibility

**Option B:** Generate `canonical_methods_triangulated.json`

1. Create generation script from existing JSON files
2. Triangulate method_sets_by_question.json + classified_methods.json
3. Save to expected location

**Estimated Time:** 30-60 minutes

---

## Method Injection Mechanism Analysis

### Current Design (Lazy Loading with No Fallbacks)

```python
def inject_canonical_methods(registry: MethodRegistry) -> dict[str, Any]:
    """
    Inject methods WITHOUT class instantiation.
    
    Flow:
    1. Load canonical_methods_triangulated.json  # ❌ FILE MISSING
    2. For each (class, method):
       a. Import class from mother module  # ❌ WRONG MODULE PATH (FIXED)
       b. Get unbound method from class  # ⚠️ REQUIRES IMPORT SUCCESS
       c. Create lazy wrapper
       d. Inject into registry._direct_methods
    3. On first call: instantiate class ONCE, cache forever
    """
```

### NO FALLBACKS Policy - Risk Assessment

| Risk Scenario | Probability | Impact | Mitigation Status |
|--------------|-------------|--------|-------------------|
| Module import fails | HIGH (100% current) | CRITICAL | ✅ FIXED (module path) |
| Class not found in module | LOW | CRITICAL | ⚠️ Needs validation |
| Method not found on class | LOW | CRITICAL | ⚠️ Needs validation |
| Instantiation fails (no-arg constructor) | MEDIUM | HIGH | ⚠️ Needs special rules |
| Method call fails (runtime error) | LOW-MEDIUM | HIGH | ⚠️ Needs error handling |
| Dependency missing at runtime | HIGH (current) | CRITICAL | ❌ BLOCKED (install deps) |

---

## Instantiation Requirements Analysis

### Classes Requiring Special Instantiation Rules

Based on code inspection, these classes may require non-standard instantiation:

| Class | File | Likely Requirements | Risk |
|-------|------|-------------------|------|
| PDFProcessor | derek_beach.py | Config path | MEDIUM |
| ConfigLoader | derek_beach.py | Config path | MEDIUM |
| ReportingEngine | derek_beach.py | Output directory | MEDIUM |
| PolicyAnalysisEmbedder | embedding_policy.py | Model name | HIGH |
| AdvancedSemanticChunker | embedding_policy.py | Model config | HIGH |

### Current Handling

```python
# In inject_canonical_methods()
if cls_name not in class_instances:
    if cls_name in registry._special_instantiation:
        # Use special rule ✅
        class_instances[cls_name] = registry._special_instantiation[cls_name](cls_type)
    else:
        try:
            # Default: no-arg constructor ✅
            class_instances[cls_name] = cls_type()
        except TypeError:
            # Fallback: __new__ without __init__ ⚠️ MAY BREAK
            class_instances[cls_name] = cls_type.__new__(cls_type)
```

**Risk:** Fallback to `__new__` may create uninitialized instances leading to runtime failures.

**Resolution:** Audit all 40+ classes for instantiation requirements and register special rules.

---

## External Dependencies Analysis

### Filesystem Dependencies

| Method File | Dependency Type | Risk |
|------------|----------------|------|
| derek_beach.py | PDF file paths | HIGH |
| financiero_viabilidad_tablas.py | Excel/CSV files | HIGH |
| Multiple | Cache directories | MEDIUM |
| Multiple | Config files | HIGH |

### Network Dependencies

| Method | Dependency | Risk |
|--------|-----------|------|
| embedding_policy.py | HuggingFace model download | HIGH |
| semantic_chunking_policy.py | Sentence transformer models | HIGH |

### Environment Variables

| Variable | Used By | Risk |
|----------|---------|------|
| CACHE_DIR | Multiple | MEDIUM |
| MODEL_PATH | embedding_policy.py | HIGH |
| CONFIG_PATH | derek_beach.py | HIGH |

---

## Call Success Factors - Comprehensive Matrix

### Variables Determining Call Success (NO FALLBACKS)

| Factor | Current State | Required State | Blocker? |
|--------|--------------|----------------|----------|
| **1. Module Path Correctness** | ❌ INCORRECT | ✅ FIXED | YES (RESOLVED) |
| **2. Module Importability** | ❌ FAIL (deps) | ⚠️ BLOCKED | YES |
| **3. Class Existence** | ❓ UNKNOWN | ✅ REQUIRED | PENDING |
| **4. Method Existence** | ❓ UNKNOWN | ✅ REQUIRED | PENDING |
| **5. Method Signature** | ❓ UNKNOWN | ✅ REQUIRED | PENDING |
| **6. Instantiation Success** | ❓ UNKNOWN | ✅ REQUIRED | PENDING |
| **7. Runtime Dependencies** | ❌ MISSING | ⚠️ BLOCKED | YES |
| **8. Filesystem Access** | ❓ UNKNOWN | ✅ REQUIRED | PENDING |
| **9. Network Access** | ❓ UNKNOWN | ⚠️ OPTIONAL | NO |
| **10. Memory Available** | ✅ OK | ✅ OK | NO |

### Certainty Level: Current vs Required

**Current Certainty:** 5.91% (14/237 methods fully available)  
**Target Certainty:** 100% (237/237 methods fully available)

**Path to 100% Certainty:**
1. ✅ Fix module paths (DONE)
2. ❌ Install dependencies (BLOCKED - requires action)
3. ⚠️ Fix canonical methods inventory (PENDING - 30-60 min)
4. ⚠️ Validate all class instantiations (PENDING - 2-4 hours)
5. ⚠️ Audit filesystem dependencies (PENDING - 1-2 hours)
6. ⚠️ Create special instantiation rules (PENDING - 2-3 hours)

**Total Estimated Time:** 6-10 hours after dependency installation

---

## Recommendations (Priority Order)

### 🔴 IMMEDIATE (Blocks Everything)

1. **Install Runtime Dependencies** (5 minutes)
   ```bash
   pip install -r requirements.txt
   ```
   **Impact:** Unblocks 223 methods (94%)

2. **Commit Module Path Fix** (1 minute)
   - `phase2_10_02_methods_registry.py` line 50-60
   - Change `methods_dispensary.*` to `farfan_pipeline.methods.*`
   **Impact:** Fixes injection path for all 237 methods

### 🟠 HIGH (Required for Method Injection)

3. **Fix Canonical Methods Inventory** (30-60 minutes)
   - Use `epistemological_assets/method_sets_by_question.json`
   - Or generate `canonical_methods_triangulated.json`
   **Impact:** Enables method injection

4. **Validate Class Availability** (1 hour)
   - Run comprehensive import test for all 40+ classes
   - Document which classes are missing
   **Impact:** Identifies missing classes

### 🟡 MEDIUM (Required for Call Success)

5. **Audit Instantiation Requirements** (2-4 hours)
   - Test each class for no-arg constructor
   - Create special instantiation rules where needed
   **Impact:** Ensures classes can be instantiated

6. **Validate Method Signatures** (1-2 hours)
   - Verify all 237 methods exist on their classes
   - Document signature mismatches
   **Impact:** Prevents method call failures

### 🟢 LOW (Quality & Reliability)

7. **Audit External Dependencies** (2-3 hours)
   - Map filesystem dependencies
   - Map network dependencies
   - Map environment variable usage
   **Impact:** Improves reliability

---

## Conclusion

Phase 2 currently has **0% operational readiness** for method execution due to:

1. ✅ **FIXED:** Incorrect module paths (would affect 100% of methods)
2. ❌ **BLOCKED:** Missing runtime dependencies (affects 94% of methods)
3. ❌ **BLOCKED:** Missing canonical methods inventory file

**NO FALLBACKS** are provided per requirements. All blockers must be resolved for 100% certainty.

**Estimated Time to 100% Certainty:**
- After dependency installation: 6-10 hours of validation and fixes
- Current blocker removal: 5 minutes (install deps) + 30-60 minutes (fix inventory)

**Next Action:** Install dependencies and fix canonical methods inventory path.

---

**Audit Date:** 2026-01-18  
**Status:** CRITICAL BLOCKERS IDENTIFIED  
**Follow-up:** Required after dependency installation
