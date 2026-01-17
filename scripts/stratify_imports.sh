#!/bin/bash
# IMPORT STRATIFICATION SCRIPT v2.0
# Phase 1: Detection (Ground Truth Establishment)
#
# This script is IDEMPOTENT and DETERMINISTIC - produces reproducible forensic evidence
# DO NOT modify code - detection must be non-invasive

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$REPO_ROOT/artifacts/stratification"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create immutable artifacts directory
mkdir -p "$ARTIFACTS_DIR"

echo "=========================================="
echo "IMPORT STRATIFICATION - Phase 1 Detection"
echo "=========================================="
echo "Repository: $REPO_ROOT"
echo "Artifacts: $ARTIFACTS_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# ARTIFACT 01: Raw Imports (verbatim extraction)
echo "[1/7] Extracting raw imports..."
{
    echo "# 01_IMPORTS_RAW.txt"
    echo "# Generated: $TIMESTAMP"
    echo "# All import statements verbatim from Python files"
    echo "# Format: <file_path>:<line_number>:<import_statement>"
    echo ""

    find "$REPO_ROOT" -type f -name "*.py" \
        -not -path "*/.*" \
        -not -path "*/__pycache__/*" \
        -not -path "*/venv/*" \
        -not -path "*/artifacts/*" \
        -not -path "*/backups/*" \
        -exec grep -nH "^\s*from\|^\s*import" {} \; 2>/dev/null || true
} > "$ARTIFACTS_DIR/01_imports_raw.txt"

# ARTIFACT 02: Normalized Imports (canonical forms)
echo "[2/7] Normalizing imports..."
python3 << PYEOF > "$ARTIFACTS_DIR/02_imports_normalized.txt"
import re
import sys
from pathlib import Path

print("# 02_IMPORTS_NORMALIZED.txt")
print("# Canonicalized import forms")
print("# Format: <canonical_module_path>|<symbols>|<source_file>:<line>")
print("")

artifacts_dir = Path("$ARTIFACTS_DIR")
raw_file = artifacts_dir / "01_imports_raw.txt"

import_pattern = re.compile(
    r'^(?P<file>[^:]+):(?P<line>\d+):\s*(?P<stmt>(?:from|import)\s+.+)$'
)

for line in open(raw_file):
    if line.startswith('#') or not line.strip():
        continue

    match = import_pattern.match(line.strip())
    if not match:
        continue

    file_path = match.group('file')
    line_num = match.group('line')
    stmt = match.group('stmt').strip()

    # Parse import statement
    if stmt.startswith('from '):
        # from X import Y, Z
        parts = stmt.split(' import ')
        if len(parts) == 2:
            module = parts[0].replace('from ', '').strip()
            symbols = parts[1].strip()
            print(f"{module}|{symbols}|{file_path}:{line_num}")
    elif stmt.startswith('import '):
        # import X, Y as Z
        modules = stmt.replace('import ', '').strip()
        for mod in modules.split(','):
            mod = mod.strip().split(' as ')[0].strip()
            print(f"{mod}||{file_path}:{line_num}")
PYEOF

# ARTIFACT 03: Module Resolution (filesystem existence)
echo "[3/7] Resolving module paths..."
python3 << PYEOF > "$ARTIFACTS_DIR/03_module_resolution.txt"
import sys
from pathlib import Path

print("# 03_MODULE_RESOLUTION.txt")
print("# Module existence verification on filesystem")
print("# Format: <module_path>|<status>|<resolved_file_path>")
print("")

repo_root = Path("$REPO_ROOT")
artifacts_dir = Path("$ARTIFACTS_DIR")
normalized_file = artifacts_dir / "02_imports_normalized.txt"

# Module search paths
search_roots = [
    repo_root,
    repo_root / 'src',
    repo_root / 'canonic_questionnaire_central',
]

seen_modules = set()

def module_to_paths(module_name):
    """Convert module name to possible file paths"""
    parts = module_name.split('.')
    possible_paths = []

    for root in search_roots:
        # Case 1: module/__init__.py
        module_dir = root / Path(*parts)
        init_file = module_dir / '__init__.py'
        if init_file.exists():
            possible_paths.append(str(init_file))

        # Case 2: module.py
        if len(parts) > 0:
            parent = root / Path(*parts[:-1]) if len(parts) > 1 else root
            module_file = parent / f"{parts[-1]}.py"
            if module_file.exists():
                possible_paths.append(str(module_file))

    return possible_paths

for line in open(normalized_file):
    if line.startswith('#') or not line.strip():
        continue

    parts = line.strip().split('|')
    if len(parts) < 3:
        continue

    module = parts[0].strip()

    if module in seen_modules:
        continue
    seen_modules.add(module)

    paths = module_to_paths(module)
    if paths:
        print(f"{module}|LIVE|{paths[0]}")
    else:
        print(f"{module}|DEAD|NO_FILE")
PYEOF

# ARTIFACT 04: Symbol Resolution (AST analysis)
echo "[4/7] Resolving symbol availability..."
python3 << PYEOF > "$ARTIFACTS_DIR/04_symbol_resolution.txt"
import sys
from pathlib import Path
import ast
import importlib.util

print("# 04_SYMBOL_RESOLUTION.txt")
print("# Symbol resolution via AST analysis")
print("# Format: <module>|<symbol>|<status>|<source_location>")
print("")

repo_root = Path("$REPO_ROOT")
artifacts_dir = Path("$ARTIFACTS_DIR")
normalized_file = artifacts_dir / "02_imports_normalized.txt"
module_resolution_file = artifacts_dir / "03_module_resolution.txt"

# Build module -> file mapping
module_files = {}
for line in open(module_resolution_file):
    if line.startswith('#') or not line.strip():
        continue
    parts = line.strip().split('|')
    if len(parts) == 3 and parts[1] == 'LIVE':
        module_files[parts[0]] = parts[2]

# Check symbol resolution
for line in open(normalized_file):
    if line.startswith('#') or not line.strip():
        continue

    parts = line.strip().split('|')
    if len(parts) < 3:
        continue

    module = parts[0].strip()
    symbols = parts[1].strip()
    source = parts[2].strip()

    if not symbols:  # bare import
        continue

    # Parse symbols (handle "X, Y, Z" and "(X, Y)")
    symbols = symbols.strip('()')
    symbol_list = [s.strip().split(' as ')[0].strip()
                   for s in symbols.split(',') if s.strip()]

    for symbol in symbol_list:
        if module not in module_files:
            print(f"{module}|{symbol}|MISSING|MODULE_DEAD")
            continue

        module_file = module_files[module]

        try:
            with open(module_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=module_file)

            # Look for symbol in AST
            found = False
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == symbol:
                        print(f"{module}|{symbol}|FOUND|{module_file}:{node.lineno}")
                        found = True
                        break
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == symbol:
                            print(f"{module}|{symbol}|FOUND|{module_file}:{node.lineno}")
                            found = True
                            break

            if not found:
                print(f"{module}|{symbol}|MISSING|NOT_IN_AST")

        except Exception as e:
            print(f"{module}|{symbol}|ERROR|{type(e).__name__}")
PYEOF

# ARTIFACT 05: Temporal/Architectural Stratification
echo "[5/7] Stratifying by architectural era..."
python3 << PYEOF > "$ARTIFACTS_DIR/05_imports_stratified.txt"
import sys
from pathlib import Path

print("# 05_IMPORTS_STRATIFIED.txt")
print("# Temporal and architectural classification")
print("# Format: <module>|<era>|<module_reality>|<symbol_reality>")
print("")

artifacts_dir = Path("$ARTIFACTS_DIR")
module_res = artifacts_dir / "03_module_resolution.txt"
symbol_res = artifacts_dir / "04_symbol_resolution.txt"

# Load module reality
module_reality = {}
for line in open(module_res):
    if line.startswith('#') or not line.strip():
        continue
    parts = line.strip().split('|')
    if len(parts) == 3:
        module_reality[parts[0]] = parts[1]

# Load symbol reality (aggregate)
symbol_reality = {}
for line in open(symbol_res):
    if line.startswith('#') or not line.strip():
        continue
    parts = line.strip().split('|')
    if len(parts) >= 3:
        key = f"{parts[0]}::{parts[1]}"
        symbol_reality[key] = parts[2]

# Architectural era classification
def classify_era(module):
    if 'orchestration.orchestrator' in module or 'orchestrator.orchestrator' in module:
        return 'ERA_ORCHESTRATOR'
    elif 'cross_cutting_infrastructure' in module:
        return 'ERA_CROSS_CUTTING'
    elif 'signal_consumption' in module:
        return 'ERA_SIGNAL_CONSUMPTION'
    elif '_deprecated' in module or 'deprecated' in module:
        return 'ERA_DEPRECATED'
    elif module.startswith('farfan_pipeline'):
        return 'ERA_MODERN'
    elif 'bootstrap' in module or 'primitives' in module:
        return 'ERA_BOOTSTRAP'
    else:
        return 'ERA_UNKNOWN'

# Output stratification
seen = set()
for module, mod_real in module_reality.items():
    if module in seen:
        continue
    seen.add(module)

    era = classify_era(module)
    # Default symbol reality (for modules without symbols checked)
    sym_real = 'N/A'

    print(f"{module}|{era}|{mod_real}|{sym_real}")
PYEOF

# ARTIFACT 06: Decision Matrix
echo "[6/7] Building decision matrix..."
python3 << PYEOF > "$ARTIFACTS_DIR/06_decision_matrix.txt"
import sys
from pathlib import Path

print("# 06_DECISION_MATRIX.txt")
print("# Mechanical remediation actions per import")
print("# Format: <module>|<era>|<module_reality>|<symbol_reality>|<action>|<status>")
print("")

artifacts_dir = Path("$ARTIFACTS_DIR")
stratified = artifacts_dir / "05_imports_stratified.txt"

# Decision rules per Phase 4 protocol
def decide_action(era, mod_real, sym_real):
    # DEAD + MISSING
    if mod_real == 'DEAD':
        return ('DELETE', 'ARCHITECTURAL_GHOST')

    # LIVE + ERA_DEPRECATED
    if mod_real == 'LIVE' and era in ['ERA_DEPRECATED', 'ERA_ORCHESTRATOR', 'ERA_CROSS_CUTTING']:
        return ('REDIRECT', 'MIGRATION_ARTIFACT')

    # LIVE + MODERN
    if mod_real == 'LIVE' and era == 'ERA_MODERN':
        return ('KEEP', 'CANONICAL')

    # Default: investigate
    return ('INVESTIGATE', 'UNKNOWN')

for line in open(stratified):
    if line.startswith('#') or not line.strip():
        continue

    parts = line.strip().split('|')
    if len(parts) < 4:
        continue

    module, era, mod_real, sym_real = parts[0], parts[1], parts[2], parts[3]
    action, status = decide_action(era, mod_real, sym_real)

    print(f"{module}|{era}|{mod_real}|{sym_real}|{action}|{status}")
PYEOF

# ARTIFACT 07: Dependency Gravity (import frequency)
echo "[7/7] Calculating dependency gravity..."
python3 << PYEOF > "$ARTIFACTS_DIR/07_dependency_gravity.txt"
import sys
from pathlib import Path
from collections import Counter

print("# 07_DEPENDENCY_GRAVITY.txt")
print("# Import frequency and centrality metrics")
print("# Format: <module>|<import_count>|<source_file_count>|<centrality>")
print("")

artifacts_dir = Path("$ARTIFACTS_DIR")
normalized = artifacts_dir / "02_imports_normalized.txt"

module_counts = Counter()
module_files = {}

for line in open(normalized):
    if line.startswith('#') or not line.strip():
        continue

    parts = line.strip().split('|')
    if len(parts) < 3:
        continue

    module = parts[0].strip()
    source_loc = parts[2].strip().split(':')[0]

    module_counts[module] += 1

    if module not in module_files:
        module_files[module] = set()
    module_files[module].add(source_loc)

# Calculate centrality (simple: count / unique_files)
for module in sorted(module_counts.keys(), key=lambda m: module_counts[m], reverse=True):
    count = module_counts[module]
    file_count = len(module_files[module])
    centrality = count / file_count if file_count > 0 else 0

    print(f"{module}|{count}|{file_count}|{centrality:.2f}")
PYEOF

echo ""
echo "=========================================="
echo "Phase 1 Detection Complete"
echo "=========================================="
echo ""
echo "Artifacts generated in: $ARTIFACTS_DIR"
echo ""
ls -lh "$ARTIFACTS_DIR"
echo ""
echo "Next: Review artifacts and proceed to Phase 2 (Stratification Analysis)"
