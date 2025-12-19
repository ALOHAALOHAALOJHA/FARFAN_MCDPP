# Phase 2 PR Merge Quick Reference

**For full details, see:** `PHASE2_MERGE_COORDINATION.md`

---

## Merge Order (DO NOT DEVIATE)

```
1. PR #341 (CANONICAL - merge first, resolve conflicts)
   ↓
2. PR #343 (JSON schemas - rebase → merge)
   ↓
3. PR #350 (Dura Lex fix - rebase → merge)
   ↓
4. Close: #340, #346, #348 (superseded by #341)
   ↓
5. PR #342 (naming - manual conflict review)
   ↓
6. PR #352 (architecture - manual duplication check)
   ↓
7. PR #354 (traceability - independent)
```

---

## Command Cheat Sheet

### Merge PR #341 (Resolve Conflicts First)
```bash
# Checkout PR #341
git fetch origin
git checkout copilot/update-router-specification-documentation

# Merge main and resolve conflicts
git merge main
# [Resolve conflicts in editor]

# Test
pytest -m "updated and not outdated" -v
ruff check farfan_core/
mypy farfan_core/farfan_core/core/

# Push and merge via GitHub UI
git push origin copilot/update-router-specification-documentation
```

### Rebase Complementary PRs (#343, #350)
```bash
# For PR #343
git checkout copilot/update-executor-config-schema
git rebase main
git push --force-with-lease origin copilot/update-executor-config-schema

# For PR #350
git checkout copilot/sub-pr-310-another-one
git rebase main
git push --force-with-lease origin copilot/sub-pr-310-another-one
```

### Close Superseded PRs (#340, #346, #348)
**Comment Template:**
```
Closing as superseded by #341. All functionality now in canonical Phase 2.

Reference: Phase 2 Merge Coordination Plan
See: PHASE2_MERGE_COORDINATION.md
```

---

## PR Status Reference

| PR | Status | Mergeable | Commits | Files | Action |
|----|--------|-----------|---------|-------|--------|
| #341 | Open | Dirty (conflicts) | 22 | 22 | **MERGE FIRST** |
| #343 | Open | Clean | 8 | 14 | Rebase → Merge |
| #350 | Draft | Clean | 2 | 17 | Rebase → Merge |
| #340 | Draft | Dirty | 2 | 5 | **CLOSE** |
| #346 | Draft | Dirty | 8 | 71 | **CLOSE** |
| #348 | Open | Dirty | 4 | 26 | **CLOSE** |
| #342 | Draft | Dirty | 10 | 83 | Manual Review |
| #352 | Draft | Dirty | 4 | 14 | Manual Review |
| #354 | Open | Unstable | 6 | 323 | Merge Last |

---

## Conflict Resolution Priority

1. **Always prefer #341's implementation** (it's canonical)
2. For naming conflicts (#342): Apply #342's naming to #341's files
3. For duplicates (#352): Keep #341 version, merge unique features
4. Document all resolutions in commit messages

---

## Test Commands

```bash
# Run Phase 2 tests
pytest -m "updated and not outdated" -v

# Lint
ruff check farfan_core/

# Type check
mypy farfan_core/farfan_core/core/

# Full test suite
pytest tests/
```

---

## Success Checklist (High Level)

- [ ] #341 merged (conflicts resolved)
- [ ] #343, #350 merged (rebased)
- [ ] #340, #346, #348 closed (comments added)
- [ ] #342, #352 merged (conflicts resolved)
- [ ] #354 merged (independent)
- [ ] All tests passing
- [ ] CI green

---

## Emergency Contacts

**Responsible:** @clasesuniversidadandina-max  
**Full Documentation:** PHASE2_MERGE_COORDINATION.md  
**Issue:** #[INSERT_NUMBER]

**When in doubt:**
1. Stop merging
2. Review PHASE2_MERGE_COORDINATION.md
3. Tag @clasesuniversidadandina-max
4. Do NOT merge out of order
