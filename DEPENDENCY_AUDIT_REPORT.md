# Dependency Audit Report for FARFAN_MPP
**Date:** 2026-01-05
**Python Version:** 3.11.14 (Project requires 3.12)

## Executive Summary

This audit identified **4 critical security vulnerabilities**, several outdated packages, and opportunities to reduce dependency bloat. The project has **84 direct dependencies** with a large footprint due to ML/NLP libraries.

---

## 🚨 Critical Security Vulnerabilities

### pypdf Package - 4 CVEs (CRITICAL - IMMEDIATE ACTION REQUIRED)

The `pypdf` package (installed as dependency of `camelot-py`) has **4 known security vulnerabilities**:

1. **CVE-2025-55197** - RAM exhaustion via crafted PDF with FlateDecode filters
   - **Fixed in:** pypdf >= 6.0.0
   - **Current version:** 3.17.4
   - **Severity:** HIGH

2. **CVE-2025-62707** - Infinite loop via inline image with DCTDecode filter
   - **Fixed in:** pypdf >= 6.1.3
   - **Current version:** 3.17.4
   - **Severity:** HIGH

3. **CVE-2025-62708** - Large memory usage via LZWDecode filter
   - **Fixed in:** pypdf >= 6.1.3
   - **Current version:** 3.17.4
   - **Severity:** HIGH

4. **CVE-2025-66019** - Memory usage up to 1GB per stream via LZWDecode filter
   - **Fixed in:** pypdf >= 6.4.0
   - **Current version:** 3.17.4
   - **Severity:** MEDIUM

**Recommendation:** Upgrade `camelot-py` to a version that uses pypdf >= 6.4.0, or consider alternatives.

---

## 📦 Outdated System Packages

The following system-level packages are outdated (less critical but should be monitored):

| Package | Current | Latest | Priority |
|---------|---------|--------|----------|
| cryptography | 41.0.7 | 46.0.3 | HIGH |
| PyJWT | 2.7.0 | 2.10.1 | HIGH |
| setuptools | 68.1.2 | 80.9.0 | MEDIUM |
| pip | 24.0 | 25.3 | MEDIUM |
| httplib2 | 0.20.4 | 0.31.0 | MEDIUM |
| oauthlib | 3.2.2 | 3.3.1 | MEDIUM |

---

## 🔍 Dependency Bloat Analysis

### 1. Duplicate/Redundant PDF Libraries

The project has **5 PDF processing libraries**:

| Library | Usage | Size Impact | Status |
|---------|-------|-------------|--------|
| **pymupdf** (fitz) | ✅ Used extensively | High (100+ MB) | KEEP |
| **PyPDF2** | ✅ Used in codebase | Medium (5 MB) | KEEP |
| **pdfplumber** | ✅ Used (31 occurrences) | Medium (10 MB) | KEEP |
| **camelot-py** | ✅ Used for tables | High (50+ MB) | KEEP (but vulnerable) |
| **tabula-py** | ✅ Used for tables | High (requires Java) | KEEP |

**Analysis:** While this seems like bloat, each library serves different purposes:
- PyMuPDF: Fast, low-level PDF processing
- PyPDF2: PDF manipulation and merging
- pdfplumber: Text extraction with layout preservation
- camelot-py: Table extraction with computer vision
- tabula-py: Java-based table extraction

**Recommendation:** All are justified, but consider consolidating table extraction to either camelot or tabula (not both) if possible.

### 2. Dual Web Framework Setup

The project uses **both FastAPI and Flask**:

| Framework | Usage | Purpose | Status |
|-----------|-------|---------|--------|
| **FastAPI** | ✅ Primary API | Modern async REST API | KEEP |
| **Flask** | ✅ Legacy/specific features | Sync endpoints, SocketIO | KEEP (if needed) |

**Analysis:** Both frameworks are actively used in the codebase. Flask appears to be used for specific features (possibly legacy code or SocketIO support).

**Recommendation:**
- **SHORT TERM:** Keep both if migration is complex
- **LONG TERM:** Consider migrating Flask endpoints to FastAPI for consistency
- **ALTERNATIVE:** Use FastAPI's WebSocket support instead of flask-socketio

### 3. Heavy ML/NLP Dependencies

The project includes heavyweight ML libraries:

| Category | Libraries | Disk Impact |
|----------|-----------|-------------|
| **Transformers** | transformers, sentence-transformers, accelerate, torch | ~5-10 GB |
| **NLP** | spacy, nltk, langdetect, textstat, proselint | ~1 GB |
| **Bayesian** | pymc, pytensor, arviz | ~500 MB |
| **ML Core** | scikit-learn, scipy, numpy | ~500 MB |

**Total ML footprint:** ~7-12 GB

**Recommendation:**
- If not all features are used, consider making some dependencies optional
- Use lighter-weight alternatives where possible (e.g., scikit-learn without deep learning)
- Consider containerization to manage large dependencies

### 4. Potential Optional Dependencies

These dependencies might be candidates for optional extras:

| Package | Purpose | Recommendation |
|---------|---------|----------------|
| **proselint** | Prose linting | Optional: use only in development |
| **textstat** | Text statistics | Optional: use only if needed |
| **fuzzywuzzy** | Fuzzy string matching | Consider using rapidfuzz directly (already installed) |
| **python-Levenshtein** | String distance | Redundant with rapidfuzz |

---

## 📊 Dependency Statistics

- **Total direct dependencies:** 84
- **Total installed packages:** ~200 (including transitive)
- **Estimated disk space:** ~10-15 GB
- **Security vulnerabilities:** 4 (all in pypdf)
- **Outdated packages:** 24 (system-level)

---

## ✅ Recommendations

### Priority 1: IMMEDIATE (Security)

1. **Fix pypdf vulnerabilities:**
   ```bash
   # Check if camelot-py has newer version with pypdf >= 6.4.0
   pip install --upgrade camelot-py[cv]

   # If not available, consider alternatives or pin pypdf manually
   pip install "pypdf>=6.4.0"
   ```

2. **Upgrade cryptography and PyJWT:**
   ```bash
   pip install --upgrade cryptography PyJWT
   ```

### Priority 2: HIGH (Cleanup)

1. **Remove redundant string matching libraries:**
   - Remove `fuzzywuzzy` and `python-Levenshtein`
   - Use `rapidfuzz` directly (already installed, faster, pure Python)

   Update `requirements.txt`:
   ```diff
   - fuzzywuzzy>=0.18.0
   - python-Levenshtein>=0.23.0
   + rapidfuzz>=3.0.0
   ```

2. **Consider consolidating table extraction:**
   - Evaluate if both `camelot-py` and `tabula-py` are needed
   - `camelot-py` is more accurate but has security issues
   - `tabula-py` requires Java runtime

### Priority 3: MEDIUM (Optimization)

1. **Make development tools optional:**
   Create `requirements-dev.txt`:
   ```
   pytest>=8.0.0
   pytest-cov>=4.1.0
   pytest-asyncio>=0.23.0
   ruff>=0.1.0
   mypy>=1.8.0
   black>=24.0.0
   ```

   Remove from main `requirements.txt`.

2. **Create optional extras for specialized features:**
   Consider creating `setup.py` or `pyproject.toml` with extras:
   ```toml
   [project.optional-dependencies]
   ml = ["torch", "transformers", "sentence-transformers"]
   bayesian = ["pymc", "pytensor", "arviz"]
   nlp = ["spacy", "nltk"]
   pdf = ["pymupdf", "pdfplumber", "camelot-py", "tabula-py"]
   ```

3. **Evaluate Flask vs FastAPI:**
   - Audit Flask usage in codebase
   - If only used for SocketIO, consider FastAPI WebSocket support
   - Create migration plan if feasible

### Priority 4: LOW (Maintenance)

1. **Update Python version:**
   - Project requires Python 3.12 but running 3.11.14
   - Ensure compatibility and upgrade runtime

2. **Update system packages:**
   ```bash
   pip install --upgrade setuptools pip wheel httplib2 oauthlib
   ```

3. **Pin dependency versions more strictly:**
   - Current uses `>=` which can lead to breaking changes
   - Consider using `~=` for more conservative updates
   - Example: `fastapi~=0.109.0` (allows 0.109.x but not 0.110.0)

---

## 📋 Proposed Updated requirements.txt

### Immediate Security Fixes

```diff
 # Document Processing (PDF, DOCX)
 pymupdf>=1.23.0
 pdfplumber>=0.10.0
-camelot-py[cv]>=0.11.0
+camelot-py[cv]>=1.0.9  # Or use version with pypdf >= 6.4.0
 tabula-py>=2.9.0
 python-docx>=1.1.0
-PyPDF2>=3.0.0
+PyPDF2>=3.0.1
+pypdf>=6.4.0  # Explicitly require secure version
```

### Remove Redundant Dependencies

```diff
 # Data Handling and Utilities
 pandas>=2.1.0
 python-dotenv>=1.0.0
 structlog>=24.1.0
 tenacity>=8.2.0
 termcolor>=2.4.0
 pyyaml>=6.0.0
-fuzzywuzzy>=0.18.0
-python-Levenshtein>=0.23.0
+rapidfuzz>=3.0.0  # Already installed via transitive deps, make it explicit
 pydot>=2.0.0
 blake3>=0.4.1
 aiofiles>=23.2.0
```

### Move Dev Dependencies Out

Create `requirements-dev.txt`:
```txt
# Development and Testing
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-asyncio>=0.23.0
ruff>=0.1.0
mypy>=1.8.0
black>=24.0.0
```

Remove these from main `requirements.txt`.

---

## 💰 Estimated Savings

| Action | Disk Space | Install Time | Security Risk |
|--------|------------|--------------|---------------|
| Remove fuzzywuzzy + Levenshtein | ~50 MB | ~2-3s | None |
| Move dev deps to separate file | ~200 MB | ~10-15s | None |
| Fix pypdf vulnerabilities | 0 MB | 0s | **-4 CVEs** |
| Consolidate table extraction | ~500 MB | ~30s | Reduced attack surface |

**Total potential savings:** ~750 MB disk space, ~45s install time, -4 security vulnerabilities

---

## 🎯 Action Plan

### Week 1: Security (CRITICAL)
- [ ] Upgrade pypdf to >= 6.4.0
- [ ] Test all PDF processing functionality
- [ ] Upgrade cryptography and PyJWT
- [ ] Run security audit again to verify fixes

### Week 2: Cleanup (HIGH)
- [ ] Remove fuzzywuzzy and python-Levenshtein
- [ ] Update all imports to use rapidfuzz
- [ ] Test string matching functionality
- [ ] Create requirements-dev.txt
- [ ] Update CI/CD pipelines

### Week 3: Optimization (MEDIUM)
- [ ] Audit Flask vs FastAPI usage
- [ ] Create migration plan if feasible
- [ ] Evaluate table extraction library consolidation
- [ ] Consider creating optional extras

### Week 4: Maintenance (LOW)
- [ ] Update Python runtime to 3.12
- [ ] Update system packages
- [ ] Review and update pinning strategy
- [ ] Document dependency rationale

---

## 📚 Additional Resources

- [pypdf Security Advisories](https://github.com/py-pdf/pypdf/security/advisories)
- [Python Dependency Management Best Practices](https://packaging.python.org/guides/writing-pyproject-toml/)
- [FastAPI vs Flask Migration Guide](https://fastapi.tiangolo.com/alternatives/)
- [rapidfuzz Documentation](https://github.com/maxbachmann/RapidFuzz)

---

## 🔐 Security Scanning Commands

Run these regularly:

```bash
# Audit dependencies for vulnerabilities
pip-audit -r requirements.txt

# Check for outdated packages
pip list --outdated

# Check dependency tree
pipdeptree

# Check for security issues in code
bandit -r .

# Check for license compliance
pip-licenses
```

---

## Summary

The FARFAN_MPP project has a comprehensive but large dependency set justified by its ML/NLP capabilities. The main concerns are:

1. **CRITICAL:** 4 security vulnerabilities in pypdf (via camelot-py)
2. **HIGH:** Redundant string matching libraries (fuzzywuzzy, python-Levenshtein)
3. **MEDIUM:** Dual web framework setup (FastAPI + Flask)
4. **LOW:** Development dependencies in production requirements

Addressing these issues will improve security, reduce bloat, and streamline maintenance while preserving functionality.
