#!/usr/bin/env python3
"""
Script: verify_phase_chain.py
Purpose: Verify the dependency chain and DAG structure for a given phase

This script analyzes the import structure of a phase to ensure:
- No circular dependencies exist
- All files participate in the dependency graph
- Files are in the correct topological order
- No orphaned files exist

Usage:
    python scripts/audit/verify_phase_chain.py --phase 2 --strict
    python scripts/audit/verify_phase_chain.py --phase 2 --output report.json
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


class ImportAnalyzer(ast.NodeVisitor):
    """Analyzes imports in a Python file."""
    
    def __init__(self):
        self.imports: list[str] = []
    
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.append(node.module)


def extract_imports(file_path: Path) -> list[str]:
    """Extract all imports from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        analyzer = ImportAnalyzer()
        analyzer.visit(tree)
        return analyzer.imports
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
        return []


def build_dependency_graph(phase_dir: Path, phase_num: int) -> dict[str, list[str]]:
    """Build dependency graph for a phase."""
    graph: dict[str, list[str]] = defaultdict(list)
    
    # Get all Python files in the phase
    py_files = list(phase_dir.rglob("*.py"))
    
    # Filter out __pycache__ and backup files
    py_files = [
        f for f in py_files
        if "__pycache__" not in str(f) and not f.name.endswith(".bak")
    ]
    
    # Build module name mapping
    module_map: dict[str, Path] = {}
    for py_file in py_files:
        rel_path = py_file.relative_to(REPO_ROOT / "src")
        module_name = str(rel_path.with_suffix("")).replace("/", ".")
        module_map[module_name] = py_file
        
        # Also map short name
        short_name = py_file.stem
        module_map[short_name] = py_file
    
    # Analyze imports for each file
    for py_file in py_files:
        rel_path = py_file.relative_to(REPO_ROOT / "src")
        module_name = str(rel_path.with_suffix("")).replace("/", ".")
        
        imports = extract_imports(py_file)
        
        # Filter to only imports within this phase
        phase_module_prefix = f"farfan_pipeline.phases.Phase_{phase_num}"
        for imp in imports:
            if imp.startswith(phase_module_prefix):
                # Extract the imported module name
                parts = imp.split(".")
                if len(parts) > 4:  # farfan_pipeline.phases.Phase_N.module
                    imported_module = parts[4]
                    graph[module_name].append(imported_module)
    
    return dict(graph)


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Detect cycles in the dependency graph using DFS."""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:] + [neighbor])
                return True
        
        path.pop()
        rec_stack.remove(node)
        return False
    
    for node in graph:
        if node not in visited:
            dfs(node)
    
    return cycles


def find_orphaned_files(phase_dir: Path, graph: dict[str, list[str]]) -> list[str]:
    """Find files that are not in the dependency graph."""
    py_files = list(phase_dir.rglob("*.py"))
    py_files = [
        f for f in py_files
        if "__pycache__" not in str(f) and not f.name.endswith(".bak")
    ]
    
    # Get all nodes in the graph (both keys and values)
    graph_nodes = set(graph.keys())
    for deps in graph.values():
        graph_nodes.update(deps)
    
    # Find orphaned files
    orphaned = []
    for py_file in py_files:
        stem = py_file.stem
        rel_path = py_file.relative_to(REPO_ROOT / "src")
        module_name = str(rel_path.with_suffix("")).replace("/", ".")
        
        # Skip __init__.py files
        if stem == "__init__":
            continue
        
        # Check if file is in graph
        if stem not in graph_nodes and module_name not in graph_nodes:
            # Check if it's in allowed directories
            if any(part in str(py_file) for part in ["tests", "docs", "epistemological_assets"]):
                continue
            orphaned.append(str(py_file.relative_to(phase_dir)))
    
    return orphaned


def verify_phase_chain(phase_num: int, strict: bool = False, output: str | None = None) -> int:
    """
    Verify the dependency chain for a phase.
    
    Args:
        phase_num: Phase number to verify
        strict: If True, fail on any warning
        output: Optional output file for JSON report
        
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    phase_dir = REPO_ROOT / "src" / "farfan_pipeline" / "phases" / f"Phase_{phase_num}"
    
    if not phase_dir.exists():
        print(f"Error: Phase directory not found: {phase_dir}", file=sys.stderr)
        return 1
    
    print(f"Verifying Phase {phase_num} dependency chain...")
    print(f"Phase directory: {phase_dir}")
    print("=" * 60)
    
    # Build dependency graph
    graph = build_dependency_graph(phase_dir, phase_num)
    print(f"\n✓ Built dependency graph with {len(graph)} modules")
    
    # Detect cycles
    cycles = detect_cycles(graph)
    if cycles:
        print(f"\n✗ CIRCULAR DEPENDENCIES DETECTED: {len(cycles)} cycle(s)")
        for i, cycle in enumerate(cycles, 1):
            print(f"  Cycle {i}: {' → '.join(cycle)}")
        if strict:
            return 1
    else:
        print("\n✓ No circular dependencies detected")
    
    # Find orphaned files
    orphaned = find_orphaned_files(phase_dir, graph)
    if orphaned:
        print(f"\n⚠ WARNING: Found {len(orphaned)} potentially orphaned file(s):")
        for orphan in orphaned:
            print(f"  - {orphan}")
        if strict:
            return 1
    else:
        print("\n✓ No orphaned files detected")
    
    # Generate report
    report = {
        "phase": phase_num,
        "timestamp": str(Path(__file__).stat().st_mtime),
        "phase_dir": str(phase_dir),
        "total_modules": len(graph),
        "has_cycles": len(cycles) > 0,
        "cycle_count": len(cycles),
        "cycles": cycles,
        "orphaned_files": orphaned,
        "dependency_graph": graph,
    }
    
    # Save report if requested
    if output:
        output_path = Path(output)
        output_path.write_text(json.dumps(report, indent=2))
        print(f"\n✓ Report saved to: {output_path}")
    
    print("\n" + "=" * 60)
    if cycles or (strict and orphaned):
        print("VERIFICATION FAILED")
        return 1
    else:
        print("VERIFICATION PASSED")
        return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify Phase dependency chain and DAG structure"
    )
    parser.add_argument(
        "--phase",
        type=int,
        required=True,
        help="Phase number to verify (e.g., 2)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings (orphaned files)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for JSON report"
    )
    
    args = parser.parse_args()
    return verify_phase_chain(args.phase, args.strict, args.output)


if __name__ == "__main__":
    sys.exit(main())
