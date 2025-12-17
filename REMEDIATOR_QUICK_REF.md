# Contract Remediator Quick Reference

## 🚀 Quick Start

```bash
# Always test first with dry-run
python scripts/contract_remediator.py --contract Q005.v3.json --dry-run

# If results look good, run for real
python scripts/contract_remediator.py --contract Q005.v3.json --strategy auto
```

## 📋 Common Commands

### Single Contract
```bash
# Auto-fix (recommended)
python scripts/contract_remediator.py --contract Q002.v3.json --strategy auto

# Targeted patches
python scripts/contract_remediator.py --contract Q002.v3.json --strategy patch

# Full regeneration
python scripts/contract_remediator.py --contract Q002.v3.json --strategy regenerate
```

### Batch Operations
```bash
# Fix multiple contracts
python scripts/contract_remediator.py --batch Q001 Q002 Q003 --strategy auto

# All contracts Q001-Q030
python scripts/contract_remediator.py --all --strategy auto

# All contracts below threshold
python scripts/contract_remediator.py --regenerate --threshold 80
```

### Safety Features
```bash
# Dry-run (no changes written)
python scripts/contract_remediator.py --all --dry-run

# List backups
python scripts/rollback_contract.py --list

# Show diff
python scripts/rollback_contract.py --diff \
  --backup Q002_backup_20250117_120000.json \
  --contract Q002.v3.json

# Rollback
python scripts/rollback_contract.py --rollback \
  --backup Q002_backup_20250117_120000.json \
  --contract Q002.v3.json
```

## 🎯 What Gets Fixed

| Issue | Fix | Score Impact |
|-------|-----|--------------|
| Identity-Schema mismatch | Align const values | +0-20 pts |
| Method assembly broken | Rebuild sources list | +0-20 pts |
| Signal threshold = 0 | Set to 0.5 | +10 pts |
| Missing schema fields | Add to properties | +0-5 pts |
| Missing source hash | Calculate SHA256 | +3 pts |

## 📊 CQVR Thresholds

- **Production**: Total ≥ 80, Tier 1 ≥ 45
- **Patchable**: Tier 1 ≥ 35, Total ≥ 60  
- **Needs Reformulation**: Tier 1 < 35

## ⚠️ Important Notes

1. **Always use --dry-run first** to preview changes
2. **Backups are automatic** - no manual backup needed
3. **Check tier 1 score** - it's the most critical
4. **Rollback is safe** - it backs up current version first
5. **Use batch mode** for multiple contracts

## 🔍 Check Contract Status

```bash
# Python one-liner to check all Q001-Q010
python3 << 'EOF'
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from scripts.contract_remediator import ContractRemediator, RemediationStrategy

remediator = ContractRemediator(
    contracts_dir=Path("src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"),
    monolith_path=Path("canonic_questionnaire_central/questionnaire_monolith.json"),
    backup_dir=Path("backups/contracts"),
    dry_run=True
)

for i in range(1, 11):
    path = remediator.contracts_dir / f"Q{i:03d}.v3.json"
    if path.exists():
        with open(path) as f:
            contract = json.load(f)
        decision = remediator.validator.validate_contract(contract)
        status = "✅" if decision.score.total_score >= 80 else "⚠️"
        print(f"{status} Q{i:03d}: {decision.score.total_score:.1f}/100 - {decision.decision.value}")
EOF
```

## 🛠️ Troubleshooting

### "No improvement" Result
- Contract may already be optimal
- Try `--strategy patch` or `--strategy regenerate`
- Check blockers in dry-run output

### Import Errors
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Permission Denied
```bash
chmod +x scripts/contract_remediator.py
chmod +x scripts/rollback_contract.py
```

## 📖 Full Documentation

See `docs/CONTRACT_REMEDIATOR.md` for complete documentation.

## 🧪 Run Tests

```bash
pip install pytest
pytest tests/test_contract_remediator.py -v
```

---

**Remember**: Dry-run first, verify changes, then commit! 🎯
