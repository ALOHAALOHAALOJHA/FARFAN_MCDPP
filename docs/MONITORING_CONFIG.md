# CQVR Monitoring Configuration

## Overview

This document defines monitoring and alerting configuration for the CQVR system in production.

## Metrics to Monitor

### Contract Quality Metrics

| Metric | Description | Collection Frequency | Retention |
|--------|-------------|---------------------|-----------|
| `cqvr.average_score` | Average CQVR score across all contracts | Every 5 minutes | 90 days |
| `cqvr.contracts.total` | Total number of contracts | Every 5 minutes | 90 days |
| `cqvr.contracts.passed_80` | Contracts scoring ≥ 80 | Every 5 minutes | 90 days |
| `cqvr.contracts.failed_40` | Contracts scoring < 40 | Every 5 minutes | 90 days |
| `cqvr.tier1_average` | Average Tier 1 score | Every 5 minutes | 90 days |
| `cqvr.tier2_average` | Average Tier 2 score | Every 5 minutes | 90 days |
| `cqvr.tier3_average` | Average Tier 3 score | Every 5 minutes | 90 days |

### Execution Metrics

| Metric | Description | Collection Frequency | Retention |
|--------|-------------|---------------------|-----------|
| `contract.execution.success_rate` | Percentage of successful executions | Every 1 minute | 30 days |
| `contract.execution.duration_ms` | Contract execution time | Every execution | 30 days |
| `contract.execution.errors` | Count of execution errors | Every 1 minute | 30 days |
| `contract.validation.failures` | Count of validation failures | Every 1 minute | 30 days |

### System Metrics

| Metric | Description | Collection Frequency | Retention |
|--------|-------------|---------------------|-----------|
| `system.memory_usage_mb` | Memory consumption | Every 1 minute | 7 days |
| `system.cpu_usage_percent` | CPU utilization | Every 1 minute | 7 days |
| `system.disk_usage_percent` | Disk space usage | Every 5 minutes | 30 days |

## Alert Rules

### Critical Alerts (P0)

**Contract Execution Failure Rate High**
```yaml
alert: ContractExecutionFailureHigh
expr: contract.execution.success_rate < 95
for: 5m
severity: critical
description: Contract execution success rate dropped below 95%
action: Page on-call engineer immediately
runbook: docs/DEPLOYMENT_RUNBOOK.md#troubleshooting
```

**Contracts Below Quality Threshold**
```yaml
alert: ContractsQualityThresholdViolation
expr: cqvr.contracts.failed_40 > 0
for: 10m
severity: critical
description: Contracts scoring below 40 detected
action: Page on-call engineer
runbook: docs/DEPLOYMENT_RUNBOOK.md#issue-quality-gate-failure
```

**Average Score Critical Drop**
```yaml
alert: AverageScoreCriticalDrop
expr: cqvr.average_score < 70
for: 15m
severity: critical
description: Average CQVR score dropped below 70
action: Page on-call engineer
runbook: docs/DEPLOYMENT_RUNBOOK.md#rollback-procedures
```

### Warning Alerts (P1)

**Average Score Below Target**
```yaml
alert: AverageScoreBelowTarget
expr: cqvr.average_score < 80
for: 30m
severity: warning
description: Average CQVR score below target of 80
action: Notify team via Slack
runbook: docs/DEPLOYMENT_RUNBOOK.md#troubleshooting
```

**Contract Execution Errors Increasing**
```yaml
alert: ContractExecutionErrorsIncreasing
expr: rate(contract.execution.errors[5m]) > rate(contract.execution.errors[15m])
for: 10m
severity: warning
description: Contract execution errors are increasing
action: Notify team via Slack
runbook: docs/DEPLOYMENT_RUNBOOK.md#issue-contract-execution-errors
```

**Memory Usage High**
```yaml
alert: MemoryUsageHigh
expr: system.memory_usage_mb > 6000
for: 10m
severity: warning
description: Memory usage exceeds 6GB
action: Notify team via Slack
```

### Info Alerts (P2)

**Quality Score Improvement**
```yaml
alert: QualityScoreImprovement
expr: cqvr.average_score > 85
for: 1h
severity: info
description: Average CQVR score improved above 85
action: Post to team channel
```

**All Contracts Passing**
```yaml
alert: AllContractsPassing
expr: cqvr.contracts.passed_80 == cqvr.contracts.total
for: 1h
severity: info
description: All contracts passing with score ≥ 80
action: Post to team channel
```

## Monitoring Dashboard

### Dashboard URL

- **Production**: https://farfan.example.com/dashboard/cqvr_dashboard.html
- **Staging**: https://staging.farfan.example.com/dashboard/cqvr_dashboard.html

### Dashboard Sections

1. **Quality Overview**
   - Average CQVR score (large display)
   - Total contracts evaluated
   - Contracts by score range
   - Quality trend over time

2. **Tier Breakdown**
   - Tier 1 (Critical) average score
   - Tier 2 (Functional) average score
   - Tier 3 (Quality) average score
   - Score distribution by tier

3. **Execution Health**
   - Success rate (last hour)
   - Error count (last hour)
   - Average execution time
   - Top 10 failing contracts

4. **System Health**
   - Memory usage
   - CPU usage
   - Disk usage
   - Deployment status

## Data Collection

### Collection Script

Run evaluation and export metrics:

```bash
#!/bin/bash
# scripts/collect_metrics.sh

python scripts/evaluate_all_contracts.py

# Export to monitoring system (customize for your monitoring tool)
python scripts/export_metrics.py --format prometheus
```

### Continuous Collection

Set up cron job for continuous monitoring:

```cron
# Run every 5 minutes
*/5 * * * * cd /opt/farfan && ./scripts/collect_metrics.sh >> /var/log/farfan/metrics.log 2>&1
```

## Integration with Monitoring Tools

### Prometheus

```yaml
scrape_configs:
  - job_name: 'farfan_cqvr'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5m
    metrics_path: '/metrics'
```

### Grafana

Import dashboard template:

```bash
# Import dashboard/grafana_dashboard.json
curl -X POST http://grafana:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboard/grafana_dashboard.json
```

### CloudWatch (AWS)

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='FARFAN/CQVR',
    MetricData=[
        {
            'MetricName': 'AverageScore',
            'Value': average_score,
            'Unit': 'None'
        }
    ]
)
```

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| P0 - Critical | Contract failures > 5%, system down | 15 minutes | Immediate page |
| P1 - High | Quality degradation, errors increasing | 1 hour | Team notification |
| P2 - Medium | Minor issues, performance degradation | 4 hours | Slack notification |
| P3 - Low | Info alerts, improvements | Next business day | Email |

### Response Actions

**P0 - Critical**
1. Acknowledge alert within 5 minutes
2. Assess impact and scope
3. Decide: Fix forward or rollback
4. Execute rollback if needed: `./scripts/rollback.sh --version previous`
5. Notify stakeholders
6. Create incident ticket
7. Begin incident response

**P1 - High**
1. Acknowledge alert within 30 minutes
2. Investigate root cause
3. Apply remediation if possible
4. Monitor for improvement
5. Document findings

**P2 - Medium**
1. Review during business hours
2. Schedule fix
3. Update monitoring if needed

## Reporting

### Daily Report

Generate daily quality report:

```bash
python scripts/evaluate_all_contracts.py
# Sends email with artifacts/CQVR_EVALUATION_REPORT.md
```

### Weekly Summary

Email to stakeholders every Monday:

- Average score trend
- Top 10 best/worst contracts
- Total remediation actions taken
- Deployment activity

### Monthly Metrics

Executive summary including:

- Overall quality trend
- Deployment success rate
- Incident count and resolution times
- System reliability (uptime)

## Maintenance

### Regular Tasks

**Daily**
- Review alerts and incidents
- Check dashboard for anomalies
- Verify backup completion

**Weekly**
- Review weekly summary
- Update runbook if needed
- Check disk space and cleanup old backups

**Monthly**
- Review alert thresholds
- Update documentation
- Archive old metrics data
- Conduct retrospective

### Alert Tuning

Review and adjust alert thresholds quarterly:

1. Analyze false positive rate
2. Check if thresholds match reality
3. Update alert rules
4. Test with historical data
5. Deploy updated configuration

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-17  
**Next Review**: 2026-01-17
