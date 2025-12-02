# QUESTIONNAIRE ACCESS CONTROL & ENFORCEMENT

**Date**: 2025-12-02  
**Status**: 🔒 ENFORCED  
**Canonical Module**: `src/farfan_pipeline/core/orchestrator/questionnaire.py`

---

## 🎯 SECURITY CONTRACT

### Access Rules:

```
✓ ALLOWED:
  - Factory (via questionnaire.py)
  - Orchestrator (via questionnaire.py)
  - Signals (via questionnaire.py)

✗ FORBIDDEN:
  - analysis/* (MUST NOT access directly)
  - processing/* (MUST NOT access directly)
  - Any direct file.open() of questionnaire_monolith.json
```

---

## 📐 ARCHITECTURE

```
questionnaire_monolith.json (FILE - 67,261 lines)
        ↓
        ↓ [SINGLE ENTRY POINT]
        ↓
questionnaire.py::load_questionnaire()
        ↓
CanonicalQuestionnaire (SINGLETON)
        ↓
        ├─→ Factory
        ├─→ Orchestrator
        └─→ Signals
            ↓
            [All other modules use these interfaces]
```

---

## 🔒 CANONICAL ACCESS MODULE

**File**: `src/farfan_pipeline/core/orchestrator/questionnaire.py`

### Key Components:

#### 1. **Canonical Paths**
```python
QUESTIONNAIRE_FILE: Final[Path] = (
    PROJECT_ROOT / "system" / "config" / "questionnaire" / "questionnaire_monolith.json"
)

QUESTIONNAIRE_SCHEMA: Final[Path] = (
    PROJECT_ROOT / "system" / "config" / "questionnaire" / "questionnaire_schema.json"
)
```

#### 2. **CanonicalQuestionnaire Class**
- **Singleton pattern**: Load once, use everywhere
- **Immutable**: Once loaded, data cannot be changed
- **Integrity verified**: SHA-256 hash checked on load
- **Schema validated**: Conforms to questionnaire_schema.json

#### 3. **Access Methods** (PUBLIC API):
```python
# High-level access
questionnaire.get_macro_question() → Dict
questionnaire.get_meso_questions() → List[Dict]
questionnaire.get_micro_questions() → List[Dict]

# Filtered access
questionnaire.get_micro_question_by_id(question_id) → Dict
questionnaire.get_questions_by_cluster(cluster_id) → List[Dict]
questionnaire.get_questions_by_policy_area(policy_area_id) → List[Dict]

# Metadata
questionnaire.get_abstraction_levels() → Dict
questionnaire.get_scoring_system() → Dict
questionnaire.get_semantic_layers() → Dict

# Integrity
questionnaire.verify_integrity() → bool
```

#### 4. **Loader Function** (SINGLE SOURCE OF TRUTH):
```python
def load_questionnaire(
    force_reload: bool = False,
    validate_schema: bool = True
) -> CanonicalQuestionnaire:
    """
    ONLY function allowed to read questionnaire_monolith.json.
    Implements singleton pattern.
    """
```

---

## ✅ CORRECT USAGE

### In Factory:
```python
from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire

def build_orchestrator():
    questionnaire = load_questionnaire()
    # Use questionnaire.get_*() methods
    return Orchestrator(questionnaire=questionnaire)
```

### In Orchestrator:
```python
class Orchestrator:
    def __init__(self, questionnaire: CanonicalQuestionnaire):
        self._questionnaire = questionnaire
        self._micro_questions = questionnaire.get_micro_questions()
```

### In Signals:
```python
from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire

def build_signal_pack(policy_area: str):
    questionnaire = load_questionnaire()
    questions = questionnaire.get_questions_by_policy_area(policy_area)
    # Process questions...
```

---

## ❌ VIOLATIONS DETECTED

### Current Violations (6 files):

#### 1. `src/farfan_pipeline/analysis/Analyzer_one.py` (2 violations)
```python
# Line 1067
self.questionnaire_path = Path(questionnaire_path)  # ✗ VIOLATION

# Line 1346
questionnaire_file = Path(questionnaire_path)  # ✗ VIOLATION
```

**Fix**:
```python
from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire

class Analyzer:
    def __init__(self):
        self._questionnaire = load_questionnaire()
        # Use self._questionnaire.get_*() methods
```

#### 2. `src/farfan_pipeline/analysis/micro_prompts.py` (1 violation)
```python
# Line 52
# Comment references questionnaire_monolith.json  # ✗ DOCUMENTATION VIOLATION
```

**Fix**: Update documentation to reference canonical module.

#### 3. `src/farfan_pipeline/processing/policy_processor.py` (1 violation)
```python
# Line 1659
questionnaire_path = Path(args.questionnaire) if args.questionnaire else None  # ✗ VIOLATION
```

**Fix**:
```python
from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire

def process_policy(args):
    questionnaire = load_questionnaire()
    # Remove args.questionnaire parameter
```

#### 4. `src/farfan_pipeline/audit/audit_system.py` (2 violations)
```python
# Line 532
with open(questionnaire_path, encoding='utf-8') as f:  # ✗ VIOLATION
    data = json.load(f)
```

**Fix**:
```python
from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire

def audit_questionnaire():
    questionnaire = load_questionnaire()
    data = questionnaire.data  # Read-only access
```

---

## 🛠️ ENFORCEMENT STRATEGY

### Phase 1: Create Canonical Module ✅ DONE
- [x] Create `questionnaire.py` with access control
- [x] Implement singleton pattern
- [x] Add integrity verification
- [x] Add schema validation

### Phase 2: Create JSON Schema ✅ DONE
- [x] Create `questionnaire_schema.json`
- [x] Define all required fields
- [x] Add validation rules
- [x] Document structure

### Phase 3: Fix Violations (TODO)
- [ ] Update `Analyzer_one.py` (2 violations)
- [ ] Update `micro_prompts.py` (1 violation)
- [ ] Update `policy_processor.py` (1 violation)
- [ ] Update `audit_system.py` (2 violations)

### Phase 4: Add Linting Rules (TODO)
- [ ] Add ruff rule to detect direct file access
- [ ] Add pre-commit hook
- [ ] Add CI check for violations

---

## 🔍 DETECTION RULES

### Ruff / flake8 Custom Rule:
```python
# .flake8 or pyproject.toml
[flake8]
custom-rules = [
    "questionnaire_access",
]

# Detect:
# - open("*questionnaire*")
# - with open(*questionnaire*)
# - Path(*questionnaire*).open()
# - json.load(*questionnaire*)
```

### Git Pre-commit Hook:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for direct questionnaire access
if git diff --cached | grep -E "(open|Path).*questionnaire_monolith"; then
    echo "❌ ERROR: Direct questionnaire access detected"
    echo "Use: from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire"
    exit 1
fi
```

---

## 📊 VALIDATION CHECKLIST

### On Load:
- [x] File exists at canonical location
- [x] Valid JSON structure
- [x] Has required top-level keys
- [x] Has all 6 blocks
- [x] Micro questions have required fields
- [x] SHA-256 hash computed
- [x] Line count recorded

### On Access:
- [x] Singleton enforced (only one instance)
- [x] Data is immutable
- [x] Access methods return copies
- [x] Integrity can be verified

---

## 🎯 BENEFITS

### Security:
- ✅ Single point of access control
- ✅ No direct file manipulation
- ✅ Integrity verification
- ✅ Audit trail possible

### Performance:
- ✅ Load once, use everywhere (singleton)
- ✅ In-memory caching
- ✅ Fast filtered access

### Maintainability:
- ✅ Change file location in ONE place
- ✅ Add access logging in ONE place
- ✅ Upgrade schema in ONE place
- ✅ Clear API for consumers

### Testing:
- ✅ Easy to mock questionnaire
- ✅ Can inject test data
- ✅ No file system dependencies in tests

---

## 📝 API DOCUMENTATION

### `load_questionnaire(force_reload=False, validate_schema=True) -> CanonicalQuestionnaire`

Load questionnaire from canonical location (singleton pattern).

**Parameters:**
- `force_reload` (bool): Bypass cache and reload from disk
- `validate_schema` (bool): Validate against JSON Schema

**Returns:**
- `CanonicalQuestionnaire`: Singleton instance

**Raises:**
- `FileNotFoundError`: If file not found
- `json.JSONDecodeError`: If invalid JSON
- `ValueError`: If schema validation fails

**Example:**
```python
from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire

# First call loads from disk
q1 = load_questionnaire()

# Second call returns cached instance
q2 = load_questionnaire()

assert q1 is q2  # Same instance
```

### `CanonicalQuestionnaire` Methods:

#### Data Access:
- `get_macro_question() -> Dict[str, Any]`
- `get_meso_questions() -> List[Dict[str, Any]]`
- `get_micro_questions() -> List[Dict[str, Any]]`

#### Filtered Access:
- `get_micro_question_by_id(question_id: str) -> Dict | None`
- `get_questions_by_cluster(cluster_id: str) -> List[Dict]`
- `get_questions_by_policy_area(policy_area_id: str) -> List[Dict]`

#### Metadata:
- `get_abstraction_levels() -> Dict[str, Any]`
- `get_scoring_system() -> Dict[str, Any]`
- `get_semantic_layers() -> Dict[str, Any]`

#### Integrity:
- `verify_integrity() -> bool`

#### Properties:
- `data: Dict[str, Any]` - Raw data (read-only)
- `metadata: QuestionnaireMetadata` - File metadata
- `schema_version: str` - Schema version
- `version: str` - Monolith version

---

## 🚀 MIGRATION GUIDE

### For Module Authors:

#### Before (WRONG):
```python
import json
from pathlib import Path

questionnaire_path = Path("config/json_files_no_schemas/questionnaire_monolith.json")
with open(questionnaire_path) as f:
    data = json.load(f)

micro_questions = data['blocks']['micro_questions']
```

#### After (CORRECT):
```python
from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire

questionnaire = load_questionnaire()
micro_questions = questionnaire.get_micro_questions()
```

### Benefits:
- ✅ No path hardcoding
- ✅ Automatic caching
- ✅ Integrity verification
- ✅ Schema validation
- ✅ Type safety

---

## 📈 NEXT STEPS

1. **Fix 6 violations** in analysis, processing, and audit modules
2. **Add linting rules** to detect future violations
3. **Update documentation** to reference canonical module
4. **Add tests** for access control
5. **Add monitoring** to log questionnaire access
6. **Consider RBAC** for different user roles

---

**Status**: 🔒 INFRASTRUCTURE READY  
**Violations**: ⚠️ 6 TO FIX  
**Priority**: HIGH (security & architecture)  
**Estimated Time**: 2-3 hours

