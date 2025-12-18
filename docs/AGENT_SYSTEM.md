# F.A.R.F.A.N Agent System

## Overview

The F.A.R.F.A.N Agent System implements strict **epistemic constraints** and **discovery protocols** to ensure rigorous, falsifiable, and evidence-based analysis of repository structure and content.

## Architecture

```
farfan_pipeline/agents/
├── __init__.py                  # Module exports
├── prime_directives.py          # Epistemic constraint enforcement
└── discovery_protocol.py        # Repository inventory acquisition
```

---

## Prime Directives: Epistemic Constraints

### Section 0.1: Non-Negotiable Constraints

| CONSTRAINT | ENFORCEMENT |
|------------|-------------|
| **NO_GUESSING** | If evidence insufficient → HALT → declare `INSUFFICIENT_EVIDENCE` → specify exact inputs required |
| **NO_HEDGING** | Forbidden terms: "probably", "likely", "maybe", "it seems", "should work" |
| **SEPARATION_MANDATORY** | Every statement labeled: `[OBSERVATION]`, `[ASSUMPTION]`, `[DECISION]` |
| **FALSIFIABILITY** | Every claim must specify what would disprove it |

### Usage Example

```python
from farfan_pipeline.agents import (
    EpistemicConstraints,
    StatementType,
    FalsifiableStatement,
)

# Create a falsifiable statement
stmt = EpistemicConstraints.create_falsifiable_statement(
    claim="[OBSERVATION] Repository contains 240 analytical methods",
    statement_type=StatementType.OBSERVATION,
    evidence=[
        "METHODS_TO_QUESTIONS_AND_FILES.json contains 240 entries",
        "METHODS_OPERACIONALIZACION.json contains 240 entries",
    ],
    disproof_conditions=[
        "Count of methods in either file differs from 240",
        "Methods list between files shows mismatch",
    ],
)

# Validate no hedging
EpistemicConstraints.validate_no_hedging(
    "The repository contains exactly 240 methods"
)  # ✓ PASS

# This would fail:
# EpistemicConstraints.validate_no_hedging(
#     "The repository probably contains 240 methods"
# )  # ✗ FAIL: EpistemicViolationError

# Validate statement is labeled
text = "[DECISION] Implement solution using approach Y"
stmt_type = EpistemicConstraints.validate_statement_labeled(text)
assert stmt_type == StatementType.DECISION

# Halt on insufficient evidence
try:
    EpistemicConstraints.halt_insufficient_evidence(
        context="method calibration",
        required_inputs=["validation_set", "num_runs"],
    )
except EpistemicViolationError as e:
    print(f"Halted: {e}")
```

---

## Discovery Protocol: Mandatory Inventory Acquisition

### Section 1.1: Triangulation Phase

**BEFORE ANY OTHER ACTION**, the discovery protocol executes:

#### Step 1.1.1: Repository Scan Commands

Comprehensive triangulation of repository structure including:
- Python source files (`.py`)
- Test files (`test_*.py`, `*_test.py`)
- Configuration files (`.toml`, `.yaml`, `.json`, `.ini`, etc.)
- Documentation (`.md`, `.rst`, `.txt`)
- Data files (`.csv`, `.pdf`, `.xlsx`, `.parquet`)
- Dependency extraction (`requirements.txt`, `pyproject.toml`)
- Architecture analysis (package structure, module hierarchy)

### Usage Example

```python
from pathlib import Path
from farfan_pipeline.agents import DiscoveryProtocol

# Initialize protocol
repo_root = Path("/path/to/repository")
protocol = DiscoveryProtocol(repo_root)

# Execute comprehensive scan
inventory = protocol.execute_repository_scan()

# Access results
print(f"Total Files: {inventory.total_files}")
print(f"Lines of Code: {inventory.total_lines_of_code:,}")
print(f"Python Files: {len(inventory.python_files)}")
print(f"Dependencies: {len(inventory.dependencies)}")

# Generate human-readable report
report = protocol.generate_inventory_report(inventory)
print(report)
```

### Inventory Structure

```python
@dataclass
class RepositoryInventory:
    python_files: list[Path]           # All .py files
    test_files: list[Path]             # Test files
    config_files: list[Path]           # Configuration files
    documentation_files: list[Path]    # Documentation
    data_files: list[Path]             # Data files
    dependencies: dict[str, str]       # name -> version
    architecture_summary: dict         # Structure analysis
    total_files: int                   # File count
    total_lines_of_code: int          # Total LOC
```

---

## Demonstration

Run the included demonstration script:

```bash
python3.12 demonstrate_agent.py
```

This executes:
1. **Epistemic Constraints Demo**: Shows validation of hedging, statement labeling, and falsifiability
2. **Discovery Protocol Demo**: Performs full repository scan and generates inventory report

---

## Testing

### Run Agent Tests

```bash
# Test epistemic constraints
pytest tests/test_agent_prime_directives.py -v

# Test discovery protocol
pytest tests/test_agent_discovery_protocol.py -v

# Run all agent tests
pytest tests/test_agent_*.py -v
```

### Test Coverage

**Prime Directives** (`test_agent_prime_directives.py`):
- ✓ No hedging validation (positive and negative cases)
- ✓ Statement labeling detection (all types)
- ✓ Insufficient evidence halt mechanism
- ✓ Falsifiable statement creation
- ✓ Constraint violation detection
- ✓ Immutability enforcement

**Discovery Protocol** (`test_agent_discovery_protocol.py`):
- ✓ Repository scan execution
- ✓ File type scanning (Python, tests, configs, docs, data)
- ✓ Dependency extraction (requirements.txt, pyproject.toml)
- ✓ Architecture analysis
- ✓ Line counting
- ✓ Inventory report generation
- ✓ Error handling

---

## Type Safety

All agent modules are fully type-annotated and pass strict type checking:

```bash
# Type check with mypy (strict mode)
mypy src/farfan_pipeline/agents/ --strict

# Lint with ruff
ruff check src/farfan_pipeline/agents/
```

Type aliases used:
- `MetadataDict`: Flexible metadata storage
- `ArchitectureSummary`: Architecture analysis results

---

## Error Handling

### EpistemicViolationError

Raised when epistemic constraints are violated:

```python
from farfan_pipeline.agents import EpistemicViolationError

try:
    EpistemicConstraints.validate_no_hedging("This probably works")
except EpistemicViolationError as e:
    print(f"Constraint violated: {e}")
    # Output: NO_HEDGING constraint violated. Forbidden terms found: ['probably']
```

### FileNotFoundError

Raised when repository root does not exist:

```python
from pathlib import Path
from farfan_pipeline.agents import DiscoveryProtocol

fake_path = Path("/nonexistent/repository")
protocol = DiscoveryProtocol(fake_path)

try:
    inventory = protocol.execute_repository_scan()
except FileNotFoundError as e:
    print(f"Repository not found: {e}")
```

---

## Integration with F.A.R.F.A.N Pipeline

The agent system can be integrated into the main F.A.R.F.A.N pipeline for:

1. **Repository Validation**: Pre-flight checks before pipeline execution
2. **Evidence Tracking**: Ensure all claims are falsifiable and evidence-based
3. **Architectural Analysis**: Verify code structure meets quality standards
4. **Dependency Auditing**: Track and validate external dependencies

### Example Integration

```python
from pathlib import Path
from farfan_pipeline.agents import DiscoveryProtocol, EpistemicConstraints

def validate_repository_before_analysis(repo_path: Path) -> bool:
    """Validate repository structure before running analysis."""
    
    # Execute discovery protocol
    protocol = DiscoveryProtocol(repo_path)
    inventory = protocol.execute_repository_scan()
    
    # Create falsifiable validation statement
    stmt = EpistemicConstraints.create_falsifiable_statement(
        claim=f"[OBSERVATION] Repository has {inventory.total_files} files",
        statement_type=StatementType.OBSERVATION,
        evidence=[f"Discovery scan counted {inventory.total_files} files"],
        disproof_conditions=["Recount produces different total"],
    )
    
    # Check minimum requirements
    has_tests = len(inventory.test_files) > 0
    has_config = len(inventory.config_files) > 0
    has_docs = len(inventory.documentation_files) > 0
    
    return all([has_tests, has_config, has_docs])
```

---

## Philosophy: Scientific Method Applied to Code

The agent system enforces a **scientific approach** to code analysis:

1. **Observations**: Facts directly from the repository (file counts, dependencies)
2. **Assumptions**: Explicit statements about what we believe (marked clearly)
3. **Decisions**: Actions based on observations and assumptions (traceable reasoning)
4. **Falsifiability**: Every claim can be tested and potentially disproven

This aligns with F.A.R.F.A.N's **SIN_CARRETA** doctrine:
- **Deterministic**: Same repository → same inventory
- **Reproducible**: Explicit evidence chains
- **Traceable**: All claims labeled and justified

---

## API Reference

### EpistemicConstraints

Static methods for constraint enforcement:

- `validate_no_hedging(text: str) -> None`
- `validate_statement_labeled(text: str) -> StatementType`
- `halt_insufficient_evidence(context: str, required_inputs: list[str]) -> None`
- `create_falsifiable_statement(...) -> FalsifiableStatement`
- `validate_falsifiability(claim: str, disproof_conditions: list[str]) -> None`

### DiscoveryProtocol

Methods for repository scanning:

- `__init__(repository_root: Path) -> None`
- `execute_repository_scan() -> RepositoryInventory`
- `generate_inventory_report(inventory: RepositoryInventory) -> str`

Private methods:
- `_scan_python_files() -> list[Path]`
- `_scan_test_files() -> list[Path]`
- `_scan_config_files() -> list[Path]`
- `_scan_documentation_files() -> list[Path]`
- `_scan_data_files() -> list[Path]`
- `_extract_dependencies() -> dict[str, str]`
- `_analyze_architecture() -> ArchitectureSummary`
- `_count_lines_of_code(python_files: list[Path]) -> int`

---

## License

Proprietary - F.A.R.F.A.N Pipeline Team

---

## Version

**Version**: 1.0.0  
**Last Updated**: 2024-12-18  
**Maintainers**: F.A.R.F.A.N Pipeline Team
