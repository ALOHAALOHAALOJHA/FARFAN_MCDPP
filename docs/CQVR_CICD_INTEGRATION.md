# CQVR CI/CD Integration

This document describes the automated Contract Quality Validation and Review (CQVR) system integrated into the CI/CD pipeline.

## Overview

The CQVR CI/CD integration provides automated quality validation for executor contracts with the following capabilities:

- **Automated Evaluation**: Runs quality checks on contract changes
- **Quality Gates**: Blocks merges for contracts scoring below threshold (default: 40/100)
- **Detailed Reports**: Generates JSON, Markdown, and HTML dashboard reports
- **Smart Triggers**: Evaluates only changed contracts on PRs, full evaluation on schedule
- **PR Comments**: Automatically comments quality results on pull requests

## Components

### 1. CQVR Batch Evaluator (`scripts/cqvr_batch_evaluator.py`)

CLI tool for batch contract evaluation:

```bash
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --output-dir cqvr_reports \
  --threshold 40 \
  --contracts Q001.v3.json Q002.v3.json
```

**Options:**
- `--contracts-dir`: Directory containing contract JSON files (required)
- `--output-dir`: Output directory for reports (default: `cqvr_reports`)
- `--threshold`: Minimum score threshold 0-100 (default: 40)
- `--contracts`: Specific contracts to evaluate (default: all)
- `--fail-below-threshold`: Exit with error if any contract fails

**Outputs:**
- `cqvr_evaluation_report.json`: Detailed JSON report
- `cqvr_evaluation_report.md`: Markdown summary report
- `cqvr_dashboard.html`: Interactive HTML dashboard

### 2. GitHub Actions Workflow (`.github/workflows/cqvr-validation.yml`)

Automated workflow with multiple trigger modes:

#### Triggers

**1. Push to main/develop** (incremental)
- Triggers on changes to contract files or validator
- Evaluates only changed contracts

**2. Pull Request** (incremental)
- Triggers on PR with contract changes
- Evaluates only changed contracts
- Comments results on PR
- Blocks merge if quality < threshold

**3. Manual Dispatch** (configurable)
- Run via GitHub Actions UI
- Inputs:
  - `contracts`: Comma-separated list of contracts (empty = all)
  - `threshold`: Quality threshold (default: 40)

**4. Scheduled** (full evaluation)
- Runs every Monday at 2 AM UTC
- Evaluates all 310 contracts
- Creates issue on failure

#### Jobs

**Job 1: detect-changes**
- Detects changed contract files in PRs/pushes
- Lists all contracts for scheduled runs

**Job 2: evaluate-contracts**
- Runs CQVR evaluation on selected contracts
- Generates reports and dashboard
- Uploads artifacts (90-day retention)
- Comments on PRs with results
- Blocks merge if quality gate fails
- Updates commit status

**Job 3: notify-on-failure**
- Creates GitHub issue on scheduled run failures
- Only runs for schedule/manual dispatch events

## Quality Thresholds

Contracts are evaluated on a 100-point scale across three tiers:

| Tier | Weight | Description | Threshold |
|------|--------|-------------|-----------|
| **Tier 1** | 55 pts | Critical components (identity, methods, signals, schema) | ≥35 |
| **Tier 2** | 30 pts | Functional components (patterns, validation, assembly) | ≥20 |
| **Tier 3** | 15 pts | Quality components (documentation, templates, metadata) | ≥8 |

**Default Quality Gate**: 40/100 (configurable)

**Triage Decisions:**
- `PARCHEAR_MINOR`: Tier 1 ≥45, Total ≥70 (minor patches needed)
- `PARCHEAR_MAJOR`: Tier 1 ≥35, Total ≥60 (major patches needed)
- `PARCHEAR_CRITICO`: Tier 1 <35 (critical issues)
- `REFORMULAR_*`: Tier 1 <35 with specific blockers (requires rebuild)

## Usage Examples

### Local Evaluation

Evaluate all contracts:
```bash
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 40
```

Evaluate specific contracts:
```bash
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 40 \
  --contracts Q001.v3.json Q002.v3.json
```

With strict threshold and failure exit:
```bash
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 80 \
  --fail-below-threshold
```

### Manual Workflow Dispatch

1. Go to **Actions** → **CQVR Contract Quality Validation**
2. Click **Run workflow**
3. Select branch
4. (Optional) Enter comma-separated contracts: `Q001.v3.json,Q002.v3.json`
5. (Optional) Set threshold: `40`
6. Click **Run workflow**

### Viewing Reports

**Artifacts** (available for 90 days):
- Navigate to workflow run
- Scroll to **Artifacts** section
- Download:
  - `cqvr-evaluation-reports-<run-number>` (JSON + Markdown)
  - `cqvr-dashboard-<run-number>` (HTML)

**PR Comments**:
- Automatically posted on pull requests
- Shows pass/fail status, scores, and triage decisions
- Links to detailed reports

## Dashboard Features

The HTML dashboard provides:
- **Summary Metrics**: Total/Passed/Failed counts
- **Pass Rate Progress Bar**: Visual pass rate indicator
- **Results Table**: Detailed contract-by-contract breakdown
- **Color-coded Status**: Green (pass) / Red (fail)
- **Responsive Design**: Works on all screen sizes

## Integration with Development Workflow

### For Developers

When creating/modifying contracts:

1. **Local Testing** (before commit):
   ```bash
   python scripts/cqvr_batch_evaluator.py \
     --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
     --threshold 40 \
     --contracts YourContract.v3.json
   ```

2. **Review Reports**:
   - Check `cqvr_reports/cqvr_dashboard.html` in browser
   - Address any issues with score < 40

3. **Commit and Push**:
   - Workflow automatically runs on PR
   - Check PR comment for results

4. **If Quality Gate Fails**:
   - Review detailed breakdown in PR comment
   - Fix identified issues
   - Push updates (workflow re-runs automatically)

### For Reviewers

When reviewing PRs:

1. **Check CQVR Comment**: Look for automated quality report
2. **Review Scores**: Ensure all contracts ≥ threshold
3. **Check Triage Decisions**: Understand required improvements
4. **Download Reports**: Review detailed artifacts if needed

## Troubleshooting

### Workflow Fails to Run

**Issue**: Workflow doesn't trigger on PR
**Solution**: Ensure PR modifies files in contract directories:
- `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/*.json`
- `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/cqvr_validator.py`
- `scripts/cqvr_batch_evaluator.py`

### Evaluation Script Fails

**Issue**: Import errors or module not found
**Solution**: Ensure dependencies installed:
```bash
pip install -e .
```

### Quality Gate Blocks Valid Contract

**Issue**: Contract blocked despite being valid
**Solution**: 
1. Review CQVR rubric criteria
2. Check tier-specific scores
3. Consider if threshold needs adjustment
4. Use manual dispatch to override threshold temporarily

## Maintenance

### Adjusting Quality Threshold

**Global**: Edit `.github/workflows/cqvr-validation.yml`:
```yaml
workflow_dispatch:
  inputs:
    threshold:
      default: '40'  # Change this value
```

**Per-run**: Use manual dispatch with custom threshold

### Modifying Evaluation Criteria

Edit `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/cqvr_validator.py`:
- Modify tier weights in `__init__`
- Adjust scoring in `_verify_*` methods
- Update triage logic in `_triage_decision`

### Changing Schedule

Edit `.github/workflows/cqvr-validation.yml`:
```yaml
schedule:
  - cron: '0 2 * * 1'  # Adjust cron expression
```

## Metrics and Monitoring

### Available Metrics

From `cqvr_evaluation_report.json`:
- `total_contracts`: Number of evaluated contracts
- `passed`: Contracts meeting threshold
- `failed`: Contracts below threshold
- `threshold`: Applied quality threshold
- `results[].score`: Individual contract scores
- `results[].tier*_score`: Tier-specific scores
- `results[].triage_decision`: Recommended action

### Tracking Over Time

Use workflow artifacts to track quality trends:
1. Download JSON reports from multiple runs
2. Compare scores over time
3. Identify contracts needing improvement
4. Monitor pass rate trends

## Security Considerations

- **Artifacts Retention**: 90 days (configurable)
- **Permissions**: Workflow has read/write for PRs, checks
- **Secret Exposure**: No secrets in reports or artifacts
- **Branch Protection**: Quality gate enforces minimum standards

## Future Enhancements

Potential improvements:
- [ ] Quality trend visualization
- [ ] Historical score tracking database
- [ ] Slack/email notifications
- [ ] Auto-remediation suggestions
- [ ] Contract diff analysis
- [ ] Performance metrics (evaluation time)
