# Phase 2 Pull Request Merge Coordination Plan

**Version:** 1.0.0  
**Effective Date:** 2025-12-19  
**Status:** ACTIVE  
**Responsible:** @clasesuniversidadandina-max  
**Labels:** phase2, coordination

---

## Executive Summary

This document establishes the strategic order for merging all active Phase 2 pull requests to prevent semantic or CI-level conflicts. **PR #341 is the canonical implementation** and serves as the baseline for all related work, rebases, and closures.

---

## Critical Merge Discipline Rules

1. **NO Phase 2 PR in this set may be merged before PR #341**
2. PR #341 must be merged with conflicts resolved first
3. All subordinate PRs must add `Depends on #341` in their PR body
4. Rebase onto main before merging subordinate or complementary PRs
5. Manual conflict review required for PRs #342 and #352 after #341 merge
6. CI/reviewers block merges that violate this order

---

## Merge Sequence Overview

```
Phase 1: CANONICAL BASELINE
├── PR #341 (MERGE FIRST - resolve conflicts)
│
Phase 2: COMPLEMENTARY (after #341)
├── PR #343 (JSON Schema) - rebase → merge
├── PR #350 (Dura Lex fix) - rebase → merge
│
Phase 3: SUPERSEDED (close)
├── PR #340 (constants) - CLOSE
├── PR #346 (cardinality) - CLOSE
├── PR #348 (certificates) - CLOSE
│
Phase 4: MANUAL REVIEW (after #341)
├── PR #342 (naming) - manual conflict resolution required
├── PR #352 (architecture) - manual duplication check required
│
Phase 5: INDEPENDENT
└── PR #354 (traceability) - merge after #341
```

---

## Detailed PR Analysis

### PRIORITY 1: Canonical Baseline

#### PR #341 - Phase 2 Canonical Implementation
**Status:** Open, mergeable_state="dirty" (HAS CONFLICTS)  
**Commits:** 22  
**Changes:** +5552 additions, 22 files changed  
**Branch:** `copilot/update-router-specification-documentation`

**Contains:**
- Phase 2a: ArgRouter (protocol-based exhaustive dispatch)
- Phase 2b: Carver (60→300 transformation with provenance)
- Phase 2c: Nexus Integration (300 micro-answers to evidence graph)
- Phase 2.1: IrrigationOrchestrator (question→chunk→task coordination)
- Phase 2.2: TaskExecutor (300-task execution with MethodRegistry)
- SignalRegistry enforcement (REQUIRED initialization)
- Batch contract loader (all 300 specialized contracts)

**Blockers:**
- Merge conflicts with main branch

**Actions Required:**
1. ✅ Checkout branch: `git checkout copilot/update-router-specification-documentation`
2. ✅ Resolve conflicts: `git merge main` → fix conflicts
3. ✅ Run tests: `pytest -m "updated and not outdated" -v`
4. ✅ Merge to main
5. ✅ Verify CI passes

**Why This PR is Canonical:**
- Production-ready with operational MethodRegistry integration
- Sequential pipeline validated (no parallel routes)
- All code review issues resolved
- SignalRegistry initialization enforced
- Complete 60→300 cardinality pipeline
- Comprehensive stability validation completed

---

### PRIORITY 2: Complementary PRs (Merge After #341)

#### PR #343 - JSON Schema Specifications
**Status:** Open, mergeable_state="clean"  
**Commits:** 8  
**Changes:** +2010 additions, 14 files changed  
**Branch:** `copilot/update-executor-config-schema`

**Contains:**
- ExecutorConfig schema (determinism, resource limits, contracts)
- ExecutorOutput schema (provenance, SHA-256 hashing)
- SynchronizationManifest schema (SISAS 60→300 mapping)
- CalibrationPolicy schema (quality thresholds, action bands)

**Dependencies:**
- Depends on #341 (schemas validate #341 data structures)

**Actions Required:**
1. ⏳ Add to PR body: `Depends on #341`
2. ⏳ After #341 merged: `git rebase main`
3. ⏳ Merge to main
4. ⏳ Verify schema validation works with #341 structures

---

#### PR #350 - Dura Lex Certificate Import Error Fix
**Status:** Draft, mergeable_state="clean"  
**Commits:** 2  
**Changes:** +193 additions / -186 deletions, 17 files changed  
**Branch:** `copilot/sub-pr-310-another-one`

**Contains:**
- Certificate status fixes for import errors
- Test script logic corrections (set `passed = False` on errors)
- Certificate schema updates for failed tests

**Dependencies:**
- Depends on #341 (certificate system infrastructure)

**Actions Required:**
1. ⏳ Add to PR body: `Depends on #341`
2. ⏳ After #341 merged: `git rebase main`
3. ⏳ Merge to main
4. ⏳ Verify certificates now correctly report failures

---

### PRIORITY 3: Superseded PRs (Close with Comments)

#### PR #340 - Phase 2 Constants Validation
**Status:** Draft, mergeable_state="dirty"  
**Commits:** 2  
**Changes:** +206 additions, 5 files changed  
**Branch:** `copilot/implement-constants-validation-test`

**Reason for Closure:**
- Constants validation now included in #341
- Test suite redundant with #341's validation

**Closure Comment Template:**
```
Closing as superseded by #341. All functionality now in canonical Phase 2.

- Constants module: Included in #341's Phase 2.1 and 2.2
- Validation tests: Covered by #341's test suite
- Cardinality invariants: Enforced in #341

Reference: Phase 2 Merge Coordination Plan
See: PHASE2_MERGE_COORDINATION.md
```

**Actions Required:**
1. ⏳ Add closure comment to PR #340
2. ⏳ Close PR #340
3. ⏳ Link to #341 for traceability

---

#### PR #346 - 60→300 Cardinality Enforcement
**Status:** Draft, mergeable_state="dirty"  
**Commits:** 8  
**Changes:** +2440 additions, 71 files changed  
**Branch:** `copilot/create-canonical-folder-structure`

**Reason for Closure:**
- Full cardinality enforcement in #341
- Structure creation redundant with #341

**Closure Comment Template:**
```
Closing as superseded by #341. All functionality now in canonical Phase 2.

- Cardinality enforcement: Complete in #341 (60→300 pipeline)
- Canonical structure: Established in #341
- Carver implementation: Production-ready in #341

Reference: Phase 2 Merge Coordination Plan
See: PHASE2_MERGE_COORDINATION.md
```

**Actions Required:**
1. ⏳ Add closure comment to PR #346
2. ⏳ Close PR #346
3. ⏳ Link to #341 for traceability

---

#### PR #348 - Certificate System Infrastructure
**Status:** Open, mergeable_state="dirty"  
**Commits:** 4  
**Changes:** +1436 additions, 26 files changed  
**Branch:** `copilot/add-certificates-presence-test`

**Reason for Closure:**
- Certificate system fully implemented in #341
- 15 certificates already validated in #341

**Closure Comment Template:**
```
Closing as superseded by #341. All functionality now in canonical Phase 2.

- Certificate system: Complete in #341
- 15 certificates: All present and validated in #341
- Test suite: Covered by #341's validation

Reference: Phase 2 Merge Coordination Plan
See: PHASE2_MERGE_COORDINATION.md
```

**Actions Required:**
1. ⏳ Add closure comment to PR #348
2. ⏳ Close PR #348
3. ⏳ Link to #341 for traceability

---

### PRIORITY 4: Manual Conflict Review Required

#### PR #342 - Naming Conventions Enforcement
**Status:** Draft, mergeable_state="dirty" (HIGH CONFLICT RISK)  
**Commits:** 10  
**Changes:** +2217 additions / -70 deletions, **83 files changed**  
**Branch:** `copilot/enforce-naming-conventions`

**Contains:**
- Complete naming convention migration (48 files renamed)
- Zero legacy exemptions (strict enforcement)
- Import path updates across 28 files
- Phase_two, schema, and certificate file renames

**Conflict Risk:**
⚠️ **HIGH** - Widespread file renames across codebase

**Dependencies:**
- Depends on #341
- Requires manual conflict review after #341 merge

**Actions Required:**
1. ⏳ Add to PR body: `Depends on #341 - Manual conflict review required`
2. ⏳ After #341 merged: Review all renamed files for conflicts
3. ⏳ Create conflict resolution matrix:
   ```
   Original Path → New Path → Conflicts with #341?
   arg_router.py → phase2_a_arg_router.py → Check
   carver.py → phase2_f_carver.py → Check
   [... continue for all 48 files]
   ```
4. ⏳ Resolve conflicts manually
5. ⏳ Update all import statements
6. ⏳ Run full test suite
7. ⏳ Merge after validation

**Special Considerations:**
- This PR renames core Phase 2 files that #341 also creates/modifies
- Must ensure naming conventions don't break #341's functionality
- May require selective merge or staged approach

---

#### PR #352 - Architecture Migration
**Status:** Draft, mergeable_state="dirty" (DUPLICATION RISK)  
**Commits:** 4  
**Changes:** +6228 additions / -577 deletions, 14 files changed  
**Branch:** `copilot/sub-pr-310-one-more-time`

**Contains:**
- 10 files migrated from orchestration/ to Phase_two/
- New file: calibration_policy.py
- README documentation (655 lines)
- Module manifest (30 files total in Phase_two/)

**Duplication Risk:**
⚠️ **MEDIUM-HIGH** - May duplicate files from #341

**Files to Check for Duplication:**
- task_planner.py (SENSITIVE)
- class_registry.py
- method_registry.py
- calibration_policy.py (NEW - check if #341 has equivalent)

**Dependencies:**
- Depends on #341
- Must not duplicate #341 functionality

**Actions Required:**
1. ⏳ Add to PR body: `Depends on #341 - Duplication check required`
2. ⏳ After #341 merged: Create duplication matrix:
   ```
   PR #352 File → Exists in #341? → Action
   task_planner.py → Check → Merge/Skip/Consolidate
   class_registry.py → Check → Merge/Skip/Consolidate
   method_registry.py → Check → Merge/Skip/Consolidate
   [... continue for all 10 files]
   ```
3. ⏳ For duplicates: Choose #341 version or consolidate
4. ⏳ For unique files: Merge normally
5. ⏳ Update README if needed
6. ⏳ Run full test suite
7. ⏳ Merge after validation

**Special Considerations:**
- README documentation may complement #341
- Calibration_policy.py may be unique to #352
- Review for architectural consistency with #341

---

### PRIORITY 5: Independent Track

#### PR #354 - Traceability Repair
**Status:** Open, mergeable_state="unstable"  
**Commits:** 6  
**Changes:** +631K additions / -542K deletions, **323 files changed**  
**Branch:** `traceability-json-path-repair-2025-12-19`

**Contains:**
- Contract field alignment
- Calibration logic improvements
- Schema validation broadening
- Score normalization

**Dependencies:**
- Independent from #341
- Merge after #341 (best practice)

**Actions Required:**
1. ⏳ Add to PR body: `Depends on #341` (for ordering only)
2. ⏳ After #341 merged: Rebase if needed
3. ⏳ Merge to main
4. ⏳ Verify traceability repairs don't conflict with #341

**Special Considerations:**
- Extremely large changeset (631K additions)
- Independent functionality (traceability repair)
- Should not conflict with #341 but merge after for safety

---

## Execution Checklist

### Phase 1: Prepare Canonical Baseline
- [ ] Review PR #341 current conflicts
- [ ] Identify all conflicting files
- [ ] Create conflict resolution strategy
- [ ] Checkout PR #341 branch locally
- [ ] Merge main into PR #341 branch
- [ ] Resolve all conflicts
- [ ] Run full test suite: `pytest -m "updated and not outdated" -v`
- [ ] Verify linting: `ruff check farfan_core/`
- [ ] Verify type checking: `mypy farfan_core/farfan_core/core/`
- [ ] Push resolved conflicts
- [ ] Merge PR #341 to main
- [ ] Verify CI passes on main

### Phase 2: Update Complementary PRs
- [ ] Update PR #343 body with `Depends on #341`
- [ ] Update PR #350 body with `Depends on #341`
- [ ] Rebase PR #343 onto updated main
- [ ] Rebase PR #350 onto updated main
- [ ] Run tests for PR #343
- [ ] Run tests for PR #350
- [ ] Merge PR #343
- [ ] Merge PR #350
- [ ] Verify CI passes

### Phase 3: Close Superseded PRs
- [ ] Add closure comment to PR #340 (use template above)
- [ ] Close PR #340
- [ ] Add closure comment to PR #346 (use template above)
- [ ] Close PR #346
- [ ] Add closure comment to PR #348 (use template above)
- [ ] Close PR #348
- [ ] Update issue tracker with closure references

### Phase 4: Manual Conflict Resolution
- [ ] Update PR #342 body with `Depends on #341 - Manual conflict review required`
- [ ] Create file rename conflict matrix for PR #342
- [ ] Review all 48 renamed files against #341 changes
- [ ] Resolve naming conflicts
- [ ] Update all import statements
- [ ] Run full test suite for PR #342
- [ ] Merge PR #342 after validation
- [ ] Update PR #352 body with `Depends on #341 - Duplication check required`
- [ ] Create file duplication matrix for PR #352
- [ ] Review all 10 migrated files against #341
- [ ] Consolidate or skip duplicates
- [ ] Merge unique files from PR #352
- [ ] Run full test suite for PR #352
- [ ] Merge PR #352 after validation
- [ ] Verify CI passes

### Phase 5: Independent Track
- [ ] Update PR #354 body with `Depends on #341`
- [ ] Rebase PR #354 if needed
- [ ] Run tests for PR #354
- [ ] Merge PR #354
- [ ] Verify CI passes

### Phase 6: Final Validation
- [ ] Run full Phase 2 test suite on main
- [ ] Verify all 300 contracts load correctly
- [ ] Verify SignalRegistry initialization
- [ ] Verify 60→300 cardinality pipeline
- [ ] Verify MethodRegistry integration
- [ ] Run integration tests
- [ ] Verify zero legacy artifacts remain
- [ ] Update Phase 2 documentation
- [ ] Close this coordination issue

---

## CI Enforcement Instructions

For reviewers and CI systems:

1. **Block any PR merge that violates the priority order**
2. **Verify "Depends on #341" in PR body for all subordinate PRs**
3. **Require manual approval for PRs #342 and #352 (conflict/duplication risk)**
4. **Check that superseded PRs (#340, #346, #348) are closed before merging others**
5. **Attach this document in review comments when clarifying merge order**

---

## Conflict Resolution Guidelines

### For PR #341 (Initial Conflicts)
1. Identify conflicting files with: `git diff --name-only main...HEAD`
2. For each conflict:
   - Understand the change in main
   - Understand the change in #341
   - Preserve #341's canonical implementation
   - Merge complementary changes from main
3. Test thoroughly after resolution
4. Commit with message: `Resolve merge conflicts with main - preserve canonical Phase 2 implementation`

### For PR #342 (Naming Conflicts)
1. Create mapping: `old_name → new_name → conflicts_with_#341?`
2. For conflicts:
   - Use #341's file if it's canonical
   - Apply #342's naming convention to #341's file
   - Update all imports in both PRs' changed files
3. Prefer #341's implementation with #342's naming

### For PR #352 (Duplication Conflicts)
1. Create mapping: `#352_file → exists_in_#341? → action`
2. For duplicates:
   - Keep #341 version (canonical)
   - Merge unique features from #352 if beneficial
   - Skip #352 file if fully redundant
3. For unique files:
   - Merge normally
   - Verify integration with #341

---

## Success Criteria

### Merge Completion
- ✅ PR #341 merged with all conflicts resolved
- ✅ PRs #343, #350 merged after #341
- ✅ PRs #340, #346, #348 closed with traceability
- ✅ PRs #342, #352 merged after manual review
- ✅ PR #354 merged independently

### Functional Validation
- ✅ All Phase 2 tests passing
- ✅ 300 contracts loading correctly
- ✅ SignalRegistry initialization working
- ✅ 60→300 cardinality pipeline operational
- ✅ MethodRegistry integration functional
- ✅ Naming conventions enforced
- ✅ Zero legacy artifacts
- ✅ CI green on main

### Documentation
- ✅ All PRs have proper traceability comments
- ✅ Merge history documented
- ✅ Conflict resolutions recorded
- ✅ Phase 2 documentation updated

---

## Why This Plan Exists

**Context:**
Multiple Phase 2 PRs were developed in parallel, creating potential conflicts. PR #341 emerged as the canonical, production-ready implementation with:
- Complete architecture (router, carver, nexus, orchestration, execution)
- Full 60→300 cardinality pipeline
- SignalRegistry enforcement
- MethodRegistry integration
- Batch contract loader
- Comprehensive validation

**Problem:**
Merging in arbitrary order would cause:
- Semantic conflicts (duplicate implementations)
- CI failures (incompatible changes)
- Legacy artifact proliferation
- Lost work (superseded PRs merged unnecessarily)

**Solution:**
This coordination plan ensures:
- Deterministic merge order
- Conflict resolution before merge
- Traceability for all decisions
- Zero legacy artifacts
- Production-ready Phase 2

---

## Contact & Escalation

**Responsible:** @clasesuniversidadandina-max  
**Labels:** phase2, coordination  
**Issue Reference:** #[INSERT_ISSUE_NUMBER]

For questions or conflicts during execution:
1. Reference this document
2. Tag @clasesuniversidadandina-max in PR comments
3. Link to specific section of this plan
4. Propose resolution following guidelines above

---

**Document Status:** ACTIVE  
**Last Updated:** 2025-12-19  
**Version:** 1.0.0
