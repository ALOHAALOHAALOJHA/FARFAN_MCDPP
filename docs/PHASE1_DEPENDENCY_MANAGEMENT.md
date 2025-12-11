# Phase 1 Dependency Management: Derek Beach & Theory of Change

## Executive Summary

This document describes the proper dependency management approach for Phase 1's critical methodological frameworks:
- **Derek Beach's Process Tracing and Evidential Tests** (Beach & Pedersen 2019)
- **Theory of Change DAG Validation** (Goertz & Mahoney 2012)

**Core Principle**: Check necessary and sufficient conditions BEFORE import. Fail fast with actionable fixes. No graceful degradation for critical infrastructure.

---

## Problem Statement (Original Spanish)

> Estudia en profunidad los metodos de dereck beach y teoria de cambio que se utilizan en fase 1, testea que todas las condiciones esten presentes para que su llamado sea instantaneo y no problematica, recubre tales invocaciones con ejercicio adversarial de considear todos los bloqueadores que teoricamente podrían generar problemas en su inocacion y solucionalos definitivamete.

**Translation**: Study Derek Beach methods and Theory of Change in Phase 1 in depth, test that all conditions are present for instantaneous and non-problematic invocation, cover invocations with adversarial exercises considering all theoretical blockers, and solve them definitively.

---

## Methodology: Necessary & Sufficient Conditions

Following the feedback principle:

1. **Examine and trace** methods used from Derek Beach
2. **Ask**: "What are necessary and sufficient conditions for smooth importation?"
3. **Check one by one** each condition
4. **Fix or fill gaps** - don't work around them
5. **Ask**: "Is there an extra variable I'm not considering that could block?"
6. **If yes**: Unblock and repeat. **If no**: Job complete.

---

## Architecture

### Phase 1 Integration Points

Derek Beach and Theory of Change are used in 3 critical subphases:

1. **SP5 (Causal Chain Extraction)**: Line 1190-1200
   - `BeachEvidentialTest.classify_test(necessity, sufficiency)`
   - Classifies causal evidence as hoop_test, smoking_gun, doubly_decisive, or straw_in_wind

2. **SP6 (Causal Integration)**: Lines 1282-1310
   - `TeoriaCambio()` - Initialize validator
   - `TeoriaCambio.validacion_completa(dag)` - Validate causal hierarchy
   - Ensures Insumos → Procesos → Productos → Resultados → Causalidad flow

3. **SP7 (Argument Analysis)**: Lines 1388-1424
   - `BeachEvidentialTest.classify_test(necessity, sufficiency)` - Classify arguments
   - `BeachEvidentialTest.apply_test_logic(...)` - Apply evidential logic

### Current Import Pattern

```python
# In phase1_spc_ingestion_full.py lines 115-133
try:
    from methods_dispensary.derek_beach import (
        BeachEvidentialTest,
        CausalExtractor,
        MechanismPartExtractor,
    )
    DEREK_BEACH_AVAILABLE = True
except ImportError:
    warnings.warn("CRITICAL: methods_dispensary.derek_beach not available.")
    DEREK_BEACH_AVAILABLE = False
    BeachEvidentialTest = None
```

**Problem**: `derek_beach.py` calls `sys.exit(1)` if dependencies missing. Import fails before we can handle it.

---

## Solution: Pre-Import Validation

### 1. Package Structure Fix

**Created**: `src/methods_dispensary/__init__.py`

**Problem Solved**: `methods_dispensary` was not a proper Python package
- No `__init__.py` meant Python couldn't import from it
- Path issues prevented module discovery

**Contents**:
```python
from methods_dispensary.derek_beach import (
    BeachEvidentialTest,
    CausalExtractor,
    MechanismPartExtractor,
    DerekBeachProducer,
)
from methods_dispensary.teoria_cambio import (
    TeoriaCambio,
    ValidacionResultado,
    AdvancedDAGValidator,
)
```

### 2. Pre-Import Dependency Validator

**Created**: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`

**Purpose**: Validate ALL dependencies BEFORE attempting import

#### Necessary Conditions Checked

1. **Core Scientific Libraries**:
   - numpy >= 1.26.4, < 2.0.0
   - scipy >= 1.11.0
   - networkx >= 3.0
   - pandas >= 2.0.0

2. **NLP Libraries**:
   - spacy >= 3.7.0

3. **Bayesian Analysis**:
   - pymc >= 5.16.0, < 5.17.0
   - arviz >= 0.17.0
   - pytensor >= 2.25.1, < 2.26

4. **PDF Processing**:
   - PyMuPDF (imported as `fitz`) >= 1.23.0

5. **Validation & Data**:
   - pydantic >= 2.0.0 (NOT 1.x)
   - PyYAML >= 6.0

6. **Fuzzy Matching**:
   - fuzzywuzzy >= 0.18.0

7. **Graph Visualization**:
   - pydot >= 1.4.0

8. **farfan_pipeline Core**:
   - farfan_pipeline.core.parameters
   - farfan_pipeline.core.types
   - farfan_pipeline.core.calibration.decorators

#### Sufficient Condition

All 15+ necessary conditions above are met = Safe to import derek_beach and teoria_cambio.

### 3. Usage Pattern

```python
from canonic_phases.Phase_one.phase1_pre_import_validator import (
    validate_derek_beach_dependencies
)

# Check BEFORE attempting import
if not validate_derek_beach_dependencies():
    logger.error("Cannot import Derek Beach - missing dependencies")
    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
    sys.exit(1)

# Now safe to import
from methods_dispensary.derek_beach import BeachEvidentialTest
from methods_dispensary.teoria_cambio import TeoriaCambio
```

---

## Validation Output

### When Dependencies Missing

```bash
$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py

❌ MISSING DEPENDENCIES:
  ✗ numpy
     Fix: pip install "numpy>=1.26.4,<2.0.0"
  ✗ scipy
     Fix: pip install "scipy>=1.11.0"
  ✗ networkx
     Fix: pip install "networkx>=3.0"
  ✗ pandas
     Fix: pip install "pandas>=2.0.0"
  ✗ spacy
     Fix: pip install "spacy>=3.7.0"
  ✗ pymc
     Fix: pip install "pymc>=5.16.0,<5.17.0"
  ✗ arviz
     Fix: pip install "arviz>=0.17.0"
  ✗ pytensor
     Fix: pip install "pytensor>=2.25.1,<2.26"
  ✗ PyMuPDF (fitz)
     Fix: pip install "PyMuPDF>=1.23.0"
  ✗ pydantic
     Fix: pip install "pydantic>=2.0.0"
  ✗ fuzzywuzzy
     Fix: pip install "fuzzywuzzy>=0.18.0"
  ✗ pydot
     Fix: pip install "pydot>=1.4.0"

Fix all missing dependencies before importing derek_beach or teoria_cambio

================================================================================
FIX COMMANDS:
================================================================================
pip install "numpy>=1.26.4,<2.0.0"
pip install "scipy>=1.11.0"
pip install "networkx>=3.0"
pip install "pandas>=2.0.0"
pip install "spacy>=3.7.0"
pip install "pymc>=5.16.0,<5.17.0"
pip install "arviz>=0.17.0"
pip install "pytensor>=2.25.1,<2.26"
pip install "PyMuPDF>=1.23.0"
pip install "pydantic>=2.0.0"
pip install "fuzzywuzzy>=0.18.0"
pip install "pydot>=1.4.0"
```

### When All Dependencies Available

```bash
$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py

✅ ALL DEPENDENCIES AVAILABLE
Safe to import derek_beach and teoria_cambio modules
```

---

## Theoretical Blockers Addressed

| Blocker | Root Cause | Solution |
|---------|------------|----------|
| "ModuleNotFoundError: No module named 'methods_dispensary'" | No `__init__.py` | Created `src/methods_dispensary/__init__.py` |
| "ERROR: Dependencia faltante. Ejecute: pip install networkx" | Missing numpy/scipy/networkx/etc | Pre-validate with `phase1_pre_import_validator.py` |
| "ImportError: cannot import name 'BeachEvidentialTest'" | Import attempted before deps checked | Validate BEFORE import attempt |
| "pydantic.errors.PydanticImportError: BaseModel requires pydantic v2" | pydantic 1.x installed | Check for pydantic >= 2.0 specifically |
| "ImportError: cannot import name 'ParameterLoaderV2'" | farfan-pipeline not installed | Check farfan_pipeline.core.* modules |
| Circular import issues | Import order problems | Use pre-import validator to ensure clean state |

---

## Why NOT Graceful Degradation?

The previous approach (phase1_method_guards.py) was **fundamentally wrong** because:

### 1. Treats Critical Infrastructure as Optional

```python
# ❌ WRONG: Graceful degradation
if DEREK_BEACH_AVAILABLE:
    result = BeachEvidentialTest.classify_test(n, s)
else:
    result = "straw_in_wind"  # Fallback - WRONG!
```

**Problem**: Derek Beach evidential tests are the CORE of causal analysis. Using a fallback value means:
- Results are invalid
- User doesn't know results are degraded
- Pipeline continues with incorrect analysis
- Wastes computation on bad data

### 2. Hides Real Problem

Wrapping with try-catch and fallbacks:
- Hides missing dependencies
- Makes debugging harder
- User doesn't fix root cause
- Technical debt accumulates

### 3. Adds Unnecessary Complexity

Circuit breakers, health monitoring, retry logic:
- Overhead for no benefit
- More code to maintain
- More points of failure
- Distracts from real issue

### 4. Goes Against Rigor and Innovation

As feedback stated: "replace mediocrity with rigor and innovation"

**Mediocre**: Add wrappers, hide problems, pretend things work
**Rigorous**: Fix root cause, fail fast, provide clear fixes

---

## Correct Approach: Fail Fast

```python
# ✅ CORRECT: Validate then fail fast
from canonic_phases.Phase_one.phase1_pre_import_validator import (
    validate_derek_beach_dependencies,
    get_missing_dependencies
)

if not validate_derek_beach_dependencies():
    missing = get_missing_dependencies()
    logger.error("CRITICAL: Cannot proceed without Derek Beach methods")
    logger.error("Missing dependencies:")
    for dep_name, fix_cmd in missing:
        logger.error(f"  - {dep_name}: {fix_cmd}")
    sys.exit(1)

# Now we KNOW imports will work
from methods_dispensary.derek_beach import BeachEvidentialTest
```

**Benefits**:
- Clear error message
- Actionable fix commands
- No wasted computation
- User fixes problem properly
- No technical debt

---

## Integration with Phase 1

### Update Import Section

In `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`:

**Before** (lines 113-133):
```python
try:
    from methods_dispensary.derek_beach import (
        BeachEvidentialTest,
        CausalExtractor,
        MechanismPartExtractor,
    )
    DEREK_BEACH_AVAILABLE = True
except ImportError:
    warnings.warn("CRITICAL: methods_dispensary.derek_beach not available.")
    DEREK_BEACH_AVAILABLE = False
```

**After**:
```python
# Validate dependencies BEFORE import
from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies

if not validate_derek_beach_dependencies():
    logger.error(
        "CRITICAL: Derek Beach dependencies not available. "
        "Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py"
    )
    raise ImportError(
        "Derek Beach is REQUIRED infrastructure. "
        "Fix missing dependencies before running Phase 1."
    )

# Now safe to import
from methods_dispensary.derek_beach import (
    BeachEvidentialTest,
    CausalExtractor,
    MechanismPartExtractor,
)
```

### No Fallbacks in Usage

**Before** (lines 1190-1200):
```python
if DEREK_BEACH_AVAILABLE and BeachEvidentialTest is not None:
    test_type = BeachEvidentialTest.classify_test(necessity, sufficiency)
else:
    test_type = 'UNAVAILABLE'
```

**After**:
```python
# No conditional - imports validated at module load
test_type = BeachEvidentialTest.classify_test(necessity, sufficiency)
```

---

## CI/CD Integration

### GitHub Actions / CI Pipeline

Add dependency installation to CI:

```yaml
- name: Install Phase 1 dependencies
  run: |
    pip install "numpy>=1.26.4,<2.0.0"
    pip install "scipy>=1.11.0"
    pip install "networkx>=3.0"
    pip install "pandas>=2.0.0"
    pip install "spacy>=3.7.0"
    pip install "pymc>=5.16.0,<5.17.0"
    pip install "arviz>=0.17.0"
    pip install "pytensor>=2.25.1,<2.26"
    pip install "PyMuPDF>=1.23.0"
    pip install "pydantic>=2.0.0"
    pip install "fuzzywuzzy>=0.18.0"
    pip install "pydot>=1.4.0"
    pip install -e .  # Install farfan-pipeline

- name: Validate Phase 1 dependencies
  run: |
    python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
```

### setup.py / requirements.txt

Ensure all dependencies in `setup.py`:

```python
install_requires=[
    # Already present
    "numpy>=1.26.4,<2.0.0",
    "scipy>=1.11.0",
    "networkx>=3.0",
    "pandas>=2.0.0",
    "spacy>=3.7.0",
    "pymc>=5.16.0,<5.17.0",
    "arviz>=0.17.0",
    "pytensor>=2.25.1,<2.26",
    "PyMuPDF>=1.23.0",
    "pydantic>=2.0.0",
    "fuzzywuzzy>=0.18.0",
    "pydot>=1.4.0",
]
```

---

## Testing

### Unit Tests

Test that validation catches missing dependencies:

```python
def test_validation_detects_missing_numpy():
    """Test that missing numpy is detected."""
    # Mock numpy import to fail
    with patch.dict('sys.modules', {'numpy': None}):
        validator = PreImportValidator()
        success = validator.validate_all()
        assert not success
        assert any('numpy' in dep for dep, _ in validator.missing_deps)

def test_validation_passes_when_all_present():
    """Test that validation passes with all deps."""
    validator = PreImportValidator()
    success = validator.validate_all()
    assert success or len(validator.missing_deps) > 0  # Depends on environment
```

### Integration Tests

Test that Phase 1 fails properly without dependencies:

```python
def test_phase1_fails_without_derek_beach():
    """Test that Phase 1 fails fast without Derek Beach."""
    # In environment without deps
    with pytest.raises(ImportError, match="Derek Beach is REQUIRED"):
        import_phase1_module()
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'methods_dispensary'"

**Diagnosis**: Missing `__init__.py` or PYTHONPATH incorrect

**Solution**:
```bash
# Check if __init__.py exists
ls -la src/methods_dispensary/__init__.py

# If missing, it was created in this PR
git pull origin copilot/study-beach-methods-change-theory

# Verify PYTHONPATH includes src/
export PYTHONPATH=/path/to/repo/src:$PYTHONPATH
```

### Problem: "ERROR: Dependencia faltante. Ejecute: pip install networkx"

**Diagnosis**: Dependencies not installed

**Solution**:
```bash
# Run validator to see all missing
python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py

# Install all missing
pip install "numpy>=1.26.4,<2.0.0"
pip install "scipy>=1.11.0"
# ... (see validator output for complete list)

# Or install from requirements
pip install -r requirements.txt
pip install -e .
```

### Problem: "pydantic.errors.PydanticImportError: BaseModel requires pydantic v2"

**Diagnosis**: pydantic 1.x installed, need 2.0+

**Solution**:
```bash
# Check version
python3 -c "import pydantic; print(pydantic.__version__)"

# Upgrade if < 2.0
pip install "pydantic>=2.0.0" --upgrade
```

### Problem: Import works but validation fails

**Diagnosis**: Validator out of sync with actual requirements

**Solution**: Update `phase1_pre_import_validator.py` with any new dependencies found in `derek_beach.py` or `teoria_cambio.py`

---

## References

### Academic
- Beach, D., & Pedersen, R. B. (2019). *Process-Tracing Methods: Foundations and Guidelines* (2nd ed.). University of Michigan Press.
- Goertz, G., & Mahoney, J. (2012). *A Tale of Two Cultures: Qualitative and Quantitative Research in the Social Sciences*. Princeton University Press.

### Implementation
- Phase 1 SPC Ingestion: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
- Pre-Import Validator: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
- methods_dispensary Package: `src/methods_dispensary/__init__.py`
- Derek Beach Module: `src/methods_dispensary/derek_beach.py`
- Theory of Change Module: `src/methods_dispensary/teoria_cambio.py`

---

## Conclusion

Proper dependency management for Phase 1:

✅ **Check necessary conditions BEFORE import**
✅ **Fail fast with actionable fixes**
✅ **No graceful degradation for critical infrastructure**
✅ **Fix root cause, not symptoms**
✅ **Rigor and innovation over mediocrity**

This approach ensures Derek Beach and Theory of Change methods are ALWAYS available when Phase 1 runs, or execution stops with clear instructions on how to fix the environment.
