# Phase 2 Canonical Migration Guide

## Overview

This guide provides step-by-step instructions for migrating Phase 2 files from legacy locations to the canonical frozen structure under `src/canonic_phases/phase_2/`.

## Prerequisites

- [ ] All existing tests pass
- [ ] Git working directory is clean
- [ ] Backup of current state created
- [ ] Review of `PHASE2_FREEZE_IMPLEMENTATION_STATUS.md` complete

## Migration Phases

### Phase 1: Preparation (Manual)

1. **Run existing tests to establish baseline:**
   ```bash
   pytest tests/test_phase2*.py -v > baseline_tests.txt
   ```

2. **Create backup branch:**
   ```bash
   git checkout -b backup/pre-phase2-migration
   git push origin backup/pre-phase2-migration
   git checkout main  # or your working branch
   ```

3. **Review migration map:**
   ```bash
   cat src/canonic_phases/phase_2/PHASE2_FREEZE_IMPLEMENTATION_STATUS.md
   ```

### Phase 2: Dry Run (Automated)

4. **Run migration script in dry-run mode:**
   ```bash
   python scripts/migrate_phase2_canonical.py --dry-run --all
   ```

5. **Review dry-run report:**
   ```bash
   cat phase2_migration_report.json | jq '.summary'
   ```

6. **Address any warnings or errors:**
   - Check for missing source files
   - Verify target directories exist
   - Resolve any path conflicts

### Phase 3: Staged Migration (Semi-Automated)

7. **Migrate phase_root modules:**
   ```bash
   python scripts/migrate_phase2_canonical.py --execute --section phase_root
   git add src/canonic_phases/phase_2/
   git commit -m "Migrate Phase 2 root modules to canonical structure"
   ```

8. **Update imports in dependent code:**
   ```bash
   # Find files importing from old locations
   grep -r "from farfan_pipeline.phases.Phase_two" src/ tests/
   
   # Update imports (manual or with sed)
   # Example: 
   # OLD: from farfan_pipeline.phases.Phase_two.carver import carve_cpp
   # NEW: from canonic_phases.phase_2.phase2_b_carver import carve_cpp
   ```

9. **Run tests after phase_root migration:**
   ```bash
   pytest tests/test_phase2*.py -v
   ```

10. **Repeat for each section:**
    ```bash
    # Executors
    python scripts/migrate_phase2_canonical.py --execute --section executors
    # Update imports, test, commit
    
    # Orchestration
    python scripts/migrate_phase2_canonical.py --execute --section orchestration
    # Update imports, test, commit
    
    # Contracts
    python scripts/migrate_phase2_canonical.py --execute --section contracts
    # Update imports, test, commit
    ```

### Phase 4: SISAS Integration (Manual)

11. **Create SISAS adapter modules:**
    ```bash
    # These are new files, not migrations
    touch src/canonic_phases/phase_2/sisas/phase2_signal_registry_adapter.py
    touch src/canonic_phases/phase_2/sisas/phase2_signal_contract_validator.py
    touch src/canonic_phases/phase_2/sisas/phase2_signal_consumption_integration.py
    touch src/canonic_phases/phase_2/sisas/phase2_signal_quality_integration.py
    ```

12. **Implement SISAS adapters:**
    - Refer to existing SISAS code in `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/`
    - Create thin adapter layer that wraps existing SISAS functionality
    - Add canonical headers to each file

### Phase 5: Schema Completion (Manual)

13. **Create remaining schemas:**
    ```bash
    # calibration_policy.schema.json
    # synchronization_manifest.schema.json
    ```

14. **Validate schemas:**
    ```bash
    # Use jsonschema validator
    python -m jsonschema -i example_config.json \
      src/canonic_phases/phase_2/schemas/executor_config.schema.json
    ```

### Phase 6: Test Implementation (Manual)

15. **Implement test stubs:**
    - Go through each `test_phase2_*.py` file
    - Replace `pytest.skip()` with actual test implementation
    - Ensure all tests pass

16. **Create certificate evidence:**
    - Run tests with verbose output
    - Capture test results for certificate evidence
    - Update certificate status from PENDING to ACTIVE

### Phase 7: Legacy Deletion (Careful!)

17. **Verify all migrations complete:**
    ```bash
    python scripts/verify_phase2_migration.py
    ```

18. **Delete legacy files (ONE AT A TIME):**
    ```bash
    # Example for one file
    git rm src/farfan_pipeline/phases/Phase_two/executors.py
    pytest tests/  # Verify nothing breaks
    git commit -m "Delete legacy executors.py monolith"
    ```

19. **Delete legacy docs:**
    ```bash
    git rm src/farfan_pipeline/phases/Phase_two/EXECUTOR_CALIBRATION_INTEGRATION_README.md
    git rm src/farfan_pipeline/phases/Phase_two/INTEGRATION_IMPLEMENTATION_SUMMARY.md
    ```

20. **Find and delete anti-pattern files:**
    ```bash
    find . -name "*_v2.py" -o -name "*_final.py" -o -name "*_old.py" -o -name "*_backup.py"
    # Review list, then delete
    ```

### Phase 8: Verification (Comprehensive)

21. **Run full test suite:**
    ```bash
    pytest tests/ -v --tb=short
    ```

22. **Verify contract compliance:**
    ```bash
    pytest tests/test_phase2*.py -v --tb=short
    ```

23. **Check certificate status:**
    ```bash
    ls -1 src/canonic_phases/phase_2/contracts/certificates/
    # Verify all 15 certificates exist and are ACTIVE
    ```

24. **Run linters:**
    ```bash
    ruff check src/canonic_phases/phase_2/
    mypy src/canonic_phases/phase_2/ --strict
    ```

## Import Update Checklist

Files that will need import updates:

### Core Orchestration
- [ ] `src/farfan_pipeline/orchestration/orchestrator.py`
- [ ] `src/farfan_pipeline/core/phases/*.py`

### Tests
- [ ] `tests/test_phase2_execution_logic.py`
- [ ] `tests/test_phase2_sisas_checklist.py`
- [ ] `tests/test_phase2_executor_contracts_cqvr_gate.py`
- [ ] Any other tests importing Phase_two modules

### Scripts
- [ ] Any scripts in `scripts/` that import Phase_two modules

## Rollback Procedure

If migration fails:

```bash
# Restore from backup branch
git checkout main
git reset --hard backup/pre-phase2-migration

# Or revert specific commits
git revert <commit-hash>
```

## Success Criteria

Migration is complete when:

- [ ] All 40+ files migrated with canonical headers
- [ ] All imports updated and validated
- [ ] All tests pass (existing + new contract tests)
- [ ] All 15 certificates ACTIVE
- [ ] Legacy files deleted
- [ ] Documentation updated
- [ ] Linters pass (ruff, mypy)
- [ ] No import errors in any part of codebase

## Troubleshooting

### Import errors after migration
```bash
# Find circular imports
python -c "import canonic_phases.phase_2"

# Check sys.path
python -c "import sys; print('\n'.join(sys.path))"
```

### Test failures
```bash
# Run with maximum verbosity
pytest tests/test_phase2*.py -vv --tb=long

# Check for missing fixtures
pytest --fixtures tests/
```

### Schema validation errors
```bash
# Validate schema syntax
python -c "import json; json.load(open('schemas/executor_config.schema.json'))"

# Check draft version
grep '$schema' schemas/*.json
```

## Support

For issues during migration:
1. Check `PHASE2_FREEZE_IMPLEMENTATION_STATUS.md` for current status
2. Review certificate evidence in `contracts/certificates/`
3. Consult test output in `tests/test_phase2_*.py`
4. Check migration report in `phase2_migration_report.json`
