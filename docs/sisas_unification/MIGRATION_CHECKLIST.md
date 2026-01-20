# SISAS Migration Checklist

**Version:** 1.0.0  
**Date:** 2026-01-19  
**Status:** CANONICAL  

---

## 1. Overview

This checklist provides step-by-step verification for migrating to the unified SISAS architecture. Complete all items in order, documenting results for audit purposes.

---

## 2. Pre-Migration Checklist (10 Items)

Complete these items BEFORE beginning the migration:

### Infrastructure Verification

| # | Item | Description | Verified By | Date | Status |
|---|------|-------------|-------------|------|--------|
| 1 | **Backup Current State** | Create full backup of current system state including databases, configurations, and logs | | | ☐ |
| 2 | **Verify Disk Space** | Ensure minimum 50GB free space for migration artifacts | | | ☐ |
| 3 | **Check Python Version** | Confirm Python 3.12+ is installed: `python --version` | | | ☐ |
| 4 | **Verify Dependencies** | Run `pip install -r requirements.txt` without errors | | | ☐ |
| 5 | **Database Connectivity** | Confirm database connections are active and responsive | | | ☐ |

### Code Verification

| # | Item | Description | Verified By | Date | Status |
|---|------|-------------|-------------|------|--------|
| 6 | **Run Existing Tests** | Execute `pytest tests/` - all tests must pass | | | ☐ |
| 7 | **Verify Method Registry** | Confirm 240 methods in `METHODS_TO_QUESTIONS_AND_FILES.json` | | | ☐ |
| 8 | **Verify Contracts** | Confirm 300 contracts in `executor_contracts/specialized/` | | | ☐ |
| 9 | **Check Class Registry** | Verify 40 classes in `class_registry.py` | | | ☐ |
| 10 | **Document Current Metrics** | Record baseline metrics for comparison | | | ☐ |

### Pre-Migration Commands

```bash
# 1. Create backup
tar -czvf backup_$(date +%Y%m%d_%H%M%S).tar.gz src/ data/ contracts/

# 2. Verify disk space
df -h .

# 3. Check Python version
python --version

# 4. Install dependencies
pip install -r requirements.txt

# 5. Test database connection
python -c "from src.database import connection; connection.test()"

# 6. Run tests
pytest tests/ -v --tb=short

# 7. Verify method registry
python -c "import json; data=json.load(open('data/METHODS_TO_QUESTIONS_AND_FILES.json')); print(f'Methods: {len(data)}')"

# 8. Verify contracts
find contracts/executor_contracts/specialized -name "*.json" | wc -l

# 9. Check class registry
grep -c "class.*:" src/class_registry.py

# 10. Record baseline metrics
python scripts/collect_metrics.py --output baseline_metrics.json
```

---

## 3. Post-Migration Checklist (15 Items)

Complete these items AFTER the migration:

### Component Verification

| # | Item | Description | Verified By | Date | Status |
|---|------|-------------|-------------|------|--------|
| 1 | **UnifiedOrchestrator Loads** | Instantiate UnifiedOrchestrator without errors | | | ☐ |
| 2 | **UnifiedFactory Creates SDO** | Factory successfully creates SignalDistributionOrchestrator | | | ☐ |
| 3 | **All Gates Initialize** | All 4 gates initialize without errors | | | ☐ |
| 4 | **Consumer Registry Populated** | All 10 consumers registered in registry | | | ☐ |
| 5 | **Signal Types Cataloged** | All 17 signal types defined and validated | | | ☐ |

### Functional Verification

| # | Item | Description | Verified By | Date | Status |
|---|------|-------------|-------------|------|--------|
| 6 | **Gate 1 Validates Scopes** | Scope alignment gate accepts valid scopes, rejects invalid | | | ☐ |
| 7 | **Gate 2 Checks Value Add** | Value add gate enforces 0.30 threshold | | | ☐ |
| 8 | **Gate 3 Matches Capabilities** | Capability gate finds eligible consumers | | | ☐ |
| 9 | **Gate 4 Creates Audit Records** | Irrigation channel gate creates audit logs | | | ☐ |
| 10 | **End-to-End Signal Flow** | Signal traverses all gates and reaches consumer | | | ☐ |

### Integration Verification

| # | Item | Description | Verified By | Date | Status |
|---|------|-------------|-------------|------|--------|
| 11 | **Run Full Test Suite** | Execute `pytest tests/` - all tests pass | | | ☐ |
| 12 | **Run Integration Tests** | Execute `pytest tests/integration/` - all pass | | | ☐ |
| 13 | **Verify Metrics Collection** | Metrics endpoint returns valid data | | | ☐ |
| 14 | **Check Dead Letter Queue** | DLQ is empty or contains only expected items | | | ☐ |
| 15 | **Compare Performance** | Latency and throughput meet or exceed baseline | | | ☐ |

### Post-Migration Commands

```bash
# 1. Test UnifiedOrchestrator
python -c "from src.orchestrator import UnifiedOrchestrator; uo = UnifiedOrchestrator(); print('OK')"

# 2. Test UnifiedFactory
python -c "from src.factory import UnifiedFactory; uf = UnifiedFactory(); sdo = uf.create_sdo(); print('OK')"

# 3. Test Gates
python -c "
from src.gates import ScopeAlignmentGate, ValueAddGate, CapabilityGate, IrrigationChannelGate
gates = [ScopeAlignmentGate(), ValueAddGate(), CapabilityGate(), IrrigationChannelGate()]
print(f'Gates initialized: {len(gates)}')
"

# 4. Verify Consumer Registry
python -c "
from src.consumers import ConsumerRegistry
registry = ConsumerRegistry()
print(f'Consumers registered: {len(registry.list_all())}')
"

# 5. Verify Signal Types
python -c "
from src.signals import SignalType
print(f'Signal types: {len(SignalType)}')
"

# 6-9. Gate validation tests
pytest tests/gates/ -v

# 10. End-to-end test
pytest tests/e2e/test_signal_flow.py -v

# 11. Full test suite
pytest tests/ -v --tb=short

# 12. Integration tests
pytest tests/integration/ -v

# 13. Check metrics
curl -s http://localhost:8000/metrics | jq '.sdo'

# 14. Check DLQ
python -c "
from src.queues import DeadLetterQueue
dlq = DeadLetterQueue()
print(f'DLQ size: {dlq.size()}')
"

# 15. Performance comparison
python scripts/compare_metrics.py baseline_metrics.json current_metrics.json
```

---

## 4. Rollback Procedure

If migration fails, follow this procedure to restore the previous state:

### 4.1 Immediate Rollback Steps

| Step | Action | Command |
|------|--------|---------|
| 1 | **Stop All Services** | `systemctl stop sisas-*` or `pkill -f python` |
| 2 | **Restore Backup** | `tar -xzvf backup_YYYYMMDD_HHMMSS.tar.gz` |
| 3 | **Restore Database** | `pg_restore -d sisas backup_db.dump` |
| 4 | **Clear Caches** | `rm -rf __pycache__ .pytest_cache` |
| 5 | **Reinstall Dependencies** | `pip install -r requirements.txt --force-reinstall` |
| 6 | **Verify Restoration** | Run pre-migration tests |
| 7 | **Restart Services** | `systemctl start sisas-*` |
| 8 | **Document Failure** | Record failure reason in incident report |

### 4.2 Rollback Script

```bash
#!/bin/bash
# rollback.sh - Emergency rollback procedure

set -e

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./rollback.sh <backup_file.tar.gz>"
    exit 1
fi

echo "=== SISAS EMERGENCY ROLLBACK ==="
echo "Backup file: $BACKUP_FILE"
echo ""

# Step 1: Stop services
echo "Step 1: Stopping services..."
pkill -f "python.*sisas" || true
sleep 5

# Step 2: Restore backup
echo "Step 2: Restoring backup..."
tar -xzvf "$BACKUP_FILE" --overwrite

# Step 3: Clear caches
echo "Step 3: Clearing caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache

# Step 4: Reinstall dependencies
echo "Step 4: Reinstalling dependencies..."
pip install -r requirements.txt --force-reinstall

# Step 5: Verify restoration
echo "Step 5: Verifying restoration..."
python -c "import json; data=json.load(open('data/METHODS_TO_QUESTIONS_AND_FILES.json')); print(f'Methods: {len(data)}')"
pytest tests/smoke/ -v --tb=short

# Step 6: Restart services
echo "Step 6: Restarting services..."
# systemctl start sisas-orchestrator
# systemctl start sisas-consumers

echo ""
echo "=== ROLLBACK COMPLETE ==="
echo "Please verify system functionality and document the incident."
```

### 4.3 Rollback Decision Matrix

| Condition | Action | Escalation |
|-----------|--------|------------|
| < 10% tests failing | Debug and fix | None |
| 10-30% tests failing | Partial rollback of affected components | Team lead |
| > 30% tests failing | Full rollback | Project manager |
| Data corruption detected | Immediate full rollback | CTO |
| Service unavailable > 5 min | Immediate full rollback | On-call engineer |

---

## 5. Validation Commands

### 5.1 Quick Validation Suite

```bash
# Run all validation in one command
python -c "
import sys
checks = []

# Check 1: Module imports
try:
    from src.orchestrator import UnifiedOrchestrator
    from src.factory import UnifiedFactory
    from src.gates import ScopeAlignmentGate
    from src.consumers import ConsumerRegistry
    from src.signals import SignalType
    checks.append(('Module imports', True))
except ImportError as e:
    checks.append(('Module imports', False, str(e)))

# Check 2: Orchestrator instantiation
try:
    uo = UnifiedOrchestrator()
    checks.append(('Orchestrator', True))
except Exception as e:
    checks.append(('Orchestrator', False, str(e)))

# Check 3: Consumer count
try:
    registry = ConsumerRegistry()
    count = len(registry.list_all())
    checks.append(('Consumer count', count == 10, f'Found {count}'))
except Exception as e:
    checks.append(('Consumer count', False, str(e)))

# Check 4: Signal types
try:
    count = len(SignalType)
    checks.append(('Signal types', count == 17, f'Found {count}'))
except Exception as e:
    checks.append(('Signal types', False, str(e)))

# Report results
print('=== SISAS VALIDATION RESULTS ===')
all_pass = True
for check in checks:
    status = '✓' if check[1] else '✗'
    msg = check[2] if len(check) > 2 else ''
    print(f'{status} {check[0]} {msg}')
    if not check[1]:
        all_pass = False

print('')
print('OVERALL:', 'PASS' if all_pass else 'FAIL')
sys.exit(0 if all_pass else 1)
"
```

### 5.2 Component Health Checks

```bash
# Gate health checks
python -c "
from src.gates import ScopeAlignmentGate, ValueAddGate, CapabilityGate, IrrigationChannelGate

gates = {
    'ScopeAlignmentGate': ScopeAlignmentGate(),
    'ValueAddGate': ValueAddGate(),
    'CapabilityGate': CapabilityGate(),
    'IrrigationChannelGate': IrrigationChannelGate()
}

for name, gate in gates.items():
    status = gate.health_check()
    print(f'{name}: {status}')
"
```

### 5.3 Signal Flow Validation

```bash
# Test signal flow through all gates
python -c "
from src.signals import Signal, SignalType
from src.orchestrator import UnifiedOrchestrator

# Create test signal
signal = Signal(
    signal_type=SignalType.SCORING_PRIMARY,
    source_phase=4,
    target_scopes=['Q042'],
    payload={'score': 8.5, 'max_score': 10.0}
)

# Process through orchestrator
uo = UnifiedOrchestrator()
result = uo.process_signal(signal)

print(f'Signal ID: {signal.signal_id}')
print(f'Gate 1: {result.gate_results[0]}')
print(f'Gate 2: {result.gate_results[1]}')
print(f'Gate 3: {result.gate_results[2]}')
print(f'Gate 4: {result.gate_results[3]}')
print(f'Dispatch: {result.dispatch_status}')
"
```

---

## 6. Sign-Off Requirements

### 6.1 Required Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | | | |
| QA Lead | | | |
| DevOps Engineer | | | |
| Project Manager | | | |

### 6.2 Completion Criteria

Before signing off, verify:

- [ ] All 10 pre-migration items completed
- [ ] All 15 post-migration items completed
- [ ] No critical test failures
- [ ] Performance meets or exceeds baseline
- [ ] Documentation updated
- [ ] Rollback procedure tested
- [ ] Team notified of completion

---

*End of Migration Checklist*
