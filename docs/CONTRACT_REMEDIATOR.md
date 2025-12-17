# Automated Contract Remediator

Automated tool for fixing and validating F.A.R.F.A.N executor contracts based on CQVR (Contract Quality, Validation, and Remediation) scores.

## Features

### Auto-fix Capabilities
- **Identity-Schema Coherence**: Fixes mismatches between `identity` fields and `output_contract.schema.properties` const values
- **Method Assembly Alignment**: Rebuilds assembly rules to align with method binding provides
- **Signal Threshold Validation**: Sets proper `minimum_signal_threshold` when mandatory signals are present
- **Output Schema Required Fields**: Ensures all required fields are defined in properties
- **Source Hash Computation**: Calculates and updates SHA256 hash from questionnaire_monolith

### Regeneration Logic
- Detects contracts needing full regeneration based on CQVR tier scores
- Pulls patterns and expected_elements from questionnaire_monolith
- Applies correct contract template structure
- Validates before writing (ensures improvement over original)

### Safety Features
- **Automatic Backups**: Creates timestamped backups before any modification
- **Dry-Run Mode**: Preview changes without writing files
- **Diff Generation**: Shows exact differences between original and modified contracts
- **Rollback Capability**: Restore contracts to any previous backup version
- **Version History**: Maintains complete remediation log in contract metadata

## Installation

The scripts are located in the `scripts/` directory and require Python 3.12+.

```bash
# Ensure you're in the repository root
cd /path/to/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL

# Scripts are ready to use
python3 scripts/contract_remediator.py --help
```

## Usage

### Basic Usage

#### Remediate Single Contract
```bash
# Auto-fix strategy (recommended)
python scripts/contract_remediator.py --contract Q002.v3.json --strategy auto

# Patch strategy (targeted fixes based on CQVR recommendations)
python scripts/contract_remediator.py --contract Q002.v3.json --strategy patch

# Regenerate strategy (pull from questionnaire_monolith)
python scripts/contract_remediator.py --contract Q002.v3.json --strategy regenerate
```

#### Remediate Multiple Contracts
```bash
# Batch by question IDs
python scripts/contract_remediator.py --batch Q001 Q002 Q003 --strategy auto

# All contracts Q001-Q030
python scripts/contract_remediator.py --all --strategy auto
```

#### Remediate Failing Contracts
```bash
# Regenerate all contracts below threshold
python scripts/contract_remediator.py --regenerate --threshold 80

# Auto-fix all contracts below 70
python scripts/contract_remediator.py --all --strategy auto --threshold 70
```

### Dry-Run Mode

Preview changes without modifying files:

```bash
# Dry-run single contract
python scripts/contract_remediator.py --contract Q002.v3.json --dry-run

# Dry-run all contracts
python scripts/contract_remediator.py --all --dry-run
```

### Custom Paths

```bash
python scripts/contract_remediator.py \
  --contract Q002.v3.json \
  --contracts-dir /custom/path/to/contracts \
  --monolith /custom/path/to/questionnaire_monolith.json \
  --backup-dir /custom/path/to/backups
```

## Rollback Utility

Restore contracts to previous versions.

### List Backups

```bash
# List all backups
python scripts/rollback_contract.py --list

# List backups for specific contract
python scripts/rollback_contract.py --list --contract Q002.v3
```

### Show Diff

```bash
python scripts/rollback_contract.py \
  --diff \
  --backup Q002_backup_20250117_120000.json \
  --contract Q002.v3.json
```

### Rollback Contract

```bash
# Rollback (creates backup of current version first)
python scripts/rollback_contract.py \
  --rollback \
  --backup Q002_backup_20250117_120000.json \
  --contract Q002.v3.json

# Dry-run rollback
python scripts/rollback_contract.py \
  --rollback \
  --backup Q002_backup_20250117_120000.json \
  --contract Q002.v3.json \
  --dry-run
```

## Remediation Strategies

### Auto Strategy
Applies all safe automatic fixes:
- Identity-schema coherence
- Method assembly alignment
- Signal threshold validation
- Output schema required fields

**When to use**: First pass on any contract, routine maintenance

### Patch Strategy
Applies targeted patches based on CQVR validation results:
- All auto fixes
- Source hash computation (C3 recommendation)
- Specific fixes for identified blockers

**When to use**: Contracts with known specific issues, moderate score (40-70)

### Regenerate Strategy
Pulls core data from questionnaire_monolith:
- Patterns
- Expected elements
- Method sets

**When to use**: Contracts with critically low scores (<40), major structural issues

## CQVR Scoring

The remediator uses CQVR validation to assess contracts:

### Tier 1: Critical Components (55 points)
- **A1** (20 pts): Identity-Schema Coherence
- **A2** (20 pts): Method-Assembly Alignment
- **A3** (10 pts): Signal Requirements Integrity
- **A4** (5 pts): Output Schema Validation

### Tier 2: Functional Components (30 points)
- **B1** (10 pts): Pattern Coverage
- **B2** (10 pts): Method Specificity
- **B3** (10 pts): Validation Rules

### Tier 3: Quality Components (15 points)
- **C1** (5 pts): Documentation Quality
- **C2** (5 pts): Human-Readable Template
- **C3** (5 pts): Metadata Completeness

### Thresholds
- **Production Ready**: Total ≥ 80, Tier 1 ≥ 45
- **Patchable**: Tier 1 ≥ 35, Total ≥ 60
- **Needs Reformulation**: Tier 1 < 35

## Output Examples

### Successful Remediation
```
Remediating Q005...
  Backed up to: Q005_backup_20250117_143022.json
  ✅ Success: 61.0 → 71.0 (+10.0)
  Fixes: signal_threshold

================================================================================
SUMMARY
================================================================================
Total processed: 1
Successful: 1
Failed: 0
No improvement: 0
Average improvement: +10.0 points
```

### No Improvement Needed
```
Remediating Q001...
  ⚠️  No improvement: 82.0

================================================================================
SUMMARY
================================================================================
Total processed: 1
Successful: 0
Failed: 0
No improvement: 1
```

### Batch Summary
```
================================================================================
SUMMARY
================================================================================
Total processed: 30
Successful: 18
Failed: 0
No improvement: 12
Average improvement: +8.3 points

✅ Production-ready contracts (≥80):
  Q001.v3.json: 82.0
  Q002.v3.json: 84.5
  Q003.v3.json: 81.2
  ...
```

## Backup System

### Backup Format
Backups are stored as:
```
backups/contracts/{QUESTION_ID}_backup_{TIMESTAMP}.json
```

Example: `Q002_backup_20250117_143022.json`

### Backup Safety
- Original contract backed up before any modification
- Current contract backed up before rollback
- Backups never overwritten
- Complete version history maintained

### Backup Retention
Backups are kept indefinitely. To clean up:

```bash
# List old backups
python scripts/rollback_contract.py --list

# Manually remove old backups
rm backups/contracts/*_backup_202412*.json
```

## Contract Metadata

After remediation, contracts include:

```json
{
  "identity": {
    "updated_at": "2025-01-17T14:30:22.123456+00:00",
    "contract_hash": "a1b2c3d4..."
  },
  "traceability": {
    "remediation_log": [
      {
        "timestamp": "2025-01-17T14:30:22.123456+00:00",
        "fixes_applied": ["signal_threshold", "identity_schema_coherence"],
        "tool": "contract_remediator.py"
      }
    ]
  }
}
```

## Integration with Pipeline

### Pre-Execution Validation
```bash
# Validate all contracts before pipeline run
python scripts/contract_remediator.py --all --dry-run --threshold 80
```

### Batch Remediation Workflow
```bash
# 1. Identify failing contracts
python scripts/contract_remediator.py --regenerate --threshold 40 --dry-run

# 2. Remediate with auto-fix
python scripts/contract_remediator.py --all --strategy auto

# 3. Validate results
python scripts/contract_remediator.py --all --dry-run

# 4. Targeted patches for remaining issues
python scripts/contract_remediator.py --batch Q005 Q006 --strategy patch
```

### Emergency Rollback
```bash
# List recent changes
python scripts/rollback_contract.py --list --contract Q002.v3

# Rollback if needed
python scripts/rollback_contract.py --rollback \
  --backup Q002_backup_20250117_120000.json \
  --contract Q002.v3.json
```

## Testing

Run the test suite:

```bash
# Install pytest if not already installed
pip install pytest

# Run remediator tests
pytest tests/test_contract_remediator.py -v

# Run integration tests
pytest tests/test_contract_remediator.py::TestContractRemediatorIntegration -v
```

## Troubleshooting

### "No improvement" Result
- Contract may already be at optimal score
- Check dry-run output to see what fixes would be applied
- Try different strategy (patch, regenerate)

### Import Errors
Ensure Python path includes src:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/F.A.R.F.A.N/src"
```

### Backup Not Found
Check backup directory:
```bash
python scripts/rollback_contract.py --list
```

### Permission Errors
Ensure write access to contracts and backups directories.

## Advanced Usage

### Programmatic Usage

```python
from pathlib import Path
from scripts.contract_remediator import (
    ContractRemediator,
    RemediationStrategy
)

remediator = ContractRemediator(
    contracts_dir=Path("src/.../specialized"),
    monolith_path=Path("canonic_questionnaire_central/questionnaire_monolith.json"),
    backup_dir=Path("backups/contracts"),
    dry_run=False
)

result = remediator.remediate_contract(
    Path("src/.../Q002.v3.json"),
    RemediationStrategy.AUTO
)

print(f"Score: {result.original_score} → {result.new_score}")
print(f"Fixes: {result.fixes_applied}")
```

### Custom Fixes

Extend the remediator with custom fix methods:

```python
class CustomRemediator(ContractRemediator):
    def _apply_auto_fixes(self, contract):
        modified, fixes = super()._apply_auto_fixes(contract)
        
        # Add custom fix
        if self._fix_custom_issue(modified):
            fixes.append("custom_fix")
        
        return modified, fixes
    
    def _fix_custom_issue(self, contract):
        # Implement custom fix logic
        pass
```

## Future Enhancements

Planned features:
- Interactive mode with user confirmation
- Parallel batch processing
- Contract validation reports (PDF/HTML)
- Integration with CI/CD pipeline
- Automatic regeneration triggers
- Contract quality dashboards

## Support

For issues or questions:
1. Check this documentation
2. Review test cases in `tests/test_contract_remediator.py`
3. Examine existing contracts for patterns
4. Refer to CQVR validation rubric in `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/Rubrica_CQVR_v2.md`
