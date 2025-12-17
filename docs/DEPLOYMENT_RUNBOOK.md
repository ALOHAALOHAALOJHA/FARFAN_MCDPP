# CQVR System Deployment Runbook

## Overview

This runbook provides step-by-step procedures for deploying the CQVR (Contract Quality Validation and Remediation) system to production.

## Pre-deployment Checklist

### Quality Requirements

- [ ] All 300 contracts evaluated
- [ ] Average CQVR score ≥ 80/100
- [ ] No contracts scoring < 40
- [ ] All Tier 1 blockers resolved

### System Readiness

- [ ] CI/CD pipeline configured and tested
- [ ] Backup procedures verified
- [ ] Rollback scripts tested
- [ ] Monitoring dashboard deployed
- [ ] Team trained on procedures

### Documentation

- [ ] Deployment runbook reviewed
- [ ] Rollback procedures documented
- [ ] Incident response plan ready
- [ ] Contact list updated

## Deployment Phases

### Phase 1: Pre-deployment Validation

**Duration**: 30 minutes

**Steps**:

1. Run comprehensive contract evaluation:
   ```bash
   python scripts/evaluate_all_contracts.py
   ```

2. Verify quality gates:
   ```bash
   # Check artifacts/CQVR_EVALUATION_REPORT.md
   # Ensure average ≥ 80 and no contracts < 40
   ```

3. Run full test suite:
   ```bash
   pytest -v
   ```

4. Create pre-deployment backup:
   ```bash
   TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
   mkdir -p backups/pre_production_$TIMESTAMP
   cp -r src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/*.json backups/pre_production_$TIMESTAMP/
   ```

**Success Criteria**:
- All tests pass
- Average score ≥ 80
- Backup created successfully

### Phase 2: Staging Deployment

**Duration**: 1 hour

**Steps**:

1. Deploy to staging environment:
   ```bash
   # Trigger staging workflow
   git push origin develop
   ```

2. Monitor staging deployment:
   ```bash
   # Watch GitHub Actions workflow
   # Verify all jobs complete successfully
   ```

3. Run integration tests in staging:
   ```bash
   # Tests run automatically in workflow
   # Verify artifacts/cqvr_evaluation_full.json
   ```

4. Manual validation in staging:
   - Open dashboard: https://staging.farfan.example.com/dashboard
   - Verify contract execution
   - Check monitoring metrics

**Success Criteria**:
- Staging deployment successful
- All integration tests pass
- No errors in logs

### Phase 3: Canary Deployment (10% of Production)

**Duration**: 24 hours monitoring

**Steps**:

1. Initiate canary deployment:
   ```bash
   # Trigger production workflow with canary option
   gh workflow run deploy-production.yml \
     -f deployment_strategy=canary \
     -f canary_percentage=10
   ```

2. Monitor canary metrics (every 4 hours for 24 hours):
   ```bash
   # Check dashboard metrics
   # Monitor error rates
   # Watch response times
   ```

3. Validate canary health:
   - Contract execution success rate > 99%
   - No increase in error rates
   - Response times within normal range
   - No user-reported issues

**Success Criteria**:
- 24 hours of stable operation
- No critical errors
- Performance within acceptable range

**Rollback Trigger**:
- Contract execution failures > 1%
- Critical errors detected
- Performance degradation > 20%

### Phase 4: Full Production Deployment

**Duration**: 2 hours

**Steps**:

1. Final pre-deployment check:
   ```bash
   python scripts/evaluate_all_contracts.py
   ```

2. Deploy to 100% production:
   ```bash
   gh workflow run deploy-production.yml \
     -f deployment_strategy=full
   ```

3. Monitor deployment:
   ```bash
   # Watch GitHub Actions workflow
   # Monitor logs in real-time
   ```

4. Post-deployment validation:
   ```bash
   # Verify all contracts loaded
   python scripts/evaluate_all_contracts.py
   
   # Check dashboard
   # Open https://farfan.example.com/dashboard
   ```

**Success Criteria**:
- Deployment completes without errors
- All 300 contracts functional
- Monitoring shows healthy metrics

### Phase 5: Post-deployment Monitoring

**Duration**: 48 hours intensive monitoring

**Monitoring Schedule**:

- **0-4 hours**: Check every 30 minutes
- **4-24 hours**: Check every 2 hours
- **24-48 hours**: Check every 4 hours

**Metrics to Monitor**:

1. Contract execution success rate
2. Average CQVR scores
3. Error rates and types
4. Response times
5. Resource utilization

**Tools**:

- CQVR Dashboard: `dashboard/cqvr_dashboard.html`
- GitHub Actions logs
- Application logs

**Alert Thresholds**:

- Contract execution failure > 1%: WARNING
- Contract execution failure > 5%: CRITICAL
- Average score drops below 75: WARNING
- Average score drops below 70: CRITICAL

## Rollback Procedures

### When to Rollback

Execute rollback if:

- Contract execution failures exceed 5%
- Critical security vulnerability detected
- Data integrity issues identified
- System instability persists > 2 hours

### Rollback Steps

1. **Immediate**: Stop current deployment
   ```bash
   # Cancel running workflows if needed
   gh run cancel <run-id>
   ```

2. **Identify backup version**:
   ```bash
   ls -la backups/ | grep production
   ```

3. **Execute rollback**:
   ```bash
   ./scripts/rollback.sh --version previous
   ```

4. **Verify rollback**:
   ```bash
   python scripts/evaluate_all_contracts.py
   ```

5. **Notify stakeholders**:
   - Send incident notification
   - Document rollback reason
   - Schedule post-mortem

### Rollback Validation

After rollback:

- [ ] All contracts restored
- [ ] Evaluation shows expected scores
- [ ] System functioning normally
- [ ] Users notified
- [ ] Incident documented

## Troubleshooting

### Issue: Quality Gate Failure

**Symptoms**: Average score < 80 or contracts < 40 detected

**Resolution**:
```bash
# Run remediation
python scripts/remediate_contracts.py

# Re-evaluate
python scripts/evaluate_all_contracts.py

# If still failing, regenerate low-scoring contracts
```

### Issue: Deployment Pipeline Failure

**Symptoms**: GitHub Actions workflow fails

**Resolution**:
1. Check workflow logs for specific error
2. Verify all dependencies installed
3. Check file permissions
4. Retry with: `gh workflow run <workflow> --ref main`

### Issue: Contract Execution Errors

**Symptoms**: Contracts fail to execute in production

**Resolution**:
1. Check contract validation:
   ```bash
   python scripts/evaluate_all_contracts.py
   ```
2. Review error logs
3. Identify failing contracts
4. Apply remediation or rollback

## Contact Information

### Team Roles

- **Deployment Lead**: Responsible for execution
- **QA Lead**: Validates quality gates
- **Incident Response**: Handles issues during deployment
- **Stakeholder Liaison**: Communicates with stakeholders

### Escalation Path

1. **Level 1**: Team Lead (Response: 15 min)
2. **Level 2**: Technical Manager (Response: 30 min)
3. **Level 3**: Engineering Director (Response: 1 hour)

## Post-deployment Tasks

After successful deployment:

- [ ] Document lessons learned
- [ ] Update runbook with improvements
- [ ] Archive deployment artifacts
- [ ] Schedule retrospective meeting
- [ ] Update system documentation
- [ ] Close deployment ticket

## Appendix

### Useful Commands

```bash
# Evaluate all contracts
python scripts/evaluate_all_contracts.py

# Remediate contracts
python scripts/remediate_contracts.py

# Rollback to previous version
./scripts/rollback.sh --version previous

# Create backup
./scripts/rollback.sh --version $(date +%Y-%m-%d)

# View dashboard
open dashboard/cqvr_dashboard.html

# Check GitHub Actions
gh run list --workflow=deploy-production.yml

# View specific run logs
gh run view <run-id> --log
```

### Quality Gate Criteria

| Metric | Minimum | Target |
|--------|---------|--------|
| Average Score | 80 | 85 |
| Contracts ≥ 80 | 80% | 95% |
| Contracts < 40 | 0 | 0 |
| Tier 1 Score | ≥ 35 | ≥ 45 |

### Deployment Windows

**Preferred**:
- Tuesday-Thursday
- 10:00 AM - 2:00 PM UTC
- Not during holidays or weekends

**Avoid**:
- Friday afternoons
- Weekends
- Major holidays
- End of month/quarter

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-17  
**Next Review**: 2026-01-17
