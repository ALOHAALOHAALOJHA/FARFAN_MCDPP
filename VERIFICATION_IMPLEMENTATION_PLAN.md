# Path/Import Verification Implementation Plan

## Status: AWAITING USER APPROVAL

## Objective
Extend the existing verification manifest system with path and import policy enforcement.
NO deletions, NO moves, only additions and targeted edits to integrate policy verification.

## Current State Analysis

### Existing Files (DO NOT DELETE)
- ✅ `farfan_core/farfan_core/core/orchestrator/verification_manifest.py` - VerificationManifestBuilder class
- ✅ `farfan_core/farfan_core/entrypoint/main.py` - VerifiedPipelineRunner class  
- ✅ `artifacts/test_suite_run/verification_manifest.json` - Real manifest (success: false)
- ✅ Package structure: `farfan_core/farfan_core/` (Canonical Location: farfan_core/farfan_core)
- ✅ Existing observability: `farfan_core/farfan_core/observability/` (currently has 3 items)

### Files to CREATE (Step by Step)

1. `farfan_core/farfan_core/observability/path_import_policy.py` - Policy dataclasses
2. `farfan_core/farfan_core/observability/policy_builder.py` - Build policies from repo state
3. `farfan_core/farfan_core/observability/import_scanner.py` - AST-based static analysis
4. `farfan_core/farfan_core/observability/path_guard.py` - Runtime path/import hooks

### Files to EDIT (Minimal Changes Only)

1. `farfan_core/farfan_core/core/orchestrator/verification_manifest.py`
   - Add method to VerificationManifestBuilder: `set_path_import_verification(report: PolicyReport)`
   
2. `farfan_core/farfan_core/entrypoint/main.py`
   - In `generate_verification_manifest()`: Add path_import_verification section to manifest
   - In `run()`: Wrap pipeline execution with path/import verification

## Implementation Sequence

### Step 1: Define Policy Contracts (New File)
**File**: `farfan_core/farfan_core/observability/path_import_policy.py`
**Purpose**: Type-safe policy definitions
**Contents**:
- `@dataclass PolicyViolation` (kind, message, file, line, operation, target)
- `@dataclass PolicyReport` (static violations, dynamic violations, path violations, sys_path violations)
- `@dataclass ImportPolicy` (allowed internal/third-party/dynamic, stdlib modules)
- `@dataclass PathPolicy` (repo_root, allowed read/write/external prefixes)
- Helper: `merge_policy_reports()`

### Step 2: Build Policies from Repo (New File)
**File**: `farfan_core/farfan_core/observability/policy_builder.py`
**Purpose**: Generate policies from actual repo state
**Contents**:
- `compute_repo_root() -> Path` - Find PROJECT_ROOT
- `build_import_policy(repo_root: Path) -> ImportPolicy`
  - allowed_internal: ["farfan_core"]
  - allowed_third_party: Read from requirements.txt + sys.stdlib_module_names
  - allowed_dynamic: [] (empty for now)
- `build_path_policy(repo_root: Path) -> PathPolicy`
  - allowed_write: [repo_root / "artifacts"]
  - allowed_read: [repo_root]
  - allowed_external: [tempfile paths, site-packages]

### Step 3: Static Import Scanner (New File)
**File**: `farfan_core/farfan_core/observability/import_scanner.py`
**Purpose**: AST-based import validation
**Contents**:
- `validate_imports(roots: Iterable[Path], policy: ImportPolicy) -> PolicyReport`
  - Parse all .py files with ast.parse
  - Extract Import/ImportFrom nodes
  - Validate against policy rules
  - Return PolicyReport with violations

### Step 4: Runtime Path Guard (New File)
**File**: `farfan_core/farfan_core/observability/path_guard.py`
**Purpose**: Runtime path/import interception
**Contents**:
- `@contextmanager guard_paths_and_imports(path_policy, import_policy, report)`
  - Patch builtins.open, os.*, pathlib.Path.*
  - Install sys.meta_path import hook
  - Validate paths against policy on access
  - Add violations to report
  - ALWAYS restore original state

### Step 5: Extend Manifest Builder (Edit Existing)
**File**: `farfan_core/farfan_core/core/orchestrator/verification_manifest.py`
**Changes**:
- Add method to VerificationManifestBuilder:
```python
def set_path_import_verification(self, report: PolicyReport):
    self.manifest_data["path_import_verification"] = {
        "success": report.ok(),
        "static_import_violations": [asdict(v) for v in report.static_import_violations],
        "dynamic_import_violations": [asdict(v) for v in report.dynamic_import_violations],
        "path_violations": [asdict(v) for v in report.path_violations],
        "sys_path_violations": [asdict(v) for v in report.sys_path_violations]
    }
    return self
```

### Step 6: Integrate into Runner (Edit Existing)
**File**: `farfan_core/farfan_core/entrypoint/main.py`
**Changes**:

A. In `__init__()` method (around line 102):
```python
from farfan_core.observability.policy_builder import (
    compute_repo_root, build_import_policy, build_path_policy
)

self.repo_root = compute_repo_root()
self.import_policy = build_import_policy(self.repo_root)
self.path_policy = build_path_policy(self.repo_root)
self.path_import_report = None
```

B. In `run()` method (around line 379):
```python
# Before pipeline execution:
from farfan_core.observability.import_scanner import validate_imports
from farfan_core.observability.path_guard import guard_paths_and_imports
from farfan_core.observability.path_import_policy import PolicyReport, merge_policy_reports

# Static analysis
static_report = validate_imports(
    roots=[
        self.repo_root / "farfan_core" / "farfan_core" / "core",
        self.repo_root / "farfan_core" / "farfan_core" / "entrypoint",
    ],
    import_policy=self.import_policy
)

# Dynamic analysis
dynamic_report = PolicyReport()
with guard_paths_and_imports(self.path_policy, self.import_policy, dynamic_report):
    # Existing pipeline execution stays here
    ...

# Merge reports
self.path_import_report = merge_policy_reports([static_report, dynamic_report])
```

C. In `generate_verification_manifest()` method (around line 1004):
```python
# After setting other manifest fields, before building:
if self.path_import_report:
    builder.set_path_import_verification(self.path_import_report)
    
# Update success calculation (around line 1070):
if self.path_import_report and not self.path_import_report.ok():
    success = False
```

## Verification Criteria

### Before declaring success:
1. ✅ `farfan_core/farfan_core/observability/path_import_policy.py` exists
2. ✅ `farfan_core/farfan_core/observability/policy_builder.py` exists
3. ✅ `farfan_core/farfan_core/observability/import_scanner.py` exists
4. ✅ `farfan_core/farfan_core/observability/path_guard.py` exists
5. ✅ Manifest builder has `set_path_import_verification()` method
6. ✅ Runner integrates verification in `run()` method
7. ✅ Generated manifest contains `path_import_verification` section
8. ✅ `success` field correctly reflects policy violations
9. ✅ NO files deleted
10. ✅ NO directory structure changes

## Safety Guarantees

- ❌ NO file deletions
- ❌ NO file moves  
- ❌ NO renaming of existing modules
- ✅ ONLY new files in `farfan_core/farfan_core/observability/`
- ✅ ONLY minimal edits to 2 existing files (manifest builder + runner)
- ✅ All changes are additive/integrative

## Questions for You

1. Should I proceed with this plan?
2. Any modifications needed before I start?
3. Do you want me to implement step-by-step with approval at each stage, or all at once?
