# F.A.R.F.A.N Troubleshooting Guide

**Common Issues and Solutions**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Execution Errors](#execution-errors)
3. [Calibration Problems](#calibration-problems)
4. [Performance Issues](#performance-issues)
5. [Data Quality Issues](#data-quality-issues)
6. [Determinism Failures](#determinism-failures)

---

## Installation Issues

### Issue: ImportError for farfan_core modules

**Symptoms**:
```
ImportError: No module named 'farfan_pipeline'
```

**Solution**:
```bash
# Ensure package is installed in editable mode
pip install -e .

# Verify installation
python -c "import src; print(src.__file__)"
```

---

### Issue: Dependency conflicts

**Symptoms**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**Solution**:
```bash
# Create fresh virtual environment
python3.12 -m venv farfan-env-new
source farfan-env-new/bin/activate

# Install with specific versions
pip install -e . --no-cache-dir

# If still failing, install dependencies manually
pip install pydantic==2.5.0
pip install fastapi==0.104.1
# ... etc
```

---

### Issue: PyMuPDF not installing

**Symptoms**:
```
ERROR: Failed building wheel for pymupdf
```

**Solution**:
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install libmupdf-dev mupdf-tools

# Install system dependencies (macOS)
brew install mupdf-tools

# Then retry
pip install pymupdf
```

---

## Execution Errors

### Issue: Phase 0 validation fails

**Symptoms**:
```
ERROR: Boot check failed - missing calibration file
```

**Solution**:
```bash
# Verify all required files exist
ls -la src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/

# Check file permissions
chmod 644 src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/*.json

# Verify cohort consistency
python -c "
import json
with open('src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json') as f:
    data = json.load(f)
    print(f\"Cohort: {data['_cohort_metadata']['cohort_id']}\")
"
```

---

### Issue: @chain = 0.0 (broken chain)

**Symptoms**:
```
ERROR: Chain integrity check failed - missing required input 'preprocessed_doc'
```

**Solution**:
```python
# Debug chain validation
from src.orchestration.method_signature_validator import validate_chain

result = validate_chain(
    method_id="D1_Q1_Executor",
    inputs=context,
    outputs=result
)

print(f"Chain validation: {result}")
print(f"Failed checks: {result.get('failed_checks', [])}")

# Fix missing inputs
if "preprocessed_doc" not in context:
    # Ensure Phase 1 completed successfully
    # Check that CPP pipeline ran
    pass
```

---

### Issue: Contract validation fails (@C < 0.7)

**Symptoms**:
```
ERROR: Contract violation - score out of range: 1.23
```

**Solution**:
```python
# Identify contract violation
def fix_contract_violations(output):
    # Clip scores to [0, 1]
    if output.score < 0.0:
        output.score = 0.0
    elif output.score > 1.0:
        output.score = 1.0
    
    # Ensure confidence is valid
    if not (0.0 <= output.confidence <= 1.0):
        output.confidence = 0.5  # Default moderate confidence
    
    # Add missing fields
    if output.provenance is None:
        output.provenance = {
            "method_id": "Unknown",
            "method_version": "1.0.0",
            "cohort": "COHORT_2024",
        }
    
    return output
```

---

### Issue: Timeout exceeded

**Symptoms**:
```
TimeoutError: Executor D6_Q5 exceeded timeout of 60s
```

**Solution**:
```json
// Increase timeout in executor_config.json
{
  "D6_Q5_TheoryOfChange": {
    "timeout_s": 120,  // Increased from 60
    "max_memory_mb": 2048
  }
}
```

**Alternative**: Optimize method
```python
# Profile method to find bottleneck
import cProfile

cProfile.run('method.execute(input_data)', 'profile_stats')

# Analyze
import pstats
p = pstats.Stats('profile_stats')
p.sort_stats('cumulative').print_stats(20)
```

---

### Issue: Memory limit exceeded

**Symptoms**:
```
MemoryError: Circuit breaker triggered - memory usage exceeded 2048 MB
```

**Solution**:
```python
# Process in smaller batches
def batch_process(large_input, batch_size=100):
    results = []
    for i in range(0, len(large_input), batch_size):
        batch = large_input[i:i+batch_size]
        result = method.execute(batch)
        results.append(result)
    
    return aggregate_results(results)

# Or increase memory limit
# executor_config.json
{
  "D6_Q5_TheoryOfChange": {
    "max_memory_mb": 4096  // Increased from 2048
  }
}
```

---

## Calibration Problems

### Issue: @b score is too low (< 0.5)

**Symptoms**:
```
ERROR: Method D1_Q1_NewMethod failed hard gate - @b = 0.42
```

**Solution**:

1. **Improve b_theory**:
   - Add statistical validation
   - Document assumptions
   - Add sensitivity analysis

2. **Improve b_impl**:
   ```bash
   # Increase test coverage
   pytest --cov=src/methods_dispensary/new_method --cov-report=html
   
   # Add missing tests
   # Target: ≥80% coverage
   ```

3. **Improve b_deploy**:
   - Run more validation tests (target: ≥20)
   - Fix bugs causing failures
   - Add error handling for edge cases

---

### Issue: Weights don't sum to 1.0

**Symptoms**:
```
AssertionError: Fusion weights sum to 0.98, expected 1.0
```

**Solution**:
```python
def normalize_weights(weights: dict) -> dict:
    """Normalize weights to sum to 1.0."""
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}

# Apply
linear_weights = normalize_weights(linear_weights)
```

---

### Issue: Method-question mismatch (@q < 0.5)

**Symptoms**:
```
WARNING: Method poorly suited for question - @q = 0.32
```

**Solution**:

1. **Reassess method capabilities**:
   - Is method actually appropriate for this question?
   - Consider using fallback method

2. **Improve method description**:
   ```python
   # Update method docstring to better reflect capabilities
   # This affects semantic alignment score
   ```

3. **Adjust question priority**:
   - If method is Priority 1 but question is Priority 3, consider downgrading method

---

## Performance Issues

### Issue: Pipeline is very slow (>10 minutes per PDT)

**Diagnosis**:
```bash
# Profile full pipeline
python -m cProfile -o pipeline_profile.stats src/orchestration/orchestrator.py

# Analyze
python -m pstats pipeline_profile.stats
>>> sort cumulative
>>> stats 20
```

**Common Bottlenecks**:

1. **Semantic embedding** (sentence-transformers)
   ```python
   # Cache embeddings
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_embedding(text: str):
       return model.encode(text)
   ```

2. **Bayesian inference** (PyMC)
   ```python
   # Reduce MCMC samples
   with pm.Model() as model:
       # ... define model
       trace = pm.sample(
           draws=1000,  # Reduced from 2000
           tune=500,    # Reduced from 1000
           chains=2,    # Reduced from 4
       )
   ```

3. **PDF extraction** (PyMuPDF)
   ```python
   # Process pages in parallel
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       pages = list(executor.map(extract_page, page_numbers))
   ```

---

### Issue: High memory usage (>8GB)

**Diagnosis**:
```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024**2:.0f} MB")
```

**Solutions**:

1. **Clear large objects**:
   ```python
   # After processing each PDT
   del preprocessed_doc
   del embeddings
   import gc
   gc.collect()
   ```

2. **Use generators instead of lists**:
   ```python
   # Instead of
   chunks = [process_chunk(c) for c in all_chunks]
   
   # Use
   chunks = (process_chunk(c) for c in all_chunks)
   ```

3. **Process in batches**:
   ```python
   batch_size = 100
   for i in range(0, len(items), batch_size):
       batch = items[i:i+batch_size]
       process_batch(batch)
   ```

---

## Data Quality Issues

### Issue: PDT has no extractable text

**Symptoms**:
```
WARNING: PDF extraction yielded 0 characters
```

**Solution**:
```python
# Check if PDF is image-based (scanned)
import fitz

doc = fitz.open("pdt.pdf")
text = doc[0].get_text()

if len(text) < 100:
    print("PDF is likely scanned - OCR required")
    
    # Use OCR
    from PIL import Image
    import pytesseract
    
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(img, lang='spa')
```

---

### Issue: @u score is very low (< 0.3)

**Symptoms**:
```
WARNING: PDT structure severely deficient - @u = 0.24
```

**Diagnosis**:
```python
# Check which components are missing
pdt_structure = analyze_pdt_structure(doc)

print(f"S (Structure): {pdt_structure['S']:.2f}")
print(f"M (Mandatory): {pdt_structure['M']:.2f}")
print(f"I (Indicators): {pdt_structure['I']:.2f}")
print(f"P (PPI): {pdt_structure['P']:.2f}")

# Identify missing blocks
missing_blocks = [
    block for block in ["Diagnóstico", "Estratégica", "PPI", "Seguimiento"]
    if block not in pdt_structure['blocks_found']
]
print(f"Missing blocks: {missing_blocks}")
```

**Solutions**:

1. **Request corrected PDT** from municipality
2. **Manually annotate** critical sections
3. **Lower confidence** in results and add caveats to report

---

### Issue: Missing indicators table

**Symptoms**:
```
WARNING: Indicator matrix not detected - I = 0.0
```

**Solution**:
```python
# Try alternative extraction methods
import camelot

# Extract tables
tables = camelot.read_pdf("pdt.pdf", pages='all')

# Find indicator table
for table in tables:
    df = table.df
    if "Línea Base" in df.columns or "Meta" in df.columns:
        print(f"Found indicator table on page {table.page}")
        indicator_matrix = df
        break
```

---

## Determinism Failures

### Issue: Non-reproducible results

**Symptoms**:
```
ERROR: Output hash mismatch - expected sha256:abc123, got sha256:def456
```

**Diagnosis**:
```bash
# Check seed consistency
echo $PYTHONHASHSEED
# Should be: 0

# Check random state
python -c "
import random
import numpy as np

random.seed(42)
np.random.seed(42)

print(f'Python random: {random.random()}')
print(f'NumPy random: {np.random.random()}')
"

# Run twice - should be identical
```

**Solutions**:

1. **Set environment variables**:
   ```bash
   export PYTHONHASHSEED=0
   export CUDA_VISIBLE_DEVICES=-1  # Disable GPU
   export OMP_NUM_THREADS=1
   export MKL_NUM_THREADS=1
   ```

2. **Fix seed management**:
   ```python
   from src.orchestration.seed_registry import SeedRegistry
   
   # Initialize at start of execution
   seed_registry = SeedRegistry(base_seed=42)
   
   # Use in method
   method_seed = seed_registry.get_seed("D1_Q1")
   random.seed(method_seed)
   np.random.seed(method_seed)
   ```

3. **Check for non-deterministic operations**:
   ```python
   # BAD: Dictionary iteration order (Python <3.7)
   for key in dict.keys():
       process(key)
   
   # GOOD: Sorted iteration
   for key in sorted(dict.keys()):
       process(key)
   
   # BAD: Set iteration
   for item in set_items:
       process(item)
   
   # GOOD: Sorted list
   for item in sorted(set_items):
       process(item)
   ```

---

### Issue: Timestamp differences

**Symptoms**:
```
WARNING: Timestamp mismatch - execution times differ by 2 hours
```

**Solution**:
```python
# Always use UTC
from datetime import datetime, timezone

# BAD
timestamp = datetime.now().isoformat()

# GOOD
timestamp = datetime.now(timezone.utc).isoformat()

# Verify
assert timestamp.endswith('+00:00') or timestamp.endswith('Z')
```

---

### Issue: Floating-point differences

**Symptoms**:
```
AssertionError: Scores differ - expected 0.8456, got 0.8457
```

**Solution**:
```python
# Use approximate comparison
import numpy as np

def approx_equal(a, b, tolerance=1e-6):
    return abs(a - b) < tolerance

# Or
np.testing.assert_allclose(a, b, rtol=1e-6, atol=1e-6)
```

---

## Emergency Procedures

### Complete Pipeline Reset

```bash
# 1. Stop all processes
pkill -f farfan

# 2. Clear caches
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf artifacts/cache/

# 3. Reinstall
pip uninstall farfan-pipeline -y
pip install -e . --no-cache-dir

# 4. Verify installation
python -c "
from src.orchestration.orchestrator import Orchestrator
print('Installation OK')
"

# 5. Run minimal test
pytest tests/test_basic.py -v
```

---

### Data Corruption Recovery

```bash
# 1. Verify input files
sha256sum data/pdt.pdf
sha256sum config/questionnaire_monolith.json

# 2. Compare with known good hashes (from manifest)
python -c "
import json
with open('artifacts/manifests/manifest.json') as f:
    manifest = json.load(f)
    print(manifest['input_artifacts']['pdt_document']['hash'])
"

# 3. If mismatch, re-download or restore from backup
cp backup/pdt.pdf data/pdt.pdf

# 4. Re-run with clean state
rm -rf artifacts/output/
python src/orchestration/orchestrator.py --pdt data/pdt.pdf ...
```

---

## Getting Help

### Collect Diagnostic Information

```bash
# Generate diagnostic report
python scripts/generate_diagnostic_report.py > diagnostic.txt

# Include:
# - Python version
# - Package versions (pip list)
# - System info (uname -a)
# - Environment variables
# - Recent error logs
# - Sample output files
```

### Submit Issue

Include:
1. Diagnostic report
2. Minimal reproducible example
3. Expected vs actual behavior
4. Error messages (full traceback)
5. Configuration files used

---

## Related Documentation

- [VALIDATION_GUIDE.md](./VALIDATION_GUIDE.md) - System integrity validation
- [DETERMINISM.md](./DETERMINISM.md) - Reproducibility guarantees
- [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md) - Configuration schemas

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit
