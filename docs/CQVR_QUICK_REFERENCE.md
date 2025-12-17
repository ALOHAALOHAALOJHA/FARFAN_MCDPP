# CQVR CI/CD Quick Reference

## Running CQVR Evaluation Locally

### Evaluate All Contracts
```bash
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 40
```

### Evaluate Specific Contracts
```bash
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 40 \
  --contracts Q001.v3.json Q002.v3.json
```

### Strict Mode (Exit on Failure)
```bash
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 80 \
  --fail-below-threshold
```

## Workflow Triggers

| Trigger | Mode | When | What Gets Evaluated |
|---------|------|------|---------------------|
| **Push** (main/develop) | Incremental | Changes to contracts pushed | Only changed contracts |
| **Pull Request** | Incremental | PR modifying contracts | Only changed contracts + PR comment + quality gate |
| **Manual Dispatch** | Configurable | Run from Actions UI | Selected contracts or all |
| **Schedule** | Full | Every Monday 2 AM UTC | All 310 contracts |

## Manual Workflow Dispatch

1. Navigate to: **Actions** → **CQVR Contract Quality Validation**
2. Click **"Run workflow"** button
3. Configure:
   - **Branch**: Select branch to run on
   - **Contracts** (optional): Comma-separated list (e.g., `Q001.v3.json,Q002.v3.json`)
   - **Threshold** (optional): Quality threshold 0-100 (default: 40)
4. Click **"Run workflow"** to execute

## Quality Scoring

### Tier Breakdown (100 points total)

| Tier | Points | Components | Threshold |
|------|--------|------------|-----------|
| **Tier 1** | 55 | Identity-schema (20), Method-assembly (20), Signal integrity (10), Output schema (5) | ≥35 |
| **Tier 2** | 30 | Pattern coverage (10), Method specificity (10), Validation rules (10) | ≥20 |
| **Tier 3** | 15 | Documentation (5), Human template (5), Metadata (5) | ≥8 |

### Triage Decisions

| Score Range | Tier 1 | Decision | Action Required |
|-------------|--------|----------|-----------------|
| 70-100 | ≥45 | `PARCHEAR_MINOR` | Minor patches |
| 60-69 | ≥35 | `PARCHEAR_MAJOR` | Major patches |
| <60 | ≥35 | `PARCHEAR_CRITICO` | Critical fixes |
| Any | <35 | `REFORMULAR_*` | Rebuild contract |

### Quality Gate (PR Only)

- **Pass**: All contracts ≥ threshold (default: 40)
- **Fail**: Any contract < threshold → **Merge blocked**

## Artifacts (90-day retention)

### 1. Evaluation Reports
- `cqvr_evaluation_report.json` - Detailed JSON with all scores
- `cqvr_evaluation_report.md` - Human-readable Markdown summary

### 2. Dashboard
- `cqvr_dashboard.html` - Interactive HTML dashboard

### Download Artifacts
1. Go to workflow run page
2. Scroll to **Artifacts** section
3. Download:
   - `cqvr-evaluation-reports-<run-number>`
   - `cqvr-dashboard-<run-number>`

## PR Comments

Auto-generated comment includes:
- ✅/❌ Overall status
- Pass/fail counts and rate
- Contract-by-contract results table
- Quality gate verdict
- Failed contracts list (if any)
- Link to detailed reports

## Notification on Failure

For scheduled/manual runs:
- Creates GitHub issue with `[CQVR]` prefix
- Labels: `cqvr`, `automated`, `quality-gate`
- Links to failed workflow run
- Reuses existing open issue if found

## Troubleshooting

### Workflow Not Triggering

**Check**:
1. Are you modifying contract files in `specialized/` directory?
2. Does `.github/workflows/cqvr-validation.yml` exist?
3. Are workflow runs enabled for the repository?

**Solution**: Ensure file paths match workflow trigger patterns

### Evaluation Fails

**Check**:
1. Python 3.12 installed?
2. Dependencies installed (`pip install -e .`)?
3. Contract JSON valid?

**Solution**: Review workflow logs for specific error

### Quality Gate Blocks Valid PR

**Options**:
1. Review CQVR rubric and fix contract issues
2. Use manual dispatch with lower threshold to test
3. Check if contract truly meets production standards
4. Adjust global threshold in workflow (requires maintainer)

## Configuration

### Change Quality Threshold

**Workflow file**: `.github/workflows/cqvr-validation.yml`

```yaml
workflow_dispatch:
  inputs:
    threshold:
      default: '40'  # ← Change this
```

### Change Schedule

**Workflow file**: `.github/workflows/cqvr-validation.yml`

```yaml
schedule:
  - cron: '0 2 * * 1'  # ← Change this (Monday 2 AM UTC)
```

**Cron format**: `minute hour day month weekday`

Examples:
- `0 2 * * 1`: Every Monday at 2 AM
- `0 0 * * *`: Every day at midnight
- `0 */6 * * *`: Every 6 hours

### Modify Evaluation Criteria

**Validator file**: `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/cqvr_validator.py`

Adjust:
- Tier weights in `__init__`
- Scoring logic in `_verify_*` methods
- Triage decisions in `_triage_decision`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All contracts passed |
| 1 | One or more contracts failed (with `--fail-below-threshold`) |

## Common Use Cases

### Pre-commit Check
```bash
# Before committing contract changes
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 40 \
  --contracts YourNewContract.v3.json
```

### Full Repository Audit
```bash
# Audit all contracts
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 80 \
  --output-dir audit_results
```

### CI/CD Testing
```bash
# Simulate CI environment
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 40 \
  --fail-below-threshold
echo $?  # Check exit code
```

## Support

For issues or questions:
1. Check workflow logs in Actions tab
2. Review `docs/CQVR_CICD_INTEGRATION.md` for details
3. Open issue with `cqvr` label
4. Include workflow run link and error messages

---

**Last Updated**: 2025-12-17  
**Version**: 1.0.0
