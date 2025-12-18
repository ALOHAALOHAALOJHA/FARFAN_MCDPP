# Naming Convention Enforcement - Quick Reference

## Summary

Implements **Section 3: NAMING CONVENTION ENFORCEMENT (STABILIZATION PHASE)** for F.A.R.F.A.N Phase 2.

## Status

✅ **IMPLEMENTED** - All 5 naming rules enforced with CI integration

## Quick Commands

```bash
# Validate naming conventions (with legacy exemptions)
python scripts/validate_naming_conventions.py

# Strict mode (show all violations)
python scripts/validate_naming_conventions.py --strict

# Validate file headers
python scripts/validate_file_headers.py --report-only

# Run tests
python -m pytest tests/test_naming_conventions.py -v
```

## Naming Rules (5 Rules)

| Rule | Pattern | Location | Example |
|------|---------|----------|---------|
| 3.1.1 | `phase2_[a-z]_[a-z0-9_]+.py` | Phase root | `phase2_a_arg_router.py` |
| 3.1.2 | `[a-z][a-z0-9_]*.py` | Packages | `base_executor.py` |
| 3.1.3 | `[a-z][a-z0-9_]*.schema.json` | Schemas | `config.schema.json` |
| 3.1.4 | `CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*.md` | Certificates | `CERTIFICATE_01_NAME.md` |
| 3.1.5 | `test_phase2_[a-z0-9_]+.py` | Tests | `test_phase2_carver.py` |

## Legacy Files

- **33 files** exempt from rules (see `.naming_exemptions`)
- New files MUST comply
- Migration plan documented in `docs/NAMING_CONVENTIONS.md`

## CI Enforcement

- GitHub workflow: `.github/workflows/naming-conventions.yml`
- Runs on every PR
- Blocks PRs with new violations
- Allows legacy files via exemptions

## Files Created

1. **`scripts/validate_naming_conventions.py`** - Main validator
2. **`scripts/validate_file_headers.py`** - Header validator
3. **`.naming_exemptions`** - Legacy file list (33 files)
4. **`.github/workflows/naming-conventions.yml`** - CI workflow
5. **`docs/NAMING_CONVENTIONS.md`** - Full documentation
6. **`docs/PHASE2_FILE_TEMPLATE.py`** - Template for new files
7. **`tests/test_naming_conventions.py`** - Test suite (14 tests)

## Test Results

```
14 tests, 14 passed, 0 failed
Coverage: All naming rules validated
Status: ✅ PASSING
```

## Documentation

- **Full Guide**: `docs/NAMING_CONVENTIONS.md`
- **Template**: `docs/PHASE2_FILE_TEMPLATE.py`
- **This File**: Quick reference for developers

## For Developers

### Creating New Phase 2 Files

1. Use template: `docs/PHASE2_FILE_TEMPLATE.py`
2. Follow naming pattern: `phase2_[letter]_[name].py`
3. Include proper header with module path
4. Validate before commit:
   ```bash
   python scripts/validate_naming_conventions.py
   ```

### Renaming Legacy Files

1. Rename file following convention
2. Update all imports
3. Remove from `.naming_exemptions`
4. Run tests
5. Submit PR

## Compliance Verification

```bash
# Should output: ✅ All naming conventions validated successfully
python scripts/validate_naming_conventions.py

# Run full test suite
python -m pytest tests/test_naming_conventions.py -v
```

## Troubleshooting

### "Violation found" error

- Check if file matches naming pattern
- Verify file location is correct
- For legacy files, check `.naming_exemptions`

### CI failing on PR

- Run local validation first
- Check GitHub Actions logs
- Verify no new violations introduced

### Test failures

- Ensure pytest installed: `pip install pytest`
- Check file paths are correct
- Verify exemption file exists

## Next Steps

After merging:
1. Monitor CI execution
2. Begin legacy file migration
3. Update team documentation
4. Schedule Phase 2 → `canonic_phases/phase_2` migration

---

**Issue**: IV - SECTION 3: NAMING CONVENTION ENFORCEMENT  
**Status**: ✅ COMPLETE  
**Last Updated**: 2025-12-18  
**Maintainer**: F.A.R.F.A.N Core Team
