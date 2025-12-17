# CQVR Deployment Guide

## Quick Start

This guide covers the deployment of the Contract Quality Validation and Remediation (CQVR) system to production.

## Prerequisites

- Python 3.12+
- All 300 contracts evaluated and meeting quality standards
- Team trained on deployment procedures
- Deployment window scheduled

## Deployment Checklist

### Before Deployment

- [ ] Run pre-deployment validation: `python scripts/pre_deployment_validation.py`
- [ ] Review deployment runbook: `docs/DEPLOYMENT_RUNBOOK.md`
- [ ] Notify stakeholders of deployment window
- [ ] Ensure team is available for monitoring

### During Deployment

- [ ] Execute staging deployment
- [ ] Monitor staging for 1 hour minimum
- [ ] Execute canary deployment (10%)
- [ ] Monitor canary for 24 hours
- [ ] Execute full production deployment
- [ ] Monitor production for 48 hours

### After Deployment

- [ ] Verify all quality gates passing
- [ ] Check monitoring dashboard
- [ ] Document lessons learned
- [ ] Update runbook if needed

## Scripts Reference

### Evaluation and Quality

```bash
# Evaluate all contracts
python scripts/evaluate_all_contracts.py

# View evaluation report
cat artifacts/CQVR_EVALUATION_REPORT.md

# Run pre-deployment validation
python scripts/pre_deployment_validation.py
```

### Remediation

```bash
# Apply automated remediation
python scripts/remediate_contracts.py

# View remediation results
cat artifacts/remediation_results.json
```

### Backup and Rollback

```bash
# Rollback to previous version
./scripts/rollback.sh --version previous

# Rollback to specific date
./scripts/rollback.sh --version 2026-01-14

# Restore from specific backup
./scripts/restore_contracts.sh --backup contracts_20260114_120000
```

## CI/CD Workflows

### Quality Gate (Automatic)

Runs on every push to main/develop and PR:
- Evaluates all contracts
- Checks quality thresholds
- Comments on PR with results

### Staging Deployment

Triggered on push to `develop` branch:

```bash
git push origin develop
```

Or manually:

```bash
gh workflow run deploy-staging.yml
```

### Production Deployment

Triggered on push to `main` branch or manually:

```bash
# Canary deployment (10%)
gh workflow run deploy-production.yml \
  -f deployment_strategy=canary \
  -f canary_percentage=10

# Full deployment
gh workflow run deploy-production.yml \
  -f deployment_strategy=full
```

## Monitoring

### Dashboard

Access the monitoring dashboard:

- **Production**: `dashboard/cqvr_dashboard.html`
- Open in browser with a local web server:

```bash
cd dashboard
python -m http.server 8000
# Open http://localhost:8000/cqvr_dashboard.html
```

### Metrics

Key metrics to monitor:

- **Average Score**: Should be ≥ 80
- **Contracts ≥ 80**: Target 95%+
- **Contracts < 40**: Must be 0
- **Execution Success Rate**: > 99%

### Alerts

See `docs/MONITORING_CONFIG.md` for complete alert configuration.

Critical alerts:
- Contract execution failure rate > 5%
- Contracts scoring < 40 detected
- Average score drops below 70

## Troubleshooting

### Quality Gate Failure

If contracts don't meet quality standards:

1. Run evaluation:
   ```bash
   python scripts/evaluate_all_contracts.py
   ```

2. Apply remediation:
   ```bash
   python scripts/remediate_contracts.py
   ```

3. Re-evaluate:
   ```bash
   python scripts/evaluate_all_contracts.py
   ```

4. If still failing, check specific contracts in `artifacts/cqvr_evaluation_full.json`

### Deployment Failure

If deployment fails:

1. Check workflow logs:
   ```bash
   gh run list --workflow=deploy-production.yml
   gh run view <run-id> --log
   ```

2. Review error messages

3. If needed, rollback:
   ```bash
   ./scripts/rollback.sh --version previous
   ```

### Performance Issues

If contracts execute slowly:

1. Check system resources
2. Review contract complexity
3. Consider optimization
4. Check monitoring dashboard for bottlenecks

## Rollback Procedures

### When to Rollback

Execute rollback if:
- Contract execution failures > 5%
- Critical security issue detected
- Data integrity compromised
- System instability > 2 hours

### How to Rollback

```bash
# Quick rollback to previous version
./scripts/rollback.sh --version previous

# Rollback to specific backup
./scripts/rollback.sh --version 2026-01-14

# Verify rollback
python scripts/evaluate_all_contracts.py
```

## Documentation

- **[DEPLOYMENT_RUNBOOK.md](docs/DEPLOYMENT_RUNBOOK.md)** - Complete deployment procedures
- **[MONITORING_CONFIG.md](docs/MONITORING_CONFIG.md)** - Monitoring and alerting setup
- **[CQVR Validator](src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/cqvr_validator.py)** - Validation implementation

## Support

For issues during deployment:

1. Check deployment runbook
2. Review troubleshooting section
3. Contact on-call engineer
4. Escalate if needed per runbook procedures

## Quality Standards

### Minimum Requirements

- Average CQVR score: ≥ 80/100
- Contracts scoring ≥ 80: 80%+
- Contracts scoring < 40: 0
- All Tier 1 components: ≥ 35/55

### Production Targets

- Average CQVR score: ≥ 85/100
- Contracts scoring ≥ 80: 95%+
- Execution success rate: > 99%
- Zero critical errors

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-17  
**Next Review**: 2026-01-17
