# Circular Import Detection Tool

## Overview

The F.A.R.F.A.N pipeline includes a comprehensive circular import detection tool that helps maintain code quality by identifying and preventing circular dependencies between Python modules.

## What are Circular Imports?

A circular import occurs when two or more modules depend on each other, either directly or indirectly:

```
Module A imports Module B
Module B imports Module C  
Module C imports Module A  ← Circular dependency!
```

Circular imports can cause:
- Runtime ImportError exceptions
- Undefined behavior during module initialization
- Difficult-to-debug issues
- Code maintenance challenges

## Tool Location

- **Script**: `scripts/check_circular_imports.py`
- **Tests**: `tests/test_circular_imports.py`

## Usage

### Basic Check (Static Analysis)

```bash
python scripts/check_circular_imports.py
```

This performs static AST-based analysis to detect circular dependencies without actually importing the modules.

### Verbose Mode

```bash
python scripts/check_circular_imports.py --verbose
```

Provides detailed logging including:
- Number of files analyzed
- Module mapping details
- Graph construction progress
- Import resolution details

### Runtime Testing

```bash
python scripts/check_circular_imports.py --test-runtime
```

In addition to static analysis, this actually attempts to import key modules to detect runtime circular import errors.

### Full Analysis

```bash
python scripts/check_circular_imports.py --verbose --test-runtime
```

Combines both static and runtime analysis with detailed logging.

## How It Works

### 1. Static Analysis (AST-based)

The tool uses Python's Abstract Syntax Tree (AST) parser to:

1. **Find all Python files** in the project (excluding common directories like `.git`, `__pycache__`, etc.)
2. **Extract imports** from each file without executing the code
3. **Build a dependency graph** mapping which modules import which other modules
4. **Detect cycles** using Tarjan's algorithm for strongly connected components

**Algorithm**: Tarjan's strongly connected components algorithm
- **Time complexity**: O(V + E) where V is modules, E is imports
- **Space complexity**: O(V)
- **Guarantees**: Finds all cycles in a single pass

### 2. Runtime Testing (Optional)

When `--test-runtime` is enabled, the tool:

1. Attempts to import key top-level modules
2. Catches `ImportError` exceptions with "circular" or "cannot import" messages
3. Reports any modules that fail due to circular dependencies

## Output Format

### When No Circular Imports Exist

```
F.A.R.F.A.N Circular Import Detection
================================================================================
Scanning: /path/to/project

Analyzed 422 modules
Found 31 import relationships

Static Analysis Results:
--------------------------------------------------------------------------------
✅ No circular imports detected!
```

### When Circular Imports Are Found

```
F.A.R.F.A.N Circular Import Detection
================================================================================
Scanning: /path/to/project

Analyzed 422 modules
Found 31 import relationships

Static Analysis Results:
--------------------------------------------------------------------------------
⚠️  Found 2 circular import(s):
================================================================================

Circular Import #1 (3 modules):
--------------------------------------------------------------------------------
  • module.a
    File: src/package/module_a.py
  • module.b
    File: src/package/module_b.py
  • module.c
    File: src/package/module_c.py

  Import dependencies within cycle:
    module.a
      → imports module.b
    module.b
      → imports module.c
    module.c
      → imports module.a
================================================================================
```

## Exit Codes

- **0**: No circular imports detected ✅
- **1**: Circular imports found ⚠️

This allows the tool to be used in CI/CD pipelines to fail builds if circular imports are introduced.

## Integration with CI/CD

### GitHub Actions

Add to your workflow:

```yaml
- name: Check for circular imports
  run: python scripts/check_circular_imports.py
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python scripts/check_circular_imports.py
if [ $? -ne 0 ]; then
    echo "❌ Commit rejected: circular imports detected"
    exit 1
fi
```

### Make/Shell Script

Add to your `Makefile` or build script:

```makefile
check-imports:
    python scripts/check_circular_imports.py

test: check-imports
    pytest tests/
```

## Testing

The tool includes comprehensive tests in `tests/test_circular_imports.py`:

```bash
# Run all tests
pytest tests/test_circular_imports.py -v

# Run only integration tests
pytest tests/test_circular_imports.py::TestCircularImportsIntegration -v
```

### Test Coverage

- ✅ No circular imports in actual codebase
- ✅ Python file discovery
- ✅ Dependency graph construction
- ✅ Cycle detection in synthetic examples
- ✅ Exclusion of ignored directories
- ✅ Module name conversion
- ✅ Import extraction from AST
- ✅ Exit code correctness
- ✅ Key module import validation
- ✅ Verbose mode functionality

## Technical Details

### Excluded Directories

The following directories are automatically excluded from analysis:

- `.git`, `.venv`, `.venv-1`, `venv`, `env`
- `__pycache__`, `.pytest_cache`, `.tox`
- `node_modules`
- `build`, `dist`, `.eggs`
- `test_output`, `artifacts`, `artifact`, `archive`
- `evidence_traces`, `trace_examples`
- `data`, `system`

### Excluded Files

- `setup.py` (avoids execution during import)

### Module Name Resolution

The tool intelligently resolves module names:

- `src/farfan_pipeline/core/types.py` → `src.farfan_pipeline.core.types`
- `src/farfan_pipeline/__init__.py` → `src.farfan_pipeline` (package)
- Relative imports are resolved to absolute module paths

## Architecture

```
CircularImportDetector
├── find_python_files()      # Discovery
├── extract_imports()         # AST parsing
├── build_dependency_graph()  # Graph construction
├── find_cycles_tarjan()      # Cycle detection (Tarjan's algorithm)
├── test_runtime_imports()    # Runtime validation
└── format_cycle_report()     # Output formatting
```

## Best Practices

### Avoiding Circular Imports

1. **Use late imports**: Import inside functions when needed
   ```python
   def my_function():
       from module import something  # Import inside function
       return something()
   ```

2. **Refactor common code**: Move shared code to a separate module
   ```python
   # Instead of A ↔ B, use A → C ← B
   # common.py - shared code
   # module_a.py - imports common
   # module_b.py - imports common
   ```

3. **Use dependency injection**: Pass dependencies as parameters
   ```python
   def process_data(data, processor):
       return processor.process(data)
   ```

4. **Use TYPE_CHECKING**: For type hints only
   ```python
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from module import MyClass  # Only imported by type checkers
   ```

5. **Restructure architecture**: Consider if circular dependency indicates poor separation of concerns

## Troubleshooting

### False Positives

If the tool reports a cycle that you believe is incorrect:

1. Run with `--verbose` to see detailed import relationships
2. Check if the imports are actually in TYPE_CHECKING blocks (tool may not distinguish)
3. Verify the module names match the actual file structure

### Missing Cycles

If you suspect a circular import but the tool doesn't detect it:

1. Run with `--test-runtime` to check actual import behavior
2. Verify the files are not in excluded directories
3. Check if the import uses dynamic import mechanisms (e.g., `importlib.import_module`)

## Current Status

As of the latest check:

- ✅ **No circular imports detected** in the F.A.R.F.A.N codebase
- **422 modules** analyzed
- **31 import relationships** mapped
- All runtime imports successful

## Contributing

When adding new code:

1. Run the circular import checker before committing
2. If introducing intentional cross-module dependencies, consider refactoring
3. Document any unavoidable complex import relationships
4. Update tests if adding new modules that should be checked

## References

- **Tarjan's Algorithm**: Tarjan, R. (1972). "Depth-first search and linear graph algorithms". SIAM Journal on Computing.
- **Python Import System**: [Python Documentation - Import System](https://docs.python.org/3/reference/import.html)
- **AST Module**: [Python Documentation - Abstract Syntax Trees](https://docs.python.org/3/library/ast.html)

---

**Maintained by**: F.A.R.F.A.N Development Team  
**Last Updated**: 2025-12-11  
**Tool Version**: 1.0.0
