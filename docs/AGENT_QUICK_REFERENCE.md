# Agent System Quick Reference

## Import

```python
from farfan_pipeline.agents import (
    EpistemicConstraints,
    StatementType,
    FalsifiableStatement,
    EpistemicViolationError,
    DiscoveryProtocol,
    RepositoryInventory,
    InventoryComponent,
)
```

## Epistemic Constraints

### Validate No Hedging
```python
EpistemicConstraints.validate_no_hedging("This is certain")  # ✓
EpistemicConstraints.validate_no_hedging("This probably works")  # ✗ Raises EpistemicViolationError
```

### Validate Statement Labeled
```python
stmt_type = EpistemicConstraints.validate_statement_labeled(
    "[OBSERVATION] Repository has 240 methods"
)
assert stmt_type == StatementType.OBSERVATION
```

### Create Falsifiable Statement
```python
stmt = EpistemicConstraints.create_falsifiable_statement(
    claim="[OBSERVATION] Repository contains 240 methods",
    statement_type=StatementType.OBSERVATION,
    evidence=["File count matches", "Cross-reference verified"],
    disproof_conditions=["Recount shows different number"],
)
```

### Halt on Insufficient Evidence
```python
try:
    EpistemicConstraints.halt_insufficient_evidence(
        context="calibration",
        required_inputs=["validation_set", "num_runs"]
    )
except EpistemicViolationError as e:
    print(f"Halted: {e}")
```

## Discovery Protocol

### Execute Repository Scan
```python
from pathlib import Path

protocol = DiscoveryProtocol(Path("/path/to/repo"))
inventory = protocol.execute_repository_scan()

# Access results
print(f"Total files: {inventory.total_files}")
print(f"Python files: {len(inventory.python_files)}")
print(f"Dependencies: {len(inventory.dependencies)}")
```

### Generate Report
```python
report = protocol.generate_inventory_report(inventory)
print(report)
```

## Statement Types

- `StatementType.OBSERVATION` - Facts from evidence
- `StatementType.ASSUMPTION` - Explicit beliefs
- `StatementType.DECISION` - Actions taken

## Forbidden Hedging Terms

"probably", "likely", "maybe", "it seems", "should work", "might", "could be", "perhaps", "possibly", "presumably"

## Run Demo

```bash
python3.12 demonstrate_agent.py
```

## Run Tests

```bash
pytest tests/test_agent_*.py -v
```

## Lint & Type Check

```bash
ruff check src/farfan_pipeline/agents/
mypy src/farfan_pipeline/agents/ --strict
```
